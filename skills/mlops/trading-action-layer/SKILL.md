---
name: trading-action-layer
description: >-
  Couche d'action déterministe et garde-fous de production pour le trading
  algorithmique — sizing par le risque (1 %/trade), calibration des contrats
  par classe d'actif, disjoncteur drawdown dur (4 %/jour), et pièges de
  traçage statique JAX (jit/vmap) pour le moteur décisionnel.
category: mlops
---

# Couche d'Action & Garde-fous de Production (Trading)

## Présentation

Ce skill couvre la couche finale, déterministe et non soumise à l'IA, entre
la sortie d'un moteur décisionnel (CEM, ES, GA) et l'envoi d'un ordre réel :
le sizing par le risque, la calibration des contrats, le disjoncteur dur, et
les pièges JAX du moteur. Complète `rl-trading-debugging` (qui couvre
l'entraînement RL/ES, pas la couche d'exécution production).

## Sizing par le risque (1 %/trade) — leçons validées en exécution

1. **fraction = |signal|, pas clip(signal)** — un planificateur CEM non
   entraîné sort des actions dans [-1, 1] avec signes aléatoires.
   `clip(signal, 0, 1)` met ~50 % des signaux à 0 → lots nuls. La
   **magnitude** porte la conviction : `fraction = clip(abs(signal), 0, 1)`.

2. **lot_souhaite = lot_max_risque × fraction**, JAMAIS
   `borne_lot_max × fraction` — sinon le lot n'est pas ancré au risque réel.

3. **Refus si lot_max_risque < lot_min** — un stop très serré peut rendre le
   lot max < lot_min. Ne PAS forcer lot_min (le risque dépasserait le seuil) :
   REFUSER l'ordre. Le respect du risque prime sur la taille minimale.

4. **Test d'or du sizer** : `perte_au_SL = lot × taille_contrat ×
   distance_SL` doit être ≈ risque_cible (1 % equity). Vérifier en exécution
   réelle, pas seulement en théorie.

## Calibration `taille_contrat` par classe d'actif

**Bug silencieux critique** : `taille_contrat` forex (100 000) appliqué à
XAUUSD (100 oz) → risque surestimé ×1000 → tous les lots à 0.00.

Calibration correcte :
- Forex (EURUSD, GBPUSD) : `100 000`
- Métaux au comptant (XAUUSD) : `100` (oz)
- Indices au comptant (US30, US500) : souvent `1`
- Crypto (BTCUSD) : `1`

**Règle** : la taille de contrat fait partie de la spec symbole (comme le
spread ou le levier). La sortir d'un dictionnaire par symbole
(`SPECS[symbol]['contract']`), JAMAIS une constante globale unique. Logger
`lot_max_autorise` : s'il est systématiquement < lot_min sur un SL
raisonnable, le contrat est faux.

## Disjoncteur drawdown dur (garde-fou hors IA)

- Seuil 4 %/jour, perte latente + réalisée cumulée.
- Coupure de TOUTES les positions + suspension des ordres jusqu'à
  réarmement manuel (opération humaine, hors portée de l'IA).
- Journal JSONL des événements + pénalité fitness maximale pour la lignée
  fautive.
- Vérifié AVANT tout calcul de signal dans la boucle d'orchestration.
- Rollover automatique des compteurs au changement de jour.

## Pièges de traçage statique JAX (jit/vmap)

Trois erreurs récurrentes — valeurs qui DOIVENT être statiques mais tracées :

1. **`jnp.arange(n)` / shapes dynamiques** — `n` doit être un entier Python
   statique. Erreur : `ConcretizationTypeError: traced array int32[]`.
   Fix : capturer `n` en closure, ou `static_argnums`.

2. **Slicing avec borne tracée** — `x[-k:]` avec `k` tracé. Erreur :
   `IndexError: Slice entries must be static integers`. Fix : `static_argnums`.

3. **`in_axes` de vmap ≠ nb d'arguments** — `in_axes=(0, None, None)` sur
   fonction à 2 args. Erreur : `ValueError: len(in_axes)=3, len(args)=2`.
   Fix : regrouper les args non-mappés en tuple/closure.

**Règle générale** : tout ce qui pilote une structure de contrôle Python
(bornes de slice, tailles de tableaux, compteurs `range`) ou une forme de
tenseur doit être statique sous jit. Tout ce qui est donnée (tenseurs, clés
PRNG) peut être tracé.

## Benchmarks validés (RTX 3090, jax 0.11, TD-MPC2 + arène 64 agents)

- Pont DLPack PyTorch→JAX : 0.34 ms
- CEM 5 000 trajectoires : 7.4 ms
- Arène 64 agents (512 pas de marché) : 54 ms
- Évolution génétique jittée : 1.8 ms

## Validation sur données réelles

Le pipeline complet (JEPA → DLPack → CEM → arène) a été validé sur données
MT5 réelles (XAUUSD M15, 50k barres) : perte JEPA auto-supervisée qui
diminue (0.16 → 0.10 en 30 steps), latents sans collapse, fitness d'arène
finie. Format CSV MT5 : `time,open,high,low,close,tick_volume,spread,
real_volume` — OHLCV = colonnes open/high/low/close/tick_volume.

## Skills liés

- `rl-trading-debugging` : entraînement RL/ES/GA (amont de cette couche).
- `scripts/verify-sizer.py` : vérification réutilisable de la calibration
  du sizer (perte au SL ≈ risque cible par classe d'actif).
