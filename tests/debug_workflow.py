import os

import cv2
import numpy as np

import pymicmac


def create_dummy_tifs(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    for i in range(3):
        img = np.random.randint(0, 255, (512, 512), dtype=np.uint8)
        cv2.imwrite(os.path.join(data_dir, f"test_{i}.tif"), img)

def debug_workflow():
    data_dir = "data"
    create_dummy_tifs(data_dir)

    image_paths = [os.path.join(data_dir, f"test_{i}.tif") for i in range(3)]

    print("--- Testing Tapioca (Tie-points) ---")
    pymicmac.tapioca(image_paths, resolution=500, exp_txt=True)

    print("\n--- Testing Tapas (Orientation) ---")
    pymicmac.tapas("RadialStd", image_paths)

    print("\n--- Testing Malt (Dense Matching) ---")
    pymicmac.malt("Ortho", image_paths, ply=True)

if __name__ == "__main__":
    debug_workflow()
