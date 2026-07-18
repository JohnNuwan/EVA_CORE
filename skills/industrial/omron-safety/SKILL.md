---
name: omron-safety
description: "Structurer les fonctions de sécurité Omron et leur intégration avec Sysmac et motion."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [omron, safety, sysmac, machine-safety, motion-safety, pl, sil]
    related_skills: [industrial-safety-sistema, omron-sysmac, drive-motion-control]
---

# Omron Safety

## Vue d'ensemble

Cette compétence couvre les principes de structuration safety dans l'écosystème Omron, en lien avec Sysmac, motion et sécurité machine. Elle aide à définir resets, permissifs sûrs, zones, reprise et cohérence entre safety, axes et comportement opérateur.

## Quand l'utiliser

À utiliser pour :
- concevoir des fonctions safety Omron ;
- intégrer safety + Sysmac + motion ;
- structurer E-stop, guard doors, zones et resets ;
- clarifier les interactions entre safety et modes machine.

Ne pas utiliser pour :
- une simple logique Sysmac sans exigence safety ;
- une analyse normative sans architecture machine réelle ;
- une correction locale sans enjeu de standardisation safety.

## Axes de structuration

1. Séparer nettement safety et logique machine.
2. Définir des conditions de reprise explicites.
3. Lier clairement safety, axes et états opérateur.
4. Formaliser les zones, permissifs et interverrouillages.
5. Prévoir un diagnostic compréhensible côté maintenance.

## Livrables attendus

- cartographie des fonctions safety ;
- matrice zones / permissifs / resets ;
- logique de reprise après défaut ;
- contrat safety ↔ motion ↔ supervision ;
- check-list FAT/SAT safety.

## Support files

- `templates/safety-zone-template.md` : gabarit de zone safety.
- `references/expert-pack.md` : points d'attention détaillés Omron safety.

## Pièges Courants (Common Pitfalls)

1. Reset safety sans préconditions claires.
2. Logique zone/safety peu lisible.
3. Mauvaise cohérence entre safety et mode machine.
4. Diagnostic insuffisant pour l'exploitation terrain.

## Liste de vérification (Checklist)

- [ ] Les fonctions safety sont isolées.
- [ ] Les zones et reprises sont documentées.
- [ ] Le lien avec motion est défini.
- [ ] Le comportement opérateur est cohérent.
- [ ] La validation terrain safety est prévue.
