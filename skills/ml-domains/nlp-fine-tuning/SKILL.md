---
name: nlp-fine-tuning
description: Use when fine-tuning NLP models — full fine-tuning, Parameter-Efficient Fine-Tuning (PEFT), LoRA, QLoRA, Adapters, Prefix Tuning, Prompt Tuning, IA3, task-specific heads, hyperparameter tuning, et bonnes pratiques.
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [nlp, fine-tuning, peft, lora, qlora, adapters, prompt-tuning, hyperparameters, training]
    related_skills: [nlp-bert, nlp-gpt, nlp-t5, nlp-transformers, llm]
---

# Fine-Tuning de Modèles NLP

## Vue d'ensemble

Le fine-tuning adapte un modèle pré-entraîné à une tâche spécifique sur un dataset cible. Les modèles Transformer modernes (100M-100B+ paramètres) nécessitent des approches de fine-tuning qui équilibrent performance, coût en mémoire VRAM, et temps d'entraînement.

Ce skill couvre l'ensemble des techniques : full fine-tuning, PEFT (LoRA, Adapters, Prefix Tuning, Prompt Tuning, IA3), QLoRA, choix des hyperparamètres, stratégies d'optimisation, et comparaison des approches.

## Quand l'utiliser

- Vous devez adapter un modèle pré-entraîné (BERT, GPT, T5, LLaMA) à votre tâche
- Vous voulez fine-tuner efficacement avec une VRAM limitée (8-24GB)
- Vous comparez les techniques PEFT pour choisir la meilleure approche
- Vous optimisez les hyperparamètres (LR, batch size, warmup)
- Vous déployez un modèle fine-tuné en production

## Full Fine-Tuning

**Principe :** Tous les paramètres du modèle sont mis à jour pendant l'entraînement.

**Avantages :** Potentiel de performance maximal, aucune modification architecturale.
**Inconvénients :** VRAM très élevée (chaque paramètre a un état d'optimiseur), temps long, stockage d'un checkpoint complet par tâche.

**Budget VRAM indicatif :**
```
Modèle  | Full FP32 | Full FP16 | LoRA r=8 | QLoRA
--------|-----------|-----------|----------|-------
BERT-base | 8GB    | 4GB       | 3GB      | 2GB
BERT-large | 16GB  | 8GB       | 6GB      | 3GB
LLaMA-7B  | 56GB   | 28GB      | 16GB     | 6GB
Mistral-7B | 56GB  | 28GB      | 16GB     | 6GB
LLaMA-13B | 104GB  | 52GB      | 30GB     | 10GB
```

**Recommandation :** full fine-tuning uniquement pour les modèles < 1B paramètres ou avec > 48GB VRAM.

## Parameter-Efficient Fine-Tuning (PEFT)

### LoRA (Low-Rank Adaptation, Hu et al., 2021)

**Principe :** Approxime la mise à jour des poids ∆W par une factorisation de rang faible.

```
∆W = B × A    où B ∈ R^(d×r), A ∈ R^(r×k), r << min(d, k)
```

- Poids pré-entraînés W figés
- Seuls A et B sont entraînés (r = 8 à 64)
- Applicable aux projections Q, K, V, O de l'attention et aux couches FFN

```python
from peft import LoraConfig, get_peft_model, TaskType

lora_config = LoraConfig(
    r=8,                     # rang de la factorisation
    lora_alpha=32,           # échelle de la mise à jour (alpha / r)
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.3")
peft_model = get_peft_model(model, lora_config)

# Nombre de paramètres entraînables
peft_model.print_trainable_parameters()
# → trainable params: 4.2M / 7.0B (0.06%)
```

**Impact performances :** r=8 atteint 95-99% de la performance du full fine-tuning sur la plupart des tâches.

### QLoRA (Dettmers et al., 2023)

**Principe :** LoRA + Quantization 4-bit NF4 du modèle de base.

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model

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

lora_config = LoraConfig(
    r=64,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.1,
)

peft_model = get_peft_model(model, lora_config)
```

**Budget QLoRA :** 6GB VRAM pour LLaMA-7B, 10GB pour LLaMA-13B, 24GB pour LLaMA-33B.

### Adapters (Houlsby et al., 2019)

**Principe :** Petits modules feed-forward insérés entre les couches du Transformer figé.

```
FFN → Adapter_down (d→bottleneck) → ReLU → Adapter_up (bottleneck→d) → LayerNorm → Skip connection
```

```python
from transformers import AutoModelForSequenceClassification
from adapter_transformers import AdapterConfig, AdapterTrainer

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")

config = AdapterConfig.load(
    "pfeiffer",           # architecture d'adaptateur
    reduction_factor=16,  # facteur de réduction du bottleneck
    non_linearity="relu",
)

model.add_adapter("my_task", config=config)
model.train_adapter("my_task")
```

**Avantages :** Pas de rang à choisir (contrairement à LoRA), architecture bien comprise.
**Inconvénients :** Ajoute un peu de latence à l'inférence (passage dans les adaptateurs).

### Prefix Tuning (Li & Liang, 2021)

**Principe :** Aucun modif sur le modèle. Ajoute des tokens "virtuels" entraînables en début d'entrée.

```
Prompt original : [cls] Classification task. [sep]
Prefix Tuning : [p1][p2][p3]...[pk] [cls] Classification task. [sep]
                  ^-- tokens virtuels entraînés uniquement
```

```python
from peft import PrefixTuningConfig, TaskType, get_peft_model

prefix_config = PrefixTuningConfig(
    task_type=TaskType.SEQ_CLS,
    num_virtual_tokens=20,   # nombre de tokens virtuels
    encoder_hidden_size=768,
    prefix_projection=True,  # MLP non-linéaire avant l'attention
)

model = get_peft_model(model, prefix_config)
```

**Idéal pour :** modèles encodeur (BERT), classification, petits datasets.

### Prompt Tuning (Lester et al., 2021)

**Principe :** Similaire à Prefix Tuning mais plus simple (soft prompts uniquement sur l'embedding layer).

```python
from peft import PromptTuningConfig, PromptTuningInit, TaskType

prompt_config = PromptTuningConfig(
    task_type=TaskType.CAUSAL_LM,
    num_virtual_tokens=20,
    prompt_tuning_init=PromptTuningInit.TEXT,  # ou RANDOM
    prompt_tuning_init_text="Classify the following text:",  # initialisation textuelle
)

model = get_peft_model(model, prompt_config)
# Paramètres entraînés : vocab_size × num_virtual_tokens × d_model
```

### IA3 (Liu et al., 2022)

**Principe :** Vecteurs d'échelle appris (learned vectors) appliqués aux activations des couches clés.

\[  \text{IA3} : h' = l \cdot h \quad\text{et}\quad h = Wx + b \]

Où `l` est un vecteur appris de la même dimension que l'activation.

**Avantages :** encore moins de paramètres que LoRA. Typiquement 10-100K paramètres seulement.

```python
from peft import IA3Config

ia3_config = IA3Config(
    task_type=TaskType.CAUSAL_LM,
    target_modules=["k_proj", "v_proj", "feed_forward"],
    feedforward_modules=["feed_forward"],
)
```

## Comparaison PEFT

| Technique | Paramètres entraînés | Qualité | Inférence | Idéal pour |
|-----------|---------------------|---------|-----------|------------|
| Full FT | 100% | ★★★★★ | Normal | Grands datasets, VRAM illimitée |
| LoRA | 0.01-0.1% | ★★★★☆ | Normal | Général, équilibre qualité/coût |
| QLoRA | 0.01-0.1% | ★★★★☆ | 4-bit | VRAM limitée (6-24GB) |
| Adapters | 1-5% | ★★★★☆ | +légère latence | Multi-tâche, production |
| Prefix Tuning | 0.001-0.01% | ★★★☆☆ | Normal | Petits datasets, encodeurs |
| Prompt Tuning | 0.0001-0.001% | ★★★☆☆ | Normal | Très petits budgets |
| IA3 | 0.0001-0.001% | ★★★☆☆ | Normal | Ultra-efficient |

## Hyperparamètres Clés

### Learning Rate
```python
# Recommandations par technique
lr_map = {
    "full_ft": 2e-5,         # BERT, RoBERTa
    "full_ft_llm": 1e-5,     # LLaMA, GPT
    "lora": 2e-4,            # 5-10× le LR full FT
    "qlora": 2e-4,
    "adapters": 1e-4,
    "prefix_tuning": 5e-5,
    "prompt_tuning": 1e-4,
    "ia3": 1e-3,
}
```

**Règle empirique :** PEFT nécessite un LR 5-10× plus élevé que full fine-tuning car les paramètres entraînés sont bien moins nombreux.

### Optimizer
```python
# Full FT et PEFT
optim = "adamw_torch"  # standard
# ou
optim = "adamw_8bit"   # bitsandbytes, économise 50% mémoire optimizer

# Warmup
training_args = TrainingArguments(
    warmup_ratio=0.1,  # 10% du total des steps en warmup
    lr_scheduler_type="cosine",
)
```

### Batch Size et Gradient Accumulation
```python
training_args = TrainingArguments(
    per_device_train_batch_size=2,    # ajuster à la VRAM
    gradient_accumulation_steps=16,   # batch effectif = 2 × 16 = 32
    # max_grad_norm pour éviter l'explosion des gradients
    max_grad_norm=1.0,
)
```

## Datasets et Tokenisation

```python
from datasets import Dataset, load_dataset
from transformers import DataCollatorForSeq2Seq

dataset = load_dataset("json", data_files="train.jsonl")

def preprocess(examples):
    inputs = tokenizer(
        examples["input"],
        max_length=512,
        truncation=True,
        padding=False,
    )
    targets = tokenizer(
        examples["output"],
        max_length=128,
        truncation=True,
        padding=False,
    )
    inputs["labels"] = targets["input_ids"]
    return inputs

tokenized_dataset = dataset.map(preprocess, batched=True, remove_columns=dataset.column_names)

# Data collator
collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)
```

## Sauvegarde et Fusion

```python
# Sauvegarde des adaptateurs LoRA (poids ~20MB vs modèle complet ~28GB)
peft_model.save_pretrained("./lora_weights/")

# Fusion LoRA → modèle complet (pour inférence plus rapide)
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.3")
merged_model = PeftModel.from_pretrained(base_model, "./lora_weights/")
merged_model = merged_model.merge_and_unload()
merged_model.save_pretrained("./model_merged/")
```

## Pièges Courants (Common Pitfalls)

1. **Oubli de charger le modèle en format approprié pour QLoRA.** `load_in_4bit=True` + `torch_dtype=torch.bfloat16` sur un GPU compatible.
2. **LR trop bas pour PEFT.** Les méthodes PEFT nécessitent un LR 5-10× plus haut que le full FT.
3. **Fusion PEFT avant évaluation sur un benchmark comparatif.** La fusion modifie légèrement le comportement. Toujours évaluer avant ET après fusion.
4. **Ne pas geler les couches non-entraînées.** Vérifier `model.requires_grad_(False)` avant d'appliquer PEFT.
5. **Double comptage des tokens de padding dans la loss.** Utiliser `ignore_index=-100` dans la CrossEntropyLoss.
6. **Appliquer LoRA à tous les modules y compris embedding/lm_head.** Cela gaspille des paramètres sans gain significatif.

## Liste de vérification (Checklist)

- [ ] Technique PEFT choisie selon le budget VRAM et la qualité souhaitée
- [ ] LR adapté à la technique (2e-4 pour LoRA, 2e-5 pour full FT)
- [ ] Warmup cosine scheduler configuré
- [ ] Batch effectif calculé (batch_size × gradient_accumulation)
- [ ] Tokenisation alignée (max_length, truncation, padding)
- [ ] Poids sauvegardés (adaptateurs ou modèle fusionné)
- [ ] Évaluation sur validation avant ET après fusion
