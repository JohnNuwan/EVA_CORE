---
name: dbt-analytics
description: "dbt (data build tool): transformations SQL analytics, testing, documentation, Jinja macros, incremental models, snapshots, exposures, CI/CD, packages."
version: 1.0.0
author: EVA & The Hive
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [dbt, sql, transformations, analytics-engineering, jinja, incremental-models, snapshots, data-testing, docs-generation]
    homepage: https://docs.getdbt.com/
    related_skills: [data-warehouse, data-pipelines, data-quality-testing, apache-spark, data-lakes-lakehouse, airflow-orchestration]
prerequisites:
  commands: [python3, pip]
  pip_packages: [dbt-core, dbt-snowflake, dbt-bigquery, dbt-postgres, dbt-trino, dbt-spark]
---

# Compétence dbt : Transformations SQL Analytics Engineering

## Vue d'ensemble

**dbt (data build tool)** est l'outil standard de l'analytics engineering. Il permet d'appliquer les principes du génie logiciel (tests, docs, CI/CD, versioning) aux transformations de données dans le warehouse.

Concepts clés :

- **Models** : fichiers SQL SELECT dans `/models/` → tables/vues dans le warehouse.
- **Tests** : assertions de qualité sur les données (unique, not_null, custom).
- **Documentation** : générée automatiquement à partir des descriptions et des tests.
- **Jinja** : templating SQL (macros, ref(), source(), variables).
- **Incremental models** : mises à jour partielles pour les grands volumes.
- **Snapshots** : SCD Type 2 nativement.
- **Exposures** : lien entre les datasets et les dashboards/notebooks.
- **Packages** : réutilisation de transformations communautaires (dbt_utils, dbt_expectations).

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Construit ou maintient des transformations SQL dans un data warehouse.
- Veut industrialiser les transformations avec tests et documentation.
- A besoin de modèles incrémentaux, snapshots, ou macros Jinja.
- Pose des questions sur les bonnes pratiques dbt (modélisation, naming, CI/CD).
- Migre des procédures stockées SQL vers dbt.

---

## Prérequis

```bash
pip install dbt-core dbt-snowflake  # adapter le provider

# Initialiser un projet
dbt init eva_analytics
cd eva_analytics
```

---

## 1. Structure d'un Projet dbt

```
eva_analytics/
├── models/
│   ├── staging/                # Silver : nettoyage et typage
│   │   ├── stg_sensors.sql
│   │   └── sources.yml        # Définition des sources
│   ├── marts/                  # Gold : modèles métier
│   │   ├── core/              # Modèles centraux
│   │   │   ├── dim_machine.sql
│   │   │   └── fact_sensor_readings.sql
│   │   └── reporting/         # Modèles de reporting
│   │       └── kpi_daily.sql
│   └── intermediate/          # Modèles intermédiaires (épuration)
│       └── int_sensor_hourly.sql
├── tests/                     # Tests custom (SQL)
│   └── assert_positive_temp.sql
├── snapshots/                 # SCD Type 2
│   └── machine_snapshot.sql
├── macros/                    # Macros Jinja réutilisables
│   └── generate_schema_name.sql
├── analyses/                  # Requêtes ad-hoc (pas de matérialisation)
├── seeds/                     # CSV importés comme tables
│   └── machine_zones.csv
├── dbt_project.yml            # Configuration du projet
├── packages.yml               # Packages externes
└── profiles.yml               # Connexions aux bases
```

---

## 2. Modèles (Models)

### 2.1 Source Definitions (`sources.yml`)

```yaml
# models/staging/sources.yml
version: 2

sources:
  - name: bronze
    schema: bronze
    database: dw_prod
    description: "Données brutes importées depuis le lac de données"
    tables:
      - name: sensor_readings
        description: "Relevés bruts des capteurs"
        columns:
          - name: machine_id
            description: "Identifiant de la machine"
            tests:
              - not_null
          - name: temperature
            description: "Température en °C"
          - name: timestamp
            description: "Horodatage de la mesure"
        loaded_at_field: _ingested_at
        freshness:
          warn_after: {count: 30, period: minute}
          error_after: {count: 60, period: minute}

      - name: machines
        description: "Référentiel des machines"
        columns:
          - name: machine_id
            tests: [unique, not_null]
```

### 2.2 Staging Model (Nettoyage)

```sql
-- models/staging/stg_sensors.sql
{{ config(
    materialized='view',
    bind=False,
    tags=['staging', 'hourly']
) }}

SELECT
    machine_id::VARCHAR(20) AS machine_id,
    temperature::DECIMAL(6,2) AS temperature,
    pression::DECIMAL(6,2) AS pression,
    timestamp::TIMESTAMP AS timestamp,
    _ingested_at::TIMESTAMP AS ingested_at,
    CASE
        WHEN temperature > 100 THEN 'CRITIQUE'
        WHEN temperature > 80 THEN 'WARNING'
        ELSE 'NORMAL'
    END AS alerte
FROM {{ source('bronze', 'sensor_readings') }}
WHERE timestamp IS NOT NULL
  AND temperature IS NOT NULL
```

### 2.3 Dimension Model

```sql
-- models/marts/core/dim_machine.sql
{{ config(
    materialized='table',
    unique_key='machine_sk',
    tags=['dimension', 'daily']
) }}

WITH machines AS (
    SELECT * FROM {{ ref('stg_machines') }}
),

final AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['machine_id']) }} AS machine_sk,
        machine_id,
        machine_type,
        site,
        zone,
        status,
        install_date,
        CURRENT_TIMESTAMP AS dbt_loaded_at
    FROM machines
    WHERE is_current = TRUE
)

SELECT * FROM final
```

### 2.4 Fact Model

```sql
-- models/marts/core/fact_sensor_readings.sql
{{ config(
    materialized='incremental',
    unique_key=['machine_sk', 'timestamp'],
    incremental_strategy='merge',
    partition_by={field: 'timestamp', data_type: 'date', granularity: 'day'},
    tags=['fact', 'real_time']
) }}

WITH sensors AS (
    SELECT * FROM {{ ref('stg_sensors') }}
    {% if is_incremental() %}
        WHERE timestamp > (SELECT MAX(timestamp) FROM {{ this }})
    {% endif %}
),

machines AS (
    SELECT machine_sk, machine_id
    FROM {{ ref('dim_machine') }}
    WHERE is_current = TRUE
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['m.machine_sk', 's.timestamp']) }} AS reading_sk,
    m.machine_sk,
    s.temperature,
    s.pression,
    s.alerte,
    s.timestamp,
    s.ingested_at
FROM sensors s
LEFT JOIN machines m ON s.machine_id = m.machine_id
```

### 2.5 Mart de Reporting

```sql
-- models/marts/reporting/kpi_daily.sql
{{ config(
    materialized='table',
    tags=['reporting', 'daily']
) }}

SELECT
    d.date,
    m.site,
    m.zone,
    COUNT(DISTINCT f.machine_sk) AS machines_actives,
    AVG(f.temperature) AS temp_moyenne,
    MAX(f.temperature) AS temp_max,
    STDDEV(f.temperature) AS temp_std,
    COUNT(*) AS nb_releves,
    SUM(CASE WHEN f.alerte = 'CRITIQUE' THEN 1 ELSE 0 END) AS nb_alertes_critiques
FROM {{ ref('fact_sensor_readings') }} f
LEFT JOIN {{ ref('dim_machine') }} m ON f.machine_sk = m.machine_sk
LEFT JOIN {{ ref('dim_date') }} d ON DATE(f.timestamp) = d.date
GROUP BY d.date, m.site, m.zone
ORDER BY d.date, m.site
```

---

## 3. Macros Jinja

### 3.1 Macro Générique

```sql
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

### 3.2 Macro Utilitaire

```sql
-- macros/pivot_columns.sql
{% macro pivot_columns(column, values, alias_prefix='') %}
    {% for value in values %}
        SUM(CASE WHEN {{ column }} = '{{ value }}' THEN 1 ELSE 0 END)
        AS {{ alias_prefix }}{{ value | lower | replace(' ', '_') }}
        {% if not loop.last %},{% endif %}
    {% endfor %}
{% endmacro %}

-- Utilisation
SELECT
    machine_id,
    {{ pivot_columns('alerte', ['CRITIQUE', 'WARNING', 'NORMAL'], 'count_') }}
FROM {{ ref('stg_sensors') }}
GROUP BY machine_id
```

### 3.3 Configuration Multi-Environnement

```yaml
# dbt_project.yml
name: eva_analytics
version: '1.0'
config-version: 2

profile: eva_analytics

model-paths: [models]
test-paths: [tests]
analysis-paths: [analyses]
macro-paths: [macros]
snapshot-paths: [snapshots]
seed-paths: [seeds]

target-path: target
clean-targets: [target, dbt_packages]

vars:
    staging_table_name: stg_sensors
    retention_days: 90
    alert_threshold: 100

models:
  eva_analytics:
    staging:
      +materialized: view
      +schema: staging
    marts:
      core:
        +materialized: table
        +schema: marts
      reporting:
        +materialized: table
        +schema: reporting
    intermediate:
      +materialized: ephemeral
```

---

## 4. Tests de Qualité

### 4.1 Tests Génériques

```yaml
# models/marts/core/schema.yml
version: 2

models:
  - name: dim_machine
    description: "Dimension des machines"
    columns:
      - name: machine_sk
        tests:
          - unique
          - not_null
      - name: machine_id
        tests:
          - unique
          - not_null
          - accepted_values:
              values: ['M-001', 'M-002', 'M-003', 'M-004', 'M-005']
      - name: status
        tests:
          - accepted_values:
              values: ['ACTIVE', 'MAINTENANCE', 'DECOMMISSIONED']

  - name: fact_sensor_readings
    description: "Faits relevés capteurs"
    columns:
      - name: temperature
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: -50
              max_value: 300
      - name: machine_sk
        tests:
          - not_null
          - relationships:
              to: ref('dim_machine')
              field: machine_sk
```

### 4.2 Tests Personnalisés (SQL)

```sql
-- tests/assert_positive_temperature.sql
-- Vérifie qu'il n'y a pas de température négative
SELECT machine_id, temperature, timestamp
FROM {{ ref('stg_sensors') }}
WHERE temperature < -50
```

### 4.3 Tests avec dbt_expectations (Package)

```yaml
# packages.yml
packages:
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.11.0"]
  - package: dbt-labs/dbt_utils
    version: 1.3.0
  - package: dbt-labs/codegen
    version: 0.13.0
```

```sql
-- Utilisation de dbt_expectations
{{ config(tags=['quality']) }}

SELECT *
FROM {{ ref('stg_sensors') }}
WHERE NOT {{ dbt_expectations.expect_column_values_to_be_between(
    'temperature', -50, 300
) }}
```

---

## 5. Snapshots (SCD Type 2)

```sql
-- snapshots/machine_snapshot.sql
{% snapshot machine_snapshot %}

{{ config(
    target_schema='snapshots',
    strategy='check',
    unique_key='machine_id',
    check_cols=['machine_type', 'site', 'zone', 'status'],
    invalidate_hard_deletes=True
) }}

SELECT * FROM {{ source('bronze', 'machines') }}

{% endsnapshot %}

-- Utilisation
SELECT * FROM {{ ref('machine_snapshot') }}
WHERE machine_id = 'M-001'
ORDER BY dbt_valid_from DESC
```

---

## 6. Documentation

### 6.1 Description des Modèles

```yaml
# models/marts/core/schema.yml (suite)
models:
  - name: fact_sensor_readings
    description: >
      Table de faits des relevés de capteurs. Chaque ligne représente
      une mesure unique d'une machine à un instant donné.
    docs:
      show: true
      node_color: '#2c7fb8'
    columns:
      - name: reading_sk
        description: "Clé de substitution unique (surrogate key)"
      - name: temperature
        description: "Température mesurée en degrés Celsius"
        tests:
          - not_null
```

### 6.2 Génération et Hébergement

```bash
# Générer la documentation
dbt docs generate

# Héberger localement
dbt docs serve --port 8080
```

---

## 7. CI/CD et Workflow

### 7.1 GitHub Actions

```yaml
# .github/workflows/dbt_ci.yml
name: dbt CI
on: [push]

jobs:
  dbt-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dbt
        run: pip install dbt-snowflake

      - name: Déployer les modèles (dev)
        run: |
          dbt deps
          dbt seed --target dev
          dbt run --target dev --full-refresh --select staging
          dbt run --target dev --select marts+
          dbt test --target dev

      - name: Générer la documentation
        run: dbt docs generate --target dev

      - name: Upload artifacts
        uses: actions/upload-pages-artifact@v3
        with:
          path: target/
```

### 7.2 Workflow de Déploiement

```bash
# Dev
dbt run --target dev
dbt test --target dev

# Staging (sur schéma dédié)
dbt run --target staging --select state:modified+  # Modèles modifiés uniquement
dbt test --target staging

# Production
dbt run --target prod --selector prod_selector
dbt test --target prod
dbt source freshness --target prod
```

---

## 8. Exposures (Traçabilité Dashboard)

```yaml
# models/marts/reporting/exposures.yml
version: 2

exposures:
  - name: oee_dashboard
    type: dashboard
    maturity: high
    url: https://looker.company.com/dashboards/42
    description: "Tableau de bord OEE temps réel"
    depends_on:
      - ref('kpi_daily')
      - ref('fact_sensor_readings')
    owner:
      name: EVA
      email: eva@thehive.local

  - name: machine_ml_features
    type: ml
    maturity: medium
    description: "Features ML pour la maintenance prédictive"
    depends_on:
      - ref('dim_machine')
      - ref('stg_sensors')
    owner:
      name: ML Team
```

---

## Pièges Courants (Pitfalls)

1. **Modèles non idempotents.**  
   - *Erreur :* Un `dbt run --full-refresh` produit des résultats différents d'une exécution normale.  
   - *Correction :* Toujours utiliser `{{ ref() }}` plutôt que les noms de tables bruts. Éviter les dépendances sur l'ordre d'exécution.

2. **Modèles incrémentaux mal configurés.**  
   - *Erreur :* `is_incremental()` sans condition WHERE → rechargement complet à chaque run.  
   - *Correction :* Toujours inclure un filtre `WHERE timestamp > (SELECT MAX(timestamp) FROM {{ this }})`.

3. **Pas de documentation ni de tests.**  
   - *Erreur :* Un projet dbt sans `schema.yml` → impossible de comprendre la sémantique des colonnes.  
   - *Correction :* `schema.yml` pour chaque modèle avec `description` et `tests`.

4. **Tests trop longs (full scan).**  
   - *Erreur :* Exécuter tous les tests sur toute l'historique → coût élevé (BigQuery/ Snowflake).  
   - *Correction :* Configurer `severity: warn` sur les tests coûteux, ou limiter aux dernières 24h.

5. **Refs cassées après changement de nom de modèle.**  
   - *Erreur :* Renommer un modèle sans mettre à jour tous les `{{ ref('ancien_nom') }}`.  
   - *Correction :* Utiliser `dbt ls --resource-type model --output name` pour auditer les dépendances. Configurer `dbt build` pour exécuter modèles dépendants en cascade.

---

## Liste de Vérification (Checklist)

- [ ] `sources.yml` définit toutes les données brutes avec freshness.
- [ ] Chaque modèle a un `schema.yml` avec description et tests.
- [ ] Les modèles incrémentaux ont la clause `{% if is_incremental() %}`.
- [ ] `{{ ref() }}` utilisé partout (pas de nom de table en dur).
- [ ] Snapshots configurés pour les dimensions à historique.
- [ ] Tests `unique` + `not_null` sur toutes les surrogate keys.
- [ ] Documentation générée (`dbt docs generate`).
- [ ] CI/CD avec tests avant merge sur la branche principale.
- [ ] Exposures définies pour les dashboards et artefacts ML.
- [ ] Packages utils installés (`dbt_utils`, `dbt_expectations`).