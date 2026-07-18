---
name: lie-algebra-based-agent-attention
description: "Implémenter des mécanismes d'attention pour agents utilisant l'algèbre de Lie sur des groupes de matrices (SE(2), SO(3)) pour améliorer l'efficacité et la précision des modèles géométriques."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [lie-algebra, attention, geometric-deep-learning, se2, so3, machine-learning, transformers]
    related_skills: [ai-foundations-exploration, spatial-decodable-image-generation, persistent-world-model-design]
---

# Attention par Algèbre de Lie pour Agents Autonomes

## Vue d'ensemble

Cette compétence applique les **groupes de Lie matriciels** (SE(2), SO(3), Aff(2)) aux mécanismes d'attention des transformers et des systèmes multi-agents. L'idée fondamentale est de traiter chaque jeton (token) comme un **élément d'un groupe de Lie** plutôt que comme un vecteur dans un espace euclidien. Cette approche permet de capturer naturellement les invariances et les symétries géométriques des données, réduisant la paramétrisation tout en améliorant la précision sur des tâches structurées spatialement.

Basé sur l'article : [The Token Is a Group Element: On Lie-Algebra Attention over Matrix Lie Groups](https://arxiv.org/abs/2606.20547)

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'implémenter un mécanisme d'attention géométrique pour des données structurées (pose, mouvement, graphes).
- D'améliorer un modèle de vision ou robotique avec des invariances de groupe explicites.
- De réduire le nombre de paramètres d'un transformer tout en maintenant sa précision.
- D'explorer des architectures d'attention alternatives basées sur la géométrie différentielle.

---

## 1. Fondements Mathématiques

### 1.1 Groupes de Lie Matriciels

| Groupe | Dimension | Description | Usage |
|:---|:---|:---|:---|
| **SO(2)** | 1 | Rotations 2D | Navigation, pose 2D |
| **SE(2)** | 3 | Rotations + translations 2D | Robot mobile, AGV |
| **SO(3)** | 3 | Rotations 3D | Drone, bras robotique |
| **SE(3)** | 6 | Rotations + translations 3D | SLAM, manipulation |
| **Aff(2)** | 6 | Transformations affines 2D | Vision, calibration |

### 1.2 Principe de l'Attention sur Groupe de Lie

Au lieu de calculer l'attention entre vecteurs `q_i` et `k_j` avec un produit scalaire, on représente les jetons comme des éléments de groupe `g_i, g_j ∈ G` et on calcule la similarité via la **distance géodésique** sur le groupe :

```
s_ij = -||log(g_i⁻¹ g_j)||² / τ
```

Où :
- `g_i, g_j` sont les éléments de groupe (matrices de transformation).
- `log(·)` est l'application logarithme qui projette le groupe vers son algèbre de Lie.
- `||·||` est la norme de Frobenius sur l'algèbre de Lie.
- `τ` est la température d'attention.

---

## 2. Implémentation

### 2.1 Calcul de l'Attention sur SE(2)

```python
import torch
import torch.nn as nn

class LieAttentionSE2(nn.Module):
    """Mécanisme d'attention utilisant l'algèbre de Lie SE(2)."""

    def __init__(self, dim: int = 128, temperature: float = 1.0):
        super().__init__()
        self.temperature = temperature
        # Projection vers les paramètres du groupe SE(2)
        self.to_group = nn.Linear(dim, 3)  # (x, y, theta)

    def se2_log(self, g: torch.Tensor) -> torch.Tensor:
        """Logarithme du groupe SE(2) vers l'algèbre Lie SE(2).
        
        Args:
            g: Tenseur (B, N, 3) représentant (x, y, theta)
        
        Returns:
            Tenseur (B, N, 3) dans l'algèbre de Lie
        """
        theta = g[..., 2:3]
        sin_t = torch.sin(theta)
        cos_t = torch.cos(theta)
        
        # Matrice de passage pour la partie translation
        # V = (sin(theta)/theta, (1-cos(theta))/theta) pour theta ≠ 0
        theta_norm = torch.norm(theta, dim=-1, keepdim=True).clamp(min=1e-8)
        v1 = sin_t / theta_norm
        v2 = (1.0 - cos_t) / theta_norm
        
        # Application aux translations
        tx = g[..., 0:1]
        ty = g[..., 1:2]
        ux = v1 * tx - v2 * ty
        uy = v2 * tx + v1 * ty
        
        return torch.cat([ux, uy, theta], dim=-1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Calcule l'attention géométrique sur SE(2).
        
        Args:
            x: Tenseur d'entrée (B, N, dim)
        
        Returns:
            Tenseur de sortie (B, N, dim)
        """
        B, N, _ = x.shape
        
        # Projection vers le groupe SE(2)
        g = self.to_group(x)  # (B, N, 3)
        
        # Calcul des distances géodésiques entre toutes les paires
        g_i = g.unsqueeze(2)   # (B, N, 1, 3)
        g_j = g.unsqueeze(1)   # (B, 1, N, 3)
        
        # Différence de groupe : g_i^(-1) * g_j approximé
        d_theta = g_j[..., 2] - g_i[..., 2]
        dx = g_j[..., 0] - g_i[..., 0]
        dy = g_j[..., 1] - g_i[..., 1]
        
        # Métrique d'attention géométrique
        log_diff = torch.stack([dx, dy, d_theta], dim=-1)
        distances = -torch.norm(log_diff, dim=-1).pow(2) / self.temperature
        
        # Softmax
        attention = torch.softmax(distances, dim=-1)
        
        # Agrégeation pondérée
        return torch.matmul(attention, x)
```

### 2.2 Intégration dans un Transformer Standard

```python
class LieTransformerLayer(nn.Module):
    """Couche Transformer où l'attention utilise SE(2) Lie group."""

    def __init__(self, dim: int = 128, n_heads: int = 4):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        
        self.lie_attentions = nn.ModuleList([
            LieAttentionSE2(self.head_dim) for _ in range(n_heads)
        ])
        self.proj = nn.Linear(dim, dim)
        self.ffn = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.ReLU(),
            nn.Linear(dim * 4, dim),
        )
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Attention multi-tête Lie
        B, N, D = x.shape
        h = x.view(B, N, self.n_heads, self.head_dim)
        h_out = []
        for i in range(self.n_heads):
            h_out.append(self.lie_attentions[i](h[:, :, i, :]))
        h = torch.cat(h_out, dim=-1)
        x = x + self.proj(h)
        x = self.norm1(x)
        
        # FFN
        x = x + self.ffn(x)
        x = self.norm2(x)
        return x
```

---

## 3. Applications aux Agents Autonomes

| Application | Groupe | Bénéfice |
|:---|:---|:---|
| **Navigation AGV** | SE(2) | Attention invariant à la rotation du robot |
| **Estimation de pose drone** | SE(3) | Meilleure précision que l'attention euclidienne |
| **Manipulation robotique** | SO(3) | Prise en compte naturelle des rotations du bras |
| **SLAM visuel** | SE(3) | Covisibilité entre frames + poses |

---

## 4. Pièges Courants

1. **Singularités du logarithme :**
   - *Erreur* : Pour les rotations proches de π (180°), le logarithme a une singularité.
   - *Correction* : Utilisez un epsilon de clamp et une approximation stable.

2. **Normalisation incorrecte :**
   - *Erreur* : Les gradients explosent si la distance géodésique n'est pas correctement normalisée.
   - *Correction* : Normalisez par la dimension du groupe et la température τ.

3. **Initialisation des paramètres du groupe :**
   - *Erreur* : Des poids aléatoires produisent des transformations incohérentes.
   - *Correction* : Initialisez les biais pour produire l'identité du groupe.

---

## Liste de vérification

- [ ] Le groupe de Lie est correctement choisi (SE(2), SO(3), SE(3)) selon la nature des données.
- [ ] L'application logarithme est stable numériquement (clamp, epsilon).
- [ ] La température d'attention τ est configurable et ajustée.
- [ ] La sortie de l'attention est correctement normalisée.
- [ ] Les gradients sont stables (vérifié sur une forward/backward pass).
- [ ] Les performances sont comparées à une baseline d'attention euclidienne standard.
