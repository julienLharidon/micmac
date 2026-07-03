import pytest
import os
import cv2
import numpy as np
from pymicmac.core.tapioca import extract_features, match_pair

def test_feature_extraction():
    # Create a dummy image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img, (50, 50), 10, (255, 255, 255), -1)
    img_path = "test_img.jpg"
    cv2.imwrite(img_path, img)

    try:
        keypoints, descriptors = extract_features(img_path)
        assert len(keypoints) > 0
        assert descriptors.shape[0] == len(keypoints)
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

def test_matching():
    # Create two dummy images with same content
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img, (50, 50), 10, (255, 255, 255), -1)
    cv2.imwrite("img1.jpg", img)
    cv2.imwrite("img2.jpg", img)

    try:
        kp1, desc1 = extract_features("img1.jpg")
        kp2, desc2 = extract_features("img2.jpg")

        matches = match_pair(desc1, desc2)
        assert len(matches) > 0

        # Test distributed run
        from pymicmac.core.tapioca import run_tapioca
        import ray
        if not ray.is_initialized():
            ray.init(num_cpus=1)
        results = run_tapioca("img*.jpg", 500)
        assert len(results) > 0
    finally:
        for f in ["img1.jpg", "img2.jpg"]:
            if os.path.exists(f):
                os.remove(f)
