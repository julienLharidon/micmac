import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from pymicmac.core.base import RadialCameraModel

class BundleAdjustment(nn.Module):
    def __init__(self, num_cameras, num_points):
        super().__init__()
        # Simplified: All cameras share the same RadialStd model for now
        self.camera_model = RadialCameraModel(focal=1000.0, pp=(500.0, 500.0))

        # Camera poses: Translation (T) and Rotation (R as Euler angles)
        self.cam_rot = nn.Parameter(torch.zeros((num_cameras, 3)))
        self.cam_pos = nn.Parameter(torch.zeros((num_cameras, 3)))
        # Initialize second camera slightly offset
        with torch.no_grad():
            self.cam_pos[1, 0] = 0.1

        # 3D Points
        p_init = torch.randn((num_points, 3)) * 0.1 + torch.tensor([0, 0, 10.0])
        self.points_3d = nn.Parameter(p_init)

        self.optimizer = optim.Adam(self.parameters(), lr=0.01)

    def rotate_point(self, p, angles):
        # Very simple Euler rotation for MVP
        # angles: (N, 3)
        c = torch.cos(angles)
        s = torch.sin(angles)
        cx, cy, cz = c[:, 0], c[:, 1], c[:, 2]
        sx, sy, sz = s[:, 0], s[:, 1], s[:, 2]

        # R = Rz * Ry * Rx (simplified)
        x, y, z = p[:, 0], p[:, 1], p[:, 2]

        # Rx
        y_new = y * cx - z * sx
        z_new = y * sx + z * cx
        y, z = y_new, z_new

        # Ry
        x_new = x * cy + z * sy
        z_new = -x * sy + z * cy
        x, z = x_new, z_new

        # Rz
        x_final = x * cz - y * sz
        y_final = x * sz + y * cz

        return torch.stack([x_final, y_final, z], dim=1)

    def compute_loss(self, observations):
        """
        observations: (N, 4) -> cam_idx, pt_idx, u, v
        """
        cam_indices = observations[:, 0].long()
        pt_indices = observations[:, 1].long()
        target_uv = observations[:, 2:]

        pts = self.points_3d[pt_indices]

        # Transform to camera coords
        # P_cam = R * (P_world - T)
        rel_pts = pts - self.cam_pos[cam_indices]
        pts_cam = self.rotate_point(rel_pts, self.cam_rot[cam_indices])

        proj_uv = self.camera_model.project(pts_cam)

        return torch.mean((proj_uv - target_uv)**2)

    def optimize_step(self, observations):
        self.optimizer.zero_grad()
        loss = self.compute_loss(observations)
        loss.backward()
        self.optimizer.step()
        return loss.item()

def load_homol_legacy(img1_path, img2_path):
    base1 = os.path.basename(img1_path)
    base2 = os.path.basename(img2_path)
    homol_path = f"Homol/Pastis{base1}/{base2}.txt"
    if not os.path.exists(homol_path):
        return None
    return np.loadtxt(homol_path)

def run_tapas(mode, pattern, out_name):
    import glob
    images = sorted(glob.glob(pattern))
    num_cams = len(images)

    # Simple observation collection
    obs_list = []
    for i in range(num_cams):
        for j in range(i + 1, num_cams):
            pts = load_homol_legacy(images[i], images[j])
            if pts is not None:
                # pts: x1, y1, x2, y2
                if pts.ndim == 1:
                    pts = pts.reshape(1, -1)
                for k in range(len(pts)):
                    obs_list.append([i, k, pts[k, 0], pts[k, 1]])
                    obs_list.append([j, k, pts[k, 2], pts[k, 3]])

    if not obs_list:
        print("No observations found in Homol/ directory.")
        return {"status": "failure", "orientation": out_name}

    obs = torch.tensor(obs_list, dtype=torch.float32)
    num_pts = int(obs[:, 1].max().item()) + 1

    ba = BundleAdjustment(num_cams, num_pts)
    print(f"Optimizing {num_cams} cameras and {num_pts} points...")

    for step in range(50):
        loss = ba.optimize_step(obs)
        if step % 10 == 0:
            print(f"Step {step}, Loss: {loss:.4f}")

    # Save orientation (Simplified)
    out_dir = f"Ori-{out_name}"
    os.makedirs(out_dir, exist_ok=True)
    for i, img in enumerate(images):
        img_base = os.path.basename(img)
        out_path = os.path.join(out_dir, f"Orientation-{img_base}.xml")
        with open(out_path, "w") as f:
            pos_str = ba.cam_pos[i].tolist()
            rot_str = ba.cam_rot[i].tolist()
            f.write(f"<Orientation>\n<Pos>{pos_str}</Pos>\n")
            f.write(f"<Rot>{rot_str}</Rot>\n</Orientation>")

    return {"status": "success", "orientation": out_name}
