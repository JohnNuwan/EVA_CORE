---
name: jepa-self-supervised-learning
description: "Compétence niveau expert en JEPA (Joint Embedding Predictive Architecture) et apprentissage auto-supervisé avancé. Couvre JEPA, I-JEPA, V-JEPA, Image-BERT, MAE, DINO, iBOT, SimCLR, MoCo, BYOL, SwAV, contrastive learning, masked image modeling, self-distillation, et les fondements théoriques de l'apprentissage de représentations."
---

# JEPA et Apprentissage Auto-Supervisé Avancé

## Présentation

Compétence niveau expert couvrant l'ensemble du paysage de l'apprentissage auto-supervisé (SSL) pour la vision par ordinateur et au-delà. Inclut les architectures prédictives à plongement joint (JEPA), les méthodes contrastives, la distillation, le masquage d'images, et les fondements théoriques de l'apprentissage de représentations.

---

## 1. Architecture JEPA

### Fondements (Yann LeCun)

- **Joint Embedding Predictive Architecture (JEPA)** : cadre d'apprentissage auto-supervisé où un encodeur contextuel traite une vue partiellement masquée et un encodeur cible (EMA) traite l'image originale. Le prédicteur opère dans l'espace de plongement.
- **I-JEPA (Image)** : prédiction de plongements de patches masqués dans l'espace sémantique plutôt que dans l'espace pixel. Utilise un masquage stratégique de blocs, un encodeur cible EMA, et un prédicteur léger.
- **V-JEPA (Vidéo)** : extension à la vidéo avec prédiction spatio-temporelle. Capture la dynamique temporelle sans fine-tuning supervisé.
- **Spatial/Global/Region Prediction** : prédiction à différents niveaux de granularité spatiale.

### Composants Clés

- **Masquage Stratégique** : masquage par blocs de grande taille pour forcer l'apprentissage sémantique (vs masquage aléatoire de patches).
- **Target Encoder EMA** : mise à jour par moyenne mobile exponentielle du teacher pour stabiliser l'entraînement.
- **Régularisation Variance/Covariance** : VICReg (Variance-Invariance-Covariance Regularization) — maximise la variance des plongements dans un batch, minimise la covariance entre dimensions.
- **Stop-gradient** : technique clé pour éviter l'effondrement (collapse) des représentations.

---

## 2. Méthodes Contrastives

### SimCLR (Chen et al., 2020)

- Augmentation invariance via paires positives
- NT-Xent loss (Normalized Temperature-scaled Cross Entropy)
- Large batch sizes et projections non-linéaires
- Température scaling

### MoCo (He et al., 2020)

- **MoCo v1** : Momentum Contrast — queue dictionary et momentum encoder
- **MoCo v2** : améliorations SimCLR (MLP projection, plus d'augmentations)
- **MoCo v3** : extension à ViT avec batch normalization adapté

### Losses

- **InfoNCE loss** : Noise Contrastive Estimation — discrimination entre paires positives et négatives
- **NT-Xent** : Normalized Temperature-scaled Cross Entropy
- **Alignment and Uniformity** : métriques théoriques pour la qualité des représentations contrastives

---

## 3. Méthodes Basées sur la Distillation

### BYOL (Grill et al., 2020)

- **Bootstrap Your Own Latent** : pas de paires négatives
- Architecture online/target avec EMA
- Prédicteur supplémentaire pour éviter l'effondrement

### DINO (Caron et al., 2021)

- **DINO v1** : self-distillation avec Vision Transformers — centering et sharpening
- **DINO v2** (2023) : pré-entraînement à grande échelle avec régularisation iBOT, KoLeo, et résolution adaptative
- Caractéristiques patch-level pour segmentation et correspondance

### iBOT (Zhou et al., 2022)

- Masked Image Modeling avec distillation BYOL/DINO
- Prédiction de tokens masqués via MIM (Masked Image Modeling)
- Intègre les forces de la distillation et du masquage

### Mécanismes

- **Centering** : soustraction de la moyenne pour éviter un collapse trivial
- **Sharpening** : température faible pour rendre la distribution de sortie plus 'peak-y'
- **Momentum Teacher** : mise à jour lente du teacher pour stabilité

---

## 4. Méthodes Basées sur le Masquage

### MAE (He et al., 2022)

- **Masked Autoencoder** : masque aléatoire de 75% des patches, reconstruction dans l'espace pixel
- Encodeur asymétrique (ne voit que les patches visibles) + décodeur léger
- Efficacité computationnelle drastique

### Image-BERT / BEiT

- **BEiT** (Bidirectional Encoder representation from Image Transformers) : prédiction de tokens visuels discrets (dVAE)
- **BEiT v2** : tokeniseur appris vector-quantized
- **BEiT v3** (ImageBERT) : alignement image-texte

### Autres Méthodes

- **PeCo** : Perceptual Codebook via loss perceptuelle
- **data2vec** : cadre unifié vision/langage/audio avec auto-distillation
- **MaskFeat** : prédiction de caractéristiques HOG sur patches masqués

---

## 5. Fondements Théoriques

### Théorie de l'Apprentissage Contrastif

- **Optimisation InfoNCE** : estimation de l'information mutuelle (mutual information lower bound)
- **Spectral Contrastive Learning** : liens avec le clustering spectral et l'analyse en composantes principales
- **Graphe d'Augmentation** : théorie des chemins de similarité entre vues augmentées

### Éviter l'Effondrement

- **SimSiam** : démontre que stop-gradient seul peut prévenir l'effondrement sans paires négatives ni EMA
- Analyse du rôle de la prédiction par rapport à la symétrie

---

## 6. Applications et Transfert

### Évaluation

- **Linear Probing** : classifier linéaire sur représentations gelées
- **Fine-tuning** : adaptation complète sur tâche cible
- **Few-shot / Semi-supervised** : performance avec peu d'exemples étiquetés

### Domaines

- **Vidéo** : I-JEPA vidéo, V-JEPA, VideoMAE
- **Audio** : AudioMAE, data2vec audio, BYOL-Audio
- **3D** : Points clouds SSL — PointMAE, Point-BERT
- **Médical** : radiologie, pathologie, histologie
- **Satellite** : télédétection multi-spectrale

---

## 7. Références et Articles Clés

- **I-JEPA** : `Image-based Joint-Embedding Predictive Architecture` (Assran et al., 2023)
- **V-JEPA** : `Revisiting Feature Prediction for Visual Pre-Training` (Bardes et al., 2024)
- **DINO v2** : `DINOv2: Learning Robust Visual Features without Supervision` (Oquab et al., 2023)
- **MAE** : `Masked Autoencoders Are Scalable Vision Learners` (He et al., 2022)
- **SimCLR** : `A Simple Framework for Contrastive Learning of Visual Representations` (Chen et al., 2020)
- **MoCo v3** : `An Empirical Study of Training Self-Supervised Vision Transformers` (Chen et al., 2021)
- **BYOL** : `Bootstrap Your Own Latent — A New Approach to Self-Supervised Learning` (Grill et al., 2020)
- **data2vec** : `A General Framework for Self-supervised Learning in Speech, Vision and Language` (Baevski et al., 2022)
- **VICReg** : `VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning` (Bardes et al., 2022)

### Catégories

- `cs.LG` — Machine Learning
- `cs.CV` — Computer Vision and Pattern Recognition
- `cs.CL` — Computation and Language
- `cs.AI` — Artificial Intelligence
- `stat.ML` — Machine Learning (Statistics)