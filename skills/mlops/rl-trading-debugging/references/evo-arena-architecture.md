# Architecture EVO-ARENA — GA + Arena walk-forward (successeur de V7d)

## Contexte : pourquoi on abandonne LSTM+ES

Après V5→V7d (DreamerV3 collapse #1, PPO collapse #2, ES bruité #5/#19, bias
dynamique collapse #18), la conclusion documentée : **les réseaux de neurones
profonds sur M15 surapprennent le bruit de marché**. 54.7M params pour un
signal qui tient dans ~30 nombres. Le GPU était à 16%/8%, le modèle ne
convergeait pas (WR 40-44%, PF 0.6-0.7, DD 7-10%).

**EVO-ARENA** fait l'inverse : stratégies-règles paramétriques (~30 gènes),
évaluées par backtest vectorisé CPU, validées par arena walk-forward stricte.

## Fichiers

```
/home/aza/ftmo_agent/
├── evo_core.py      — génome (30 gènes), backtest vectorisé, métriques FTMO
├── evo_ga.py        — GA : îlots, tournoi, crossover, mutation adaptative
├── evo_gpu_bt.py    — backtest GPU (ÉCHOUÉ : séquentiel = mauvais sur GPU)
├── evo_gpu.py       — présélection GPU approximative (ÉCHOUÉ : corr +0.157)
├── train_evo.py     — orchestrateur 32 CPUs + registry champions
├── test_synth.py    — test de capacité sur marché synthétique
└── checkpoints_evo/ — registry JSON, logs, historique
```

## Génome (30 gènes, ∈ [0,1]³⁰)

- **Signaux d'entrée** : use_ema_cross, use_rsi, use_vwap, use_bb, use_macd,
  use_adx + leurs seuils (ema_slope_min, rsi_long_max, rsi_short_min, ...)
- **Mode** : trade_mode (<0.33 trend, <0.66 mean-reversion, sinon both)
- **Sessions** : session_start, session_end, max_spread
- **Sorties** : sl_atr_mult, tp_atr_mult, use_slbe, slbe_trigger, use_trail,
  trail_atr_mult, max_hold_bars
- **Money mgmt** : risk_pct (0.25%-1%), allow_long, allow_short

`decode_genome()` mappe [0,1] vers intervalles réels (GENE_RANGES).

## Backtest vectorisé CPU (~130-170ms / 47k barres)

Boucle Python mais opérations numpy scalaires (pas de DataFrame.iloc dans la
boucle — les arrays sont extraits une fois via `df_to_arrays()`). SL/TP sur
extrêmes de barre, SLBE, trailing, sizing risque fixe, commission, spread
variable par session, slippage déterministe (0.2×spread, pas de bruit →
reproductible, crucial pour l'arena).

## Fitness (V2 — ambitieuse)

```
si limites OK (DDj≤2%, DDt≤5%):
    fitness = monthly_pct × 3.0
    + 25 + 2×(monthly-10) si monthly ≥ 10%   # bonus palier
    + 6.0                                     # bonus limites
sinon:
    fitness = -8×(DDj-2) - 6×(DDt-5)          # guidage vers les clous
+ 0.15×min(WR-50,10) + 3×min(PF-1,1) si ≥20 trades
- 0.5×(20-n_trades) sinon
```

**Leçon V1** : la fitness initiale (pnl_pct + bonus prudence) plafonnait à
+2.4%/mois car "être prudent" était assez récompensé. La V2 rend le profit
mensuel le moteur principal (×3) avec un palier à +10%.

## GA V2 — Island Model (anti-convergence)

**Problème V1** : population unique de 384 → top-4 identiques à gen 150,
best figé 100 générations (convergence génétique sur 1 ancêtre).

**Solution** : 6 îlots de 64 qui évoluent indépendamment (sélection et
croisement internes). Migration du meilleur vers l'îlot voisin toutes les
15 générations. Mutation adaptative : σ×2.5 et rate×1.8 si le best stagne
≥20 générations.

Résultat V2 : best progresse à CHAQUE génération (11.6→20.6 en 21 gens)
au lieu de stagner dès gen 150.

## Arena walk-forward stricte

K=6 fenêtres temporelles disjointes, chacune train(75%)/val(25%).
Promotion championne UNIQUEMENT si, sur ≥2/3 des fenêtres de validation :
- monthly_pct ≥ +10%
- max_daily_dd ≤ 2%
- max_dd ≤ 5%
- profit_factor ≥ 1.3, win_rate ≥ 50%, n_trades ≥ 10

Registry JSON avec contrôle de décorrélation (distance euclidienne entre
génomes : on rejette une championne trop proche d'une existante).

## Ce qui a ÉCHOUÉ (documenté, ne pas réessayer)

### GPU backtest barre-par-barre (evo_gpu_bt.py)
Principe : P stratégies simultanées, boucle sur T barres, kernels (P,) par
barre. **60s pour 64 backtests vs 0.17s CPU**. L'overhead de lancement CUDA
(~3µs × ~15 kernels × 19500 barres) tue tout. Le séquentiel barre-par-barre
est le MAUVAIS problème pour le GPU. De plus les résultats divergeaient du
CPU (logique subtile différente).

### GPU présélection approximative (evo_gpu.py)
Score vectorisé (rendement futur moyen à 4h capté par les signaux) sur
200k génomes en 0.6s. **Corrélation avec le backtest réel : +0.157** (faible).
Seulement 4/20 du top-20 GPU rentables au vrai backtest. Cause : le score
ignore SL/TP/sizing/spread/DD — précisément ce qui détermine la rentabilité.
Un génome peut capter des rendements futurs positifs mais mourir sur un SL
trop serré.

### Multithreading CUDA
`illegal memory access` avec 2 threads partageant les GPU + empty_cache.
PyTorch CUDA n'est pas thread-safe dans ce pattern → utiliser 1 thread ou
des processus séparés.

## Leçon matérielle (importante)

Le backtest de stratégies est **intrinsèquement séquentiel** (chaque barre
dépend de la position ouverte). Le bon hardware :
- **CPU** : oui, massivement (32 cœurs × stratégies indépendantes) ✅
- **GPU** : non pour le séquentiel ; utile SEULEMENT si on réécrit le
  backtest de façon fully-vectorisée SANS dépendance temporelle (ex: grid
  search de signaux précalculés), ce qui est un problème différent.
- **RAM** : population 4096+ tient aisément (génome = 30 floats).

La bonne métrique de vitesse : **~20 000 stratégies/minute** sur 32 CPUs,
pas "GB de VRAM utilisés".

## Utilisation

```bash
cd ~/ftmo_agent && source venv/bin/activate
# Test de capacité (DOIT trouver la stratégie longue sur marché haussier)
python test_synth.py
# Run complet : 500 gens, 6 îlots de 64, arena toutes les 25 gens
python train_evo.py --gens 500 --pop 384 --arena-every 25 --fresh
```

## Résultats de référence

- V1 (pop unique, fitness prudente) : plafonne à +2.4%/mois, DDj 1.5%,
  DDt 5%, PF 1.43, WR 43% — limites FTMO OK mais profit insuffisant.
- V2 (îlots + fitness ambitieuse) : convergence continue, voir
  checkpoints_evo/run_v2_islands.log.
