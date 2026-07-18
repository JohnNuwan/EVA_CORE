---
name: electrical-distribution-protection
description: "Structurer la distribution électrique industrielle, la coordination des protections, les sélectivités et la conformité basse tension."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [industrial, electrical, distribution, protection, selectivity, low-voltage, iec-60204, iec-61439]
    related_skills: [electrical-schematics-eplan, emc-protection-grounding, multi-sector-industrial-standards]
---

# Distribution et protection électrique industrielle

## Vue d'ensemble

Cette compétence couvre la structuration des distributions BT industrielles : architecture de puissance, sélectivité, coordination des protections, schéma de liaison à la terre, continuité de service, repérage et conformité aux normes applicables. Elle aide à produire des livrables techniques cohérents entre calcul, schéma, exploitation et maintenance.

## Quand l'utiliser

À utiliser pour :
- définir une architecture de distribution BT industrielle ;
- dimensionner et coordonner des protections ;
- préparer un audit de conformité d'armoire ou TGBT ;
- vérifier sélectivité, pouvoir de coupure et chutes de tension.

Ne pas utiliser pour :
- un simple schéma unifilaire sans analyse de protection ;
- une étude bâtiment pure sans interaction machine/process ;
- une réponse purement réglementaire sans architecture de distribution réelle.

## Références clés

- IEC 60204-1
- IEC 61439
- IEC 60364
- IEC 60947

## Axes de structuration

1. Définir le schéma de distribution et les départs critiques.
2. Vérifier Icc, sélectivité et coordination amont/aval.
3. Documenter schéma de terre, continuité de service et maintenance.
4. Identifier les contraintes machine vs bâtiment.
5. Prévoir les preuves d'audit et les réserves de conformité.

## Livrables attendus

- schéma de distribution ;
- matrice protections / réglages / sélectivité ;
- vérification Icc et pouvoir de coupure ;
- synthèse schéma de terre et chute de tension ;
- check-list d'audit BT.

## Support files

- `templates/electrical-audit-checklist.md` : checklist d'audit terrain.
- `references/protection-coordination-matrix.md` : trame de coordination des protections.

## Pièges Courants (Common Pitfalls)

1. Choisir des protections sans vérifier Icc.
2. Oublier la sélectivité amont/aval.
3. Mélanger exigences machine et exigences distribution bâtiment.
4. Sous-documenter la maintenabilité des départs critiques.

## Liste de vérification (Checklist)

- [ ] Schéma de distribution défini.
- [ ] Icc estimé ou calculé.
- [ ] Sélectivité documentée.
- [ ] Chutes de tension vérifiées.
- [ ] Conformité normative identifiée.
- [ ] Maintenabilité et continuité de service sont considérées.
