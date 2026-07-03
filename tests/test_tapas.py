import torch
import pytest
from pymicmac.core.tapas import BundleAdjustment

def test_ba_optimization():
    # Simple setup: 2 cameras, 1 point
    # Camera 1 at origin, Camera 2 at (1, 0, 0)
    # Point at (0, 0, 10)

    # In reality, we'd have many points and noisy initial estimates
    ba = BundleAdjustment(num_cameras=2, num_points=1)

    # Mock some observations
    # cam_idx, point_idx, u, v
    obs = torch.tensor([
        [0, 0, 500.0, 500.0],
        [1, 0, 400.0, 500.0]
    ], dtype=torch.float32)

    # Run one step of optimization
    initial_loss = ba.compute_loss(obs)
    ba.optimize_step(obs)
    final_loss = ba.compute_loss(obs)

    assert final_loss < initial_loss

def test_run_tapas_integration():
    from pymicmac.core.tapas import run_tapas
    import os
    # Mock some homol data
    os.makedirs("Homol/Pastis1.JPG", exist_ok=True)
    with open("Homol/Pastis1.JPG/2.JPG.txt", "w") as f:
        # x1 y1 x2 y2
        f.write("500.0 500.0 400.0 500.0\n")

    # Create mock images list
    with open("1.JPG", "w") as f: f.write("")
    with open("2.JPG", "w") as f: f.write("")

    try:
        res = run_tapas("FraserBasic", "[1-2].JPG", "TestOut")
        assert res["status"] == "success"
        assert os.path.exists("Ori-TestOut")
    finally:
        import shutil
        if os.path.exists("Homol"): shutil.rmtree("Homol")
        if os.path.exists("Ori-TestOut"): shutil.rmtree("Ori-TestOut")
        if os.path.exists("1.JPG"): os.remove("1.JPG")
        if os.path.exists("2.JPG"): os.remove("2.JPG")
