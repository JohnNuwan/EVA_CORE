---
name: data-management-databases
description: Compétence en recherche en gestion des données et bases de données suivie sur arXiv sous cs.DB. Couvre les bases de données relationnelles et NoSQL, le traitement de requêtes, l'optimisation, les entrepôts de données, les data lakes, l'intégration de données, la qualité des données, les graphes de connaissances, et l'IA pour les bases de données.
---

# Gestion des Données et Bases de Données — arXiv

## Présentation
Ce skill couvre la recherche en systèmes de gestion de données, bases de données et entrepôts de données via arXiv (cs.DB et domaines connexes). Il englobe les architectures classiques (SQL, NoSQL), les évolutions modernes (data lakes, lakehouse), et la convergence avec l'IA (NL2SQL, agents SQL autonomes, KG embeddings).

## Bases de Données et Moteurs de Requêtes
- **SQL et optimisation de requêtes** — plans d'exécution, réécriture, optimisation coût-base.
- **Indexation** — B-trees, hash indexes, indexation multi-dimensionnelle.
- **Exécution parallèle** — parallélisme intra-et inter-requêtes, distribution.
- **Bases de données en mémoire** — HyPer, Hyper, VectorWise.

## NoSQL et Bases de Données Distribuées
- **MongoDB** — document stores, sharding, aggregation pipeline.
- **Cassandra et DynamoDB** — bases orientées colonnes, cohérence éventuelle, anneaux.
- **Graph Databases** — Neo4j, Property Graphs, requêtes de parcours.
- **NewSQL** — Spanner, CockroachDB, TiDB — SQL distribué avec ACID.

## Data Lakes et Entrepôts de Données
- **Architecture lakehouse** — Delta Lake, Apache Iceberg, Apache Hudi.
- **Pipelines ETL/ELT** — ingestion, transformation, chargement.
- **Gouvernance des lacs de données** — catalogues, traçabilité des données.
- **Traitement par lots et streaming** — Apache Spark, Flink, Kafka.

## IA pour les Bases de Données
- **NL2SQL** — traduction de langage naturel en SQL (Spider, BIRD, WikiSQL).
- **Spider 2.0-AIFunc** — benchmark avec fonctions définies par l'utilisateur, exécution SQL multi-étape.
- **Agents SQL autonomes** — agents LLM pour l'interaction avec bases de données.
- **Optimisation auto-gérée** — knobs d'indexation et de configuration automatiques via ML.
- **Query synthesis et debugging** — réparation automatique de requêtes.

## Graphes de Connaissances et Ontologies
- **KG Embeddings** — TransE, RotatE, ComplEx, ConvE.
- **RDF et SPARQL** — web sémantique, raisonnement.
- **Construction de KGs** — extraction d'entités et relations, alignement.
- **Graphes de connaissances hybrides** — TACTIC-KG : KG + tactiques de preuve.

## Qualité des Données et Gouvernance
- **Nettoyage des données** — détection et réparation d'erreurs, imputation.
- **Déduplication** — entity resolution, blocking, matching probabiliste.
- **Traçabilité (data lineage)** — provenance, versionnement.
- **Gouvernance responsable** — privacy, fairness, auditabilité.

## Catégories arXiv
- `cs.DB` — bases de données, systèmes de gestion de données.
- `cs.IR` — recherche d'information, indexing.
- `cs.AI` — agents SQL, NL2SQL, KGs.
- `cs.SE` — architecture logicielle, pipelines.

## Articles Notables
- "Spider 2.0-AIFunc: A Benchmark for Evaluating AI Functions in Database Agents" (arXiv)
- "TACTIC-KG: A Knowledge Graph of Proof Tactics" (arXiv)
- "Large Language Models meet Databases: NL2SQL and Beyond" (Survey)
- "Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics" (CIDR 2021)
