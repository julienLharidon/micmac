$ProjectId = gcloud config get-value project
$Region = "europe-west1"
$Zone = "europe-west1-b"

Write-Host "Deploying infrastructure for project: $ProjectId"

cd install/gcp

terraform init
terraform apply -var="project_id=$ProjectId" -var="region=$Region" -var="zone=$Zone" -auto-approve

gcloud container clusters get-credentials pymicmac-cluster --zone "$Zone" --project "$ProjectId"

helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update
helm install kuberay-operator kuberay/kuberay-operator --version 1.1.0

(Get-Content ray-cluster.yaml).Replace('${PROJECT_ID}', $ProjectId) | kubectl apply -f -
