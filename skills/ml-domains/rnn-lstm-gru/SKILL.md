---
name: rnn-lstm-gru
description: Guide complet des réseaux de neurones récurrents — RNN, LSTM, GRU, backpropagation through time, bidirectionnel, architectures modernes. En français.
---

# RNN / LSTM / GRU — Guide Complet

Des fondamentaux aux variantes modernes, implémentations et applications 2025.

---

## 1. Le Problème des Séquences

```python
# Données séquentielles : pas d'indépendance i.i.d.
# Chaque entrée dépend des précédentes
# Besoin de mémoire : hidden state h_t

# Séquences typiques :
# - Texte : h_t = f(tok_t, h_{t-1})
# - Audio : h_t = f(frame_t, h_{t-1})
# - Time series : h_t = f(x_t, h_{t-1})
# - Vidéo : h_t = f(frame_t, h_{t-1})
```

---

## 2. Vanilla RNN (Elman, 1990)

### Formulation mathématique
```
h_t = tanh(W_h · h_{t-1} + W_x · x_t + b)
y_t = W_y · h_t + b_y

h_t ∈ ℝ^d : hidden state
x_t ∈ ℝ^n : entrée à l'instant t
W_h ∈ ℝ^(d×d) : poids récurrent
W_x ∈ ℝ^(d×n) : poids d'entrée
```

```python
class RNNCell(nn.Module):
    """Cellule RNN vanilla."""
    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.W_xh = nn.Linear(input_size, hidden_size)
        self.W_hh = nn.Linear(hidden_size, hidden_size)
    
    def forward(self, x: torch.Tensor, h_prev: torch.Tensor):
        """x: (batch, input_size), h_prev: (batch, hidden_size)"""
        h = torch.tanh(self.W_xh(x) + self.W_hh(h_prev))
        return h


class VanillaRNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers=1):
        super().__init__()
        self.rnn_cells = nn.ModuleList([
            RNNCell(input_size if i == 0 else hidden_size, hidden_size)
            for i in range(num_layers)
        ])
    
    def forward(self, x: torch.Tensor):
        """x: (batch, seq_len, input_size)"""
        batch, seq_len, _ = x.shape
        h = [torch.zeros(batch, cell.hidden_size, device=x.device)
             for cell in self.rnn_cells]
        
        outputs = []
        for t in range(seq_len):
            x_t = x[:, t, :]
            for i, cell in enumerate(self.rnn_cells):
                h[i] = cell(x_t if i == 0 else h[i-1], h[i])
            outputs.append(h[-1])
        
        return torch.stack(outputs, dim=1), h[-1]
```

### Backpropagation Through Time (BPTT)
```python
# Le gradient se propage à travers le temps (t → t-1 → ...)
# ∂L/∂W_h = Σ_t ∂L/∂h_t · ∂h_t/∂W_h
# ∂h_t/∂h_{t-1} = W_h · (1 - tanh²(W_h·h_{t-1} + ...))

# Problème : vanishing gradient
# ||∂h_t/∂h_{t-k}|| ≤ ||W_h||^k → 0 si ||W_h|| < 1
# → Impossible d'apprendre des dépendances longues (> 10-20 pas)
```

### Problèmes des RNN vanilla

| Problème | Cause | Conséquence |
|----------|-------|-------------|
| Vanishing gradient | ||W_h|| < 1 | Dépendances longues impossibles |
| Exploding gradient | ||W_h|| > 1 | NaN, instabilité |
| Saturation tanh | |net| >> 1 | Gradient mort |
| Forgetfulness | Compression non-linéaire | Tout oublie rapidement |

---

## 3. LSTM (Hochreiter & Schmidhuber, 1997)

### Architecture
```
┌─────────────────────────────────────┐
│              Cell State C_t         │
│   ┌─────────────────────────────┐   │
│   │  oublie     entrée    sortie │   │
│   │  C_t = f·C_{t-1} + i·C~_t  │   │
│   └─────────────────────────────┘   │
│                                      │
│  f_t = σ(W_f·[h_{t-1}, x_t])       │ ← Forget gate
│  i_t = σ(W_i·[h_{t-1}, x_t])       │ ← Input gate
│  C~_t = tanh(W_C·[h_{t-1}, x_t])   │ ← Candidate
│  o_t = σ(W_o·[h_{t-1}, x_t])       │ ← Output gate
│  h_t = o_t · tanh(C_t)             │
└─────────────────────────────────────┘
```

### Implémentation complète
```python
class LSTMCell(nn.Module):
    """Cellule LSTM avec les 4 portes."""
    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Concaténation des 4 portes en un seul Linear pour efficacité
        self.gates = nn.Linear(input_size + hidden_size, 4 * hidden_size)
    
    def forward(self, x, state):
        """x: (batch, input_size)
        state: (h, c)  # hidden state + cell state
        """
        h_prev, c_prev = state
        
        # Calcul des 4 portes en parallèle
        gates = self.gates(torch.cat([x, h_prev], dim=-1))
        f, i, o, g = gates.chunk(4, dim=-1)
        
        # Sigmoid pour les portes, tanh pour le candidat
        forget = torch.sigmoid(f)   # Porte d'oubli
        input_ = torch.sigmoid(i)    # Porte d'entrée
        output = torch.sigmoid(o)    # Porte de sortie
        candidate = torch.tanh(g)    # Nouveau contenu candidat
        
        # Mise à jour cell state
        c = forget * c_prev + input_ * candidate
        h = output * torch.tanh(c)
        
        return h, c


class LSTM(nn.Module):
    """Implémentation complète bidirectionnelle."""
    def __init__(self, input_size, hidden_size, num_layers=1, 
                 bidirectional=False, dropout=0.0):
        super().__init__()
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1
        
        # Couches empilées
        self.cells = nn.ModuleList()
        for l in range(num_layers):
            for d in range(self.num_directions):
                inp = input_size if l == 0 else hidden_size * self.num_directions
                self.cells.append(LSTMCell(inp, hidden_size))
        
        self.dropout = nn.Dropout(dropout) if dropout > 0 else nn.Identity()
    
    def forward(self, x, states=None):
        """x: (batch, seq_len, input_size)"""
        batch, seq_len, _ = x.shape
        hidden = self.hidden_size
        
        # Initialisation des états
        if states is None:
            h = [torch.zeros(batch, hidden, device=x.device) 
                 for _ in range(len(self.cells))]
            c = [torch.zeros(batch, hidden, device=x.device) 
                 for _ in range(len(self.cells))]
        
        # Boucle temporelle
        outputs = []
        for t in range(seq_len):
            x_t = x[:, t, :]
            
            # Forward direction
            for l in range(self.num_layers):
                idx = l * self.num_directions
                h[idx], c[idx] = self.cells[idx](x_t, (h[idx], c[idx]))
                x_t = self.dropout(h[idx])
            
            # Backward direction (si bidirectionnel)
            if self.bidirectional:
                x_t = x[:, seq_len - 1 - t, :]  # lecture inverse
                for l in range(self.num_layers):
                    idx = l * self.num_directions + 1
                    h[idx], c[idx] = self.cells[idx](x_t, (h[idx], c[idx]))
                    x_t = self.dropout(h[idx])
            
            # Concaténation des directions
            if self.bidirectional:
                outputs.append(torch.cat([h[0], h[1]], dim=-1))
            else:
                outputs.append(h[0])
        
        return torch.stack(outputs, dim=1), (h, c)
```

### Pourquoi LSTM résout le vanishing gradient ?
```python
# ∂C_t/∂C_{t-1} = f_t  (porte d'oubli)
# Si f_t ≈ 1, le gradient passe sans atténuation
# Le LSTM peut apprendre des dépendances de 100+ pas
# C'est le « highway gradient » — autoroute du gradient
```

---

## 4. GRU (Cho et al., 2014)

### Architecture
```
h_t = (1 - z_t) · h_{t-1} + z_t · h~_t

r_t = σ(W_r·[h_{t-1}, x_t])   ← Reset gate
z_t = σ(W_z·[h_{t-1}, x_t])   ← Update gate
h~_t = tanh(W·[r_t·h_{t-1}, x_t])  ← Candidat

2 portes au lieu de 4 (LSTM)
Pas de cell state séparé
```

```python
class GRUCell(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        # Reset et update gates en parallèle
        self.rz_gates = nn.Linear(input_size + hidden_size, 2 * hidden_size)
        self.new_gate = nn.Linear(input_size + hidden_size, hidden_size)
    
    def forward(self, x, h_prev):
        combined = torch.cat([x, h_prev], dim=-1)
        r_and_z = self.rz_gates(combined)
        r, z = r_and_z.chunk(2, dim=-1)
        r = torch.sigmoid(r)
        z = torch.sigmoid(z)
        
        h_candidate = self.new_gate(torch.cat([x, r * h_prev], dim=-1))
        h_candidate = torch.tanh(h_candidate)
        
        h = (1 - z) * h_prev + z * h_candidate
        return h
```

### LSTM vs GRU

| Propriété | LSTM | GRU |
|-----------|------|-----|
| Portes | 4 (f, i, o, g) | 2 (r, z) |
| Paramètres | 4(d²+di) | 3(d²+di) |
| Cell state | Oui (C_t) | Non |
| Protection oubli | Explicite (porte f) | Implicite (z) |
| Performance | Similaire (lég. mieux) | Similaire (plus rapide) |
| Petits datasets | ★★★★☆ | ★★★★☆ |
| Grands datasets | ★★★★★ | ★★★★★ |

---

## 5. Bidirectional RNN (BiRNN)

```python
class BidirectionalLSTM(nn.Module):
    """LSTM qui voit le futur et le passé."""
    def __init__(self, input_size, hidden_size, num_layers=1):
        super().__init__()
        self.forward_lstm = LSTM(input_size, hidden_size, num_layers)
        self.backward_lstm = LSTM(input_size, hidden_size, num_layers)
    
    def forward(self, x):
        # Direction avant : normal
        h_fwd, _ = self.forward_lstm(x)
        
        # Direction arrière : séquence inversée
        x_rev = torch.flip(x, dims=[1])
        h_bwd, _ = self.backward_lstm(x_rev)
        h_bwd = torch.flip(h_bwd, dims=[1])
        
        # Concaténation
        return torch.cat([h_fwd, h_bwd], dim=-1)

# Applications : NER, POS tagging, traduction
# Avantage : contexte complet des deux côtés
# Inconvénient : pas causal (ne peut pas stream)
```

---

## 6. Architectures Empilées (Stacked RNN)

```python
# Avantages :
# - Hiérarchie temporelle
# - Représentations plus abstraites à chaque couche
# - Capturer différentes échelles de temps

# Désavantages :
# - Plus de paramètres
# - Gradient plus difficile (plus de couches)
# - Vanishing/exploding gradient multiplié

# Solution moderne : residual connections entre les couches
class ResidualLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers=4):
        super().__init__()
        self.layers = nn.ModuleList([
            LSTMCell(input_size if i == 0 else hidden_size, hidden_size)
            for i in range(num_layers)
        ])
    
    def forward(self, x):
        for layer in self.layers:
            residual = x
            x = layer(x)
            if x.shape == residual.shape:
                x = x + residual  # skip connection
        return x
```

---

## 7. Variantes Modernes (2019-2025)

### QRNN (Quasi-RNN, 2017)
```python
# Combine convolutions 1D (parallélisable) + portes LSTM
# ~16x plus rapide que LSTM à l'entraînement
# ~4x plus rapide à l'inférence
```

### IndRNN (Independently RNN, 2018)
```python
# W_h est une matrice diagonale : chaque neurone est indépendant
# Évite le vanishing/exploding gradient
# Peut apprendre des séquences de 5000+ pas
```

### Phased LSTM (2016)
```python
# Porte chronométrée : ouvre/ferme périodiquement
# Pour données avec événements irréguliers
```

### Neural ODE (2018)
```python
# h_{t+1} = h_t + f(h_t, t) · dt
# Temps continu : peut interpoler à n'importe quel instant
# Paramètre le temps comme variable continue
```

---

## 8. Applications Clés (2025)

| Domaine | Modèle | Pourquoi RNN/LSTM |
|---------|--------|-------------------|
| **Forecasting financier** | LSTM + Attention | Séries temporelles multi-scale |
| **Reconnaissance vocale** | BiLSTM + CTC | Séquences audio alignées |
| **Traduction automatique** | LSTM + Attention | Seq2Seq |
| **Génération musicale** | LSTM + VAE | Patterns temporels longs |
| **Anomalie détection** | LSTM-Autoencoder | Reconstruction de séquences |
| **Healthcare (ECG)** | BiLSTM | Signaux vitaux longs |
| **Contrôle robotique** | GRU | Planification séquentielle |

### Time Series Forecasting avec LSTM
```python
class TimeSeriesLSTM(nn.Module):
    def __init__(self, n_features, hidden=128, n_layers=2, n_outputs=1):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, n_layers, 
                            batch_first=True, dropout=0.2)
        self.regressor = nn.Sequential(
            nn.Linear(hidden, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, n_outputs),
        )
    
    def forward(self, x):
        # x: (batch, seq_len, n_features)
        _, (h_n, _) = self.lstm(x)  # h_n: (n_layers, batch, hidden)
        h_last = h_n[-1]  # dernière couche
        return self.regressor(h_last)
```

---

## 9. LSTM / GRU vs Transformers

| Critère | LSTM/GRU | Transformer |
|---------|----------|-------------|
| **Complexité** | O(n) | O(n²) |
| **Parallélisation** | Séquentielle | Parallèle (pas de récurrence) |
| **Dépendances longues** | ✓ (avec porte d'oubli) | ✓✓ (attention directe) |
| **Streaming/online** | ✓✓ (état récurrent) | ✗ (besoin séquence complète) |
| **Petites données** | ✓✓ | ✗ (besoin beaucoup) |
| **Grandes données** | ✓ | ✓✓ |
| **Compréhension** | Facile | Difficile (attention maps) |

### Quand utiliser RNN/LSTM en 2025 ?
```python
# 1. Streaming (audio, trading en temps réel)
# 2. Séquences courtes (< 100 tokens)
# 3. Données limitées
# 4. Besoin de contrôle explicite du temps
# 5. Combinaison avec Transformer (mamba-lstm hybride)
```

---

## 10. Hybrides RNN-Transformer

### Transformer avec biais récurrent (2023-2025)
```python
class RecurrentMemoryTransformer(nn.Module):
    """Transformer avec état récurrent compressé."""
    def __init__(self, d_model, n_heads, memory_size=64):
        super().__init__()
        self.memory_tokens = nn.Parameter(torch.randn(1, memory_size, d_model))
        self.attention = MultiHeadAttention(d_model, n_heads)
        self.memory_update = GRUCell(d_model, d_model)
    
    def forward(self, x, memory_prev):
        # Concatène mémoire aux tokens
        combined = torch.cat([x, memory_prev.expand(x.size(0), -1, -1)], dim=1)
        out = self.attention(combined, combined, combined)
        
        # Extrait et met à jour la mémoire
        memory_new = out[:, -memory_size:, :].mean(dim=1)
        memory_new = self.memory_update(memory_new, memory_prev.mean(dim=1))
        return out[:, :-memory_size, :], memory_new
```

---

## Références

- LSTM (Hochreiter, 1997) : https://www.bioinf.jku.at/publications/older/2604.pdf
- GRU (Cho, 2014) : https://arxiv.org/abs/1406.1078
- QRNN : https://arxiv.org/abs/1611.01576
- IndRNN : https://arxiv.org/abs/1803.04831
- BiLSTM-CRF : https://arxiv.org/abs/1508.01991
- Phased LSTM : https://arxiv.org/abs/1610.09513
- Neural ODE : https://arxiv.org/abs/1806.07366
- Le défi du long-range arena : https://arxiv.org/abs/2011.04006