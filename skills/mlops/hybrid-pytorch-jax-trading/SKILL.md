---
name: hybrid-pytorch-jax-trading
description: >-
  Architecture hybride PyTorch (encodeur JEPA GPU 0) + JAX (planification
  TD-MPC2 + arène génétique GPU 1) pour le trading RL, reliées par DLPack
  zéro-copie. Pièges JAX sous jit/vmap, Time-JEPA temporel, et conformité
  qualité stricte (PEP 8/484, docstrings Google français, assertions de forme).
category: mlops
---

# Pipeline hybride PyTorch + JAX pour trading RL

Architecture validée sur The Hive (2× RTX 3090, torch 2.6+cu124, jax 0.11.0).
Code de référence : `~/ftmo_agent/eva/`. Détails session :
`references/eva-hybrid-architecture.md`.

## Quand utiliser cette architecture

- Encodeur lourd auto-supervisé (JEPA/Transformer) en PyTorch sur un GPU,
  moteur décisionnel (world model + MPC + évolution) en JAX sur un autre GPU.
- Planification vectorisée (CEM : N trajectoires indépendantes depuis un état
  commun) — parallélisable GPU, CONTRAIREMENT au backtest bar-par-barre
  séquentiel (voir skill rl-trading-debugging Pattern #22 : CPU × 32 reste
  l'optimum pour le backtest réel).

## Pont DLPack PyTorch → JAX

```python
tableau = jax.dlpack.from_dlpack(t.detach().contiguous().float())
tableau = jax.device_put(tableau, jax.devices("gpu")[-1])  # GPU dédié JAX
```

Fonctionne CPU→JAX et cuda:0→JAX cuda:1. Toujours `.detach()` +
`.contiguous()` avant `from_dlpack`. Assertion post-transfert :
`tableau.shape == tuple(t.shape)`.

## Pièges JAX sous jit/vmap (validés par l'erreur)

1. **`jnp.arange(n)` avec n tracé → ConcretizationTypeError**. Les
   hyperparamètres structurels (horizon, fenêtre) sont capturés en **closure
   statique** (variables Python dans `__init__`), jamais en arguments
   dynamiques. Pattern : wrapper défini dans `__init__` capturant
   `horizon`/`gamma`, puis `jax.jit(jax.vmap(wrapper, in_axes=(None,None,0)))`.
2. **CEM multi-itérations** : boucle Python `for` avec `jax.random.split`
   (corps jitté via `@partial(jax.jit, static_argnums=(0,))`), pas de
   `lax.scan` sur les itérations si la clé change.
3. **Dimensions perdues sous vmap population** : `jax.vmap(f, in_axes=(0,
   None, None))` mappe l'axe population — dans `f`, écrire le code
   agent-individuel en 1D (`action[0]`, `jnp.roll(hist)` sans axis), vmap
   ajoute l'axe 0.
4. **Population de Pytrees** : UN Pytree dont chaque feuille a un axe
   population en tête (via `jax.vmap(muter)(cles)`), pas une liste de Pytrees.
   Reconstruction : `jax.tree.map(lambda *xs: jnp.stack(xs), *individus)`.
5. **Premier appel jit = compilation XLA lente** (~2 s pour CEM 512 traj) —
   mesurer les perfs après warmup.

## Time-JEPA (JEPA pour séries financières 1D)

- Transformer 1D pré-norm, latent H=128 figé, SDPA = FlashAttention-2 auto.
- Masquage : bloc contigu ~20 % ancré dans la SECONDE moitié (futur) de la
  séquence ; positions masquées = token moyen du contexte.
- Cible EMA : deepcopy + `requires_grad_(False)`, mise à jour
  `p.mul_(0.999).add_(p_online.detach(), alpha=0.001)` sur paramètres ET
  buffers.
- Perte : Smooth-L1 entre prédicteur(latents online) et latents cible EMA
  (stop-grad) sur positions masquées uniquement.
- **Prétraitement obligatoire** : rendements multi-horizons + winsorisation
  ±5σ AVANT l'encodeur — les prix bruts non stationnaires font diverger l'EMA.

## Pièges PyTorch spécifiques

- **Padding temporel** : sur `(B, T)`, `F.pad(r, (0,0,h,0))` padde la DERNIÈRE
  dimension. Pour le temps : `F.pad(r.unsqueeze(-1), (0,0,h,0)).squeeze(-1)`.
- **Collision d'attributs** : ne jamais nommer un buffer `moyenne` et une
  méthode `moyenne()` — utiliser `moyenne_courante` etc.

## Conformité qualité exigée par l'utilisateur

- PEP 8/484 : ruff 0 erreur, typage complet des signatures (Tensor/Array).
- Docstrings Google Style en FRANÇAIS (objectif, Args, Returns, Raises) :
  pydocstyle --convention=google 0 violation. Docstring `__init__` AVANT
  `super().__init__()`.
- Assertions de forme à l'entrée des blocs critiques (ValueError/TypeError
  ciblés, jamais try-except:pass).
- Vérification ad-hoc : script `/tmp/hermes-verify-*.py` créé, exécuté,
  supprimé — pas de suite verte permanente dans ce workspace.

## Fitness et garde-fous (couche action)

- Fitness arène : `Sortino×2 − MaxDrawdown% + NetProfit%` (Sortino = moyenne
  retours / downside-deviation des retours négatifs).
- Sanitizer : lot = risque%×equity/(distance_SL×contrat), plafonné par marge
  equity×levier/(prix×contrat) ; écrasement consigné.
- Disjoncteur : perte jour (latente+réalisée) ≥ 4 % → ferme tout, suspend
  l'IA, pénalité fitness −1000, journal JSONL, réarmement manuel.

## Liens

- `references/eva-hybrid-architecture.md` : pipeline E.V.A complet, écarts
  assumés, résultats de vérification.
- Skill `rl-trading-debugging` : Patterns #15, #21, #22 (backtest CPU,
  validation multi-critères, GA stratégies-règles).
