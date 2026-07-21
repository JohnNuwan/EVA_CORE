---
name: rhlf-preference
description: Guide complet du Reinforcement Learning from Human Feedback et optimisation de préférences — RLHF, DPO, KTO, IPO, ORPO, SimPO, récompenses, alignment. En français.
---

# RLHF & Preference Optimization — Guide Complet

De RLHF à DPO, aligner les LLM avec les préférences humaines.

---

## 1. Le Problème de l'Alignment

```python
# Un LLM pré-entraîné (next token prediction) peut :
# - Être toxique
# - Mentir (hallucinations)
# - Refuser d'aider
# - Être non-aligné avec les valeurs humaines

# Solution : alignment = rendre le modèle utile, honnête, inoffensif
```

### Pipeline d'Alignment

```
1. Pré-entraînement (next token prediction)
   ↓
2. SFT (Supervised Fine-Tuning) — imiter des démonstrations
   ↓
3. RM (Reward Model) — apprendre les préférences humaines
   ↓
4. RL fine-tuning (PPO/GRPO) — optimiser vers RM
   ou
   DPO — alignment direct (sans RM explicite)
```

---

## 2. Collecte des Préférences

### Format Bradley-Terry
```python
# Soient deux réponses y_w (chosen) et y_l (rejected) pour un prompt x
# Le labelleur humain choisit la meilleure
# Modèle de préférence Bradley-Terry :
# P(y_w > y_l | x) = σ(r(x, y_w) - r(x, y_l))
# où σ = sigmoid, r = reward model score
```

### Types de données de préférence

| Type | Description | Exemple |
|------|-------------|---------|
| Paires (chosen/rejected) | Comparaison binaire | A > B |
| Ranking | Classement de N réponses | A > B > C > D |
| Ratings | Score sur échelle | 1-5 étoiles |
| Binaire | Accept/Reject | ✓ / ✗ |
| Langue naturelle | Feedback textuel | "Trop long, sois concis" |

---

## 3. Reward Model Training

```python
class RewardModel(nn.Module):
    """Modèle de récompense : prédit un score pour (prompt, réponse)."""
    def __init__(self, base_model, dropout=0.1):
        super().__init__()
        self.base_model = base_model
        self.value_head = nn.Sequential(
            nn.Linear(base_model.config.hidden_size, 1024),
            nn.Dropout(dropout),
            nn.ReLU(),
            nn.Linear(1024, 1),
        )
    
    def forward(self, input_ids, attention_mask):
        # Récupérer le hidden state du dernier token
        outputs = self.base_model(input_ids, attention_mask=attention_mask,
                                  output_hidden_states=True)
        hidden = outputs.hidden_states[-1]
        # Prendre le dernier token non-padding
        last_indices = attention_mask.sum(dim=1) - 1
        last_hidden = hidden[torch.arange(hidden.size(0)), last_indices]
        reward = self.value_head(last_hidden).squeeze(-1)
        return reward


def train_reward_model(reward_model, dataloader, optimizer):
    """Entraîne le réward model sur des paires (chosen, rejected).
    
    Loss : -log σ( r(x, y_w) - r(x, y_l) )
    """
    reward_model.train()
    total_loss = 0
    
    for batch in dataloader:
        # batch: {prompt, chosen_ids, chosen_mask, rejected_ids, rejected_mask}
        reward_chosen = reward_model(batch['chosen_ids'], batch['chosen_mask'])
        reward_rejected = reward_model(batch['rejected_ids'], batch['rejected_mask'])
        
        # Bradley-Terry loss
        loss = -F.logsigmoid(reward_chosen - reward_rejected).mean()
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    
    return total_loss / len(dataloader)
```

---

## 4. RLHF (PPO avec Reward Model)

```python
class PPOWithRM(nn.Module):
    """RLHF : PPO avec un réward model pré-entraîné.
    
    Composants :
    - Policy (π_θ) : le LLM qu'on entraîne
    - Value Model (V_φ) : estimateur de valeur
    - Reward Model (r_ψ) : gelé, donne les récompenses
    - Reference Model (π_ref) : gelé, KL divergence
    """
    def __init__(self, policy, value_model, reward_model, ref_model,
                 kl_coef=0.1, clip_range=0.2):
        super().__init__()
        self.policy = policy              # Apprentissage
        self.value_model = value_model    # Apprentissage
        self.reward_model = reward_model  # Gelé
        self.ref_model = ref_model        # Gelé
        self.kl_coef = kl_coef
        self.clip_range = clip_range
    
    def compute_rewards(self, prompts, responses, masks):
        """Calcule la récompense totale = RM score - KL penalty."""
        with torch.no_grad():
            # Score du réward model
            scores = self.reward_model(prompts, responses, masks)
            
            # KL divergence penalty avec le modèle de référence
            log_probs = self.policy.get_log_probs(prompts, responses)
            ref_log_probs = self.ref_model.get_log_probs(prompts, responses)
            kl = log_probs - ref_log_probs  # KL par token
            
            # Récompense finale : RM score - β · KL
            # KL penalty évite que le modèle ne s'éloigne trop
            kl_penalty = self.kl_coef * kl
            rewards = scores.unsqueeze(-1) - kl_penalty
        
        return rewards
    
    def train_step(self, batch):
        prompts, responses, masks = batch
        
        # Forward pass
        log_probs, values = self.policy(prompts, responses, masks)
        rewards = self.compute_rewards(prompts, responses, masks)
        
        # Generalized Advantage Estimation
        advantages, returns = self.compute_gae(rewards, values, masks)
        
        # PPO clip loss
        ratio = torch.exp(log_probs - old_log_probs)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip_range, 1 + self.clip_range) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()
        
        # Value loss
        value_loss = F.mse_loss(values, returns)
        
        return policy_loss + 0.5 * value_loss
```

### Problèmes du RLHF

```python
# 1. **Instabilité d'entraînement** : PPO est notoirement instable
# 2. **Complexité** : 4 modèles à gérer (policy, value, reward, ref)
# 3. **Récompense hack** : le modèle apprend à tromper le RM
# 4. **Reward over-optimization** : trop de KL → modèle cassé
# 5. **Coûteux** : nécessite un RM entraîné sur données humaines
```

---

## 5. DPO — Direct Preference Optimization (Rafailov et al., 2023)

### Formulation mathématique
```python
# DPO reformule RLHF directement sur les préférences
# Pas besoin de Reward Model séparé !
#
# Intuition : le ratio π_θ(y|x) / π_ref(y|x) encode implicitement un reward
# r_θ(x,y) = β · log(π_θ(y|x) / π_ref(y|x))
#
# Loss : L = -E[ log σ(β · (r_θ(x, y_w) - r_θ(x, y_l))) ]
#       = -E[ log σ(β · [log(π_θ(y_w|x) / π_ref(y_w|x)) - 
#                           log(π_θ(y_l|x) / π_ref(y_l|x))]) ]
```

### Implémentation
```python
class DPOTrainer:
    """Direct Preference Optimization — version complète."""
    def __init__(self, model, ref_model, beta=0.1, lr=1e-6):
        self.model = model          # Politique à entraîner
        self.ref_model = ref_model   # Modèle de référence (gelé)
        self.beta = beta            # Température KL
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    
    def get_log_probs(self, model, input_ids, attention_mask, labels):
        """Calcule les log-probabilités des tokens labels."""
        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        
        # Shift pour next-token prediction
        shift_logits = logits[..., :-1, :].contiguous()
        shift_labels = labels[..., 1:].contiguous()
        shift_mask = attention_mask[..., 1:].contiguous()
        
        # Log-probs
        log_probs = -F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            reduction='none',
        ).view_as(shift_labels)
        
        # Masquer le padding
        log_probs = log_probs * shift_mask
        
        # Somme des log-probs sur la réponse
        return log_probs.sum(dim=-1) / shift_mask.sum(dim=-1)
    
    def dpo_loss(self, batch):
        """Calcule la loss DPO sur un batch de paires."""
        # Log probs du modèle courant
        policy_chosen_logps = self.get_log_probs(
            self.model, batch['chosen_ids'], batch['chosen_mask'], batch['chosen_labels'])
        policy_rejected_logps = self.get_log_probs(
            self.model, batch['rejected_ids'], batch['rejected_mask'], batch['rejected_labels'])
        
        with torch.no_grad():
            # Log probs du modèle de référence
            ref_chosen_logps = self.get_log_probs(
                self.ref_model, batch['chosen_ids'], batch['chosen_mask'], batch['chosen_labels'])
            ref_rejected_logps = self.get_log_probs(
                self.ref_model, batch['rejected_ids'], batch['rejected_mask'], batch['rejected_labels'])
        
        # Log-ratios d'importance
        pi_logratios = policy_chosen_logps - policy_rejected_logps
        ref_logratios = ref_chosen_logps - ref_rejected_logps
        
        # Implicit reward
        beta_logratios = self.beta * (pi_logratios - ref_logratios)
        
        # DPO loss : -log σ(β · delta_log_ratio)
        losses = -F.logsigmoid(beta_logratios)
        loss = losses.mean()
        
        # Métriques
        chosen_reward = self.beta * (policy_chosen_logps - ref_chosen_logps).detach()
        rejected_reward = self.beta * (policy_rejected_logps - ref_rejected_logps).detach()
        accuracy = (chosen_reward > rejected_reward).float().mean()
        
        return {
            'loss': loss,
            'chosen_reward': chosen_reward.mean().item(),
            'rejected_reward': rejected_reward.mean().item(),
            'accuracy': accuracy.item(),
        }
    
    def train(self, dataset, num_epochs=3, batch_size=4):
        """Entraîne le modèle avec DPO."""
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        for epoch in range(num_epochs):
            for batch in dataloader:
                metrics = self.dpo_loss(batch)
                metrics['loss'].backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                self.optimizer.zero_grad()
                
                print(f"Epoch {epoch} | Loss: {metrics['loss']:.4f} | "
                      f"Acc: {metrics['accuracy']:.3f} | "
                      f"Reward Δ: {metrics['chosen_reward'] - metrics['rejected_reward']:.3f}")
```

---

## 6. KTO — Kahneman-Tversky Optimization (2024)

```python
# KTO : pas besoin de paires (chosen/rejected) !
# Juste des exemples « bons » ou « mauvais » individuellement
# Basé sur la théorie des perspectives (Kahneman-Tversky)

def kto_loss(policy_logps, ref_logps, y_is_good, beta=0.1):
    """
    KTO Loss :
    L = 1 - σ(β · (log(π/π_ref) - z_0))  pour y_good
    L = 1 - σ(-β · (log(π/π_ref) - z_0)) pour y_bad
    
    Où z_0 = β · KL(π || π_ref) (bias de référence)
    """
    log_ratio = policy_logps - ref_logps
    
    # KL implicit bias
    kl = (log_ratio.exp() - 1 - log_ratio).mean()
    z0 = beta * kl.detach()
    
    loss_good = (1 - F.sigmoid(beta * (log_ratio - z0))) * y_is_good
    loss_bad = (1 - F.sigmoid(-beta * (log_ratio - z0))) * (1 - y_is_good)
    
    return (loss_good + loss_bad).mean()
```

---

## 7. IPO — Identity Preference Optimization (2023)

```python
# IPO : remplace le sigmoid par une loss quadratique
# Plus simple à optimiser, pas de saturation

def ipo_loss(policy_logps, ref_logps, beta=0.1):
    """Identity Preference Optimization.
    
    L = (log(π/π_ref) - 1/(2β))²  pour la paire (chosen, rejected)
    """
    log_ratio = policy_logps - ref_logps
    
    # IPO loss : (difference - τ^(-1))²
    tau = 0.5 * beta
    loss = (log_ratio - 1/tau) ** 2
    
    return loss.mean()
```

---

## 8. ORPO — Odds Ratio Preference Optimization (2024)

```python
# ORPO : combine SFT + DPO en UN SEUL STAGE
# Pas besoin de référence séparée
# La loss = NLL (imiter les bonnes réponses) + OR (préférer les bonnes)

def orpo_loss(policy_logps_chosen, policy_logps_rejected, lambda_coef=0.1):
    """Odds Ratio Preference Optimization.
    
    L = -log π(y_w|x) + λ · log(1 + odds_ratio)
    
    Où odds = π(y|x) / (1 - π(y|x))
    OR = odds(y_w) / odds(y_rejected)
    """
    # NLL loss (SFT)
    sft_loss = -policy_logps_chosen.mean()
    
    # Odds ratio
    odds_chosen = torch.exp(policy_logps_chosen)
    odds_rejected = torch.exp(policy_logps_rejected)
    log_odds_ratio = torch.log(odds_chosen / odds_rejected)
    
    # ORPO penalty
    or_loss = -F.logsigmoid(log_odds_ratio).mean()
    
    return sft_loss + lambda_coef * or_loss
```

---

## 9. SimPO — Simple Preference Optimization (2024)

```python
# SimPO : encore plus simple que DPO !
# Utilise la récompense moyenne (avg log prob) au lieu du ratio
# Pas besoin de modèle de référence

def simpo_loss(policy_logps_chosen, policy_logps_rejected, 
               beta=2.0, gamma_beta_ratio=1.0):
    """Simple Preference Optimization.
    
    L = -log σ(β · (avg_log_prob_chosen - avg_log_prob_rejected) - γ)
    
    Où γ = reward margin (target gap between chosen and rejected)
    """
    # Log-probabilités moyennes (récompense average per token)
    avg_chosen = policy_logps_chosen.mean(dim=-1)
    avg_rejected = policy_logps_rejected.mean(dim=-1)
    
    reward_margin = avg_chosen - avg_rejected - gamma_beta_ratio
    loss = -F.logsigmoid(beta * reward_margin).mean()
    
    return loss
```

---

## 10. GRPO — Group Relative Policy Optimization (DeepSeek-R1, 2025)

```python
class GRPOTrainer:
    """Group Relative Policy Optimization.
    
    Utilisé par DeepSeek-R1 pour le reasoning RL.
    Pas de critic (value model) — utilise un groupe d'échantillons.
    """
    def __init__(self, model, ref_model=None, group_size=8, 
                 beta=0.04, clip_epsilon=0.2):
        self.model = model
        self.ref_model = ref_model
        self.group_size = group_size
        self.beta = beta
        self.clip_epsilon = clip_epsilon
    
    def compute_group_advantage(self, rewards):
        """Avantage = (reward - mean(G)) / std(G) normalisé intra-groupe."""
        rewards = torch.tensor(rewards)
        return (rewards - rewards.mean()) / (rewards.std() + 1e-8)
    
    def train_step(self, prompts, group_size=8):
        """
        Pour chaque prompt :
        1. Génère G = 8 réponses différentes (température élevée)
        2. Évalue chaque réponse (récompense connue : math, code)
        3. Calcule avantage intra-groupe
        4. PPO clip (sans critic)
        """
        all_responses = []
        for _ in range(group_size):
            response = self.model.generate(prompts, temperature=0.7, top_p=0.95)
            all_responses.append(response)
        
        # Évaluation des réponses (récompense = exactitude pour math/code)
        rewards = [evaluate(response) for response in all_responses]
        advantages = self.compute_group_advantage(rewards)
        
        # GRPO loss
        total_loss = 0
        for response, adv in zip(all_responses, advantages):
            log_probs = self.model.get_log_probs(prompts, response)
            
            if self.ref_model:
                with torch.no_grad():
                    ref_log_probs = self.ref_model.get_log_probs(prompts, response)
                kl = F.kl_div(log_probs, ref_log_probs, reduction='sum')
            else:
                kl = 0
            
            # Policy gradient avec clipping
            ratio = torch.exp(log_probs - log_probs.detach())  # approx
            clipped = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon)
            loss = -torch.min(ratio * adv, clipped * adv).mean()
            loss += self.beta * kl
            
            total_loss += loss
        
        return total_loss / group_size
```

---

## 11. Tableau Comparatif

| Méthode | RM nécessaire | Modèle réf. | Données | Complexité | Stabilité | Année |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| RLHF (PPO) | ✓ | ✓ | Paires | ★★★★★ | ★★☆☆☆ | 2020 |
| DPO | ✗ | ✓ | Paires | ★★★☆☆ | ★★★★☆ | 2023 |
| KTO | ✗ | ✓ | Individ. | ★★★☆☆ | ★★★★☆ | 2024 |
| IPO | ✗ | ✓ | Paires | ★★★☆☆ | ★★★★★ | 2023 |
| ORPO | ✗ | ✗ | Paires | ★★☆☆☆ | ★★★☆☆ | 2024 |
| SimPO | ✗ | ✗ | Paires | ★★☆☆☆ | ★★★★☆ | 2024 |
| GRPO | ✗ | ✓ | Groupes | ★★★★☆ | ★★★☆☆ | 2025 |

---

## 12. Métriques d'Alignment

```python
# Évaluation d'Alignment
# - AlpacaEval : rate vs GPT-4 dans des conversations
# - MT-Bench : jugement multi-tour
# - Helpful/Harmless (Anthropic) : utilité vs innocuité
# - TruthfulQA : véracité
# - RewardBench : comparaison des RM
# - Chatbot Arena : classement Elo par votes humains
```

---

## Références

- RLHF (InstructGPT) : https://arxiv.org/abs/2203.02155
- DPO : https://arxiv.org/abs/2305.18290
- KTO : https://arxiv.org/abs/2402.01306
- IPO : https://arxiv.org/abs/2310.12036
- ORPO : https://arxiv.org/abs/2403.07691
- SimPO : https://arxiv.org/abs/2405.14734
- GRPO (DeepSeek-R1) : https://arxiv.org/abs/2501.12948
- Reward Model : https://arxiv.org/abs/2204.05862
- AlpacaEval : https://github.com/tatsu-lab/alpaca_eval
- MT-Bench : https://arxiv.org/abs/2306.05685