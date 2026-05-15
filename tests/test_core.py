from pymicmac.core.base import Camera, ImageSet


def test_camera_init():
    cam = Camera(focal_length=1000)
    assert cam.focal_length == 1000

def test_image_set():
    imgs = ImageSet(["im1.jpg", "im2.jpg"])
    assert len(imgs) == 2
