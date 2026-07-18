---
name: br-motion-control
description: "Structurer les axes et la logique motion B&R dans Automation Studio."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [br, motion, automation-studio, axis, servo, machine-oem]
    related_skills: [drive-motion-control, br-automation-studio, industrial-safety-sistema]
---

# B&R Motion Control

## Vue d'ensemble

Cette compétence couvre la structuration des axes B&R dans Automation Studio, avec un accent sur machines rapides, synchronisation, diagnostics, cohérence HMI et safety. Elle aide à séparer proprement objets axes, orchestration machine, gestion des défauts et exploitation terrain.

## Quand l'utiliser

À utiliser pour :
- concevoir des axes B&R dans une machine OEM ;
- formaliser synchronisation, homing et diagnostics ;
- structurer le lien motion, HMI et safety ;
- préparer une architecture de maintenance exploitable.

Ne pas utiliser pour :
- un simple bloc automate sans dimension motion ;
- une étude safety sans pilotage d'axes ;
- un réglage ponctuel drive sans objectif d'architecture.

## Axes de structuration

1. Isoler couche axes et orchestration machine.
2. Définir les états : not-ready, homing, ready, moving, stopping, fault.
3. Penser motion, HMI et safety ensemble.
4. Rendre les diagnostics directement exploitables.
5. Prévoir le comportement après défaut et après redémarrage machine.

## Livrables attendus

- matrice axes / synchronisations ;
- modèle d'états et défauts ;
- stratégie de homing et de reprise ;
- contrat HMI ↔ motion ;
- check-list FAT/SAT motion.

## Support files

- `templates/axis-template.md` : gabarit d'axe.
- `references/expert-pack.md` : points d'attention détaillés B&R motion.
- `references/version-validation-matrix.md` : matrice de validation rapide.

## Pièges Courants (Common Pitfalls)

1. Architecture motion trop monolithique.
2. HMI et motion mal alignés.
3. Safety ajoutée trop tard dans la conception.
4. Diagnostic maintenance trop pauvre.

## Liste de vérification (Checklist)

- [ ] Les axes sont modulaires.
- [ ] La synchronisation est documentée.
- [ ] Les diagnostics sont exploitables.
- [ ] Le lien safety/HMI est cohérent.
- [ ] La reprise après défaut est définie.
