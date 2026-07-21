---
name: mamba-ssm
description: Guide complet des State Space Models (SSM)— Mamba, S4, Mamba-2, sélection d'état, parallélisation, implémentations en PyTorch. En français.
---

# Mamba & State Space Models — Guide Complet

Des SSM fondationnels à Mamba-2, architectures alternatives aux Transformers.

---

## 1. Introduction aux State Space Models

### Représentation d'état continue

Un SSM (State Space Model) transforme une séquence d'entrée u(t) en sortie y(t) via un état latent h(t) :

```
h'(t) = A · h(t) + B · u(t)    (équation d'état)
y(t)  = C · h(t) + D · u(t)    (équation d'observation)

h(t) ∈ ℝ^N : état latent (dimension N)
u(t) ∈ ℝ^D : entrée
A ∈ ℝ^(N×N) : matrice d'évolution
B ∈ ℝ^(N×D) : matrice d'entrée
C ∈ ℝ^(D×N) : matrice de sortie
D ∈ ℝ^(D×D) : skip connection
```

### Discrétisation (pour traitement séquentiel)

```python
# SSM continu → discret via ZOH (Zero-Order Hold)
# Δ : pas de temps appris

def discretize(A, B, delta):
    """ZOH discrétization."""
    # A_bar = exp(Δ · A)
    # B_bar = (exp(Δ · A) - I) · A^(-1) · B
    
    I = torch.eye(A.size(-1))
    A_bar = torch.matrix_exp(delta.unsqueeze(-1) * A)
    B_bar = (A_bar - I) @ A.inverse() @ B
    return A_bar, B_bar

# Forme discrète :
# h_k = A_bar · h_{k-1} + B_bar · u_k
# y_k = C · h_k (+ D · u_k)
```

---

## 2. S4 — Structured State Space Sequence Model (2022)

### La découverte clé

Le S4 (Gu et al., 2022) montre qu'en structurant A comme une matrice de HiPPO (High-Order Polynomial Projection Operators), le SSM peut capturer des dépendances à très long terme.

```python
# Matrice HiPPO-LegS (décomposition)
# A_{nk} = -(2n+1)^(1/2) · (2k+1)^(1/2) pour n > k
# A_{nn} = -(n+1)
# A_{nk} = 0 pour n < k

# Propriété : permet la compression polynomiale de l'historique
# La matrice A contient l'équivalent d'un « window d'attention » structuré
```

### Normal Plus Low-Rank (NPLR) Parametrization

```python
# A = Λ - P·P^T (diagonale + rank-1)
# Permet le calcul O(N·L) au lieu de O(N²·L)

# Kernel convolutionnel explicite :
# K = (C·B, C·A·B, C·A²·B, ..., C·A^k·B)
# La sortie s'écrit : y = K * u (convolution 1D)
```

### Propriétés fondamentales

| Propriété | SSM Vanilla | S4 |
|-----------|------------|-----|
| Mémoire | Peu de tokens | Milliers de tokens |
| Parallélisation | Récursive | Convolution + récurrence |
| Long-range capture | ✗ | ✓✓✓ |
| Entraînement stable | ✗ | ✓ |

---

## 3. S5 — Simplification du S4 (2022)

```python
# S4 : A est structurée (diagonale + low-rank)
# S5 : A complètement diagonale (pas de HiPPO séparé)
# → Plus simple, plus rapide, aussi performant

# Avantage : pas de HiPPO kernel computation
# A = diag(λ_1, ..., λ_N)
```

---

## 4. Mamba — S4 avec Sélection d'État (Gu & Dao, 2023)

### L'innovation : paramètres dépendants de l'entrée

```
# SSM traditionnel : (A, B, C, Δ) fixes pour toute la séquence
# Mamba : (B, C, Δ) = f(x_t) — fonctions de l'entrée !
# A reste fixe (stabilité), mais B, C, Δ varient par token

# Cela fait de Mamba un « attention-like » :
# - Chaque token choisit quels tokens passés écouter (sélection)
# - Mais en O(n) au lieu de O(n²)
```

### Architecture Mamba

```
┌─────────────────────────────────────┐
│            Entrée x                  │
│              │                       │
│    ┌─────────┴─────────┐             │
│    │   Linear (expand)  │             │
│    └─────────┬─────────┘             │
│              │                       │
│    ┌─────────┴─────────┐             │
│    │   Conv1D (s)       │  ← causal conv locale
│    └─────────┬─────────┘             │
│              │                       │
│    ┌─────────┴─────────┐             │
│    │   SiLU activation  │            │
│    └─────────┬─────────┘             │
│              │                       │
│    ┌─────────┴─────────┐             │
│    │   SSM (S6)         │  ← sélection par token
│    └─────────┬─────────┘             │
│              │                       │
│    ┌─────────┴─────────┐             │
│    │   Linear (project) │            │
│    └─────────┬─────────┘             │
│              │                       │
│    ┌─────────┴─────────┐             │
│    │   + Residual      │             │
│    └─────────────────────┘             │
└─────────────────────────────────────┘
```

### Implémentation du SSM sélectif (S6)

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class SelectiveSSM(nn.Module):
    """Mamba S6 — Selective State Space Model.
    
    La différence clé : Δ, B, C sont des fonctions du token x_t.
    """
    def __init__(self, d_model: int, d_state: int = 16):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        
        # Paramètres fixes (pas dépendants de l'entrée)
        # A est log-spaced (stabilité numérique)
        self.A_log = nn.Parameter(torch.log(
            torch.arange(1, d_state + 1, dtype=torch.float32)
        ).unsqueeze(0).repeat(d_model, 1))  # (d_model, d_state)
        
        # D (skip connection)
        self.D = nn.Parameter(torch.ones(d_model))
        
        # Projections dépendantes de l'entrée
        self.dt_proj = nn.Linear(d_model, d_model, bias=True)   # log Δ
        self.B_proj = nn.Linear(d_model, d_state, bias=False)   # B(x)
        self.C_proj = nn.Linear(d_model, d_state, bias=False)   # C(x)
    
    def forward(self, x: torch.Tensor):
        """x: (batch, seq_len, d_model)"""
        batch, seq_len, _ = x.shape
        
        # Paramètres dépendants de l'entrée
        delta = F.softplus(self.dt_proj(x))  # (B, L, D)
        B = self.B_proj(x)  # (B, L, D_state)
        C = self.C_proj(x)  # (B, L, D_state)
        A = -torch.exp(self.A_log)  # (D, D_state) — négatif pour stabilité
        
        # Discrétisation: A_bar = exp(Δ·A)
        delta_A = delta.unsqueeze(-1) * A  # (B, L, D, D_state)
        
        # Scan récurrent (version naïve — O(n) séquentiel)
        # En pratique : scan parallèle (associative scan)
        h = torch.zeros(batch, self.d_model, self.d_state, device=x.device)
        outputs = []
        
        for t in range(seq_len):
            delta_t = delta[:, t, :]  # (B, D)
            B_t = B[:, t, :]         # (B, D_state)
            C_t = C[:, t, :]         # (B, D_state)
            x_t = x[:, t, :]         # (B, D)
            
            # Mise à jour d'état
            A_bar = torch.exp(delta_t.unsqueeze(-1) * A)  # (B, D, D_state)
            B_bar = (A_bar - 1) / A  # (B, D, D_state)
            
            h = h * A_bar + B_bar.unsqueeze(-1).transpose(-2, -1) * x_t.unsqueeze(-1)
            
            # Sortie
            y_t = (h @ C_t.unsqueeze(-1)).squeeze(-1)  # (B, D)
            y_t = y_t + self.D * x_t  # skip connection
            outputs.append(y_t)
        
        return torch.stack(outputs, dim=1)  # (B, L, D)
```

### Parallel Associative Scan

```python
# Le vrai Mamba utilise un scan parallèle (pas la boucle for ci-dessus)
# Principe : l'opérateur (a, b) ⊕ (a', b') = (a·a', a·b' + b)
# est associatif → peut être parallélisé avec un scan binaire
#
# Résultat : O(log n) étapes parallèles au lieu de O(n) séquentielles
# C'est ce qui rend Mamba entraînable efficacement

# Pscan — Parallel Scan :
def pscan(A, B):
    """
    A : (batch, seq_len, ...)  — les coefficients A_bar
    B : (batch, seq_len, ...)  — les coefficients B_bar * x
    Retourne h_0, h_1, ..., h_L où h_k = A_k·h_{k-1} + B_k
    
    Complexité parallèle : O(log n)
    """
    # implémentation binaire associative
    pass
```

---

## 5. Mamba-2 (2024)

### Améliorations

| Aspect | Mamba-1 | Mamba-2 |
|--------|---------|---------|
| SSM kernel | Hand-written CUDA | Triton-native |
| State dimension | d_state=16 | d_state=64-256 |
| SSM formulation | S6 (sélectif) | SSD (State Space Dual) |
| Alignement | Aucun | HuggingFace, transformers |
| Scalability | Limitée | Jusqu'à 3B+ |

### SSD — State Space Dual

```python
# Mamba-2 formule le SSM comme un produit matrice structurée
# SSM = produit entre une matrice semi-séparable (SSM) 
#       et une matrice de sélection (attention-like)
#
# y = (L ◦ S) · u
# Où L = matrice de masque causal (1 si i≥j)
#       S = matrice structurée semi-séparable
# 
# Cela unifie SSM et attention dans un même formalisme
```

```python
# Implémentation Mamba-2 (simplifiée)
class Mamba2(nn.Module):
    def __init__(self, d_model, d_state=64, expand=2):
        super().__init__()
        self.d_model = d_model
        self.d_inner = d_model * expand
        self.d_state = d_state
        
        self.in_proj = nn.Linear(d_model, self.d_inner * 2, bias=False)
        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False)
        
        self.conv1d = nn.Conv1d(self.d_inner, self.d_inner, 
                                kernel_size=4, padding=3, groups=self.d_inner)
        self.norm = nn.RMSNorm(self.d_inner)
        
        # SSD parameters
        self.A = nn.Parameter(torch.empty(d_model, d_state).uniform_(0.1, 0.5))
        self.D = nn.Parameter(torch.ones(d_model))
    
    def forward(self, x):
        B, L, D = x.shape
        
        x_and_res = self.in_proj(x)
        x1, x2 = x_and_res.chunk(2, dim=-1)  # gate + main
        x1 = F.silu(x1)
        
        x2 = self.conv1d(x2.transpose(-1, -2))[..., :L].transpose(-1, -2)
        x2 = self.norm(x2)
        x2 = F.silu(x2)
        
        # SSD computation (structure semi-séparable)
        y = self.ssd_forward(x2)  # parallel structured matrix multiply
        
        y = y * x1  # gating
        return self.out_proj(y)
```

---

## 6. Comparaison Transformers vs Mamba

| Propriété | Transformers | Mamba (SSM) |
|-----------|-------------|-------------|
| **Complexité** | O(n²) | O(n) |
| **Qualité pré-training** | ★★★★★ | ★★★★☆ |
| **Long-range (>64K)** | ✓✓ (avec FA) | ✓✓✓ (naturel) |
| **Inférence (streaming)** | Cache KV O(n) | État O(1) — constant |
| **Inférence throughput** | ~2000 tok/s (7B) | ~3000 tok/s (7B) |
| **Parallélisation** | Oui (attention) | Oui (associative scan) |
| **Expressivité** | Très haute | Haute |
| **Recalage sur préférences** | Facile (format existant) | Moins standard |

### Benchmarks Long-Range Arena (LRA)

```python
# LRA : benchmark de dépendances longues
# Dataset (ListOps, Text, Retrieval, Image, Pathfinder)

# Résultats (accuracy) :
# Transformer (standard)  : ~55%
# Transformer + Performer: ~57%
# S4                    : ~86%  
# Mamba                 : ~82-85%
# Mamba-2               : ~84-87%
```

---

## 7. Implémentation Complète Mamba Block

```python
class MambaBlock(nn.Module):
    """Block Mamba complet prêt pour un réseau profond."""
    def __init__(self, d_model: int, d_state: int = 16, expand: int = 2):
        super().__init__()
        d_inner = d_model * expand
        
        self.norm = nn.LayerNorm(d_model)
        self.ssm = SelectiveSSM(d_inner, d_state)
        
        # Projections
        self.in_proj = nn.Linear(d_model, d_inner * 2, bias=False)
        self.out_proj = nn.Linear(d_inner, d_model, bias=False)
        
        # Convolution
        self.conv = nn.Conv1d(d_inner, d_inner,
                              kernel_size=4, groups=d_inner,
                              padding=3, bias=False)
    
    def forward(self, x: torch.Tensor):
        """x: (batch, seq_len, d_model)"""
        residual = x
        x = self.norm(x)
        
        # Projection d'entrée + gating
        x_proj = self.in_proj(x)
        x_main, x_gate = x_proj.chunk(2, dim=-1)
        x_gate = F.silu(x_gate)
        
        # Convolution 1D (locale)
        x_main = self.conv(x_main.transpose(-1, -2))[..., :x_main.size(1)]
        x_main = x_main.transpose(-1, -2)
        
        # SSM
        x_main = self.ssm(x_main)
        
        # Gating + projection de sortie
        y = F.silu(x_main) * x_gate
        y = self.out_proj(y)
        
        return y + residual


class MambaLM(nn.Module):
    """Modèle de langage complet basé Mamba."""
    def __init__(self, vocab_size: int, d_model: int = 768,
                 n_layers: int = 24, d_state: int = 16):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            MambaBlock(d_model, d_state) for _ in range(n_layers)
        ])
        self.norm_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
    
    def forward(self, tokens: torch.Tensor):
        x = self.embedding(tokens)
        for layer in self.layers:
            x = layer(x)
        x = self.norm_f(x)
        return self.lm_head(x)
    
    def generate(self, tokens, max_new=100):
        """Génération autoregressive (état O(1))."""
        for _ in range(max_new):
            logits = self.forward(tokens)
            next_token = logits[:, -1, :].argmax(dim=-1, keepdim=True)
            tokens = torch.cat([tokens, next_token], dim=-1)
        return tokens
```

---

## 8. Hybrides Mamba-Transformer

```
# Mamba + Attention mix
# Les couches basses : convolution + SSM (efficace)
# Les couches hautes : attention (expressivité)

# Exemple : Jamba (AI21 Labs, 2024)
# - Architecture hybride Mamba + Transformer
# - 1 couche attention toutes les 4 couches
# - Meilleur compromis efficacité/qualité

# Autres hybrides :
# - Zamba (Zyphra) : Mamba → attention → Mamba
# - Mamba-2-Hybrid : intermédiaire
# - Samba (Microsoft) : alternance Mamba + Sliding Window Attention
```

---

## Références

- Efficiently Modeling Long Sequences with S4 : https://arxiv.org/abs/2111.00396
- Mamba : Linear-Time Sequence Modeling with Selective State Spaces : https://arxiv.org/abs/2312.00752
- Mamba-2 : https://arxiv.org/abs/2405.21060
- S5 : Simplified State Space Layers : https://arxiv.org/abs/2208.04933
- HiPPO : Recurrent Memory with Optimal Polynomial Projections : https://arxiv.org/abs/2008.07669
- Jamba (AI21) : https://arxiv.org/abs/2403.19887
- Zamba : https://arxiv.org/abs/2405.16712
- Mamba officiel : https://github.com/state-spaces/mamba