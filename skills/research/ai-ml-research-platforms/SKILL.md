---
name: ai-ml-research-platforms
description: "Compétence niveau ingénieur/docteur sur les plateformes de recherche en IA/ML. Couvre Hugging Face (modèles, datasets, Spaces, Daily Papers, Trending Papers), PapersWithCode (SOTA, benchmarks, leaderboards), Kaggle (compétitions, datasets, notebooks), OpenReview, ACL Anthology, Semantic Scholar API, OpenAlex, Zeno, W&B, MLflow, Gradio, et l'écosystème MLOps."
category: research
tags: [huggingface, paperswithcode, kaggle, mlops, veille-ia, recherche-ml, openreview]
---

# Plateformes de Recherche en IA/ML — Référence Ingénieur/Docteur

## Présentation

Ce skill couvre l'ensemble des plateformes essentielles pour la veille, la recherche, l'expérimentation et le partage en intelligence artificielle et machine learning. Il est conçu pour un niveau ingénieur/docteur nécessitant une maîtrise approfondie de l'écosystème.

---

## 1. Hugging Face — Écosystème

### Models Hub (1M+ modèles)
- **Transformers** : bibliothèque centrale pour modèles NLP/CV/Audio
- **Diffusers** : modèles de diffusion (Stable Diffusion, Flux)
- **PEFT** : fine-tuning paramètre-efficace (LoRA, AdaLoRA, IA3)
- **TRL** : reinforcement learning pour LLM (DPO, PPO, GRPO)
- **TGI (Text Generation Inference)** : déploiement performant
- **Sentence Transformers** : embeddings et similarité sémantique

### Datasets
- 100k+ datasets sur HF Hub
- Intégration native avec `datasets` library (streaming, map, shard)
- Support image, audio, texte, vidéo, multimodal
- Dataset viewer et configuration

### Spaces
- Déploiement Gradio/Streamlit/Docker instantané
- Hardware : CPU gratuit, GPU T4/L4/A10G/A100 payant
- ZeroGPU pour économie de crédits
- Templates : LLM chat, TTS, STT, image gen, object detection

### HF Papers Daily
- **TradingAgents** (multi-agent LLM) — ~91k GitHub stars
- **SkillOpt** (Microsoft) — optimisation de skills — ~11k stars
- **ResearchStudio-Idea** — génération d'idées de recherche
- Trending papers quotidiens avec code, démos, métriques
- Filtrage par domaine (NLP, CV, RL, Audio, Multimodal)

### Hub API
- `huggingface_hub` Python SDK
- Upload/download modèles et datasets
- Gestion des versions, tags, métadonnées
- Inference API gratuite (rate-limited)

---

## 2. PapersWithCode

### SOTA Tracker
- Suivi de l'état-de-l'art par tâche et par dataset
- Classement par métrique (accuracy, BLEU, F1, MAE, etc.)
- Historique temporel de progression
- Alertes de nouveau SOTA

### Leaderboards
- Par domaine : NLP, CV, Audio, Robotics, Medical, etc.
- Par dataset : ImageNet, GLUE, SQuAD, COCO, etc.
- Filtres : date, venue, type de méthode
- Intégration avec code GitHub

### 100k+ Papers
- Liens directs vers PDF, code, démos
- Métriques rapportées directement extraites
- Évaluation reproductible
- Evaluation Tables : visualisation comparative

### Benchmark API
- `paperswithcode-client` Python
- Requêtes : papers, tasks, datasets, methods, leaderboards
- Pagination, filtrage, recherche

---

## 3. Kaggle

### Featured Competitions
- ARC Prize 2026 : $850k — raisonnement abstrait
- LLM Fine-tuning : optimisation de modèles
- Pokémon TCG AI Battle : $240k — RL avec cartes
- Compétitions classiques : bourses, assurance, santé

### Getting Started
- Titanic, House Prices, Spaceship Titanic
- Introduction à Pandas, ML, DL, Feature Engineering
- Notebooks gagnants commentés

### Research Competitions
- Compétitions académiques sans prize money
- Datasets de recherche : genomics, physics, satellite
- Notebooks Kernel-only avec GPU T4 gratuit

### Playground
- Compétitions synthétiques mensuelles
- Thèmes variés (santé, sport, finance, climat)
- Idéal pour prototypage et exploration

### Kaggle Notebooks
- GPU T4/P100, TPU v3-8 gratuit (30h/semaine)
- BigQuery intégré
- Datasets publics 200k+
- Code competition : soumission directe

---

## 4. MLOps & Expérimentation

### Weights & Biases (W&B)
- Logging d'expériences : metrics, hyperparams, artefacts
- Suivi de runs avec comparaison visuelle
- Sweeps : recherche hyperparamétrique
- Model Registry : gestion de cycle de vie
- Reports : rapports dynamiques et partageables

### MLflow
- Tracking : runs, params, metrics, tags
- Models : packaging, serving, registry
- Projects : reproductibilité, conda/docker env
- Open-source, auto-hébergeable

### Kubeflow
- Pipelines ML sur Kubernetes
- Fairing : build/train/déploy
- Katib : hyperparameter tuning
- KFServing : déploiement serverless

### Neptune
- Metadata store pour expérimentations
- Comparaison de runs, query, search
- Intégration 30+ frameworks
- Dashboard temps réel

### Comet
- Suivi d'expériences collaboratif
- Optimisation d'hyperparamètres
- Monitoring de modèles
- Panneaux personnalisés

### DVC (Data Version Control)
- Versionnement de datasets et modèles
- Pipelines ML reproductibles
- Intégration Git + S3/GCS/SSH
- Experiments : tracking de runs

---

## 5. API Recherche

### Semantic Scholar API
- 200M+ papers académiques
- Champs : title, abstract, authors, venue, citations
- Embeddings : similarité sémantique
- Recommendations personnalisées
- API gratuite avec rate limiting (100 req/s)

### OpenAlex
- Index ouvert de 250M+ travaux académiques
- Entités : works, authors, sources, institutions, concepts
- Graphe de citations complet
- Licence CC0 — usage libre sans restriction
- API REST + RDF

### Crossref
- DOI registration et métadonnées
- 120M+ records avec DOI
- Références bibliographiques
- API gratuite, rate limiting modéré

---

## 6. Plateformes Émergentes

### Zeno
- LLM observability et evaluation
- Comparaison de réponses côte-à-côte
- Métriques personnalisées
- Datasets de test et golden datasets

### Arize AI
- Monitoring de modèles en production
- Dérive de données, biais, performance
- Root cause analysis
- LLM Tracing

### LangFuse
- Observabilité LLM en production
- Traces, spans, coûts, latence
- Prompt management
- Evaluations : LLM-as-judge, human, regex
- Open-source, auto-hébergeable

### Gradio
- Déploiement rapide de démos ML
- Interface : texte, image, audio, vidéo, dataframe
- Hosting gratuit sur HF Spaces
- Gradio Blocks : interfaces complexes, multiples entrées/sorties
- Queue, theming, authentification

---

## 7. Catégories et Mots-Clés

### Catégories
| Catégorie | Plateformes |
|-----------|-------------|
| Veille Scientifique | Semantic Scholar, OpenAlex, arXiv, PapersWithCode |
| Modèles & Datasets | Hugging Face Hub, Kaggle Datasets |
| Compétitions | Kaggle, DrivenData, EvalAI |
| Observabilité | W&B, MLflow, LangFuse, Arize, Zeno |
| Déploiement | Gradio, HF Spaces, TGI, vLLM |
| Gestion de Projet | DVC, MLflow Projects, Kubeflow |

### Mots-Clés Essentiels
- `sota`, `state-of-the-art`, `benchmark`, `leaderboard`
- `pre-trained`, `fine-tuning`, `LoRA`, `quantization`
- `experiment tracking`, `hyperparameter optimization`
- `model registry`, `artifact store`, `pipeline`
- `embedding`, `semantic search`, `vector database`
- `LLM observability`, `guardrails`, `evaluation`
- `open-source`, `reproducible`, `replicability`

---

## 8. Workflow de Veille Quotidien

1. **HF Papers Daily** → scan trending → repository clé
2. **PapersWithCode** → vérifier SOTA sur les tâches pertinentes
3. **Semantic Scholar** → citation graph, recommandations
4. **Kaggle** → nouvelles compétitions, kernels gagnants
5. **GitHub Trending** → repos IA émergents
6. **ArXiv Sanity/Librarian** → nouveaux papiers filtrés
7. **W&B Reports** → expériences partagées par la communauté

### Script de Veille Automatisée
```python
# Exemple de workflow Python
from huggingface_hub import HfApi
from paperswithcode import PapersWithCodeClient
import requests

api = HfApi()
# Récupérer les trending papers HF
papers = api.list_papers(sort="trending", limit=10)

# Rechercher SOTA sur PapersWithCode
client = PapersWithCodeClient()
sota = client.paper_list(tasks="text-classification", items_per_page=5)
```

---

## Ressources

- [Hugging Face Docs](https://huggingface.co/docs)
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [OpenAlex](https://docs.openalex.org/)
- [PapersWithCode API](https://paperswithcode.com/api/v1/docs/)
- [Kaggle API](https://www.kaggle.com/docs/api)
- [W&B Docs](https://docs.wandb.ai/)
- [LangFuse](https://langfuse.com/docs)