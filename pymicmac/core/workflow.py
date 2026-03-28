import ray
import torch
import time
from .solver import RadialCameraModel, reprojection_loss

@ray.remote
class TapasWorker:
    """
    Worker Ray pour la compensation par faisceaux (Tapas/Martini).
    Chaque worker peut s'occuper d'une partie du bloc ou du bloc entier.
    """
    def __init__(self, image_id, initial_params):
        self.image_id = image_id
        self.model = RadialCameraModel(**initial_params)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1.0)

    def optimize_pose(self, points_3d, observations, rotation_init, translation_init):
        """
        Optimise les paramètres intrinsèques et de pose pour cette image.
        Note: Pour une compensation globale, on utiliserait un acteur centralisé.
        """
        # Conversion en Tenseurs PyTorch
        points_3d = torch.tensor(points_3d, dtype=torch.float32)
        observations = torch.tensor(observations, dtype=torch.float32)
        rotation = torch.tensor(rotation_init, dtype=torch.float32, requires_grad=True)
        translation = torch.tensor(translation_init, dtype=torch.float32, requires_grad=True)

        # Lancement de l'optimisation (500 itérations pour la démo)
        final_loss = 0.0
        for _ in range(500):
            self.optimizer.zero_grad()
            loss = reprojection_loss(self.model, points_3d, observations, rotation, translation)
            loss.backward()
            self.optimizer.step()
            final_loss = loss.item()

        return {
            "image_id": self.image_id,
            "final_loss": final_loss,
            "focal": self.model.focal.item(),
            "pp": self.model.pp.detach().numpy().tolist()
        }

@ray.remote
def tapioca_mock(image_id):
    """
    Simule l'extraction de points (Tapioca).
    """
    print(f"Extraction des points pour {image_id}...")
    time.sleep(1)
    return {"image_id": image_id, "features": 1000}
