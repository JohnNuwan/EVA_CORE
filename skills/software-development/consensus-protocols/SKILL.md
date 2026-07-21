---
name: consensus-protocols
description: "Mécanismes de consensus blockchain — PoW, PoS, DPoS, PBFT, HotStuff, DAG-based (Avalanche, Hedera), PoH (Solana), PoET, Narwhal & Bullshark, Sui (Narwhal+Tusk), et comparaison détaillée des protocoles."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [consensus, pow, pos, pBFT, hotstuff, avalanche, hedera, solana, sui, aptos, polkadot, cosmos, ibft, narwhal, dag, proof-of-history, nock]
    related_skills: [layer2-scaling, defi-protocols, web3-dapp, smart-contracts]
---

# Protocoles de Consensus — Architecture, Théorie & Implémentation

## Quand utiliser ce skill

- Comprendre, comparer ou implémenter un mécanisme de consensus blockchain
- Concevoir une sidechain, un rollup ou une appchain avec son propre consensus
- Auditer les propriétés de sécurité (finality, liveness, fault tolerance) d'un protocole
- Développer un client validator / node dans un réseau décentralisé
- Implémenter un protocole BFT personnalisé pour un consortium

## 1. Fondements Théoriques

### 1.1 Le Problème des Généraux Byzantins

Un système est **Byzantin Fault Tolerant (BFT)** s'il tolère jusqu'à `f` nœuds défaillants ou malveillants sur `n = 3f + 1` nœuds.

```
Théorème de Lamport, Shostak, Pease (1982) :
- La communication synchrone (timeout connu) est nécessaire pour BFT
- f byzantins nécessitent au moins n >= 3f + 1 participants
- f crash nécessitent au moins n >= 2f + 1
```

### 1.2 Propriétés Fondamentales

| Propriété | Définition | Violation |
|-----------|------------|-----------|
| **Safety** | Aucun fork — tout le monde voit le même état | Double spend, reorg |
| **Liveness** | Le système continue de produire des blocs | Stalled chain, finality halt |
| **Finality** | Une fois confirmé, un bloc est définitif | Reorg, uncle blocks |
| **Censorship Resistance** | N'importe quelle tx valide est incluse | Front-running, blacklisting |
| **Fairness** | Ordre équitable des transactions | MEV, proposer bias |

### 1.3 CAP Theorem pour Blockchains

Tout protocole fait un compromis entre :
- **Consistency** — Tous les nœuds voient les mêmes données (Safety)
- **Availability** — Le système répond toujours (Liveness)
- **Partition Tolerance** — Fonctionne même avec des nœuds isolés

| Protocole | Consistency | Availability | Partition | Finality |
|-----------|-------------|--------------|-----------|----------|
| PoW (Bitcoin) | Faible (6 confirmations) | Haute | Haute | Probabiliste |
| PoS (Ethereum) | Haute (finality gadget) | Haute | Haute | 2 épisodes (~13min) |
| PBFT (Hyperledger) | Parfaite | Faible en partition | Très haute | Instantanée |
| Avalanche | Probabiliste | Haute | Haute | Probabiliste (~1s) |
| HotStuff (Diem) | Parfaite | Faible en partition | Haute | 1 vue |
| Narwhal+Tusk (Sui) | Parfaite | Haute | Haute | ~1s |

## 2. Proof of Work (PoW)

### 2.1 Fonctionnement

```
H(block_header) < Target   (Target ∝ 1/Difficulty)
```

```python
def mine_block(block, difficulty):
    target = 2**(256 - difficulty) - 1
    while True:
        block.nonce = secrets.randbits(64)
        h = hashlib.sha256(hashlib.sha256(block.serialize()).digest()).digest()
        if int.from_bytes(h, 'big') < target:
            return block.nonce, h
        block.nonce += 1
```

### 2.2 GHOST Rule (Greedy Heaviest Observed Subtree)

Ethereum PoW utilise GHOST pour sélectionner la branche la plus lourde (incluant les oncles), pas la plus longue :

```python
def ghost_choice(genesis):
    """Sélectionne la feuille avec le plus de travail cumulé"""
    total_weight = {}
    def weight(block):
        return 1 + sum(weight(child) for child in block.children)
    return max(chain.leaves, key=weight)
```

## 3. Proof of Stake (PoS) — Ethereum Casper FFG + LMD-GHOST

### 3.1 Architecture Ethereum PoS (Gasper)

- **Casper FFG (finality gadget)** : checkpoints votés par les validateurs, finalisation après 2/3 des votes
- **LMD-GHOST (fork choice)** : dernière message driven GHOST — sélectionne la branche avec le plus de votes

```python
class Validator:
    def __init__(self, balance, pubkey):
        self.balance = balance       # 32 ETH minimum
        self.effective_balance = balance
        self.activation_epoch = 0
        self.slashed = False
        self.withdrawable_epoch = far_future

class BeaconChain:
    def __init__(self):
        self.validators = []
        self.epoch = 0
        self.finalized_checkpoint = None

    def attest(self, validator_index, target_epoch, source_epoch, head_root):
        # Vote de consensus
        v = self.validators[validator_index]
        weight = v.effective_balance // 1e9  # GWei → ETH simplifié

        # Récompense si le vote est correct
        if target_epoch == self.epoch and head_root in self.chain:
            v.balance += weight * BASE_REWARD

    def slash(self, validator_index, proof):
        """Double vote ou vote contradictoire = slashing"""
        v = self.validators[validator_index]
        penalty = max(v.effective_balance // 32, 1 * 10**18)  # 1 ETH minimum
        v.balance -= penalty
        v.slashed = True
        v.withdrawable_epoch = self.epoch + 8192  # ~36 jours de mise en veille
```

### 3.2 Finality Computation

```python
def compute_finality(checkpoints):
    """Un checkpoint est finalisé s'il est justifié et que son enfant est justifié"""
    justified = {}
    for cp in checkpoints:
        if cp.votes >= 2/3 * total_balance:
            justified[cp.epoch] = cp
            if cp.epoch - 1 in justified:
                cp.finalized = True
```

### 3.3 Récompenses et Pénalités

| Action | Récompense/Pénalité | Fréquence |
|--------|---------------------|-----------|
| Attestation correcte | +base_reward * inclusion_delay_factor | Chaque epoch (~6.4min) |
| Proposer un bloc | +base_reward / 8 | ~1 fois/semaine |
| Sync committee | +base_reward * 2 | ~1 jour/256 jours |
| Slashing | Pénalité de 1/32 du stake + 3 jours de malus | Rare |
| Inactivité | Pénalité proportionnelle au temps offline | Continue |

## 4. PBFT — Practical Byzantine Fault Tolerance

### 4.1 Phases du Protocole

```
CLIENT → (REQUEST) → LEADER
LEADER → (PRE-PREPARE) → TOUS
CHAQUE → (PREPARE) → TOUS       # Quorum: 2f+1
CHAQUE → (COMMIT) → TOUS        # Quorum: 2f+1
CHAQUE → (REPLY) → CLIENT
```

### 4.2 Implémentation Simplifiée

```python
class PBFTNode:
    def __init__(self, node_id, n_nodes):
        self.id = node_id
        self.n = n_nodes
        self.f = (n_nodes - 1) // 3
        self.view = 0
        self.log = []
        self.state = {}  # Machine à états

    @property
    def is_primary(self):
        return self.view % self.n == self.id

    def handle_request(self, client_msg):
        if not self.is_primary:
            return self.forward_to(self.primary, client_msg)

        # Phase 1: Pre-prepare
        seq_no = len(self.log) + 1
        pp_req = {
            'type': 'PRE-PREPARE',
            'view': self.view,
            'sequence': seq_no,
            'digest': hash(client_msg.data),
            'data': client_msg.data
        }
        self.broadcast(pp_req)

    def handle_pre_prepare(self, msg):
        if self._verify(msg):
            # Phase 2: Prepare
            self.log.append(msg)
            prep = {'type': 'PREPARE', 'view': msg.view, 'sequence': msg.sequence,
                    'digest': msg.digest, 'node_id': self.id}
            self.broadcast(prep)

    def handle_prepare(self, msg):
        # Collecter 2f+1 PREPARE → Phase 3: Commit
        if self._count('PREPARE', msg.sequence) >= 2 * self.f:
            commit = {'type': 'COMMIT', 'view': msg.view, 'sequence': msg.sequence,
                      'digest': msg.digest, 'node_id': self.id}
            self.broadcast(commit)

    def handle_commit(self, msg):
        if self._count('COMMIT', msg.sequence) >= 2 * self.f + 1:
            # EXÉCUTION — appliquer l'opération à la machine à états
            self.state.update(msg.digest.data)
            self.send_reply(client)
```

## 5. HotStuff — BFT with Linear View Change

Utilisé par Libra/Diem puis amélioré par les protocoles modernes (Aptos, Sui).

### 5.1 Pipeline à 3 phases + View Change

```
Phase 1: PREPARE    ─┐
Phase 2: PRECOMMIT   ─┤  Chaque phase élève le niveau de sécurité
Phase 3: COMMIT      ─┘  Les 3 = bloc finalisé
```

**Avantage clé** : O(n) messages (vs O(n²) pour PBFT).

```python
class HotStuffNode:
    def __init__(self):
        self.high_qc = None   # Highest Quorum Certificate
        self.b_leaf = None    # Current leaf
        self.locked_qc = None # Locked QC (ne recule pas)

    def on_receive_proposal(self, proposal):
        # Vérifier que parent_qc ≥ high_qc
        if proposal.parent_qc >= self.high_qc:
            self.b_leaf = proposal.block
            # Nouveau vote
            self.send_vote(proposal)

    def advance(self, new_block):
        # View change simplifié
        # Chaque nouveau leader inclut le high_qc
        # Les validateurs ne votent que si locked_qc ≤ high_qc
        new_block.justify = self.high_qc
        self.broadcast(new_block)
```

## 6. DAG-Based Consensus — Avalanche

### 6.1 Avalanche Consensus Protocol

Métastabilité : pas de leader, pas de BFT classique. Les nœuds échantillonnent aléatoirement d'autres nœuds.

```python
class AvalancheNode:
    def __init__(self, confidence=20, alpha=0.8):
        self.confidence_threshold = confidence
        self.alpha = alpha  # Seuil de rejet
        self.preferred = True  # Vert ou rouge
        self.consecutive_success = 0

    def consensus_round(self, preference):
        """Échantillonner k nœuds, suivre la majorité"""
        k = 20  # Sample size
        samples = self.sample(k)
        count_yes = sum(1 for s in samples if s.preference)

        if count_yes / k >= self.alpha:
            self.preference = True
            self.consecutive_success += 1
        else:
            self.preference = False
            self.consecutive_success = 0

        return self.consecutive_success >= self.confidence_threshold
```

**Résultat** : Finalité probabiliste en ~1 seconde, scalable à milliers de validateurs.

### 6.2 Avalanche DAG (Structure Vertex)

```
Blocs connectés en DAG via des bords de référence :
  ┌─────┐    ┌─────┐    ┌─────┐
  │ v1  │────│ v2  │────│ v3  │────...
  └─────┘    └─────┘    └─────┘
      └────────┴───────────┘    (bords de préférence aléatoire)
```

## 7. Narwhal & Bullshark / Tusk (Sui & Mysten Labs)

Narwhal est un **mempool à haut débit** + Bullshark/Tusk est le **consensus**.

### 7.1 Narwhal — Primary Worker Model

```
Primary 1 ── Certificat ──┐
Worker 1a  ──── batch ────┤
Worker 1b  ──── batch ────┤  Narwhal = Dissémination asynchrone des transactions
Primary 2 ── Certificat ──┤
...                        ┘
               ↓
         Bullshark (consensus)
               ↓
          Committed blocks
```

**Performance**: Narwhal peut disséminer 100k+ tx/s, Bullshark les ordonne en <1s.

## 8. DAG Autres Protocoles

| Protocole | Type | Finality | TPS | Validateurs | Notes |
|-----------|------|----------|-----|-------------|-------|
| **Hedera Hashgraph** | Gossip + virtual voting | ~3-5s | 10k+ | 39 (mainnet) | Gossip about gossip, BFT asynchrone |
| **Avalanche (DAG)** | Métastabilité | ~1s | 4500+ | Scalable | Subnets, C-Chain EVM |
| **Fantom (Lachesis)** | DAG + ABFT | ~1s | 5000+ | Scalable | EVM compatible (Opera) |
| **IOTA Tangle** | DAG (DAG légèrement orienté) | Probabiliste | Illimité | 0 (sans mineurs) | Pas de frais, coordicide en cours |

## 9. Protocoles de Validation Alternatives

### 9.1 PoH — Proof of History (Solana)

Horodatage cryptographique continu (VDF — Verifiable Delay Function). Pas un consensus seul, mais un composant qui accélère le blocage.

```rust
// Simplifié — Solana utilise SHA-256 en chaîne
struct PoHEntry {
    hash: [u8; 32],    // hash(previous_hash || data)
    data: Vec<u8>,
    slot: u64,         // Index temporel
}

impl PoHGenerator {
    fn tick(&mut self) {
        self.current_hash = hash(&[self.current_hash, self.slot_counter.to_le_bytes()].concat());
        self.slot_counter += 1;
    }
}
```

**Avantage** : 400ms de slot, 4000+ transactions par slot → ~50k TPS soutenus.

### 9.2 PolkaDOT — GRANDPA + BABE

- **BABE** (Blind Assignment for Blockchain Extension) : production de blocs basée sur VRF
- **GRANDPA** (GHOST-based Recursive ANcestor Deriving Prefix Agreement) : finalité

```python
def grandpa_vote(chain, checkpoint):
    """Chaque validateur vote pour le plus récent bloc ancêtre des 2/3 validateurs"""
    # GRANDPA peut finaliser plusieurs blocs en une ronde
    # Contrairement à Casper qui finalise 1 checkpoint par epoch
    precommits = collect_precommits(checkpoint)
    if len(precommits) >= 2/3 * total_validators:
        chain.finalize(chain.best_block)
```

### 9.3 Cosmos — Tendermint BFT (CometBFT)

PBFT simplifié pour les appchains :

| Round | Phase | Description |
|-------|-------|-------------|
| 0 | Propose | Le proposer envoie un bloc |
| 1 | Pre-vote | Les validateurs votent |
| 2 | Pre-commit | Nouveau vote si ≥2/3 pre-votes |
| 3 | Commit | Final + retour au proposer suivant |
| View change | New round | Timeout → nouveau proposer |

## 10. Tableau Comparatif Final

| Métrique | Bitcoin (PoW) | Ethereum (PoS) | Solana (PoH+PoS) | Avalanche | Hedera | Sui (Narwhal) | Cosmos (Tendermint) |
|----------|---------------|----------------|------------------|-----------|--------|----------------|---------------------|
| **Finality** | ~60min (6 blocs) | ~13min (2 epochs) | ~400ms (slot) | ~1s | ~5s | ~1s | ~7s |
| **Throughput** | ~7 TPS | ~15 TPS (L1) | ~50k TPS | ~4500 TPS | ~10k TPS | ~100k+ TPS | ~10k TPS |
| **Validateurs** | 1M+ (mineurs) | ~900k | ~2000 | ~1500 | 39 (en growth) | ~100+ | 100-150 |
| **BFT Tolerance** | 50% hashrate | 1/3 stake | 1/3 stake | <1/2 stake | 1/3 | 1/3 | 1/3 |
| **Energy** | Très élevée | Très faible | Faible | Faible | Faible | Faible | Faible |
| **Complexité** | Faible | Très élevée | Haute | Moyenne | Élevée | Très élevée | Moyenne |
