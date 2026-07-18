# Architecture The Hive — Référence d'implémentation supérieure

> Source : github.com/JohnNuwan/The_Hive (main branch, Mars 2026)
> Récupéré via curl sur raw.githubusercontent.com — session du 17/07/2026

## Contexte

The Hive est le projet "parent" de l'utilisateur. Architecture MoE (Mixture of
Experts) avec 12+ modules spécialisés. Le module `eva-lab` contient le pipeline
d'entraînement RL (MuZero + DreamerV3) et l'`eva-banker` gère l'exécution live.

**État au 08/03/2026** (ROADMAP) : "live gelé sans champion valide,
entraînement massif priorisé." The Hive a le MÊME problème que ftmo_agent :
aucun modèle rentable. La différence est que l'architecture de validation et
de promotion est déjà en place.

## 1. Arena Darwinienne (`eva_lab/arena.py`)

L'Arena évalue les modèles sur historique réel avec des métriques multi-critères,
pas seulement le PnL.

### Métriques trackées (POSITION_MECHANICS_KEYS)

```python
POSITION_MECHANICS_KEYS = (
    "split_efficiency",
    "pyramid_efficiency",
    "slbe_capture_rate",
    "hold_drag_score",
    "close_quality_score",
    "pyramids_opened",
    "pyramids_rejected",
    "slbe_triggered",
    "slbe_hit",
    "split_executed",
    "close_winner_count",
    "close_loser_count",
    "hold_streak_mean",
    "hold_under_trend_penalty_count",
    "tp_like_exit_count",
    "entry_blocked_vwap",
    "entry_blocked_adx",
    "entry_blocked_obv",
    "actions_above_vwap",
    "actions_below_vwap",
    "actions_low_adx",
    "obv_divergent_actions",
    "hold_in_trend_count",
    "hold_in_range_count",
    "split_rejected",
    "split_rejected_no_value",
    "inactive_episode_penalties",
    "insufficient_entry_penalties",
    "directional_imbalance_penalties",
    "realized_close_bonus_count",
    "realized_split_bonus_count",
    "slbe_exit_bonus_count",
)
```

### Métriques de performance (_empty_metrics baseline)

```python
{
    "profit_factor": 0.0,      # gross_profit / gross_loss
    "return_pct": 0.0,         # rendement total
    "net_realized_pct": 0.0,   # PnL réalisé net
    "gross_profit_pct": 0.0,
    "gross_loss_pct": 0.0,
    "win_rate": 0.0,           # % de trades gagnants
    "total_trades": 0,
}
```

### Leçon clé pour ftmo_agent

ftmo_agent valide sur PnL seul (`val_pnl > best_val_pnl`). L'Arena track
profit_factor, win_rate, position mechanics. Un modèle avec PnL > 0 mais
win_rate < 50% et profit_factor < 1.5 ne devrait PAS être promu champion.

## 2. Champion Promoter (`eva_lab/champion_promoter.py`)

### Politique de sélection live

```python
allowed = {"champion_only", "champion_then_latest", "checkpoint_preview"}
# Default: "champion_only" — seul un champion validé peut trader live
```

### Critères de promotion (ROADMAP)

Un champion doit valider :
- `win_rate` > seuil
- `profit_factor` > seuil
- `drawdown` < limite
- `expectancy` > seuil
- `sample_size` > minimum

### Leçon clé

ftmo_agent sauvegarde `best.pt` si `val_pnl > best_val_pnl`. C'est insuffisant :
un coup de chance sur un petit échantillon peut produire un PnL positif.
Il faut valider sur N trades minimum + profit_factor + win_rate.

## 3. Genetic Registry (`eva_lab/genetic_updater.py`)

### Registre ADN multi-horizon

```python
HORIZONS = ["scalp", "intraday", "swing"]

# Structure du registre
{
    "version": "2.1-MTF",
    "current_champion": "gen_042_intraday",
    "champions": {
        "scalp": "gen_038_scalp",
        "intraday": "gen_042_intraday",
        "swing": "gen_015_swing",
    },
    "generations": {
        "gen_000_baseline": {
            "win_rate": {"scalp": 50.0, "intraday": 50.0, "swing": 50.0},
            "return_pct": {"scalp": 0.0, "intraday": 0.0, "swing": 0.0},
            "battles_won": {"scalp": 0, "intraday": 0, "swing": 0},
            "horizon_accuracy": {"scalp": 0.33, "intraday": 0.33, "swing": 0.33},
        },
        # ... chaque génération est tracée
    },
}
```

### Leçon clé

ftmo_agent écrase `best.pt` à chaque amélioration. Pas d'historique des
générations. Le genetic registry permet de :
- Comparer des générations entre elles
- Faire un rollback si une génération régresse
- Tracker l'évolution ADN (quels hyperparams ont marché)

## 4. Multi-Horizon (`eva_lab/muzero/config.py`)

```python
class MuZeroConfigV3:
    def __init__(self, **overrides):
        self.horizon = overrides.get("horizon") or os.getenv("MUZERO_HORIZON", "intraday")
        self.primary_timeframe = get_horizon_timeframe(self.horizon)
        # scalp → M5, intraday → M15, swing → H1
        self.history_bars = get_horizon_history_bars(self.horizon, fallback=4000)
        self.symbols = resolve_training_symbols(...)
        self.feature_profile = resolve_feature_profile(self.horizon, self.model_family)
```

### Configs par horizon

| Horizon | Timeframe | History bars | Features |
|---------|-----------|-------------|----------|
| scalp | M5 | 4000 | profil scalp (plus court terme) |
| intraday | M15 | 4000 | profil intraday |
| swing | H1 | 4000 | profil swing (plus long terme) |

### Leçon clé

ftmo_agent utilise un seul horizon (M15, 1000 steps). The Hive entraîne des
modèles séparés par horizon. Un modèle scalp n'a pas les mêmes features ni
le même reward shaping qu'un modèle swing.

## 5. Espace d'actions réduit (5 au lieu de 8)

```python
# The Hive (eva_lab/muzero/environment.py)
HOLD = 0
BUY = 1
SELL = 2
SPLIT = 3    # entrée fractionnée (risk management)
CLOSE = 4
ACTION_NAMES = ["HOLD", "BUY", "SELL", "SPLIT", "CLOSE"]
```

ftmo_agent utilise 8 actions : HOLD, BUY, SELL, CLOSE, SPLIT_BUY, SPLIT_SELL,
PYRAMID, PARTIAL_CLOSE. Les actions PYRAMID et PARTIAL_CLOSE sont des
distractions qui augmentent l'espace d'exploration sans bénéfice prouvé.

## 6. Reward Shaping avancé (MuZeroConfigV3)

```python
# Bonus
self.quality_trade_bonus = 10.0           # trade de qualité (bon timing)
self.final_growth_bonus = 50.0            # croissance finale > 10%
self.final_growth_threshold = 0.10
self.slbe_activation_bonus = 6.0          # SLBE activé = bon risk management
self.split_with_profit_bonus = 10.0       # split en profit = bon scaling
self.close_big_winner_bonus = 15.0        # fermer un gros gagnant

# Pénalités
self.drawdown_time_penalty_rate = 0.2     # pénalité par step en drawdown
self.max_drawdown_penalty = 10.0
self.loss_penalty_multiplier = 2.0        # pertes pénalisées ×2
```

### Leçon clé

ftmo_agent utilise un reward shaping basique (equity_change × pnl_scale +
time_decay + holding_bonus). The Hive reward les COMPORTEMENTS de qualité
(SLBE, split, close timing) pas seulement le PnL.

## 7. Risk Manager (`eva_banker/services/risk.py`)

### Garde-fous (Constitution Loi 2)

```python
RiskValidator(
    max_risk_per_trade=1.0,        # 1% max par trade
    max_daily_drawdown=4.0,        # 4% DD journalier (FTMO = 5%)
    max_total_drawdown=8.0,        # 8% DD total (FTMO = 10%)
    max_open_positions=3,
    anti_tilt_losses=2,            # 2 pertes consécutives → pause
    anti_tilt_hours=24,            # pause de 24h
)
```

### Checks de validation

1. SL obligatoire (pas de trade sans stop-loss)
2. Session de marché ouverte (pas de week-end/rollover)
3. Risque par trade < max
4. Anti-tilt (pas de trading après N pertes)
5. DD journalier < limite
6. DD total < limite
7. Nombre de positions < max
8. VaR < seuil (calculate_var sur historique de returns)

### Leçon clé

ftmo_agent n'a pas de risk manager au niveau exécution. L'environnement
vérifie les DD limits mais il n'y a pas de validation d'ordre avant exécution
live. Le RiskValidator de The Hive est une couche critique pour le trading réel.

## 8. Architecture MoE — Modules pertinents

| Module | Rôle | Pertinence pour ftmo_agent |
|--------|------|---------------------------|
| `eva-banker` | Trading + risque | Risk manager + MT5 hybride |
| `eva-lab` | Entraînement RL | Arena + champion + genetic |
| `eva-quant-lab` | Calculs Julia | Monte Carlo, portfolio opt |
| `eva-nervous` | gRPC router | Communication inter-modules |
| `eva-core` | Orchestrateur LLM | NLU + routage d'intention |

## 9. Plan d'intégration ftmo_agent → The Hive

### Priorité 1 : Corriger Pattern #14 (bias asymétrique)
- Sans modèle rentable, le reste est inutile
- Injecter un signal de direction basé sur EMA slope / momentum

### Priorité 2 : Intégrer l'Arena
- Remplacer `val_pnl > best_val_pnl` par validation multi-critères
- Ajouter profit_factor, win_rate, expectancy, sample_size
- Implémenter le genetic registry

### Priorité 3 : Connecter au live
- Adapter le RiskValidator de The Hive
- MT5 hybride (local/serveur) pour FTMO/FTUK/Fundnext
- DreamerGate pour inference-only vs training
