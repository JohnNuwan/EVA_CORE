---
name: stable-baselines3
description: Guide complet de Stable-Baselines3 — RL, PPO, SAC, TD3, DQN, A2C, environnements Gymnasium, callbacks, evaluation, et bonnes pratiques. En français.

---

# Stable-Baselines3 — Guide Complet (Français)

Bibliothèque d'apprentissage par renforcement basée sur PyTorch.

---

## 1. Installation et Concepts

```bash
pip install stable-baselines3[extra]
pip install gymnasium shimmy

# Pour MuJoCo
pip install mujoco
```

### Algorithmes disponibles
| Algorithme | Espace d'actions | Type |
|-----------|-----------------|------|
| PPO | Discret / Continu | On-policy |
| A2C | Discret / Continu | On-policy |
| DQN | Discret | Off-policy |
| SAC | Continu | Off-policy |
| TD3 | Continu | Off-policy |
| DDPG | Continu | Off-policy |
| HER | Discret / Continu | Replay buffer wrapper |

---

## 2. Premier Entraînement

```python
import gymnasium as gym
from stable_baselines3 import PPO, A2C, DQN, SAC, TD3
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor

# Créer l'environnement
env = gym.make("CartPole-v1")
env = Monitor(env)  # Pour le logging

# Créer et entraîner
model = PPO(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    verbose=1,
)

model.learn(total_timesteps=100_000)

# Évaluer
mean_reward, std_reward = evaluate_policy(
    model, env, n_eval_episodes=10, deterministic=True
)

print(f"Récompense moyenne : {mean_reward:.2f} ± {std_reward:.2f}")

# Sauvegarder / Charger
model.save("ppo_cartpole")
model = PPO.load("ppo_cartpole")

# Inférence
obs, _ = env.reset()
for _ in range(1000):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, _ = env.step(action)
    if terminated or truncated:
        obs, _ = env.reset()
```

---

## 3. PPO — Proximal Policy Optimization

```python
from stable_baselines3 import PPO

model = PPO(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    n_steps=2048,               # Étapes par rollout
    batch_size=64,              # Taille de batch pour l'update
    n_epochs=10,                # Époques par update
    gamma=0.99,                 # Facteur de discount
    gae_lambda=0.95,            # GAE λ
    clip_range=0.2,             # Clip ε pour PPO
    clip_range_vf=None,         # Clip pour le value function
    ent_coef=0.0,               # Coefficient d'entropie
    vf_coef=0.5,                # Coefficient du value loss
    max_grad_norm=0.5,          # Gradient clipping
    use_sde=False,              # State-dependent exploration
    target_kl=None,             # KL divergence cible (early stopping)
    policy_kwargs=dict(
        net_arch=dict(
            pi=[256, 256],      # Architecture du policy network
            vf=[256, 256],      # Architecture du value network
        ),
        activation_fn=torch.nn.ReLU,
    ),
    verbose=1,
)
```

---

## 4. SAC — Soft Actor-Critic

```python
from stable_baselines3 import SAC

model = SAC(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    buffer_size=1_000_000,
    learning_starts=1000,
    batch_size=256,
    tau=0.005,                  # Taux de mise à jour du réseau cible
    gamma=0.99,
    train_freq=1,               # Fréquence d'entraînement
    gradient_steps=1,           # Nombre de gradient steps par train_freq
    ent_coef="auto",            # Entropie auto-ajustée
    policy_kwargs=dict(
        net_arch=dict(
            pi=[256, 256],
            qf=[256, 256],
        ),
    ),
    verbose=1,
)

model.learn(total_timesteps=500_000)
```

---

## 5. DQN — Deep Q-Network

```python
from stable_baselines3 import DQN

model = DQN(
    "MlpPolicy",
    env,
    learning_rate=1e-3,
    buffer_size=100_000,
    learning_starts=50_000,
    batch_size=32,
    tau=1.0,
    gamma=0.99,
    train_freq=4,               # Fréquence d'entraînement (en étapes)
    gradient_steps=1,
    target_update_interval=1000,# Mise à jour du réseau cible
    exploration_fraction=0.1,   # Fraction du training avec exploration
    exploration_initial_eps=1.0,# ε initial
    exploration_final_eps=0.05, # ε final
    max_grad_norm=10,
    policy_kwargs=dict(
        net_arch=[256, 256],
    ),
    verbose=1,
)
```

---

## 6. Callbacks Personnalisés

```python
from stable_baselines3.common.callbacks import (
    BaseCallback, EvalCallback,
    CheckpointCallback, StopTrainingOnRewardThreshold,
)
import numpy as np

# Callback d'évaluation
eval_callback = EvalCallback(
    eval_env,
    best_model_save_path="./logs/best_model",
    log_path="./logs/results",
    eval_freq=10_000,
    deterministic=True,
    render=False,
    n_eval_episodes=5,
)

# Callback de checkpoint
checkpoint_callback = CheckpointCallback(
    save_freq=50_000,
    save_path="./logs/checkpoints",
    name_prefix="rl_model",
)

# Callback personnalisé
class CustomCallback(BaseCallback):
    """Callback personnalisé avec log TensorBoard."""
    
    def __init__(self, verbose=0):
        super().__init__(verbose)
    
    def _on_step(self) -> bool:
        # Ajouter un log personnalisé
        self.logger.record("custom/value", np.random.random())
        
        # Arrêt conditionnel
        if self.num_timesteps > 1_000_000:
            return False  # Arrêter l'entraînement
        return True

# Entraînement avec callbacks
model.learn(
    total_timesteps=500_000,
    callback=[eval_callback, checkpoint_callback, CustomCallback()],
    tb_log_name="ppo_experiment",
)
```

---

## 7. Réseaux Personnalisés (CNN, LSTM)

```python
import torch.nn as nn

# Policy CNN pour images
policy_kwargs = dict(
    features_extractor_class=NatureCNN,
    features_extractor_kwargs=dict(features_dim=512),
    net_arch=[256, 128],
)

model = PPO("CnnPolicy", env, policy_kwargs=policy_kwargs)

# Feature extractor personnalisé
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class CustomCNN(BaseFeaturesExtractor):
    """Extracteur de features personnalisé."""
    
    def __init__(self, observation_space, features_dim=256):
        super().__init__(observation_space, features_dim)
        n_input_channels = observation_space.shape[0]
        
        self.cnn = nn.Sequential(
            nn.Conv2d(n_input_channels, 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU(),
            nn.Flatten(),
        )
        
        with torch.no_grad():
            n_flatten = self.cnn(
                torch.as_tensor(observation_space.sample()[None]).float()
            ).shape[1]
        
        self.linear = nn.Sequential(
            nn.Linear(n_flatten, features_dim),
            nn.ReLU(),
        )
    
    def forward(self, observations):
        return self.linear(self.cnn(observations))
```

---

## 8. Environnements Personnalisés

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np


class MonEnv(gym.Env):
    """Environnement personnalisé."""
    
    metadata = {"render_modes": ["human"], "render_fps": 30}
    
    def __init__(self):
        super().__init__()
        
        # Espace d'actions : discret (0=gauche, 1=droite)
        self.action_space = spaces.Discrete(2)
        
        # Espace d'observations
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(4,), dtype=np.float32,
        )
        
        self.reset()
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.position = 0.0
        obs = np.array([self.position, 0.0, 0.0, 0.0], dtype=np.float32)
        return obs, {}
    
    def step(self, action):
        if action == 0:
            self.position -= 0.1
        else:
            self.position += 0.1
        
        reward = -abs(self.position)  # Rester près de 0
        terminated = abs(self.position) > 5.0
        
        obs = np.array([self.position, 0.0, 0.0, 0.0], dtype=np.float32)
        return obs, reward, terminated, False, {}
```

---

## 9. Vectorisation et Parallélisme

```python
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import (
    DummyVecEnv, SubprocVecEnv, VecNormalize,
)

# Environnements parallèles
vec_env = make_vec_env(
    "CartPole-v1",
    n_envs=8,
    seed=42,
    vec_env_cls=SubprocVecEnv,  # Multiprocessing
)

# Normalisation des observations/récompenses
vec_env = VecNormalize(
    vec_env,
    norm_obs=True,
    norm_reward=True,
    clip_obs=10.0,
)

model = PPO("MlpPolicy", vec_env, verbose=1)
model.learn(total_timesteps=1_000_000)

# Sauvegarder les stats de normalisation
vec_env.save("vec_normalize.pkl")
```

---

## 10. Hyperparameter Tuning

```python
import optuna
from stable_baselines3.common.evaluation import evaluate_policy


def optimiser_hyperparametres(trial):
    """Fonction objectif pour Optuna."""
    return {
        "learning_rate": trial.suggest_float("lr", 1e-5, 1e-2, log=True),
        "n_steps": trial.suggest_categorical("n_steps", [512, 1024, 2048]),
        "gamma": trial.suggest_float("gamma", 0.9, 0.9999),
        "gae_lambda": trial.suggest_float("gae_lambda", 0.8, 1.0),
        "ent_coef": trial.suggest_float("ent_coef", 0.0, 0.1),
    }

study = optuna.create_study(direction="maximize")
study.optimize(lambda trial: entrainer_et_evaluer(trial), n_trials=50)
```

---

## Références
- SB3 Docs : https://stable-baselines3.readthedocs.io/
- Gymnasium : https://gymnasium.farama.org/
- RL Zoo : https://github.com/DLR-RM/rl-baselines3-zoo