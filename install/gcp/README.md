# Guide de Déploiement PyMicMac sur GCP (GKE + Ray)

Ce guide explique comment monter l'infrastructure nécessaire sur Google Cloud Platform pour exécuter PyMicMac.

## 1. Prérequis
*   Un projet GCP actif.
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installé et configuré.
*   [Terraform](https://www.terraform.io/downloads) installé.
*   [kubectl](https://kubernetes.io/docs/tasks/tools/) installé.

## 2. Déploiement de l'Infrastructure (IaC)

1.  **Authentification** :
    ```bash
    gcloud auth application-default login
    gcloud config set project [VOTRE_PROJECT_ID]
    ```

2.  **Initialisation et Application Terraform** :
    ```bash
    cd install/gcp
    terraform init
    terraform apply -var="project_id=[VOTRE_PROJECT_ID]" -var="region=europe-west1"
    ```
    *Cela va créer un cluster GKE Autopilot et un bucket GCS.*

3.  **Configuration de kubectl** :
    ```bash
    gcloud container clusters get-credentials pymicmac-cluster --region europe-west1
    ```

## 3. Installation de Ray (KubeRay)

Déployez l'opérateur KubeRay pour gérer le cluster Ray sur GKE :
```bash
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm install kuberay-operator kuberay/kuberay-operator --version 1.1.1
kubectl apply -f ray-cluster.yaml
```
*(Le fichier `ray-cluster.yaml` définit les ressources CPU/GPU des workers Ray)*

## 4. Préparation des Données de Test

Utilisez le script fourni pour uploader des images de test vers GCS :
```bash
export BUCKET_NAME=pymicmac-data-[VOTRE_PROJECT_ID]
python3 scripts/upload_test_data.py --bucket $BUCKET_NAME --dir ./data/test_images
```

## 5. Exécution du Traitement

Lancez le job PyMicMac sur le cluster Ray :
```bash
ray job submit --address http://localhost:8265 -- python3 demo_pymicmac.py --bucket $BUCKET_NAME
```

## 6. Nettoyage
Pour éviter des frais inutiles :
```bash
terraform destroy -var="project_id=[VOTRE_PROJECT_ID]"
```
