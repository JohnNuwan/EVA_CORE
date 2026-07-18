---
name: opc-ua-information-modeling
description: "Utiliser quand l'utilisateur doit concevoir, auditer ou normaliser un modèle d'information OPC UA avec namespaces, NodeIds, types, méthodes et alignement Companion Specification."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [opc-ua, information-model, nodeset, namespace, companion-specification, modeling]
    related_skills: [industrial-protocols, opc-ua-scanner, isa95-modelling]
---

# OPC UA Information Modeling

## Vue d'ensemble

Cette compétence structure les modèles d'information OPC UA au-delà de la simple connectivité : organisation des namespaces, stabilité des NodeIds, typage, BrowseNames, méthodes, événements et cohérence avec les Companion Specifications.

## Quand l'utiliser

À utiliser pour :
- concevoir ou auditer un NodeSet ;
- aligner un modèle OPC UA avec ISA-95, UNS ou un modèle métier ;
- préparer un export UANodeSet réutilisable ;
- valider la cohérence de BrowseNames, namespaces et types.

Ne pas utiliser pour :
- un simple test client/serveur OPC UA sans travail de modélisation ;
- une table de tags plate sans ambition sémantique ;
- un besoin limité à la lecture brute de variables.

## Principes de fond

1. Les NodeIds doivent être stables et gouvernés.
2. Les BrowseNames doivent rester lisibles et cohérents.
3. Les namespaces séparent clairement standard, constructeur et métier projet.
4. Les types et relations portent la sémantique, pas seulement les noms.
5. Le modèle doit rester exploitable par plusieurs clients sans connaissance implicite du projet.

## Support files

- `references/model-governance-checklist.md` : garde-fous minimaux pour namespaces, NodeIds, BrowseNames et export NodeSet.

## Pièges Courants (Common Pitfalls)

1. Utiliser des NodeIds instables générés sans gouvernance.
2. Mélanger sémantique métier et structure technique dans un seul namespace confus.
3. Répliquer un simple arbre de tags sans modélisation de types.
4. Oublier la validation de BrowseNames, DisplayNames et références.

## Liste de vérification (Checklist)

- [ ] Les namespaces sont explicitement gouvernés.
- [ ] Les NodeIds sont stables et documentés.
- [ ] Les types et relations sont définis proprement.
- [ ] Le modèle peut être compris par un client tiers.
- [ ] Le NodeSet peut être validé par un outillage de contrôle.
