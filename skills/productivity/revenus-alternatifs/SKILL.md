---
name: revenus-alternatifs
description: "Générer des revenus automatisés avec l'agent : freelance IA (ComeUp/Malt/Fiverr) + crypto passif (airdrop bot, wallet EVM, monitoring DefiLlama). Couvre la création de gigs, les livrables testés, le wallet EVM, le bot airdrop, et le cron de monitoring."
category: productivity
---

# Revenus Alternatifs Automatisés

## Quand utiliser ce skill

- L'utilisateur veut générer des revenus passifs/automatisés
- Le freelance IA est la colonne vertébrale (argent sûr, immédiat)
- Les revenus crypto (airdrop) sont le complément spéculatif (gratuit, pas de capital)
- L'utilisateur rejette le mining GPU (mort depuis le merge ETH) et le trading algorithmique basique (trop volatile)

## Répartition des rôles

- **Utilisateur** : crée les comptes (ComeUp, exchanges), valide les propositions, gère la relation client/facturation
- **Agent (E.V.A)** : rédige les gigs, produit les livrables techniques, setup le wallet, gère le monitoring airdrop 24/7

## Phase 1 — Freelance IA (comeup.com en priorité)

### Les 3 services qui se vendent

| Service | Prix base | Options | Livrable |
|---------|-----------|---------|----------|
| 📄 Extraction PDF→Excel (OCR) | 20€ (30 pages) | +30€ (100p), +80€ (500p), +25€ pipeline | Excel 3 feuilles (Données/CQ/Texte brut) |
| ⚡ Automation Python | 80€ (1 tâche) | +40€ multi-étapes, +30€ API, +50€ rapport | Script + README, code source fourni |
| 🤖 Chatbot RAG documents privés | 250€ (1 source) | +80€ multi-sources, +50€ mémoire, +100€ déploiement | Interface web, hébergement local |

### Stratégie de lancement
- 3 gigs publiés dès le départ (les nouveautés sont mises en avant)
- Prix d'appel bas pour acheter les premiers avis 5 étoiles
- Répondre < 1h aux contacts (la plateforme met en avant la réactivité)
- Livrer en avance sur les premières commandes
- Marge dans les options, pas dans l'offre de base

### Livrables à préparer AVANT la première commande
- `extracteur_pdf.py` : PDF natif (pdfplumber) + OCR auto (Tesseract fra+eng) → Excel
- `fusion_data.py` : fusion CSV/Excel + dédoublonnage + rapport
- Tester chaque livrable avec des données de test avant de le déclarer "prêt"

## Phase 2 — Crypto passif (airdrop hunting)

### Wallet EVM dédié
```bash
uv run --with eth-account python3 -c "
from eth_account import Account
import secrets
account = Account.create(secrets.token_hex(32))
print(f'Adresse : {account.address}')
print(f'Private Key : {account.key.hex()}')
"
```
- `chmod 600` sur le fichier de wallet
- Ne JAMAIS commiter la private key
- Wallet dédié airdrop uniquement (gas seulement)

### Bot monitoring airdrop
- Source : `api.llama.fi/protocols` (trier par `createdAt`)
- Catégories à potentiel : DEX, Lending, Yield, Derivatives, Bridge, Cross-Chain, Staking Pool
- Endpoint `/airdrops` n'existe pas (404) — utiliser `/protocols` à la place
- Cache de 6h entre les vérifications

### Cron job monitoring passif
```bash
# ~/.hermes/scripts/airdrop-monitor.sh (no_agent=True)
#!/bin/bash
cd /home/USER/revenus-alternatifs/airdrop || exit 1
OUTPUT=$(uv run --with requests,web3 python3 airdrop_bot.py --check 2>&1)
if echo "$OUTPUT" | grep -q "NOUVEAUX PROTOCOLES"; then
    echo "=== Airdrop Monitor ==="
    echo "$OUTPUT"
fi
```
- Le script doit être dans `~/.hermes/scripts/` (chemin relatif requis)
- `schedule="every 6h"` pour ne pas spammer DefiLlama

### Prérequis on-chain
- Envoyer ~10-20€ d'ETH sur Arbitrum ou Base (gas L2)
- Vérifier avec `uv run airdrop_bot.py --claim`

## Structure projet recommandée

```
revenus-alternatifs/
├── freelance/
│   ├── gigs/            ← Descriptions des services au format .md
│   └── livrables/       ← Scripts Python testés et prêts à livrer
└── airdrop/
    ├── wallet-eva.json   ← Wallet EVM (chmod 600)
    ├── config.json       ← RPC, intervalles
    ├── airdrop_bot.py    ← Bot monitoring + claims
    └── cache_*.json      ← Cache anti-doublons
```

## Pitfalls

- **Ne pas recommander le mining** : GPU mining ETH est mort (merge 2022). L'utilisateur le sait et le rejette.
- **Ne pas recommander le trading algorithmique basique** : grid/market making/momentum sur crypto = perte garantie. L'utilisateur le rejette.
- **Ne pas survendre l'IA** : vendre la vitesse, la confidentialité (GPU local = RGPD), pas la supériorité sur l'humain.
- **Ne pas vendre de signaux de trading** : illégal en France sans agrément AMF.
- **Ne pas passer de challenges prop firm** : interdit par les TOS.
- **Dépendances uv** : préférer `uv run --with <package>` plutôt que `pip install` — pas de pollution système, compatible PEP 668.
- **web3.py** : installer via `uv run --with web3`, pas d'installation globale nécessaire.
- **Cache airdrop** : initialiser avec `rm -f cache_*.json` avant la première vérification.
- **Scripts cron** : les chemins absolus/relatifs dans `cronjob script=` sont refusés — placer dans `~/.hermes/scripts/` et utiliser le nom de fichier seul.