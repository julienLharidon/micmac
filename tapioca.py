#!/usr/bin/env python3
import sys
import argparse
import ray
from pymicmac.core.tapioca import run_tapioca

def main():
    parser = argparse.ArgumentParser(description="PyMicMac Tapioca (Tie-points generation)")
    parser.add_argument("mode", help="Matching mode (e.g., MulScale)")
    parser.add_argument("pattern", help="Image pattern")
    parser.add_argument("args", nargs="*", help="Additional arguments (scale, etc.)")

    args = parser.parse_args()

    # Initialize Ray locally if not already connected to a cluster
    # Use RAY_ADDRESS env var to connect to a remote cluster
    if not ray.is_initialized():
        import os
        address = os.environ.get("RAY_ADDRESS")
        if address:
            print(f"Connecting to Ray at {address}...")
            ray.init(address=address)
        else:
            ray.init()

    print(f"Running Tapioca in mode {args.mode} on {args.pattern}")
    results = run_tapioca(args.pattern, args.args[0] if args.args else 1000)
    print(f"Matched {len(results)} pairs.")

if __name__ == "__main__":
    main()
