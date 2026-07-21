---
name: llm
description: Guide complet des Large Language Models — architectures, fine-tuning, RLHF, DPO, quantization, inference, prompting, et déploiement. En français.

---

# Large Language Models — Guide Complet (Français)

LLMs : de la théorie au déploiement. Transformers, fine-tuning, optimisation.

---

## 1. Architecture Transformer

```
Entrée : [CLS] Tok_1 Tok_2 ... [SEP]
  │
  ├── Token Embeddings
  ├── Positional Embeddings
  └── (Segment Embeddings)
  │
  ▼
┌─────────────────────────┐
│  Multi-Head Attention   │ ← Q, K, V
│  + Residual + LayerNorm │
├─────────────────────────┤
│  Feed-Forward Network   │
│  + Residual + LayerNorm │
└─────────────────────────┘
  × N couches
  │
  ▼
Sortie : logits par token
```

### Self-Attention
```python
# Q, K, V = X @ W_q, X @ W_k, X @ W_v
# Attention(Q, K, V) = softmax(QK^T / √d_k) V

def self_attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    attention = torch.softmax(scores, dim=-1)
    return torch.matmul(attention, V), attention
```

### Variantes d'attention
- **Multi-Head Attention (MHA)** : attention parallèle sur plusieurs têtes
- **Multi-Query Attention (MQA)** : K, V partagés entre têtes (PaLM)
- **Grouped-Query Attention (GQA)** : compromis MHA/MQA (Llama 2+)
- **FlashAttention** : attention O(n) en mémoire (fused kernel)
- **Sliding Window** : fenêtre locale + quelques tokens globaux (Mistral)

---

## 2. Modèles Majeurs (2024-2025)

### Modèles ouverts
| Modèle | Params | Contexte | Forces |
|--------|--------|----------|--------|
| Llama 3 | 8B-405B | 128K | Performance généraliste |
| Mistral | 7B-123B | 128K | Efficacité |
| Qwen 2.5 | 0.5B-72B | 128K | Multilingue, code |
| DeepSeek V3 | 671B MoE | 128K | Raisonnement, math |
| Phi-4 | 14B | 16K | Raisonnement |
| Gemma 2 | 2B-27B | 8K | Famille Google |

### Modèles propriétaires
| Modèle | Forces |
|--------|--------|
| GPT-4o | Multimodal, rapide |
| Claude 3.5 | Raisonnement, code, long contexte |
| Gemini 2 | Multimodal natif |

---

## 3. Fine-Tuning

### Full Fine-Tuning
```python
from transformers import (
    AutoModelForCausalLM, AutoTokenizer,
    TrainingArguments, Trainer,
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType

# 1. Charger le modèle
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# 2. Tokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B")
tokenizer.pad_token = tokenizer.eos_token

# 3. Préparer les données
def tokenize(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=2048,
        padding="max_length",
    )

dataset = load_dataset("json", data_files="data.jsonl")
dataset = dataset.map(tokenize, batched=True)

# 4. Entraînement
training_args = TrainingArguments(
    output_dir="./llama3-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    warmup_steps=100,
    logging_steps=10,
    save_strategy="epoch",
    bf16=True,
    optim="adamw_8bit",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
)

trainer.train()
```

---

## 4. PEFT (Parameter-Efficient Fine-Tuning)

### LoRA — Low-Rank Adaptation

```python
from peft import LoraConfig, get_peft_model, TaskType

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,                         # Rang de décomposition
    lora_alpha=32,                # Facteur d'échelle
    lora_dropout=0.05,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    bias="none",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 41,943,040 || all params: 8,070M || trainable%: 0.52%
```

### QLoRA (Quantized LoRA)
```python
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-8B",
    quantization_config=bnb_config,
    device_map="auto",
)

model = get_peft_model(model, lora_config)
# 8B modèle en ~6 Go VRAM avec LoRA
```

---

## 5. Alignment (RLHF, DPO)

### DPO — Direct Preference Optimization

```python
from trl import DPOTrainer

# Format des données DPO
# {"prompt": "...", "chosen": "...", "rejected": "..."}

dpo_trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,          # Modèle de référence (gelé)
    args=training_args,
    train_dataset=preference_dataset,
    tokenizer=tokenizer,
    beta=0.1,                     # Paramètre de régularisation
    max_length=1024,
)

dpo_trainer.train()
```

### RLHF classique
```
1. Supervised Fine-Tuning (SFT)
2. Reward Model Training (préférences humaines)
3. PPO (RL avec le reward model)
```

---

## 6. Quantification

| Méthode | Bits | VRAM (3B) | Qualité |
|---------|------|-----------|---------|
| FP32 | 32 | 24 Go | Parfaite |
| FP16 | 16 | 16 Go | Excellente |
| BF16 | 16 | 16 Go | Excellente (⚠️ précision) |
| INT8 | 8 | 8 Go | Très bonne |
| NF4 (QLoRA) | 4 | 6 Go | Bonne |
| GPTQ | 2-4-8 | 6-8 Go | Bonne |
| AWQ | 4 | ~6 Go | Très bonne |
| GGUF/llama.cpp | 2-8 | Variable | Bonne |

```python
# BitsAndBytes 4-bit
from transformers import BitsAndBytesConfig

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

# GPTQ
model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-7B-GPTQ",
    device_map="auto",
)
```

---

## 7. Inférence Optimisée

```python
# vLLM (haute performance serving)
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3-8B",
    tensor_parallel_size=2,
    dtype="bfloat16",
    max_model_len=8192,
)

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=512,
)

outputs = llm.generate(prompts, sampling_params)


# llama.cpp (CPU-friendly, GGUF)
# ./llama-cli -m modele.gguf -p "Prompt" -n 512

# TensorRT-LLM (NVIDIA, ultra-optimisé)
# ~5x plus rapide que vanilla PyTorch
```

---

## 8. Prompting Avancé

```python
# Few-shot
prompt = """Classifie le sentiment : positif, négatif, neutre.

Texte : J'adore ce film. → positif
Texte : C'était horrible. → négatif
Texte : Le film est sorti hier. → neutre
Texte : {texte_utilisateur} → """

# Chain-of-Thought (CoT)
prompt = """Résous étape par étape.
Question : Si j'ai 3 pommes et que j'en mange 2, combien en reste-t-il ?
Réfléchissons :
1. J'ai 3 pommes
2. J'en mange 2
3. 3 - 2 = 1
Réponse : 1

Question : {question}
Réfléchissons :"""

# System prompt structuré
system = """Tu es un assistant expert en programmation.
Règles :
- Réponds en français
- Montre le code dans des blocs ```python
- Explique chaque étape
- Si tu ne sais pas, dis-le honnêtement"""
```

---

## 9. Fine-Tuning Paramètres

| Paramètre | Valeur typique | Rôle |
|-----------|---------------|------|
| Learning rate | 2e-5 (full) / 1e-4 (LoRA) | Pas d'apprentissage |
| Batch size | 4-64 | Échantillons par étape |
| Epochs | 1-3 | Passes sur les données |
| Warmup ratio | 0.03-0.1 | Montée progressive du LR |
| Weight decay | 0.01-0.1 | Régularisation |
| Max seq length | 512-4096 | Longueur de séquence |
| Gradient accumulation | 4-16 | Simule de plus gros batchs |

---

## 10. Évaluation

```python
# Benchmarks standard
- MMLU : compréhension multitâche
- HumanEval : génération de code
- GSM8K : raisonnement mathématique
- HellaSwag : complétion de bon sens
- TruthfulQA : véracité
- MT-Bench : chat multi-tour
- AlpacaEval : comparaison avec GPT-4

# lm-evaluation-harness
# lm_eval --model hf --model_args pretrained=meta-llama/Llama-3-8B \
#         --tasks mmlu,hellaswag,gsm8k --batch_size 8
```

---

## Références
- Attention Is All You Need : https://arxiv.org/abs/1706.03762
- Llama : https://llama.meta.com/
- HuggingFace TRL : https://huggingface.co/docs/trl/
- vLLM : https://docs.vllm.ai/
- PEFT : https://huggingface.co/docs/peft/