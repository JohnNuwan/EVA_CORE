---
name: transformers-avance
description: Guide complet et avancé des architectures Transformer — implémentations, variantes (GPT, BERT, T5, LLaMA), mécanismes, optimisation. En français.
---

# Transformers — Guide Avancé (Français)

Architectures, mécanismes, implémentations, des fondamentaux aux variantes 2025.

---

## 1. Architecture Transformer Complète

```
┌──────────────────────────────────────────────────┐
│                 Sortie                            │
│                      ▲                            │
│               ┌──────┴──────┐                     │
│               │   Linear    │                     │
│               │  + Softmax  │                     │
│               └──────┬──────┘                     │
│                      ▲                            │
│         ┌────────────┴────────────┐               │
│         │    Add & LayerNorm      │               │
│         └────────────┬────────────┘               │
│                      ▲                            │
│         ┌────────────┴────────────┐               │
│         │   Feed-Forward (FFN)    │               │
│         │  (SwiGLU / ReLU / GELU) │               │
│         └────────────┬────────────┘               │
│                      ▲                            │
│         ┌────────────┴────────────┐               │
│         │    Add & LayerNorm      │               │
│         └────────────┬────────────┘               │
│                      ▲                            │
│         ┌────────────┴────────────┐               │
│         │  Multi-Head Attention   │               │
│         │   (GQA / MQA / MHA)     │               │
│         └────────────┬────────────┘               │
│                      ▲                            │
│               ┌──────┴──────┐                     │
│               │   Embedding  │ ← Positional Enc.  │
│               │   + Tokens   │                    │
│               └─────────────┘                     │
└──────────────────────────────────────────────────┘
           × N couches
```

### Les 3 grandes familles

| Famille | Modèle | Usage |
|---------|--------|-------|
| **Encoder-only** | BERT, RoBERTa, DeBERTa | Classification, NER, QA |
| **Decoder-only** | GPT, LLaMA, Mistral, Qwen | Génération autoregressive |
| **Encoder-Decoder** | T5, BART, FLAN-T5 | Traduction, résumé, seq2seq |

---

## 2. Positional Encodings

### Sinusoidal (Vaswani et al., 2017)
```python
def positional_encoding(max_len: int, d_model: int) -> torch.Tensor:
    pe = torch.zeros(max_len, d_model)
    position = torch.arange(max_len).unsqueeze(1).float()
    div_term = torch.exp(
        torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model)
    )
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe.unsqueeze(0)  # (1, max_len, d_model)
```

### RoPE — Rotary Position Embedding (LLaMA, Mistral, Qwen)
```python
def apply_rotary_emb(x: torch.Tensor, freqs: torch.Tensor) -> torch.Tensor:
    """Applique RoPE aux tenseurs Q et K.
    x: (batch, seq_len, n_heads, dim_per_head)
    freqs: (seq_len, dim_per_head//2, 2)  # cos, sin pré-calculés
    """
    cos, sin = freqs[..., 0], freqs[..., 1]  # (seq_len, dim_per_head//2)
    x_rot = torch.stack([-x[..., 1::2], x[..., ::2]], dim=-1).reshape_as(x)
    return x * cos.unsqueeze(1).unsqueeze(0) + x_rot * sin.unsqueeze(1).unsqueeze(0)
```

**Avantage RoPE** : décroissance naturelle de l'attention avec la distance relative ; extrapolation au-delà de la longueur d'entraînement.

### ALiBi (Mistral, Falcon)
```python
# ALiBi = Attention avec biais linéaire
# scores = QK^T / sqrt(d) + bias
bias = -slope * positions_diagonale  # pénalité linéaire croissante
```
ALiBi permet l'extrapolation de contexte : entraîné sur 2K peut inférer sur 8K+.

### YaRN et NTK-aware scaling
```python
# Étalement de RoPE pour l'extrapolation de contexte
# NTK-aware : modifie la fréquence de rotation
freqs = freqs * (scale_factor ** (torch.arange(0, dim, 2) / dim))
```

---

## 3. Attention Variantes

### Multi-Head Attention (MHA)
```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_head = d_model // n_heads
        self.n_heads = n_heads
        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x, mask=None):
        B, T, D = x.shape
        Q = self.W_q(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        K = self.W_k(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)
        V = self.W_v(x).view(B, T, self.n_heads, self.d_head).transpose(1, 2)

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_head)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        attn = torch.softmax(scores, dim=-1)
        out = torch.matmul(attn, V).transpose(1, 2).contiguous().view(B, T, D)
        return self.W_o(out)
```

### Multi-Query Attention (MQA) — PaLM
- Q: n_heads têtes distinctes
- K, V: 1 seule tête partagée entre toutes
- Gains : mémoire cache KV 1/n_heads

### Grouped-Query Attention (GQA) — LLaMA 2+
```python
# Compromis MHA / MQA
# n_kv_heads < n_heads (ex: 8 queries, 4 KVs)
# Chaque groupe de queries partage un KV
class GroupedQueryAttention(nn.Module):
    def __init__(self, d_model, n_heads, n_kv_heads):
        super().__init__()
        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads
        self.n_rep = n_heads // n_kv_heads  # répétition des KV
        self.head_dim = d_model // n_heads
        self.W_q = nn.Linear(d_model, n_heads * self.head_dim, bias=False)
        self.W_k = nn.Linear(d_model, n_kv_heads * self.head_dim, bias=False)
        self.W_v = nn.Linear(d_model, n_kv_heads * self.head_dim, bias=False)
        self.W_o = nn.Linear(n_heads * self.head_dim, d_model, bias=False)

    def forward(self, x, mask=None):
        B, T, D = x.shape
        Q = self.W_q(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        K = self.W_k(x).view(B, T, self.n_kv_heads, self.head_dim).transpose(1, 2)
        V = self.W_v(x).view(B, T, self.n_kv_heads, self.head_dim).transpose(1, 2)
        # Répéter K,V pour chaque groupe
        K = K.repeat_interleave(self.n_rep, dim=1)
        V = V.repeat_interleave(self.n_rep, dim=1)
        # Attention computation...
```

### FlashAttention (Dao et al., 2022-2023)
```python
# FlashAttention v1 : attention O(n) en mémoire
# FlashAttention v2 : ~2x plus rapide que v1
# FlashAttention v3 : optimisé pour Hopper (H100)

# Principe : tiling + recomputation
# 1. Charge Q, K, V par blocs dans SRAM (fast)
# 2. Calcule softmax en ligne
# 3. Recompute le gradient (pas de stash mémoire)
#
# Avantages :
# - Mémoire : O(N) au lieu de O(N²)
# - Vitesse : 2-4x plus rapide
# - Support : torch.compile, xformers, triton

# Utilisation :
# pip install flash-attn
from flash_attn import flash_attn_func

# Q, K, V: (batch, seqlen, nheads, headdim)
out, _ = flash_attn_func(
    Q, K, V,
    dropout_p=0.0,
    softmax_scale=1.0/math.sqrt(head_dim),
    causal=True,
)
```

### Attention sliding window (Mistral, LongLoRA)
```python
# Attention locale + quelques tokens globaux
# Fenêtre W = 4096 tokens
# Token global tous les N = 4096 tokens
# Complexité O(L * W) au lieu de O(L²)
```

### Attention sparse / dilated (Longformer, BigBird)
```python
# Sliding window + dilation + global tokens
# - Fenêtre locale (taille w)
# - Dilatation (saut d'espaces)
# - Tokens globaux (CLS, etc.)
```

---

## 4. Feed-Forward Networks (FFN)

### Variantes FFN (par ordre chronologique)

| Modèle | Activation | Structure |
|--------|-----------|-----------|
| Original | ReLU | up → ReLU → down |
| GPT-2 | GELU | up → GELU → down |
| LLaMA | SwiGLU | up1 * sigmoid(up1*β) * up2 → down |
| PaLM | SwiGLU | up1 → SiLU → up2 → down |
| T5 | ReLU | up → ReLU → down |
| GLU-128k | SwiGLU | gating amélioré |

```python
# SwiGLU (LLaMA family)
class SwiGLU(nn.Module):
    def forward(self, x):
        x, gate = x.chunk(2, dim=-1)
        return F.silu(gate) * x

# GELU (GPT-2, BERT)
class GELU(nn.Module):
    def forward(self, x):
        return 0.5 * x * (1 + torch.erf(x / math.sqrt(2)))
        # Approximation tanh : 0.5 * x * (1 + torch.tanh(...))
```

### Dimension de la FFN
```python
# LLaMA 7B: d_model=4096, d_ff=11008 (≈ 2.7x d_model)
# GPT-3 175B: d_model=12288, d_ff=49152 (4x)
# DeepSeek-V3: d_model=7168, d_ff=2048 (MoE)
```

---

## 5. Architectures Détaillées

### GPT (Decoder-only autoregressif)
```python
# Causal attention (masked)
# Pas d'encoder, génération token par token
# Pré-entraînement : next token prediction
def generate_causal(model, prompt: torch.Tensor, max_new: int):
    for _ in range(max_new):
        logits = model(prompt)  # (1, seq_len, vocab_size)
        logits_last = logits[:, -1, :]  # dernier token seulement
        next_token = torch.argmax(logits_last, dim=-1)
        prompt = torch.cat([prompt, next_token.unsqueeze(0)], dim=1)
    return prompt
```

### BERT (Encoder-only)
```python
# Bidirectional (pas de causal mask)
# Pré-entraînement : MLM (Masked Language Modeling) + NSP
# Fine-tuning : classification sur [CLS]
class BERTClassifier(nn.Module):
    def __init__(self, bert_name="bert-base-uncased", n_classes=2):
        super().__init__()
        self.bert = AutoModel.from_pretrained(bert_name)
        self.classifier = nn.Linear(self.bert.config.hidden_size, n_classes)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        cls_token = outputs.last_hidden_state[:, 0, :]  # [CLS]
        return self.classifier(cls_token)
```

### T5 (Encoder-Decoder)
```python
# Text-to-Text : tout est reformulé en texte
# Pré-entraînement : span corruption (remplace spans → sentinelles)
# Architecture : encoder (bidirectionnel) → decoder (causal)
# T5-base : 220M paramètres, T5-xxl : 11B
```

---

## 6. Optimisations Clés

### KV Cache (inférence)
```python
# Cache les K et V calculés pour les tokens précédents
# Évite de recalculer toute la séquence à chaque step
# Mémoire : O(n_layers * seq_len * d_model)
# Compression : MQA/GQA réduit la mémoire du cache

class KVCache:
    def __init__(self, max_batch, max_seq, n_layers, n_kv_heads, head_dim):
        self.cache = torch.zeros(n_layers, 2, max_batch, max_seq,
                                 n_kv_heads, head_dim)
        self.seq_len = 0

    def update(self, layer, k, v):
        """Ajoute K, V pour les nouveaux tokens."""
        self.cache[layer, 0, :, self.seq_len:self.seq_len+k.size(-2)] = k
        self.cache[layer, 1, :, self.seq_len:self.seq_len+v.size(-2)] = v
        past = self.cache[layer, :, :, :self.seq_len]
        self.seq_len += k.size(-2)
        return past[:, 0], past[:, 1]
```

### Speculative Decoding
```python
# 1. Un petit modèle (draft) génère γ tokens rapidement
# 2. Le grand modèle vérifie en parallèle
# 3. Accepte ou rejette, accordéon
# Résultat : 2-3x plus rapide sans perte de qualité
```

### Prefix Caching (prompt caching)
```python
# Cache l'état KV du préfixe du prompt
# Partagé entre plusieurs requêtes avec le même préfixe
# Jusqu'à 10x de réduction de latence pour les prompts longs
```

---

## 7. Entraînement Stable

```python
# Warmup + cosine LR
def get_cosine_schedule_with_warmup(optimizer, warmup_steps, total_steps):
    def lr_lambda(step):
        if step < warmup_steps:
            return step / max(1, warmup_steps)
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.5 * (1.0 + math.cos(math.pi * progress))
    return LambdaLR(optimizer, lr_lambda)

# z-loss (stabilisation, PaLM)
# Perte auxiliaire : penalise les logits qui s'éloignent de 0
# z_loss = 1e-4 * log(sum(exp(logits)))²

# QK-Normalization (stabilise l'entraînement en BF16)
# Normalise Q et K avant le calcul du score
```

---

## 8. Scaling Laws (Kaplan et al., Hoffmann et al.)

```python
# Loi de Kaplan (2020) : plus de paramètres > plus de données
# Loi de Chinchilla (2022) : 20 tokens par paramètre optimal
#
# Compute-optimal :
# Pour un budget C (FLOPs) :
# N_opt = C^0.5, D_opt = C^0.5  (Chinchilla)
# vs N_opt = C^0.73, D_opt = C^0.27 (Kaplan)

# Exemple : 7B modèle → 140B tokens (Chinchilla-optimal)
```

---

## 9. Variantes Modernes (2024-2025)

| Modèle | Famille | Originalité |
|--------|---------|-------------|
| **LLaMA 3** | Decoder | GQA, RoPE, SwiGLU, 128K ctx |
| **Mistral** | Decoder | Sliding window, GQA, RoPE |
| **Qwen 2.5** | Decoder | GQA, RoPE, SwiGLU, 128K |
| **DeepSeek-V3** | Decoder MoE | Multi-Token Prediction, MTP |
| **Phi-4** | Decoder | Entraînement sur données synthétiques |
| **Gemma 2** | Decoder | GQA, Logit soft-capping, RoPE |
| **T5 (FLAN)** | Enc-Dec | Prompt tuning, instruction tuning |
| **xGen-MM** | Decoder | Vision-Language natif |

### Multi-Token Prediction (DeepSeek)
```python
# Prédit plusieurs tokens futurs simultanément
# Chaque niveau utilise l'embedding du token précédent + représentation partagée
# Améliore le raisonnement et l'utilisation du cache
```

---

## 10. Implémentation Complète Simplifiée

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class DecoderLayer(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, n_heads, dropout,
                                               batch_first=True)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # Self-attention + résiduelle
        attn_out, _ = self.self_attn(x, x, x, attn_mask=mask,
                                     need_weights=False)
        x = self.norm1(x + self.dropout(attn_out))
        # FFN + résiduelle
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        return x


class MiniTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=512, n_heads=8,
                 n_layers=6, d_ff=2048, max_len=1024):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_len, d_model)
        self.layers = nn.ModuleList([
            DecoderLayer(d_model, n_heads, d_ff)
            for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)

    def forward(self, tokens):
        B, T = tokens.shape
        pos = torch.arange(0, T, device=tokens.device).unsqueeze(0)
        x = self.token_embedding(tokens) + self.pos_embedding(pos)
        # Causal mask
        mask = torch.triu(torch.ones(T, T, device=tokens.device) * float('-inf'),
                          diagonal=1)
        for layer in self.layers:
            x = layer(x, mask)
        x = self.norm(x)
        logits = self.lm_head(x)
        return logits
```

---

## Références

- Attention Is All You Need : https://arxiv.org/abs/1706.03762
- RoFormer (RoPE) : https://arxiv.org/abs/2104.09864
- GQA (LLaMA 2) : https://arxiv.org/abs/2305.13245
- FlashAttention : https://arxiv.org/abs/2205.14135
- Scaling Laws : https://arxiv.org/abs/2001.08361
- LLaMA : https://arxiv.org/abs/2302.13971
- DeepSeek-V3 : https://arxiv.org/abs/2412.19437
- ALiBi : https://arxiv.org/abs/2108.12409