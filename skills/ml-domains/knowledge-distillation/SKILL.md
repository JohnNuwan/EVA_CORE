---
name: knowledge-distillation
description: Guide complet de la distillation de connaissances — logits, features, on-policy, black-box, white-box, distillation d'étapes, TinyLLM, Phi, implémentations. En français.
---

# Knowledge Distillation — Guide Complet

Transférer le savoir d'un grand modèle vers un petit : logits, features, architectures 2024-2025.

---

## 1. Principe Fondamental

```python
# Idée : un petit modèle (student) apprend d'un grand (teacher)
# Le teacher a déjà la connaissance. Le student copie son comportement.
#
# Pourquoi ?
# - Déploiement plus rapide et moins cher
# - Moins de mémoire/vRAM
# - Meilleure latence
# - Peut égaler le teacher avec ~10-50% des paramètres
```

### Types de Distillation

```
             Distillation
           /       |       \
     Logits      Features    On-policy
     (Hinton)    (FitNets)   (SeqKD)
        |           |           |
   Softmax des   Couches     Génération
   logits        interm.     du teacher
        |           |           |
   BERT→TinyBERT  ResNet→     LLAMA→
                  TinyViT     TinyLLAMA
```

---

## 2. Distillation de Logits (Hinton et al., 2015)

### Formulation mathématique
```
L = α · L_CE(student, hard_labels) + β · L_KD(soft_labels)

L_KD = KL(softmax(z_T / τ), softmax(z_S / τ))

Où :
- z_T et z_S : logits du teacher et student
- τ (temperature) : contrôle la « douceur » des probabilités
  - τ → 0 : one-hot (pas d'info sur les relations entre classes)
  - τ → ∞ : distribution uniforme
  - τ ≈ 2-8 : bon compromis
- α, β : coefficients de pondération
```

### Implémentation complète
```python
class DistillationLoss(nn.Module):
    """Perte de distillation classique (Hinton)."""
    def __init__(self, temperature=4.0, alpha=0.5):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
    
    def forward(self, student_logits, teacher_logits, labels):
        # Hard loss (cross-entropy standard)
        hard_loss = F.cross_entropy(student_logits, labels)
        
        # Soft loss (KL divergence)
        # Les logits sont adoucis par la temperature
        soft_student = F.log_softmax(student_logits / self.temperature, dim=-1)
        soft_teacher = F.softmax(teacher_logits / self.temperature, dim=-1)
        
        # KL divergence (moyenne sur le batch)
        soft_loss = F.kl_div(soft_student, soft_teacher, reduction='batchmean')
        # Multiplier par T² (gradient scaling)
        soft_loss = soft_loss * (self.temperature ** 2)
        
        # Combinaison
        return self.alpha * hard_loss + (1 - self.alpha) * soft_loss


class DistillationTrainer:
    """Entraîne un student avec un teacher gelé."""
    def __init__(self, teacher, student, temperature=4.0, alpha=0.5):
        self.teacher = teacher.eval()  # Gelé
        self.student = student
        self.criterion = DistillationLoss(temperature, alpha)
    
    def train_step(self, batch):
        inputs, labels = batch
        
        with torch.no_grad():
            teacher_logits = self.teacher(inputs)
        
        student_logits = self.student(inputs)
        loss = self.criterion(student_logits, teacher_logits, labels)
        
        loss.backward()
        return loss.item()
```

---

## 3. Distillation de Features (FitNets, Romero et al., 2015)

```python
# Au lieu des logits, on distille les activations intermédiaires
# Le student apprend à reproduire les « features » du teacher
# Utile pour la vision et les modèles profonds

class FitNetLoss(nn.Module):
    """Distillation au niveau des couches cachées."""
    def __init__(self, teacher_channels, student_channels, hidden=512):
        super().__init__()
        # Régresseur pour adapter les dimensions student → teacher
        self.regressor = nn.Sequential(
            nn.Linear(student_channels, hidden),
            nn.ReLU(),
            nn.Linear(hidden, teacher_channels),
        )
    
    def forward(self, student_feat, teacher_feat):
        # student_feat: (B, C_s, H, W)
        # teacher_feat: (B, C_t, H, W)
        student_mapped = self.regressor(
            student_feat.flatten(2).mean(dim=-1)
        )
        teacher_flat = teacher_feat.flatten(2).mean(dim=-1)
        return F.mse_loss(student_mapped, teacher_flat)
```

### Attention Transfer (Zagoruyko & Komodakis, 2017)
```python
class AttentionTransfer(nn.Module):
    """Distille les cartes d'attention spatiale.
    
    Idée : une image qui active fortement le teacher 
    doit aussi activer le student.
    """
    def attention_map(self, features):
        """Carte d'attention spatiale."""
        # Sum des channels → carte 2D
        return features.pow(2).sum(dim=1)
    
    def loss(self, student_maps, teacher_maps):
        # MSE entre les cartes normalisées
        loss = 0
        for s_map, t_map in zip(student_maps, teacher_maps):
            s_norm = s_map / s_map.view(s_map.size(0), -1).sum(dim=-1, keepdim=True)
            t_norm = t_map / t_map.view(t_map.size(0), -1).sum(dim=-1, keepdim=True)
            loss += F.mse_loss(s_norm, t_norm)
        return loss
```

---

## 4. Sequence-Level Knowledge Distillation (SeqKD, Kim & Rush, 2016)

```python
# Pour les modèles séquentiels (NLP, LLM) :
# Le student apprend à imiter les séquences générées par le teacher

class SeqKD:
    """Sequence-Level Knowledge Distillation pour Transformers.
    
    Deux modes :
    1. **Word-level** : le student maximise P(student_token | teacher_history)
       → loss = KL(teacher_logits || student_logits) par token
    2. **Sequence-level** : le teacher génère des séquences
       → le student s'entraîne dessus (comme des données réelles)
    """
    
    @staticmethod
    def word_level_kd(student_logits, teacher_logits, mask=None):
        """KL divergence par token."""
        loss = F.kl_div(
            F.log_softmax(student_logits, dim=-1),
            F.softmax(teacher_logits, dim=-1),
            reduction='none',
        )
        if mask is not None:
            loss = loss * mask.unsqueeze(-1)
        return loss.sum() / mask.sum()
    
    @staticmethod
    def sequence_level_kd(teacher, student, prompts, max_new=128):
        """Le teacher génère, le student imite."""
        # Génération par le teacher
        with torch.no_grad():
            generated = teacher.generate(prompts, max_new_tokens=max_new)
        
        # Entraînement du student sur les sorties générées
        outputs = student(generated, labels=generated)
        return outputs.loss
```

---

## 5. On-Policy Distillation (MiniLLM, 2023)

```python
# Problème de SeqKD : le student ne voit que les « bonnes » réponses
# → il ne sait pas quoi faire quand il fait une erreur
#
# Solution : distillation on-policy
# Le student génère sa propre réponse → le teacher la note

class OnPolicyDistillation:
    """Distillation on-policy (MiniLLM, 2023).
    
    1. Le student génère une réponse (échantillonnage)
    2. Le teacher donne les logits pour cette réponse
    3. Le student apprend via KL divergence
    4. Reverse KL : P(student) || Q(teacher) au lieu de Q || P
       → le student est « optimiste » et explore
    """
    def loss(self, student, teacher, prompt):
        # Student génère (on-policy)
        student_output = student.generate(prompt, do_sample=True)
        
        # Teacher évalue
        with torch.no_grad():
            teacher_logits = teacher(prompt, student_output).logits
        
        # Student apprend
        student_logits = student(prompt, student_output).logits
        
        # Reverse KL
        student_probs = F.log_softmax(student_logits, dim=-1)
        teacher_probs = F.softmax(teacher_logits, dim=-1)
        
        return F.kl_div(student_probs, teacher_probs, reduction='batchmean')
```

---

## 6. Black-Box Distillation (API Distillation, 2023+)

```python
# Quand le teacher est une API (GPT-4, Claude, etc.)
# On ne peut pas accéder aux logits/activations
# Seulement aux textes générés

class BlackBoxDistillation:
    """Distillation sans accès aux logits.
    
    Méthodes :
    1. **Data Generation** : prompt GPT-4 → collecter sorties
       → fine-tuner un modèle ouvert dessus
    2. **Self-Instruct** : le teacher génère des instructions
       le student apprend à y répondre
    3. **Constitutional AI** : le teacher critique le student
    
    Exemple : Alpaca (Stanford, 2023)
    - 52K instructions générées par GPT-3.5
    - Fine-tuning de LLaMA 7B → Alpaca 7B
    - 100$ de coût API vs millions pour un pré-entraînement
    """
    @staticmethod
    def generate_training_data(api_model, prompts):
        """Génère des données d'entraînement via API.
        
        Args:
            api_model: fonction qui appelle l'API (ex: GPT-4)
            prompts: liste de prompts
        Returns:
            Dataset de (prompt, response) pour fine-tuning
        """
        dataset = []
        for prompt in prompts:
            response = api_model(prompt, temperature=0.7)
            dataset.append({"prompt": prompt, "response": response})
        return dataset
```

---

## 7. TinyLLaMA / Phi — Modèles Distillés

### TinyLLaMA (1.1B, 2024)
```python
# TinyLLaMA 1.1B :
# - 1.1B paramètres
# - Distillé de LLaMA 2 (7B)
# - Mélange de : pré-entraînement + distillation
# - Performances : surpasse tous les modèles < 3B

# Architecture :
# - 22 couches, 2048 hidden
# - GQA (2 KV heads)
# - RoPE, SwiGLU
```

### Phi-3 / Phi-4 (Microsoft, 2024)
```python
# Phi : distillation via données synthétiques
# Pas de teacher traditionnel
# Les données sont générées par GPT-4/LLaMA
# Puis filtrées pour qualité

# Phi-3 Mini (3.8B) :
# - 4.4T tokens de données synthétiques
# - Surpasse Llama 3 8B sur plusieurs benchmarks
# - 3.8B paramètres, 128K contexte

# Phi-4 (14B) :
# - 14B paramètres
# - Données synthétiques de haute qualité
# - Code + math + raisonnement
# - Compétitif avec des modèles 3x plus grands
```

---

## 8. Progressive Distillation (Step Distillation)

```python
# Distillation progressive : réduit le nombre d'étapes
# Utilisé pour les modèles de diffusion

class ProgressiveDistillation:
    """Distillation progressive pour la génération.
    
    Principe : 
    1. Teacher : modèle en N étapes
    2. Student : modèle en N/2 étapes
    3. Le student apprend à sauter des étapes
    4. Le nouveau student devient teacher
    5. Répéter jusqu'à N très petit
    
    Application : FLUX.1-schnell (4 étapes !)
    """
    def distill_step(self, teacher, student, batch):
        # Teacher fait un pas de génération
        with torch.no_grad():
            teacher_out = teacher(batch, steps=100)
        
        # Student apprend à faire la même chose en 50 étapes
        student_out = student(batch, steps=50)
        
        return F.mse_loss(student_out, teacher_out)
```

---

## 9. Self-Distillation

```python
# Le modèle apprend de lui-même (pas de teacher externe)
# Le modèle profond (plus de couches) enseigne
# au modèle superficiel (moins de couches)
# Ou : version EMA (exponential moving average) du modèle

class SelfDistillation:
    """Auto-distillation : le modèle est son propre teacher.
    
    Utilisation : DINO, BYOL, data augmentations
    
    Avantages :
    - Pas besoin de gros modèle externe
    - Apprentissage plus stable
    - Représentations plus robustes
    """
    def __init__(self, model, momentum=0.996):
        self.student = model
        self.teacher = copy.deepcopy(model)  # EMA
        for p in self.teacher.parameters():
            p.requires_grad = False
    
    @torch.no_grad()
    def update_teacher(self):
        for p_s, p_t in zip(self.student.parameters(), self.teacher.parameters()):
            p_t.data = self.momentum * p_t.data + (1 - self.momentum) * p_s.data
```

---

## 10. Implémentation Complète

```python
class DistillationPipeline:
    """Pipeline de distillation complet."""
    def __init__(self, teacher, student, tokenizer, config):
        self.teacher = teacher
        self.student = student
        self.tokenizer = tokenizer
        self.config = config
    
    def distill_logits(self, dataloader):
        """Distillation de logits (Hinton)."""
        criterion = DistillationLoss(
            temperature=self.config.temperature,
            alpha=self.config.alpha,
        )
        optimizer = torch.optim.AdamW(self.student.parameters(), 
                                       lr=self.config.lr)
        
        for batch in dataloader:
            inputs = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            with torch.no_grad():
                teacher_out = self.teacher(inputs).logits
            
            student_out = self.student(inputs).logits
            loss = criterion(student_out, teacher_out, labels)
            
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
    
    def distill_sequence(self, prompts, max_new=128):
        """Distillation de séquence (SeqKD)."""
        with torch.no_grad():
            teacher_responses = self.teacher.generate(
                prompts, max_new_tokens=max_new,
                temperature=0.7, do_sample=True,
            )
        
        # Fine-tuning du student sur les réponses
        dataset = [{"input_ids": p, "labels": r} 
                   for p, r in zip(prompts, teacher_responses)]
        # Entraînement standard (SFT)
        self.train_sft(dataset)
```

---

## 11. Tableau Comparatif

| Méthode | Type | Accès Teacher | Qualité | Coût | Année |
|---------|------|:-------------:|:-------:|:----:|:----:|
| Logit KD | Logits | Boîte blanche | ★★★★☆ | Bas | 2015 |
| FitNet | Features | Boîte blanche | ★★★★☆ | Moyen | 2015 |
| Attention Transfer | Features | Boîte blanche | ★★★★★ | Moyen | 2017 |
| SeqKD | Séquences | Boîte blanche | ★★★★☆ | Bas | 2016 |
| On-Policy KD | Séquences | Boîte blanche | ★★★★★ | Moyen | 2023 |
| TinyLLaMA | Données | Mixte | ★★★★★ | Élevé | 2024 |
| Phi-4 | Synthétique | Boîte noire | ★★★★★ | Élevé | 2024 |
| Progressive | Diffusion | Boîte blanche | ★★★★☆ | Bas | 2023 |
| Self-Distill | Features | Auto | ★★★★☆ | Bas | 2021 |

---

## Références

- Distilling the Knowledge (Hinton, 2015) : https://arxiv.org/abs/1503.02531
- FitNets : https://arxiv.org/abs/1412.6550
- SeqKD : https://arxiv.org/abs/1606.07947
- MiniLLM : https://arxiv.org/abs/2306.08543
- TinyLLaMA : https://github.com/jzhang38/TinyLlama
- Phi-3 : https://arxiv.org/abs/2404.14219
- Progressive Distillation : https://arxiv.org/abs/2202.00512
- Alpaca : https://crfm.stanford.edu/2023/03/13/alpaca.html
- Attention Transfer : https://arxiv.org/abs/1612.03928