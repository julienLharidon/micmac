# Infrastructure for OVH Cloud (OpenStack)

resource "openstack_containerinfra_cluster_v1" "k8s" {
  name                = "pymicmac-ovh"
  cluster_template_id = var.template_id
  master_count        = 1
  node_count          = 3
  flavor              = "b2-7"
}

resource "openstack_objectstorage_container_v1" "bucket" {
  region = var.region
  name   = "pymicmac-data"
}

# Example of GPU Node Pool on OVH Managed K8s
# (Typically managed via OVH console or separate terraform resource for Managed K8s nodes)
