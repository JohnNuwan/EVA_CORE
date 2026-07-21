---
name: osint-cryptocurrency-blockchain
description: OSINT sur les cryptomonnaies et la blockchain — traçage de transactions, analyse de wallets, identification d'adresses, mixers, DeFi, NFT forensics et investigation de bloc.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, blockchain, crypto, bitcoin, ethereum, wallet, transactions, nft, defi, forensics]
---

# OSINT Cryptocurrency & Blockchain Forensics

## 🎯 Description

Investigation de transactions blockchain et cryptomonnaies : traçage d'adresses Bitcoin/Ethereum, analyse de flux de fonds, identification de wallets, détection de mixers/tumbleurs, OSINT sur protocoles DeFi, analyse NFT, et corrélation avec des identités réelles via données de marché et registres KYC.

---

## 📋 Outils Essentiels

### Explorateurs de Blocs — Bitcoin
| Outil | URL | Usage |
|-------|-----|-------|
| **Blockchain.com** | https://www.blockchain.com/explorer | Explorateur Bitcoin complet |
| **Blockchair** | https://blockchair.com | Multi-blockchain (BTC, ETH, LTC, BCH, etc.) |
| **OXT.me** | https://oxt.me | Analyse avancée BTC (clustering, tags) |
| **BitcoinWhosWho** | https://bitcoinwhoswho.com | Identification d'adresses |
| **WalletExplorer** | https://www.walletexplorer.com | Clustering de wallets |
| **BTC.com** | https://btc.com | Explorateur Bitcoin |
| **TradeBlock** | https://tradeblock.com/blockchain/ | Analyse de transactions |
| **Learnmeabitcoin** | https://learnmeabitcoin.com/explorer | Explorateur pédagogique |

### Explorateurs de Blocs — Ethereum
| Outil | URL | Usage |
|-------|-----|-------|
| **Etherscan** | https://etherscan.io | Explorateur Ethereum principal |
| **Ethplorer** | https://ethplorer.io | Analyse de tokens ERC-20 |
| **Bloxy** | https://bloxy.info | Analytics Ethereum |
| **Dune Analytics** | https://dune.com | Dashboards SQL on-chain |
| **Nansen** | https://nansen.ai | Wallet labels, smart money (payant) |
| **Tokenview** | https://tokenview.com | Multi-chain explorer |
| **Covalent** | https://www.covalenthq.com | API unifiée multi-chain |
| **DeBank** | https://debank.com | Portfolio DeFi multi-chain |
| **Zapper** | https://zapper.fi | Portfolio DeFi dashboard |
| **Etherscan Pro** | https://pro.etherscan.io | API avancée + alerts |

### Analyse de Flux et Mixers
| Outil | URL | Usage |
|-------|-----|-------|
| **Chainalysis** | https://www.chainalysis.com | Forensics blockchain (entreprise) |
| **CipherTrace** | https://ciphertrace.com | Analyse AML (payant) |
| **Elliptic** | https://www.elliptic.co | Investigation crypto (payant) |
| **Whirly (wasabi)** | https://wasabiwallet.io | CoinJoin analysis |
| **Bitcoin Fog** | - | Mixer Bitcoin (démantelé 2021) |
| **ChipMixer** | - | Mixer démantelé 2023 |
| **Tornado Cash** | https://tornadocash.eth.link | Mixer Ethereum (sanctionné OFAC) |
| **Whitestorm** | https://whitestorm.io | Privacy coin |

### Identification et KYC
| Outil | URL | Usage |
|-------|-----|-------|
| **Coinbase Analytics** | - | Analytics interne Coinbase |
| **Glassnode** | https://glassnode.com | On-chain metrics |
| **Santiment** | https://santiment.net | Crypto intelligence |
| **Arkham Intelligence** | https://arkhamintelligence.com | Labeling + visualisation |
| **ChainAbuse** | https://www.chainabuse.com | Signalement de fraudes |
| **CryptoScamDB** | https://cryptoscamdb.org | Base de scams |
| **RugDoc** | https://rugdoc.io | Analyse de rug pulls |
| **TokenSniffer** | https://tokensniffer.com | Détection de tokens frauduleux |
| **Honeypot.is** | https://honeypot.is | Détection de honeypots |
| **DexScreener** | https://dexscreener.com | Suivi de paires trading |

### Crypto OSINT Général
| Outil | URL | Usage |
|-------|-----|-------|
| **Bitcoin Abuse** | https://www.bitcoinabuse.com | Base d'adresses liées à la fraude |
| **CryptoSLAM** | https://cryptoslam.io | Analyse NFT |
| **Dune Analytics** | https://dune.com | Requêtes SQL personnalisées |
| **The Graph** | https://thegraph.com | Indexation blockchain décentralisée |
| **Tenderly** | https://tenderly.co | Débogage de transactions |
| **Phalcon (BlockSec)** | https://phalcon.blocksec.com | Analyse de transactions complexes |
| **Eigenphi** | https://eigenphi.io | MEV et robotique financière |
| **DefiLlama** | https://defillama.com | TVL, protocoles, hacks |
| **Revert Finance** | https://revert.finance | Analyse de trades |

---

## 🔧 Méthodologie d'Investigation

### Phase 1 : Collecte d'Adresses

```bash
# 1. Scanner les sources pour trouver des adresses crypto
grep -roP '^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$' ./data/     # Bitcoin legacy
grep -roP '^bc1[a-zA-HJ-NP-Z0-9]{39,59}$' ./data/          # Bitcoin segwit
grep -roP '^0x[a-fA-F0-9]{40}$' ./data/                    # Ethereum

# 2. Extraire des adresses de posts / forums
# Chercher : "send BTC to", "donate", wallet addresses

# 3. Vérifier sur BitcoinAbuse
curl -s "https://www.bitcoinabuse.com/api/reports/check?address=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
```

### Phase 2 : Analyse de Transactions Bitcoin

```bash
# Via Blockchair API (gratuit limité)
curl -s "https://api.blockchair.com/bitcoin/dashboards/address/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" | jq .

# WalletExplorer - clustering de wallets
# Naviguer sur https://www.walletexplorer.com

# OXT.me - analyse avancée
# Naviguer sur https://oxt.me

# Clustering heuristique Bitcoin
# 1. Regrouper les adresses qui sont inputs d'une même transaction (multi-input)
# 2. Suivre les outputs jusqu'à épuisement (change addresses)
# 3. Marquer les adresses connues (exchange, mixer, service)
```

### Phase 3 : Analyse de Transactions Ethereum

```bash
# Etherscan API
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0x...&sort=desc&apikey=KEY" | jq .

# Récupérer les tokens ERC-20 associés
curl -s "https://api.etherscan.io/api?module=account&action=tokentx&address=0x...&apikey=KEY" | jq .

# Analyse de contrat (bytecode, ABI)
curl -s "https://api.etherscan.io/api?module=contract&action=getsourcecode&address=0x...&apikey=KEY"

# Traçage DeFi
# 1. Identifier les interactions avec des protocoles (Uniswap, Curve, Aave)
# 2. Suivre les swaps, liquidations, dépôts
# 3. Analyser les flash loans
```

### Phase 4 : Visualisation de Flux

```bash
# Arkham Intelligence (web)
# Naviguer sur https://arkhamintelligence.com

# Bitquery (API graphQL)
curl -s -X POST "https://graphql.bitquery.io/" \
  -H "X-API-KEY: KEY" \
  -d '{
    "query": "{
      bitcoin(network: bitcoin) {
        inputs(
          outputAddress: {is: \"1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\"}
          options: {direction: inbound, height: {gt: 0}}
        ) {
          blockHeight
          txHash
          value
        }
      }
    }"
  }' | jq .
```

### Phase 5 : Corrélation avec Identités

```bash
# 1. Adresse trouvée → rechercher sur les réseaux sociaux
google-chrome "site:twitter.com 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
google-chrome "site:reddit.com 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
google-chrome "0x..." "bitcoin" OR "ethereum"

# 2. Chercher dans les forums crypto
# site:bitcointalk.org ADRESSE
# site:reddit.com/r/bitcoin ADRESSE

# 3. Vérifier s'il y a eu un KYC associé
# Échanges : si l'adresse est taggée "Binance", "Coinbase", le KYC a été fait

# 4. Recherche dans les leaks de CEX
# Certains échanges ont fuité (FTX, etc.)
```

---

## 📊 Techniques Avancées

### Détection de Mixers/Tumbleurs
```bash
# Signes d'utilisation de mixer :
# - Transactions avec des montants ronds (ex: 1.0 BTC exact)
# - Multiples outputs de même valeur
# - Pas de change address évidente
# - Pauses temporelles inhabituelles

# Tornado Cash (Ethereum)
# 1. Déposer ETH (1, 10, 100 ETH)
# 2. Avecdraw vers une nouvelle adresse
# 3. Le lien entre deposit et withdraw est rompu (anonymity set)

# Wasabi Wallet / CoinJoin (Bitcoin)
# - Transactions avec 5+ participants
# - Tous les inputs de même valeur
# - Outputs aléatoires
```

### Analyse NFT
```bash
# OpenSea
# Naviguer sur https://opensea.io/ADRESSE

# Etherscan (NFT transfers)
curl -s "https://api.etherscan.io/api?module=account&action=tokennfttx&address=0x...&apikey=KEY"

# CryptoSlam - analyse de collection
# Naviguer sur https://cryptoslam.io

# Blur - marketplace NFT
# Naviguer sur https://blur.io
```

### Échanges et Plateformes
```bash
# Identifier les dépôts sur exchange
# 1. Vérifier sur WalletExplorer (clustering exchange)
# 2. Chercher les adresses de dépôt connues
# 3. Cross-référencer avec les leaks

# Transactions cross-chain (bridges)
# - Utilisation de bridges : AnySwap, Multichain, Wormhole
# - Traçage via les smart contracts de bridge
# - Suivi des wrapped tokens
```

### Analyse de Rug Pull / Scam
```bash
# 1. Vérifier le contrat du token
# 2. Analyser la distribution initiale
# 3. Vérifier la liquidity pool (DEX)
# 4. Chercher des adresses de dev
# 5. Analyser les tax tokens

# Outils :
# TokenSniffer: https://tokensniffer.com
# Honeypot.is: https://honeypot.is
# RugDoc: https://rugdoc.io
# DexScreener: https://dexscreener.com
# Bubblemaps: https://bubblemaps.io (visualisation distribution tokens)
```

---

## 🛠️ Scripts Utiles

### Script d'Analyse de Wallet Bitcoin
```bash
#!/bin/bash
# analyze_btc_wallet.sh
ADDRESS="$1"

echo "=== Analyse de $ADDRESS ==="

# 1. Solde et transactions (Blockchair)
echo "--- Solde ---"
curl -s "https://api.blockchair.com/bitcoin/dashboards/address/$ADDRESS" | \
  jq '{balance: .data[].address.balance, received: .data[].address.received, tx_count: .data[].address.transaction_count}'

# 2. Dernières transactions
echo "--- Dernières transactions ---"
curl -s "https://api.blockchair.com/bitcoin/dashboards/address/$ADDRESS" | \
  jq '.data[].transactions | .[:5] | .[].hash'

# 3. Vérifier dans les bases de fraude
echo "--- BitcoinAbuse ---"
curl -s "https://www.bitcoinabuse.com/api/reports/check?address=$ADDRESS" | jq .
```

### Script de Crawl d'Adresses Crypto sur une Page Web
```bash
#!/bin/bash
# extract_crypto_addresses.sh
URL="$1"

echo "=== Extraction d'adresses crypto depuis $URL ==="

# Télécharger
content=$(curl -sL "$URL")

# Bitcoin
echo "--- Bitcoin ---"
echo "$content" | grep -oP '^[13][a-km-zA-HJ-NP-Z1-9]{25,34}' | sort -u
echo "$content" | grep -oP 'bc1[a-zA-HJ-NP-Z0-9]{39,59}' | sort -u

# Ethereum
echo "--- Ethereum ---"
echo "$content" | grep -oP '0x[a-fA-F0-9]{40}' | sort -u

# Litecoin
echo "--- Litecoin ---"
echo "$content" | grep -oP '^L[a-km-zA-HJ-NP-Z1-9]{25,34}' | sort -u

# Monero
echo "--- Monero ---"
echo "$content" | grep -oP '^4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}' | sort -u
```

---

## 📝 Cas d'Usage Typiques

### Investigation de Ransomware
```bash
# 1. Trouver l'adresse BTC de demande de rançon
# 2. Analyser les transactions entrantes (paiements)
# 3. Identifier les clusters de wallets (via OXT/WalletExplorer)
# 4. Suivre le flux vers des exchanges
# 5. Identifier l'échange de sortie (fiat off-ramp)
```

### Traçage de Vol DeFi
```bash
# 1. Identifier le contrat attaqué
# 2. Analyser la tx d'exploitation (Tenderly, Phalcon)
# 3. Suivre les fonds volés
# 4. Vérifier les bridges utilisés
# 5. Surveiller les adresses sur Etherscan/Nansen
```

### Due Diligence Crypto
```bash
# 1. Analyser le token (sniffer, rugdoc, honeybot)
# 2. Vérifier les wallets des fondateurs
# 3. Analyser la gouvernance on-chain
# 4. Vérifier les audits de sécurité
# 5. Cross-référencer avec les registres d'entreprises
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Mixers** : Tornado Cash et Wasabi Wallet rendent le traçage difficile. Utiliser des heuristiques de clustering combinées.
- **Cross-chain** : Les bridges compliquent le traçage. Les données peuvent être fragmentées sur plusieurs chaînes.
- **Privacy coins** : Monero, Zcash (shielded) sont quasi-intraçables sans données de CEX.
- **Non-custodial** : Les wallets non-custodiaux n'ont pas de KYC. Impossible de remonter à une identité sans données on-chain.
- **APIs limitées** : Etherscan (5 req/sec), Blockchair (gratuit limité). Utiliser des clés API payantes pour le volume.
- **Faux positifs** : Les adresses taggées "exchange" peuvent être des dépôts d'utilisateurs, pas de la plateforme elle-même.
- **Légalité** : Le traçage de transactions publiques est légal. L'accès non autorisé aux plateformes d'échange ne l'est pas.
- **RGPD crypto** : Les adresses ne sont pas des données personnelles en soi, mais liées à une identité, elles le deviennent.

---

## 🔗 Références

- https://etherscan.io
- https://www.blockchain.com/explorer
- https://www.walletexplorer.com
- https://oxt.me
- https://www.bitcoinabuse.com
- https://github.com/jivoi/awesome-osint#cryptocurrency
- https://dashboard.arkhamintelligence.com
- https://dune.com
- https://defillama.com