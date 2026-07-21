---
name: attention-mecanismes
description: Guide complet des mécanismes d'attention — softmax, scalaire, croisée, flash, sparse, linéaire, FFT, multi-tâches, state-space. En français.
---

# Mécanismes d'Attention — Guide Complet

Tous les mécanismes d'attention : des fondamentaux aux avancées 2024-2025.

---

## 1. Fondements Mathématiques

### Scaled Dot-Product Attention
```
Attention(Q, K, V) = softmax(QKᵀ / √d_k) V

Q ∈ ℝ^(n×d_k) : Queries
K ∈ ℝ^(m×d_k) : Keys
V ∈ ℝ^(m×d_v) : Values
d_k : dimension des clés
```

```python
def scaled_dot_product_attention(Q, K, V, mask=None):
    """Attention scalaire avec produit matriciel.
    
    Args:
        Q: (batch, heads, seq_q, d_k)
        K: (batch, heads, seq_k, d_k)
        V: (batch, heads, seq_k, d_v)
        mask: (batch, 1, seq_q, seq_k) — booléen ou float(-inf)
    """
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))
    
    attn_weights = F.softmax(scores, dim=-1)
    output = torch.matmul(attn_weights, V)
    return output, attn_weights
```

### Pourquoi /√d_k ?
```python
# Sans scaling : var(QKᵀ) = d_k
# Pour d_k=512, les scores ont var=512
# Softmax devient extrêmement peaked (gradients ≈ 0)
# Avec /√d_k : var = 1, gradients sains
```

---

## 2. Taxonomie Complète

```
                        Attention
                       /    |    \
              Self-attention | Cross-attention
                    /    \        \
           Causal    Bidirectional  Enc-Dec
                    |
          +----+----+-------+--------+
          |    |    |       |        |
        Softmax  Linear  Sparse  Flash   Fourier
          |      (Linformer,  (Longformer,  (Dao 2022)
          |       Performer)  BigBird)
          |
      Multi-Head (MHA)
      Grouped-Query (GQA)
      Multi-Query (MQA)
```

---

## 3. Self-Attention (Intra-séquence)

### Bidirectionnelle (BERT)
```python
# Chaque token peut voir tous les tokens avant ET après
# Pas de masque causal
# Utile : compréhension, classification, NER
```

### Causale (GPT, LLaMA)
```python
# Chaque token ne voit que lui-même et les tokens précédents
# Masque triangulaire supérieur = -inf
def causal_mask(seq_len, device='cpu'):
    return torch.triu(
        torch.full((seq_len, seq_len), float('-inf'), device=device),
        diagonal=1,
    )
    # [[0, -inf, -inf, -inf],
    #  [0, 0, -inf, -inf],
    #  [0, 0, 0, -inf],
    #  [0, 0, 0, 0]]
```

### Prefix Mask (T5, ULM)
```python
# Les premiers tokens (prefix) ont une attention bidirectionnelle
# Les tokens suivants sont causals
# Utile : fine-tuning avec préfixe figé
```

---

## 4. Cross-Attention (Inter-séquences)

### Encoder-Decoder (T5, BART, Transformer original)
```python
class CrossAttention(nn.Module):
    """Q vient du decoder, K,V viennent de l'encoder."""
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
    
    def forward(self, decoder_hidden, encoder_output, mask=None):
        Q = self.q_proj(decoder_hidden)  # (B, T_dec, D)
        K = self.k_proj(encoder_output)  # (B, T_enc, D)
        V = self.v_proj(encoder_output)  # (B, T_enc, D)
        # ... attention softmax(QK^T/√d)V ...
```

### Cross-attention multimodale (LLaVA, Flamingo)
```python
# Q = tokens texte, K,V = tokens image (vision encoder)
# Permet au texte de « lire » les images
```

---

## 5. FlashAttention (Dao et al., 2022-2023-2024)

### FlashAttention v1 (NeurIPS 2022)
```python
# Principe : tiling + recomputation sans matériel custom
# 1. Divise Q, K, V en blocs qui tiennent dans SRAM (19KB par SM sur A100)
# 2. Calcule softmax en ligne (en blocs)
# 3. Accumule le résultat dans SRAM
# 4. Recompute forward durant le backward (pas de stash mémoire O(N²))

# Impact :
# - Mémoire : O(N) au lieu de O(N²) pour le calcul
# - 2-4x plus rapide que PyTorch standard
# - Supporte dropout, mask, causal
```

### FlashAttention v2 (2023)
```python
# Améliorations :
# 1. Réduction des lectures/écritures globales (less non-matmul FLOPs)
# 2. Meilleur séquencement des opérations
# 3. Séquences non-puissances-de-2
# ~2x plus rapide que FAv1
```

### FlashAttention v3 (2024, Hopper/H100)
```python
# Optimisé pour architecture Hopper :
# - WGMMA (Warp Group Matrix Multiply-Accumulate)
# - Async TMA (Tensor Memory Accelerator)
# - Pas de kernel Python, tout en PTX/SASS
# ~1.5-2x plus rapide que FAv2 sur H100
```

```python
# Utilisation pratique
import torch
from flash_attn import flash_attn_func

# Interface standard
# Q, K, V: (batch_size, seqlen, nheads, headdim)
out, lse, _ = flash_attn_func(
    q, k, v,
    dropout_p=0.0,
    softmax_scale=None,  # 1/sqrt(head_dim) par défaut
    causal=False,
    window_size=(-1, -1),  # (-1, -1) = full attention
    alibi=False,
    deterministic=False,
)

# Avec padding (sequences de longueurs variables)
from flash_attn import flash_attn_varlen_func
```

### FlashAttention Triton
```python
import triton
import triton.language as tl

@triton.jit
def flash_attention_kernel(Q, K, V, O, ...):
    # Implémentation Triton personnalisable
    # Plus lent que CUDA natif mais plus flexible
```

---

## 6. Attention Linéaire / Subquadratique

### Linformer (2020)
```python
# Projette K et V linéairement vers une dimension réduite (k << n)
# P = softmax(Q(K^T E)) / sqrt(d)  avec E: (n, k)
# Mémoire : O(nk) au lieu de O(n²)
```

### Performer (FAVOR+, 2020)
```python
# FAVOR+ : Fast Attention via Orthogonal Random Features
# Attention(Q,K) ≈ φ(Q)φ(K)ᵀ où φ est une feature map
# softmax(QKᵀ) ≈ φ(Q) · φ(K)ᵀ
# Résultat : attention linéaire O(n)

def favor_plus(Q, K, V, num_features=256):
    """Attention approximée par features aléatoires."""
    # φ(x) = h(x) · f(Wx + b)
    # où h(x)=exp(||x||²/2), f = exponetielle
    Q_prime = feature_map(Q, num_features)
    K_prime = feature_map(K, num_features)
    return (Q_prime @ (K_prime.transpose(-2, -1) @ V)) / n
```

### RWKV (2023) — Attention linéaire récurrente
```python
# Combine RNN (efficace) + Transformer (expressif)
# Attention linéaire basée sur le temps
# Récurrence : a_t = e^{-w} · a_{t-1} + e^{k_t} · v_t
# Sortie : o_t = W_o · (a_t / (e^{-w} · b_{t-1} + e^{k_t}))
```

---

## 7. Attention Sparse et Structurée

### Longformer (2020)
```python
# 3 types de motifs :
# 1. Fenêtre locale (sliding window, taille w)
# 2. Dilatation (trous dans la fenêtre)
# 3. Tokens globaux (attention complète sur quelques tokens)

# Complexité : O(L × w) vs O(L²)
```

### BigBird (2020)
```python
# 3 motifs combinés :
# 1. Fenêtre locale (w tokens de chaque côté)
# 2. Random (r tokens aléatoires)
# 3. Global (g tokens avec attention entière)
# Complexité : O(L × (w + r + g))
```

### ETC / LongT5 (2021)
```python
# Attention globale via des tokens side-car
# Ajoute n_sidetokens globaux avant la séquence
# Chaque token global peut voir toute la séquence
```

### Sparse Attention (OpenAI, 2019)
```python
# Motifs fixes : strided, fixed, compressed
# strided : un token sur k
# fixed : positions prédéterminées
```
---

## 8. Attention Croisée Avancée

### Cross-attention dans les systèmes multimodaux

```python
# Flamingo (DeepMind) : Perceiver Resampler
# Résout l'asynchronie vision-langage
# Vision encoder → Perceiver (apprend à « résumer » l'image)
# → Cross-attention avec GATED XATTN-DENSE

class GatedCrossAttention(nn.Module):
    """Cross-attention avec gate apprise (Flamingo)."""
    def __init__(self, d_model, n_heads):
        self.attn = MultiHeadAttention(d_model, n_heads)
        self.gate = nn.Parameter(torch.zeros(1, 1, d_model))
    
    def forward(self, lang_hidden, vision_hidden):
        x = self.attn(lang_hidden, vision_hidden, vision_hidden)
        return lang_hidden + torch.tanh(self.gate) * x
```

### Cross-attention pour RAG
```python
# Q = requête, K, V = documents retrievés
# Même mécanisme que encoder-decoder
# Fusionne la connaissance externe dans l'attention decoder
```

---

## 9. Attention Multi-Résolution

### Axial Attention (Google, 2019)
```python
# Pour images : attention séparée sur les axes H et W
# Au lieu de attention 2D O(H²W²), fait attention 
# sur les lignes puis sur les colonnes
# Complexité : O(H²W + HW²) au lieu de O(H²W²)
```

### Perceiver (DeepMind, 2021)
```python
# Architecture d'attention asymétrique
# 1. Projection du signal d'entrée via cross-attention
# 2. Traitement avec self-attention sur un latent réduit
# Complexité découplée de la taille d'entrée

class PerceiverBlock(nn.Module):
    def __init__(self, d_latent, n_latents=256):
        self.cross_attn = CrossAttention(d_latent, n_heads=8)
        self.self_attn = MultiHeadAttention(d_latent, n_heads=8)
    
    def forward(self, latent, data):
        latent = self.cross_attn(latent, data, data)
        latent = self.self_attn(latent, latent, latent)
        return latent
```

---

## 10. Mécanismes d'Attention Récente (2024-2025)

### Differential Attention (DIFF Transformer, 2024)
```python
# Remplace softmax(QK^T) par softmax(Q1K1^T) - λ · softmax(Q2K2^T)
# L'attention différentielle annule le bruit
# Permet des modèles plus profonds avec moins d'attention collapse
```

### MLA — Multi-head Latent Attention (DeepSeek-V2/V3)
```python
# Compresse Q, K, V dans un espace latent de dimension réduite
# Cache KV compressé : ~12.5% de la mémoire standard
# Maintient la qualité via une projection de reconstruction

class MultiHeadLatentAttention(nn.Module):
    """Attention avec KV latent compressé."""
    def __init__(self, d_model, n_heads, d_latent=512):
        # Compression KV
        self.W_kv_down = nn.Linear(d_model, d_latent)
        self.W_q_down = nn.Linear(d_model, d_latent)
        # Reconstruction
        self.W_k_up = nn.Linear(d_latent, d_model)
        self.W_v_up = nn.Linear(d_latent, d_model)
```

### Lizard Attention
```python
# Combinaison de plusieurs sparse patterns appris
# Chaque tête apprend son propre motif d'attention
```

### Contrastive Attention
```python
# Attention qui maximise la différence entre tokens pertinents et non-pertinents
# Inspiré du contrastive learning
```

---

## 11. Attention Caching et Optimisation

```python
# KV Cache — le secret de l'inférence rapide
class StreamingKVCache:
    """Cache KV avec gestion mémoire optimisée."""
    def __init__(self, max_batch_size, max_seq_len, n_layers, 
                 n_kv_heads, head_dim, dtype=torch.float16):
        shape = (max_batch_size, max_seq_len, n_kv_heads, head_dim)
        self.k_cache = [torch.zeros(shape, dtype=dtype) for _ in range(n_layers)]
        self.v_cache = [torch.zeros(shape, dtype=dtype) for _ in range(n_layers)]
        self.valid_positions = 0
    
    def update(self, layer_id, k, v):
        B, T, H, D = k.shape
        assert T == 1  # décodage autoregressif
        self.k_cache[layer_id][:, self.valid_positions] = k.squeeze(1)
        self.v_cache[layer_id][:, self.valid_positions] = v.squeeze(1)
        self.valid_positions += 1
        return (self.k_cache[layer_id][:, :self.valid_positions],
                self.v_cache[layer_id][:, :self.valid_positions])
```

---

## 12. Tableau Comparatif

| Mécanisme | Complexité | Mémoire | Qualité | Année |
|-----------|-----------|---------|---------|-------|
| MHA (full) | O(n²) | O(n²) | ★★★★★ | 2017 |
| FlashAttn v1 | O(n²) | O(n) | ★★★★★ | 2022 |
| FlashAttn v2 | O(n²) | O(n) | ★★★★★ | 2023 |
| Linformer | O(nk) | O(nk) | ★★★☆☆ | 2020 |
| Performer | O(n) | O(n) | ★★★☆☆ | 2020 |
| Longformer | O(nw) | O(nw) | ★★★★☆ | 2020 |
| RWKV | O(n) | O(n) | ★★★★☆ | 2023 |
| MLA (DeepSeek) | O(n²) | O(n) | ★★★★★ | 2024 |
| Differential | O(n²) | O(n²) | ★★★★★ | 2024 |

---

## Références

- Attention Is All You Need : https://arxiv.org/abs/1706.03762
- FlashAttention : https://arxiv.org/abs/2205.14135
- FlashAttention v2 : https://arxiv.org/abs/2307.08691
- FlashAttention v3 : https://arxiv.org/abs/2407.08608
- Linformer : https://arxiv.org/abs/2006.04768
- Performer : https://arxiv.org/abs/2009.14794
- Longformer : https://arxiv.org/abs/2004.05150
- BigBird : https://arxiv.org/abs/2007.14062
- RWKV : https://arxiv.org/abs/2305.13048
- DeepSeek-V2 MLA : https://arxiv.org/abs/2405.04434
- DIFF Transformer : https://arxiv.org/abs/2410.05258
- Perceiver : https://arxiv.org/abs/2103.03206