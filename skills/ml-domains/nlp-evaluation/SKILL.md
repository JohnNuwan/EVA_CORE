---
name: nlp-evaluation
description: Use when evaluating NLP models — metrics (BLEU, ROUGE, METEOR, CIDEr, BERTScore, MoverScore, perplexity, chrF, TER), benchmarks (GLUE, SuperGLUE, SQuAD, XTREME, HellaSwag, MMLU, ARC), human evaluation, et interprétation des scores.
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [nlp, evaluation, metrics, benchmarks, bleu, rouge, bertscore, glue, superglue, mmlu, perplexity]
    related_skills: [nlp-transformers, nlp-bert, nlp-gpt, nlp-t5, evaluating-llms-harness]
---

# Évaluation en NLP — Métriques et Benchmarks

## Vue d'ensemble

L'évaluation est un pilier du NLP : sans métriques fiables, impossible de comparer des modèles, d'optimiser des hyperparamètres, ou de faire du reporting scientifique. Ce skill couvre les métriques automatisées (n-gram, embedding, LLM-based), les benchmarks standardisés (GLUE, SuperGLUE, MMLU, etc.), les protocoles d'évaluation humaine, et les bonnes pratiques pour éviter les pièges statistiques.

## Quand l'utiliser

- Vous devez évaluer un modèle de génération (résumé, traduction, dialogue)
- Vous comparez des modèles sur un benchmark standardisé
- Vous interprétez des métriques et voulez comprendre leurs limites
- Vous mettez en place un pipeline d'évaluation automatisé
- Vous voulez éviter les pièges de la significativité statistique

## Métriques Automatisées

### Métriques Basées sur les n-grammes

#### BLEU (Papineni et al., 2002)

**Principe :** Précision modifiée des n-grammes (1-gram à 4-gram) avec une pénalité de brièveté (BP).

```
BLEU = BP × exp(Σ (1/4) log p_n)
BP = min(1, exp(1 - |ref|/|cand|))
```

**Calcul :**
```python
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

reference = ["le chat est sur le tapis"]
candidate = "le chat sur le tapis"

# Avec smoothing (évite BLEU=0 pour les phrases courtes)
smoothie = SmoothingFunction().method4
bleu = sentence_bleu([reference.split()], candidate.split(), smoothing_function=smoothie)
# → BLEU ≈ 0.62

# BLEU-4 standard
from datasets import load_metric
bleu_metric = load_metric("bleu")
results = bleu_metric.compute(predictions=[candidate.split()], references=[[ref.split()]])
```

**Limites :**
- Ne capture pas la sémantique (synonymes pénalisés)
- Fonctionne mal pour les phrases très courtes
- Pas de notion de recall (précision pure)

**Corpus BLEU :** calcule la moyenne géométrique sur tout le corpus, pas la moyenne des BLEU individuels.

#### ROUGE (Lin, 2004)

**Famille de métriques :**
- **ROUGE-N** : recall des n-grammes (N=1, 2)
- **ROUGE-L** : Longest Common Subsequence (LCS)
- **ROUGE-W** : Weighted LCS
- **ROUGE-S** : Skip-gram co-occurrence

```python
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
scores = scorer.score("le chat est sur le tapis", "le chat sur le tapis")
# → {'rouge1': {'f': 0.83, 'p': 0.83, 'r': 0.83}, ...}

# With HuggingFace evaluate
import evaluate
rouge = evaluate.load("rouge")
results = rouge.compute(predictions=["le chat sur le tapis"],
                         references=["le chat est sur le tapis"])
```

**ROUGE-L** est le plus utilisé pour la summarization. Mesure la plus longue sous-séquence commune (pas nécessairement contiguë).

#### METEOR (Banerjee & Lavie, 2005)

**Principe :** Alignement d'unigrammes avec stemmatisation, synonymes (WordNet), et pénalité de fragmentation.

```
METEOR = (1 - penalty) × F_mean
penalty = 0.5 × (chunks / unigrams_matched)^3
```

**Avantage sur BLEU :** corrélation humaine plus élevée, prend en compte les synonymes.

```python
from nltk.translate.meteor_score import meteor_score

score = meteor_score(["le chat est sur le tapis"], "le chat sur le tapis")
```

#### chrF (Popović, 2015)

**Principe :** F-score basé sur les n-grammes de caractères (pas de mots). Excellent pour les langues morphologiquement riches.

```python
from sacrebleu import corpus_chrf

score = corpus_chrf(["le chat sur le tapis"], [["le chat est sur le tapis"]])
```

#### TER (Translation Edit Rate)
**Principe :** Nombre d'éditions (insertion, suppression, substitution, décalage) nécessaires pour transformer la candidate en référence. Plus bas = meilleur.

### Métriques Basées sur les Embeddings

#### BERTScore (Zhang et al., 2020)

**Principe :** Similarité cosinus entre les embeddings BERT des tokens candidats et de référence.

```
BERTScore = (1 + β²) × precision × recall / (β² × precision + recall)
precision = Σ_i max_j cos(e_i_cand, e_j_ref)
recall = Σ_j max_i cos(e_i_cand, e_j_ref)
```

```python
from bert_score import score

P, R, F1 = score(
    ["le chat sur le tapis"],
    ["le chat est sur le tapis"],
    lang="fr",
    model_type="bert-base-multilingual-cased",
    rescale_with_baseline=True,
)
# F1 ≈ 0.96 (corrélation humaine élevée)
```

**Avantages :** Capture la similarité sémantique, bon pour les paraphrases.
**Limite :** Nécessite un GPU, sensible au choix du modèle BERT.

#### MoverScore (Zhao et al., 2019)

**Principe :** Extension de BERTScore avec le **Word Mover's Distance (WMD)** — distance de transport optimal entre les distributions de sens.

Plus sensible que BERTScore aux différences sémantiques fines.

#### BLEURT (Sellam et al., 2020)

**Principe :** Modèle T5 fine-tuné sur des jugements humains pour prédire la qualité d'une traduction.

```python
from bleurt import score

checkpoint = "bleurt/BLEURT-20"
scorer = score.BleurtScorer(checkpoint)
scores = scorer.score(references=[reference], candidates=[candidate])
```

### Métriques de Classification

```python
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

# Classification standard
accuracy = accuracy_score(y_true, y_pred)
precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro")

# Pour multi-label
from sklearn.metrics import classification_report
print(classification_report(y_true, y_pred, target_names=labels))
```

#### Perplexité (PPL)

**Principe :** Mesure de l'incertitude du modèle sur un corpus. Plus bas = mieux.

```
PPL = exp(-(1/N) Σ log P(x_i | x_<i))
```

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import math

model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

inputs = tokenizer("Le transformateur a révolutionné le NLP.", return_tensors="pt")
with torch.no_grad():
    outputs = model(**inputs, labels=inputs["input_ids"])
    loss = outputs.loss
    ppl = math.exp(loss.item())

print(f"Perplexité: {ppl:.2f}")
# GPT-2 sur texte anglais : 30-40
# LLaMA-7B sur texte anglais : 7-10
# Mistral-7B sur texte anglais : 5-6
```

## Benchmarks Standardisés

### GLUE (General Language Understanding Evaluation)

9 tâches de compréhension du langage :
- **CoLA** : acceptabilité linguistique (Matthews Corr.)
- **SST-2** : sentiment (Accuracy)
- **MRPC** : paraphrase (F1/Accuracy)
- **STS-B** : similarité textuelle (Pearson/Spearman)
- **QQP** : paraphrase Quora (F1/Accuracy)
- **MNLI** : inférence naturelle (Accuracy)
- **QNLI** : QA inférence (Accuracy)
- **RTE** : entailment textuel (Accuracy)
- **WNLI** : anaphore Winograd (Accuracy)

```python
from datasets import load_dataset

glue_dataset = load_dataset("glue", "sst2")
glue_metric = load("glue", "sst2")
```

### SuperGLUE

Version plus difficile de GLUE :
- **BoolQ** : QA binaire
- **CB** : entailment 3 classes
- **COPA** : choix causal de phrase
- **MultiRC** : QA multi-réponses
- **ReCoRD** : QA lecture complétion
- **RTE** : entailment (même que GLUE)
- **WiC** : sens du mot en contexte
- **WSC** : résolution de coréférence Winograd

### MMLU (Massive Multitask Language Understanding)

57 sujets (STEM, humanities, social sciences, medicine, etc.) en format question à choix multiples.

```python
from datasets import load_dataset

mmlu = load_dataset("mmlu", "all")
# Format : {"question": "...", "choices": ["A", "B", "C", "D"], "answer": 0}
```

### HellaSwag

**Principe :** Complétion de phrases avec choix déroutants (adversarial filtering). Teste le "common sense reasoning".

### SQuAD (Stanford Question Answering Dataset)

**SQuAD 1.1 :** extraction de réponse dans un passage.
**SQuAD 2.0 :** ajoute des questions sans réponse.

Métriques : Exact Match (EM) et F1.

```python
from datasets import load_metric

squad_metric = load_metric("squad")
predictions = [{"id": "q1", "prediction_text": "Paris"}]
references = [{"id": "q1", "answers": {"text": ["Paris", "la ville de Paris"], "answer_start": [0, 0]}}]
squad_metric.compute(predictions=predictions, references=references)
```

### XTREME (Cross-lingual TRansfer Evaluation of Multilingual Encoders)

9 tâches, 40 langues. Évalue la capacité multilingue des modèles.

### Autres Benchmarks

- **ARC** (AI2 Reasoning Challenge) : questions scientifiques, easy/challenge
- **TruthfulQA** : véracité des réponses
- **HumanEval** : génération de code Python
- **GSM8K** : mathématiques multi-étapes
- **BigBench** : 204 tâches extrêmement variées

## Évaluation Humaine

### Protocole
- **Multi-annotateurs :** minimum 3 annotateurs par échantillon
- **Fleiss' Kappa** : mesure de l'accord inter-annotateur
- **Échelles :** Likert 1-5, pairwise comparisons, Best-Worst Scaling

### Critères
- **Fluidité** : grammaire, naturel
- **Adéquation** : information correcte
- **Cohérence** : logique et structure
- **Utilité** : pertinence pour la tâche

## Significativité Statistique

```python
import numpy as np
from scipy.stats import bootstrap

# Bootstrap pour comparer deux modèles
def bootstrap_significance(scores_a, scores_b, n_resamples=10000):
    diffs = np.array(scores_a) - np.array(scores_b)

    # Intervalle de confiance bootstrap
    res = bootstrap((diffs,), np.mean, n_resamples=n_resamples)
    ci = res.confidence_interval

    # Significativité à 95%
    if ci.low > 0:
        return f"A significativement meilleur (IC: [{ci.low:.3f}, {ci.high:.3f}])"
    elif ci.high < 0:
        return f"B significativement meilleur (IC: [{ci.low:.3f}, {ci.high:.3f}])"
    else:
        return f"Pas de différence significative (IC: [{ci.low:.3f}, {ci.high:.3f}])"
```

## Pièges Courants (Common Pitfalls)

1. **BLEU score anonyme (sans nom de tokenizer).** BLEU varie selon le tokenizer. Utiliser `sacrebleu` pour des résultats reproductibles.
2. **ROUGE sans stemming.** Les flexions grammaticales (chat/chats) réduisent artificiellement le score.
3. **Moyenne des BLEU phrase par phrase ≠ corpus BLEU.** Toujours calculer le BLEU agrégé sur tout le corpus.
4. **Perplexité non comparable entre tokenizers.** PPL dépend du vocabulaire. Comparer uniquement avec le même tokenizer.
5. **Benchmark contamination.** Vérifier que le modèle n'a pas vu les données de test pendant l'entraînement.
6. **Pas d'intervalle de confiance.** Une différence de 0.2 BLEU peut être non significative.
7. **Évaluation humaine biaisée.** Annotateurs non natifs, tâche mal définie, échelle ambiguë.

## Liste de vérification (Checklist)

- [ ] Métrique adaptée à la tâche (BLEU/ROUGE pour génération, F1 pour classification)
- [ ] Un tokenizer standardisé (sacrebleu) pour la reproductibilité
- [ ] Intervalle de confiance ou bootstrap pour les comparaisons
- [ ] Évaluation humaine avec accord inter-annotateur (Fleiss' Kappa)
- [ ] Benchmark reconnu pour la tâche (GLUE, MMLU, etc.)
- [ ] Vérification de contamination du dataset de test