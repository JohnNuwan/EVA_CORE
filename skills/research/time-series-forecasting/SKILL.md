---
name: time-series-forecasting
description: "Compétence niveau expert en prévision de séries temporelles. Couvre ARIMA, Prophet, neural forecast, transformers temporels, Informer, Autoformer, FEDformer, PatchTST, TimesNet, N-BEATS, N-HiTS, TFT, DeepAR, MQ-CNN, temporal fusion, foundation models pour time series, Lag-Llama, TimesFM, MOIRAI, TF-T5, ensemble, hierarchical reconciliation, probabilistic forecasting, et M5/M6 competitions."
keywords: [time series, forecasting, ARIMA, Prophet, transformers, N-BEATS, neural forecast, hierarchical]
categories: [stat.ML, stat.ME, cs.LG, cs.AI, q-fin.ST, q-fin.EC, math.PR]
---

# Compétence Prévision de Séries Temporelles

## Présentation

Cette compétence couvre l'ensemble des méthodes de prévision de séries temporelles, des approches classiques aux transformers temporels, en passant par le deep learning, les foundation models et les méthodes probabilistes.

---

## Méthodes Classiques

- **ARIMA** : Autoregressive Integrated Moving Average
- **SARIMA** : Seasonal ARIMA
- **Exponential Smoothing (ETS)** : Lissage exponentiel (Holt-Winters)
- **Theta Method** : Méthode Theta (décomposition et extrapolation)
- **STL Decomposition** : Décomposition saisonnière par LOESS
- **TBATS** : Trigonometric, Box-Cox, ARMA, Trend, Seasonal
- **Structural Time Series** : Séries temporelles structurelles (Unobserved Components)
- **State Space Models / Kalman Filter** : Filtre de Kalman pour séries temporelles
- **Bayesian Structural Time Series (BSTS)** : Séries structurelles bayésiennes

## ML et Gradient Boosting

- **XGBoost / Random Forest / GBM** : Arbres pour séries temporelles
- **Feature Engineering** : Lags, rolling windows, calendar features, holiday effects
- **External Regressors** : Régresseurs exogènes
- **Windowing** : Fenêtrage temporel pour l'entraînement supervisé
- **Cross-Validation Temporelle** : Validation croisée adaptée aux séries temporelles
- **Purged Walk-Forward** : Validation purgée pour éviter le data leakage
- **Backtesting** : Backtesting systématique des modèles

## Deep Learning

- **DeepAR** : Modèle autorégressif profond (Amazon, probabilistic forecasting)
- **DeepState** : State space models profonds
- **DeepFactors** : Factor models profonds
- **N-BEATS** : Neural Basis Expansion Analysis for Interpretable Time Series
- **N-HiTS** : Neural Hierarchical Interpolation for Time Series (plus scalable)
- **TCN (Temporal Convolutional Network)** : Réseaux de convolution temporels
- **WaveNet** : Convolutions dilatées causales
- **TFT (Temporal Fusion Transformer)** : Transformer avec mécanismes interprétables
- **Interpretability VAE** : VAE pour interprétabilité des séries temporelles
- **Attention Encoders** : Encodeurs à attention pour séries temporelles

## Transformers Temporels

- **Informer** : ProbSparse self-attention pour longues séquences
- **Autoformer** : Auto-correlation mechanism au lieu de l'attention
- **FEDformer** : Frequency Enhanced Decomposed Transformer (seasonal-trend)
- **PatchTST** : Patches de séries temporelles avec Transformers
- **Crossformer** : Cross-dimensional attention pour séries multivariées
- **TimesNet** : Multi-périodicité avec convolution 2D
- **iTransformer** : Inverted Transformers pour séries multivariées
- **Pyraformer** : Pyramidal attention multi-échelle

## Foundation Models for Time Series

- **Lag-Llama** : Modèle de fondation avec distributions de lags
- **TimesFM (Google)** : Foundation model pour séries temporelles
- **MOIRAI** : Unified foundation model (Salesforce)
- **TF-T5** : Text-to-Text Transfer Transformer pour séries temporelles
- **Tiny Time Mixers (TTM)** : Modèles compacts pour séries temporelles
- **Chronos (Amazon)** : Probabilistic foundation model
- **Pretrained Zero-Shot** : Généralisation zero-shot des foundation models
- **In-Context Learning** : Apprentissage en contexte pour séries temporelles
- **M5 Accuracy Competition** : Compétition M5 (précision de prévision)
- **M6 Trading Competition** : Compétition M6 (prévision + trading)

## Probabilistic et Hiérarchique

- **Probabilistic Forecasting** : Prévision probabiliste (distributions complètes)
- **Quantile Regression** : Régression quantile pour prévisions par intervalles
- **Distribution Prediction** : Prédiction directe de la distribution
- **CRPS (Continuous Ranked Probability Score)** : Score probabiliste
- **PIT (Probability Integral Transform)** : Transformation pour calibration
- **QRA (Quantile Regression Averaging)** : Agrégation de quantiles
- **Hierarchical Reconciliation** : Réconciliation hiérarchique des prévisions
- **Bottom-Up / Top-Down** : Méthodes d'agrégation classiques
- **Optimal Combination** : Combinaison optimale (Hyndman et al.)
- **MinT (Minimum Trace)** : Réconciliation par trace minimale
- **Grouped Reconciliation** : Réconciliation par groupes
- **Forecast Coherence** : Cohérence des prévisions entre niveaux