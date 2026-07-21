---
name: graph-neural-networks
description: Guide complet des réseaux de neurones à graphes — GCN, GAT, GIN, GraphSAGE, graphes hétérogènes, Transformers de graphes, applications. En français.
---

# Graph Neural Networks (GNN) — Guide Complet

Apprentissage sur graphes : convolution, attention, message passing, implémentations.

---

## 1. Pourquoi les Graphes ?

```python
# Données structurées en graphe partout :
# - Molécules : atomes = nœuds, liaisons = arêtes
# - Réseaux sociaux : utilisateurs = nœuds, amitiés = arêtes
# - Transport : villes = nœuds, routes = arêtes
# - Code : variables = nœuds, dépendances = arêtes
# - Web : pages = nœuds, liens = arêtes
# - Connaissances : entités = nœuds, relations = arêtes

# Propriété fondamentale : pas de grille régulière
# Chaque nœud a un nombre variable de voisins
# Les GNN généralisent le deep learning à ce domaine
```

### Notations
```python
# G = (V, E) : graphe avec |V| = n nœuds, |E| = m arêtes
# X ∈ ℝ^(n×d) : matrice de features des nœuds
# A ∈ {0,1}^(n×n) : matrice d'adjacence
# E ∈ ℝ^(m×d_e) : features des arêtes
# L ∈ ℝ^d : labels (classification de nœuds/graphes)
```

---

## 2. Message Passing — Le Principe Fondamental

```python
# Tous les GNN sont basés sur le Message Passing :
# h_v^(k+1) = UPDATE(h_v^(k), AGGREGATE({h_u^(k) | u ∈ N(v)}))

# Équivalent en formules :
# m_v^(k+1) = Σ_{u∈N(v)} MESSAGE(h_v^(k), h_u^(k), e_vu)
# h_v^(k+1) = UPDATE(h_v^(k), m_v^(k+1))

class MessagePassingLayer(nn.Module):
    """Couche générique de message passing."""
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.message_fn = nn.Linear(in_dim * 2, out_dim)
        self.update_fn = nn.GRUCell(out_dim, out_dim)
    
    def forward(self, x, adj):
        """x: (n, d) features des nœuds
        adj: (n, n) matrice d'adjacence
        """
        n = x.size(0)
        
        # Étape 1 : calcul des messages
        # Pour chaque arête (i,j), message = f(x_i || x_j)
        messages = []
        for i in range(n):
            neighbors = adj[i].nonzero().squeeze(-1)
            x_i = x[i].expand(len(neighbors), -1)
            x_j = x[neighbors]
            msg = self.message_fn(torch.cat([x_i, x_j], dim=-1))
            messages.append(msg.sum(dim=0))  # AGGREGATION = sum
        
        m = torch.stack(messages)  # (n, out_dim)
        
        # Étape 2 : mise à jour
        h = self.update_fn(m, x)
        return h
```

---

## 3. GCN — Graph Convolutional Network (Kipf & Welling, 2017)

### Formulation
```
H^(l+1) = σ(D̃^(-1/2) · Ã · D̃^(-1/2) · H^(l) · W^(l))

Où :
- Ã = A + I (self-loops)
- D̃_ii = Σ_j Ã_ij (degré)
- H^(0) = X (features initiales)
```

```python
class GCNLayer(nn.Module):
    """Couche GCN (Kipf & Welling, 2017)."""
    def __init__(self, in_features, out_features):
        super().__init__()
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        self.bias = nn.Parameter(torch.FloatTensor(out_features))
        self.reset_parameters()
    
    def reset_parameters(self):
        glorot_uniform(self.weight)
        zeros_(self.bias)
    
    def forward(self, x, adj):
        """x: (n, d_in), adj: (n, n) — normalisée."""
        # GCN conv : D^(-1/2) · A · D^(-1/2) · X · W
        support = torch.mm(x, self.weight)  # (n, d_out)
        output = torch.spmm(adj, support)   # (n, d_out)
        return output + self.bias


class GCN(nn.Module):
    """GCN à 2 couches pour classification de nœuds."""
    def __init__(self, n_features, n_classes, hidden=16):
        super().__init__()
        self.conv1 = GCNLayer(n_features, hidden)
        self.conv2 = GCNLayer(hidden, n_classes)
    
    def forward(self, x, adj_norm):
        # adj_norm : D⁻¹/² · Ã · D⁻¹/² (pré-calculée)
        x = F.relu(self.conv1(x, adj_norm))
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, adj_norm)
        return F.log_softmax(x, dim=1)


def normalize_adj(A):
    """Normalisation symétrique de l'adjacence."""
    A_hat = A + torch.eye(A.size(0), device=A.device)  # self-loops
    D = torch.diag(A_hat.sum(dim=1).pow(-0.5))
    return D @ A_hat @ D
```

### Limitations GCN
```python
# 1. Transductif : besoin du graphe complet pour l'entraînement
# 2. Pas de features d'arêtes
# 3. Même poids pour tous les voisins (pas d'attention)
# 4. Pas de profondeur (>3 couches → oversmoothing)
```

---

## 4. GraphSAGE (Hamilton et al., 2017)

```python
# GraphSAGE = SAmple & aggreGatE
# Solution au problème inductif : généralise à de nouveaux nœuds
# Échantillonne un nombre fixe de voisins (pas tous)

class GraphSAGELayer(nn.Module):
    """Couche GraphSAGE avec échantillonnage."""
    def __init__(self, in_dim, out_dim, n_sample=10, aggregator='mean'):
        super().__init__()
        self.n_sample = n_sample
        self.W = nn.Linear(in_dim * 2, out_dim)  # concatène self + neighbor
        
        if aggregator == 'mean':
            self.aggregate = lambda x: x.mean(dim=0)
        elif aggregator == 'max':
            self.aggregate = lambda x: x.max(dim=0)[0]
        elif aggregator == 'lstm':
            self.aggregate = lambda x: LSTM_aggregator(x.unsqueeze(0)).squeeze(0)
    
    def forward(self, x, adj):
        """Génère des embeddings pour de nouveaux nœuds."""
        n = x.size(0)
        h = []
        
        for i in range(n):
            neighbors = adj[i].nonzero().squeeze(-1)
            if len(neighbors) > self.n_sample:
                neighbors = neighbors[torch.randperm(len(neighbors))[:self.n_sample]]
            
            if len(neighbors) > 0:
                neighbor_emb = self.aggregate(x[neighbors])
            else:
                neighbor_emb = torch.zeros(x.size(1), device=x.device)
            
            # Concaténation + transformation
            combined = torch.cat([x[i], neighbor_emb])
            h.append(F.relu(self.W(combined)))
        
        return torch.stack(h)
```

---

## 5. GAT — Graph Attention Network (Velickovic et al., 2018)

```python
# GAT : attention sur les voisins (poids différents par voisin)
# Chaque nœud apprend l'importance de ses voisins

class GATLayer(nn.Module):
    """Couche d'attention sur graphe (GAT)."""
    def __init__(self, in_dim, out_dim, n_heads=8, concat=True, dropout=0.6):
        super().__init__()
        self.n_heads = n_heads
        self.concat = concat
        self.dropout = dropout
        
        self.W = nn.Linear(in_dim, out_dim * n_heads, bias=False)
        self.a = nn.Parameter(torch.zeros(1, n_heads, 2 * out_dim))
        self.leaky_relu = nn.LeakyReLU(0.2)
        
    def forward(self, x, adj):
        """x: (n, d_in), adj: (n, n)"""
        n = x.size(0)
        
        # Transformation linéaire
        h = self.W(x).view(n, self.n_heads, -1)  # (n, n_heads, d_out)
        
        # Attention coefficients
        # Pour chaque arête, concatène [h_i || h_j]
        h_i = h.unsqueeze(1).expand(-1, n, -1, -1)   # (n, n, n_heads, d)
        h_j = h.unsqueeze(0).expand(n, -1, -1, -1)   # (n, n, n_heads, d)
        
        # Score d'attention e_ij = a^T · [W·h_i || W·h_j]
        concat = torch.cat([h_i, h_j], dim=-1)  # (n, n, n_heads, 2d)
        e = self.leaky_relu((self.a * concat).sum(dim=-1))  # (n, n, n_heads)
        
        # Softmax sur les voisins (masqué par adj)
        e = e.masked_fill(adj.unsqueeze(-1) == 0, float('-inf'))
        alpha = F.softmax(e, dim=1)  # (n, n, n_heads)
        alpha = F.dropout(alpha, self.dropout, training=self.training)
        
        # Agrégation pondérée
        h_prime = (alpha.unsqueeze(-1) * h.unsqueeze(0)).sum(dim=1)
        
        if self.concat:
            return h_prime.view(n, -1)  # concaténer les têtes
        else:
            return h_prime.mean(dim=1)  # moyenner les têtes
```

### GATv2 (Brody et al., 2022)
```python
# GATv2 corrige un problème de GAT : l'attention n'est pas assez expressive
# Changement : a^T · LeakyReLU(W·[h_i || h_j])
#     au lieu de LeakyReLU(a^T · W·[h_i || h_j])
# Résultat : attention strictement plus expressive
```

---

## 6. GIN — Graph Isomorphism Network (Xu et al., 2019)

```python
# GIN : aussi expressif que le test de Weisfeiler-Lehman
# Théoriquement le GNN le plus expressif possible (message passing)

class GINLayer(nn.Module):
    """Graph Isomorphism Network.
    
    h_v^(k+1) = MLP((1 + ε) · h_v^(k) + Σ_{u∈N(v)} h_u^(k))
    """
    def __init__(self, in_dim, out_dim, epsilon=None):
        super().__init__()
        if epsilon is None:
            self.eps = nn.Parameter(torch.zeros(1))
        else:
            self.eps = epsilon
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, out_dim),
            nn.BatchNorm1d(out_dim),
            nn.ReLU(),
            nn.Linear(out_dim, out_dim),
        )
    
    def forward(self, x, adj):
        # Aggregation sum
        neighbor_sum = torch.mm(adj, x)  # somme des voisins
        
        # Combinaison
        combined = (1 + self.eps) * x + neighbor_sum
        return self.mlp(combined)
```

---

## 7. Graph Transformers (2021-2024)

```python
# Les Transformers s'appliquent aussi aux graphes !
# Mais attention O(n²) vs graphes souvent creux

class GraphTransformer(nn.Module):
    """Transformer adapté aux graphes.
    
    Innovations :
    1. Positional Encoding structurel (Laplacian PE)
    2. Attention masquée par l'adjacence (ou biais structurel)
    3. Features d'arêtes dans l'attention
    """
    def __init__(self, d_model=512, n_heads=8, n_layers=6):
        super().__init__()
        self.layers = nn.ModuleList([
            TransformerLayer(d_model, n_heads) for _ in range(n_layers)
        ])
        self.laplacian_pe = LaplacianPE(d_model)  # PE structurel
    
    def forward(self, x, adj, edge_attr=None):
        # Positional encoding (Laplacien)
        laplacian_emb = self.laplacian_pe(adj)
        x = x + laplacian_emb
        
        for layer in self.layers:
            if edge_attr is not None:
                x = layer(x, adj, edge_attr)
            else:
                x = layer(x, adj)
        return x


class LaplacianPE(nn.Module):
    """Positional Encoding basé sur le Laplacien du graphe.
    
    Les k plus petites valeurs propres du Laplacien
    donnent une signature unique de la position dans le graphe.
    """
    def __init__(self, d_model, k=8):
        super().__init__()
        self.k = k
        self.proj = nn.Linear(k, d_model)
    
    def forward(self, adj):
        # L = D - A (Laplacien)
        D = torch.diag(adj.sum(dim=-1))
        L = D - adj
        
        # Top-k eigenvectors
        eigenvals, eigenvecs = torch.linalg.eigh(L)
        pe = eigenvecs[:, :self.k]  # (n, k)
        
        return self.proj(pe)
```

---

## 8. Applications

### Classification de molécules
```python
class MoleculeGNN(nn.Module):
    """GNN pour prédire les propriétés des molécules."""
    def __init__(self, node_dim, edge_dim, hidden=64):
        super().__init__()
        self.conv1 = GINLayer(node_dim, hidden)
        self.conv2 = GINLayer(hidden, hidden)
        self.conv3 = GINLayer(hidden, hidden)
        self.pool = global_mean_pool
        self.classifier = nn.Linear(hidden, 2)
    
    def forward(self, data):
        x, adj, batch = data.x, data.adj, data.batch
        x = self.conv1(x, adj)
        x = self.conv2(x, adj)
        x = self.conv3(x, adj)
        x = self.pool(x, batch)  # global mean → 1 embedding par molécule
        return self.classifier(x)
```

### GNN pour la programmation (code)
```python
# Code Transformers avec graphe de flot de contrôle + graphe de dépendances
# GraphCodeBERT, CodeGNN, etc.
# Améliore : summarization, bug detection, etc.
```

### Recommender Systems
```python
# PinSAGE (Pinterest) : GNN pour recommandation
# LightGCN : simplifié, meilleur que MF sur collaborative filtering
```

---

## 9. Implémentation Complète (PyTorch Geometric)

```python
# pip install torch_geometric

import torch_geometric as pyg
from torch_geometric.nn import GCNConv, GATConv, SAGEConv
from torch_geometric.data import Data

# Création d'un graphe
edge_index = torch.tensor([[0, 1, 1, 2],
                            [1, 0, 2, 1]], dtype=torch.long)
x = torch.randn(3, 4)  # 3 nœuds, 4 features
data = Data(x=x, edge_index=edge_index)

# GCN avec PyG
class GCN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(4, 16)
        self.conv2 = GCNConv(16, 7)
    
    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)
```

---

## 10. Tableau des GNN

| Modèle | Message | Aggregation | Expressivité | Inductif | Année |
|--------|---------|:-----------:|:------------:|:--------:|:----:|
| GCN | W·h_j | Mean | ★★★☆☆ | Transductif | 2017 |
| GraphSAGE | W·[h_i, h_j] | Mean/Max/LSTM | ★★★☆☆ | ✓ | 2017 |
| GAT | α_ij · W·h_j | Attention | ★★★★☆ | ✓ | 2018 |
| GATv2 | α_ij · W·h_j | Attention | ★★★★★ | ✓ | 2022 |
| GIN | (1+ε)·h_i + Σh_j | Sum | ★★★★★ | ✓ | 2019 |
| GraphTransf. | Attention + PE | Full Attention | ★★★★★ | ✓ | 2021 |
| GPS | Mix GNN + Transf. | Global + Local | ★★★★★ | ✓ | 2022 |

---

## 11. Oversmoothing et Solutions

```python
# Problème : avec >3 couches GCN, tous les nœuds
# deviennent identiques (convergent vers une constante)
#
# Solutions :
# 1. Skip connections (JK-Net, DeepGCN)
# 2. PairNorm : normalise les embeddings après chaque couche
# 3. DropEdge : retire aléatoirement des arêtes
# 4. Normalisation (réduit l'anisotropie)
# 5. Mix d'ordre élevé (GPR-GNN)

class JKNet(nn.Module):
    """Jumping Knowledge Network (Xu et al., 2018).
    
    Concatène les sorties de toutes les couches :
    h_final = [h^(1), h^(2), h^(3), ..., h^(K)]
    """
    def __init__(self, n_layers=4, hidden=64):
        self.layers = nn.ModuleList([GCNLayer(hidden, hidden) 
                                      for _ in range(n_layers)])
        self.jk = nn.Linear(hidden * n_layers, hidden)
```

---

## Références

- GCN (Kipf & Welling, 2017) : https://arxiv.org/abs/1609.02907
- GraphSAGE (Hamilton et al., 2017) : https://arxiv.org/abs/1706.02216
- GAT (Velickovic et al., 2018) : https://arxiv.org/abs/1710.10903
- GATv2 (Brody et al., 2022) : https://arxiv.org/abs/2105.14491
- GIN (Xu et al., 2019) : https://arxiv.org/abs/1810.00826
- Graph Transformer : https://arxiv.org/abs/2012.09699
- PyTorch Geometric : https://pytorch-geometric.readthedocs.io/
- Oversmoothing : https://arxiv.org/abs/2009.08819
- JK-Net : https://arxiv.org/abs/1806.03536