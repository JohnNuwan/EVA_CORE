# Paper Trading Multi-Symboles E.V.A

Architecture et résultats de la session du 2026-07-21 pour le paper trading
live multi-symboles sans ordres réels sur The Hive.

## Sources de données live gratuites

| Symbole | Source | API | Coût | Notes |
|---------|--------|-----|:----:|-------|
| BTCUSDT, SOLUSDT | Binance REST | `/api/v3/klines` | Gratuit | 1000 req/min, illimité |
| HYPUSDT | Bybit REST | `/v5/market/kline` | Gratuit | Rate limit 50 req/s |
| XAUUSD | Yahoo Finance (GLD ×10) | `yfinance` | Gratuit | ETF GLD ×10 = spot or |
| EUR/USD, autres | Alpha Vantage | `FX_INTRADAY` | Free tier | Quotidien gratuit |

## Architecture

```
Binance REST ─┬─ BTCUSDT M15 ──→ champion gen99 (+38.82%) → ordre virtuel
              ├─ SOLUSDT M15 ──→ champion gen9  (+7.67%)  → ordre virtuel
Bybit REST ───└─ HYPUSDT M15 ──→ champion gen4  (+5.59%)  → ordre virtuel
GLD ×10 ───────────────────────→ champion gen4  (+5.06%)  → ordre virtuel
                                          │
                                          ▼
                               Portefeuille virtuel
                               100 000$ répartis (35/20/20/25)
                               P&L tracké, positions suivies en MTM
```

## Script

`~/jepa_eva/paper_trading.py`

### Boucle d'exécution (tick 60s)

1. **Data** : tick toutes les 60s via API REST (pas de WebSocket)
   - BTCUSDT, SOLUSDT : Binance `/api/v3/klines?interval=15m&limit=138`
   - HYPUSDT : Bybit `/v5/market/kline?category=spot&symbol=HYPEUSDT&interval=15&limit=138`
   - XAUUSD : GLD ×10 via `yfinance.download("GLD", period="2d", interval="15m")`
2. **Encodeur** : proxy latent simplifié (normalisation grossière prix/50000).
   En production : appeler `JEPAPipeline.encoder()` sur chaque symbole (GPU 0).
3. **Planification** : `TDMPC2Planner(nb_trajectoires=512, nb_iterations=2)`
4. **Sanitizer** : `ActionSanitizer` risque 1%, distance SL par ATR
5. **Exécution** : ordre virtuel uniquement (direction ±1, lots calculés)

### Allocation du capital

| Symbole | Allocation | Champion | Capital virtuel |
|---------|:----------:|:--------:|:---------------:|
| BTCUSDT | 35% | gen99 +38.82% | 35 000$ |
| SOLUSDT | 20% | gen9 +7.67% | 20 000$ |
| HYPUSDT | 20% | gen4 +5.59% | 20 000$ |
| XAUUSD | 25% | gen4 +5.06% | 25 000$ |

### États des champions (2026-07-21)

| Symbole | Champion | Profit holdout | Drawdown | Win Rate | PF | Trades |
|---------|:--------:|:--------------:|:--------:|:--------:|:--:|:-----:|
| BTCUSDT | gen99 | **+38.82%** | 0.01% | 72.7% | 5.25 | 11 |
| SOLUSDT | gen9 | **+7.67%** | 4.87% | 51.1% | 1.72 | 438 |
| XAUUSD | gen4 | **+5.06%** | 0.08% | 42.9% | 17.15 | 70 |
| HYPUSDT | gen4 | **+5.59%** | 0.24% | 62.7% | 10.15 | 204 |
| ETHUSDT | gen4 | -1.89% | 5.30% | 36.8% | 2.63 | 370 |

### Cron jobs

Deux cron jobs Hermes gèrent le paper trading automatiquement :

1. **Airdrop Monitor** — toutes les 6h via `airdrop-monitor.sh`
2. **Paper Trading** — toutes les 15min via `paper-trading-eva.sh`

Le script daemon `paper_trading.py` tourne en continu en background
(process Hermes). Le cron est une redondance pour couvrir les crashs.

### Limites connues

1. **Proxy latent** : l'encodeur JEPA n'est pas appelé en live. Solution :
   pré-calculer les latents en batch toutes les 15min via `precompute_latents.py`.
2. **GLD ×10 vs XAUUSD spot** : le facteur 10 est approximatif (GLD ≈ 1/10e
   d'once). Les rendements M15 sont corrélés à >99% avec le spot XAUUSD.
   Pour entraîner : utiliser données MT5 (~$2,395). Pour live : GLD ×10 (~$3,740).
3. **ETHUSDT** : champion non généralisant (-1.89%). Solution :
   `train_arena_generalisee.py --symbole ETHUSDT --generations 200 --lambda_holdout 2.0`
4. **JAX mémoire GPU 0** : les backtests allouent ~14 GiB. Si `train_jepa.py`
   plante OOM après un backtest, attendre 5-10s que la mémoire se libère.

## Commandes

```bash
# Lancer le paper trading (daemon)
cd ~/jepa_eva && PYTHONPATH=. venv/bin/python paper_trading.py

# Backtester un champion
PYTHONPATH=. venv/bin/python backtest_validation.py \
  --champion registry_arena_validated/champions/champion_gen99.npz \
  --symbole BTCUSDT

# Chaîne complète pour un nouveau symbole (JEPA + latents + arène)
PYTHONPATH=. venv/bin/python train_jepa.py --symbole BTCUSDT --steps 2000
PYTHONPATH=. venv/bin/python precompute_latents.py --symbole BTCUSDT --checkpoint checkpoints_jepa/jepa_final_BTCUSDT_m15.pt
PYTHONPATH=. venv/bin/python train_arena_validated.py --symbole BTCUSDT --generations 100

# Scraper depuis Bybit
PYTHONPATH=. venv/bin/python scrape_crypto.py \
  --pairs HYPUSDT --timeframe m15 --barres 50000 --source bybit
```