# E.V.A — Détails de session et extraits d'implémentation validés

Détails spécifiques à la session 2026-07-19 : construction de
`~/ftmo_agent/jax_arena.py` et du package `~/ftmo_agent/eva/`.
À lire quand on reprend ou étend ce pipeline.

## Transcription des erreurs JAX rencontrées (et leur fix exact)

### Erreur 1 — ConcretizationTypeError
```
jax.errors.ConcretizationTypeError: Abstract tracer value encountered
where concrete value is expected: traced array with shape int32[]
It arose in the jnp.arange argument 'stop'
```
Cause : `horizon` passé en argument de `_simuler_trajectoire` tracée par
jit. Fix : closure statique —
```python
horizon_s, gamma_s = self.horizon, self.gamma
def simuler_statique(p, latent, actions):
    return _simuler_trajectoire(p, latent, actions, horizon_s, gamma_s)
self._simuler_batch = jax.jit(jax.vmap(simuler_statique, in_axes=(None, None, 0)))
```

### Erreur 2 — IndexError slicing dynamique
```
IndexError: Slice entries must be static integers.
Got slice(JitTracer(~int32[]), None, None) at position 0
```
Cause : `jnp.argsort(fitness)[-nb_elites:]` avec `nb_elites` tracé dans
`_evoluer_jit`. Fix :
```python
@partial(jax.jit, static_argnums=(0, 4, 5, 6))  # self, nb_elites, taux, sigma
```
Attention au décalage d'indices : self compte comme arg 0 — nb_elites est
le paramètre 4 (pas 3) après self, population, fitness, cle.

### Erreur 3 — vmap arity
```
ValueError: vmap in_axes ... got len(in_axes)=3, len(args)=2
```
Fix : regrouper les données marché en tuple-arg —
```python
jax.vmap(evaluer_un_agent, in_axes=(0, None))
# appel : fn(population, (prix, latents))
```

## Configuration matérielle validée (The Hive)

- jax 0.11.0 (jax-cuda12-plugin) — `jax.devices()` = [cuda:0, cuda:1].
- torch 2.6.0+cu124 — SDPA/FlashAttention-2 actif
  (`torch.backends.cuda.flash_sdp_enabled() == True`).
- JAX voit les 2 GPUs ; PyTorch encodeur sur cuda:0, core JAX sur cuda:1
  via `jax.device_put(arr, gpus[-1])`.
- Python 3.13.5, venv `~/ftmo_agent/venv`. PYTHONPATH=. requis pour
  importer `eva` / `jax_arena` depuis le repo.

## Vérification ad-hoc (méthode)

Pas de suite pytest canonique dans le repo — les contrôles sont des
scripts temporaires `/tmp/hermes-verify-*.py` (créés, exécutés, résumés
comme "vérification ad-hoc", jamais présentés comme suite verte) +
scripts permanents rejouables `~/ftmo_agent/tests/test_bloc_{a,b,c}.py`
et `test_integration_gpu.py`. Linters : `ruff check` + `pydocstyle
--convention=google` (installés dans le venv).

## Formule fitness exacte (spec)

```python
sortino = mean(retours) / sqrt(mean(min(retours, 0)**2) + 1e-12)
max_dd_pct = (equity_peak - equity_final) / equity_peak * 100
net_profit = (equity_final - capital_initial) / capital_initial * 100
fitness = sortino * 2.0 - max_dd_pct + net_profit
```
Vérifié numériquement : `allclose(fitness, sortino*2 - dd + profit, atol=1e-4)`.

## Évolution génétique jittée (pattern)

```python
idx = jnp.argsort(fitness)[-nb_elites:]
elites = jax.tree.map(lambda p: p[idx], population)
# crossover arithmétique/géométrique signée : jnp.where(masque, sign(a)*sqrt(|a*b|), (a+b)/2)
# mutation : f + bernoulli(c, taux) * normal(c) * sigma  (par feuille, clés splittées)
enfants = jax.vmap(crossover)(parents_a, parents_b, cles)
enfants = jax.vmap(mutation)(enfants, cles_m)
population = jax.tree.map(lambda e, n: jnp.concatenate([e, n]), elites, enfants)
```
Anti-consanguinité : `mean(var(poids_aplatis, axis=0))` < seuil → bruit
multiplicatif `p * (1 + normal * 1.5)`.
