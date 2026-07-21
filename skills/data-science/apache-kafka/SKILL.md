---
name: apache-kafka
description: "Apache Kafka: plateforme de streaming d'événements distribuée — producers, consumers, Kafka Streams, Kafka Connect, ksqlDB, schema registry, KRaft."
version: 1.0.0
author: EVA & The Hive
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [kafka, event-streaming, kafka-streams, kafka-connect, ksqldb, schema-registry, avro, protobuf, kraft]
    homepage: https://kafka.apache.org/
    related_skills: [apache-spark, apache-flink, data-pipelines, data-quality-testing, airflow-orchestration]
prerequisites:
  commands: [python3, pip, java]
  pip_packages: [kafka-python, confluent-kafka, faust-streaming, avro-python3, fastavro, jsonschema]
---

# Compétence Apache Kafka : Streaming d'Événements Distribué

## Vue d'ensemble

**Apache Kafka** est la plateforme de streaming d'événements décentralisée la plus déployée en production. Son architecture log distribuée (« commit log ») permet :

- **Ingestion en temps réel** de millions d'événements/s.
- **Stockage durable et répliqué** avec rétention configurable.
- **Traitement stream** nativement (Kafka Streams, ksqlDB).
- **Connecteurs** Kafka Connect pour l'intégration avec 200+ systèmes.
- **Exactly-once semantics** entre producers, brokers et consumers.

Cette compétence couvre l'architecture KRaft (ZooKeeper déprécié), le Schema Registry (Avro/Protobuf/JSON Schema), les patterns de production (idempotence, transactions, répartition des partitions), Kafka Connect (source/sink), Kafka Streams (DSL bas niveau et haut niveau), ksqlDB, et l'observabilité (Cruise Control, Kafka Exporter, Burrow).

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Veut configurer un cluster Kafka (KRaft mode) productif.
- Demande d'écrire des producers/consumers Python Java ou Go.
- Besoin de streaming d'événements entre microservices.
- Veut utiliser Kafka Connect pour ingérer/exporter des données.
- Pose des questions sur l'ordonnancement, la répartition des partitions, le rebalancing.
- A besoin de exactly-once, idempotence ou transactions.

---

## Prérequis

```bash
# Client Python complet
pip install kafka-python confluent-kafka faust-streaming avro-python3 fastavro jsonschema

# Confluent CLI (optionnel — gestion de cluster local)
curl -sL https://cnfl.io/cli | sh -s -- -b /usr/local/bin
```

---

## 1. Architecture KRaft (Kafka Raft)

### 1.1 Configuration KRaft — Pas de ZooKeeper

```properties
# config/kraft/server.properties
process.roles=controller,broker
node.id=1
controller.quorum.voters=1@localhost:9093
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
advertised.listeners=PLAINTEXT://kafka-1:9092
log.dirs=/data/kafka/data
num.partitions=3
default.replication.factor=3
min.insync.replicas=2
auto.create.topics.enable=false
```

```bash
# Formater le cluster (1ère fois)
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID \
    -c config/kraft/server.properties

# Démarrer KRaft
bin/kafka-server-start.sh config/kraft/server.properties
```

### 1.2 Topics et Partitions

```bash
# Création
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --create --topic sensors-raw --partitions 6 \
    --replication-factor 3 --config cleanup.policy=delete \
    --config retention.ms=604800000  # 7 jours

# Description
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --describe --topic sensors-raw

# Modification (ajout de partitions)
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --alter --topic sensors-raw --partitions 12
```

---

## 2. Producers : Écriture d'Événements

### 2.1 Producer Idempotent (Exactly-Once par Défaut)

```python
from confluent_kafka import Producer
import json

conf = {
    'bootstrap.servers': 'kafka-1:9092,kafka-2:9092,kafka-3:9092',
    'client.id': 'eva-sensor-producer',
    'acks': 'all',                             # Tous les ISR accusent
    'enable.idempotence': True,                # Exactly-once garanti
    'compression.type': 'snappy',
    'linger.ms': 5,                            # Batch jusqu'à 5ms
    'batch.size': 65536,                       # 64KB par batch
    'max.in.flight.requests.per.connection': 5,
}

producer = Producer(conf)

def delivery_report(err, msg):
    if err:
        print(f"ÉCHEC delivery : {err}")
    else:
        print(f"OK → partition {msg.partition()} | offset {msg.offset()}")

# Envoi avec clé = machine_id (garantit l'ordre par machine)
machine_id = "MACHINE-042"
payload = json.dumps({
    "machine_id": machine_id,
    "temperature": 87.3,
    "pression": 2.15,
    "timestamp": "2026-07-22T10:30:00Z"
}).encode('utf-8')

producer.produce(
    topic="sensors-raw",
    key=machine_id.encode('utf-8'),
    value=payload,
    callback=delivery_report
)

producer.flush()
```

### 2.2 Partitionnement Personnalisé

```python
# Round-robin sans clé
# sticky partitioner (défaut depuis Kafka 2.4) : groupe les messages en batch

# Avec clé : hash par défaut (murmur2) garantit même partition pour même clé
# Utile pour préserver l'ordre des événements d'une même entité

# Partitionneur personnalisé (Python)
from confluent_kafka import Producer
import hashlib

class SensorPartitioner:
    def partition(topic, key, partitions):
        # Envoyer les alertes critiques sur les partitions 0-1
        if b"CRITIQUE" in key:
            return 0
        # Hash standard pour les autres
        return hashlib.sha256(key).hexdigest().__hash__() % partitions
```

---

## 3. Consumers : Lecture d'Événements

### 3.1 Consumer fiable avec Gestion des Offsets

```python
from confluent_kafka import Consumer, KafkaError
import json

conf = {
    'bootstrap.servers': 'kafka-1:9092,kafka-2:9092',
    'group.id': 'eva-sensor-processor',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,              # Commit manuel
    'max.poll.interval.ms': 300000,           # 5 min max
    'session.timeout.ms': 45000,
    'heartbeat.interval.ms': 15000,
    'fetch.min.bytes': 1024,                  # Au moins 1KB par fetch
    'fetch.max.wait.ms': 500,
    'isolation.level': 'read_committed',      # Évite les messages transactionnels non commités
}

consumer = Consumer(conf)
consumer.subscribe(['sensors-raw'])

try:
    while True:
        msg = consumer.poll(1.0)  # timeout 1s
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Erreur : {msg.error()}")
                break

        data = json.loads(msg.value().decode('utf-8'))
        print(f"{msg.key()} | p{msg.partition()}@{msg.offset()} | {data['temperature']}°C")

        # Commit manuel après traitement réussi
        consumer.commit(asynchronous=False)
finally:
    consumer.close()
```

### 3.2 Reprise sur Erreur (Dead Letter Topic)

```python
def process_message(msg):
    try:
        data = json.loads(msg.value())
        # Traitement métier
        if data.get("temperature", 0) > 200:
            raise ValueError("Température hors échelle")
        return data
    except Exception as e:
        # Envoi vers Dead Letter Queue
        dlq_producer.produce(
            topic="sensors-dlq",
            key=msg.key(),
            value=msg.value(),
            headers={"error": str(e), "original_topic": msg.topic()}
        )
        dlq_producer.flush()
        return None
```

---

## 4. Kafka Streams : Traitement Stateful

### 4.1 Stream-DSL avec kafka-streams-python (Faust)

```python
import faust

app = faust.App(
    'sensor-stream-processor',
    broker='kafka://kafka-1:9092',
    value_serializer='json',
    consumer_auto_offset_reset='earliest',
    store='rocksdb://',              # State store RocksDB
)

class SensorEvent(faust.Record):
    machine_id: str
    temperature: float
    pression: float
    timestamp: str

class AlertAgg(faust.Record):
    machine_id: str
    count: int
    max_temp: float

sensor_topic = app.topic('sensors-raw', value_type=SensorEvent)
alert_topic = app.topic('sensors-alerts', value_type=AlertAgg)
alert_table = app.Table('alert-counts', default=int)

@app.agent(sensor_topic)
async def process_sensors(stream):
    async for event in stream.group_by(SensorEvent.machine_id):
        if event.temperature > 100:
            alert_table[event.machine_id] += 1
            await alert_topic.send(
                value=AlertAgg(
                    machine_id=event.machine_id,
                    count=alert_table[event.machine_id],
                    max_temp=event.temperature
                )
            )

# Fenêtrage temporel
@app.agent(sensor_topic)
async def windowed_avg(stream):
    async for event in stream \
            .group_by(SensorEvent.machine_id) \
            .tumbling(60):  # fenêtre de 60s
        yield event
```

### 4.2 KTable et GlobalKTable

```python
# KTable : table partitionnée (joindre avec un flux partitionné de la même clé)
machine_table = app.Table('machine-metadata', default=dict)

# GlobalKTable : copie complète sur tous les nœuds (joindre avec n'importe quelle clé)
global_config = app.GlobalTable('global-config', default=dict)
```

---

## 5. Kafka Connect : Intégration 200+ Systèmes

### 5.1 Source Connector (PostgreSQL → Kafka)

```json
{
  "name": "postgres-sensors-connector",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
    "connection.url": "jdbc:postgresql://postgres:5432/sensors",
    "connection.user": "kafka_connect",
    "connection.password": "${file:/secrets/db-password.txt}",
    "table.whitelist": "sensor_readings",
    "mode": "incrementing",
    "incrementing.column.name": "id",
    "topic.prefix": "postgres-",
    "poll.interval.ms": 5000,
    "transforms": "wrap",
    "transforms.wrap.type": "org.apache.kafka.connect.transforms.HoistField$Value",
    "transforms.wrap.field": "payload",
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "http://schema-registry:8081",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://schema-registry:8081"
  }
}
```

### 5.2 Sink Connector (Kafka → Parquet sur S3)

```json
{
  "name": "s3-sensors-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "s3.bucket.name": "data-lake-raw",
    "s3.part.size": 5242880,
    "topics": "sensors-raw",
    "flush.size": 10000,
    "rotate.interval.ms": 600000,
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "partitioner.class": "io.confluent.connect.storage.partitioner.HourlyPartitioner",
    "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
    "locale": "fr_FR",
    "timezone": "UTC",
    "schema.compatibility": "NONE",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://schema-registry:8081"
  }
}
```

---

## 6. ksqlDB : Streaming SQL

```sql
-- Création d'un stream
CREATE STREAM sensor_readings (
    machine_id VARCHAR KEY,
    temperature DOUBLE,
    pression DOUBLE,
    timestamp VARCHAR
) WITH (
    KAFKA_TOPIC = 'sensors-raw',
    VALUE_FORMAT = 'JSON'
);

-- Fenêtre tumbling 5 min
CREATE TABLE temp_avg_5min AS
    SELECT machine_id,
           AVG(temperature) AS avg_temp,
           MAX(temperature) AS max_temp,
           COUNT(*) AS count
    FROM sensor_readings
    WINDOW TUMBLING (SIZE 5 MINUTES)
    GROUP BY machine_id
    EMIT CHANGES;

-- Filtrage en continu (alerte)
CREATE STREAM high_temp_alerts AS
    SELECT machine_id, temperature, timestamp
    FROM sensor_readings
    WHERE temperature > 100
    EMIT CHANGES;

-- Jointure stream-table
CREATE TABLE machines (
    machine_id VARCHAR PRIMARY KEY,
    site VARCHAR,
    zone VARCHAR
) WITH (
    KAFKA_TOPIC = 'machines',
    VALUE_FORMAT = 'JSON'
);

CREATE STREAM enriched_sensors AS
    SELECT s.machine_id, s.temperature, m.site, m.zone
    FROM sensor_readings s
    LEFT JOIN machines m ON s.machine_id = m.machine_id
    EMIT CHANGES;
```

---

## 7. Schema Registry (Avro / Protobuf / JSON Schema)

### 7.1 Avro Producer avec Schema Registry

```python
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import json

schema_registry_conf = {'url': 'http://schema-registry:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

schema_str = """{
  "namespace": "com.eva.sensors",
  "type": "record",
  "name": "SensorReading",
  "fields": [
    {"name": "machine_id", "type": "string"},
    {"name": "temperature", "type": "double"},
    {"name": "pression", "type": "double", "default": 0.0},
    {"name": "timestamp", "type": "string"}
  ]
}"""

avro_serializer = AvroSerializer(
    schema_registry_client, schema_str,
    lambda obj, ctx: obj
)

producer = Producer({'bootstrap.servers': 'kafka-1:9092'})
topic = 'sensors-avro'

def send_sensor(data):
    producer.produce(
        topic=topic,
        key=data['machine_id'],
        value=avro_serializer(
            data,
            SerializationContext(topic, MessageField.VALUE)
        )
    )

send_sensor({
    "machine_id": "M-001",
    "temperature": 87.3,
    "pression": 2.15,
    "timestamp": "2026-07-22T10:30:00Z"
})
producer.flush()
```

### 7.2 Évolution de Schéma (Backward / Forward)

```bash
# Compatibilité par défaut : BACKWARD
# → Les consumers anciens lisent les nouveaux messages

# Modifier la compatibilité
curl -X PUT http://schema-registry:8081/config \
  -H "Content-Type: application/json" \
  -d '{"compatibility": "FORWARD_TRANSITIVE"}'

# Vérifier la compatibilité avant déploiement
curl -X POST http://schema-registry:8081/compatibility/subjects/sensors-raw-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "{\"type\":\"record\",...}"}'
```

---

## 8. Observabilité et Monitoring

### 8.1 Metrics Exporter (JMX → Prometheus)

```yaml
# Kafka exporter : metrics JMX → Prometheus format
# GitHub : danielqsj/kafka_exporter

scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets:
        - 'kafka-exporter:9308'
        - 'kafka-1:9308'
```

### 8.2 Cruise Control (Rebalance Automatique)

```bash
# Détection de déséquilibre
bin/kafka-cruise-control-start.sh \
    --config config/cruisecontrol.properties \
    --port 9090

# Proposer un plan de rebalancement
curl "http://localhost:9090/kafkacruisecontrol/rebalance?dryRun=true&verbose=true"

# Exécuter
curl -X POST "http://localhost:9090/kafkacruisecontrol/rebalance?dryRun=false"
```

### 8.3 Burrow (Consumer Lag)

```bash
# Burrow surveille le lag de tous les consumers
# Configuration :
[consumer.eva-sensor-processor]
servers = "kafka-1:9092,kafka-2:9092"
group = "eva-sensor-processor"

# Endpoint HTTP : /v3/kafka/{cluster}/consumer/{group}/lag
curl http://burrow:8000/v3/kafka/local/consumer/eva-sensor-processor/lag
```

---

## 9. Patterns de Production

### 9.1 Exactly-Once Semantics (EOS)

```python
# Producer : enable.idempotence=True
# Consumer : isolation.level=read_committed
# Transactions : Atomic multi-topic writes

producer_conf = {
    'bootstrap.servers': 'kafka-1:9092',
    'enable.idempotence': True,
    'transactional.id': 'eva-sensor-txn-1',
}

producer = Producer(producer_conf)
producer.init_transactions()

try:
    producer.begin_transaction()
    producer.produce('sensors-raw', key=b'M-001', value=b'...')
    producer.produce('sensors-audit', key=b'M-001', value=b'...')
    producer.commit_transaction()
except Exception:
    producer.abort_transaction()
```

### 9.2 Retry Pattern

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  sensors-raw │───▶│  retry-0     │───▶│  retry-1     │───▶ DLQ
│  (principal) │    │  (5s delay)  │    │  (60s delay) │
└──────────────┘    └──────────────┘    └──────────────┘
```

### 9.3 Compacted Topics (Dernière Valeur par Clé)

```bash
# Rétention = compact uniquement
bin/kafka-topics.sh --bootstrap-server localhost:9092 \
    --create --topic machine-state \
    --config cleanup.policy=compact \
    --config min.cleanable.dirty.ratio=0.5 \
    --config delete.retention.ms=100
```

---

## Pièges Courants (Pitfalls)

1. **Rebalancement fréquent des consumers.**  
   - *Erreur :* `session.timeout.ms` trop bas ou `max.poll.interval.ms` trop court → le consumer est exclu du groupe.  
   - *Correction :* Augmenter `session.timeout.ms` (45s-60s) et `max.poll.interval.ms` (5min+). Vérifier le temps de traitement des messages.

2. **Messages dupliqués sans idempotence.**  
   - *Erreur :* Le producer retente un message après timeout réseau, et Kafka l'accepte deux fois.  
   - *Correction :* Toujours activer `enable.idempotence=true` sur le producer.

3. **Topics sans réplication (RF=1).**  
   - *Erreur :* Un broker tombe → perte totale de données.  
   - *Correction :* `default.replication.factor=3` et `min.insync.replicas=2`.

4. **Ordre des messages non garanti.**  
   - *Erreur :* Plusieurs partitions sans clé → ordre non préservé entre partitions.  
   - *Correction :* Utiliser une clé pour garantir l'ordre par entité (ex : machine_id). Une seule partition peut aussi garantir l'ordre global, mais limite le débit.

5. **Lag de consommation non surveillé.**  
   - *Erreur :* Le consumer lag augmente silencieusement jusqu'à dépasser la rétention → perte de messages.  
   - *Correction :* Déployer Burrow ou Kafka Lag Exporter, alerting Prometheus.

6. **Évolution de schéma sans compatibilité.**  
   - *Erreur :* Ajout d'un champ requis → les consumers anciens crash.  
   - *Correction :* Toujours définir `default` pour les nouveaux champs. Respecter la règle de compatibilité (BACKWARD par défaut).

---

## Liste de Vérification (Checklist)

- [ ] KRaft configuré (plus de ZooKeeper).
- [ ] `enable.idempotence=true` sur tous les producers.
- [ ] `replication.factor >= 3` pour les topics critiques.
- [ ] `min.insync.replicas=2` pour garantir la durabilité.
- [ ] Schema Registry déployé (Avro/Protobuf/JSON Schema).
- [ ] Dead Letter Topic configuré pour les échecs de traitement.
- [ ] Burrow ou équivalent pour le monitoring de lag.
- [ ] Cruise Control pour le rebalancement automatique.
- [ ] Kafka Connect pour l'intégration source/sink.
- [ ] Transactions configurées pour exactly-once multi-topic.