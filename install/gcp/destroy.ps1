$ProjectId = gcloud config get-value project

cd install/gcp

kubectl delete raycluster raycluster-pymicmac
helm uninstall kuberay-operator

terraform destroy -var="project_id=$ProjectId" -auto-approve
