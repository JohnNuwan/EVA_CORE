---
name: nlp-gpt
description: Use when working with Generative Pre-trained Transformer models — GPT-1/2/3/4, autoregressive language modeling, causal masking, ChatGPT, inference optimization, prompting, et architectures dérivées (GPT-Neo, LLaMA, Mistral).
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [nlp, gpt, autoregressive, causal-lm, generative, transformer, llm, chatgpt]
    related_skills: [nlp-transformers, nlp-prompting, nlp-fine-tuning, llm, transformers-avance]
---

# GPT — Generative Pre-trained Transformer

## Vue d'ensemble

Les modèles GPT (Generative Pre-trained Transformer) d'OpenAI ont défini l'architecture autoregressive des LLMs modernes. Contrairement aux encodeurs bidirectionnels (BERT), les modèles GPT utilisent un **masquage causal** qui empêche chaque token de voir les tokens suivants, ce qui les rend adaptés à la génération séquentielle.

Ce skill couvre : l'architecture causale, GPT-1/2/3/4, les modèles open-source (GPT-Neo, LLaMA, Mistral, Qwen, DeepSeek), l'inférence et la génération, les optimisations (KV cache, speculative decoding, quantization), et les techniques de prompting.

## Architecture Causal (Autoregressive)

**Principe fondamental :** Chaque token ne peut s'appuyer que sur les tokens **précédents** (à gauche). Masque causal triangulaire.

```
Attention_mask (causal) :
[1, 0, 0, 0, 0]
[1, 1, 0, 0, 0]
[1, 1, 1, 0, 0]
[1, 1, 1, 1, 0]
[1, 1, 1, 1, 1]
```

**Formulation mathématique :**
```
P(x) = Π P(x_t | x_<t)
```

**GPT-1 (2018) :** 12 couches, 768 hidden, 12 têtes, 117M paramètres. Pré-entraînement sur BooksCorpus.
**GPT-2 (2019) :** 48 couches, 1600 hidden, 1600M paramètres. Dataset WebText (40GB).
**GPT-3 (2020) :** 96 couches, 12288 hidden, 96 têtes, 175B paramètres. 570GB de données.

## Génération Autoregressive

### Beam Search (pour tâches discriminatives)
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

inputs = tokenizer("L'intelligence artificielle", return_tensors="pt")

# Beam search pour tâches structurées
outputs = model.generate(
    **inputs,
    num_beams=5,
    early_stopping=True,
    max_new_tokens=50,
    no_repeat_ngram_size=3,
)
```

### Échantillonnage (pour créativité)
```python
outputs = model.generate(
    **inputs,
    do_sample=True,
    temperature=0.7,
    top_k=50,
    top_p=0.95,
    max_new_tokens=100,
    repetition_penalty=1.1,
)
```

**Paramètres de température :**
- 0.0 → 0.7 : déterministe à créatif
- 0.7 → 1.5 : créatif à chaotique
- > 1.5 : généralement incohérent

## KV Cache (Optimisation d'Inférence)

Le KV cache stocke les clés et valeurs de l'attention pour les tokens déjà générés, évitant de les recalculer.

```python
class CausalLMWithKVCache:
    def __init__(self, model):
        self.model = model
        self.past_key_values = None

    def generate_token(self, input_ids):
        with torch.no_grad():
            outputs = self.model(
                input_ids,  # un seul token à la fois (sauf premier)
                past_key_values=self.past_key_values,
                use_cache=True,
            )
            self.past_key_values = outputs.past_key_values
            return outputs.logits[:, -1, :]
```

**Impact :** réduit la complexité de `O(N²)` à `O(N)` par token généré. Économise 90%+ des FLOPs sur des séquences longues.

## Modèles Open-Source Majeurs

### GPT-Neo / GPT-J (EleutherAI)
```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neox-20b")
# 20B paramètres, architecture similaire à GPT-3
```

### LLaMA (Meta, 2023)
```python
from transformers import LlamaForCausalLM, LlamaTokenizer

model = LlamaForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B")
tokenizer = LlamaTokenizer.from_pretrained("meta-llama/Llama-3.2-3B")
```

**Innovations clés :**
- SwiGLU activation (LLaMA, 2023)
- RoPE (Rotary Position Embeddings)
- RMSNorm au lieu de LayerNorm
- LLaMA 2/3/4 : améliorations de dataset, RLHF, Grouped Query Attention (GQA)

### Mistral (2023)
```python
from transformers import MistralForCausalLM

model = MistralForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.3")
```

**Innovations :**
- Sliding Window Attention (attention fenêtrée, complexité O(N * W))
- GQA (Grouped Query Attention)
- 32k contexte natif

### Qwen / DeepSeek (2024-2025)
- **Qwen2.5 :** 0.5B à 72B, SwiGLU + RoPE + GQA, 128k tokens contexte
- **DeepSeek-V2/V3 :** MoE (Mixture of Experts), 671B paramètres, 37B actifs
- **DeepSeek-R1 :** reasoning amélioré via GRPO + RL

## Quantization pour Inférence

```python
# Bitsandbytes 4-bit
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.3",
    quantization_config=bnb_config,
    device_map="auto",
)

# GPTQ (via AutoGPTQ)
from auto_gptq import AutoGPTQForCausalLM

model = AutoGPTQForCausalLM.from_quantized("TheBloke/Mistral-7B-GPTQ")

# AWQ (via AutoAWQ)
model = AutoModelForCausalLM.from_pretrained(
    "casperhansen/mistral-7b-awq",
    device_map="auto",
)
```

## Flash Attention

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    attn_implementation="flash_attention_2",  # ou "sdpa"
    torch_dtype=torch.bfloat16,
)
```

**Gain :** 2-4× plus rapide, consommation mémoire divisée par 2-3, supporte des séquences très longues.

## Speculative Decoding

Prédire plusieurs tokens en parallèle avec un petit modèle draft, vérifiés par le modèle target.

```python
from transformers import AutoModelForCausalLM

# Génération avec speculation (pris en charge nativement dans HF Transformers 4.45+)
assistant_model = AutoModelForCausalLM.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2-xl")

outputs = model.generate(
    **inputs,
    assistant_model=assistant_model,
    max_new_tokens=100,
    do_sample=True,
)
```

**Gain :** 2-3× throughput supplémentaire pour l'inférence batch.

## Comparaison des Architectures

| Modèle | Attention | Activation | Position | Taille max |
|--------|-----------|------------|----------|------------|
| GPT-2 | Full causal | GELU | Learned | 1.5B |
| GPT-3 | Full causal | GELU | Learned (rotary) | 175B |
| LLaMA | Full causal | SwiGLU | RoPE | 70B |
| Mistral | Sliding window | SwiGLU | RoPE | 7B |
| Qwen2.5 | Full + GQA | SwiGLU | RoPE | 72B |
| DeepSeek-V3 | MoE + MHA | SwiGLU | RoPE | 671B |

## Pièges Courants (Common Pitfalls)

1. **Pas de pad_token sur les modèles causaux.** GPT/LLaMA n'ont pas de pad_token par défaut. Utiliser `pad_token = eos_token`.
2. **Attention mask non fourni au batch.** La génération batchée sans attention_mask produit des résultats incorrects.
3. **Temperature trop élevée pour des tâches factuelles.** Utiliser temperature=0.1-0.3 pour la précision, 0.7-1.0 pour la créativité.
4. **Oubli du KV cache au-delà du premier appel.** Le re-calcul complet est `O(N²)` au lieu de `O(N)`.
5. **Utilisation de beam search pour des prompts créatifs.** Beam search favorise les séquences génériques et répétitives.

## Liste de vérification (Checklist)

- [ ] Modèle causal compatible avec la tâche (génération vs compréhension)
- [ ] Tokenizer avec pad_token configuré
- [ ] Flash Attention activée (si GPU compatible)
- [ ] Quantization adaptée au matériel (4-bit si VRAM < 24GB)
- [ ] Temperature et top_p/ top_k réglés pour la créativité souhaitée
- [ ] Repetition penalty présent pour les longues générations
