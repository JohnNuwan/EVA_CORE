---
name: wincc-unified
description: "Utiliser quand l'utilisateur demande de structurer, générer, auditer ou migrer des interfaces Siemens WinCC Unified avec scripts, tags, alarmes et faceplates."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [siemens, wincc-unified, hmi, scada, alarmes, faceplates, javascript]
    related_skills: [siemens-scl, scada-hmi-programming-languages, ignition-scada]
---

# WinCC Unified

## Vue d'ensemble

Cette compétence structure les projets WinCC Unified autour des écrans, faceplates, tags, alarmes, tendances, recettes et scripts JavaScript. Elle aide à produire des HMIs cohérentes, maintenables et alignées avec l'architecture PLC Siemens.

## Quand l'utiliser

À utiliser pour :
- concevoir ou normaliser un projet WinCC Unified ;
- préparer une migration HMI Siemens moderne ;
- définir une bibliothèque de faceplates ;
- structurer alarmes, tendances et commandes opérateur.

Ne pas utiliser pour :
- un simple besoin SCADA web générique hors écosystème Siemens ;
- une logique machine qui doit rester côté PLC ;
- un petit correctif isolé sans enjeu d'architecture HMI.

## Axes de structuration

1. Séparer objets de procédé, vues synoptiques, vues maintenance et vues réglages.
2. Garder un contrat tags stable entre PLC et HMI.
3. Normaliser l'affichage des états, défauts, permissifs et modes.
4. Réserver les scripts Unified aux besoins HMI ; ne pas y déplacer la logique procédé.
5. Prévoir dès le départ alarmes, historisation et diagnostic opérateur.

## Livrables attendus

- taxonomie d'écrans et de navigation ;
- modèle de faceplates et conventions d'instance ;
- matrice tags/commandes/alarmes ;
- règles de scripts JavaScript ;
- check-list FAT/SAT HMI.

## Support files

- `references/hmi-design-matrix.md` : matrice de cadrage des écrans, faceplates, alarmes, scripts et validation HMI.

## Pièges Courants (Common Pitfalls)

1. Reproduire dans l'HMI une logique qui devrait rester dans l'automate.
2. Multiplier les tags HMI redondants sans contrat clair avec le PLC.
3. Concevoir des faceplates sans états standardisés ni défauts exploitables.
4. Sous-documenter les recettes, tendances et ack alarmes.

## Liste de vérification (Checklist)

- [ ] La navigation HMI est structurée par usage métier.
- [ ] Le contrat tags PLC↔HMI est explicite.
- [ ] Les états, modes et alarmes sont standardisés.
- [ ] Les scripts Unified restent limités au périmètre supervision.
- [ ] Une validation FAT/SAT spécifique HMI est prévue.
