import torch
import pytest
from pymicmac.core.base import RadialCameraModel

def test_radial_camera_projection():
    # Focal 1000, Principal Point (500, 500)
    # No distortion initially
    model = RadialCameraModel(focal=1000.0, pp=(500.0, 500.0), k1=0.0, k2=0.0)

    # 3D point in camera coords (X, Y, Z)
    p3d = torch.tensor([[0.0, 0.0, 10.0], [1.0, 1.0, 10.0]], dtype=torch.float32)

    # Projected:
    # [0, 0, 10] -> [0/10, 0/10] * 1000 + 500 = [500, 500]
    # [1, 1, 10] -> [1/10, 1/10] * 1000 + 500 = [600, 600]
    p2d = model.project(p3d)

    assert torch.allclose(p2d[0], torch.tensor([500.0, 500.0]))
    assert torch.allclose(p2d[1], torch.tensor([600.0, 600.0]))

def test_radial_distortion():
    # k1 = 0.1
    model = RadialCameraModel(focal=1000.0, pp=(500.0, 500.0), k1=0.1, k2=0.0)
    p3d = torch.tensor([[1.0, 0.0, 10.0]], dtype=torch.float32)

    # x = 1/10 = 0.1, y = 0
    # r2 = 0.01
    # distortion = (1 + 0.1 * 0.01) = 1.001
    # x_dist = 0.1 * 1.001 = 0.1001
    # p2d = 0.1001 * 1000 + 500 = 600.1
    p2d = model.project(p3d)

    assert torch.allclose(p2d[0, 0], torch.tensor(600.1))
    assert torch.allclose(p2d[0, 1], torch.tensor(500.0))

def test_autograd_camera():
    model = RadialCameraModel(focal=1000.0, pp=(500.0, 500.0))
    model.focal.requires_grad = True

    p3d = torch.tensor([[1.0, 1.0, 10.0]], dtype=torch.float32)
    p2d = model.project(p3d)

    loss = p2d.sum()
    loss.backward()

    assert model.focal.grad is not None
    assert model.focal.grad != 0
