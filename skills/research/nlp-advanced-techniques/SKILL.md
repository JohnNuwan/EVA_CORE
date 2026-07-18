---
name: nlp-advanced-techniques
description: "Compétence niveau expert en techniques avancées de NLP. Couvre les embeddings (Word2Vec, GloVe, FastText, ELMo), les transformers BERT/RoBERTa/ALBERT/DeBERTa, les approches few-shot/zero-shot, les prompt engineering avancées, le decoding (beam search, top-k, top-p, temperature, contrastive, speculative), les evaluation metrics (BLEU, ROUGE, METEOR, BERTScore, COMET, BLEURT, Perplexity), les data augmentation, le data labeling, les tokenizers (BPE, WordPiece, SentencePiece, Unigram), NER, RE, EE, QA, summarization, translation, parsing, et cross-lingual transfer."
keywords: [NLP, transformers, embeddings, tokenization, few-shot, decoding, evaluation, NER, LLM]
categories: [cs.CL, cs.LG, cs.AI, cs.IR, cs.CY]
---

# Compétence Techniques Avancées de NLP

## Présentation

Cette compétence couvre les techniques avancées de traitement automatique du langage naturel, des embeddings classiques aux Transformers, en passant par le prompt engineering, les méthodes de décodage et l'évaluation.

---

## Embeddings et Architectures

- **Word2Vec** : CBOW (Continuous Bag of Words) et Skip-Gram
- **GloVe** : Global Vectors for Word Representation (co-occurrence matrix)
- **FastText** : Embeddings subword (morphologie, OOV)
- **ELMo** : Embeddings from Language Models (biLM contextuels)
- **BERT** : Bidirectional Encoder Representations from Transformers
- **RoBERTa** : Robustly Optimized BERT Approach (plus de données, plus d'entraînement)
- **XLNet** : Permutation LM (autoregressive avec bidirectionnalité)
- **ALBERT** : A Lite BERT (parameter sharing, factorized embeddings)
- **DeBERTa** : Decoding-enhanced BERT with Disentangled Attention
- **ELECTRA** : Efficiently Learning an Encoder that Classifies Token Replacements
- **T5** : Text-to-Text Transfer Transformer
- **BART** : Bidirectional and Auto-Regressive Transformer
- **Longformer / BigBird** : Transformers pour longs documents (sparse attention)
- **FNet** : Fourier Transform (mix d'attention + Fourier)
- **ConvBERT** : Convolutions + attention
- **LayoutLM** : NLP pour documents structurés
- **Encoder-Decoder / Causal LM** : Architecture encodeur-décodeur vs causal

## Tokenisation

- **BPE (Byte-Pair Encoding)** : Tokenisation GPT (byte-level BPE)
- **WordPiece** : Tokenisation BERT
- **SentencePiece** : Tokenisation non supervisée (Unigram, BPE)
- **Unigram** : Modèle de tokenisation probabiliste
- **tiktoken** : Tokenizer rapide OpenAI (cl100k_base, o200k_base)
- **Tokenizer Training** : Entraînement de tokenizer (merge rules, vocabulary)
- **Merges / Vocabulary** : Fichiers merges.txt et vocab.json
- **Subword Regularization** : Régularisation par différentes segmentations
- **BPE-Dropout** : Dropout lors de la tokenisation pour robustesse
- **Byte-Level BPE** : BPE au niveau byte (universal, pas d'OOV)

## Few-Shot et Zero-Shot

- **Prompting** : Conception de prompts pour tâches NLP
- **In-Context Learning (ICL)** : Apprentissage en contexte avec exemples
- **Few-Shot** : Quelques exemples dans le prompt
- **Zero-Shot** : Pas d'exemple, uniquement l'instruction
- **PET (Pattern-Exploiting Training)** : Exploitation de patterns pour few-shot
- **P-Tuning** : Prompt tuning avec embedding appris
- **Prompt Tuning** : Ajustement des embeddings du prompt (soft prompt)
- **Prefix Tuning** : Ajustement de préfixes pour génération
- **Instruction Tuning (FLAN, T0)** : Fine-tuning sur instructions
- **Natural Instructions** : Instructions en langage naturel
- **Cross-Task Generalization** : Généralisation entre tâches
- **Meta-Learning (MAML)** : Apprendre à apprendre

## Décodage et Génération

- **Greedy Decoding** : Décodage glouton
- **Beam Search** : Recherche par faisceau (beam width, beams)
- **Top-K Sampling** : Échantillonnage parmi les K meilleurs tokens
- **Top-p (Nucleus Sampling)** : Échantillonnage nucleus
- **Temperature** : Contrôle de la température de softmax
- **Repetition Penalty** : Pénalité de répétition
- **No-Repeat N-gram** : Interdiction de répétition de n-grams
- **Contrastive Search** : Recherche contrastive pour cohérence
- **Speculative Decoding** : Décodage spéculatif (draft model + target model)
- **Medusa** : Décodage spéculatif multi-tête
- **Self-Speculative** : Draft avec le même modèle
- **Constrained Decoding** : Décodage sous contraintes (regex, CFG)
- **Grammar-Guided** : Décodage guidé par grammaire
- **Guidance** : Guidance structurée (outlines, jsonformer)

## Évaluation

- **Perplexity** : Mesure de confusion du modèle
- **BLEU** : Bilingual Evaluation Understudy (précision n-gram)
- **ROUGE** : Recall-Oriented Understudy for Gisting Evaluation (ROUGE-1, ROUGE-2, ROUGE-L)
- **METEOR** : Metric for Evaluation of Translation with Explicit ORdering
- **CIDEr / SPICE** : Métriques pour description d'images / scènes
- **BERTScore** : Évaluation basée sur BERT (précision, recall, F1)
- **COMET** : Neural framework pour évaluation de traduction
- **BLEURT** : BERT-based Learned Evaluation metric
- **GEANT / RUSE / QE** : Quality Estimation
- **Human Evaluation** : Likert scale, pairwise, best-of-n
- **LLM-as-Judge** : Évaluation par LLM (MT-Bench, AlpacaEval)
- **MMLU / GSM8K / HumanEval** : Benchmarks standards
- **HELM** : Holistic Evaluation of Language Models
- **LM Eval Harness** : Framework d'évaluation standardisé

## Tâches Avancées

- **NER (Named Entity Recognition)** : Fine-grained, nested, discontinuous
- **RE (Relation Extraction)** : Extraction de relations entre entités
- **EE (Event Extraction)** : Extraction d'événements
- **Nested NER** : Entités imbriquées
- **Discontinuous NER** : Entités discontinues
- **QA (Question Answering)** : Extractive & Generative
- **Summarization** : Abstractive & Extractive
- **MT (Machine Translation)** : NMT avec Transformers
- **Dependency Parsing (UD)** : Parse syntaxique Universal Dependencies
- **Semantic Parsing (AMR)** : Abstract Meaning Representation
- **Discourse Parsing (RST)** : Rhetorical Structure Theory