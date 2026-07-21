---
name: nlp-tokenizers
description: Use when you need to understand, implement, or debug NLP tokenizers — BPE, WordPiece, Unigram, SentencePiece, tokenizer training, vocab management, special tokens, et intégration HuggingFace.
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [nlp, tokenizers, bpe, wordpiece, sentencepiece, preprocessing, huggingface]
    related_skills: [nlp-embeddings, nlp-transformers, llm]
---

# Tokenizers NLP — Segmentation de Texte et Vocabulaires

## Vue d'ensemble

Les tokenizers sont la première couche de toute pipeline NLP. Ils transforment un texte brut en séquence d'identifiants numériques compréhensibles par un modèle. Le choix du tokenizer impacte directement la couverture lexicale, la longueur des séquences, la capacité à généraliser hors-vocabulaire (OOV), et la performance globale du modèle.

Ce skill couvre les 4 algorithmes majeurs de tokenisation, les API standards (HuggingFace `tokenizers`, `transformers.AutoTokenizer`), la gestion des tokens spéciaux, et les techniques avancées (tokenizer merging, vocab pruning).

## Quand l'utiliser

- Vous devez tokeniser/prétokeniser un texte pour un modèle Transformer.
- Vous entraînez un tokenizer personnalisé sur un corpus spécifique (domaine médical, code source, multilingue).
- Vous rencontrez des problèmes de longueur de séquence, de tokens inconnus [UNK], ou de découpage inattendu.
- Vous voulez comprendre comment BPE, WordPiece ou Unigram fonctionnent en profondeur.
- Vous devez optimiser la taille du vocabulaire ou ajouter des tokens spéciaux (PAD, CLS, SEP, MASK).

## Algorithmes de Tokenisation

### 1. Byte-Pair Encoding (BPE)

**Principe :** Algorithme de compression adapté à la tokenisation. Fusionne itérativement les paires de symboles les plus fréquentes jusqu'à atteindre la taille de vocabulaire cible.

**Étapes :**
1. Prétokenisation : découpage en mots via regex (GPT-2 : `r'\p{L}+|\p{N}+|[^\p{L}\p{N}\s]+'`)
2. Initialisation : vocabulaire = tous les caractères uniques (bytes)
3. Itération : trouver la paire (A, B) la plus fréquente → la fusionner en un nouveau symbole AB
4. Arrêt : taille cible atteinte

**Implémentation :**
```python
from tokenizers import Tokenizer, models, trainers, pre_tokenizers

tokenizer = Tokenizer(models.BPE(unk_token="[UNK]"))
tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=True)

trainer = trainers.BpeTrainer(
    vocab_size=30000,
    special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"],
    min_frequency=2,
)
tokenizer.train_from_iterator(corpus_lines, trainer=trainer)
```

**Modèles utilisant BPE :** GPT-1/2/3/4, LLaMA, RoBERTa, BART, T5 (version BPE modifiée), LLaMA 2/3

**Variante : Byte-level BPE (BBPE, utilisé par GPT-2/Llama).** Fonctionne directement sur les bytes, pas de prétokenisation. Garantit zéro OOV technique mais séquences plus longues pour les caractères multi-octets.

### 2. WordPiece

**Principe :** Similaire à BPE mais fusionne les paires qui **maximisent la vraisemblance** du corpus, pas la fréquence brute.

**Critère de fusion :**
```
score = freq(AB) / (freq(A) * freq(B))
```
On fusionne la paire qui maximise ce rapport (meilleur gain de likelihood).

**Implémentation :**
```python
from tokenizers import Tokenizer, models, trainers, pre_tokenizers

tokenizer = Tokenizer(models.WordPiece(unk_token="[UNK]"))
tokenizer.pre_tokenizer = pre_tokenizers.BertPreTokenizer()

trainer = trainers.WordPieceTrainer(
    vocab_size=30000,
    special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"],
    min_frequency=2,
    limit_alphabet=1000,
)
tokenizer.train_from_iterator(corpus_lines, trainer=trainer)
```

**Particularité :** les tokens WordPiece commencent par `##` pour indiquer une continuation de mot (`"playing"` → `"play" + "##ing"`).

**Modèles utilisant WordPiece :** BERT, DistilBERT, ELECTRA, MobileBERT, ALBERT

### 3. Unigram Language Model

**Principe :** Approche probabiliste. Commence avec un large vocabulaire et élimine itérativement les tokens les moins utiles (minimisation de la perte de log-vraisemblance).

**Algorithme :**
1. Initialisation : vocabulaire exhaustif (tous les sous-mots possibles + phrases complètes)
2. E-step : estimer la probabilité de chaque token sur le corpus (via EM)
3. M-step : supprimer les tokens à faible probabilité (typiquement 10-20% par itération)
4. Répéter jusqu'à taille cible

**Avantage :** produit des tokenizations multiples possibles, peut être combiné avec Viterbi/beam search pour trouver la meilleure segmentation.

**Implémentation :**
```python
from tokenizers import Tokenizer, models, trainers, pre_tokenizers

tokenizer = Tokenizer(models.Unigram())
tokenizer.pre_tokenizer = pre_tokenizers.Metaspace()

trainer = trainers.UnigramTrainer(
    vocab_size=30000,
    special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"],
    unk_token="[UNK]",
)
tokenizer.train_from_iterator(corpus_lines, trainer=trainer)
```

**Modèles utilisant Unigram :** XLNet, T5 (version SentencePiece), AlBERT, CamemBERT, FlauBERT

### 4. SentencePiece

**Principe :** Framework de tokenisation **indépendant de la langue** qui fonctionne directement sur le texte brut (pas de prétokenisation). Peut utiliser BPE ou Unigram comme sous-algorithme.

**Particularités :**
- Traite le texte comme une séquence d'Unicode (approche subword régulière)
- Normalisation intégrée (NFKC, lowercase, custom rules)
- Mode **BPE** ou **Unigram** au choix
- Ajoute `▁` (U+2581) comme marqueur de début de mot

**Implémentation :**
```python
import sentencepiece as spm

# Entraînement
spm.SentencePieceTrainer.train(
    input="corpus.txt",
    model_prefix="sp_model",
    vocab_size=32000,
    model_type="bpe",        # ou "unigram"
    character_coverage=0.9995,  # 1.0 pour multilingue
    split_digits=True,
    byte_fallback=True,
)

# Chargement
sp = spm.SentencePieceProcessor(model_file="sp_model.model")
ids = sp.encode("Bonjour le monde", out_type=int)
tokens = sp.encode("Bonjour le monde", out_type=str)
```

**Modèles utilisant SentencePiece :** T5, mT5, ByT5, LLaMA, Gemma, NLLB

## API HuggingFace Transformers

```python
from transformers import AutoTokenizer

# Chargement automatique
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("t5-small")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B")

# Tokenisation
enc = tokenizer(
    "Bonjour le monde",
    padding="max_length",
    truncation=True,
    max_length=512,
    return_tensors="pt",  # "pt", "tf", "np"
)
# → input_ids, attention_mask, token_type_ids

# Détokenisation
tokenizer.decode(enc["input_ids"][0], skip_special_tokens=True)
# → "Bonjour le monde"

# Batch processing
batch = tokenizer(
    ["phrase 1", "phrase 2", "phrase 3"],
    padding=True,
    truncation=True,
    max_length=128,
    return_tensors="pt",
)
```

## Gestion des Tokens Spéciaux

```python
# Ajout de nouveaux tokens spéciaux
tokenizer.add_special_tokens({
    "pad_token": "[PAD]",
    "cls_token": "[CLS]",
    "sep_token": "[SEP]",
    "mask_token": "[MASK]",
    "unk_token": "[UNK]",
    "bos_token": "<s>",
    "eos_token": "</s>",
    "additional_special_tokens": ["[ENTITY]", "[CUSTOM]"]
})

# Ajout de tokens de vocabulaire (résize de l'embedding matrix nécessaire)
num_added = tokenizer.add_tokens(["mon_token", "autre_token"])
model.resize_token_embeddings(len(tokenizer))
```

## Optimisation et Dépannage

### Problème : découpage trop agressif (trop de tokens)
```python
# Option 1 : augmenter le vocabulaire
# Option 2 : utiliser un tokenizer avec coverage multilingue
# Option 3 : ajouter des tokens du domaine
tokenizer.add_tokens(["TensorFlow", "PyTorch", "JAX", "transformers"])
```

### Problème : [UNK] en masse sur un domaine spécialisé
```python
# Solution : entraîner un tokenizer mixte (fusion)
from tokenizers import Tokenizer, trainers
# Entraîner sur corpus général + spécialisé
combined_corpus = general_corpus + domain_corpus
tokenizer.train_from_iterator(combined_corpus, trainer=trainer)
```

### Réduction de la longueur de séquence (LLM inference)
```python
# Utiliser un tokenizer plus récent (LLaMA 3 tokenizer plus efficace que GPT-2)
# Vérifier le nombre de tokens
tokens = tokenizer.encode(long_text)
print(f"Tokens: {len(tokens)}, Caractères: {len(long_text)}")
# Ratio ~3.5 caractères/token pour l'anglais
```

## Pièges Courants (Common Pitfalls)

1. **Tokenizer non aligné avec le pré-entraînement.** Un modèle pré-entraîné a un tokenizer fixe — ne pas le modifier sans ré-entraîner ou au moins adapter la couche d'embedding.
2. **Oubli de resize_token_embeddings après add_tokens().** Le modèle ne connaît pas les nouveaux IDs d'embedding.
3. **Pad token manquant sur les modèles génératifs.** GPT-2, LLaMA n'ont pas de pad_token par défaut — utiliser le eos_token comme pad.
4. **Attention mask non fourni pendant l'inférence.** Les séquences paddées sans attention_mask produisent des embeddings de padding non nuls.
5. **Tokenizer différent entre entraînement et inférence.** Résultat : des IDs hors distribution et des résultats catastrophiques.
6. **Truncation par la gauche vs droite.** Pour les modèles génératifs (GPT), il faut tronquer la gauche (conserver la fin). Pour BERT, tronquer la droite.
7. **Vocabulaire trop petit pour un corpus spécialisé.** Augmenter vocab_size ou ajouter des tokens du domaine.

## Liste de vérification (Checklist)

- [ ] Le tokenizer correspond au modèle pré-entraîné (vérifier config.json)
- [ ] Les tokens spéciaux sont définis (pad, unk, bos, eos selon le modèle)
- [ ] La troncature et le padding sont cohérents avec le type de modèle (génératif vs bi-directionnel)
- [ ] L'attention mask est fourni avec les input_ids
- [ ] Le vocabulaire a été redimensionné si des tokens ont été ajoutés
- [ ] La normalisation SentencePiece/byte-level est cohérente entre entraînement et inférence
