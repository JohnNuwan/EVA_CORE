---
name: industry4-workflows-pipelines
description: "Concevoir, modéliser et optimiser des pipelines de workflows industriels pour l'Industrie 4.0, de la donnée capteur à la prise de décision automatisée."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [industry40, workflows, pipelines, bpmn, orchestration, kafka, airflow, iot]
    related_skills: [industry-4-0-advanced-architecture, industry50-and-sustainability, industrial-communication-protocols]
---

# Pipelines de Workflows Industrie 4.0

## Vue d'ensemble

Cette compétence fournit une méthodologie complète pour **concevoir, orchestrer et optimiser** des pipelines de workflows en environnement Industrie 4.0. Elle couvre l'ensemble de la chaîne : de l'acquisition de données depuis les capteurs et automates jusqu'à la prise de décision automatisée, en passant par le traitement en temps réel et le stockage.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'automatiser un flux de production avec des données IoT temps réel.
- De concevoir une architecture de pipeline de données industriel (Kafka, Node-RED, Airflow).
- D'optimiser un workflow MES ou SCADA existant.
- De modéliser un processus industriel avec BPMN et de l'intégrer à un système d'orchestration.
- De créer un jumeau numérique connecté à des flux de données en continu.

---

## 1. Architecture d'un Pipeline Industriel 4.0

### 1.1 Couches Fondamentales

| Couche | Composants | Technologie |
|:---|:---|:---|
| **Acquisition** | Capteurs, PLC, RFID, IoT Gateways | MQTT, OPC-UA, Modbus |
| **Transport** | File de messages, streaming | Apache Kafka, RabbitMQ, NATS |
| **Traitement** | Transformation, agrégation, filtrage | Node-RED, Apache Flink, ksqlDB |
| **Stockage** | Base temps réel, historique, lac de données | InfluxDB, TimescaleDB, MinIO |
| **Orchestration** | Enchaînement, supervision, alertes | Apache Airflow, Prefect, n8n |
| **Décision** | Analyse, ML, dashboard | Jupyter, Grafana, MLflow |

### 1.2 Flux de Données Typique

```
[Capteurs/PLC] → MQTT Broker → [Kafka]
                                   ↓
[Node-RED] → Transformation → [Base Temps Réel]
                                   ↓
[Airflow] → Orchestration Pipeline → [Stockage Historique]
                                   ↓
[Dashboard Grafana / Décision Automatisée]
```

---

## 2. Mise en Œuvre des Pipelines

### 2.1 Acquisition avec MQTT et Node-RED

**Configuration du broker MQTT (Mosquitto) :**

```bash
# Installation
sudo apt install mosquitto mosquitto-clients  # Linux
# ou avec Docker
docker run -d -p 1883:1883 --name mqtt eclipse-mosquitto
```

**Flux Node-RED typique pour ingestion de données PLC :**

```json
[{"id":"plc-input","type":"mqtt in","topic":"factory/line1/sensors","qos":2,"broker":"localhost:1883"},
 {"id":"transform","type":"function","func":"msg.payload = JSON.parse(msg.payload); return msg;"},
 {"id":"influx-out","type":"influxdb out","database":"factory_metrics","precision":"ms"}]
```

### 2.2 Orchestration avec Apache Airflow

**DAG industriel pour pipeline ETL temps réel :**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "EVA",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

def extract_iot_data():
    """Extraction des données de production depuis Kafka."""
    from kafka import KafkaConsumer
    consumer = KafkaConsumer("factory-sensors", bootstrap_servers="kafka:9092")
    # Logique d'extraction...
    return {"status": "extracted", "records": 1500}

def transform_quality_metrics(**context):
    """Transformation des métriques qualité."""
    # Aggrégation, nettoyage, validation...
    pass

def load_to_warehouse(**context):
    """Chargement dans le lac de données historique."""
    pass

with DAG(
    dag_id="industry40_production_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="*/5 * * * *",  # Toutes les 5 minutes
    catchup=False,
    default_args=default_args,
) as dag:
    extract = PythonOperator(task_id="extract_iot", python_callable=extract_iot_data)
    transform = PythonOperator(task_id="transform_quality", python_callable=transform_quality_metrics)
    load = PythonOperator(task_id="load_warehouse", python_callable=load_to_warehouse)

    extract >> transform >> load
```

---

## 3. Modélisation avec BPMN

Le standard **BPMN 2.0** (Business Process Model and Notation) est recommandé pour modéliser visuellement les workflows industriels.

| Élément BPMN | Usage Industriel | Exemple |
|:---|:---|:---|
| **Événement de début** | Déclencheur du processus | Réception d'une commande |
| **Tâche (Task)** | Opération unitaire | Contrôle qualité, soudure |
| **Passerelle (Gateway)** | Décision conditionnelle | Test OK → Suite / Test KO → Rebut |
| **Événement intermédiaire** | Attente ou message | Attente validation opérateur |
| **Événement de fin** | Terminaison du processus | Expédition, archivage |

---

## 4. Cas d'Usage Concrets

| Cas | Problème | Solution Pipeline |
|:---|:---|:---|
| **Maintenance prédictive** | Pannes inattendues | Capteurs → Kafka → ML (anomaly detection) → Alerte |
| **Traçabilité de production** | Lots non tracés | RFID → MQTT → Kafka → Base documentaire (traçabilité) |
| **Optimisation énergétique** | Surconsommation | Compteurs → InfluxDB → Grafana → Boucle de rétroaction |
| **Contrôle qualité automatisé** | Inspection manuelle lente | Vision → ML → Décision → SCADA |

---

## 5. Pièges Courants

1. **Saturation du bus de données :**
   - *Erreur* : Envoyer chaque variation de capteur (10 ms) sur Kafka sans filtrage.
   - *Correction* : Implémentez un deadband (seuil de variation minimum) et du batch avant publication.

2. **Désynchronisation des pipelines :**
   - *Erreur* : Un pipeline en aval reçoit des données avant que le pipeline en amont ait fini sa transformation.
   - *Correction* : Utilisez des mécanismes de watermark ou de checkpoint dans Airflow.

3. **Absence de gestion des pannes :**
   - *Erreur* : Aucun mécanisme de replay en cas de défaillance d'un composant du pipeline.
   - *Correction* : Activez les dead letter queues (DLQ) Kafka et les retries Airflow avec exponential backoff.

---

## Liste de vérification

- [ ] Les sources de données (capteurs, PLC, MES) sont identifiées et leurs débits estimés.
- [ ] Le protocole de transport (MQTT, Kafka, OPC-UA) est adapté au volume et à la latence requis.
- [ ] Un orchestrateur (Airflow, Prefect, n8n) est configuré avec des retries et alertes.
- [ ] Les pipelines sont modélisés graphiquement (BPMN ou diagramme de flux).
- [ ] La gestion des erreurs inclut dead letter queue et mécanisme de replay.
- [ ] Les métriques de performance (débit, latence, taux d'erreur) sont exposées via Grafana ou un tableau de bord équivalent.
