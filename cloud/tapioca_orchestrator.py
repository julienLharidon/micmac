#!/usr/bin/env python3
"""
Orchestrateur Cloud-Native pour MicMac (Tapioca)
Remplace le système de Makefile de MicMac pour une distribution sur Cloud Run.
Gère le workflow : Détection des images -> PastDevlop -> Pastis (Appariement).
"""

import os
import sys
import subprocess
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage

# --- Configuration (Variables d'Environnement) ---
CLOUD_RUN_WORKER_URL = os.getenv("CLOUD_RUN_WORKER_URL")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET", "micmac-data-ign")

# Configuration du Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class TapiocaCloudOrchestrator:
    """
    Pilote l'exécution de Tapioca en décomposant les tâches de calcul
    photogrammétrique en unités atomiques distribuables sur Cloud Run.
    """

    def __init__(self, bucket_name):
        self.storage_client = storage.Client()
        self.gcs_bucket = self.storage_client.bucket(bucket_name)

    # --- Gestion de la Liste des Images ---

    def list_target_images(self, pattern):
        """Récupère la liste des fichiers images à traiter depuis GCS."""
        logging.info(f"Recherche des images sur GCS (Bucket: {GCS_BUCKET_NAME})")
        blobs_iterator = self.gcs_bucket.list_blobs()

        # Filtre basique des images .tif (à étendre avec le support regex)
        images_list = [blob.name for blob in blobs_iterator if blob.name.endswith('.tif')]
        logging.info(f"Images détectées : {len(images_list)}")
        return images_list

    # --- Dispatcher de Tâches ---

    def _execute_worker_task(self, micmac_command):
        """Dispatche une commande MicMac vers un worker Cloud Run ou localement."""
        if not CLOUD_RUN_WORKER_URL:
            # Mode local par défaut (Dev/Demo)
            logging.info(f"[EXECUTION LOCALE] : {micmac_command}")
            try:
                return subprocess.run(micmac_command, shell=True, check=True)
            except subprocess.CalledProcessError as err:
                logging.error(f"Erreur locale sur la commande : {micmac_command}")
                raise err

        # Mode Cloud Run (Dispatch via HTTP POST)
        logging.info(f"[DISPATCH CLOUD RUN] : {micmac_command}")
        try:
            response = requests.post(
                CLOUD_RUN_WORKER_URL,
                json={"cmd": micmac_command, "bucket": GCS_BUCKET_NAME},
                timeout=1800  # Timeout long pour les calculs photogrammétriques
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            logging.error(f"Échec de l'appel Cloud Run pour : {micmac_command}")
            raise err

    # --- Phases du Workflow Tapioca ---

    def run_mulscale_strategy(self, image_pattern, low_res_size, full_res_size):
        """
        Implémente la stratégie MulScale :
        1. Resampling des images (PastDevlop).
        2. Appariement Basse-Résolution global.
        3. Appariement Haute-Résolution par blocs.
        """
        images_list = self.list_target_images(image_pattern)
        if not images_list:
            logging.warning("Aucune image trouvée pour le workflow.")
            return

        logging.info("--- PHASE 1 : Resampling (PastDevlop) ---")
        # Parallélisation massive : 1 instance par image
        # Cela réduit drastiquement le temps total de préparation.
        with ThreadPoolExecutor(max_workers=20) as executor:
            for img_name in images_list:
                devlop_cmd = f"mm3d PastDevlop {img_name} Sz1={low_res_size} Sz2={full_res_size}"
                executor.submit(self._execute_worker_task, devlop_cmd)

        logging.info("--- PHASE 2 : Appariement Global Basse-Résolution ---")
        # On calcule les points de liaison sur les images réduites (tous les couples)
        low_res_match_cmd = (
            f"mm3d Pastis . 'NKS-Rel-AllCpleOfPattern@{image_pattern}' {low_res_size} "
            f"NKS=NKS-Assoc-CplIm2Hom@_SRes@dat"
        )
        self._execute_worker_task(low_res_match_cmd)

        logging.info("--- PHASE 3 : Appariement Haute-Résolution (Final) ---")
        # Phase de raffinement sur les images à résolution cible
        high_res_match_cmd = (
            f"mm3d Pastis . 'NKS-Rel-SsECh@{image_pattern}@2' {full_res_size} "
            f"NKS=NKS-Assoc-CplIm2Hom@@dat"
        )
        self._execute_worker_task(high_res_match_cmd)

# --- Point d'Entrée Principal ---

def main():
    if len(sys.argv) < 3:
        print("Utilisation: tapioca_orchestrator.py <Mode> <Pattern> [Options...]")
        print("Modes supportés: MulScale")
        sys.exit(1)

    execution_mode = sys.argv[1]
    file_pattern = sys.argv[2]

    orchestrator = TapiocaCloudOrchestrator(GCS_BUCKET_NAME)

    if execution_mode == "MulScale":
        # Valeurs par défaut : 300 (LowRes), -1 (No resize for HighRes)
        low_res = int(sys.argv[3]) if len(sys.argv) > 3 else 300
        full_res = int(sys.argv[4]) if len(sys.argv) > 4 else -1
        orchestrator.run_mulscale_strategy(file_pattern, low_res, full_res)
    else:
        logging.error(f"Mode d'exécution non supporté : {execution_mode}")

if __name__ == "__main__":
    main()
