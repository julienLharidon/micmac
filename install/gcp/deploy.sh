#!/bin/bash
set -e

PROJECT_ID=$(gcloud config get-value project)
REGION="europe-west1"
ZONE="europe-west1-b"

echo "Deploying infrastructure for project: $PROJECT_ID"

cd install/gcp

# Terraform
terraform init
terraform apply -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="zone=$ZONE" -auto-approve

# Connect to GKE
gcloud container clusters get-credentials pymicmac-cluster --zone "$ZONE" --project "$PROJECT_ID"

# Install KubeRay Operator (assumes helm is installed)
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update
helm install kuberay-operator kuberay/kuberay-operator --version 1.1.0

# Deploy Ray Cluster
sed "s/\${PROJECT_ID}/$PROJECT_ID/g" ray-cluster.yaml | kubectl apply -f -

echo "Deployment complete."
