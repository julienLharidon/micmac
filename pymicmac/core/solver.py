"""
Ce module contient le moteur de calcul géométrique pour PyMicMac.
Il implémente les modèles de caméras et les fonctions de perte pour la compensation.
"""

import torch
import torch.nn as nn


class RadialCameraModel(nn.Module):
    """
    Modèle de caméra implémentant la projection perspective avec distorsion radiale.
    Ce modèle est compatible avec les types RadialBasic et RadialStd de MicMac.
    """

    def __init__(self, focal_length=1000.0, principal_point_x=0.0, principal_point_y=0.0, radial_k1=0.0, radial_k2=0.0):
        """
        Initialise les paramètres intrinsèques de la caméra comme paramètres entraînables.
        """
        super().__init__()

        # Paramètres intrinsèques (optimisables)
        self.focal_length = nn.Parameter(torch.tensor(float(focal_length)))
        self.principal_point = nn.Parameter(torch.tensor([float(principal_point_x), float(principal_point_y)]))
        self.radial_distortion_coeffs = nn.Parameter(torch.tensor([float(radial_k1), float(radial_k2)]))

    def project_3d_to_2d(self, points_3d, rotation_matrix, translation_vector):
        """
        Projette un nuage de points 3D vers le plan image (pixels).

        Args:
            points_3d (Tensor): Coordonnées 3D dans le repère monde [N, 3].
            rotation_matrix (Tensor): Matrice de rotation de la caméra [3, 3].
            translation_vector (Tensor): Vecteur de translation de la caméra [3].

        Returns:
            Tensor: Coordonnées 2D projetées en pixels [N, 2].
        """
        # 1. Transformation du repère monde vers le repère caméra (P_cam = R*P_world + T)
        points_camera_space = torch.matmul(rotation_matrix, points_3d.T).T + translation_vector

        # 2. Projection perspective sur le plan normalisé (z=1)
        # On évite la division par zéro en ajoutant un petit epsilon
        z_coords = points_camera_space[:, 2].unsqueeze(1)
        normalized_coords = points_camera_space[:, :2] / (z_coords + 1e-8)

        x_norm = normalized_coords[:, 0]
        y_norm = normalized_coords[:, 1]

        # 3. Application du modèle de distorsion radiale polynomiale
        # r^2 = x^2 + y^2
        radius_squared = x_norm**2 + y_norm**2
        distortion_factor = (
            1
            + self.radial_distortion_coeffs[0] * radius_squared
            + self.radial_distortion_coeffs[1] * (radius_squared**2)
        )

        x_distorted = x_norm * distortion_factor
        y_distorted = y_norm * distortion_factor

        # 4. Passage du plan image normalisé aux pixels (Matrice K)
        u_pixels = self.focal_length * x_distorted + self.principal_point[0]
        v_pixels = self.focal_length * y_distorted + self.principal_point[1]

        return torch.stack([u_pixels, v_pixels], dim=1)


def compute_reprojection_error(camera_model, points_3d, observed_pixels, rotation_matrix, translation_vector):
    """
    Calcule l'erreur quadratique moyenne de reprojection (MSE).

    Cette fonction est utilisée comme fonction de coût (Loss) pour l'optimisation.
    """
    # Projection des points 3D via le modèle courant
    projected_pixels = camera_model.project_3d_to_2d(points_3d, rotation_matrix, translation_vector)

    # Calcul de la distance euclidienne carrée entre projection et observation
    squared_errors = torch.sum((projected_pixels - observed_pixels)**2, dim=1)

    return torch.mean(squared_errors)
