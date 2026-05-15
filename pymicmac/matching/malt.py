import numpy as np
import ray


@ray.remote
def correlate_tile(tile1, tile2):
    """Placeholder for SGM/MGM correlation on a tile."""
    # Semi-Global Matching logic here
    return np.zeros(tile1.shape[:2])

def malt(mode, image_set, **kwargs):
    """
    Dense Matching (Malt).
    Distributed correlation using Ray.
    """
    print(f"Running Malt in {mode} mode")

    # Implementation:
    # 1. Tiling of images
    # 2. Parallel correlation (SGM/MGM) via Ray
    # 3. Disparity to 3D point cloud (PLY)
    # 4. Ortho-rectification

    if kwargs.get("ply"):
        _generate_ply(image_set)

    if mode == "Ortho":
        _generate_ortho(image_set)

    return None

def _generate_ply(image_set):
    print("Generating colorized 3D PLY...")

def _generate_ortho(image_set):
    print("Generating Ortho-image...")
