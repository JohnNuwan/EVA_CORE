---
name: reinforcement-learning
description: Guide complet de Deep Reinforcement Learning — PPO, GRPO, DPO, SAC, TD3, DreamerV3, Q-learning, algorithms, mathématique, implémentations. En français.
---

# Deep Reinforcement Learning — Guide Complet

Algorithmes, mathématiques, implémentations de PPO à DreamerV3.

---

## 1. Fondamentaux du RL

### Markov Decision Process (MDP)
```
Un MDP est défini par (S, A, P, R, γ) :
- S : états
- A : actions
- P(s'|s,a) : probabilité de transition
- R(s,a) : récompense immédiate
- γ ∈ [0,1] : facteur d'actualisation

Objectif : trouver π* = argmax_π E[Σ γ^t R_t]
```

### Boucle Agent-Environnement
```python
class Agent:
    def act(self, state) -> action:
        """Choisit une action selon la politique."""
        raise NotImplementedError

class Environment:
    def step(self, action) -> tuple[state, reward, done, info]:
        """Exécute l'action, retourne nouvel état et récompense."""
        raise NotImplementedError

# Boucle d'entraînement
state, _ = env.reset()
for episode in range(num_episodes):
    done = False
    episode_reward = 0
    while not done:
        action = agent.act(state)
        next_state, reward, done, truncated, info = env.step(action)
        agent.learn(state, action, reward, next_state, done)
        state = next_state
        episode_reward += reward
```

---

## 2. Taxonomie des Algorithmes RL

```
                    Reinforcement Learning
                   /                     \
          Value-Based                 Policy-Based
          (apprend V ou Q)            (apprend π)
              |                              |
          DQN, Double DQN,            REINFORCE, PPO
          Rainbow, C51                TRPO, A2C/A3C
              |                              |
              └──────────┬───────────────────┘
                         │
                   Actor-Critic
              (apprend V + π ensemble)
                        |
                    PPO, SAC, TD3,
                    DDPG, A2C, IMPALA
                        |
               ┌────────┴────────┐
          On-policy           Off-policy
          (PPO, A2C,          (SAC, TD3,
           IMPALA)             DQN, DDPG)
```

### On-policy vs Off-policy

| Critère | On-policy | Off-policy |
|---------|-----------|------------|
| Données de la politique | Même politique | Politique différente (buffer) |
| Sample efficiency | Faible | Élevée |
| Stabilité | Haute | Modérée |
| Exemples | PPO, TRPO, A2C | SAC, DQN, TD3 |

---

## 3. Policy Gradient Fondamental

### REINFORCE (Monte Carlo Policy Gradient)

∇J(θ) = E[ Σ_t ∇log π_θ(a_t|s_t) · G_t ]

Où G_t = Σ_{k=0}^{T-t} γ^k R_{t+k} (return cumulé)

```python
class REINFORCE(nn.Module):
    """Policy gradient vanilla."""
    def __init__(self, state_dim, action_dim, hidden=128):
        super().__init__()
        self.policy = nn.Sequential(
            nn.Linear(state_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, action_dim),
        )
        self.optimizer = optim.Adam(self.parameters(), lr=3e-4)
    
    def get_action_probs(self, state):
        logits = self.policy(state)
        return Categorical(logits=logits)
    
    def act(self, state):
        probs = self.get_action_probs(state)
        return probs.sample().item()
    
    def learn(self, episode):
        states, actions, rewards = episode
        G = 0
        returns = []
        for r in reversed(rewards):
            G = r + 0.99 * G
            returns.insert(0, G)  # discounted returns
        returns = torch.tensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)  # normalize
        
        loss = 0
        for s, a, G_t in zip(states, actions, returns):
            probs = self.get_action_probs(s)
            log_prob = probs.log_prob(a)
            loss += -log_prob * G_t  # maximize E[log π · G]
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
```

---

## 4. PPO — Proximal Policy Optimization (OpenAI, 2017)

### Formulation mathématique

```
L^CLIP(θ) = E_t[min(r_t(θ) · A_t, clip(r_t(θ), 1-ε, 1+ε) · A_t)]

Où r_t(θ) = π_θ(a_t|s_t) / π_θ_old(a_t|s_t) : ratio d'importance
A_t : avantage estimé
ε : clipping (typiquement 0.2)
```

### Implémentation complète
```python
class ActorCritic(nn.Module):
    """Réseau partagé actor-critic."""
    def __init__(self, state_dim, action_dim, hidden=256):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
        )
        self.actor = nn.Linear(hidden, action_dim)  # mean (continuous)
        self.critic = nn.Linear(hidden, 1)           # value
    
    def forward(self, state):
        features = self.encoder(state)
        action_mean = self.actor(features)
        value = self.critic(features)
        return action_mean, value


class PPO:
    """Proximal Policy Optimization."""
    def __init__(self, state_dim, action_dim, clip_epsilon=0.2,
                 gamma=0.99, gae_lambda=0.95, lr=3e-4, entropy_coef=0.01):
        self.actor_critic = ActorCritic(state_dim, action_dim)
        self.optimizer = optim.Adam(self.actor_critic.parameters(), lr=lr)
        self.clip_epsilon = clip_epsilon
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.entropy_coef = entropy_coef
    
    def compute_gae(self, rewards, values, dones):
        """Generalized Advantage Estimation.
        
        A_t = δ_t + (γλ)δ_{t+1} + (γλ)²δ_{t+2} + ...
        Où δ_t = r_t + γV(s_{t+1}) - V(s_t)
        """
        advantages = []
        gae = 0
        values = values.squeeze()
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1 or dones[t]:
                delta = rewards[t] - values[t]
            else:
                delta = rewards[t] + self.gamma * values[t+1] - values[t]
            gae = delta + self.gamma * self.gae_lambda * (1 - dones[t]) * gae
            advantages.insert(0, gae)
        
        returns = torch.tensor(advantages) + values.detach()
        advantages = torch.tensor(advantages)
        return advantages, returns
    
    def update(self, batch):
        """Update sur un batch de trajectoires."""
        states, actions, old_log_probs, advantages, returns = batch
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        for _ in range(10):  # 10 epochs
            action_means, values = self.actor_critic(states)
            dist = Normal(action_means, 1.0)
            log_probs = dist.log_prob(actions).sum(dim=-1)
            entropy = dist.entropy().sum(dim=-1).mean()
            
            # PPO clipped objective
            ratios = torch.exp(log_probs - old_log_probs)
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1 - self.clip_epsilon, 
                                1 + self.clip_epsilon) * advantages
            actor_loss = -torch.min(surr1, surr2).mean()
            
            # Value loss (clipped également)
            value_pred = values.squeeze()
            value_loss = F.mse_loss(value_pred, returns)
            
            # Entropy bonus (exploration)
            entropy_loss = -self.entropy_coef * entropy
            
            total_loss = actor_loss + 0.5 * value_loss + entropy_loss
            
            self.optimizer.zero_grad()
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.actor_critic.parameters(), 0.5)
            self.optimizer.step()
```

---

## 5. GRPO — Group Relative Policy Optimization (DeepSeek-R1, 2025)

GRPO élimine le critic network en utilisant un groupe d'échantillons.

### Formulation
```
J_GRPO(θ) = E[1/G Σ_i (min(r_i · A_i, clip(r_i, 1-ε, 1+ε) · A_i) - β · D_KL(π_θ || π_ref))]

A_i = (R_i - mean(G)) / std(G)  # avantage intra-groupe

Où G = taille du groupe d'échantillons
r_i = π_θ(o_i|q) / π_θ_old(o_i|q)  # ratio d'importance
β = coefficient de régularisation KL
```

### Implémentation
```python
class GRPO:
    """Group Relative Policy Optimization (DeepSeek-R1 style)."""
    def __init__(self, policy, ref_policy, group_size=8, 
                 clip_epsilon=0.2, beta=0.04):
        self.policy = policy
        self.ref_policy = ref_policy  # gelé
        self.group_size = group_size
        self.clip_epsilon = clip_epsilon
        self.beta = beta
    
    def compute_advantages(self, rewards):
        """Avantage intra-groupe."""
        rewards = torch.tensor(rewards)  # (group_size,)
        return (rewards - rewards.mean()) / (rewards.std() + 1e-8)
    
    def update(self, queries, responses, rewards):
        """Update avec groupe d'échantillons."""
        advantages = self.compute_advantages(rewards)
        
        # Pour chaque échantillon du groupe
        for q, r, adv in zip(queries, responses, advantages):
            with torch.no_grad():
                # KL divergence avec le modèle de référence
                ref_log_probs = self.ref_policy.get_log_probs(q, r)
            
            # Ratio d'importance
            log_probs = self.policy.get_log_probs(q, r)
            ratio = torch.exp(log_probs - ref_log_probs)
            
            # Loss PPO clip + KL penalty
            surr1 = ratio * adv
            surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 
                                1 + self.clip_epsilon) * adv
            policy_loss = -torch.min(surr1, surr2)
            
            # KL régularisation
            kl = F.kl_div(log_probs, ref_log_probs, reduction='batchmean')
            total_loss = policy_loss + self.beta * kl
            
            total_loss.backward()
```

**Pourquoi GRPO ?**
- Pas de critic → moins de mémoire (pas de réseau V supplémentaire)
- Groupe d'échantillons → variance réduite sur l'estimation de l'avantage
- KL penalty → ne s'éloigne pas trop du modèle de base

---

## 6. DPO — Direct Preference Optimization (2023)

DPO reformule RLHF directement sur les préférences.

### Formulation
```
L_DPO(π_θ; π_ref) = -E_{(x, y_w, y_l) ~ D} [log σ(β · (r_θ(x, y_w) - r_θ(x, y_l)))]

Où r_θ(x, y) = log(π_θ(y|x) / π_ref(y|x))
β : température de préférence
y_w : réponse choisie, y_l : réponse rejetée
```

```python
class DPOTrainer:
    """Direct Preference Optimization."""
    def __init__(self, policy, ref_policy, beta=0.1, lr=1e-5):
        self.policy = policy
        self.ref_policy = ref_policy  # gelé
        self.beta = beta
        self.optimizer = optim.AdamW(policy.parameters(), lr=lr)
    
    def dpo_loss(self, prompt, chosen, rejected):
        """Calcule la perte DPO."""
        # Log probs de la politique courante
        policy_chosen_logps = self.policy.get_log_probs(prompt, chosen)
        policy_rejected_logps = self.policy.get_log_probs(prompt, rejected)
        
        with torch.no_grad():
            # Log probs du modèle de référence
            ref_chosen_logps = self.ref_policy.get_log_probs(prompt, chosen)
            ref_rejected_logps = self.ref_policy.get_log_probs(prompt, rejected)
        
        # Log-ratio d'importance
        pi_logratios = policy_chosen_logps - policy_rejected_logps
        ref_logratios = ref_chosen_logps - ref_rejected_logps
        
        logits = pi_logratios - ref_logratios
        
        # DPO loss
        loss = -F.logsigmoid(self.beta * logits).mean()
        
        # Métriques pour monitoring
        chosen_reward = self.beta * (policy_chosen_logps - ref_chosen_logps).detach()
        rejected_reward = self.beta * (policy_rejected_logps - ref_rejected_logps).detach()
        
        return loss, chosen_reward.mean(), rejected_reward.mean()
```

### Variantes DPO

| Variante | Innovation | Référence |
|----------|-----------|-----------|
| **IPO** | Loss quadratique sans sigmoid | arXiv:2310.12036 |
| **KTO** | Pas besoin de paires (juste bon/mauvais) | arXiv:2402.01306 |
| **ORPO** | Combine SFT + DPO en un seul stage | arXiv:2403.07691 |
| **SimPO** | Utilise la récompense moyenne des tokens | arXiv:2405.14734 |
| **R-DPO** | Régularisation length-aware | 2024 |

---

## 7. SAC — Soft Actor-Critic (2018)

```python
class SAC:
    """Maximum entropy RL — exploration + stabilité."""
    def __init__(self, state_dim, action_dim, alpha=0.2, 
                 tau=0.005, gamma=0.99):
        # Policy, Q networks (x2 pour double Q)
        self.actor = GaussianPolicy(state_dim, action_dim)
        self.critic1 = QNetwork(state_dim, action_dim)
        self.critic2 = QNetwork(state_dim, action_dim)
        self.critic_target1 = QNetwork(state_dim, action_dim)
        self.critic_target2 = QNetwork(state_dim, action_dim)
        
        # Égalisation des cibles
        self.critic_target1.load_state_dict(self.critic1.state_dict())
        self.critic_target2.load_state_dict(self.critic2.state_dict())
        
        # Entropy temperature (apprise ou fixe)
        self.log_alpha = nn.Parameter(torch.log(torch.tensor(alpha)))
        self.target_entropy = -action_dim  # -dim(A)
    
    def update(self, batch, alpha=None):
        state, action, reward, next_state, done = batch
        
        # Update Q
        with torch.no_grad():
            next_action, next_log_prob = self.actor.sample(next_state)
            target_q1 = self.critic_target1(next_state, next_action)
            target_q2 = self.critic_target2(next_state, next_action)
            target_q = torch.min(target_q1, target_q2)
            target_q = reward + (1 - done) * self.gamma * (target_q - alpha * next_log_prob)
        
        q1 = self.critic1(state, action)
        q2 = self.critic2(state, action)
        q_loss = F.mse_loss(q1, target_q) + F.mse_loss(q2, target_q)
        
        # Update policy
        new_action, log_prob = self.actor.sample(state)
        q1_new = self.critic1(state, new_action)
        q2_new = self.critic2(state, new_action)
        q_new = torch.min(q1_new, q2_new)
        policy_loss = (alpha * log_prob - q_new).mean()
        
        # Soft update targets
        for tp, sp in zip(self.critic_target1.parameters(), 
                          self.critic1.parameters()):
            tp.data.copy_(self.tau * sp.data + (1 - self.tau) * tp.data)
```

---

## 8. TD3 — Twin Delayed DDPG (2018)

```python
class TD3:
    """Twin Delayed DDPG : pour environnements continus."""
    # Améliorations clés :
    # 1. Double Q-learning (réduit le biais)
    # 2. Delayed policy update (policy moins souvent que Q)
    # 3. Target policy smoothing (bruit sur l'action cible)
    # 4. Clipping de l'action cible
    
    @torch.no_grad()
    def target_policy_smoothing(self, action):
        noise = torch.randn_like(action) * self.policy_noise
        noise = noise.clamp(-self.noise_clip, self.noise_clip)
        smoothed_action = (action + noise).clamp(-1, 1)
        return smoothed_action
```

---

## 9. DreamerV3 — World Models (Hafner et al., 2024)

```python
# DreamerV3 : RL basé sur un modèle du monde appris
# 3 composants :
# 1. World Model (RSSM) : prédit les états futurs
# 2. Critic : évalue les états
# 3. Actor : choisit les actions

class DreamerV3:
    """
    DreamerV3 : RL dans un rêve latent.
    
    World Model (RSSM) :
    - Recurrent State-Space Model
    - h_t = GRU(h_{t-1}, z_{t-1}, a_{t-1})
    - z_t ~ q(z_t | h_t, x_t)  (posterior)
    - z_t ~ p(z_t | h_t)       (prior)
    - x_hat = decode(z_t, h_t)
    - r_hat = reward_predict(z_t, h_t)
    
    Entraînement : 
    1. Collecter données (real env)
    2. Entraîner World Model sur données réelles
    3. Rollout imaginaire dans le monde appris
    4. Entraîner Actor/Critic sur les rollouts imaginaires
    """
    pass
```

---

## 10. Tableau Comparatif

| Algorithme | Type | Action | Sample eff. | Stabilité | Année |
|-----------|------|--------|-------------|-----------|-------|
| REINFORCE | On-policy | D/C | ★☆☆☆☆ | ★★☆☆☆ | 1992 |
| DQN | Off-policy | D | ★★★★☆ | ★★★☆☆ | 2013 |
| PPO | On-policy | D/C | ★★★☆☆ | ★★★★☆ | 2017 |
| SAC | Off-policy | C | ★★★★★ | ★★★★☆ | 2018 |
| TD3 | Off-policy | C | ★★★★★ | ★★★★★ | 2018 |
| DPO | Offline | LLM | N/A | ★★★★★ | 2023 |
| GRPO | On-policy | LLM | ★★★☆☆ | ★★★★☆ | 2024 |
| DreamerV3 | Model-based | D/C | ★★★★★ | ★★★★★ | 2024 |

---

## 11. RL pour LLM (2024-2025)

| Étape | Algorithme | Rôle |
|-------|-----------|------|
| SFT | Cross-entropy | Imiter des démonstrations |
| RM | Regression Bradley-Terry | Apprendre les préférences humaines |
| RLHF | PPO + RM | Optimiser vers les préférences |
| DPO | DPO loss direct | Optimiser les préférences sans RM |
| GRPO | GRPO + groupe | Optimiser avec récompense connue (math, code) |

---

## Références

- PPO : https://arxiv.org/abs/1707.06347
- SAC : https://arxiv.org/abs/1801.01290
- TD3 : https://arxiv.org/abs/1802.09477
- DPO : https://arxiv.org/abs/2305.18290
- GRPO (DeepSeek-R1) : https://arxiv.org/abs/2501.12948
- DreamerV3 : https://arxiv.org/abs/2301.04104
- REINFORCE : https://link.springer.com/article/10.1007/BF00992696
- GAE (Generalized Advantage Estimation) : https://arxiv.org/abs/1506.02438
- RLHF : https://arxiv.org/abs/2203.02155
- KTO : https://arxiv.org/abs/2402.01306
- ORPO : https://arxiv.org/abs/2403.07691