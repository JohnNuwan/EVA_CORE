---
name: rl-trading-debugging
description: >-
  Diagnostic et correction des échecs d'entraînement RL pour le trading —
  patterns de collapse du reward, choix d'algorithme (ES vs PPO vs Dreamer),
  tests synthétiques de capacité, et pièges spécifiques aux environnements
  financiers.
category: mlops
---

# Diagnostic RL pour Trading

## Présentation

Ce skill documente les patterns d'échec récurrents dans l'entraînement
d'agents RL pour le trading (FTMO challenges, forex, crypto) et les
solutions validées expérimentalement. Couvre DreamerV3, PPO, et Evolution
Strategies (ES).

## Pattern #1 : Collapse du reward head vers la moyenne

**Symptôme** : `reward_loss = 0.0000` dans les logs, `entropy` stagne à ~1.38 nat,
l'agent fait 0 trades en validation.

**Cause racine** : Le reward_head (MLP 2×512) du World Model DreamerV3 prédit
la moyenne des rewards pour tous les états. Le MSE (Mean Squared Error) a
pour solution optimale la moyenne de la distribution. Avec ~90% de steps
HOLD (reward ~0) et ~10% de trades (reward ~+0.20), le réseau sort ~0.04
pour tout.

**Tentatives échouées** :
- Weighted MSE (pondération par écart à la moyenne) : ne suffit pas
- Stratified sampling 50/50 HOLD/trades : le réseau converge quand même
- Prior+posterior reward loss : inutile si KL=0
- Warm-up RSSM 80 épisodes : le RSSM ignore les observations (KL≈0)
- KL weight ×20 (0.1→2.0) : ne force pas le RSSM à utiliser les observations
- Reward_head 3×2048 sur GPU1 séparé : converge toujours vers la moyenne
- Action comme input explicite du reward_head (BUY-HOLD = +0.063 symlog) :
  le signal existe mais l'avantage est noyé dans le bruit

**Conclusion** : DreamerV3 ne convient pas au trading. Le RSSM prior ne
capture pas assez d'info observationnelle (KL→0) parce que les prix sont
des marches aléatoires.

## Pattern #2 : PPO collapse vers entropie zéro

**Symptôme** : `entropy → 0.000` en ~10 itérations, `actor_loss = 0.0`,
validation 0 trades.

**Cause** : Le critic apprend à prédire la valeur constante (toutes les
actions ont la même espérance) → avantages = 0 → pas de gradient pour
l'actor. L'entropie s'effondre vers une politique déterministe HOLD.

**Ne pas utiliser PPO pour le trading** sans avoir d'abord validé que
l'environnement produit des avantages non-nuls.

## Pattern #3 : Credit assignment temporel

**Symptôme** : Même sur un marché synthétique qui monte à 100%, l'agent
ne fait pas BUY.

**Cause** : Pour gagner, l'agent doit exécuter BUY → HOLD... → CLOSE.
La probabilité d'exécuter cette chaîne aléatoirement est infime (~0.5%).
Le reward n'arrive qu'au CLOSE, bien après le BUY.

**Solutions validées** :
1. **Reward dense par step** : donner le delta de PnL non-réalisé à
   chaque step (pas seulement au CLOSE). L'agent voit immédiatement
   l'effet de BUY dans un marché qui monte.
2. **Auto-close** : forcer la fermeture des positions après N bars
   de profit (ex: 20 bars). L'agent n'a pas besoin d'apprendre CLOSE.
3. **Features enrichies** : inclure le PnL non-réalisé et la direction
   de la position directement dans l'observation.

## Pattern #4 : ES (Evolution Strategies) — l'approche qui fonctionne

**Pourquoi ES marche quand DreamerV3 et PPO échouent** :
- Pas de value function → pas de collapse du critic
- Pas de reward_head → pas de prédiction de moyenne
- Optimisation directe du fitness (PnL réalisé)
- Population diversifiée naturellement → exploration inhérente
- Gradient estimé par perturbations (pas de backprop through time)

### Architecture V5.1 recommandée (corrigée, SUPERSEDED by V6 pour multi-symbole)

```
ESPolicy: LSTM 2×128 → head 128→8 actions + frozen_action_mask
...
```

**⚠️ V5.1 est adéquat pour UN SEUL symbole. Pour le multi-symbole,
utiliser l'architecture V6 (Pattern #13) : un agent par symbole.**

### Architecture V6 recommandée (multi-agent spécialisé)
Population: 16 agents parallèles (2 GPUs)
σ (mutation): 0.02
lr (ES): 0.1
elite_frac: 0.25 (top 25% sélectionnés)
Évaluation: 1000 steps, stochastique (temperature 1.5→0.3)
Fitness: PnL RÉALISÉ pur (balance finale - initiale) en %
Bias fixe: HOLD=-4.0, BUY=+3.0, SELL=+3.0, SPLIT=+1.5, CLOSE=+0.5
frozen_action_mask: SEUL HOLD gelé (bias-driven anti-collapse)
                    BUY et SELL DÉGELÉS → LSTM apprend la direction
Evolve: magnitude-based (fit/max_abs_fit, pas sign)
max_workers: len(devices) * 2 (pas *3 — surcharge mémoire)
NaN guard: old_master_vec.clone() avant update, rollback si NaN
empty_cache: torch.cuda.empty_cache() après chaque evaluate + chaque gen
~100s/gen avec pop=16, eval=1000 steps sur 2× RTX 3090 (~5h pour 200 gens)
```

Référence complète : voir `references/code-patterns.md`.
Architecture V6 multi-agent : voir `references/v6-multi-agent.md`.

**PITFALL CRITIQUE** : Ne PAS utiliser le reward total comme fitness.
Les bonus d'ouverture (+0.20/trade) et le time-decay dominent le signal.
Une politique qui trade au hasard peut avoir un reward total > une politique
qui trade peu mais bien. Utiliser le PnL réalisé pur :
```python
fitness = (env.balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100.0
if num_trades > 0:
    fitness += 2.0  # léger bonus d'activité
if num_trades == 0:
    fitness -= 50.0  # pénalité zéro-trade
```

**Antithetic sampling** : évaluer `master + ε` et `master - ε` pour chaque
vecteur de bruit. Le gradient effectif = (fitness_plus - fitness_minus) × ε.
Cela annule le bruit de baseline et double la précision du gradient.

### Configuration environnement

- Rewards denses : 100% des steps non-nuls (pour le WM, pas pour le fitness ES)
- Auto-close : après 20 bars de profit (l'agent n'a pas besoin d'apprendre CLOSE)
- Curriculum learning 3 phases : phase 1 sans frictions → phase 3 réaliste
- PnL scale ×100 en phase 1 (amplifie le signal PnL pour l'ES)

## Pattern #5 : Master ES ne trade pas (logits plats)

**Symptôme** : t±=N/N (toutes les politiques bruitées tradent) mais la
validation déterministe du master fait 0 trades, génération après génération.

**Cause racine** : Les poids du réseau sont initialisés aléatoirement →
tous les logits sont proches de zéro → HOLD est le max par une marge
infime. Les perturbations (σ=0.02) inversent aléatoirement l'argmax,
donc les politiques bruitées tradent. Mais le gradient est du bruit :
les directions de bruit qui font trader ne sont pas corrélées avec
le PnL, donc le master ne converge pas vers le trading.

### Solution initiale (insuffisante seule) : `action_bias` en buffer
Exclu des `parameters()` → non affecté par `_get_params_flat` /
`_set_params_flat` → survit à toutes les mises à jour ES.

```python
class ESPolicy(nn.Module):
    def __init__(self, ...):
        super().__init__()
        self.lstm = nn.LSTM(...)
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, action_dim, bias=False)  # PAS de bias natif
        )
        # Bias fixe anti-HOLD — buffer non-apprenable
        action_bias = torch.zeros(action_dim)
        action_bias[0] = -2.0    # HOLD  ← pénalisé
        action_bias[1] = +1.0    # BUY   ← favorisé
        action_bias[2] = +1.0    # SELL  ← favorisé
        action_bias[4] = +0.5    # SPLIT_BUY
        action_bias[5] = +0.5    # SPLIT_SELL
        self.register_buffer('action_bias', action_bias)

    def forward(self, x, hidden=None):
        out, h = self.lstm(x, hidden)
        logits = self.head(out[:, -1, :])
        return logits + self.action_bias, h  # biais ajouté ici
```

**Pourquoi `bias=False` sur la dernière couche Linear** : pour éviter un
double biais (le biais natif de Linear + le buffer). Les deux seraient
dans des chemins différents (un dans parameters(), l'autre dans buffers()).

**Piège** : ne PAS utiliser `self.head[-1].bias.data.copy_(bias)` car
le biais de la couche Linear fait partie de `parameters()` et sera
écrasé à chaque `_set_params_flat`.

### Check-list étendue

Quand le master ES ne trade pas en validation :

1. [ ] Vérifier que t± montre que les politiques bruitées tradent
2. [ ] Si t±=N/N mais validation=0 trades → logits plats → Pattern #5
3. [ ] Ajouter un `action_bias` en `register_buffer` avec HOLD négatif
4. [ ] Vérifier que `_get_params_flat` n'inclut PAS le buffer (count_params)
5. [ ] Vérifier que le biais survit après `evolve()` → `_create_population()`

### Dual GPU pour ES

Avec 2 GPUs, paralléliser l'évaluation de la population avec
`ThreadPoolExecutor`. Chaque worker est assigné à un GPU via `device_idx`.

```python
devices = ('cuda:0', 'cuda:1')
# Répartir la population : pop[i] → devices[i % 2]
# max_workers = len(devices) * 3
# Chaque _evaluate_one prend (policy, env, steps, device_idx)
```

PyTorch libère le GIL pendant les opérations CUDA → les threads
sont efficaces pour paralléliser les forward passes LSTM.

## Test Synthétique de Capacité

Avant de debugger un algorithme RL sur données réelles, **toujours tester
sur un environnement synthétique trivial** :

1. Créer un marché qui monte (ou descend) de façon déterministe
2. Donner des rewards denses (delta PnL par step) + auto-close
3. Inclure PnL non-réalisé et direction dans l'observation
4. Vérifier que l'agent apprend BUY (marché haussier) ou SELL (baissier)
   en < 30 générations

Si l'agent n'apprend PAS sur le synthétique, le RL est cassé.
S'il apprend sur le synthétique mais pas sur le réel, le problème
vient des features (pas assez prédictives).

## Pattern #6 : `reset()` écrase les paramètres de validation manuels

**Symptôme** : La validation produit systématiquement 0 trades ou des résultats
incohérents (symboles aléatoires, step aléatoire) alors que l'entraînement
montre des trades (t±=N/N).

**Cause racine** : La méthode `_validate()` définit manuellement des paramètres
spécifiques (`current_symbol`, `current_step`, `start_step`...) pour contrôler
les conditions d'évaluation, puis appelle `env.reset()` qui les écrase avec
des valeurs aléatoires. La validation s'exécute donc sur un environnement
différent de celui prévu.

Ce bug est silencieux : aucun crash, aucun warning. Les métriques de validation
sont simplement fausses (calculées sur des données/symboles aléatoires).

**Exemple de code buggé** :
```python
def _validate(self):
    env = MyEnv(data_dict, curriculum_episode=9999)
    env.current_symbol = 'XAUUSD'
    env.current_step = env.lookback + len(env.df) - 3000  # dernières barres
    env.reset()  # ← ÉCRASE current_symbol et current_step !
    obs = env._get_obs()
```

**Solution** : Ne PAS appeler `reset()` après avoir défini manuellement des
paramètres d'environnement. Initialiser l'état manuellement en répliquant
tous les champs que `reset()` initialise.

```python
def _validate(self):
    env = MyEnv(data_dict, curriculum_episode=9999)
    env.current_symbol = 'XAUUSD'
    env.current_step = env.lookback + len(env.df) - 3000
    # PAS de reset() — init manuelle de TOUS les champs d'état
    env.balance = INITIAL_BALANCE
    env.peak_balance = env.balance
    env.daily_start_balance = env.balance
    env.positions = []
    env.trades_today = 0
    env.total_trades = 0
    env.winning_trades = 0
    env.consecutive_losses = 0
    env.cooldown_until = 0
    env.episode_reward = 0.0
    # ... tous les champs que reset() initialise ...
    obs = env._get_obs()
```

**Piège** : `reset()` dans `__init__` est appelé automatiquement. Si on
override les champs APRÈS la construction mais AVANT d'appeler `reset()`
une deuxième fois, la première initialisation (celle de `__init__`) n'est
pas le problème — c'est bien l'appel explicite à `reset()` APRÈS avoir
défini les paramètres qui est buggé.

**Vérification** : Après l'init manuelle, ajouter une assertion :
```python
assert env.current_symbol == 'XAUUSD'
assert env.current_step == expected_step
```

## Pattern #7 : Antithetic sampling cassé — +ε et -ε sur des marchés différents

**Symptôme** : t±=N/N (toutes les politiques bruitées tradent), fitness effective
faible et non-convergente, validation déterministe = trades mais PnL aléatoire.

**Cause racine** : L'antithetic sampling évalue master+ε et master-ε sur des
environnements DIFFÉRENTS (symboles et steps aléatoires distincts). La
différence de fitness (f_plus - f_minus) est dominée par le bruit du marché,
pas par l'effet de la perturbation ε. Le gradient ES = bruit pur.

**Code buggé** :
```python
for i, ((_, noise, _), _) in enumerate(zip(self.population, envs)):
    # BUG: nouvel env avec reset() aléatoire → marché DIFFÉRENT de envs[i]
    anti_env = MultiSymbolEnvV4(data_dict, ...)
    all_tasks.append((anti_policy, anti_env, ...))
```

**Solution** : Capturer l'état initial de env_plus (symbole, step) AVANT évaluation,
puis l'injecter dans anti_env au lieu d'appeler reset().

```python
# Étape 0 : capturer l'état de chaque env_plus
env_states = [{'symbol': e.current_symbol, 'step': e.current_step,
               'features': e.features, 'df': e.df, 'spec': e.spec}
              for e in envs]

# Antithetic avec MÊME état
for i, ...:
    anti_env = MultiSymbolEnvV4(data_dict, ...)
    all_tasks.append((anti_policy, anti_env, ..., env_states[i]))
```

Et dans `_evaluate_one`, utiliser `init_state` au lieu de `env.reset()`.

**Vérification** : Après le fix, les paires +ε/-ε doivent avoir des fitness
fortement corrélées (même direction de marché). Si fitness_plus ≈ fitness_minus
pour toutes les paires, c'est que le marché domine encore — augmenter pop_size.

## Pattern #8 : Dérive des poids qui contre le bias anti-HOLD → overtrade

**Symptôme V5 (BUY/SELL gelés)** : Le master trade massivement (51 trades en 500 steps de
validation), winrate bloqué à ~41%, PnL négatif systématique. BUY et SELL
ont des logits quasi identiques (~+3.00 chacun) → l'agent alterne BUY/SELL
aléatoirement sans direction.

**Cause racine** : Le `frozen_action_mask` gelait HOLD + BUY + SELL. Avec
BUY=+3.0 et SELL=+3.0 (bias fixe), les deux actions sont toujours également
probables. Le réseau ne peut pas apprendre à choisir la direction car sa
contribution est masquée. L'agent overtrade dans les deux sens et perd
les spreads/commissions.

**Solution V5.1 corrigée** : Geler UNIQUEMENT HOLD. BUY et SELL doivent
être libres pour que le LSTM apprenne à moduler le bias en fonction des
features de marché. Le réseau peut ainsi produire BUY > SELL dans un
marché haussier, et SELL > BUY dans un marché baissier.

```python
class ESPolicy(nn.Module):
    def __init__(self, ...):
        ...
        self.register_buffer('frozen_action_mask', torch.ones(action_dim))
        self.frozen_action_mask[0] = 0.0  # HOLD uniquement → gelé
        # BUY(1) et SELL(2) DÉGELÉS → le réseau apprend la direction

    def forward(self, x, hidden=None):
        out, h = self.lstm(x, hidden)
        logits = self.head(out[:, -1, :])
        return logits * self.frozen_action_mask + self.action_bias, h
```

**Étape obligatoire après evolve()** : remettre à zéro UNIQUEMENT les
poids HOLD (canal 0). Les poids BUY/SELL sont laissés libres.

```python
def evolve(self, fitness):
    ...
    # Seul HOLD (canal 0) est remis à zéro — BUY/SELL libres
    with torch.no_grad():
        self.master.head[-1].weight.data[0] = 0.0
    self._create_population()
```

**Vérification** : Logger `buy_hold_gap = logit[BUY] - logit[HOLD]` ET
`buy_sell_gap = logit[BUY] - logit[SELL]`. Si `buy_sell_gap ≈ 0` après
30+ générations, les features ne sont pas assez informatives pour que
le LSTM apprenne la direction → Pattern #13.

**Piège historique** : La V5 gelait HOLD/BUY/SELL en pensant que « l'agent
n'a pas besoin d'apprendre la direction ». C'est faux : sans modulation
BUY vs SELL par le réseau, l'agent overtrade aléatoirement.

## Pattern #10 : Crash silencieux ES — ThreadPoolExecutor avale les exceptions

**Symptôme** : L'entraînement ES s'arrête brutalement après N générations
sans stack trace, sans message d'erreur. Le processus est simplement mort.
Le log s'arrête net (ex: 13/200 générations).

**Cause racine** : `ThreadPoolExecutor.submit()` exécute `_evaluate_one`
dans des threads. Si une exception est levée dans un worker (OOM CUDA,
IndexError dans l'environnement, NaN dans les tenseurs), elle est capturée
par le Future mais jamais `.result()`-ée si le thread meurt avant. Sans
try/except explicite, le processus s'éteint silencieusement.

**Solution** : Wrapper chaque `future.result()` dans un try/except, et
wrapper tout `evaluate_population()` dans un try/except au niveau de
la boucle d'entraînement.

```python
# Dans evaluate_population() — try/except par future
for future in as_completed(futures):
    anti, idx = futures[future]
    try:
        fitness, num_trades = future.result()
    except Exception as e:
        print(f"   ⚠️  Erreur évaluation (anti={anti}, idx={idx}): {e}")
        fitness = -100.0  # fitness minimale en cas d'erreur
    ...

# Dans train_es.py run() — try/except global
try:
    effective_fitness, fitness_plus, fitness_minus = \
        self.agent.evaluate_population(envs, steps=self.eval_steps)
except Exception as e:
    print(f"   ❌ CRASH gen {gen}: {e}")
    traceback.print_exc()
    self.agent.save(os.path.join(self.save_dir, f'crash_gen{gen}.pt'))
    break
```

**Pourquoi -100 comme fallback** : Une fitness de -100 est pire que la
pénalité zéro-trade (-50). Les élites excluront naturellement ce membre.

## Pattern #11 : NaN dans le gradient ES après plusieurs générations

**Symptôme** : L'entraînement tourne normalement pendant N générations,
puis crash silencieux. Les logs de fitness montrent une dégradation
progressive (best_fitness → 0) avant le crash.

**Cause racine** : Accumulation de NaN dans le gradient ES. Scénario :
- `fit_clipped = np.clip(fit, -100, 100)` où `fit` peut être NaN
  si l'environnement produit un PnL indéfini (division par zéro, etc.)
- `grad += w * noise_primary * (fit_clipped / max_abs_fit)` produit NaN
- `master_vec += self.lr * grad` → master_vec contient NaN
- Le forward suivant (LSTM) produit des NaN → l'évaluation suivante
  produit des NaN → cascade

**Solution** : Sauvegarder `old_master_vec` AVANT l'update, détecter
NaN/Inf après, et rollback si nécessaire.

```python
def evolve(self, fitness):
    ...
    old_master_vec = master_vec.clone()  # sauvegarde AVANT update
    master_vec += self.lr * grad

    if torch.isnan(master_vec).any() or torch.isinf(master_vec).any():
        print(f"   ⚠️  NaN/Inf détecté après evolve! Update annulée.")
        master_vec = old_master_vec  # rollback
    else:
        self._set_params_flat(self.master, master_vec)
    ...
```

**Piège** : Ne PAS faire `master_vec = self._get_params_flat(self.master)`
pour restaurer — si le master a déjà été partiellement modifié, cette
lecture peut retourner des valeurs corrompues. Toujours sauvegarder
avec `.clone()` avant l'update.

## Pattern #12 : Accumulation mémoire GPU entre générations ES

**Symptôme** : Crash OOM après N générations, même avec une petite
population. La mémoire GPU allouée augmente progressivement.

**Cause racine** : Chaque `evaluate_population()` crée N politiques
antithetic (`anti_policy`) sur GPU. PyTorch garde le cache CUDA même
après garbage collection. Les `ThreadPoolExecutor` workers peuvent
aussi accumuler des tenseurs dans leur contexte.

**Solution** :
1. `torch.cuda.empty_cache()` après chaque `evaluate_population()` et
   après chaque génération
2. Réduire `max_workers` de `len(devices)*3` à `len(devices)*2`
3. Nettoyer sur TOUS les GPUs, pas seulement le primary

```python
# Après evaluate_population() — vider le cache sur tous les GPUs
for device in self.devices:
    with torch.cuda.device(device):
        torch.cuda.empty_cache()

# Dans train_es.py run() — après chaque génération
torch.cuda.empty_cache()
```

**Workers ThreadPoolExecutor** : `len(devices) * 2` est suffisant. Avec
`len(devices)*3`, trop de workers se partagent les GPUs, causant des
pics mémoire et des contentions.

**Symptôme** : Le master trade (grâce au frozen_action_mask) mais le PnL
ne s'améliore pas génération après génération. Les best_fitness fluctuent
aléatoirement sans tendance haussière.

**Cause racine** : `np.sign(fit)` donne un poids de ±1 à TOUTES les
perturbations, quelle que soit leur fitness effective. Une perturbation
avec fitness=+0.01 reçoit le même poids qu'une avec fitness=+7.0. Comme
la plupart des fitness effectives sont proches de zéro (bruit de marché),
le gradient est dominé par des signes aléatoires.

**Code buggé** :
```python
for (idx, (fit, (_, noise, device))), w in zip(elite, weights):
    fit_clipped = np.clip(fit, -100, 100)
    grad += w * noise_primary * np.sign(fit_clipped)  # ±1, égalise tout
```

**Solution** : Pondérer par la magnitude normalisée du fitness. Les
perturbations qui donnent un fitness fort reçoivent plus de poids.

```python
# Normaliser par la magnitude max des élites
elite_fitness = np.array([fit for _, (fit, _) in zip(elite, ...)])
max_abs_fit = max(np.max(np.abs(elite_fitness)), 1.0)

for (idx, (fit, (_, noise, device))), w in zip(elite, weights):
    fit_clipped = np.clip(fit, -100, 100)
    grad += w * noise_primary * (fit_clipped / max_abs_fit)  # pondéré
```

**Pourquoi ça aide** : Les perturbations chanceuses (fitness élevé) ont
un impact proportionnellement plus fort sur le gradient. Les perturbations
bruiteuses (fitness ~0) ont un impact négligeable. Le rapport signal/bruit
du gradient s'améliore.

**Piège** : Le `max_abs_fit` doit être calculé sur le même ensemble
d'élites que la boucle de gradient. Ne pas le pré-calculer sur toute
la population (inclut les non-élites).

Quand l'agent ne trade pas :

1. [ ] Vérifier que 100% des steps ont un reward non-nul
2. [ ] Vérifier que BUY/SELL donne un reward immédiat supérieur à HOLD
3. [ ] Tester sur environnement synthétique (trending up/down)
4. [ ] Si ES : vérifier que le fitness (PnL pur) augmente avec les générations
5. [ ] Si ES et t±=N/N mais validation=0 trades → Pattern #5 (logits plats)
6. [ ] Si ES et validation=0 trades mais résultats incohérents → Pattern #6 (reset écrase params)
7. [ ] Logger `buy_hold_gap = logit[BUY] - logit[HOLD]` en validation : si gap < 1.0 → Pattern #8 (poids contrent le bias)
8. [ ] Si PPO/Dreamer : vérifier que l'entropie ne collapse pas à 0
9. [ ] Vérifier que l'observation inclut le statut de position et PnL latent
10. [ ] Ajouter auto-close pour forcer la réalisation du PnL
11. [ ] Vérifier que SEUL HOLD est gelé dans frozen_action_mask, pas BUY/SELL (Pattern #8)
12. [ ] Vérifier que le `head[-1].weight[0]` (HOLD uniquement) est remis à zéro après `evolve()`

Quand l'ES converge vers du trading mais le PnL ne s'améliore pas :

1. [ ] Vérifier que le fitness est basé sur le PnL pur (pas reward total)
2. [ ] Vérifier que l'antithetic sampling utilise le MÊME marché (Pattern #7)
3. [ ] Réduire la température d'exploration (temp_start plus bas)
4. [ ] Augmenter pop_size (16→32) pour un meilleur gradient
5. [ ] Augmenter eval_steps (1000→2000) pour réduire le bruit d'évaluation
6. [ ] Vérifier que le biais anti-HOLD est en buffer ET masqué dans forward (Pattern #8)
7. [ ] Si BUY et SELL ont des logits quasi identiques après 30+ gens → Pattern #8 (features pas assez informatives)
8. [ ] Remplacer `np.sign(fit)` par `fit / max_abs_fit` dans evolve() (Pattern #9)
9. [ ] Logger `buy_hold_gap` ET `buy_sell_gap` en validation
10. [ ] Logger `grad_norm` dans les métriques evolve : si norme → 0, le gradient est mort

Quand le master trade en validation mais PnL négatif systématiquement :

1. [ ] Vérifier que les features sont informatives (corrélation avec rendements futurs)
2. [ ] Tester avec un marché synthétique simple pour valider la capacité d'apprentissage
3. [ ] Ajouter des features de timing (heure de la session, jour de la semaine)
4. [ ] Réduire le nombre d'actions (HOLD/BUY/SELL/CLOSE uniquement)
5. [ ] Si overtrade (>30 trades/500 steps) → vérifier que BUY/SELL ne sont pas tous deux à ~+3.0 (Pattern #8)
6. [ ] Logger `buy_sell_gap = logit[BUY] - logit[SELL]` : si ≈0, le réseau n'apprend pas la direction
7. [ ] Si 90%+ des trades sont dans la même direction (BUY ou SELL) → vérifier le bias directionnel externe → Pattern #18
8. [ ] Si bias externe présent → le supprimer et revenir à bias fixe symétrique + pénalité imbalance (Pattern #18)
9. [ ] Vérifier la séparation train/val : pas de chevauchement entre zones d'entraînement et validation

Quand l'entraînement crash sans erreur :

1. [ ] Vérifier les logs : arrêt brutal sans stack trace → Pattern #10 (ThreadPoolExecutor)
2. [ ] Ajouter try/except autour de chaque `future.result()` (Pattern #10)
3. [ ] Ajouter try/except autour de `evaluate_population()` dans la boucle principale (Pattern #10)
4. [ ] Vérifier NaN dans master_vec après evolve → Pattern #11 (NaN guard)
5. [ ] Ajouter `old_master_vec.clone()` avant l'update + détection NaN/Inf (Pattern #11)
6. [ ] Vérifier la mémoire GPU : `torch.cuda.empty_cache()` après chaque gen (Pattern #12)
7. [ ] Réduire `max_workers` de `len(devices)*3` à `len(devices)*2` (Pattern #12)

## Pattern #13 : Dilution du gradient ES avec données multi-symboles

**Symptôme** : Un seul agent ES entraîné sur 7 symboles (XAUUSD, EURUSD,
US30, BTCUSD...) ne converge pas. BUY et SELL restent quasi identiques
(±0.02) même après 30+ générations. Le winrate est bloqué à ~41%.

**Cause racine** : Chaque symbole a des dynamiques incompatibles :
- XAUUSD : volatil, valeurs refuges, corrélé à l'inflation
- EURUSD : range, macro, sensible aux taux d'intérêt
- BTCUSD : crypto, momentum-driven, décorrélé du forex
- US30 : indices, trend-following, gaps à l'ouverture

Un seul LSTM doit apprendre toutes ces dynamiques contradictoires.
Le gradient ES est la moyenne des gradients sur tous les symboles :
si XAUUSD dit BUY mais EURUSD dit SELL, le gradient net ≈ 0. Aucun
apprentissage de direction n'est possible.

**Preuve expérimentale** : Après 6 générations ES avec BUY/SELL dégelés
et 7 symboles, `buy_hold_gap = +7.01` mais `buy_sell_gap ≈ 0.00`.
Le réseau ne différencie pas BUY de SELL parce que le signal de
direction est noyé dans le mélange de symboles.

**Solution V6** : Architecture multi-agent spécialisé — un agent ES par
symbole. Chaque agent voit UN SEUL type de dynamique → gradient propre.

```
MultiAgentOrchestrator
 ├── SingleSymbolEnv(XAUUSD) → ESAgent(LSTM 2×128, 367k params)
 ├── SingleSymbolEnv(EURUSD) → ESAgent(LSTM 2×128, 367k params)
 ├── ... (un agent par symbole)
 └── MasterAgent (allocation de capital, Phase 2)
```

- Chaque agent esclave est entraîné indépendamment sur son symbole
- Le gradient ES n'est plus dilué → le réseau peut apprendre BUY vs SELL
- Les agents peuvent diverger : XAUUSD apprend à shorter, US30 à longer
- pop_size=8 suffit (données homogènes), eval_steps=500 (plus rapide)
- ~12s/génération pour 7 agents (vs ~100s pour 1 agent multi-symbole)

Implémentation de référence : `ftmo_agent/specialized_agents.py`.
Détails complets : `references/v6-multi-agent.md`.

**Piège** : Ne PAS réutiliser le MultiSymbolEnvV4 tel quel pour les
esclaves. Utiliser `SingleSymbolEnv` qui force le symbole après
construction (le `reset()` dans `__init__` change le symbole).

```python
class SingleSymbolEnv:
    def __init__(self, data_dict, symbol, ...):
        self.env = MultiSymbolEnvV4(data_dict, ...)
        # Forcer après construction (reset() dans __init__ l'a changé)
        self.env.current_symbol = symbol
        self.env.features, self.env.feature_names, self.env.df = data_dict[symbol]
        self.env.spec = SYMBOLS[symbol]
```

**Phase 2 (MasterAgent)** : Après pré-entraînement des esclaves, un agent
maître reçoit leurs signaux et apprend l'allocation de capital :
- Quels symboles trader (poids softmax sur N symboles + HOLD)
- Taille de position par symbole
- Gestion des corrélations (ex: ne pas longer US30 et shorter US500)

**Check-list multi-agent** :
1. [ ] Vérifier que chaque agent voit UN SEUL symbole (current_symbol fixe)
2. [ ] Vérifier que `n_features` est pris depuis l'environnement (pas les données brutes)
3. [ ] Logger `buy_sell_gap` par symbole : si >1.0, l'agent apprend la direction
4. [ ] Si buy_sell_gap ≈ 0 après 30+ gens sur UN symbole → features pas informatives
5. [ ] Phase 1 : entraînement indépendant (150 gens par agent)
6. [ ] Phase 2 : fine-tuning joint + MasterAgent (TODO)

### Résumé — 19 patterns documentés

Pour vérifier l'intégrité de l'agent ES après toute modification de
`es_agent.py`, exécuter le script de vérification :
`references/verify-es-policy.py` (7 tests : frozen_action_mask, forward,
evolve, NaN guard, empty_cache, evaluate_population, _validate).

## Pattern #14 : Bias BUY/SELL symétrique — pas de gradient de direction

**Symptôme** : Même avec BUY/SELL dégelés (Pattern #8), après 30+ générations
`buy_sell_gap ≈ 0.00` pour tous les symboles. Les politiques bruitées tradent
(t±=8/8) mais la validation déterministe du master fait 0 trades.

**Cause racine** : Avec `action_bias[BUY] = +3.0` et `action_bias[SELL] = +3.0`
(identiques), en mode stochastique BUY et SELL ont ~50% de chances chacun.
L'agent ouvre dans les deux sens aléatoirement. Le gradient ES ne peut pas
apprendre "BUY > SELL sur un marché haussier" car échantillonnage symétrique.

**Preuve expérimentale** :
- V5.1 (BUY/SELL dégelés, 7 symboles) : après 6 générations, buy_sell_gap ≈ 0
- V6 (agents spécialisés par symbole) : après 28 générations,
  buy_sell_gap ≈ 0 pour les 7 agents. Validation = 0 trades.

**Solution** : Injecter un signal de direction asymétrique dans le bias,
calculé à partir des features de marché. Le réseau n'apprend pas la
direction from scratch — il reçoit un "hint" et apprend le timing.

```python
class ESPolicy(nn.Module):
    def compute_directional_bias(self, features):
        trend = features[:, trend_indices].mean(dim=-1)
        direction = torch.tanh(trend * 10)  # ∈ [-1, +1]
        bias = self.action_bias.clone()
        bias[BUY] += direction * 2.0    # hausse → BUY favorisé
        bias[SELL] -= direction * 2.0   # hausse → SELL défavorisé
        return bias

    def forward(self, x, hidden=None):
        out, h = self.lstm(x, hidden)
        logits = self.head(out[:, -1, :])
        dir_bias = self.compute_directional_bias(out[:, -1, :])
        return logits * self.frozen_action_mask + dir_bias, h
```

**Résultat** : marché haussier → BUY=+5.0, SELL=+1.0. Marché baissier → inverse.
Le réseau peut TOUJOURS contrebalancer via les logits appris.

**Check-list** :
1. [ ] Si buy_sell_gap ≈ 0 après 10+ générations → Pattern #14
2. [ ] Ajouter un signal de direction dans le bias (tendance, momentum)
3. [ ] Vérifier que buy_sell_gap > 1.0 et suit la tendance du marché
4. [ ] Si le réseau contrebalance trop → réduire l'amplitude (×2 → ×1)

## Pattern #15 : Validation PnL-seul insuffisante — Arena multi-critères

**Symptôme** : Un modèle sauvegardé comme `best.pt` (val_pnl > 0) perd de
l'argent en live. Le winrate est < 50%, le profit_factor < 1.5, mais le PnL
est positif sur l'échantillon de validation par chance.

**Cause racine** : ftmo_agent utilise `val_pnl > best_val_pnl` comme seul
critère de sauvegarde. Un PnL positif sur 500 steps peut être dû à 2-3
trades chanceux, pas à une stratégie rentable.

**Solution** : S'inspirer de l'Arena darwinienne de The Hive
(`eva_lab/arena.py`). La promotion d'un champion doit valider :
- `win_rate` > seuil (ex: 55%)
- `profit_factor` > 1.5 (gross_profit / gross_loss)
- `drawdown` < limite FTMO (5% daily, 10% total)
- `expectancy` > 0 (perte moyenne / trade)
- `sample_size` > 30 trades minimum

De plus, tracker les POSITION_MECHANICS : SLBE capture rate, pyramid
efficiency, hold drag score, close quality score. Un modèle avec bon PnL
mais mauvaise position mechanics ne sera pas robuste en live.

**Architecture de référence** : voir `references/the-hive-architecture.md`
pour l'implémentation complète (Arena, ChampionPromoter, GeneticUpdater,
multi-horizon, position mechanics tracking).

**Genetic Registry** : Au lieu d'écraser `best.pt`, maintenir un registre
ADN (JSON) qui trace chaque génération avec ses métriques. Permet rollback
et comparaison inter-générations.

```python
# Au lieu de:
if val_pnl > self.best_val_pnl:
    self.agent.save('best.pt')

# Faire:
champion_metrics = {
    'win_rate': val_wr,
    'profit_factor': gross_profit / max(gross_loss, 1),
    'drawdown': max_daily_dd,
    'expectancy': (gross_profit + gross_loss) / max(trades, 1),
    'sample_size': val_trades,
}
if self._is_promotion_worthy(champion_metrics):
    self._register_generation(champion_metrics)
    self.agent.save(f'checkpoints_es/gen_{gen}_champion.pt')
```

**Check-list** :
1. [ ] Remplacer val_pnl seul par validation multi-critères
2. [ ] Ajouter profit_factor, win_rate, expectancy, sample_size
3. [ ] Implémenter un genetic registry (JSON, pas juste best.pt)
4. [ ] Tracker position mechanics (SLBE, pyramid, hold drag)
5. [ ] Exiger sample_size > 30 trades avant promotion

## Pattern #16 : Crashs silencieux ES — 2 tentatives, 8-10 générations max

**Symptôme** : L'entraînement ES V5.1 s'arrête à 8/200 générations
(checkpoints_es) et 10/200 (checkpoints_es_debug) sans erreur visible.
Le log s'arrête net. Aucun crash_gen*.pt sauvegardé.

**Cause racine probable** : Malgré les try/except (Pattern #10) et NaN
guard (Pattern #11), le processus meurt silencieusement. Causes possibles :
- OOM GPU progressif (Pattern #12) qui tue le processus avant que le
  try/except ne puisse sauvegarder
- ThreadPoolExecutor worker qui meurt (segfault CUDA) sans lever d'exception
- Le log file n'est pas flushé avant le crash → dernières lignes perdues

**Confirmation expérimentale** :
- checkpoints_es : 8 générations, best=+1.96 (gen 6), val=-1.20% (gen 5)
- checkpoints_es_debug : 10 générations, best=+1.62 (gen 1), val=-0.93% (gen 5)
- Les deux ont le même profil : val PnL négatif, winrate 41%, 0 trades master

**Solution** :
1. Ajouter `sys.stdout.flush()` après chaque log line
2. Ajouter un signal handler pour SIGTERM/SIGKILL qui sauvegarde l'état
3. Utiliser `torch.cuda.memory_allocated()` pour logger la mémoire GPU
4. Réduire pop_size si OOM (16→8) plutôt que de crasher
5. Logger dans un fichier ET stdout (déjà fait, mais s'assurer du flush)

**Piège** : Le `log_file.flush()` existe dans train_es.py mais pas
`sys.stdout.flush()`. Si le processus est tué par l'OS (OOM killer), le
buffer stdout peut être perdu.

## Pattern #17 : Solution V7 — bias directionnel dynamique + Arena multi-critères

**⚠️ MISE À JOUR** : Le bias directionnel dynamique (Partie 1 de cette
solution) est **superseded par V7b / Pattern #18**. Sur un marché
fortement directionnel (XAUUSD +145%), le bias externe calculé depuis
les indicateurs devient systématiquement biaisé BUY et court-circuite
l'apprentissage du réseau. V7b revient à un bias fixe symétrique
BUY=+3.0/SELL=+3.0 avec pénalité de déséquilibre dans le fitness.
L'Arena multi-critères (Partie 2) reste valide et est toujours utilisée.

**Symptômes résolus** : Pattern #14 (bias symétrique, pas de gradient de
direction) ET Pattern #15 (validation PnL-seul insuffisante).

**Solution V7** : Au lieu d'un bias fixe BUY=+3.0/SELL=+3.0, le bias est
calculé dynamiquement à chaque step depuis 5 indicateurs techniques (EMA
slope, RSI, VWAP distance, MACD histogram, ADX). Le réseau n'apprend pas
la direction from scratch — il reçoit un "hint" directionnel et apprend
le timing + la modulation.

### Architecture V7 (XAUUSD seul, 5 actions)

- **5 actions** : HOLD, BUY, SELL, CLOSE, SPLIT_CLOSE (fini les 8 actions
  avec PYRAMID/PARTIAL_CLOSE/SPLIT_BUY/SPLIT_SELL qui diluaient le gradient)
- **1 symbole** : XAUUSD seul (Pattern #13 confirmé — multi-symbole dilue)
- **20 features** : 16 techniques + 4 de position (vs 296 bruitées avant)
- **Bias dynamique** : buy_bias et sell_bias ∈ [0, 1] calculés à chaque step
  → ajoutés au logits comme `logits[:, BUY] += buy_bias * 3.0`
- **Reward = Sharpe local** : `(pnl - mean_returns) / std_returns * 10 +
  pnl * 50`, pas PnL brut → un trade à +0.5% avec faible volatilité vaut
  plus qu'un trade à +2% avec haute volatilité
- **SLBE obligatoire** : tout trade en profit > 0.5% verrouille au breakeven
- **Arena de validation** : WR>55% + PF>1.3 + DD<5% + 30 trades + expectancy>0
- **Champion Registry** : JSON avec historique de toutes les générations,
  pas juste best.pt écrasé

### Preuve expérimentale (test 3 générations)

- Gen 0 : 264 trades, **200 BUY vs 64 SELL** → le biais directionnel fonctionne
  (XAUUSD était haussier sur la période → plus de BUY que SELL)
- Gen 0 : `buy_sell_gap ≠ 0` pour la première fois (V5.1 et V6 restaient à ~0)
- Gen 2 : best fitness +4.77 (vs +2.89 au gen 0) → convergence
- Le master TRADE en mode déterministe (plus de collapse HOLD)
- ~60s/gen sur 2× RTX 3090 avec pop=16, 1000 steps

### Code clé — bias directionnel

```python
def _get_directional_bias(self):
    """Retourne (buy_bias, sell_bias) ∈ [0,1] basé sur 5 indicateurs."""
    ema_signal = np.clip(ema_slope * 500, -1, 1)     # tendance
    rsi_signal = 0.5 if rsi < 0.3 else (-0.5 if rsi > 0.7 else (rsi-0.5)*0.5)
    vwap_signal = -0.3 if vwap_dist > 0.002 else (0.3 if vwap_dist < -0.002 else 0)
    macd_signal = np.clip(macd_hist * 200, -0.5, 0.5)
    trend_strength = min(adx * 2, 1.0)                # amplification

    total = (ema_signal + rsi_signal + vwap_signal + macd_signal) / 4
    total *= (0.5 + trend_strength * 0.5)

    return max(total, 0), max(-total, 0)  # (buy_bias, sell_bias)
```

### Code clé — forward avec bias dynamique

```python
def forward(self, x, hidden=None, buy_bias=0.0, sell_bias=0.0):
    out, h = self.lstm(x, hidden)
    logits = self.head(self.ln(out[:, -1, :]))
    logits = logits * self.frozen_mask + self.base_bias
    logits[:, BUY] += buy_bias * 3.0   # DYNAMIQUE, pas fixe
    logits[:, SELL] += sell_bias * 3.0
    return logits, h
```

### Arena — validation multi-critères

```python
class Arena:
    MIN_WIN_RATE = 55.0
    MIN_PROFIT_FACTOR = 1.3
    MAX_DRAWDOWN = 5.0
    MIN_TRADES = 30

    def evaluate(self, policy, device):
        # Évaluer en mode DÉTERMINISTE (argmax, pas sampling)
        # sur les 3000 dernières barres (non vues à l'entraînement)
        # Calculer: PnL, trades, WR, PF, DD, expectancy, Sharpe
        # passed = True seulement si TOUS les critères passent
```

### Check-list V7

1. [ ] Utiliser 5 actions max (HOLD/BUY/SELL/CLOSE/SPLIT_CLOSE)
2. [ ] 1 symbole par agent (XAUUSD d'abord)
3. [ ] Bias directionnel dynamique (pas fixe symétrique)
4. [ ] Reward = Sharpe ratio local (pas PnL brut)
5. [ ] SLBE obligatoire à +0.5%
6. [ ] Validation Arena multi-critères (pas PnL seul)
7. [ ] Champion Registry JSON (pas best.pt écrasé)
8. [ ] 20 features propres (pas 296 bruitées)
9. [ ] Détection auto GPU/CPU dans le trainer

Référence complète : `references/v7-xauusd-architecture.md` (V7 original,
**obsolète** — voir V7c ci-dessous).
Architecture V7c (actuelle) : `references/v7c-xauusd-architecture.md`.

## Pattern #18 : Bias directionnel dynamique externe → collapse BUY sur marché haussier

**Symptômes** : Sur XAUUSD 2024-2026 (2286 → 5598, +145 %), le bias
directionnel dynamique introduit en V7 (Pattern #17) devient
systématiquement biaisé BUY. Dès la gen 20, la distribution d'actions
en validation donne **256 BUY vs 8 SELL** (97 % de BUY). Le winrate
dégringole à **41,7 %** — l'agent achète tout, y compris les sommets,
et ne shorter jamais les retracements. Le PnL est négatif malgré un
marché haussier.

**Cause racine** : La fonction `_get_directional_bias()` de
`env_xauusd.py` calcule `buy_bias` et `sell_bias` depuis 5 indicateurs
techniques (EMA slope, RSI, VWAP, MACD histogram, ADX). Sur un marché
qui monte de +145 %, **tous ces indicateurs sont haussiers en moyenne** :

- EMA slope > 0 sur la majorité des bars → `ema_signal > 0`
- RSI fréquemment > 0.5 mais rarement < 0.3 → `rsi_signal ≥ 0`
- VWAP distance : le prix est souvent au-dessus du VWAP → `vwap_signal ≥ 0`
- MACD histogram > 0 en tendance haussière → `macd_signal > 0`
- ADX élevé en tendance forte → `trend_strength` amplifie le total

Résultat : `total = (ema + rsi + vwap + macd) / 4 * (0.5 + adx*0.5)`
est **presque toujours positif** → `buy_bias = max(total, 0) > 0` et
`sell_bias = max(-total, 0) = 0` à quasi-chaque step. Le logit BUY
reçoit `+buy_bias * 3.0` en permanence tandis que le logit SELL ne
reçoit rien. Le réseau est **passif** : il suit le biais au lieu
d'apprendre la direction. Ses logits appris sont noyés sous le
`+3.0 * buy_bias` qui vaut souvent +2 à +3.

**Contradiction avec le Pattern #14** : Le Pattern #14 recommandait
d'injecter un signal de direction asymétrique dans le bias pour
débloquer `buy_sell_gap ≈ 0`. C'était correct dans le contexte V5/V6
(bias fixe symétrique, réseau qui n'apprend pas la direction). **Mais
ce bias directionnel DOIT venir du réseau lui-même** (via les logits
appris), pas d'indicateurs externes codés en dur. Un bias externe
calculé depuis les mêmes features que le réseau voit n'ajoute aucune
information — il écrase simplement la sortie du réseau avec une
heuristique fixe. Le réseau n'a plus de raison d'apprendre : la
décision est déjà prise par `_get_directional_bias()`.

**Preuve expérimentale** :
- Gen 0 : 200 BUY vs 64 SELL (apparence de succès — le biais « fonctionne »)
- Gen 20 : 256 BUY vs 8 SELL (le biais s'accentue — le réseau converge
  vers BUY car toute perturbation qui réduit BUY est pénalisée par le
  marché haussier + le bias externe)
- Gen 20 : WR = 41,7 %, val PnL négatif → l'agent achète les sommets
  et ne shorter jamais les retracements
- `buy_sell_gap` est élevé (≈ +4 à +6) mais **artificiel** — il vient
  du bias externe, pas des logits appris

### Solution : retirer le bias directionnel externe

1. **Supprimer `_get_directional_bias()`** de `env_xauusd.py` — ne plus
   calculer `buy_bias` / `sell_bias` depuis les indicateurs techniques.
2. **Revenir à un bias fixe symétrique** : `BUY = +3.0`, `SELL = +3.0`
   (identiques). Le réseau reçoit un hint anti-HOLD mais aucune
   préférence directionnelle.
3. **Laisser le réseau apprendre seul la direction** via les logits
   du LSTM. Les 20 features (EMA slope, RSI, VWAP, MACD, ADX...) sont
   déjà dans l'observation — le réseau peut les utiliser pour moduler
   BUY vs SELL sans que l'environnement ne décide pour lui.
4. **Ajouter une pénalité forte sur le déséquilibre BUY/SELL** dans le
   fitness, pour forcer le réseau à explorer les deux directions :

```python
# Dans le calcul du fitness ES
buy_count = sum(1 for a in actions if a == BUY)
sell_count = sum(1 for a in actions if a == SELL)

if total_trades > 2:
    min_dir = min(buy_count, sell_count)
    max_dir = max(buy_count, sell_count)
    balance_ratio = min_dir / max(1, max_dir)  # 0=unidirectionnel, 1=équilibré

    # Bonus équilibré: jusqu'à +5.0 si parfaitement équilibré
    fitness += balance_ratio * 5.0

    # Pénalité unidirectionnel: jusqu'à -10.0 si 100% unidirectionnel
    imbalance = 1.0 - balance_ratio  # 0=équilibré, 1=unidirectionnel
    fitness -= imbalance * 10.0
```

5. **Logger le ratio BUY/SELL** à chaque génération pour détecter
   rapidement tout collapse directionnel :

```python
print(f"  Actions: {buy_count} BUY / {sell_count} SELL "
      f"(ratio {buy_count/max(sell_count,1):.1f}:1, "
      f"imbalance={imbalance:.2f})")
```

### Pourquoi le bias externe échoue sur marché haussier

| Indicateur    | Valeur moyenne sur XAUUSD 2024-2026 | Signal généré |
|---------------|--------------------------------------|---------------|
| EMA slope     | > 0 (tendance haussière)            | `ema_signal > 0` |
| RSI           | 0.55-0.70 (momentum haussier)       | `rsi_signal ≥ 0` |
| VWAP distance | > 0 (prix au-dessus du VWAP)        | `vwap_signal ≥ 0` |
| MACD histogram| > 0 (tendance haussière)            | `macd_signal > 0` |
| ADX           | 25-40 (tendance forte)              | `trend_strength` amplifie |

**Total** : presque toujours positif → `buy_bias > 0`, `sell_bias = 0`
→ le logit BUY reçoit `+bias * 3.0` en permanence → le réseau est
court-circuité.

### Code corrigé — forward sans bias directionnel externe

```python
def forward(self, x, hidden=None):
    """Forward sans bias directionnel externe.
    Le réseau apprend seul la direction via les logits du LSTM.
    Bias fixe symétrique BUY=+3.0 / SELL=+3.0 (anti-HOLD uniquement).
    """
    out, h = self.lstm(x, hidden)
    logits = self.head(self.ln(out[:, -1, :]))
    logits = logits * self.frozen_mask + self.base_bias
    # PAS de buy_bias / sell_bias dynamique
    # base_bias[BUY] = +3.0, base_bias[SELL] = +3.0 (symétrique)
    return logits, h
```

### Évolution des patterns de bias

| Version | Bias BUY/SELL | Problème | Pattern |
|---------|---------------|----------|---------|
| V5      | +3.0 / +3.0 fixe, gelés | Pas de direction apprise (gap≈0) | #8, #14 |
| V6      | +3.0 / +3.0 fixe, dégelés | Pas de direction (multi-symbole dilue) | #13 |
| V7      | Dynamique (EMA/RSI/VWAP/MACD/ADX) | Collapse BUY sur marché haussier | **#18** |
| V7.1    | +3.0 / +3.0 fixe symétrique + pénalité imbalance | Réseau apprend seul la direction | — |

**Leçon** : Un bias directionnel externe basé sur des indicateurs
techniques est une heuristique codée en dur qui court-circuite
l'apprentissage du réseau. Sur un marché fortement directionnel
(haussier ou baissier), ce bias devient systématique et empêche
l'agent d'apprendre à shorter (ou longer). La direction doit venir
exclusivement des logits appris par le réseau, stimulés par une
pénalité de déséquilibre BUY/SELL dans le fitness.

### Check-list

1. [ ] Si 90%+ des trades sont dans la même direction → vérifier le
      bias directionnel externe → Pattern #18
2. [ ] Supprimer `_get_directional_bias()` de l'environnement
3. [ ] Revenir à `base_bias[BUY] = +3.0`, `base_bias[SELL] = +3.0`
      (symétrique, anti-HOLD uniquement)
4. [ ] Ajouter `balance_penalty = imbalance * 20.0` dans le fitness
   (implémentation réelle: bonus +5.0 équilibré, pénalité -10.0 imbalance)
5. [ ] Logger le ratio BUY/SELL à chaque génération
6. [ ] Vérifier que `buy_sell_gap` (logits appris seulement, sans bias)
      diverge de 0 au fil des générations → le réseau apprend la direction
7. [ ] Si `buy_sell_gap` reste à 0 après 30+ gens → les features ne sont
      pas assez informatives (pas un problème de bias)

## Pattern #19 : Sous-utilisation GPU en ES — bottleneck CPU sur env.step

**Symptôme** : GPU à 10-13% d'utilisation pendant l'entraînement ES, 47s par
génération dont 46.6s sur CPU. Le forward pass GPU prend 0.35ms mais le
step complet prend ~2.9ms.

**Cause racine** : L'environnement de trading `env.step()` est du code Python
pur (numpy/pandas) qui tourne sur CPU. À chaque step, le flux est :
1. CPU construit l'obs (numpy) → transfer CPU→GPU (1 obs, batch=1)
2. GPU fait le forward LSTM (0.35ms pour 226K params)
3. GPU retourne l'action → transfer GPU→CPU
4. CPU exécute `env.step()` (numpy, pandas, python — ~2.5ms)

Le GPU attend le CPU 90% du temps. Le modèle est trop petit (226K params)
pour saturer le GPU, et les transfers CPU↔GPU à chaque step tuent la
performance. Avec 16 politiques × 1000 steps = 16000 aller-retours.

**Benchmark GPU (RTX 3090)** :
- batch=1, h=128 (226K params) : 0.35ms/call
- batch=16, h=128 (226K params) : 0.38ms/call
- batch=16, h=512 (3.5M params) : 1.22ms/call

Le passage de batch=1 à batch=16 ne change presque rien (0.35→0.38ms)
parce que le GPU n'est pas saturé. Mais le passage à h=512 reste rapide
(1.22ms) tout en utilisant mieux le GPU.

**Solutions validées (session 2026-07-17, hd=128→512, 47s→13s/gen)** :

1. **L=1 incremental stepping** — Au lieu de forward L=lookback (48 timesteps)
   à CHAQUE step, initialiser le LSTM une fois avec L=lookback, puis faire
   L=1 (un seul timestep) pour les steps suivants. Réduit le forward de
   18.8ms → 4.9ms/step (3.8× plus rapide). Le LSTM conserve son hidden state
   entre les calls.

   ```python
   # INIT: forward L=lookback pour initialiser
   for i in range(P):
       obs_t = torch.from_numpy(obs_list[i]).unsqueeze(0).to(device)
       logits, hidden_states[i] = model(obs_t, hidden_states[i])
   # Puis boucle: forward L=1
   for step_i in range(steps):
       last_obs = obs_list[i][-1:]  # (1, F) — dernier timestep seulement
       obs_t = torch.from_numpy(last_obs).unsqueeze(0).to(device)  # (1, 1, F)
       logits, hidden_states[i] = model(obs_t, hidden_states[i])
   ```

2. **16 modules nn.LSTM séparés** (un par politique) — Au lieu d'utiliser
   `functional_call` en boucle (18.25ms/step), créer P modules ESPolicyV7
   sur GPU avec `set_params_flat()`. Le kernel cuDNN est 6× plus rapide
   (2.86ms/step pour 16 × batch=1). `functional_call` a un overhead par
   call qui s'additionne.

3. **Batched mask+sample** — Rassembler les P logits en un tensor `(P, 5)`,
   un seul `masked_fill` + `multinomial` au lieu de P individuels.
   Réduit de 5.5ms → 1.8ms/step.

4. **Batched obs transfer** — `np.stack()` des P obs en un seul tensor,
   un seul `torch.from_numpy().to(device)` par step.

5. **Modèle plus gros** — hidden_dim 128→512 (226K→3.5M params).
   Le GPU est mieux utilisé et le modèle est plus expressif.

6. **TF32 activé** — `torch.backends.cuda.matmul.allow_tf32 = True`
   et `torch.backends.cudnn.allow_tf32 = True`.

**PITFALLS critiques découverts** :

- **`torch.vmap` + `nn.LSTM` = CRASH**. `vmap` ne fonctionne PAS avec
  `nn.LSTM` car cuDNN appelle `flatten_parameters()` qui échoue sur les
  poids batchés (`RuntimeError: shape '[10240, 1]' is invalid for input
  of size 163840`). Utiliser des modules séparés à la place.

- **`functional_call` en boucle est 6× plus lent** que des modules séparés
  (18.25ms vs 2.86ms pour 16 forwards). Préférer `set_params_flat()` sur
  des modules nn.LSTM séparés.

- **ThreadPoolExecutor n'accélère PAS env.step**. Le GIL empêche les
  threads de paralléliser le code numpy/pandas. Sequential est plus rapide
  (4.2ms vs 11.7ms pour 16 envs × 100 steps).

- **`multiprocessing.Pool` pour env.step est impraticable** : l'env
  contient le DataFrame complet (15MB pickled). Le overhead de pickling
  dépasse le gain.

- **CUDA streams ne helpent PAS** pour petits kernels (4.67ms en séquentiel
  = 4.65ms en parallèle sur 2 GPUs). Les kernels sont trop petits.

- **`torch.compile` ne help PAS** pour nn.LSTM cuDNN (0.29ms raw vs 0.31ms
  compiled).

**Approche optimale non encore implémentée** : Custom LSTM avec `torch.bmm`
(poids batched `(P, 4*hd, F)`) en mode L=1 atteint **0.45ms/step** (vs
2.86ms pour 16×nn.LSTM). Total théorique ~6.3s/gen. Nécessite un LSTM
custom complet avec extraction manuelle des poids.

**Benchmark détaillé (RTX 3090, PyTorch 2.6, CUDA 12.4)** :

| Approche | Forward/step | Total/gen (500×2) |
|----------|-------------|-------------------|
| Original (ThreadPool, L=48, h=128) | 18.8ms | ~47s |
| functional_call loop (L=1, h=512) | 5.6ms | ~18s |
| 16 × nn.LSTM batch=1 (L=1, h=512) | 2.86ms | ~13s |
| Custom bmm LSTM (L=1, h=512) | 0.45ms | ~6.3s (théorique) |
| nn.LSTM batch=16 shared weights | 0.18ms | N/A (ES nécessite poids différents) |

**Check-list** :
1. [ ] Vérifier `nvidia-smi` pendant l'entraînement : si GPU < 20% → bottleneck CPU
2. [ ] Profiler : `forward pass time` vs `env.step time` — si ratio < 0.2, le GPU attend
3. [ ] Utiliser L=1 incremental stepping (init avec L=lookback, puis L=1)
4. [ ] Créer P modules nn.LSTM séparés (pas functional_call, pas vmap)
5. [ ] Batcher mask+sample (un seul masked_fill + multinomial pour P politiques)
6. [ ] Activer TF32 (`torch.backends.cuda.matmul.allow_tf32 = True`)
7. [ ] Augmenter hidden_dim (128→512) si le modèle est sous 1M params
8. [ ] NE PAS utiliser ThreadPoolExecutor pour env.step (GIL)
9. [ ] NE PAS utiliser vmap avec nn.LSTM (crash cuDNN)
10. [ ] NE PAS utiliser multiprocessing.Pool pour env.step (pickling overhead)
11. [ ] Env.step en séquentiel (plus rapide que threads pour numpy pur)
12. [ ] Optionnel : custom bmm LSTM pour 6× plus de speedup sur le forward

## Pattern #20 : Dual-GPU antithetic parallèle + optimisations VRAM (V7d)

**Symptôme** : GPU à 3.4% d'utilisation (0.83 GB / 24 GB), GPU 1 complètement
inutilisé pour l'entraînement, `pop_size=16` avec `hidden_dim=1024` (13.7M
params) utilise à peine 0.57 GB de VRAM pour les poids.

**Cause racine** : L'évaluation antithetic (+ε et -ε) était séquentielle —
+ε sur GPU 0, puis -ε sur GPU 0. Le GPU 1 n'était jamais utilisé. De plus,
`TF32` était activé dans `__init__` mais pas au niveau module, et les noises
(6.55 GB pour pop=128) étaient alloués sur GPU.

### Solutions validées (session 2026-07-17, V7d)

1. **Dual-GPU antithetic parallèle** : Créer DEUX `BatchedPolicyV7` —
   `batched_policy` sur GPU 0 (+ε), `batched_policy_minus` sur GPU 1 (-ε).
   Lancer l'évaluation dans deux `threading.Thread` en parallèle. Chaque
   thread utilise son propre GPU et son propre `ThreadPoolExecutor`.

   ```python
   # Dans __init__:
   self.batched_policy = BatchedPolicyV7(...).to(self.primary_device)      # GPU 0
   self.batched_policy_minus = BatchedPolicyV7(...).to(self.secondary_device)  # GPU 1

   # Dans evaluate_population:
   def run_plus():
       results_box[0] = self._run_batch_episode(envs, steps, temperature)

   def run_minus():
       results_box[1] = self._run_batch_episode(
           anti_envs, steps, temperature,
           init_states=env_states,
           policy=self.batched_policy_minus,
           device=self.secondary_device,
           pool=self._get_pool_minus(),
       )

   t_plus = threading.Thread(target=run_plus)
   t_minus = threading.Thread(target=run_minus)
   t_plus.start(); t_minus.start()
   t_plus.join(); t_minus.join()
   ```

   **PITFALL** : Les deux threads partagent le même `ThreadPoolExecutor`
   → `map()` retourne un générateur paresseux qui plante (`TypeError: 'generator'
   object is not subscriptable`). Solution : `list(pool.map(...))` et créer
   des pools séparés (`_pool` et `_pool_minus`).

2. **TF32 au niveau module** : `torch.backends.cuda.matmul.allow_tf32 = True`
   doit être activé AVANT tout import torch — au top du fichier, pas dans
   `__init__`. Ajouter aussi `torch.backends.cudnn.benchmark = True`.

   ```python
   # Top de es_agent_v7.py
   torch.backends.cuda.matmul.allow_tf32 = True
   torch.backends.cudnn.allow_tf32 = True
   torch.backends.cudnn.benchmark = True
   ```

3. **Noises sur CPU** : Les noises (pop_size × n_params × 4 bytes) peuvent
   dépasser 6 GB pour pop=128. Les garder sur CPU et transférer par morceau.

   ```python
   # Au lieu de:
   self.noises = torch.randn(pop_size, n_params, device=self.primary_device) * sigma
   # Faire:
   self.noises = torch.randn(pop_size, n_params) * sigma  # CPU

   # Dans evolve:
   noise_i = self.noises[idx].to(self.primary_device)  # CPU→GPU par élite
   ```

4. **`_set_weights_param_by_param`** : Transférer et appliquer les noises
   un paramètre à la fois au lieu d'allouer tout le vecteur (13 GB) sur GPU.
   Économise toute la VRAM des noises.

   ```python
   def _set_weights_param_by_param(self, master_flat, noises, device):
       offset = 0
       for name, shape in self._param_shapes.items():
           n = int(np.prod(shape))
           master_slice = master_flat[offset:offset + n]
           noise_slice = noises[:, offset:offset + n]  # (P, n) sur CPU
           param = self.batched_weights[name]  # (P, *shape) sur device
           master_gpu = master_slice.to(device)  # transfer seulement ce slice
           noise_gpu = noise_slice.to(device)
           param.data.copy_(master_gpu.view(1, *shape).expand_as(param.data))
           param.data.add_(noise_gpu.view(self.pop_size, *shape))
           del master_gpu, noise_gpu
           offset += n
   ```

5. **`set_weights_from_flat` in-place** : Utiliser `param.data.copy_()` et
   `param.data.add_()` au lieu de créer un tensor temporaire (`master_slice.unsqueeze(0)
   + noise_slice`). Évite l'allocation d'un second vecteur de la taille
   des poids.

### Multiprocessing.Pool — TESTÉ ET REJETÉ

`multiprocessing.Pool` avec initializer (chaque worker a son propre env en
mémoire) était 33× plus rapide en théorie (3.6ms/step vs 117.8ms/step) mais
en pratique **plus lent** (38.7s vs 22.4s pour 100 steps avec h=2048).

**Cause** : Le overhead IPC (pickle des obs (48, 20) + mask (5,) + info dict
à chaque step, 64 envs × 1000 steps × 2 antithetic) annule complètement le
gain CPU. Chaque step fait un aller-retour worker→main pour récupérer obs + mask.

**Benchmark comparatif (pop=64, h=2048, 100 steps)** :

| Approche | Temps/100 steps | VRAM/GPU |
|----------|------------------|----------|
| ThreadPool (V7c) | 22.4s | 13.3 GB |
| Multiprocessing.Pool | 38.7s | 13.3 GB |

**Conclusion** : `ThreadPoolExecutor` reste la meilleure approche pour ce
workload. Le vrai bottleneck est l'IPC, pas le GIL. La solution ultime serait
de vectoriser `env.step` sur GPU (tensors au lieu d'objets Python), mais
cela nécessite un rewrite complet de `env_xauusd.py`.

### Configuration V7d (actuelle)

| Paramètre | V7c | V7d |
|-----------|-----|-----|
| pop_size | 16 | **64** |
| hidden_dim | 512 | **2048** |
| Params/politique | 3.5M | **54.7M** |
| steps | 1000 | **500** |
| Dual-GPU | Non (1 GPU) | **Oui (+ε GPU 0 \|\| -ε GPU 1)** |
| TF32 | Dans __init__ | **Module-level** |
| Noises | Sur GPU | **Sur CPU** |
| VRAM GPU 0 | 0.83 GB (3.4%) | **17.9 GB (73%)** |
| VRAM GPU 1 | 0 GB (0%) | **19.5 GB (79%)** |
| Temps/gen | 26s | 112s |
| Politiques × params | 16 × 3.5M = 56M | **64 × 54.7M = 3.5B** |

Le temps/gen augmente (112s vs 26s) mais le travail par gen est 62× supérieur
(3.5B params vs 56M). Le rapport qualité/temps est meilleur.

Référence complète : `references/v7d-dual-gpu-architecture.md`.

### Check-list dual-GPU + VRAM

1. [ ] Vérifier `nvidia-smi` : si GPU 1 = 0% → créer `batched_policy_minus` sur GPU 1
2. [ ] TF32 au TOP du fichier, pas dans `__init__`
3. [ ] Noises sur CPU si pop × n_params × 4 > 2 GB
4. [ ] `_set_weights_param_by_param` si n_params > 10M
5. [ ] `set_weights_from_flat` in-place (`copy_` + `add_`, pas de `+`)
6. [ ] `threading.Thread` pour +ε et -ε en parallèle
7. [ ] Pools ThreadPoolExecutor séparés pour chaque thread
8. [ ] `list(pool.map(...))` — ne JAMAIS indexer un générateur paresseux
9. [ ] NE PAS utiliser `multiprocessing.Pool` pour env.step (IPC overhead > gain CPU)
10. [ ] Logger VRAM par GPU : `torch.cuda.memory_allocated(i)` après chaque gen

## Pattern #21 : GA + stratégies-règles — ce qui marche après 6 échecs NN

**Contexte** : après DreamerV3 (#1), PPO (#2), ES/LSTM (#5,#8,#13,#18,#19,#20),
la conclusion est que les NN profonds surapprennent le bruit M15. La solution
validée : **algorithme génétique sur stratégies-règles paramétriques** (~30
gènes), backtest vectorisé CPU, arena walk-forward.

**Pourquoi ça marche là où ES/LSTM échouait** :
- 30 gènes (signal) au lieu de 54.7M params (bruit) → convergence réelle
- Backtest CPU vectorisé : 130-170ms/stratégie, ~20 000 stratégies/min sur 32 CPUs
- Arena walk-forward K=6 fenêtres : anti-overfitting par construction
- Stratégies interprétables (on lit les règles gagnantes)

**Anti-convergence — ISLAND MODEL** : population unique → top-4 identiques,
best figé 100+ générations. Solution : 6 îlots de 64 évoluant indépendamment,
migration du meilleur toutes les 15 gens, mutation adaptative (σ×2.5 si
stagnation ≥20 gens). Résultat : best progresse à chaque génération.

**Fitness ambitieuse** : ne pas récompenser la prudence seule. Si limites FTMO
OK (DDj≤2%, DDt≤5%), fitness = monthly_pct × 3 + palier +25 à ≥10%/mois.
Sinon la population plafonne à +2.4%/mois "confortable".

**Test de capacité obligatoire** : sur marché synthétique haussier, le GA doit
trouver allow_long=True + trend mode en <10 générations (validé : gen 1).

Référence complète : `references/evo-arena-architecture.md`.

## Pattern #22 : Le GPU ne parallélise PAS un backtest séquentiel

**Tenté et ÉCHOUÉ** (ne pas réessayer) :

1. **Backtest GPU barre-par-barre** (P stratégies simultanées, boucle T barres,
   kernels (P,) par barre) : 60s pour 64 backtests vs 0.17s CPU. L'overhead de
   lancement CUDA (~3µs × ~15 kernels × ~19500 barres) dépasse le calcul.
   Le séquentiel temporel est le mauvais problème pour le GPU.

2. **Présélection GPU approximative** (score = rendement futur moyen capté par
   les signaux, 200k génomes en 0.6s) : corrélation avec le backtest réel
   **+0.157** (inutilisable). Le score ignore SL/TP/sizing/spread/DD — ce qui
   détermine précisément la rentabilité. 4/20 du top-20 GPU rentables au réel.

3. **Multithreading CUDA** (2 threads + empty_cache) : `illegal memory access`.
   PyTorch CUDA n'est pas thread-safe dans ce pattern.

**Leçon** : le backtest de trading est séquentiel (position dépend de la barre
précédente). Le GPU n'aide QUE si on élimine la dépendance temporelle (grid
search de signaux précalculés = problème différent). Pour le backtest réel :
**32 CPUs × stratégies indépendantes** est l'optimum. Ne pas forcer le GPU.

## Skills Liés

- `project-restructuring` : organisation du projet après prototypage RL
- `content-creation-guidelines` : conventions de commit en français
- `references/the-hive-architecture.md` : architecture Arena + champion de The Hive
- `local-ai-stack` : infrastructure Docker pour services IA locaux (vLLM, ComfyUI)
- `references/gpu-batch-eval-profiling.md` : benchmarks détaillés GPU batch evaluation (Pattern #19)
- `references/evo-arena-architecture.md` : architecture EVO-ARENA (GA + arena walk-forward, Patterns #21/#22)
- `references/mt5-wine-data-pipeline.md` : pipeline MT5 sous Wine pour données historiques FTMO multi-timeframes (M1→D1), prérequis i386, extraction MQL5 vs API Python, montage NTFS, pitfall sudo -S bloqué