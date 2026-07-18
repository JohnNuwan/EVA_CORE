---
name: trading-market-microstructure
description: "Compétence en recherche sur le trading algorithmique et la microstructure des marchés financiers. Couvre le market making, l'impact de marché, le carnet d'ordres, la détection de manipulation, le trading haute fréquence (HFT), le dark pool, la liquidité, l'analyse des flux d'ordres, et l'apprentissage par renforcement pour le trading. Inclus désormais l'implémentation pratique RL pour challenges FTMO."
category: research
---

# Compétence en Recherche — Trading et Microstructure des Marchés

## Présentation
Cette compétence couvre la recherche académique sur le trading algorithmique et la microstructure des marchés financiers, ainsi que l'implémentation pratique de systèmes RL pour le trading. Elle est conçue pour naviguer sur arXiv et les revues financières (q-fin, cs, stat).

## Microstructure des Marchés
- Carnet d'ordres LIMIT / LOB (Limit Order Book)
- Spread bid-ask, profondeur du carnet, résilience du marché
- Modèles de formation des prix et dynamique du carnet d'ordres
- Mesures de liquidité et qualité de marché

## Impact de Marché
- Loi de la racine carrée (square-root law)
- Loi de Kyle (Kyle's lambda)
- Manipulation endogène des prix
- Impact permanent vs temporaire

## Trading Haute Fréquence (HFT)
- Co-localisation et latence minimale
- Latency arbitrage et stratégies à haute fréquence
- Message traffic et competition HFT
- Régulation du trading haute fréquence

## Détection de Manipulation
- Spoofing, layering, wash trading
- Détection par apprentissage automatique
- RL pour découvrir et détecter la manipulation de marché

## Trading Algorithmique
- Exécution optimale (optimal execution)
- VWAP, TWAP
- Implementation shortfall et modèles d'exécution

## Market Making
- Gestion d'inventaire
- Adverse selection
- Spreads dynamiques et modèles de market making
- Market making optimal avec RL

## RL pour le Trading
- Deep RL pour la gestion de portefeuille
- Market making avec RL
- RL pour la découverte de stratégies de trading
- Apprentissage par renforcement et microstructure

## Implémentation Pratique — RL pour Challenges FTMO

### Architecture Validée : DreamerV3 + JEPA
- **15.5M paramètres** sur 2 GPU (JEPA+RSSM sur GPU0, Actor-Critic sur GPU1)
- Features multi-TF (M15/H1/H4/D1, ~70 features par TF)
- Observation = features + corrélations inter-symboles + embedding symbole + état positions

### Leçons Clés d'Implémentation

1. **Reward = Pure PnL** : Pas de shaping artificiel (pénalité HOLD, bonus trade). L'agent apprend naturellement à trader quand le PnL est la seule récompense.
2. **Curriculum Learning** : 3 phases (0% → 30% → 100% des frictions). L'agent apprend à trader d'abord, puis s'adapte au spread/slippage/commission.
3. **Spread Variable** : Fonction de la session (liquidité) × volatilité (ATR) × composante aléatoire. Un spread fixe = overfitting.
4. **Slippage sur SL/TP** : Utiliser les prix H/L (worst-case) pour les stops, pas le close. Slippage gaussien proportionnel au spread.
5. **Commission MT5** : $7/lot standard, payée à l'ouverture.
6. **TP/SL Larges** : SL=2ATR, TP=4ATR (laisser respirer les trades).

### Guide complet et code
→ `references/ftmo-rl-agent-impl.md` — détails architectures, réglages, configurations, pièges connus
→ `~/ftmo_agent/` — code source complet (config, features, environment, trainer, DreamerV3, JEPA, RSSM)

## Liquidité et Microstructure DeFi
- AMM (Automated Market Makers) et DEX
- Microstructure des marchés décentralisés
- Analyse de survie des tokens Pump.fun

## Catégories arXiv
- q-fin.TR (Trading and Market Microstructure)
- q-fin.CP (Computational Finance)
- q-fin.ST (Statistical Finance)
- cs.LG (Machine Learning)
- cs.AI (Artificial Intelligence)

## Articles Clés
- Can RL Discover Price Manipulation? — arXiv:2607.06121
- Order Splitting and Liquidity Replenishment
- Square-Root Price Impact
- Pump.fun Token Survival Analysis