---
name: jax-trading-arena
description: >-
  Pipeline décisionnel JAX pour le trading quantitatif — World Model GRU,
  planificateur TD-MPC2 (CEM), arène génétique vmap/jit, pont DLPack
  PyTorch↔JAX. Pièges XLA (arguments statiques), benchmarks RTX 3090, et
  standards de qualité E.V.A (PEP 8/484/257 français, asserts de forme).
---

# Arène Décisionnelle JAX pour Trading (E.V.A.)

## Présentation

Classe de tâche : construire un moteur décisionnel trading en JAX pur
(World Model latent, planification MPC par entropie croisée, évolution
génétique de populations d'agents vectorisée), interfacé à un encodeur
PyTorch via DLPack zéro-copie. Implémentation de référence validée :
`~/ftmo_agent/jax_arena.py` (autonome, ~900 lignes) et le package
`~/ftmo_agent/eva/` (modules séparés). Validé sur The Hive : jax 0.11.0,
torch 2.6+cu124, 2× RTX 3090 (PyTorch sur cuda:0, JAX sur cuda:1).

## Architecture validée

```
OHLCV → DynamicNormalizer (PyTorch) → TimeJEPAEncoder (GPU 0)
      → jax.dlpack.from_dlpack → device_put(cuda:1)
      → TDMPC2Planner (GRU + CEM 5 000 traj, jit)
      → JaxGeneticArena (64 agents, vmap+jit)
      → ActionSanitizer (écrasement lot > 1% risque)
      → DrawdownDisconnecter (coupure à 4% journalier)
```

Fitness spécifiée : `(Sortino × 2) − MaxDrawdown% + NetProfit%`
(Sortino sur downside deviation des retours négatifs).

## Pièges JAX/XLA critiques (Pattern importé du skill rl-trading-debugging #23)

1. **ConcretizationTypeError** : hyperparamètre tracé utilisé dans
   `jnp.arange` / slice / range. FIX : capturer par closure statique ou
   passer en `static_argnums` — jamais en argument dynamique.
2. **"Slice entries must be static integers"** : `jnp.argsort(f)[-n:]` avec
   `n` tracé. FIX : `@partial(jax.jit, static_argnums=(0, 4, 5, 6))` pour
   self + tous les int scalaires (nb_elites, taux, sigma).
3. **vmap in_axes arity mismatch** : regrouper les données partagées dans
   un tuple-arg `(prix, latents)` avec `in_axes=(0, None)`.
4. **Évolution jittée** : générer `taille_pop − nb_elites` enfants via
   `jax.vmap(crossover)` + `jax.vmap(mutation)` sur Pytrees, puis
   `jnp.concatenate([elites, enfants])` — tout reste dans XLA.

## Pont DLPack PyTorch→JAX

```python
tenseur = torch_tensor.detach().contiguous()
if tenseur.dtype != torch.float32:
    tenseur = tenseur.float()
tableau = jax.dlpack.from_dlpack(tenseur)
tableau = jax.device_put(tableau, gpus[-1])  # cuda:1
assert tableau.shape == tuple(tenseur.shape)
```

Cross-GPU torch cuda:0 → jax cuda:1 validé (~0,35 ms pour (64,128) après
warmup). Guard : TypeError si non-tenseur, ValueError si vide ou >3D.

## Benchmarks réels (RTX 3090, jax 0.11.0, après warmup XLA)

| Opération | Latence |
|---|---|
| DLPack (64×128) | 0,34 ms |
| CEM 5 000 traj × 6 iters | 7,4 ms |
| Arène 64 agents × 512 pas (scan) | 54 ms |
| Évolution génétique jittée | 2-3 ms |

Le premier appel compile XLA (peut prendre 2 s+) — toujours mesurer après
warmup et rapporter des moyennes.

## Piège simulation arène : composition du drift (levier non borné)

**Symptôme** : fitness/net_profit explosent de façon irréaliste
(ex: +3308% sur 512 barres, sortino 13829) puis oscillent violemment
(-181 → +2293) entre générations.

**Cause racine** : calculer le rendement depuis le PRIX D'ENTRÉE au lieu de
la barre précédente. `retour = position × (prix/prix_entree − 1)` avec une
position tanh ±1 constante et `prix_entree` figé : si le prix dérive, le
retour se COMPOSE par barre → artefact de levier non borné, pas du trading.

**FIX (mark-to-market barre-à-barre)** : le rendement d'une barre =
position × variation relative du prix DEPUIS LA BARRE PRÉCÉDENTE.
`prix_entree` mémorise le prix de la barre précédente (pas l'entrée de
position) et est initialisé à `prix_seq[0]` (jamais 1.0, sinon le premier
rendement est énorme). Cela borne le retour à la volatilité barre-à-barre
(réaliste). Vérification : sur drift monotonique +30%, net_profit max doit
rester < 100% (et non +3308%).

**Leçon** : toute simulation d'arène trading doit être mark-to-market. Une
fitness qui dépasse quelques % par segment de quelques centaines de barres
est un signal d'alarme de levier non borné, pas une stratégie gagnante.

## Pré-entraînement JEPA validé (fondation des latents)

`~/ftmo_agent/train_jepa.py` : AdamW + cosine schedule + warmup, gradient
clipping, checkpoints périodiques. Sur 50k barres XAUUSD M15 (batch=32,
2000 steps, ~30s) : perte Smooth-L1 **0.129 → 0.0087** (×15), aucun
collapse (EMA 0.999 efficace). Encodeur figé sauvegardé
(`checkpoints_jepa/jepa_final_*.pt`, 10 Mo). Validation sur données jamais
vues : latents std ~1.5 (pas de collapse), similarité cosinus 0.99 entre
fenêtres adjacentes (lisses/cohérents). `precompute_latents.py` encode tout
l'historique en `.npz` (prix + latents alignés) pour l'entraînement de
l'arène. **Piège** : chunk le pré-calcul à ≤512 barres (position embedding
de l'encodeur = 512, pas 4096).

## Standards qualité E.V.A (exigés par l'utilisateur)

- **PEP 8 / PEP 484** : typage complet, NamedTuple pour les Pytrees,
  constantes UPPER_CASE, `ruff check` : 0 erreur.
- **PEP 257 Google Style EN FRANÇAIS** : toutes docstrings avec objectif
  algorithmique, Args typés, Returns, Raises. Vérifier avec
  `pydocstyle --convention=google` : 0 violation. Ne pas oublier les
  docstrings de `__init__` (D107) — placées AVANT `super().__init__()`.
- **Asserts de forme aux blocs critiques** : entrée JEPA, pont DLPack,
  sortie planner, fitness population. Jamais de `try/except: pass`
  générique ; exceptions ciblées ValueError/TypeError avec messages
  précis (formes attendues vs reçues).
- **Pièges PyTorch associés** : `F.pad(t, (0,0,h,0))` sur 2D padde la
  dernière dim (unsqueeze/pad/squeeze pour la dim temporelle) ; suffixer
  les buffers `*_courante` pour éviter les collisions méthode/attribut ;
  jamais de variable `l` seule (E741).

## Validation holdout + champions rejouables (anti-overfitting)

Après qu'une arène évolue, trois étapes la rendent exploitable :

1. **Trades discrets** : étendre l'état de simulation avec `nb_trades`,
   `trades_gagnants`, `profit_brut`, `perte_brute`, `pnl_trade_courant`.
   Un trade est "fermé" quand la position repasse par zéro ou change de
   signe ; on accumule alors win_rate (%) et profit_factor (profit_brut /
   perte_brute). Sans ça, le registry trace wr/pf/trades = 0 et la
   promotion n'utilise que fitness+DD (incomplet, Pattern #15).

2. **Sauvegarder les POIDS du champion** (pas seulement les métriques) :
   `jax.tree.map(lambda p: np.asarray(p[idx]), population)` → aplati →
   `np.savez_compressed`. Bloquant : sans poids, impossible de rejouer,
   backtester ou déployer le champion.

3. **Boucle train→backtest→promotion conditionnelle** : à chaque
   génération, évaluer le champion sur le HOLDOUT (barres > 80 %) toutes
   les N gens ; ne promouvoir QUE s'il généralise (net_profit > 0 et
   drawdown ≤ 5 %). Résultat réel sur 200 gens XAUUSD : 1/40 champion
   généralise (gen4 : +5.06 % holdout, pf 17.15, 70 trades) — et son
   fitness_train était faible (0.545). La sélection par généralisation
   trouve des perles que la fitness train seule rate, et détecte la
   dérive en surapprentissage (holdout −13 % après gen ~50).
   **Piège** : ne jamais promouvoir sur la seule fitness train — c'est
   le signal d'overfitting n°1.

Implémentation : `backtest_validation.py` (recharge champion, évalue sur
holdout, verdict GÉNÉRALISE/SURAPPRENTISSAGE) et
`train_arena_validated.py` (boucle conditionnelle). Détails :
`references/validation-holdout-champions.md`.

## Fichiers de référence

- `~/ftmo_agent/jax_arena.py` — module consolidé autonome (les 6
  composants + benchmark GPU exécutable : `PYTHONPATH=. venv/bin/python jax_arena.py`).
- `~/ftmo_agent/eva/` — version modulaire (normalisation, encodeur_jepa,
  pont_jax, planificateur_tdmpc2, arene_genetique, assainisseur_actions,
  disjoncteur_drawdown) + `eva/README.md`.
- `~/ftmo_agent/tests/test_bloc_{a,b,c}.py` et `test_integration_gpu.py` —
  scripts de fumée rejouables (pas pytest ; lancer avec PYTHONPATH=.).
- `references/entrainement-arena-latents.md` — entraînement arène sur
  latents JEPA réels (precompute + train_arena), ChampionRegistry Pattern
  #15, et le bug mark-to-market corrigé (composition du drift).
- `references/validation-holdout-champions.md` — trades discrets,
  sauvegarde poids champion, backtest validation, boucle train→backtest→
  promotion conditionnelle (anti-overfitting), dépôt git jepa_eva.

## Skills liés

- `rl-trading-debugging` (Patterns #15 validation multi-critères, #21 GA,
  #22 GPU vs backtest séquentiel — le CEM est de la planification
  vectorisée, pas un backtest bar-par-barre, donc GPU-compatible).
- `jepa-self-supervised-learning` (EMA 0.999, masquage bloc futur 20 %,
  Smooth-L1, stop-gradient).
