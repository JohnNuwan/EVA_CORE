---
name: fat-sat-iq-oq-pq-automation
description: "Utiliser quand l'utilisateur doit structurer des validations FAT/SAT ou qualification IQ/OQ/PQ avec traçabilité exigences↔tests↔preuves pour projets d'automatisme."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [fat, sat, iq, oq, pq, validation, qualification, tests, tracabilite]
    related_skills: [iso-quality, process-pharma, industrial-audit]
---

# FAT / SAT / IQ / OQ / PQ Automation

## Vue d'ensemble

Cette compétence structure les livrables de validation et de qualification pour les systèmes automatisés. Elle relie exigences, cas de test, preuves, écarts et critères d'acceptation afin d'éviter les plans de tests plats, non traçables ou impossibles à rejouer.

## Quand l'utiliser

À utiliser pour :
- préparer FAT/SAT d'une machine ou d'une ligne ;
- cadrer IQ/OQ/PQ dans un contexte réglementé ;
- construire une matrice exigences↔tests↔preuves ;
- formaliser des réserves et écarts de mise en service.

Ne pas utiliser pour :
- un simple smoke test sans exigences traçables ;
- un document de recette opératoire non qualifiante ;
- une note informelle sans valeur contractuelle.

## Structure attendue

1. Périmètre et hypothèses.
2. Référentiel d'exigences.
3. Cas de tests détaillés.
4. Preuves attendues.
5. Gestion des écarts / réserves.
6. Critères de clôture.

## Support files

- `templates/traceability-matrix.md` : modèle de matrice de traçabilité réutilisable.

## Pièges Courants (Common Pitfalls)

1. Définir des tests sans rattachement à des exigences.
2. Mélanger FAT, SAT et qualification réglementaire dans une seule logique floue.
3. Oublier les preuves attendues dès la conception des tests.
4. Clôturer une validation sans registre clair des écarts.

## Liste de vérification (Checklist)

- [ ] Les exigences source sont identifiées.
- [ ] Chaque test a un objectif, une preuve et un critère d'acceptation.
- [ ] Les écarts et réserves ont un statut.
- [ ] La différence FAT/SAT/IQ/OQ/PQ est explicitée.
- [ ] La traçabilité est maintenue de bout en bout.
