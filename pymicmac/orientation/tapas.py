import torch


def rodrigues_to_rotation_matrix(v):
    """
    Convert a rotation vector (Rodrigues parameters) to a rotation matrix.
    v: (3,) tensor
    """
    theta = torch.norm(v)
    if theta < 1e-6:
        return torch.eye(3, device=v.device, dtype=v.dtype)

    k = v / theta
    k_cross = torch.zeros((3, 3), device=v.device, dtype=v.dtype)
    k_cross[0, 1] = -k[2]
    k_cross[0, 2] = k[1]
    k_cross[1, 0] = k[2]
    k_cross[1, 2] = -k[0]
    k_cross[2, 0] = -k[1]
    k_cross[2, 1] = k[0]

    # Rodrigues' rotation formula
    R = torch.eye(3, device=v.device, dtype=v.dtype) + \
        torch.sin(theta) * k_cross + \
        (1 - torch.cos(theta)) * (k_cross @ k_cross)
    return R


def batch_rodrigues_to_rotation_matrix(v):
    """
    v: (N, 3) tensor
    """
    # Vectorized Rodrigues implementation
    theta = torch.norm(v, dim=1, keepdim=True)  # (N, 1)

    # Avoid division by zero
    mask = theta < 1e-6
    safe_theta = torch.where(mask, torch.ones_like(theta), theta)
    k = v / safe_theta

    batch_size = v.shape[0]
    k_cross = torch.zeros((batch_size, 3, 3), device=v.device, dtype=v.dtype)
    k_cross[:, 0, 1] = -k[:, 2]
    k_cross[:, 0, 2] = k[:, 1]
    k_cross[:, 1, 0] = k[:, 2]
    k_cross[:, 1, 2] = -k[:, 0]
    k_cross[:, 2, 0] = -k[:, 1]
    k_cross[:, 2, 1] = k[:, 0]

    eye_batch = torch.eye(3, device=v.device, dtype=v.dtype).expand(
        batch_size, 3, 3
    )

    sin_t = torch.sin(theta).unsqueeze(-1)
    cos_t = torch.cos(theta).unsqueeze(-1)

    R = eye_batch + sin_t * k_cross + (1 - cos_t) * (k_cross @ k_cross)

    # Replace cases where theta was too small with identity
    R[mask.squeeze()] = torch.eye(3, device=v.device, dtype=v.dtype)

    return R


class RadialCameraModel(torch.nn.Module):
    def __init__(self, focal=1000.0, pp=(500, 500), k1=0.0):
        super().__init__()
        self.focal = torch.nn.Parameter(torch.tensor(focal))
        self.pp = torch.nn.Parameter(torch.tensor(pp, dtype=torch.float32))
        self.k1 = torch.nn.Parameter(torch.tensor(k1))

    def forward(self, points_3d, r_mats, t_vecs):
        """
        points_3d: (N, 3)
        r_mats: (N, 3, 3) rotation matrices
        t_vecs: (N, 3) translations
        """
        # Transform points to camera coordinates: P_cam = R * P_world + t
        p_cam = (r_mats @ points_3d.unsqueeze(-1)).squeeze(-1) + t_vecs

        z = p_cam[:, 2:3]
        # Avoid division by zero and points behind the camera
        z = torch.clamp(z, min=0.1)
        p_img_norm = p_cam[:, :2] / z

        # Radial distortion
        r2 = torch.sum(p_img_norm**2, dim=1, keepdim=True)
        dist = 1 + self.k1 * r2
        p_img_dist = p_img_norm * dist

        return p_img_dist * self.focal + self.pp


class BundleAdjustment(torch.nn.Module):
    def __init__(self, num_cameras, num_points, initial_intrinsics=None):
        super().__init__()
        self.r_vecs = torch.nn.Parameter(torch.zeros((num_cameras, 3)))
        self.t_vecs = torch.nn.Parameter(torch.zeros((num_cameras, 3)))
        self.points_3d = torch.nn.Parameter(torch.zeros((num_points, 3)))

        self.camera_model = RadialCameraModel(**(initial_intrinsics or {}))

    def forward(self, cam_indices, point_indices):
        r_mats_all = batch_rodrigues_to_rotation_matrix(self.r_vecs)

        r_mats = r_mats_all[cam_indices]
        t_vecs = self.t_vecs[cam_indices]
        pts3d = self.points_3d[point_indices]

        return self.camera_model(pts3d, r_mats, t_vecs)


def tapas(model_type, image_set, observations=None, num_iterations=100, **kwargs):
    """
    Orientation/Bundle Adjustment (Tapas).
    observations: dict with 'cam_idx', 'point_idx', 'points_2d'
    """
    print(f"Running Tapas with {model_type}")

    if observations:
        return _run_bundle_adjustment(observations, num_iterations)

    if kwargs.get("export_legacy"):
        _export_legacy_orientation(image_set)

    return None


def _run_bundle_adjustment(obs, num_iterations=100):
    cam_indices = torch.tensor(obs['cam_idx'], dtype=torch.long)
    point_indices = torch.tensor(obs['point_idx'], dtype=torch.long)
    points_2d = torch.tensor(obs['points_2d'], dtype=torch.float32)

    num_cameras = cam_indices.max().item() + 1
    num_points = point_indices.max().item() + 1

    model = BundleAdjustment(num_cameras, num_points)

    # Initialize with some random noise to avoid zero gradients if applicable
    with torch.no_grad():
        model.t_vecs[:, 2] = 5.0  # Default depth
        model.points_3d += torch.randn_like(model.points_3d) * 0.1

    optimizer = torch.optim.Adam(model.parameters(), lr=0.1)

    for i in range(num_iterations):
        optimizer.zero_grad()
        predicted_2d = model(cam_indices, point_indices)

        loss = torch.nn.functional.mse_loss(predicted_2d, points_2d)
        loss.backward()
        optimizer.step()

        if i % 100 == 0:
            print(f"Iteration {i}, Loss: {loss.item()}")

    return model


def _export_legacy_orientation(image_set):
    print("Exporting legacy orientation files...")
