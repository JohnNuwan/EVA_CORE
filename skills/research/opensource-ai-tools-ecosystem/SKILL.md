---
name: opensource-ai-tools-ecosystem
description: "Compétence niveau ingénieur/docteur sur l'écosystème des outils IA open-source. Couvre GitHub trending (repos clés), frameworks ML/DL, outils d'agents, frameworks LLM, toolkits MCP, RAG frameworks, evaluation harnesses, vector databases, inference engines, et orchestration."
category: research
tags: [opensource, github-trending, frameworks-ia, agents-llm, mlops, inference, vectordb]
---

# Écosystème des Outils IA Open-Source — Référence Ingénieur/Docteur

## Présentation

Ce skill couvre l'ensemble des outils open-source essentiels pour le développement, le déploiement et l'orchestration de systèmes d'IA. Il permet de naviguer l'écosystème en évolution rapide, d'identifier les frameworks dominants, et de choisir les outils adaptés à chaque couche de la stack technique.

---

## 1. GitHub Trending — Repos Clés (Période Récente)

### Stabilité et Sécurité
- **usestrix/strix** — AI Penetration Testing — ~38k stars/semaine
- Analyse de vulnérabilités, exploitation automatisée, rapports

### Finance & Investissement
- **xbtlin/ai-berkshire** — Value Investing AI — ~11k stars
- Analyse fondamentale, screening, rapports financiers
- **daily_stock_analysis** — Analyse boursière quotidienne automatisée

### Speech & Audio
- **huggingface/speech-to-speech** — STT + TTS unifié — ~5.6k stars
- Pipeline complet voix vers voix

### OCR & Document Processing
- **allenai/olmocr** — OCR multimodal — ~18k stars
- Layout understanding, table extraction, formula recognition

### Browser Automation
- **browser-use/video-use** — Navigation web automatisée — ~15k stars
- Agents autonomes, scraping, workflows

### Skills & Tools
- **alirezarezvani/claude-skills** — 345 skills, ~21k stars
- Bibliothèque de compétences pour Claude Code

### Cartographie & NLP
- **Robbyant/lingbot-map** — NLP cartographique — ~10k stars
- Extraction de lieux, géocodage, cartes sémantiques

---

## 2. Frameworks ML/DL

### PyTorch
- Framework de recherche dominant (2024-2026)
- TorchScript, TorchServe, TorchRec, TorchVision
- `torch.compile` : JIT compilation, GPU kernel fusion
- Distributed : DDP, FSDP, DeepSpeed, Tensor Parallel
- PyTorch/XLA : TPU support
- PyTorch Lightning : boilerplate reduction

### JAX
- Accélération numérique avec XLA compilation
- `jax.jit`, `jax.vmap`, `jax.pmap` : auto-parallélisation
- `jax.grad` : différentiation automatique
- Deep Learning : Flax, Haiku, Equinox, Keras 3
- Recherche : Transformer, diffusion, RL (Brax)

### TensorFlow / Keras
- TF 2.x : eager execution, Keras intégré
- TF Lite : déploiement mobile/edge
- TF Serving : model serving en production
- TFX : pipelines ML complets
- Keras 3 : multi-backend (JAX, TF, PyTorch)

### Bibliothèques Spécialisées
- **Transformers** (HF) : 500k+ modèles, 100+ architectures
- **Diffusers** : diffusion pipelines (txt2img, img2img, inpainting)
- **timm** (PyTorch Image Models) : 300+ architectures CV
- **OpenCV** : vision par ordinateur, tracking, calibration
- **TorchGeo** : deep learning géospatial

---

## 3. Frameworks Agents

### LangChain
- Chaînes de LLM, outils, mémoire, agents
- LCEL (LangChain Expression Language) : pipelines déclaratifs
- LangSmith : observabilité, tracing, evaluation
- LangGraph : graphes d'états pour agents complexes
- Intégrations : 700+ providers

### CrewAI
- Multi-agent orchestration hiérarchique
- Rôles : Agent → Task → Crew → Process
- Outils, mémoire, délégation
- Support LLM : OpenAI, Anthropic, Ollama, HF

### AutoGen (Microsoft)
- Multi-agent conversations
- Assistant Agent, User Proxy, Group Chat
- Code execution, human-in-the-loop
- AutoGen Studio : UI de debug

### smolagents (HF)
- Agents légers, code-first
- Outils, memory, planning
- Intégration Transformers
- Idéal pour prototypage rapide

### OpenDevin
- Agent de développement logiciel autonome — ~79k stars
- Bash, code, browse, filesystem
- Sandbox sécurisé, web UI

### Autres
- **Agno** (ex-Phidata) : agents multi-modal
- **Semantic Kernel** (Microsoft) : AI orchestration
- **DSPy** : compilation de programmes LLM
- **CrewAI Flows** : workflows structurés

---

## 4. Toolkits MCP (Model Context Protocol)

### Anthropic MCP
- Protocole standardisé outil → LLM
- Serveurs MCP : filesystem, GitHub, Slack, DB, web
- Security : sandbox, permissions, scopes
- Code-first : Python, TypeScript SDK

### MCP Clients
- Claude Desktop, Claude Code
- Continue.dev, Cursor IDE
- Intégration VS Code, JetBrains

### MCP Servers Populaires
- **Everything** : démo/tests
- **Filesystem** : read/write/search
- **GitHub** : issues, PRs, commits, repos
- **PostgreSQL/SQLite** : query DB
- **Playwright** : browser automation
- **Brave Search** : web search
- **Memory** : persistance contextuelle

---

## 5. RAG Frameworks

### LlamaIndex
- Indexation de données : documents, DB, API
- Query engine, chat engine, agent
- Routers, retrievers, rerankers, postprocessors
- LlamaParse : parsing PDF avancé
- 100+ integrations data sources

### Haystack (deepset)
- Pipelines RAG : indexing → retrieval → generation
- Nodes : retrievers, readers, generators, rankers
- DocumentStore : Elasticsearch, OpenSearch, Qdrant, Weaviate
- OpenAPI, REST API, UI

### LangChain RAG
- Document loaders, text splitters, vector stores
- RetrievalQA, ConversationalRetrievalChain
- ParentDocumentRetriever, SelfQueryRetriever
- Ensemble retriever, multi-query retriever

### Autres
- **RAGatouille** : ColBERT v2 late interaction
- **FlashRAG** : bibliothèque de recherche RAG
- **Canopy** (Pinecone) : RAG complet
- **Qdrant RAG** : retrieval intégré vector DB

---

## 6. Evaluation Harnesses

### LM Evaluation Harness (EleutherAI)
- 200+ benchmarks standardisés
- MMLU, GSM8K, HumanEval, HellaSwag, ARC, TruthfulQA
- Format : few-shot, zero-shot, chain-of-thought
- Résultats reproductibles, comparaison de modèles

### LangFuse Evaluation
- LLM-as-judge, regex, exact match, human eval
- Dataset de test, golden dataset
- Tracing, scoring, feedback
- Monitoring production

### DeepEval (Confident AI)
- 15+ métriques : faithfulness, relevancy, hallucination, toxicity
- Intégration CI/CD
- Tests unitaires, intégration, end-to-end
- LLM-as-judge, custom metrics

### Autres
- **RAGAS** : évaluation de pipelines RAG
- **TruLens** : feedback functions, ground truth
- **AlpacaEval** : LLM-as-judge, length-controlled
- **MT Bench** : multi-turn conversation
- **LMSYS Chatbot Arena** : classement Elo

---

## 7. Vector Databases

### Chroma
- Embedding + retrieval, léger, local
- Python-first, API REST optionnelle
- DuckDB backend, persistance sur disque
- Idéal pour prototypage et applications embarquées

### Pinecone (serverless)
- Vector DB cloud-native, scale automatique
- Indexation, search, filtering
- Namespaces, metadata, hybrid search
- Sparse-dense, pod/serverless

### Weaviate
- GraphQL native, vector + keyword search
- Modules : generative search, Q&A, NER
- Multi-tenancy, replication, hybrid
- Auto-schema, CRUD vectoriel

### Qdrant
- Rust-based, performance élevée
- Filtering avancé, payload indexing
- Quantization, on-disk, multi-node
- Recommandation, grouping, discovery

### Milvus (Zilliz)
- Cloud-native, échelle peta-scale
- GPU acceleration, indexation IVF/HNSW/SCANN
- Attu UI, PyMilvus SDK
- Knowhere : moteur de similarité, modular

---

## 8. Moteurs d'Inférence

### vLLM
- LLM serving haute performance
- PagedAttention : gestion mémoire efficace
- Continuous batching, prefix caching, speculative decoding
- OpenAI-compatible API
- Quantization : GPTQ, AWQ, FP8, INT4

### Text Generation Inference (TGI, HF)
- Déploiement optimisé Transformers
- Message streaming, batching
- Quantization : bitsandbytes, GPTQ, AWQ, Marlin
- Safety : content filter, rate limiting

### llama.cpp
- Inférence LLM sur CPU/GPU, quantifié GGUF
- 4-bit, 5-bit, 6-bit, 8-bit quantization
- Metal, CUDA, Vulkan, SYCL
- Serveur OpenAI-compatible

### Ollama
- Gestion de modèles LLM locaux
- Modelfile : personnalisation, template
- API REST, bibliothèque Python/JS
- 100k+ modèles sur Ollama Hub

### TensorRT-LLM (NVIDIA)
- Optimisation GPU NVIDIA, TensorRT compilation
- In-flight batching, multi-GPU, FP8/INT4/INT8
- Plugins : attention, RoPE, GQA
- Support : Llama, Mistral, Falcon, GPT, BLOOM

### Autres
- **SGLang** : structured generation, RadixAttention
- **MLC-LLM** : déploiement everywhere (web, mobile, edge)
- **llamafile** : single-file LLM executable
- **LocalAI** : OpenAI API drop-in local

---

## 9. Catégories et Tableau Récapitulatif

| Couche | Outils |
|--------|--------|
| Frameworks DL | PyTorch, JAX, TensorFlow, Keras 3 |
| LLM Inference | vLLM, TGI, llama.cpp, Ollama, TensorRT-LLM |
| Agents | LangChain, CrewAI, AutoGen, OpenDevin, smolagents |
| RAG | LlamaIndex, Haystack, LangChain, Qdrant |
| Vector DB | Chroma, Pinecone, Weaviate, Qdrant, Milvus |
| Evaluation | LM Eval Harness, LangFuse, DeepEval, RAGAS |
| MCP | Anthropic MCP, Continue, Claude Code |
| DevOps ML | Kubeflow, MLflow, DVC, W&B |

---

## 10. Workflow de Sélection d'Outils

1. **Définir le besoin** : RAG, Agent, Fine-tuning, Inférence, Eval
2. **Prototypage** : Chroma + LangChain/LlamaIndex + Ollama
3. **Production** : vLLM (LLM) + Qdrant/Milvus (vector DB) + LangFuse (eval)
4. **Agents** : CrewAI (multi-agent) ou OpenDevin (code autonome)
5. **CI/CD ML** : MLflow + DVC + GitHub Actions
6. **Monitoring** : LangFuse + Arize + W&B

### Checklist de Choix
- Open-source ? Licence ? Communauté ?
- Performance : throughput, latency, scaling
- Stack technique : Python, Rust, Go, C++
- Maintenance : commits récents, issues, PRs
- Intégration : API, SDK, compatibilité

---

## Ressources

- [GitHub Trending](https://github.com/trending)
- [PyTorch Docs](https://pytorch.org/docs)
- [LangChain Docs](https://python.langchain.com/docs)
- [vLLM Docs](https://docs.vllm.ai)
- [LM Eval Harness](https://github.com/EleutherAI/lm-evaluation-harness)
- [MCP Specification](https://modelcontextprotocol.io)
- [Ollama Library](https://ollama.com/library)