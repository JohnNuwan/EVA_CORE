---
name: value-at-risk
description: >-
  Calculer et interpréter les mesures de risque financier : Value-at-Risk (VaR)
  paramétrique, historique et Monte-Carlo ; Conditional VaR (CVaR/Expected
  Shortfall) ; Stress tests par scénario ; Risk budgeting et allocation optimale
  sous contrainte de risque ; Décomposition des risques d'un portefeuille.
category: finance
---

# Gestion des Risques Financiers — VaR, CVaR, Stress Tests & Risk Budgeting

## Présentation

La gestion du risque est le fondement de toute stratégie de trading durable.
Ce skill couvre les méthodes standard de mesure du risque, du calcul de la
Value-at-Risk (VaR) aux stress tests avancés, en passant par l'allocation
sous contrainte de risque.

**Déclencheurs :** "VaR", "Value-at-Risk", "CVaR", "Expected Shortfall",
"gestion du risque", "risk management", "stress test", "drawdown",
"risk budget", "allocation risque", "volatilité cible", "ratio de Sharpe",
"gestion de portefeuille".

## Value-at-Risk (VaR)

### Définition

La VaR à p% sur horizon h jours est la perte maximale attendue avec une
probabilité p (généralement 1% ou 5%). Exemple : VaR 95% 1 jour = -2%
signifie qu'il y a 5% de chances de perdre plus de 2% en un jour.

### Méthode 1 : VaR Paramétrique (Variance-Covariance)

```python
import numpy as np
from scipy.stats import norm

def var_parametrique(returns, confidence=0.95, horizon=1):
    """
    VaR paramétrique : suppose que les rendements suivent une loi normale
    """
    mu = returns.mean() * horizon
    sigma = returns.std() * np.sqrt(horizon)
    z = norm.ppf(1 - confidence)
    return mu + z * sigma  # valeur négative = perte

# Exemple
returns = np.random.normal(0.001, 0.02, 1000)  # mock
var_95_1d = var_parametrique(returns, 0.95, 1)
# Retourne ~ -0.0319 (~ -3.2%)
```

**Limites :** Suppose la normalité des rendements (faux : kurtosis > 3,
skew négatif pour les actions).

### Méthode 2 : VaR Historique

```python
def var_historique(returns, confidence=0.95, horizon=1):
    """
    VaR historique : utilise le quantile empirique des rendements passés
    """
    # Annualiser ou ajuster l'horizon
    if horizon > 1:
        # Rolling sum pour horizon > 1
        ret_horizon = returns.rolling(horizon).sum().dropna()
    else:
        ret_horizon = returns
    
    quantile = 1 - confidence
    return np.percentile(ret_horizon, quantile * 100)

# Exemple
var_95_hist = var_historique(returns_series, 0.95, 1)
```

**Avantages :** Pas d'hypothèse de distribution, capture les queues de
distribution réelles.
**Limites :** Dépend de la période choisie, suppose que le passé se répète.

### Méthode 3 : VaR Monte-Carlo

```python
def var_monte_carlo(prices, confidence=0.95, n_simulations=10000, horizon=1):
    """
    VaR Monte-Carlo : simule des trajectoires de prix aléatoires
    """
    log_returns = np.log(prices / prices.shift(1)).dropna()
    mu = log_returns.mean()
    sigma = log_returns.std()
    
    # Simulation de trajectoires
    last_price = prices.iloc[-1]
    simulations = []
    
    for _ in range(n_simulations):
        # GBM (Geometric Brownian Motion)
        random_shocks = np.random.normal(mu, sigma, horizon)
        drift = (mu - 0.5 * sigma**2) * horizon
        price_path = last_price * np.exp(drift + random_shocks.sum())
        simulations.append(price_path)
    
    losses = (np.array(simulations) - last_price) / last_price
    return np.percentile(losses, (1 - confidence) * 100)

# VaR 99% Monte-Carlo sur 1 jour
var_99_mc = var_monte_carlo(df['close'], 0.99, 50000, 1)
```

## Conditional VaR (CVaR / Expected Shortfall)

La CVaR est la perte **moyenne** au-delà du seuil VaR. Plus robuste que
la VaR car elle capture la queue de distribution.

```python
def cvar(returns, confidence=0.95):
    """Expected Shortfall (CVaR) = moyenne des pertes au-delà de VaR"""
    var = var_historique(returns, confidence)
    return returns[returns <= var].mean()

# CVaR 95% = ~3.5-4% pour un portefeuille actions (contre ~2.5% VaR 95%)
```

**Réglementaire :** Bâle III impose l'Expected Shortfall (CVaR) au lieu de
la VaR depuis 2019. La CVaR est plus conservative.

## Risk Decomposition (Décomposition des risques)

Comprendre d'où vient le risque (par actif, par secteur, par facteur) :

```python
def risk_contribution(weights, cov_matrix):
    """
    Calcule la contribution de chaque actif au risque total du portefeuille.
    Sum(risk_contrib) = portefeuille std
    """
    port_std = np.sqrt(weights @ cov_matrix @ weights)
    marginal_risk = (cov_matrix @ weights) / port_std
    risk_contrib = weights * marginal_risk / port_std
    return risk_contrib  # proportion (sum = 1.0)

# Exemple : 3 actifs
weights = np.array([0.5, 0.3, 0.2])
cov = np.array([[0.04, 0.01, 0.005],
                [0.01, 0.09, 0.002],
                [0.005, 0.002, 0.16]])
rc = risk_contribution(weights, cov)
# Si rc = [0.30, 0.40, 0.30] -> l'actif 2 contribue 40% du risque avec 30% du poids
```

**Risk Parity :** Ajuster les poids pour que chaque actif contribue
également au risque (popularisé par Bridgewater All Weather).

## Stress Tests

### Scénarios macro prédéfinis

```python
scenarios = {
    "2008 Crisis":          {"equities": -0.40, "bonds": +0.10, "gold": +0.15, "oil": -0.60},
    "2020 Covid":           {"equities": -0.35, "bonds": +0.05, "gold": +0.08, "oil": -0.55},
    "2022 Inflation":       {"equities": -0.18, "bonds": -0.13, "gold": -0.05, "oil": +0.10},
    "2024 Carry Unwind":    {"equities": -0.10, "bonds": +0.02, "gold": +0.03, "oil": -0.08},
    "Stagflation":          {"equities": -0.25, "bonds": -0.10, "gold": +0.20, "oil": +0.15},
    "US Default (tail risk)": {"equities": -0.50, "bonds": -0.20, "gold": +0.40, "oil": -0.30},
}

def stress_test(portfolio, scenarios):
    """Applique chaque scénario au portefeuille et calcule la perte"""
    results = {}
    for name, shocks in scenarios.items():
        pnl = 0
        for asset, weight in portfolio.items():
            if asset in shocks:
                pnl += weight * shocks[asset]
        results[name] = pnl
    return results

# Exemple : portefeuille 60/40 actions/obligations
portfolio = {"equities": 0.60, "bonds": 0.40}
stress_test(portfolio, scenarios)
# → {'2008 Crisis': -0.20, '2022 Inflation': -0.16, 'Covid': -0.19, ...}
```

### Stress test personnalisé avec corrélations extrêmes

```python
def stress_correlation_shock(cov_matrix, shock_factor=2.0):
    """
    Simule un choc de corrélation : en crise, toutes les corrélations
    convergent vers 1 (tout baisse en même temps).
    """
    std = np.sqrt(np.diag(cov_matrix))
    corr = cov_matrix / np.outer(std, std)
    # Forcer les corrélations à 0.7-0.9 (pas 1.0, un peu de diversité résiduelle)
    corr_shock = np.clip(corr + shock_factor * 0.3, 0.7, 0.99)
    # Reconstruire la matrice de covariance
    return corr_shock * np.outer(std, std)
```

## Drawdown Management

```python
def max_drawdown(equity_curve):
    """Maximum drawdown (MDD) = plus grande perte pic→creux"""
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    return drawdown.min(), drawdown.idxmin()

def recovery_time(equity_curve, drawdown_threshold=-0.10):
    """Temps de récupération après un drawdown de -10%"""
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    in_drawdown = drawdown < drawdown_threshold
    # Compter les périodes consécutives en drawdown
    groups = (in_drawdown != in_drawdown.shift()).cumsum()
    drawdown_periods = groups[in_drawdown].value_counts()
    return drawdown_periods.max()  # en barres
```

**Règles de gestion du drawdown :**
- **Réduction de taille** : Si drawdown > seuil A → réduire taille de 50%
- **Stop trading** : Si drawdown > seuil B (ex: -20%) → arrêt complet,
  analyse des causes, pas de reprise avant validation
- **Cooling period** : Après un stop, attendre N jours avant de recommencer
- **Scale-in progressif** : Reprendre à 25%, puis 50%, puis 100%

## Risk Budgeting

### Allocation à volatilité cible

```python
def target_vol_portfolio(assets_returns, target_vol=0.12):
    """Trouver le levier pour atteindre une volatilité cible"""
    port_vol = assets_returns.std()  # volatilité du portefeuille actuel
    leverage = target_vol / port_vol
    return min(leverage, 3.0)  # cap à 3x max

# Contrôle de levier sur un portefeuille long-only
def apply_risk_cap(position_value, equity, max_risk_pct=0.02):
    """
    Calcule la taille de position maximale basée sur le risque.
    max_risk_pct = % du capital risqué sur ce trade
    """
    max_risk_amount = equity * max_risk_pct
    max_position = max_risk_amount / position_value
    return max_position
```

### Risk Parity (allocation équi-risque)

```python
def risk_parity_weights(cov_matrix):
    """
    Calcule les poids Risk Parity : chaque actif contribue également au risque
    total. Résolution itérative (pas de solution analytique).
    """
    from scipy.optimize import minimize
    
    n = len(cov_matrix)
    def objective(weights):
        port_risk = np.sqrt(weights @ cov_matrix @ weights)
        risk_contrib = weights * (cov_matrix @ weights) / port_risk
        target = 1.0 / n
        return np.sum((risk_contrib - target)**2)
    
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
    bounds = [(0, 1) for _ in range(n)]
    result = minimize(objective, np.ones(n)/n, bounds=bounds,
                      constraints=constraints)
    return result.x
```

## Pièges à éviter

1. **VaR sous-estime le risque extrême** : La VaR 99% ignore ce qui se passe
   dans le 1% restant. La CVaR est toujours plus conservative.
2. **Corrélations instables en crise** : Les corrélations doublent ou triplent
   en stress (tout corrèle à 1 en 2008). Ne pas utiliser la matrice historique
   pour les stress tests.
3. **Période d'estimation trop courte** : Un an de données quotidiennes = 252
   points. Pour VaR 99%, seulement 2-3 observations dans la queue. Minimum
   3-5 ans recommandé.
4. **Liquidité non modélisée** : La VaR suppose qu'on peut sortir à tout
   moment. Sur les petits caps, crypto altcoins, obligations corporate, la
   liquidité disparaît en crise → la VaR sous-estime massivement.
5. **Sur-optimisation du risk budgeting** : Risk parity sur données récentes
   va concentrer le risque. Utiliser des matrices shrinkées (Ledoit-Wolf).
6. **Oublier le risque de change** : Un portefeuille US investi en Europe a
   un risque EUR/USD. Hedging FX obligatoire.
7. **Levier mal calibré** : Levier 3x sur un portefeuille à volatilité 15%
   = volatilité effective 45% → VaR 99% 1-jour ~ -8%. En drawdown de 30%,
   le levier augmente automatiquement (leverage spirale).

## Vérification

- [ ] VaR paramétrique ET historique calculées (comparer les écarts)
- [ ] CVaR mesurée pour les queues extrêmes
- [ ] Stress tests appliqués : 2008, 2020, 2022, stagflation
- [ ] Le drawdown maximum est connu (backtest + pire cas historique)
- [ ] Les seuils de réduction d'exposition sont définis
- [ ] La corrélation de crise est modélisée (pas seulement historique)
- [ ] Risk decomposition effectuée (savoir quel actif contribue le plus)

## Skills liés

- `position-sizing-kelly` — allocation du capital par trade
- `backtesting-strategies` — intégrer le risk management dans le backtest
- `options-pricing-greeks` — risques spécifiques options (gamma, vega, theta)