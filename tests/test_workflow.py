import os

import cv2
import numpy as np

from pymicmac.features.tapioca import export_legacy_txt, tapioca
from pymicmac.matching.malt import malt
from pymicmac.orientation.tapas import tapas


def test_tapioca(tmp_path):
    img_path = str(tmp_path / "test.tif")
    cv2.imwrite(img_path, np.random.randint(0, 255, (100, 100), dtype=np.uint8))

    res = tapioca([img_path], resolution=100)
    assert len(res) == 1
    assert len(res[0]) >= 0

def test_export_legacy(tmp_path):
    img_path = str(tmp_path / "test.tif")
    pts = [((10, 10), [0.1]*128)]
    export_legacy_txt([pts], [img_path])
    assert os.path.exists(img_path + ".txt")

def test_tapas():
    # Mainly checks it doesn't crash as it's a placeholder
    assert tapas("RadialStd", ["im1.jpg"]) is None

def test_malt():
    # Mainly checks it doesn't crash as it's a placeholder
    assert malt("Ortho", ["im1.jpg"]) is None
