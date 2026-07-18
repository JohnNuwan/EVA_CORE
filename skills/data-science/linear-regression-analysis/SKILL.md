---
name: linear-regression-analysis
description: "Analyse et modélisation de régressions linéaires."
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [regression, statistics, predictive-modeling, scikit-learn, statsmodels, industry-analytics]
    related_skills: [data-analysis-exploration, predictive-maintenance-ml, engineering-project-management]
---

# Framework d'Analyse par Régression Linéaire Évolué

## Vue d'ensemble

Ce framework structure l'application des régressions linéaires, en allant au-delà de la simple corrélation. Il intègre la validation statistique rigoureuse, la gestion des variables multiples, et l'interprétation métier pour des applications industrielles.

## Quand l'utiliser

À utiliser pour :
- **Analyse prédictive** : Prédire une variable continue (consommation, usure, durée de vie) à partir de paramètres process.
- **Diagnostic de corrélation** : Quantifier l'impact réel d'un paramètre (ex: température) sur un résultat (ex: précision pièce).
- **Benchmarking de modèle** : Comparer la performance statistique de plusieurs modèles.

## Pipeline d'exécution structuré

1. **Prétraitement** : Nettoyage des données (NaN, outliers via Z-score), normalisation des features (`StandardScaler`).
2. **Choix du modèle** :
    - `statsmodels` pour l'inférence statistique (P-values, intervalles de confiance, R² ajusté).
    - `scikit-learn` pour le déploiement applicatif et scoring prédictif.
3. **Diagnostic des résidus** : Vérification de l'homoscédasticité et de la normalité (critique en industrie).
4. **Validation croisée** : Éviter le surapprentissage (overfitting) par k-fold cross-validation.

## Exemple d'utilisation (Inférence Statistique)

```python
import statsmodels.api as sm
import pandas as pd

# 1. Préparation (y: résultat, X: features)
X = df[['temp', 'pressure', 'rpm']]
X = sm.add_constant(X) # Indispensable pour l'ordonnée à l'origine
y = df['product_quality']

# 2. Modélisation
model = sm.OLS(y, X).fit()

# 3. Interprétation complète
print(model.summary())
```

## Pièges et Bonnes Pratiques Industriels

1. **Multicolinéarité** : Si deux variables process sont trop corrélées (ex: temp1 et temp2), les coefficients deviennent instables. Utiliser le **VIF (Variance Inflation Factor)** pour éliminer les variables redondantes.
2. **Outliers physiques** : En industrie, un outlier n'est pas toujours une erreur de mesure, mais parfois un événement critique (défaillance). Ne pas les supprimer sans analyse métier.
3. **Interprétabilité vs Précision** : Privilégier la régression linéaire simple pour sa transparence avec les opérateurs, plutôt qu'une "boîte noire" (XGBoost) si la précision est proche.
4. **R² n'est pas tout** : En industrie, l'erreur quadratique moyenne (**RMSE**) en unités physiques (ex: "l'erreur est en moyenne de ±2°C") est souvent plus parlante qu'un score R².

## Checklist avant validation
- [ ] Test VIF réalisé (détection multicolinéarité).
- [ ] Test de normalité des résidus (Durbin-Watson).
- [ ] Validation croisée (k-fold) effectuée.
- [ ] Rapport sur le RMSE (Root Mean Squared Error) en unités réelles.
