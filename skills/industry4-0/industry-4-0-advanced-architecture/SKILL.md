---
name: industry-4-0-advanced-architecture
description: "Concevoir et implémenter des architectures avancées Industrie 4.0 : IoT industriel, jumeaux numériques, MES/ERP intégrés et maintenance prédictive."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [industry40, iot, digital-twin, mes, erp, smart-factory, automation, architecture]
    related_skills: [industry4-workflows-pipelines, interoperability-of-industrial-systems, industrial-communication-protocols]
---

# Architectures Avancées de l'Industrie 4.0

## Vue d'ensemble

Cette compétence décrit les **architectures modernes de l'Industrie 4.0**, couvrant l'intégration de l'IoT industriel, des jumeaux numériques, des systèmes MES/ERP, de la maintenance prédictive et de l'automatisation connectée. Elle fournit une méthodologie pour concevoir une usine connectée de bout en bout, de la couche capteur jusqu'à la prise de décision stratégique.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir l'architecture IT/OT d'une usine connectée (greenfield ou retrofit).
- D'intégrer des capteurs IoT avec un MES et un ERP existants.
- De déployer un jumeau numérique pour de la simulation ou de la surveillance.
- D'implémenter une solution de maintenance prédictive basée sur les données capteurs.
- De cartographier les flux de données entre les différents niveaux de l'automatisation (ISA-95).

---

## 1. Architecture de Référence (Pyramide ISA-95 Étendue)

### 1.1 Niveaux de la Pyramide Connectée

| Niveau | Couche | Composants | Protocoles |
|:---|:---|:---|:---|
| **Niveau 5** | Cloud / Big Data | AWS IoT, Azure, Google Cloud, Databricks | HTTPS, MQTTS, gRPC |
| **Niveau 4** | ERP / PLM / BI | SAP, Oracle, Infor | SOAP, REST, SFTP |
| **Niveau 3** | MES / Historien | AVEVA, Siemens Opcenter, Ignition | OPC-UA, ODBC |
| **Niveau 2** | SCADA / Supervision | WinCC, Citect, ClearSCADA | OPC-DA, OPC-UA |
| **Niveau 1** | Automates (PLC/RTU) | Siemens, Rockwell, Schneider | Profinet, Modbus, Ethernet/IP |
| **Niveau 0** | Capteurs / Actionneurs | IoT, RFID, Vannes, Motoréducteurs | Modbus RTU, IO-Link, 4-20mA |

### 1.2 Schéma d'Architecture Connectée

```
[Niveau 4-5] Cloud / ERP
     ↑ REST / MQTTS ↓
[Niveau 3] MES / Historien ――――― [Jumeau Numérique]
     ↑ OPC-UA ↓
[Niveau 2] SCADA / HMI ――――― [Tableau de Bord]
     ↑ Profinet / Modbus ↓
[Niveau 1] PLC / RTU ――――― [Edge Computing]
     ↑ IO-Link / 4-20mA ↓
[Niveau 0] Capteurs / Actionneurs
```

---

## 2. Composants Clés

### 2.1 IoT Industriel (IIoT)

```yaml
Infrastructure IIoT typique:
  Capteurs: [Température, Pression, Vibration, Débit, Courant]
  Gateway: { type: "Industrial IoT Gateway", protocole: "MQTT", edge: true }
  Broker: { type: "Mosquitto / EMQX", port: 1883, TLS: true }
  Processing: { stream: "Kafka / Flink", batch: "Spark / Airflow" }
  Storage: { time-series: "InfluxDB", historical: "MinIO / S3" }
```

**Exemple de lecture capteur avec Python :**

```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(f"Capteur {data['sensor_id']}: {data['value']}{data['unit']}")
    # Envoi vers InfluxDB ou Kafka

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.actemium.local", 1883, 60)
client.subscribe("factory/line1/sensors/#")
client.loop_forever()
```

### 2.2 Jumeau Numérique (Digital Twin)

Un jumeau numérique est une **réplique virtuelle** d'un système physique qui s'enrichit des données temps réel.

| Type | Usage | Technologie |
|:---|:---|:---|
| **Jumeau de produit** | Simulation du comportement avant fabrication | Ansys, Simcenter |
| **Jumeau de production** | Optimisation de ligne en temps réel | Tecnomatix, Visual Components |
| **Jumeau de performance** | Prédiction de défaillance | Python + ML (LSTM, Prophet) |

### 2.3 MES (Manufacturing Execution System)

| Fonction MES | Données d'entrée | Sortie / Décision |
|:---|:---|:---|
| Gestion d'ordres de fabrication | ERP → MES | Affectation des ressources |
| Traçabilité | Codes-barres, RFID | Historique complet de production |
| Contrôle qualité | Mesures (SPC) | Alertes dérive (Cp, Cpk) |
| Performance | TRS, OEE | Tableau de bord temps réel |
| Gestion des rebuts | Quantités rebutées | Pareto des causes |

---

## 3. Mise en Œuvre

### 3.1 Étapes de Transformation Digitale

1. **Audit de l'existant** : Inventaire des équipements, protocoles, systèmes d'information.
2. **Définition de l'architecture cible** : Choix des technologies et de leur intégration.
3. **Déploiement de l'infrastructure** : Réseau, capteurs, gateways, serveurs.
4. **Intégration des systèmes** : MES ↔ ERP, MES ↔ PLC, Historien ↔ SCADA.
5. **Développement des applications** : Jumeau numérique, maintenance prédictive, dashboard.
6. **Mise en production et monitoring** : Validation, formation, suivi des KPI.

### 3.2 Exemple : Pipeline de Maintenance Prédictive

```python
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from influxdb import InfluxDBClient

# 1. Récupération des données temps réel
client = InfluxDBClient(host="localhost", database="factory_metrics")
results = client.query("SELECT * FROM vibration WHERE time > now() - 7d")

# 2. Feature engineering
df = pd.DataFrame(results.get_points())
features = np.column_stack([
    df["vibration_rms"],
    df["temperature"],
    df["rpm"],
    df["hours_since_maintenance"],
])

# 3. Prédiction de la durée de vie restante (RUL)
model = RandomForestRegressor(n_estimators=200)
model.fit(features_train, rul_train)
rul_pred = model.predict(features[-1:])
print(f"RUL estimée : {rul_pred[0]:.0f} heures")
```

---

## 4. Pièges Courants

1. **Surcharge de données (Data Lake devenu Data Swamp) :**
   - *Erreur* : Collecter toutes les données sans filtre ni structure.
   - *Correction* : Définissez des data governance rules : quoi collecter, à quelle fréquence, pour quel usage.

2. **Latence non maîtrisée de bout en bout :**
   - *Erreur* : Données PLC → Cloud → Décision avec 5s de latence, inacceptable pour un arrêt d'urgence.
   - *Correction* : Implémentez un edge computing pour les décisions temps réel (< 100ms), et cloud pour l'analytique différée.

3. **Silos entre IT et OT :**
   - *Erreur* : L'équipe IT gère le réseau, l'équipe OT gère les PLC, aucune coordination.
   - *Correction* : Mettez en place une équipe IT/OT convergée avec des objectifs communs et des processus de changement partagés.

---

## Liste de vérification

- [ ] La pyramide ISA-95 est cartographiée avec les systèmes réels de l'usine.
- [ ] Les protocoles de communication entre niveaux sont définis (OPC-UA, MQTT, Modbus, etc.).
- [ ] Un edge computing est prévu pour les décisions temps réel.
- [ ] Le MES est interfacé avec l'ERP (ordres, stocks, traçabilité).
- [ ] Un jumeau numérique est déployé pour au moins un processus critique.
- [ ] La maintenance prédictive est en place sur des équipements rotatifs (moteurs, pompes, ventilateurs).
- [ ] Un dashboard de supervision (OEE, TRS, alertes) est accessible aux opérateurs.
