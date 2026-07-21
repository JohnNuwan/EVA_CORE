---
name: tokenomics
description: "Conception de tokenomics — standards ERC (20, 4626, 2612), modèles inflationnistes/déflationnistes, mécanismes de gouvernance, ve tokenomics, bonding curves, initial DEX offerings, liquidity mining, vesting schedules, et modèles de valeur."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [tokenomics, erc-20, erc-4626, token-design, governance, ve-model, bonding-curves, ico, ido, liquidity-mining, vesting, defi, token-engineering, airdrop, dao]
    related_skills: [defi-protocols, smart-contracts, nft-development, layer2-scaling]
---

# Tokenomics — Ingénierie des Tokens, Économie & Gouvernance

## Quand utiliser ce skill

- Concevoir la tokenomics d'un nouveau protocole DeFi ou d'une DAO
- Implémenter un token ERC-20 avec taxes, rebase, ou mécanismes avancés
- Définir un schedule de vesting, airdrop, ou liquidity mining
- Modéliser des bonding curves pour continuous token offering
- Architecture de gouvernance : veToken (vote-escrowed), Quadratic Voting

## 1. Standards de Tokens — Guide Complet

### 1.1 ERC-20 — Token Fongible Standard

```solidity
contract EVAToken is ERC20, ERC20Permit, Ownable {
    uint256 public constant MAX_SUPPLY = 1_000_000_000e18; // 1B
    mapping(address => bool) public blacklisted;

    // Taxes : 2% sur chaque transfer
    uint256 public buyTax = 200;    // 2% (basis points)
    uint256 public sellTax = 200;
    address public treasury;
    mapping(address => bool) public isExcludedFromTax;

    constructor() ERC20("EVA Token", "EVAT") ERC20Permit("EVA Token") {
        treasury = msg.sender;
        _mint(msg.sender, 100_000_000e18); // 10% initial
    }

    // ERC-20 surchargé avec taxes
    function _update(address from, address to, uint256 value) internal override {
        require(!blacklisted[from] && !blacklisted[to], "Blacklisted");

        if (!isExcludedFromTax[from] && !isExcludedFromTax[to]) {
            uint256 taxAmount = value * (to == address(uniswapPair) ? sellTax : buyTax) / 10000;
            uint256 netAmount = value - taxAmount;
            super._update(from, treasury, taxAmount);
            super._update(from, to, netAmount);
        } else {
            super._update(from, to, value);
        }
    }

    // Burn mechanism
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
```

### 1.2 ERC-2612 — Permit (Gasless Approvals)

```solidity
// Approbation sans ETH — signature EIP-712
// L'utilisateur signe un message, un relayer soumet la tx

// Utilisation côté frontend :
const signature = await signer.signTypedData(domain, types, {
    owner: userAddress,
    spender: spenderAddress,
    value: ethers.parseEther("1000"),
    nonce: await token.nonces(userAddress),
    deadline: deadline,
});

await token.permit(userAddress, spenderAddress, value, deadline, v, r, s);
```

### 1.3 ERC-4626 — Tokenized Vault (Yield-Bearing)

Déjà détaillé dans `solidity-advanced`. Point clé : standardiser les vaults de yield pour l'interopérabilité.

### 1.4 ERC-20 Rebase (am-ple) — Elastic Supply

```solidity
// Exemple : token à supply élastique (Ampleforth style)
contract Ample is ERC20 {
    uint256 public lastRebase;
    uint256 public rebasePeriod = 3600; // 1h

    function rebase(int256 supplyDelta) external onlyRebaser {
        // supplyDelta > 0 = inflation, < 0 = déflation
        uint256 newSupply = totalSupply();
        if (supplyDelta > 0) newSupply += uint256(supplyDelta);
        else newSupply -= uint256(-supplyDelta);

        _totalSupply = newSupply;
        // Les balances ne changent pas — c'est la valeur stockée dans _totalSupply
        // qui est ajustée via un oracle de prix
        lastRebase = block.timestamp;
    }
}
```

## 2. Modèles Économiques des Tokens

### 2.1 Modèle Inflationniste vs Déflationniste

| Modèle | Token | Taux | Mécanisme | Effet |
|--------|-------|------|-----------|-------|
| **Inflationniste** | ETH (avant Merge) | ~4.5%/an | Mining rewards | Récompense les validateurs |
| **Déflationniste** | ETH (post-Merge) | Variable | EIP-1559 burn | Rarefaction |
| **Inflation plafonnée** | SOL | 8→1.5%/an | Stake rewards + inflation décroissante | Stabilité long terme |
| **Capped supply** | BTC | 21M max | Halving tous les 4 ans | Pénurie programmable |
| **Bonding curve** | Synthetic | Continu | Mint/burn selon formule | Prix déterministe |

### 2.2 EIP-1559 — Fee Burning

```
Base Fee (brûlé) + Priority Fee (validateur)
Base Fee ∝ bloc plein → augmente
             bloc vide → diminue (max ±12.5%)
```

### 2.3 Exemple de Token à Mécanisme de Burn

```solidity
// Burn automatique à chaque transfer (Shiba-style)
// Ou burn via buyback (BNB auto-burn)
contract DeflationaryToken is ERC20 {
    uint256 public constant BURN_RATE = 100;  // 1%
    uint256 public constant MIN_BALANCE = 10000e18;  // Minimum pour ne pas brûler

    function _update(address from, address to, uint256 value) internal override {
        if (value >= MIN_BALANCE && from != address(0) && to != address(0)) {
            uint256 burnAmount = value * BURN_RATE / 10000;
            super._update(from, address(0), burnAmount); // Burn
            super._update(from, to, value - burnAmount);
        } else {
            super._update(from, to, value);
        }
    }
}
```

## 3. Token Distribution — Vesting, Airdrop, TGE

### 3.1 Vesting Contract (Streaming / Cliff + Linear)

```solidity
contract VestingVault {
    struct Grant {
        address recipient;
        uint256 totalAmount;
        uint256 cliff;            // Durée du cliff (secondes)
        uint256 duration;         // Durée totale du vesting
        uint256 start;            // Timestamp de début
        uint256 claimed;          // Montant déjà réclamé
        bool revocable;
    }

    mapping(bytes32 => Grant) public grants;
    IERC20 public token;
    address public admin;

    function createGrant(
        address recipient,
        uint256 amount,
        uint256 cliff,
        uint256 duration,
        bool revocable
    ) external onlyAdmin {
        bytes32 id = keccak256(abi.encodePacked(recipient, block.timestamp));
        grants[id] = Grant(recipient, amount, cliff, duration, block.timestamp, 0, revocable);
        token.transferFrom(msg.sender, address(this), amount);
    }

    function claimable(bytes32 grantId) public view returns (uint256) {
        Grant memory g = grants[grantId];
        if (block.timestamp < g.start + g.cliff) return 0;

        uint256 elapsed = block.timestamp - g.start;
        uint256 vested = elapsed >= g.duration ? g.totalAmount : g.totalAmount * elapsed / g.duration;
        return vested - g.claimed;
    }

    function claim(bytes32 grantId) external {
        uint256 amount = claimable(grantId);
        require(amount > 0, "Nothing to claim");
        grants[grantId].claimed += amount;
        token.transfer(grants[grantId].recipient, amount);
    }

    // Revoke (si revocable)
    function revoke(bytes32 grantId) external onlyAdmin {
        Grant memory g = grants[grantId];
        require(g.revocable, "Not revocable");
        uint256 unvested = g.totalAmount - (g.claimed + claimable(grantId));
        token.transfer(admin, unvested);
        delete grants[grantId];
    }
}
```

**Distribution typique TGE :**
```
Team (20%):         4y vest, 1y cliff, linear
Investors (15%):    2y vest, 6mo cliff
Treasury/DAO (25%): Non-vested, gouvernance
Ecosystem (25%):    Liquidity mining + grants
Community (15%):    Airdrop + public sale
```

### 3.2 Airdrop — Merkle Distribution

```solidity
contract MerkleAirdrop {
    bytes32 public merkleRoot;
    IERC20 public token;
    mapping(address => bool) public claimed;

    function claim(uint256 amount, bytes32[] calldata proof) external {
        require(!claimed[msg.sender], "Already claimed");
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender, amount));
        require(MerkleProof.verify(proof, merkleRoot, leaf), "Invalid proof");
        claimed[msg.sender] = true;
        token.transfer(msg.sender, amount);
    }
}
```

## 4. Bonding Curves — Continuous Token Offering

### 4.1 Formule Mathématique

```solidity
// Bonding curve linéaire
// Prix = basePrice + slope * supply
contract BondingCurve {
    uint256 public basePrice = 0.001 ether;
    uint256 public slope = 0.0001 ether;
    uint256 public supply;
    ERC20 public token;

    function buy(uint256 amount) external payable {
        uint256 cost = getCost(amount);
        require(msg.value >= cost, "Insufficient ETH");

        token.mint(msg.sender, amount);  // Mint les tokens
        supply += amount;

        // Rembourser surplus
        if (msg.value > cost) payable(msg.sender).transfer(msg.value - cost);
    }

    function getCost(uint256 amount) public view returns (uint256) {
        // ∫(basePrice + slope * S) dS de supply à supply+amount
        uint256 endSupply = supply + amount;
        return basePrice * amount + slope * (endSupply * endSupply - supply * supply) / 2;
    }

    function sell(uint256 amount) external {
        require(token.balanceOf(msg.sender) >= amount, "Insufficient balance");
        uint256 revenue = getCost(amount); // Similaire à buy mais inverse
        token.burn(msg.sender, amount);
        supply -= amount;
        payable(msg.sender).transfer(revenue);
    }
}
```

**Types de courbes :**
- **Lineaire** : `P = a + b*S` — simple, prévisible
- **Exponentielle** : `P = a * e^(b*S)` — rareté rapide
- **Logarithmique** : `P = a * ln(1 + S)` — saturation
- **Sigmoid** : `P = L / (1 + e^(-k(S - x₀)))` — S-curve, adoption

## 5. veTokenomics (Vote-Escrowed Tokens)

Inspiré de Curve (veCRV) et popularisé par Convex, Frax, et d'autres.

### 5.1 Principe

```
Token → Lock (1-4 ans) → veToken (non-transférable)
    │                          │
    │                          ├── Vote sur les pools de récompenses
    │                          ├── Boost de farming (2.5x)
    │                          ├── Fees du protocole (partage)
    │                          └── Airdrop eligibility
    │
    └── Pas de lock → Token liquide mais pas de boost/vote
```

### 5.2 Implémentation

```solidity
contract VotingEscrow {
    struct LockedBalance {
        int128 amount;
        uint256 end;
    }

    mapping(address => LockedBalance) public locked;
    IERC20 public token;

    uint256 public constant MAX_TIME = 4 * 365 * 86400; // 4 ans

    // Lock tokens
    function createLock(uint256 amount, uint256 unlockTime) external {
        require(unlockTime <= block.timestamp + MAX_TIME, "Max 4y");
        token.transferFrom(msg.sender, address(this), amount);

        locked[msg.sender] = LockedBalance(int128(amount), unlockTime);
    }

    // Augmenter le lock time
    function increaseUnlockTime(uint256 newUnlockTime) external {
        LockedBalance storage lb = locked[msg.sender];
        require(newUnlockTime > lb.end, "Must extend");
        require(newUnlockTime <= block.timestamp + MAX_TIME, "Max 4y");
        lb.end = newUnlockTime;
    }

    // Voting power (décroît linéairement avec le temps)
    function getVotes(address user) external view returns (uint256) {
        LockedBalance memory lb = locked[user];
        if (lb.end <= block.timestamp) return 0;
        return lb.amount * (lb.end - block.timestamp) / MAX_TIME;
    }
}
```

### 5.3 Impact sur la Tokenomics

| Métrique | Sans veToken | Avec veToken |
|----------|-------------|--------------|
| **Volatilité** | Haute (free float) | Faible (lock réduit l'offre circulante) |
| **Gouvernance** | Faible participation | Engagée (les locks votent) |
| **TVL** | Moyenne | Élevée (boost incite au lock) |
| **Dumping (TGE)** | Risque élevé | Verrouillé pour 1-4 ans |
| **Prix** | Volatile | Plus stable (circ suppy réduit) |

## 6. Liquidity Mining (Yield Farming)

### 6.1 Distribution de Récompenses

```solidity
contract StakingRewards {
    IERC20 public stakingToken;
    IERC20 public rewardsToken;

    uint256 public rewardRate;          // Tokens/s
    uint256 public lastUpdateTime;
    uint256 public rewardPerTokenStored;
    mapping(address => uint256) public rewards;
    mapping(address => uint256) public userRewardPerTokenPaid;

    modifier updateReward(address account) {
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = block.timestamp;
        if (account != address(0)) {
            rewards[account] = earned(account);
            userRewardPerTokenPaid[account] = rewardPerTokenStored;
        }
        _;
    }

    function rewardPerToken() public view returns (uint256) {
        if (totalSupply() == 0) return rewardPerTokenStored;
        return rewardPerTokenStored + (block.timestamp - lastUpdateTime) * rewardRate * 1e18 / totalSupply();
    }

    function earned(address account) public view returns (uint256) {
        return balanceOf(account) * (rewardPerToken() - userRewardPerTokenPaid[account]) / 1e18 + rewards[account];
    }

    // Notify new rewards (appelé par le distributeur)
    function notifyRewardAmount(uint256 reward) external onlyOwner {
        rewardRate = reward / DURATION;
        lastUpdateTime = block.timestamp;
    }
}
```

### 6.2 Stratégies de Distribution

| Stratégie | Description | Exemple |
|-----------|-------------|---------|
| **Proportional** | Récompenses proportionnelles au stake | Uniswap (UNI) |
| **Weighted by pool** | Pools avec multiplicateur | Curve (gauge weights) |
| **Time-weighted** | Récompenses augmentent avec la durée | Sushi (xSUSHI) |
| **Decaying emissions** | Distribution qui diminue avec le temps | Compound (COMP) |
| **Vesting rewards** | Les récompenses sont verrouillées | Olympus (OHM) |

## 7. DAO Governance

### 7.1 Systèmes de Vote

| Système | Description | Forces | Faiblesses |
|---------|-------------|--------|------------|
| **Simple quorum** | >50% des votes, quorum 20% | Simple | Plutocratie |
| **Quadratic Voting** | Coût d'un vote = n² | Équitable | Sybil |
| **Conviction Voting** | Poids augmente avec la durée | Engagement | Lent |
| **Holographic Consensus** | Booster via stake | Scalable | Complexe |

### 7.2 Quadratic Voting Implementation

```solidity
contract QuadraticVoting {
    function vote(uint256 proposalId, address option, uint256 votes) external {
        // Le coût en tokens pour voter est votes²
        // Si l'utilisateur veut voter 5 fois, il paie 25 tokens
        uint256 cost = votes * votes;
        require(token.balanceOf(msg.sender) >= cost, "Insufficient");

        // Voter 1x = 1 token (1:1)
        // Voter 2x = 4 tokens (2:4)
        // Voter 10x = 100 tokens (10:100)
        // → Rend les gros votes très chers

        token.transferFrom(msg.sender, address(vault), cost);
        proposals[proposalId].results[option] += votes;
    }
}
```

## 8. Outils de Modélisation Tokenomics

| Outil | Usage | URL |
|-------|-------|-----|
| **Tokenomics Hub** | Analyse de distribution et schedule | tokenomicshub.ai |
| **Messari** | Research + data tokenomics | messari.io |
| **Token Unlocks** | Suivi des vesting schedules + cliff | token.unlocks.app |
| **Dune Analytics** | On-chain tokenomics dashboard | dune.com |
| **Nansen** | Holder analysis, whale tracking | nansen.ai |
| **LlamaRisk** | Évaluation des risques tokenomics | llamarisk.com |
| **Coingecko Terminal** | DeFi data, trading volume | coingecko.com/terminal |
