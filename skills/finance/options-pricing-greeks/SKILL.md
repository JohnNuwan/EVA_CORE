---
name: options-pricing-greeks
description: >-
  Pricing et analyse des options : modèle Black-Scholes, calcul des Greeks
  (Delta, Gamma, Theta, Vega, Rho), volatilité implicite, skew, term structure,
  surface de volatilité. Tree pricing binomial pour options américaines.
  Sensibilités et hedging.
category: finance
---

# Options — Pricing, Greeks & Volatilité Implicite

## Présentation

Les options sont des instruments financiers complexes dont le prix dépend de
6 facteurs : prix du sous-jacent, strike, temps, volatilité, taux d'intérêt,
dividendes. Ce skill couvre le calcul des prix (Black-Scholes, binomial,
Monte-Carlo), les Greeks (sensibilités) et l'analyse de la volatilité
implicite.

**Déclencheurs :** "options", "Black-Scholes", "Greeks", "delta", "gamma",
"theta", "vega", "rho", "volatilité implicite", "IV", "skew", "surface de
vol", "pricing", "call", "put", "hedging".

## Black-Scholes Pricing

### Modèle (1973)

Formule de Black-Scholes pour un call européen :

```
C = S * N(d1) - K * e^(-r*T) * N(d2)
P = K * e^(-r*T) * N(-d2) - S * N(-d1)

d1 = [ln(S/K) + (r + σ²/2) * T] / (σ * √T)
d2 = d1 - σ * √T
```

Où :
- `S` = prix du sous-jacent
- `K` = strike
- `T` = temps jusqu'à l'échéance (années)
- `r` = taux sans risque
- `σ` = volatilité
- `N(·)` = fonction de répartition normale centrée réduite

### Implémentation Python

```python
import numpy as np
from scipy.stats import norm

def black_scholes(S, K, T, r, sigma, option_type='call'):
    """
    Prix Black-Scholes pour option européenne.
    
    Args:
        S: prix du sous-jacent
        K: strike
        T: temps jusqu'à maturité (années)
        r: taux sans risque
        sigma: volatilité annualisée
        option_type: 'call' ou 'put'
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return price

# Exemple : Call AAPL, S=200, K=210, T=30j, r=5%, σ=25%
price = black_scholes(200, 210, 30/365, 0.05, 0.25, 'call')
# ~ 2.85 EUR
```

## Les Greeks

Les Greeks mesurent la sensibilité du prix de l'option à chaque paramètre.

### Delta (Δ) — Sensibilité au sous-jacent

Le Delta mesure la variation du prix de l'option pour une variation de 1 EUR
du sous-jacent.

```python
def delta(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    
    if option_type == 'call':
        return norm.cdf(d1)
    else:
        return -norm.cdf(-d1)

# Delta d'un call ATM (S≈K) avec T=30j → ~0.52
# Delta d'un call ITM deep → ~1.0 (comme être long le sous-jacent)
# Delta d'un put OTM deep → ~0.0
```

**Interprétation :**
- Delta Call : 0 à 1
- Delta Put : -1 à 0
- ATM ~0.5 pour call, ~-0.5 pour put
- Delta ≈ probabilité de finir ITM (approximation)
- Delta-adjusted position : combien d'actions = 1 option

### Gamma (Γ) — Variation du Delta

Le Gamma mesure la variation du Delta pour une variation de 1 EUR du
sous-jacent.

```python
def gamma(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return norm.pdf(d1) / (S * sigma * np.sqrt(T))

# Gamma max à ATM, décroît avec le temps (approche de l'échéance)
# Gamma d'une option ATM à 7j de l'échéance → TRÈS élevé
```

**Gamma risque :** Un portefeuille short gamma (vendeur d'options) gagne
quand le sous-jacent ne bouge pas, mais perd TRÈS vite si le sous-jacent
bouge (gamma négatif = vulnérabilité aux spikes).

### Theta (Θ) — Time Decay

Le Theta mesure la perte de valeur de l'option par jour (time decay).
Toujours négatif pour l'acheteur, positif pour le vendeur.

```python
def theta(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    theta_call = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                 - r * K * np.exp(-r * T) * norm.cdf(d2))
    
    if option_type == 'call':
        return theta_call / 365  # par jour
    else:
        theta_put = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                    + r * K * np.exp(-r * T) * norm.cdf(-d2))
        return theta_put / 365

# Theta d'un call ATM 30j → ~-0.02 par jour (perd ~2 centimes/jour)
# Theta s'accélère exponentiellement dans les 30 derniers jours
```

### Vega (ν) — Sensibilité à la Volatilité

Le Vega mesure la variation du prix pour une variation de 1% de la volatilité
implicite.

```python
def vega(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    return S * norm.pdf(d1) * np.sqrt(T) / 100  # pour 1% de vol

# Vega max à ATM, augmente avec le temps
# Vega d'une option ATM 60j → ~0.15-0.25
# Vega = 0 à l'échéance
```

**Vega risque :** Long Vega = profite d'une hausse de la volatilité implicite.
Short Vega = profite d'une baisse de la volatilité (décroissance naturelle).
Les IV spikes en crise → short Vega se fait malmener.

### Rho (ρ) — Sensibilité au Taux

Le Rho mesure la variation du prix pour une variation de 1% du taux d'intérêt.

```python
def rho(S, K, T, r, sigma, option_type='call'):
    d2 = (np.log(S / K) + (r - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    
    if option_type == 'call':
        return K * T * np.exp(-r * T) * norm.cdf(d2) / 100  # pour 1% de taux
    else:
        return -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

# Rho est généralement le Greek le moins important (sauf pour les options longues)
# Rho d'un call 1 an ATM → ~0.05 (faible impact)
```

### Tableau récapitulatif des Greeks

| Greek | Symbole | Unité | Call Long | Put Long | Call Short | Put Short |
|---|---|---|---|---|---|---|
| Delta | Δ | $/$ | + | - | - | + |
| Gamma | Γ | Δ/$ | + | + | - | - |
| Theta | Θ | $/jour | - | - | + | + |
| Vega | ν | $/%vol | + | + | - | - |
| Rho | ρ | $/%taux | + | - | - | + |

## Volatilité Implicite (IV)

### Calcul de l'IV par inversion de Black-Scholes

L'IV est la volatilité qui, injectée dans Black-Scholes, donne le prix de
marché de l'option.

```python
def implied_volatility(market_price, S, K, T, r, option_type='call'):
    """
    Calcule la volatilité implicite en inversant Black-Scholes.
    Utilise la méthode de Newton-Raphson.
    """
    from scipy.optimize import brentq
    
    def price_diff(sigma):
        return black_scholes(S, K, T, r, sigma, option_type) - market_price
    
    try:
        return brentq(price_diff, 0.001, 5.0)  # IV 0.1% à 500%
    except ValueError:
        # Cas extrêmes (prix trop bas/haut)
        return np.nan
```

### Skew (sourire de volatilité)

Le skew décrit la forme de l'IV en fonction du strike.

- **Equity skew** : IV plus haute pour les puts OTM que calls OTM
  (protection contre les baisses est chère — peur du marché)
- **FX smile** : IV symétrique, plus haute loin de ATM
  (événements extrêmes dans les deux directions)
- **Commodity skew** : IV plus haute pour les calls (risque de pénurie)

```python
def analyze_skew(options_chain):
    """
    Analyse le skew à partir d'une chaîne d'options.
    """
    atm_strike = options_chain['strike'].iloc[(options_chain['strike'] - S).abs().argmin()]
    
    options_chain['moneyness'] = options_chain['strike'] / atm_strike
    options_chain['iv'] = options_chain.apply(
        lambda r: implied_volatility(r['price'], S, r['strike'], T, r), axis=1)
    
    # Skew = difference entre put 25-delta et call 25-delta
    return options_chain
```

### Term Structure (structure par terme)

L'IV varie aussi par échéance. Normalement, les options longues ont une IV
plus basse (mean-reversion de la volatilité) :

- **Normal (contango)** : IV courte < IV longue (marché calme)
- **Inverse (backwardation)** : IV courte > IV longue (stress immédiat)
- **Flat** : peu de différence (anticipations neutres)

### Surface de Volatilité

La surface de vol combine skew + term structure en 3D (strike × time × IV).
Utile pour :
- Repérer les anomalies de pricing (arbitrage)
- Calibrer des modèles de volatilité stochastique
- Valoriser des produits exotiques

## Pricing par Arbre Binomial (Options Américaines)

Les options américaines (exercice avant échéance) nécessitent un arbre :

```python
def binomial_tree(S, K, T, r, sigma, n=100, option_type='call'):
    """
    Prix d'une option (américaine) par arbre binomial de Cox-Ross-Rubinstein.
    """
    dt = T / n
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    discount = np.exp(-r * dt)
    
    # Prix à maturité
    prices = np.zeros(n + 1)
    for i in range(n + 1):
        S_T = S * (u**i) * (d**(n - i))
        if option_type == 'call':
            prices[i] = max(S_T - K, 0)
        else:
            prices[i] = max(K - S_T, 0)
    
    # Remonter l'arbre avec early exercise check
    for step in range(n - 1, -1, -1):
        for i in range(step + 1):
            S_t = S * (u**i) * (d**(step - i))
            prices[i] = discount * (p * prices[i + 1] + (1 - p) * prices[i])
            
            # Early exercise (américain)
            if option_type == 'call':
                prices[i] = max(prices[i], S_t - K)
            else:
                prices[i] = max(prices[i], K - S_t)
    
    return prices[0]
```

## Pièges à éviter

1. **Black-Scholes suppose une volatilité constante** : En réalité, la
   volatilité implicite varie (skew, term structure). Utiliser la surface
   de vol, pas une IV unique.
2. **Le Gamma explose près de l'échéance** : Une option ATM à 1 jour de
   l'échéance a un Gamma énorme. Un petit mouvement du sous-jacent change
   radicalement sa valeur → très risqué pour les shorts gamma.
3. **Theta ≠ "gain garanti" pour le vendeur** : Un mouvement adverse du
   sous-jacent peut anéantir tout le theta en une heure.
4. **Volatilité implicite ≠ volatilité réalisée** : Vendre des options
   parce que "l'IV est élevée" suppose que l'IV va baisser. L'IV peut
   rester élevée longtemps (marché anxieux).
5. **Les options américaines valent plus que les européennes** : Ne pas
   utiliser Black-Scholes (européen) pour des options américaines.
   Utiliser l'arbre binomial.
6. **Dividendes** : Oublier les dividendes dans le pricing sous-estime le
   prix des puts et surestime celui des calls. Corriger avec le modèle
   Black-Scholes-Merton (S réduit de la valeur actuelle des dividendes).
7. **Liquidité des options** : Les options OTM lointaines et les échéances
   longues sont illiquides. Le spread bid-ask peut être 50%+ du prix.

## Vérification

- [ ] Les 5 Greeks sont calculables pour toute option
- [ ] Le skew par strike est analysé
- [ ] La term structure par échéance est extraite
- [ ] La surface de volatilité peut être construite
- [ ] Les options américaines utilisent le pricing binomial
- [ ] Les dividendes sont inclus si applicables
- [ ] Le spread bid-ask est vérifié avant tout trade

## Références

- `references/options-greeks-cheatsheet.md` — formule des Greeks à portée
  de main (à créer si nécessaire)

## Skills liés

- `options-strategies` — construire des stratégies multi-legs
- `value-at-risk` — intégrer le gamma risk et vega risk dans le risk model