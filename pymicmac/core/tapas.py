"""
Module pour la compensation par faisceaux (Tapas).
"""
import torch

from .solver import RadialCameraModel, compute_reprojection_error


def run_bundle_adjustment(image_id, initial_parameters, points_3d, observations_2d, rot_init, trans_init):
    """
    Exécute l'optimisation locale pour une image.
    """
    camera_model = RadialCameraModel(
        focal_length=initial_parameters.get("focal_length", 1000.0),
        principal_point_x=initial_parameters.get("principal_point_x", 0.0),
        principal_point_y=initial_parameters.get("principal_point_y", 0.0)
    )

    optimizer = torch.optim.Adam(camera_model.parameters(), lr=1.0)

    points_3d_tensor = torch.tensor(points_3d, dtype=torch.float32)
    observations_2d_tensor = torch.tensor(observations_2d, dtype=torch.float32)
    rotation_tensor = torch.tensor(rot_init, dtype=torch.float32, requires_grad=True)
    translation_tensor = torch.tensor(trans_init, dtype=torch.float32, requires_grad=True)

    final_loss_value = 0.0
    for _ in range(500):
        optimizer.zero_grad()
        loss = compute_reprojection_error(
            camera_model,
            points_3d_tensor,
            observations_2d_tensor,
            rotation_tensor,
            translation_tensor
        )
        loss.backward()
        optimizer.step()
        final_loss_value = loss.item()

    return {
        "image_id": image_id,
        "final_mse_loss": final_loss_value,
        "optimized_focal_length": camera_model.focal_length.item(),
        "optimized_principal_point": camera_model.principal_point.detach().numpy().tolist()
    }
