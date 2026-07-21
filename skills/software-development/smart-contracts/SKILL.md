---
name: smart-contracts
description: "Architecture, développement, audit et déploiement de smart contracts — patterns de sécurité, optimisation de gas, tests formels, et lifecycle mainnet/testnet."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [solidity, vyper, hardhat, foundry, smart-contracts, security, audit, ethereum, evm]
    related_skills: [solidity-advanced, defi-protocols, web3-dapp, layer2-scaling]
---

# Développement de Smart Contracts — Architecture & Sécurité

## Quand utiliser ce skill

- L'utilisateur doit concevoir, implémenter ou auditer un smart contract EVM (Ethereum, Polygon, Arbitrum, Optimism, Base)
- Besoin de déployer un contrat avec Hardhat ou Foundry sur testnet/mainnet
- Audit de sécurité : vulnérabilités, pattern de design, optimisation de gas
- Bridge entre Solidity et les couches d'interaction web3

## 1. Stack Technique et Outillage

### Frameworks recommandés

| Outil | Usage | Quand |
|-------|-------|-------|
| **Hardhat** | Développement, tests, réseau local, plugins | Projets standards, équipe, debugging |
| **Foundry** | Tests ultra-rapides en Solidity natif (forge), fuzzing, invariant testing | Projets avancés, sécurité, gas golf |
| **Remix IDE** | Prototypage rapide en ligne | Quick contracts, debugging direct |

### Installation

```bash
# Hardhat
npm init -y && npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat

# Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

## 2. Patterns de Design Essentiels

### 2.1 Proxy Patterns (Upgradeability)

```solidity
// Proxy transparent (UUPS vs Transparent)
// UUPS — mise à jour dans l'implémentation (moins cher, plus sûr si bien fait)
contract MyContract is Initializable, UUPSUpgradeable {
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() { _disableInitializers(); }

    function initialize(address owner) public initializer {
        __Ownable_init(owner);
        __UUPSUpgradeable_init();
    }

    function _authorizeUpgrade(address newImplementation)
        internal override onlyOwner {}
}
```

### 2.2 Minimal Proxy (Clone Factory / ERC-1167)

Pour déployer des centaines d'instances à coût réduit :

```solidity
contract CloneFactory {
    function createClone(address target) internal returns (address result) {
        bytes20 targetBytes = bytes20(target);
        assembly {
            let clone := mload(0x40)
            mstore(clone, 0x3d602d80600a3d3981f3363d3d373d3d3d363d73)
            mstore(add(clone, 0x14), targetBytes)
            mstore(add(clone, 0x28), 0x5af43d82803e903d91602b57fd5bf3)
            result := create(0, clone, 0x37)
        }
    }
}
```

### 2.3 Pull Over Push (Retraits sécurisés)

```solidity
// ❌ Push — vulnérable au reentrancy et aux transferts bloqués
payable(user).transfer(amount);

// ✅ Pull — l'utilisateur retire lui-même
mapping(address => uint256) public balances;

function withdraw() external {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;
    (bool success,) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

## 3. Sécurité — Les 10 Vulnérabilités Mortelles

| # | Vulnérabilité | Description | Mitigation |
|---|---------------|-------------|------------|
| 1 | **Reentrancy** | Appel externe rappelle votre fonction avant mise à jour de l'état | CEI (Checks-Effects-Interactions), ReentrancyGuard |
| 2 | **Integer Overflow/Underflow** | Dépassement de capacité (Solidity ^0.8 inclut checked math) | Utiliser SafeMath ou ^0.8 |
| 3 | **Access Control** | Fonctions sans modificateur onlyOwner / onlyRole | OpenZeppelin Ownable, AccessControl |
| 4 | **Front-running** | MEV — les mineurs/validateurs voient vos tx en attente | Commit-Reveal, Submarine, Flashbots |
| 5 | **Oracle Manipulation** | Manipulation du prix via un oracle décentralisé | TWAP (Uniswap V3), Chainlink, RedStone |
| 6 | **Flash Loan Attacks** | Attaque à capital zéro via prêts flash | Limiter les dépendances aux pools de liquidité |
| 7 | **Signature Replay** | Réutilisation d'une signature signée sur une autre chaîne | EIP-712 avec chainId, nonce, deadline |
| 8 | **Delegatecall Injection** | Modification dangereuse du contexte de stockage | Proxy pattern strict, séparation logique/données |
| 9 | **Rounding Errors** | Erreurs d'arrondi dans les calculs de ratio | Multiplier avant de diviser (fixed-point math) |
| 10 | **Denial of Service** | Boucle infinie, array unbounded, griefing | Gas limit, limites de taille, pull pattern |

## 4. Optimisation de Gas — Techniques Clés

- **Storage vs Memory vs Calldata** : Lire storage coûte ~2100 gas ; memory ~3 gas. Charger en mémoire dès que possible.
- **Struct packing** : Ordonner les types par taille (uint128, uint128 avant uint256) pour utiliser un seul slot.
- **Short-circuit** : Tester les conditions les moins chères d'abord dans les `require`.
- **Immutable & Constant** : `uint256 immutable` stocké dans le bytecode (pas de SLOAD).
- **Batch operations** : Un tableau d'inputs plutôt que N transactions.
- **Yul/Assembly** : Opérations bas niveau pour le gas golf extrême (réservé aux experts).

```solidity
// Avant — 3 SLOADs
function getValue() external view returns (uint256 a, uint256 b) {
    return (storageVar1, storageVar2);
}

// Après — 0 SLOAD (immutable)
uint256 immutable DEPLOYED_AT = block.timestamp;
```

## 5. Déploiement et Vérification

```bash
# Hardhat deploy + verify
npx hardhat run scripts/deploy.ts --network sepolia
npx hardhat verify --network sepolia <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>

# Foundry
forge script script/Deploy.s.sol:DeployScript --rpc-url sepolia --broadcast --verify
```

## 6. Tests et Audit

```solidity
// Foundry — fuzzing automatique
function testFuzz_RevertIfInvalidAmount(uint256 amount) public {
    vm.assume(amount > 0 && amount < 1e30);
    uint256 balanceBefore = token.balanceOf(address(this));
    token.approve(address(swapRouter), amount);
    // ...
}
```

### Checklist d'audit
- [ ] CEI pattern partout (Checks → Effects → Interactions)
- [ ] Pas de delegatecall vers des adresses non contrôlées
- [ ] ERC-712 pour les signatures (replay protection)
- [ ] Tests d'invariant Foundry (fuzzing + stateless)
- [ ] Analyse statique (Slither, Mythril, 4naly3er)
- [ ] Limites sur les boucles (griefing)
- [ ] Fonctions pause/emergency (Pausable d'OZ)
