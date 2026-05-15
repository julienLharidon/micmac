import torch


class RadialCameraModel(torch.nn.Module):
    def __init__(self, focal=1000.0, pp=(500, 500), k1=0.0):
        super().__init__()
        self.focal = torch.nn.Parameter(torch.tensor(focal))
        self.pp = torch.nn.Parameter(torch.tensor(pp, dtype=torch.float32))
        self.k1 = torch.nn.Parameter(torch.tensor(k1))

    def forward(self, points_3d, r, t):
        # r, t are rotation and translation
        # Project points_3d to 2D
        # Simplified projection for demonstration
        p_cam = points_3d @ r.T + t
        z = p_cam[:, 2:3]
        p_img = p_cam[:, :2] / z

        # Radial distortion
        r2 = torch.sum(p_img**2, dim=1, keepdim=True)
        dist = 1 + self.k1 * r2
        p_img_dist = p_img * dist

        return p_img_dist * self.focal + self.pp

def tapas(model_type, image_set, **kwargs):
    """
    Orientation/Bundle Adjustment (Tapas).
    Uses PyTorch autograd for optimization.
    """
    print(f"Running Tapas with {model_type}")
    # In a real implementation, we would set up the optimization loop here
    # with Camera models and Tie-points.

    # Export legacy XML/DAT
    if kwargs.get("export_legacy"):
        _export_legacy_orientation(image_set)

    return None

def _export_legacy_orientation(image_set):
    print("Exporting legacy orientation files...")
    # Placeholder for XML/DAT export logic
