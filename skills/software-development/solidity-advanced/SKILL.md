---
name: solidity-advanced
description: "Solidity avancé — assembly Yul, gas golf extrême, optimisations EVM, patterns de sécurité avancés, EIP-712, EIP-2535 (Diamond), EIP-4626, et ERC-4337 (Account Abstraction)."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [solidity, yul, assembly, evm, opcodes, gas-golf, diamond-standard, account-abstraction, erc-4337, eip-2535]
    related_skills: [smart-contracts, defi-protocols, nft-development, layer2-scaling]
---

# Solidity Avancé — Assembly, Gas Golf & Patterns Émergents

## Quand utiliser ce skill

- Optimisation de gas extrême (competitions, protocoles à fort volume)
- Implémentations en Yul/Assembly pour des contrats critiques
- Standards avancés : Diamond (EIP-2535), Account Abstraction (ERC-4337), ERC-4626
- Sécurité avancée : timelocks, gouvernance, signature aggregation

## 1. Yul / Assembly Inline

### 1.1 Opérations mémoire

```solidity
// Lire le slot de stockage directement (0 SLOAD si déjà en cache)
function readStorageSlot(bytes32 slot) external view returns (bytes32 value) {
    assembly {
        value := sload(slot)
    }
}

// Copier des données calldata → memory sans SLOAD
function fastArrayCopy(uint256[] calldata data) internal pure returns (uint256[] memory out) {
    assembly {
        let len := data.length
        out := mload(0x40)
        mstore(out, len)
        let src := data.offset
        let dst := add(out, 0x20)
        for { let i := 0 } lt(i, len) { i := add(i, 1) } {
            mstore(dst, calldataload(src))
            src := add(src, 0x20)
            dst := add(dst, 0x20)
        }
        mstore(0x40, dst)  // Free memory pointer update
    }
}
```

### 1.2 Return Data sans abi.encode

```solidity
// Économise le coût d'abi.encode (~200 gas)
function returnTwoValues() external pure returns (uint256 a, address b) {
    assembly {
        a := 42
        b := address()
        mstore(0x00, a)
        mstore(0x20, b)
        return(0x00, 0x40)
    }
}
```

### 1.3 create2 — Déploiement à adresse déterministe

```solidity
function deployDeterministic(bytes memory bytecode, bytes32 salt) internal returns (address addr) {
    assembly {
        addr := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
        if iszero(extcodesize(addr)) { revert(0, 0) }
    }
}
// Calculer l'adresse avant déploiement (utile pour les counterfactuals)
function getAddress(bytes memory bytecode, bytes32 salt) internal view returns (address) {
    bytes32 hash = keccak256(abi.encodePacked(
        bytes1(0xff), address(this), salt, keccak256(bytecode)
    ));
    return address(uint160(uint256(hash)));
}
```

## 2. EIP-2535 Diamond Standard (Multi-facet Proxy)

Permet de dépasser la limite de 24KB des contrats EVM en découpant la logique en plusieurs facets.

```solidity
// DiamondCut — ajouter/remplacer/supprimer des fonctions
struct FacetCut {
    address facetAddress;
    FacetCutAction action;
    bytes4[] functionSelectors;
}

function diamondCut(FacetCut[] calldata _diamondCut, address _init, bytes calldata _calldata) external onlyOwner {
    LibDiamond.enforceIsContractOrEoa(_init);
    uint256 selectorCount = LibDiamond.diamondStorage().selectors.length;

    for (uint256 i = 0; i < _diamondCut.length;) {
        LibDiamond.diamondCutStorage[_diamondCut[i].action](
            _diamondCut[i].facetAddress,
            _diamondCut[i].functionSelectors
        );
        unchecked { ++i; }
    }

    LibDiamond.initializeDiamondCut(_init, _calldata);
    emit DiamondCut(_diamondCut, _init, _calldata);
}
```

**Avantages** : Upgradeable sans limite de taille, modules indépendants, gas partagé.

## 3. ERC-4337 Account Abstraction

Les wallets deviennent des smart contracts. Transactions `UserOperation` via un bundler → EntryPoint → wallet contract.

```solidity
// Wallet abstrait compatible ERC-4337
contract MyWallet is IAccount {
    function validateUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external override returns (uint256 validationData) {
        // Vérifier la signature EIP-712
        bytes32 hash = MessageHashUtils.toEthSignedMessageHash(userOpHash);
        address recovered = userOp.signature.recover(hash);
        require(recovered == owner, "Invalid signature");

        // Payer le gas
        if (missingAccountFunds > 0) {
            (bool success,) = msg.sender.call{value: missingAccountFunds}("");
            (success);
        }
        return 0; // 0 = succès
    }
}
```

**Cas d'usage** : Gasless transactions, social recovery, batch operations, key rotation.

## 4. EIP-4626 Tokenized Vault Standard

Standard unifié pour les yield-bearing vaults (Aave, Compound, Yearn).

```solidity
contract MyVault is ERC4626 {
    using SafeERC20 for IERC20;

    constructor(IERC20 _asset, string memory _name, string memory _symbol)
        ERC4626(_asset) ERC20(_name, _symbol) {}

    // Implémentation du yield
    function totalAssets() public view override returns (uint256) {
        return asset.balanceOf(address(this));
    }

    // Surcharge pour le compounding automatique
    function _deposit(address caller, address receiver, uint256 assets, uint256 shares)
        internal override {
        super._deposit(caller, receiver, assets, shares);
        _compoundYield();
    }

    function _compoundYield() internal {
        uint256 balance = asset.balanceOf(address(this));
        if (balance > 0) _deployToYieldSource(balance);
    }
}
```

## 5. EIP-712 Typed Structured Data Signatures

```solidity
bytes32 constant PERMIT_TYPEHASH = keccak256(
    "Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"
);
bytes32 constant DOMAIN_SEPARATOR = keccak256(abi.encode(
    keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
    keccak256("Token"),
    keccak256("1"),
    block.chainid,
    address(this)
));

function permit(address owner, address spender, uint256 value, uint256 deadline,
    uint8 v, bytes32 r, bytes32 s) external {
    require(block.timestamp <= deadline, "Expired");
    bytes32 structHash = keccak256(abi.encode(PERMIT_TYPEHASH, owner, spender, value, nonces[owner]++, deadline));
    bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash));
    address signer = ecrecover(digest, v, r, s);
    require(signer == owner, "Invalid signature");
    _approve(owner, spender, value);
}
```

## 6. Gas Golf Extrême — Table des Coûts

| Opération | Gas | Alternative optimisée | Économie |
|-----------|-----|----------------------|----------|
| SLOAD (froid) | 2100 | Calldata (0) / Immutable (3 depl.) | ~2100 |
| SLOAD (chaud) | 100 | Memoriaiser en mémoire | ~97 |
| SSTORE (0→v) | 22100 | pack struct | — |
| WASM + CALL | ~2600 | 0 si déjà warm | — |
| abi.encode | 500+ | Raw memory packing | 200-500 |
| require() | variable | Custom error `revert Error()` ≤200 | ~100 |
| Modifier | 150+ | Fonction interne | 50-150 |
| Transfer ETH | ~6700 | call{gas: stipend} | ~500 |

## 7. Patterns de Sécurité Avancés

### 7.1 Timelock Controller

```solidity
contract TimelockController {
    uint256 public immutable delay; // ex: 2 jours
    mapping(bytes32 => bool) public operations;

    function schedule(address target, bytes calldata data, bytes32 predecessor, bytes32 salt)
        external onlyRole(PROPOSER_ROLE) {
        bytes32 id = hashOperation(target, data, predecessor, salt);
        operations[id] = true;
        emit CallScheduled(id, 0, target, 0, data, predecessor, delay, salt);
    }

    function execute(address target, bytes calldata data, bytes32 predecessor, bytes32 salt)
        external payable onlyRole(EXECUTOR_ROLE) {
        bytes32 id = hashOperation(target, data, predecessor, salt);
        require(operations[id], "Not scheduled");
        require(block.timestamp >= getTimestamp(id) + delay, "Too early");
        operations[id] = false;
        _call(target, 0, data);
    }
}
```

### 7.2 Signature Aggregation (EIP-712 + BLS)

Pour la gouvernance on-chain : agréger des centaines de votes en une seule tx via BLS (boneh-lynn-shacham) ou ECDSA batch.

## 8. Outils d'Analyse Avancée

| Outil | Usage | Commande |
|-------|-------|----------|
| **Slither** | Analyse statique (détection vulns, visualisation inheritance) | `slither .` |
| **Echidna** | Property-based fuzzing | `echidna-test src/ --config config.yaml` |
| **Certora** | Formal verification | `certoraRun src/Contract.sol --verify Contract:spec.spec` |
| **Halmos** | Symbolic execution (open source) | `halmos --sym-var uint256` |
| **GasReporter** | Gas usage per function | `npx hardhat gas-reporter` |
| **Surya** | Diagrammes d'héritage + graphe d'appels | `surya inheritance src/` |
