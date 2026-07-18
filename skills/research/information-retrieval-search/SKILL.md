---
name: information-retrieval-search
description: "Compétence en recherche d'information et systèmes de recherche suivie sur arXiv sous cs.IR. Couvre le ranking, la recherche dense, le RAG (retrieval-augmented generation), les moteurs de recherche neuronaux, l'apprentissage à classer, les systèmes de recommandation, la recherche multimodale, la récupération cross-modale, et l'évaluation de la recherche."
category: research
tags: [arxiv, recherche-information, ranking, dense-retrieval, RAG, recommandation, recherche-multimodale, évaluation, retrieval]
---

# Recherche d'Information et Systèmes de Recherche — Recherche sur arXiv

## Présentation

Cette compétence couvre la veille et l'analyse de la recherche en recherche d'information et systèmes de recherche publiée sur arXiv sous `cs.IR`. Elle permet de suivre les avancées en ranking, recherche dense, RAG (retrieval-augmented generation), moteurs de recherche neuronaux, apprentissage à classer (LTR), systèmes de recommandation, recherche multimodale, récupération cross-modale et évaluation de la recherche.

## Domaines de Recherche

### 1. Recherche Neuronale et Ranking
- **Dense retrieval** — recherche par similarité dense dans des espaces vectoriels (DPR, ANCE, REPT)
- **ColBERT** — contextualized late interaction pour le scoring de passages
- **Re-ranking** — modèles cross-encoder pour le re-ranking de résultats (monoT5, RankT5, Cohere)
- **Apprentissage à classer (LTR)** — approches pointwise, pairwise et listwise
- **Sparse retrieval** — modèles à sac-de-mots neuronaux (SPLADE, uniCOIL, BERT-based term weighting)
- **Hybrid retrieval** — combinaison de recherche dense et sparse

### 2. Retrieval-Augmented Generation (RAG)
- **Systèmes hybrides** — architectures combinant retrieval et génération
- **Embedding models** — modèles de plongement textuel pour le RAG (E5, BGE, Instructor, GTE, Voyage)
- **Récupération contextuelle** — intégration du contexte dans la boucle de retrieval
- **RAG multi-étapes** — pipelines de retrieval itératif et de raisonnement
- **RAG multimodal** — retrieval augmenté pour données image, audio, vidéo
- **Fine-tuning pour RAG** — adaptation de modèles pour la tâche de retrieval

### 3. Systèmes de Recommandation
- **Filtrage collaboratif** — factorisation matricielle, modèles basés voisins
- **Factorisation** — SVD, NMF, modèles latents
- **Recommandation séquentielle** — modèles de séquence pour sessions utilisateur (SASRec, BERT4Rec)
- **LLM pour recommandation** — utilisation de grands modèles de langage pour la recommandation (P5, RecLLM)
- **Recommandation sensible au contexte** — intégration du contexte temporel, géographique et social
- **Cold-start** — gestion des nouveaux utilisateurs et nouveaux items

### 4. Recherche Multimodale
- **Cross-modal retrieval** — récupération entre modalités (texte→image, image→texte)
- **CLIP** — modèle de plongement vision-langage (OpenAI CLIP, OpenCLIP, SigLIP)
- **Image-texte** — recherches hybrides image-texte
- **Recherche vidéo** — récupération de contenu vidéo par requêtes textuelles
- **Recherche audio-texte** — récupération cross-modale entre audio et texte

### 5. Évaluation de la Recherche
- **Métriques NDCG** — Normalized Discounted Cumulative Gain
- **MAP** — Mean Average Precision
- **Pertinence** — évaluation de la pertinence des résultats (explicite, implicite)
- **Jugements humains** — collecte et agrégation de jugements de pertinence
- **Évaluation sans jugements** — métriques basées sur le comportement utilisateur (A/B testing, interleaving)
- **Benchmarks** — MS MARCO, TREC, BEIR, MTEB, LoTTE

### 6. Recherche Conversationnelle
- **Agents de recherche** — systèmes de recherche interactifs et conversationnels
- **Search-as-conversation** — recherche incrémentale en mode dialogue
- **Clarification** — pose de questions de clarification pour désambiguïser l'intention
- **Search-oriented dialogue** — dialogues orientés vers la recherche d'information

## Catégories arXiv

- `cs.IR` — Information Retrieval
- `cs.CL` — Computation and Language
- `cs.LG` — Machine Learning
- `cs.CV` — Computer Vision and Pattern Recognition

## Utilisation

### Recherche hebdomadaire
```bash
# Recherche dense
arxiv_search query="dense retrieval ColBERT DPR" categories=cs.IR max_results=10

# RAG
arxiv_search query="retrieval augmented generation RAG" categories=cs.IR,cs.CL max_results=10

# Systèmes de recommandation
arxiv_search query="recommender system LLM sequential" categories=cs.IR max_results=10

# Recherche multimodale
arxiv_search query="cross-modal retrieval CLIP text-image" categories=cs.IR,cs.CV max_results=10

# Évaluation
arxiv_search query="retrieval evaluation NDCG benchmark MTEB" categories=cs.IR max_results=10
```

### Veille continue
- Surveiller les nouvelles soumissions dans `cs.IR` quotidiennement
- Suivre les conférences: SIGIR, CIKM, WSDM, ECIR, NeurIPS, ICML
- Consulter les benchmarks MTEB et BEIR pour les modèles de retrieval
- Configurer des alertes arXiv pour: "dense retrieval", "RAG", "ColBERT", "cross-encoder", "recommender", "CLIP"

## Articles Notables

| Article | Domaine |
|---------|---------|
| DPR (Facebook) | Dense Passage Retrieval |
| ColBERT (Stanford) | Late interaction retrieval |
| SPLADE | Sparse lexical retrieval |
| monoT5 / RankT5 | Re-ranking |
| E5 / BGE / Instructor | Embedding models |
| P5 / RecLLM | LLM pour recommandation |
| MS MARCO | Benchmark de passage ranking |
| BEIR | Benchmark cross-domain retrieval |

## Mise à Jour

Cette compétence doit être mise à jour mensuellement avec les nouveaux modèles de retrieval, les avancées en RAG, les nouvelles architectures de recommandation et les benchmarks émergents.