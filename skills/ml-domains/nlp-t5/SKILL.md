---
name: nlp-t5
description: Use when working with T5 and encoder-decoder models — text-to-text framework, span corruption pre-training, BART, PEGASUS, mT5, FLAN-T5, fine-tuning, summarization, translation, et génération conditionnelle.
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [nlp, t5, encoder-decoder, bart, pegasus, seq2seq, text-to-text, flan]
    related_skills: [nlp-transformers, nlp-fine-tuning, nlp-gpt, nlp-bert, nlp-seq2seq]
---

# T5 — Text-to-Text Transfer Transformer

## Vue d'ensemble

T5 (Raffel et al., 2020) unifie toutes les tâches NLP dans un cadre **text-to-text** : l'entrée et la sortie sont toujours du texte. Cette uniformisation permet d'entraîner un seul modèle sur des dizaines de tâches simultanément. Le pré-entraînement utilise un objectif de **span corruption** (masquage de spans contigus) sur le colossal C4 dataset (750GB).

Ce skill couvre : l'architecture encodeur-décodeur T5, le span corruption, le fine-tuning, les variantes (mT5, FLAN-T5, BART, PEGASUS), les tâches supportées, et les optimisations.

## Architecture Encodeur-Décodeur

**Spécifications :**

| Modèle | Couches | Hidden | Têtes | Paramètres |
|--------|---------|--------|-------|------------|
| T5-small | 6+6 | 512 | 8 | 60M |
| T5-base | 12+12 | 768 | 12 | 220M |
| T5-large | 24+24 | 1024 | 16 | 770M |
| T5-3B | 24+24 | 2048 | 32 | 2.8B |
| T5-11B | 24+24 | 4096 | 64 | 11B |

**Particularités architecturales :**
- **Relative Positional Bias** (pas de position encoding absolu)
- **LayerNorm avant chaque sous-couche** (T5-style, décalé du post-norm)
- **Activation ReLU** (pas GELU, pour des raisons historiques)
- **Same Adapter activé** (paramètres partagés encodeur/décodeur)

## Pré-entraînement : Span Corruption

Contrairement au MLM de BERT (tokens isolés masqués), T5 masque des **spans entiers de tokens** et remplace chaque span par un unique token sentinelle `<extra_id_0>`, `<extra_id_1>`, etc.

**Exemple :**
```
Entrée originale :
"Le transformateur T5 a révolutionné le NLP."

Span corruption (span_length=3, corruption_rate=15%) :
"Le transformateur <extra_id_0> révolutionné le <extra_id_1>."

Cible :
"<extra_id_0> T5 a <extra_id_1> NLP. <extra_id_2>"
```

**Pourcentage de corruption :** 15% du texte, spans de longueur moyenne 3.

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer

model = T5ForConditionalGeneration.from_pretrained("t5-base")
tokenizer = T5Tokenizer.from_pretrained("t5-base")

# Préfixe de tâche
input_text = "translate English to French: The transformer is powerful."
inputs = tokenizer(input_text, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_length=50,
    num_beams=4,
    early_stopping=True,
)

translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Tâches Text-to-Text

T5 utilise des **préfixes textuels** pour indiquer la tâche :

```python
tasks = {
    "summarize": "summarize: Le texte à résumer...",
    "translate": "translate English to French: The text...",
    "classification": "cola sentence: This sentence is correct.",
    "qa": "question: What is T5? context: ...",
    "ner": "Be careful with Morgan Freeman's iguana.",
    "nl2sql": "question: count of employees in sales context: TABLE employees, department",
}
```

### Summarization
```python
from transformers import pipeline

summarizer = pipeline("summarization", model="t5-base")

summary = summarizer(
    long_text,
    max_length=150,
    min_length=30,
    do_sample=False,
    truncation=True,
)
```

### Traduction
```python
model = T5ForConditionalGeneration.from_pretrained("t5-base")
tokenizer = T5Tokenizer.from_pretrained("t5-base")

def translate(text, src="English", tgt="French"):
    input_text = f"translate {src} to {tgt}: {text}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=512, num_beams=5)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Variantes de T5

### FLAN-T5 (Chung et al., 2022)

**Fine-tuned Language Net — T5 amélioré par instruction tuning.**
- FLAN-T5 fine-tuné sur 1800+ tâches en format instruction
- Amélioration massive sur le zero-shot et few-shot
- Disponible en : small, base, large, xl (3B), xxl (11B)

```python
from transformers import T5ForConditionalGeneration, AutoTokenizer

model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
```

**Gains par rapport à T5 vanilla :**
- +20% sur une moyenne de 183 benchmarks
- Meilleur zero-shot que GPT-3 sur plusieurs tâches
- Raisonnement en CoT (Chain-of-Thought) amélioré

### mT5 (Xue et al., 2021)
- T5 multilingue : 101 langues, tokenizer SentencePiece commun
- C4 multilingue couvre 50TB de données
- mT5-small : 300M paramètres

```python
from transformers import MT5ForConditionalGeneration, MT5Tokenizer

model = MT5ForConditionalGeneration.from_pretrained("google/mt5-base")
tokenizer = MT5Tokenizer.from_pretrained("google/mt5-base")
```

### ByT5 (Xue et al., 2022)
- T5 qui tokenise directement les **bytes** (pas de vocabulaire)
- Avantage : 0 OOV, fonctionne sur toute langue sans tokenizer
- Inconvénient : séquences ~4× plus longues

## BART (Lewis et al., 2020)

BART combine les forces de BERT (bidirectionnel encodeur) et GPT (autoregressif décodeur).

**Pré-entraînement :** corruption de texte (denoising) sur l'encodeur, décodeur autoregressif reconstruit.

**Types de corruption BART :**
- Token Masking (masquage aléatoire)
- Token Deletion (suppression)
- Text Infilling (masquage de spans, comme T5)
- Sentence Permutation (mélange de phrases)
- Document Rotation (rotation aléatoire)

```python
from transformers import BartForConditionalGeneration, BartTokenizer

model = BartForConditionalGeneration.from_pretrained("facebook/bart-large")
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large")

# Summarization
summary = model.generate(
    **tokenizer(long_text, return_tensors="pt", max_length=1024, truncation=True),
    max_length=150,
    num_beams=4,
)
```

**Points forts :**
- Excellent pour la **summarization abstractive** (SOTA sur CNN/DailyMail longtemps)
- Très bon pour la compréhension de texte (classification, QA)
- Fine-tuning plus stable que T5 sur petits datasets

## PEGASUS (Zhang et al., 2020)

**Pré-entraînement Gap Sentence Generation (GSG) :**
- MASQUE des phrases entières (pas des tokens) — 30% des phrases
- Apprend à générer les phrases masquées à partir du reste du document

**Idéal pour :** summarization uniquement. Surpasse BART et T5 sur la tâche de résumé.

```python
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

model = PegasusForConditionalGeneration.from_pretrained("google/pegasus-xsum")
tokenizer = PegasusTokenizer.from_pretrained("google/pegasus-xsum")
```

## Comparatif Encodeur-Décodeur

| Modèle | Pré-entraînement | Points forts | Meilleur pour |
|--------|-------------------|--------------|---------------|
| T5 | Span corruption | Multi-tâche, multi-format | Tout NLP |
| FLAN-T5 | T5 + instruction tuning | Zero-shot, few-shot | Instructions |
| BART | Denoising + AR | Summarization, compréhension | Résumé, QA |
| PEGASUS | Gap sentence masking | Summarization | Résumé pur |
| mT5 | C4 multilingue | 101 langues | Multilingue |
| ByT5 | Byte-level | Zéro OOV | Langues rares |

## Fine-tuning T5

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments
from datasets import Dataset

dataset = Dataset.from_dict({
    "input": ["summarize: Le T5 est un modèle puissant."],
    "output": ["T5 est un modèle puissant."],
})

def preprocess(examples):
    inputs = tokenizer(examples["input"], max_length=512, truncation=True, padding="max_length")
    targets = tokenizer(examples["output"], max_length=128, truncation=True, padding="max_length")
    inputs["labels"] = targets["input_ids"]
    return inputs

tokenized = dataset.map(preprocess, batched=True)

training_args = TrainingArguments(
    output_dir="./t5_finetuned",
    learning_rate=3e-4,  # T5 nécessite un LR plus élevé que BERT
    per_device_train_batch_size=8,
    num_train_epochs=5,
    weight_decay=0.01,
    predict_with_generate=True,
    evaluation_strategy="epoch",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
)

trainer.train()
```

## Pièges Courants (Common Pitfalls)

1. **Oubli du préfixe de tâche.** T5 sans préfixe se comporte aléatoirement. Toujours ajouter `"summarize: "`, `"translate: "`, etc.
2. **Token lengths dépassés.** T5-base a une max_length de 512 tokens encodeur. Utiliser LongT5 ou partitionner.
3. **LR trop bas pour T5.** T5 préfère LR 1e-3 à 3e-4 (vs BERT 2e-5). Un LR trop bas ne fine-tune pas efficacement.
4. **Predict_with_generate non activé dans TrainingArguments.** Sans lui, l'évaluation ne décode pas les séquences, juste les logits.
5. **Span corruption mal configuré pour pré-entraînement personnalisé.** Vérifier span_length et corruption_rate.

## Liste de vérification (Checklist)

- [ ] Préfixe de tâche présent dans l'entrée
- [ ] Tokenizer T5/mT5/FLAN-T5 correspondant
- [ ] Learning rate adapté (3e-4 pour T5, 1e-4 pour FLAN-T5)
- [ ] predict_with_generate=True dans les arguments d'entraînement
- [ ] max_length encodeur suffisant (512+)
- [ ] Beam search évalué sur la tâche cible (summarization, translation)
