---
name: eva-data-pipeline
description: >-
  Pipeline opérationnel des données pour E.V.A — acquisition (Binance crypto,
  MT5 forex), environnement venv, entraînement JEPA, arène, et backtest.
  Capturé depuis The Hive (2× RTX 3090, CUDA 12.4, Debian 13).
---

# Pipeline de Données E.V.A — Acquisition & Entraînement

## Quand utiliser cette compétence

- Ajouter un nouvel actif (crypto, forex, indice) au pipeline E.V.A.
- Restaurer l'environnement d'entraînement (venv, torch, jax).
- Obtenir des données historiques pour un nouveau symbole.
- Suivre le workflow complet : données → JEPA → latents → arène → backtest.

## Installation / Restauration du venv

**Projet** : `~/jepa_eva/` (dépôt git, branch main).

```bash
cd ~/jepa_eva
python3 -m venv venv
venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cu124
venv/bin/pip install "jax[cuda12]"
venv/bin/pip install pandas numpy requests
```

**Vérification** :
```bash
venv/bin/python -c "import torch; print(f'torch {torch.__version__}, CUDA {torch.cuda.is_available()}')"
venv/bin/python -c "import jax; print(f'jax {jax.__version__}, devices: {jax.device_count()}')"
```

**Attention** : JAX installe sa propre cuDNN (9.25) qui entre en conflit avec
celle de torch (9.1). Le warning pip est inoffensif — les deux fonctionnent
sur GPU différents.

## Acquisition de données

### Crypto spot (Binance API)

Script : `~/jepa_eva/scrape_crypto.py` (voir `references/scrape-crypto.md`).

Usage :
```bash
cd ~/jepa_eva && PYTHONPATH=. venv/bin/python scrape_crypto.py \
  --pairs BTCUSDT,ETHUSDT,SOLUSDT --timeframe m15 --barres 50000
```

- API publique Binance, limite 1000 barres par requête, pagination automatique.
- Format sortie : `data/<PAIRE>_<TF>.csv` (50 000 barres, compatible MT5).
- Fallback Bybit si Binance échoue.
- Skip automatique si le fichier existe déjà.

Paires recommandées : BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT, ADAUSDT.

#### Fallback Bybit pour tokens absents de Binance

Certains tokens ne sont pas listés sur Binance (ex: HYPEUSDT = Hyperliquid).
Le scraper détecte l'erreur 400 et bascule sur l'API Bybit :

```bash
cd ~/jepa_eva && PYTHONPATH=. venv/bin/python scrape_crypto.py \
  --pairs HYPUSDT --timeframe m15 --barres 50000 --source bybit
```

**Particularités Bybit** :
- Limite 200 barres/requête (vs 1000 Binance) → rate limit 0.3s entre appels
- Retourne du plus récent au plus ancien → inverser avec `list(reversed(batch))`
- Moins d'historique pour tokens récents (HYPE : 36k barres max)
- Champs kline identiques à Binance : `[ts, open, high, low, close, volume, ...]`

### Forex / Indices

#### MT5 (données historiques)

Les données existent déjà dans `~/jepa_eva/data/` :
- XAUUSD, EURUSD, GBPUSD, BTCUSD (CFD), GER40, US30, US500, US100
- Timeframes : d1, h1, h4, m15 (50 000 barres chacun)
- Format : `time,open,high,low,close,tick_volume,spread,real_volume`

#### Yahoo Finance (live or)

```bash
venv/bin/pip install yfinance
```

**Ticker gold** : utiliser **GLD ETF ×10** plutôt que GC=F :
```python
import yfinance as yf
gld = yf.download("GLD", period="2d", interval="15m")
# GLD ≈ 1/10e d'once → XAUUSD spot = GLD × 10
o = gld["Open"].values * 10
h = gld["High"].values * 10
l_ = gld["Low"].values * 10
c = gld["Close"].values * 10
```

Alternativement `GC=F` (gold futures COMEX, ~$4,070). Le spot XAUUSD direct
n'existe pas sur Yahoo. GLD ×10 donne les meilleurs rendements M15 (corrélation
>99% avec le spot MT5).

#### Alpha Vantage (historique quotidien)

API key : `W14YCJIG4291TJ7E`. Endpoint premium pour intraday XAUUSD — seul
le quotidien forex est accessible en free tier. Préférer Yahoo Finance pour
l'intraday or.

```python
import requests
requests.get("https://www.alphavantage.co/query", params={
    "function": "FX_INTRADAY", "from_symbol": "XAU",
    "to_symbol": "USD", "interval": "15min",
    "apikey": "W14YCJIG4291TJ7E",
})
```

## Pipeline d'entraînement complet

### Étape 1 : Pré-entraîner l'encodeur JEPA

```bash
cd ~/jepa_eva
PYTHONPATH=. venv/bin/python train_jepa.py --symbole <PAIRE> --steps 2000 --batch 32
```

- Durée : ~30s sur RTX 3090 (60-80 step/s)
- Perte cible : < 0.02 en 2000 steps (part de ~0.12)
- Checkpoint : `checkpoints_jepa/jepa_final_<PAIRE>_<TF>.pt` (~10 Mo)

**Critique** : l'encodeur JEPA doit être ré-entraîné par CLASSE D'ACTIF.
L'encodeur XAUUSD ne fonctionne pas sur BTCUSDT (0 champions, -28% holdout).
Voir "Leçon : ré-entraînement par classe d'actif" ci-dessous.

### Étape 2 : Pré-calculer les latents

```bash
PYTHONPATH=. venv/bin/python precompute_latents.py \
  --symbole <PAIRE> \
  --checkpoint checkpoints_jepa/jepa_final_<PAIRE>_<TF>.pt
```

- Sortie : `latents/<PAIRE>_<TF>_latents.npz` (prix + latents 128-dim, 50 000 barres).
- Durée : ~2s.

### Étape 3 : Entraîner l'arène génétique

```bash
PYTHONPATH=. venv/bin/python train_arena_validated.py \
  --symbole <PAIRE> --generations 100
```

- 64 agents, 100 générations, ~30s (3-4 gen/s sur RTX 3090).
- Validation holdout toutes les 5 générations (barres 80-100%).
- Résultat : `registry_arena_validated/<PAIRE>_registry.jsonl` + champions .npz.

### Étape 4 : Backtester le champion

```bash
PYTHONPATH=. venv/bin/python backtest_validation.py \
  --champion registry_arena_validated/champions/<champion>.npz \
  --symbole <PAIRE>
```

- Verdict : "GÉNÉRALISE" si net_profit > 0% ET drawdown ≤ 5%.
- "SURAPPRENTISSAGE" sinon.

## Leçon : ré-entraînement par classe d'actif

**Ne jamais utiliser l'encodeur d'un actif sur un autre.** Résultat de
l'expérience (2026-07-21) :

| Symbole | Encodeur | Champions | Holdout |
|---------|:--------:|:---------:|:-------:|
| BTCUSDT | XAUUSD (or) | 0 | **-28%** ❌ |
| BTCUSDT | BTCUSDT (spécifique) | **13** | **+38.82%** ✅ |

**Cause** : le `DynamicNormalizer` standardise les entrées (log returns + FFT +
LayerNorm), mais les dynamiques temporelles diffèrent :
- XAUUSD : volatilité ~0.5-1%/jour, patterns lents, pas de gaps
- BTCUSDT : volatilité ~2-5%/jour, gaps fréquents, patterns rapides

L'encodeur JEPA capture ces structures temporelles spécifiques à chaque classe
d'actif. Il faut un encodeur par classe d'actif.

## Gestion mémoire GPU

**The Hive** : 2× RTX 3090, 24 GiB VRAM chacun.

| GPU | Usage permanent | Usage entraînement |
|:---:|:---------------|:-------------------|
| 0 | Services AI stack (vLLM, ComfyUI) ~8 GiB | JEPA (PyTorch) ~2-3 GiB |
| 1 | Libre | Arène (JAX), backtest |

**Piège** : les processus JAX laissent la mémoire GPU 0 allouée (~14 GiB)
après un backtest. Si le prochain entraînement JEPA plante avec OOM :
- Attendre 5-10s que la mémoire se libère automatiquement
- Ou lancer sur GPU 1 : `CUDA_VISIBLE_DEVICES=1 venv/bin/python train_jepa.py ...`
- Ou tuer le processus résiduel : `kill <PID>` (vérifier avec `nvidia-smi`)

## Résultats validés (2026-07-21)

| Symbole | Champions | Record holdout | Meilleur champion |
|---------|:---------:|:--------------:|:-----------------:|
| XAUUSD | 1 | +5.06% | gen4 |
| BTCUSDT | **13** | **+38.82%** 🏆 | gen99 |
| ETHUSDT | 1 | -1.89% | gen4 |
| SOLUSDT | 2 | +7.67% | gen9 |
| HYPUSDT | 1 | +5.59% | gen4 |

**Piège ETHUSDT** : malgré un encodeur JEPA de bonne qualité (perte 0.0099),
l'arène n'a trouvé qu'1 champion avec un holdout négatif (-1.89%). Les
crypto-monnaies à forte volatilité (ETH) peuvent nécessiter plus de
générations (200+) ou un λ_holdout plus agressif dans la fitness d'évolution.
Utiliser `train_arena_generalisee.py --symbole ETHUSDT --generations 200 --lambda_holdout 2.0` pour forcer la généralisation.

## Paper Trading Multi-symboles

Script : `~/jepa_eva/paper_trading.py` (daemon background).

Architecture pour exécuter les champions en live sans ordres réels :

```
Binance REST ─┬─ BTCUSDT M15 ──→ champion gen99 (+38.82%) → ordre virtuel
              ├─ SOLUSDT M15 ──→ champion gen9  (+7.67%)  → ordre virtuel
Bybit REST ───└─ HYPUSDT M15 ──→ champion gen4  (+5.59%)  → ordre virtuel
GLD ×10 ───────────────────────→ champion gen4  (+5.06%)  → ordre virtuel
                                          │
                                          ▼
                               Portefeuille virtuel
                               100 000$ (35/20/20/25)
```

**Sources live gratuites** :
- BTC/SOL : Binance REST (`/api/v3/klines`, gratuit)
- HYPE : Bybit REST (`/v5/market/kline`, gratuit, 200 barres/req)
- XAUUSD : GLD ETF ×10 via `yfinance` (Yahoo Finance, gratuit)

**Cron jobs Hermes** :
1. `airdrop-monitor.sh` — toutes les 6h, `workdir=~/revenus-alternatifs/airdrop`
2. `paper-trading-eva.sh` — toutes les 15min, `workdir=~/jepa_eva`
   (Rapport tick + positions + P&L)

**Usage** :
```bash
cd ~/jepa_eva && PYTHONPATH=. venv/bin/python paper_trading.py &
```

Boucle : tick 60s → rafraîchir les M15 des 4 symboles → proxy latent →
planifier CEM → sanitizer 1% → exécution virtuelle → mark-to-market.

**Limites** :
- Encodeur JEPA live non appelé (proxy latent simplifié).
- GLD ×10 est approximatif (ETF suit l'or à 99.9%, rendements M14 cohérents).
- 4 champions lourds → JAX peut saturer GPU 1 momentanément.

**Référence détaillée** : `references/paper-trading-multi-symbol.md`.

## Références

- `references/scrape-crypto.md` : détails du scraper Binance/Bybit.
- `references/paper-trading-multi-symbol.md` : architecture paper trading live, allocation portefeuille, résultats champions, cron jobs.
- `scripts/scrape_crypto.py` : script autonome de téléchargement OHLCV crypto depuis Binance/Bybit.
- `scripts/paper-trading-eva.sh` : script cron pour rapport paper trading (toutes les 15min).