---
name: eva-trading-pipeline
description: >-
  Pipeline E.V.A (JEPA PyTorch GPU0 -> DLPack -> arène génétique JAX GPU1) pour
  trading évolutif sur données MT5 réelles. Patterns validés sur The Hive :
  simulation mark-to-market, trades discrets, backtest holdout, calibration
  contrat, pré-entraînement JEPA, promotion multi-critères.
---

# Pipeline E.V.A — Trading Évolutif JEPA + Arène JAX

## Présentation

Leçons validées en exécution réelle (The Hive, 2× RTX 3090, XAUUSD M15 50k
barres) sur le pipeline E.V.A : encodeur JEPA temporel (PyTorch GPU 0) → pont
DLPack zéro-copie → arène génétique JAX (64 agents vmap/jit, GPU 1) →
garde-fous production (sanitizer risque 1%, disjoncteur 4%/jour). Couvre les
pièges critiques qui font la différence entre un squelette qui tourne et un
agent qui généralise.

## Pattern #1 : Artefact de levier composé (fitness explosive)

**Symptôme** : En entraînant l'arène sur latents réels, la fitness explose à
des valeurs absurdes (net_profit +3308% sur 512 barres, sortino 13829). Les
"champions" records sont des exploits statistiques, pas des stratégies.

**Cause racine** : rendement par barre calculé depuis le prix d'entrée FIGÉ :
`retour = position × (prix/prix_entree − 1)`. Avec position tanh±1 constante
et drift de prix, le retour se COMPOSE de façon explosive — levier non borné.

**Solution** : mark-to-market barre-à-barre. Le rendement utilise le prix de
la barre PRÉCÉDENTE :
```python
prix_precedent = etat.prix_entree  # mémorisé à chaque pas
rendement_prix = (prix - prix_precedent) / prix_precedent
retour_net = position * rendement_prix - cout
# puis prix_entree = prix (mark-to-market)
```
Initialiser `prix_entree = prix_seq[0]` (premier prix du segment), JAMAIS 1.0
— sinon le premier rendement est (prix_0/1.0 − 1) = +200 000%.

**Vérification** : sur drift monotonique +30%, net_profit max population ≪
100% (volatilité barre-à-barre), pas +3308%.

## Pattern #2 : Position embedding trop court pour le pré-calcul

**Symptôme** : `ValueError: Séquence 4096 > position embedding 512` en
encodant tout l'historique en une passe.

**Solution** : chunker à la longueur du position embedding (512), concaténer
les latents. Ne jamais dépasser la borne du position embedding.

## Pattern #3 : Trades discrets (promotion multi-critères Pattern #15)

**Symptôme** : l'arène simule une position CONTINUE mark-to-market →
win_rate / profit_factor / nb_trades = 0 dans le registry. La promotion ne
peut utiliser que fitness+DD, pas les critères complets (WR>55%, PF>1.3,
>30 trades).

**Solution** : détecter la fermeture d'un trade par CHANGEMENT DE SIGNE de
position (ou passage à zéro), accumuler le P&L du trade :
```python
changement_signe = (position != 0) & (signal != 0) & (sign(signal) != sign(position))
retour_neutre = (position != 0) & (signal == 0)
trade_ferme = changement_signe | retour_neutre
nb_trades += trade_ferme
trades_gagnants += trade_ferme & (pnl_trade > 0)
profit_factor = profit_brut / max(perte_brute, eps)
```
Étendre l'état de simulation (nb_trades, trades_gagnants, profit_brut,
perte_brute, pnl_trade_courant) et le résultat (win_rate, profit_factor,
nb_trades).

## Pattern #4 : Backtest holdout — le seul juge de la généralisation

**Règle d'or** : toute arène entraînée sur 80% de l'historique DOIT être
évaluée sur le holdout 20%. La fitness train SEULE ne prédit PAS la
généralisation.

**Observé (E.V.A, XAUUSD M15)** : champion train fitness 2.08 → holdout
−8.14% (dd 13.7%) = surapprentissage ; champion train fitness 0.83 → holdout
+8.15% (pf 1.32) = généralise.

**Méthode** : sauvegarder les POIDS Pytree du champion (npz, pas seulement
les métriques), recharger dans une arène à population 1, évaluer sur le
holdout. Verdict : généralise si net_profit > 0 ET drawdown ≤ 5%.

## Pattern #5 : Sanitizer — calibration contrat par classe d'actif

**Symptôme** : tous les lots calculés tombent à 0.00 alors que le risque 1%
devrait autoriser plusieurs lots.

**Cause** : `taille_contrat = 100_000` (forex) appliqué à XAUUSD. Pour l'or,
1 lot = 100 oz → risque 1000× surestimé → lot_max_risque ≈ 0 → tous les
ordres refusés.

**Solution** : calibrer par classe d'actif (métaux 100 oz, forex 100 000,
indices selon le contrat). Fraction de risque = `|signal[1]|` (le CEM produit
des actions dans [-1,1], la magnitude porte la conviction), PAS
`clip(signal[1])` qui écrase les négatifs à 0.

**Vérification** : lot_max_risque(SL=5$, equity=100k, contrat=100) = 2.0
lots, perte au SL = 1000$ = exactement 1%.

## Pattern #6 : Pré-entraînement JEPA — convergence saine

**Référence validée** : AdamW + cosine schedule + warmup 50, lr 3e-4,
gradient clipping 1.0, EMA 0.999. Sur XAUUSD M15 (50k barres), 2000 steps,
batch 32 : perte 0.129 → 0.0087 (~66 step/s sur RTX 3090). Latents cohérents
(cos 0.991 fenêtres adjacentes, std 1.46 — pas de collapse).

**Vérification anti-collapse** : std latents > 0.05, similarité cosinus
fenêtres adjacentes > 0.9. Si std < 0.01 → collapse (EMA cassé).

## Pattern #7 : Orchestrateur production — robustesse

- Vérifier le disjoncteur AVANT tout calcul de signal (court-circuiter le tick).
- Ne pas émettre un ordre si lot < lot_min (après écrasement) — warning, pas d'ordre.
- Réordonner les `except` : `torch.cuda.OutOfMemoryError` AVANT `RuntimeError`
  (OOM est une sous-classe de RuntimeError → clause inatteignable sinon).
- Arrêt propre SIGINT/SIGTERM via handler qui bascule un flag `actif`.

## Pattern #8 : Ablation world model — preuve de la valeur du GRU

**Résultat (2026-07-21)** : comparaison CEM avec GRU entraîné vs GRU aléatoire
sur XAUUSD M15, 500 barres holdout :

| Métrique | GRU entraîné | GRU aléatoire | Écart |
|----------|:------------:|:-------------:|:-----:|
| PnL | **+3.04%** | **-12.45%** | **+15.49%** |
| Win rate | **50%** | **25%** | ×2 |
| Disjonctions (DD>4%) | **63** | **467** | **-86%** |
| Drawdown max | 6.80% | 13.58% | -50% |

**Conclusion** : le world model GRU entraîné apporte une réelle valeur au CEM.
Sans lui, le planificateur CEM dégénère en bruit — perte massive, disjonctions
permanentes. Le GRU apprend une dynamique latente utilisable par la
planification.

**Commande ablation** :
```bash
cd ~/jepa_eva && source ~/ftmo_agent/venv/bin/activate && PYTHONPATH=.
# Avec GRU entraîné
python3 backtest_endtoend.py --world_model checkpoints_wm/world_model_XAUUSD_m15.npz --nb_pas 500
# Avec GRU aléatoire
python3 backtest_endtoend.py --nb_pas 500
```

## Environnement validé (The Hive)

- torch 2.6+cu124 (SDPA/FlashAttention-2 OK), jax 0.11.0 CUDA (2 devices).
- Données : 8 symboles MT5 × 5 timeframes, 50k barres m15, format
  `time,open,high,low,close,tick_volume,spread,real_volume`.
- DLPack zéro-copie cuda:0 → cuda:1 (~0.34 ms pour 64×128 après warmup).
- CEM 5000 trajectoires ~7.4 ms ; arène 64 agents (512 pas) ~54 ms ; évolution ~1.8 ms.

## Références

- `references/pipeline-eva-real-data.md` : benchmarks, résultats d'entraînement,
  verdicts backtest holdout par champion, et extraits de code validés.
