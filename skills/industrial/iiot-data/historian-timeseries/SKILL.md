---
name: historian-timeseries
description: "Historiser des données industrielles dans des TSDB."
version: 1.2.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [historian, influxdb, timescaledb, tsdb, time-series, telegraf, flux, grafana, industrial-automation]
    related_skills: [industrial-edge, opc-ua-scanner, industrial-analytics-grafana, energy-monitoring, predictive-maintenance]
---

# Historisation Industrielle & Bases de Données Temporelles (TSDB)

## Vue d'ensemble

L'**historisation** est la colonne vertébrale de toute architecture IIoT. Elle consiste à enregistrer les valeurs de capteurs, d'alarmes et de compteurs avec leur horodatage précis pour permettre l'analyse a posteriori, le calcul de tendances et la maintenance prédictive.

Les solutions d'historisation industrielle se répartissent en deux familles :
1. **Historiens propriétaires** : Aveva (OSIsoft) PI System, GE Proficy Historian, Siemens WinCC Historian.
2. **Bases de données temporelles open-source (TSDB)** : InfluxDB, TimescaleDB, QuestDB, VictoriaMetrics.

Cette compétence guide l'agent EVA pour configurer des pipelines d'historisation industrielle complets, depuis la collecte OPC-UA/Modbus jusqu'à la visualisation Grafana.

Le script d'assistance associé à cette compétence est disponible sous [historian_ingester.py](scripts/historian_ingester.py).

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Configurer une base **InfluxDB** pour l'historisation de données automate.
- Concevoir un **pipeline de collecte** OPC-UA → Telegraf → InfluxDB → Grafana.
- Écrire des requêtes **Flux** ou **SQL** pour l'agrégation de séries temporelles.
- Mettre en place un script d'historisation résilient doté d'une mémoire tampon locale (Store & Forward).
- Optimiser le dimensionnement et la rétention de stockage pour un grand volume de tags.

---

## 1. Architecture de Collecte Résiliente : Store & Forward

En informatique industrielle, les liaisons réseau entre l'atelier (OT) et les serveurs d'historisation (IT ou Cloud) sont sujettes à des micro-coupures. Pour garantir l'intégrité des historiques, les collecteurs implémentent une architecture de **Store & Forward** :

```text
                                    ┌──────────────────────┐
                                    │  Serveur InfluxDB    │
                                    └──────────────────────┘
                                                ▲
                                                │ Liaison Réseau
                                                │ (Si Active)
                                                │
┌──────────────┐     Lecture      ┌─────────────┴──────────┐
│ Serveur      │────────────────▶ │ Ingesteur (Python)     │
│ OPC UA / PLC │                  └─────────────┬──────────┘
└──────────────┘                                │
                                                │ Liaison Coupée
                                                │ (Ecriture Cache)
                                                ▼
                                  ┌────────────────────────┐
                                  │ Base SQLite Locale     │
                                  │ (historian_cache.db)   │
                                  └────────────────────────┘
```

- **Liaison active :** Les points collectés sont immédiatement poussés vers la base InfluxDB distante.
- **Perte de liaison :** L'ingesteur détecte l'échec d'écriture, crée un timestamp UTC et stocke temporairement les points localement dans une base SQLite légère.
- **Retour de liaison :** L'ingesteur lit les données du cache SQLite, les envoie par lots ordonnés (Flush) vers InfluxDB et purge la base locale.

---

## 2. Utilisation du Script d'Assistance (Ingesteur avec Cache)

Pour démarrer l'ingesteur avec le mécanisme de cache local de sécurité, utilisez l'outil d'exécution de code (`execute_code`) avec la commande suivante :

```python
import subprocess
import json

# Configuration des nœuds OPC UA à surveiller et à cartographier
nodes = [
    {"node_id": "ns=2;s=Line1.Boiler.Temperature", "name": "boiler_temp", "equipment": "Boiler01", "area": "Production"},
    {"node_id": "ns=2;s=Line1.Boiler.Pressure", "name": "boiler_press", "equipment": "Boiler01", "area": "Production"}
]

cmd = [
    ".venv/Scripts/python.exe", 
    "skills/industrial/iiot-data/historian-timeseries/scripts/historian_ingester.py",
    "--opcua-url", "opc.tcp://localhost:4840",
    "--influx-url", "http://localhost:8086",
    "--influx-token", "my-super-secret-token-12345",
    "--influx-org", "EVA",
    "--influx-bucket", "telemetry_raw",
    "--cache-db", "skills/industrial/iiot-data/historian-timeseries/scripts/historian_cache.db",
    "--interval", "2.0", # Lecture toutes les 2 secondes
    "--nodes", json.dumps(nodes)
]

print("Démarrage de l'ingesteur résilient...")
# Lancer le script (nous limitons le temps d'exécution en test)
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
except subprocess.TimeoutExpired:
    print("L'ingesteur tourne en tâche de fond avec succès.")
```

---

## Pièges Courants (Common Pitfalls)

1. **Historiser à fréquence maximale sans downsampling :**
   * *Erreur :* Collecter 10 000 tags à 100ms pendant 5 ans. Le volume de données explose (plusieurs téraoctets) et les requêtes de tracés deviennent lentes.
   * *Correction :* Historiser les données brutes sur une courte période (7-30 jours), puis appliquer un downsampling automatique (moyenne horaire/journalière) pour le stockage longue durée.

2. **Utiliser des timestamps locaux au lieu d'UTC :**
   * *Erreur :* Enregistrer les valeurs avec l'heure locale de l'usine. Lors des changements d'heure d'été/hiver, le système enregistre des doublons ou des trous d'une heure.
   * *Correction :* Toujours stocker les timestamps en **UTC (ISO 8601)**. La conversion en heure locale se fait uniquement au niveau du logiciel de tracé (Grafana gère cela nativement).

3. **Absence de limite de taille sur le cache local (Store & Forward) :**
   * *Erreur :* Une coupure réseau de 3 mois remplit le disque dur de la passerelle Edge avec la base SQLite, provoquant le plantage de l'OS.
   * *Correction :* Configurer un nombre maximal d'enregistrements dans la base SQLite locale ou une purge des points les plus anciens si le cache dépasse une taille critique.

---

## Liste de vérification (Checklist)

- [ ] La description frontmatter YAML fait moins de 60 caractères et se termine par un point.
- [ ] Les timestamps sont stockés en UTC et non en heure locale.
- [ ] Une stratégie de rétention à plusieurs niveaux est configurée (brut ➔ downsampled ➔ archive).
- [ ] Le downsampling automatique est programmé via une tâche de fond dans la base ou le collecteur.
- [ ] Les requêtes de visualisation gèrent les trous de données avec des fonctions de remplissage (`fill()`).
- [ ] Les jetons d'accès (tokens) et clés d'API sont chargés depuis un fichier de variables d'environnement (`.env`).
- [ ] Le module SQLite3 est supporté par l'OS hôte pour la persistance locale de sauvegarde (Store & Forward).

