# DreamerV3 — Verdict final après diagnostic exhaustif

## Résumé

Après 10+ itérations de correctifs (V4→V4.3→V5) sur un agent de trading FTMO
à 8 actions, **DreamerV3 ne parvient pas à produire une politique qui trade.**
L'agent converge systématiquement vers HOLD (action 0) avec entropie ≈ 1.38 nat
et 0 trades en validation, quel que soit le reward shaping.

## Correctifs testés (tous en échec)

| # | Correctif | Résultat |
|---|-----------|----------|
| 1 | Dense rewards (100% steps non-nuls) | ❌ WM collapse |
| 2 | Weighted MSE reward loss | ❌ WM collapse |
| 3 | Stratified sampling 50/50 HOLD/trades | ❌ WM collapse |
| 4 | Prior+posterior reward loss | ❌ WM collapse |
| 5 | Warm-up RSSM 80 épisodes | ❌ Pas d'amélioration |
| 6 | KL weight ×20 pendant warm-up | ❌ Pas d'amélioration |
| 7 | AC gelé pendant warm-up | ❌ Pas d'amélioration |
| 8 | Reward_head 3×2048 sur GPU1 | ❌ WM collapse |
| 9 | Action explicite en input reward_head | ❌ WM collapse |
| 10 | Horizon 15 + 16 AC steps/ep | ❌ entropie descend puis remonte |

## Cause racine

Le **RSSM ignore les observations** (KL converge vers 0 en ~20 épisodes).
Sans info observationnelle dans l'état latent, le reward_head ne peut
pas distinguer les états rentables des états perdants. Il prédit la
moyenne des rewards (~0.04 en symlog) pour tous les états.

L'avantage imaginaire est nul → l'AC n'apprend rien → la politique
reste uniforme ou converge vers HOLD.

## Test synthétique — diagnostic de capacité

Pour isoler le problème (features vs RL), un environnement synthétique
`TrendingEnv` a été créé :
- Prix monte de +0.1% par step avec bruit
- Action space = {HOLD, BUY, SELL, CLOSE}
- L'action optimale est BUY → CLOSE

**Résultats :**
- **Sans signaux explicites** (obs factice) : ES et PPO font 0 trades
- **Avec PnL non-réalisé + direction dans l'obs** : ES et PPO font encore 0 trades
- **Avec reward dense (delta PnL/step) + auto-close** : (test en cours)

## Recommandation

Pour les environnements de trading :
1. **Ne pas utiliser DreamerV3** — architecture fondamentalement inadaptée
2. **ES avec PnL pur** nécessite un reward dense (delta PnL/step)
3. **PPO avec LSTM** nécessite les mêmes conditions
4. Le vrai goulet est le **credit assignment temporel** — BUY→HOLD→CLOSE
   est une chaîne que l'agent ne découvre jamais par exploration aléatoire
