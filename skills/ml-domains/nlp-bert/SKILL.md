---
name: nlp-bert
description: Use when working with BERT and its variants — architecture, pre-training, fine-tuning, inference, embeddings, distillé, optimisation, et benchmarks (RoBERTa, DistilBERT, ALBERT, ELECTRA, DeBERTa, SpanBERT).
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [nlp, bert, roberta, electra, deberta, bidirectional, masked-lm, fine-tuning]
    related_skills: [nlp-tokenizers, nlp-embeddings, nlp-fine-tuning, nlp-transformers, transformers-avance]
---

# BERT — Bidirectional Encoder Representations from Transformers

## Vue d'ensemble

BERT (Devlin et al., 2019) a marqué un tournant en NLP avec son pré-entraînement bidirectionnel profond. Contrairement aux modèles autoregressifs (GPT), BERT utilise un **Masked Language Model (MLM)** pour capturer le contexte gauche ET droit simultanément. Il définit le paradigme "pré-entraînement + fine-tuning" qui domine le NLP depuis 2019.

Ce skill couvre : l'architecture BERT de base, les 2 objectifs de pré-entraînement, le fine-tuning par tâche, les variantes majeures (RoBERTa, DistilBERT, ALBERT, ELECTRA, DeBERTa), les techniques d'optimisation, et les benchmarks.

## Architecture BERT

**Spécifications des tailles standard :**

| Modèle   | Couches | Hidden | Têtes | Paramètres |
|----------|---------|--------|-------|------------|
| BERT-base| 12      | 768    | 12    | 110M       |
| BERT-large| 24     | 1024   | 16    | 340M       |

**Composants :**
- Embedding layer : token + segment (token_type) + position (sinusoïdal appris)
- N × Transformer Encoder blocks (attention bidirectionnelle)
- MLM head + NSP head (pré-entraînement)

**Objectif combiné de pré-entraînement :**

1. **Masked Language Model (MLM) :** 15% des tokens sont masqués → prédire le token original.
   - 80% → `[MASK]`, 10% → token aléatoire, 10% → inchangé
   - Évite le décalage pré-entraînement/fine-tuning (pas de `[MASK]` en fine-tuning)

2. **Next Sentence Prediction (NSP) :** Prédire si deux phrases se suivent (50% vrai, 50% aléatoire).
   - **Attention :** RoBERTa a montré que NSP n'est pas nécessaire
   - Albert l'a remplacé par Sentence Order Prediction (SOP)

## Pré-entraînement BERT

```python
from transformers import BertForPreTraining, BertTokenizer, DataCollatorForLanguageModeling
from datasets import load_dataset

model = BertForPreTraining.from_pretrained("bert-base-uncased")
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Collateur pour MLM
collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=True,
    mlm_probability=0.15,
)
```

## Fine-tuning BERT

### Classification de texte
```python
from transformers import BertForSequenceClassification, Trainer, TrainingArguments

model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2,
)

training_args = TrainingArguments(
    output_dir="./bert_classifier",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    warmup_ratio=0.1,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
)

trainer.train()
```

### Question Answering (SQuAD)
```python
from transformers import BertForQuestionAnswering

model = BertForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

inputs = tokenizer(
    question, context,
    return_tensors="pt",
    max_length=384,
    truncation="only_second",
)

outputs = model(**inputs)
start_logits = outputs.start_logits
end_logits = outputs.end_logits

# Extraction de la réponse
start_idx = torch.argmax(start_logits)
end_idx = torch.argmax(end_logits[start_idx:]) + start_idx
answer = tokenizer.decode(inputs["input_ids"][0][start_idx:end_idx+1])
```

### Token Classification (NER)
```python
from transformers import BertForTokenClassification

model = BertForTokenClassification.from_pretrained(
    "bert-base-cased",
    num_labels=9,  # B-PER, I-PER, B-ORG, etc.
)
```

## Variantes de BERT

### RoBERTa (Robustly Optimized BERT, Liu et al., 2019)

**Améliorations clés :**
- Suppression du NSP (entraînement sur phrases contiguës)
- Dynamic Masking (masque différent à chaque epoch)
- Plus gros batches (8K vs 256) et plus de données (160GB vs 16GB)
- Tokenizer BPE byte-level (pas WordPiece)
- Optimiseur Adam avec plus d'itérations

```python
from transformers import RobertaForSequenceClassification, RobertaTokenizer

model = RobertaForSequenceClassification.from_pretrained("roberta-large")
tokenizer = RobertaTokenizer.from_pretrained("roberta-large")
```

**Variante : RoBERTa-multilingual** — XLM-R (Conneau et al., 2020). 100 langues, 2.5TB de données CommonCrawl, state-of-the-art multilingue.

### DistilBERT (Sanh et al., 2019)

**Distillation de connaissance :** BERT-base (teacher) → DistilBERT (student, 40% plus petit, 60% plus rapide).

```python
from transformers import DistilBertForSequenceClassification

model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased")
```

**Pas de token_type_ids** (DistilBERT n'a pas la tête NSP), garde 97% des performances de BERT.

### ALBERT (Lan et al., 2020)

**Réduction de paramètres :**
1. **Factorisation de l'embedding :** `V × H` → `V × E + E × H` (E << H)
2. **Paramètres partagés :** tous les blocs Transformer partagent les mêmes poids

| Modèle   | Paramètres | Performance (GLUE) |
|----------|------------|-------------------|
| BERT-large | 334M     | 84.5              |
| ALBERT-xxl | 235M     | 89.4 (SOP)        |

**Objectif SOP (Sentence Order Prediction) :** Prédire l'ordre des phrases (pas si elles se suivent mais dans quel ordre). Plus difficile que NSP.

### ELECTRA (Clark et al., 2020)

**Architecture GAN pour le NLP :**
- **Generator :** petit MLM (remplace les tokens masqués)
- **Discriminator :** BERT classifiant chaque token comme "original" ou "remplacé"

**Avantage :** utilise TOUS les tokens (pas seulement les 15% masqués). Plus efficace en calcul à performance égale.

```python
from transformers import ElectraForPreTraining, ElectraTokenizer

model = ElectraForPreTraining.from_pretrained("google/electra-base-discriminator")
tokenizer = ElectraTokenizer.from_pretrained("google/electra-base-discriminator")
```

### DeBERTa (He et al., 2021)

**DeBERTa (Decoding-enhanced BERT with disentangled attention) :**
- **Désentrelacement :** attention calculée séparément sur le contenu et la position
- **Absolute position decoding layer** ajoutée pour l'attention croisée

**DeBERTa-v3 :** améliore l'efficacité du pré-entraînement avec ELECTRA-style.

State-of-the-art sur SuperGLUE et MNLI.

```python
from transformers import DebertaV2ForSequenceClassification

model = DebertaV2ForSequenceClassification.from_pretrained("microsoft/deberta-v3-large")
```

### SpanBERT (Joshi et al., 2020)

**Spécialisé boundary masking :** masque des spans contigus de tokens (pas des tokens isolés).

**Objectif :** Span Boundary Objective (SBO) — prédire un token masqué à partir des embeddings de ses tokens de bordure.

Excellent pour NER, QA, relation extraction.

## Comparatif des Variantes

| Variante    | Principe | Nb param | Performance | Cas d'usage |
|-------------|----------|----------|-------------|-------------|
| BERT        | MLM+NSP  | 110-340M | Baseline    | Général    |
| RoBERTa     | MLM only, dynamic mask | 125-355M | +3-4% GLUE | NLP général, benchmarks |
| DistilBERT  | Distillation | 66M | 97% perf, 60% plus rapide | Production, devices |
| ALBERT      | Partage + factorisation | 12-235M | Niveau BERT-large | Ressources limitées |
| ELECTRA     | Discriminateur MLM | 110-335M | +5% GLUE | Haute performance |
| DeBERTa     | Attention désentrelacée | 140-435M | SOTA SuperGLUE | Recherche |
| SpanBERT    | Span masking + SBO | 110-340M | +5% NER/QA | Extraction |

## Optimisation BERT

### Quantification (ONNX)
```python
from optimum.onnxruntime import ORTModelForSequenceClassification, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig

model = ORTModelForSequenceClassification.from_pretrained("bert-base-uncased")
quantizer = ORTQuantizer.from_pretrained(model)
qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False)
quantizer.quantize(save_dir="./bert_quantized", quantization_config=qconfig)
```

### Inférence accélérée
```python
# Flash Attention (scaling du temps à l'inférence)
model.to("cuda")
with torch.inference_mode():
    outputs = model(**inputs)  # Déjà optimisé par PyTorch compile?

# TorchScript
traced_model = torch.jit.trace(model, (inputs["input_ids"], inputs["attention_mask"]))
```

### Fine-tuning efficace (PEFT)
Voir `nlp-fine-tuning` pour LoRA/QLoRA sur BERT.

## Pièges Courants (Common Pitfalls)

1. **Tokenizer BERT cased vs uncased.** Changer entre les deux casse la compréhension des majuscules/noms propres. Toujours utiliser le tokenizer correspondant au modèle.
2. **Longueur de séquence dépassée.** BERT plafonne à 512 tokens. Utiliser des modèles Longformer/BigBird pour des séquences plus longues.
3. **Pas de redimensionnement après ajout de tokens.** `model.resize_token_embeddings(len(tokenizer))` obligatoire si `add_tokens()` a été utilisé.
4. **NSP inutile après RoBERTa.** Ne pas gaspiller du calcul sur NSP pour des modèles modernes.
5. **Attention mask oublié sur les séquences paddées.** Les embeddings de padding polluent l'attention.

## Liste de vérification (Checklist)

- [ ] Choix de la variante BERT adaptée (RoBERTa, DistilBERT, etc.) selon le budget et la tâche
- [ ] Tokenizer correspondant exactement au modèle pré-entraîné
- [ ] Troncature gérée (max_length=512, truncation_strategy adaptée)
- [ ] Learning rate fine-tuning typique : 2e-5 à 5e-5
- [ ] Warmup ratio (10%) pour stabiliser l'entraînement
- [ ] Evaluation sur validation après chaque epoch
