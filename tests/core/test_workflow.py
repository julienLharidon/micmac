import numpy as np
import pytest
import ray

from pymicmac.core.workflow import BundleAdjustmentWorker, extract_tie_points_ray


@pytest.fixture(scope="module")
def ray_fix():
    ray.init(ignore_reinit_error=True)
    yield
    ray.shutdown()

def test_extract_tie_points_ray(ray_fix):
    future = extract_tie_points_ray.remote("test_ray.tif")
    result = ray.get(future)
    assert result["image_id"] == "test_ray.tif"
    assert result["number_of_features"] == 1000

def test_bundle_adjustment_worker(ray_fix):
    points_3d = np.random.rand(10, 3)
    observations_2d = np.random.rand(10, 2)
    rot = np.eye(3)
    trans = np.zeros(3)
    params = {"focal_length": 1000.0}

    worker = BundleAdjustmentWorker.remote("img_ray", params)
    future = worker.optimize_camera_pose_and_intrinsics.remote(points_3d, observations_2d, rot, trans)
    result = ray.get(future)

    assert result["image_id"] == "img_ray"
    assert "final_mse_loss" in result
