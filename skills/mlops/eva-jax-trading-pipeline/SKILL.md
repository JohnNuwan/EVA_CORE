---
name: eva-jax-trading-pipeline
description: >-
  Pipeline de trading évolutif JEPA (PyTorch) → DLPack → JAX (arène génétique
  TD-MPC2) sur cluster dual-GPU. Pièges validés : mark-to-market barre-à-barre,
  fitness guidée par holdout anti-overfitting, sizing par classe d'actif,
  statiques JAX sous jit, in_axes vmap.
category: mlops
---

# Pipeline JEPA→JAX de Trading Évolutif (E.V.A)

Architecture validée sur The Hive (2× RTX 3090) : encodeur JEPA temporel
auto-supervisé (PyTorch, GPU 0) → pont DLPack zéro-copie → moteur JAX (GPU 1) :
planificateur TD-MPC2 (CEM 5 000 trajectoires) + arène génétique 64 agents
sous `jax.vmap`/`jax.jit`. Projet de référence : `~/jepa_eva`
(github.com/JohnNuwan/jepa_eva).

## Chaîne complète

1. `train_jepa.py` : pré-entraîner l'encodeur JEPA (perte 0.129→0.0087 sur
   XAUUSD M15). Vérifier latents cohérents (cos fenêtres adjacentes > 0.9,
   std > 0.05 = pas de collapse EMA).
2. `precompute_latents.py` : latents de tout l'historique (50 000×128). Le
   chunk est borné par le position embedding (512) — jamais au-delà.
3. `train_arena_generalisee.py` : arène guidée par holdout (recommandé).
4. `backtest_validation.py` / `evaluer_multi_symbole.py` : validation holdout
   et cross-symboles.
5. `train_world_model.py` : GRU supervisé transitions H_t→H_{t+1} pour CEM.

## Pièges critiques validés (2026-07-19)

### P1 — Backtest : composition du drift = artefact de levier infini
Retour calculé depuis le prix d'entrée (`position × (prix/prix_entree − 1)`)
avec position maintenue → drift composé sans borne → +3308 % sur 512 barres,
sortino 13 829. **Solution** : mark-to-market barre-à-barre. Retour du pas =
`position × (prix_t − prix_{t−1}) / prix_{t−1}` ; `prix_entree` réassigné au
prix courant à CHAQUE pas (jamais figé). Initialiser `prix_entree=prix_seq[0]`.
**Test de capacité** : sur drift +30 % monotonique, net_profit doit rester
<< 100 %.

### P2 — Sélection sur fitness train → dérive surapprentissage
Sélectionner les parents sur fitness train seule → 1/40 champion qui
généralise, dérive après ~50 gens (holdout −13 %). **Solution** : score
d'évolution = `fitness_train + λ × fitness_holdout` (λ=1.0, holdout rafraîchi
sur toute la population toutes les 5 gens) + promotion conditionnelle
(sauvegarder le champion QUE si net_profit > 0 ET dd ≤ 5 % au holdout) +
sauvegarde des POIDS (npz) pas juste des métriques. **Piège clé** : le
meilleur champion holdout avait fitness_train faible (0.545) — la sélection
train seule l'aurait raté. Résultat : champion robuste 8/8 symboles.

### P3 — Sizing : calibration taille_contrat par classe d'actif
`taille_contrat=100_000` (forex) sur XAUUSD → risque 1000× surestimé → tous
les lots à 0. **Calibrer** : métaux spot 100 oz, forex 100 000, indices cash
selon broker, crypto 1. `lot_max = (risque% × equity)/(distance_SL ×
taille_contrat)`. **Ne JAMAIS appliquer lot_min avant le plafond de risque** —
si lot_max < lot_min, REFUSER l'ordre. Fraction de risque = `|signal|` pour
actions CEM dans [-1,1] (sinon signaux négatifs → fraction 0).

### P3b — Stop loss basé ATR, jamais fixe (validé par l'utilisateur)
Un SL fixe (ex. 5$ sur XAUUSD M15) est trop serré : le bruit stoppe prématurément
ET le lot devient artificiellement gros (`lot = risque/(SL×contrat)` → 2.0 lots).
**Solution** : `SL = 2 × ATR(14)` (volatilité réelle). Résultat : lots ~0.5-0.9
(raisonnables), SL ~16-33$ (non étouffé), risque 1% toujours exact. L'ATR doit
être recalculé à chaque tick sur la fenêtre courante. L'utilisateur surveille le
réalisme des lots — toujours vérifier le sizing sur la classe d'actif réelle.

### P8 — Connecteur broker : interface abstraite + stub pour tests sans infra
Avant le live, définir `ConnecteurBroker` abstrait (connecter, tick_courant,
envoyer_ordre, fermer_position, equity, positions_ouvertes) implémenté par :
`ConnecteurStub` (broker simulé en mémoire : slippage ask/bid, P&L, positions —
testé) et `ConnecteurMT5` (squelette ZMQ/EA pour VM Windows KVM, lève
NotImplementedError tant que l'ISO n'est pas là). Cela découple l'orchestrateur
du broker et permet des tests end-to-end complets sans VM. Branchement MT5 :
VM Windows 11 KVM → MT5 + EA ZMQ/JSON → ConnecteurMT5.

### P4 — JAX sous jit : statiques pour slices et dimensions
`jnp.arange(horizon)`, `argsort()[-nb_elites:]`, `jnp.split` échouent sous
jit si les tailles sont tracées. **Solution** : capturer `horizon`, `gamma`,
`nb_elites` en closure statique OU `static_argnums`. Erreur typique :
"ConcretizationTypeError: Abstract tracer" / "Slice entries must be static".

### P5 — vmap : in_axes doit correspondre aux args positionnels
`vmap(f, in_axes=(0, None, None))` sur une fonction à 2 args →
"len(in_axes)=3, len(args)=2". **Solution** : closure à 2 args avec tuple de
données `(prix, latents)`, `in_axes=(0, None)`.

### P6 — torch.nn.functional.pad sur tenseur 2D
`pad(x, (0,0,h,0))` sur `(B,T)` padde la dernière dim, pas la temporelle →
"stack expects each tensor to be equal size". **Solution** :
`pad(x.unsqueeze(-1), (0,0,h,0)).squeeze(-1)`.

### P7 — except : ordre des sous-classes
`torch.cuda.OutOfMemoryError` hérite de `RuntimeError` — le placer APRÈS
rend la clause inaccessible (Pyright reportUnusedExcept). Toujours la
sous-classe d'abord.

## CEM TD-MPC2 — perf validée (RTX 3090)
CEM 5 000 traj × 6 iters ≈ 7 ms ; arène 64 agents (512 pas) ≈ 54 ms ;
évolution génétique ≈ 2 ms. Le premier appel jit inclut la compilation XLA
(~2 s) — mesurer après warmup. CEM de planification vectorisé = GPU-friendly
(contrairement au backtest bar-par-barre, cf. Pattern #22 rl-trading-debugging).

## Workflow git propre
Dépôt isolé par pipeline (jepa_eva séparé de ftmo_agent). Pousser via
credential helper `store` + `~/.git-credentials` (chmod 600) — jamais de
token dans l'URL remote en clair (bloqué par le scanner, et fuite).
Commits en français, artefacts lourds régénérables (champions, checkpoints)
dans .gitignore.

## Skills liés
- `rl-trading-debugging` : 22 patterns RL/ES/GA pour trading (EVO-ARENA GA-règles).
- `references/eva-arena-jax-architecture.md` : détails session, commandes,
  benchmarks et fichiers du pipeline E.V.A.
