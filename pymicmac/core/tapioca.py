"""
Module pour l'extraction de points de liaison (Tapioca).
"""
import os
import time

import numpy as np
import torch


def extract_tie_points(image_path):
    """
    Extrait les points de liaison d'une image.
    Version de préproduction pour évaluation des performances.
    """
    # On simule une charge de travail proportionnelle à la taille de l'image si elle existe
    file_size = 0
    if os.path.exists(image_path):
        file_size = os.path.getsize(image_path)

    print(f"Traitement de {image_path} (taille: {file_size} octets)...")

    start_time = time.time()

    # Simulation de la charge de calcul avec PyTorch
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 2048x2048 est une taille typique
    current_tensor = torch.randn(1, 3, 2048, 2048).to(device)

    # Quelques couches de convolutions
    with torch.no_grad():
        # Première couche: 3 -> 64
        conv1 = torch.nn.Conv2d(3, 64, kernel_size=3, padding=1).to(device)
        current_tensor = conv1(current_tensor)

        # Couches suivantes: 64 -> 64
        conv_rest = torch.nn.Conv2d(64, 64, kernel_size=3, padding=1).to(device)
        for _ in range(4):
            current_tensor = conv_rest(current_tensor)

    if device == "cuda":
        torch.cuda.synchronize()

    elapsed = time.time() - start_time

    # Retourne des points fictifs
    return {
        "image_id": image_path,
        "number_of_features": 1000,
        "processing_time": elapsed,
        "device": device,
        "points": np.random.rand(1000, 2).tolist()
    }
