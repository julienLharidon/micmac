"""
Ce module gère l'orchestration distribuée des tâches PyMicMac via Ray.
Il définit les acteurs pour l'extraction de points et la compensation par faisceaux.
"""

import ray
import torch
import time
from .solver import RadialCameraModel, compute_reprojection_error


@ray.remote
class BundleAdjustmentWorker:
    """
    Acteur Ray responsable de la compensation par faisceaux (Tapas / Martini).
    Chaque worker gère l'optimisation des paramètres pour une ou plusieurs images.
    """

    def __init__(self, image_id, initial_parameters_dict):
        """
        Initialise le modèle de caméra et l'optimiseur.
        """
        self.image_id = image_id

        # Initialisation du modèle géométrique avec les valeurs de départ
        self.camera_model = RadialCameraModel(
            focal_length=initial_parameters_dict.get("focal_length", 1000.0),
            principal_point_x=initial_parameters_dict.get("principal_point_x", 0.0),
            principal_point_y=initial_parameters_dict.get("principal_point_y", 0.0)
        )

        # Choix de l'optimiseur (Adam pour la robustesse en démo)
        self.optimizer = torch.optim.Adam(self.camera_model.parameters(), lr=1.0)

    def optimize_camera_pose_and_intrinsics(self, points_3d, observations_2d, rotation_matrix_init, translation_vector_init):
        """
        Exécute une boucle d'optimisation pour minimiser l'erreur de reprojection.
        """
        # Conversion des entrées NumPy en tenseurs PyTorch
        points_3d_tensor = torch.tensor(points_3d, dtype=torch.float32)
        observations_2d_tensor = torch.tensor(observations_2d, dtype=torch.float32)

        # La pose (extrinsèques) est également optimisée
        rotation_tensor = torch.tensor(rotation_matrix_init, dtype=torch.float32, requires_grad=True)
        translation_tensor = torch.tensor(translation_vector_init, dtype=torch.float32, requires_grad=True)

        final_loss_value = 0.0

        # Boucle d'optimisation (500 itérations)
        for _ in range(500):
            self.optimizer.zero_grad()

            # Calcul de la fonction de coût
            loss = compute_reprojection_error(
                self.camera_model,
                points_3d_tensor,
                observations_2d_tensor,
                rotation_tensor,
                translation_tensor
            )

            # Rétropropagation et mise à jour
            loss.backward()
            self.optimizer.step()

            final_loss_value = loss.item()

        # Retourne les résultats optimisés sous forme de dictionnaire JSON-compatible
        return {
            "image_id": self.image_id,
            "final_mse_loss": final_loss_value,
            "optimized_focal_length": self.camera_model.focal_length.item(),
            "optimized_principal_point": self.camera_model.principal_point.detach().numpy().tolist()
        }


@ray.remote
def extract_tie_points_mock(image_id):
    """
    Simulation asynchrone de l'extraction de points de liaison (Tapioca).
    """
    print(f"Extraction des points de liaison pour {image_id}...")

    # Simule un temps de calcul (extraction SIFT/Digeo)
    time.sleep(1)

    return {
        "image_id": image_id,
        "number_of_features": 1000
    }
