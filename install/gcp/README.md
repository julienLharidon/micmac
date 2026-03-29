# Guide de Déploiement PyMicMac sur GCP (GKE + Ray + IAM)

Ce guide détaille le montage de l'infrastructure et la configuration des identités (IAM) pour sécuriser l'accès aux données.

## 1. Prérequis
*   Un projet GCP actif.
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
*   [Terraform](https://www.terraform.io/downloads).

## 2. Déploiement de l'Infrastructure (IaC)

1.  **Authentification et Configuration** :
    ```bash
    gcloud auth application-default login
    gcloud config set project [PROJECT_ID]
    ```

2.  **Application de l'Infrastructure** :
    ```bash
    cd install/gcp
    terraform init
    terraform apply -var="project_id=[PROJECT_ID]" -var="region=europe-west1"
    ```
    *Terraform crée automatiquement :*
    - *Un compte de service pour les nœuds (`pymicmac-gke-nodes`).*
    - *Un compte de service pour l'application (`pymicmac-app-sa`) avec accès au bucket GCS.*
    - *Le cluster GKE avec Workload Identity activé.*

3.  **Accès au Cluster** :
    ```bash
    gcloud container clusters get-credentials pymicmac-cluster --region europe-west1
    ```

## 3. Configuration de Workload Identity (IAM)

Pour que vos pods Ray (identités Kubernetes) puissent accéder à GCS sans clé JSON, nous lions le compte de service Kubernetes au compte de service GCP :

1.  **Création du Namespace et du Service Account Kubernetes** :
    ```bash
    kubectl create namespace pymicmac
    kubectl create serviceaccount ray-worker-sa --namespace pymicmac
    ```

2.  **Liaison IAM (Binding)** :
    Liez l'identité Kubernetes au compte de service GCP géré par Terraform :
    ```bash
    gcloud iam service-accounts add-iam-policy-binding pymicmac-app-sa@[PROJECT_ID].iam.gserviceaccount.com \
        --role roles/iam.workloadIdentityUser \
        --member "serviceAccount:[PROJECT_ID].svc.id.goog[pymicmac/ray-worker-sa]"
    ```

3.  **Annotation du Service Account K8s** :
    ```bash
    kubectl annotate serviceaccount ray-worker-sa --namespace pymicmac \
        iam.gke.io/gcp-service-account=pymicmac-app-sa@[PROJECT_ID].iam.gserviceaccount.com
    ```

## 4. Installation de KubeRay

Installez l'opérateur Ray en spécifiant le compte de service configuré pour vos workers :
```bash
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm install kuberay-operator kuberay/kuberay-operator
```
*Lors du déploiement de votre cluster Ray, assurez-vous d'utiliser `serviceAccountName: ray-worker-sa` dans la spec des pods.*

## 5. Test et Démo

Chargez vos données et lancez le traitement comme décrit dans la démo principale :
```bash
# Upload via gcloud (utilise vos droits personnels)
gsutil cp -r ./data/test_images gs://pymicmac-data-[PROJECT_ID]/raw-images/

# Exécution du job (utilise le compte de service pymicmac-app-sa via Workload Identity)
ray job submit --address http://localhost:8265 -- python3 demo_pymicmac.py
```

## 6. Sécurité (Best Practices)
*   **Principe du Moindre Privilège** : Le compte `pymicmac-app-sa` n'a accès qu'au bucket spécifique du projet.
*   **Pas de clés statiques** : Grâce à Workload Identity, aucune clé JSON n'est stockée dans les pods.
