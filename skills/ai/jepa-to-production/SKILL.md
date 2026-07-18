---
name: jepa-to-production
description: "Mise en production de modèles EB-JEPA avec Docker."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    maturity: production
    tags: [jepa, docker, deployment, production, testing]
    related_skills: [jepa-joint-embedding-predictive, industrial-ai-pipeline]
---

# Mise en Production de Modèles EB-JEPA (Energy-Based)

## Rôle et Identité
Vous êtes un ingénieur MLOps principal et un expert en déploiement de modèles de Deep Learning sur architectures Edge. Votre rôle est de containeriser, d'optimiser et de déployer en production des modèles de type EB-JEPA (Energy-Based Joint Embedding Predictive Architecture) pour des tâches industrielles de vision en temps réel.

## Vue d'ensemble
Déployer des modèles auto-supervisés volumineux comme JEPA (notamment V-JEPA et EB-JEPA) sur des PC Edge d'atelier requiert une gestion rigoureuse des pilotes GPU, des images de conteneurs, et de l'allocation mémoire. Cette compétence fournit les templates opérationnels et le guide d'optimisation pour la containerisation et l'inférence sécurisée en production.

---

## 1. Processus de Containerisation et Déploiement

```
[Modèle EB-JEPA] ──► Optimisation FP16/INT8 ──► Image Docker (CUDA)
                                                        │
                                                        ▼
                                            [PC Edge d'Atelier]
                                                        │ (Nvidia Runtime)
                                                        ▼
                                            [Inférence temps réel]
```

### Commandes de Déploiement en Production
1.  **Construction de l'image** :
    ```bash
    docker build -t jepa-inference:v1.0.0 .
    ```
2.  **Lancement avec accès GPU complet** :
    ```bash
    docker run --gpus all --rm -p 8080:8080 --name jepa-service jepa-inference:v1.0.0
    ```

---

## 2. Dockerfile Optimisé pour l'Inférence GPU (Multi-Stage)

Ce Dockerfile utilise un build multi-étapes pour installer les dépendances nécessaires (dont git) puis générer une image de production minimale et épurée.

```dockerfile
# Étape 1 : Build et installation des dépendances
FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Installer la librairie EB-JEPA de Meta AI
RUN pip install --user git+https://github.com/facebookresearch/eb_jepa.git

# Étape 2 : Image finale légère
FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

WORKDIR /app

# Installer les dépendances d'exécution d'images
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Récupérer les paquets installés depuis le builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 8080
ENTRYPOINT ["python", "app.py"]
```

---

## 3. Script de Validation de l'Inférence (PyTest)

Ce fichier de test valide le chargement du modèle et la forme des vecteurs de caractéristiques retournés.

```python
# test_production_inference.py
import pytest
import torch
from eb_jepa.models import create_jepa_encoder

def test_encoder_inference_on_gpu():
    """Valide l'extraction de caractéristiques sémantiques sur GPU CUDA."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Initialisation du modèle
    model = create_jepa_encoder("vit_small")
    model.to(device)
    model.eval()
    
    # Lot d'images fictif : 1 image, 3 canaux, 224x224 pixels
    dummy_tensor = torch.randn(1, 3, 224, 224).to(device)
    
    with torch.no_grad():
        embeddings = model(dummy_tensor)
        
    assert embeddings is not None
    # Vérification des dimensions de sortie
    assert embeddings.shape[0] == 1  # Taille du lot
    assert embeddings.shape[2] == 384  # Embedding dimension pour ViT-S
```

---

## 4. Pièges Courants (Common Pitfalls)
*   **Conflit de Version CUDA** : Utiliser une image de base Docker dont la version de CUDA dépasse la version maximale supportée par le pilote GPU physique installé sur le PC Edge de l'atelier. **Solution** : Toujours exécuter `nvidia-smi` sur l'hôte et choisir une image Docker correspondante (ex: CUDA 12.1 pour pilote >= 525).
*   **Contraintes de Licence Constructeur** : Déployer les modèles officiels V-JEPA dans un contexte commercial. Les checkpoints officiels V-JEPA sont sous licence CC BY-NC 4.0. **Solution** : Utiliser l'implémentation EB-JEPA (`eb_jepa`) sous licence **Apache 2.0** et réentraîner le modèle sur vos données.

---

## 5. Liste de vérification (Checklist)
- [ ] Valider la compatibilité de la version CUDA du conteneur avec le pilote hôte.
- [ ] Configurer le runtime Nvidia (`--gpus all`) sur le démon Docker de l'hôte.
- [ ] Mesurer la consommation mémoire GPU au démarrage et en charge active (éviter les débordements OOM).
- [ ] Vérifier la conformité des licences d'exploitation commerciales pour les modèles et bibliothèques tiers.
- [ ] Automatiser l'exécution des tests de validation d'inférence lors de la construction du conteneur (CI/CD).
