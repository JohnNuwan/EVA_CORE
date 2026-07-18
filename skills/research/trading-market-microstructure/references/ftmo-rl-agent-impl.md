# FTMO Challenge — RL Agent Implementation Guide

## Architecture Overview

**DreamerV3** (model-based RL) for FTMO prop trading challenges.

### Components
- **GPU0** (13.4M params): JEPA (self-supervised encoder) + RSSM World Model (recurrent state-space model)
- **GPU1** (2.1M params): Actor-Critic (policy + value network)
- Total: ~15.5M parameters

### Data Flow
```
OHLC Data → Multi-TF Features (M15/H1/H4/D1) → JEPA Encoder → RSSM Latent Dynamics
    ↓                                                    ↓
Features + Correlations + Embeddings           Actor-Critic Policy
    ↓                                                    ↓
Stacked Observation (lookback=48)               Action: HOLD/BUY/SELL/CLOSE...
```

## Environment Design (Key Lessons)

### 1. Reward — Pure PnL beats Shaping
```python
# BAD — agent learns to HOLD:
reward = pnl_norm * 15 + 1.0 if win else pnl_norm * 5
# Plus HOLD penalty, trade bonus, etc.

# GOOD — agent learns organically:
reward = equity_change / account_size  # Pure relative PnL
```

### 2. Spread — Must Be Variable
```python
# Static spread → agent overfits to unrealistic conditions
spread = base * session_mult * vol_mult + random_component
# session_mult: 0.8 (liquid hours) to 2.0 (thin hours)
# vol_mult: proportional to ATR deviation from mean
```

### 3. Slippage — Critical for FTMO Realism
```python
slippage = abs(normal(base_slippage, slp_std)) * vol_mult
# Applied on SL/TP exits, not just entries
# SL/TP checked against H/L (worst-case), not close price
```

### 4. Commission — $7/Lot Standard
```python
self.balance -= spec.commission_per_lot * lots  # Paid on entry
```

### 5. Curriculum Learning — 3 Phases
| Phase | Episodes | Spread | Slippage | Commission | Max Trades |
|-------|----------|--------|----------|------------|------------|
| 1 | 0-200 | 0% | 0% | 0% | 20 |
| 2 | 200-500 | 30% | 30% | 0% | 12 |
| 3 | 500+ | 100% | 100% | 100% | 8 |

The agent learns to trade first, then adapts to frictions.

### 6. TP/SL Ratios — Give Room
- SL = 2.0 ATR (was 1.5 — too tight)
- TP = 4.0 ATR (was 3.0)
- Risk per trade: 0.5% (was 1% — too aggressive)

## Feature Engineering (70 per TF × 4 TFs = ~280 total)

### Essential Features Added
- **HV10/HV20/HV30**: Historical volatility at multiple horizons
- **HV_ratio**: Short-term vs long-term volatility regime
- **MACD/RSI/DI slopes**: Momentum of technical indicators
- **Spread estimation**: From OHLC (Roll's estimator) or real spread data
- **Correlation features**: Rolling correlations between symbols (XAUUSD↔US30, etc.)
- **Lag features**: Shifted versions of key indicators (lag 1, 2)
- **Session volatility profile**: Which market session is most active
- **Candle patterns**: Doji, hammer, shooting star, engulfing (one-hot)
- **Range positions**: Multiple windows (8, 24, 48 bars)

### Features to Remove/Avoid
- Overlapping redundant features (body_ratio + upper_wick + lower_wick already cover candle shape)
- Raw prices (always normalize to returns/ratios)

## FTMO Rules Implementation

```python
FTMO_CONFIG = {
    "account_size": 10000,
    "daily_dd_limit": 0.05,      # 5% daily drawdown
    "total_dd_limit": 0.10,      # 10% total drawdown
    "profit_target": 0.10,       # 10% profit target
    "max_trades_per_day": 8,
    "max_concurrent_positions": 3,
    "max_hold_bars": 96,         # 24h at M15
    "min_hold_bars": 4,          # 1h at M15
    "cooldown_after_losses": 3,
    "cooldown_bars": 8,
}
```

## Known Failure Modes

1. **Agent learns HOLD** → Pure PnL reward + curriculum fix this
2. **Entropy collapse** → Cyclic temperature restart (every 500 eps, reset to 2.0), entropy floor at 0.5 nats
3. **JEPA divergence** → Lower VICReg weights (sim=10, var=10, cov=0.5, was 25/25/1), slower target momentum (0.999)
4. **Overfitting to spread** → Variable spread + curriculum prevents this
5. **Directional bias** → Anti-bias penalty (light, ~0.01) if >65% trades in one direction

## File Structure

```
ftmo_agent/
├── config.py                  # Symbol specs, FTMO rules, curriculum, risk config
├── features_v2.py             # 70-feature multi-TF engineering + correlations
├── environment_v4.py          # V4: spread, slippage, commission, curriculum, pure PnL
├── dreamer_trainer_v2.py      # DreamerV3 agent (15.5M params, dual GPU)
├── train_v4.py                # Training loop with curriculum
├── ftmo_diag_v4.py            # Diagnostics / action probability inspection
├── octopus/
│   ├── engine_src_networks_jepa.py         # TSJEPA encoder
│   ├── engine_src_networks_world_model.py   # RSSM dynamics
│   └── engine_src_networks_actor_critic.py  # Actor-Critic heads
└── data/                      # {symbol}_m15.csv (50k bars each)
```