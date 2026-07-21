---
name: defi-automation
description: "Automation DeFi : monitoring d'airdrops, création de wallets, surveillance on-chain, et automatisation d'interactions sur EVM."
category: finance
---

# Automation DeFi — Airdrop Hunting & Monitoring On-Chain

## Quand utiliser ce skill

- L'utilisateur veut générer des revenus passifs en crypto (airdrops, DeFi)
- Il faut créer un wallet EVM dédié, surveiller les nouveaux protocoles, automatiser les interactions on-chain
- L'utilisateur accepte le risque : le gas investi (20-50€) est le seul coût, le gain potentiel est 200-3000€+ sur 3-6 mois

## Principe

L'agent crée et gère un wallet dédié (isolé des wallets perso de l'utilisateur). Le bot surveille les nouveaux protocoles listés sur DefiLlama, car les nouveaux listings sont souvent suivis d'airdrops. L'utilisateur n'a qu'à envoyer le gas. L'agent gère tout le reste.

## Stack technique

- **Wallet** : EVM (Ethereum, Arbitrum, Optimism, Base, Polygon, etc.)
- **Monitoring** : DefiLlama API (`api.llama.fi/protocols`)
- **On-chain** : web3.py (pip install web3)
- **Scripting** : Python 3.11+, uv pour les dépendances
- **Scheduling** : Cron job Hermes (toutes les 6h en mode no_agent)

## Workflow de setup

### 1. Créer un wallet EVM dédié

```bash
uv run --with eth-account python3 -c "
from eth_account import Account
import secrets
account = Account.create(secrets.token_hex(32))
print(f'Adresse : {account.address}')
print(f'Private Key : {account.key.hex()}')
"
```

Sauvegarder en `chmod 600` dans un fichier JSON dédié.

### 2. Installer les dépendances

```bash
uv run --with requests,web3 python3 -c "import web3; print('OK')"
```

### 3. Créer le bot de monitoring

Le bot doit :
- Interroger DefiLlama pour les nouveaux protocoles (trier par `createdAt`)
- Marquer les protocoles avec catégorie DEX/Lending/Bridge/Staking comme "potentiel airdrop"
- Vérifier les balances gas sur les chaînes principales
- Filtrer les protocoles déjà vus (cache JSON)
- S'exécuter en mode cron (toutes les 6h, silencieux si rien de nouveau)

### 4. Configurer le cron job

```bash
# Créer le script shell dans ~/.hermes/scripts/
# Mode no_agent=true avec script shell qui pipe l'output
hermes cron create --name "Airdrop Monitor" --schedule "every 6h" --script "airdrop-monitor.sh" --no-agent
```

## Sources de données

| Source | Endpoint | Usage |
|--------|----------|-------|
| DefiLlama | `https://api.llama.fi/protocols` | Nouveaux protocoles (triés par createdAt) |
| Etherscan | `https://api.etherscan.io/api` | Activité wallet (sans clé = limité) |
| Arbiscan | `https://api.arbiscan.io/api` | Activité wallet Arbitrum |
| Basescan | `https://api.basescan.org/api` | Activité wallet Base |

## Métriques de suivi

- **Wallet** : équilibrer gas sur Arbitrum/Base (minimum 0.005-0.01 ETH)
- **Monitoring** : vérifier les nouveaux protocoles toutes les 6h
- **Résultat** : 3-10 airdrops reçus sur 20-30 protocoles ciblés
- **ROI** : 10x-60x sur le gas investi, gain probable 200-3000€ sur 3-6 mois

## Structure projet recommandée

```
~/revenus-alternatifs/airdrop/
├── wallet-eva.json          # Wallet EVM (chmod 600)
├── config.json              # Configuration réseau
├── airdrop_bot.py           # Bot monitoring principal
├── cache_airdrops.json      # Cache des airdrops vus
├── cache_protocoles.json    # Cache des protocoles vus
└── setup_airdrop.py         # Script de vérification du setup
```

## Pitfalls

- **Gas insuffisant** : le wallet doit avoir au moins 0.005 ETH sur la chaîne cible pour interagir. Sans gas, impossible de claim ou d'interagir.
- **Rate limiting** : Etherscan/Arbiscan limitent les appels sans API key. Prioriser DefiLlama qui est gratuit.
- **Cache** : le premier run va détecter TOUS les protocoles (30+). Le cache filtre les vus pour les runs suivants.
- **Sécurité** : NE JAMAIS commit le wallet. Fichier en `chmod 600`. Ne pas mettre de fonds importants.
- **Airdrop ≠ garanti** : la plupart des protocoles n'airdrop pas. C'est un jeu de volume : plus on interagit, plus on a de chances.

## Support fichiers

- `references/airdrop-bot-session.md` — détails session-specific de l'implémentation (structure, cron job, wallet)