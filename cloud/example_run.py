#!/usr/bin/env python3
"""
Exemple de Calcul MicMac Cloud-Native (IGN)
Ce script lance le montage FUSE, initialise l'orchestrateur et
démarre un workflow Tapioca MulScale complet.
"""

import os
import sys
import time
import subprocess
import logging
from cloud.tapioca_orchestrator import TapiocaCloudOrchestrator

# --- Configuration de l'Environnement de Démo ---
FUSE_MOUNT_DIR = "/mnt/micmac_ign_project"
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET", "micmac-data-ign")
DEFAULT_IMAGE_PATTERN = "*.tif"

# Configuration du Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- Montage et Démontage du Système de Fichiers ---

def initialize_gcs_mount():
    """Démarre le wrapper FUSE en tâche de fond pour le streaming GCS."""
    logging.info(f"Initialisation du montage GCS (Bucket: {GCS_BUCKET_NAME}) sur {FUSE_MOUNT_DIR}")
    os.makedirs(FUSE_MOUNT_DIR, exist_ok=True)

    # Lancement asynchrone du script de gestion I/O
    fuse_process = subprocess.Popen(["python3", "cloud/micmac_fs.py", FUSE_MOUNT_DIR])

    # Attente de stabilisation du montage
    logging.info("Patientez 5 secondes pour la stabilisation du montage FUSE...")
    time.sleep(5)

    return fuse_process

def cleanup_gcs_mount(fuse_process):
    """Libère proprement les ressources et démonte le système de fichiers."""
    logging.info(f"Nettoyage du point de montage : {FUSE_MOUNT_DIR}")
    try:
        # Commande système pour démonter FUSE
        subprocess.run(["fusermount", "-u", FUSE_MOUNT_DIR], check=True)
        fuse_process.terminate()
        logging.info("Montage FUSE libéré avec succès.")
    except Exception as err:
        logging.error(f"Erreur lors du démontage FUSE : {err}")

# --- Exécution du Workflow Tapioca ---

def execute_tapioca_workflow():
    """Orchestre le workflow Tapioca MulScale sur le jeu d'images cible."""
    logging.info("--- Démarrage de l'Orchestration Cloud-Native (Tapioca) ---")

    # 1. Instanciation de l'orchestrateur
    orchestrator = TapiocaCloudOrchestrator(GCS_BUCKET_NAME)

    # 2. On se place dans le point de montage GCS/FUSE
    # Les binaires mm3d (PastDevlop/Pastis) croiront travailler sur un disque local.
    original_working_directory = os.getcwd()
    os.chdir(FUSE_MOUNT_DIR)

    try:
        # Lancement de la stratégie MulScale
        # Paramètres : Low-Res (500px), High-Res (No resize = -1)
        orchestrator.run_mulscale_strategy(DEFAULT_IMAGE_PATTERN, 500, -1)
        logging.info("--- Workflow Tapioca (MulScale) terminé sans erreurs. ---")
    finally:
        # Retour au répertoire d'origine après le calcul
        os.chdir(original_working_directory)

# --- Point d'Entrée Principal ---

def main():
    """Point d'entrée principal pour la démonstration."""
    fuse_handle = None
    try:
        # Étape 1 : Activation du streaming GCS
        fuse_handle = initialize_gcs_mount()

        # Étape 2 : Exécution du calcul photogrammétrique distribué
        execute_tapioca_workflow()

    except KeyboardInterrupt:
        logging.warning("Interruption manuelle détectée par l'utilisateur.")
    except Exception as err:
        logging.error(f"Échec de l'exécution du workflow Cloud-Native : {err}")
    finally:
        # Étape 3 : Nettoyage final
        if fuse_handle:
            cleanup_gcs_mount(fuse_handle)

if __name__ == "__main__":
    main()
