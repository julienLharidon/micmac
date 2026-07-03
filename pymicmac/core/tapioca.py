import cv2
import os
import numpy as np
import ray


def extract_features(image_path):
    """
    Extract SIFT features from an image.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)

    # Convert keypoints to numpy array for serialization
    kp_array = np.array([kp.pt for kp in keypoints], dtype=np.float32)
    return kp_array, descriptors

def match_pair(desc1, desc2):
    """
    Match two sets of descriptors.
    """
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(desc1, desc2)

    # Extract match indices
    match_indices = np.array([[m.queryIdx, m.trainIdx] for m in matches])
    return match_indices

@ray.remote
def process_pair(img_path1, img_path2):
    """
    Ray task to extract and match a pair of images.
    """
    kp1, desc1 = extract_features(img_path1)
    kp2, desc2 = extract_features(img_path2)
    matches = match_pair(desc1, desc2)
    return {
        "img1": img_path1,
        "img2": img_path2,
        "kp1": kp1,
        "kp2": kp2,
        "matches": matches
    }

def save_homol_legacy(img1_path, img2_path, kp1, kp2, matches):
    """
    Save matches in legacy MicMac Homol format (simplified).
    Homol/PastisImg1/Img2.dat
    """
    base1 = os.path.basename(img1_path)
    base2 = os.path.basename(img2_path)
    homol_dir = f"Homol/Pastis{base1}"
    os.makedirs(homol_dir, exist_ok=True)

    out_path = os.path.join(homol_dir, f"{base2}.txt")
    with open(out_path, "w") as f:
        for m in matches:
            p1 = kp1[m[0]]
            p2 = kp2[m[1]]
            f.write(f"{p1[0]} {p1[1]} {p2[0]} {p2[1]}\n")

def run_tapioca(image_pattern, scale):
    """
    Main entry point for distributed Tapioca.
    """
    import glob
    images = sorted(glob.glob(image_pattern))

    results_refs = []
    # All-to-all matching (simplified for legacy parity 'MulScale')
    for i in range(len(images)):
        for j in range(i + 1, len(images)):
            results_refs.append(process_pair.remote(images[i], images[j]))

    results = ray.get(results_refs)

    for res in results:
        save_homol_legacy(
            res["img1"], res["img2"], res["kp1"], res["kp2"], res["matches"]
        )

    return results
