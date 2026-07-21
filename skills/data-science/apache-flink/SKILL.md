---
name: apache-flink
description: "Apache Flink: stream processing unifié (batch = cas particulier du stream), event time, stateful computations, CEP, savepoints, exactly-once."
version: 1.0.0
author: EVA & The Hive
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [flink, stream-processing, event-time, flink-sql, cep, beam, savepoint, state-backend]
    homepage: https://flink.apache.org/
    related_skills: [apache-kafka, apache-spark, data-quality-testing, data-pipelines, airflow-orchestration]
prerequisites:
  commands: [python3, pip, java]
  pip_packages: [apache-flink, apache-flink-statefun, pyflink]
---

# Compétence Apache Flink : Traitement de Flux Unifié (Streaming & Batch)

## Vue d'ensemble

**Apache Flink** est le moteur de traitement de flux le plus avancé, avec une philosophie radicale : **le batch est un cas particulier du streaming à temps borné**. Ses caractéristiques clés :

- **Event Time processing** : traitement basé sur l'horloge de l'événement, pas du système.
- **State Backend** : état distribué scalable (RocksDB, Heap, ForSt).
- **Savepoints / Checkpoints** : reprise exactement-une-fois (exactly-once) sans perte.
- **Flink SQL** : requêtes SQL stream avec des tables dynamiques.
- **CEP (Complex Event Processing)** : détection de patterns temporels complexes.

Cette compétence couvre : PyFlink (Python), Flink SQL, CEP, gestion d'état (RocksDB), sauvegarde et restauration (savepoints), déploiement sur YARN/Kubernetes, intégration Kafka, watermarking, et fenêtrage avancé.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- A besoin de streaming temps réel avec exactly-once garanti.
- Doit manipuler des états distribués (machine learning online, sessions, agrégations).
- Veut détecter des séquences complexes d'événements (fraude, maintenance prédictive).
- Demande du batch unifié avec le même code que le streaming.
- Pose des questions sur les watermarks, les triggers, les state backends.

---

## Prérequis

```bash
pip install apache-flink pyflink
```

Vérification :

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(4)
print(f"Flink {env}"[:50])
```

---

## 1. Concepts Fondamentaux

### 1.1 Event Time vs Processing Time vs Ingestion Time

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.time_characteristic import TimeCharacteristic

env = StreamExecutionEnvironment.get_execution_environment()

# Event time (recommandé — basé sur l'horloge des capteurs)
env.set_stream_time_characteristic(TimeCharacteristic.EventTime)

# Processing time (basé sur l'horloge de l'exécuteur — le plus simple)
# env.set_stream_time_characteristic(TimeCharacteristic.ProcessingTime)

# Ingestion time (basé sur l'horloge de la source Kafka — entre les deux)
# env.set_stream_time_characteristic(TimeCharacteristic.IngestionTime)
```

### 1.2 Watermarks : Gestion du Retard

```python
from pyflink.datastream.watermark import WatermarkStrategy
from pyflink.datastream.watermark import TimestampAssigner
from pyflink.common.time import Duration

class SensorTimestampAssigner(TimestampAssigner):
    def extract_timestamp(self, value, record_timestamp):
        import datetime
        return datetime.datetime.fromisoformat(value['timestamp']).timestamp() * 1000

# Watermark : 10 secondes de tolérance au retard
watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
    Duration.of_seconds(10)
).with_timestamp_assigner(SensorTimestampAssigner())

stream = env.from_collection([
    {"machine_id": "M-001", "temperature": 87.3, "timestamp": "2026-07-22T10:00:00"},
    {"machine_id": "M-001", "temperature": 88.1, "timestamp": "2026-07-22T10:00:30"},
    # ... événements avec jusqu'à 10s de retard accepté
])

stream = stream.assign_timestamps_and_watermarks(watermark_strategy)
```

---

## 2. PyFlink DataStream API

### 2.1 Source Kafka

```python
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema

properties = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'flink-sensor-processor',
    'auto.offset.reset': 'earliest',
}

kafka_source = FlinkKafkaConsumer(
    topics='sensors-raw',
    deserialization_schema=SimpleStringSchema(),
    properties=properties
)

# Garantie exactly-once avec Kafka
kafka_source.set_start_from_earliest()
kafka_source.set_commit_offsets_on_checkpoints(True)

stream = env.add_source(kafka_source)
```

### 2.2 Transformations avec État

```python
from pyflink.datastream import MapFunction, FlatMapFunction
from pyflink.datastream.state import ValueStateDescriptor
import json

# Map simple
class ParseSensor(MapFunction):
    def map(self, value):
        return json.loads(value)

parsed = stream.map(ParseSensor()).name("parse-json")

# FlatMap avec état
class TemperatureTracker(FlatMapFunction):
    def __init__(self):
        self.state = None

    def open(self, runtime_context):
        # État persistant par clé (machine_id)
        desc = ValueStateDescriptor('max_temp_state', Types.DOUBLE())
        self.state = runtime_context.get_state(desc)

    def flat_map(self, value, collector):
        max_temp_prev = self.state.value() or 0.0
        if value['temperature'] > max_temp_prev + 5:  # Pic de +5°C
            collector.collect({
                "alarme": "PIC_TEMPERATURE",
                "machine_id": value['machine_id'],
                "temperature": value['temperature'],
                "precedent_max": max_temp_prev
            })
        if value['temperature'] > max_temp_prev:
            self.state.update(value['temperature'])

tracked = parsed.key_by(lambda x: x['machine_id']) \
                .flat_map(TemperatureTracker())
```

### 2.3 Keyed State : Différents Types

```python
from pyflink.datastream.state import (
    ValueStateDescriptor, ListStateDescriptor, MapStateDescriptor,
    ReducingStateDescriptor, AggregatingStateDescriptor
)

# ListState : historique des températures
list_desc = ListStateDescriptor('temp_history', Types.DOUBLE())
temp_history = runtime_context.get_list_state(list_desc)

# MapState : configuration par capteur
map_desc = MapStateDescriptor('sensor_config', Types.STRING(), Types.DOUBLE())
sensor_config = runtime_context.get_map_state(map_desc)

# AggregatingState : moyenne glissante
# (plus efficace que de stocker toute la liste)
```

---

## 3. Fenêtrage Avancé

### 3.1 Tumbling, Sliding, Session Windows

```python
from pyflink.datastream.window import (
    TumblingEventTimeWindows, SlidingEventTimeWindows,
    EventTimeSessionWindows, GlobalWindows
)
from pyflink.common.time import Time

# Tumbling : fenêtre fixe de 5 min
tumbling_window = parsed \
    .key_by(lambda x: x['machine_id']) \
    .window(TumblingEventTimeWindows.of(Time.minutes(5))) \
    .aggregate(TempAggregator())

# Sliding : fenêtre de 15 min, avance toutes les 5 min
sliding_window = parsed \
    .key_by(lambda x: x['machine_id']) \
    .window(SlidingEventTimeWindows.of(Time.minutes(15), Time.minutes(5))) \
    .aggregate(TempAggregator())

# Session : fenêtre basée sur les écarts entre événements (> 2 min = nouvelle session)
session_window = parsed \
    .key_by(lambda x: x['machine_id']) \
    .window(EventTimeSessionWindows.with_gap(Time.minutes(2))) \
    .aggregate(TempAggregator())

# Agrégateur personnalisé
class TempAggregator(AggregateFunction):
    def create_accumulator(self):
        return {'sum': 0.0, 'count': 0, 'min': float('inf'), 'max': -float('inf')}

    def add(self, value, acc):
        acc['sum'] += value['temperature']
        acc['count'] += 1
        acc['min'] = min(acc['min'], value['temperature'])
        acc['max'] = max(acc['max'], value['temperature'])
        return acc

    def get_result(self, acc):
        return {
            'avg_temp': acc['sum'] / acc['count'],
            'min_temp': acc['min'],
            'max_temp': acc['max'],
            'count': acc['count']
        }

    def merge(self, acc1, acc2):
        return {
            'sum': acc1['sum'] + acc2['sum'],
            'count': acc1['count'] + acc2['count'],
            'min': min(acc1['min'], acc2['min']),
            'max': max(acc1['max'], acc2['max']),
        }
```

### 3.2 Triggers Personnalisés

```python
from pyflink.datastream.window import TriggerResult, Trigger
from pyflink.datastream.window import TimeWindow

class EarlyFireTrigger(Trigger):
    """Déclenche un résultat après 5 événements ET au bout de 30s max"""
    def on_element(self, element, timestamp, window, ctx):
        count_ctx = ctx.get_partitioned_state(
            ValueStateDescriptor('count', Types.INT()))
        count = (count_ctx.value() or 0) + 1
        count_ctx.update(count)

        if count >= 5:
            count_ctx.clear()
            return TriggerResult.FIRE_AND_PURGE
        return TriggerResult.CONTINUE

    def on_processing_time(self, time, window, ctx):
        return TriggerResult.FIRE

    def on_event_time(self, time, window, ctx):
        return TriggerResult.FIRE_AND_PURGE

    def clear(self, window, ctx):
        ctx.get_partitioned_state(
            ValueStateDescriptor('count', Types.INT())).clear()
```

---

## 4. Flink SQL : Tables Dynamiques

### 4.1 Source Kafka en SQL

```sql
CREATE TABLE sensor_readings (
    machine_id STRING,
    temperature DOUBLE,
    pression DOUBLE,
    `timestamp` TIMESTAMP(3) METADATA FROM 'timestamp',
    WATERMARK FOR `timestamp` AS `timestamp` - INTERVAL '10' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'sensors-raw',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink-sql-consumer',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.fail-on-missing-field' = 'true',
    'json.ignore-parse-errors' = 'false'
);
```

### 4.2 Fenêtrage SQL (Tumbling / Hop / Session)

```sql
-- Fenêtre tumbling de 5 minutes
SELECT
    machine_id,
    TUMBLE_END(`timestamp`, INTERVAL '5' MINUTE) AS fenetre_fin,
    AVG(temperature) AS temp_moyenne,
    MAX(temperature) AS temp_max,
    COUNT(*) AS nb_mesures
FROM sensor_readings
GROUP BY
    machine_id,
    TUMBLE(`timestamp`, INTERVAL '5' MINUTE);

-- Fenêtre glissante (Hop)
SELECT
    machine_id,
    HOP_END(`timestamp`, INTERVAL '5' MINUTE, INTERVAL '15' MINUTE) AS fenetre_fin,
    AVG(temperature) AS temp_moyenne
FROM sensor_readings
GROUP BY
    machine_id,
    HOP(`timestamp`, INTERVAL '5' MINUTE, INTERVAL '15' MINUTE);
```

### 4.3 Jointure Flux - Table de Référence

```sql
-- Création d'une table de référence (machines)
CREATE TABLE machines (
    machine_id STRING PRIMARY KEY NOT ENFORCED,
    site STRING,
    zone STRING
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:postgresql://postgres:5432/sensors',
    'table-name' = 'machines',
    'lookup.cache.max-rows' = '5000',
    'lookup.cache.ttl' = '10min'
);

-- Jointure stream-table
SELECT
    s.machine_id,
    s.temperature,
    m.site,
    m.zone
FROM sensor_readings AS s
LEFT JOIN machines FOR SYSTEM_TIME AS OF s.proctime AS m
ON s.machine_id = m.machine_id;
```

### 4.4 Sink vers Delta Lake

```sql
CREATE TABLE temp_agg_delta (
    machine_id STRING,
    fenetre_fin TIMESTAMP(3),
    temp_moyenne DOUBLE,
    temp_max DOUBLE,
    nb_mesures BIGINT
) WITH (
    'connector' = 'delta',
    'table-path' = 's3://data-lake/curated/temp_agg/',
    'delta.auto-optimize.auto-compact' = 'true'
);

INSERT INTO temp_agg_delta
SELECT ... FROM sensor_readings ...;
```

---

## 5. Complex Event Processing (CEP)

### 5.1 Détection de Patterns Temporels

```python
from pyflink.datastream.cep.pattern import Pattern, AfterMatchSkipStrategy
from pyflink.datastream.cep import CEP
from pyflink.datastream.cep.functions import PatternProcessFunction
from pyflink.common.time import Time

# Pattern : augmentation rapide + pic critique dans les 2 min
pattern = Pattern.begin("mesure_stable") \
    .where(lambda v: 80 <= v['temperature'] <= 90) \
    .next("hausse_rapide") \
    .where(lambda v: v['temperature'] > 100) \
    .times_or_more(3) \
    .within(Time.minutes(2))

# Sauter les patterns qui se chevauchent
skip_strategy = AfterMatchSkipStrategy.skip_past_last_event()
pattern = pattern.with_skip_strategy(skip_strategy)

# Appliquer le pattern
keyed_stream = parsed.key_by(lambda x: x['machine_id'])
pattern_stream = CEP.pattern(keyed_stream, pattern)

class AlertePatternFunction(PatternProcessFunction):
    def process_match(self, match, ctx, collector):
        hausse = match.get('hausse_rapide')
        collector.collect({
            "machine_id": hausse[-1]['machine_id'],
            "type": "SURECHUFFEMENT_RAPIDE",
            "derniere_temp": hausse[-1]['temperature'],
            "nb_pics": len(hausse),
            "timestamp": hausse[-1]['timestamp']
        })

alerts = pattern_stream.process(AlertePatternFunction())
alerts.add_sink(...)
```

### 5.2 CEP Multi-Pattern

```python
# Pattern combiné : alarme si température élevée ET pression chute
pattern = Pattern.begin("temp_elevee") \
    .where(lambda v: v['temperature'] > 95) \
    .followed_by("pression_basse") \
    .where(lambda v: v['pression'] < 1.0) \
    .within(Time.minutes(1))
```

---

## 6. State Backend et Checkpointing

### 6.1 Configuration State Backend

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.state_backend import RocksDBStateBackend

env = StreamExecutionEnvironment.get_execution_environment()

# RocksDB (recommandé pour les états > 1 Go)
rocks_backend = RocksDBStateBackend(
    checkpoint_data_uri='file:///data/flink/checkpoints',
    enable_incremental=True
)
env.set_state_backend(rocks_backend)

# HeapStateBackend (pour petits états, en mémoire)
# env.set_state_backend(StateBackend())

# Configuration RocksDB fine
config = rocks_backend.get_db_options()
config.set_option("rocksdb.block.cache-size", "256mb")
config.set_option("rocksdb.writebuffer.size", "64mb")
config.set_option("rocksdb.max.write.buffer.number", "4")
```

### 6.2 Checkpointing de Production

```python
from pyflink.common.time import Duration

env.enable_checkpointing(60000)  # Checkpoint toutes les 60s
env.get_checkpoint_config().set_checkpoint_storage_dir(
    's3://flink-checkpoints/sensors-job/')

env.get_checkpoint_config().set_min_pause_between_checkpoints(30000)
env.get_checkpoint_config().set_checkpoint_timeout(Duration.of_minutes(10))
env.get_checkpoint_config().set_max_concurrent_checkpoints(1)
env.get_checkpoint_config().enable_externalized_checkpoints(
    'RETAIN_ON_CANCELLATION')  # Garde les checkpoints après arrêt

# Exactly-once (vs at-least-once)
env.get_checkpoint_config().set_checkpointing_mode('EXACTLY_ONCE')
```

### 6.3 Savepoints : Mise à jour à Chaud

```bash
# Déclencher un savepoint
bin/flink savepoint <job_id> s3://flink-savepoints/

# Redémarrer avec un nouveau JAR depuis un savepoint
bin/flink run -s s3://flink-savepoints/savepoint-xxxxx/ \
    -c com.eva.SensorJob \
    eva-flink-job-2.0.jar

# Arrêt avec savepoint
bin/flink stop --savepointPath s3://flink-savepoints/ <job_id>
```

---

## 7. Déploiement et Opérations

### 7.1 Cluster Kubernetes (Flink Operator)

```yaml
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: sensor-processor
spec:
  image: eva/flink-sensor-job:1.0
  flinkVersion: v1_20
  serviceAccount: flink
  jobManager:
    resource:
      memory: "4096m"
      cpu: 2
    replicas: 1
  taskManager:
    resource:
      memory: "8192m"
      cpu: 4
    replicas: 4
  job:
    jarURI: local:///opt/flink/usrlib/eva-flink-job.jar
    entryClass: com.eva.SensorJob
    args: ["--kafka.bootstrap.servers", "kafka:9092"]
    parallelism: 8
    upgradeMode: savepoint
    state: running
  flinkConfiguration:
    state.backend: rocksdb
    state.checkpoints.dir: s3://flink-checkpoints/
    state.savepoints.dir: s3://flink-savepoints/
    high-availability: org.apache.flink.kubernetes.highavailability.KubernetesHaServices
    high-availability.storageDir: s3://flink-ha/
```

### 7.2 Gestion des Backpressure

```python
# Vérifier le backpressure
# Flink Web UI → http://flink-dashboard:8081
# Jobs → Job actuel → Backpressure

# Ou via REST API
curl http://flink-jobmanager:8081/jobs/<job_id>/backpressure
```

---

## 8. Batch Unifié (Même Code que le Streaming)

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

# Batch = stream borné
env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(env)

# Lecture batch (fichier borné)
t_env.execute_sql("""
    CREATE TABLE batch_source (
        machine_id STRING,
        temperature DOUBLE,
        `timestamp` TIMESTAMP(3)
    ) WITH (
        'connector' = 'filesystem',
        'path' = 's3://data-lake/raw/sensors/date=2026-07-22/',
        'format' = 'parquet'
    )
""")

# Même SQL que le streaming
t_env.execute_sql("""
    INSERT INTO temp_agg
    SELECT machine_id, AVG(temperature), MAX(temperature)
    FROM batch_source
    GROUP BY machine_id
""").wait()
```

---

## Pièges Courants (Pitfalls)

1. **Idle sources sans watermark.**  
   - *Erreur :* Une partition Kafka vide bloque toutes les fenêtres car le watermark n'avance pas.  
   - *Correction :* Configurer `WatermarkStrategy.with_idleness(Duration.ofMinutes(1))`.

2. **RocksDB trop lent.**  
   - *Erreur :* Manque d'optimisation RocksDB (cache trop petit, write buffer sous-dimensionné).  
   - *Correction :* Augmenter `rocksdb.block.cache-size` (256-512 MB par TM). Utiliser `enable_incremental=True`.

3. **Checkpoints trop fréquents.**  
   - *Erreur :* Intervalle de checkpoint trop court (< 30s) → overhead I/O sur RocksDB et réseau.  
   - *Correction :* Minimum 60s entre checkpoints. Utiliser `set_min_pause_between_checkpoints`.

4. **Perte d'état après modification de code.**  
   - *Erreur :* Changer le nom d'un state descriptor invalide l'état existant.  
   - *Correction :* Utiliser le paramètre `uid()` sur les opérateurs stateful et `setUidHash()` pour garantir la compatibilité des savepoints. Nommer explicitement `valueState` avec des UIDs stables.

5. **Pas de gestion des late events.**  
   - *Erreur :* Les événements arrivant après le watermark sont ignorés silencieusement.  
   - *Correction :* Utiliser `sideOutputLateData()` pour capturer les événements tardifs dans un flux secondaire.

---

## Liste de Vérification (Checklist)

- [ ] Watermark configuré (event time processing).
- [ ] `with_idleness()` sur les sources potentiellement inactives.
- [ ] State backend RocksDB pour états > 1 Go.
- [ ] Checkpoints toutes les 60s minimum avec répertoire externe (S3/HDFS).
- [ ] Savepoints avant toute mise à jour de code.
- [ ] `uid()` défini sur tous les opérateurs stateful.
- [ ] Side output pour les late events.
- [ ] Backpressure monitoré dans l'interface Web.
- [ ] Exactly-once activé (Kafka source + checkpoint).
- [ ] Tests de reprise avec arrêt/reprise sur savepoint.