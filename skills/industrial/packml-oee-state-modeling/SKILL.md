---
name: packml-oee-state-modeling
description: "Utiliser quand l'utilisateur doit relier les états machine PackML à un modèle OEE/TRS robuste pour supervision, historisation et MES."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [packml, oee, trs, state-model, mes, supervision, historisation]
    related_skills: [packml-isa-tr88, oee-performance, mes-integration]
---

# PackML OEE State Modeling

## Vue d'ensemble

Cette compétence fait le lien entre les états PackML et les besoins TRS/OEE. Elle aide à éviter les modèles de temps de marche / arrêt trop simplistes et à produire un découpage d'états exploitable par le SCADA, l'historian et le MES.

## Quand l'utiliser

À utiliser pour :
- concevoir un modèle d'états machine ;
- normaliser les causes d'arrêt et micro-arrêts ;
- fiabiliser les calculs de disponibilité, performance et qualité ;
- préparer l'intégration d'états machine au SCADA ou au MES.

Ne pas utiliser pour :
- un simple compteur de pièces ;
- un calcul OEE déconnecté de la machine réelle ;
- une machine sans structuration minimale de modes et arrêts.

## Principes de modélisation

1. Séparer état machine, mode machine et cause d'arrêt.
2. Éviter les états fourre-tout du type `Stopped` sans sous-catégorie.
3. Garder une taxonomie stable pour la performance et la qualité.
4. Lier chaque perte OEE à une cause opérationnelle ou technique identifiable.
5. Prévoir un mapping explicite PLC ↔ SCADA ↔ Historian ↔ MES.

## Support files

- `references/state-oee-mapping-matrix.md` : matrice de mapping entre états PackML, causes d'arrêt, pertes OEE et systèmes consommateurs.

## Pièges Courants (Common Pitfalls)

1. Calculer l'OEE depuis des signaux bruts sans modèle d'états.
2. Confondre arrêt planifié, arrêt non planifié et attente amont/aval.
3. Ne pas historiser les transitions d'état avec horodatage fiable.
4. Laisser au SCADA le soin d'inventer les causes d'arrêt sans contrat automate.

## Liste de vérification (Checklist)

- [ ] Les états PackML et leurs transitions sont définis.
- [ ] Les causes d'arrêt sont classifiées.
- [ ] Le mapping vers les pertes OEE est explicite.
- [ ] Les transitions sont historisées.
- [ ] L'intégration MES/SCADA repose sur un contrat stable.
