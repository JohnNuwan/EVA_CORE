---
name: industrial-monitoring-stack
description: "Use when designing or implementing the technical monitoring stack for PLCs, robots, historians, alerting, and industrial dashboards."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, monitoring, opc-ua, modbus, historian, dashboard, alerting, maintenance, oee]
    related_skills: [opc-ua-scanner, historian-timeseries, industrial-analytics-grafana, plc-diagnostic, industrial-protocols, oee-performance, predictive-maintenance, energy-monitoring]
---

# Stack technique de monitoring industriel

## Vue d'ensemble

Cette compétence décrit la mise en œuvre concrète d'un stack de monitoring industriel réutilisable. Elle ne se limite pas à collecter des valeurs : elle organise la chaîne complète entre équipements, collecte, historisation, calculs, visualisation, alertes et exploitation maintenance.

Elle s'applique aux environnements mêlant PLC, robots, variateurs, compteurs d'énergie, SCADA et couches IIoT. Le résultat attendu est une architecture robuste, lisible et extensible, pas une juxtaposition de scripts hétérogènes.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- de concevoir ou déployer une architecture de monitoring multi-équipements ;
- de définir quels tags lire, à quelle fréquence et pour quel usage ;
- de bâtir une chaîne PLC/robot → collecteur → historian → dashboard ;
- de structurer alertes, diagnostics et KPIs à partir des données terrain ;
- de standardiser une approche Actemium réutilisable sur plusieurs projets.

Ne pas utiliser pour :
- un seul script de test protocolaire sans architecture globale ;
- une visualisation ponctuelle sans historisation ni gouvernance de données ;
- un sujet purement MES/ERP sans composante terrain.

## 1. Architecture de référence

```text
┌───────────────┐   ┌──────────────┐   ┌─────────────────────┐   ┌──────────────────────┐
│ PLC / Robot / │   │  Collecteur  │   │ Historian / TSDB    │   │ Dashboards / Alertes │
│ Drive / Meter │──▶│ store-forward│──▶│ brut + agrégé + KPI │──▶│ maintenance / OEE    │
└───────────────┘   └──────────────┘   └─────────────────────┘   └──────────────────────┘
         │                    │                    │                         │
         └────── Diagnostics ─┴────── Cache local ┴────── API / SQL / Flux ─┘
```

### Principes d'architecture
- Le terrain reste la source de vérité des états temps réel.
- Le collecteur ne doit pas réinventer la logique machine, seulement la capter et l'enrichir légèrement.
- L'historian stocke en UTC avec stratégie de rétention explicite.
- Le dashboard sert l'opération, pas la curiosité : chaque vue doit répondre à une décision métier.

## 2. Taxonomie canonique recommandée

Toujours classer les points dans des familles stables :
- `Cmd` : commandes exposées ou surveillées
- `Sts` : états stables de machine, cellule, robot, variateur
- `Alm` : alarmes, défauts, warnings
- `Ana` : analogiques et mesures continues
- `Cnt` : compteurs, pièces, heures, cycles
- `Safe` : sécurité, permissifs, états sûrs
- `Kpi` : indicateurs calculés
- `Meta` : firmware, version, recette, mode, source

Cette taxonomie évite les registres plats illisibles et facilite la construction des dashboards et des règles d'alerte.

## 3. Stratégie d'acquisition par type de signal

| Type de signal | Méthode préférée | Fréquence typique | Usage |
|---|---|---:|---|
| États machine | subscription ou polling rapide | 250 ms à 1 s | disponibilité, séquences |
| Défauts / alarmes | événementiel ou polling court | 250 ms à 1 s | diagnostic |
| Analogiques process | polling régulier | 1 s à 10 s | tendance, régulation, dérive |
| Énergie / utilités | polling lent | 5 s à 60 s | EnPI, coût, dérive |
| Vibrations locales | acquisition dédiée | selon capteur | maintenance prédictive |
| Infos CPU / diagnostic PLC | polling lent ou à la demande | 30 s à 5 min | maintenance |
| États robot | via PLC ou API constructeur | 250 ms à 1 s | cellule robotisée |

## 4. Registre minimal des points à collecter

### PLC / machine
- état global machine ;
- mode auto / manuel / arrêt ;
- défaut général ;
- cause d'arrêt ;
- temps de cycle courant ;
- compteur pièces bonnes / rebuts ;
- permissifs critiques ;
- mesures process clés.

### Robot
- `Ready`, `Busy`, `Fault`, `CycleDone`, `AtHome`, `InAuto`, `InTeach` ;
- numéro d'alarme robot ;
- programme / recette active ;
- temps de cycle robot ;
- blocage handshake PLC ↔ robot.

### Variateur / motion
- vitesse réelle ;
- consigne ;
- état prêt / défaut ;
- courant / charge si disponible ;
- température drive ou moteur ;
- nombre de défauts / code défaut.

### Énergie / utilités
- puissance instantanée ;
- énergie cumulée ;
- intensités / tensions ;
- débit air / eau / vapeur si disponible ;
- consommation par lot ou produit si calculable.

## 5. Historisation et rétention

### Règles minimales
- stocker tous les timestamps en UTC ;
- distinguer brut court terme, agrégé moyen terme, archive long terme ;
- utiliser un cache local si la liaison vers l'historian n'est pas garantie ;
- historiser par besoin, pas par réflexe.

### Stratégie type
- brut : 7 à 30 jours ;
- agrégé minute / heure : 3 à 12 mois ;
- agrégé journalier : 1 à 5 ans.

### À historiser en priorité
- états et transitions utiles ;
- défauts et acquittements ;
- analogiques critiques ;
- compteurs de production ;
- énergie ;
- changements de mode / recette.

## 6. Dashboards minimum à fournir

### Vue maintenance
- disponibilité communication ;
- derniers défauts ;
- variables critiques hors plage ;
- santé automate / robot / drive ;
- chronologie des événements.

### Vue exploitation
- état actuel ;
- cadence ;
- temps de cycle ;
- compteurs ;
- temps d'arrêt ;
- état des utilités critiques.

### Vue performance
- OEE / TRS ;
- répartition des états ;
- top 10 défauts ;
- micro-arrêts ;
- énergie par pièce / lot.

## 7. Alertes utiles vs bruit inutile

Définir les alertes par persistance et contexte :
- température > seuil pendant N minutes ;
- défaut communication sur équipement critique ;
- CPU en surcharge persistante ;
- robot `Busy` trop longtemps sans `CycleDone` ;
- temps de cycle > nominal + tolérance pendant N cycles ;
- hausse inhabituelle des micro-arrêts ;
- consommation énergétique anormale à production constante.

Éviter les alertes sur chaque fluctuation instantanée.

## 8. Exploitation maintenance et diagnostic

Le stack doit aider à répondre vite à :
- que s'est-il passé avant l'arrêt ?
- quel équipement a décroché en premier ?
- le défaut est-il process, automate, robot, réseau, safety ou énergie ?
- la dérive est-elle brutale ou progressive ?
- le problème est-il isolé ou récurrent ?

Toujours conserver une chronologie combinant :
- état machine ;
- défaut ;
- événement robot ;
- qualité de communication ;
- mesure analogique critique.

## 9. KPI et calculs dérivés

Calculer dans la couche data ou dashboard :
- disponibilité ;
- performance ;
- qualité ;
- OEE / TRS ;
- MTBF / MTTR si les données sont suffisantes ;
- énergie / pièce ;
- temps d'attente robot ;
- fréquence des défauts ;
- taux de micro-arrêts.

## Support files

- `templates/monitoring-point-register-template.md` : registre standard des points à collecter.
- `templates/full-monitoring-point-register-template.md` : registre complet avec criticité, dashboards, alertes et KPI associés.
- `templates/alert-matrix-template.md` : matrice d'alertes et d'escalade.
- `templates/grafana-dashboard-pack-template.md` : structure standard des dashboards maintenance, robot, exploitation et OEE.
- `templates/historian-data-model-template.md` : modèle de données type pour InfluxDB ou TimescaleDB.
- `templates/plc-historian-contract-template.md` : contrat de données entre PLC et Historian.
- `templates/robot-historian-contract-template.md` : contrat de données entre cellule robot et Historian.
- `references/kpi-catalog.md` : catalogue des KPI maintenance, exploitation, robot, énergie et OEE.
- `references/alarm-governance-checklist.md` : règles de gouvernance pour des alertes actionnables et peu bruyantes.

## Pièges Courants (Common Pitfalls)

1. **Collecter tous les tags accessibles.**
   Corriger avec un registre gouverné, limité aux usages réels.

2. **Mettre toute l'intelligence dans le dashboard.**
   Corriger en stabilisant taxonomie, historisation et calculs essentiels en amont.

3. **Utiliser une seule fréquence de polling pour tout.**
   Corriger en adaptant la collecte à la dynamique physique du signal.

4. **Historiser sans stratégie de rétention.**
   Corriger avec brut, agrégé et archive.

5. **Oublier les signaux d'interface robot ↔ PLC.**
   Corriger en suivant explicitement le contrat de cellule robotisée.

6. **Déployer des alertes sans temporisation.**
   Corriger avec filtres de persistance et de criticité.

## Liste de vérification (Checklist)

- [ ] L'architecture source → collecteur → historian → dashboard est définie.
- [ ] La taxonomie des points est stabilisée.
- [ ] Le registre des points inclut source, fréquence, criticité et usage.
- [ ] La stratégie d'historisation et de rétention est définie.
- [ ] Une vue maintenance et une vue exploitation existent.
- [ ] Les alertes sont contextualisées et temporisées.
- [ ] Les signaux robot et motion sont intégrés si présents sur le périmètre.
