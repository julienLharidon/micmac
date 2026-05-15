
import cv2
import ray


def _extract_local(image_path, method="sift"):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    if method == "sift":
        detector = cv2.SIFT_create()
    else:
        raise NotImplementedError(f"Method {method} not implemented")

    keypoints, descriptors = detector.detectAndCompute(img, None)
    return [(kp.pt, desc) for kp, desc in zip(keypoints, descriptors)]

@ray.remote
def extract_features_task(image_path, method="sift"):
    return _extract_local(image_path, method)

def export_legacy_txt(results, image_paths):
    """Export tie-points to legacy MicMac ExpTxt format."""
    for path, pts in zip(image_paths, results):
        txt_path = path + ".txt"
        with open(txt_path, "w") as f:
            for pt, desc in pts:
                desc_str = ' '.join(map(str, desc))
                f.write(f"{pt[0]} {pt[1]} {desc_str}\n")

def tapioca(image_paths, resolution=1000, method="sift", use_ray=False, **kwargs):
    """
    Tie-point extraction (Tapioca).
    """
    if use_ray:
        if not ray.is_initialized():
            ray.init()
        futures = [extract_features_task.remote(p, method) for p in image_paths]
        results = ray.get(futures)
    else:
        results = [_extract_local(p, method) for p in image_paths]

    # Export to legacy format if requested
    if kwargs.get("exp_txt"):
        export_legacy_txt(results, image_paths)

    return results

def ann():
    pass

def pastis():
    pass
