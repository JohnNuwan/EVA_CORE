# V6 : Architecture Multi-Agent Spécialisé par Symbole

## Problème résolu

Un seul agent ES entraîné sur 7 symboles (XAUUSD, EURUSD, US30, GER40,
US500, US100, BTCUSD) ne converge pas. Cause : le gradient ES est la
moyenne des gradients sur tous les symboles. Si XAUUSD dit BUY mais
EURUSD dit SELL, le gradient net ≈ 0. Aucun apprentissage de direction.

## Architecture

```
MultiAgentOrchestrator (specialized_agents.py)
│
├── Phase 1 : Entraînement indépendant
│   ├── SingleSymbolEnv("XAUUSD")  → ESAgent(pop=8, LSTM 2×128)
│   ├── SingleSymbolEnv("EURUSD")  → ESAgent(pop=8, LSTM 2×128)
│   ├── SingleSymbolEnv("US30")    → ESAgent(pop=8, LSTM 2×128)
│   ├── SingleSymbolEnv("GER40")   → ESAgent(pop=8, LSTM 2×128)
│   ├── SingleSymbolEnv("US500")   → ESAgent(pop=8, LSTM 2×128)
│   ├── SingleSymbolEnv("US100")   → ESAgent(pop=8, LSTM 2×128)
│   └── SingleSymbolEnv("BTCUSD")  → ESAgent(pop=8, LSTM 2×128)
│
└── Phase 2 : Fine-tuning joint (TODO)
    └── MasterAgent(allocation capital + HOLD global)
```

## Classes

### SingleSymbolEnv
Wrapper qui force MultiSymbolEnvV4 sur un seul symbole.
Le reset() dans __init__ change le symbole → on le re-force après.

### SpecializedAgent
Un ESAgent + son symbole + méthodes train_generation / validate.
Chaque agent a son propre `es` (ESAgent) avec son propre ESPolicy.

### MasterAgent (placeholder)
Réseau FeedForward qui reçoit les features agrégées des N agents
et produit des poids softmax sur N+1 sorties (N symboles + HOLD).

### MultiAgentOrchestrator
Coordonne l'entraînement : charge les données, crée les agents,
exécute la Phase 1 (train_phase1), prépare la Phase 2.

## Paramètres

| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| pop_size | 8 | Données homogènes (1 symbole), gradient plus propre |
| eval_steps | 500 | Plus rapide, évaluation reste fiable sur 1 symbole |
| hidden_dim | 128 | LSTM 2 couches, ~367k params/agent |
| sigma | 0.02 | Mutation ES standard |
| lr | 0.1 | Learning rate ES |
| n_generations | 150 | ~12s/gen × 7 agents → ~30 min |
| validation | toutes les 10 gens | Diagnostic BUYvsSELL, PnL par symbole |

## Validation

Chaque agent est validé sur les 3000 dernières barres de SON symbole.
Métriques par symbole :
- PnL (%)
- Nombre de trades, winrate
- buy_vs_sell = logit[BUY] - logit[SELL]
  - Si > 1.0 → l'agent préfère BUY (marché haussier)
  - Si < -1.0 → l'agent préfère SELL (marché baissier)
  - Si ≈ 0 → l'agent n'a pas appris la direction

## Fichier

`ftmo_agent/specialized_agents.py` — implémentation de référence.
Commit : 19fdb62 sur github.com/JohnNuwan/Jepa_dreamer.

## Points d'attention

1. `n_features` doit être pris depuis l'environnement (296 avec
   embeddings + corrélations), pas depuis les données brutes (276).
2. SingleSymbolEnv doit re-forcer le symbole après construction
   car `reset()` dans `__init__` de MultiSymbolEnvV4 le change.
3. Les checkpoints sont sauvegardés par symbole :
   `checkpoints_specialized/{SYMBOL}_best.pt`
4. Chaque agent a son propre GPU (alternance cuda:0/cuda:1).