import time
import subprocess
import os
import torch
import numpy as np
import pandas as pd

def run_legacy(dataset_path):
    print("Running Legacy MicMac...")
    start_time = time.time()
    # Mocking legacy run since we don't have the binaries built in this environment
    # In a real scenario, we would call the compiled MicMac binaries
    # subprocess.run(["mm3d", "Tapioca", "MulScale", ".*.JPG", "500", "1500"], cwd=dataset_path)
    # subprocess.run(["mm3d", "Tapas", "FraserBasic", ".*.JPG", "Out=Arbitrary"], cwd=dataset_path)
    time.sleep(2) # Mock delay
    end_time = time.time()

    # Mock results (localization and orientation)
    legacy_results = {
        "duration": end_time - start_time,
        "poses": {
            "1.JPG": {"pos": [0, 0, 0], "ori": [0, 0, 0]},
            "2.JPG": {"pos": [1, 0, 0], "ori": [0.1, 0, 0]},
        }
    }
    return legacy_results

def run_pymicmac(dataset_path):
    print("Running PyMicMac...")
    start_time = time.time()
    # Call our local wrappers
    subprocess.run(["python3", "tapioca.py", "MulScale", "data/gravillons/Gravillons/*.JPG", "500"])
    subprocess.run(["python3", "tapas.py", "FraserBasic", "data/gravillons/Gravillons/*.JPG", "Out=Benchmark"])
    end_time = time.time()

    results = {"duration": end_time - start_time, "poses": {}}

    # Parse generated XMLs
    ori_dir = "Ori-Benchmark"
    if os.path.exists(ori_dir):
        import xml.etree.ElementTree as ET
        for f in os.listdir(ori_dir):
            if f.endswith(".xml"):
                img_name = f.replace("Orientation-", "").replace(".xml", "")
                tree = ET.parse(os.path.join(ori_dir, f))
                root = tree.getroot()
                pos = eval(root.find("Pos").text)
                ori = eval(root.find("Rot").text)
                results["poses"][img_name] = {"pos": pos, "ori": ori}

    return results

def compare(legacy, pymicmac):
    print("\n--- Benchmark Results ---")
    print(f"Legacy Duration: {legacy['duration']:.2f}s")
    print(f"PyMicMac Duration: {pymicmac['duration']:.2f}s")

    diffs = []
    for img in legacy['poses']:
        p1 = np.array(legacy['poses'][img]['pos'])
        p2 = np.array(pymicmac['poses'][img]['pos'])
        o1 = np.array(legacy['poses'][img]['ori'])
        o2 = np.array(pymicmac['poses'][img]['ori'])

        pos_diff = np.linalg.norm(p1 - p2)
        ori_diff = np.linalg.norm(o1 - o2) # Simplified angular diff

        diffs.append({"image": img, "pos_L2": pos_diff, "ori_diff": ori_diff})

    df = pd.DataFrame(diffs)
    print(df)
    return df

if __name__ == "__main__":
    legacy = run_legacy("data/gravillons/Gravillons")
    pymicmac = run_pymicmac("data/gravillons/Gravillons")
    compare(legacy, pymicmac)
