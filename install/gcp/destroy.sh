#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
ZONE="europe-west1-b"

cd install/gcp

kubectl delete raycluster raycluster-pymicmac
helm uninstall kuberay-operator

terraform destroy -var="project_id=$PROJECT_ID" -auto-approve
