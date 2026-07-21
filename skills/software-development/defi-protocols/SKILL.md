---
name: defi-protocols
description: "Architecture et développement de protocoles DeFi — DEX (AMM, orderbook), lending/borrowing, yield aggregators, liquid staking, stablecoins, MEV, bridges cross-chain et oracles."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [defi, amm, uniswap, curve, balancer, aave, compound, makerdao, mev, oracles, bridges, yield-farming, lending, stablecoins]
    related_skills: [smart-contracts, solidity-advanced, layer2-scaling, tokenomics]
---

# Développement DeFi — DEX, Lending, Yield, MEV & Oracles

## Quand utiliser ce skill

- Concevoir ou auditer un protocole DeFi (AMM, lending market, yield optimizer, CDP stablecoin)
- Implémenter un AMM constant product (Uniswap V2/V3)
- Développer un marché de lending (Aave-style)
- Analyser et capturer du MEV (sandwich, arbitrage, liquidations)
- Intégrer des oracles (Chainlink, RedStone, Pyth, TWAP)

## 1. AMM — Automated Market Maker

### 1.1 Uniswap V2 — Constant Product (x * y = k)

```solidity
contract Pair {
    uint112 public reserve0;
    uint112 public reserve1;
    uint256 public kLast;

    // Swap avec fee (0.3%)
    function swap(uint256 amount0Out, uint256 amount1Out, address to, bytes calldata data) external lock {
        require(amount0Out > 0 || amount1Out > 0, "Insufficient output");
        (uint112 _reserve0, uint112 _reserve1,) = getReserves();

        // CEI
        _update(balance0 - amount0Out, balance1 - amount1Out, _reserve0, _reserve1);

        // Vérification k = (reserve0 - amount0In) * (reserve1 - amount1In) >= _reserve0 * _reserve1
        uint256 balance0Adjusted = balance0 * 1000 - amount0In * 3;
        uint256 balance1Adjusted = balance1 * 1000 - amount1In * 3;
        require(balance0Adjusted * balance1Adjusted >= uint256(_reserve0) * _reserve1 * 1000**2, "K");
    }
}
```

**Maths essentielles :**
- `amountIn * (1 - fee) * reserveOut / (reserveIn + amountIn * (1 - fee))` = quantité reçue
- Slippage = `1 / (1 - Δx / reserveIn) - 1` (augmente vite à ~100% de la pool)
- Impermanent loss = `2√r / (1 + r) - 1` où `r = ratio price change`

### 1.2 Uniswap V3 — Concentrated Liquidity

```solidity
// Position NFT — liquidité concentrée entre [tickLower, tickUpper]
struct Position {
    uint128 liquidity;       // Liquidité fournie
    uint256 feeGrowthInside0LastX128;
    uint256 feeGrowthInside1LastX128;
    uint128 tokensOwed0;     // Fees accumulées en token0
    uint128 tokensOwed1;     // Fees accumulées en token1
}

// Mint une nouvelle position
function mint(MintParams calldata params)
    external override returns (uint256 tokenId, uint128 liquidity, uint256 amount0, uint256 amount1) {
    // Calcul de la liquidité optimale pour la range donnée
    liquidity = LiquidityAmounts.getLiquidityForAmounts(
        sqrtRatioX96,
        TickMath.getSqrtRatioAtTick(params.tickLower),
        TickMath.getSqrtRatioAtTick(params.tickUpper),
        params.amount0Desired,
        params.amount1Desired
    );
}
```

**Concept clé :** La liquidité est inactive hors de la range choisie. Permet 1000-10000x le capital efficiency d'Uniswap V2.

### 1.3 Curve Finance — StableSwap

Pour les paires de stablecoins ou d'actifs corrélés : `D = A * n^n * S + D^(n+1) / (n^n * P)`

```solidity
// Approximation simplifiée
function getD(uint256[2] memory xp, uint256 A) internal pure returns (uint256) {
    uint256 s = xp[0] + xp[1];
    if (s == 0) return 0;

    uint256 dPrev = 0;
    uint256 d = s;
    uint256 ann = A * 2;  // n = 2

    for (uint256 i = 0; i < 255; i++) {
        uint256 dp = d;
        for (uint256 j = 0; j < 2; j++) {
            dp = dp * d / (xp[j] * 2);
        }
        dPrev = d;
        d = (ann * s + dp * 2) * d / ((ann - 1) * d + (2 + 1) * dp);
        if (d == dPrev) break;
    }
    return d;
}
```

## 2. Lending / Borrowing (Aave Style)

### 2.1 Architecture d'un Marché de Lending

```
Dépôt → aToken (interest-bearing) → Pool
Emprunt → Debt Token → Collatéral requis
Liquidation → Seuil de collatéral dépassé → Liquidateur rembourse → Bonus
```

```solidity
contract LendingPool {
    // Réserve : chaque actif = une réserve
    struct ReserveData {
        uint256 totalLiquidity;       // Total déposé
        uint256 totalDebt;            // Total emprunté
        uint256 availableLiquidity;   // Disponible
        uint256 liquidityRate;        // Taux de rendement (AAPY)
        uint256 borrowRate;           // Taux d'emprunt
        uint256 utilizationRate;      // = totalDebt / totalLiquidity
        address aTokenAddress;        // Token représentatif du dépôt
        uint40 lastUpdateTimestamp;
    }

    // Collatéral requis = amountBorrowed * liquidationThreshold / collateralFactor
    function borrow(address asset, uint256 amount) external {
        ReserveData storage reserve = reserves[asset];
        require(isLiquidatable(msg.sender, asset, amount), "Insufficient collateral");

        uint256 healthFactor = calculateHealthFactor(msg.sender);
        require(healthFactor > 1e18, "Unhealthy position");

        reserve.totalDebt += amount;
        reserve.availableLiquidity -= amount;

        // Mise à jour des taux basée sur l'utilisation
        _updateInterestRates(asset);
        IERC20(asset).safeTransfer(msg.sender, amount);
    }

    // Liquidation : le liquidateur rembourse la dette, reçoit le collatéral + bonus
    function liquidationCall(address user, address debtAsset, uint256 debtAmount) external {
        require(calculateHealthFactor(user) < 1e18, "Healthy");

        uint256 collateralAmount = _calculateCollateral(user, debtAmount);
        uint256 bonus = collateralAmount * liquidationBonus / 10000;
    }
}
```

### 2.2 Modèles de Taux d'Intérêt

- **JumpRate** (Aave V2) : taux bas jusqu'à U_optimal, puis pente raide
- **Variable** (Compound) : `borrowRate = base + multiplier * utilization`
- **Stable Rate** (Aave) : taux fixe, plus élevé que variable

```solidity
// Aave-style: JumpRateModel
function calculateBorrowRate(uint256 utilization) internal pure returns (uint256) {
    uint256 U_OPTIMAL = 0.8e18;     // 80%
    uint256 BASE = 0.02e18;         // 2%
    uint256 SLOPE1 = 0.07e18;       // 7%
    uint256 SLOPE2 = 3.00e18;       // 300%

    if (utilization <= U_OPTIMAL) {
        return BASE + (utilization * SLOPE1 / U_OPTIMAL);
    } else {
        return BASE + SLOPE1 + (utilization - U_OPTIMAL) * SLOPE2 / (1e18 - U_OPTIMAL);
    }
}
```

## 3. MEV (Maximal Extractable Value)

### 3.1 Types de MEV

| Type | Description | Profit | Risque |
|------|-------------|--------|--------|
| **Sandwich** | Acheter avant + vendre après un gros swap | Faible | Competition |
| **Arbitrage** | Profiter d'un écart de prix entre DEX | Moyen | Gas war |
| **Liquidation** | Liquider des positions sous-collatéralisées | Élevé | Gas war |
| **JIT Liquidity** | Ajouter/retirer de la liquidité autour d'un swap | Moyen | Capital lock |

### 3.2 Backrun avec Flashbots

```python
from flashbots import flashbot
from eth_account import Account
from web3 import Web3

# Bundle : une transaction privée soumise directement aux builders Ethereum
bundle = [
    {"signed_transaction": tx_arbitrage.rawTransaction},
    {"signed_transaction": tx_profit_collect.rawTransaction}
]

# Envoyer le bundle au relayeur Flashbots
flashbot(w3, account)
w3.flashbots.send_bundle(
    bundle,
    target_block_number=block_number + 1,
    opts={"min_timestamp": int(time.time()) + 1}
)
```

## 4. Oracles

### 4.1 Comparaison des Oracle Providers

| Provider | Type | Latence | Sécurité | Coût |
|----------|------|---------|----------|------|
| **Chainlink** | Aggregated (DON) | ~minutes | Très haute | Gas + LINK |
| **RedStone** | Pull-based on-demand | 10s | Haute | Faible |
| **Pyth Network** | Solana puis Wormhole cross-chain | <1s | Haute | Très faible |
| **TWAP (Uniswap V3)** | On-chain, pondéré | Configurable | Native | Gratuit |

### 4.2 Oracle TWAP Uniswap V3

```solidity
// Oracle intégré Uniswap V3 — accumule les prix à chaque swap
contract Oracle {
    function consult(address pool, uint32 secondsAgo) external view returns (int256 arithmeticMeanTick) {
        uint32[] memory secondsAgos = new uint32[](2);
        secondsAgos[0] = secondsAgo;
        secondsAgos[1] = 0;

        (int56[] memory tickCumulatives,) = IUniswapV3Pool(pool).observe(secondsAgos);
        arithmeticMeanTick = (tickCumulatives[1] - tickCumulatives[0]) / int56(int32(secondsAgo));
    }
}
```

## 5. Stablecoins

### 5.1 Types de Stablecoins

| Type | Exemple | Mécanisme | Risque |
|------|---------|-----------|--------|
| **Fiat-backed** | USDC, USDT, USDP | 1:1 avec réserve fiat | Centralisation, audit |
| **Crypto-backed overcollat.** | DAI (MakerDAO) | CDP (Collateralized Debt Position) | Liquidation, oracle |
| **Algorithmic** | FRAX (partiel), LUSD | Seigniorage + arbitrage | Depeg, bank run |
| **Crypto-backed undercollat.** | crvUSD, ETHUSD (Liquity) | AMO (Algorithmic Market Operations) | Complexité |

### 5.2 CDP — Collateralized Debt Position (MakerDAO-style)

```solidity
contract CDPManager {
    struct Vault {
        address owner;
        uint256 collateral;    // ETH, wstETH, etc.
        uint256 debt;          // DAI généré
        uint256 liquidationPrice;
    }

    // Ouvrir une position : bloquer collatéral → générer stablecoin
    function openVault(address collateralAsset, uint256 depositAmount) external {
        // Ratio de collatéral minimum = 150%
        uint256 maxDebt = (depositAmount * price) / 1.5e18;
        vaults[vaultId] = Vault(msg.sender, depositAmount, 0, 0);
    }

    // Liquidation si ratio < seuil
    function liquidate(uint256 vaultId) external {
        Vault memory v = vaults[vaultId];
        uint256 collateralValue = v.collateral * getPrice();
        uint256 ratio = collateralValue * 1e18 / v.debt;
        require(ratio < LIQUIDATION_RATIO, "Safe");

        // Liquidateur paie la dette, reçoit collatéral + bonus
    }
}
```

## 6. Bridges Cross-Chain

### Architectures principales :
- **Lock & Mint** : Lock sur chaîne A, mint sur chaîne B (centralisé, liquidity-efficient)
- **Burn & Mint** : Burn sur A, mint sur B (nécessite trust)
- **Optimistic** : Relay + challenge window (ex: Nomad)
- **Light Client** : Vérification des têtes de bloc (ex: IBC, LayerZero V2)
- **Liquidity Network** : Market makers (ex: Stargate, Across)

## 7. Pipelines d'Analyse On-Chain (Dune, The Graph)

### The Graph — Subgraph

```graphql
# subgraph.yaml
dataSources:
  - kind: ethereum/contract
    name: UniswapV3Factory
    network: mainnet
    source:
      address: "0x1F98431c8aD98523631AE4a59f267346ea31F984"
      abi: Factory
    mapping:
      kind: ethereum/events
      apiVersion: 0.0.7
      entities:
        - Pool
      abis:
        - name: Factory
          file: ./abis/Factory.json
      eventHandlers:
        - event: PoolCreated(indexed address,indexed address,indexed uint24,address)
          handler: handlePoolCreated
```

### Métriques DeFi Essentielles
- **TVL** : Total Value Locked (capital total dans le protocole)
- **Volume** : Transactions quotidiennes
- **Taux d'utilisation** : debt / liquidity (détermine les taux)
- **Revenue** : Fees collectées par le protocole
- **Debt Ratio** : Dette totale / collatéral total (risque systémique)
