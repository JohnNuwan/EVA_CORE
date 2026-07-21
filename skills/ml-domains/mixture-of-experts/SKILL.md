---
name: mixture-of-experts
description: Guide complet des Mixture of Experts (MoE) — Switch Transformer, DeepSeek-V3, Mixtral, Expert Choice, load balancing, routage, implémentations. En français.
---

# Mixture of Experts (MoE) — Guide Complet

Architectures à experts, routage, load balancing, des fondamentaux aux modèles 2025.

---

## 1. Principe Fondamental

### Architecture générale

```
          Sortie
             ▲
             │
    ┌────────┴────────┐
    │   Routeur (Top-K)│  ← Gating
    └───┬─────────┬──┘
        │         │
   ┌────▼──┐ ┌───▼────┐
   │Expert1│ │Expert2│ ... ExpertN
   │ (FFN) │ │ (FFN) │
   └────┬──┘ └───┬────┘
        │         │
        └──┬──┬──┘
           ▼ ▼
    ┌──────────────┐
    │   Combinaison │  = Σ g_i · E_i(x)
    └──────────────┘
```

### Formulation mathématique
```
MoE(x) = Σ_{i=1}^{N} G(x)_i · E_i(x)

G(x) = softmax(TopK(x · W_g, k))   ← Gating/routage

TopK(v, k)_i = v_i si v_i dans top-k, -inf sinon
E_i(x) = FFN_i(x)
```

**Propriété clé** : seuls k experts sur N sont actifs par token.
- k = 2 (standard) : 2 experts sur 8 (25% de paramètres utilisés)
- Économie : ~4x plus de paramètres pour ~2x le compute

---

## 2. Routage (Gating)

### Softmax Router (standard)
```python
class SoftmaxRouter(nn.Module):
    """Routeur standard : softmax pondéré."""
    def __init__(self, d_model: int, n_experts: int, k: int = 2):
        super().__init__()
        self.d_model = d_model
        self.n_experts = n_experts
        self.k = k
        self.gate = nn.Linear(d_model, n_experts, bias=False)
    
    def forward(self, x: torch.Tensor):
        """x: (batch, seq_len, d_model)
        Retourne : weights (batch, seq_len, n_experts), indices (batch, seq_len, k)
        """
        logits = self.gate(x)  # (B, L, n_experts)
        
        # Top-K selection
        top_k_logits, top_k_indices = torch.topk(logits, self.k, dim=-1)
        
        # Weighted softmax (seulement sur les top-k)
        top_k_weights = F.softmax(top_k_logits.float(), dim=-1).type_as(x)
        
        return top_k_weights, top_k_indices
```

### Noisy Top-K Router (ajoute du bruit pour l'exploration)
```python
class NoisyTopKRouter(nn.Module):
    """Routeur avec bruit gaussien pour équilibrer la charge."""
    def __init__(self, d_model, n_experts, k=2, noise_std=0.1):
        super().__init__()
        self.w_gate = nn.Linear(d_model, n_experts, bias=False)
        self.w_noise = nn.Linear(d_model, n_experts, bias=False)
        self.k = k
        self.noise_std = noise_std
    
    def forward(self, x):
        logits = self.w_gate(x)
        noise = torch.randn_like(logits) * F.softplus(self.w_noise(x))
        noisy_logits = logits + noise * self.noise_std
        
        top_k_logits, indices = torch.topk(noisy_logits, self.k, dim=-1)
        weights = F.softmax(top_k_logits, dim=-1)
        return weights, indices
```

---

## 3. Load Balancing (Équilibrage de Charge)

### Problème : collapse des experts
```python
# Sans régularisation, le routeur apprend à toujours envoyer
# les tokens vers les mêmes 1-2 experts (collapse)
# → Les autres experts ne sont jamais entraînés
# → Gaspillage de paramètres
```

### Loss d'équilibrage (Switch Transformer)

```python
def load_balancing_loss(gate_logits, top_k_indices, n_experts):
    """Perte auxiliaire pour équilibrer la charge entre experts.
    
    Principe : chaque expert doit recevoir ~1/n_experts des tokens.
    """
    batch, seq_len, k = top_k_indices.shape
    n_tokens = batch * seq_len
    
    # Fraction de tokens assignés à chaque expert
    counts = torch.zeros(n_experts, device=gate_logits.device)
    for i in range(n_experts):
        counts[i] = (top_k_indices == i).sum().float()
    fraction_assigned = counts / (n_tokens * k)
    
    # Fraction de poids moyens (importance)
    weights = torch.zeros(n_experts, device=gate_logits.device)
    probs = F.softmax(gate_logits, dim=-1)
    for i in range(n_experts):
        weights[i] = probs[..., i].sum().float()
    fraction_weight = weights / n_tokens
    
    # Perte auxiliaire : produit des fractions (minimal si uniforme)
    aux_loss = n_experts * (fraction_assigned * fraction_weight).sum()
    return aux_loss
```

### Z-loss (DeepSeek-V3)
```python
# Perte de stabilisation du routage
# z_loss = 10^-4 · mean(gate_logits²)
# Empêche les logits de devenir trop grands
def z_loss(gate_logits):
    return 1e-4 * (gate_logits ** 2).mean()
```

### Loss totale
```python
loss = nll_loss + alpha * aux_loss + beta * z_loss
# alpha = 0.01 (Switch Transformer)
# beta = 0.001 (DeepSeek-V3)
```

---

## 4. Expert Choice (2022)

Innovation : au lieu du routeur choisir des experts pour chaque token (Token Choice), ce sont les experts qui choisissent les tokens.

```python
class ExpertChoiceRouter(nn.Module):
    """Expert Choice : chaque expert sélectionne ses tokens favoris.
    
    Avantage : contrôle parfait de la charge (load balancing garanti)
    """
    def __init__(self, d_model, n_experts, capacity_factor=1.25):
        super().__init__()
        self.gate = nn.Linear(d_model, n_experts)
        self.capacity = None  # = capacity_factor * n_tokens / n_experts
    
    def forward(self, x):
        # x: (batch, seq_len, d_model)
        logits = self.gate(x)  # (B, L, n_experts)
        
        scores_per_expert = logits.transpose(1, 2)  # (B, n_experts, L)
        
        # Chaque expert choisit top-k tokens
        # k = capacity = capacity_factor * L / n_experts
        top_k_scores, top_k_indices = torch.topk(
            scores_per_expert, self.capacity, dim=-1
        )
        
        return top_k_scores, top_k_indices
```

---

## 5. Switch Transformer (Google, 2021)

### Architecture
```python
class SwitchFFN(nn.Module):
    """Switch Transformer : Top-1 routing (k=1).
    Simplification extrême du routage.
    """
    def __init__(self, d_model, d_ff, n_experts=8):
        super().__init__()
        self.n_experts = n_experts
        self.router = SoftmaxRouter(d_model, n_experts, k=1)
        
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(d_model, d_ff),
                nn.ReLU(),
                nn.Linear(d_ff, d_model),
            )
            for _ in range(n_experts)
        ])
    
    def forward(self, x):
        weights, indices = self.router(x)  # chaque token → 1 expert
        weights = weights.squeeze(-1)      # (B, L)
        indices = indices.squeeze(-1)      # (B, L)
        
        output = torch.zeros_like(x)
        for expert_id, expert in enumerate(self.experts):
            mask = (indices == expert_id)
            if mask.any():
                expert_in = x[mask]
                expert_out = expert(expert_in)
                output[mask] += expert_out * weights[mask].unsqueeze(-1)
        
        return output
```

### Résultats : 7x plus de params, même compute
```python
# T5-Base : 220M paramètres
# Switch-Base : 220M paramètres par token (~7B total)
# Même FLOPs, mais 7x plus de paramètres
# → 2x plus performant que T5-Base
```

---

## 6. Mixtral 8x7B (Mistral, 2024)

```python
# Mixtral 8x7B : 46.7B paramètres au total
#                 12.9B paramètres actifs par token
# Top-2 routing sur 8 experts
# Chaque expert = FFN standard (SwiGLU)
# Architecture : LLaMA-like avec MoE

class MixtralMoE(nn.Module):
    """Block MoE de Mixtral."""
    def __init__(self, d_model=4096, d_ff=14336, n_experts=8, top_k=2):
        super().__init__()
        self.router = SoftmaxRouter(d_model, n_experts, k=top_k)
        
        self.experts = nn.ModuleList([
            FeedForward(d_model, d_ff) for _ in range(n_experts)
        ])
    
    def forward(self, x):
        B, L, D = x.shape
        weights, indices = self.router(x)  # (B, L, 2), (B, L, 2)
        
        output = torch.zeros_like(x)
        for i in range(self.top_k):
            # Contribution de l'expert i pour chaque token
            for expert_id, expert in enumerate(self.experts):
                mask = (indices[..., i] == expert_id)
                if mask.any():
                    output[mask] += expert(x[mask]) * weights[mask, i:i+1]
        
        return output


class FeedForward(nn.Module):
    """FFN SwiGLU (Mixtral style)."""
    def __init__(self, d_model, d_ff):
        super().__init__()
        self.w1 = nn.Linear(d_model, d_ff)
        self.w2 = nn.Linear(d_model, d_ff)
        self.w3 = nn.Linear(d_ff, d_model)
    
    def forward(self, x):
        return self.w3(F.silu(self.w1(x)) * self.w2(x))
```

---

## 7. DeepSeek-V3 (MoE, 2024-2025)

### Architecture
```python
# DeepSeek-V3 : 671B paramètres totaux, 37B actifs
# 256 experts fins + 1 shared expert
# Top-8 routing (256 experts)
# Fine-grained expert + shared expert isolation

# Innovations clés :
# 1. Multi-Token Prediction (MTP)
# 2. Multi-Head Latent Attention (MLA)
# 3. Auxiliary-loss-free load balancing
# 4. Node-limited routing
```

### Auxiliary-Loss-Free Load Balancing (DeepSeek-V3)
```python
# Au lieu d'une perte auxiliaire, DeepSeek-V3 utilise
# un biais dynamique par expert :
# b_i = b_i + γ · (f_i - f_target)

# Où f_i = fraction de tokens assignée à l'expert i
# f_target = top_k / n_experts
# γ = taux d'ajustement

class DynamicBiasBalancer:
    """Équilibrage sans perte auxiliaire."""
    def __init__(self, n_experts, top_k, gamma=0.001):
        self.biases = torch.zeros(n_experts)
        self.target = top_k / n_experts
        self.gamma = gamma
    
    def update(self, assignment_counts):
        # assignment_counts: nombre de tokens par expert
        total = assignment_counts.sum()
        for i in range(len(self.biases)):
            f_i = assignment_counts[i] / total
            self.biases[i] += self.gamma * (f_i - self.target)
        return self.biases
```

### Node-Limited Routing (économie réseau)
```python
# Principe : chaque token ne peut être routé que vers
# les experts présents sur max M nœuds (serveurs)
# → Réduit la communication inter-nœuds (all-to-all)
# → Améliore le throughput
```

---

## 8. Variantes et Innovations

### Fine-Grained Expert (DeepSeek-V2/V3)
```python
# Beaucoup d'experts fins : 64-256 experts au lieu de 8
# Chaque expert a moins de paramètres
# Plus de combinaisons possibles → meilleur routage
```

### Shared Expert Isolation (DeepSeek-V3)
```python
# 1 expert partagé (toujours actif) + experts fins (routés)
# Le shared expert capture la connaissance commune
# Les fins experts capturent la connaissance spécialisée
```

### DeepSeek-R1 (Raise-1, 2025)
```python
# Entraînement RL sur le modèle MoE
# Utilise GRPO (Group Relative Policy Optimization)
# Développe le « reasoning » par chaîne de pensée longue
# Le routage MoE permet à différentes chaînes de pensée
# de spécialiser différents experts
```

### Qwen2.5-MoE
```python
# 14.3B params actifs, 42B totaux
# Architecture : Qwen2.5 + MoE
# Top-8 routing sur 64 experts
```

---

## 9. Implémentation Complète

```python
class MoELayer(nn.Module):
    """Couche MoE complète avec équilibrage de charge."""
    def __init__(self, d_model: int, d_ff: int, n_experts: int = 8, 
                 top_k: int = 2, capacity_factor: float = 1.25):
        super().__init__()
        self.d_model = d_model
        self.d_ff = d_ff
        self.n_experts = n_experts
        self.top_k = top_k
        
        # Routeur
        self.router = SoftmaxRouter(d_model, n_experts, k=top_k)
        
        # Experts
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(d_model, d_ff),
                nn.GELU(),
                nn.Linear(d_ff, d_model),
            )
            for _ in range(n_experts)
        ])
        
        # Compteurs pour le load balancing
        self.register_buffer('expert_counts', torch.zeros(n_experts))
        self.register_buffer('total_tokens', torch.tensor(1))
    
    def forward(self, x: torch.Tensor):
        B, L, D = x.shape
        n_tokens = B * L
        
        # Routage
        weights, indices = self.router(x)  # (B, L, k), (B, L, k)
        
        # Calcul de la perte auxiliaire
        aux_loss = self._compute_aux_loss(weights, indices)
        
        # Exécution des experts
        output = torch.zeros_like(x)
        for i in range(self.top_k):
            w_i = weights[..., i:i+1]  # (B, L, 1)
            idx_i = indices[..., i]    # (B, L)
            
            for expert_id, expert in enumerate(self.experts):
                mask = (idx_i == expert_id)
                if mask.any():
                    expert_in = x[mask]
                    output[mask] += expert(expert_in) * w_i[mask]
        
        return output, aux_loss
    
    def _compute_aux_loss(self, weights, indices):
        """Perte d'équilibrage Switch Transformer."""
        B, L, k = indices.shape
        n_tokens = B * L
        
        # Fraction de tokens par expert
        counts = torch.zeros(self.n_experts, device=weights.device)
        for i in range(self.n_experts):
            counts[i] = (indices == i).sum().float()
        f_assigned = counts / (n_tokens * k)
        
        # Poids moyen par expert (probabilité du routeur)
        f_weight = torch.zeros(self.n_experts, device=weights.device)
        # Approximation : on utilise les poids moyens des top-k
        f_weight = weights.mean(dim=(0, 1))
        
        return self.n_experts * (f_assigned * f_weight).sum()
```

---

## 10. Tableau Comparatif

| Modèle | Experts | Top-k | Actifs | Totaux | Coût FLOPs |
|--------|---------|-------|--------|--------|-----------|
| Switch-Base | 8 | 1 | 220M | ~7B | 1x |
| Switch-Large | 32 | 1 | 1.1B | ~37B | 1x |
| GShard | 2048 | 2 | 600M | 600B | 1x |
| Mixtral 8x7B | 8 | 2 | 12.9B | 46.7B | 2x |
| DeepSeek-V2 | 160 | 6 | 21B | 236B | ~3x |
| DeepSeek-V3 | 257 | 8 | 37B | 671B | ~5x |
| Qwen2.5-MoE | 64 | 8 | 14.3B | 42B | ~2x |

---

## 11. Inférence avec MoE

```python
# Défis :
# 1. Communication inter-GPU (all-to-all pour chaque couche MoE)
# 2. Déséquilibre de charge : certains GPU plus chargés
# 3. Memory bandwidth : tous les experts doivent tenir en mémoire

# Solutions :
# - Expert Parallelism : chaque GPU a une partie des experts
# - Capacity-aware scheduling
# - Pipeline parallelism pour les tokens vers plusieurs experts

# DeepSeek-V3 inférence :
# 1. MLA layers : tensor parallelism
# 2. MoE layers : expert parallelism + data parallelism
# 3. Dynamic adjustment du capacity factor
```

---

## Références

- Outrageously Large Neural Networks (MoE original) : https://arxiv.org/abs/1701.06538
- Switch Transformers : https://arxiv.org/abs/2101.03961
- GShard : https://arxiv.org/abs/2006.16668
- Mixtral of Experts : https://arxiv.org/abs/2401.04088
- DeepSeek-V2 : https://arxiv.org/abs/2405.04434
- DeepSeek-V3 : https://arxiv.org/abs/2412.19437
- DeepSeek-R1 : https://arxiv.org/abs/2501.12948
- Expert Choice : https://arxiv.org/abs/2202.09368
- ST-MoE : https://arxiv.org/abs/2202.08906
- MegaBlocks : https://arxiv.org/abs/2211.15841 (efficient MoE implementation)