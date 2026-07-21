---
name: blockchain-cryptography
description: Guide complet de la cryptographie blockchain — Merkle Trees, BLS signatures, Schnorr, Account Abstraction, Threshold Signatures, zk-Rollups, MEV, et protocoles blockchain.
category: cybersecurite
tags: [blockchain, merkle-tree, bls, schnorr, threshold, ethereum, bitcoin, cryptography]
---

# Cryptographie Blockchain — Guide Approfondi

## Sommaire
1. [Merkle Trees et Patricia Merkle Tries](#merkle-trees)
2. [Signatures dans Bitcoin](#signatures-bitcoin)
3. [Signatures dans Ethereum](#signatures-ethereum)
4. [BLS Aggregation (Ethereum 2.0)](#bls-aggregation)
5. [Schnorr et Taproot (Bitcoin)](#schnorr-taproot)
6. [Account Abstraction (EIP-4337)](#account-abstraction)
7. [Threshold Cryptography en Blockchain](#threshold-crypto)
8. [zk-Rollups Cryptographie](#zk-rollups)
9. [MEV et Protocoles](#mev-et-protocoles)

---

## 1. Merkle Trees et Patricia Merkle Tries

### 1.1 Binary Merkle Tree

Structure arborescente où chaque nœud est un hash de ses enfants.

```
         Root = H(H01 || H23)
        /                     \
   H01 = H(H0 || H1)       H23 = H(H2 || H3)
    /        \                /         \
  H0=H(Tx0)  H1=H(Tx1)    H2=H(Tx2)  H3=H(Tx3)
```

**Propriétés** :
- Vérification d'un élément : `O(log n)` hashs
- Preuve : le chemin (siblings) de la feuille à la racine
- **SPV (Simplified Payment Verification)** : un nœud léger peut vérifier une transaction avec seulement la racine de Merkle

```python
import hashlib

class MerkleTree:
    def __init__(self, leaves):
        self.leaves = [hashlib.sha256(l).digest() for l in leaves]
        self.nodes = self._build(self.leaves)
        self.root = self.nodes[-1][0] if self.nodes else None
    
    def _build(self, level):
        levels = [level]
        while len(level) > 1:
            next_level = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1] if i + 1 < len(level) else left
                combined = hashlib.sha256(left + right).digest()
                next_level.append(combined)
            levels.append(next_level)
            level = next_level
        return levels
    
    def get_proof(self, index):
        """Retourne le chemin de preuve pour une feuille donnée"""
        proof = []
        for level in self.nodes[:-1]:  # Tous les niveaux sauf la racine
            sibling_idx = index ^ 1 if index % 2 == 0 else index ^ 1
            if sibling_idx < len(level):
                proof.append(level[sibling_idx])
            index //= 2
        return proof
    
    @staticmethod
    def verify_proof(root, leaf, proof, index):
        """Vérifie qu'une feuille est dans l'arbre"""
        current = hashlib.sha256(leaf).digest()
        for sibling in proof:
            if index % 2 == 0:
                current = hashlib.sha256(current + sibling).digest()
            else:
                current = hashlib.sha256(sibling + current).digest()
            index //= 2
        return current == root
```

### 1.2 Merkle Patricia Trie (Ethereum)

Structure plus complexe utilisée par Ethereum pour le **State Trie** :

```python
# Ethereum utilise un hexary Merkle Patricia Trie
# Chaque nœud peut être :
# - NULL : nœud vide
# - Branch : 16 enfants (0x0-0xF) + valeur
# - Extension : chemin + nœud suivant (optimisation préfixe commun)
# - Leaf : chemin + valeur

def ethereum_state_proof(state_root, address, storage_key, provider):
    """
    Preuve de l'état d'un contrat :
    1. Prove_Account(account_key) → preuve dans le state trie
    2. Prove_Storage(storage_key) → preuve dans le storage trie du contrat
    
    La preuve combine les deux.
    """
    account_proof = provider.eth_getProof(address, [storage_key], "latest")
    return account_proof  # {accountProof, storageProof, balance, codeHash}
```

### 1.3 Verkle Trees (Ethereum en route)

**Verkle Trees** = Merkle Trees avec **Vector Commitments** (elliptic curve commitments au lieu de hash).

```python
# Avantage : la preuve Verkle est plus petite et plus rapide
# O(log_k n) → O(log_{256} n) car chaque nœud a 256 enfants
# La preuve d'un élément parmi 10^9 ne nécessite que ~4 engagements

# Utilise le perfectionnement de Pedersen sur Banderwagon
def verkle_commit(values, basis_G, basis_Q):
    """Verkle commitment sur k valeurs"""
    # C = ∑ value_i · G_i + blinding · Q
    # G_i sont k points indépendants sur la courbe
    C = sum(v * g for v, g in zip(values, basis_G))
    C += blinding * basis_Q
    return C
```

---

## 2. Signatures dans Bitcoin

### 2.1 ECDSA dans Bitcoin

Bitcoin utilise **ECDSA sur secp256k1** :

```
Courbe : y² = x³ + 7 mod p
p = 2²⁵⁶ - 2³² - 2⁹ - 2⁸ - 2⁷ - 2⁶ - 2⁴ - 1 (Fermat prime)
Ordre n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (Gx, Gy)
```

**Format de signature** : DER-encodée (avant SegWit)

```bash
# Décoder une transaction Bitcoin
bitcoin-cli decoderawtransaction <tx_hex>

# Les signatures ECDSA dans Bitcoin contiennent :
# - r (32 octets) : coordonnée x de k·G
# - s (32 octets) : k⁻¹·(hash_tx + r·privkey) mod n
# - SIGHASH flag (1 octet) : type de signature
```

**Low-S value** : Bitcoin exige `s < n/2` pour éviter le malleability (BIP 62, BIP 146).

### 2.2 SIGHASH Types

```python
SIGHASH_ALL     = 0x01  # Signe toutes les entrées et sorties
SIGHASH_NONE    = 0x02  # Signe les entrées seulement
SIGHASH_SINGLE  = 0x03  # Signe les entrées et une sortie
SIGHASH_ANYONECANPAY = 0x80  # Ne signe que cette entrée
# Combinaisons : SIGHASH_SINGLE|ANYONECANPAY, etc.
```

### 2.3 ScriptPubKey (P2PKH, P2SH, P2WPKH)

```bash
# P2PKH (Pay to Public Key Hash) — Legacy
OP_DUP OP_HASH160 <20-byte-hash> OP_EQUALVERIFY OP_CHECKSIG

# P2SH (Pay to Script Hash)
OP_HASH160 <20-byte-script-hash> OP_EQUAL

# P2WPKH (Pay to Witness Public Key Hash) — SegWit
# Pas de script, l'adresse est bech32 encodée
# bc1q<20-byte-key-hash>

# P2TR (Pay to Taproot) — Taproot
# <32-byte-x-only-pubkey> OP_CHECKSIG
```

---

## 3. Signatures dans Ethereum

### 3.1 ECDSA sur secp256k1

Ethereum utilise ECDSA de manière légèrement différente de Bitcoin :

```python
from eth_keys import keys
from eth_account.messages import encode_defunct

def ethereum_sign(message, private_key_hex):
    """Signature Ethereum (ECDSA sur secp256k1)"""
    pk = keys.PrivateKey(bytes.fromhex(private_key_hex))
    
    # Encodage du message selon EIP-191
    prefixed = encode_defunct(text=message)
    
    # Signature
    signature = pk.sign_msg(prefixed)
    
    return {
        'r': hex(signature.r),
        's': hex(signature.s),
        'v': signature.v,  # Chaîne de récupération (27 ou 28, ou 35+chain_id)
    }

# Récupération de l'adresse depuis la signature
def recover_address(message, signature):
    pk = keys.PublicKey.recover_from_msg(
        encode_defunct(text=message),
        signature
    )
    return pk.to_checksum_address()

# EIP-155 : chain ID dans v (protège contre le rejeu cross-chain)
def eip155_signature(tx, chain_id=1):
    """v = 2*chain_id + 35 + recovery_id"""
    v = 2 * chain_id + 35 + recovery_id
    return (r, s, v)
```

### 3.2 EIP-712 — Typed Data Signing

Standard pour les signatures structurées (Ethereum EIP-712) :

```python
from eth_account.messages import encode_typed_data

def sign_eip712(private_key, domain, types, value):
    """
    Signature structurée EIP-712.
    Permet aux utilisateurs de voir ce qu'ils signent dans MetaMask.
    """
    typed_data = {
        "domain": domain,     # {name, version, chainId, verifyingContract}
        "types": types,       # {EIP712Domain, Person, ...}
        "message": value,     # les vraies données
    }
    
    encoded = encode_typed_data(typed_data)
    signed = private_key.signHash(encoded)
    return signed
```

### 3.3 EIP-1559 — Fee Market

Le nouveau modèle de frais change la structure de signature :

```python
# EIP-1559 transaction (type 2)
tx_1559 = {
    'chainId': chain_id,
    'nonce': nonce,
    'maxPriorityFeePerGas': priority_fee,  # Tip au mineur
    'maxFeePerGas': max_fee,              # Plafond total
    'gas': gas_limit,
    'to': address,
    'value': amount,
    'data': data,
    'accessList': access_list,            # Optional
    'signature': (v, r, s)
}
```

---

## 4. BLS Aggregation (Ethereum 2.0)

### 4.1 BLS12-381 dans Ethereum

**Ethereum 2.0** utilise BLS12-381 pour la vérification de validateur :

```python
# BLS12-381 sur Ethereum (EIP-2333, EIP-2334)
from eth2spec.utils import bls

# KeyGen : derive_child_sk(master_sk, path)
# Chaque validateur a :
#   - withdrawal_key (pour retirer les fonds)
#   - signing_key (pour signer les attestations)

def eth2_sign_attestation(validator_key, slot, block_root, source_epoch, target_epoch):
    """Signe une attestation pour un validateur Ethereum 2.0"""
    # Domaine : type de message (attestation)
    domain = compute_domain(DOMAIN_BEACON_ATTESTER, fork_version, genesis_validators_root)
    
    # Objet de signature
    signing_root = compute_signing_root(attestation_data, domain)
    
    return bls.Sign(validator_key, signing_root)
```

**Fast Aggregate Verification** :
```python
def verify_aggregate_attestation(pubkeys, signature, message):
    """
    Vérifie une signature BLS agrégée pour N validateurs.
    Une seule équation de pairing au lieu de N.
    """
    # e(G₁, σ) = ∏ e(pk_i, H(m))
    # Une vérification O(1) en pairings !
    return bls.FastAggregateVerify(pubkeys, message, signature)
```

### 4.2 Petites optimisations BLS

```python
# Randomisable signature : rendre les signatures non-liables
# (Rogue key protection)
def randomize_bls(signature, random_r):
    """BLS signature randomization (pour la vie privée)"""
    return signature + random_r * H(public_key)

# Proof of Possession (PoP)
# Chaque validateur doit prouver qu'il possède la clé privée
pop = bls.Sign(private_key, public_key.to_bytes())
assert bls.Verify(public_key, public_key.to_bytes(), pop)
```

### 4.3 Échange de clés Distributed Key Generation (DKG)

```python
# Ethereum 2.0 utilise DKG pour les comités de sync
# N validateurs génèrent collectivement une clé publique agrégée
# sans jamais révéler leur clé privée individuelle
```

---

## 5. Schnorr et Taproot (Bitcoin)

### 5.1 BIP 340 — Schnorr Signatures

Bitcoin adopte Schnorr via Taproot (BIP 340, 341) :

```python
import hashlib

def schnorr_sign(message, private_key, public_key):
    """
    Schnorr sur secp256k1 : BIP 340
    Spécificités : clé publique en x-only (32 octets)
    """
    # Nonce déterministe (BIP 340)
    k = nonce_deterministic(private_key, message)
    
    # R = k·G (x-coordinate)
    R = point_mul(G, k)
    r = R.x  # seulement la coordonnée x
    
    # e = H(r || pk || m) mod n
    e = int.from_bytes(hashlib.sha256(
        r.to_bytes(32, 'big') +
        public_key.x.to_bytes(32, 'big') +
        message
    ).digest(), 'big') % n
    
    # s = k + e·privkey mod n
    s = (k + e * private_key) % n
    
    return (r, s)  # 64 octets

def schnorr_verify(public_key, message, signature):
    """
    Vérification Schnorr (BIP 340)
    s·G = R + e·P  ?  où e = H(R || P || m)
    """
    r, s = signature
    e = int.from_bytes(hashlib.sha256(
        r.to_bytes(32, 'big') +
        public_key.x.to_bytes(32, 'big') +
        message
    ).digest(), 'big') % n
    
    sG = point_mul(G, s)
    eP = point_mul(public_key, e)
    R = point_add(sG, neg(eP))  # sG - eP = R
    
    return R.x == r
```

### 5.2 Taproot (BIP 341)

Combinaison de clé publique + script caché :

```python
# Taproot : output = P (key path) OU Q (script path)
# P = Q + H(Q || script) * G  (Tweak)
# 
# - Key path : signature directe avec la clé tweaked
# - Script path : révélation du script via Merkle tree (MAST)

def taproot_output(internal_key, script_tree):
    """
    Crée une adresse Taproot.
    P = internal_key + tweak
    tweak = H(internal_key || merkle_root || 0)
    """
    # 1. Construire le MAST (Merkle Alternative Script Tree)
    merkle_root = compute_merkle_root(script_tree)
    
    # 2. Calculer l'output key
    tweak = int.from_bytes(tagged_hash(
        "TapTweak",
        internal_key.x.to_bytes(32, 'big') + merkle_root
    ), 'big') % n
    
    output_key = point_add(internal_key, point_mul(G, tweak))
    return output_key
```

---

## 6. Account Abstraction (EIP-4337)

### 6.1 Principe

Permet aux contrats d'agir comme des comptes externes :

```python
# EIP-4337 : UserOperation
class UserOperation:
    sender: Address          # Adresse du smart contract wallet
    nonce: int
    initCode: bytes          # Code d'initialisation
    callData: bytes          # Données d'appel
    callGasLimit: int
    verificationGasLimit: int
    preVerificationGas: int
    maxFeePerGas: int
    maxPriorityFeePerGas: int
    paymasterAndData: bytes  # Paymaster (sponsorisation)
    signature: bytes         # Signature agrégée
    
    def hash(self):
        return keccak256(abi.encode(
            self.sender, self.nonce,
            keccak256(self.initCode),
            keccak256(self.callData),
            self.callGasLimit,
            self.verificationGasLimit,
            self.preVerificationGas,
            self.maxFeePerGas,
            self.maxPriorityFeePerGas,
            keccak256(self.paymasterAndData)
        ))
```

### 6.2 Signature Aggregation

```python
# Les bundlers agrègent N UserOperations en un seul bundle
# Chaque opération a sa propre signature
# Après EIP-7562 : agrégation de signatures SIMILAIRES

# Types d'agrégation supportés :
# 1. ECDSA normal (chaque signature séparée)
# 2. BLS aggregation (même clé de validateur, signature agrégée)
# 3. Schnorr batch (plusieurs signatures Schnorr)
```

---

## 7. Threshold Cryptography en Blockchain

### 7.1 Distributed Key Generation (DKG)

**Exemple : protocole de threshold signing pour wallets multi-sig** :

```python
def dkg_protocol(participants, threshold, curve):
    """
    DKG distribué : n participants, t threshold.
    Personne ne connaît la clé privée complète.
    """
    # 1. Chaque participant génère un polynôme secret de degré t-1
    # 2. Distribue les évaluations aux autres participants
    # 3. Chaque participant somme les évaluations reçues
    #    → sa part de la clé (sk_i)
    # 4. Clé publique : somme des engagements
    
    return public_key, {i: secret_share_i for i in participants}

def threshold_sign(sk_share, message, participants_indices, n, t):
    """
    Signature threshold : t des n participants signent
    Chaque participant produit une signature partielle via Lagrange.
    """
    # Signature partielle : σ_i = H(m)^{sk_i}
    partial_sig = bls_sign(sk_share, message)
    
    # Combinaison via Lagrange :
    # σ = ∏ σ_i^{λ_i}  où λ_i sont les coefficients de Lagrange
    def lagrange_coeff(i, indices):
        num = 1
        den = 1
        for j in indices:
            if j != i:
                num *= j
                den *= j - i
        return num * modular_inverse(den, n)
    
    combined_sig = 1
    for i, sig_part in zip(participants_indices, partial_sigs):
        lambda_i = lagrange_coeff(i, participants_indices)
        combined_sig *= sig_part ** lambda_i
    
    return combined_sig
```

### 7.2 Applications Wallet

```python
# Portefeuilles threshold : diviser la clé privée en 5 parts
# où 3 parts suffisent pour signer (t=3, n=5)

# Protocole : GG18, GG20, CMP (Canetti, Lindell, etc.)
# Utilisé par : ZenGo, Fireblocks, MPCLib

# Les échanges de messages entre participants sont faits via un
# protocole MPC (Multi-Party Computation) avec canaux sécurisés
```

---

## 8. zk-Rollups Cryptographie

### 8.1 Circuits ZK pour Blockchains

```python
# Les zk-rollups (zkSync, StarkNet, Polygon zkEVM, Scroll)
# utilisent des circuits ZK pour compresser les transactions

def zk_rollup_proof(batch_txs, old_state_root, new_state_root, batch_commitment):
    """
    Le circuit ZK d'un rollup vérifie :
    1. Chaque transaction a une signature valide (ECDSA vérification dans le circuit)
    2. Les transitions d'état sont correctes (add, sub, transfer)
    3. new_state_root = f(old_state_root, batch_txs)
    4. Les signatures sont agrégées (si BLS)
    """
    # Le circuit doit vérifier des ECDSA → coûteux (plusieurs millions de contraintes)
    # Optimisation : vérifier 1 ECDSA par batch via signature aggregation
    
    # Coût en contraintes (circom) :
    # - 1 ECDSA verify : ~30M contraintes (en native)
    # - 1 ECDSA verify : ~2M contraintes (avec secp256k1 precomputes)
    # - 1 BLS verify : ~100K contraintes
    pass
```

### 8.2 Proof Recursion

```python
# Preuve de preuve : vérifier N proofs en une seule
# zkSync = PLONK recursive proofs
# StarkNet = STARK → SNARK compression via recursive proofs

# Chaque couche réduit la taille de la preuve :
# Layer 1 : instruction processor (plusieurs preuves)
# Layer 2 : aggregation circuit (une preuve par 10 processeurs)
# Layer 3 : final SNARK (une preuve unique sur Ethereum)
```

---

## 9. MEV et Protocoles

### 9.1 MEV (Maximal Extractable Value)

```python
# Cryptographie utilisée dans MEV :
# - Flashbots : bundles chiffrés envoyés aux mineurs
# - SGX (Intel Software Guard eXtensions) : exécution confidentielle

# Protocole : MEV-Boost
# Les proposants reçoivent des blocs chiffrés
# Déchiffrement seulement après sélection
# Empêche la censure et le frontrunning
```

### 9.2 Chiffrement des Transactions

```python
# EIP-XXXX : Chiffrement des transactions en mempool
# Utilisation de threshold encryption :
# 1. Le dépôt chiffre la transaction avec une clé publique
# 2. La clé de déchiffrement est distribuée parmi n déchiffreurs
# 3. t parmi n doivent déchiffrer pour que la transaction soit visible
# → Évite le frontrunning, sandwich attacks
```

### 9.3 Light Client Verification

```python
# Les clients légers (light clients) vérifient la blockchain
# sans stocker l'état complet
# Vérifient uniquement les headers + preuves de Merkle

# Verkle trees (en route) : preuve plus petite
# Sync committees (Ethereum 2.0) : BLS aggregation des signatures
# des validateurs pour vérifier un header
```

---

## Références

- **Bitcoin BIP 340 (Schnorr)** : https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki
- **Bitcoin BIP 341 (Taproot)** : https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki
- **Ethereum EIP-1559** : https://eips.ethereum.org/EIPS/eip-1559
- **Ethereum EIP-4337 (Account Abstraction)** : https://eips.ethereum.org/EIPS/eip-4337
- **Ethereum 2.0 BLS** : https://eips.ethereum.org/EIPS/eip-2333
- **Merkle Patricia Trie** : https://ethereum.org/en/developers/docs/data-structures-and-encoding/patricia-merkle-trie/
- **Verkle Trees (KZG)** : https://verkle.info
- **BLS Aggregation (Ethereum 2.0)** : https://eth2book.info/altair/part2/building_blocks/signatures/
- **libsecp256k1** : https://github.com/bitcoin-core/secp256k1
- **Rust BLS** : https://docs.rs/bls-signatures/latest/bls_signatures/
- **Flashbots MEV** : https://docs.flashbots.net
- **MPCLib (Threshold)** : https://github.com/taurushq/mpclib