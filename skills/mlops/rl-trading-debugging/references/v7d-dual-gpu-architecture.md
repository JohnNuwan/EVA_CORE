# Architecture V7d — Dual-GPU antithetic parallèle + VRAM optimisée

## Contexte

V7c utilisait 0.83 GB de VRAM sur 24 GB (3.4%), GPU 1 inutilisé.
V7d corrige avec dual-GPU antithetic parallèle, noises sur CPU, et
_set_weights_param_by_param pour économiser la VRAM.

Évolution: V5.1 → V6 → V7 → V7b → V7c → **V7d (dual-GPU, h=2048, pop=64)**

## Fichiers du projet

```
/home/aza/ftmo_agent/
├── env_xauusd.py      — Environnement XAUUSD (5 actions, SLBE, Sharpe reward)
├── es_agent_v7.py     — Agent ES V7d (dual-GPU, batch GPU, TF32 module-level)
├── arena_v7.py        — Arena darwinienne (WR>55%, PF>1.3, DD<5%)
├── train_v7.py        — Trainer (200 gens, pop=64, steps=500, h=2048, dual GPU)
└── checkpoints_v7/    — Logs, métriques, registry, champions
```

## Différences clés V7c → V7d

| Aspect | V7c | V7d |
|--------|-----|-----|
| pop_size | 16 | **64** |
| hidden_dim | 512 (3.5M params) | **2048 (54.7M params)** |
| Dual-GPU | Non | **Oui (+ε GPU 0 \|\| -ε GPU 1)** |
| TF32 | Dans `__init__` | **Module-level (top du fichier)** |
| Noises | Sur GPU | **Sur CPU** (économise 6-13 GB VRAM) |
| set_weights | Alloue un tensor temporaire | **In-place (`copy_` + `add_`)** |
| VRAM GPU 0 | 0.83 GB (3.4%) | **17.9 GB (73%)** |
| VRAM GPU 1 | 0 GB (0%) | **19.5 GB (79%)** |
| Temps/gen | 26s | 112s |
| Politiques × params | 56M total | **3.5B total** |

## Architecture V7d

### 1. TF32 au niveau module (PAS dans __init__)

```python
# TOP de es_agent_v7.py — AVANT tout import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cudnn.benchmark = True
```

**PITFALL** : Si TF32 est activé dans `__init__`, les premiers imports torch
peuvent déjà avoir initialisé les flags. Il faut les mettre au top du fichier.

### 2. Dual BatchedPolicyV7 (un par GPU)

```python
# Dans ESAgentV7.__init__:
self.batched_policy = BatchedPolicyV7(
    input_dim, hidden_dim, action_dim, num_layers, pop_size
).to(self.primary_device)  # GPU 0 — +ε

if self.dual_gpu:
    self.batched_policy_minus = BatchedPolicyV7(
        input_dim, hidden_dim, action_dim, num_layers, pop_size
    ).to(self.secondary_device)  # GPU 1 — -ε
```

### 3. Noises sur CPU

```python
# Au lieu de (V7c):
self.noises = torch.randn(pop_size, n_params, device=self.primary_device) * sigma
# V7d:
self.noises = torch.randn(pop_size, n_params) * sigma  # CPU

# Dans evolve():
for (idx, fit), w in zip(elite, weights):
    noise_i = self.noises[idx].to(self.primary_device)  # CPU→GPU par élite
    grad += w * noise_i * (fit_clipped / max_abs_fit)

# Nouveaux noises:
self.noises = torch.randn(self.pop_size, self._total_params) * self.sigma  # CPU
```

### 4. _set_weights_param_by_param (VRAM minimal)

Transfère chaque paramètre séparément au lieu de tout allouer sur GPU:

```python
def _set_weights_param_by_param(self, master_flat, noises, device):
    offset = 0
    for name, shape in self._param_shapes.items():
        n = int(np.prod(shape))
        master_slice = master_flat[offset:offset + n]
        noise_slice = noises[:, offset:offset + n]  # CPU
        param = self.batched_weights[name]  # GPU
        master_gpu = master_slice.to(device)
        noise_gpu = noise_slice.to(device)
        param.data.copy_(master_gpu.view(1, *shape).expand_as(param.data))
        param.data.add_(noise_gpu.view(self.pop_size, *shape))
        del master_gpu, noise_gpu
        offset += n
```

### 5. Antithetic parallèle via threading

```python
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

**PITFALL** : Pools ThreadPoolExecutor séparés obligatoires. Sinon
`map()` retourne un générateur paresseux non-indexable
(`TypeError: 'generator' object is not subscriptable`).

### 6. _run_batch_episode paramétrable

La méthode accepte `policy`, `device`, `pool` pour router vers le bon GPU:

```python
def _run_batch_episode(self, envs, steps, temperature,
                       init_states=None, policy=None, device=None, pool=None):
    _policy = policy if policy is not None else self.batched_policy
    _device = device if device is not None else self.primary_device
    # ... tous les .to(self.primary_device) remplacés par .to(_device)
```

## Multiprocessing.Pool — TESTÉ ET REJETÉ

### Benchmark (pop=64, h=2048, 100 steps)

| Approche | Temps/100 steps | Notes |
|----------|-----------------|-------|
| ThreadPool (V7d) | 22.4s | Générateur paresseux OK |
| Multiprocessing.Pool | 38.7s | IPC overhead > gain CPU |

### Pourquoi multiprocessing est plus lent

1. Chaque step: 64 × (pickle obs (48×20 float32) + mask (5 bool) + info dict)
   ≈ 256 KB transféré par step
2. 1000 steps × 256 KB × 2 antithetic = 51.2 MB de transfert IPC total
3. Le worker retourne obs complète + mask + info à chaque step → pickle cost

### Implémentation testée (désactivée)

```python
# Worker global — créé une fois par processus
_worker_envs = {}
_worker_df = None

def _mp_init_worker(df_data):
    global _worker_df
    _worker_df = df_data

def _mp_step_worker(args):
    env_id, action, init_state = args
    # ... créer/reset env si besoin
    obs, _, done, info = env.step(action)
    next_obs = env._get_obs()  # (lookback, F) — coûteux à pickler
    mask = env.get_action_mask()
    return env_id, next_obs, done, mask, env_info
```

La méthode `_init_mp_pools` existe toujours dans `es_agent_v7.py` mais est
désactivée (pass). Le code multiprocessing est conservé pour référence future.

## Configuration recommandée

```bash
python train_v7.py --gens 200 --pop 64 --steps 500 --sigma 0.02 --lr 0.1
```

- 112s/génération sur 2× RTX 3090 (h=2048, dual-GPU, TF32)
- 200 générations ≈ 6h
- VRAM: 17.9 GB GPU 0 (73%), 19.5 GB GPU 1 (79%)
- Validation Arena toutes les 10 générations

## Résultats V7d (premières générations)

| Gen | Temps | best_fitness | mean_fitness | Notes |
|-----|-------|-------------|-------------|-------|
| 0 | 114.5s | +11.97 | -1.25 | val WR=43.6% PF=0.71 |
| 1 | 111.8s | +12.58 | +0.77 | — |
| 2 | 109.3s | +18.85 | -1.07 | — |
| 3 | 112.8s | +20.56 | -0.12 | Progression constante |

## Vrais bottlenecks restants

1. **env.step CPU** : 0.39ms × 64 envs / 32 threads ≈ 0.78ms théorique
   mais 145ms en pratique (overhead GIL sur code Python pur)
2. **IPC obs** : (48, 20) float32 = 3.8 KB × 64 = 244 KB par step à
   transférer CPU→GPU
3. **Solution ultime** : vectoriser env.step sur GPU (tensors au lieu d'objets
   Python). Nécessite un rewrite complet de env_xauusd.py.
