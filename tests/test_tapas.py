import torch

from pymicmac.orientation.tapas import (
    BundleAdjustment,
    RadialCameraModel,
    batch_rodrigues_to_rotation_matrix,
    tapas,
)


def test_radial_model():
    model = RadialCameraModel()
    pts = torch.randn(10, 3)
    r_mats = torch.eye(3).expand(10, 3, 3)
    t_vecs = torch.zeros(10, 3)
    out = model(pts, r_mats, t_vecs)
    assert out.shape == (10, 2)

def test_tapas_legacy_export():
    assert tapas("RadialStd", ["im1.jpg"], export_legacy=True) is None

def test_batch_rodrigues():
    v = torch.randn(5, 3)
    R = batch_rodrigues_to_rotation_matrix(v)
    assert R.shape == (5, 3, 3)
    v0 = torch.zeros(1, 3)
    R0 = batch_rodrigues_to_rotation_matrix(v0)
    assert torch.allclose(R0, torch.eye(3).unsqueeze(0))

def test_bundle_adjustment_pytorch():
    num_cameras = 2
    num_points = 5
    gt_r_vecs = torch.zeros(num_cameras, 3)
    gt_t_vecs = torch.tensor([[0., 0., 5.], [0.5, 0., 5.]])
    gt_points_3d = torch.tensor([
        [0., 0., 0.], [0.1, 0., 0.], [0., 0.1, 0.], [-0.1, 0., 0.], [0., -0.1, 0.]
    ])

    cam_idx = []
    point_idx = []

    model_gt = BundleAdjustment(num_cameras, num_points)
    with torch.no_grad():
        model_gt.r_vecs.copy_(gt_r_vecs)
        model_gt.t_vecs.copy_(gt_t_vecs)
        model_gt.points_3d.copy_(gt_points_3d)

        for c in range(num_cameras):
            for p in range(num_points):
                cam_idx.append(c)
                point_idx.append(p)

        obs_cam_idx = torch.tensor(cam_idx, dtype=torch.long)
        obs_point_idx = torch.tensor(point_idx, dtype=torch.long)
        points_2d = model_gt(obs_cam_idx, obs_point_idx)

    obs = {
        'cam_idx': cam_idx,
        'point_idx': point_idx,
        'points_2d': points_2d.tolist()
    }

    optimized_model = tapas("RadialStd", None, observations=obs, num_iterations=200)

    with torch.no_grad():
        final_predicted = optimized_model(obs_cam_idx, obs_point_idx)
        final_loss = torch.nn.functional.mse_loss(final_predicted, points_2d)
        assert final_loss.item() < 100.0

def test_tapas_ceres():
    obs = {
        'cam_idx': [0, 0, 1, 1],
        'point_idx': [0, 1, 0, 1],
        'points_2d': [[500, 500], [510, 500], [490, 500], [500, 500]]
    }
    # Test that Ceres solver doesn't crash
    # Optimization might be slow or need more iterations for real accuracy
    res = tapas("RadialStd", None, observations=obs, solver="ceres")
    assert res is not None
    assert 'r_vecs' in res
