---
name: recommendation-systems
description: "Compétence niveau expert en systèmes de recommandation. Couvre collaborative filtering, matrix factorization, SVD, ALS, neural CF, NCF, wide & deep, DLRM, two-tower, sequence models, GRU4Rec, SASRec, BERT4Rec, Transformers4Rec, session-based, graph-based recommender, PinSage, lightGCN, multi-task, multi-staged ranking, cold-start, exploration-exploitation, fairness, evaluate offline/online, A/B testing, et industrial systems (YouTube, Netflix, Spotify, Amazon)."
keywords: [recommender systems, collaborative filtering, matrix factorization, neural CF, SASRec, LightGCN, ranking]
categories: [cs.IR, cs.LG, cs.AI, stat.ML, cs.CY]
---

# Compétence Systèmes de Recommandation

## Présentation

Cette compétence couvre l'ensemble des systèmes de recommandation, du filtrage collaboratif classique aux architectures industrielles modernes basées sur les Transformers et les GNNs.

---

## Méthodes Fondamentales

- **Collaborative Filtering** : User-user et item-item nearest neighbors
- **Matrix Factorization** : SVD, FunkSVD, SVD++
- **ALS (Alternating Least Squares)** : Moindres carrés alternés (implicite/explicite)
- **timeSVD** : Factorization avec biais temporels
- **Factorization Machines (FM)** : Machines de factorisation (Rendle)
- **FFM (Field-aware FM)** : FM par champs
- **DeepFM** : FM + MLP (wide & deep pour features)
- **xDeepFM** : Explicit feature interaction via Compressed Interaction Network
- **AFM (Attentional FM)** : FM avec mécanisme d'attention
- **NFM (Neural FM)** : FM avec réseau de neurones
- **Neural CF (NCF)** : GMF (Generalized Matrix Factorization), MLP, NeuMF
- **Wide & Deep** : Google Play Store (mémoire + généralisation)
- **DeepCross (DCN)** : Deep & Cross Network (cross layers)
- **DCNv2** : DCN amélioré avec transformations digitales
- **DLRM** : Deep Learning Recommendation Model (Meta)
- **DIN (Deep Interest Network)** : Réseau d'intérêt profond (Alibaba)
- **DIEN (Deep Interest Evolution Network)** : Évolution des intérêts

## Sequence et Session

- **Sequence Models** : Modèles séquentiels prédictifs
- **Session-Based** : Recommandation basée sur la session en cours
- **GRU4Rec** : GRU pour recommandation session-based
- **SR-GNN** : Session-based Recommendation with Graph Neural Networks
- **NISER** : Normalized and Integrated Session-based Recommendation
- **COTREC** : Contrastive Learning for Session-based Recommendation
- **SASRec** : Self-Attentive Sequential Recommendation
- **BERT4Rec** : BERT pour recommandation séquentielle bidirectionnelle
- **Transformers4Rec** : Transformers pour recommandation (NVIDIA)
- **P5 / Recformer** : LLM pour recommandation
- **LLM4Rec** : Utilisation de LLM pour la recommandation
- **Sequential Rules / Markov** : Règles séquentielles et chaînes de Markov

## Graph Recommenders

- **Bipartite Graphs** : Graphes user-item
- **PinSage** : GraphSAGE adapté pour Pinterest (random walks + GCN)
- **LightGCN** : GCN simplifié (ne retient que le propagation)
- **NGCF** : Neural Graph Collaborative Filtering
- **UltraGCN** : Ultra-simplification des GCNs
- **SIMGCL** : Simple Interest Graph Contrastive Learning
- **SGL (Self-supervised Graph Learning)** : Apprentissage contrastif sur graphe
- **NCL (Neighborhood-enriched Contrastive Learning)** : Apprentissage contrastif enrichi
- **Knowledge Graph Enhanced** : KGAT, CKAN, RippleNet, MKR

## Ranking et Multi-stage

- **Recall/Retrieval** : Two-tower (query/user tower + item tower)
- **ANN / HNSW** : Approximate Nearest Neighbor (Hierarchical Navigable Small World)
- **Coarse Ranking / Fine Ranking** : Classement grossier puis fin
- **Re-ranking** : Réordonnancement final
- **Listwise / Pairwise** : Fonctions de perte listwise (LambdaRank) et pairwise
- **LambdaRank / LambdaMART** : RankNet avec gradient listwise
- **NDCG** : Normalized Discounted Cumulative Gain
- **MAP** : Mean Average Precision
- **MRR** : Mean Reciprocal Rank
- **Diversity (MMR / DPP)** : Maximum Marginal Relevance, Determinantal Point Process

## Industrial Systems

- **YouTube Deep Neural Network** : Architecture YouTube (candidate generation + ranking)
- **Netflix** : Recommandation Netflix (collaborative + content)
- **Spotify** : Recommandation Spotify (collaborative + audio features)
- **Amazon Item-to-Item** : Item-to-item collaborative filtering
- **Pinterest PinSage** : Visual discovery + graph
- **TikTok ForYou** : Recommendation multimodale
- **E-Commerce Recs** : Cross-sell, upsell, frequently bought together
- **News Recs** : Recommandation d'articles d'actualité (Microsoft News, Google News)