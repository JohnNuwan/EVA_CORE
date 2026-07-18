#!/usr/bin/env python3
"""Script de vérification ES policy V5.1 — frozen_action_mask, NaN guard, évolution.
À exécuter après toute modification de es_agent.py. 7 tests.
Usage: python3 references/verify-es-policy.py
"""
import sys
sys.path.insert(0, '.')
import torch
import numpy as np
from es_agent import ESPolicy, ESAgent

errors = 0

# 1. frozen_action_mask: SEUL HOLD gelé (V5.1 — BUY/SELL dégelés)
p = ESPolicy(296, 128, 8)
mask = p.frozen_action_mask.tolist()
assert mask == [0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], f"mask={mask}"
print("1. frozen_action_mask: HOLD=0 (gelé), BUY/SELL=1 (libres)  ✅")

# 2. forward: BUY/SELL diffèrent (poids non-nuls car dégelés V5.1)
p = ESPolicy(296, 128, 8)
for w in p.head[-1].parameters():
    torch.nn.init.normal_(w, mean=0, std=0.5)
x = torch.randn(1, 48, 296)
logits, _ = p(x)
assert not torch.isnan(logits).any()
buy, sell = logits[0, 1].item(), logits[0, 2].item()
assert abs(buy - sell) > 0.001, f"BUY={buy:.4f} SELL={sell:.4f}"
print(f"2. forward: BUY={buy:.2f} SELL={sell:.2f}  ✅")

# 3. HOLD weight = 0 après evolve (seul HOLD est remis à zéro)
agent = ESAgent(296, 128, 8, 4, 0.02, 0.1)
agent.evolve([1.0, 0.5, 0.2, -0.5])
hw = agent.master.head[-1].weight.data[0]
assert hw.abs().max().item() < 1e-6, f"HOLD weight={hw}"
print("3. evolve: head.weight[0] (HOLD) = 0  ✅")

# 4. NaN guard: master propre après evolve avec NaN
agent = ESAgent(296, 128, 8, 4, 0.02, 0.1)
agent.evolve([float('nan'), 0.5, 0.2, -0.5])
mf = agent._get_params_flat(agent.master)
assert not torch.isnan(mf).any() and not torch.isinf(mf).any()
print("4. NaN guard: master propre après evolve(NaN)  ✅")

# 5. empty_cache
for d in agent.devices:
    with torch.cuda.device(d):
        torch.cuda.empty_cache()
print("5. empty_cache: OK  ✅")

# 6. Intégration evaluate_population
from train_es import ESTrainer
trainer = ESTrainer(n_generations=1, pop_size=4, eval_steps=100, hidden_dim=64,
                    sigma=0.02, lr=0.1, save_dir='/tmp/hermes-verify-es')
envs = trainer._create_envs(0)
eff, fp, fm = trainer.agent.evaluate_population(envs, steps=100)
assert len(eff) == 4 and all(not np.isnan(f) for f in eff)
print(f"6. evaluate_population: pop=4, fitness={[f'{f:+.2f}' for f in eff]}  ✅")

# 7. _validate ne crash pas
vp, vt, vw = trainer._validate()
assert not np.isnan(vp)
print(f"7. _validate: PnL={vp:+.2f}% trades={vt} wr={vw:.0f}%  ✅")

print(f"\n{'🎉 7/7 OK' if errors == 0 else f'❌ {errors} erreurs'}")
