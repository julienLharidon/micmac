import torch
import torch.nn as nn

class RadialCameraModel(nn.Module):
    """
    Modèle de caméra avec distorsion radiale (RadialBasic / RadialStd)
    """
    def __init__(self, focal=1000.0, pp_x=0.0, pp_y=0.0, r1=0.0, r2=0.0):
        super().__init__()
        self.focal = nn.Parameter(torch.tensor(float(focal)))
        self.pp = nn.Parameter(torch.tensor([float(pp_x), float(pp_y)]))
        self.radial = nn.Parameter(torch.tensor([float(r1), float(r2)]))

    def project(self, points_3d, rotation, translation):
        """
        Projette des points 3D (caméra-space) vers le plan image avec distorsion.
        """
        # 1. Transformation rigide (R*P + T)
        p_cam = torch.matmul(rotation, points_3d.T).T + translation

        # 2. Projection perspective
        x = p_cam[:, 0] / p_cam[:, 2]
        y = p_cam[:, 1] / p_cam[:, 2]

        # 3. Application de la distorsion radiale
        r2 = x**2 + y**2
        dist = 1 + self.radial[0] * r2 + self.radial[1] * (r2**2)

        x_dist = x * dist
        y_dist = y * dist

        # 4. Passage en pixels (Intrinsèques)
        u = self.focal * x_dist + self.pp[0]
        v = self.focal * y_dist + self.pp[1]

        return torch.stack([u, v], dim=1)

def reprojection_loss(model, points_3d, observations, rotation, translation):
    """
    Erreur de reprojection (Moindres carrés)
    """
    projected = model.project(points_3d, rotation, translation)
    return torch.mean(torch.sum((projected - observations)**2, dim=1))
