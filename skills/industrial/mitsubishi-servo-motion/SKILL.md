---
name: mitsubishi-servo-motion
description: "Structurer les axes servo Mitsubishi et leur intégration dans les projets GX Works3."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [mitsubishi, servo, motion, gx-works3, axis, melsec]
    related_skills: [drive-motion-control, mitsubishi-gx-works3]
---

# Mitsubishi Servo Motion

## Vue d'ensemble

Cette compétence couvre les axes servo Mitsubishi dans les projets GX Works3, avec un accent sur la structuration des séquences motion, du homing, des défauts, des états et de la maintenance. Elle vise des architectures lisibles où la logique axe reste distincte de la logique machine globale.

## Quand l'utiliser

À utiliser pour :
- concevoir des axes servo Mitsubishi ;
- structurer homing, séquences et diagnostics ;
- définir les contrats commandes / états / défauts ;
- formaliser la reprise après défaut et les limites d'axe.

Ne pas utiliser pour :
- un simple projet GX Works3 sans motion ;
- une étude variateur isolée sans logique axe ;
- une logique safety complète hors périmètre servo.

## Axes de structuration

1. Séparer état axe et état machine.
2. Centraliser les défauts motion.
3. Définir explicitement homing, limites et reprise.
4. Prévoir un diagnostic clair côté maintenance.
5. Garder une séquence machine découplée des détails servo.

## Livrables attendus

- matrice axes / modes / références ;
- stratégie de homing ;
- table défauts / resets / acquittements ;
- logique de reprise après défaut ;
- check-list FAT/SAT motion.

## Support files

- `templates/axis-template.md` : gabarit de description d'axe.
- `references/expert-pack.md` : points d'attention détaillés Mitsubishi servo.
- `references/version-validation-matrix.md` : matrice de validation rapide.

## Pièges Courants (Common Pitfalls)

1. Homing mal cadré.
2. Motion trop couplé à la séquence globale.
3. Diagnostics insuffisants pour maintenance.
4. Réarmement d'axe non formalisé.

## Liste de vérification (Checklist)

- [ ] Homing et limites sont documentés.
- [ ] Les défauts motion sont centralisés.
- [ ] La séparation axe / machine est claire.
- [ ] La reprise après défaut est définie.
- [ ] Les diagnostics maintenance sont exploitables.
