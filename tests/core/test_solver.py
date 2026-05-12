import pytest
import torch

from pymicmac.core.solver import RadialCameraModel, compute_reprojection_error


def test_camera_projection():
    model = RadialCameraModel(focal_length=1000.0)
    points_3d = torch.tensor([[0.0, 0.0, 5.0]], dtype=torch.float32)
    rot = torch.eye(3)
    trans = torch.zeros(3)

    pixels = model.project_3d_to_2d(points_3d, rot, trans)

    # x_norm = 0/5 = 0, y_norm = 0/5 = 0
    # u = 1000 * 0 + 0 = 0
    # v = 1000 * 0 + 0 = 0
    assert pixels.shape == (1, 2)
    assert torch.allclose(pixels, torch.tensor([[0.0, 0.0]]))

def test_reprojection_error():
    model = RadialCameraModel(focal_length=1000.0)
    points_3d = torch.tensor([[0.1, 0.1, 5.0]], dtype=torch.float32)
    observed = torch.tensor([[25.0, 25.0]], dtype=torch.float32)
    rot = torch.eye(3)
    trans = torch.zeros(3)

    # P_cam = [0.1, 0.1, 5.0]
    # norm = [0.02, 0.02]
    # pixels = [1000*0.02, 1000*0.02] = [20, 20]
    # error = (20-25)^2 + (20-25)^2 = 25 + 25 = 50
    # mean error = 50

    error = compute_reprojection_error(model, points_3d, observed, rot, trans)
    assert pytest.approx(error.item()) == 50.0
