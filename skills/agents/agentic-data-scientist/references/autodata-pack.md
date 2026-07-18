# Autodata : Automatisation de la Science des Données Synthétiques par Agents

Ce document de référence décrit l'architecture de boucle fermée d'optimisation de données synthétiques basée sur les travaux de recherche de Meta FAIR (*Autodata: An agentic data scientist to create high quality synthetic data*, arXiv 2026).

---

## 1. Concept de Boucle Fermée de Données Synthétiques

Les méthodes traditionnelles de génération de données synthétiques (comme *Self-Instruct*) reposent sur une génération en une seule passe ("one-shot") qui souffre rapidement de redondances et d'hallucinations non détectées. 

L'approche **Autodata** introduit une boucle fermée où l'agent IA joue le rôle d'un scientifique des données complet : il formule une hypothèse (recette de génération), produit les données, réalise une évaluation qualitative et quantitative, diagnostique les échecs et ajuste de manière itérative sa recette.

---

## 2. L'Architecture Agentic Self-Instruct

Pour générer des jeux de données d'entraînement ciblés sur la frontière d'apprentissage actuelle d'un modèle, le système déploie plusieurs agents spécialisés :

```
                  ┌──────────────┐
                  │ Challenger   │  <── Analyse les faiblesses actuelles du solveur
                  └──────┬───────┘
                         │ (Génère des énoncés de tâches ciblés)
                         ▼
                  ┌──────────────┐
                  │ Solver       │  <── Résout les tâches (génère les réponses)
                  └──────┬───────┘
                         │ (Énoncés + Réponses candidates)
                         ▼
                  ┌──────────────┐
                  │ Judge        │  <── Valide la cohérence logique et filtre les erreurs
                  └──────┬───────┘
                         │
                         ▼
          [ Jeu de Données Synthétiques Validé ]
```

*   **Challenger (Orchestrateur)** : Identifie les faiblesses actuelles du modèle cible et génère de nouvelles requêtes complexes spécifiquement conçues pour le pousser dans ses retranchements.
*   **Solver (Weak/Strong Solvers)** : Résout les tâches générées et produit les paires d'instructions-réponses candidates.
*   **Judge** : Évalue la qualité, détecte les anomalies sémantiques, filtre les doublons, et formule les diagnostics de correction.

---

## 3. Méta-Optimisation Évolutionnaire (Outer Loop)

En plus de générer des données, le framework Autodata fait évoluer les invites et instructions de l'agent lui-même. Un algorithme évolutionnaire externe évalue la performance du jeu de données généré sur un ensemble de validation :
*   Si le jeu de données améliore le score de validation, la recette d'invite de l'agent est conservée et mutée pour l'itération suivante.
*   Cela permet à l'agent d'optimiser de manière autonome sa propre efficacité en tant que concepteur de données au fil du temps.
