---
name: data-lakes-lakehouse
description: "Data Lakes & Lakehouse: architecture Delta Lake, Apache Iceberg, Apache Hudi, catalog (Hive Metastore/AWS Glue/Unity Catalog), LakehouseFS, optimisation format table."
version: 1.0.0
author: EVA & The Hive
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [data-lake, lakehouse, delta-lake, apache-iceberg, apache-hudi, hive-metastore, glue-catalog, unity-catalog, parquet, paimon, dremio, trino]
    homepage: https://delta.io/
    related_skills: [data-warehouse, apache-spark, data-pipelines, dbt-analytics, data-quality-testing, airflow-orchestration]
prerequisites:
  commands: [python3, pip, java]
  pip_packages: [delta-spark, pyspark, pyiceberg, pyhudi, pandas, pyarrow]
---

# Compétence Data Lake & Lakehouse : Architecture et Formats de Table

## Vue d'ensemble

Le **Lakehouse** est la convergence du data lake (stockage brut, bon marché) et du data warehouse (ACID, performance SQL). Ses piliers :

- **Formats de table ouverts** : Delta Lake, Apache Iceberg, Apache Hudi.
- **ACID transactions** sur des fichiers Parquet/ORC.
- **Time Travel** : requêter les données à n'importe quel instant.
- **Schema evolution** : ajouter/supprimer/renommer des colonnes sans réécriture.
- **Catalog unifié** : Hive Metastore, AWS Glue, Unity Catalog.
- **Moteurs de requête** : Trino, Spark, Dremio, Flink, DuckDB.

Cette compétence couvre les trois formats leaders (Delta, Iceberg, Hudi), les catalogs, les opérations de maintenance (compaction, vacuum, expiration de snapshots), les optimisations de performance (Z-order, partitionnement évolutif), et l'intégration avec les moteurs de requête modernes.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Conçoit une architecture de données moderne (lakehouse).
- Doit choisir entre Delta Lake, Iceberg ou Hudi.
- Veut migrer d'un data lake traditionnel (fichiers HDFS bruts) vers un lakehouse ACID.
- Pose des questions sur Time Travel, schema evolution, compaction, vacuum.
- Intègre Trino, Dremio, DuckDB avec un lakehouse.

---

## Prérequis

```bash
pip install delta-spark pyspark pyiceberg pyhudi pandas pyarrow
```

---

## 1. Architecture Lakehouse

### 1.1 Stack Technologique

```
┌─────────────────────────────────────────────────────────┐
│                    Moteurs de Requête                     │
│  Trino  Spark  Flink  Dremio  DuckDB  Presto  Athena     │
├─────────────────────────────────────────────────────────┤
│                   Formats de Table                        │
│    Delta Lake    Apache Iceberg    Apache Hudi            │
│    ├─ Parquet ──┤  ├─ Parquet ──┤  ├─ Parquet ──┤       │
│    ├─ Transaction Log ──────────┤  ├─ Timeline ─┤       │
│    └─── Metadata / Statistics ──┘  └─ Markers ──┘       │
├─────────────────────────────────────────────────────────┤
│           Catalog / Metastore                              │
│  Hive Metastore  AWS Glue  Unity Catalog  Nessie (Git)   │
├─────────────────────────────────────────────────────────┤
│               Stockage Objet / HDFS                        │
│          S3   ADLS   GCS   MinIO   HDFS   NFS             │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Choix du Format

| Critère | Delta Lake | Iceberg | Hudi |
|---------|-----------|---------|------|
| **Écosystème** | Databricks, Spark natif | Universel (Trino, Flink, Spark) | Trino, Flink, Spark |
| **ACID** | Oui (transaction log) | Oui (via manifest files) | Oui (timeline) |
| **Time Travel** | Oui (version / timestamp) | Oui (snapshot ID) | Oui (instant time) |
| **Schema Evolution** | Oui (mergeSchema) | Oui (add/drop/rename) | Oui (schémamarker) |
| **Partition Evolution** | Non (fixe) | Oui (peut changer) | Oui (partition replace) |
| **Performance** | Excellent (Z-order) | Excellent (hidden partitioning) | Bon (Clustering) |
| **Maturité** | Très mature (Databricks) | Mature (Netflix, Apple) | Mature (Uber) |

---

## 2. Delta Lake

### 2.1 Configuration Spark + Delta

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("EVA-DeltaLake") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.databricks.delta.optimizeWrite.enabled", "true") \
    .config("spark.databricks.delta.autoCompact.enabled", "true") \
    .config("spark.databricks.delta.retentionDurationCheck.enabled", "false") \
    .getOrCreate()
```

### 2.2 Écriture ACID

```python
# Création d'une table Delta
df.write.format("delta") \
    .mode("overwrite") \
    .partitionBy("date") \
    .option("delta.tuneFileSizesForRewrites", "true") \
    .save("/data/lake/bronze/sensors/")

# Append avec mergeSchema (ajout automatique de colonnes)
df_new.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/data/lake/bronze/sensors/")
```

### 2.3 MERGE (Upsert)

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/data/lake/silver/sensors")

# Upsert : mettre à jour les lignes existantes, insérer les nouvelles
delta_table.alias("target") \
    .merge(
        df_updates.alias("source"),
        "target.machine_id = source.machine_id AND target.timestamp = source.timestamp"
    ) \
    .whenMatchedUpdate(set={
        "temperature": "source.temperature",
        "pression": "source.pression",
        "updated_at": "current_timestamp()"
    }) \
    .whenNotMatchedInsert(values={
        "machine_id": "source.machine_id",
        "temperature": "source.temperature",
        "pression": "source.pression",
        "timestamp": "source.timestamp",
        "created_at": "current_timestamp()"
    }) \
    .execute()
```

### 2.4 Time Travel

```python
# Lire une version antérieure
df_v1 = spark.read.format("delta") \
    .option("versionAsOf", "1") \
    .load("/data/lake/silver/sensors/")

# Lire à une date
df_ts = spark.read.format("delta") \
    .option("timestampAsOf", "2026-07-20") \
    .load("/data/lake/silver/sensors/")

# Lister l'historique
from delta.tables import DeltaTable
history = DeltaTable.forPath(spark, "/data/lake/silver/sensors/").history()
history.select("version", "timestamp", "operation", "operationParameters").show()
```

### 2.5 Optimisation : Z-Order et Compaction

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/data/lake/silver/sensors/")

# Z-ordering : clustering intelligent sur les colonnes de filtre
delta_table.optimize() \
    .executeZOrderBy("machine_id", "date")

# Compaction : fusionner les petits fichiers
delta_table.optimize() \
    .executeCompaction()

# Vacuum : supprimer les fichiers non référencés (après la période de rétention)
delta_table.vacuum(retentionHours=168)  # 7 jours
```

### 2.6 Delta Change Data Feed

```python
# Activer le CDF
spark.sql("""
    ALTER TABLE delta.`/data/lake/silver/sensors/`
    SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
""")

# Lire les changements depuis la version 5
df_changes = spark.read.format("delta") \
    .option("readChangeDataFeed", "true") \
    .option("startingVersion", "5") \
    .load("/data/lake/silver/sensors/")
```

---

## 3. Apache Iceberg

### 3.1 Configuration Iceberg

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("EVA-Iceberg") \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.iceberg_catalog",
            "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.iceberg_catalog.type", "hive") \
    .config("spark.sql.catalog.iceberg_catalog.uri", "thrift://hive-metastore:9083") \
    .getOrCreate()
```

### 3.2 Création de Table Iceberg

```sql
CREATE TABLE iceberg_catalog.sensors.sensor_readings (
    machine_id STRING,
    temperature DOUBLE,
    pression DOUBLE,
    timestamp TIMESTAMP
)
USING iceberg
PARTITIONED BY (hours(timestamp))
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.target-file-size-bytes' = '268435456',  -- 256 MB
    'write.parquet.compression-codec' = 'snappy',
    'history.expire.max-snapshot-age-ms' = '604800000'  -- 7 jours
);
```

### 3.3 Iceberg Features

```sql
-- Schema evolution
ALTER TABLE sensor_readings ADD COLUMN vibration DOUBLE;
ALTER TABLE sensor_readings RENAME COLUMN vibration TO vibration_level;
ALTER TABLE sensor_readings DROP COLUMN vibration_level;
ALTER TABLE sensor_readings ALTER COLUMN temperature TYPE DECIMAL(8,2);

-- Time Travel (snapshot ID)
SELECT * FROM sensor_readings
  FOR SYSTEM_TIME AS OF '2026-07-20 10:00:00';

-- Incremental read (entre deux snapshots)
SELECT * FROM sensor_readings
  FOR SYSTEM_VERSION BETWEEN 1 AND 5;

-- Partition evolution (Iceberg 1.2+ uniquement)
ALTER TABLE sensor_readings
  ADD PARTITION FIELD bucket(16, machine_id);
```

### 3.4 Maintenance Iceberg

```python
# Expire les vieux snapshots
spark.sql("""
    CALL iceberg_catalog.system.expire_snapshots(
        'sensors.sensor_readings',
        TIMESTAMP '2026-07-15 00:00:00'
    )
""")

# Réécrire les fichiers de données (compaction)
spark.sql("""
    CALL iceberg_catalog.system.rewrite_data_files(
        'sensors.sensor_readings',
        'strategy=>"sort", sort_order=>"machine_id ASC, timestamp ASC"'
    )
""")

# Réécrire les manifests
spark.sql("""
    CALL iceberg_catalog.system.rewrite_manifests(
        'sensors.sensor_readings'
    )
""")

# Supprimer les fichiers orphelins
spark.sql("""
    CALL iceberg_catalog.system.remove_orphan_files(
        'sensors.sensor_readings'
    )
""")
```

### 3.5 PyIceberg (Sans Spark)

```python
from pyiceberg.catalog import load_catalog
from pyiceberg.expressions import GreaterThanOrEqual

catalog = load_catalog(
    "default",
    **{
        "type": "rest",
        "uri": "http://iceberg-rest:8181/catalog",
        "warehouse": "s3://data-lake/iceberg/"
    }
)

table = catalog.load_table("sensors.sensor_readings")

# Requête sans Spark
scan = table.scan(
    row_filter=GreaterThanOrEqual("temperature", 100),
    limit=1000
)

for record in scan.to_pandas().to_dict(orient="records"):
    print(record)
```

---

## 4. Apache Hudi

### 4.1 Hudi avec Spark

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("EVA-Hudi") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.extensions",
            "org.apache.spark.sql.hudi.HoodieSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
    .getOrCreate()

# Écriture Hudi (Copy-on-Write)
df.write.format("hudi") \
    .option("hoodie.table.name", "sensor_readings") \
    .option("hoodie.datasource.write.recordkey.field", "machine_id") \
    .option("hoodie.datasource.write.precombine.field", "timestamp") \
    .option("hoodie.datasource.write.partitionpath.field", "date") \
    .option("hoodie.datasource.write.operation", "upsert") \
    .option("hoodie.upsert.shuffle.parallelism", "4") \
    .mode("append") \
    .save("/data/lake/hudi/sensors/")
```

### 4.2 Hudi Query Types

```python
# Snapshot Query (état actuel)
df_snapshot = spark.read.format("hudi") \
    .load("/data/lake/hudi/sensors/")

# Incremental Query (depuis un instant)
df_incr = spark.read.format("hudi") \
    .option("hoodie.datasource.query.type", "incremental") \
    .option("hoodie.datasource.read.begin.instanttime", "20260722100000") \
    .load("/data/lake/hudi/sensors/")

# Read-Optimized Query (Merge-on-Read)
df_ro = spark.read.format("hudi") \
    .option("hoodie.datasource.query.type", "read_optimized") \
    .load("/data/lake/hudi/sensors/")
```

---

## 5. Catalog et Metastore

### 5.1 Hive Metastore

```bash
# Schema de la base Hive Metastore
# Tables : DBS, TBLS, PARTITIONS, COLUMNS_V2, SDS, SERDES, etc.

# Initialisation
schematool -initSchema -dbType postgres

# Démarrer le service
hive --service metastore --hiveconf hive.metastore.port=9083
```

### 5.2 Unity Catalog (Open Source)

```bash
# Unity Catalog OSS (Databricks)
docker run -p 8080:8080 \
  -v /data/unity-catalog:/unity-catalog \
  -e UC_SERVER_CONF=/unity-catalog/server.yaml \
  unitycatalog/unity-catalog-server:latest
```

### 5.3 Nessie (Catalog Git-Like)

```python
from pynessie import NessieClient

client = NessieClient(base_url="http://nessie:19120/api/v1")

# Branches comme Git
client.create_branch("feature-2026-07")
client.merge("feature-2026-07", "main")

# Référencement temporel
ref = client.get_reference("main")
hash_main = ref.hash_
client.create_branch("experiment", hash_main)
```

---

## 6. Interrogation avec Moteurs Modernes

### 6.1 Trino (Presto SQL)

```sql
-- Delta Lake via Trino
CREATE TABLE delta_sensors (
    machine_id VARCHAR,
    temperature DOUBLE,
    pression DOUBLE,
    timestamp TIMESTAMP
) WITH (
    format = 'PARQUET',
    external_location = 's3://data-lake/delta/sensors/'
);

-- Iceberg via Trino
SELECT * FROM iceberg.sensors.sensor_readings
WHERE machine_id = 'M-001'
  AND timestamp >= TIMESTAMP '2026-07-20';
```

### 6.2 DuckDB (Analyse Locale Rapide)

```sql
-- Lire directement depuis Delta/Iceberg
INSTALL delta;
LOAD delta;

SELECT machine_id, AVG(temperature) AS avg_temp
FROM delta_scan('s3://data-lake/delta/sensors/')
WHERE machine_id IN ('M-001', 'M-002')
GROUP BY machine_id;

-- Iceberg via DuckDB
INSTALL iceberg;
LOAD iceberg;
SELECT * FROM iceberg_scan('s3://data-lake/iceberg/sensors/');
```

---

## Pièges Courants (Pitfalls)

1. **Petits fichiers (small file problem).**  
   - *Erreur :* Des milliers de fichiers de 1 Mo → métadonnées énormes, lectures lentes.  
   - *Correction :* Configurer `target-file-size-bytes` (Delta: 256MB, Iceberg: 256MB). Exécuter une compaction régulière.

2. **Pas de vacuum / expire snapshots.**  
   - *Erreur :* Les anciens fichiers ne sont jamais supprimés → stockage gonflé (10× le volume réel).  
   - *Correction :* Planifier `VACUUM` (Delta) ou `expire_snapshots` (Iceberg) régulièrement.

3. **Time Travel sans rétention.**  
   - *Erreur :* Les anciennes versions sont supprimées immédiatement → impossible de revenir en arrière.  
   - *Correction :* Configurer `delta.logRetentionDuration` (Delta), `history.expire.max-snapshot-age-ms` (Iceberg).

4. **Catalog non sauvegardé.**  
   - *Erreur :* Le Hive Metastore perd ses données → les tables existent sur S3 mais sont invisibles.  
   - *Correction :* Sauvegarder le metastore PostgreSQL. Ou utiliser un catalog basé sur fichier (Nessie, Unity Catalog).

5. **Écritures concurrentes sans gestion de conflits.**  
   - *Erreur :* Deux jobs écrivent sur la même table Delta → conflit de transaction log.  
   - *Correction :* Configurer `delta.concurrentWrite` et gérer les retries. Préférer un seul writer planifié.

---

## Liste de Vérification (Checklist)

- [ ] Format de table choisi (Delta / Iceberg / Hudi) selon l'écosystème.
- [ ] Taille de fichier cible configurée (256 MB idéal).
- [ ] Compaction régulière planifiée (journalière/hebdomadaire).
- [ ] Vacuum / expire snapshots actif (rétention 7+ jours).
- [ ] Catalog metastore sauvegardé (Hive Metastore / Glue / Unity).
- [ ] Time Travel testé (requête historique fonctionnelle).
- [ ] Schema evolution testée (ajout/suppression de colonne).
- [ ] Partitionnement adapté aux requêtes (date, machine_id, site).
- [ ] Conflits d'écriture gérés (idempotence, retry).
- [ ] Moteurs de requête connectés (Trino, Spark, DuckDB).