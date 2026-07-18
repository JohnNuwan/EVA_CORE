---
name: industrial-blockchain-applications
description: "Implémenter la blockchain dans les environnements industriels pour la traçabilité des ressources, la sécurisation des données IoT et l'automatisation par smart contracts."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [blockchain, smart-contracts, ethereum, hyperledger, industry40, traceability, iot, supply-chain]
    related_skills: [industrial-cybersecurity-guidelines, iso-standards-for-industry, interoperability-of-industrial-systems]
---

# Blockchain Industrielle pour l'Industrie 4.0

## Vue d'ensemble

Cette compétence explore les **applications pratiques de la blockchain** dans l'environnement industriel : traçabilité des ressources, sécurisation des données IoT, automatisation par smart contracts, certification immuable et gestion décentralisée de la supply chain. Elle couvre les plateformes adaptées (Ethereum, Hyperledger Fabric), les architectures décentralisées et les cas d'usage concrets.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'implémenter une solution de traçabilité inviolable pour une chaîne de production.
- De déployer des smart contracts pour automatiser des processus inter-entreprises.
- De sécuriser les données issues de capteurs IoT sur une blockchain.
- De certifier des documents ISO ou des contrôles qualité de manière immuable.
- D'auditer une supply chain multi-acteurs avec une DLT (Distributed Ledger Technology).

---

## 1. Concepts Fondamentaux

### 1.1 Blockchain vs DLT pour l'Industrie

| Critère | Blockchain Publique (Ethereum) | Blockchain Privée/Consortium (Hyperledger) |
|:---|:---|:---|
| **Accès** | Ouvert (anonyme) | Restreint (membres connus) |
| **Consensus** | Proof-of-Stake / PoW (lent) | Raft / Kafka / PBFT (rapide) |
| **Débit** | ~15–30 TPS | > 1 000 TPS |
| **Confidentialité** | Faible (données visibles) | Haute (canaux privés) |
| **Coût** | Élevé (gas fees) | Faible (contrôlé) |
| **Usage industriel** | Certification, traçabilité publique | Supply chain privée, consortium |

### 1.2 Cas d'Usage Industriels Prioritaires

| Cas | Problème | Solution Blockchain | Plateforme |
|:---|:---|:---|:---|
| **Traçabilité matière** | Certification d'origine falsifiable | Hash des certificats sur la chaîne | Ethereum (public) |
| **Smart contract qualité** | Contrôle manuel, papier | Automatisation des validations qualité | Hyperledger Fabric |
| **IoT sécurisé** | Données capteurs falsifiables | Signature des mesures sur la blockchain | IOTA / Hyperledger |
| **Supply chain multi-acteurs** | Litiges de responsabilité | Enregistrement immuable des transferts | Hyperledger Fabric |
| **Certification ISO** | Perte de documents | Stockage décentralisé des certificats | Ethereum (IPFS) |

---

## 2. Smart Contract pour l'Industrie (Solidity)

### 2.1 Exemple : Contrat de Traçabilité de Lot

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BatchTraceability {
    struct Batch {
        string batchId;
        string productName;
        uint256 productionDate;
        address manufacturer;
        address currentHolder;
        bool isActive;
    }

    struct Transfer {
        address from;
        address to;
        uint256 timestamp;
        string location;
        string documents;
    }

    mapping(string => Batch) public batches;
    mapping(string => Transfer[]) public transfers;

    event BatchCreated(string indexed batchId, address manufacturer);
    event BatchTransferred(string indexed batchId, address from, address to);

    function createBatch(
        string memory _batchId,
        string memory _productName,
        uint256 _productionDate
    ) public {
        require(!batches[_batchId].isActive, "Batch already exists");
        batches[_batchId] = Batch({
            batchId: _batchId,
            productName: _productName,
            productionDate: _productionDate,
            manufacturer: msg.sender,
            currentHolder: msg.sender,
            isActive: true
        });
        emit BatchCreated(_batchId, msg.sender);
    }

    function transferBatch(
        string memory _batchId,
        address _to,
        string memory _location,
        string memory _documents
    ) public {
        require(batches[_batchId].isActive, "Batch not active");
        require(batches[_batchId].currentHolder == msg.sender, "Not the holder");

        transfers[_batchId].push(Transfer({
            from: msg.sender,
            to: _to,
            timestamp: block.timestamp,
            location: _location,
            documents: _documents
        }));

        batches[_batchId].currentHolder = _to;
        emit BatchTransferred(_batchId, msg.sender, _to);
    }

    function getTransferHistory(
        string memory _batchId
    ) public view returns (Transfer[] memory) {
        return transfers[_batchId];
    }
}
```

### 2.2 Déploiement avec Hardhat

```bash
# Installation
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# Compilation
npx hardhat compile

# Déploiement local
npx hardhat run scripts/deploy.ts --network localhost
```

---

## 3. Intégration IoT-Blockchain

### 3.1 Architecture de Sécurisation des Données Capteurs

```
Capteur → Gateway → [Horodatage + Signature] → Transaction Blockchain
                                                      ↓
                                              Stockage IPFS/Arweave
                                                      ↓
                                          Vérification par smart contract
```

**Exemple de publication de données IoT signées :**

```python
from web3 import Web3
from eth_account import Account
import json

# Connexion au nœud
w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_KEY"))
account = Account.from_key("PRIVATE_KEY")

# Données capteur
sensor_data = {
    "sensor_id": "TEMP_001",
    "value": 23.5,
    "unit": "celsius",
    "timestamp": 1719234567,
    "signature": account.sign_message(
        text=str(1719234567) + "TEMP_001" + "23.5"
    ).signature.hex()
}

# Publication sur la blockchain
tx = {
    'to': '0xSmartContractAddress',
    'value': 0,
    'gas': 100000,
    'gasPrice': w3.eth.gas_price,
    'nonce': w3.eth.get_transaction_count(account.address),
    'data': w3.eth.contract(
        address='0xSmartContractAddress',
        abi=CONTRACT_ABI
    ).functions.publishSensorData(
        sensor_data["sensor_id"],
        sensor_data["value"],
        sensor_data["timestamp"],
        sensor_data["signature"]
    ).build_transaction()['data']
}

signed_tx = account.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
```

---

## 4. Pièges Courants

1. **Blockchain comme solution à tout :**
   - *Erreur* : Vouloir mettre toutes les données industrielles sur la blockchain.
   - *Correction* : N'utilisez la blockchain que pour ce qui nécessite immuabilité, traçabilité ou confiance décentralisée. Le reste (données temps réel, logs massifs) reste dans des bases classiques.

2. **Gas fees non maîtrisés (Ethereum) :**
   - *Erreur* : Publier chaque mesure capteur (coût prohibitif).
   - *Correction* : Faites du batch (publication périodique agrégée) ou utilisez une couche L2 (Polygon, Arbitrum) ou un consortium (Hyperledger).

3. **Clés privées compromises :**
   - *Erreur* : Stocker la clé privée en clair dans un fichier de configuration.
   - *Correction* : Utilisez un HSM (Hardware Security Module), un coffre (Vault), ou un service de gestion de clés cloud.

---

## Liste de vérification

- [ ] Le cas d'usage justifie-t-il réellement le recours à la blockchain ? (immuabilité, décentralisation, confiance)
- [ ] La plateforme est choisie (Ethereum public vs Hyperledger consortium vs IOTA).
- [ ] Le smart contract est compilé, déployé sur un testnet et audité.
- [ ] Les données IoT sont signées avant publication sur la blockchain.
- [ ] Les clés privées sont stockées de manière sécurisée (HSM, Vault).
- [ ] Les coûts de transaction (gas) sont estimés et budgétisés.
