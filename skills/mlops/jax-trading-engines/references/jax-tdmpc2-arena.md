# Référence JAX : TD-MPC2 + Arène génétique (Patterns #23 à #26)

Détails de session E.V.A (2026-07-19) — code validé sur The Hive
(2× RTX 3090, torch 2.6+cu124, jax 0.11.0, jax-cuda12-plugin).

## Architecture du pipeline E.V.A

```
OHLCV -> DynamicNormalizer + TimeJEPAEncoder (PyTorch, GPU 0)
      -> jax.dlpack.from_dlpack (zéro-copie) -> JAX (GPU 1)
      -> World Model GRU + CEM 5000 traj (jax.jit + jax.vmap)
      -> ActionSanitizer (1% risque) + DrawdownDisconnector (4%/jour)
```

Fichiers : `~/ftmo_agent/eva/*.py` (package), `~/ftmo_agent/jax_arena.py`
(module consolidé autonome ~890 lignes), `~/ftmo_agent/jepa_pipeline.py`,
`~/ftmo_agent/action_sanitizer.py`, `~/ftmo_agent/main.py`.

## Pattern #23 : les hyperparamètres structurels doivent être STATIQUES sous jit/vmap

Toute valeur utilisée pour un slice, un `jnp.arange`, ou la forme d'un
tableau doit être statique (Python int/float, jamais un traceur JAX).

Erreurs typiques rencontrées :
- `ConcretizationTypeError: Abstract tracer value ... jnp.arange argument 'stop'`
  → `horizon` passé en argument dynamique à une fonction jittée qui fait
  `jnp.arange(horizon)`. Fix : capturer `horizon` en closure statique.
- `IndexError: Slice entries must be static integers`
  → `nb_elites` tracé sous jit alors qu'il sert à `array[-nb_elites:]`.
  Fix : le passer en `static_argnums`.

Règles :
- Capturer les hyperparamètres structurels (horizon, gamma, nb_elites,
  tailles) via closure ou `static_argnums` — jamais en arguments dynamiques.
- `static_argnums=(0,)` pour `self` dans les méthodes `@partial(jax.jit, ...)`.
- Ajouter les hyperparamètres de slicing dans `static_argnums` (ex. `(0, 4, 5, 6)`).

## Pattern #24 : vmap sur une fonction à N args — fermer via closure/tuple

`jax.vmap(f, in_axes=...)` exige exactement autant d'entrées `in_axes` que
d'arguments positionnels de `f`.

Erreur rencontrée :
- `ValueError: vmap in_axes ... len(in_axes)=3, len(args)=2`
  → fonction interne à 3 args (params, prix, latents) mappée avec
  `in_axes=(0, None, None)` alors que le jit extérieur n'attend que 2 args.

Fix validé : regrouper les arguments non-mappés en un seul tuple passé
comme `in_axes=None`, ou réduire la fonction à 2 args
`(params_agent, (prix_seq, latents_seq))` et `in_axes=(0, None)`.

## Pattern #25 : calibration du contrat par classe d'actif (CRITIQUE trading)

`taille_contrat` doit correspondre à la classe d'actif, sinon le risque est
massivement fausse.

- XAUUSD / métaux : 1 lot = 100 oz → `taille_contrat = 100`.
- Forex : 1 lot = 100 000 unités → `taille_contrat = 100_000`.

Erreur rencontrée : contrat laissé à 100_000 pour XAUUSD → risque 1000×
surestimé → tous les lots écrasés à 0.00, aucun ordre émis. Silencieux.

Sizing validé (risque% × equity / (SL_dist × contrat), plafonné par la marge) :
- XAUUSD, equity 100k, SL 5$, risque 1% → lot_max = 1000/(5×100) = 2.0 lots.
- Perte au SL = lot × contrat × SL_dist (en devise du compte).

## Pattern #26 : CEM non entraîné — fraction = |signal[1]|, lot borné par le risque

Un planner CEM avec world model aléatoire produit des actions dans [-1, 1]
(bruit). Deux pièges pour le sanitizer :

1. `fraction = clip(signal[1], 0, 1)` ignore la magnitude quand signal[1] < 0.
   Fix : `fraction = |signal[1]|` — la magnitude porte la conviction.
2. `lot_souhaite = lot_max_borne × fraction` (borne dure, ex. 100 lots) →
   avec fraction ~0, lot ~0, ordres refusés en masse. Fix :
   `lot_souhaite = lot_max_risque × fraction` — toujours borné par le risque
   calculé (risque% × equity / (SL × contrat)), jamais par une borne arbitraire.

Protection absolue : si `lot_max_risque < lot_min` (stop trop serré pour
respecter 1%), REFUSER l'ordre (ne pas forcer lot_min qui dépasserait le risque).

## Benchmarks validés (RTX 3090, cuda:1, après warmup XLA)

| Opération | Latence |
|---|---|
| DLPack (64×128) | 0.34 ms |
| CEM 5 000 trajectoires (6 iters) | 7.4 ms |
| Arène 64 agents (512 pas, vmap+jit) | 54.5 ms |
| Évolution génétique (crossover+mutation Pytrees) | 2.8 ms |

## Gotchas DLPack torch->jax

- `jax.dlpack.from_dlpack(t.detach().contiguous().float())` — le tenseur
  doit être contiguous et float32.
- Zéro-copie réel seulement si torch et jax sur le MÊME GPU ; sinon
  `jax.device_put(tableau, device_cible)` fait un transfert P2P optimisé XLA.
- 1er appel lent (compilation), ~70 µs après warmup pour (4,128).

## Gotcha SIGTERM pendant compilation XLA

Interrompre (SIGTERM/timeout) pendant la compilation XLA →
`INTERNAL: ptxas exited with non-zero error code 15` (contexte CUDA détruit).
Comportement à gérer proprement (catch RuntimeError, arrêt sans corruption).
Prévoir warmup avant la boucle temps réel.
