---
name: scada-migration-legacy-to-modern
description: "Utiliser quand l'utilisateur doit cadrer une migration SCADA/HMI depuis une plateforme legacy vers un environnement moderne avec réduction du risque et non-régression."
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [scada, migration, legacy, hmi, modernisation, non-regression, transition]
    related_skills: [ignition-scada, wincc-unified, scada-hmi-programming-languages]
---

# SCADA Migration Legacy to Modern

## Vue d'ensemble

Cette compétence cadre une migration SCADA/HMI progressive : inventaire des écrans, scripts, tags, alarmes, historiques, interfaces externes, puis stratégie de transition et de validation pour limiter le risque de régression opératoire.

## Quand l'utiliser

À utiliser pour :
- migrer un SCADA ou une HMI vieillissante ;
- évaluer la dette technique d'une plateforme legacy ;
- préparer une coexistence temporaire old/new ;
- construire un plan de non-régression supervision.

Ne pas utiliser pour :
- un simple ajout d'écran ;
- une migration uniquement IT sans impact exploitation ;
- une refonte totale sans reprise des exigences existantes.

## Étapes clés

1. Inventaire des écrans, tags, alarmes, scripts, recettes et historiques.
2. Cartographie des dépendances externes.
3. Identification des écarts fonctionnels legacy ↔ cible.
4. Stratégie de bascule : big bang, coexistence ou migration incrémentale.
5. Validation opératoire et non-régression.

## Pièges Courants (Common Pitfalls)

1. Sous-estimer les scripts legacy et dépendances cachées.
2. Migrer les synoptiques sans reprendre alarmes, historiques et recettes.
3. Oublier la phase de coexistence ou le plan de retour arrière.
4. Valider techniquement la cible sans validation usage opérateur/maintenance.

## Liste de vérification (Checklist)

- [ ] L'inventaire fonctionnel legacy est complet.
- [ ] Les dépendances externes sont cartographiées.
- [ ] La stratégie de bascule est explicitée.
- [ ] La non-régression est testée.
- [ ] Un plan de retour arrière est prévu.
