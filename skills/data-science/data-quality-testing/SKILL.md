---
name: data-quality-testing
description: "Data quality & testing: Great Expectations, Soda, dbt tests, data validation, freshness monitoring, anomaly detection, data observability, schema drift."
version: 1.0.0
author: EVA & The Hive
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [data-quality, great-expectations, soda, data-testing, data-validation, anomaly-detection, schema-drift, data-observability, monte-carlo]
    homepage: https://greatexpectations.io/
    related_skills: [dbt-analytics, data-pipelines, data-warehouse, data-lakes-lakehouse, apache-spark, airflow-orchestration]
prerequisites:
  commands: [python3, pip]
  pip_packages: [great_expectations, soda-core, soda-core-postgres, soda-core-snowflake, soda-core-bigquery, pandera, pyarrow, pandas]
---

# Compétence Data Quality & Testing : Validation et Observabilité

## Vue d'ensemble

La **qualité des données** est le pilier le plus critique de toute infrastructure data. Cette compétence couvre les outils et méthodes pour :

- **Great Expectations** : framework de validation avec expectation stores, Data Docs, suites.
- **Soda Core** : validation légère en ligne de commande, idéale pour CI/CD.
- **dbt Tests** : tests génériques et personnalisés intégrés aux transformations.
- **Pandera** : validation de schéma pandas/polars en Python.
- **Freshness Monitoring** : vérification de l'actualité des données.
- **Anomaly Detection** : détection de dérives (volume, distribution, schema).
- **Schema Drift** : détection des changements de structure.
- **Data Observability** : monitoring continu (Sifflet, Monte Carlo, Databand).

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Doit valider la qualité des données ingérées (nulls, doublons, types, ranges).
- Veut configurer des alertes sur la fraîcheur des données.
- A besoin de détecter des anomalies de volume ou de distribution.
- Implémente un pipeline CI/CD avec validation des données.
- Pose des questions sur les frameworks de data observability.

---

## 1. Great Expectations

### 1.1 Initialisation

```bash
pip install great_expectations

# Initialiser un projet
great_expectations init

# Connexion à une datasource
great_expectations datasource new
```

### 1.2 Configuration Datasource (Python)

```python
import great_expectations as ge
from great_expectations.core.batch import BatchRequest
from great_expectations.data_context import FileDataContext

context = FileDataContext.create(project_root_dir="./gx_project")

# Datasource Parquet
datasource_config = {
    "name": "sensors_datasource",
    "class_name": "Datasource",
    "execution_engine": {"class_name": "PandasExecutionEngine"},
    "data_connectors": {
        "parquet_connector": {
            "class_name": "ConfiguredAssetFilesystemDataConnector",
            "assets": {
                "sensor_readings": {
                    "base_directory": "/data/lake/silver/sensors/",
                    "pattern": "date=(.*)/.*\.parquet",
                    "group_names": ["date"],
                }
            },
            "base_directory": "/data/lake/silver/sensors/",
            "default_regex": {
                "pattern": "(.*)",
                "group_names": ["filename"],
            },
        }
    },
}
context.add_datasource(**datasource_config)
```

### 1.3 Création d'Expectations (Suites)

```python
import great_expectations as ge

# Créer une suite d'expectations
suite = context.add_expectation_suite("sensors_quality_suite")

batch_request = BatchRequest(
    datasource_name="sensors_datasource",
    data_connector_name="parquet_connector",
    data_asset_name="sensor_readings",
)

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="sensors_quality_suite",
)

# Expectations sur les colonnes
validator.expect_column_to_exist("machine_id")
validator.expect_column_to_exist("temperature")
validator.expect_column_to_exist("pression")
validator.expect_column_to_exist("timestamp")

# Contraintes de nullité
validator.expect_column_values_to_not_be_null("machine_id")
validator.expect_column_values_to_not_be_null("temperature")
validator.expect_column_values_to_not_be_null("timestamp")

# Contraintes de plage
validator.expect_column_values_to_be_between(
    "temperature", min_value=-50, max_value=300
)
validator.expect_column_values_to_be_between(
    "pression", min_value=0, max_value=50
)

# Contraintes de type
validator.expect_column_values_to_be_of_type("machine_id", "str")
validator.expect_column_values_to_be_of_type("temperature", "float64")

# Contraintes d'unicité (clé composite)
validator.expect_compound_columns_to_be_unique(
    ["machine_id", "timestamp"]
)

# Distribution (quantiles)
validator.expect_column_quantile_values_to_be_between(
    "temperature",
    quantile_ranges={
        "quantiles": [0.05, 0.25, 0.5, 0.75, 0.95],
        "value_ranges": [
            [10, 30],     # 5% des valeurs entre 10 et 30
            [40, 60],     # 25% des valeurs entre 40 et 60
            [55, 75],     # 50% (médiane) entre 55 et 75
            [70, 90],     # 75% des valeurs entre 70 et 90
            [85, 120],    # 95% des valeurs entre 85 et 120
        ],
    }
)

# Valeurs distinctes
validator.expect_column_distinct_values_to_be_in_set(
    "alerte", ["NORMAL", "WARNING", "CRITIQUE"]
)

# Taille de la table
validator.expect_table_row_count_to_be_between(min_value=100, max_value=50000)

# Enregistrer la suite
validator.save_expectation_suite(discard_failed_expectations=False)

# Générer les Data Docs
context.build_data_docs()
```

### 1.4 Exécution des Validations

```python
# Valider un nouveau batch
results = context.run_checkpoint(
    checkpoint_name="sensors_checkpoint",
    batch_request=batch_request,
)

# Résultats
if results["success"]:
    print("✅ Toutes les expectations passent")
else:
    for result in results["run_results"].values():
        for exp_result in result["expectation_suite_results"]:
            if not exp_result["success"]:
                print(f"❌ Échec : {exp_result['expectation_config']['expectation_type']} "
                      f"— {exp_result.get('exception_info', {}).get('raised_exception', '')}")
```

### 1.5 Data Docs (HTML)

```bash
# Générer et ouvrir les rapports
great_expectations docs build
great_expectations docs open
```

---

## 2. Soda Core

### 2.1 Configuration

```yaml
# configuration.yml
data_source sensors_db:
  type: postgres
  host: postgres-1.data.internal
  port: 5432
  username: ${SODA_DB_USER}
  password: ${SODA_DB_PASSWORD}
  database: dw_prod
  schema: marts
```

### 2.2 Checks de Qualité (YAML)

```yaml
# checks/sensors_checks.yml
checks for marts.fact_sensor_readings:
  # Fraîcheur
  - freshness(timestamp) < 1h
  - freshness(_ingested_at) < 2h

  # Volume
  - row_count > 0
  - row_count between 100 and 50000:
      name: Volume journalier attendu
      warn: when < 100
      fail: when < 10

  # Nulls
  - missing_count(machine_sk) = 0:
      name: Aucune machine manquante
  - missing_count(temperature) = 0:
      name: Aucune température manquante

  # Doublons
  - duplicate_count(reading_sk) = 0:
      name: Pas de doublons sur la clé primaire

  # Plages
  - min(temperature) >= -50:
      name: Température min valide
  - max(temperature) <= 300:
      name: Température max valide

  # Types
  - schema:
      name: Vérification du schéma
      warn:
        when schema changes:
          column types: FAIL
          column deletion: WARN
          column addition: WARN
      fail:
        when forbidden column present:
          - password
          - secret

  # Distribution (anomaly detection)
  - anomaly detection for temperature:
      sensitivity: 0.1
      depth: 7d
```

### 2.3 Exécution Soda

```bash
# Validation simple
soda scan -d sensors_db -c configuration.yml checks/sensors_checks.yml

# Sortie JSON pour ingestion
soda scan -d sensors_db -c configuration.yml checks/sensors_checks.yml \
    --output-json > soda_results.json

# Intégration Airflow
soda scan -d sensors_db -c configuration.yml checks/sensors_checks.yml \
    --dag-id sensors_pipeline
```

### 2.4 Soda Cloud (Observabilité Continue)

```bash
# Envoyer les résultats vers Soda Cloud
soda scan -d sensors_db -c configuration.yml checks/sensors_checks.yml \
    --soda-cloud
```

---

## 3. Pandera : Validation de Schéma Python

### 3.1 Définition du Schéma Pandera

```python
import pandera as pa
from pandera.typing import DataFrame, Series

class SensorSchema(pa.DataFrameModel):
    """Schéma de validation pour les données capteurs"""
    machine_id: Series[str] = pa.Field(
        str_length={"min_value": 3, "max_value": 20},
        nullable=False
    )
    temperature: Series[float] = pa.Field(
        in_range={"min_value": -50, "max_value": 300},
        nullable=False
    )
    pression: Series[float] = pa.Field(
        in_range={"min_value": 0, "max_value": 50},
        nullable=True
    )
    timestamp: Series[object] = pa.Field(
        nullable=False
    )
    alerte: Series[str] = pa.Field(
        isin=["NORMAL", "WARNING", "CRITIQUE"],
        nullable=True
    )

    @pa.dataframe_check
    def no_duplicate_readings(cls, df: DataFrame) -> bool:
        """Vérifie qu'il n'y a pas de doublons (machine_id + timestamp)"""
        return not df.duplicated(subset=["machine_id", "timestamp"]).any()

    @pa.dataframe_check
    def temperature_range_valid(cls, df: DataFrame) -> bool:
        """Vérifie que la température est dans une plage réaliste"""
        return df['temperature'].between(-50, 300).all()
```

### 3.2 Validation en Pipeline

```python
import pandas as pd
import pandera as pa

# Lecture
df = pd.read_parquet("/data/lake/silver/sensors/date=2026-07-22/")

# Validation — lève une exception si échec
try:
    df_validated = SensorSchema.validate(df, lazy=True)
    print(f"✅ {len(df_validated)} lignes valides")
except pa.errors.SchemaErrors as err:
    print(f"❌ Erreurs de validation : {len(err.failure_cases)}")
    for case in err.failure_cases.head(5):
        print(f"  - {case['column']} : {case['check']} → valeur={case['value']}")
```

### 3.3 Décorateur pour Pipeline

```python
@pa.check_types(lazy=True)
def transform_sensor_data(data: DataFrame[SensorSchema]) -> DataFrame[OutputSchema]:
    """Fonction avec validation automatique entrée/sortie"""
    result = data.groupby("machine_id").agg(
        temp_moyenne=("temperature", "mean"),
        nb_releves=("temperature", "count"),
    ).reset_index()
    return result
```

---

## 4. Détection d'Anomalies

### 4.1 Détection de Schema Drift

```python
import pandas as pd
import json

def detect_schema_drift(current_path: str, expected_schema: dict) -> dict:
    """Détecte les changements de schéma par rapport à un schéma de référence"""
    df = pd.read_parquet(current_path)
    current_schema = {col: str(dtype) for col, dtype in df.dtypes.items()}

    changes = {"added": [], "removed": [], "type_changed": []}

    for col, dtype in current_schema.items():
        if col not in expected_schema:
            changes["added"].append(col)
        elif expected_schema[col] != dtype:
            changes["type_changed"].append({"col": col, "expected": expected_schema[col], "got": dtype})

    for col in expected_schema:
        if col not in current_schema:
            changes["removed"].append(col)

    if any(changes.values()):
        print(f"⚠️ Schema drift détecté : {json.dumps(changes, indent=2)}")

    return changes

# Schéma attendu
expected = {
    "machine_id": "object",
    "temperature": "float64",
    "pression": "float64",
    "timestamp": "datetime64[ns]",
    "alerte": "object"
}

detect_schema_drift("/data/lake/silver/sensors/", expected)
```

### 4.2 Détection d'Anomalies de Volume

```python
import numpy as np
from datetime import datetime, timedelta

class VolumeAnomalyDetector:
    def __init__(self, window_days: int = 30):
        self.window_days = window_days
        self.history = []

    def check_volume(self, table: str, current_count: int) -> dict:
        from_date = datetime.now() - timedelta(days=self.window_days)

        # Simuler l'historique des volumes
        self.history.append(current_count)
        if len(self.history) < 7:
            return {"status": "insufficient_data", "count": current_count}

        mean = np.mean(self.history[-7:])
        std = np.std(self.history[-7:])
        z_score = (current_count - mean) / (std + 1e-6)

        result = {
            "status": "ok",
            "count": current_count,
            "mean_7d": round(mean, 0),
            "z_score": round(z_score, 2),
        }

        if abs(z_score) > 3:
            result["status"] = "critical"
            result["alert"] = f"Volume anormal : {current_count} (moyenne={mean:.0f}, z={z_score:.2f})"
        elif abs(z_score) > 2:
            result["status"] = "warning"

        return result
```

### 4.3 Détection de Données Tardives (Late Data)

```python
def detect_late_data(table_path: str, max_lag_hours: int = 2) -> dict:
    """Vérifie que les données les plus récentes ne sont pas trop vieilles"""
    df = pd.read_parquet(table_path)
    max_ts = df['timestamp'].max()
    now = datetime.utcnow()
    lag = (now - max_ts).total_seconds() / 3600

    result = {
        "table": table_path,
        "latest_timestamp": str(max_ts),
        "lag_hours": round(lag, 2),
        "status": "ok" if lag <= max_lag_hours else "critical",
    }

    if lag > max_lag_hours:
        result["alert"] = f"Données en retard : {lag:.1f}h (max {max_lag_hours}h)"
    elif lag > max_lag_hours * 0.8:
        result["status"] = "warning"

    return result
```

---

## 5. Alerting et Observabilité

### 5.1 Pipeline d'Alerting

```python
import requests

class DataQualityAlert:
    def __init__(self, slack_webhook: str = None, pagerduty_key: str = None):
        self.slack_webhook = slack_webhook
        self.pagerduty_key = pagerduty_key

    def alert(self, severity: str, title: str, message: str):
        if severity == "critical":
            self._pagerduty(title, message)
        self._slack(title, message)
        print(f"[{severity.upper()}] {title} : {message}")

    def _slack(self, title, message):
        if self.slack_webhook:
            requests.post(self.slack_webhook, json={
                "text": f"*{title}*\n{message}"
            })

    def _pagerduty(self, title, message):
        if self.pagerduty_key:
            requests.post("https://events.pagerduty.com/v2/enqueue", json={
                "routing_key": self.pagerduty_key,
                "event_action": "trigger",
                "payload": {
                    "summary": title,
                    "severity": "critical",
                    "source": "eva-data-quality",
                    "custom_details": {"message": message},
                }
            })

alert = DataQualityAlert(
    slack_webhook=Variable.get("slack_alert_webhook"),
    pagerduty_key=Variable.get("pagerduty_key"),
)

# Utilisation
volume_result = detector.check_volume("fact_sensor_readings", 50)
if volume_result["status"] == "critical":
    alert.alert("critical", "Volume anormal", volume_result["alert"])
```

---

## 6. Monitoring Continu (Data Observability)

### 6.1 Tableau de Bord de Qualité

```yaml
# SQL pour tableau de bord qualité
SELECT
    table_name,
    last_checked_at,
    ROUND(freshness_minutes, 1) AS freshness_min,
    row_count,
    null_rate,
    duplicate_rate,
    schema_version,
    CASE
        WHEN freshness_minutes > 60 THEN '🔴'
        WHEN freshness_minutes > 30 THEN '🟡'
        ELSE '🟢'
    END AS freshness_status,
    CASE
        WHEN null_rate > 0.05 THEN '🔴'
        WHEN null_rate > 0.01 THEN '🟡'
        ELSE '🟢'
    END AS null_status
FROM data_quality.metrics
WHERE date = CURRENT_DATE
ORDER BY table_name;
```

### 6.2 Intégration Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def check_data_quality(**context):
    import great_expectations as ge
    from great_expectations.data_context import FileDataContext

    context_gx = FileDataContext(project_root_dir="./gx_project")

    results = context_gx.run_checkpoint(
        checkpoint_name="sensors_checkpoint",
        batch_request=None,
    )

    if not results["success"]:
        raise ValueError("Échec des contrôles de qualité des données")

with DAG(...) as dag:
    extract = PythonOperator(...)
    transform = PythonOperator(...)
    load = PythonOperator(...)

    quality_check = PythonOperator(
        task_id='data_quality_check',
        python_callable=check_data_quality,
    )

    load >> quality_check  # Le quality gate bloque la suite
```

---

## Pièges Courants (Pitfalls)

1. **Trop de tests, pas assez d'actions.**  
   - *Erreur :* 200 expectations qui échouent toutes → les équipes ignorent les alertes.  
   - *Correction :* Commencer par 5-10 tests critiques (nulls sur clés, freshness, doublons). Ajouter progressivement.

2. **Seuils trop stricts.**  
   - *Erreur :* `expect_column_values_to_be_between("temperature", 10, 50)` → bloque des données valides la nuit où il fait 8°C.  
   - *Correction :* Utiliser des seuils adaptés à la réalité terrain. Ajouter des fenêtres de tolérance.

3. **Pas de gestion des valeurs manquantes autorisées.**  
   - *Erreur :* `expect_column_values_to_not_be_null` sur une colonne optionnelle → blocage du pipeline.  
   - *Correction :* `mostly=0.95` pour tolérer 5% de nulls.

4. **Freshness mal configurée sur des pipelines à latence.**  
   - *Erreur :* Un pipeline qui met 45 minutes à s'exécuter → alerte freshness fausse toutes les heures.  
   - *Correction :* Configurer le seuil en fonction du SLA réel du pipeline, pas d'un idéal.

5. **Schema drift ignoré.**  
   - *Erreur :* Une source ajoute une colonne → les validations échouent silencieusement.  
   - *Correction :* Configurer `when schema changes: WARN` dans Soda, et investiguer automatiquement.

---

## Liste de Vérification (Checklist)

- [ ] Great Expectations ou Soda configuré sur chaque couche (bronze/silver/gold).
- [ ] Tests de nullité sur les colonnes clés (primary key, FK).
- [ ] Tests de plage sur les mesures numériques.
- [ ] Freshness monitoring configuré (< 30 min pour temps réel, < 24h pour batch).
- [ ] Détection de doublons sur les clés composites.
- [ ] Schema drift détecté et alerté.
- [ ] Anomaly detection sur les volumes (Z-score > 3 ou écart > 20%).
- [ ] Pipeline de qualité bloquant (quality gate avant utilisation des données).
- [ ] Alerting Slack/PagerDuty configuré.
- [ ] Dashboard de qualité visible par l'équipe.