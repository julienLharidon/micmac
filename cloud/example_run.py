#!/usr/bin/env python3
import os
import time
import subprocess
from cloud.tapioca_orchestrator import TapiocaOrchestrator

# Configuration
MOUNT_POINT = "/mnt/micmac_project"
BUCKET_NAME = os.getenv("GCS_BUCKET", "micmac-data-ign")
IMAGE_PATTERN = "*.tif"

def mount_cloud_fs():
    """Lancement du wrapper FUSE en tâche de fond."""
    print(f"--- Montage de GCS {BUCKET_NAME} sur {MOUNT_POINT}")
    os.makedirs(MOUNT_POINT, exist_ok=True)

    # Utilisation du wrapper Python micmac_fs
    fuse_proc = subprocess.Popen(["python3", "cloud/micmac_fs.py", MOUNT_POINT])

    # Attente du montage
    time.sleep(5)
    return fuse_proc

def run_tapioca_workflow():
    """Exemple d'orchestration Tapioca Cloud-Native."""
    print("--- Démarrage de l'Orchestrateur Tapioca")
    orch = TapiocaOrchestrator(BUCKET_NAME)

    # On se place dans le point de montage pour que les commandes mm3d
    # voient les fichiers "locaux" streamés depuis GCS
    os.chdir(MOUNT_POINT)

    # Lancement MulScale : 500 (LowRes), 2000 (FullRes)
    orch.run_mulscale(IMAGE_PATTERN, 500, 2000)

    print("--- Workflow Tapioca terminé avec succès.")

if __name__ == "__main__":
    fuse_p = None
    try:
        fuse_p = mount_cloud_fs()
        run_tapioca_workflow()
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")
    finally:
        if fuse_p:
            print("--- Démontage du système de fichiers")
            subprocess.run(["fusermount", "-u", MOUNT_POINT])
            fuse_p.terminate()
