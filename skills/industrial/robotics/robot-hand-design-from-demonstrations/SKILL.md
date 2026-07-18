---
name: robot-hand-design-from-demonstrations
description: "Utiliser quand l'utilisateur veut transformer des démonstrations humaines en exigences de conception, d'optimisation et de validation pour une main robotique, plutôt que produire seulement un résumé académique."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [robotics, dexterous-hand, imitation-learning, reinforcement-learning, additive-manufacturing, grasping]
    related_skills: [robotics-abb, robot-programming-languages, ai-industrial-vision, predictive-maintenance-ml]
---

# Robot Hand Design from Demonstrations

## Vue d'ensemble

Cette compétence s'appuie sur les approches de génération de mains robotiques à partir de démonstrations humaines, mais la reformule comme un workflow d'ingénierie exploitable. Elle aide à passer d'un corpus de mouvements humains à un cahier de conception, un pipeline d'optimisation, un plan de prototypage et une stratégie de validation fonctionnelle.

## Quand l'utiliser

À utiliser pour :
- concevoir une main robotique inspirée de gestes humains ;
- cadrer un pipeline démonstrations → cinématique → optimisation → prototype ;
- comparer plusieurs architectures de doigts, degrés de liberté ou transmissions ;
- préparer une preuve de concept robotique mêlant IA, simulation et fabrication additive.

Ne pas utiliser pour :
- un simple résumé d'article scientifique ;
- une préhension robotique sans besoin de conception mécanique ;
- une étude purement commande sans démonstrations humaines ni choix de morphologie.

## Workflow recommandé

1. Définir les tâches cibles : prises, manipulations, contraintes d'objets.
2. Collecter et normaliser les démonstrations humaines.
3. Identifier les variables essentielles : doigts, contacts, amplitudes, postures.
4. Traduire ces besoins en exigences morphologiques et cinématiques.
5. Optimiser les designs candidats par simulation ou RL.
6. Prototyper les meilleurs candidats.
7. Valider en essais fonctionnels et comparer à la baseline humaine ou robotique.

## 1. Collecte de données

- Capturer des gestes représentatifs du périmètre applicatif, pas seulement des gestes « jolis ».
- Prévoir une calibration robuste des capteurs ou du système de motion capture.
- Conserver les métadonnées de tâche : objet, orientation, succès/échec, vitesse, contraintes.
- Nettoyer les données pour l'inverse cinématique, la segmentation des phases de mouvement et l'analyse des contacts.

## 2. Optimisation du design robotique

- Comparer plusieurs nombres de DoF, géométries de doigts et stratégies de transmission.
- Utiliser un cadre d'optimisation qui sépare :
  - morphologie,
  - commande,
  - métriques de réussite,
  - coût matériel.
- Si un algorithme RL est employé, expliciter : observation, action, reward, contraintes, simulateur.
- Chercher le bon compromis entre dextérité, robustesse mécanique et coût de fabrication.

## 3. Fabrication et prototypage

- Préparer des exports CAO / STL propres et traçables.
- Séparer clairement prototype démonstrateur et design industrialisable.
- Documenter matériaux, tolérances, points d'usure, actionneurs et capteurs.
- Tester les composants critiques avant assemblage complet.

## 4. Vérification fonctionnelle

- Définir des scénarios de tests : prise, maintien, repositionnement, robustesse, répétabilité.
- Comparer les performances aux hypothèses initiales ou à une baseline.
- Mesurer précision, taux de succès, force de prise, sensibilité aux variations d'objet.
- Distinguer limitations algorithmiques, mécaniques et capteurs.

## Livrables attendus

- matrice tâches ↔ exigences fonctionnelles ;
- cahier de paramètres morphologiques ;
- stratégie d'optimisation et de simulation ;
- plan de prototypage ;
- protocole de validation fonctionnelle.

## Support files

- `references/design-evaluation-matrix.md` : critères de comparaison entre designs.

## Pièges Courants (Common Pitfalls)

1. Utiliser des démonstrations non représentatives des tâches réelles.
2. Optimiser la simulation sans intégrer les contraintes de fabrication.
3. Sous-estimer l'importance des capteurs et de la calibration.
4. Confondre réussite d'une démo et robustesse sur un ensemble de cas.

## Liste de vérification (Checklist)

- [ ] Les tâches cibles sont définies.
- [ ] Les démonstrations sont calibrées et annotées.
- [ ] Les hypothèses morphologiques sont explicites.
- [ ] La stratégie d'optimisation est traçable.
- [ ] Le protocole de validation distingue simulation et essais physiques.
