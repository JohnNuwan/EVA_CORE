---
name: cross-vendor-plc-scada-patterns
description: "Orchestrer des livrables et des patterns transverses entre Rockwell Studio 5000, Siemens TIA Portal/SCL et Ignition SCADA."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
created_by: agent
metadata:
  tags: [industrial-automation, rockwell, siemens, ignition, scada, plc, cross-vendor, patterns]
---

# Patterns transverses PLC/SCADA multi-constructeurs

## Vue d'ensemble

Utiliser cette compétence quand l'utilisateur ne demande pas seulement du code sur un seul environnement, mais une montée en compétence, une structuration durable, ou un pack de livrables couvrant plusieurs briques parmi :
- Rockwell Studio 5000 / Structured Text / L5X
- Siemens TIA Portal / SCL / FB-FC-DB
- Ignition SCADA / Jython / tags / Named Queries

L'objectif n'est pas de répéter trois réponses séparées, mais de produire une vue cohérente du système industriel : logique automate, structures de données, conventions de nommage, échanges PLC↔SCADA, alarmes, séquenceurs, diagnostics et modèles réutilisables.

Référence utile fournie avec cette compétence : `references/rockwell-siemens-ignition-crosswalk.md`.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande par exemple :
- de « monter en compétence » sur Rockwell, Siemens, Ignition
- de standardiser plusieurs environnements d'automatisme/supervision
- de comparer les équivalents entre Studio 5000, TIA Portal et Ignition
- de construire une bibliothèque de patterns, templates ou standards projet
- de concevoir une architecture PLC + SCADA multi-constructeurs

## Démarche recommandée

1. Identifier les trois couches du besoin :
   - couche logique automate
   - couche données/tags
   - couche supervision/SCADA

2. Répondre par familles de patterns plutôt que par anecdotes :
   - démarrage/arrêt moteur
   - machine d'état / séquenceur
   - temporisation
   - analog scaling
   - alarmes et acquittement
   - commandes HMI / retours d'état
   - interverrouillages et défauts

3. Produire systématiquement un crosswalk multi-constructeurs :
   - équivalent Siemens
   - équivalent Rockwell
   - équivalent Ignition
   - différence de sémantique ou de portée

4. Quand l'utilisateur veut une vraie montée en compétence, proposer un pack structuré :
   - standard de nommage
   - bibliothèque de blocs/patterns
   - modèle de tags PLC↔SCADA
   - conventions d'alarmes
   - stratégie de diagnostic
   - exemple complet de flux commande/retour

5. Si un des environnements est au centre du besoin, détailler davantage cette cible sans perdre la compatibilité transversale.

## Formats de livrables à privilégier

### 1. Pack standards
Fournir si possible :
- conventions de nommage I/O, internes, HMI, alarmes
- règles de portée des variables
- règles de conversion de types
- règles de temporisation
- règles de mapping tags/UDT/DB

### 2. Bibliothèque de patterns
Constituer les patterns minimaux suivants :
- moteur simple
- vanne simple
- analog input avec mise à l'échelle
- séquenceur CASE / étapes
- défaut mémorisé + reset
- heartbeat PLC↔SCADA
- commande manuelle / auto / défaut interdit

### 3. Matrice de mapping PLC↔SCADA
Toujours expliciter :
- commande opérateur
- acquittement défaut
- état machine
- disponibilité
- défaut synthétique
- grandeurs process
- qualité / communication

## Règles d'or

- Toujours distinguer mémoire persistante et variables temporaires.
- Toujours expliciter les différences de portée : Controller Tags vs Program Tags, FB/DB vs FC, tags Ignition côté provider.
- Toujours rappeler que Ignition exécute du Jython 2.7 : pas de syntaxe Python 3 moderne.
- Toujours traiter les lectures/écritures de tags Ignition en bulk quand plusieurs tags sont concernés.
- Toujours signaler les différences de sémantique des timers plutôt que supposer une équivalence parfaite entre Siemens et Rockwell.
- Toujours présenter la couche supervision comme consommatrice de données propres, stables et nommées, non comme un duplicata de la logique PLC.

## Pièges courants

1. Répondre outil par outil sans faire le lien système.
   - Correction : relier code automate, structure de tags et exploitation SCADA dans une même réponse.

2. Traduire littéralement une logique d'un constructeur à l'autre.
   - Correction : comparer les intentions fonctionnelles avant de traduire la syntaxe.

3. Oublier la couche données.
   - Correction : fournir un mapping explicite entre variables PLC, tags SCADA, alarmes et retours HMI.

4. Proposer des exemples de supervision qui dupliquent la sécurité ou les interlocks du PLC.
   - Correction : laisser la sécurité et la logique critique côté automate ; utiliser SCADA pour commande supervisée, visualisation, historisation et diagnostic.

## Checklist

- [ ] La réponse couvre bien PLC + données + SCADA.
- [ ] Les différences Siemens/Rockwell sont explicitées, pas supposées identiques.
- [ ] Ignition est traité en Jython 2.7 avec opérations bulk et Named Queries si nécessaire.
- [ ] Au moins un pattern réutilisable est proposé, pas seulement de la théorie.
- [ ] Un pack durable (standards, patterns, mapping, exemple) est proposé si l'utilisateur cherche une montée en compétence.
