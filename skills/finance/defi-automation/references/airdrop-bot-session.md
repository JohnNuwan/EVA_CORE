# Session : Setup Airdrop Bot E.V.A (2026-07-21)

## Contexte
- Setup sur The Hive (2× RTX 3090, 125GB RAM, EPYC 32 cœurs)
- ~/revenus-alternatifs/airdrop/ comme répertoire de base
- GPU 1 libre, GPU 0 occupé (~8GB VRAM, services IA)

## Wallet EVM créé
- Adresse : 0xC98be244CE41f7dc1Eb79B19fc52e6a359eaEa2a4
- Fichier : ~/revenus-alternatifs/airdrop/wallet-eva.json (chmod 600)
- Private key dans le fichier (NE PAS COMMIT)
- Réseau par défaut : Arbitrum One (RPC: https://arb1.arbitrum.io/rpc)

## Config
- ~/revenus-alternatifs/airdrop/config.json
- Chaînes : Arbitrum, Ethereum, Base, Polygon

## Cron job actif
- job_id : 88b8b7d2736d
- Nom : Airdrop Monitor E.V.A
- Fréquence : toutes les 6h
- Mode : no_agent (script shell)
- Script : ~/.hermes/scripts/airdrop-monitor.sh
- Workdir : ~/revenus-alternatifs/airdrop
- Prochaine exécution : 2026-07-21T21:28:52+02:00

## Caches
- ~/revenus-alternatifs/airdrop/cache_airdrops.json
- ~/revenus-alternatifs/airdrop/cache_protocoles.json

## Commandes utiles
```bash
# Vérification manuelle
cd ~/revenus-alternatifs/airdrop
uv run --with requests,web3 python3 airdrop_bot.py --check

# Vérifier le wallet
uv run --with requests,web3 python3 airdrop_bot.py --claim

# Exécuter le cron immédiatement
hermes cron run 88b8b7d2736d
```

## Prochaines étapes
1. Envoyer ~10-20€ d'ETH sur Arbitrum pour le gas
2. Lancer --claim pour vérifier les balances
3. Interagir avec les protocoles détectés (swaps, LP, bridges)
4. Vérifier les claims périodiquement