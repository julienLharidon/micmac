import torch

from pymicmac.orientation.tapas import RadialCameraModel, tapas


def test_radial_model():
    model = RadialCameraModel()
    pts = torch.randn(10, 3)
    r = torch.eye(3)
    t = torch.zeros(3)
    out = model(pts, r, t)
    assert out.shape == (10, 2)

def test_tapas_legacy_export():
    # Test with export_legacy=True to cover that branch
    assert tapas("RadialStd", ["im1.jpg"], export_legacy=True) is None
