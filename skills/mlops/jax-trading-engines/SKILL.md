---
name: jax-trading-engines
description: >-
  Construction de moteurs décisionnels JAX pour le trading — pont DLPack
  PyTorch->JAX zéro-copie, World Model GRU, planification CEM (TD-MPC2),
  arène génétique vmap/jit, sanitizer de risque et disjoncteur drawdown.
  Couvre les pièges JIT/vmap, la calibration de contrat par actif et le
  sizing de lot.
category: mlops
---

# Moteurs décisionnels JAX pour le trading

## Présentation

Compétence pour construire le côté JAX d'un pipeline de trading souverain
dual-GPU : encodage latent PyTorch (GPU 0) -> DLPack -> moteur JAX (GPU 1)
-> garde-fous déterministes. Complète `rl-trading-debugging` (qui couvre le
diagnostic RL/ES/GA) en se concentrant sur la MÉCANIQUE JAX de production.

Cas d'usage : TD-MPC2, planification CEM, arène génétique sous jax.vmap/jit,
couche d'action avec règles de risque strictes (FTMO).

## Pipeline de référence (E.V.A)

```
OHLCV -> DynamicNormalizer + TimeJEPAEncoder (PyTorch, GPU 0)
      -> jax.dlpack.from_dlpack (zéro-copie) -> JAX (GPU 1)
      -> World Model GRU + CEM (jax.jit + jax.vmap)
      -> ActionSanitizer (risque 1%) + DrawdownDisconnector (4%/jour)
```

## Règles d'or JAX (jit / vmap)

1. **Hyperparamètres structurels = STATIQUES.** Toute valeur servant à un
   slice, `jnp.arange`, ou une forme de tableau doit être statique (int/float
   Python). Les capturer via closure ou `static_argnums` — JAMAIS en argument
   dynamique. Sinon `ConcretizationTypeError` (arange) ou `IndexError: Slice
   entries must be static integers` (slicing).
2. **vmap : autant d'in_axes que d'args.** Regrouper les arguments non-mappés
   en un tuple passé `in_axes=None`. Erreur typique :
   `len(in_axes)=3, len(args)=2`.
3. **Méthodes jittées** : `@partial(jax.jit, static_argnums=(0,))` pour
   `self`, + indices des hyperparamètres de slicing.

## Règles d'or trading (sizing / risque)

1. **Calibration contrat par actif (CRITIQUE).** `taille_contrat` = 100 pour
   XAUUSD/métaux (1 lot = 100 oz), 100_000 pour le forex. Une mauvaise
   valeur fausse le risque par des ordres de grandeur, SILENCIEUSEMENT.
2. **Sizing** : lot = risque% × equity / (SL_dist × contrat), plafonné par la
   marge (equity × levier / (prix × contrat)). Le levier déplafonne le
   profit, le risque est contrôlé par le SL.
3. **CEM non entraîné** : actions dans [-1,1]. Utiliser `fraction = |signal[1]|`
   (magnitude = conviction), et borner `lot_souhaite` par le risque calculé,
   JAMAIS par une borne arbitraire (sinon lot ~0, ordres refusés en masse).
4. **Protection absolue** : si `lot_max_risque < lot_min` (stop trop serré),
   REFUSER l'ordre plutôt que forcer lot_min qui dépasserait le risque.
5. **Disjoncteur drawdown** : seuil journalier (ex. 4%) sur perte latente +
   réalisée. Coupe TOUTES les positions, suspend les ordres jusqu'à
   réarmement MANUEL, journalise (JSONL) avec pénalité de fitness. Garde-fou
   non soumis à l'IA, vérifié AVANT tout calcul de signal.

## Checklist

1. [ ] jit/vmap : hyperparamètres structurels en closure/static_argnums
2. [ ] vmap : in_axes == nombre d'args positionnels
3. [ ] DLPack : tenseur `.detach().contiguous().float()` avant from_dlpack
4. [ ] taille_contrat calibré à l'actif (100 XAUUSD / 100k forex)
5. [ ] lot borné par risque calculé, refus si < lot_min
6. [ ] disjoncteur vérifié avant chaque émission d'ordre
7. [ ] warmup XLA avant la boucle temps réel (SIGTERM pendant compile = ptxas 15)

## Références

- `references/jax-tdmpc2-arena.md` — patterns #23-#26 détaillés (jit/vmap,
  calibration contrat, sanitizer CEM), benchmarks RTX 3090 (DLPack 0.34 ms,
  CEM 5000 traj 7.4 ms, arène 64 agents 54.5 ms), gotchas DLPack et SIGTERM.

## Skill lié

- `rl-trading-debugging` : diagnostic RL/ES/GA (22 patterns), fitness,
  arena multi-critères, pourquoi GA > NN pour le trading M15.
