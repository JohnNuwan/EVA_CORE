---
name: nlp-llm-research
description: >-
  Compétence professionnelle en recherche en traitement du langage naturel
  et grands modèles de langage suivie sur arXiv sous cs.CL, cs.LG et cs.AI.
  Couvre les architectures LLM, l'entraînement, le fine-tuning, l'inférence,
  l'évaluation, le raisonnement, la génération augmentée par récupération,
  le TALN multilingue et la théorie des LLM.
category: research
---

# Compétence en Recherche en TALN et LLM (cs.CL, cs.LG, cs.AI)

## Présentation

La recherche en TALN et LLM s'étend sur cs.CL (Langage et Calcul), cs.LG (Apprentissage Automatique) et cs.AI (Intelligence Artificielle) avec un volume considérable. Cette compétence fournit une structure pour naviguer dans la recherche sur les LLM de l'architecture au déploiement.

## Domaines de Recherche Principaux

### 1. Architectures des LLM
- **Architectures Transformer** : Mécanismes d'attention, multi-tête, causale
- **Attention efficace** : Attention linéaire, flash attention, fenêtre glissante
- **Mixture of Experts** : Couches MoE, routage d'experts, équilibrage de charge
- **Optimisation du cache KV** : Compression, méthodes adaptatives aux tokens, partage de profondeur
- **Modèles à long contexte** : Extensions RoPE, ALiBi, interpolation de position
- **Modèles à espace d'états** : Mamba, Mamba-2, alternatives récurrentes aux transformers
- **Factorisation résiduelle inter-couches** : Compression de cache KV via DepthWeave-KV

### 2. Entraînement et Fine-Tuning
**Densité arXiv** : Très élevée
- **Objectifs de pré-entraînement** : Prédiction du prochain token, MLM masqué, UL2
- **Lois d'échelle** : Entraînement économiquement optimal, lois de Chinchilla
- **Fine-tuning supervisé (SFT)** : Ajustement par instructions, alignement
- **RLHF** : Apprentissage par renforcement à partir de feedback humain, PPO
- **DPO** : Optimisation directe des préférences, KTO, SPIN
- **GRPO** : Optimisation de politique relative par groupes
- **LoRA et adaptateurs** : Fine-tuning paramètre-efficace, QLoRA, DoRA
- **Pré-entraînement continu** : Adaptation de domaine, injection de connaissances

### 3. Inférence et Déploiement
- **Décodage spéculatif** : Proposer-vérifier, Medusa, auto-spéculatif
- **Gestion du cache KV** : Mise en cache en ligne, partage de préfixe
- **Quantification** : GPTQ, AWQ, NF4, inférence FP8
- **Élagage (pruning)** : Élagage par magnitude, SparseGPT, Wanda
- **Distillation** : Distillation de connaissances, correspondance de logits
- **Mise en lots** : Batching continu, batching dynamique

### 4. Raisonnement et Chaîne de Pensée
- **Chaîne de pensée (CoT)** : CoT zero-shot, few-shot, auto-consistance
- **Arbre de pensée (ToT)** : Recherche BFS/DFS, élagage
- **Raisonnement assisté par programme** : Code comme raisonnement, PAL
- **Auto-amélioration** : STaR, ReST, itération experte, raisonnement constitutionnel
- **Modèles de récompense de processus** : Supervision par étape

### 5. Génération Augmentée par Récupération (RAG)
- **Architecture RAG** : Lire après récupération, récupération itérative
- **Récupération dense** : Modèles d'embedding (e5, bge, instructor)
- **Recherche hybride** : Dense + sparse, fusion de rangs réciproques
- **RAG agentique** : Auto-interrogation, routage, utilisation d'outils
- **Compression de contexte** : Reclassement, résumé, filtrage

### 6. Sécurité et Alignement
- **Alignement** : IA constitutionnelle, RLHF, DPO, KTO
- **Red-teaming** : Tests adversaires, détection de jailbreak
- **Réduction de toxicité** : Filtrage de contenu, classifyeurs de sécurité
- **Hallucination** : Ancrage factuel, génération de citations, calibration
- **Filigrane** : Filigrane statistique pour la détection de sortie LLM, méthodes calibrées (ICML 2026)

### 7. Évaluation et Références
- **Connaissances générales** : MMLU, MMLU-Pro, GPQA, ARC
- **Raisonnement** : GSM8K, MATH, BIG-Bench, HumanEval
- **Capacités agentiques** : AgentBench, SWE-bench, WebArena, GAIA
- **LLM comme juge** : Évaluation par modèle, comparaison par paires
- **Sécurité** : TruthfulQA, critères HHH

### 8. TALN Multilingue et Code
- **Modèles multilingues** : mBERT, XLM-R, mT5, BLOOM, Aya
- **Transfert cross-lingue** : Transfert zero-shot, alignement cross-lingue
- **LLMs pour le code** : CodeLlama, StarCoder, DeepSeek-Coder
- **Synthèse de programmes** : Text-to-SQL, génération de code, agents de codage autonomes

### 9. LLMs Multimodaux
- **Modèles vision-langage** : CLIP, LLaVA, GPT-4V, Gemini, Florence
- **VLA (Vision-Langage-Action)** : Agents robotiques combinant vision et langage
- **Modèles du monde** : Modèles incarnés 4D pour la manipulation robotique

## Articles Notables Récents (Mi-2026)
1. **DepthWeave-KV: Token-Adaptive Cross-Layer Residual Factorization for KV Cache Compression** — cs.AI
2. **FreqDepthKV: Frequency-Guided Depth Sharing for Robust KV Cache Compression** — cs.AI
3. **Spider 2.0-AIFunc: Text-to-SQL vers Flux SQL Natifs IA** — cs.AI/cs.CL
4. **Beyond Heuristic Tuning: Power-Calibrated LLM Watermarking** — stat.ML (ICML 2026)
5. **Rethinking Indic AI from a Lens of Cultural Heritage Preservation** — cs.AI/cs.CL

## Comment Effectuer la Veille
- **Principal** : `/list/cs.CL/recent`
- **Cross-list** : `/list/cs.LG/recent` (architecture et entraînement des LLM)
- **Agents et langage** : `/list/cs.AI/recent` (agents LLM, utilisation d'outils)
- **Mots-clés** : "LLM", "transformer", "attention", "fine-tuning", "RLHF", "RAG", "reasoning"