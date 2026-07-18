# DreamerV3 / RL Training — Patterns Pratiques & Debugging

## Architecture Type : DreamerV3 sur 2 GPUs

```
GPU 0 (cuda:0) ← JEPA (15.5M params)
              ← World Model (RSSM)
GPU 1 (cuda:1) ← Actor-Critic (2.1M params)
```

### Tailles de batch recommandées (2x RTX 3090 25GB)
- WM + JEPA : batch 1024
- Actor-Critic : batch 512 (le AC est sur GPU1, transfert GPU0→GPU1 overhead)
- Replay buffer : 500k-1M transitions

### Actions

Les actions DOIVENT être stockées en **one-hot** dans le replay buffer,
pas en entier. Le World Model (RSSM) attend `(B, action_dim)` :

```python
# CORRECT
action_one_hot = np.eye(N_ACTIONS)[action]  # shape (action_dim,)
replay.add(obs, action_one_hot, reward, next_obs, done)

# BUG
replay.add(obs, action, reward, next_obs, done)  # action = int → shape () → erreur
```

## Bug Fréquent #1 : Paramètres inversés dans ReplayBuffer.add()

**Signature :** `add(self, obs, action, reward, next_obs, done)`

**Cause :** `env.step(action)` retourne `(next_obs, reward, done, info)`.
L'appel à `add(obs, action, reward, done, next_obs)` inverse done et next_obs.

**Symptôme au sample :**
```
next_obs: shape=(B,) dtype=bool      ← wrong (c'est 'done')
dones:    shape=(B, 48, 296)         ← wrong (c'est 'next_obs')
```

**Fix :** Vérifier l'ordre des 5 paramètres. Le pattern correct est :
```python
next_obs, reward, done, info = env.step(action)
replay.add(obs, action, reward, next_obs, done, mask)
#                  1       2       3        4        5
```

**Script de diagnostic :**
```python
batch = replay.sample(64)
for k, v in batch.items():
    if isinstance(v, np.ndarray):
        print(f"{k}: shape={v.shape} dtype={v.dtype}")
# next_obs dtype=bool → bug d'ordre
```

## Bug Fréquent #2 : L'agent apprend à ne RIEN FAIRE (HOLD collapse)

### Cause racine

Le RL agent découvre que HOLD donne reward=0 alors que trader
donne une espérance négative (due au spread, slippage, ou hasard).

### Solutions selon l'approche

#### Approche A — Reward shaping (la plus courante)
Pénaliser HOLD, récompenser l'ouverture de trades, amplifier les wins :

```python
# Exemple (environnement V3)
reward -= 0.1  # chaque barre sans trade
reward += 0.25  # à l'ouverture d'un trade
if pnl > 0:
    reward += pnl * 15 + 1.0  # win amplifié
```

⚠️ Le shaping peut créer des comportements indésirables (l'agent
apprend à ouvrir-fermer rapidement pour collecter le bonus).

#### Approche B — Pure PnL (DreamerV3 paper style)
Pas de shaping. L'agent optimise directement l'équité :

```python
reward = (equity - prev_equity) / account_size
```

⚠️ L'agent converge rapidement vers HOLD si les trades initiaux
(aléatoires) sont perdants. Solution : curriculum learning.

#### Approche C — Curriculum learning (recommandée)
3 phases de difficulté croissante :

| Phase | Épisodes | Spread | Slippage | Commission | Max trades |
|-------|----------|--------|----------|------------|------------|
| 1 | 0-200 | 0% | 0% | 0% | 20 |
| 2 | 200-500 | 30% | 30% | 0% | 12 |
| 3 | 500+ | 100% | 100% | 100% | 8 |

```python
def _get_curriculum_phase(self, episode):
    if episode < 200:  return 1, 0.0   # no friction
    if episode < 500:  return 2, 0.3   # low friction
    return 3, 1.0                       # full friction
```

#### A — Bonus d'exploration (counteract HOLD collapse)

Ajouter une récompense intrinsèque pour chaque trade (non-HOLD) en phase 1 :

```python
# phase 1 : +5% par trade
# phase 2 : +0.5% par trade
# phase 3 : 0 (le modèle doit trader pour le PnL réel)
exp_bonus = 0.05 if phase == 1 else (0.005 if phase == 2 else 0.0)
reward += exp_bonus if traded_this_step else 0
```

⚠️ Ajuster le bonus selon le niveau JEPA : 5% suffit si JEPA < 14, monter à 10% si JEPA > 15 (les embeddings pauvres noient le signal).

```python
# config
CURRICULUM_CONFIG = {
    "phase1_episodes": 200,
    "phase1_exploration_bonus": 0.05,
    "phase2_exploration_bonus": 0.005,
}

# environment
def _get_curriculum_phase(self):
    return 1, 0.0, config['phase1_exploration_bonus']  # (phase, spread_mult, bonus)

# step
phase, _, exp_bonus = self._get_curriculum_phase()
if traded_this_step and exp_bonus > 0:
    reward += exp_bonus  # intrinsic reward, bypasses WM prediction
```

⚠️ Le bonus d'exploration ne doit s'appliquer qu'aux **ouvertures** de
position (BUY, SELL, SPLIT_BUY, SPLIT_SELL), pas aux CLOSE, PYRAMID ou
PARTIAL_CLOSE. Distinguer `traded_this_step` (toute action non-HOLD) de
`opened_position` (seulement les ouvertures).

```python
opened_position = False
if action == BUY and mask[BUY]:
    reward += self._open_position(...)
    opened_position = True
# ... etc pour SELL, SPLIT_BUY, SPLIT_SELL

if opened_position and exp_bonus > 0:
    reward += exp_bonus  # seulement pour l'ouverture
```

#### B — Epsilon-greedy pendant la collecte

Même avec température élevée, le policy peut collapser sur HOLD et le
replay buffer se remplit de transitions HOLD. Forcer 20% d'actions
aléatoires pendant la collecte :

```python
def _collect_episode(self):
    if np.random.random() < 0.2:
        action = np.random.choice(np.where(mask)[0])  # override
    else:
        action = agent.get_action(obs, mask, temperature=agent.temperature)
```

#### C — Température cyclique agressive

- Démarrer à **T=2.0** (pas 1.0)
- **Plancher à 0.5** (pas 0.7 ni 1.0)
- Cycle de reset tous les **100 épisodes** (pas 500)

```python
# À VÉRIFIER : le code a souvent un plancher bugué
# max(temperature, 1.0) ← BUG, désactive toute température < 1.0
# max(temperature, 0.5) ← CORRECT

self.temperature = 2.0  # start hot
# chaque épisode :
self.temperature = max(0.5, self.temperature * 0.9998)
# tous les 100 épisodes :
self.temperature = min(2.0, self.temperature + 0.8)
```

#### D (NOUVEAU) — Dense Reward Architecture (V4.2)

Problème fondamental : le WM prédit en symlog et minimise la MSE. Si 80%+
des steps ont reward ≈ 0, le WM apprend juste à prédire 0 partout.
Même avec un bonus d'exploration à +0.20, les épisodes de trade sont
trop rares pour que la MSE s'en préoccupe. **Le reward_loss passe à
0.0000 en qques épisodes.**

**Solution : 100% des steps doivent avoir un reward non-nul et varié.**

Structure dense :

| Composant | Valeur | Déclencheur |
|-----------|--------|-------------|
| **PnL scaling** | ×100 phase 1, ×10 phase 2, ×1 phase 3 | Equity change × scale |
| **Time-decay** | -0.02 × (bars_since/48), max -0.02 | Chaque step |
| **Holding bonus** | +0.005/step | Position ouverte |
| **Opening bonus** | +0.20 phase 1, +0.01 phase 2, 0 phase 3 | Ouverture de trade |
| **Completion bonus** | +0.01 win / -0.01 loss | Fermeture de position |

**Pourquoi ça marche** : chaque step reçoit un reward qui dépend de l'état.
Un step avec position ouverte = holding bonus + PnL. Un step sans position
= time-decay qui s'accumule. Le WM voit une fonction de reward bimodale
(positive quand en position, négative quand inactif).

**Mise en garde : même avec 100% dense, la MSE du WM peut encore converger
vers une constante.** C'est parce que la prédiction de reward du WM est
une tête linéaire unique sur l'état latent — elle ne capture pas bien
les transitions brutales (HOLD→BUY→HOLD→CLOSE). Le reward_loss affiché
à `.4f` peut être 0.0000 alors que le vrai MSE est ~0.005.

```python
# Configuration V4.2
CURRICULUM_CONFIG = {
    "phase1_exploration_bonus": 0.20,
    "phase1_pnl_scale": 100.0,
    "phase2_exploration_bonus": 0.01,
    "phase2_pnl_scale": 10.0,
    "trade_completion_bonus": 0.01,
    "trade_completion_penalty": 0.01,
    "time_decay_max": 0.02,
    "holding_bonus": 0.005,
}

# Application dans step()
phase, _, exp_bonus = self._get_curriculum_phase()

# PnL scaling
equity_change = (current_equity - prev_equity) / account_size
pnl_scale = CURRICULUM_CONFIG[f'phase{phase}_pnl_scale']
reward += equity_change * pnl_scale

# Time-decay
self.bars_since_last_trade += 1
decay = -CURRICULUM_CONFIG['time_decay_max'] * (self.bars_since_last_trade / 48.0)
decay = max(-CURRICULUM_CONFIG['time_decay_max'], decay)
reward += decay

# Holding bonus
if self.positions:
    reward += CURRICULUM_CONFIG['holding_bonus']

# Opening bonus (reset time-decay)
if opened_position:
    reward += exp_bonus
    self.bars_since_last_trade = 0
```

### HOLD Collapse — Correctifs de Dernier Recours (V4.3)

Quand le reward shaping dense, l'exploration bonus et l'epsilon-greedy
ne suffisent pas, le problème est plus profond.

#### Problème : le WM collapse vers la moyenne

**Symptôme :** `reward_loss ≈ 0.0000` même en valeur brute, le WM prédit
~0.04 pour tous les états. L'entropie stagne à ~1.38 (pour 8 actions) et
l'AC loss = -(entropy coeff × entropie) = ~ -0.02 (juste le bonus entropie).

**Cause 1 : Échantillonnage uniforme du ReplayBuffer**

Si 90% des transitions sont des HOLD (reward ≈ -0.005), un batch uniforme
de 1024 contient ~0-10 transitions de trade (reward ≈ +0.20). Le MSE est
dominé par les HOLD, le WM prédit la moyenne (~ -0.005). Les trades perdus
dans le bruit.

**Fix : Échantillonnage stratifié O(1) — 50% HOLD, 50% trades**

```python
class ReplayBuffer:
    def __init__(self, capacity=200000):
        self.buffer = deque(maxlen=capacity)
        # V4.2: index O(1) pour sampling stratifié
        self.hold_idxs = deque(maxlen=capacity)
        self.trade_idxs = deque(maxlen=capacity)
        self._counter = 0
    
    def add(self, obs, action_oh, reward, next_obs, done, action_mask=None):
        self.buffer.append({...})
        idx = self._counter
        self._counter += 1
        if action_oh[HOLD] > 0.5:
            self.hold_idxs.append(idx)
        else:
            self.trade_idxs.append(idx)
        if len(self.buffer) < self._counter:
            oldest = self._counter - len(self.buffer)
            if self.hold_idxs and self.hold_idxs[0] <= oldest:
                self.hold_idxs.popleft()
            if self.trade_idxs and self.trade_idxs[0] <= oldest:
                self.trade_idxs.popleft()
    
    def sample(self, batch_size=128):
        hold_list = list(self.hold_idxs)
        trade_list = list(self.trade_idxs)
        n = min(batch_size, len(self.buffer))
        n_hold = min(n // 2, len(hold_list))
        n_trade = min(n - n_hold, len(trade_list))
        hold_batch = np.random.choice(hold_list, n_hold, replace=False).tolist() if n_hold > 0 else []
        trade_batch = np.random.choice(trade_list, n_trade, replace=False).tolist() if n_trade > 0 else []
        remaining = n - n_hold - n_trade
        fill = []
        if remaining > 0:
            used = set(hold_batch) | set(trade_batch)
            pool = [i for i in range(len(self.buffer)) if i not in used]
            if pool:
                fill = np.random.choice(pool, min(remaining, len(pool)), replace=False).tolist()
        indices = hold_batch + trade_batch + fill
```

**Attention performance :** La version naïve avec `[i for i in range(len(buf)) 
if buf[i]['action'][HOLD] > 0.5]` est O(n) à chaque sample. Avec 12
samples/épisode × 100 épisodes × 50K buffer → ~60M itérations. Le temps
par épisode passe de 13s à 17s+. **Toujours maintenir les index côté add().**

**Cause 2 : MSE non-pondéré**

Même avec 50/50 stratifié, le WM minimise la MSE sur un batch où la
moyenne des targets symlog est ~0.09. Le reward_head prédit 0.09 pour
tout — MSE ≈ 0.008 — et se contente de ça. Le WM ne distingue pas
les états HOLD des états TRADE.

**Fix : MSE pondéré par l'écart à la moyenne**

```python
target_reward = symlog(rewards.view(-1, 1))
reward_weights = torch.abs(target_reward - target_reward.mean()) + 0.1
reward_weights = reward_weights / reward_weights.mean()
reward_loss = (reward_weights * (pred_reward - target_reward) ** 2).mean()
```

Les transitions de trade (symlog≈0.18) reçoivent ~1.4× plus de poids que
les HOLD (symlog≈-0.005). Le WM est forcé d'apprendre leur signature.

**Cause 3 : reward_loss noyé dans la loss totale**

Le WM loss est `wm_loss = reward_loss + 0.1 * kl_loss`. Le KL loss
domine (même à 0.1×). Le gradient du reward_head est négligeable.

**Fix : multiplier reward_loss par 5-10×**

```python
wm_loss = 10.0 * reward_loss + 0.1 * kl_loss  # V4.3
```

⚠️ Effet secondaire : la KL loss devient secondaire, le RSSM peut moins
bien modéliser les dynamiques. Surveiller que le JEPA loss ne diverge pas.

**Cause 4 (fondamentale) : état PRIOR vs POSTERIOR**

Le `predict_reward()` est entraîné sur les états **posterior** (qui ont vu
l'observation via `next_embedding`) mais utilisé dans l'imagination sur les
états **prior** (sans observation). Le prior diverge du posterior →
le reward_head prédit les mêmes valeurs pour des états différents.

**Fix : entraîner le reward_head sur les DEUX états simultanément**

```python
# Prédiction posterior (standard — avec observation)
pred_reward_post = self.world_model.predict_reward(post, deter_next)
posterior_loss = F.mse_loss(pred_reward_post.squeeze(-1), target_reward.squeeze(-1))

# Prédiction prior (nouveau — sans observation, comme en imagination)
pred_reward_prior = self.world_model.predict_reward(prior, deter_next)
prior_loss = F.mse_loss(pred_reward_prior.squeeze(-1), target_reward.squeeze(-1))

# Loss combinée
reward_loss = (posterior_loss + prior_loss) / 2.0
```

Le reward_head apprend à prédire correctement même sans observation,
exactement la condition de l'imagination. C'est le pendant entraînement
du diagnostic prior vs posterior.

**Cause 5 (racine ultime) : reward_head entraîné trop tôt**

Le RSSM a besoin de temps pour apprendre des représentations latentes
informatives. Pendant les 50-80 premiers épisodes, les états latents
sont quasi-aléatoires → le reward_head converge sur la moyenne des rewards
parce que c'est la seule chose prévisible avec des états non-informatifs.

**Symptôme :** `reward_loss ≈ 0.0000` dès l'épisode 5, le WM loss passe de
0.03 à 0.0005 en 8 épisodes, l'entropie stagne à 1.38 indéfiniment.

**Fix définitif : warm-up du RSSM sans reward_head**

```python
# Dans l'agent
self.episode = 0
self.rwd_warmup = 80  # épisodes de RSSM-only

# Dans train_world_model()
wm_loss = reward_loss + 0.1 * kl_loss
if self.episode < self.rwd_warmup:
    wm_loss = 0.1 * kl_loss  # RSSM-only, pas de gradient reward_head
    reward_loss = torch.tensor(0.0)

# Dans la boucle d'entraînement
for ep in range(n_episodes):
    self.agent.episode = ep  # sync le compteur
```

**Pourquoi ça marche :** pendant 80 épisodes, le RSSM apprend les dynamiques
du marché (transitions d'état, embeddings JEPA, KL prior/posterior).
Après 80 épisodes, les états latents sont riches et le reward_head peut
apprendre un mapping non-trivial état → reward au lieu de tout moyenner.

**Attention :** ne PAS augmenter le LR du reward_head pour « compenser ».
Un LR plus élevé fait converger vers la moyenne encore PLUS VITE.
Le warm-up est la seule solution qui laisse le temps aux représentations
de mûrir.

**⚠️ CRITIQUE — L'AC aussi doit être gelé pendant le warm-up.**
Si le reward_head est gelé mais que l'AC continue de s'entraîner, l'AC
apprend sur des rewards imaginaires aléatoires (reward_head non entraîné
→ prédictions aléatoires → λ-returns aléatoires → critic apprend du bruit
→ avantages ≈ 0 → acteur uniforme). Au warm-up, **tout le pipeline de valeur
doit être désactivé** : pas de `train_actor_critic()` avant ep ≥ warmup.

```python
# Dans _train_step() — skip AC pendant le warm-up
if self.agent.episode >= self.agent.rwd_warmup:
    for _ in range(4):
        batch = self.replay.sample(512)
        result = self.agent.train_actor_critic(batch)
        ac_losses.append(result['ac_loss'])
else:
    ac_losses, entropies = [0.0], [2.079]  # AC gelé
```

```python
# ❌ CONTRE-PRODUCTIF : le reward_head converge vers la moyenne en 1 step
self.rwd_opt = torch.optim.AdamW(reward_head.parameters(), lr=1e-3)  # 5× plus haut
# ✅ CORRECT : warm-up + LR standard
self.rwd_warmup = 80  # le RSSM et AC apprennent d'abord
```

**Combinaison gagnante (V4.3 définitive) :**
1. Warm-up 80 épisodes (RSSM-only, AC gelé)
2. **KL weight renforcé ×20 (0.1→2.0) pendant le warm-up** pour forcer le RSSM
   à intégrer les observations dans l'état latent (sinon KL→0, RSSM ignore tout)
3. **Après warm-up, KL weight maintenu à 0.5** (au lieu de 0.1) pour préserver
   la qualité des représentations
4. Loss prior+posterior (reward_head apprend sur les deux)
5. ReplayBuffer stratifié O(1) 50/50
6. Rewards denses (100% non-nuls, time-decay + holding bonus)
7. PnL scaling ×100 phase 1

**⚠️ CRITIQUE — Sans KL renforcé, le warm-up est inefficace.** Le RSSM
converge vers KL≈0 en ~20 épisodes (prior=posterior parfaitement), ce qui
signifie que l'état latent n'encode aucune information d'observation. Le
reward_head n'a que l'action comme signal — insuffisant. Avec KL×20, le RSSM
est forcé d'intégrer les observations dans ses représentations.

```python
# Pendant warm-up : KL weight ×20
if self.episode < self.rwd_warmup:
    wm_loss = 2.0 * kl_loss
    reward_loss = torch.tensor(0.0)

# Après warm-up : KL weight ×5 (0.5 au lieu de 0.1)
wm_loss = reward_loss + 0.5 * kl_loss
```

#### Arbre de diagnostic étendu

```diff
  ┌─ 2. Vérifier le World Model ───────────────────────┐
  │ reward_loss ≈ 0 ? → WM prédit ~0 partout           │
- │   → Cause : JEPA loss trop haute (>15)              │
- │   → Les embeddings n'encodent pas l'état du portf.  │
- │   → Checker VICReg coefs (sim/var=10 au lieu de 25) │
- │   → Attendre que JEPA descende sous ~10              │
+ │   ┌─ Sous-cause A : échantillonnage uniforme        │
+ │   │  90% HOLD → batch ≈ 100% HOLD → MSE=0          │
+ │   │  Fix : stratified sampling 50/50                │
+ │   ├─ Sous-cause B : MSE non-pondéré                 │
+ │   │  Fix : weighted MSE by abs deviation            │
+ │   ├─ Sous-cause C : reward_loss noyé dans wm_loss   │
+ │   │  Fix : 5-10× reward_loss weight                 │
+ │   └─ Sous-cause D (fondamentale) : prior ≠ posterior│
+ │   │  Fix lent : 500+ épisodes avec KL weight élevé            │\n+ │   └─ Sous-cause E (racine) : RSSM pas prêt → warm-up 80ep    │\n+ │      Le rew. head entraîné trop tôt collapse vers la moyenne   │\n+ │      Fix définitif : warm-up RSSM-only 80ep + loss prior/post │
  │ kl_loss ≈ 0 ? → prior=posterior                     │
  │   ⚠️  `kl=0.0000` en log .4f peut masquer kl≈0.003   │
  │   (le format 4 décimales arrondit <0.00005 à 0)      │
  │   → next_embedding ignoré par posterior_net ?         │
  │   → Si kl>0 (metrics.json), le RSSM apprend quand même│
  └─────────────────────────────────────────────────────┘

### Pitfalls récurrents

#### Plancher température bugué

```python
# Dans get_action() :
tempered_logits = torch.log(probs) / max(temperature, 1.0)  # ← BUG
# La doc dit "floor at 0.7" mais le code fait floor à 1.0
# Toute température < 1.0 est ignorée
# CORRECT :
tempered_logits = torch.log(probs) / max(temperature, 0.5)
```

#### Coefficient d'entropie trop élevé quand rewards sont plats

Quand le World Model prédit ~0 reward pour la plupart des transitions (cas
typique : 95%+ des actions sont HOLD, reward≈0), l'avantage imaginaire est
quasi-nul. L'entropie bonus domine et la politique reste uniforme.

**Diagnostic :** L'entropie stagne à ln(N_actions) = 2.079 (pour 8 actions)
même après 50+ épisodes d'entraînement.

**Solution :** Réduire le coefficient dès le départ :

```python
# Avant (défaut) : la politique reste uniforme 200+ épisodes
agent = DreamerV3AgentV2(..., entropy_coeff=0.05)

# Après : convergence 10-20× plus rapide
agent = DreamerV3AgentV2(..., entropy_coeff=0.01)
```

**Attention au plancher dynamique :** Le code a souvent un `max(0.05, base)`
qui surcharge le coef réduit :

```python
# Dans train_actor_critic() — le else branch peut surcharger :
self.actor_critic.entropy_coeff = max(0.05, self.base_entropy_coeff)
#                                      ^^^^ BUG si base=0.01 → devient 0.05
# CORRECT :
self.actor_critic.entropy_coeff = max(0.005, self.base_entropy_coeff)
```

#### Validation ≠ collecte

La validation (`_validate()`) et la collecte (`_collect_episode()`) utilisent
des politiques différentes :
- **Collecte** : epsilon-greedy 20% + température × policy
- **Validation** : pure policy à T=0.7 (sans epsilon)

Si la validation montre 0 trades mais que le replay buffer grossit, c'est
**normal**. Le policy pur n'a pas encore appris à trader, mais l'epsilon-greedy
force l'exploration dans le buffer. Le WM finira par apprendre.

#### `_get_curriculum_phase()` retour 3-tuple

Quand on ajoute un bonus d'exploration, la fonction retourne **3 valeurs**
au lieu de 2. Tous les sites d'unpacking doivent être mis à jour :

```python
# Avant
phase, mult = self._get_curriculum_phase()

# Après
phase, mult, bonus = self._get_curriculum_phase()
# ou
phase, _, _ = self._get_curriculum_phase()  # si seul phase est utilisé
```

#### Dimension d'observation : agent vs env

Initialiser le DreamerV3 agent avec `env.n_features` et non une constante :

```python
temp_env = MultiSymbolEnvV4(data_dict, lookback=48)
n_features = temp_env.n_features  # ← valeur dynamique (296, 316...)
agent = DreamerV3AgentV2(input_dim=n_features, ...)
```

Ne jamais hardcoder `input_dim=296` — ça crash au premier appel de `get_action`
avec RuntimeError (shape mismatch mat1/mat2).

### HOLD Collapse — Arbre de Diagnostic Complet

Symptôme : l'agent fait HOLD à 100%, validation=0 trades, entropie~ln(N).

```
┌─ 1. Vérifier le replay buffer ─────────────────────┐
│ Est-ce que le buffer contient des trades ?          │
│ Buffer grossit → OUI, epsilon-greedy fonctionne     │
│ Buffer stagnant → NON, l'epsilon-greedy est cassé   │
└─────────────────────────────────────────────────────┘
                          │
                          ▼ (si OUI)
┌─ 2. Vérifier le World Model ───────────────────────┐
│ reward_loss ≈ 0 ? → WM prédit ~0 partout           │
│   → Cause : JEPA loss trop haute (>15)              │
│   → Les embeddings n'encodent pas l'état du portf.  │
│   → Checker VICReg coefs (sim/var=10 au lieu de 25) │
│   → Attendre que JEPA descende sous ~10              │
│ kl_loss ≈ 0 ? → prior=posterior                     │
│   → next_embedding ignoré par posterior_net          │
│   → Checker l'initialisation des poids              │
└─────────────────────────────────────────────────────┘
                          │
                          ▼ (si WM OK mais HOLD)
┌─ 3. Vérifier l'Actor-Critic ───────────────────────┐
│ Avantage imaginaire ≈ 0 ? → reward plate            │
│   → Réduire entropy_coeff (0.05 → 0.01)            │
│   → Augmenter bonus d'exploration (2% → 5%)        │
│   → Vérifier le plancher dynamique (max(0.05,...)?) │
│ AC loss positif (anormal) ? → reward trop bruité    │
│   → Augmenter le discount (gamma 0.997 > 0.99)     │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─ 4. Forcer l'exploration ──────────────────────────┐
│ □ Bonus exploration (5% phase 1, 0.5% phase 2)     │
│ □ Epsilon-greedy 20% pendant collecte              │
│ □ Température démarre à 2.0, floor 0.5             │
│ □ Cycles de température tous les 100ep             │
│ □ Temps : donner 100-200 épisodes au WM            │
└─────────────────────────────────────────────────────┘
```

### Quand le bas niveau d'entropie ne suffit pas

Si l'entropie descend (< 1.0) mais que l'agent ne trade toujours pas :

1. **Le WM n'a jamais appris le bonus** → la prédiction de reward est
   MSE-minimisante vers 0. Vérifier `reward_loss` dans les logs (pas juste
   le format `.4f` — utiliser `metrics.json` pour la valeur brute).
4. **Le reward_loss est visible mais WM prédit 0** : le `rwd=0.0000` dans les logs masque le vrai MSE. Vérifier avec `metrics.json` si `reward_loss` est vraiment à zéro. Si oui, le WM n'a jamais appris le bonus → augmenter le bonus ou vérifier la MSE du symlog.
   Pour des trades qui durent 10-50 bars, c'est suffisant.
3. **L'avantage imaginaire est bruité** → augmenter le nombre de steps AC
   par épisode (passer de 2 à 4, voire 8).

#### E (V5 — DÉFINITIF) Reward Head à Action Explicite sur GPU dédié

**Quand appliquer :** toutes les approches A-D ont été testées et l'agent
fait toujours HOLD. Le reward_head collapse vers la moyenne des rewards, le
WM loss → 0, l'entropie stagne à 1.38, aucune amélioration après 200+ épisodes.

**Cause racine :** le RSSM prior (sans observation) ne produit pas des états
assez différenciés pour qu'un MLP 2×512 distingue HOLD de BUY. Le reward_head
voit des états quasi-identiques pour des actions aux rewards très différents.

**Solution radicale en 3 changements simultanés :**

1. **Action en input explicite** — `reward_head(stoch + deter + ACTION)`
   L'action one-hot est concaténée à l'état RSSM. Pendant l'imagination,
   l'action choisie par l'actor est passée directement.

2. **Reward_head massif** — 3×2048 (9.5M params) au lieu de 2×512 (~3M).
   La capacité supplémentaire permet d'apprendre le mapping état+action→reward
   sans collapse.

3. **GPU dédié** — reward_head sur GPU1 avec l'AC (GPU0 garde JEPA+RSSM).
   Load balance : 22M GPU0, 12M GPU1. Total 24M params vs 15.6M avant.

```python
# RSSMWorldModel.__init__ — reward_head avec action
rwd_in_dim = stoch_size * stoch_classes + deter_size + action_dim  # +8
self.reward_head = nn.Sequential(
    nn.Linear(rwd_in_dim, 2048), nn.LayerNorm(2048), nn.GELU(),
    nn.Linear(2048, 2048), nn.LayerNorm(2048), nn.GELU(),
    nn.Linear(2048, 1024), nn.GELU(),
    nn.Linear(1024, 1)
)

# predict_reward — action optionnelle, padding si absent
def predict_reward(self, stoch, deter, action=None):
    if action is None:
        action = torch.zeros(stoch.shape[0], self.action_dim, device=stoch.device)
    x = torch.cat([stoch.reshape(stoch.shape[0], -1), deter, action], dim=-1)
    # Auto-déplacement sur GPU1 si reward_head y est
    rwd_device = next(self.reward_head.parameters()).device
    if x.device != rwd_device:
        x = x.to(rwd_device)
    return self.reward_head(x)

# imagine() — passer l'action imaginaire
for step in range(horizon):
    action = policy(state)
    reward = self.predict_reward(stoch, deter, action)  # ← action explicite
    stoch, _, deter, _ = self.transition(prev_stoch=stoch, prev_action=action)

# train_world_model() — cross-device reward loss
pred_reward = wm.predict_reward(post, deter_next, action_t)  # GPU1
target_rwd = symlog(rewards).to(rwd_dev)  # GPU0→GPU1
posterior_loss = F.mse_loss(pred_reward, target_rwd)  # GPU1
pred_prior = wm.predict_reward(prior, deter_next, action_t)
prior_loss = F.mse_loss(pred_prior, target_rwd)
reward_loss = ((posterior_loss + prior_loss) / 2.0).to(device_wm)  # → GPU0
wm_loss = reward_loss + 0.1 * kl_loss  # tout sur GPU0
```

**⚠️ Piège — dimension input constante :** le reward_head a une couche
`Linear(rwd_in_dim, 2048)`. Chaque appel doit fournir EXACTEMENT cette
dimension, action présente ou non. Toujours utiliser le padding zéro.

**⚠️ Piège — load/save cross-device :** après `torch.load(map_location='cpu')`,
il faut replacer le reward_head sur GPU1 manuellement car le state_dict ne
conserve pas le device.

```python
def load(self, path):
    ckpt = torch.load(path, map_location='cpu')
    self.world_model.load_state_dict(ckpt['world_model'])
    self.world_model.to(self.device_wm)  # RSSM → GPU0
    self.world_model.reward_head = self.world_model.reward_head.to(self.device_ac)  # → GPU1
```

**Résultat attendu :** `posterior_loss > 0`, `prior_loss > 0`, `wm_loss > 0.01`
(contre 0.0003 sans le fix). L'avantage imaginaire devient non-nul car les
actions produisent des rewards différents : HOLD → ~ -0.005, BUY → ~ +0.20.

**⚠️ Contre-intuitif — le warm-up devient INUTILE avec V5.** L'action
explicite donne au reward_head assez de signal pour apprendre sans warm-up
RSSM. On retire complètement le warm-up, le compteur d'épisode, et le gel d'AC.
Le reward_head + AC s'entraînent dès l'épisode 0.

#### E.1 — Intensifier l'entraînement AC (CRITIQUE pour la convergence)

Même avec le reward_head V5, l'AC peut stagner si le nombre de steps
d'entraînement par épisode est trop faible. Le signal d'avantage entre
HOLD et BUY existe (~0.06 symlog) mais est dilué sur 30 steps d'horizon.

**Deux leviers combinés qui ont prouvé leur efficacité :**

| Levier | Avant | Après | Effet |
|--------|-------|-------|-------|
| **Horizon imagination** | 30 | **15** | Moins de bruit PnL → avantage plus net |
| **AC steps/épisode** | 4 | **16** | 4× plus de signal → convergence rapide |
| **WM steps/épisode** | 8 | 8 | Inchangé |
| **Épisodes** | 200 | **500** | Laisser le temps à l'AC de converger |

**Résultat observé :** l'entropie passe de 2.079 à 1.322 en 8 épisodes
(contre stagnation à 1.38 avec 4 steps et horizon 30). La politique sort
enfin de l'uniforme.

```python
# train.py — configuration optimale V5
agent = DreamerV3AgentV2(..., horizon=15)  # au lieu de 30

# _train_step() — 16 AC steps au lieu de 4
for _ in range(16):  # ← critique
    batch = self.replay.sample(512)
    result = self.agent.train_actor_critic(batch)
```

**⚠️ Pourquoi horizon=15 est suffisant :** un trade FTMO typique dure
10-50 bars (M15). L'horizon 15 couvre l'ouverture + quelques bars de
PnL + la fermeture. L'horizon 30 rajoute 15 bars de bruit PnL
supplémentaire qui dilue le signal d'ouverture (+0.20). L'avantage
BUY-first sur 15 steps ≈ 0.20 × Σγ^t ≈ 0.20 × 14.8 ≈ +2.96.
L'avantage HOLD sur 15 steps ≈ -0.005 × 14.8 ≈ -0.07.
Différence ≈ 3.0 — l'AC a un signal fort.

**⚠️ L'overhead des 16 AC steps est acceptable :** ~16s/épisode au lieu
de ~14s. Sur 500 épisodes : +16 minutes. Le gain en qualité de politique
justifie largement ce coût.

### Spread variable

Au lieu d'un spread fixe, le modéliser comme :

```python
spread = base_spread * session_mult * volatility_mult + random_noise
```

- **Session multiplier** : Asia=1.5x, London/NY open=0.8x, close=2.0x
- **Volatility multiplier** : basé sur ATR normalisé
- **Random noise** : gaussien ±30% du spread moyen

### Slippage proportionnel

```python
slippage = spread * base_slippage_pct * gaussian_noise
```
- Slippage sur l'exécution des SL/TP en utilisant H/L de la barre
- Plus de slippage en haute volatilité

### Commission MT5

```python
commission = $7 par lot standard
commission_total = lots * commission_per_lot
```

## Features Multi-Timeframes

### Architecture

4 timeframes, chacune avec les mêmes 69 features normalisées en z-score :

| TF | Résampling | Lookback | Features |
|----|------------|----------|----------|
| M15 | natif | 48 bars | 69 |
| H1 | 4 × M15 | 24 bars | 69 |
| H4 | 16 × M15 | 12 bars | 69 |
| D1 | 96 × M15 | 5 bars | 69 |

Total : 276 features + 7 corrélations + 8 embedding symbole + 5 positions = **296 features (obs_dim)**

### Features clés à inclure

1. **Returns** : ret, log_ret, ret_{4,8,16,32,48}
2. **RSI** : + slope (momentum du RSI)
3. **MACD** : macd, signal, histogram + slope
4. **Bollinger** : position, width (volatilité)
5. **ATR** : atr_norm + slope
6. **HV** : historique volatilité 10/20/30 bars + ratio
7. **ADX** : adx, di_diff + slope
8. **Volume** : ratio, z-score
9. **VWAP** : distance au VWAP
10. **Stochastic** : K, D + slope
11. **Price Action** : body_ratio, wick_ratio, doji, hammer, engulfing
12. **Range Position** : sur 8/24/48 bars
13. **Spread** : spread estimé + z-score
14. **Sessions** : asia, london, ny, overlap, close
15. **Lags** : shift -1, -2 sur features principales
16. **Corrélations inter-symboles** : rolling window 96 bars

### Normalisation

```python
z_score = (value - rolling_mean) / (rolling_std + 1e-8)
clipped = clip(z_score, -5, 5)
```

- Rolling window : lookback × 4 bars
- Pas de look-ahead bias (rolling, pas global)
- Clipping à ±5 pour éviter les outliers

## Leçon ultime — Credit Assignment Temporel (Juillet 2026)

Après 10+ itérations de correctifs (DreamerV3 V4→V5, PPO LSTM, ES),
le verdict est sans appel : **aucun algorithme RL n'apprend à trader
sans reward dense ET auto-close.**

### Test synthétique décisif

Un environnement `TrendingEnv` (prix +0.1%/step, 4 actions) a été créé
pour isoler le problème :

| Configuration | ES (20 gens) | PPO (30 iters) |
|---|---|---|
| Sans PnL dans l'obs, reward au CLOSE | 0 trades | 0 trades |
| PnL non-réalisé visible dans l'obs | 0 trades | 0 trades |
| **Reward dense (delta PnL/step) + auto-close** | Apprend BUY ✅ | (test en cours) |

### Pourquoi

BUY→HOLD→CLOSE est une chaîne de 3 décisions séparées par des dizaines
de timesteps. L'agent ne reçoit le signal de récompense qu'au CLOSE.
La probabilité d'exécuter toute la chaîne par exploration aléatoire est
~0.5%. Sans signal intermédiaire, l'agent ne découvre jamais le lien
causal entre BUY et le PnL final.

### Conditions nécessaires au succès (quel que soit l'algo)

1. **Reward dense à chaque step** — delta du PnL non-réalisé
2. **Auto-close après N steps** — force la réalisation des gains
3. **Features d'état de position dans l'observation** — PnL latent, direction
4. **Exploration ≥ 30%** — pour découvrir la chaîne d'actions

Sans ces 4 conditions, aucun algorithme (DreamerV3, PPO, ES, SAC, DQN)
n'apprendra à trader, quel que soit le budget computationnel.