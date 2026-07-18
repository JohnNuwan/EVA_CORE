---
name: jepa-joint-embedding-predictive
description: "Architecture JEPA et applications de vision industrielle."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    maturity: pilot
    tags: [jepa, yann-lecun, meta-ai, self-supervised-learning, computer-vision, video-understanding, world-model, industry40]
    related_skills: [ai-foundations-exploration, predictive-maintenance-ml, computer-vision-quality, robotics-kuka, robotics-fanuc, robotics-abb, jepa-to-production]
---

# JEPA — Joint Embedding Predictive Architecture

## Vue d'ensemble

JEPA est une architecture d'apprentissage auto-supervisé conçue par **Yann LeCun** (Meta AI / FAIR) depuis 2022, brique centrale de sa vision pour l'AMI (Advanced Machine Intelligence). Contrairement aux approches génératives (prédire les pixels) ou contrastives (aligner des vues), JEPA **prédit la représentation abstraite d'une partie masquée** à partir de la représentation des parties visibles, dans l'espace latent.

## Quand l'utiliser

- Pour implémenter de la détection d'anomalies visuelles sans données étiquetées de défauts
- Pour construire un modèle du monde physique à partir de flux vidéo industriels
- Pour de la reconnaissance de patterns sur ligne de production avec très peu d'exemples annotés
- Pour de la surveillance de scènes dynamiques (robotique, AGV, convoyeurs)
- Pour remplacer des approches de vision classiques quand les données de défauts sont rares

---

## 1. Principe Fondamental

```
[Image/Vidéo] → Context Encoder → Embedding des parties visibles
                                      ↓
                                 Predictor → Embedding prédit (parties masquées)
                                      ↓
                     Target Encoder → Embedding réel (vérité terrain)
                                      ↓
                           Loss = ||prédit - réel||²
```

- Le prédicteur travaille dans **l'espace latent**, pas dans l'espace pixel.
- Il peut **ignorer les détails imprévisibles** (bruit, texture) et se concentrer sur la sémantique.
- **Pas de collapse de représentation** (contrairement aux méthodes contrastives).
- **Pas de gaspillage sur les détails** (contrairement aux méthodes génératives type MAE).

## 2. Variantes Existantes (7 repos facebookresearch)

### 2.1 I-JEPA — Image (ijepa)
- **Repo** : `github.com/facebookresearch/ijepa` (3.5k stars, archivé)
- **Papier** : arXiv 2301.08243, CVPR 2023
- **Principe** : Prédit la représentation de patches d'image masqués dans l'espace latent
- **Architecture** : ViT-H 632M paramètres, 16 A100 GPUs, < 72h
- **Performance** : SOTA low-shot classification ImageNet (12 exemples/classe)
- **Code** : PyTorch, checkpoints disponibles

### 2.2 V-JEPA — Vidéo (jepa)
- **Repo** : `github.com/facebookresearch/jepa` (4k stars)
- **Papier** : arXiv 2404.08471
- **Principe** : Prédit des régions spatio-temporelles masquées dans l'espace latent
- **Architecture** : ViT-L/H, patch 2x16x16, masquage spatial ET temporel
- **Performance** : K400 82%, SSv2 72.2%, ImageNet 77.4% (frozen eval)
- **Données** : VideoMix2M (2M vidéos)
- **Licence** : CC BY-NC

### 2.3 EB-JEPA — Energy-Based (eb_jepa)
- **Repo** : `github.com/facebookresearch/eb_jepa` (729 stars)
- **Papier** : arXiv 2602.03604 (Janvier 2026)
- **Principe** : Bibliothèque légère unifiant les approches JEPA avec une formulation energy-based
- **Exemples** : Image JEPA (CIFAR-10), Video JEPA, **AC Video JEPA** (Action-Conditioned, pour la planification dans environnement Two Rooms)
- **Licence** : **Apache 2.0** (pas de restriction non-commerciale !)
- **Particularité** : Fonctionne sur une seule GPU, quelques heures d'entraînement

### 2.4 JEPA-WMS — World Models (jepa-wms)
- **Repo** : `github.com/facebookresearch/jepa-wms` (419 stars)
- **Principe** : JEPA comme **modèle du monde** pour la planification physique
- **Environnements** : DROID, RoboCasa (vrais robots), Metaworld, Push-T, PointMaze (simulation)
- **Encodeurs** : DINOv2 ViT-S, DINOv3 ViT-L, V-JEPA-2 ViT-G
- **Profondeur de prédiction** : 6 à 24 pas dans le futur
- **Modèles pré-entraînés** : Disponibles sur Hugging Face
- **Comparaison** : vs DINO-WM, V-JEPA-2-AC(fixed)

### 2.5 JEPA Intuitive Physics (jepa-intuitive-physics)
- **Repo** : `github.com/facebookresearch/jepa-intuitive-physics` (262 stars)
- **Principe** : La compréhension intuitive de la physique émerge du pré-entraînement auto-supervisé sur vidéos naturelles
- **Évaluation** : IntPhys, GRASP, InfLevel-lab
- **Métrique** : Surprise — à quel point le modèle est surpris par des événements physiquement impossibles
- **Conclusion** : V-JEPA développe une compréhension implicite des lois physiques sans supervision

### 2.6 TD-JEPA — Temporal Difference (td_jepa)
- **Repo** : `github.com/facebookresearch/td_jepa` (45 stars)
- **Principe** : Représentations latentes prédictives pour le **RL zero-shot**
- **Base** : Meta Motivo
- **Environnements** : ExORL/DMC (walker, cheetah, quadruped, maze) et OGBench (antmaze, cube, puzzle)
- **Entrée** : États proprioceptifs ou RGB pixels
- **Comparaison** : vs FB, HILP, ICVF, Laplacian, RLDP, BYOL

### 2.7 3D-JEPA — Localisation 3D (locate-3d)
- **Repo** : `github.com/facebookresearch/locate-3d` (449 stars)
- **Principe** : Apprentissage auto-supervisé sur nuages de points 3D (point clouds)
- **Application** : Localisation d'objets dans des scènes 3D à partir d'expressions langagières
- **Pipeline** : CLIP/DINO → nuage de points 3D → 3D-JEPA (masquage latent) → fine-tuning → masques 3D + bounding boxes
- **Modèle** : Locate 3D (600M), 3D-JEPA encoder (300M)
- **Dataset** : Locate 3D Dataset (130K annotations)
- **Usage** : Robots, AR, devices

> **Plans d'implémentation détaillés** : voir [`references/implementation-plans.md`](references/implementation-plans.md) pour le guide pas-à-pas EB-JEPA et I-JEPA (setup, code, API REST, intégration OPC UA, roadmap 8 semaines).
> **Template MLOps de production** : voir le skill [`jepa-to-production`](../jepa-to-production/SKILL.md) pour le Dockerfile et les tests PyTest prêts au déploiement.

---

## 3. Comparaison avec les Autres Approches

| Approche | Mécanisme | Problème | JEPA vs |
|---|---|---|---|
| **Générative** (MAE, VideoMAE) | Prédire les pixels masqués | Gaspille de la capacité sur les détails imprévisibles | JEPA ignore ces détails → plus efficace |
| **Contrastive** (SimCLR, DINO, MoCo) | Aligner les vues augmentées | Besoin d'augmentations agressives, risque de collapse | JEPA n'a pas besoin d'augmentations ni de negative pairs |
| **Invariante** (JEA, I-JEPA sans prédicteur) | Embeddings identiques | Pas de modélisation des relations spatiales | JEPA prédit les relations entre parties |

---

## 4. Applications Industrielles

### 4.1 Inspection Qualité Visuelle (Zero-Shot / Few-Shot)

**Problème** : Les défauts de production sont rares → impossible de constituer un dataset équilibré.

**Solution I-JEPA** :
```
1. Pré-entraîner I-JEPA sur des images de pièces BONNES (non étiquetées)
2. Le modèle apprend la représentation "normale"
3. En production : si l'erreur de prédiction JEPA dépasse un seuil → anomalie
4. Pas besoin d'images de défauts pour l'entraînement
```

```python
# Pseudo-code inspection qualité avec I-JEPA
def detect_anomaly(image, jepa_model, threshold=0.15):
    # Masquer aléatoirement des patches
    masked_image, mask = apply_mask(image)
    # Prédire les représentations des patches masqués
    predicted = jepa_model.predictor(
        jepa_model.context_encoder(masked_image)
    )
    # Comparer avec les vraies représentations
    target = jepa_model.target_encoder(image)
    prediction_error = F.mse_loss(predicted, target[mask])
    return prediction_error > threshold  # True = anomalie
```

### 4.2 Surveillance de Ligne de Production (Vidéo)

**Problème** : Surveiller une ligne 24/7, détecter les comportements anormaux.

**Solution V-JEPA** :
```
1. Pré-entraîner V-JEPA sur des séquences vidéo de production NORMALE
2. Le backbone apprend le flux "normal" de la ligne
3. En temps réel : erreur de prédiction élevée sur les portions masquées
   → comportement anormal (blocage, bourrage, vitesse anormale)
4. Alerte avant l'arrêt machine
```

### 4.3 Robotique — Modèle du Monde Physique

**Problème** : Un robot doit comprendre les conséquences de ses actions.

**Solution V-JEPA** :
```
- V-JEPA apprend un modèle prédictif du monde physique
- Le robot peut "imaginer" le résultat d'une action avant de l'exécuter
- Applications : préhension adaptative, navigation AGV, évitement de collisions
```

### 4.4 Maintenance Prédictive par Vision

**Problème** : Détecter l'usure avant la panne.

**Solution I-JEPA + Sonde** :
```
1. Pré-entraîner I-JEPA sur des images d'équipement en bon état
2. Geler le backbone, ajouter une sonde de régression fine
3. Quelques exemples annotés de niveaux d'usure suffisent
4. Prédiction continue du niveau d'usure
```

### 4.5 SCADA Augmenté — Analyse d'Écrans HMI

**Problème** : Des opérateurs surveillent des écrans HMI.

**Solution I-JEPA** :
```
- I-JEPA reconnaît les patterns normaux d'un écran HMI
- Détection automatique de configurations anormales
- Capture et classification automatique des écrans d'alarme
```

---

## 5. Implémentation de Référence (PyTorch)

### 5.1 Context Encoder + Target Encoder + Predictor

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class JEPA(nn.Module):
    """Joint Embedding Predictive Architecture — version simplifiée."""
    
    def __init__(self, embed_dim=768, predictor_depth=6, encoder_depth=12):
        super().__init__()
        self.embed_dim = embed_dim
        
        # Context encoder : encode les patches visibles
        self.context_encoder = ViT(depth=encoder_depth, embed_dim=embed_dim)
        
        # Target encoder : encode les patches cibles (EMA du context encoder)
        self.target_encoder = ViT(depth=encoder_depth, embed_dim=embed_dim)
        self._init_target_encoder()
        
        # Predictor : prédit les embeddings des patches masqués
        self.predictor = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 4),
            nn.GELU(),
            *[TransformerBlock(embed_dim * 4) for _ in range(predictor_depth)],
            nn.Linear(embed_dim * 4, embed_dim),
        )
    
    def _init_target_encoder(self):
        """Initialise le target encoder comme copie du context encoder."""
        for param_t, param_c in zip(
            self.target_encoder.parameters(),
            self.context_encoder.parameters()
        ):
            param_t.data.copy_(param_c.data)
            param_t.requires_grad = False  # Pas de gradient sur le target
    
    def update_target_encoder(self, momentum=0.996):
        """EMA update du target encoder."""
        for param_t, param_c in zip(
            self.target_encoder.parameters(),
            self.context_encoder.parameters()
        ):
            param_t.data = momentum * param_t.data + (1 - momentum) * param_c.data
    
    def forward(self, x, mask):
        """
        Args:
            x: Tenseur d'entrée [B, C, H, W] ou [B, T, C, H, W]
            mask: Masque binaire [B, N] où N est le nombre de patches
        Returns:
            loss: Erreur de prédiction L2 dans l'espace latent
        """
        # Encoder le contexte (patches visibles)
        context_embeddings = self.context_encoder(x, mask=~mask)
        
        # Encoder les cibles (tous les patches)
        with torch.no_grad():
            target_embeddings = self.target_encoder(x, mask=None)
        
        # Prédire les embeddings des patches masqués
        predictions = self.predictor(context_embeddings)
        
        # Loss : L2 entre prédictions et cibles, uniquement sur patches masqués
        loss = F.mse_loss(
            predictions[mask],
            target_embeddings[mask]
        )
        return loss
```

### 5.2 Masquage par Blocs (I-JEPA)

```python
import random

def generate_block_mask(num_patches, aspect_ratio_scale=(0.75, 1.5), 
                        scale_scale=(0.15, 0.2), seed=None):
    """
    Génère un masque de blocs pour I-JEPA.
    On masque ~15-20% des patches en blocs contigus.
    
    Args:
        num_patches: Nombre total de patches
        aspect_ratio_scale: Échelle du ratio d'aspect du bloc
        scale_scale: Échelle de la taille du bloc (fraction)
    
    Returns:
        mask: Tenseur booléen [num_patches] — True = masqué
    """
    if seed is not None:
        random.seed(seed)
    
    mask = torch.zeros(num_patches, dtype=torch.bool)
    target_area = random.uniform(*scale_scale) * num_patches
    aspect_ratio = random.uniform(*aspect_ratio_scale)
    
    h = int(round((target_area * aspect_ratio) ** 0.5))
    w = int(round((target_area / aspect_ratio) ** 0.5))
    
    h = min(h, int(num_patches ** 0.5))
    w = min(w, int(num_patches ** 0.5))
    
    top = random.randint(0, int(num_patches ** 0.5) - h)
    left = random.randint(0, int(num_patches ** 0.5) - w)
    
    for i in range(top, top + h):
        for j in range(left, left + w):
            idx = i * int(num_patches ** 0.5) + j
            if idx < num_patches:
                mask[idx] = True
    
    return mask
```

### 5.3 Détection d'Anomalies avec I-JEPA

```python
class JEPAAnomalyDetector:
    """Détecteur d'anomalies basé sur l'erreur de prédiction JEPA."""
    
    def __init__(self, jepa_model, threshold_percentile=95):
        self.model = jepa_model
        self.threshold_percentile = threshold_percentile
        self.threshold = None
        self.normal_errors = []
    
    def fit_threshold(self, normal_images_loader):
        """Calibre le seuil sur des images normales."""
        self.model.eval()
        errors = []
        with torch.no_grad():
            for images in normal_images_loader:
                for _ in range(5):  # 5 masques aléatoires par image
                    mask = generate_block_mask(196)  # 14x14 patches
                    loss = self.model(images, mask)
                    errors.append(loss.item())
        
        self.threshold = torch.quantile(
            torch.tensor(errors), 
            self.threshold_percentile / 100
        )
        print(f"Seuil d'anomalie calibré : {self.threshold:.4f}")
    
    def predict(self, image, n_masks=10):
        """Détecte une anomalie sur une image.
        
        Returns:
            is_anomaly: bool
            confidence: score d'anomalie (0-1)
        """
        self.model.eval()
        errors = []
        with torch.no_grad():
            for _ in range(n_masks):
                mask = generate_block_mask(196, seed=_)
                loss = self.model(image.unsqueeze(0), mask)
                errors.append(loss.item())
        
        mean_error = sum(errors) / len(errors)
        confidence = min(mean_error / self.threshold, 1.0)
        is_anomaly = mean_error > self.threshold
        
        return is_anomaly, confidence
```

---

## 6. Checklist d'Implémentation

- [ ] Choisir la variante JEPA adaptée (I-JEPA pour images, V-JEPA pour vidéo)
- [ ] Collecter un dataset de données normales (pas besoin de labels)
- [ ] Pré-entraîner JEPA sur les données normales (ou utiliser un checkpoint pré-entraîné)
- [ ] Calibrer le seuil d'anomalie sur un set de validation normale
- [ ] Valider sur des anomalies connues (même en petit nombre)
- [ ] Déployer en inference (backbone gelé, forward pass uniquement)

---

## 7. Pièges Courants

1. **Confondre JEPA avec un modèle génératif** : JEPA ne génère pas de pixels. C'est un modèle prédictif dans l'espace latent. Ne pas s'attendre à ce qu'il remplisse les pixels manquants.

2. **Masquage trop petit** : Si on masque des patches isolés et non des blocs contigus, la tâche est trop facile → le modèle n'apprend rien de profond.

3. **Masquage spatial uniquement pour la vidéo** : Sans masquage temporel, la frame précédente/suivante donne la réponse → pas d'apprentissage.

4. **Données d'entraînement insuffisantes** : JEPA a besoin de diversité. Pour l'industrie, filmer plusieurs cycles de production sous différents éclairages/angles.

5. **Seuil d'anomalie non calibré** : Toujours calibrer le seuil sur un set de validation normal avant de déployer.

6. **Licence CC BY-NC (I-JEPA, V-JEPA, JEPA-WMS)** : Les checkpoints pré-entraînés Meta sont interdits en usage commercial. Stratégie de contournement : utiliser l'architecture (code open-source) et ré-entraîner from scratch sur données propriétaires. Voir `references/implementation-plans.md` section 2.1. Pour un déploiement sans contrainte de licence, préférer **EB-JEPA** (Apache 2.0).

7. **Accès web bloqué par les moteurs de recherche** : Google, Semantic Scholar et arXiv peuvent bloquer les requêtes automatisées (CAPTCHA, erreurs d'encodage). Utiliser le navigateur intégré avec `browser_console` pour extraire le contenu des pages rendues, ou les APIs directes (GitHub Raw, Hugging Face).

---

## 8. Références Complémentaires

- **`references/implementation-plans.md`** : Plans EB-JEPA & I-JEPA pour l'industrie
- **`references/jepa-2026-landscape.md`** : Positionnement JEPA dans l'écosystème IA 2026
  (Brain/Hands, Agent Skills, Context Engineering, Modèles)

## 9. Sources

- Papier I-JEPA : arXiv 2301.08243 (CVPR 2023)
- Papier V-JEPA : arXiv 2404.08471
- Papier EB-JEPA : arXiv 2602.03604
- Blog Meta AI I-JEPA : ai.meta.com/blog/yann-lecun-ai-model-i-jepa/ (Juin 2023)
- Blog Meta AI V-JEPA : ai.meta.com/blog/v-jepa-yann-lecun-ai-model-video-joint-embedding-predictive-architecture/ (Fév 2024)
- Code officiel V-JEPA : github.com/facebookresearch/jepa (PyTorch, licence CC BY-NC)
- Code EB-JEPA : github.com/facebookresearch/eb_jepa (PyTorch, licence Apache 2.0)
- Vision de Yann LeCun sur l'AMI : ai.meta.com/blog/yann-lecun-advancing-machine-intelligence/

## 9. Références

- [Plans d'implémentation EB-JEPA & I-JEPA](references/implementation-plans.md) — Setup, code, roadmap
- [Analyse d'applicabilité industrielle](references/industrial-applicability-analysis.md) — Classement des 7 variantes par cas d'usage