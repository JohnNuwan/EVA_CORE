---
name: robot-safety-cell-design
description: "Concevoir la sécurité d'une cellule robotisée : modes, zones, interverrouillages et resets."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [robotics, safety, cell, interlocks, reset, fences]
    related_skills: [robot-plc-standard-interface, robotics-abb, robotics-fanuc, robotics-kuka, robotics-staubli]
---

# Sécurité de cellule robotisée

## Vue d'ensemble

Cette compétence structure la sécurité d'une cellule robotisée : clôtures, portes, arrêts d'urgence, modes Auto/Teach/Manual, reset sécurité, zones et interverrouillages avec le PLC. Elle vise une architecture compréhensible par automaticiens, roboticiens, maintenance et validation sécurité.

## Quand l'utiliser

À utiliser pour :
- définir une architecture safety robot ;
- structurer les signaux Safe entre robot, automate et cellule ;
- définir les conditions de reset et de reprise ;
- harmoniser les modes opérateurs.

Ne pas utiliser pour :
- une simple interface robot sans enjeux safety ;
- une logique sécurité machine générale non robotisée ;
- une note d'exploitation sans conception d'architecture.

## Principes recommandés

- séparer sécurité, process et défauts robot ;
- définir explicitement les zones ;
- rendre le reset sécurité conditionnel et traçable ;
- documenter l'effet safety sur cycle et motion ;
- distinguer clairement Auto, Teach et modes dégradés.

## Signaux minimaux

- FenceClosed
- EStopOk
- RobotSafe
- TeachMode
- AutoMode
- ResetRequired
- SafeMotionReleased

## Livrables attendus

- matrice zones / modes / resets ;
- table des signaux Safe ;
- logique de reprise et de reset ;
- effet safety sur le cycle robot ;
- check-list FAT/SAT cellule.

## Support files

- `templates/safety-zone-matrix.md` : matrice des zones.
- `templates/safety-reset-template.md` : logique de reset.
- `templates/cell-modes-template.md` : modes opératoires.
- `references/expert-pack.md` : points d'attention cellule robotisée.

## Pièges Courants (Common Pitfalls)

1. Mélanger défaut sécurité et défaut process.
2. Autoriser un reset sans préconditions claires.
3. Ne pas distinguer mode Teach et mode Auto.
4. Sous-documenter l'effet safety sur le cycle et la remise en production.

## Liste de vérification (Checklist)

- [ ] Les modes Auto/Teach/Manual sont définis.
- [ ] Les zones et clôtures sont documentées.
- [ ] Les préconditions de reset sont claires.
- [ ] L'effet safety sur le cycle robot est explicité.
- [ ] La reprise en production après défaut est cadrée.
