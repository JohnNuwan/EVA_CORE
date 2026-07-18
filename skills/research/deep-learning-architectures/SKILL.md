---
name: deep-learning-architectures
description: "Compétence niveau expert en architectures deep learning avancées. Couvre les Transformers détaillés, State Space Models Mamba, Hyena, RWKV, ConvNets modernes, GNNs, Normalizing Flows, Diffusion Models, VAE, GANs, Mixture of Experts, efficient architectures (MobileNet, EfficientNet, TinyML), Neural Architecture Search, et les foundation models."
keywords: [deep learning, transformers, state space models, Mamba, diffusion models, GNN, mixture of experts, NAS]
categories: [cs.LG, cs.CV, cs.AI, cs.CL, stat.ML]
---

# Compétence Architectures Deep Learning Avancées

## Présentation

Cette compétence couvre en profondeur les architectures de deep learning modernes et avancées, des Transformers aux State Space Models en passant par les modèles génératifs, les GNNs et les architectures efficientes.

---

## Transformers Profonds

- **Attention Mechanisms** : Scaled dot-product, multi-head attention
- **Cross-Attention** : Mécanisme d'attention croisée encodeur-décodeur
- **Causal / Bidirectional** : Attention causale (decoding) vs bidirectionnelle (encoding)
- **Sparse Attention** : Attention éparse et factorisée (Longformer, BigBird)
- **Linear Attention** : Attention linéaire (Linear Transformers, Performer, FastFormer)
- **Flash Attention** : Algorithme IO-aware d'attention exacte plus rapide
- **RoPE (Rotary Position Embedding)** : Encodage positionnel rotatif
- **ALiBi** : Attention with Linear Biases pour longue contexte
- **QK-LayerNorm** : Normalisation des clés et requêtes
- **GQA (Grouped Query Attention)** : Attention par groupes de têtes (Llama 2/3)
- **MQA (Multi-Query Attention)** : Multi-Query Attention (PaLM)
- **MLA (Multi-head Latent Attention)** : Attention latente multi-tête (DeepSeek)
- **DeepSeek Attention** : Mécanismes spécifiques aux modèles DeepSeek
- **KV Cache** : Cache des clés/valeurs pour inférence efficace
- **Sliding Window Attention** : Fenêtre glissante pour longs contextes (Mistral)
- **Long Context** : YaRN, NTK-aware, Position Interpolation

## State Space Models

- **S4** : Structured State Space Sequence model
- **DSS** : Diagonal State Space
- **Mamba** : SSM sélectif avec hardware-aware parallel scan
- **Mamba-2** : Selective SSM v2 avec améliorations de stabilité
- **H3** : Hungry Hungry Hippos (hybrid SSM + attention)
- **Hyena Hierarchy** : Hiérarchie Hyena (long convolutions)
- **RWKV** : Modèle RNN-like avec entraînement parallélisable
- **Linear Attention Alternatives** : Alternatives à l'attention quadratique
- **Global Convolution** : Convolutions globales paramétriques
- **Structured Matrices** : Matrices structurées (Toeplitz, Cauchy, Vandermonde)
- **Diagonally Dominant / Complex Diagonal** : Structures de matrices SSM

## Efficient Architectures

- **MobileNet** : Convolutions depthwise-separable (MobileNetV1/V2/V3)
- **EfficientNet** : Scaling compound (width, depth, resolution)
- **ConvNeXt** : ConvNet modernisé avec design inspiré des ViT
- **Tiny ML / MCUNet** : Réseaux pour microcontrôleurs
- **Pruning** : Élagage de poids structuré et non-structuré
- **Quantization Aware Training (QAT)** : Entraînement avec quantification simulée
- **Knowledge Distillation** : Distillation de connaissances (teacher-student)
- **Neural Architecture Search (NAS)** : DARTS, ENAS, SPOS, Once-for-All

## Modèles Génératifs Profonds

- **Diffusion Models** : Score-matching, SDE/ODE probabiliste
- **DDPM** : Denoising Diffusion Probabilistic Models
- **DDIM** : Denoising Diffusion Implicit Models (échantillonnage accéléré)
- **Flow Matching** : Matching de flots pour génération continue
- **Rectified Flow** : Flots redressés (Stable Diffusion 3)
- **Consistency Models** : Modèles de cohérence (one-step generation)
- **VAE** : Variational Autoencoders (VQ-VAE, dVAE, beta-VAE)
- **GANs** : StyleGAN, BigGAN, Conditional GAN, Diffusion GAN

## Graph Neural Networks

- **MPNN (Message Passing Neural Network)** : Framework général des GNNs
- **GCN (Graph Convolutional Network)** : Convolution sur graphes (Kipf & Welling)
- **GAT (Graph Attention Network)** : Attention sur voisins du graphe
- **GraphSAGE** : Échantillonnage et agrégation pour grands graphes
- **GIN (Graph Isomorphism Network)** : Maximum de pouvoir expressif des MPNNs
- **Deep GNNs / Over-smoothing** : Problème du sur-lissage dans les GNNs profonds
- **JK-Net** : Jumping Knowledge pour GNNs profonds
- **Graph Transformers / GPS** : Transformers pour graphes avec encodage structurel
- **GraphGPS** : General, Powerful, Scalable Graph Transformer
- **Spectral GNNs** : GNNs basés sur le laplacien du graphe
- **Equivariant GNNs** : GNNs équivariants (SE(3), E(n))
- **Geometric Deep Learning** : Principes géométriques unifiés (Bronstein)

## Mixture of Experts

- **Sparse MoE** : Mélange d'experts éparse
- **Expert Choice** : Routage par choix des experts
- **TopK / Balanced Routing** : Routage Top-K avec équilibrage
- **Load Balancing Loss** : Pénalité d'équilibrage de charge entre experts
- **Capacity Factor** : Facteur de capacité pour la régulation batch
- **Switch Transformer** : MoE simplifié (un expert par token)
- **ST-MoE** : Stable Training of Mixture of Experts
- **DeepSeekMoE** : MoE fine-grained avec experts partagés
- **Fine-Grained MoE** : Routage fin avec plus d'experts plus petits
- **Shared Experts** : Experts partagés spécialisés (DeepSeekMoE)