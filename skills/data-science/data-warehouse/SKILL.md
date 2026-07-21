---
name: data-warehouse
description: "Data Warehouse: modélisation dimensionnelle (Kimball/Inmon/Data Vault), star schema, Snowflake, BigQuery, Redshift, SQL analytique avancé, optimisation, SCD types."
version: 1.0.0
author: EVA & The Hive
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [data-warehouse, star-schema, snowflake-schema, kimball, inmon, data-vault, snowflake, bigquery, redshift, scd, olap, mpp]
    homepage: https://www.snowflake.com/
    related_skills: [data-pipelines, data-lakes-lakehouse, dbt-analytics, data-quality-testing, airflow-orchestration]
prerequisites:
  commands: [python3, pip]
  pip_packages: [dbt-core, dbt-snowflake, dbt-bigquery, dbt-postgres, sqlalchemy, psycopg2-binary, snowflake-connector-python, google-cloud-bigquery]
---

# Compétence Data Warehouse : Modélisation & SQL Analytique

## Vue d'ensemble

Le **Data Warehouse** est le socle de la Business Intelligence et de l'analyse décisionnelle. Cette compétence couvre :

- **Modélisation dimensionnelle** (Kimball) : star schema, snowflake schema.
- **Modélisation 3NF** (Inmon) : normalisation entreprise.
- **Data Vault 2.0** : hubs, links, satellites pour l'auditabilité.
- **SQL analytique avancé** : fenêtrage, cubes, rollup, grouping sets.
- **Optimisation** : clustering, partitionnement, materialized views, query profiling.
- **SCD (Slowly Changing Dimensions)** : type 0, 1, 2, 3, 6.
- **Snowflake, BigQuery, Redshift** : spécificités de chaque plateforme.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Conçoit un schéma de base de données analytique.
- Veut implémenter un star schema (faits + dimensions).
- Pose des questions sur les SCD, la modélisation dimensionnelle.
- Doit optimiser des requêtes SQL analytiques lentes.
- Migre vers Snowflake, BigQuery ou Redshift.

---

## 1. Modélisation Dimensionnelle (Kimball)

### 1.1 Star Schema : Structure Canonique

```sql
-- TABLE DE FAITS : mesures quantitatives
CREATE TABLE fact_sensor_readings (
    reading_sk    BIGINT IDENTITY PRIMARY KEY,  -- Surrogate key
    machine_sk    INT NOT NULL,                  -- FK vers dimension
    date_sk       INT NOT NULL,                  -- FK vers dimension temps
    time_sk       INT NOT NULL,                  -- FK vers dimension heure
    temperature   DECIMAL(6,2),
    pression      DECIMAL(6,2),
    vibration     DECIMAL(6,2),
    cycle_time    INT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE DE DIMENSION : attributs descriptifs
CREATE TABLE dim_machine (
    machine_sk    INT IDENTITY PRIMARY KEY,
    machine_id    VARCHAR(20) NOT NULL,
    machine_type  VARCHAR(50),
    site          VARCHAR(100),
    zone          VARCHAR(50),
    install_date  DATE,
    status        VARCHAR(20),
    valid_from    DATE NOT NULL,
    valid_to      DATE,
    is_current    BOOLEAN DEFAULT TRUE
);

-- DIMENSION TEMPS (granularité jour)
CREATE TABLE dim_date (
    date_sk       INT PRIMARY KEY,
    date          DATE NOT NULL,
    year          INT,
    quarter       INT,
    month         INT,
    month_name    VARCHAR(20),
    week          INT,
    day_of_week   INT,
    is_weekend    BOOLEAN,
    is_holiday    BOOLEAN,
    fiscal_year   INT,
    fiscal_quarter INT,
    UNIQUE(date)
);

-- DIMENSION HEURE (granularité minute)
CREATE TABLE dim_time (
    time_sk       INT PRIMARY KEY,
    heure         INT,
    minute        INT,
    hour_minute   VARCHAR(5),  -- HH:MM
    shift         VARCHAR(20), -- Matin/Après-midi/Nuit
    UNIQUE(heure, minute)
);
```

### 1.2 Requêtage Star Schema

```sql
-- Analyse OEE par site et par mois
SELECT
    m.site,
    d.year,
    d.month,
    COUNT(DISTINCT f.machine_sk) AS machines_actives,
    AVG(f.temperature) AS temp_moyenne,
    MAX(f.temperature) AS temp_max,
    COUNT(*) AS nb_releves
FROM fact_sensor_readings f
JOIN dim_machine m ON f.machine_sk = m.machine_sk
JOIN dim_date d ON f.date_sk = d.date_sk
WHERE m.is_current = TRUE
  AND d.year = 2026
GROUP BY m.site, d.year, d.month
ORDER BY m.site, d.year, d.month;
```

---

## 2. SCD (Slowly Changing Dimensions)

### 2.1 Types de SCD

| Type | Comportement | Usage |
|------|-------------|-------|
| **SCD 0** | Rétroactif fixe | Colonnes qui ne changent jamais |
| **SCD 1** | Écrasement | Correction d'erreur, pas d'historique |
| **SCD 2** | Nouvelle version | Historique complet (le plus courant) |
| **SCD 3** | Colonne précédente | Besoin de l'ancienne valeur uniquement |
| **SCD 6** | Hybride 1+2+3 | Tracking + current value |

### 2.2 SCD Type 2 Implementation (SQL)

```sql
-- Mise à jour SCD Type 2
MERGE INTO dim_machine AS target
USING (
    SELECT machine_id, machine_type, site, zone
    FROM staging_machine_updates
) AS source
ON target.machine_id = source.machine_id AND target.is_current = TRUE

-- Si les données ont changé : fermer l'ancienne version
WHEN MATCHED AND (
    target.machine_type <> source.machine_type OR
    target.site <> source.site OR
    target.zone <> source.zone
) THEN UPDATE SET
    valid_to = CURRENT_DATE,
    is_current = FALSE

-- Nouvelle version
INSERT (machine_id, machine_type, site, zone, valid_from, valid_to, is_current)
VALUES (source.machine_id, source.machine_type, source.site, source.zone,
        CURRENT_DATE, NULL, TRUE);
```

### 2.3 SCD Type 2 Query (Snapshot Temporel)

```sql
-- État des machines à une date donnée
SELECT f.*, m.machine_type, m.site, m.zone
FROM fact_sensor_readings f
JOIN dim_machine m ON f.machine_sk = m.machine_sk
WHERE m.valid_from <= '2026-06-15'
  AND (m.valid_to IS NULL OR m.valid_to > '2026-06-15');
```

---

## 3. SQL Analytique Avancé

### 3.1 Fenêtrage (Window Functions)

```sql
-- Rang et comparaison temporelle
SELECT
    machine_id,
    date,
    temperature,
    AVG(temperature) OVER (
        PARTITION BY machine_id
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moyenne_7j,
    temperature - LAG(temperature, 1) OVER (
        PARTITION BY machine_id ORDER BY date
    ) AS variation_jour,
    RANK() OVER (
        PARTITION BY machine_id
        ORDER BY temperature DESC
    ) AS rang_chaud
FROM sensor_readings;

-- Cumul mensuel
SELECT
    site,
    date,
    nb_releves,
    SUM(nb_releves) OVER (
        PARTITION BY site, EXTRACT(YEAR_MONTH FROM date)
        ORDER BY date
    ) AS cumul_mensuel
FROM daily_agg;
```

### 3.2 GROUP BY Extensions (Cubes, Rollup, Grouping Sets)

```sql
-- ROLLUP : hiérarchie (site → zone → machine)
SELECT
    site, zone, machine_id,
    AVG(temperature) AS temp_moyenne,
    GROUPING(site) AS is_site_total,
    GROUPING(zone) AS is_zone_total
FROM fact_sensor_readings f
JOIN dim_machine m ON f.machine_sk = m.machine_sk
GROUP BY ROLLUP(site, zone, machine_id);

-- CUBE : toutes les combinaisons
SELECT site, zone, machine_id, AVG(temperature)
FROM fact_sensor_readings f
JOIN dim_machine m ON f.machine_sk = m.machine_sk
GROUP BY CUBE(site, zone, machine_id);

-- GROUPING SETS : combinaisons spécifiques
SELECT site, zone, machine_id, AVG(temperature)
FROM fact_sensor_readings f
JOIN dim_machine m ON f.machine_sk = m.machine_sk
GROUP BY GROUPING SETS (
    (site, zone),
    (site),
    (zone),
    ()
);
```

### 3.3 Pivot / Unpivot

```sql
-- PIVOT : transformer des lignes en colonnes
SELECT *
FROM (
    SELECT machine_type, month, temperature
    FROM fact_sensor_readings f
    JOIN dim_machine m ON f.machine_sk = m.machine_sk
    JOIN dim_date d ON f.date_sk = d.date_sk
    WHERE d.year = 2026
)
PIVOT (
    AVG(temperature)
    FOR month IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
) AS p;

-- UNPIVOT (BigQuery) : colonnes → lignes
SELECT machine_id, month, avg_temp
FROM `project.dataset.kpi_table`
UNPIVOT (
    avg_temp FOR month IN (jan, feb, mar, apr)
);
```

---

## 4. Data Vault 2.0

### 4.1 Structure Data Vault

```sql
-- HUB : clés d'entreprise (business keys)
CREATE TABLE hub_machine (
    machine_hk    CHAR(32) PRIMARY KEY,  -- Hash MD5 de la business key
    machine_id    VARCHAR(20) NOT NULL,
    load_date     TIMESTAMP,
    record_source VARCHAR(100),
    UNIQUE(machine_id)
);

-- LINK : associations entre hubs
CREATE TABLE link_sensor_machine (
    sensor_machine_lk  CHAR(32) PRIMARY KEY,
    sensor_hk          CHAR(32) REFERENCES hub_sensor(sensor_hk),
    machine_hk         CHAR(32) REFERENCES hub_machine(machine_hk),
    load_date          TIMESTAMP,
    record_source      VARCHAR(100)
);

-- SATELLITE : attributs contextuels
CREATE TABLE sat_machine_details (
    machine_hk     CHAR(32) REFERENCES hub_machine(machine_hk),
    load_date      TIMESTAMP,
    record_source  VARCHAR(100),
    machine_type   VARCHAR(50),
    site           VARCHAR(100),
    zone           VARCHAR(50),
    install_date   DATE,
    hash_diff      CHAR(32),  -- Hash de tous les attributs pour détecter les changements
    PRIMARY KEY (machine_hk, load_date)
);
```

### 4.2 Data Vault vs Kimball

| Critère | Kimball (Star Schema) | Data Vault 2.0 |
|---------|----------------------|----------------|
| Complexité | Faible (compréhension métier) | Élevée (technique) |
| Audit trail | SCD type 2 limité | Complet (chaque changement) |
| Intégration multi-source | Difficile | Naturelle |
| Performance requêtes | Excellente (star) | Nécessite une couche de présentation |
| Cas d'usage | BI, tableaux de bord | Data Lakehouse, audit, conformité |

---

## 5. Spécificités des Plateformes Cloud

### 5.1 Snowflake

```sql
-- Clustering automatique
ALTER TABLE fact_sensor_readings
CLUSTER BY (date_sk, machine_sk);

-- Materialized view
CREATE MATERIALIZED VIEW mv_machine_daily AS
SELECT date_sk, machine_sk, AVG(temperature) AS avg_temp
FROM fact_sensor_readings
GROUP BY date_sk, machine_sk;

-- Time Travel (accès aux données historiques)
SELECT * FROM fact_sensor_readings
  AT (TIMESTAMP => '2026-07-20 10:00:00'::TIMESTAMP);

-- Zero-copy cloning (environnement de test)
CREATE DATABASE dw_dev CLONE dw_prod;

-- Query profiling
SELECT * FROM TABLE(
    INFORMATION_SCHEMA.QUERY_HISTORY_BY_SESSION(
        SESSION_ID => <session_id>,
        RESULT_LIMIT => 100
    )
);
```

### 5.2 BigQuery

```sql
-- Partitionnement et clustering
CREATE TABLE `project.dw.fact_sensor_readings`
PARTITION BY DATE(timestamp)
CLUSTER BY machine_sk
OPTIONS(
    require_partition_filter = TRUE,
    partition_expiration_days = 365
);

-- BI Engine (accélération en mémoire)
-- Réserver 10 Go pour les tables les plus interrogées

-- Scripting et procédures
DECLARE target_date DATE DEFAULT CURRENT_DATE();
CREATE TEMP TABLE temp_agg AS
SELECT machine_sk, COUNT(*) AS cnt
FROM fact_sensor_readings
WHERE DATE(timestamp) = target_date;

-- Slot estimation (optimisation des coûts)
SELECT
    query,
    total_slot_ms,
    total_bytes_billed
FROM `region-us`.INFORMATION_SCHEMA.JOBS
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR);
```

### 5.3 Amazon Redshift

```sql
-- Distribution style (clairé par machine jointe)
CREATE TABLE fact_sensor_readings (
    ...
) DISTKEY(machine_sk)
  SORTKEY(date_sk, time_sk);

-- Compression
ANALYZE COMPRESSION fact_sensor_readings;

-- Materialized views
CREATE MATERIALIZED VIEW mv_daily_avg AS
SELECT date_sk, machine_sk, AVG(temperature) AS avg_temp
FROM fact_sensor_readings
GROUP BY date_sk, machine_sk;

-- Query plan
EXPLAIN
SELECT m.site, AVG(f.temperature)
FROM fact_sensor_readings f
JOIN dim_machine m ON f.machine_sk = m.machine_sk
GROUP BY m.site;

-- WLM (Workload Management) — queues
-- Configurer les queues pour séparer ETL et BI
```

---

## 6. Optimisation des Performances

### 6.1 Stratégies par Plateforme

| Technique | Snowflake | BigQuery | Redshift |
|-----------|-----------|----------|----------|
| Partitionnement | `CLUSTER BY` | `PARTITION BY` | `SORTKEY` |
| Distribution | Automatique | Automatique | `DISTKEY` |
| Compression | Automatique | Automatique | `ENCODE` manuel |
| Cache | Result set cache | BI Engine | Result cache |
| Tuning slots | Virtual warehouse | Slots réservés | WLM queues |

### 6.2 Analyse de Requêtes Lentes

```sql
-- Identifier les goulots d'étranglement
-- 1. Full table scans
EXPLAIN SELECT ...;  -- Vérifier l'utilisation des indexes/clés

-- 2. Jointures distribuées (Redshift)
-- Éviter les broadcasts de grandes tables

-- 3. Trop de partitions lues
SELECT table_name, SUM(row_count) AS rows
FROM fact_sensor_readings
WHERE date_sk BETWEEN 20250101 AND 20250722;
--> Si millions de lignes : partition filter manquant

-- 4. Compression inefficace
ANALYZE COMPRESSION dim_machine;
```

---

## Pièges Courants (Pitfalls)

1. **Trop de colonnes dans la table de faits.**  
   - *Erreur :* Mettre des attributs dimensionnels dans la table de faits → jointures impossibles, redondance.  
   - *Correction :* Les attributs descriptifs vont dans les dimensions, les mesures dans les faits.

2. **SCD Type 2 sans clé de substitution (surrogate key).**  
   - *Erreur :* Utiliser la clé naturelle (machine_id) comme clé primaire → impossible d'avoir plusieurs versions.  
   - *Correction :* Toujours créer une `machine_sk` auto-incrémentée.

3. **Jointure sans index/clé de distribution.**  
   - *Erreur :* Faire JOIN sur une colonne non indexée → full scan des deux tables.  
   - *Correction :* Vérifier les clés de jointure, indices, `DISTKEY` (Redshift), clustering.

4. **Requêtes sans partition pruning.**  
   - *Erreur :* WHERE sans filtre sur la colonne de partition → toutes les partitions lues.  
   - *Correction :* Toujours filtrer sur la colonne de partition (date_sk, date, timestamp).

5. **Dimension date générée manuellement (incomplète).**  
   - *Erreur :* Pas de table dim_date → pas de capacité d'analyse calendaire, jours fériés, etc.  
   - *Correction :* Générer la dim_date sur 10+ ans avec tous les attributs calendaires.

---

## Liste de Vérification (Checklist)

- [ ] Star schema : faits + dimensions clairement séparés.
- [ ] Surrogate key (auto-incrément) sur chaque dimension.
- [ ] SCD Type 2 pour les dimensions qui changent dans le temps.
- [ ] Table dim_date générée (10 ans, jours fériés, trimestres fiscaux).
- [ ] Partitionnement/clustering sur les colonnes de filtrage.
- [ ] Compression activée sur les tables de faits.
- [ ] Tests de performance (EXPLAIN, profiling).
- [ ] Data Vault ou Kimball selon les besoins d'audit.
- [ ] Materialized views pour les agrégations fréquentes.
- [ ] Documentation du modèle dimensionnel (dictionnaire de données).