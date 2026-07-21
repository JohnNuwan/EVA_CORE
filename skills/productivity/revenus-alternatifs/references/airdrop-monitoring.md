# Airdrop Monitoring — Détails techniques

## API DefiLlama

**Endpoint :** `GET https://api.llama.fi/protocols`

**Format réponse :** tableau JSON de protocoles, chacun avec `name`, `slug`, `description`, `chain`, `category`, `tvl`, `createdAt`, `twitter`, `url`.

**Tri :** par `createdAt` descendant pour obtenir les plus récents.

**Limite :** 30 premiers suffisent (les protocoles les plus récents ont le plus de chances d'airdroper).

**Catégories à potentiel airdrop :**
| Catégorie | Raison |
|-----------|--------|
| DEX | Souvent un token de gouvernance + airdrop au lancement |
| Lending | Aave, Compound, Morpho ont tous airdropé |
| Yield | Yearn, Convex, etc. |
| Derivatives | dYdX, GMX, Synthetix |
| Bridge | LayerZero, Stargate, Hop |
| Cross-Chain | Protocoles inter-chaînes récents |
| Staking Pool | Lido, Rocket Pool, SSV |
| Liquid Restaking | EigenLayer, ether.fi, Kelp |
| RWA (Real World Assets) | Tokenisation d'actifs réels |

## Wallet EVM

**Package :** `eth-account` (léger, pas de dépendance web3)
**Génération :** `Account.create(secrets.token_hex(32))` donne un wallet frais
**Stockage :** fichier JSON avec `chmod 600` (ne JAMAIS commiter)
**Sécurité :** wallet dédié airdrop uniquement, pas de fonds importants

## Script watchdog (no_agent=True)

Conditionnel : ne sortir du texte que si des nouveaux protocoles sont détectés.
Sortie silencieuse (exit 0) si rien de nouveau ou en cas d'erreur.

## Résolution de problèmes

| Symptôme | Cause | Solution |
|----------|-------|----------|
| `Route GET:/airdrops not found` | Endpoint `/airdrops` n'existe plus | Utiliser `/protocols` à la place |
| `api.airdropalert.com` ne résout pas | DNS ou domaine mort | Ignorer, utiliser DefiLlama uniquement |
| Cache dit "dans X heures" | MIN_CHECK_INTERVAL = 6h | Supprimer `cache_*.json` pour forcer la vérification |
| Balance 0 partout | Wallet vide | Envoyer ETH sur Arbitrum/Base depuis une exchange |