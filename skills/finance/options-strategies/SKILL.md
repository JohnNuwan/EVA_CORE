---
name: options-strategies
description: >-
  Concevoir, analyser et exécuter des stratégies d'options multi-legs :
  spreads verticaux (call/put spread), straddles, strangles, butterflies,
  condors, collars, covered calls, ratio spreads, calendars, diagonals.
  Payoff diagrams, breakeven, max profit/loss, Greeks du spread, selection
  de strike et échéance.
category: finance
---

# Stratégies d'Options — Spreads, Combinaisons & Payoffs

## Présentation

Les stratégies d'options permettent de construire des profils de risque/
rendement impossibles à obtenir avec des positions linéaires (actions,
futures). Ce skill couvre toutes les stratégies standard, leur analyse
quantitative et leur sélection selon le contexte de marché.

**Déclencheurs :** "stratégie options", "call spread", "put spread",
"straddle", "strangle", "butterfly", "condor", "collar", "covered call",
"ratio spread", "calendar spread", "diagonal spread", "options multi-leg",
"profit diagram", "payoff".

## Catégories de Stratégies

### 1. Stratégies Directionnelles (bullish / bearish)

| Stratégie | Construction | Max Profit | Max Loss | Break-even |
|---|---|---|---|---|
| **Long Call** | Achat d'un call | Illimité | Premium payé | Strike + Premium |
| **Long Put** | Achat d'un put | Strike - Premium | Premium payé | Strike - Premium |
| **Bull Call Spread** | Achat call K1 + vente call K2 | (K2-K1) - net debit | Débit net | K1 + débit |
| **Bear Put Spread** | Achat put K2 + vente put K1 | (K2-K1) - net debit | Débit net | K2 - débit |
| **Call Ratio Backspread** | Vente 1 call K1 + achat 2 calls K2 | Potentiel illimité à la hausse | (K2-K1) - credit | 2*K2-K1 + credit |
| **Put Ratio Backspread** | Vente 1 put K2 + achat 2 puts K1 | Potentiel illimité à la baisse | (K2-K1) - credit | K1 - (credit) |

### 2. Stratégies de Volatilité

| Stratégie | Construction | Quand l'utiliser |
|---|---|---|
| **Long Straddle** | Achat Call ATM + Achat Put ATM | Volatilité anticipée (earnings, macro) |
| **Long Strangle** | Achat Call OTM + Achat Put OTM | Volatilité anticipée (moins cher que straddle) |
| **Short Straddle** | Vente Call ATM + Vente Put ATM | Volatilité stable (theta positif) |
| **Short Strangle** | Vente Call OTM + Vente Put OTM | Volatilité stable, theta positif (populaire) |
| **Long Butterfly** | Achat K1 + vente 2*K2 + achat K3 | Volatilité faible, range serré |
| **Long Condor** | Achat K1 + vente K2 + vente K3 + achat K4 | Volatilité faible, range large |
| **Christmas Tree** | Calendrier + spread | Combinaison temps et direction |

### 3. Stratégies de Couverture (Hedging)

| Stratégie | Construction | Usage |
|---|---|---|
| **Protective Put** | Long action + Long Put | Assurance contre baisse |
| **Covered Call** | Long action + Short Call | Générer du revenu (pocher la prime) |
| **Collar** | Long action + Short Call + Long Put | Couverture à coût nul / faible |
| **Put Spread Collar** | Long action + Short Call + Bear Put Spread | Couverture avec risque défini |
| **Married Put** | Long action + Long Put ATM | Position avec stop garanti |

### 4. Stratégies de Temps (Time Decay)

| Stratégie | Construction | Theta |
|---|---|---|
| **Calendar Spread Call** | Short call échéance proche + Long call échéance lointaine | Theta positif (vendre le temps proche, acheter le temps lointain) |
| **Diagonal Spread** | Short call proche + Long call lointain (K différent) | Theta positif + delta directionnel |
| **Double Calendar** | Calendar call + calendar put | Vente de temps pure, direction neutre |

## Payoff Diagrams — Analyse Quantitative

### Profit/Loss pour un spread vertical

```python
def payoff_spread_vertical(S, K_long, K_short, premium_long, premium_short,
                            option_type='call', position=1):
    """
    Payoff pour un spread vertical.
    
    Args:
        S: array de prix du sous-jacent
        K_long: strike de la jambe achetée
        K_short: strike de la jambe vendue
        premium_long: prime payée pour la jambe longue
        premium_short: prime reçue pour la jambe courte
        option_type: 'call' ou 'put'
        position: 1 (bull) ou -1 (bear)
    
    Returns:
        P&L à l'échéance
    """
    net_debit = premium_long - premium_short
    
    if option_type == 'call':
        payoff_long = np.maximum(S - K_long, 0) * position
        payoff_short = -np.maximum(S - K_short, 0) * position
    else:
        payoff_long = np.maximum(K_long - S, 0) * position
        payoff_short = -np.maximum(K_short - S, 0) * position
    
    return (payoff_long + payoff_short) - net_debit

# Exemple : Bull Call Spread AAPL
# Achat Call 200 @ 8.00, Vente Call 210 @ 3.50
S_range = np.linspace(180, 230, 100)
pnl = payoff_spread_vertical(S_range, 200, 210, 8.0, 3.5, 'call', 1)
# Max profit = 210-200 - (8-3.5) = 5.5
# Max loss = 8-3.5 = 4.5
# Breakeven = 200 + 4.5 = 204.5
```

### Greeks du spread

```python
def spread_greeks(S, K1, K2, T, r, sigma, option_type='call', ratio=1):
    """
    Calcule les Greeks combinés d'un spread vertical.
    Les Greeks d'un spread = Greek(jambe longue) - Greek(jambe courte).
    """
    from options_pricing import delta, gamma, theta, vega
    
    # Positions : on achète K1 et vend K2
    delta_net = delta(S, K1, T, r, sigma, option_type) * ratio \
              - delta(S, K2, T, r, sigma, option_type) * ratio
    gamma_net = gamma(S, K1, T, r, sigma) * ratio \
              - gamma(S, K2, T, r, sigma) * ratio
    theta_net = theta(S, K1, T, r, sigma, option_type) * ratio \
              - theta(S, K2, T, r, sigma, option_type) * ratio
    vega_net = vega(S, K1, T, r, sigma) * ratio \
             - vega(S, K2, T, r, sigma) * ratio
    
    return {'delta': delta_net, 'gamma': gamma_net,
            'theta': theta_net, 'vega': vega_net}
    
# Les spreads verticaux ont un vega net faible (bon pour les stratégies
# de volatilité stable)
```

## Sélection des Strikes et Échéances

### Par scénario de marché

| Contexte | Stratégie | Strike | Échéance |
|---|---|---|---|
| **Fort haussier (earnings beat)** | Long Call | ATM ou OTM-1 | 30-45 jours |
| **Haussier modéré** | Bull Call Spread | K1=ATM, K2=OTM+2 | 45-60 jours |
| **Baissier modéré** | Bear Put Spread | K1=ATM, K2=OTM+2 | 45-60 jours |
| **Volatilité élevée anticipée** | Straddle ATM | ATM | Jusqu'à l'event + 7j |
| **Volatilité élevée, budget limité** | Strangle OTM | OTM+1 ou +2 | Jusqu'à l'event + 7j |
| **Range serré, theta play** | Short Strangle | OTM+2 ou +3 | 30-45 jours (theta max) |
| **Range indéfini, pas de biais** | Butterfly / Condor | ATM +-1 | 30-45 jours |
| **Couverture de portefeuille** | Put Spread | 5-10% OTM | 60-90 jours (roll) |
| **Générer du revenu** | Covered Call | OTM+2 ou +3 | 30 jours (roll chaque mois) |

### Règle d'or : 30-45 jours

La décroissance temporelle (theta) est maximale dans les 30-45 derniers jours
avant l'échéance. C'est la meilleure période pour les vendeurs d'options,
et la pire pour les acheteurs.

- **Vendeur** : Vendre à T+45, racheter à T+7 (éviter le gamma spike final)
- **Acheteur** : Acheter à T+60+, vendre avant T+30

## Analyse des Probabilités

### Probabilité de finir ITM

```python
def prob_itm(S, K, T, r, sigma, option_type='call'):
    """
    Probabilité (neutre au risque) que l'option finisse ITM.
    Approximée par N(d2) pour call, N(-d2) pour put.
    """
    d2 = (np.log(S / K) + (r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    if option_type == 'call':
        return norm.cdf(d2)
    else:
        return 1 - norm.cdf(d2)

# Put 5% OTM, 45j, σ=25% → prob ≈ 23%
# Call 5% OTM, 45j, σ=25% → prob ≈ 25%
```

### Probability of Profit (POP)

```python
def pop_strangle(S, K_put, K_call, T, r, sigma, premium_received):
    """
    POP pour un short strangle : probabilité que les deux options expirent OTM.
    """
    d2_put = (np.log(S / K_put) + (r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2_call = (np.log(S / K_call) + (r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    
    prob_put_itm = norm.cdf(-d2_put)  # Put ITM si S < K_put
    prob_call_itm = norm.cdf(d2_call)  # Call ITM si S > K_call
    
    return 1 - (prob_put_itm + prob_call_itm)
```

## Exécution et Gestion des Positions

### Ordres pour options multi-legs

```python
# Les brokers proposent des ordres combinés pour les spreads
# Format générique :
order = {
    "legs": [
        {"side": "BUY",  "option": "AAPL 20260725 200 C", "qty": 1},
        {"side": "SELL", "option": "AAPL 20260725 210 C", "qty": 1}
    ],
    "order_type": "NET_DEBIT",  # ou NET_CREDIT
    "limit_price": 4.50,
    "time_in_force": "DAY"
}
```

### Gestion des positions

| Situation | Action |
|---|---|
| **Spread en profit proche de max** | Prendre le profit (pas de greed) |
| **Short strangle qui approche un strike** | Rouler (roll up/down) ou ajuster |
| **Long straddle après gros move** | Vendre le côté gagnant, garder le perdant |
| **Covered call deep ITM** | Laisser assigner ou rouler |
| **Spread atteint 50% de perte max** | Couper (stop loss mental) |

## Pièges à éviter

1. **Short strangle pendant les earnings** : L'IV est élevée (bonne prime)
   mais le gap overnight peut blow un strike. Éviter ou décaler largement.
2. **Gamma risk sur short options proches de l'échéance** : Les 7 derniers
   jours, le gamma explose. Un petit mouvement peut faire perdre des mois
   de theta en un jour. Sortir des shorts avant T-7.
3. **Pin risk** : À l'échéance, si le sous-jacent termine exactement au
   strike, l'assignation est incertaine. Ne pas garder de shorts ATM à
   l'échéance.
4. **Liquidité des options lointaines** : Spread bid-ask des options à 6+
   mois peut être 20-30% du prix. Favoriser les échéances < 90 jours.
5. **Sur-trading des options** : Frais de commission + spread. Un spread
   à 4 jambes coûte 4x en frais. Calculer le breakeven frais inclus.
6. **Vega quand l'IV est au plus bas** : Les short strangles en IV basse
   (VIX < 12) rapportent peu et risquent une expansion soudaine de la vol.
7. **Dividendes sur les calls** : Avant un ex-dividende, les calls ATM/ITM
   perdent de la valeur (le sous-jacent baisse du montant du dividende).
   Ne pas être long call avant un ex-div non protégé.

## Vérification

- [ ] Le payoff diagram complet est tracé (profit/loss à chaque prix)
- [ ] Les breakeven (souvent 2 pour les non-linéaires) sont calculés
- [ ] Le max profit et max loss sont connus avant l'entrée
- [ ] Les Greeks du spread sont calculés (delta net, gamma net, theta net)
- [ ] La POP (probability of profit) est > 50%
- [ ] Le ratio risk/reward du spread est évalué
- [ ] L'échéance est dans la fenêtre theta optimale (30-45j)
- [ ] L'exit plan est défini (profit target + stop loss)

## Skills liés

- `options-pricing-greeks` — pricing et Greeks pour analyser chaque jambe
- `value-at-risk` — intégrer le risque options dans le portefeuille
- `position-sizing-kelly` — allocation adaptée à la complexité des strats options