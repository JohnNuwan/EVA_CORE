# Architecture V7c — XAUUSD hybride règles + ES (Batch GPU)

## Contexte

V7 utilisait un bias directionnel dynamique (EMA/RSI/VWAP/MACD/ADX) qui
s'est révélé biaisé BUY sur marché haussier (Pattern #18). V7b est revenu
à un bias fixe symétrique. V7c ajoute l'optimisation GPU batch (Pattern #19)
et hidden_dim=512.

Évolution: V5.1 (échec) → V6 (échec) → V7 (bias dynamique, échec) →
V7b (bias fixe, h=128) → **V7c (bias fixe, h=512, batch GPU)**

## Fichiers du projet

```
/home/aza/ftmo_agent/
├── env_xauusd.py      — Environnement XAUUSD (5 actions, SLBE, Sharpe reward)
├── es_agent_v7.py     — Agent ES (bias fixe symétrique, LSTM 2×512, batch GPU)
├── arena_v7.py        — Arena darwinienne (WR>55%, PF>1.3, DD<5%, 30+ trades)
├── train_v7.py        — Trainer (200 gens, pop=16, 1000 steps, h=512, dual GPU)
└── checkpoints_v7/    — Logs, métriques, registry, champions
```

## Différences clés V7 → V7b → V7c

| Aspect | V7 (échec) | V7b | V7c (actuel) |
|--------|------------|-----|--------------|
| Bias BUY/SELL | Dynamique (indicateurs) | Fixe +3.0/+3.0 | Fixe +3.0/+3.0 |
| hidden_dim | 128 (226K params) | 128 (226K) | **512 (3.5M)** |
| Évaluation | ThreadPool séquentiel | ThreadPool séquentiel | **Batch GPU (16 modules)** |
| Temps/gen | 47s | 47s | **26s** |
| Gen 0 WR | 42.8% | 43.6% | **48.5%** |
| Gen 0 PnL | -8.24% | -6.40% | **-3.54%** |
| Biais BUY/SELL | 256/8 (collapse) | 130/134 (équilibré) | 22/242 (init aléatoire) |
| Séparation train/val | Non (chevauchement) | Oui (gap 2000 bars) | Oui (gap 2000 bars) |
| Fitness | PnL + bonus équilibre +1 | PnL + Sharpe + pénalité x10 | PnL + Sharpe + pénalité x10 |
| TF32 | Non | Non | **Oui** |

## Architecture V7c

### Bias fixe symétrique (Pattern #18)

Le bias directionnel externe a été supprimé. Le réseau apprend seul la
direction via les logits du LSTM.

```python
base_bias = torch.zeros(action_dim)
base_bias[HOLD] = -1.0
base_bias[BUY] = +3.0       # symétrique avec SELL
base_bias[SELL] = +3.0      # symétrique avec BUY
base_bias[CLOSE] = +0.5
base_bias[SPLIT_CLOSE] = -0.5
```

Le forward ignore les paramètres buy_bias/sell_bias (conservés pour
rétrocompatibilité de l'interface mais non utilisés).

### Fitness avec pénalité biais x10 + Sharpe

```python
fitness = pnl_pct
if num_trades > 0:
    fitness += 2.0
else:
    fitness -= 50.0

# Pénalité biais directionnel (Pattern #18)
if num_trades > 2:
    balance_ratio = min(buy, sell) / max(1, max(buy, sell))
    fitness += balance_ratio * 5.0      # bonus équilibré
    fitness -= (1.0 - balance_ratio) * 10.0  # pénalité imbalance

# Sharpe ratio local
if len(equity_curve) > 10:
    returns = np.diff(eq) / eq[:-1]
    sharpe = np.mean(returns) / (np.std(returns) + 1e-8)
    fitness += sharpe * 5.0
```

### Batch evaluation GPU (Pattern #19)

16 modules ESPolicyV7 séparés sur GPU (round-robin sur 2 GPUs).
Modules persistants (pas de re-création à chaque génération).
TF32 activé pour accélérer les matmuls.

### Séparation train/val

```python
# Train: barres [48, n-5000]
max_start = len(df) - 48 - 3000 - 2000
env.current_step = 48 + np.random.randint(0, max_start)

# Val (Arena): barres [n-3000, n] — jamais vues à l'entraînement
```

## Résultats V7c (test 3 générations)

| Métrique | V7a (ancien) | V7c (actuel) | Amélioration |
|----------|-------------|--------------|--------------|
| Params | 226K | 3.5M | 15× plus |
| Temps/gen | 47s | 26s | -44% |
| Gen 0 WR | 42.8% | 48.5% | +5.7pp |
| Gen 0 PnL | -8.24% | -3.54% | +4.7pp |
| Gen 0 PF | 0.66 | 0.85 | +0.19 |
| Gen 0 DD | 9.01% | 6.26% | -2.75pp |
| Gen 2 best | +4.77 | +9.56 | +4.79 |

## Configuration recommandée

```bash
python train_v7.py --gens 200 --pop 16 --steps 1000 --sigma 0.02 --lr 0.1
```

- 26s/génération sur 2× RTX 3090 (h=512, batch GPU, TF32)
- 200 générations ≈ 1h26
- Validation Arena toutes les 10 générations
- Détection automatique GPU (1, 2, ou CPU fallback)
