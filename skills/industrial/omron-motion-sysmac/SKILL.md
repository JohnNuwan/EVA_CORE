---
name: omron-motion-sysmac
description: "Structurer les axes et la logique motion Omron dans Sysmac Studio."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [omron, motion, sysmac, axis, servo, ethercat]
    related_skills: [drive-motion-control, omron-sysmac, omron-safety]
---

# Omron Motion Sysmac

## Vue d'ensemble

Cette compétence couvre la structuration d'axes motion Omron dans Sysmac Studio, avec un accent sur l'intégration des blocs motion, homing, tâches synchrones, diagnostics et lien avec la sécurité. Elle aide à garder des architectures lisibles entre logique d'axe, séquence machine et comportement opérateur.

## Quand l'utiliser

À utiliser pour :
- structurer des axes et la logique motion Omron ;
- définir homing, synchronisation et reprise après défaut ;
- cadrer le lien motion, tâches primaires et safety ;
- préparer un diagnostic exploitable côté HMI/maintenance.

Ne pas utiliser pour :
- un simple projet Sysmac sans pilotage d'axes ;
- une logique safety sans motion ;
- un réglage ponctuel hors besoin d'architecture.

## Axes de structuration

1. Garder les blocs motion dans la tâche synchrone appropriée.
2. Définir clairement états axe, homing et défauts.
3. Séparer la séquence machine des détails d'axe.
4. Rendre visibles les dépendances réseau et servo.
5. Prévoir une stratégie de reprise et de retour en référence.

## Livrables attendus

- matrice axes / tâches / références ;
- stratégie de homing et de limites ;
- modèle de défauts et d'acquittement ;
- contrat motion ↔ safety ↔ supervision ;
- check-list FAT/SAT motion.

## Support files

- `templates/axis-template.md` : gabarit d'axe Omron.
- `references/expert-pack.md` : points d'attention détaillés Sysmac motion.
- `references/version-validation-matrix.md` : matrice de validation rapide.

## Pièges Courants (Common Pitfalls)

1. Motion hors tâche synchrone adaptée.
2. Diagnostics axes trop faibles.
3. Reprise défaut ou homing mal spécifiés.
4. Contrat motion ↔ safety mal défini.

## Liste de vérification (Checklist)

- [ ] Les blocs motion sont dans la bonne tâche.
- [ ] Homing et limites sont documentés.
- [ ] Les défauts axes sont synthétisés.
- [ ] Le lien avec safety est défini.
- [ ] La reprise après défaut est explicitée.
