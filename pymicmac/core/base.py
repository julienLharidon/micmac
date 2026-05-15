
class Camera:
    """Base class for camera models."""
    def __init__(self, focal_length=None, principal_point=None, distortion=None):
        self.focal_length = focal_length
        self.principal_point = principal_point
        self.distortion = distortion

    def project(self, point_3d):
        """Project a 3D point to 2D image coordinates."""
        raise NotImplementedError

    def unproject(self, point_2d, depth):
        """Unproject a 2D image point to 3D given depth."""
        raise NotImplementedError

class ImageSet:
    """Collection of images for a photogrammetric project."""
    def __init__(self, image_paths):
        self.image_paths = image_paths
        self.cameras = {} # Map image path to Camera object
        self.tie_points = None

    def __len__(self):
        return len(self.image_paths)
