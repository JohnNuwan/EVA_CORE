---
name: beckhoff-twinsafe
description: "Structurer les fonctions de sécurité Beckhoff TwinSAFE et les intégrer au motion EtherCAT."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [beckhoff, twinsafe, safety, ethercat, motion-safety, machine-safety]
    related_skills: [industrial-safety-sistema, beckhoff-twincat, drive-motion-control]
---

# Beckhoff TwinSAFE

## Vue d'ensemble

Cette compétence couvre TwinSAFE dans les architectures Beckhoff, avec un accent particulier sur l'intégration safety + motion + EtherCAT. Elle aide à définir arrêts sûrs, zones, réarmements, effets sur axes et frontière claire entre logique standard, sécurité et supervision.

## Quand l'utiliser

À utiliser pour :
- concevoir une architecture safety Beckhoff ;
- intégrer TwinSAFE avec motion EtherCAT ;
- formaliser portes, STO, zones, resets et permissifs sûrs ;
- documenter le comportement machine après défaut safety.

Ne pas utiliser pour :
- une simple question TwinCAT hors sécurité ;
- une logique d'axe sans fonction safety ;
- une analyse normative pure sans architecture machine réelle.

## Axes de structuration

1. Concevoir safety et motion ensemble.
2. Définir précisément l'effet safety sur chaque axe.
3. Séparer état safety, état axe et état machine.
4. Formaliser les conditions de reset et de reprise.
5. Prévoir un diagnostic exploitable pour validation et maintenance.

## Livrables attendus

- cartographie des fonctions TwinSAFE ;
- matrice zones / axes / permissifs ;
- stratégie de reset et de retour en service ;
- contrat safety ↔ standard ↔ supervision ;
- check-list FAT/SAT safety.

## Support files

- `templates/twinsafe-zone-template.md` : gabarit de zone safety.
- `references/expert-pack.md` : points d'attention détaillés TwinSAFE.
- `references/version-validation-matrix.md` : matrice de validation rapide.

## Pièges Courants (Common Pitfalls)

1. Effets safety sur axes mal documentés.
2. Zones ou portes sans logique de reprise claire.
3. Couplage ambigu entre runtime standard et sécurité.
4. Diagnostic safety insuffisant pour la maintenance.

## Liste de vérification (Checklist)

- [ ] Les effets safety sur axes sont définis.
- [ ] Les resets et zones sont documentés.
- [ ] La séparation safety / standard est claire.
- [ ] Le comportement après défaut est validé.
- [ ] Les scénarios de reprise sont explicités.
