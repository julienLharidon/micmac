# Infrastructure for GKE with Ray support

# 1. Dedicated Service Account for GKE Nodes
resource "google_service_account" "gke_nodes" {
  account_id   = "pymicmac-gke-nodes"
  display_name = "Service Account for PyMicMac GKE Nodes"
}

# 2. Assign IAM Roles for Node Functionality
resource "google_project_iam_member" "node_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

resource "google_project_iam_member" "node_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

resource "google_project_iam_member" "node_metadata" {
  project = var.project_id
  role    = "roles/stackdriver.resourceMetadata.writer"
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

# 3. Dedicated Service Account for PyMicMac Application (Workload Identity)
resource "google_service_account" "app_sa" {
  account_id   = "pymicmac-app-sa"
  display_name = "Service Account for PyMicMac App (Access to GCS)"
}

# 4. GCS Permissions for the Application
resource "google_storage_bucket_iam_member" "app_gcs_admin" {
  bucket = google_storage_bucket.data_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.app_sa.email}"
}

# 5. GKE Cluster with Workload Identity Enabled
resource "google_container_cluster" "primary" {
  name     = "pymicmac-cluster"
  location = var.region

  # Workload Identity configuration
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  node_config {
    service_account = google_service_account.gke_nodes.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  enable_autopilot = true
}

# 6. GCS Bucket for Project Data
resource "google_storage_bucket" "data_bucket" {
  name          = "pymicmac-data-${var.project_id}"
  location      = "EU"
  force_destroy = true
}
