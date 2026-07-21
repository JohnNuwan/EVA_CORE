---
name: backtesting-strategies
description: >-
  Concevoir, implémenter, backtester et valider des stratégies de trading
  algorithmique. Couvre vectorized backtest, event-driven backtest, metrics
  de performance (Sharpe, Sortino, Calmar, MDD), walk-forward analysis,
  optimisation bayésienne, robustesse et overfitting detection.
category: finance
---

# Backtesting de Stratégies de Trading — Conception & Validation

## Présentation

Le backtesting est le processus de simulation d'une stratégie de trading sur
des données historiques pour évaluer sa performance. Mais backtester bien
est difficile — 90% des backtests sont sur-optimisés et ne survivent pas au
live trading. Ce skill fournit la méthodologie pour concevoir, implémenter
et valider des backtests robustes.

**Déclencheurs :** "backtest", "backtester", "stratégie de trading", "trading
algorithmique", "stratégie quant", "backtesting framework", "validation",
"forward test", "paper trading".

## Frameworks de backtesting Python

| Framework | Type | Forces | Faiblesses |
|---|---|---|---|
| **Backtrader** | Event-driven | Communauté, broker intégré, docs | Lent, pas vectorisé |
| **VectorBT** | Vectorized | Très rapide, optimisation, portefeuille | Courbe d'apprentissage |
| **Zipline** | Event-driven | Quantopian legacy, intraday | Installation difficile |
| **Freqtrade** | Event-driven | Crypto, live ready, web UI | Limité au crypto |
| **Lean (QuantConnect)** | Cloud event-driven | Multi-broker, intraday réel | Payant pour backtests lourds |
| **NautilusTrader** | Event-driven | Haute fréquence, C++ core | Complexe |
| **Pandas + Numpy** | Vectorized maison | Contrôle total, pas de dépendance | Tout à coder |

**Recommandation EVA :**
- **Analyse rapide / screening** → `pandas` vectorized (200 lignes)
- **Backtest sérieux + optimisation** → `backtrader` ou `vectorbt`
- **Production live** → `freqtrade` (crypto) ou implémentation maison

## Design patterns de stratégie

### Pattern 1 : Cross-over de moyennes mobiles

```python
# Vectorized backtest minimal
import pandas as pd
import numpy as np

def backtest_crossover(df, fast=20, slow=50):
    df = df.copy()
    df['sma_fast'] = df['close'].rolling(fast).mean()
    df['sma_slow'] = df['close'].rolling(slow).mean()
    df['signal'] = 0
    df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1
    df.loc[df['sma_fast'] <= df['sma_slow'], 'signal'] = -1
    df['position'] = df['signal'].shift(1)  # next-dat entry
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['position'] * df['returns']
    return df
```

### Pattern 2 : Mean reversion (Bollinger Bands)

```python
def backtest_bbands(df, window=20, std_dev=2):
    df = df.copy()
    df['sma'] = df['close'].rolling(window).mean()
    df['std'] = df['close'].rolling(window).std()
    df['upper'] = df['sma'] + std_dev * df['std']
    df['lower'] = df['sma'] - std_dev * df['std']
    df['signal'] = 0
    df.loc[df['close'] < df['lower'], 'signal'] = 1   # achat oversold
    df.loc[df['close'] > df['upper'], 'signal'] = -1  # vente overbought
    df['position'] = df['signal'].shift(1)
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['position'] * df['returns']
    return df
```

### Pattern 3 : ML-based signal (features → classifier)

```python
def ml_signal_pipeline(df, features_cols, target_col, model_cls):
    """Pipeline ML : feature engineering → train → predict → backtest"""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import TimeSeriesSplit

    df = df.dropna().copy()
    X = df[features_cols].values
    y = df[target_col].values  # 1 (hausse) / -1 (baisse)
    
    # Walk-forward cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    predictions = np.zeros(len(df))
    for train_idx, test_idx in tscv.split(X):
        model = model_cls()
        model.fit(X[train_idx], y[train_idx])
        predictions[test_idx] = model.predict(X[test_idx])
    
    df['signal'] = predictions
    df['position'] = df['signal'].shift(1)
    df['strategy_returns'] = df['position'] * df['returns']
    return df
```

## Métriques de performance

| Métrique | Formule | Interprétation |
|---|---|---|
| **Sharpe Ratio** | `E(Rp - Rf) / σ(Rp)` | >1.0 bon, >2.0 excellent (annualisé) |
| **Sortino Ratio** | `E(Rp - Rf) / σ_downside(Rp)` | Idem mais pénalise seulement la volatilité négative |
| **Calmar Ratio** | `CAGR / MDD` | Rendement annualisé / drawdown max |
| **Max Drawdown** | `min(cummax(cumreturns) - cumreturns)` | Plus grosse perte pic→creux |
| **Win Rate** | `Won trades / Total trades` | >50% acceptable selon risk/reward |
| **Profit Factor** | `Gross profit / Gross loss` | >2.0 bon |
| **Expectancy** | `E(Win%) * Avg Win - E(Lose%) * Avg Loss` | >0 = profitable |
| **Recovery Factor** | `Net profit / MDD` | >5 bon |
| **Return / MDD** | `Return ann / MDD` | >1.0 acceptable |

**Annualisation :**
```
Sharpe annualisé = Sharpe_journalier * √252
Sortino annualisé = Sortino_journalier * √252
```

## Overfitting Detection

### Problème

Plus on optimise de paramètres sur un historique court, plus on capture le
bruit au lieu du signal. Le backtest devient beau, le live devient moche.

### Remèdes

**① Walk-Forward Analysis (WFA)**
Découper l'historique en fenêtres train/val qui avancent dans le temps :
```
[TRAIN | VAL] [TRAIN | VAL] [TRAIN | VAL] ...
```
Optimiser les paramètres sur TRAIN, les tester sur VAL. La moyenne des
Sharpe sur les VAL donne le Sharpe hors échantillon.

**② Deflated Sharpe Ratio (DSR)**
Corrige le Sharpe observé du nombre de tentatives (multiples stratégies,
paramètres) :

```
DSR = CDF_Z( (SR_obs * √(n-1) - E(max SR sous H0)) / σ(max SR) )
```

Si DSR < 0.95, la stratégie n'est pas significativement meilleure que
le hasard.

**③ Purged Cross-Validation (Purging + Embargo)**
Pour les séries temporelles, ne pas laisser fuiter l'information du futur
dans le passé. Ajouter un **gap** (embargo) entre train et test :
```python
# Exemple : 5 splits avec embargo de 20 jours
for train_start, train_end, test_start, test_end in splits:
    train_end_effective = train_end - embargo_days  # purge
```

**④ Paramètres parcimonieux**
Règle empirique : 5 ans de données quotidiennes supportent ~3 paramètres
libres. Une stratégie à 10 paramètres optimisés sur 2 ans est presque
certainement overfit.

## Optimisation bayésienne des paramètres

Au lieu d'une grid search (coûteuse, 100% overfit), utiliser l'optimisation
bayésienne avec `optuna` ou `scikit-optimize` :

```python
import optuna

def objective(trial):
    fast = trial.suggest_int('fast', 5, 100)
    slow = trial.suggest_int('slow', fast + 10, 200)
    stop_loss = trial.suggest_float('sl', 0.01, 0.05)
    
    result = run_backtest(fast=fast, slow=slow, sl=stop_loss)
    return result['sharpe_ratio']

study = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler())
study.optimize(objective, n_trials=200)
```

**Attention :** Toujours faire la WFA après l'optimisation pour valider
hors échantillon.

## Gestion des biais de backtest (les "assassins silencieux")

| Biais | Description | Remède |
|---|---|---|
| **Look-ahead bias** | Utiliser des données non disponibles à l'époque | `shift(1)` sur les signaux |
| **Survivorship bias** | Backtester seulement les actifs qui existent encore | Inclure les actifs delistés |
| **Liquidity bias** | Supposer une exécution parfaite même sur illiquides | Modéliser slippage + spread |
| **Path dependency** | L'ordre des trades impacte le P&L final | Réplication monte-carlo |
| **Selection bias** | Choisir la période qui fait briller | WFA, multi-périodes |
| **Data snooping** | Tester 1000 stratégies, publier la meilleure | DSR, Bonferroni correction |

### Correction du slippage et spreads

Ne jamais supposer une exécution au prix de clôture. Modéliser :

```python
def apply_slippage(df, slippage_bps=2):
    """Applique un slippage de N bps par trade"""
    trades = df[df['position'] != df['position'].shift(1)]
    slippage = slippage_bps / 10000  # 2 bps = 0.02%
    df.loc[trades.index, 'strategy_returns'] -= slippage
    return df
```

## Pièges à éviter

1. **Backtester sur la mauvaise unité de temps :** Les données daily cachent
   la volatilité intraday. Utiliser au moins H1 pour le scalping, H4/D1 pour
   le swing.
2. **Optimiser trop finement :** Un pas de 1 sur une SMA (20, 21, 22...) est
   du bruit. Un pas de 5-10 capture le signal.
3. **Ne pas inclure les coûts de transaction :** Les frais + slippage + spread
   peuvent transformer une stratégie gagnante en perdante.
4. **Backtester seulement en tendance haussière :** Si le backtest couvre
   2010-2021 (bull run de 11 ans), il est inutile. Toujours inclure un marché
   baissier (2022, 2008).
5. **Taille de l'échantillon :** Minimum 100 trades pour que les métriques
   soient statistiquement significatives. 500+ pour un vrai test.
6. **Confondre corrélation et causalité :** Une stratégie qui marche sur
   AAPL ne marchera pas sur TSLA. Backtester sur plusieurs actifs.
7. **Levenier :** Une stratégie avec Sharpe=0.5 mais levier 10x donne des
   rendements incroyables... jusqu'au premier drawdown qui liquide tout.
   Sharpe est neutre au levier — toujours regarder le drawdown.

## Vérification

- [ ] Le look-ahead bias est vérifié (signal = position après shift(1))
- [ ] Les coûts de transaction (slippage 2-5bps + spread) sont inclus
- [ ] Au moins 2 périodes de marché différentes sont testées (bull + bear)
- [ ] Walk-forward analysis passée (validation out-of-sample)
- [ ] Minimum 100 trades dans l'historique
- [ ] Sharpe > 1.0 en out-of-sample avant d'aller en prod
- [ ] DSR > 0.95 si optimisation multi-paramètres

## Skills liés

- `ml-trading-prediction` — features ML pour le backtest
- `position-sizing-kelly` — allocation optimale post-backtest
- `market-analysis` — analyse technique de base