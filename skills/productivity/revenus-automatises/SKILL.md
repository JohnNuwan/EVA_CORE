---
name: revenus-automatises
description: "Pipeline de revenus automatisés : freelance IA (ComeUp) géré par email + airdrop bot crypto. L'agent produit les livrables et gère les clients ; l'humain valide et encaisse."
category: productivity
---

# Revenus automatisés — Freelance + Airdrop

Pipeline complet combinant revenus actifs (freelance IA) et passifs (chasse aux airdrops), géré par l'agent. L'humain garde la main sur l'identité légale, la validation finale et l'encaissement.

## Structure du projet

```
~/revenus-alternatifs/
├── freelance/
│   ├── gigs/                    # 3 gigs ComeUp prêts à publier
│   │   ├── 01-extraction-pdf-excel.md
│   │   ├── 02-automatisation-python.md
│   │   └── 03-chatbot-rag.md
│   └── livrables/               # Scripts testés, prêts à adapter
│       ├── extracteur_pdf.py     # PDF → Excel (OCR + natif)
│       └── fusion_data.py       # Fusion CSV/Excel + dédoublonnage
└── airdrop/
    ├── wallet-eva.json          # Wallet EVM dédié (chmod 600)
    ├── config.json              # Configuration réseau
    ├── airdrop_bot.py           # Bot monitoring DefiLlama
    └── cache_*.json             # Cache de suivi
```

## Phase 1 — Freelance IA (ComeUp)

### Workflow client via email

L'agent (E.V.A) gère toute la communication client de bout en bout :

1. Client envoie un email → agent lit via **Himalaya** CLI
2. Agent répond pour clarifier le besoin / négocier
3. Agent produit le livrable technique (script testé, README)
4. **Humain valide** le livrable
5. Agent livre au client + suit la satisfaction

L'humain n'intervient QUE pour : valider le livrable et encaisser.

### Setup Himalaya

```bash
curl -sSL https://raw.githubusercontent.com/pimalaya/himalaya/master/install.sh | PREFIX=~/.local sh
```

Configurer `~/.config/himalaya/config.toml` avec IMAP/SMTP Gmail (App Password
dédié). Voir le skill `himalaya` pour la config complète.

### Limites de l'agent

- Ne PEUT PAS créer de compte sur les plateformes (captcha, vérif téléphone)
- Ne PEUT PAS valider les CGV (légal, incombant à l'humain)
- Ne PEUT PAS encaisser l'argent (compte bancaire nominatif)
- Ne PEUT PAS passer d'appels téléphoniques
- Ne PEUT PAS recevoir de SMS (2FA)

### Les 3 gigs

| Service | Prix base | Options | Livrable |
|---------|-----------|---------|----------|
| Extraction PDF→Excel | 20€ | +30€/+80€ volume, +25€ pipeline | extracteur_pdf.py testé |
| Automation Python | 80€ | +40€/+25€/+30€/+50€/+80€ options | fusion_data.py testé |
| Chatbot RAG privé | 250€ | +80€/+50€/+100€/+60€/+30€ options | À coder sur commande |

### Stratégie de lancement

1. Publier les 3 gigs sur ComeUp (comeup.com)
2. Prix d'appel bas (20€) pour les premiers avis 5 étoiles
3. Marge dans les options, pas dans l'offre de base
4. Répondre < 1h aux contacts
5. Livrer en avance sur les premières commandes

## Phase 2 — Airdrop bot

### Génération du wallet EVM

```bash
uv run --with eth-account python3 -c "
from eth_account import Account
import secrets
account = Account.create(secrets.token_hex(32))
print(f'Adresse : {account.address}')
print(f'PK : {account.key.hex()}')
"
```

Sauvegarder dans `~/revenus-alternatifs/airdrop/wallet-eva.json` (chmod 600).

### Monitoring

Script `airdrop_bot.py` avec modes :
- `--check` : vérifie les nouveaux protocoles sur DefiLlama
- `--claim` : vérifie les balances gas sur Arbitrum, Ethereum, Base, Polygon
- `--monitor` : mode cron (identique à --check, silencieux si rien)

Cron Hermes toutes les 6h via `no_agent=true` + script shell.

### Stratégie

- Interagir tôt sur les nouveaux protocoles listés DefiLlama
- Cibler catégories : DEX, Lending, Bridge, Cross-chain, Derivatives
- Gas sur L2 uniquement (Arbitrum, Base, Polygon) — ~10-20€ suffit
- Ne jamais mettre de fonds importants dans le wallet dédié

## Pitfalls

- **Ne pas survendre le chatbot RAG** : le moteur TF-IDF ne comprend pas les
  synonymes, documenter les limites dans le README client.
- **Ne pas promettre de rendements** pour l'airdrop : c'est spéculatif, le
  risque est limité au gas investi (~20€).
- **Le wallet EVM est dédié** : jamais de fonds importants, uniquement du gas.
- **Himalaya nécessite un App Password Gmail** (pas le mot de passe principal).
- **Les scripts livrables doivent être testés AVANT la première commande.**