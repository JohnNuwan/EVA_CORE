# Setup Airdrop Bot — Phase 2

## Installation

```bash
# Wallet EVM
uv run --with eth-account python3 -c "
from eth_account import Account
import secrets
account = Account.create(secrets.token_hex(32))
print(f'Adresse : {account.address}')
print(f'PK : {account.key.hex()}')
"

# Dépendances
uv run --with requests,web3 python3 -c "import web3; print('OK')"
```

## Fichiers

- `~/revenus-alternatifs/airdrop/wallet-eva.json` — wallet (chmod 600)
- `~/revenus-alternatifs/airdrop/config.json` — réseau RPC
- `~/revenus-alternatifs/airdrop/airdrop_bot.py` — bot principal
- `~/revenus-alternatifs/airdrop/cache_*.json` — cache de suivi

## Cron Hermes

```bash
hermes cron create --every 6h --script airdrop-monitor.sh --no-agent
```

Script dans `~/.hermes/scripts/airdrop-monitor.sh` : exécute le bot --check,
ne sort du texte que si des nouveaux protocoles sont détectés.

## Usage

```bash
cd ~/revenus-alternatifs/airdrop
uv run --with requests,web3 python3 airdrop_bot.py --check   # vérifier
uv run --with requests,web3 python3 airdrop_bot.py --claim   # bilan wallet
```

## API Sources

- DefiLlama : `https://api.llama.fi/protocols` (top 30 nouveaux protocoles)
- Arbitrum : RPC public `https://arb1.arbitrum.io/rpc`
- Base : RPC public `https://mainnet.base.org`

## Recommandation gas

Envoyer ~10-20€ d'ETH sur Arbitrum ou Base. Le wallet ne doit contenir QUE du
gas — jamais de fonds importants.