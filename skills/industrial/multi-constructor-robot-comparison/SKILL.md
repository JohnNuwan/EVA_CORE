---
name: multi-constructor-robot-comparison
description: "Comparer les principales plateformes de robots industriels et choisir la plus adaptée au cas d'usage."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [robotics, industrial, abb, fanuc, kuka, staubli, comparison]
    related_skills: [robotics-abb, robotics-fanuc, robotics-kuka, robotics-staubli]
---

# Tableau comparatif multi-constructeurs robots

## Vue d'ensemble

Cette compétence aide à comparer ABB, Fanuc, KUKA et Stäubli selon les critères de programmation, simulation, sécurité, intégration PLC, motion et maintenance.

## Quand l'utiliser
- Choisir une plateforme robot pour une nouvelle cellule.
- Préparer une standardisation multi-sites.
- Comparer les environnements RAPID, TP/Karel, KRL et VAL 3.
- Définir une stratégie d'intégration robot ↔ PLC ↔ HMI.

## Lecture rapide
- ABB : très fort en RAPID, multitâche, RobotStudio et flexibilité cellule.
- Fanuc : très fort en diffusion marché, robustesse atelier et intégration production.
- KUKA : très fort en architectures cellules complexes, KRL, WorkVisual et logique système.
- Stäubli : très fort en propreté, précision, pharma/agro et VAL 3 modulaire.

## Critères de comparaison
| Critère | ABB | Fanuc | KUKA | Stäubli |
|---|---|---|---|---|
| Langage | RAPID | TP + Karel | KRL | VAL 3 |
| Simulation offline | très forte | bonne | forte | bonne |
| Intégration PLC | forte | forte | forte | bonne |
| Sécurité cellule | forte | forte | forte | forte |
| Flexibilité logicielle | très forte | moyenne à forte | forte | forte |
| Standardisation multi-cellules | forte | forte | forte | moyenne à forte |
| Applications propres/pharma | bonne | moyenne | moyenne | très forte |

## Pièges Courants (Common Pitfalls)
1. Choisir une marque uniquement sur habitude locale sans regarder support, simulation et maintenance.
2. Sous-estimer la différence entre langage robot et stratégie PLC/SCADA.
3. Mélanger comparaison mécanique et comparaison d'outillage logiciel.

## Liste de vérification (Checklist)
- [ ] Le cas d'usage robot est clairement défini.
- [ ] Les besoins simulation/offline sont identifiés.
- [ ] La stratégie PLC ↔ robot ↔ HMI est connue.
- [ ] Les contraintes sécurité et maintenance sont prises en compte.
