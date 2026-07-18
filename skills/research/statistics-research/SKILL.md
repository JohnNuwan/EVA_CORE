---
name: statistics-research
description: >-
  Compétence professionnelle en recherche en statistiques suivie sur arXiv
  sous stat.* et math.ST. Couvre la méthodologie statistique, l'inférence,
  la conception d'expériences, l'inférence causale, les statistiques
  bayésiennes, les statistiques haute dimension, les séries temporelles,
  les statistiques spatiales, le calcul statistique et les applications.
category: research
---

# Compétence en Recherche en Statistiques (stat.*)

## Présentation

Les statistiques sur arXiv reçoivent environ 334 nouvelles soumissions par semaine dans les sous-catégories (stat.ME, stat.ML, stat.TH, stat.CO, stat.AP, math.ST). Cette compétence fournit une structure pour naviguer dans le paysage de la recherche statistique en lien avec le ML et l'IA.

## Domaines de Recherche Principaux

### 1. Méthodologie Statistique (stat.ME)
**Densité arXiv** : La plus élevée dans stat.* (~45 entrées/jour)
- **Conception d'expériences** : Plans d'expérience, conception optimale, méthodologie de surface de réponse
- **Conception d'expériences pour l'IA** : Évaluation de la découverte autonome de modèles par l'IA agentique
- **Inférence causale** : Résultats potentiels, DAGs, variables instrumentales
- **Statistiques spatiales** : Régression spatiale, krigeage, effets de débordement spatial
- **Données longitudinales et groupées** : Modèles mixtes, GEE, effets aléatoires
- **Données manquantes** : Imputation multiple, algorithme EM
- **Séries temporelles** : ARIMA, modèles espace-état, prévision, ruptures structurelles

### 2. Théorie Statistique (math.ST, stat.TH)
**Densité arXiv** : Élevée
- **Théorie de la décision** : Admissibilité, minimaxité, risque bayésien, estimation par retrait
- **Statistiques haute dimension** : Lasso, ridge, pénalisation par norme nucléaire
- **Estimation fonctionnelle** : Régression non paramétrique, estimation de densité, fonctionnelles spectrales
- **Minimisation approchée du risque** : Règles de retrait-seuil dans l'estimation de la moyenne normale
- **Estimation de Stein** : Estimateur de James-Stein, estimateurs de covariance par retrait
- **Formes bilinéaires** : Estimation dans des panneaux de tenseurs décalés
- **Théorie des copules** : Copules imprécises discrètes, matrices de signes alternés

### 3. Statistiques Bayésiennes (stat.ME, stat.CO)
**Densité arXiv** : Élevée
- **Inférence bayésienne** : Calcul a posteriori, choix du prior, comparaison de modèles
- **Bayésien non paramétrique** : Processus de Dirichlet, priors par processus gaussiens
- **Méthodes MCMC** : Hamiltonien Monte Carlo, NUTS, saut réversible, SMC
- **Bayésien variationnel** : Champ moyen, VB amorti, VB pondéré par importance
- **Problèmes inverses bayésiens** : Approches par vraisemblance neuronale avec approximation convexe

### 4. Calcul Statistique (stat.CO)
**Densité arXiv** : Modérée
- **Méthodes de Monte Carlo** : Échantillonnage d'importance, Monte Carlo séquentiel, filtres particulaires
- **Diagnostics MCMC** : Diagnostics de convergence, taille d'échantillon effective
- **Optimisation pour les statistiques** : Algorithme EM, algorithmes MM, IRLS
- **Fonctionnelles spectrales** : Propagation d'erreur dans les estimateurs de covariance par retrait

### 5. Statistiques pour l'Apprentissage Automatique (stat.ML)
**Densité arXiv** : ~150 entrées/semaine — fortement cross-listé avec cs.LG
- **Théorie de l'apprentissage statistique** : Bornes de généralisation, théorie PAC, biais-variance
- **Méthodes à noyau** : RKHS, régression à noyau, SVM
- **Processus gaussiens** : Régression GP, deep GPs, GP passant à l'échelle
- **Théorie des réseaux de neurones** : NTK, limites mean-field, robustesse en largeur
- **Boosting** : Gradient boosting, décodage par liste, théorie du boosting
- **Réseaux de diffusion** : Capacité de séparation sur données de faible dimension
- **Théorie espace-fonction** : Dichotomie pour l'apprentissage compositionnel
- **Filigrane des LLMs** : Filigrane calibré statistiquement (ICML 2026)

### 6. Statistiques Appliquées (stat.AP)
- **Biostatistiques** : Essais cliniques, analyse de survie, bioinformatique
- **Statistiques environnementales** : Modélisation climatique, événements extrêmes
- **Économétrie** : Économétrie financière, données de panel
- **Psychométrie** : Théorie de la réponse à l'item, analyse factorielle
- **Finance statistique (q-fin.ST)** : Modélisation des risques, optimisation de portefeuille

## Outils Statistiques Clés pour la Recherche en IA/ML

| Outil | Domaine | Application |
|-------|---------|-------------|
| **Intervalles de confiance** | stat.ME, stat.TH | Quantification d'incertitude pour le ML |
| **Tests d'hypothèses** | stat.ME | Tests A/B, comparaison de modèles |
| **Inférence causale** | stat.ME | Estimation d'effet de traitement, équité |
| **Inférence bayésienne** | stat.ME, stat.CO | Réseaux de neurones bayésiens, modèles GP |
| **Conception d'expériences** | stat.ME | Apprentissage actif |
| **Statistiques haute dimension** | math.ST | Sélection de caractéristiques |

## Articles Notables Récents (Mi-2026)
1. **Embracing Spillover: Spatial Effects in Experiments** — stat.ME
2. **Experimental Design Approach to Evaluating Agentic AI's Autonomous Model Discovery** — stat.ME/cs.AI
3. **Error Propagation in Spectral Functionals of Shrinkage Covariance Estimators** — stat.ME/math.ST
4. **Approximate Risk Minimization Over Shrinking-Thresholding Rules** — math.ST
5. **Boosting with List-Decodable Codes** — stat.ML (COLT 2026)
6. **Beyond Heuristic Tuning: Power-Calibrated LLM Watermarking** — stat.ML (ICML 2026)
7. **Width-Robust Learnability in Mean-Field Bayesian Neural Networks** — stat.ML

## Comment Effectuer la Veille
- **Méthodologie** : `/list/stat.ME/recent` (volume le plus élevé)
- **ML statistique** : `/list/stat.ML/recent` (~150 entrées/semaine)
- **Théorie statistique** : `/list/math.ST/recent`
- **Calcul statistique** : `/list/stat.CO/recent`
- **Statistiques appliquées** : `/list/stat.AP/recent`
- **Toutes les statistiques** : `/list/stat/recent` (~334 entrées/semaine)
- **Mots-clés** : "causal", "experimental design", "Bayesian", "high-dimensional", "convergence"