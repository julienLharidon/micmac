# Infrastructure for GKE with Ray support

resource "google_container_cluster" "primary" {
  name     = "pymicmac-cluster"
  location = var.region

  # Habilite Ray / KubeRay (via Helm or Operator)
  enable_autopilot = true
}

resource "google_storage_bucket" "data_bucket" {
  name          = "pymicmac-data-${var.project_id}"
  location      = "EU"
  force_destroy = true
}

# Example of GPU Node Pool for Tapas/MALT
resource "google_container_node_pool" "gpu_pool" {
  name       = "gpu-pool"
  cluster    = google_container_cluster.primary.id
  node_count = 2

  node_config {
    machine_type = "n1-standard-8"
    guest_accelerator {
      type  = "nvidia-tesla-t4"
      count = 1
    }
  }
}
