# Architecture V7 — XAUUSD hybride règles + ES

## Contexte

V5.1 et V6 ont échoué (Patterns #14 et #15). V7 est une refonte complète
qui résout ces patterns en injectant un signal directionnel dynamique et
une validation Arena multi-critères.

## Fichiers du projet

```
/home/aza/ftmo_agent/
├── env_xauusd.py      — Environnement XAUUSD (5 actions, SLBE, Sharpe reward)
├── es_agent_v7.py     — Agent ES (bias directionnel dynamique, LSTM 2×128)
├── arena_v7.py        — Arena darwinienne (WR>55%, PF>1.3, DD<5%, 30+ trades)
├── train_v7.py        — Trainer (200 gens, pop=16, 1000 steps, dual GPU auto)
└── checkpoints_v7/    — Logs, métriques, registry, champions
```

## Différences clés vs V5.1/V6

| Aspect | V5.1/V6 (échec) | V7 |
|--------|-----------------|-----|
| Actions | 8 (HOLD/BUY/SELL/CLOSE/SPLIT_BUY/SPLIT_SELL/PYRAMID/PARTIAL_CLOSE) | 5 (HOLD/BUY/SELL/CLOSE/SPLIT_CLOSE) |
| Symboles | 7 en parallèle | 1 (XAUUSD) |
| Bias BUY/SELL | Fixe symétrique (+3.0/+3.0) | Dynamique basé sur EMA/RSI/VWAP/MACD |
| Reward | PnL brut | Sharpe ratio local (50-step window) |
| Validation | val_pnl > 0 = best.pt | Arena: WR>55% + PF>1.3 + DD<5% + 30 trades |
| SLBE | Non | Obligatoire à +0.5% |
| Features | 296 (bruit) | 20 (signal propre) |
| Registry | best.pt écrasé | JSON registry avec historique |

## Bias directionnel dynamique

Le bias n'est plus fixe — il est calculé à chaque step depuis 5 indicateurs :

```python
def _get_directional_bias(self):
    # Signal 1: EMA slope (tendance)
    ema_signal = np.clip(ema_slope * 500, -1, 1)
    # Signal 2: RSI (survente/surachat)
    rsi_signal = 0.5 if rsi < 0.3 else (-0.5 if rsi > 0.7 else (rsi - 0.5) * 0.5)
    # Signal 3: VWAP distance (mean reversion)
    vwap_signal = -0.3 if vwap_dist > 0.002 else (0.3 if vwap_dist < -0.002 else 0)
    # Signal 4: MACD histogram
    macd_signal = np.clip(macd_hist * 200, -0.5, 0.5)
    # Signal 5: ADX (amplification de tendance)
    trend_strength = min(adx * 2, 1.0)

    total = (ema_signal + rsi_signal + vwap_signal + macd_signal) / 4
    total *= (0.5 + trend_strength * 0.5)  # tendance forte → signal amplifié

    buy_bias = max(total, 0)
    sell_bias = max(-total, 0)
    return buy_bias, sell_bias
```

Dans le forward de la policy, le bias est ajouté aux logits :
```python
logits[:, BUY] += buy_bias * 3.0
logits[:, SELL] += sell_bias * 3.0
```

## Reward = Sharpe ratio local

Au lieu de PnL brut, le reward normalise par la volatilité des retours :

```python
def _compute_sharpe_reward(self, pnl_pct):
    self.returns_history.append(pnl_pct)
    if len(self.returns_history) > 50:
        self.returns_history = self.returns_history[-50:]
    if len(self.returns_history) < 5:
        return pnl_pct * 100
    mean_ret = np.mean(self.returns_history)
    std_ret = np.std(self.returns_history) + 1e-8
    sharpe = (pnl_pct - mean_ret) / std_ret
    return pnl_pct * 50 + sharpe * 10
```

## Arena de validation

Critères de promotion (tous doivent passer) :
- Win rate > 55%
- Profit factor > 1.3
- Max drawdown < 5%
- Minimum 30 trades
- Expectancy > 0

Un modèle rejeté est quand même enregistré dans le registry pour
comparison, mais n'est pas promu champion.

## Résultats initiaux (test 3 gens)

- Gen 0: 264 trades (200 BUY vs 64 SELL), WR=42.8%, bias directionnel fonctionne
- Gen 2: best fitness +4.77 (vs +2.89 au gen 0)
- Le master TRADE en mode déterministe (plus de collapse HOLD)
- BUY/SELL asymétriques → le gradient ES voit la direction

## Configuration recommandée

```bash
python train_v7.py --gens 200 --pop 16 --steps 1000 --sigma 0.02 --lr 0.1
```

- ~60s/génération sur 2× RTX 3090
- 200 générations ≈ 3h20
- Validation Arena toutes les 10 générations
- Détection automatique GPU (1, 2, ou CPU fallback)
