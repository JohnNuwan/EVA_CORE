# Wallet & Airdrop Automation — Guide pratique

## Création d'un wallet EVM dédié pour l'agent

### Méthode 1 : Python (eth-account)
```python
# ~/hermes/scripts/airdrop/create_wallet.py
import secrets
from eth_account import Account

# Générer un wallet frais
private_key = "0x" + secrets.token_hex(32)
account = Account.from_key(private_key)

print(f"Adresse  : {account.address}")
print(f"Privée   : {private_key}")  # À stocker immédiatement, ne JAMAIS log
print(f"Seed     : à générer via BIP39 si besoin")
```

### Méthode 2 : cast (foundry)
```bash
cast wallet new
# Output:
#   Address:     0x...
#   Private key: 0x...
#   Mnemonic:    ...
```

### Stockage sécurisé
```bash
mkdir -p ~/.hermes/secure/wallet/
chmod 700 ~/.hermes/secure/
# Stocker la seed dans un fichier chiffré
# (gpg avec mot de passe utilisateur)
```

## Wallet EVM recommandé

- **Réseaux L2** : Arbitrum, Optimism, Base, Polygon zkEVM
- **Réseaux test** : Sepolia, Arbitrum Sepolia, Base Sepolia
- **Tokens** : ETH (gas L2) uniquement au début

## Airdrop hunting — workflow

### 1. Veille
- **DefiLlama** : https://defillama.com/airdrops
- **Etherscan** : nouveaux contrats déployés
- **Twitter/X** : comptes @airdrops, @DefiLlama, @claimables
- **Dune** : dashboards airdrop tracking
- **Blogs** : protocol blogs (Arbitrum, Optimism, zkSync, LayerZero, etc.)

### 2. Interactions automatisables
- **Bridging** : deposit/withdraw sur L2 (via Across, Stargate, Hop)
- **Swaps** : échanges sur DEX (Uniswap, Curve, Balancer)
- **Lending** : supply/borrow sur Aave, Compound, Morpho
- **Liquidity** : add/remove LP sur paires stables
- **NFT** : mint, bridge, trade (si pertinent)
- **Governance** : vote sur les propositions (si requis)

### 3. Scripts de surveillance
```python
# Surveillance cron : check new protocols on DefiLlama
import requests, json

url = "https://api.llama.fi/protocols"
data = requests.get(url).json()

# Filtrer par date de création récente
new_protocols = [p for p in data if p.get('listedAt', 0) > timestamp_24h_ago]
for p in new_protocols:
    print(f"Nouveau: {p['name']} - {p['url']} - Chaînes: {p['chains']}")
```

### 4. Script d'interaction de base (web3.py)
```python
from web3 import Web3

# Connexion à Arbitrum
w3 = Web3(Web3.HTTPProvider('https://arb1.arbitrum.io/rpc'))
account = w3.eth.account.from_key(private_key)

# Swapper sur un DEX
# ... (adapté au protocole cible)
```

## Protocoles airdrop classiques à surveiller
- **L2s** : Arbitrum (déjà fait), zkSync (déjà fait), Base, Scroll, Linea, Taiko, zkEVM
- **Bridges** : LayerZero, Stargate, Across, Hop, Synapse
- **DEX** : Uniswap (déjà fait), Sushi, Pancake, Trader Joe
- **Lending** : Aave, Compound, Morpho, Radiant
- **Restaking** : EigenLayer, Kelp, EtherFi, Swell, Renzo
- **L2s à venir** : Fuel, MegaETH, Monad, Berachain

## Pièges spécifiques airdrop

- **Snapshot** : ne pas interagir après le snapshot (gas perdu)
- **Wallet farming** : certains protocoles détectent les wallets "sybil" (multi-comptes). Un seul wallet dédié suffit.
- **Gas timing** : interagir quand le gas est bas (wekeend, nuit)
- **Contrats honeypot** : toujours vérifier le code source Etherscan avant d'approuver
- **Taxes** : en France, les airdrops sont imposables (flat tax 30% ou PFU). À déclarer en revenus exceptionnels.

## Budget recommandé
- **Gas initial** : 20-50€ sur L2 (Arbitrum/Base)
- **Interactions** : ~0.5-2$ par interaction selon le réseau
- **Surveillance** : gratuit (cron jobs)