# PyMicMac User Guide

PyMicMac is a cloud-native refactor of the MicMac legacy photogrammetry software, optimized for GCP and distributed computing via Ray.

## Installation

```bash
pip install -r requirements.txt
```

## Running Tapioca (Tie-points)

PyMicMac supports legacy MicMac syntax for tie-point generation:

```bash
python3 tapioca.py MulScale "data/gravillons/Gravillons/*.JPG" 500
```

## Running Tapas (Orientation)

```bash
python3 tapas.py FraserBasic "data/gravillons/Gravillons/*.JPG" Out=Arbitrary
```

## Benchmarking

To compare PyMicMac results with the original MicMac:

```bash
python3 bench/benchmark.py
```

This will output localization (L2) and orientation differences between the two versions.
