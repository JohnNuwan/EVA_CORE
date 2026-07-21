---
name: position-sizing-kelly
description: >-
  Dimensionner les positions de trading selon le critère de Kelly, la gestion
  de drawdown, la volatilité cible et les règles de money management.
  Couvre le Kelly fractionnaire, le Half-Kelly, le Kelly pour stratégies
  multi-actifs, la gestion de la courbe de capital et le contrôle du levier.
category: finance
---

# Position Sizing & Kelly Criterion — Allocation Optimale du Capital

## Présentation

Le dimensionnement des positions est plus important que le signal lui-même.
Une stratégie gagnante avec un mauvais position sizing peut faire faillite ;
une stratégie médiocre avec un bon position sizing peut être rentable.
Ce skill couvre les méthodes mathématiques d'allocation du capital.

**Déclencheurs :** "position sizing", "kelly criterion", "critère de Kelly",
"money management", "taille de position", "lot sizing", "gestion du capital",
"optimal f", "half-kelly", "drawdown control", "volatilité cible".

## Kelly Criterion — Principe

### Formule de base

Le critère de Kelly (1956) maximise la croissance à long terme du capital :

```
Kelly % = (p * b - q) / b
```

Où :
- `p` = probabilité de gagner
- `q` = probabilité de perdre (= 1 - p)
- `b` = ratio odds reçus (gain net / perte nette, ex: 2:1 → b=2)

### Implémentation

```python
def kelly_criterion(win_rate, avg_win, avg_loss):
    """
    Calcule le pourcentage optimal du capital à risquer par trade.
    
    Args:
        win_rate: ratio de trades gagnants (0-1)
        avg_win: gain moyen en unités de risque
        avg_loss: perte moyenne en unités de risque (positive)
    
    Returns:
        f* : fraction optimale du capital
    """
    b = avg_win / avg_loss  # odds ratio
    p = win_rate
    q = 1 - p
    kelly = (p * b - q) / b
    return max(kelly, 0.0)  # pas de pari négatif

# Exemple : stratégie avec 55% win rate, gain moyen 2x la perte
kelly = kelly_criterion(0.55, 200, 100)
# kelly = (0.55 * 2 - 0.45) / 2 = 0.325 → risquer 32.5% du capital
```

**Attention :** Kelly full (>30%) est EXTREMEMENT agressif. Un drawdown
de 30% sur une série de trades perdants est probable.

### Kelly appliqué aux rendements financiers

```python
def kelly_from_returns(strategy_returns):
    """
    Kelly estimate from a series of returns.
    Utilise la formule : f* = μ / σ² (pour une distribution normale)
    """
    mu = strategy_returns.mean()
    sigma2 = strategy_returns.var()
    if sigma2 == 0:
        return 0.0
    return mu / sigma2

# Equivalent mais plus robuste :
def kelly_optimal_f(trades):
    """
    Optimal f (Kelly discret) : maximise la croissance géométrique.
    """
    from scipy.optimize import minimize_scalar
    
    def growth_rate(f):
        if f <= 0 or f >= 1:
            return -np.inf
        # Taux de croissance = sum(log(1 + f * (trade_pl / max_loss)))
        max_loss = abs(min(trades)) if min(trades) < 0 else abs(max(trades))
        returns = [np.log(1 + f * t / max_loss) for t in trades]
        return sum(returns)
    
    result = minimize_scalar(lambda f: -growth_rate(f), bounds=(0.001, 0.999),
                             method='bounded')
    return result.x
```

## Kelly Fractionnaire — Le Compromis

Le Kelly full maximise la croissance mais avec une volatilité extrême :
- Probabilité de drawdown de 50% = f / (1-f) ≈ 50% pour f=0.33
- Le Kelly fractionnaire réduit le risque en sacrifiant une partie de la croissance

```python
def fractional_kelly(win_rate, avg_win, avg_loss, fraction=0.25):
    """
    Fractional Kelly : utiliser une fraction du Kelly optimal.
    
    Args:
        fraction: 0.25 = Quarter Kelly, 0.50 = Half Kelly
    """
    full_kelly = kelly_criterion(win_rate, avg_win, avg_loss)
    return full_kelly * fraction

# Règles empiriques
# Half-Kelly (0.5) : bon compromis croissance/sécurité
# Quarter-Kelly (0.25) : très conservateur, drawdown max ~10-15%
# Kelly full (1.0) : réservé aux stratégies avec edge très fort et drawdown toléré
```

### Pourquoi utiliser Half-Kelly ?

| Fraction | Croissance | Drawdown max estimé | Ruine proba |
|---|---|---|---|
| Full (1.0) | Maximale | 30-50% | 10-15% |
| Half (0.5) | 75% du max | 15-25% | <1% |
| Quarter (0.25) | 44% du max | 7-12% | ~0% |
| Third (0.33) | 60% du max | 10-18% | <1% |

**Recommandation:** Toujours utiliser au maximum Half-Kelly. Quarter-Kelly
pour les stratégies directionnelles agressives.

## Volatilité cible (Target Vol)

### Principe

Ajuster la taille de position pour que la position contribue une volatilité
cible au portefeuille (indépendant du Kelly) :

```python
def target_vol_position_size(portfolio_value, asset_price, asset_vol,
                              target_vol_pct=0.02, atr=None):
    """
    Calcule la taille de position pour une volatilité cible.
    
    Args:
        portfolio_value: valeur du portefeuille (EUR)
        asset_price: prix actuel de l'actif
        asset_vol: volatilité annualisée de l'actif (ex: 0.25)
        target_vol_pct: % du portefeuille de volatilité quotidienne cible
        atr: optionnel, ATR à la place de la volatilité
    
    Returns:
        nombre d'unités à acheter/vendre
    """
    daily_vol = asset_vol / np.sqrt(252)
    position_value = portfolio_value * target_vol_pct / daily_vol
    return position_value / asset_price
```

### Fixed Fractional (Risk % par trade)

```python
def risk_percent_position(portfolio_value, stop_loss_pct, risk_per_trade=0.01):
    """
    Taille de position basée sur le risque par trade.
    
    Args:
        portfolio_value: capital total (EUR)
        stop_loss_pct: % de perte sur la position si SL touché (ex: 0.02)
        risk_per_trade: % du capital à risquer (ex: 0.01 = 1%)
    
    Returns:
        taille de la position en EUR
    """
    max_risk_amount = portfolio_value * risk_per_trade
    position_value = max_risk_amount / stop_loss_pct
    return position_value
```

## Multi-Asset Kelly

Pour un portefeuille multi-actifs, il faut tenir compte des corrélations :

```python
def multi_asset_kelly(expected_returns, cov_matrix, risk_free_rate=0.0):
    """
    Kelly optimal pour N actifs (solution de Markowitz avec maximisation
    de la croissance).
    
    weights_kelly = Σ^{-1} * (μ - r_f)
    """
    from scipy.optimize import minimize
    
    n = len(expected_returns)
    
    def neg_growth(weights):
        port_return = weights @ expected_returns - risk_free_rate
        port_vol = weights @ cov_matrix @ weights
        # Taux de croissance = port_return - 0.5 * port_vol
        return -(port_return - 0.5 * port_vol)
    
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
    bounds = [(-0.2, 0.3) for _ in range(n)]  # shorts et longs
    
    result = minimize(neg_growth, np.ones(n)/n, bounds=bounds,
                      constraints=constraints)
    return result.x
```

## Gestion de la Courbe de Capital (Equity Curve)

### Scaling progressif (compounding)

```python
def scale_position_by_equity(base_position, current_equity, initial_equity,
                              scale_up=True):
    """
    Ajuste la taille des positions en fonction de l'équité.
    """
    growth_factor = current_equity / initial_equity
    
    if scale_up:
        return base_position * growth_factor
    else:
        # Ne scale que si > initial
        return base_position * max(growth_factor, 1.0)
```

### Drawdown-based reduction

```python
def drawdown_adjusted_kelly(full_kelly, current_drawdown, thresholds=None):
    """
    Réduit le Kelly en fonction du drawdown actuel.
    Exemple : -10% → moitié, -20% → stop.
    """
    if thresholds is None:
        thresholds = {0.05: 1.0,    # -5% : Kelly full
                      0.10: 0.5,    # -10% : Half-Kelly
                      0.15: 0.25,   # -15% : Quarter-Kelly
                      0.20: 0.0}    # -20% : STOP
    
    for dd_threshold, factor in sorted(thresholds.items()):
        if current_drawdown >= dd_threshold:
            return full_kelly * factor
    return full_kelly

# Exemple
current_dd = -0.12  # -12% de drawdown
adjusted = drawdown_adjusted_kelly(0.33, current_dd)
# → 0.33 * 0.5 = 0.165 (Half-Kelly)
```

## Anti-Martingale vs Martingale

- **Martingale** : Doubler après une perte (DANGEREUX, ruine garantie)
- **Anti-Martingale** : Augmenter après un gain (prudent, capture les runs)

```python
def anti_martingale_size(base_size, consecutive_wins, multiplier=1.5, max_mult=3.0):
    """
    Anti-Martingale : augmenter la taille après chaque gain consécutif.
    Limité à max_mult fois la taille de base.
    """
    factor = min(1.0 + (multiplier - 1.0) * consecutive_wins, max_mult)
    return base_size * factor

def martingale_risk_warning():
    """
    NE JAMAIS UTILISER LE MARTINGALE.
    La probabilité de ruine est de 100% sur un nombre infini de trades.
    """
    pass
```

## Pièges à éviter

1. **Kelly surestime la taille si l'estimation du win rate est mauvaise :**
   Une erreur de 5% sur le win rate peut doubler le Kelly. Toujours utiliser
   le pire cas de l'intervalle de confiance.
2. **Oublier le slippage :** Le Kelly est calculé sur les returns nets de
   frais. Si les frais transforment un win rate de 55% en 53%, le Kelly
   change drastiquement.
3. **Path dependence :** Une série de 5 pertes consécutives sur Kelly full
   (35% du capital) → portefeuille -90%. Sur Half-Kelly → -50%. Le Kelly
   ne protège PAS des séquences.
4. **Sur-optimiser le Kelly :** Calculer le Kelly sur la meilleure période
   du backtest donne f* trop élevé. Utiliser le Kelly moyen sur toutes les
   fenêtres walk-forward.
5. **Corrélation entre trades :** Le Kelly suppose des trades indépendants.
   Si vos trades sont corrélés (même actif, même horizon), le risque est
   sous-estimé (variance effective plus grande).
6. **Effet de levier non linéaire :** Un Kelly de 50% sur un compte à levier
   10x = 500% d'exposition. Un mouvement de 10% adverse liquide tout.

## Vérification

- [ ] Le Kelly fractionnaire (Half ou Quarter) est utilisé, jamais le full
- [ ] La taille de position est recalculée après chaque trade (équité change)
- [ ] La réduction de taille sur drawdown est implémentée
- [ ] Le slippage et les frais sont inclus dans le calcul de Kelly
- [ ] Les corrélations entre trades sont évaluées
- [ ] Un stop de sécurité (ex: -20% max drawdown) est en place
- [ ] Anti-martingale préféré à martingale (jamais de martingale)

## Skills liés

- `value-at-risk` — cadre de risque pour calibrer le Kelly
- `backtesting-strategies` — backtester le Kelly dans la stratégie
- `options-strategies` — position sizing adapté aux options (gamma risk)