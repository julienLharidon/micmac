import cv2
import numpy as np
import ray

from pymicmac.features.tapioca import tapioca


def test_tapioca_ray(tmp_path):
    img_path = str(tmp_path / "test_ray.tif")
    cv2.imwrite(img_path, np.random.randint(0, 255, (100, 100), dtype=np.uint8))

    # Initialize ray if not done
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)

    res = tapioca([img_path], resolution=100, use_ray=True)
    assert len(res) == 1
    assert len(res[0]) >= 0
