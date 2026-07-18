---
name: machine-learning-research
description: >-
  Compétence professionnelle en recherche en apprentissage automatique suivie
  sur arXiv. Couvre le deep learning, la théorie de l'apprentissage statistique,
  les architectures neuronales, l'apprentissage de représentations,
  l'optimisation, la généralisation, et les fondements de l'IA/ML à travers
  les catégories cs.LG et stat.ML.
category: research
---

# Compétence en Recherche en Apprentissage Automatique (cs.LG / stat.ML)

## Présentation

L'apprentissage automatique sur arXiv couvre deux catégories principales avec environ 1 000+ nouvelles soumissions par semaine (cs.LG : ~1 034 entrées/semaine, stat.ML : ~150 entrées/semaine). Cette compétence fournit une structure pour naviguer, évaluer et synthétiser la recherche en ML.

## Domaines de Recherche Principaux

### 1. Architectures de Deep Learning
**Densité arXiv** : Très élevée (cs.LG principal)

- **Transformers** : Mécanismes d'attention, attention efficace, modèles à long contexte, compression de cache KV (ex : DepthWeave-KV, FreqDepthKV)
- **Réseaux de neurones graphiques** : Attention sur graphes, méthodes spectrales, transformeurs de graphes (ex : Graph Convolutional Attention)
- **Réseaux convolutifs** : CNN modernes, ConvNext, architectures efficaces
- **Recherche d'architectures neuronales** : NAS différentiable, méthodes évolutionnaires
- **Mixture of Experts** : MoE sparse, stratégies de routage, équilibrage de charge
- **Modèles à espace d'états** : Mamba, S4, alternatives récurrentes à l'attention

### 2. Apprentissage de Représentations
- **Apprentissage auto-supervisé** : Méthodes contrastives (SimCLR, MoCo), modélisation masquée (MAE)
- **Apprentissage de variétés** : Plongements par chemins d'entropie maximale (EntroPath), UMAP, t-SNE
- **Démêlage (disentanglement)** : Représentations désintriquées, mécanismes indépendants
- **Espaces de plongement** : Apprentissage métrique, plongements hyperboliques

### 3. Théorie de l'Apprentissage Statistique
**Densité arXiv** : Élevée (stat.ML principal, cs.LG secondaire)

- **Bornes de généralisation** : PAC-Bayes, dimension VC, complexité de Rademacher
- **Noyau tangent neuronal (NTK)** : Régime NTK, apprentissage paresseux, apprentissage de caractéristiques
- **Limites de processus gaussiens** : Programmes de tenseurs, limites de largeur infinie
- **Analyse de convergence** : Dynamique de descente de gradient, paysage de perte
- **Apprentissage robuste en largeur** : Réseaux bayésiens mean-field, lois d'échelle

### 4. ML Bayésien et Probabiliste
- **Réseaux de neurones bayésiens** : VI mean-field, ensembles profonds, approximation de Laplace
- **Processus gaussiens** : Conception de noyaux, GP passant à l'échelle, deep GPs
- **Problèmes inverses bayésiens** : Approximation convexe pour vraisemblances neuronales
- **Inférence variationnelle** : Flows normalisants, VAE, inférence par diffusion
- **Quantification d'incertitude** : Prédiction conforme, ensembles de crédibilité

### 5. Optimisation pour le ML
**Densité arXiv** : Élevée (cs.LG + math.OC)
- **Méthodes du premier ordre** : SGD, Adam, AdamW, méthodes adaptatives, préconditionnement
- **Méthodes du second ordre** : K-FAC, Shampoo, méthodes de type Newton
- **Planifications de taux d'apprentissage** : Cosinus, warmup, LR cyclique
- **Régularisation** : Weight decay, dropout, stochastic depth
- **Normalisation** : Batch norm, layer norm, RMS norm, normalisation adaptive

### 6. Méthodes à Noyau et Réseaux de Diffusion
- **Réseaux de diffusion** : Diffusion de Mallat, capacité de séparation sur données de faible dimension
- **RKHS** : Conception de noyaux, caractéristiques aléatoires, approximation de Nyström
- **Méthodes spectrales** : Matrices aléatoires en ML, clustering spectral
- **Laplaciens de graphes** : Convergence des laplaciens de graphes avec divergence symétrique

### 7. Apprentissage Continu et par Transfert
- **Oubli catastrophique** : Méthodes par régularisation, replay, architecture
- **Adaptation de domaine** : Adaptation non supervisée, adaptation sans source
- **Apprentissage few-shot** : Méta-apprentissage, méthodes basées sur les métriques
- **Retenir ou adapter** : Théorie de généralisation de l'apprentissage continu (stat.ML)

### 8. Modèles Génératifs
- **Modèles de diffusion** : Débruitage par diffusion, score matching, flow matching
- **GANs** : Dynamique d'entraînement, métriques d'évaluation
- **Modèles autorégressifs** : PixelCNN, Transformers pour la génération
- **Flows normalisants** : Architectures inversibles, flows continus

## Signal des Conférences (Champ Comments)
- **ICML**, **NeurIPS**, **ICLR** : Conférences ML de premier plan
- **COLT**, **AISTATS**, **UAI** : Théorie/statistiques
- **ECML**, **ACML**, **AAAI** : ML/IA général
- **Ateliers (Workshops)** : Ex : "ICML'26 Workshop RLxF"
- **Prépublication seulement** : Pas encore évalué par les pairs

## Tendances Récentes Notables (Mi-2026)
1. **Compression de cache KV** : Partage de profondeur, factorisation résiduelle inter-couches
2. **ML informé par la physique** : Solveurs d'EDP neuronaux, plongements informés par la physique
3. **Modèles de fondation pour graphes** : Modèles hétérographes pour applications scientifiques
4. **Désapprentissage de concepts** : Suppression de concepts de modèles entraînés (TILDE)
5. **Modèles de fondation pour séries temporelles** : Corpus multivariés à grande échelle
6. **Lois d'échelle** : Robustesse en largeur, limites des programmes de tenseurs

## Comment Effectuer la Veille
- **Scan hebdomadaire** : `/list/cs.LG/recent` (1 034 entrées/semaine — parcourir les titres)
- **Profondeur théorique** : `/list/stat.ML/recent` (150 entrées/semaine — plus ciblé)
- **Surveillance des cross-lists** : Articles dans cs.LG cross-listés de stat.ML, cs.AI, cs.CV, math.OC
- **Mots-clés à suivre** : "foundation model", "scaling", "attention", "transformer", "diffusion", "representation", "generalization"