---
name: defi-yield-strategies
description: >-
  Stratégies de rendement en finance décentralisée (DeFi) : yield farming,
  staking, liquidity provision (LP) sur pools stables et volatiles, lending
  (Aave, Compound), restaking (EigenLayer), veTokenomics, optimisation des
  récompenses, impermanent loss hedging, bridges cross-chain, delta-neutral
  strategies. Automatisation on-chain via bots.
category: finance
---

# DeFi — Yield Farming, Staking, LP & Optimisation de Rendement

## Présentation

La finance décentralisée (DeFi) offre des rendements bien supérieurs à la
finance traditionnelle, mais avec des risques supplémentaires (smart contract,
impermanent loss, oracle, bridge, réglementaire). Ce skill couvre les
stratégies de rendement, leur analyse quantitative et leur automatisation.

**Déclencheurs :** "DeFi", "yield farming", "staking", "liquidity pool",
"LP", "Aave", "Compound", "EigenLayer", "veToken", "impermanent loss",
"delta neutral", "lending", "borrowing", "yield optimization", "yield
aggregator", "Lido", "Rocket Pool", "cross-chain", "bridge".

## Stratégies de Base

### ① Lending (Prêt)

Prêter des tokens sur des protocoles de money market.

| Protocole | Chaîne | APY Variable | APY Stable | Risque |
|---|---|---|---|---|
| **Aave** | ETH, Polygon, Avalanche | 2-8% | 3-6% | Smart contract, oracle |
| **Compound** | ETH | 2-5% | N/A | Smart contract |
| **Morpho** | ETH | 3-8% | N/A | Optimiseur, isolation |
| **Spark** | ETH | 2-6% | N/A | Fork Aave, DAI focus |
| **JustLend** | TRON | 4-12% | N/A | TRON, stabilité à vérifier |
| **Kamino** | Solana | 4-10% | N/A | Solana native |

**Analyse :**
```python
def lending_apr_analysis(protocol_data):
    """Calcule le rendement net après frais et inflation du jeton"""
    supply_apr = protocol_data['supply_apr']
    utilization = protocol_data['utilization_rate']
    reserve_factor = protocol_data['reserve_factor']  # part du protocole
    
    # Rendement net = supply_apr * (1 - reserve_factor)
    net_apr = supply_apr * (1 - reserve_factor)
    
    # Rendement réel en USD = net_apr - inflation_jeton
    return net_apr
```

### ② Liquidity Provision (Pools)

Fournir de la liquidité sur un DEX.

| Type de Pool | DEX | Rendement | Risque Spécifique |
|---|---|---|---|
| **Stable (DAI/USDC)** | Uniswap V3, Curve | 3-15% | Faible IL, forte concurrence |
| **Volatile (ETH/USDC)** | Uniswap V3 | 10-60% | IL élevé |
| **Concentrated** | Uniswap V3 | 20-100%+ | IL très élevé si sort du range |
| **Stableswap** | Curve | 5-20% | Stablecoins, faible IL |
| **Weighted** | Balancer | 8-30% | IL modéré selon weight |
| **LMSR** | Polymarket | Variable | Marchés de prédiction |

**Exemple : Pool Uniswap V3 concentré**
```python
def uniswap_v3_returns(fees_earned, price_range_low, price_range_high,
                       current_price, initial_liquidity, days):
    """
    Calcule le rendement annualisé d'une position LP Uniswap V3.
    Inclut l'impermanent loss si le prix sort du range.
    """
    # Si price dans le range : fees seulement
    # Si price hors range : plus de fees (position 100% stablecoin)
    il = 0
    if current_price < price_range_low or current_price > price_range_high:
        il = (current_price - price_range_low)**2 / (2 * current_price * price_range_low)
    
    total_return = fees_earned - initial_liquidity * il
    return (total_return / initial_liquidity) * (365 / days)
```

### ③ Staking (Simple + Liquid)

| Type | Protocole | Rendement | Lock-up |
|---|---|---|---|
| **ETH Staking** | Lido (stETH) | 3-4% | Non (stETH liquide) |
| **ETH Staking** | Rocket Pool (rETH) | 3-4% | Non |
| **ETH Staking** | Solo validator (32 ETH) | 3-4% | ~36h unbonding |
| **MATIC Staking** | Stader, Lido | 5-8% | 7-14j unbonding |
| **SOL Staking** | Marinade (mSOL), Jito (JitoSOL) | 6-8% | Non (LST) |
| **ATOM Staking** | Cosmos Hub | 15-20% | 21j unbonding |
| **DOT Staking** | Polkadot | 12-16% | 28j unbonding |

**Principes :**
- Les LST (Liquid Staking Tokens) évitent le lock-up
- L'autocompounding via des vaults (Yearn, Beefy) augmente le rendement
- Le restaking (EigenLayer, Symbiotic) permet de réutiliser l'ETH staké
  pour sécuriser d'autres protocoles → rendement supplémentaire (1-3%)

### ④ Yield Aggregators & Autocompound

| Protocole | Chaîne | Stratégie | Rendement Moyen |
|---|---|---|---|
| **Yearn Finance** | ETH, Fantom, Arbitrum | Autocompound, curation | 5-20% |
| **Beefy Finance** | Multi-chain (20+) | Autocompound vaults | 8-40% |
| **Convex** | ETH | Optimisation CRV rewards | 10-30% |
| **Stake DAO** | ETH, Polygon | Autocompound veToken | 10-25% |

## Stratégies Avancées

### ⑤ Delta-Neutral LP

Éliminer le risque de direction (impermanent loss) en hedgeant le sous-jacent
avec des perpétuels ou des options :

```python
def delta_neutral_lp(eth_amount, usdc_amount, perp_market, leverage=1.0):
    """
    Stratégie : Fournir ETH/USDC LP + Short ETH perp.
    Le short perp hedge la position ETH.
    
    Returns:
        net_pnl = LP_fees - funding_rate + price_pnl
    """
    # 1. Fournir la liquidité ETH/USDC (50/50)
    lp_value = eth_amount * eth_price + usdc_amount
    
    # 2. Short ETH perp pour la quantité ETH (hedge)
    short_size = eth_amount * eth_price * leverage
    
    # 3. Rendements
    lp_fees_apr = estimate_lp_fees(lp_value)
    funding_cost = estimate_perp_funding(short_size)  # généralement négatif (payeur)
    il_hedged = 0  # Perfect hedge = pas d'IL
    
    net_return = lp_fees_apr - funding_cost
    return net_return

# Exemple : ETH/USDC LP 10k + short ETH perp 5k
# LP APY ~25%, funding -10% → net ~15% annualisé
```

### ⑥ veTokenomics

Les tokens de gouvernance verrouillés (vote-escrowed) offrent des récompenses
supplémentaires :

| Protocole | Token ve | Lock-up | Boost | Rendement supplémentaire |
|---|---|---|---|---|
| **Curve** | veCRV | 4 ans max | Jusqu'à 2.5x sur LP | Voting bribes (Hidden Hand) |
| **Balancer** | veBAL | 1 an max | Boost LP rewards | Bribes |
| **Aerodrome** | veAERO | 4 ans max | Boost LP rewards | Bribes (Base chain) |
| **Frax** | veFXS | 4 ans max | Boost | Gauge weight voting |
| **Thena** | veTHE | 4 ans max | Boost | BSC chain |

**Stratégie bribes :**
- Les protocoles paient des bribes (Hidden Hand, Votemarket) pour que les
  veToken holders votent pour leur gauge → le yield peut doubler ou tripler.
- Maximiser : voter chaque semaine, collecter bribes + récompenses de pool.

### ⑦ Restaking (EigenLayer)

Restaking : utiliser l'ETH staké pour sécuriser des AVS (Actively Validated
Services) et gagner des récompenses supplémentaires.

| AVS | Type | Rendement additionnel | Risque |
|---|---|---|---|
| **EigenDA** | Data availability | 1-2% | Slashing potentiel |
| **Lagrange** | ZK prover | 2-4% | Slashing |
| **AltLayer** | Rollup sequencer | 2-5% | Opérateur, slashing |
| **Wormhole** | Cross-chain oracle | 1-3% | Oracle risk |

**Points de vigilance :**
- Chaque AVS ajoute un risque de slashing
- L'ETH staké est exposé à des smart contracts supplémentaires
- Le rendement supplémentaire doit compenser le risque de slashing

## Impermanent Loss (IL) — Analyse Quantitative

```python
def impermanent_loss(price_ratio):
    """
    Calcule l'impermanent loss pour un pool 50/50.
    
    price_ratio = prix_final / prix_initial
    """
    sqrt_ratio = np.sqrt(price_ratio)
    return 2 * sqrt_ratio / (1 + sqrt_ratio) - 1

# Exemples :
# ETH x2 → IL = -5.7%
# ETH x3 → IL = -13.4%
# ETH x5 → IL = -25.5%
# ETH /2 → IL = -5.7% (symétrique)
# ETH /5 → IL = -25.5%
```

L'IL est un coût d'opportunité : si ETH x2, hodl rapporte +100%, LP rapporte
+100% - 5.7% + fees. Avec assez de fees, le LP peut battre le hodl.

**Stratégies pour minimiser l'IL :**
- Pools stables (stablecoin pairs : IL ~0%)
- Range étroit Uniswap V3 sur actifs corrélés (stETH/ETH)
- Pools à poids non égaux (80/20 Balancer : moins d'IL)
- Delta-hedging via perp (annule l'IL)

## Risk Assessment

### Tableau des risques DeFi

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| **Smart contract bug** | Faible (1-5%) | Catastrophique (perte totale) | Audit multiple, assuré (Nexus Mutual), blue chips |
| **Oracle manipulation** | Faible | Élevé (liquidation) | Chainlink, TWAP, time-weighted |
| **Impermanent loss** | Élevé (volatile) | Modéré (5-25%) | Delta hedge, pools stables |
| **Bridge hack** | Moyen | Élevé (perte bridge) | Bridges audités, canonicaux |
| **Liquidation (leverage)** | Moyen (volatilité) | Élevé | Sur-collatéralisation, alertes |
| **Regulatory** | En hausse | Moyen à élevé | Diversification, KYC optionnel |
| **Rug pull (long tail)** | Élevé | Catastrophique | Blue chips seulement, vérification |
| **MEV / sandwich** | Élevé | Faible | RPC privé (Flashbots, Eden) |

### Due Diligence Checklist

- [ ] Contrat audité par au moins 2 firmes (Trail of Bits, OpenZeppelin,
      Certora, Code4rena)
- [ ] TVL > 50M (moins de risque de rug)
- [ ] Time-lock (> 24h) sur les fonctions admin
- [ ] Multi-sig sur les administrateurs (≥3/5)
- [ ] Pas de mint illimité (vérifier le supply)
- [ ] Liquidité suffisante pour sortir (> 100k)
- [ ] Pas de proxy upgradeable non timelocké

## Automatisation

### Scripts clés

```python
# 1. Harvest et autocompound
def auto_harvest(vault_contract, wallet):
    """Déclenche le harvest et autocompound périodiquement"""
    pending = vault_contract.earned(wallet)
    if pending > MIN_HARVEST_AMOUNT:
        tx = vault_contract.getReward()
        wait_for_tx(tx)
        # Swap reward → LP token et re-deposit
        return tx

# 2. Rebalancement de range LP V3
def rebalance_range(pool_id, current_price, range_width_pct=20):
    """Ajuster les bornes LP quand le prix approche d'une borne"""
    lower = current_price * (1 - range_width_pct/200)
    upper = current_price * (1 + range_width_pct/200)
    # Collecter fees, retirer l'ancienne position, ouvrir la nouvelle
    return lower, upper

# 3. Alerte liquidation
def monitor_positions(compound_contract, wallet):
    """Surveiller le health factor et alerter si < 1.5"""
    health = compound_contract.getHealthFactor(wallet)
    if health < 1.5:
        alert(f"Health factor: {health} — risque de liquidation")
    return health
```

## Pièges à éviter

1. **IL non hedgé en pool volatile** : Fournir ETH/USDC sur Uniswap V3 range
   20%, ETH fait x2 → perte de capital. Toujours calculer l'IL potentiel.
2. **Rug pull sur tokens long-tail** : Les tokens à faible cap avec des
   pools à 500% APY sont 90% des rug pulls. Ne farmer que les blue chips.
3. **Frais de gas qui mangent le rendement** : Sur ETH L1, un harvest coûte
   $20-50. Si le pool rapporte 100$ par mois et qu'il faut harvest toutes
   les semaines → les frais mangent 80% du rendement. Préférer L2 (Arbitrum,
   Optimism, Base) ou autocompound automatique.
4. **Impermanent loss sur range étroit V3** : Quand le prix sort du range,
   la position est 100% dans un seul token — plus de fees, IL réalisé.
   Un range trop étroit est dangereux.
5. **Lock-up veToken trop long** : Verrouiller pour 4 ans expose à un
   drawdown massif (CRV a fait -90% en 2022). Fractionner les lock-ups.
6. **Risque de bridge** : Un bridge hack détruit tout ce qui est sur l'autre
   chaîne. Pour les grosses positions, préférer les ponts canonical vs tiers.
7. **Corrélation crypto** : En bear market, tout baisse ensemble. La
   diversification DeFi ne protège pas d'un effondrement systémique.

## Vérification

- [ ] Les contrats de tous les protocoles utilisés sont audités
- [ ] L'IL potentiel est calculé avant tout dépôt LP
- [ ] Les frais de gas sont inclus dans le rendement net
- [ ] Le health factor est surveillé (lending) avec seuil d'alerte à 1.5
- [ ] Les positions LP ont une stratégie de rebalancement
- [ ] Le lock-up des veTokens est fractionné
- [ ] Les bridges utilisés sont canonical ou audités
- [ ] Un plan de sortie existe pour chaque position

## Skills liés

- `web3-onchain-trading` — interactions on-chain, MEV, arbitrage
- `value-at-risk` — intégrer les risques DeFi