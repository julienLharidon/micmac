#!/usr/bin/env python3
"""
MicMac Cloud Filesystem (FUSE)
Redirige les accès fichiers locaux vers Google Cloud Storage et Redis.
Permet à MicMac de fonctionner en mode 'Stateless' sur Cloud Run.
"""

import os
import sys
import errno
import logging
import threading
from fuse import FUSE, FuseOSError, Operations
from google.cloud import storage
import redis

# --- Paramètres de Configuration ---
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET", "micmac-data-ign")
REDIS_HOST_ADDR = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT_NUM = int(os.getenv("REDIS_PORT", 6379))
LOCAL_WORKSPACE_DIR = os.getenv("MICMAC_LOCAL_CACHE", "/tmp/micmac_cache")

class MicMacCloudFilesystem(Operations):
    """
    Implémentation FUSE pour l'abstraction I/O de MicMac.
    Gère le streaming GCS, le cache Redis pour les points de liaison,
    et un cache local pour le support de l'accès aléatoire (TIFF).
    """

    def __init__(self, bucket_name, redis_client):
        self.storage_client = storage.Client()
        self.gcs_bucket = self.storage_client.bucket(bucket_name)
        self.redis_cache = redis_client
        self.local_workspace = LOCAL_WORKSPACE_DIR

        # Création du répertoire de travail local pour le cache
        os.makedirs(self.local_workspace, exist_ok=True)

        # Cache de métadonnées (répertoires virtuels GCS) pour limiter les appels API
        self._virtual_dir_metadata = {}
        # Suivi des fichiers modifiés localement devant être uploadés sur GCS
        self._modified_files_registry = set()
        self._cache_lock = threading.Lock()

    # --- Utilitaires de Chemin ---

    def _get_gcs_blob_name(self, fuse_path):
        """Convertit un chemin FUSE en nom d'objet GCS (sans le slash initial)."""
        return fuse_path.lstrip("/")

    def _get_local_cache_path(self, fuse_path):
        """Mappe un chemin FUSE vers le stockage local temporaire en préservant la structure."""
        gcs_name = self._get_gcs_blob_name(fuse_path)
        local_path = os.path.join(self.local_workspace, gcs_name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        return local_path

    # --- Gestion des Métadonnées (Attributs) ---

    def getattr(self, path, fh=None):
        """Récupère les attributs d'un fichier ou répertoire (appelé très fréquemment)."""
        gcs_blob_name = self._get_gcs_blob_name(path)

        # Racine du système de fichiers
        if path == "/":
            return dict(st_mode=(16877), st_nlink=2, st_size=4096)

        # Priorité 1 : Fichier/Dossier présent dans le cache local
        local_path = self._get_local_cache_path(path)
        if os.path.exists(local_path):
            stat_info = os.lstat(local_path)
            return dict((key, getattr(stat_info, key)) for key in (
                'st_atime', 'st_ctime', 'st_gid', 'st_mode',
                'st_mtime', 'st_nlink', 'st_size', 'st_uid'
            ))

        # Priorité 2 : Objet existant sur GCS
        blob = self.gcs_bucket.get_blob(gcs_blob_name)
        if blob:
            # Mode 33188 = Fichier régulier (rw-r--r--)
            return dict(st_mode=(33188), st_nlink=1, st_size=blob.size)

        # Priorité 3 : Répertoire virtuel sur GCS (préfixe d'objets)
        with self._cache_lock:
            if gcs_blob_name in self._virtual_dir_metadata:
                return self._virtual_dir_metadata[gcs_blob_name]

            # Vérification de l'existence d'objets avec ce préfixe
            blobs_found = list(self.gcs_bucket.list_blobs(
                prefix=gcs_blob_name + "/", max_results=1
            ))
            if blobs_found:
                # Mode 16877 = Répertoire (rwxr-xr-x)
                attr = dict(st_mode=(16877), st_nlink=2, st_size=4096)
                self._virtual_dir_metadata[gcs_blob_name] = attr
                return attr

        raise FuseOSError(errno.ENOENT)

    # --- Opérations de Répertoire ---

    def readdir(self, path, fh):
        """Liste le contenu d'un répertoire en fusionnant GCS et le cache local."""
        gcs_prefix = self._get_gcs_blob_name(path)
        if gcs_prefix:
            gcs_prefix += "/"

        entries = ['.', '..']

        # Listing GCS (Objets et Sous-répertoires virtuels)
        blobs_iterator = self.gcs_bucket.list_blobs(prefix=gcs_prefix, delimiter="/")
        for blob in blobs_iterator:
            entries.append(os.path.basename(blob.name.rstrip("/")))
        for folder_prefix in blobs_iterator.prefixes:
            entries.append(os.path.basename(folder_prefix.rstrip("/")))

        # Listing local (Fichiers créés ou modifiés non encore synchronisés)
        local_dir_path = self._get_local_cache_path(path)
        if os.path.isdir(local_dir_path):
            entries.extend(os.listdir(local_dir_path))

        return list(set(entries))

    def mkdir(self, path, mode):
        """Crée un répertoire localement (sera virtuel sur GCS)."""
        local_path = self._get_local_cache_path(path)
        os.makedirs(local_path, exist_ok=True)
        with self._cache_lock:
            self._virtual_dir_metadata[self._get_gcs_blob_name(path)] = dict(
                st_mode=(16877), st_nlink=2, st_size=4096
            )
        return 0

    # --- Opérations de Fichiers (Lecture/Écriture) ---

    def create(self, path, mode, fi=None):
        """Crée un nouveau fichier dans le cache local."""
        local_path = self._get_local_cache_path(path)
        self._modified_files_registry.add(path)
        return os.open(local_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)

    def open(self, path, flags):
        """Ouvre un fichier, en le téléchargeant depuis Redis ou GCS si nécessaire."""
        gcs_name = self._get_gcs_blob_name(path)
        local_path = self._get_local_cache_path(path)

        # Si le fichier n'est pas local, on tente de le récupérer du Cloud
        if not os.path.exists(local_path):
            # 1. Vérification Redis (Haute performance pour les points de liaison Homol/)
            redis_data = self.redis_cache.get(f"file:{gcs_name}")
            if redis_data:
                with open(local_path, "wb") as f:
                    f.write(redis_data)
            else:
                # 2. Téléchargement depuis GCS
                blob = self.gcs_bucket.get_blob(gcs_name)
                if blob:
                    blob.download_to_filename(local_path)

        # Marquage pour upload si ouverture en mode écriture
        if (flags & os.O_WRONLY) or (flags & os.O_RDWR):
            self._modified_files_registry.add(path)

        return os.open(local_path, flags)

    def read(self, path, length, offset, fh):
        """Lit les données depuis le fichier local (support de l'accès aléatoire)."""
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, data, offset, fh):
        """Écrit les données localement et marque le fichier comme modifié."""
        os.lseek(fh, offset, os.SEEK_SET)
        bytes_written = os.write(fh, data)
        self._modified_files_registry.add(path)
        return bytes_written

    def truncate(self, path, length, fh=None):
        """Tronque le fichier local."""
        local_path = self._get_local_cache_path(path)
        with open(local_path, 'r+') as f:
            f.truncate(length)
        self._modified_files_registry.add(path)

    def release(self, path, fh):
        """Ferme le fichier et synchronise vers GCS/Redis s'il a été modifié."""
        os.close(fh)
        if path in self._modified_files_registry:
            gcs_name = self._get_gcs_blob_name(path)
            local_path = self._get_local_cache_path(path)

            # Upload persistant vers GCS
            blob = self.gcs_bucket.blob(gcs_name)
            blob.upload_from_filename(local_path)

            # Mise en cache Redis pour les dossiers critiques (ex: Homol/)
            if "Homol" in gcs_name:
                with open(local_path, "rb") as f:
                    # Cache de 1h pour les échanges entre instances
                    self.redis_cache.set(f"file:{gcs_name}", f.read(), ex=3600)

            self._modified_files_registry.remove(path)
        return 0

    # --- Opérations de Suppression et Renommage ---

    def unlink(self, path):
        """Supprime un fichier localement et sur GCS."""
        gcs_name = self._get_gcs_blob_name(path)
        local_path = self._get_local_cache_path(path)
        if os.path.exists(local_path):
            os.remove(local_path)
        self.gcs_bucket.blob(gcs_name).delete()
        if path in self._modified_files_registry:
            self._modified_files_registry.remove(path)
        return 0

    def rename(self, old_path, new_path):
        """Renomme un fichier/répertoire (Copie + Suppression sur GCS)."""
        old_gcs = self._get_gcs_blob_name(old_path)
        new_gcs = self._get_gcs_blob_name(new_path)

        # GCS ne supporte pas le renommage direct : Copy -> Delete
        old_blob = self.gcs_bucket.blob(old_gcs)
        if old_blob.exists():
            self.gcs_bucket.copy_blob(old_blob, self.gcs_bucket, new_gcs)
            old_blob.delete()

        # Renommage dans le cache local
        old_local = self._get_local_cache_path(old_path)
        new_local = self._get_local_cache_path(new_path)
        if os.path.exists(old_local):
            os.rename(old_local, new_local)
        return 0

# --- Point d'Entrée Principal ---

def main():
    if len(sys.argv) != 2:
        print(f"Utilisation: {sys.argv[0]} <point_de_montage>")
        sys.exit(1)

    mountpoint = sys.argv[1]
    logging.basicConfig(level=logging.INFO)

    # Connexion à Redis
    redis_conn = redis.Redis(host=REDIS_HOST_ADDR, port=REDIS_PORT_NUM)

    # Démarrage de FUSE
    print(f"Lancement du Filesystem MicMac sur {mountpoint}...")
    FUSE(
        MicMacCloudFilesystem(GCS_BUCKET_NAME, redis_conn),
        mountpoint,
        foreground=True,
        allow_other=True
    )

if __name__ == '__main__':
    main()
