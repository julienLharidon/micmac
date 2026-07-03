#!/usr/bin/env python3
import sys
import argparse
from pymicmac.core.tapas import run_tapas

def main():
    parser = argparse.ArgumentParser(description="PyMicMac Tapas (Orientation)")
    parser.add_argument("mode", help="Orientation mode (e.g., FraserBasic)")
    parser.add_argument("pattern", help="Image pattern")
    parser.add_argument("args", nargs="*", help="Additional arguments")

    args = parser.parse_args()

    out_name = "Arbitrary"
    for arg in args.args:
        if arg.startswith("Out="):
            out_name = arg.split("=")[1]

    print(f"Running Tapas in mode {args.mode} on {args.pattern}")
    result = run_tapas(args.mode, args.pattern, out_name)
    print(f"Orientation saved to {result['orientation']}")

if __name__ == "__main__":
    main()
