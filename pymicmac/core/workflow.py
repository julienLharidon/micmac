"""
Ce module gère l'orchestration distribuée des tâches PyMicMac via Ray.
Il définit les acteurs pour l'extraction de points et la compensation par faisceaux.
"""

import ray

from .tapas import run_bundle_adjustment
from .tapioca import extract_tie_points


@ray.remote
class BundleAdjustmentWorker:
    """
    Acteur Ray responsable de la compensation par faisceaux.
    """

    def __init__(self, image_id, initial_parameters_dict):
        self.image_id = image_id
        self.initial_parameters = initial_parameters_dict

    def optimize_camera_pose_and_intrinsics(self, points_3d, obs_2d, rot_init, trans_init):
        return run_bundle_adjustment(
            self.image_id,
            self.initial_parameters,
            points_3d,
            obs_2d,
            rot_init,
            trans_init
        )

@ray.remote
def extract_tie_points_ray(image_id):
    """
    Version Ray de l'extraction de points de liaison.
    """
    return extract_tie_points(image_id)

# Pour maintenir la compatibilité avec demo_pymicmac.py si nécessaire
extract_tie_points_mock = extract_tie_points_ray
