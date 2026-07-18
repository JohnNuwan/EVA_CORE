---
name: plc-scada-platform-standards
description: "Use when standardizing or producing expert packs across Siemens SCL, Rockwell Studio 5000, Ignition SCADA, and PLC↔SCADA integration. Creates coordinated, professional deliverables instead of isolated vendor notes."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, plc, scada, siemens, rockwell, ignition, standards, integration, fat, sat]
    related_skills: [siemens-scl, rockwell-studio5000, ignition-scada, industrial-generator]
---

# PLC / SCADA Platform Standards Packs

## Vue d'ensemble

Cette compétence sert à produire une base d'expertise structurée et réutilisable quand l'utilisateur demande de "monter le niveau" ou de créer des packs experts couvrant plusieurs plateformes industrielles à la fois. Le bon livrable n'est pas une note unique et plate, mais un ensemble coordonné de standards par plateforme plus un document d'intégration transverse.

Elle est particulièrement adaptée aux environnements Actemium où le même standard doit rester cohérent entre Siemens, Rockwell, Ignition et les interfaces PLC ↔ SCADA.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- de créer des packs experts ou standards pour plusieurs technologies industrielles en parallèle ;
- de structurer une base commune Siemens / Rockwell / Ignition ;
- de définir un contrat de tags, d'alarmes et de commandes entre PLC et SCADA ;
- de produire une documentation durable réutilisable pour conception, audit, FAT et SAT.

Ne pas utiliser pour :
- un simple snippet de code mono-plateforme ;
- une correction ponctuelle sans objectif de standardisation ;
- une note de travail d'une seule session sans valeur de réutilisation.

## Structure cible du livrable

Toujours viser 4 blocs coordonnés :
1. Pack Siemens SCL / TIA Portal
2. Pack Rockwell Studio 5000 / Logix Designer
3. Pack Ignition SCADA / Jython
4. Pack d'intégration PLC ↔ SCADA transverse

Ajouter ensuite un README de bundle sous `output/docs/guides/...` pour orienter l'exploitation du lot.

## Contenu minimal de chaque pack

### 1. Architecture
- découpage des blocs / responsabilités ;
- conventions de structuration ;
- séparation commandes, états, alarmes, analogiques.

### 2. Modèle de données
- UDT / structures équivalentes ;
- taxonomie canonique `Cmd`, `Sts`, `Alm`, `Ana`, `Meta` quand applicable ;
- variables stables à exposer au SCADA.

### 3. Patterns prêts à l'emploi
- moteur / vanne / pompe si pertinent ;
- séquenceur machine ;
- traitement analogique ;
- timeout, permissifs, défauts mémorisés.

### 4. Interface supervision
- règles d'écriture commande ;
- variables publiées au synoptique ;
- résumés d'alarmes ;
- historisation utile vs bruit inutile.

### 5. Vérification
- checklist experte ;
- scénarios FAT ;
- scénarios SAT.

## Workflow recommandé

1. Identifier les plateformes demandées.
2. Produire un document expert par plateforme, pas un mélange unique.
3. Produire un document transverse d'intégration PLC ↔ SCADA.
4. Centraliser le lot dans un bundle README sous `output/docs/guides/`.
5. Si des skills spécialisées existent déjà, s'y appuyer comme source métier, mais enregistrer les détails concrets de la session dans `references/` du présent umbrella quand ils sont réutilisables.

## Conventions de fond

- Le PLC reste la source de vérité du comportement machine temps réel.
- Le SCADA n'invente pas la logique de procédé ; il l'expose, la journalise et la rend opérable.
- Les commandes opérateur doivent toujours passer par une zone de commande dédiée.
- Les états exposés doivent être synthétiques, stables et lisibles.
- Les livrables doivent être rangés professionnellement sous `output/` quand un bundle utilisateur est demandé.

## Support files

- `references/pack-outline.md` : plan détaillé des 4 packs et contenu minimal attendu.

## Pièges Courants (Common Pitfalls)

1. **Rédiger un seul document monolithique multi-technologies.**
   Corriger en séparant les packs par plateforme puis en ajoutant un document transverse d'intégration.

2. **Confondre standard PLC et comportement HMI.**
   Garder la logique métier temps réel côté automate et réserver au SCADA l'affichage, la traçabilité et l'interaction opérateur.

3. **Documenter des tags sans taxonomie commune.**
   Stabiliser au minimum les familles `Cmd`, `Sts`, `Alm`, `Ana`, `Meta` ou leurs équivalents projet.

4. **Oublier le bundle final orienté utilisateur.**
   Toujours fournir un README de synthèse indiquant les packs créés, leur rôle et l'ordre d'exploitation.

## Liste de vérification (Checklist)

- [ ] Les 4 blocs de livrables ont été couverts ou explicitement exclus.
- [ ] Chaque pack contient architecture, patterns, interface supervision et vérification.
- [ ] Le contrat PLC ↔ SCADA est documenté séparément.
- [ ] Le bundle final est rangé sous `output/docs/guides/`.
- [ ] Les livrables sont rédigés de façon professionnelle et réutilisable.
