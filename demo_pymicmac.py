"""
Script de démonstration de PyMicMac.
Ce script valide le flux de travail distribué avec Ray et l'optimisation avec PyTorch.
"""

import ray
import torch
import numpy as np
from pymicmac.core.workflow import BundleAdjustmentWorker, extract_tie_points_mock


def generate_synthetic_photogrammetry_data(n_points=100, true_focal_length=1000.0):
    """
    Génère des données synthétiques (points 3D et observations 2D bruitées).
    """
    # 1. Génération de points 3D aléatoires dans le monde
    points_3d = np.random.rand(n_points, 3) * 10

    # 2. Définition de la pose de la caméra (R=Identité, T=0,0,5)
    rotation_matrix = np.eye(3)
    translation_vector = np.array([0.0, 0.0, 5.0])

    # 3. Projection perspective théorique (Caméra parfaite)
    # P_cam = R*P_world + T
    points_camera_space = points_3d + translation_vector

    # x/z, y/z
    x_normalized = points_camera_space[:, 0] / points_camera_space[:, 2]
    y_normalized = points_camera_space[:, 1] / points_camera_space[:, 2]

    # u = f*x, v = f*y
    u_pixels = true_focal_length * x_normalized
    v_pixels = true_focal_length * y_normalized

    observations_2d = np.stack([u_pixels, v_pixels], axis=1)

    # 4. Ajout d'un bruit de mesure (Gaussien de 1 pixel)
    noise = np.random.randn(n_points, 2)
    observations_2d += noise

    return points_3d, observations_2d, rotation_matrix, translation_vector


def run_demo():
    """
    Exécute le workflow complet de démonstration de PyMicMac.
    """
    print("🚀 Initialisation du cluster Ray...")
    # Initialisation en mode local pour la démonstration
    ray.init(local_mode=True)

    print("\n--- ÉTAPE 1 : TAPIOCA (Extraction de points en parallèle) ---")
    image_names = ["IMG_001.JPG", "IMG_002.JPG", "IMG_003.JPG"]
    tapioca_futures = [extract_tie_points_mock.remote(img) for img in image_names]
    tapioca_results = ray.get(tapioca_futures)

    for result in tapioca_results:
        print(f"Image {result['image_id']} : {result['number_of_features']} points de liaison extraits.")

    print("\n--- ÉTAPE 2 : TAPAS (Compensation par faisceaux PyTorch / Ray) ---")
    # Génération de données synthétiques pour une image (Vraie focale = 1000)
    points_3d, observations_2d, rot_init, trans_init = generate_synthetic_photogrammetry_data()

    # Configuration initiale volontairement erronée (Focale = 900)
    initial_config = {
        "focal_length": 900.0,
        "principal_point_x": 0.0,
        "principal_point_y": 0.0
    }

    # Création du worker BundleAdjustment sur Ray
    tapas_worker = BundleAdjustmentWorker.remote("IMG_001.JPG", initial_config)

    # Lancement de l'optimisation asynchrone
    optimization_future = tapas_worker.optimize_camera_pose_and_intrinsics.remote(
        points_3d,
        observations_2d,
        rot_init,
        trans_init
    )

    final_results = ray.get(optimization_future)

    print(f"Résultat Tapas pour {final_results['image_id']} :")
    print(f" - Perte finale (MSE) : {final_results['final_mse_loss']:.4f}")
    print(f" - Focale après optimisation : {final_results['optimized_focal_length']:.2f} (Attendu: ~1000)")

    ray.shutdown()
    print("\n✅ Démo PyMicMac terminée avec succès.")


if __name__ == "__main__":
    run_demo()
