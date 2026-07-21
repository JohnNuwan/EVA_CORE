---
name: data-pipelines
description: "Data pipelines: conception, patterns ETL/ELT, médaillon architecture (bronze/silver/gold), data contracts, lineage, métriques, tests, reverse ETL."
version: 1.0.0
author: EVA & The Hive
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [data-pipeline, etl, elt, medallion-architecture, data-contract, data-lineage, data-observability, reverse-etl, dataops]
    homepage: https://dataprocess.website/
    related_skills: [airflow-orchestration, apache-spark, apache-kafka, data-warehouse, data-lakes-lakehouse, dbt-analytics, data-quality-testing]
prerequisites:
  commands: [python3, pip]
  pip_packages: [pandas, pyarrow, great_expectations, soda-core, dbt-core, sqlalchemy, psycopg2-binary, openlineage-python]
---

# Compétence Data Pipelines : Conception, Architecture & Patterns

## Vue d'ensemble

Un **data pipeline** est l'épine dorsale de toute organisation data-driven. Cette compétence couvre l'architecture complète :

- **ETL vs ELT** : quand utiliser chaque approche.
- **Architecture Médaillon** : bronze (raw) → silver (clean) → gold (agrégé).
- **Data Contracts** : API de données entre producteurs et consommateurs.
- **Lineage** : traçabilité des données de bout en bout (OpenLineage).
- **Observabilité** : métriques de santé (freshness, volume, schema, quality).
- **Reverse ETL** : synchronisation vers les systèmes opérationnels (CRM, ERP).
- **DataOps** : CI/CD pour les pipelines, tests en staging.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Conçoit une nouvelle architecture de données de bout en bout.
- A besoin de patterns ETL/ELT pour ingérer des sources variées.
- Veut implémenter l'architecture médaillon (bronze/silver/gold).
- Pose des questions sur les data contracts, le lineage ou l'observabilité.
- Demande à industrialiser un pipeline existant avec monitoring et alerting.

---

## 1. Architecture Médaillon (Medallion)

### 1.1 Les Trois Couches

```
┌─────────────────────────────────────────────────────────────┐
│                      GOLD (Agrégé)                          │
│  KPIs, OEE, rapports, tableaux de bord, ML features         │
│  Modèle dimensionnel, star schema, vues matérialisées       │
├─────────────────────────────────────────────────────────────┤
│                     SILVER (Nettoyé)                         │
│  Données dédupliquées, typées, validées, enrichies          │
│  Jointures, normalisation, SCD type 2                       │
├─────────────────────────────────────────────────────────────┤
│                     BRONZE (Raw)                             │
│  Copie exacte des sources, format natif (JSON/Avro/Parquet) │
│  Partitionné par date, immuable, rétention configurable     │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Bronze Layer — Ingestion Raw

```python
# Ingestion depuis Kafka vers bronze (Delta/Parquet)
import pandas as pd
from datetime import datetime

def ingest_to_bronze(source_path: str, bronze_path: str, table: str):
    """Copie raw avec timestamp d'ingestion"""
    df = pd.read_parquet(source_path)
    df['_ingested_at'] = datetime.utcnow()
    df['_source'] = source_path

    # Partition Hive-style
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    output = f"{bronze_path}/{table}/date={date_str}/"
    df.to_parquet(output, partition_cols=["date"], compression="snappy")
    return output

# Caractéristiques bronze :
# - Immuable : jamais modifié après écriture
# - Format natif : JSON, Avro, Parquet
# - Partitionnement temporel (date=YYYY-MM-DD/)
# - Champs système : _ingested_at, _source, _file_name
```

### 1.3 Silver Layer — Nettoyage et Standardisation

```python
def bronze_to_silver(bronze_path: str, silver_path: str):
    """Déduplication, typage, validation"""
    df = pd.read_parquet(bronze_path)

    # Nettoyage
    df = df.drop_duplicates(subset=["machine_id", "timestamp"])
    df = df.dropna(subset=["machine_id", "temperature"])

    # Typage strict
    df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df[df['temperature'].between(-50, 300)]  # Plage réaliste

    # Enrichissement
    df['date'] = df['timestamp'].dt.date
    df['heure'] = df['timestamp'].dt.hour
    df['jour_semaine'] = df['timestamp'].dt.dayofweek

    # SCD Type 1 (écrasement)
    df.to_parquet(
        f"{silver_path}/sensors/date={df['date'].iloc[0]}/",
        partition_cols=["date"],
        compression="snappy"
    )
    return len(df)

# Caractéristiques silver :
# - Données propres, typées, validées
# - Pas de doublons
# - Colonnes standardisées
# - SCD type 1 ou 2 selon l'usage
```

### 1.4 Gold Layer — Agrégations Métier

```python
def silver_to_gold(silver_path: str, gold_path: str):
    """Agrégations métier et KPIs"""
    df = pd.read_parquet(silver_path)

    # Agrégation machine + heure
    df_gold = df.groupby(["machine_id", "date", "heure"]).agg(
        temp_moyenne=("temperature", "mean"),
        temp_max=("temperature", "max"),
        temp_min=("temperature", "min"),
        temp_std=("temperature", "std"),
        nb_mesures=("temperature", "count"),
        nb_alertes=("alerte", lambda x: (x == "CRITIQUE").sum()),
    ).reset_index()

    df_gold.to_parquet(
        f"{gold_path}/kpi_sensors/date={df['date'].iloc[0]}/",
        partition_cols=["date"],
        compression="snappy"
    )
    return df_gold.shape[0]
```

---

## 2. ETL vs ELT : Choix Stratégique

### 2.1 ETL (Extract → Transform → Load)

```
Avantages :
- Données nettoyées avant chargement → base cible légère
- Moins de compute sur la cible
- Idéal pour sources sensibles / PII à anonymiser

Inconvénients :
- Transform engine doit scaler (Spark)
- Perte de granularité si la cible ne stocke pas le raw
- Plus lent à l'ingestion
```

### 2.2 ELT (Extract → Load → Transform)

```
Avantages :
- Ingestion rapide (copie raw)
- Transform engine = la cible (Snowflake, BigQuery, Redshift)
- Toute la flexibilité des transformations post-hoc
- Data scientists accèdent aux données brutes

Inconvénients :
- Compute coûteux sur la cible
- Nécessite un warehouse scalable
- Données raw = stockage volumineux
```

### 2.3 Table de Décision

| Critère | ETL | ELT |
|---------|-----|-----|
| Volume de données | Moyen (< 10 To) | Très grand (> 10 To) |
| Cible | Base traditionnelle | Data Warehouse Cloud |
| Latence requise | Modérée | Faible à modérée |
| Data Science raw | Non | Oui |
| Anonymisation | Avant chargement | Possible après |
| Coût compute | Fixe (cluster Spark) | Variable (warehouse) |

---

## 3. Data Contracts

### 3.1 Définition d'un Data Contract

Un data contract est un accord formel entre un **producteur** et un **consommateur** de données, spécifiant :

- **Schema** : nom des colonnes, types, contraintes.
- **Freshness** : à quelle fréquence les données sont mises à jour.
- **Volume** : nombre de lignes/événements attendus.
- **SLA** : temps d'engagement pour la livraison.
- **Qualité** : règles de validation (null ratio, range, uniqueness).

### 3.2 Exemple de Data Contract (YAML)

```yaml
# contracts/sensor_readings.yaml
dataset: sensors.bronze.sensor_readings
owners:
  producer: team-ingestion
  consumer: team-analytics
version: 1.2.0
schema:
  fields:
    machine_id:
      type: string
      required: true
      description: Identifiant unique de la machine
    temperature:
      type: double
      required: true
      constraints:
        min: -50
        max: 300
    pression:
      type: double
      required: false
      constraints:
        min: 0
        max: 50
    timestamp:
      type: timestamp
      required: true
  primary_key: [machine_id, timestamp]
freshness:
  interval: 15 minutes
  sla: 5 minutes
volume:
  min_rows_per_hour: 1000
  max_rows_per_hour: 100000
quality:
  null_rate_max: 0.01
  duplicate_rate_max: 0.0
  validity_rate_min: 0.98
```

### 3.3 Validation Automatique

```python
import yaml
import pandas as pd

def validate_data_contract(df: pd.DataFrame, contract_path: str) -> dict:
    with open(contract_path) as f:
        contract = yaml.safe_load(f)

    results = {"passed": True, "checks": []}

    # Validation schema
    for field, spec in contract['schema']['fields'].items():
        if spec['required'] and field not in df.columns:
            results['checks'].append(f"MISSING: {field}")
            results['passed'] = False

    # Validation contraintes
    for field, spec in contract['schema']['fields'].items():
        if 'constraints' in spec and field in df.columns:
            if 'min' in spec['constraints']:
                if df[field].min() < spec['constraints']['min']:
                    results['checks'].append(f"MIN_FAIL: {field}")
                    results['passed'] = False

    return results
```

---

## 4. Data Lineage (OpenLineage)

### 4.1 Intégration OpenLineage

```python
from openlineage.client import OpenLineageClient
from openlineage.client.run import RunEvent, RunState, Run
from openlineage.client.event import Dataset, Job, ParentRun
from datetime import datetime

client = OpenLineageClient(url="http://marquez:5000")

def emit_lineage(job_name: str, inputs: list, outputs: list):
    """Émet un événement de lineage"""
    event = RunEvent(
        eventType=RunState.COMPLETE,
        eventTime=datetime.utcnow().isoformat(),
        run=Run(runId=job_name),
        job=Job(namespace="eva-pipelines", name=job_name),
        inputs=[Dataset(namespace="s3", name=p) for p in inputs],
        outputs=[Dataset(namespace="s3", name=p) for p in outputs],
        producer="eva-data-pipeline"
    )
    client.emit(event)

# Usage
emit_lineage(
    "bronze_to_silver",
    inputs=["s3://data-lake/bronze/sensors/date=2026-07-22/"],
    outputs=["s3://data-lake/silver/sensors/date=2026-07-22/"]
)
```

### 4.2 Marquez (Visualisation du Lineage)

```bash
docker run -d -p 5000:5000 -p 5001:5001 marquezproject/marquez:latest
# UI : http://localhost:3000
```

---

## 5. Observabilité des Pipelines

### 5.1 Métriques Essentielles

| Métrique | Description | Seuil d'alerte |
|----------|-------------|----------------|
| **Freshness** | Temps depuis la dernière mise à jour | > 30 min |
| **Volume** | Nombre de lignes par intervalle | ±20% vs moyenne |
| **Schema Drift** | Changement dans les colonnes / types | Tout changement |
| **Null Rate** | Ratio de valeurs manquantes | > 1% sur colonnes clés |
| **Row Count** | Nombre de lignes écrites | < seuil minimum |

### 5.2 Pipeline de Monitoring

```python
import time

class PipelineMonitor:
    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        self.start_time = time.time()
        self.metrics = {}

    def record_row_count(self, table: str, count: int):
        self.metrics[f"{table}.row_count"] = count
        # Alerte si volume anormal
        expected = self._get_expected_volume(table)
        if expected and abs(count - expected) / expected > 0.2:
            print(f"⚠️ Volume anormal sur {table}: {count} (attendu: {expected})")

    def record_freshness(self, table: str, last_timestamp):
        lag = datetime.now() - last_timestamp
        self.metrics[f"{table}.freshness_min"] = lag.total_seconds() / 60
        if lag > timedelta(minutes=30):
            print(f"🔴 Freshness dépassée sur {table}: {lag}")

    def finish(self):
        duration = time.time() - self.start_time
        self.metrics["duration_s"] = duration
        # Envoyer vers InfluxDB / Prometheus
        return self.metrics
```

---

## 6. DataOps : CI/CD pour les Pipelines

### 6.1 Tests de Pipeline Automatisés

```python
# tests/test_sensors_pipeline.py
import pytest
import pandas as pd

def test_bronze_schema():
    """Vérifie que les colonnes bronze sont présentes"""
    df = pd.read_parquet("/tmp/test_bronze/")
    required_cols = {"machine_id", "temperature", "timestamp", "_ingested_at"}
    assert required_cols.issubset(df.columns), f"Manque: {required_cols - set(df.columns)}"

def test_silver_clean():
    """Vérifie l'absence de doublons dans silver"""
    df = pd.read_parquet("/tmp/test_silver/")
    dupes = df.duplicated(subset=["machine_id", "timestamp"]).sum()
    assert dupes == 0, f"{dupes} doublons trouvés"

def test_gold_kpis():
    """Vérifie les KPIs gold"""
    df = pd.read_parquet("/tmp/test_gold/")
    assert df['temp_moyenne'].between(-50, 300).all()
    assert df['nb_mesures'].min() >= 0
```

### 6.2 Validation de Pipeline (Schema + Qualité)

```python
def validate_pipeline_output(stage: str, path: str) -> bool:
    """Checklist de validation après chaque étape"""
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(path)
    schema = pf.schema

    checks = {
        "bronze": lambda s: "_ingested_at" in str(s),
        "silver": lambda s: "temperature" in str(s) and "heure" in str(s),
        "gold": lambda s: "temp_moyenne" in str(s),
    }

    if stage in checks:
        result = checks[stage](schema)
        if not result:
            print(f"ÉCHEC validation {stage}")
            return False
    return True
```

---

## 7. Reverse ETL

### 7.1 Warehouse → Systèmes Opérationnels

```python
def reverse_etl_to_crm(metrics_path: str, api_endpoint: str):
    """Envoie les KPIs gold vers le CRM/Slack/ERP"""
    df = pd.read_parquet(metrics_path)

    # Agrégation quotidienne par machine
    daily_kpis = df.groupby("machine_id").agg(
        oee=("oee", "mean"),
        alert_count=("nb_alertes", "sum"),
    ).reset_index()

    # Push vers API CRM
    import requests
    for _, row in daily_kpis.iterrows():
        requests.post(api_endpoint, json={
            "machine_id": row['machine_id'],
            "oee_score": round(row['oee'], 3),
            "alert_count": int(row['alert_count']),
        })
```

### 7.2 Cas d'Usage Reverse ETL

- **CRM** (Salesforce, HubSpot) : KPI client, historique d'achat.
- **Marketing** : segments d'audience depuis le warehouse.
- **Support** (Zendesk) : statut client, utilisation produit.
- **ERP** : prévisions de demande, stocks.

---

## Pièges Courants (Pitfalls)

1. **Pipeline non idempotent.**  
   - *Erreur :* Un retry ou un backfill insère des lignes en double.  
   - *Correction :* Utiliser INSERT OVERWRITE, MERGE/DELETE+INSERT, ou des colonnes de déduplication.

2. **Pas de gestion des données tardives (late data).**  
   - *Erreur :* Une écriture en bronze datée d'hier arrive aujourd'hui → la partition daily est déjà fermée.  
   - *Correction :* Accepter les données tardives dans des partitions séparées (late/) ou en silver avec upsert.

3. **Manque de monitoring de la fraîcheur.**  
   - *Erreur :* Le pipeline se bloque silencieusement → les tableaux de bord montrent des données obsolètes de 3 jours.  
   - *Correction :* Monitorer la `max(timestamp)` de chaque table.

4. **Schema drift non détecté.**  
   - *Erreur :* Une source SQL ajoute une colonne → le pipeline échoue ou charge des données fausses.  
   - *Correction :* Utiliser schema evolution (mergeSchema) + alerter sur les changements de schéma.

5. **Pipeline trop rigide (hardcoded paths).**  
   - *Erreur :* Les chemins de fichiers sont codés en dur → impossible de tester en staging.  
   - *Correction :* Paramétrer les chemins (environnement, config, arguments).

---

## Liste de Vérification (Checklist)

- [ ] Architecture médaillon (bronze → silver → gold).
- [ ] Data contract signé entre producteur et consommateur.
- [ ] Pipeline idempotent (retry et backfill sans doublons).
- [ ] OpenLineage intégré pour le traçage des données.
- [ ] Monitoring de la fraîcheur avec alerting.
- [ ] Détection de schema drift.
- [ ] Tests automatisés (schema, volume, qualité).
- [ ] Reverse ETL configuré pour les systèmes opérationnels.
- [ ] Paramétrage environnement (dev/staging/prod).
- [ ] Documentation du pipeline (README + metadata).