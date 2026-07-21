---
name: web3-onchain-trading
description: >-
  Trading et analyse on-chain : interactions smart contracts via web3.py/ethers,
  MEV (sandwich, backrun), arbitrage DEX cross-pool, flash loans, mempool
  monitoring, DEX aggregation, liquidation bots, sniping, token analysis
  (rug pull detection, honeypot, liquidity analysis), portfolio tracking
  multi-chain.
category: finance
---

# Web3 & On-Chain — Trading Automatisé, MEV & Arbitrage

## Présentation

La blockchain offre une transparence totale des flux et des opportunités de
trading uniques : arbitrage entre DEX, MEV (Maximal Extractable Value),
liquidations, sniping. Contrairement aux marchés traditionnels, tout est
visible en temps réel dans le mempool. Ce skill couvre l'infrastructure
technique et les stratégies pour trader on-chain de façon automatisée.

**Déclencheurs :** "web3", "on-chain", "MEV", "arbitrage DEX", "flash loan",
"mempool", "Uniswap", "sandwich", "backrun", "sniper bot", "liquidation bot",
"cross-chain", "DEX aggregation", "token analysis", "rug pull".

## Infrastructure Web3

### Stack technique

| Composant | Python | JavaScript |
|---|---|---|
| **Client RPC** | web3.py | ethers.js / viem |
| **DEX interactions** | web3 + ABI | Uniswap SDK |
| **Mempool** | Nœud local + websocket | Flashbots / MEV-share |
| **Analyse** | Dune Analytics API | The Graph (Subgraph) |
| **Pricing** | CoinGecko / DexScreener | 0x API |
| **Cross-chain** | Chainlink CCIP / LayerZero | Wormhole / Hyperlane |

### Connexion RPC de base

```python
from web3 import Web3
import json

# Connexion à un nœud Ethereum
RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Vérifier la connexion
print(f"Connecté : {w3.is_connected()}")
print(f"Bloc : {w3.eth.block_number}")
print(f"ETH Balance : {w3.eth.get_balance('0x...') / 1e18} ETH")

# Connexion via websocket (mempool)
WS_URL = "wss://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
w3_ws = Web3(Web3.WebsocketProvider(WS_URL))
```

## Arbitrage DEX

### Principe

Acheter un token sur un DEX où il est moins cher, le vendre sur un autre
DEX où il est plus cher. La différence moins les frais de gas et les frais
de swap = profit.

```python
def check_arbitrage(token_address, dex_a='uniswap_v3', dex_b='sushiswap'):
    """
    Vérifie s'il existe un arbitrage entre deux DEX pour un token.
    
    Args:
        token_address: adresse du token à arbitrer
        dex_a: nom du premier DEX
        dex_b: nom du second DEX
    
    Returns:
        profit estimé, direction
    """
    # 1. Récupérer les prix sur chaque DEX
    price_a = get_dex_price(dex_a, 'WETH', token_address)
    price_b = get_dex_price(dex_b, 'WETH', token_address)
    
    # 2. Calculer la différence
    if price_a < price_b:
        # Acheter sur A, vendre sur B
        spread = (price_b - price_a) / price_a
        direction = f"{dex_a} → {dex_b}"
    else:
        spread = (price_a - price_b) / price_b
        direction = f"{dex_b} → {dex_a}"
    
    # 3. Soustraire les frais
    # Uniswap V3 fee tier: 0.01%, 0.05%, 0.30%, 1.00%
    dex_fee = 0.003  # 0.3% pour V3
    gas_estimate = estimate_gas_arbitrage() / 1e18 * eth_price
    
    profit = spread - 2 * dex_fee - (gas_estimate / trade_size)
    
    return {
        'spread': spread,
        'profit_net': profit,
        'direction': direction,
        'profitable': profit > 0.001  # min 0.1% de marge
    }
```

### Flash Loans

Les flash loans permettent d'emprunter sans collatéral à condition de
rembourser dans la même transaction. Parfait pour l'arbitrage sans capital.

```python
def flash_loan_arbitrage(amount_eth, pool_a, pool_b, flash_loan_provider='aave'):
    """
    Flash loan arbitrage : emprunter → swaper A → swaper B → rembourser.
    Tout dans une seule transaction.
    """
    # 1. Emprunter amount_eth via Aave flash loan
    
    # 2. Dans la callback :
    #    - Swap ETH → TOKEN sur pool_a
    #    - Swap TOKEN → ETH sur pool_b (plus cher)
    #    - Rembourser le flash loan + fee (0.09% pour Aave)
    
    # 3. Profit = amount_out_b - amount_in_a - flash_loan_fee - gas
    flash_loan_fee = amount_eth * 0.0009  # 0.09% Aave
    gas_cost = 150000 * 30e9 / 1e18  # 150k gas @ 30 gwei
    
    return amount_out_b - amount_in_a - flash_loan_fee - gas_cost
```

**Attention :** La compétition pour les flash loan arbitrages est intense.
Les MEV bots détectent et exécutent en millièmes de seconde. Un bot amateur
paie le gas pour que le bot professionnel prenne le trade.

## MEV (Maximal Extractable Value)

### Types de MEV

| Type | Description | Profit potentiel | Complexité |
|---|---|---|---|
| **Sandwich** | Acheter avant un gros achat, vendre après | Faible (0.1-1%) | Faible |
| **Backrun** | Exécuter juste après une transaction | Moyen | Moyenne |
| **Liquidation** | Liquider une position sous-collatéralisée | Élevé (5-10%) | Haute |
| **JIT (Just-in-time)** | Insérer liquidité avant un gros swap DEX | Moyen | Haute |
| **Atomic arbitrage** | Flash loan + multi-DEX | Variable | Très haute |
| **TG (Temporal Gas)** | Faire monter le gas pour forcer un ordre | Faible | Faible (toxique) |

### Sandwich Attack

```python
def sandwich_simulation(tx_hash, token_in, token_out, amount_in, dex):
    """
    Simule un sandwich autour d'une transaction cible.
    
    1. Frontrun : acheter token avant la cible (prix monte)
    2. Target transaction : la cible achète (prix monte encore)
    3. Backrun : revendre le token acheté au frontrun
    
    Profit = (prix_backrun - prix_frontrun) * volume - gas*2
    """
    # Récupérer la transaction du mempool
    pending_tx = w3.eth.get_transaction(tx_hash)
    
    # Simuler l'impact sur le pool
    current_reserves = get_pool_reserves(dex, token_in, token_out)
    price_before = current_reserves[0] / current_reserves[1]
    
    # Après frontrun
    frontrun_amount = amount_in * 0.1  # 10% de la tx cible
    reserves_after_frontrun = simulate_swap(current_reserves, frontrun_amount, token_in)
    price_after_frontrun = reserves_after_frontrun[0] / reserves_after_frontrun[1]
    
    # Après la tx cible
    reserves_after_target = simulate_swap(reserves_after_frontrun, amount_in, token_in)
    price_after_target = reserves_after_target[0] / reserves_after_target[1]
    
    # Profit = vendre le frontrun au prix après target
    frontrun_tokens_out = frontrun_amount / price_after_frontrun
    backrun_eth_in = frontrun_tokens_out * price_after_target
    profit = backrun_eth_in - frontrun_amount
    
    return profit
```

**Éthique :** Le sandwich est considéré comme MEV toxique. Certaines
juridictions le considèrent comme manipulation de marché.

### Flashbots (MEV-Boost)

Pour éviter les sandwichs sur ses propres transactions et faire du backrun
sans compétition :

```python
from flashbots import flashbots

# Envoyer une transaction privée via Flashbots pour éviter le mempool
def send_private_tx(tx_data, signer):
    """Envoie une transaction via Flashbots (protection MEV)"""
    flashbots_provider = flashbots.FlashbotsProvider(w3, signer)
    
    bundle = [
        {"signed_transaction": signer.sign_transaction(tx_data)}
    ]
    
    result = flashbots_provider.send_bundle(bundle, target_block_number)
    return result
```

## DEX Aggregation et Routing

Les meilleurs prix ne sont pas sur un seul DEX mais en splitant entre
plusieurs pools :

```python
def optimal_route(token_in, token_out, amount, max_splits=3):
    """
    Trouve le meilleur itinéraire multi-hop entre DEX.
    Utilise un algorithme de plus court chemin pondéré.
    """
    # Graphe des pools disponibles
    pools = get_all_pools(token_in, token_out)
    
    # BFS avec meilleur prix
    best_route = None
    best_price = 0
    
    for split in range(1, max_splits + 1):
        routes = generate_routes(pools, split)
        for route in routes:
            expected_out = simulate_route(route, amount)
            if expected_out > best_price:
                best_price = expected_out
                best_route = route
    
    return best_route, best_price

# Comparer avec les API existantes (plus simple) :
# 1inch API   : https://api.1inch.io
# 0x API      : https://api.0x.org
# ParaSwap    : https://apiv5.paraswap.io
# Li.Fi       : https://li.quest
```

## Token Analysis (Due Diligence On-Chain)

Avant d'interagir avec un token inconnu, vérifier :

```python
def analyze_token(token_address):
    """Analyse complète d'un token (détection rug pull)"""
    checks = {}
    
    # 1. Liquidité
    liquidity = get_token_liquidity(token_address)
    checks['liquidity_usd'] = liquidity
    checks['liquidity_sufficient'] = liquidity > 50000  # > 50k USD
    
    # 2. Holder distribution
    holders = get_top_holders(token_address, 10)
    top10_pct = sum(h['balance'] for h in holders) / total_supply
    checks['top10_concentration'] = top10_pct
    checks['decentralized'] = top10_pct < 0.5
    
    # 3. Honeypot test
    try:
        test_buy = swap_simulation(token_address, 'WETH', 0.1)
        test_sell = swap_simulation('WETH', token_address, test_buy)
        checks['can_sell'] = test_sell > 0
    except:
        checks['can_sell'] = False  # HONEYPOT !
    
    # 4. Contract vérifié
    checks['verified'] = is_contract_verified(token_address)
    
    # 5. Owner power
    owner = get_contract_owner(token_address)
    checks['owner_can_mint'] = can_mint(owner, token_address)
    checks['owner_can_pause'] = can_pause(owner, token_address)
    checks['owner_can_blacklist'] = can_blacklist(owner, token_address)
    
    # 6. Rug score (0 = safe, 10 = rug)
    rug_score = sum([
        not checks['liquidity_sufficient'],      # +2
        not checks['decentralized'],              # +1
        not checks['can_sell'],                    # +3
        not checks['verified'],                    # +1
        checks['owner_can_mint'],                  # +2
        checks['owner_can_blacklist'],             # +1
    ])
    checks['rug_score'] = rug_score
    checks['safe'] = rug_score < 4
    
    return checks
```

## Liquidation Bots (Lending Protocols)

Quand un emprunteur voit son health factor < 1, toute personne peut
liquider sa position et recevoir un bonus (5-15%).

```python
def monitor_liquidations(protocol='aave', min_profit_eth=0.01):
    """
    Surveille les positions liquidadables sur Aave / Compound.
    """
    # Récupérer toutes les positions
    positions = get_all_positions(protocol)
    
    liquidable = []
    for pos in positions:
        health = pos['health_factor']
        if health < 1.0:
            # Calculer le profit de liquidation
            debt = pos['debt_value']
            collateral = pos['collateral_value']
            
            # Bonus de liquidation: 5-10% sur la dette repayée
            liquidation_bonus = 0.05  # 5% sur Aave
            repay_amount = debt * 0.5  # Liquidater max 50% de la dette
            
            profit = repay_amount * liquidation_bonus
            gas_cost = estimate_liquidation_gas()
            
            if profit - gas_cost > min_profit_eth:
                liquidable.append({
                    'position': pos,
                    'profit_net': profit - gas_cost,
                    'token': pos['collateral_token']
                })
    
    return sorted(liquidable, key=lambda x: x['profit_net'], reverse=True)
```

## Pièges à éviter

1. **Compétition MEV :** Les bots professionnels ont une latence de quelques
   microsecondes, des nœuds optimisés, et des connexions privées aux
   mineurs/validateurs. Un bot amateur sur Alchemy public ne gagnera
   presque jamais un arbitrage.
2. **Gas war :** En compétition MEV, le gas monte à des niveaux absurdes.
   Une transaction qui échoue coûte quand même le gas. Limiter le gas price.
3. **Rug pull / Honeypot :** Toujours vérifier `can_sell` avant d'acheter
   un token inconnu. Les honeypots laissent acheter mais pas vendre.
4. **Smart contract non audité :** Un bug dans le contrat cible peut
   bloquer les fonds ou les faire voler. Pour les stratégies qui laissent
   des fonds dans un contrat (LP, vault), l'audit est obligatoire.
5. **RPC rate limit :** Les providers gratuits (Infura, Alchemy) limitent
   à 10-100 req/s. Pour le monitoring en temps réel, un nœud local
   (geth/erigon) ou un service dédié est nécessaire.
6. **Revert non géré :** Toujours catcher les revert dans les appels
   simulate (pas de call reverted pour arrêter le bot).
7. **Tax tokens :** Certains tokens ont des frais de transfert (tax).
   Ces frais ne sont pas dans le routing standard et peuvent casser la
   rentabilité. Vérifier avec `token.owner_fee` / `token.sell_tax`.

## Vérification

- [ ] Connexion RPC et websocket fonctionnelles
- [ ] Les prix DEX sont correctement récupérés (via pool contracts)
- [ ] La simulation de swap fonctionne (call, pas send)
- [ ] L'analyse token vérifie sell, honeypot, holder concentration
- [ ] Le gas estimé est inclus dans tous les calculs de rentabilité
- [ ] Les transactions MEV passent par Flashbots ou RPC privé
- [ ] Les erreurs de revert sont catchées (pas de crash du bot)
- [ ] La stratégie est testée sur testnet avant mainnet

## Références

- `references/dex-addresses.md` — adresses des pools DEX les plus courants
  sur ETH, BSC, Arbitrum, Optimism (à créer si nécessaire)
- `references/flash-loan-providers.md` — frais et adresses des flash loan
  providers

## Skills liés

- `defi-yield-strategies` — farming et LP on-chain
- `value-at-risk` — intégrer les risques on-chain (hack, bridge)