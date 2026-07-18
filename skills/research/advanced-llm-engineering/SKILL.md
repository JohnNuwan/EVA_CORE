---
name: advanced-llm-engineering
description: "Compétence niveau expert en ingénierie avancée des grands modèles de langage. Couvre l'architecture Transformer profonde, l'inférence optimisée, KV cache, speculative decoding, quantization (GPTQ, AWQ, GGUF), MoE, distillation, alignment (RLHF, DPO, GRPO), RAG avancé, fine-tuning (LoRA, QLoRA, DoRA), évaluation, safety, watermarking, et déploiement."
---

# Ingénierie Avancée des Grands Modèles de Langage (LLM)

## Présentation

Compétence niveau expert en ingénierie avancée des LLMs. Couvre l'architecture profonde des Transformers, l'optimisation d'inférence, la quantification, le fine-tuning, l'alignement, le RAG, la sécurité, et le déploiement en production.

---

## 1. Architecture Profonde

### Détails du Transformer

- **Architecture** : blocs encoder/décoder, attention multi-tête, FFN (Feed-Forward Network)
- **Attention Variants** :
  - **RoPE** (Rotary Position Embedding) : encodage de position relatif rotatif
  - **ALiBi** (Attention with Linear Biases) : biais linéaire pour les positions distantes
  - **GQA** (Grouped Query Attention) : compromis entre MHA et MQA
  - **MQA** (Multi-Query Attention) : clés/valeurs partagées entre têtes
  - **MLA** (Multi-head Latent Attention) : projection latente pour KV cache réduit
- **DeepSeekMoE** : architecture MoE (Mixture of Experts) fine-grained avec partage d'experts
  - **Sparse MoE** : activation sélective d'experts par token
  - **Expert Routing** : routage top-k avec load balancing loss
  - **Load Balancing** : régularisation pour distribution uniforme entre experts

### Normalisation et Activations

- **RMSNorm / LayerNorm** : stabilisation de l'entraînement
- **GLU Variants** : SwiGLU, GeGLU — activations gated pour FFN plus expressives

---

## 2. Inférence Optimisée

### KV Cache Management

- **KV Cache** : mise en cache des clés/valeurs pour décodage auto-régressif
- **PagedAttention (vLLM)** : gestion mémoire paginée du KV cache
- **Continuous Batching** : traitement par lots dynamique pendant l'inférence
- **Prefix Caching** : réutilisation du cache pour prompts partagés

### Décodage Accéléré

- **Speculative Decoding** : génération spéculative avec modèle draft
  - **Medusa** : têtes parallèles de prédiction de tokens futurs
  - **Self-Speculative** : auto-spéculation avec couches précoces
- **Tensor Parallelism** : parallélisation entre GPU pour les opérations linéaires
- **Pipeline Parallelism** : découpage des couches entre GPU

---

## 3. Quantification et Compression

### Méthodes de Quantification

- **GPTQ** (Frantar et al., 2023) : quantification post-entraînement basée sur la Hessienne — 4-bit et 3-bit
- **AWQ** (Lin et al., 2024) : Activation-aware Weight Quantization — préserve les canaux importants
- **GGUF / GGML** : format de quantification pour CPU/GPU mixte (llama.cpp)
- **bitsandbytes** : NF4 (NormalFloat4), FP4 pour fine-tuning et inférence

### Méthodes Avancées

- **AQLM** (Additive Quantization of Language Models) : quantification additive extreme (2-bit)
- **QuIP** (Quantization with Incoherence Processing) : transformation de Hadamard + quantification
- **FP8 Training/Inference** : format 8-bit pour entraînement et inférence
- **Calibration Datasets** : sélection de données pour calibration optimale

---

## 4. Fine-tuning Avancé

### Méthodes PEFT (Parameter-Efficient Fine-Tuning)

- **LoRA** (Low-Rank Adaptation) : matrices de rang faible injectées dans les couches d'attention
- **QLoRA** : LoRA + quantification 4-bit NF4 avec double quantification
- **DoRA** (Weight-Decomposed Low-Rank Adaptation) : décomposition magnitude/direction de LoRA
- **PiSSA** : meilleure initialisation de LoRA via décomposition SVD des poids pré-entraînés
- **LoRA-XS** : adaptation de rang extrêmement faible
- **rsLoRA** : scale factor dépendant du rang pour stabilité
- **VeRA** : vectors aléatoires partagés avec biais appris
- **Adapter Fusion** : combinaison de multiples adapters LoRA

### Prompt Engineering Appris

- **Prompt Tuning** : tokens virtuels continus appris
- **Soft Prompt** : embeddings optimisés par gradient
- **P-tuning v2** : prompt tuning profond optimisé pour tous les niveaux

---

## 5. Alignment

### RLHF (Reinforcement Learning from Human Feedback)

- **PPO** (Proximal Policy Optimization) : optimisation proximale avec récompense apprise
- **Reward Model Training** : entraînement d'un modèle de récompense sur préférences humaines
- **Process Reward Model** : récompense par étape (process-level vs outcome-level)

### Méthodes Sans RL

- **DPO** (Direct Preference Optimization) : optimisation directe sur préférences sans PPO
- **KTO** (Kahneman-Tversky Optimization) : optimisation basée sur la théorie des perspectives
- **IPO** (Identity Preference Optimization) : préférence optimale basée sur l'identité
- **ORPO** : odds ratio préférence optimization — combine SFT et alignment
- **GRPO** (Group Relative Policy Optimization) : DeepSeek — optimisation par groupe sans modèle de critique
- **RLOO** : REINFORCE Leave-One-Out — variance réduite

### Autres Approches

- **Constitutional AI** : auto-formation via principes constitutionnels
- **Self-Play SPIN** : auto-jeu — le modèle apprend contre ses propres générations

---

## 6. RAG et Agents

### Architectures RAG

- **RAG Fusion** : combinaison de multiples sources retrievées
- **Corrective RAG** : correction et raffinement des documents retrievés
- **Self-RAG** : réflexion du modèle sur ses propres retrievals
- **Agentic RAG** : agent décidant quand et quoi retriever
- **Multi-Hop RAG** : retrieval en plusieurs étapes avec raisonnement
- **Graph RAG** : retrieval sur graphe de connaissances
- **Memory-Augmented LLM** : mémoire explicite pour contexte long

### Capacités Agent

- **Tool-Use** : appel d'outils externes (APIs, calculatrices, bases de données)
- **Function Calling** : invocation structurée de fonctions
- **Planning & Execution** : décomposition de tâches et exécution séquentielle

---

## 7. Sécurité et Watermarking

### Défense contre les Injections

- **Prompt Injection Defense** : filtrage, instruction hierarchy, perplexity filtering
- **Guardrails** : systèmes de garde-fous paramétriques et non-paramétriques
- **Red Teaming** : test d'attaque systématique pour découvrir les vulnérabilités

### Watermarking

- **KGW Watermark** (Kirchenbauer et al., 2023) : watermarking calibré basé sur la partition du vocabulaire
- **Power-Calibrated Watermarking** (2026, ICML) : watermarking calibré en puissance pour haute détectabilité
- Détection statistique avec faux positifs contrôlés

---

## 8. Références et Articles Clés

### Articles Fondamentaux

- **DeepSeek-V2/V3** : architecture MoE et MLA
- **Gemma 4 Report** (2026) : rapport technique du modèle Gemma 4
- **DepthWeave-KV** : entrelacement profond du KV cache
- **FreqDepthKV** : KV cache adapté à la fréquence et profondeur
- **TrainingAgents** : formation d'agents LLM autonomes
- **Power-Calibrated Watermarking** (ICML 2026)

### Catégories

- `cs.CL` — Computation and Language
- `cs.LG` — Machine Learning
- `cs.AI` — Artificial Intelligence
- `cs.CR` — Cryptography and Security