# Patterns de Code — RL Trading (V5.1)

> ⚠️ V5.1 = BUY/SELL DÉGELÉS (seul HOLD reste gelé).
> V5 (obsolète) gelait HOLD+BUY+SELL → Pattern #8 (overtrade symétrique).
> Voir Pattern #14 pour la limite de V5.1 : le bias symétrique BUY=+3/SELL=+3
> ne permet pas au gradient ES d'apprendre la direction.

## ESPolicy V5.1 : seul HOLD gelé, BUY/SELL libres

```python
class ESPolicy(nn.Module):
    def __init__(self, input_dim=296, hidden_dim=128, action_dim=8, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, action_dim, bias=False)  # PAS de bias natif
        )
        # HOLD=0, BUY=1, SELL=2, CLOSE=3, SPLIT_BUY=4, SPLIT_SELL=5, PYRAMID=6, PARTIAL_CLOSE=7
        action_bias = torch.zeros(action_dim)
        action_bias[0] = -4.0    # HOLD  ← fortement pénalisé
        action_bias[1] = +3.0    # BUY   ← fortement favorisé
        action_bias[2] = +3.0    # SELL  ← fortement favorisé
        action_bias[3] = +0.5    # CLOSE ← léger encouragement
        action_bias[4] = +1.5    # SPLIT_BUY
        action_bias[5] = +1.5    # SPLIT_SELL
        # PYRAMID(6), PARTIAL_CLOSE(7) = 0
        self.register_buffer('action_bias', action_bias)

        # V5.1: SEUL HOLD est gelé. BUY et SELL sont DÉGELÉS.
        self.register_buffer('frozen_action_mask', torch.ones(action_dim))
        self.frozen_action_mask[0] = 0.0  # HOLD → gelé (bias seul)
        # BUY(1) et SELL(2) = 1.0 → le LSTM peut moduler le bias

    def forward(self, x, hidden=None):
        out, h = self.lstm(x, hidden)
        logits = self.head(out[:, -1, :])
        # Canaux gelés (HOLD) = bias seul. Canaux libres = logits + bias.
        return logits * self.frozen_action_mask + self.action_bias, h

    def count_params(self):
        return sum(p.numel() for p in self.parameters())
```

**⚠️ Pattern #14 — Limite de V5.1** : Avec BUY=+3.0 et SELL=+3.0 (symétriques),
le gradient ES ne peut pas apprendre la direction. Après 28 générations,
`buy_sell_gap ≈ 0.00` pour tous les symboles. Solution : injecter un signal
de direction asymétrique basé sur les features (voir Pattern #14 dans SKILL.md).

**Pourquoi seul HOLD est gelé** : HOLD doit rester purement bias-driven pour
éviter le collapse "zéro trade" (le réseau apprend à tout HOLDer car c'est
sécurisé). BUY et SELL doivent être libres pour que le LSTM apprenne la
direction en fonction des features de marché.

## Antithetic sampling V5.1 — MÊME marché

```python
def evaluate_population(self, envs, steps=1000):
    master_vec = self._get_params_flat(self.master)

    # Étape 0: capturer l'état initial de CHAQUE env_plus
    env_states = []
    for env_plus in envs:
        env_states.append({
            'symbol': env_plus.current_symbol,
            'step': env_plus.current_step,
            'features': env_plus.features,
            'feature_names': env_plus.feature_names,
            'df': env_plus.df,
            'spec': env_plus.spec,
        })

    all_tasks = []

    # +ε : avec env normal (init_state=None → reset() standard)
    for i, ((policy_plus, noise, device), env_plus) in enumerate(zip(self.population, envs)):
        device_idx = i % len(self.devices)
        all_tasks.append((policy_plus, env_plus, device_idx, False, i, None))

    # -ε : MÊME état initial que +ε (BUGFIX V5)
    for i, ((_, noise, _), _) in enumerate(zip(self.population, envs)):
        device_idx = i % len(self.devices)
        anti_device = self.devices[device_idx]

        anti_policy = ESPolicy(...).to(anti_device)
        self._set_params_flat(anti_policy, master_vec.to(anti_device) - noise.to(anti_device))

        # Créer env frais mais injecter le MÊME état
        anti_env = MultiSymbolEnvV4(data_dict, ...)
        all_tasks.append((anti_policy, anti_env, device_idx, True, i, env_states[i]))

    # V5.1: max_workers = len(devices) * 2 (pas *3 — surcharge mémoire)
    with ThreadPoolExecutor(max_workers=len(self.devices) * 2) as executor:
        futures = {}
        for policy, env, device_idx, anti, idx, init_state in all_tasks:
            future = executor.submit(
                self._evaluate_one, policy, env, steps, device_idx, temperature, init_state
            )
            futures[future] = (anti, idx)

    # ...
    effective_fitness = [p - m for p, m in zip(fitness_plus, fitness_minus)]
    return effective_fitness, fitness_plus, fitness_minus
```

## _evaluate_one avec init_state

```python
def _evaluate_one(self, policy, env, steps, device_idx, temperature=1.0,
                  init_state=None):
    INITIAL_BALANCE = FTMO_CONFIG['account_size']
    ZERO_TRADE_PENALTY = 50.0
    device = self.devices[device_idx]

    if init_state is not None:
        # BUGFIX V5: utiliser le MÊME état que +ε
        env.current_symbol = init_state['symbol']
        env.features = init_state['features']
        env.feature_names = init_state['feature_names']
        env.df = init_state['df']
        env.spec = init_state['spec']
        env.current_step = init_state['step']
        # Init manuelle (pas de reset() aléatoire)
        env.balance = INITIAL_BALANCE
        env.peak_balance = env.balance
        env.daily_start_balance = env.balance
        env.prev_equity = env.balance
        env.positions = []
        env.trades_today = 0
        env.consecutive_losses = 0
        env.cooldown_until = 0
        env.last_trade_day = -1
        env.total_trades = 0
        env.winning_trades = 0
        env.buy_trades = 0
        env.sell_trades = 0
        env.episode_pnl = 0
        env.realized_pnl = 0
        env.bars_since_last_trade = 0
        env.max_dd_exceeded = False
        env.peak_equity = env.balance
        env.episode_reward = 0.0
        obs = env._get_obs()
    else:
        obs = env.reset()

    # ... boucle d'évaluation avec sampling stochastique ...
```

## evolve() V5.1 : magnitude-based + zeroing HOLD uniquement

```python
def evolve(self, fitness):
    ranked = sorted(enumerate(zip(fitness, self.population)),
                   key=lambda x: x[1][0], reverse=True)

    n_elite = max(1, int(self.pop_size * self.elite_frac))
    elite = ranked[:n_elite]

    # Pondération par rang
    ranks = np.arange(len(elite), 0, -1)
    weights = ranks / sum(ranks)

    # V5: magnitude-based (pas sign-based)
    elite_fitness = np.array([f for (f, _) in [x[1] for x in elite]])
    max_abs_fit = max(np.max(np.abs(elite_fitness)), 1.0)

    master_vec = self._get_params_flat(self.master)
    grad = torch.zeros_like(master_vec)

    for (idx, (fit, (_, noise, device))), w in zip(elite, weights):
        noise_primary = noise.to(self.primary_device)
        fit_clipped = np.clip(fit, -100, 100)
        # V5: pondéré par magnitude (pas np.sign → ±1 qui égalise tout)
        grad += w * noise_primary * (fit_clipped / max_abs_fit)

    grad = grad / max(1, n_elite)

    # V5.1: NaN guard — sauvegarder avant update, rollback si NaN
    old_master_vec = master_vec.clone()
    master_vec += self.lr * grad

    if torch.isnan(master_vec).any() or torch.isinf(master_vec).any():
        print(f"   ⚠️  NaN/Inf détecté après evolve! Update annulée.")
        master_vec = old_master_vec  # rollback
    else:
        self._set_params_flat(self.master, master_vec)

    # V5.1: remettre à zéro UNIQUEMENT HOLD (canal 0)
    # BUY/SELL sont libres d'apprendre
    with torch.no_grad():
        self.master.head[-1].weight.data[0] = 0.0  # HOLD uniquement

    self._create_population()
    self.generation += 1

    return {
        'best_fitness': elite_fitness[0],
        'mean_fitness': np.mean(fitness),
        'elite_mean': np.mean(elite_fitness),
        'grad_norm': round(grad.norm().item(), 6),
    }
```

## Fitness ES — PnL pur (PAS reward total)

```python
def _evaluate_one(self, ...):
    # ... boucle d'évaluation ...
    realized_pnl_pct = (env.balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100.0
    fitness = realized_pnl_pct

    if num_trades > 0:
        fitness += 2.0       # bonus activité modéré
    if num_trades == 0:
        fitness -= 50.0      # pénalité zéro-trade

    return fitness, num_trades
```

## Configuration ES recommandée (V5.1)

```python
ESAgent(
    input_dim=296, hidden_dim=128, action_dim=8,
    pop_size=16, sigma=0.02, lr=0.1,
    elite_frac=0.25, devices=('cuda:0', 'cuda:1'),
    temp_start=1.5, temp_end=0.3, temp_decay_gens=150
)
# Évaluation: 1000 steps, stochastique, antithetic corrigé
# Fitness: PnL pur (balance finale) + bonus activité 2%
# Bias: HOLD=-4.0, BUY/SELL=+3.0 (⚠️ symétrique → Pattern #14)
# frozen_action_mask: SEUL HOLD gelé, BUY/SELL libres
# max_workers: len(devices) * 2 (pas *3)
# NaN guard: old_master_vec.clone() + rollback
# ~100s/gen avec pop=16 sur 2× RTX 3090 (~5h pour 200 gens)
```

## Reward dense (100% steps non-nuls)

```python
# Dans environment.step() :
self.bars_since_last_trade += 1
decay = -0.02 * (self.bars_since_last_trade / 48.0)
decay = max(-0.02, decay)
reward += decay                          # time-decay

if self.positions:
    reward += 0.005                      # holding bonus

if opened_position:
    reward += exp_bonus                  # 0.20 phase 1, 0.01 phase 2
    self.bars_since_last_trade = 0

pnl_scale = cfg.get(f'phase{phase}_pnl_scale', 1.0)
reward += equity_change * pnl_scale      # ×100 en phase 1
```

## Auto-close dans l'environnement

```python
# Dans environment.step(), après check SL/TP :
elif pos.unrealized_pnl(current_price) > 0 and pos.bars_held >= 20:
    positions_to_close.append((i, 'AUTO_PROFIT'))
```

## Init manuelle de validation (PAS de reset())

```python
def _validate(self):
    env = MultiSymbolEnvV4(data_dict, curriculum_episode=9999)
    env.current_symbol = 'XAUUSD'
    env.features, env.feature_names, env.df = data_dict['XAUUSD']
    env.spec = SYMBOLS['XAUUSD']
    env.current_step = env.lookback + len(env.df) - 3000
    # PAS de reset() — init manuelle
    env.balance = FTMO_CONFIG['account_size']
    env.peak_balance = env.balance
    env.daily_start_balance = env.balance
    env.prev_equity = env.balance
    env.positions = []
    env.trades_today = 0
    env.consecutive_losses = 0
    env.cooldown_until = 0
    env.last_trade_day = -1
    env.total_trades = 0
    env.winning_trades = 0
    env.buy_trades = 0
    env.sell_trades = 0
    env.episode_pnl = 0
    env.realized_pnl = 0
    env.bars_since_last_trade = 0
    env.max_dd_exceeded = False
    env.peak_equity = env.balance
    env.episode_reward = 0.0
    obs = env._get_obs()
```

## Dual GPU avec ThreadPoolExecutor

```python
devices = ('cuda:0', 'cuda:1')
# V5.1: max_workers = len(devices) * 2 (pas *3 — surcharge mémoire GPU)
max_workers = len(devices) * 2  # 4 workers pour 2 GPUs

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {}
    for policy, env, device_idx, anti, idx, init_state in all_tasks:
        future = executor.submit(
            self._evaluate_one, policy, env, steps, device_idx, temperature, init_state
        )
        futures[future] = (anti, idx)
    for future in as_completed(futures):
        ...
```

## Test synthétique de capacité

```python
class TrendingEnv:
    """Marché qui monte de +0.1%/step avec bruit."""
    def __init__(self, lookback=48):
        self.lookback = lookback
        self.price = 100.0
        self.balance = FTMO_CONFIG['account_size']
        self.position = None  # (direction, entry_price)
        self.total_trades = 0
        self.winning_trades = 0

    def step(self, action):
        # Price up with noise
        self.price *= 1.001 + np.random.randn() * 0.0005

        # DENSE reward: delta PnL
        old_unrealized = position_pnl if position else 0
        # ... update price ...
        new_unrealized = position_pnl if position else 0
        reward = new_unrealized - old_unrealized

        # Auto-close after 50 steps
        if position and steps_since_open > 50:
            close_position()

    def get_action_mask(self):
        mask[HOLD] = True
        mask[BUY] = self.position is None
        mask[SELL] = self.position is None
        mask[CLOSE] = self.position is not None
        return mask
```

## Diagnostic : logits en validation

```python
# Quand la validation fait 0 trades, logger les logits
if env.total_trades == 0 and first_logits is not None:
    top_actions = np.argsort(first_logits)[::-1][:4]
    top_str = " | ".join(
        f"{ACTION_NAMES[a]}={first_logits[a]:+.2f}"
        for a in top_actions if not np.isinf(first_logits[a])
    )
    mask_names = [ACTION_NAMES[i] for i, m in enumerate(env.get_action_mask()) if m]
    print(f"🔍 DEBUG: 0 trades | top_logits={top_str} | mask={mask_names}")

# Diagnostic supplémentaire V5: gap BUY-HOLD
buy_hold_gap = logit[BUY] - logit[HOLD]
if buy_hold_gap < 1.0:
    print(f"⚠️  buy_hold_gap={buy_hold_gap:.2f} — le bias est contré par le réseau")

# V5.1: gap BUY-SELL (direction apprise ?)
buy_sell_gap = logit[BUY] - logit[SELL]
if abs(buy_sell_gap) < 0.5:
    print(f"⚠️  buy_sell_gap={buy_sell_gap:.2f} — direction non apprise (Pattern #14)")
```

## Curriculum Learning

```python
CURRICULUM_CONFIG = {
    "enabled": True,
    "phase1_episodes": 200,       # pas de spread, pas de commission
    "phase1_spread_mult": 0.0,
    "phase1_pnl_scale": 100.0,    # amplifier le PnL ×100
    "phase1_exploration_bonus": 0.20,
    "phase2_episodes": 300,       # 30% spread
    "phase2_spread_mult": 0.3,
    "phase2_pnl_scale": 10.0,
    "phase2_exploration_bonus": 0.01,
    "phase3_spread_mult": 1.0,    # full frictions
}
```
