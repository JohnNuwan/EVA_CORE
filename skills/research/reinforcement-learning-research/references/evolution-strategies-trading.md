# Evolution Strategies pour Trading — Architecture & Patterns

## Pourquoi ES plutôt que DreamerV3/PPO

L'ES contourne les problèmes fondamentaux qui font échouer DreamerV3 et PPO
sur les environnements de trading :

| Problème | DreamerV3 | PPO | ES |
|----------|-----------|-----|-----|
| Value function collapse | Oui (reward_head → moyenne) | Oui (critic → constant) | **Pas de value function** |
| RSSM ignore observations | Oui (KL→0) | N/A | N/A |
| Reward shaping sensible | Oui | Oui | **PnL pur comme fitness** |
| Exploration | Epsilon-greedy 20% | Epsilon-greedy | **Population naturelle** |
| Parallélisation | Limitée (1 env) | 8 envs | **N agents × M envs** |

## Architecture

```
ESPolicy (LSTM 2×128, 369K params):
  obs (B, 48, 296) → LSTM → hidden (128) → Linear(128, 128) → Linear(128, 8)
  
Population: N agents (8-16 recommandé)
Mutation: bruit gaussien σ=0.02-0.03 sur tous les poids
Sélection: top 25% (elite_frac=0.25), moyenne pondérée par fitness
LR d'évolution: 0.01-0.02 (pas le LR SGD, le taux d'apprentissage évolutif)
```

## Hyperparamètres optimaux

```python
ESAgent(
    input_dim=296,      # n_features de l'environnement
    hidden_dim=128,     # LSTM 2 couches
    action_dim=8,       # HOLD/BUY/SELL/CLOSE/SPLIT_*
    pop_size=8,         # 8-16 selon GPU dispo
    sigma=0.03,         # Écart-type de la mutation gaussienne
    lr=0.02,            # Taux d'apprentissage évolutif
    elite_frac=0.25,    # Top 25% sélectionnés
)
```

## Fitness = PnL pur

**CRITIQUE :** La fitness doit être le PnL pur, PAS le reward total
(incluant le reward shaping). Sinon l'agent optimise le reward shaping
plutôt que l'argent.

```python
def evaluate_single(policy, env, steps=1000) -> float:
    obs = env.reset()
    for _ in range(steps):
        action = policy.sample(obs, mask, deterministic=False)
        obs, _, done, _ = env.step(action)
        if done: break
    return (env.balance - account_size) / account_size * 100  # PnL%
```

## Diagnostics du test synthétique

Le test synthétique `TrendingEnv` (prix +0.1%/step, 4 actions) a révélé :

### Ce qui NE MARCHE PAS
- **PnL différé (reward au CLOSE seulement)** : 0 trades, ES et PPO échouent
- **PnL non-réalisé visible dans l'obs** : 0 trades, toujours pas de signal
- **Sans auto-close** : l'agent n'apprend jamais à fermer ses positions

### Ce qui MARCHE
- **Reward dense (delta PnL/step) + auto-close à 50 steps** : l'agent apprend BUY
- Le passage de -8% à +17% PnL en 20 générations ES confirme que l'algo fonctionne

### Leçon clé : credit assignment temporel
BUY→HOLD→CLOSE est une chaîne de 3 actions séparées par des dizaines de steps.
La probabilité d'exécuter toute la chaîne aléatoirement est ~0.5%.
**Sans reward intermédiaire visible, l'agent ne découvre jamais le lien causal.**

## Exploration : epsilon-greedy 30%

30% d'exploration aléatoire pendant l'évaluation. Sans ça, la population
converge trop vite vers HOLD (PnL=0% garanti vs trades risqués).

```python
if np.random.random() < 0.3:  # 30% exploration
    action = np.random.choice(valid_actions)
else:
    action = policy.argmax(obs, mask)
```

## Conditions nécessaires au succès

Pour que le RL fonctionne en trading :
1. **Reward dense à chaque step** — delta du PnL non-réalisé (pas juste au CLOSE)
2. **Auto-close** — mécanisme qui force la réalisation des gains après N steps
3. **Features explicites** — PnL latent, direction de la position dans l'observation
4. **Exploration ≥ 30%** — pour que l'agent découvre la chaîne BUY→HOLD→CLOSE

Sans ces 4 conditions, **aucun algorithme RL** (DreamerV3, PPO, ES, SAC) n'apprendra
à trader, quel que soit le nombre de paramètres ou de GPUs.

## Performance

- **8 agents × 1000 steps** : ~27 secondes par génération
- **500 générations** : ~3.7 heures
- **GPU** : cuda:0 pour l'inférence (pas de backprop → très léger)
- **Mémoire** : ~500 MB pour 8 agents (les poids sont clonés)

## Pitfalls

1. **Fitness = reward total (PAS PnL)** → l'agent maximise le reward shaping
2. **Epsilon trop faible (< 20%)** → population converge sur HOLD en < 5 générations
3. **Sigma trop élevé (> 0.05)** → la population diverge, pas d'apprentissage
4. **Reward non-dense (seulement au CLOSE)** → credit assignment impossible
5. **Pas d'auto-close** → l'agent ne réalise jamais les gains
6. **État LSTM non réinitialisé entre évaluations** → contamination inter-épisodes
