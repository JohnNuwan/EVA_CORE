---
name: layer2-scaling
description: "Solutions de passage à l'échelle Layer 2 — Optimistic Rollups (Arbitrum, Optimism), ZK-Rollups (zkSync, StarkNet, Scroll), Validiums, Volitions, State Channels, Plasma, sidechains (Polygon PoS), et solutions hybrides."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [layer2, optimistic-rollup, zk-rollup, arbitrum, optimism, zksync, starknet, scroll, polygon, sidechain, validium, state-channel, plasma, bridging, celestia]
    related_skills: [smart-contracts, consensus-protocols, defi-protocols, solidity-advanced]
---

# Layer 2 — Passage à l'Échelle de la Blockchain

## Quand utiliser ce skill

- Comprendre et choisir la bonne solution L2 (rollup, sidechain, validium)
- Déployer un contrat sur Arbitrum, Optimism, zkSync, StarkNet ou Scroll
- Développer un bridge cross-L2 (messaging, token bridging)
- Implémenter un custom Validium ou Volition
- Comprendre les mathématiques des ZK-proofs (Groth16, PLONK, STARK)
- Concevoir une architecture L3 sur un L2 (appchain L3, hyperchains)

## 1. Taxonomie des Solutions L2

```
                     Solutions L2
                    /            \
           Rollups                  Sidechains
          /       \               /        \
   Optimistic    ZK-Rollup   Polygon PoS   xDai/Gnosis
   (Arbitrum,    (zkSync,    (checkpoint  (consensus
    Optimism)     StarkNet,   plasma)      propre)
                  Scroll)

   Validity / Volition → Hybride validium (données off-chain, proofs on-chain)
   State Channels → Lightning, Raiden (pair-à-pair, instantané)
   Plasma → Rootstock, Polygon Plasma (arbres Merkle, fraud proofs simplifiés)
```

## 2. Optimistic Rollups

### 2.1 Architecture Principe

```
L2 Sequencer
    │
    ├── Reçoit les transactions utilisateurs
    ├── Les ordonne et les exécute
    ├── Publie batch de transactions compressées sur L1
    └── Met à jour l'état L2
            │
            ▼
L1: Bridge contract + sequencer inbox
    │   - Vérifie les proofs de fraude (7 jours de challenge)
    │   - Challenge window: 7 jours sur Arbitrum, ~7 jours sur Optimism
    ▼
Finalité L1 (~13 min) après challenge window
```

### 2.2 Contrat Bridge Optimistic

```solidity
// Simplifié — bridge Optimism
contract L2OutputOracle {
    struct OutputProposal {
        bytes32 outputRoot;   // Hash de l'état L2
        uint128 timestamp;
        uint128 l2BlockNumber;
    }

    OutputProposal[] public proposals;
    uint256 public submissionInterval = 1800;  // ~30 min L1
    uint256 public finalizationPeriod = 7 days;

    function proposeL2Output(bytes32 outputRoot, uint256 l2BlockNumber) external {
        require(msg.sender == sequencer, "Only sequencer");
        proposals.push(OutputProposal(outputRoot, block.timestamp, l2BlockNumber));
    }

    function finalizeWithdrawal(
        bytes calldata withdrawalData,
        bytes32[] calldata merkleProof,
        uint256 outputIndex
    ) external {
        // 1. Vérifier que la challenge window est passée
        require(block.timestamp >= proposals[outputIndex].timestamp + finalizationPeriod, "Not finalizable");

        // 2. Vérifier le Merkle proof dans l'output root
        bytes32 root = proposals[outputIndex].outputRoot;
        require(MerkleProof.verify(merkleProof, root, keccak256(withdrawalData)), "Invalid proof");

        // 3. Exécuter le retrait
        (bool success,) = msg.sender.call(withdrawalData);
        require(success, "Withdrawal failed");
    }
}
```

### 2.3 Arbitrum vs Optimism

| Caractéristique | Arbitrum (Nitro) | Optimism (OP Stack) |
|-----------------|-------------------|---------------------|
| **VM** | Geth (WASM) | Geth (EVM équivalent) |
| **Preuves de fraude** | Interactive (multi-round) | Single-round |
| **Challenge window** | 7 jours | 7 jours |
| **Frais L2** | ~$0.01-0.05 | ~$0.01-0.05 |
| **Finalité L1** | ~1 semaine | ~1 semaine |
| **Bridging** | Native (TokenBridge, Arbitrum Bridge) | Native (Standard Bridge) |
| **EVM équivalence** | Complète (Nitro) | Complète (Bedrock) |
| **Native USDC** | ✅ (CCTP) | ✅ (CCTP) |
| **Gas token** | ETH | ETH |
| **Fraud proof** | AnyTrust (alternate: validium) | Fault proof (Cannon) |

## 3. ZK-Rollups

### 3.1 Comment Fonctionne un ZK-Rollup

```
Utilisateurs → Transactions L2 → Prover
                                ↓
                     Génère un ZK-Proof
                     (Groth16, PLONK, STARK)
                                ↓
                     Verify contract on L1
                     Vérifie la preuve + état mis à jour
```

**Avantage clé** : pas de challenge window — finalité instantanée sur L1 dès que le proof est vérifié.

### 3.2 ZK Math — Les Fondamentaux

```python
# Concept QAP (Quadratic Arithmetic Program) — simplifié
# Un programme est transformé en contraintes de rang 1 (R1CS)
# Puis en Polynomial IOP
# Puis compressé via des engagement schemes (KZG, FRI)

# Exemple : prouver qu'on connaît x, y tel que x³ - 3x² + 2x = y
# R1CS :
#   s[0] * s[0] = s[1]       # s[1] = x²
#   s[1] * s[0] = s[2]       # s[2] = x³
#   3 * s[1] = s[3]          # s[3] = 3x²
#   2 * s[0] = s[4]          # s[4] = 2x
#   s[2] - s[3] + s[4] = s[5]  # s[5] = y
```

**Groth16** (zkSync Lite, Loopring) : Proofs très petits (128-256 octets), vérification rapide (~3ms), nécessite une trusted setup.

**PLONK** (zkSync Era) : Universal trusted setup, plus flexible que Groth16.

**STARK** (StarkNet) : Pas de trusted setup, transparent, plus gros proofs (~100KB), vérification plus lente.

### 3.3 Comparaison ZK-Rollups

| | zkSync Era | StarkNet | Scroll | Polygon zkEVM |
|---|---|---|---|---|
| **Type** | ZK-Rollup | ZK-Rollup | ZK-Rollup | ZK-Rollup |
| **VM** | zkEVM (LLVM-based) | Cairo VM | zkEVM | zkEVM |
| **Langage** | Solidity + LLVM | Cairo | Solidity | Solidity |
| **EVM compatible** | Oui (partiel) | Non (Cairo natif) | Oui (complet) | Oui |
| **Proof system** | PLONK++ | STARK | Halo2 | PIL / zkProver |
| **Finality** | ~1h (prover time) | ~quelques heures | ~30min | ~1h |
| **TPS** | ~10k+ | ~50k+ (théorique) | ~5k | ~2k |
| **Bridge** | Native + third party | Native + third party | Native | Native |
| **Trusted setup** | Oui (universal) | Non (STARK) | Oui (Halo2) | Oui |

### 3.4 Déploiement sur zkSync Era

```solidity
// zkSync Era — Solidity natif
// Déploiement standard Hardhat
// Pas de modification de contrat nécessaire
// MAIS attention aux différences subtiles :

// 1. CREATE2 disponible (pas besoin du pattern proxy)
// 2. Contract addresses = déterministes (CREATE = CREATE2 behaviour)
// 3. Gas estimation = différente (utilisation de gas multi-dimensionnel)

// 4. Paymaster — gasless transactions
contract Paymaster is IPaymaster {
    function validateAndPayForPaymasterTransaction(
        bytes32 _txHash,
        bytes32 _suggestedSignedHash,
        Transaction calldata _transaction
    ) external returns (bytes4 magic, bytes memory context) {
        // Valider que le user peut payer en USDC au lieu d'ETH
        return (IPaymaster.VALIDATION_SUCCESS, "");
    }
}
```

## 4. Bridges — Le Maillon Faible

### 4.1 Classification des Bridges

| Type | Sécurité | Rapidité | Exemple |
|------|----------|----------|---------|
| **Native (canonical)** | Maximale (même sécurité L1) | 7j (OR) / qq min (ZK) | Arbitrum Bridge, Optimism Bridge |
| **Liquidity Network** | Capital-efficient, risqué | Rapide (<1 min) | Stargate, Across |
| **Third-party (liquidity pools)** | Dépend du protocole | Instantané | Hop, Synapse, Connext |
| **Validator/MPC** | Dépend des valideurs | Rapide | Wormhole, Multichain (AnySwap) |
| **Optimistic (relay + challenge)** | Haute (~L1) | 30 min - 1h | Nomad |

### 4.2 Vulnerabilités Historiques des Bridges

| Incident | Bridge | Perte | Cause |
|----------|--------|-------|-------|
| **Ronin Bridge** | Axie Infinity | $625M | Validation compromise (5/9 clés) |
| **Wormhole** | Solana-Ethereum | $325M | Signature verification vuln |
| **Nomad** | Optimistic | $190M | Zero-address parameter flaw |
| **Multichain** | AnySwap | $130M | MPC/validator compromise |
| **Poly Network** | Cross-chain | $611M (rendu) | Smart contract vuln |
| **Orbit Bridge** | Klaytn | $82M | Proxy contract backdoor |

### 4.3 Implémentation Simplifiée d'un Bridge Canonique

```solidity
// L1 Bridge
contract L1Bridge {
    mapping(address => uint256) public deposits;
    address public l2Bridge;

    event DepositInitiated(address indexed user, address token, uint256 amount);

    function depositETH() external payable {
        require(msg.value > 0, "Amount must be > 0");
        deposits[msg.sender] += msg.value;
        emit DepositInitiated(msg.sender, address(0), msg.value);
    }

    function finalizeWithdrawal(address user, uint256 amount, bytes32[] calldata proof) external {
        // Vérifier proof du L2 → L1
        require(block.timestamp >= challengeWindowEnd, "Still challengeable");
        deposits[user] -= amount;
        payable(user).transfer(amount);
    }
}

// L2 Bridge
contract L2Bridge {
    address public l1Bridge;

    function withdrawETH(uint256 amount) external {
        // Brûler le wETH or native ETH sur L2
        payable(l1Bridge).transfer(amount);
        // L2 bridge emet un event que le L1 bridge écoute
    }
}
```

## 5. Sidechains (Polygon PoS, Gnosis Chain)

Contrairement aux rollups, chaque sidechain a son propre consensus et sa propre sécurité.

| | Polygon PoS | Gnosis Chain | xDai |
|---|---|---|---|
| **Consensus** | PoS (Bor + Heimdall) | PoS (Geth + Gnosis Beacon) | PoA → PoS |
| **Bridge** | Plasma + PoS bridge | Omnibridge | xDai bridge |
| **Sécurité** | Dépend des valideurs Polygon | Dépend des valideurs Gnosis | Validateurs en nombre limité |
| **Temps de bloc** | ~2.5s | ~5s | ~5s |
| **Finalité** | ~64 blocs (~2.5min) | ~5min | ~5min |
| **Avantage** | Faible coût, large écosystème | Stablecoin xDai, décentralisé | Stable, peu de frais |

## 6. State Channels (Lightning, Raiden)

### 6.1 Principe

```
Alice ──[channel open]── Bob
   │                       │
   ├── 1.0 ETH ──────────┤   (état initial)
   ├── 0.8 ETH → 0.2 ETH ┤   (off-chain, signature)
   ├── 0.3 ETH → 0.7 ETH ┤   (off-chain, nouvelle signature)
   │                       │
   └──[channel close]─────┘   (dernier état signé → on-chain)
```

**Avantages** : Instantané, zéro frais, passage à l'échelle infini.
**Inconvénients** : Complexité UX, nécessite de garder les participants en ligne, nécessite un dépôt de capital.

## 7. Validium et Volition

### 7.1 Validium

Données hors-chaîne (data availability committee) + ZK-proof on-chain.

```
Données → Data Availability Committee (DAC)
Proof → L1 (verify contract)
```

**Tradeoff** : Moins cher (données off-chain) mais moins sécurisé (disponibilité des données).

**Exemple** : Arbitrum AnyTrust, zkSync Era (mode validium optionnel).

### 7.2 Volition (zkSync Era)

Hybride : chaque utilisateur choisit rollup (data on-chain) ou validium (data off-chain) par transaction.

## 8. Data Availability (DA) Solutions

| Solution | Type | TPS | Frais | Sécurité |
|----------|------|-----|-------|----------|
| **Ethereum (blobs EIP-4844)** | L1 DA | ~100k (blobs) | Faible (blob market) | Très haute |
| **Celestia** | Modular DA | ~6.7 MB/s | Très faible | Data availability sampling |
| **EigenDA** | Restaked DA | ~10 MB/s | Très faible | EigenLayer restaking |
| **Avail** | Polygon DA | ~1 MB/s | Faible | Validium-ready |
| **Near DA** | Fast finality | ~5 MB/s | Faible | Near consensus |

### EIP-4844 Proto-Danksharding

```python
# Nouveau type de transaction : BlobTransaction
# Les blobs ne sont pas stockés éternellement (~18 jours)
# Utilisé par les rollups pour publier des données à coût réduit

class BlobTransaction:
    blob_versioned_hash: bytes32  # hash(commitment, version)
    max_fee_per_blob_gas: uint256
    blob_gas: uint256

# Nouveaux opcodes :
# BLOBHASH (0x49) — récupérer le hash d'un blob
# TLOAD / TSTORE — transitory storage (utile pour rollups)
```

## 9. Tableau de Décision — Quelle L2 Choisir ?

| Cas d'usage | Recommandation | Raison |
|-------------|---------------|--------|
| Déploiement EVM simple | Arbitrum ou Optimism | Compatibilité totale, écosystème large |
| ZK natif (Cairo) | StarkNet | Performance, finalité rapide |
| EVM + ZK | zkSync Era | Bon équilibre, volition disponible |
| Gaming, haute fréquence | Validium (Immutable X) | Zéro gas pour les utilisateurs |
| Bridge entre rollups | Across, Stargate | Liquidité agrégée |
| Appchain modulaire | Celestia + Polygon CDK | Contrôle total de la stack |
| Finance institutionnelle | Arbitrum (Nitro) | Sécurité, track record |
