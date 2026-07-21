---
name: crypto-income-automation
description: >-
  Revenus crypto automatisés sans trading directionnel — airdrop hunting,
  DeFi yield farming, staking, provision de liquidité sur paires stables.
  L'agent gère la surveillance, les interactions on-chain, et le wallet
  management. Zéro capital requis pour les airdrops.
category: finance
---

# Crypto Income Automation — Revenus passifs crypto

## Quand utiliser ce skill

- L'utilisateur veut générer des revenus crypto sans trading ni mining
- L'utilisateur a rejeté le trading basique (volatilité, risque de perte)
- L'utilisateur veut un pipeline automatisé que l'agent gère 24/7
- Besoin de créer un wallet dédié pour l'agent

## Principes clés

- **Pas de trading directionnel** : les stratégies ici sont non-directionnelles (airdrops, yield farming, staking, LP stables). Zéro spéculation sur le prix.
- **L'agent gère, l'utilisateur récolte** : je crée et opère le wallet, les scripts, l'automation. L'utilisateur fournit le capital initial (gas L2, ~20-50€) et récupère les gains.
- **Coût = gas uniquement** : les airdrops ne coûtent que du gas sur L2 (Arbitrum, Optimism, Base). Les autres stratégies (yield) nécessitent du capital.

## Pistes classées par risque décroissant

### 1. Airdrop Hunting (Phase 2 prioritaire)
- **Risque** : ~0 (coût = gas L2, quelques $/mois)
- **Potentiel** : 500-5000$+ par airdrop si timing + volume
- **Automation** : surveillance des nouveaux protocoles, interactions on-chain, claims, testnets
- **Wallet** : EVM dédié généré par l'agent. Voir `references/wallet-airdrop-automation.md`
- **Sites de veille** : DefiLlama airdrops, Etherscan, Dune dashboards, Twitter crypto

### 2. DeFi Yield Farming (stablecoins)
- **Risque** : faible (stablecoins, protocoles audités)
- **Rendement** : 5-15% APY sur Aave, Compound, Morpho
- **Capital requis** : oui (minimum 50-100€ pour que ça compte)
- **Automation** : compounding automatique, rééquilibrage

### 3. Staking
- **Risque** : faible (slashing risk sur certains protocoles)
- **Rendement** : 3-12% APY (ETH, L2s, SOL)
- **Capital requis** : oui
- **Automation** : délégation, compounding, monitoring

### 4. Provision de liquidité (paires stables)
- **Risque** : faible (impermanent loss minimal sur stable-stable)
- **Rendement** : 3-20% APY
- **Capital requis** : oui
- **Automation** : rééquilibrage, claim des fees

## Stack technique

### Wallet
- Génération via Python (eth-account) ou cast (foundry)
- Stockage sécurisé : seed phrase chiffrée dans `~/.hermes/secure/wallet/`
- Wallet EVM compatible Ethereum, Arbitrum, Optimism, Base, Polygon

### Automation
- Scripts Python avec web3.py / ethers.js
- Cron jobs Hermes pour surveillance périodique
- Base de données locale des interactions (txns, claims, protocoles)

### Surveillance
- Scraping des annonces d'airdrop (Twitter, DefiLlama, blogs)
- Monitoring des smart contracts pour nouveaux claims
- Alertes sur les fenêtres de claim / snapshot

## Workflow de lancement

1. **Créer le wallet dédié** (voir `references/wallet-airdrop-automation.md`)
2. **Financer le wallet** (gas sur L2: Arbitrum/Base/Optimism, ~20€)
3. **Déployer le script de surveillance** (cron job Hermes)
4. **Interagir avec les protocoles cibles** (testnets, mainnet)
5. **Monitorer les claims et snapshots**
6. **Récolter les gains** sur un wallet de collecte séparé

## Pitfalls

- **Ne jamais exposer la seed phrase.** Le wallet agent est dédié et isolé. Jamais de seed dans le code, les logs, ou les messages.
- **Gas sur L2 seulement.** Ne jamais envoyer de fonds sur L1 (Ethereum mainnet) pour les interactions — les frais sont 10-50x plus élevés.
- **Un wallet = un profil.** Ne pas mélanger airdrop hunting avec les wallets perso de l'utilisateur.
- **Vérifier les contrats.** Ne pas interagir avec des contrats non vérifiés (rug pulls, honeypots).
- **Ne pas recommander le trading directionnel** (l'utilisateur a rejeté: trop volatil, perte assurée).
- **Ne pas recommander le mining** (rejeté: "c'est de l'arnaque").
- **Ne pas recommander la location GPU** (rejeté: besoin des GPUs).

## Références

- `references/wallet-airdrop-automation.md` — création du wallet dédié, stack technique, protocoles cibles, scripts d'interaction