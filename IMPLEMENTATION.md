# PyMicMac Implementation Status

The following modules and features have been implemented in the `pymicmac` library:

## 1. Core Architecture (`pymicmac/core`)
- **`Camera`**: Base class for camera models, supporting focal length, principal point, distortion, and sensor size.
- **`ImageSet`**: Manages a collection of images, their associated cameras, and tie-points. Integrated with `CameraDatabase`.

## 2. Feature Extraction (`pymicmac/features`)
- **`tapioca`**: Main entry point for tie-point extraction.
    - Distributed processing using **Ray**.
    - Local fallback for single-node execution.
    - Support for classical SIFT descriptors via OpenCV.
    - Plugin architecture placeholder for modern detectors (SuperPoint, LoFTR).
    - **Legacy Export**: Support for MicMac `ExpTxt` (TXT) format for tie-points.
- **`ann` / `pastis`**: Aliases for matching workflows.

## 3. Orientation / Bundle Adjustment (`pymicmac/orientation`)
- **`tapas`**: Entry point for orientation solving.
- **`RadialCameraModel`**: Differentiable camera model implemented in **PyTorch**. Supports radial distortion and focal length optimization via autograd.
- **Legacy Support**: Placeholder for exporting orientation to MicMac XML/DAT formats.

## 4. Dense Matching (`pymicmac/matching`)
- **`malt`**: Distributed dense matching.
    - Tiling strategy for large images.
    - Ray-ready correlation tasks (SGM/MGM placeholder).
    - Workflow for colorized **3D PLY** and **Ortho-image** generation.

## 5. Storage and Cloud-Native Layers (`pymicmac/storage`)
- **`cloud_storage`**: Modern storage using **Apache Parquet**.
- **`LegacyGateway`**: Interface for reading/writing historical MicMac formats.

## 6. Utilities (`pymicmac/utils`)
- **`CameraDatabase`**: Fully functional parser for `DicoCamera.xml`. Allows looking up sensor dimensions by camera model name.

## 7. Quality Assurance and CI/CD
- **`run-CI.sh`**: Local script for comprehensive quality checks.
- **Ruff**: Linting and import sorting.
- **Bandit**: Security scanning (specifically for XML vulnerabilities).
- **Lizard**: Complexity monitoring (CCN < 10, NLOC < 60).
- **Pytest + Coverage**: Unit tests with > 80% coverage (currently 90%).
- **GitHub Action**: Automated CI on push/PR.

## 8. Documentation and Verification
- **`WORKFLOW.md`**: Detailed trace of MicMac v1 command execution.
- **`tests/debug_workflow.py`**: End-to-end debug script using generated sample data.
