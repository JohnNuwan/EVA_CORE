---
name: apache-spark
description: "Apache Spark: traitement distribué batch & streaming avec PySpark, Spark SQL, MLlib, Structured Streaming et optimisation Catalyst/Tungsten."
version: 1.0.0
author: EVA & The Hive
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [spark, pyspark, spark-sql, streaming, big-data, databricks, emr, glue, parquet, delta-lake]
    homepage: https://spark.apache.org/
    related_skills: [apache-kafka, apache-flink, data-lakes-lakehouse, data-pipelines, airflow-orchestration]
prerequisites:
  commands: [python3, pip, java]
  pip_packages: [pyspark, delta-spark, pyarrow, pandas]
---

# Compétence Apache Spark : Traitement Distribué Batch & Streaming

## Vue d'ensemble

**Apache Spark** est le moteur unifié de traitement distribué pour l'analyse de gros volumes de données. Il excelle dans quatre domaines :

- **Spark SQL** : Requêtes SQL sur DataFrames/DataSets, optimisation Catalyst.
- **Structured Streaming** : Traitement en continu avec exactement-une-fois (exactly-once).
- **MLlib** : Machine learning distribué (régression, classification, clustering).
- **GraphX** : Traitement de graphes.

Cette compétence couvre les patterns de production : déploiement sur cluster (YARN/Kubernetes), optimisation Catalyst/Tungsten, tuning mémoire, gestion des shuffles, et intégration avec le lac de données (Delta Lake, Iceberg, Hudi).

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Demande de traiter de gros volumes de données (Go → Po) avec PySpark ou Scala.
- Veut exécuter des transformations ETL distribuées sur un cluster (Databricks, EMR, Glue).
- A besoin de streaming structuré à partir de Kafka ou de fichiers.
- Pose des questions sur l'optimisation Spark (shuffle, partitionnement, Catalyst).
- Veut écrire/lire en Delta Lake, Iceberg ou Parquet avec Spark.

---

## Prérequis

### Installation Locale (développement)

```bash
pip install pyspark delta-spark pyarrow pandas
```

Vérification :

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .appName("EVA-Spark-Test") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()
print(f"Spark {spark.version} OK — {spark.sparkContext.defaultParallelism} partitions par défaut")
spark.stop()
```

### Java

Spark nécessite Java 8/11/17 :

```bash
java -version  # >= 8 requis
```

---

## 1. SparkSession : Configuration de Production

### 1.1 Session avec Optimisations

```python
from pyspark.sql import SparkSession
import os

spark = SparkSession.builder \
    .appName("EVA-ETL-Production") \
    .config("spark.sql.adaptive.enabled", "true") \           # AQE : Adaptive Query Execution
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \    # Gestion du skew
    .config("spark.sql.cbo.enabled", "true") \                  # Cost-Based Optimizer
    .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64MB") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.dynamicAllocation.enabled", "true") \
    .config("spark.shuffle.service.enabled", "true") \
    .getOrCreate()
```

### 1.2 Delta Lake + Catalog

```python
spark = SparkSession.builder \
    .appName("EVA-DeltaLake") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()
```

---

## 2. Spark SQL : DataFrames & Requêtes

### 2.1 Lecture Multi-Format

```python
# Parquet (format natif recommandé)
df = spark.read.parquet("/data/raw/events/")

# Delta Lake (ACID, time travel)
df_delta = spark.read.format("delta").load("/data/lake/events/")

# CSV
df_csv = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("mode", "FAILFAST") \
    .csv("/data/raw/captures.csv")

# JSON (multi-ligne ou lignes)
df_json = spark.read \
    .option("multiline", "true") \
    .json("/data/raw/sensors.json")

# Kafka (streaming)
df_kafka = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "sensors-topic") \
    .load()
```

### 2.2 Transformations Essentielles

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Filtrage & sélection
df_clean = df.filter(F.col("temperature").isNotNull()) \
             .select("machine_id", "timestamp", "temperature")

# Colonnes calculées
df_enriched = df_clean.withColumn("heure", F.hour("timestamp")) \
    .withColumn("alerte", F.when(F.col("temperature") > 100, F.lit("CRITIQUE"))
                          .otherwise(F.lit("NORMAL")))

# Agrégation
df_agg = df_enriched.groupBy("machine_id", "heure") \
    .agg(
        F.mean("temperature").alias("temp_moyenne"),
        F.stddev("temperature").alias("temp_std"),
        F.count("*").alias("nb_mesures"),
        F.collect_list("alerte").alias("alertes")
    )

# Fenêtrage : top-N par groupe
w = Window.partitionBy("machine_id").orderBy(F.desc("temp_moyenne"))
df_top = df_agg.withColumn("rang", F.row_number().over(w)) \
               .filter(F.col("rang") <= 3)

# Dédoublonnage avec fenêtre
df_dedup = df.withColumn("rn", F.row_number().over(
    Window.partitionBy("machine_id", "timestamp").orderBy("event_time")
)) .filter(F.col("rn") == 1).drop("rn")
```

### 2.3 Jointures Optimisées

```python
# Broadcast join (petite table en mémoire)
df_broadcast = df_faits.join(F.broadcast(df_dimension), "machine_id", "left")

# Sort-merge join (par défaut pour grandes tables)
df_result = df_ventes.join(df_produits, "produit_id", "inner")

# Hint explicite
df_result = df_ventes.join(df_produits.hint("skew", "produit_id"), "produit_id")
```

---

## 3. Structured Streaming : Temps Réel

### 3.1 Lecture depuis Kafka

```python
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

schema = StructType([
    StructField("machine_id", StringType()),
    StructField("temperature", DoubleType()),
    StructField("pression", DoubleType()),
    StructField("timestamp", TimestampType()),
])

stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker1:9092,broker2:9092") \
    .option("subscribe", "sensors-raw") \
    .option("startingOffsets", "latest") \
    .option("maxOffsetsPerTrigger", "10000") \
    .load() \
    .select(F.from_json(F.col("value").cast("string"), schema).alias("data")) \
    .select("data.*")
```

### 3.2 Fenêtres Temporelles (Tumbling / Sliding)

```python
# Fenêtre tumbling de 5 minutes
df_windowed = stream_df \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        F.window("timestamp", "5 minutes"),
        "machine_id"
    ) \
    .agg(
        F.mean("temperature").alias("temp_moyenne"),
        F.max("temperature").alias("temp_max"),
        F.count("*").alias("nb_releves")
    )
```

### 3.3 Écriture en Sortie

```python
# Append mode (insertions uniquement)
query = df_windowed.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/data/checkpoints/sensors") \
    .table("lakes.sensors_agg") \
    .trigger(processingTime="1 minute") \
    .start()

# Complete mode (rewrite complet)
query_stream = df_windowed.writeStream \
    .format("console") \
    .outputMode("complete") \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()
```

### 3.4 Exactly-Once avec Checkpointing

```python
# Le checkpoint est la clé de l'exactly-once
# Stocker sur un système fiable (HDFS, S3, ADLS)
query = stream_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "s3://checkpoints/sensors-job/") \
    .trigger(processingTime="30 seconds") \
    .toTable("bronze.sensor_readings")
```

---

## 4. Optimisation des Performances (Catalyst + Tungsten)

### 4.1 AQE — Adaptive Query Execution (Spark 3+)

```python
# Configurations clés AQE
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64MB")
```

### 4.2 Partitionnement

```python
# Répartition optimale
df_partitionne = df.repartition(200, "machine_id")   # hash par machine_id
df_range = df.repartitionByRange(50, "timestamp")     # range pour ordre temporel
df_coalesce = df.coalesce(50)                         # réduire sans shuffle

# Bucketing (optimise les futures jointures)
df.write.bucketBy(20, "produit_id") \
    .sortBy("date_vente") \
    .mode("overwrite") \
    .saveAsTable("ventes_bucketed")
```

### 4.3 Taille des Fichiers

```python
# Contrôle des fichiers de sortie
df.write \
    .option("maxRecordsPerFile", "500000") \
    .option("parquet.block.size", "256MB") \
    .mode("overwrite") \
    .parquet("/data/curated/")
```

### 4.4 Cache et Persistance

```python
# Persistance en mémoire/série
df_cached = df_clean.cache()                              # cache en mémoire
df_persist = df_clean.persist(StorageLevel.MEMORY_AND_DISK_SER)

# Nettoyage
df_cached.unpersist()
```

### 4.5 Plan d'Exécution

```python
# Visualiser le plan Catalyst
df.explain("formatted")          # plan textuel détaillé
df.explain("cost")               # plan avec coûts estimés
df.explain("codegen")            # code généré par Tungsten

# Voir les étapes physiques
df.explain(True)
```

---

## 5. MLlib : Machine Learning Distribué

### 5.1 Pipeline de Feature Engineering

```python
from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer
from pyspark.ml import Pipeline

# Préparation
indexer = StringIndexer(inputCol="machine_type", outputCol="type_idx")
assembler = VectorAssembler(
    inputCols=["temperature", "pression", "vibration", "cycle_time"],
    outputCol="features"
)
scaler = StandardScaler(inputCol="features", outputCol="scaled_features")

pipeline = Pipeline(stages=[indexer, assembler, scaler])
df_transformed = pipeline.fit(df).transform(df)
```

### 5.2 Régression / Classification Distribuée

```python
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import RegressionEvaluator

rf = RandomForestRegressor(
    featuresCol="scaled_features",
    labelCol="defaillance",
    numTrees=100,
    maxDepth=10,
    subsamplingRate=0.8
)

model = rf.fit(df_train)
predictions = model.transform(df_test)

evaluator = RegressionEvaluator(labelCol="defaillance", metricName="rmse")
rmse = evaluator.evaluate(predictions)
print(f"RMSE : {rmse:.4f}")
```

### 5.3 K-Means Clustering Distribué

```python
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

kmeans = KMeans(featuresCol="scaled_features", k=5, seed=42)
model = kmeans.fit(df_train)

# Silhouette score
evaluator = ClusteringEvaluator(featuresCol="scaled_features")
silhouette = evaluator.evaluate(model.transform(df_train))
print(f"Silhouette : {silhouette:.4f}")
```

---

## 6. Intégration Delta Lake (ACID sur le Lac)

### 6.1 Écriture et Time Travel

```python
# Écriture ACID
df.write.format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .save("/data/lake/sensors/")

# Time Travel : requêter une version antérieure
df_v1 = spark.read.format("delta") \
    .option("versionAsOf", "1") \
    .load("/data/lake/sensors/")

df_timestamp = spark.read.format("delta") \
    .option("timestampAsOf", "2026-06-01") \
    .load("/data/lake/sensors/")
```

### 6.2 MERGE (Upsert) — Delta Lake

```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "/data/lake/sensors/")

delta_table.alias("target") \
    .merge(
        df_updates.alias("source"),
        "target.machine_id = source.machine_id AND target.timestamp = source.timestamp"
    ) \
    .whenMatchedUpdateAll() \
    .whenNotMatchedInsertAll() \
    .execute()
```

### 6.3 Optimisation Z-Order

```python
# Z-ordering sur les colonnes de filtrage fréquent
delta_table.optimize() \
    .executeCompaction()  # fusionne les petits fichiers

delta_table.optimize() \
    .executeZOrderBy("machine_id", "date")  # clustering multi-colonnes
```

---

## 7. Déploiement et Tuning Cluster

### 7.1 Databricks / EMR / Glue

```yaml
# Configuration Databricks recommandée
# Cluster : 4-8 workers (r5.2xlarge ou équivalent)
# Spark config :
spark.sql.adaptive.enabled: true
spark.sql.adaptive.coalescePartitions.enabled: true
spark.sql.adaptive.skewJoin.enabled: true
spark.sql.shuffle.partitions: auto
spark.databricks.delta.optimizeWrite: true
spark.databricks.delta.autoCompact: true
```

### 7.2 Taille des Partitions

```python
# Règle empirique : ~100-200MB par partition
taille_estimee = 500 * 1024 * 1024  # 500 MB
nb_partitions = taille_estimee / (100 * 1024 * 1024)  # ~5 partitions

# AQE s'occupe de l'optimisation automatique
```

### 7.3 Gestion des Skew (Données Déséquilibrées)

```python
# 1. Salted key pour répartir la charge
from pyspark.sql import functions as F
import random

salting = F.concat(F.col("machine_id"), F.lit("_"), 
                   (F.rand() * 10).cast("int"))
df_salted = df_dim.withColumn("salt", 
    (F.rand() * 10).cast("int"))
df_faits_salted = df_faits.crossJoin(
    spark.range(10).toDF("salt")
)

# 2. Ou laisser AQE gérer automatiquement
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
```

---

## 8. Monitoring et Debugging

### 8.1 Spark UI

```python
# Accès à l'interface Web (port 4040 par défaut)
# http://localhost:4040/
# Voir : Jobs, Stages, Storage, Environment, SQL, Executors
```

### 8.2 Metrics Programmatiques

```python
# Événements Spark (pour analyse des goulots)
spark.sparkContext.setLogLevel("WARN")

# Accumulators pour le suivi
accum = spark.sparkContext.accumulator(0)

def track_batch(df):
    accum.add(df.count())
    return df

df_tracked = df.rdd.mapPartitions(track_batch)
```

---

## Pièges Courants (Pitfalls)

1. **Shuffle explosif.**  
   - *Erreur :* `groupBy()`, `join()` ou `distinct()` sur des colonnes à haute cardinalité sans partitionnement préalable. Le shuffle peut dépasser la mémoire disponible.  
   - *Correction :* Pré-partitionner avec `repartition()` sur la clé de jointure, activer AQE, et augmenter `spark.sql.shuffle.partitions`.

2. **Petits fichiers (small file problem).**  
   - *Erreur :* Spark écrit des milliers de petits fichiers Parquet (128 Ko) qui ralentissent les lectures futures.  
   - *Correction :* Utiliser `coalesce()`, `repartition()`, `maxRecordsPerFile`, `delta.autoCompact` dans Databricks.

3. **Skew dans les jointures.**  
   - *Erreur :* Une clé de jointure très fréquente (ex : `machine_id` pour la machine la plus active) submerge un seul executor.  
   - *Correction :* Activer `spark.sql.adaptive.skewJoin.enabled=true` ou utiliser des salted keys.

4. **Serialisation Kryo non configurée.**  
   - *Erreur :* Par défaut Spark utilise Java serialization (lent). Les UDFs et classes personnalisées ralentissent.  
   - *Correction :* `spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")`.

5. **Broadcast join manqué.**  
   - *Erreur :* Spark fait un sort-merge join coûteux sur une table de dimension de 10 Mo.  
   - *Correction :* Forcer le broadcast : `df.join(F.broadcast(small_df), "key")`. Augmenter `spark.sql.autoBroadcastJoinThreshold` (défaut 10 Mo).

6. **Cache sans nettoyage.**  
   - *Erreur :* `df.cache()` sans `unpersist()` sature la mémoire des executors.  
   - *Correction :* Toujours libérer : `df.unpersist()` ou `spark.catalog.clearCache()`.

7. **Schema evolution non géré.**  
   - *Erreur :* Delta Lake par défaut rejette les nouveaux champs lors d'un append.  
   - *Correction :* `option("mergeSchema", "true")` lors de l'écriture.

---

## Liste de Vérification (Checklist)

- [ ] AQE activé (`spark.sql.adaptive.enabled=true`).
- [ ] Broadcast join pour les petites tables de dimension.
- [ ] Partitionnement adapté à la taille des données (100-200 MB par partition).
- [ ] Checkpoint location configurée pour le streaming.
- [ ] Schema evolution gérée (mergeSchema pour Delta).
- [ ] Spark UI accessible (port 4040) pour le debugging.
- [ ] Kryo serializer configuré pour les charges lourdes.
- [ ] Shuffle partitions adaptées (200 par défaut, ajuster selon le cluster).
- [ ] Compression Parquet Snappy (bon ratio vitesse/taille).
- [ ] Delta Lake optimisé (Z-order, compaction automatique).