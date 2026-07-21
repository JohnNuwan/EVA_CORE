# Référence — Pipeline E.V.A (jepa_eva), session 2026-07-19

Détails opérationnels du pipeline JEPA→DLPack→JAX validé sur The Hive.
Projet : `~/jepa_eva` (github.com/JohnNuwan/jepa_eva, branche main).

## Structure du dépôt

| Fichier | Rôle |
|---|---|
| `eva/` | Package modulaire (normalisation, encodeur JEPA, pont DLPack, TD-MPC2, arène) |
| `jepa_pipeline.py` | OHLCV (B,T,5) → latents (B,T,128) sur GPU 0 |
| `jax_arena.py` | Arène consolidée : CEM + trades discrets + benchmark GPU |
| `action_sanitizer.py` | Risque 1 % + DrawdownDisconnector 4 %/jour (JSONL) |
| `donnees_reelles.py` | Chargeur CSV MT5 (8 symboles, 50k barres m15) |
| `train_jepa.py` | Pré-entraînement JEPA (AdamW + cosine + EMA) |
| `precompute_latents.py` | Latents 50k barres (chunk ≤ 512 = position embedding) |
| `train_arena.py` | Arène simple + sauvegarde poids champions |
| `train_arena_validated.py` | Promotion conditionnelle (holdout) |
| `train_arena_generalisee.py` | Évolution guidée par fitness train+λ·holdout |
| `train_world_model.py` | GRU supervisé transitions H_t→H_{t+1} (Adam pur JAX) |
| `backtest_validation.py` | Backtest holdout d'un champion |
| `backtest_endtoend.py` | Rejeu historique chaîne complète |
| `evaluer_multi_symbole.py` | Généralisation cross-symboles (8 symboles) |
| `connecteur_mt5.py` | Interface broker abstraite + stub fonctionnel + squelette MT5 ZMQ |
| `main.py` | Orchestrateur boucle (charge JEPA+world model entraînés, SL basé ATR) |

## Commandes validées (venv ~/ftmo_agent/venv, PYTHONPATH=.)

```bash
# 1. Pré-entraîner JEPA (~30 s, 66 step/s)
python train_jepa.py --symbole XAUUSD --steps 2000 --batch 32
# 2. Latents tout l'historique (~2 s/symbole)
python precompute_latents.py --symbole XAUUSD
# 3. Arène guidée par généralisation (~3 min, 200 gens)
python train_arena_generalisee.py --symbole XAUUSD --generations 200 --eval_holdout 5
# 4. World model GRU (~30 s, 19 step/s)
python train_world_model.py --symbole XAUUSD --steps 500
# 5. Backtest / multi-symbole
python backtest_validation.py --champion <npz>
python evaluer_multi_symbole.py --champion <npz>
```

## Benchmarks RTX 3090 (après warmup XLA)

- DLPack (64×128) : 0.34 ms
- CEM 5 000 traj × 6 iters : 7.4 ms
- Arène 64 agents (512 pas) : 54 ms
- Évolution génétique : 2 ms
- Entraînement arène : ~8 gen/s (simple), ~1 gen/s (avec holdout périodique)

## Résultats clés

- Encodeur JEPA : perte 0.129 → 0.0087, latents cos 0.991, std 1.46 (pas de collapse).
- Champion arène généralisée (gen0) : +8.11 % XAUUSD holdout, pf 13.5, 82 trades,
  GÉNÉRALISE 8/8 symboles (BTCUSD +14 %, US100 +3.9 %, GER40 +2.9 %...).
- World model GRU : perte 1.30 → 0.82 (500 steps).
- Backtest end-to-end (world model) : +29 % / 200 pas.
- Sizing XAUUSD : SL = 2 × ATR(14) → lots 0.5-0.9 (risque 1 % exact). SL fixe 5 $
  = trop serré (lots 2.0, stoppé par le bruit) — validé avec l'utilisateur.
- ConnecteurStub : ordre 0.5 lot @ 2000.2 (slippage ask), close +240 $, equity 100240.

## Données

`~/ftmo_agent/data/` : 8 symboles (XAUUSD, EURUSD, GBPUSD, BTCUSD, US30.cash,
US500.cash, US100.cash, GER40.cash) × 5 timeframes (m15,h1,h4,d1), 50 000
barres m15 chacun. Format : `time,open,high,low,close,tick_volume,spread,real_volume`.
Lien symbolique `~/jepa_eva/data → ~/ftmo_agent/data` (évite duplication 41 Mo).
Holdout = 20 % final (barres 40 000–50 000).

## Git

Auth durable : `git config credential.helper store` + `~/.git-credentials`
(format `https://USER:TOKEN@github.com`, chmod 600). Le scanner bloque tout
token en clair dans une commande — utiliser le credential helper.
