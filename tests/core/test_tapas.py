import numpy as np

from pymicmac.core.tapas import run_bundle_adjustment


def test_run_bundle_adjustment():
    points_3d = np.random.rand(10, 3)
    observations_2d = np.random.rand(10, 2)
    rot = np.eye(3)
    trans = np.zeros(3)
    params = {"focal_length": 1000.0}

    result = run_bundle_adjustment("img1", params, points_3d, observations_2d, rot, trans)

    assert result["image_id"] == "img1"
    assert "final_mse_loss" in result
    assert "optimized_focal_length" in result
