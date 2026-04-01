# Guide de Déploiement PyMicMac sur GCP (GKE + Ray + IAM)

Ce guide détaille le montage de l'infrastructure et la configuration des identités (IAM) pour sécuriser l'accès aux données, optimisé pour une utilisation depuis **Cloud Shell**.

## 1. Prérequis
*   Un projet GCP actif.
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (Pré-installé sur Cloud Shell).
*   [Terraform](https://www.terraform.io/downloads) (Pré-installé sur Cloud Shell).

## 2. Déploiement de l'Infrastructure (IaC)

1.  **Authentification et Configuration** :
    ```bash
    gcloud auth application-default login
    # Le projet est généralement déjà configuré dans Cloud Shell, sinon :
    # gcloud config set project $(gcloud config get-value project)
    ```

2.  **Application de l'Infrastructure** :
    ```bash
    cd install/gcp
    terraform init
    terraform apply -var="project_id=$(gcloud config get-value project)" -var="region=europe-west1"
    ```
    *Terraform crée automatiquement le cluster GKE, les comptes de service et le bucket GCS.*

3.  **Accès au Cluster** :
    ```bash
    gcloud container clusters get-credentials pymicmac-cluster --region europe-west1
    ```

## 3. Configuration de Workload Identity (IAM)

1.  **Création du Namespace et du Service Account Kubernetes** :
    ```bash
    kubectl create namespace pymicmac
    kubectl create serviceaccount ray-worker-sa --namespace pymicmac
    ```

2.  **Liaison IAM (Binding)** :
    ```bash
    gcloud iam service-accounts add-iam-policy-binding pymicmac-app-sa@$(gcloud config get-value project).iam.gserviceaccount.com \
        --role roles/iam.workloadIdentityUser \
        --member "serviceAccount:$(gcloud config get-value project).svc.id.goog[pymicmac/ray-worker-sa]"
    ```

3.  **Annotation du Service Account K8s** :
    ```bash
    kubectl annotate serviceaccount ray-worker-sa --namespace pymicmac \
        iam.gke.io/gcp-service-account=pymicmac-app-sa@$(gcloud config get-value project).iam.gserviceaccount.com
    ```

## 4. Installation de KubeRay et RayCluster

L'opérateur KubeRay gère le cycle de vie de vos clusters Ray sur Kubernetes.

1.  **Installation de l'Opérateur** :
    ```bash
    helm repo add kuberay https://ray-project.github.io/kuberay-helm/
    helm install kuberay-operator kuberay/kuberay-operator
    ```

2.  **Déploiement du Cluster Ray (RayCluster)** :
    Utilisez le fichier `ray-cluster.yaml` fourni pour créer le cluster avec les bons droits d'accès GCS (Workload Identity) :
    ```bash
    kubectl apply -f ray-cluster.yaml
    ```
    *Ce fichier configure :*
    - *Un Head node avec le Dashboard activé.*
    - *Des Worker nodes (auto-scalables de 1 à 10).*
    - *L'utilisation du compte de service `ray-worker-sa` pour chaque pod.*

3.  **Vérification** :
    Attendez que les pods soient en état `Running` :
    ```bash
    kubectl get pods -n pymicmac
    ```

## 5. Test et Démo (depuis Cloud Shell)

### Résolution de "ray: command not found"
Si la commande `ray` n'est pas disponible dans votre environnement Cloud Shell, installez le client Ray :
```bash
pip3 install "ray[default]"
# Assurez-vous que le répertoire des binaires utilisateur est dans votre PATH
export PATH=$PATH:~/.local/bin
```

### Connexion au Cluster Ray
Pour soumettre un job, vous devez accéder au tableau de bord Ray (Dashboard) via un port-forward :
1.  **Port-forward du Dashboard** :
    ```bash
    # Dans un nouveau terminal Cloud Shell
    kubectl port-forward svc/raycluster-head-svc 8265:8265 -n pymicmac
    ```

2.  **Upload des données** :
    ```bash
    gsutil cp -r ../../data/test_images gs://pymicmac-data-$(gcloud config get-value project)/raw-images/
    ```

3.  **Exécution du job** :
    Il est impératif de spécifier le répertoire de travail (`--working-dir .`) pour que Ray uploade votre code local (`demo_pymicmac.py` et le package `pymicmac`) sur le cluster :
    ```bash
    # Exécutez cette commande à la racine du projet (où se trouve demo_pymicmac.py)
    ray job submit --address http://localhost:8265 \
        --working-dir . \
        -- python3 demo_pymicmac.py
    ```
    *Note : Si le cluster n'a pas les bibliothèques nécessaires, Ray les installera via le `runtime_env` automatiquement si vous ajoutez un fichier `requirements.txt` à la racine.*

## 6. Sécurité (Best Practices)
*   **Identité** : Le job s'exécute avec l'identité `pymicmac-app-sa` grâce à Workload Identity.
*   **Nettoyage** : `terraform destroy -var="project_id=$(gcloud config get-value project)"`
