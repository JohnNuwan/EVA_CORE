---
name: industrial-analytics-grafana
description: "Utiliser quand l'utilisateur demande de configurer, optimiser ou concevoir des tableaux de bord Grafana reliés à des bases temporelles (InfluxDB, TimescaleDB, Prometheus) pour monitorer des équipements industriels."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [grafana, influxdb, timescaledb, dashboards, industrial-analytics]
    related_skills: [industrial-databases, industrial-edge, oee-performance]
---

# Tableaux de Bord Industriels Grafana & Bases Temporelles

## Vue d'ensemble

L'analyse de données industrielles requiert la visualisation historique de milliers de capteurs (températures, pressions, états, vibrations). **Grafana** s'est imposé comme l'outil standard pour concevoir des tableaux de bord dynamiques et performants, connectés à des bases de données de séries temporelles (TSDB) comme **InfluxDB**, **TimescaleDB** (extension PostgreSQL) ou **Prometheus**.

Les visualisations industrielles clés incluent :
- **Les courbes de tendance (Trends) :** Analyse comparative de capteurs sur plusieurs périodes.
- **Les diagrammes de Gantt (State Timeline) :** Suivi chronologique des états machine (Production, Panne, Attente).
- **Les jauges physiques :** Indicateurs instantanés pour les opérateurs.
- **Les rapports de synthèses périodiques (tableaux de données).**

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire ou d'optimiser des requêtes de séries temporelles (InfluxQL, Flux, PostgreSQL/TimescaleDB SQL) pour Grafana.
- De configurer des variables dynamiques dans Grafana (filtrage par équipement, usine, ligne).
- D'implémenter des alertes intelligentes dans Grafana (dérive thermique, dépassement de seuil critique).
- De structurer des requêtes d'agrégation temporelle (moyennes horaires, totaux journaliers) pour éviter de saturer l'affichage.

**Ne pas utiliser pour :**
- Les requêtes SQL transactionnelles classiques sans notion d'historisation temporelle.

---

## 1. Requêtes Temporelles Optimsées pour Grafana

Pour afficher des millions de points dans Grafana sans faire planter le navigateur, les requêtes doivent impérativement regrouper les données par intervalles temporels dynamiques en utilisant la variable Grafana `$__interval`.

### Exemple de requête TimescaleDB (SQL) :
```sql
SELECT
  -- $__timeGroup hérite de l'intervalle d'affichage de Grafana
  $__timeGroup(timestamp, $__interval) AS "time",
  -- Agrégation des valeurs physiques pour l'intervalle choisi
  AVG(temperature_celsius) AS "Température Moyenne",
  MAX(temperature_celsius) AS "Température Max"
FROM process_telemetry
WHERE
  -- Filtrage sur la plage temporelle sélectionnée par l'opérateur
  timestamp BETWEEN $__timeFrom() AND $__timeTo()
  AND sensor_id = '$sensor_variable' -- Utilisation d'une variable dynamique
GROUP BY 1
ORDER BY 1;
```

### Exemple de requête InfluxDB (Flux) :
```flux
from(bucket: "factory_telemetry")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "sensor_data")
  |> filter(fn: (r) => r["_field"] == "pressure_bar")
  |> filter(fn: (r) => r["equipment_id"] == "${equipment_variable}")
  -- Agrégation dynamique selon le zoom temporel de Grafana
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "pression_moyenne")
```

---

## 2. Configuration d'Alertes Grafana (Alerting)

Dans un contexte industriel, les alertes évitent les pannes machines. Grafana permet d'évaluer une expression d'alerte et de la notifier (via Teams, Slack, Email, webhook).

### Règle d'alerte type :
1. **Requête (A) :** Récupérer la moyenne de température des moteurs sur 5 minutes.
2. **Expression de réduction (B) :** Réduire la série temporelle en une valeur unique (ex: maximum de la période).
3. **Condition (C) :** Déclencher si la valeur réduite de `B` est supérieure à `80` (Seuil de surchauffe en °C) pendant plus de 2 minutes.

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Requêtes sans agrégation sur de longues périodes (Out of Memory) :**
    *   *Erreur :* Demander à Grafana de charger les valeurs brutes d'une température enregistrée toutes les 100 ms sur une période de 1 an. La requête renvoie des millions de lignes, sature la mémoire du serveur de base de données et fige le navigateur de l'opérateur.
    *   *Correction :* Toujours utiliser les fonctions d'agrégation (`AVG`, `MAX`, `aggregateWindow`) combinées avec l'intervalle dynamique `$__interval` ou `v.windowPeriod` de Grafana.
2.  **Hardcoding des identifiants d'équipements :**
    *   *Erreur :* Créer un tableau de bord par machine avec des requêtes pointant vers un ID figé (`sensor_id = 42`). Cela multiplie le travail de maintenance si de nouvelles machines sont installées.
    *   *Correction :* Utiliser des variables Grafana de type *Query* (ex: `SELECT distinct sensor_id FROM telemetry`) pour créer des menus déroulants dynamiques en haut du tableau de bord.

---

## Liste de vérification (Checklist)

- [ ] Toutes les requêtes de séries temporelles utilisent les variables de temps dynamiques de Grafana (`$__timeFrom()`, `$__timeTo()` ou `range(start: v.timeRangeStart)`).
- [ ] L'agrégation temporelle est active et proportionnelle au zoom d'affichage (`$__interval` ou `v.windowPeriod`).
- [ ] Les tableaux de bord utilisent des variables dynamiques pour permettre de basculer facilement d'un équipement ou d'une ligne à l'autre.
- [ ] Les seuils d'alerte configurés possèdent des temporisations (ex: "pendant plus de 5 minutes") pour éviter les fausses alertes sur des pics de démarrage transitoires.

