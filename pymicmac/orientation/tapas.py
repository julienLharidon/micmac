import numpy as np
import pyceres
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


def tapas(model_type, image_set, observations=None, solver="pytorch", **kwargs):
    """
    Orientation/Bundle Adjustment (Tapas).
    solver: "pytorch" or "ceres"
    """
    print(f"Running Tapas with {model_type} using {solver} solver")

    if observations:
        if solver == "ceres":
            return _run_ceres_bundle_adjustment(observations)
        return _run_bundle_adjustment(observations, kwargs.get("num_iterations", 100))

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

    with torch.no_grad():
        model.t_vecs[:, 2] = 5.0
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


class ReprojectionCost(pyceres.CostFunction):
    """
    Ceres Cost Function for Bundle Adjustment.
    Calculates reprojection error for a single observation.
    """
    def __init__(self, observation_2d):
        super().__init__()
        self.observation_2d = observation_2d
        self.set_num_residuals(2)
        # Parameters: [r_vec(3), t_vec(3), point_3d(3), intrinsics(4)]
        self.set_parameter_block_sizes([3, 3, 3, 4])

    def Evaluate(self, parameters, residuals, jacobians):
        r_vec = torch.tensor(parameters[0])
        t_vec = torch.tensor(parameters[1])
        point_3d = torch.tensor(parameters[2]).unsqueeze(0)
        intrinsics = parameters[3]

        # Intrinsics: focal, ppx, ppy, k1
        model = RadialCameraModel(focal=intrinsics[0],
                                  pp=(intrinsics[1], intrinsics[2]),
                                  k1=intrinsics[3])

        r_mat = rodrigues_to_rotation_matrix(r_vec).unsqueeze(0)
        predicted_2d = model(point_3d, r_mat, t_vec.unsqueeze(0)).squeeze(0)

        diff = predicted_2d - torch.tensor(self.observation_2d)
        residuals[0] = diff[0].item()
        residuals[1] = diff[1].item()

        # Jacobeans would be calculated here if not using AutoDiff
        # In pyceres we can use AutoDiff if available or numerical diff.
        return True


def _run_ceres_bundle_adjustment(obs):
    """
    Run Bundle Adjustment using Ceres Solver via pyceres.
    """
    print("Initializing Ceres Solver...")
    cam_indices = np.array(obs['cam_idx'])
    point_indices = np.array(obs['point_idx'])
    points_2d = np.array(obs['points_2d'])

    num_cameras = int(cam_indices.max() + 1)
    num_points = int(point_indices.max() + 1)

    r_vecs = [np.zeros(3) for _ in range(num_cameras)]
    t_vecs = [np.array([0.0, 0.0, 5.0]) for _ in range(num_cameras)]
    points_3d = [np.random.randn(3) * 0.1 for _ in range(num_points)]
    intrinsics = np.array([1000.0, 500.0, 500.0, 0.0])

    problem = pyceres.Problem()

    for i in range(len(points_2d)):
        cost_func = ReprojectionCost(points_2d[i])
        problem.add_residual_block(cost_func, None,
                                   [r_vecs[cam_indices[i]],
                                    t_vecs[cam_indices[i]],
                                    points_3d[point_indices[i]],
                                    intrinsics])

    options = pyceres.SolverOptions()
    options.linear_solver_type = pyceres.LinearSolverType.DENSE_SCHUR
    options.minimizer_progress_to_stdout = True

    summary = pyceres.SolverSummary() # Fixed class name
    pyceres.solve(options, problem, summary)

    print(summary.BriefReport())
    return {
        'r_vecs': r_vecs,
        't_vecs': t_vecs,
        'points_3d': points_3d,
        'intrinsics': intrinsics
    }


def _export_legacy_orientation(image_set):
    print("Exporting legacy orientation files...")
