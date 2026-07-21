---
name: quantization-optimization
description: Guide complet de la quantification et optimisation de modèles — GPTQ, AWQ, GGUF, bitsandbytes, QAT, SmoothQuant, FP8, distillation, pruning. En français.
---

# Quantification & Optimisation de Modèles — Guide Complet

Réduire la mémoire, accélérer l'inférence, déployer sur plus de matériel.

---

## 1. Pourquoi Quantifier ?

```python
# 1. Mémoire VRAM
# FP32 : 4 bytes/param → 175B modèle = 700 Go
# FP16 : 2 bytes/param → 175B modèle = 350 Go
# INT4 : 0.5 byte/param → 175B modèle = 87 Go

# 2. Vitesse
# INT8 matmul : 2x plus rapide que FP16 sur A100/H100
# INT4 matmul : 4x plus rapide (mais qualité réduite)

# 3. Déploiement
# Un Llama 70B en FP16 tient sur 2×A100 (80 Go chacune)
# En INT4 : 1×A100 suffit
```

### Trade-off Quantification

```
Précision (FP32) ───────────────────────────────────────────── Efficacité
     ┌────────┬────────┬────────┬────────┬────────┐
    FP32     FP16     INT8     INT4     INT2     NF4
     Haute                         Basse
     précision                      latence
     Lente                          Rapide
     Beaucoup                       Peu
     VRAM                           VRAM
```

---

## 2. Types de Quantification

### Symétrique vs Asymétrique
```python
# Quantification symétrique : z=0
# x_q = round(x / scale)
# scale = max(|x|) / (2^(b-1) - 1)

# Quantification asymétrique : z != 0
# x_q = round(x / scale + z)
# scale = (max(x) - min(x)) / (2^b - 1)
# z = round(-min(x) / scale)
```

### Per-Tensor vs Per-Channel vs Per-Group
```python
# Per-Tensor : 1 scale pour tout le tenseur (le moins précis)
# Per-Channel : 1 scale par channel de sortie
# Per-Group : 1 scale par groupe de N valeurs (le plus précis)
#   ex: group_size=128 dans GPTQ/AWQ
```

---

## 3. GPTQ (Frantar et al., 2023)

```python
# GPTQ : quantification post-entraînement basée sur
# l'approximation de la matrice de Fisher / Hessian
#
# Principe : 
# 1. Prendre un petit ensemble de calibration (128-256 samples)
# 2. Quantifier les poids colonne par colonne
# 3. Compenser l'erreur de quantification sur les colonnes restantes

# Propriétés :
# - Weight-only quantization (pas de calibration activations)
# - GPU-friendly : Tensor Cores compatibles
# - 4-bit : très bonne qualité
# - 2-bit : dégradation notable

def gptq_quantize(W, H, bits=4, group_size=128):
    """
    W: matrice de poids (in_feat, out_feat)
    H: matrice Hessian (in_feat, in_feat) — info de Fisher
    Quantifie W en bits bits avec compensation d'erreur.
    """
    W_quant = W.clone().float()
    H_diag = torch.diag(H)
    
    # Tri par importance (diagonale du Hessian)
    importance = torch.argsort(H_diag, descending=True)
    
    for idx in importance:
        w = W_quant[idx, :]
        
        # Quantifier ce poids
        q = quantize_weight(w, bits)
        err = w - dequantize_weight(q, bits)  # erreur de quantification
        
        # Compenser l'erreur sur les poids non encore quantifiés
        if len(remaining) > 0:
            W_quant[remaining, :] -= err * H[idx, remaining] / H[idx, idx]
    
    return W_quant
```

```python
# Utilisation pratique
# pip install auto-gptq
from auto_gptq import AutoGPTQForCausalLM

model = AutoGPTQForCausalLM.from_quantized(
    "TheBloke/Llama-2-7B-GPTQ",
    model_basename="gptq_model-4bit-128g",
    use_triton=True,           # Kernels Triton optimisés
    device_map="auto",
)
```

---

## 4. AWQ (Lin et al., 2024)

```python
# AWQ = Activation-aware Weight Quantization
# Innovation : regarde les activations (pas seulement les poids)
# Les « poids importants » sont ceux qui correspondent 
# à des activations élevées (salient channels)
# Protection : scaling (pas de recalibration coûteuse)

class AWQ:
    """Activation-Aware Weight Quantization.
    
    Étapes :
    1. Analyser les activations sur un petit dataset
    2. Identifier les channels saillants
    3. Appliquer un scaling protecteur aux poids importants
    4. Quantifier en INT4 (standard)
    """
    
    @staticmethod
    def compute_scales(model, calibration_data, alpha=0.5):
        """Calcule les scales de protection AWQ."""
        # Mesurer l'importance de chaque channel
        # importance = activation_magnitude^alpha
        pass
    
    @staticmethod
    def apply_scale(model, scales):
        """Applique le scaling aux poids."""
        # W_scaled = W / scales
        # Plus tard, on peut remultiplier par scales dans l'inférence
        pass
```

```python
# Utilisation pratique
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7B-hf",
)
model.quantize(
    tokenizer,
    quant_config={"zero_point": True, "q_group_size": 128, 
                  "w_bit": 4, "version": "GEMM"},
)

# AWQ vs GPTQ :
# AWQ : meilleure qualité à 4-bit, plus simple
# GPTQ : plus mature, écosystème plus large
```

---

## 5. BitsAndBytes (4-bit QLoRA)

```python
# QLoRA : Quantized LoRA (Dettmers et al., 2023)
# NF4 : NormalFloat4 — distribution normalisée
# Double quantization : quantifier les scales aussi

from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",          # NormalFloat4
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,      # Double quantization
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B",
    quantization_config=bnb_config,
    device_map="auto",
)

# NF4 : distribution normalisée pour les poids
# Double quant : scales en INT8 au lieu de FP32
# → ~5.5 Go pour 7B modèle (au lieu de 14 Go FP16)
```

### NF4 — NormalFloat4
```python
# NF4 est optimisé pour la distribution des poids :
# Les poids des réseaux suivent approximativement N(0, σ)
# NF4 alloue plus de niveaux de quantification près de 0
# (où il y a plus de poids) et moins dans les queues

# Format NF4 :
# 0, 1, 2, 3, 4, 5, 6, 7 (niveaux asymétriques autour de 0)
# Distribution non-uniforme adaptée à N(0, σ)
```

---

## 6. GGUF / llama.cpp

```python
# GGUF : format de quantification pour CPU (et GPU)
# Utilisé par llama.cpp, Ollama, LM Studio
# Très flexible : 2-bit à 8-bit, Q4_K_M, Q5_K_S, etc.

# Types GGUF :
# Q2_K   : 2-bit (très compressé, perte importante)
# Q3_K_S : 3-bit small
# Q3_K_M : 3-bit medium
# Q4_0   : 4-bit (rapide)
# Q4_K_M : 4-bit (meilleur compromis qualité/vitesse) ⭐
# Q5_K_M : 5-bit (excellente qualité)
# Q6_K   : 6-bit (quasi FP16)
# Q8_0   : 8-bit (aucune perte perceptible)

# Utilisation :
# ./llama-cli -m model.Q4_K_M.gguf -p "Prompt" -n 512

# Propriétés :
# - K-quants : quantification par super-blocs
# - Imatrix : importance matrix pour meilleure quantification
# - MoE support : Mixtral, DeepSeek
# - Split : entre CPU et GPU
```

### K-Quant (llama.cpp)
```python
# K-Quant : quantification par blocs adaptatifs
# Principe :
# Les blocs « importants » (high variance) reçoivent plus de bits
# Les blocs « plats » reçoivent moins de bits
#
# Q4_K_M = medium quality 4-bit avec mélange Q4/Q5/Q6
# selon l'importance des blocs
```

---

## 7. SmoothQuant (Xiao et al., 2023)

```python
# SmoothQuant : quantification INT8 des activations
# Problème : les activations ont des outliers (valeurs extrêmes)
# SmoothQuant les « lisse » en transférant la difficulté :
# - On migre la variance des activations vers les poids
# - Les activations deviennent plus lisses (quantifiables)
# - Les poids sont reparamétrés (W_smoothed)

def smooth_quant(model, calibration_data, alpha=0.5):
    """SmoothQuant : quantification INT8 des activations.
    
    Principe mathématique :
    Y = X · W = (X / s) · (s · W)
    où s_j = max(|X_j|)^alpha / max(|W_j|)^(1-alpha)
    
    s transfère la variance de X vers W.
    X/s est plus lisse → quantifiable en INT8
    s·W est plus rugueux → mais poids en FP16
    """
    # Calibration : mesurer les stats des activations
    # Migration : appliquer le scaling
    pass
```

---

## 8. FP8 Training (H100 native)

```python
# H100 supporte FP8 nativement (2x plus rapide que FP16)
# FP8 training : poids en FP16, calculs en FP8

# FP8 Formats :
# E4M3 : 4 bits exposant, 3 bits mantisse
#        (plage ±448, 3 bits mantisse)
# E5M2 : 5 bits exposant, 2 bits mantisse
#        (plage ±57344, 2 bits mantisse)

# Stratégie :
# Forward : E4M3 (précision)
# Backward : E5M2 (plage pour gradients)

# Utilisation (Transformer Engine) :
import transformer_engine.pytorch as te

linear = te.Linear(4096, 4096, dtype=torch.float8)
# Les calculs de matmul sont automatiquement en FP8
```

---

## 9. QAT — Quantization-Aware Training

```python
# QAT : simuler la quantification pendant l'entraînement
# Le modèle apprend à être robuste à la quantification
# Meilleure qualité que PTQ (Post-Training Quantization)

class QATLinear(nn.Module):
    """Linear avec quantification simulée (Fake Quant)."""
    def __init__(self, in_features, out_features, n_bits=8):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.n_bits = n_bits
    
    def fake_quantize(self, x):
        """Simule la quantification pendant l'entraînement.
        
        Pendant forward : quantise et déquantise (arrondi)
        Pendant backward : arrondi ignoré (STE — Straight-Through Estimator)
        """
        scale = x.abs().max() / (2**(self.n_bits - 1) - 1)
        x_q = torch.round(x / scale)
        x_deq = x_q * scale
        # STE : backward passe à travers sans arrondi
        return x + (x_deq - x).detach()
    
    def forward(self, x):
        w_q = self.fake_quantize(self.weight)
        return F.linear(x, w_q)
```

---

## 10. Pruning (Élagage)

```python
# Pruning = retirer des poids inutiles
# Objectif : réduire la taille sans perdre en qualité

# Types de pruning :
# 1. **Magnitude pruning** : retirer les poids les plus petits
# 2. **SparseGPT** (2023) : pruning 50% sans perte
# 3. **Wanda** (2023) : pruning basé sur poids × activation
# 4. **Semi-structured** : format 2:4 (50% sparse, compatible GPU)

class SparseGPT:
    """SparseGPT : pruning structuré sans fine-tuning.
    
    Principe : un peu comme GPTQ mais met à zéro les poids
    au lieu de les quantifier.
    - 50% sparse : aucune perte de perplexité
    - 60% sparse : légère perte
    - 2:4 sparsity : support hardware natif (NVIDIA Ampere+)
    """
    pass
```

---

## 11. Distillation comme Optimisation

```python
# Knowledge distillation comme technique d'optimisation :
# Le modèle student (plus petit) apprend du teacher
# Soft labels (logits) + hard labels (target)

# Résultat : un modèle 2-3x plus petit avec 95%+ de la qualité
```

---

## 12. Tableau Récapitulatif

| Méthode | Bits | VRAM (7B) | VRAM (70B) | Qualité | Calibration |
|---------|:---:|:--------:|:--------:|:------:|:----------:|
| FP16 | 16 | 14 Go | 140 Go | ★★★★★ | - |
| INT8 (bitsandbytes) | 8 | 7 Go | 70 Go | ★★★★☆ | - |
| INT8 (SmoothQuant) | 8 | 7 Go | 70 Go | ★★★★★ | 100 samples |
| GPTQ 4-bit | 4 | 4 Go | 35 Go | ★★★★☆ | 128 samples |
| AWQ 4-bit | 4 | 4 Go | 35 Go | ★★★★★ | 128 samples |
| NF4 (QLoRA) | 4 | 5.5 Go | 55 Go | ★★★★☆ | - |
| GGUF Q4_K_M | 4 | 4.5 Go | 45 Go | ★★★★☆ | - |
| GGUF Q2_K | 2 | 2.5 Go | 25 Go | ★★★☆☆ | - |
| Sparse 50% | 16 | 7 Go | 70 Go | ★★★★★ | 128 samples |

---

## 13. Guide Pratique

```python
# Quel format choisir ?

# CPU only → GGUF (Q4_K_M)
# GPU, max qualité → AWQ 4-bit
# GPU, fine-tuning → QLoRA (NF4 + double quant)
# GPU, compatibilité → GPTQ 4-bit
# Production, throughput → INT8 (SmoothQuant)
# Ultra compression → GGUF Q2_K ou NF4
# Latence critique → FP8 (H100)
```

---

## Références

- GPTQ : https://arxiv.org/abs/2210.17323
- AWQ : https://arxiv.org/abs/2306.00978
- QLoRA (NF4) : https://arxiv.org/abs/2305.14314
- SmoothQuant : https://arxiv.org/abs/2211.10438
- FP8 (H100) : https://arxiv.org/abs/2209.05433
- SparseGPT : https://arxiv.org/abs/2301.00774
- Wanda (Pruning) : https://arxiv.org/abs/2306.11695
- LLM.int8() : https://arxiv.org/abs/2208.07339
- llama.cpp : https://github.com/ggerganov/llama.cpp
- BitsAndBytes : https://github.com/bitsandbytes-foundation/bitsandbytes