import torch
import torch.nn as nn

class RadialCameraModel(nn.Module):
    """
    Standard Radial Camera Model (MicMac RadialStd parity).
    Projects 3D points in camera coordinates to 2D image coordinates.
    """
    def __init__(self, focal=1.0, pp=(0.0, 0.0), k1=0.0, k2=0.0, k3=0.0):
        super().__init__()
        self.focal = nn.Parameter(torch.tensor(float(focal)))
        self.pp = nn.Parameter(torch.tensor(pp, dtype=torch.float32))
        self.k = nn.Parameter(torch.tensor([k1, k2, k3], dtype=torch.float32))

    def project(self, points_3d: torch.Tensor) -> torch.Tensor:
        """
        Args:
            points_3d: Tensor of shape (N, 3) in camera coordinates.
        Returns:
            points_2d: Tensor of shape (N, 2) in image coordinates.
        """
        # Normalized coordinates
        z = points_3d[:, 2:3]
        xy = points_3d[:, :2] / z

        # Radial distortion
        r2 = torch.sum(xy**2, dim=1, keepdim=True)
        radial = 1.0 + self.k[0] * r2 + self.k[1] * r2**2 + self.k[2] * r2**3

        xy_dist = xy * radial

        # Projection
        uv = xy_dist * self.focal + self.pp
        return uv
