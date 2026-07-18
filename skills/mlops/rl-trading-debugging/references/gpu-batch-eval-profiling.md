# GPU Batch Evaluation Profiling — ES V7 (2026-07-17)

> Session-specific benchmark data for Pattern #19.
> Hardware: 2× RTX 3090 (24GB each), 32 CPUs, PyTorch 2.6+cu124, Python 3.13.

## Problem

Original `es_agent_v7.py` used `ThreadPoolExecutor` with 16 sequential
`_evaluate_one` calls, each doing forward L=lookback (48 timesteps) batch=1
on GPU. Result: 47s/generation for pop=16, eval=500 steps, antithetic.

## Profiling methodology

Isolated each component (forward, mask+sample, env.step) with explicit
`time.time()` + `torch.cuda.synchronize()` around GPU operations.

## Key benchmarks

### Forward pass comparison (hd=512, P=16, L=48)

| Method | Time/iter | Notes |
|--------|-----------|-------|
| `functional_call` loop (16× batch=1) | 18.25ms | Overhead per call dominates |
| 16 × `nn.LSTM` batch=1 (separate modules) | 2.86ms | cuDNN kernel, no overhead |
| `torch.vmap` + `functional_call` | **CRASH** | cuDNN `flatten_parameters` fails |
| Custom `bmm` LSTM (batched weights) | 15.22ms | L=48, too many timesteps |
| Custom `bmm` LSTM L=1 | 0.45ms | Best, but needs manual LSTM |
| `nn.LSTM` batch=16 shared weights | 0.33ms | Can't use (different weights per policy) |

### L=1 incremental stepping (the key insight)

Instead of forwarding L=48 timesteps at every step, initialize the LSTM
hidden state once with L=48, then forward L=1 for subsequent steps.

| Mode | Forward/step | Speedup |
|------|-------------|---------|
| L=48 every step (original) | 18.8ms | 1× |
| L=1 after init (optimized) | 4.9ms | 3.8× |

### Mask+sample optimization

| Method | Time/step |
|--------|-----------|
| Per-policy mask+sample (16× individual) | 5.5ms |
| Batched mask+sample (1× on `(P,5)` tensor) | 1.8ms |

### env.step parallelism

| Method | Time (16 envs × 100 steps) |
|--------|---------------------------|
| Sequential | 0.42s (4.2ms/step) |
| ThreadPoolExecutor(16) | 1.17s (11.7ms/step) — GIL kills it |
| multiprocessing.Pool | Impractical (15MB env pickling) |

### CUDA streams (2 GPUs, 8+8 split)

| Method | Time/step |
|--------|-----------|
| Sequential (8 GPU0 + 8 GPU1) | 4.67ms |
| Streams (8 GPU0 ‖ 8 GPU1) | 4.65ms — no speedup |

## Final architecture (13s/gen)

```python
# 1. Create P separate modules on GPU
self.population_models = [
    ESPolicyV7(input_dim, hidden_dim, action_dim).to(device)
    for i in range(pop_size)
]

# 2. Set weights via set_params_flat (master ± noise)
def _update_population_models(self, sign=+1.0):
    master_vec = get_params_flat(self.master)
    for i, model in enumerate(self.population_models):
        device = next(model.parameters()).device
        params = master_vec.to(device) + sign * self.noises[i].to(device)
        set_params_flat(model, params)

# 3. Init: forward L=lookback for LSTM hidden state
logits_batch = torch.zeros(P, action_dim, device=primary_device)
for i in range(P):
    obs_t = torch.from_numpy(obs_list[i]).unsqueeze(0).to(device)
    logits_i, hidden_states[i] = model(obs_t, hidden_states[i])
    logits_batch[i] = logits_i.to(primary_device)

# 4. Main loop: mask+sample batched, then env.step sequential, then forward L=1
for step_i in range(steps):
    # Batched mask+sample
    masks = np.stack([envs[i].get_action_mask() for i in range(P)])
    masks_t = torch.from_numpy(masks).to(primary_device)
    logits_masked = logits_batch.masked_fill(~masks_t, float('-inf'))
    actions = torch.multinomial(F.softmax(logits_masked/temp, dim=-1), 1)

    # Sequential env.step
    for i in range(P):
        if active[i]:
            obs_list[i], _, done, _ = envs[i].step(int(actions[i]))

    # Forward L=1 for next step
    last_obs = np.stack([obs_list[i][-1] for i in range(P)])
    last_obs_t = torch.from_numpy(last_obs).to(primary_device)
    for i in range(P):
        if active[i]:
            obs_i = last_obs_t[i:i+1].to(device).unsqueeze(0)  # (1,1,F)
            logits_i, hidden_states[i] = model(obs_i, hidden_states[i])
            logits_batch[i] = logits_i.to(primary_device)
```

## What didn't work

1. **`torch.vmap` with `nn.LSTM`**: `RuntimeError: shape '[10240, 1]' is
   invalid for input of size 163840` — cuDNN's `flatten_parameters` cannot
   handle batched weights. This is a fundamental limitation.

2. **`functional_call` in a loop**: Works but 6× slower than separate
   modules due to per-call overhead. Not suitable for >8 policies.

3. **ThreadPoolExecutor for env.step**: GIL prevents parallelism for
   numpy/pandas code. Sequential is 2.8× faster.

4. **CUDA streams for small kernels**: Kernels are too small (0.18ms each)
   to benefit from stream parallelism. No measurable speedup.

5. **`torch.compile` on nn.LSTM**: cuDNN kernel is already optimal.
   Compile adds overhead (0.31ms vs 0.29ms).

## Next step: custom bmm LSTM (6.3s/gen theoretical)

A custom LSTM using `torch.bmm` with batched weights `(P, 4*hd, F)` in
L=1 mode achieves 0.45ms/step (vs 2.86ms for 16×nn.LSTM). This would
bring total to ~6.3s/gen. Requires:
- Manual extraction of LSTM weights from flat vector
- Custom forward with `torch.bmm` for gate computation
- Manual LayerNorm + head with batched weights
- Not yet implemented in production code
