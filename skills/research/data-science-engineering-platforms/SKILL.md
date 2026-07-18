---
name: data-science-engineering-platforms
description: "Compétence niveau expert en data science et data engineering platforms. Couvre les pipelines de données, les data warehouses (Snowflake, BigQuery, Redshift, Databricks), les data lakes, les streaming (Kafka, Flink, Spark Streaming), les orchestrators (Airflow, Prefect, Dagster), les bases de données vectorielles, les feature stores, les model registries, et les MLOps platforms."
keywords: [data engineering, data science, MLOps, Snowflake, Kafka, Airflow, streaming, data warehouse, vector databases]
categories: [cs.DB, cs.DC, cs.LG, cs.IR, cs.SE, cs.AI]
---

# Compétence Data Science et Data Engineering

## Présentation

Cette compétence couvre les plateformes et outils de data science et data engineering, des data warehouses aux bases vectorielles en passant par le streaming, l'orchestration et les pipelines MLOps.

---

## Data Warehousing

- **Snowflake** : Concept cloud agnostic (compute/storage séparés), data sharing, time travel
- **BigQuery** : Serverless, columnar, BigQuery ML, Omni, BI Engine
- **Redshift** : Columnar, distribution keys, sort keys, Spectrum, AQUA
- **Databricks Lakehouse** : Lakehouse architecture (Delta Lake, Unity Catalog)
- **Synapse / ClickHouse** : Analytics Azure / OLAP columnar haute performance
- **Modern Data Stack** : Architecture data moderne (dbt, Airbyte, Fivetran, Snowflake)
- **dbt (Data Build Tool)** : Transformations SQL versionnées, tests, documentation
- **Data Modeling** : Star/snowflake, Kimball (dimensional), Inmon (normalized), Data Vault 2.0

## Streaming et Real-time

- **Apache Kafka** : Topics, partitions, consumer groups, offsets, brokers, replication
- **Kafka Streams / ksqlDB** : Stream processing directement avec Kafka
- **Schema Registry** : Avro/Protobuf/JSON Schema pour sérialisation
- **Confluent** : Platform Kafka enterprise (Control Center, connectors)
- **Apache Flink** : Event-time, watermarks, stateful processing, exactly-once
- **Flink SQL** : Requêtes SQL en continu sur streams
- **Spark Structured Streaming** : Micro-batches et continuous processing
- **Kafka Connect** : Sources/sinks connecteurs (Debezium CDC, JDBC, S3)
- **Debezium CDC** : Change Data Capture (MySQL, PostgreSQL, MongoDB)
- **Apache Pulsar / Redpanda** : Alternatives Kafka (geo-replication, Kafka API compatible)

## Data Pipelines

- **Apache Airflow** : DAGs, Sensors, operators (Python, Bash, SQL), XCom, pools, SLAs
- **Prefect 2/3** : Events, automations, deployments, work pools (push/pull)
- **Dagster** : Software-defined assets, ops, sensors, schedules, asset lineage
- **Meltano** : Plateforme ELT open source, Singer taps/targets
- **Fivetran** : ELT managé, connectors pré-bâtis
- **Airbyte** : ELT open source, connectors, normalization

## Data Quality et Observabilité

- **Great Expectations** : Expectations, suites, data docs, store backends
- **Soda** : SodaCL, scans, checks automation, OSS scanner
- **dbt Tests** : Tests de fraîcheur, d'unicité, de nullité, personnalisés
- **Data Freshness** : Fraîcheur des données, timeliness
- **Volume / Schema / Distribution** : Validation de volume, schéma, distribution
- **Lineage (OpenLineage / Marquez)** : Traçabilité des données (column-level lineage)
- **Atlan / Monte Carlo / Sifflet** : Plateformes de catalog + observabilité

## ML Platforms et MLOps

- **MLflow** : Tracking, registry, projects, models (serve, deploy)
- **Kubeflow** : Pipelines ML, Katib (hyperparameter tuning), KFServing
- **Weights & Biases** : Experiment tracking, sweeps, model registry, reports
- **Neptune / Comet** : Plateformes d'experiment tracking alternatives
- **Feast / Tecton** : Feature stores (online + offline serving)
- **ML Metadata** : Artifacts, metadata tracking, model versioning
- **Deployment Strategies** : Canary, shadow, champion-challenger, A/B
- **Inference Pipelines** : Pre/post-processing, batch inference, real-time endpoints

## Vector Databases et Search

- **Pinecone** : Vector database managée, namespaces, metadata filtering
- **Chroma** : Vector DB open source intégrée
- **Weaviate** : Vector + object storage, modules IA intégrés
- **Qdrant** : Vector DB haute performance, payload filtering
- **Milvus** : Vector DB cloud native, GPU support
- **pgvector** : Extension vectorielle pour PostgreSQL
- **FAISS** : Bibliothèque de recherche ANN (Meta)
- **HNSW** : Algorithme Hierarchical Navigable Small World
- **ANN / MIPS** : Approximate Nearest Neighbor, Maximum Inner Product Search
- **Hybrid Search** : Dense + sparse retrieval (BM25 + embeddings)
- **Embedding Generation** : Sentence Transformers, OpenAI, Cohere embeddings
- **RAG Retrieval** : Retrieval-Augmented Generation pipelines