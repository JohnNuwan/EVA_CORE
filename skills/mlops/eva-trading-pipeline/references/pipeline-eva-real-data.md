# Pipeline E.V.A — Détails de validation sur données réelles

Référence de session : pipeline E.V.A validé sur The Hive (2× RTX 3090,
torch 2.6+cu124, jax 0.11.0) sur XAUUSD M15 (50 000 barres MT5).

## Benchmarks GPU (moyennes après warmup XLA, cuda:1)

| Opération | Latence |
|---|---|
| DLPack (64×128) | 0.34 ms |
| CEM 5 000 trajectoires (6 iters) | 7.4 ms |
| Arène 64 agents (512 pas) | 54 ms |
| Évolution génétique jittée | 1.8 ms |

## Pré-entraînement JEPA (XAUUSD M15, 2000 steps, batch 32)

- Config : AdamW + cosine + warmup 50, lr 3e-4, clip 1.0, EMA 0.999.
- Perte : 0.129 → 0.0087 (×15, ~66 step/s).
- Encodeur figé : latents std 1.46, cos fenêtres adjacentes 0.991, aucun collapse.
- Checkpoints : checkpoints_jepa/jepa_final_XAUUSD_m15.pt (10 Mo).

## Bug critique : artefact de levier composé

Avant fix (rendement depuis prix d'entrée figé) :
- gen 51 : fitness 65.6, np +70%
- gen 64 : fitness 2294, np +2295%
- gen 83 : fitness 30967, np +3308%, sortino 13829  ← ABSURDE

Après fix (mark-to-market barre-à-barre + prix_entree=prix_seq[0]) :
- rendements réalistes ~1-4% sur 512 barres
- progression par paliers saine : 0.21→0.83→1.56→2.08→2.13→2.67→3.41

## Verdicts backtest holdout (barres 40000-50000, jamais vues)

| Champion | Fitness train | Holdout np | Holdout dd | PF | Verdict |
|---|---|---|---|---|---|
| gen0 | 0.211 | +2.31% | 0.27% | 1.32 | GÉNÉRALISE |
| gen1 | 0.834 | +8.15% | 0.64% | 0.06 | GÉNÉRALISE (rentable) |
| gen9 | 1.556 | −1.44% | 5.45% | 0.95 | SURAPPRENTISSAGE |
| gen23 | 2.075 | −8.14% | 13.72% | 1.07 | SURAPPRENTISSAGE |

Leçon : la fitness train la plus élevée (gen23) est la PIRE en holdout. Le
backtest holdout est le seul juge fiable — la fitness seule favorise la
surapprentissage.

## Code validé — mark-to-market (jax_arena.py)

```python
prix_precedent = jnp.maximum(etat.prix_entree, EPS)
rendement_prix = (prix - prix_precedent) / prix_precedent
retour_net = etat.position * rendement_prix - cout
# prix_entree = prix (mark-to-market), init = prix_seq[0]
```

## Code validé — détection trades discrets

```python
pnl_trade = etat.pnl_trade_courant + retour_net
changement_signe = (etat.position != 0) & (signal != 0) & (jnp.sign(signal) != jnp.sign(etat.position))
retour_neutre = (etat.position != 0) & (signal == 0)
trade_ferme = changement_signe | retour_neutre
nb_trades += trade_ferme.astype(float)
gagne = trade_ferme & (pnl_trade > 0)
profit_factor = profit_brut / max(perte_brute, 1e-9)
```

## Code validé — sanitizer (calibration XAUUSD)

```python
# taille_contrat = 100 (oz pour métaux), PAS 100_000 (forex)
risque_montant = equity * (risque_max_pct / 100.0)          # 1000$ pour 1%/100k
lot_risque = risque_montant / (distance_sl * taille_contrat) # 1000/(5*100)=2.0 lots
lot_marge = (equity * levier_max) / (prix * taille_contrat)  # plafond marge
lot_max = min(lot_risque, lot_marge)
# fraction = |signal[1]| (CEM produit [-1,1], magnitude = conviction)
# lot_souhaite = lot_max * fraction ; refus si lot_max < lot_min
```

## Structure dépôt jepa_eva (branche main)

- eva/ : package modulaire (normalisation, JEPA, pont DLPack, TD-MPC2, arène)
- jax_arena.py : arène consolidée + CEM + benchmark GPU
- jepa_pipeline.py / action_sanitizer.py / donnees_reelles.py / main.py
- train_jepa.py / precompute_latents.py / train_arena.py / backtest_validation.py
- checkpoints_jepa/ (encodeur 10Mo), latents/ (50k×128), registry_arena/champions/ (poids npz)
