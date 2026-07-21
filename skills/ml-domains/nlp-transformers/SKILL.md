---
name: nlp-transformers
description: Use when working with Transformer architecture internals — attention mechanisms (scaled dot-product, multi-head, cross-attention, Flash Attention), positional encoding (sinusoidal, RoPE, ALiBi, relative), normalization, feed-forward, architecture variants, et implémentation from scratch.
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [nlp, transformers, attention, multi-head, positional-encoding, rope, alibi, flash-attention, architecture]
    related_skills: [nlp-bert, nlp-gpt, nlp-t5, nlp-seq2seq, transformers-avance, llm]
---

# Transformers — Architecture et Mécanismes d'Attention

## Vue d'ensemble

L'architecture Transformer (Vaswani et al., 2017, "Attention Is All You Need") est le fondement de tous les modèles NLP modernes. Sa contribution centrale est le mécanisme d'attention, qui permet de capturer les dépendances entre tous les tokens d'une séquence sans récurrence.

Ce skill couvre en détail : l'attention multi-tête, les positional encodings, la normalisation, les blocs feed-forward, les variantes modernes (Flash Attention, GQA, MQA, Sliding Window), l'implémentation from scratch, et les optimisations.

## Quand l'utiliser

- Vous implémentez un Transformer from scratch (projet pédagogique ou recherche)
- Vous voulez comprendre les mécanismes d'attention en profondeur
- Vous optimisez un Transformer existant (Flash Attention, GQA)
- Vous comparez différentes architectures (full attention, sliding window, sparse)
- Vous déboguez des problèmes d'attention (attention collapse, position non capturée)

## Mécanisme d'Attention

### Scaled Dot-Product Attention

**Formule :**
```
Attention(Q, K, V) = softmax(Q · K^T / √d_k) · V
```

**Implémentation :**
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q, K, V: [batch, heads, seq_len, d_k]
    """
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    attn_weights = F.softmax(scores, dim=-1)
    output = torch.matmul(attn_weights, V)
    return output, attn_weights
```

**Complexité :** `O(N² · d_k)` — quadratique en la longueur de séquence N. C'est le goulot d'étranglement des Transformers.

### Multi-Head Attention

**Principe :** h têtes d'attention en parallèle, chacune apprenant des relations différentes.

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.1):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_k = d_model // n_heads
        self.n_heads = n_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        batch, seq_len, _ = x.shape

        # Projection et reshape : [batch, seq, d_model] → [batch, n_heads, seq, d_k]
        Q = self.W_q(x).view(batch, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(x).view(batch, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(x).view(batch, seq_len, self.n_heads, self.d_k).transpose(1, 2)

        # Attention
        attn_out, _ = scaled_dot_product_attention(Q, K, V, mask)

        # Concat et projection
        attn_out = attn_out.transpose(1, 2).contiguous().view(batch, seq_len, -1)
        return self.W_o(attn_out)
```

**Dimension :** `d_model` = 512 (base), `n_heads` = 8, `d_k` = 64.

### Cross-Attention

Utilisé dans l'encodeur-décodeur : Q vient du décodeur, K et V de l'encodeur.

```python
class CrossAttention(nn.Module):
    def forward(self, decoder_emb, encoder_output, mask=None):
        Q = self.W_q(decoder_emb)       # du décodeur
        K = self.W_k(encoder_output)     # de l'encodeur
        V = self.W_v(encoder_output)     # de l'encodeur
        # ... standard multi-head attention
```

## Positional Encoding

### Sinusoïdal (Vaswani et al., 2017)

**Formule :**
```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

```python
class SinusoidalPositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]
```

**Avantage :** généralise à des séquences plus longues que l'entraînement.

### Learned Positional Embedding (BERT, GPT-2)

```python
class LearnedPositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super().__init__()
        self.pe = nn.Embedding(max_len, d_model)

    def forward(self, x):
        positions = torch.arange(0, x.size(1), device=x.device).unsqueeze(0)
        return x + self.pe(positions)
```

**Limite :** ne généralise pas au-delà de `max_len`. Utilisé dans BERT, GPT-2.

### RoPE — Rotary Position Embeddings (Su et al., 2021)

**Principe :** Multiplie les embeddings de Q et K par une matrice de rotation qui dépend de la position.

Application directe dans l'espace des têtes d'attention, pas d'addition dans l'embedding.

```python
def apply_rotary_emb(x, cos, sin):
    # x: [batch, n_heads, seq, d_k]
    # Diviser en paires de dimensions et appliquer la rotation
    x_rot = x[..., ::2] * cos - x[..., 1::2] * sin
    x_other = x[..., 1::2] * cos + x[..., ::2] * sin
    return torch.stack([x_rot, x_other], dim=-1).flatten(-2)
```

**Propriétés :**
- Décroissance naturelle de l'attention avec la distance
- Généralisation aux longues séquences
- Utilisé dans : LLaMA, Mistral, Qwen, Gemini, GPT-4

### ALiBi (Press et al., 2022)

**Principe :** Ajoute un biais linéaire aux scores d'attention, proportionnel à la distance entre tokens.

```python
def alibi_attention(Q, K, slopes=None):
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)

    if slopes is None:
        n_heads = Q.size(1)
        slopes = 2 ** (-8 / n_heads * torch.arange(1, n_heads + 1))
        slopes = slopes.unsqueeze(1).unsqueeze(1)

    # Biais : |i - j| * (-slope)
    seq_len = Q.size(-2)
    position_bias = torch.arange(seq_len).unsqueeze(1) - torch.arange(seq_len).unsqueeze(0)
    position_bias = position_bias.abs().to(Q.device) * (-slopes).unsqueeze(-1)

    scores = scores + position_bias
    return F.softmax(scores, dim=-1)
```

**Avantage :** généralisation naturelle aux longues séquences sans entraînement supplémentaire. Utilisé dans : BLOOM, MPT.

## Variantes d'Attention Optimisées

### Flash Attention (Dao et al., 2022)

**Principe :** Attention exacte mais sans matérialiser la matrice N×N des scores. Utilise le tiling GPU et recompute les poids pendant le backward.

```python
# Avec PyTorch 2.0+ (utilise Flash Attention automatiquement)
with torch.backends.cuda.sdp_kernel(enable_flash=True):
    output = F.scaled_dot_product_attention(Q, K, V, attn_mask=mask, dropout_p=0.1)

# Avec HuggingFace
model = AutoModel.from_pretrained(model_name, attn_implementation="flash_attention_2")
```

**Gain :** 2-4× plus rapide, consommation mémoire divisée par 2-3 (pas de matrice N²).

### Grouped Query Attention (GQA, Ainslie et al., 2023)

**Principe :** Réduit le nombre de têtes K et V (mais garde Q complet). Économise le KV cache.

```
MHA (Multi-Head Attention) :  n_heads_Q = n_heads_K = n_heads_V = h
GQA :  n_heads_Q = h,  n_heads_K = n_heads_V = g (g < h)
MQA (Multi-Query Attention) :  n_heads_K = n_heads_V = 1
```

**Utilisé dans :** LLaMA 2 (GQA), PaLM (MQA), Mistral (GQA), Falcon (MQA).

### Sliding Window Attention (Beltagy et al., 2020)

**Principe :** Chaque token ne voit que W tokens de chaque côté. Complexité O(N × W).

```python
def sliding_window_attention(Q, K, V, window_size=4096):
    # Créer un masque qui ne garde que les tokens dans la fenêtre
    seq_len = Q.size(-2)
    mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=-window_size)
    mask = mask * torch.tril(torch.ones(seq_len, seq_len), diagonal=window_size)
    return scaled_dot_product_attention(Q, K, V, mask=mask)
```

**Utilisé dans :** Mistral (window=4096), Longformer, BigBird, GPT-4 (hybride).

## Normalisation

### LayerNorm (Ba et al., 2016)
```python
class LayerNorm(nn.Module):
    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(d_model))
        self.beta = nn.Parameter(torch.zeros(d_model))
        self.eps = eps

    def forward(self, x):
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True, unbiased=False)
        return self.gamma * (x - mean) / (std + self.eps) + self.beta
```

### RMSNorm (Zhang & Sennrich, 2019)
```python
class RMSNorm(nn.Module):
    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d_model))
        self.eps = eps

    def forward(self, x):
        rms = torch.sqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)
        return self.weight * (x / rms)
```

**Avantage :** 5-10% plus rapide que LayerNorm, pas de calcul de moyenne. Utilisé dans LLaMA, Mistral, Qwen.

## Bloc Transformer Complet

```python
class TransformerBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, n_heads, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),  # ou ReLU, SwiGLU
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )
        self.norm2 = nn.LayerNorm(d_model)

    def forward(self, x, mask=None):
        # Pre-norm (standard moderne)
        x = x + self.attention(self.norm1(x), mask)
        x = x + self.ffn(self.norm2(x))
        return x
```

**Note :** Pre-norm (norm avant la sous-couche) est la norme moderne. Post-norm (original Vaswani) est instable.

## Pièges Courants (Common Pitfalls)

1. **Post-norm vs Pre-norm.** Post-norm (original) instable pour les modèles profonds. Pre-norm standard aujourd'hui.
2. **Pas de mask causal pour les modèles génératifs.** Les tokens futurs fuient dans l'attention.
3. **Oubli de √d_k dans le scaling.** Scores non scalés = gradients instables avec softmax saturé.
4. **Flash Attention non compatible avec tous les GPUs.** Nécessite compute capability 8.0+ (Ampere). Fallback sur SDPA.
5. **RoPE mal appliqué.** L'application de la rotation doit être symétrique sur Q et K.
6. **Positional encoding après dropout.** L'ordre des opérations compte : PE → Dropout → Attention.

## Liste de vérification (Checklist)

- [ ] Mécanisme d'attention adapté (full, sliding window, sparse)
- [ ] Positional encoding cohérent avec le modèle (sinusoïdal, RoPE, ALiBi)
- [ ] Pre-norm (standard) ou post-norm (compatibilité)
- [ ] Flash Attention/SDPA activé si GPU compatible
- [ ] Mask causal présent pour modèles génératifs
- [ ] d_model divisible par n_heads
- [ ] Dimension FFN correcte (d_ff = 4× d_model par défaut)