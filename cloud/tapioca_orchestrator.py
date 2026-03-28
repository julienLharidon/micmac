#!/usr/bin/env python3
import os
import sys
import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage

# --- Configuration (ENV variables) ---
CLOUD_RUN_WORKER_URL = os.getenv("CLOUD_RUN_WORKER_URL")
BUCKET_NAME = os.getenv("GCS_BUCKET", "micmac-data")

class TapiocaOrchestrator:
    def __init__(self, bucket_name):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)

    def list_images(self, pattern):
        # Scan GCS Bucket
        blobs = self.bucket.list_blobs()
        images = [b.name for b in blobs if b.name.endswith('.tif')] # In a real system, use regex for pattern matching
        return images

    def _call_cloud_run(self, command):
        """Dispatches a command to a Cloud Run worker."""
        if not CLOUD_RUN_WORKER_URL:
            # Fallback to local execution for demo/dev
            print(f"[LOCAL] Executing: {command}")
            return subprocess.run(command, shell=True, check=True)

        print(f"[CLOUD RUN] Dispatching: {command}")
        resp = requests.post(
            CLOUD_RUN_WORKER_URL,
            json={"cmd": command, "bucket": BUCKET_NAME},
            # auth=... # Google Service Account token should be here
        )
        resp.raise_for_status()
        return resp.json()

    def run_mulscale(self, pattern, ss_res, full_res):
        images = self.list_images(pattern)
        print(f"--- Orchestrating MulScale for {len(images)} images ---")

        # 1. Map Phase: Parallel PastDevlop (one per image)
        # Benefit: High CPU parallelization for image rescaling
        with ThreadPoolExecutor(max_workers=20) as executor:
            for img in images:
                cmd = f"mm3d PastDevlop {img} Sz1={ss_res} Sz2={full_res}"
                executor.submit(self._call_cloud_run, cmd)

        # 2. Low-Res Global Match
        # In Tapioca MulScale, low-res images are matched against all others
        # We run this on a single (potentially larger) instance or split it
        low_res_cmd = f"mm3d Pastis . 'NKS-Rel-AllCpleOfPattern@{pattern}' {ss_res} NKS=NKS-Assoc-CplIm2Hom@_SRes@dat"
        self._call_cloud_run(low_res_cmd)

        # 3. High-Res Map-Reduce Phase
        # Decomposing Pastis into individual couples matching is the most efficient cloud approach
        # For simplicity, here we process the high-res step by batch of images
        high_res_cmd = f"mm3d Pastis . 'NKS-Rel-SsECh@{pattern}@2' {full_res} NKS=NKS-Assoc-CplIm2Hom@@dat"
        self._call_cloud_run(high_res_cmd)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: tapioca_orchestrator.py <Mode> <Pattern> [options]")
        sys.exit(1)

    mode = sys.argv[1]
    pattern = sys.argv[2]

    orch = TapiocaOrchestrator(BUCKET_NAME)

    if mode == "MulScale":
        ss_res = int(sys.argv[3]) if len(sys.argv) > 3 else 300
        full_res = int(sys.argv[4]) if len(sys.argv) > 4 else -1
        orch.run_mulscale(pattern, ss_res, full_res)
    else:
        print(f"Mode {mode} not yet supported in this orchestrator.")
