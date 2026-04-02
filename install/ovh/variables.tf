variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "europe-west1"
}

variable "template_id" {
  description = "The OVH OpenStack template ID for Kubernetes"
  type        = string
}
