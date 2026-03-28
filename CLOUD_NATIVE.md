# Architecture MicMac Cloud-Native (IGN)

## 1. Schéma d'Architecture Système

```text
[ Client (CLI/Mobile) ]
       |
       v
[ Orchestrateur (Python/Tapioca) ] <--- Gère le workflow (Graphes de tâches)
       |
       +--- [ Job: PastDevlop (N images) ] ---> [ Cloud Run Workers ]
       |                                              | (FUSE Mount via cloud/micmac_fs.py)
       |                                              v
       |                                     [ Google Cloud Storage (Images/TIFFs) ]
       |                                     [ Redis (Cache Homologues/TiePoints)  ]
       |
       +--- [ Job: Pastis (Matching)     ] ---> [ Cloud Run Workers ]
                                                      |
                                                      v
                                             [ Firestore (Pose Matrix/Incrementality) ]
                                             [ Firebase Cloud Messaging (Mobile Sync) ]
```

## 2. Composants de l'Implémentation

### A. I/O Abstraction Wrapper (`cloud/micmac_fs.py`)
- **FUSE Implementation** : Intercepte les appels système `open`, `read`, `write`, `create`, `mkdir`.
- **Random Access Support** : Crucial pour les fichiers TIFF. Utilise un cache local temporaire pour permettre les `lseek` et les mises à jour de headers (TIFF tags) sans corrompre les fichiers.
- **Cloud Sync** : Téléchargement paresseux (lazy loading) depuis GCS et upload automatique lors de la fermeture (`release`) du fichier.
- **Performance** : Utilise un cache de répertoire en mémoire pour éviter les latences de listing GCS dans `getattr`.

### B. Cloud-Native Orchestrator (`cloud/tapioca_orchestrator.py`)
- **Découplage** : Remplace le système obsolète de Makefile de MicMac par un orchestrateur Python dynamique.
- **Parallélisation** : Décompose `Tapioca` en tâches atomiques (`PastDevlop` par image, `Pastis` par bloc ou couple).
- **Worker Dispatching** : Supporte l'exécution locale et le dispatch vers Cloud Run via API REST (scaffoldé).

### C. Incrementality & Mobile (`cloud/micmac_mobile_inc.py`)
- **Pose Patching** : Utilise Firestore pour stocker la matrice de pose globale sous forme de JSON, permettant à `Tapas` de venir "patcher" les résultats sans recharger tout le bloc.
- **Mobile Optimization** : Exporte les résidus et la densité de points en format binaire compressé (Protobuf/FlatBuffers) pour une consommation fluide sur mobile via Firebase.

## 3. Déploiement

1.  **Containeriser** MicMac (incluant le wrapper FUSE).
2.  **Lancer le worker** sur Cloud Run avec les permissions GCS/Firestore.
3.  **Utiliser l'Orchestrateur** pour piloter le calcul depuis n'importe quel environnement (local ou CI/CD).
