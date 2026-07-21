---
name: ml-trading-prediction
description: >-
  Appliquer le machine learning aux marchés financiers : feature engineering
  à partir de données OHLCV, ordre book, sentiment ; modèles supervisés
  (Random Forest, XGBoost, LSTM, Transformers) pour prédiction directionnelle
  et régression de prix ; walk-forward validation ; régimes de marché ;
  gestion des non-stationnarités.
category: finance
---

# Machine Learning pour le Trading — Prédiction de Prix & Signaux

## Présentation

Le ML appliqué au trading est radicalement différent du ML classique.
Les séries financières sont **non stationnaires**, **bruitées** (SNR < 1),
et la distribution change dans le temps. Ce skill couvre le pipeline complet :
feature engineering → modèles → validation adaptée → production.

**Déclencheurs :** "machine learning trading", "ML finance", "prédiction prix",
"features trading", "LSTM trading", "XGBoost trading", "Random Forest trading",
"modèle prédictif", "signal ML", "deep learning trading".

## Data Pipeline

### Sources de données

| Source | Type | API | Limites |
|---|---|---|---|
| **Yahoo Finance** | OHLCV, actions/ETF | `yfinance` | 2k req/h (rate limit) |
| **Binance** | OHLCV, order book, trades | `python-binance` / CCXT | Gratuit, temps réel |
| **Alpha Vantage** | OHLCV, fondamentaux | `alpha_vantage` | 5 req/min (gratuit) |
| **Polygon.io** | OHLCV, options, news | `polygon` | Payant ($29-199/mois) |
| **FRED** | Macro données | `fredapi` | Gratuit (limité) |
| **CoinGecko** | Crypto + on-chain | API REST | 30 req/min gratuit |
| **Intrinio** | Fondamentaux US | API | Payant |
| **Lobster / LOBSTER** | Order book reconstitué | Fichiers | Gratuit pour Nasdaq |

### Feature Engineering

#### Features de prix et volatilité

```python
def price_features(df):
    """Génère les features de base à partir d'OHLCV"""
    features = pd.DataFrame(index=df.index)
    
    # Rendements
    features['return_1'] = df['close'].pct_change(1)
    features['return_5'] = df['close'].pct_change(5)
    features['return_20'] = df['close'].pct_change(20)
    
    # Log-returns (normalité approchée)
    features['log_return'] = np.log(df['close'] / df['close'].shift(1))
    
    # Volatilités (rolling std annualisée)
    features['vol_5'] = df['close'].pct_change().rolling(5).std() * np.sqrt(252)
    features['vol_20'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)
    
    # Range (volatilité intra-bar)
    features['range'] = (df['high'] - df['low']) / df['close']
    features['body'] = abs(df['close'] - df['open']) / df['close']
    
    # Garman-Klass volatility (plus robuste que close-to-close)
    features['gk_vol'] = np.sqrt(
        (np.log(df['high']/df['low'])**2) / 2
        - (2*np.log(2)-1) * np.log(df['close']/df['open'])**2
    )
    
    return features
```

#### Features techniques

```python
def technical_features(df):
    """Indicateurs techniques comme features ML"""
    import pandas_ta as ta
    features = pd.DataFrame(index=df.index)
    
    # RSI avec plusieurs window
    for w in [6, 14, 21]:
        features[f'rsi_{w}'] = ta.rsi(df['close'], w)
    
    # MACD avec signaux
    macd = ta.macd(df['close'])
    features['macd'] = macd['MACD_12_26_9']
    features['macd_signal'] = macd['MACDs_12_26_9']
    features['macd_hist'] = macd['MACDh_12_26_9']
    
    # Bollinger %B (position dans les bandes)
    bb = ta.bbands(df['close'])
    features['bb_%b'] = bb['BBB_20_2.0']
    features['bb_width'] = bb['BBU_20_2.0'] - bb['BBL_20_2.0']
    
    # ATR (Average True Range)
    features['atr_14'] = ta.atr(df['high'], df['low'], df['close'], 14)
    
    # Moyennes mobiles ratios
    for w1, w2 in [(10, 30), (20, 50), (50, 200)]:
        sma1 = ta.sma(df['close'], w1)
        sma2 = ta.sma(df['close'], w2)
        features[f'sma_{w1}_{w2}_ratio'] = sma1 / sma2
    
    return features
```

#### Features de market microstructure

```python
def microstructure_features(df):
    """Features de microstructure (nécessite du tic par tic)"""
    # Roll spread (bid-ask implicite)
    autocov_1 = df['return_1'].autocorr(lag=1)
    roll_spread = 2 * np.sqrt(-autocov_1) if autocov_1 < 0 else 0
    
    # Amihud Illiquidity Ratio
    df['amihud'] = abs(df['return_1']) / (df['volume'] * df['close'])
    
    # VPIN (Volume-synchronized Probability of Informed Trading)
    # Nécessite order book, mais approximation avec volume bars
    df['vpin'] = abs(df['volume'].diff()) / df['volume'].rolling(50).sum()
    
    return df
```

#### Target Engineering

```python
# Target 1 : Direction binaire (hausse/baisse)
df['target_1d'] = (df['close'].shift(-1) > df['close']).astype(int)  # 1 = hausse

# Target 2 : Direction sur horizon N
def target_future_return(df, horizon=5):
    return (df['close'].shift(-horizon) > df['close']).astype(int)

# Target 3 : Régression (rendement futur)
df['target_reg'] = df['close'].pct_change(-1)

# Target 4 : Quantile returns (multi-class)
def target_quantile(df, q=3):
    ret = df['close'].pct_change(-1)
    bins = pd.qcut(ret.dropna(), q=q, labels=False)
    return bins  # 0=baisser, 1=neutre, 2=monter

# Target 5 : Triple Barrier (départ/stop/limite — Lopez de Prado)
# Utiliser `mlfinlab.labeling.get_events()` pour le labelling avancé
```

## Modèles ML pour le trading

### Tableau comparatif

| Modèle | Type | Forces | Faiblesses |
|---|---|---|---|
| **Logistic Regression** | Linéaire | Rapide, interprétable | Sous-performe, linéaire |
| **Random Forest** | Ensemble | Robuste, features importantes | Overfit sur bruit, pas extrapolation |
| **XGBoost / LightGBM** | Gradient Boosting | Top tabulaire, vitesses | Pas de séquence |
| **LSTM** | Deep Learning séquentiel | Capture dépendances temporelles | Lent à entraîner, overfit facile |
| **Transformer (Time Series)** | Attention | Long range, parallel training | Données massives nécessaires |
| **CNN (Temporal)** | 1D Conv | Patterns locaux, moins paramètres | Pas de long range |
| **HMM** | Markov caché | Régimes de marché | États figés |
| **Gaussian Process** | Bayésien | Incertitude native | Lent >10k points |

### Exemple : XGBoost pour prédiction binaire

```python
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score

def train_xgboost_model(X_train, y_train, X_val, y_val):
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.01,
        subsample=0.8,
        colsample_bytree=0.8,
        early_stopping_rounds=50,
        eval_metric='logloss'
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    return model

# Walk-forward validation
def walk_forward_xgboost(df, features_cols, target_col, window_train=500, window_test=50):
    """Walk-forward : train sur 500 bars, test sur 50, slide"""
    df = df.dropna().reset_index(drop=True)
    models, predictions = [], []
    
    start = window_train
    while start + window_test < len(df):
        train = df.iloc[start - window_train : start]
        test = df.iloc[start : start + window_test]
        
        model = train_xgboost_model(
            train[features_cols], train[target_col],
            test[features_cols], test[target_col]
        )
        preds = model.predict(test[features_cols])
        predictions.extend(preds)
        models.append(model)
        start += window_test
    
    return predictions, models
```

### Exemple : LSTM pour prédiction de séquence

```python
import torch
import torch.nn as nn

class LSTMPredictor(nn.Module):
    def __init__(self, n_features, hidden_dim=128, n_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden_dim, n_layers,
                           batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_dim, 3)  # classes baisser/neutre/monter
        
    def forward(self, x):
        # x: (batch, seq_len, n_features)
        lstm_out, (h_n, c_n) = self.lstm(x)
        last_hidden = h_n[-1, :, :]  # dernier état caché
        return self.fc(last_hidden)

def create_sequences(df, features_cols, seq_len=60):
    """Crée des séquences de seq_len pour LSTM"""
    data = df[features_cols].values
    X, y = [], []
    for i in range(seq_len, len(data)):
        X.append(data[i-seq_len:i])
        y.append(df['target_class'].iloc[i])
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)
```

## Non-stationnarité et régimes de marché

### Détection de régimes

Les marchés changent de régime (tendance, range, crise). Le modèle doit
s'adapter :

```python
# Régime de volatilité (ex : VIX pour SPX)
df['vol_regime'] = pd.cut(df['vol_20'], bins=[0, 0.15, 0.35, np.inf],
                           labels=['low', 'med', 'high'])

# Régime de tendance (ADX)
import pandas_ta as ta
df['adx'] = ta.adx(df['high'], df['low'], df['close'])

# Régime de corrélation (BTC vs SPX)
corr_rolling = df['btc_return'].rolling(60).corr(df['spx_return'])
df['corr_regime'] = np.where(corr_rolling > 0.5, 'risk_on',
                    np.where(corr_rolling < -0.3, 'hedge', 'neutral'))
```

### Adaptive model retraining

Le retraining périodique n'est pas idéal. Stratégies :

1. **Time-based** : retrain toutes les semaines (naïf)
2. **Drift-based** : retrain si la distribution des features change
   (KS-test entre données récentes et train set)
3. **Performance-based** : retrain si Sharpe glissant < seuil
4. **Regime-switching** : un modèle par régime (coûteux mais performant)

```python
from scipy.stats import ks_2samp

def should_retrain(features_recent, features_train, threshold=0.05):
    """Détecte le concept drift via KS-test"""
    for col in features_recent.columns:
        stat, p_value = ks_2samp(features_recent[col], features_train[col])
        if p_value < threshold:
            return True  # drift détecté
    return False
```

## Métriques de validation spécifiques au trading

| Métrique | Formule | Pourquoi |
|---|---|---|
| **Precision** | TP / (TP + FP) | Combien de signaux long étaient corrects |
| **Recall** | TP / (TP + FN) | Combien de vrais hausses ont été captées |
| **F1-score** | 2 * P * R / (P + R) | Équilibre |
| **Accuracy** | (TP + TN) / total | Trompeur si classes déséquilibrées |
| **MCC** | Matthews Corr Coef | Robuste au déséquilibre |
| **Sharpe prédictif** | Sharpe out-of-sample | Corrigé de l'overfit, pratique |

**Ne jamais** se fier à l'accuracy seule sur du trading : si les classes
sont 60/40, un modèle qui prédit toujours "hausse" a 60% d'accuracy mais
est inutile.

## Pièges à éviter

1. **Data leakage :** Utiliser des données futures dans les features (ex:
   moyenne mobile qui inclut la barre actuelle → `shift(1)` obligatoire).
   Vérifier que chaque feature utilise uniquement les données disponibles
   au moment du trade.
2. **Normalisation glissante :** StandardScaler fit sur tout l'historique
   (le futur fuit dans le passé). Utiliser un scaler glissant (fit sur
   train seulement, appliqué sur test).
3. **Imbalanced classes :** Les marchés sont ~50/50 (hausse/baisse). Si le
   modèle prédit 80% hausse, suspect. Utiliser class_weight ou smote.
4. **Fuite de rendement :** Si target = rendement du lendemain, ne pas
   inclure de features calculées avec le close du lendemain.
5. **Modèle trop complexe :** Un LSTM avec 1M paramètres sur 10k points
   va mémoriser le bruit. Règle : n_params < n_samples / 10.
6. **Pas de purge temporelle :** La CV classique (K-Fold) mélange passé
   et futur. Toujours utiliser TimeSeriesSplit ou walk-forward.
7. **Corriger pour le multiple testing :** Si vous testez 100 features, 5
   seront significatives par hasard (p<0.05). Utiliser Bonferroni.

## Vérification

- [ ] Le pipeline walk-forward est implémenté (train/val glissants)
- [ ] Il n'y a pas de data leakage (toutes les features sont shiftées)
- [ ] Les coûts de transaction sont intégrés après le signal
- [ ] Le Sharpe out-of-sample dépasse le Sharpe in-sample d'au moins 50%
- [ ] Le modèle est testé sur 2+ régimes de marché différents
- [ ] La détection de drift est en place (ou le retraining est planifié)
- [ ] La normalisation est glissante (pas de fit sur tout l'historique)

## Références

- `references/feature-catalog.md` — catalogue complet de features de pricing,
  microstructure, sentiment, on-chain (à créer si nécessaire)

## Skills liés

- `backtesting-strategies` — framework de backtest
- `position-sizing-kelly` — allocation post-signal
- `value-at-risk` — risk model pour déployer le modèle