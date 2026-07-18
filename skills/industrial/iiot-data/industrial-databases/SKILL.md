---
name: industrial-databases
description: "Utiliser quand l'utilisateur demande d'historiser des données d'automates, de concevoir des bases de données de production ou d'optimiser des requêtes SQL/InfluxQL industrielles."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [sql, postgresql, influxdb, time-series, trs, oee, scada, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Bases de Données Industrielles (SQL & Séries Temporelles)

## Vue d'ensemble

Le stockage des données est crucial pour la traçabilité, l'analyse qualité, et l'affichage des tableaux de bord industriels. Les environnements industriels (MES, SCADA) utilisent deux grands types de bases de données :
1. **Les bases relationnelles (SQL : PostgreSQL, SQL Server, MySQL) :** Pour les recettes de fabrication, les configurations d'équipements, la traçabilité des lots et les journaux d'alarmes.
2. **Les bases de séries temporelles (NoSQL : InfluxDB, TimescaleDB) :** Conçues pour l'enregistrement à haute fréquence des données de capteurs (télémesures).

Cette compétence guide l'agent EVA pour concevoir des schémas de base de données performants et des requêtes optimisées pour l'informatique industrielle.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir une table pour enregistrer les mesures d'un automate (Tags Historian).
- D'écrire des requêtes SQL pour calculer le Taux de Rendement Synthétique (TRS / OEE).
- D'intégrer des scripts Python pour écrire des points de données dans InfluxDB.
- D'optimiser des requêtes SQL lentes sur des tables contenant des millions d'enregistrements temporels.

**Ne pas utiliser pour :**
- Des tâches d'administration système de serveurs de bases de données (sauvegardes, clusters) hors du contexte applicatif industriel.

---

## 1. Schéma SQL de Standard d'Historisation (Tag Historian)

Pour stocker efficacement des valeurs de tags d'automates sans dupliquer les métadonnées, toujours séparer les définitions de tags des valeurs mesurées (relation 1-N) :

```sql
-- Table des métadonnées des tags
CREATE TABLE cfg_tags (
    tag_id SERIAL PRIMARY KEY,
    tag_path VARCHAR(255) UNIQUE NOT NULL, -- ex: '[default]Zone1/Motor1/Speed'
    description VARCHAR(255),
    unit VARCHAR(20)
);

-- Table des mesures (données historiques de type float)
CREATE TABLE history_float (
    tag_id INT REFERENCES cfg_tags(tag_id),
    t_stamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    val_value DOUBLE PRECISION NOT NULL,
    quality_code INT NOT NULL, -- ex: 192 pour "GOOD" (standard OPC)
    PRIMARY KEY (tag_id, t_stamp)
);

-- Index pour accélérer les requêtes temporelles
CREATE INDEX idx_history_time ON history_float (t_stamp DESC);
```

---

## 2. Calculs de KPI Industriels (TRS / OEE)

Le calcul du TRS nécessite d'agréger le temps de fonctionnement, les cadences de production et les rebuts. Voici une requête SQL type pour calculer les indicateurs d'un lot de production :

```sql
SELECT 
    lot_number,
    -- Temps de fonctionnement total en minutes
    SUM(duration_minutes) AS total_duration,
    
    -- Quantité totale produite (bonnes + rebuts)
    SUM(qty_good + qty_scrap) AS total_produced,
    
    -- Taux de Qualité = Produits Bons / Produits Totaux
    CASE 
        WHEN SUM(qty_good + qty_scrap) > 0 
        THEN (SUM(qty_good)::float / SUM(qty_good + qty_scrap)::float) * 100 
        ELSE 0 
    END AS quality_rate,
    
    -- Taux de Performance = Quantité Produite / Cadence Théorique attendue
    -- (Supposons une cadence cible de 10 pièces par minute)
    CASE 
        WHEN SUM(duration_minutes) > 0 
        THEN (SUM(qty_good + qty_scrap)::float / (SUM(duration_minutes) * 10.0)) * 100 
        ELSE 0 
    END AS performance_rate

FROM batch_production_logs
WHERE start_time >= '2026-06-01 00:00:00'
GROUP BY lot_number;
```

---

## 3. Écriture dans InfluxDB avec Python

Pour de la télémétrie haute fréquence, InfluxDB est idéal. Exemple d'écriture asynchrone de valeurs depuis Python :

```python
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "mon_super_token_de_securite"
org = "EVA"
bucket = "Telemetrie_Atelier1"

with InfluxDBClient(url="http://192.168.1.210:8086", token=token, org=org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    # Création d'un point de données
    point = Point("mesures_moteurs") \
        .tag("moteur_id", "Moteur_01") \
        .field("vitesse", 1450.5) \
        .field("temperature", 42.8) \
        .time(datetime.utcnow(), WritePrecision.NS)
        
    # Écriture dans le bucket
    write_api.write(bucket=bucket, org=org, record=point)
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Absence d'indexation sur la colonne temps :**
   * *Erreur :* Faire des recherches ou des tris sur des tables d'historique de plusieurs millions de lignes sans index sur la colonne `t_stamp` ou `timestamp`. Les requêtes mettent plusieurs minutes à s'exécuter et surchargent la base.
   * *Correction :* Toujours créer un index composite `(tag_id, t_stamp DESC)` ou utiliser une base partitionnée comme TimescaleDB.

2. **Écritures SQL ligne par ligne (N+1 queries) :**
   * *Erreur :* Écrire les valeurs de 1000 capteurs en faisant 1000 requêtes `INSERT` individuelles.
   * *Correction :* Utiliser des insertions groupées (Bulk Insert) avec SQL (`INSERT INTO ... VALUES (...), (...), ...`) ou l'API de batch InfluxDB.

---

## Liste de vérification (Checklist)

- [ ] Les tables contenant des enregistrements temporels possèdent un index sur la colonne de temps (`t_stamp`).
- [ ] Les requêtes de calculs (TRS, moyennes, ratios) incluent une clause `CASE` pour éviter les erreurs de division par zéro (`division by zero`).
- [ ] Les requêtes SQL utilisent des variables liées (paramétrées) pour éviter tout risque d'injection SQL.
- [ ] Les écritures de données haute fréquence sont regroupées par lots (Batching) pour soulager la base de données.

