# E.V.A — Architecture hybride PyTorch + JAX pour trading RL

Architecture validée sur The Hive (2× RTX 3090, torch 2.6+cu124, jax 0.11.0,
session 2026-07-19). Code : `~/ftmo_agent/eva/`.

## Pipeline

```
OHLCV brut (B, T, 5)
  → DynamicNormalizer : rendements multi-horizons [1,2,5,15,30,60],
    ranges intrabarre relatifs, FFT (composantes cycliques), RunningLayerNorm
    (stats cumulatives momentum 0.01 + winsorisation ±5σ anti-spikes macro)
  → (B, T, 27) features stationnaires
  → TimeJEPAEncoder : Transformer 1D pré-norm (4 têtes, 3 couches, SDPA
    = FlashAttention-2 auto sur Ampere+), latent H=128, masquage de bloc
    futur 20% + prédicteur + cible EMA 0.999 (anti-collapse), perte Smooth-L1
  → (B, 128) latents sur GPU 0
  → JAXTransitionBridge : jax.dlpack.from_dlpack + device_put → GPU 1
  → TDMPC2Planner : world model GRU (H_t → H_{t+1} sous action A_t),
    CEM : 5000 trajectoires × horizon 5 en vmap, élites → distribution
    gaussienne → première action de la meilleure séquence
  → JaxGeneticArena : 64 agents vmap, fitness = Sortino×2 − MaxDD% + NetProfit,
    crossover arithmétique/géométrique + mutation gaussienne adaptive +
    anti-consanguinité (variance inter-poids < seuil → bruit multiplicatif)
  → ActionSanitizer : lot écrasé si risque > 1% equity (sizing par SL,
    plafond marge equity×levier/(prix×contrat))
  → DrawdownDisconnecter : perte jour ≥ 4% → ferme tout, suspend l'IA,
    pénalité fitness −1000, journal JSONL, réarmement manuel uniquement
```

## Points critiques d'implémentation

### RunningLayerNorm (anti-saturation)
Buffers `moyenne_courante`/`variance_courante` mis à jour en `train()` par
moyenne mobile cumulée, puis winsorisation `clamp(z, ±clip_std)` AVANT les
paramètres affines. Ne jamais nommer un buffer `moyenne`/`variance` et une
méthode du même nom — collision d'attributs silencieuse.

### Rendements multi-horizons (piège de padding)
Sur un tenseur 2D `(B, T)`, `F.pad(r, (0, 0, h, 0))` padde la DERNIÈRE
dimension. Pour padder le temps en tête :
`F.pad(r.unsqueeze(-1), (0, 0, h, 0)).squeeze(-1)`.

### EMA JEPA
`p_cible.mul_(momentum).add_(p_online.detach(), alpha=1-momentum)` sur les
paramètres, `copy_` sur les buffers. Cible = `copy.deepcopy` + `requires_grad_(False)`.
Perte : Smooth-L1 entre prédicteur(latents online contexte) et
latents cible EMA (stop-grad) sur les positions masquées uniquement.

### JAX sous jit/vmap (détaillé dans SKILL.md)
- Hyperparamètres structurels → closure statique, jamais arguments tracés.
- Population = Pytree à axe population en tête, pas liste.
- Code agent-individuel en 1D, vmap ajoute l'axe 0.
- CEM : boucle Python sur itérations avec `jax.random.split`, corps jitté.

### Conformité qualité exigée par l'utilisateur
- PEP 8/484 : ruff 0 erreur, typage complet (signatures + Tensor/Array).
- Docstrings Google Style en FRANÇAIS : objectif algorithmique, Args, Returns,
  Raises — pydocstyle --convention=google : 0 violation. Docstring
  `__init__` placée AVANT `super().__init__()`.
- Assertions de forme à l'entrée des blocs critiques (JEPA forward, pont
  DLPack, planner) : ValueError/TypeError ciblés, jamais try-except:pass.
- Vérification ad-hoc : script /tmp/hermes-verify-*.py créé, exécuté
  (13/13 contrôles), supprimé — pas de suite verte permanente.

## Écart assumé
Dans l'arène, le signal de trading par agent est dérivé de la valeur prédite
par le GRU (tanh) plutôt que d'un CEM complet par agent par pas — reste pur
JAX/jittable. CEM complet par agent = double vmap (pop × trajectoires), à
refactorer si besoin.

## Résultats de vérification (session 2026-07-19)
- Bloc A : RunningLayerNorm écrête ±5σ, DynamicNormalizer (B,T,27), JEPA
  latent (B,T,128), EMA fonctionnel — OK.
- Bloc B : pont DLPack CPU→cuda:1 et cuda:0→cuda:1, CEM 256→512 traj, arène
  8 agents évolutive — OK.
- Bloc C : sanitizer écrase lot 100→0.01 si SL serré, disjoncteur saute ≥4 %
  et suspend les ordres — OK.
- Intégration : OHLCV→features (4,100,27)→latents (4,100,128) GPU0→DLPack→
  JAX GPU1→CEM→action→ordre validé — OK. ruff 0 erreur, pydocstyle 0 violation.

## Liens
- Skill parent : `hybrid-pytorch-jax-trading`.
- Skills liés (bundled, non modifiables) : `rl-trading-debugging` (Patterns
  #15, #21, #22), `jepa-self-supervised-learning`.
