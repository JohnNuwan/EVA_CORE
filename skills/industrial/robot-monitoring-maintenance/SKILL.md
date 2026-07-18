---
name: robot-monitoring-maintenance
description: "Use when monitoring industrial robots through PLC interfaces, cell states, fault tracking, cycle metrics, and maintenance-oriented dashboards."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [robotics, monitoring, maintenance, plc, handshake, dashboard, diagnostics]
    related_skills: [robot-plc-standard-interface, industrial-monitoring-stack, robotics-abb, robotics-fanuc, robotics-kuka, robotics-staubli]
---

# Monitoring maintenance pour cellules robotisées

## Vue d'ensemble

Cette compétence couvre le monitoring utile des robots industriels dans un contexte de maintenance, d'exploitation et de diagnostic. Le principe directeur est simple : on ne cherche pas seulement à savoir qu'un robot existe, mais à savoir s'il est prêt, bloqué, en défaut, en sécurité, ralenti ou source de pertes de cadence.

Le monitoring robot le plus robuste passe souvent par l'interface standard robot ↔ PLC, complétée au besoin par des données du contrôleur robot, du variateur ou du SCADA.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- de surveiller une cellule robotisée ;
- de diagnostiquer des blocages robot ↔ PLC ;
- de construire un dashboard maintenance robot ;
- de standardiser les états et défauts robots entre marques ;
- de suivre des temps de cycle, défauts et pertes de disponibilité d'un robot.

Ne pas utiliser pour :
- la seule programmation trajectoire d'un robot sans sujet monitoring ;
- une simple table de bits sans vision maintenance / diagnostic ;
- une étude purement sécurité sans exploitation des états de cellule.

## 1. Signaux minimum à surveiller

### États robot vers PLC
- `Ready`
- `Busy`
- `Fault`
- `CycleDone`
- `AtHome`
- `InAuto`
- `InTeach` ou `InManual`
- `ResetRequired`

### Sécurité / permissifs
- `FenceClosed`
- `EStopOk`
- `RobotSafe`
- `GuardResetRequired`

### Diagnostic utile
- code défaut robot ;
- catégorie défaut ;
- programme actif ;
- recette / format ;
- temps de cycle robot ;
- temps d'attente avant départ ;
- nombre de reprises / resets ;
- temps depuis dernier cycle complet.

## 2. Questions auxquelles le monitoring doit répondre

- Le robot est-il prêt mais jamais démarré ?
- Le robot part-il mais ne termine-t-il pas ?
- Le PLC attend-il le robot ou l'inverse ?
- Le défaut est-il robot, sécurité, préhenseur, périphérique ou process ?
- La cadence se dégrade-t-elle ?
- Le nombre de resets augmente-t-il ?
- Les blocages sont-ils concentrés sur une recette ou un mode ?

## 3. Table de bord minimum robot

### Vue instantanée cellule
- état robot ;
- mode ;
- statut sécurité ;
- défaut actif ;
- temps de cycle courant ;
- commande en attente.

### Vue maintenance
- derniers codes défauts ;
- top défauts sur période ;
- durée cumulée des blocages ;
- temps moyen avant défaut ;
- temps moyen de reprise ;
- chronologie `Ready/Busy/Fault/CycleDone`.

### Vue performance
- cycles / heure ;
- temps d'attente robot ;
- temps d'attente PLC / périphériques ;
- taux de cycle incomplet ;
- temps moyen de retour Home.

## 4. Architecture de collecte recommandée

### Niveau standard
- suivre les états robots via le PLC ;
- historiser les transitions d'états ;
- historiser les défauts et acquittements ;
- relier les temps de cycle à la machine ou ligne.

### Niveau avancé
- ajouter données natives du contrôleur robot si disponibles ;
- suivre les sous-ensembles critiques : pince, vision, changeur outil, convoyeurs associés ;
- corréler défauts robot avec qualité communication et permissifs safety.

## 5. Indicateurs robot particulièrement utiles

- taux de disponibilité robot ;
- temps moyen d'attente de départ ;
- temps moyen de cycle ;
- nombre de défauts / heure ;
- durée moyenne de blocage ;
- nombre de resets ;
- pourcentage de cycles terminés sans reprise ;
- part des arrêts causés par robot vs périphérique vs PLC.

## 6. Standardisation multi-marques

Quelle que soit la marque, exposer un contrat externe homogène :
- `Ready`
- `Busy`
- `Fault`
- `CycleDone`
- `AtHome`
- `InAuto`
- `InTeach`
- `ResetRequired`
- `FaultCode`
- `ProgramId`
- `CycleTime`

Le détail propriétaire ABB/Fanuc/KUKA/Stäubli peut rester interne, mais la couche monitoring transverse doit rester stable.

## Support files

- `templates/robot-monitoring-tag-list-template.md` : registre type des points robot à suivre.
- `references/robot-diagnostic-scenarios.md` : scénarios types de blocage, attente, défauts répétés et sous-performance robot.

## Pièges Courants (Common Pitfalls)

1. **Surveiller seulement le bit Fault.**
   Corriger en historisant aussi `Ready`, `Busy`, `CycleDone`, modes et temps de cycle.

2. **Ne pas distinguer attente robot et attente PLC.**
   Corriger avec une chronologie explicite du handshake.

3. **Mélanger signaux safety et signaux process.**
   Corriger en séparant `Safe`, `Sts` et `Alm`.

4. **Faire un dashboard dépendant d'une seule marque.**
   Corriger avec un contrat externe multi-constructeurs.

5. **Ne pas historiser les resets.**
   Corriger car les resets répétés sont souvent un très bon indicateur de dégradation cachée.

## Liste de vérification (Checklist)

- [ ] Les états robot minimum sont suivis.
- [ ] Les défauts, resets et temps de cycle sont historisés.
- [ ] Le dashboard distingue exploitation, maintenance et performance.
- [ ] Le handshake robot ↔ PLC est exploitable en chronologie.
- [ ] Le contrat externe est réutilisable entre marques.
