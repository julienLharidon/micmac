import ray
import torch
import numpy as np
from pymicmac.core.workflow import TapasWorker, tapioca_mock

def generate_mock_data(n_points=100):
    """
    Génère des points 3D factices et leurs observations 2D bruitées.
    """
    points_3d = np.random.rand(n_points, 3) * 10
    # Rotation (identité) et Translation (0,0,5)
    rotation = np.eye(3)
    translation = np.array([0, 0, 5])

    # Projection parfaite avec f=1000
    f = 1000.0
    u = f * (points_3d[:, 0] / (points_3d[:, 2] + 5))
    v = f * (points_3d[:, 1] / (points_3d[:, 2] + 5))

    observations = np.stack([u, v], axis=1)
    # Ajout d'un bruit de 1px
    observations += np.random.randn(n_points, 2)

    return points_3d, observations, rotation, translation

def main():
    print("🚀 Initialisation du cluster Ray...")
    ray.init(local_mode=True) # Mode local pour la démo, sinon cluster distant

    print("\n--- ÉTAPE 1 : TAPIOCA (Extraction de points en parallèle) ---")
    images = ["IMG_001.JPG", "IMG_002.JPG", "IMG_003.JPG"]
    futures = [tapioca_mock.remote(img) for img in images]
    results = ray.get(futures)
    for res in results:
        print(f"Image {res['image_id']} : {res['features']} points extraits.")

    print("\n--- ÉTAPE 2 : TAPAS (Compensation par faisceaux PyTorch / Ray) ---")
    # Simulation de données pour une image
    points_3d, observations, rot, trans = generate_mock_data()

    # Paramètres de départ légèrement dégradés (f=900 au lieu de 1000)
    initial_params = {"focal": 900.0, "pp_x": 0.0, "pp_y": 0.0}

    # Création du worker Tapas sur Ray
    tapas_worker = TapasWorker.remote("IMG_001.JPG", initial_params)

    # Lancement de l'optimisation
    result_future = tapas_worker.optimize_pose.remote(points_3d, observations, rot, trans)
    final_res = ray.get(result_future)

    print(f"Résultat Tapas pour {final_res['image_id']} :")
    print(f" - Perte finale (MSE) : {final_res['final_loss']:.4f}")
    print(f" - Focale après optimisation : {final_res['focal']:.2f} (Attendu: ~1000)")

    ray.shutdown()
    print("\n✅ Démo PyMicMac terminée avec succès.")

if __name__ == "__main__":
    main()
