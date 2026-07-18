---
name: industrial-monitoring-pack
description: "Use when structuring a reusable industrial monitoring pack across PLCs, robots, historians, dashboards, diagnostics, and performance KPIs."
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [industrial, monitoring, plc, robot, opc-ua, historian, grafana, maintenance, oee]
    related_skills: [industrial-monitoring-stack, robot-monitoring-maintenance, plc-diagnostic, historian-timeseries, industrial-analytics-grafana, oee-performance]
---

# Pack Monitoring Industriel

## Vue d'ensemble

Cette compétence sert d'umbrella quand l'utilisateur ne veut pas seulement lire quelques tags, mais mettre en place une capacité de monitoring industrielle réutilisable pour automates, robots, variateurs, énergie, alarmes et KPIs de performance.

Le bon livrable n'est pas un script isolé. C'est un pack structuré comprenant :
- une couche de connectivité vers les équipements ;
- un modèle de données canonique ;
- une historisation fiable ;
- des tableaux de bord ;
- une logique d'alertes ;
- une vue maintenance / diagnostic ;
- une vue performance / OEE.

Cette skill oriente la composition du pack et s'appuie sur des skills détaillées spécialisées pour l'implémentation technique.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- de « mettre en place un monitoring industriel » pour une machine, une cellule robotisée, une ligne ou un atelier ;
- de standardiser la supervision de plusieurs PLC / robots / variateurs ;
- de créer un socle maintenance + diagnostic + optimisation ;
- de relier collecte terrain, historian, dashboard et alerting ;
- de bâtir un pack réutilisable EVA pour plusieurs projets.

Ne pas utiliser pour :
- une simple lecture ponctuelle de quelques tags sans objectif de réutilisation ;
- un dashboard unique sans stratégie de données ni diagnostic ;
- une intégration mono-protocole triviale déjà couverte par une skill spécialisée.

## Structure cible du pack

Toujours viser 7 blocs coordonnés :
1. Connectivité terrain
2. Registre des points et taxonomie canonique
3. Historisation / store & forward
4. Dashboard exploitation et maintenance
5. Alertes et règles de dérive
6. Diagnostic automate / robot / communication
7. KPIs de performance, énergie et OEE

## Découpage recommandé par niveau de maturité

### Niveau 1 — Monitoring de base
- connexion aux équipements ;
- lecture états, défauts, mesures ;
- dashboard temps réel ;
- quelques alertes critiques.

### Niveau 2 — Maintenance / diagnostic
- buffer diagnostic PLC ;
- états robot et interface robot ↔ PLC ;
- suivi qualité communication ;
- top défauts, chronologies, temps d'arrêt ;
- vues maintenance.

### Niveau 3 — Optimisation / performance
- OEE / TRS ;
- micro-arrêts ;
- temps de cycle ;
- analyses de tendance ;
- énergie ;
- détection de dérives et maintenance prédictive légère.

## Rôles des skills détaillées à mobiliser

### Noyau monitoring multi-équipements
- `industrial-monitoring-stack`
- `historian-timeseries`
- `industrial-analytics-grafana`
- `industrial-protocols`

### Diagnostic maintenance
- `plc-diagnostic`
- `opc-ua-scanner`
- `industrial-diagnostic`
- `predictive-maintenance`

### Robotique et interface cellule
- `robot-monitoring-maintenance`
- `robot-plc-standard-interface`
- `robotics-abb`
- `robotics-fanuc`
- `robotics-kuka`
- `robotics-staubli`

### Performance et exploitation
- `oee-performance`
- `energy-monitoring`
- `packml-oee-state-modeling`

## Workflow recommandé

1. Identifier les équipements et protocoles réellement disponibles.
2. Définir le périmètre métier : maintenance, diagnostic, performance, énergie, robot.
3. Construire un registre des points par criticité et fréquence de collecte.
4. Choisir les voies d'acquisition : polling, subscription, lecture événementielle.
5. Déployer l'historisation avec cache local si la liaison n'est pas garantie.
6. Concevoir deux vues minimum : maintenance / exploitation.
7. Ajouter une vue performance si le client veut de l'optimisation et du TRS.
8. Formaliser les seuils d'alertes et les procédures de réponse.

## Décisions structurantes à figer très tôt

- Quel protocole par équipement : OPC UA, Modbus TCP, EtherNet/IP, S7, ADS, MQTT ?
- Quels points sont vitaux, utiles, ou seulement « nice to have » ?
- Quelles données sont historisées en brut, agrégées ou non historisées ?
- Quels calculs vivent au plus près du terrain et lesquels vivent dans la couche data ?
- Quelle séparation entre vue opérateur, vue maintenance et vue management ?
- Quels signaux robot passent via le PLC et lesquels restent propriétaires robot ?

## Support files

- `references/pack-outline.md` : structure détaillée du pack et livrables attendus.
- `references/terrain-implementation-pack.md` : recette de déploiement terrain par protocole et constructeur.
- `references/dashboard-historian-pack.md` : blueprint historian, Grafana, vues et alertes.
- `references/monitoring-maturity-roadmap.md` : trajectoire de progression du monitoring de la simple visibilité au prédictif ciblé.
- `references/protocol-selection-matrix.md` : aide au choix entre OPC UA, S7, EtherNet/IP, ADS, Modbus TCP et interface robot ↔ PLC.
- `references/diagnostic-fault-catalog.md` : catalogue de défauts types par famille d'équipement et signaux à suivre.
- `references/probable-causes-matrix.md` : matrice symptôme → causes probables → points à vérifier.
- `references/rapid-diagnostic-tree.md` : arbre de diagnostic rapide pour distinguer défaut data, communication et métier.
- `references/reference-architectures.md` : architectures types machine simple, cellule robotisée, ligne multi-PLC, utilities et Edge/OT/IT.
- `templates/deployment-readiness-checklist.md` : checklist de préparation avant déploiement.
- `templates/machine-state-matrix-template.md` : matrice canonique des états machine.
- `templates/packml-oee-mapping-template.md` : mapping PackML vers OEE / TRS.

## Pièges Courants (Common Pitfalls)

1. **Faire un dashboard avant de définir le modèle de données.**
   Corriger en stabilisant d'abord la taxonomie des points, états et défauts.

2. **Surcharger le système avec tous les tags disponibles.**
   Corriger en classant les points par criticité, fréquence et usage réel.

3. **Mélanger exploitation temps réel et reporting long terme sans stratégie de rétention.**
   Corriger avec des niveaux brut / agrégé / archive.

4. **Ignorer l'interface robot ↔ PLC.**
   Corriger en standardisant les états `Ready`, `Busy`, `Fault`, `CycleDone`, `AtHome`, `InAuto`.

5. **Limiter le monitoring aux alarmes sans contexte de performance.**
   Corriger en ajoutant temps de cycle, états machine, micro-arrêts et OEE quand pertinent.

## Liste de vérification (Checklist)

- [ ] Les 7 blocs du pack sont couverts ou explicitement exclus.
- [ ] Les protocoles réels sont identifiés par équipement.
- [ ] Le registre des points et la criticité sont définis.
- [ ] L'historisation et la stratégie de rétention sont cadrées.
- [ ] Une vue maintenance / diagnostic existe.
- [ ] Une vue robot existe si une cellule robotisée est concernée.
- [ ] Les règles d'alerte et la gouvernance des KPIs sont documentées.
