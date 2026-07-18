---
name: siemens-sinamics-motion
description: "Configurer et diagnostiquer les variateurs Siemens Sinamics et leurs intégrations motion."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [siemens, sinamics, motion, drive, profidrive, servo, axis]
    related_skills: [drive-motion-control, siemens-scl, siemens-safety]
---

# Siemens Sinamics Motion

## Vue d'ensemble

Cette compétence couvre les variateurs Sinamics et leur intégration dans les architectures motion Siemens. Elle aide à structurer les axes, le homing, les profils de mouvement, les diagnostics, Profidrive et le lien avec Safety Integrated et la séquence machine.

## Quand l'utiliser

À utiliser pour :
- concevoir une architecture drive/motion Siemens ;
- structurer les axes et les contrats états/commandes/défauts ;
- définir le homing, les limites, les références et les reprises après défaut ;
- cadrer les interactions motion ↔ safety ↔ supervision.

Ne pas utiliser pour :
- un simple code SCL sans enjeu drive/axe ;
- une étude safety complète hors périmètre motion ;
- un besoin variateur isolé sans standardisation d'architecture.

## Axes de structuration

1. Séparer commande axe, état axe, diagnostic drive et orchestration machine.
2. Documenter les dépendances Profidrive/Profinet et les sources de référence.
3. Définir clairement les modes : disabled, ready, referenced, moving, stopping, fault.
4. Formaliser l'effet Safety Integrated sur les états et séquences de redémarrage.
5. Prévoir une vue maintenance orientée défauts, acquittements et causes probables.

## Livrables attendus

- matrice axes / variateurs / références ;
- contrat commandes / états / défauts ;
- stratégie de homing et de limites ;
- mapping diagnostics pour HMI/maintenance ;
- check-list FAT/SAT motion Siemens.

## Support files

- `templates/motion-axis-template.md` : gabarit de fiche axe.
- `references/expert-pack.md` : points d'attention détaillés Sinamics.
- `references/fat-sat-checklist.md` : validation terrain minimale.
- `references/version-validation-matrix.md` : matrice de validation rapide.

## Pièges Courants (Common Pitfalls)

1. Homing et références insuffisamment spécifiés.
2. Séquence machine trop couplée aux détails de l'asservissement.
3. Diagnostics motion insuffisants pour la maintenance.
4. Redémarrage après défaut ou arrêt safety non formalisé.

## Liste de vérification (Checklist)

- [ ] Les axes ont états, commandes et défauts définis.
- [ ] Homing, limites et références sont documentés.
- [ ] Les diagnostics sont exploitables côté maintenance.
- [ ] L'intégration Safety Integrated est explicitée.
- [ ] Les scénarios de reprise après défaut sont définis.
