---
name: meta-learning
description: Guide complet du méta-apprentissage (learning to learn) — MAML, Reptile, proto-nets, few-shot, zero-shot, metric-based, optimization-based, model-based. En français.
---

# Méta-Apprentissage (Meta-Learning) — Guide Complet

Apprendre à apprendre : adaptation rapide avec peu de données, few-shot learning.

---

## 1. Le Problème Few-Shot

```python
# Apprentissage standard : 1000s d'exemples par classe
# Few-shot : 1, 5 ou 10 exemples par classe
# Le méta-apprentissage = apprendre sur des tâches

# Formulation few-shot :
# N-way K-shot : N classes, K exemples par classe
# 5-way 1-shot : 5 classes, 1 exemple chacune
# 5-way 5-shot : 5 classes, 5 exemples chacune
```

### Taxonomie

```
         Méta-Apprentissage
        /         |         \
  Basé sur    Basé sur     Basé sur
  l'optimis.   les métriques   les modèles
     (MAML,     (ProtoNets,    (MANN,
     Reptile)    RelationNets)  CNP)
        |            |            |
   Gradient     Distance    Mémoire
   interne      dans un     externe
   (inner loop)  espace      (external
                appris      memory)
```

---

## 2. MAML — Model-Agnostic Meta-Learning (Finn et al., 2017)

### Principe

```python
# MAML : trouver une initialisation θ telle que
# QUELQUES pas de gradient sur une nouvelle tâche
# donnent un modèle performant

# Deux boucles :
# Outer loop : méta-apprentissage (mettre à jour θ)
# Inner loop : adaptation rapide (θ → θ')

# θ' = θ - α · ∇_θ L_tache(f_θ, D_support)
# θ ← θ - β · ∇_θ L_tache(f_θ', D_query)
```

### Implémentation
```python
class MAML(nn.Module):
    """Model-Agnostic Meta-Learning.
    
    Fonctionne avec n'importe quel modèle differentiable.
    """
    def __init__(self, model, inner_lr=0.01, meta_lr=0.001, 
                 inner_steps=5, first_order=False):
        super().__init__()
        self.model = model
        self.inner_lr = inner_lr
        self.meta_lr = meta_lr
        self.inner_steps = inner_steps
        self.first_order = first_order  # FOMAML (plus rapide)
        self.meta_optimizer = torch.optim.Adam(model.parameters(), lr=meta_lr)
    
    def forward(self, support_x, support_y, query_x):
        """Adaptation rapide (inner loop) sur support set,
        prédiction sur query set.
        
        Args:
            support_x: (n_way * k_shot, ...)
            support_y: (n_way * k_shot,)
            query_x: (n_way * n_query, ...)
        """
        # Copier les paramètres (inner loop = paramètres privés)
        fast_weights = {name: param.clone() 
                       for name, param in self.model.named_parameters()}
        
        # Inner loop : adaptation sur support set
        for _ in range(self.inner_steps):
            logits = self.model.functional_forward(support_x, fast_weights)
            loss = F.cross_entropy(logits, support_y)
            
            grads = torch.autograd.grad(loss, fast_weights.values(),
                                        create_graph=not self.first_order)
            fast_weights = {
                name: w - self.inner_lr * g
                for (name, w), g in zip(fast_weights.items(), grads)
            }
        
        # Query set prediction
        logits = self.model.functional_forward(query_x, fast_weights)
        return logits
    
    def meta_train_step(self, task_batch):
        """Étape d'entraînement méta (outer loop)."""
        meta_loss = 0
        for task in task_batch:
            logits = self.forward(task['support_x'], task['support_y'],
                                  task['query_x'])
            meta_loss += F.cross_entropy(logits, task['query_y'])
        
        meta_loss /= len(task_batch)
        
        self.meta_optimizer.zero_grad()
        meta_loss.backward()
        self.meta_optimizer.step()
        
        return meta_loss.item()


class FunctionalModel(nn.Module):
    """Modèle avec forward fonctionnel pour MAML."""
    def __init__(self, input_dim=28*28, hidden=64, n_way=5):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden)
        self.fc2 = nn.Linear(hidden, hidden)
        self.fc3 = nn.Linear(hidden, n_way)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)
    
    def functional_forward(self, x, weights):
        """Forward avec des poids donnés (pour gradient adaptation)."""
        x = F.linear(x, weights['fc1.weight'], weights['fc1.bias'])
        x = F.relu(x)
        x = F.linear(x, weights['fc2.weight'], weights['fc2.bias'])
        x = F.relu(x)
        x = F.linear(x, weights['fc3.weight'], weights['fc3.bias'])
        return x
```

### FOMAML — First-Order MAML
```python
# MAML classique : dérivée seconde (très coûteux)
# FOMAML : ignore les dérivées de l'inner loop
# (create_graph=False)
# Résultat : 3x plus rapide, presque aussi performant
```

---

## 3. Reptile (Nichol et al., 2018)

```python
# Reptile : encore plus simple que MAML !
# On exécute SGD sur chaque tâche
# On déplace l'initialisation vers le résultat

class Reptile:
    """Reptile — meta-learning par interpolation simple.
    
    θ ← θ + ε · (θ'_tache - θ)
    
    Avantages :
    - Pas de dérivée seconde
    - Pas de forward fonctionnel
    - Aussi performant que MAML
    - Plus rapide
    """
    def __init__(self, model, inner_lr=0.01, meta_lr=0.1, inner_steps=5):
        self.model = model
        self.inner_lr = inner_lr
        self.meta_lr = meta_lr
        self.inner_steps = inner_steps
        self.optimizer = torch.optim.SGD(model.parameters(), lr=meta_lr)
    
    def meta_train_step(self, task_batch):
        for task in task_batch:
            # Copie des poids
            old_weights = [p.clone() for p in self.model.parameters()]
            
            # Adaptation sur la tâche (SGD standard)
            inner_optim = torch.optim.SGD(self.model.parameters(), 
                                          lr=self.inner_lr)
            for _ in range(self.inner_steps):
                logits = self.model(task['support_x'])
                loss = F.cross_entropy(logits, task['support_y'])
                inner_optim.zero_grad()
                loss.backward()
                inner_optim.step()
            
            # Reptile update : interpolation
            for p, old_p in zip(self.model.parameters(), old_weights):
                p.data = old_p + self.meta_lr * (p.data - old_p)
```

---

## 4. ProtoNet — Prototypical Networks (Snell et al., 2017)

```python
# Approche basée sur les métriques
# Chaque classe est représentée par son prototype (moyenne)
# Classification = distance à chaque prototype

class ProtoNet(nn.Module):
    """Prototypical Networks for Few-Shot Learning.
    
    Pour N-way K-shot :
    1. Encoder les K exemples de chaque classe → prototypes
    2. Query → encoder → distance aux prototypes
    3. Softmax sur les distances négatives
    
    Formule : P(y=c | x) = softmax(-d(f(x), p_c))
    où p_c = 1/K · Σ_{x_i ∈ support_c} f(x_i)
    """
    def __init__(self, encoder, distance='euclidean'):
        super().__init__()
        self.encoder = encoder  # CNN, ResNet, etc.
        self.distance = distance
    
    def forward(self, support_x, support_y, query_x):
        """support_x: (n_way * k_shot, C, H, W)
        support_y: (n_way * k_shot,)
        query_x: (n_way * n_query, C, H, W)
        """
        # Encoder tous les exemples
        support_emb = self.encoder(support_x)  # (n_way*k_shot, D)
        query_emb = self.encoder(query_x)      # (n_way*n_query, D)
        
        # Calculer les prototypes
        n_way = len(torch.unique(support_y))
        prototypes = []
        for c in range(n_way):
            mask = (support_y == c)
            proto = support_emb[mask].mean(dim=0)  # prototype = mean
            prototypes.append(proto)
        prototypes = torch.stack(prototypes)  # (n_way, D)
        
        # Distance aux prototypes
        if self.distance == 'euclidean':
            dists = torch.cdist(query_emb, prototypes)  # (n_query, n_way)
        elif self.distance == 'cosine':
            query_norm = F.normalize(query_emb, dim=1)
            proto_norm = F.normalize(prototypes, dim=1)
            dists = -query_norm @ proto_norm.t()
        
        # Softmax négatif
        logits = -dists  # plus proche = plus probable
        return logits


def proto_loss(logits, query_y):
    """Cross-entropy loss pour ProtoNet."""
    return F.cross_entropy(logits, query_y)


# Exemple complet d'entraînement
def train_protonet(encoder, train_loader, epochs=100):
    model = ProtoNet(encoder)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    for epoch in range(epochs):
        for batch in train_loader:
            # batch = {'support_x': ..., 'support_y': ...,
            #          'query_x': ..., 'query_y': ...}
            logits = model(batch['support_x'], batch['support_y'], 
                          batch['query_x'])
            loss = proto_loss(logits, batch['query_y'])
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
```

---

## 5. Relation Networks (Sung et al., 2018)

```python
# Extension de ProtoNet : la distance n'est pas figée
# Un réseau apprend la métrique de similarité

class RelationNet(nn.Module):
    """Relation Network : apprend la métrique de similarité."""
    def __init__(self, encoder, relation_module):
        super().__init__()
        self.encoder = encoder
        self.relation_module = relation_module  # MLP qui calcule « similarité »
    
    def forward(self, support_x, support_y, query_x):
        # Prototypes comme ProtoNet
        support_emb = self.encoder(support_x)
        n_way = len(torch.unique(support_y))
        
        prototypes = torch.stack([
            support_emb[support_y == c].mean(dim=0)
            for c in range(n_way)
        ])
        
        query_emb = self.encoder(query_x)
        
        # Paires (query, prototype) → relation module
        n_query = query_emb.size(0)
        query_expanded = query_emb.unsqueeze(1).expand(-1, n_way, -1)
        proto_expanded = prototypes.unsqueeze(0).expand(n_query, -1, -1)
        
        # Concaténation des paires
        pairs = torch.cat([query_expanded, proto_expanded], dim=-1)
        pairs = pairs.view(n_query * n_way, -1)
        
        # Score de relation
        relations = self.relation_module(pairs).view(n_query, n_way)
        return relations  # Pas besoin de softmax (relation scores)
```

---

## 6. Métriques et Evaluation

```python
class FewShotEvaluator:
    """Évaluation few-shot avec intervalle de confiance."""
    def __init__(self, model, n_tasks=1000, n_way=5, k_shot=1, n_query=15):
        self.model = model
        self.n_tasks = n_tasks
        self.n_way = n_way
        self.k_shot = k_shot
        self.n_query = n_query
    
    @torch.no_grad()
    def evaluate(self, dataset):
        """Évalue sur n_tasks aléatoires."""
        accuracies = []
        for _ in range(self.n_tasks):
            # Échantillonner une tâche
            task = dataset.sample_task(self.n_way, self.k_shot, self.n_query)
            
            logits = self.model(task['support_x'], task['support_y'],
                               task['query_x'])
            preds = logits.argmax(dim=-1)
            acc = (preds == task['query_y']).float().mean().item()
            accuracies.append(acc)
        
        mean_acc = np.mean(accuracies)
        ci = 1.96 * np.std(accuracies) / np.sqrt(len(accuracies))
        
        return {
            'accuracy': mean_acc,
            'ci_95': ci,
            'tasks': self.n_tasks,
        }

# Benchmarks :
# MiniImageNet : 100 classes, 84×84 images
# TieredImageNet : 608 classes, 84×84
# CIFAR-FS : 100 classes, 32×32
# Omniglot : 1623 caractères, 28×28
```

---

## 7. Meta-Learning pour la Robotique

```python
# MAML est particulièrement adapté pour la robotique :
# - Adaptation rapide à de nouvelles conditions
# - Nouvelle texture, poids, friction
# - Domain randomization + meta-learning

# Exemple : meta-RL (MAML + RL)
# L'agent apprend à s'adapter rapidement
# à de nouvelles récompenses/dynamiques
```

---

## 8. Meta-Learning pour les LLM (2024-2025)

```python
# Les LLM sont des meta-apprenants naturels !
# In-context learning = meta-learning implicite

# Méta-apprentissage explicite pour LLM :
# 1. Apprendre des prompts optimaux (Soft Prompt Tuning)
# 2. Méta-apprendre des jeux de paramètres LoRA
# 3. Apprendre à générer des exemples few-shot

class MetaPromptTuning(nn.Module):
    """Soft prompt tuning = meta-learning."""
    def __init__(self, llm, n_prompt_tokens=16):
        super().__init__()
        self.llm = llm
        self.soft_prompts = nn.Parameter(
            torch.randn(1, n_prompt_tokens, llm.config.d_model)
        )
    
    def meta_learn_prompts(self, task_batch):
        """Méta-apprendre des soft prompts."""
        # Chaque tâche = nouveau jeu de prompts
        pass
```

---

## 9. Algorithmes Comparés

| Algorithme | Type | 5-way 1-shot | 5-way 5-shot | Vitesse |
|-----------|:----:|:----------:|:----------:|:------:|
| MAML | Optimisation | 48.7% | 63.1% | ★★☆☆☆ |
| FOMAML | Optimisation | 48.1% | 62.8% | ★★★☆☆ |
| Reptile | Optimisation | 49.7% | 63.8% | ★★★★☆ |
| ProtoNet | Métrique | 49.4% | 68.2% | ★★★★★ |
| RelationNet | Métrique | 50.4% | 66.3% | ★★★★☆ |
| MatchingNet | Métrique | 43.6% | 56.0% | ★★★★★ |
| MetaOptNet | Optimisation | 52.2% | 69.6% | ★★★☆☆ |

*Benchmark MiniImageNet*

---

## 10. Implémentation Complète Few-Shot

```python
class FewShotTask:
    """Échantillonner une tâche few-shot depuis un dataset."""
    def __init__(self, dataset, n_way=5, k_shot=1, n_query=15):
        self.dataset = dataset  # (images, labels)
        self.n_way = n_way
        self.k_shot = k_shot
        self.n_query = n_query
    
    def sample(self):
        images, labels = self.dataset
        classes = torch.unique(labels)
        selected_classes = classes[torch.randperm(len(classes))[:self.n_way]]
        
        support_x, support_y = [], []
        query_x, query_y = [], []
        
        for i, cls in enumerate(selected_classes):
            cls_indices = (labels == cls).nonzero().squeeze(-1)
            perm = torch.randperm(len(cls_indices))
            
            # K-shot support
            support_idx = cls_indices[perm[:self.k_shot]]
            support_x.append(images[support_idx])
            support_y.append(torch.full((self.k_shot,), i))
            
            # N_query query
            query_idx = cls_indices[perm[self.k_shot:self.k_shot + self.n_query]]
            query_x.append(images[query_idx])
            query_y.append(torch.full((self.n_query,), i))
        
        return {
            'support_x': torch.cat(support_x),
            'support_y': torch.cat(support_y),
            'query_x': torch.cat(query_x),
            'query_y': torch.cat(query_y),
        }
```

---

## Références

- MAML (Finn et al., 2017) : https://arxiv.org/abs/1703.03400
- Reptile (Nichol et al., 2018) : https://arxiv.org/abs/1803.02999
- ProtoNet (Snell et al., 2017) : https://arxiv.org/abs/1703.05175
- RelationNet (Sung et al., 2018) : https://arxiv.org/abs/1711.06025
- MatchingNet (Vinyals et al., 2016) : https://arxiv.org/abs/1606.04080
- Meta-Learning Survey : https://arxiv.org/abs/1810.03548
- Model-Agnostic Meta-Learning (cheat sheet) : https://paperswithcode.com/task/meta-learning