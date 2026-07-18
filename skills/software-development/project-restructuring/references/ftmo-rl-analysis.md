# Analyse d'Environnement RL Trading — Cas FTMO Agent

## Contexte

Analyse d'un agent DreamerV3 (15.5M params sur 2 GPUs) entraîné à passer
les challenges FTMO (compte $10K, DD 5%/jour, 10%/total, profit target 10%).

L'agent apprenait systématiquement à **ne rien faire** (action HOLD) —
stratégie optimale dans un environnement où trader = espérance négative.

## Symptômes Observés

```
Logs d'entraînement (ultra3) :
Ep 25   | val=+0.02%  trades=2  ← meilleur score, quasi aléatoire
Ep 400  | val=-0.95%  trades=17 ← l'agent essaie, perd
Ep 1000 | val=+0.00%  trades=0  ← HOLD system, plus jamais de trades
Ep 3000 | val=+0.00%  trades=0  ← convergence vers "ne rien faire"
```

## Analyse des Causes

### 1. Reward Shaping Contradictoire

```
Reward V3 :
  HOLD              → -0.1/bar (pénalité faible)
  Ouvrir un trade   → +0.25 (bonus one-shot)
  Trade gagnant     → PnL × 15 + 1.0 (amplifié)
  Trade perdant     → PnL × 5 (amplifié aussi)

Mais en pratique :
  Espérance(HOLD)   ≈ -0.1/bar → -10 sur 100 bars
  Espérance(TRADE)  ≈ -0.5/trade en moyenne
  → HOLD gagne mathématiquement
```

Le shaping était contradictoire : on forçait à trader (pénalité HOLD)
mais on punissait les pertes 5×. L'arbitrage était toujours en faveur
de l'inaction.

### 2. Spread Fixe Irréaliste

Les spreads étaient statiques dans la config :
```python
XAUUSD: spread=20 points  # Réel: 25-40 pips
EURUSD: spread=12 points  # Correct
```

Sans variation de spread, l'agent apprenait sur un environnement trop
"facile" qui ne généralisait pas au réel.

### 3. Absence de Slippage

Aucun slippage modélisé sur les SL/TP. En réel :
- Slippage sur SL XAUUSD = 5-15 pips
- Pire sur les news (50+ pips)
- FTMO utilise les prix réels du marché

L'agent n'était pas préparé à ces conditions.

### 4. Pas de Commission

Pas de frais de broker ($7/lot standard MT5). Sur 100 trades à 0.5 lot :
- Commission réelle = 100 × 0.5 × $7 = **$350** sur un compte $10K
- Soit 3.5% du compte rien qu'en frais — impossible à ignorer

### 5. Pas de Curriculum Learning

L'agent était jeté directement dans l'environnement réel avec spreads,
slippage, et règles FTMO strictes. Il n'avait aucune phase d'exploration
où trader était "gratuit" pour apprendre.

## Solutions Implémentées (V4)

### Nouvelle Reward : Pure PnL

```python
# V4 — Une seule ligne
reward = (equity - prev_equity) / account_size  # PnL relatif pur
# Pas de pénalité HOLD, pas de bonus trade, pas d'amplification
```

L'agent apprend naturellement : trader = faire gagner ou perdre de l'argent.

### Spread Variable

```python
# V4 — Spread dynamique
base = spec.spread_points_mean * spec.pip_size  # Spread moyen
session_mult = 1.5 if asian_session else 0.8 if london_ny else 1.0
vol_mult = min(3.0, atr / mean_atr)  # Élargi si volatile
spread = base * session_mult * vol_mult * random_noise
```

### Slippage Gaussien

```python
# V4 — Slippage proportionnel
base_slippage = spread_mean * slippage_pct_mean  # ~30% du spread
slippage = abs(gaussian(base_slippage, base_slippage * 0.5))
# Appliqué sur l'entrée, le SL et le TP
```

### Commission MT5

```python
# V4 — $7 par lot standard
commission = spec.commission_per_lot * lots  # $7 × lots
balance -= commission  # Payée immédiatement à l'ouverture
```

### Curriculum Learning (3 Phases)

| Phase | Épisodes | Spread | Slippage | Commission | Max Trades/Jour |
|-------|----------|--------|----------|------------|-----------------|
| 1 | 0-200 | 0% | 0% | 0% | 20 |
| 2 | 200-500 | 30% | 30% | 0% | 12 |
| 3 | 500+ | 100% | 100% | 100% | 8 |

### Autres Ajustements

- **TP/SL** : 1.5/3.0 ATR → 2.0/4.0 ATR (plus de marge)
- **Risque** : 1%/trade → 0.5%/trade
- **Features** : 33/TF → 69/TF (HV10/20/30, slopes, lag, corrélations)
- **Observation** : ajout des corrélations inter-symboles

## Leçons Générales pour les Environnements RL Trading

1. **Vérifier que l'environnement est "solvable"** avant de lancer
   l'entraînement : un agent aléatoire doit pouvoir gagner au moins
   quelques trades. Si l'espérance est négative même sur 10K épisodes,
   le problème est l'environnement, pas l'algorithme.

2. **Ne pas faire confiance au reward shaping.** Plus il y a de
   termes de shaping (pénalités, bonus, coefficients), plus il est
   probable qu'ils créent des artefacts non-désirés. La reward la plus
   robuste est celle qu'on veut optimiser directement (ex: PnL).

3. **Curriculum learning = presque obligatoire** pour les environnements
   financiers complexes. Commencer sans frictions, les ajouter
   progressivement.

4. **Les frictions (spread, slippage, commission) ne sont pas des détails.**
   Elles changent fondamentalement l'espérance mathématique de chaque
   action. Les ignorer = entraîner sur un jeu différent de celui qu'on
   veut résoudre.

## Références

- [DreamerV3 paper](https://arxiv.org/abs/2301.04104) — Mastering Diverse Domains through World Models
- [FTMO Challenge Rules](https://ftmo.com/en/challenge-rules/) — Règles officielles
- Config originale V3 et config V4 dans le projet `ftmo_agent/`