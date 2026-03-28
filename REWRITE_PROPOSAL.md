# Proposition de Réécriture Cloud-Native de MicMac (PyMicMac)

Cette proposition détaille l'architecture et la stratégie de réécriture du projet MicMac en Python, optimisé pour le Cloud, en utilisant des technologies modernes de calcul distribué et de stockage.

## 1. Stack Technique Cible

*   **Moteur de Calcul Distribué** : **Ray** (Natif Python, gestion fine des Acteurs et de la mémoire partagée via Plasma).
*   **Moteur de Géométrie et Optimisation** : **PyTorch** (Différenciation automatique pour les modèles de caméras, calcul GPU).
*   **Stockage des Données Tabulaires** : **Apache Iceberg** (Format Parquet, partitionnement efficace, requêtes SQL via Trino/Spark).
*   **Stockage Objet (Images & Blobs)** : **MinIO** ou **Ceph S3** (Compatibilité S3, haute performance pour les gros volumes).
*   **Formats de Sortie** : **COG** (Cloud Optimized GeoTIFF) pour l'ortho/MNS et **COPC** (Cloud Optimized Point Cloud) pour la 3D.
*   **Orchestration** : **Kubernetes** (KubeRay pour la gestion élastique des clusters).

## 2. Architecture Système (Ray Actors)

Le système est décomposé en acteurs Ray asynchrones pour une scalabilité maximale :

*   **`WorkflowManager`** : Pilote le graphe de dépendances global.
*   **`StorageProxy`** : Interface unifiée vers S3 avec mise en cache locale.
*   **`ImageProcessor`** : Workers dédiés à la pyramide d'images et au prétraitement.
*   **`OptimizationSolver`** : Acteurs GPU centralisant la compensation par faisceaux (Bundle Adjustment).
*   **`TilingWorker`** : Workers gérant les tuiles 3D pour la corrélation dense (Malt).

## 3. Détails des Composants Majeurs

### A. Tapioca (Extraction et Matching)
*   **Extraction** : Utilisation de PyTorch (SIFT/Digeo ou modèles DL type SuperPoint) pour extraire les descripteurs sur GPU par batches.
*   **Matching** : Utilisation de **Faiss** distribué pour la recherche de voisins proches.
*   **Modes supportés** : `All`, `Line` (fenêtre glissante), `Graph` (basé sur le recouvrement basse résolution).
*   **Persistance** : Les tie-points sont streamés vers une table Iceberg `tie_points`.

### B. Tapas / Martini (Orientation et Compensation)
*   **Modélisation** : Chaque modèle de caméra MicMac (Radial, Fraser, Fish-Eye) est implémenté comme un `nn.Module` PyTorch.
*   **Solveur** : Optimiseur de type `Levenberg-Marquardt` implémenté en Torch pour bénéficier de l'Autograd.
*   **GCP** : Intégration des points d'appui comme des contraintes dans la fonction de perte (Loss).
*   **Initialisation** : Workflow Martini pour une orientation relative rapide avant l'optimisation globale.

### C. MALT (Corrélation Dense)
*   **Algorithme** : Implémentation distribuée de **SGM/MGM** (Option A) pour assurer la parité MicMac.
*   **Extensibilité** : Interface plugin pour l'intégration de modèles **Neural MVS** (Option B) de type MVSNet.
*   **Tuilage** : Découpage spatial 3D distribué sur Ray pour traiter des zones massives en parallèle.

## 4. Interopérabilité et Export
*   **Legacy Gateway** : Module de conversion des tables Iceberg vers les formats MicMac XML/DAT historiques.
*   **Cloud Exports** : Génération directe de COG et COPC LAZ 1.4 vers S3.
*   **Catalogage** : Génération de métadonnées **STAC** pour l'indexation géographique.

## 5. Roadmap de Développement

1.  **Phase 1 (POC)** : Infrastructure de base (Ray + MinIO) et prototype de Tapas avec PyTorch sur un petit bloc d'images.
2.  **Phase 2 (Tapioca)** : Pipeline distribué d'extraction et de matching avec stockage Iceberg.
3.  **Phase 3 (Malt)** : Implémentation du tuilage SGM distribué et sorties COG/COPC.
4.  **Phase 4 (Parité)** : Portage des modèles de distorsion restants et finalisation de la passerelle Legacy.

---
*Cette proposition vise à transformer MicMac d'un outil de bureau puissant en une plateforme de traitement photogrammétrique à l'échelle planétaire.*
