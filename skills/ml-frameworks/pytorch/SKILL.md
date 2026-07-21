---
name: pytorch
description: Guide complet de PyTorch — tenseurs, autograd, nn.Module, DataLoader, GPU, entraînement, déploiement, TorchScript, optimiseurs, et bonnes pratiques. En français.

---

# PyTorch — Guide Complet (Français)

Framework de deep learning par Meta. PyTorch 2.x avec `torch.compile`.

---

## 1. Installation et Concepts

```bash
pip install torch torchvision torchaudio
# GPU CUDA : pip install torch --index-url https://download.pytorch.org/whl/cu124
```

### Concept central
- **Tenseur** = tableau multidimensionnel (CPU ou GPU)
- **Autograd** = différenciation automatique
- **nn.Module** = brique de base des réseaux
- **DataLoader** = chargement par lots
- **torch.compile** = compilation JIT (PyTorch 2.0+)

---

## 2. Tenseurs

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# Création
x = torch.tensor([1.0, 2.0, 3.0])
y = torch.zeros(3, 4)
z = torch.ones(2, 3, dtype=torch.float32)
identite = torch.eye(3)
aleatoire = torch.randn(5, 10)  # N(0, 1)
arange = torch.arange(0, 10, 0.5)

# Types
x = torch.tensor([1, 2], dtype=torch.int32)   # int32
x = torch.tensor([1.0], dtype=torch.float64)   # float64
x = x.float()                                   # conversion
x = x.long()

# GPU
if torch.cuda.is_available():
    x = x.cuda()          # ou x.to('cuda')
    x = x.to('cuda:0')
x = x.cpu()               # Retour au CPU

# Indexation et reshaping
x = torch.randn(3, 4, 5)
print(x.shape)            # torch.Size([3, 4, 5])
x[0, :, :]                # Premier élément
x.view(-1, 5)             # Reshape : 12×5
x.reshape(12, 5)          # Reshape (peut copier)
x.unsqueeze(0)            # Ajouter dimension (1, 3, 4, 5)
x.squeeze()               # Retirer dimensions de taille 1
x.permute(2, 0, 1)        # Transposition généralisée
x.transpose(0, 1)         # Échanger deux dimensions

# Opérations
a + b                     # Addition élément par élément
a @ b                     # Multiplication matricielle
torch.matmul(a, b)
torch.cat([a, b], dim=0)  # Concaténation
torch.stack([a, b], dim=0)# Empilement
a.sum(), a.mean(), a.std()
a.max(), a.min(), a.argmax()
```

---

## 3. Autograd (Différenciation Automatique)

```python
# Tous les tenseurs avec requires_grad=True tracent l'historique
x = torch.tensor([2.0, 3.0], requires_grad=True)
y = x ** 2 + 3 * x + 1

# Calculer les gradients
y.sum().backward()
print(x.grad)  # dy/dx = 2x + 3 → [7, 9]

# Détacher du graphe
z = y.detach()                # Nouveau tenseur sans historique
with torch.no_grad():         # Contexte sans gradient
    predictions = modele(x)

# Zéro les gradients (important !)
optimiseur.zero_grad()
modele.zero_grad()

# Rétropropagation manuelle
perte = (predictions - cibles).pow(2).sum()
perte.backward()
```

---

## 4. nn.Module — Construction de Réseaux

```python
class MLP(nn.Module):
    """Perceptron multicouche avec dropout et batch norm."""
    
    def __init__(
        self,
        dim_entree: int = 784,
        dim_cachee: int = 256,
        dim_sortie: int = 10,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        
        self.fc1 = nn.Linear(dim_entree, dim_cachee)
        self.bn1 = nn.BatchNorm1d(dim_cachee)
        self.fc2 = nn.Linear(dim_cachee, dim_cachee)
        self.bn2 = nn.BatchNorm1d(dim_cachee)
        self.fc3 = nn.Linear(dim_cachee, dim_sortie)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout(x)
        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

# Initialisation
modele = MLP(dim_entree=784, dim_cachee=512, dim_sortie=10)

# Poids initiaux personnalisés
def init_poids(m: nn.Module) -> None:
    if isinstance(m, nn.Linear):
        nn.init.kaiming_normal_(m.weight, mode='fan_out')
        nn.init.zeros_(m.bias)

modele.apply(init_poids)

# Accéder aux paramètres
for nom, param in modele.named_parameters():
    print(f"{nom}: {param.shape}")

# Nombre total de paramètres
total = sum(p.numel() for p in modele.parameters())
print(f"Paramètres : {total:,}")
```

---

## 5. Fonctions de Perte et Optimiseurs

```python
# Pertes
perte_mse = nn.MSELoss()
perte_ce = nn.CrossEntropyLoss()          # Softmax + NLL intégré
perte_bce = nn.BCEWithLogitsLoss()        # BCE + sigmoïde

# Optimiseurs
optimiseur = torch.optim.Adam(modele.parameters(), lr=1e-3)
optimiseur = torch.optim.SGD(modele.parameters(), lr=0.01, momentum=0.9)
optimiseur = torch.optim.AdamW(modele.parameters(), lr=1e-3, weight_decay=1e-4)

# Scheduler (ajustement du learning rate)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimiseur, T_max=100
)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimiseur, mode='min', patience=10
)
scheduler = torch.optim.lr_scheduler.StepLR(optimiseur, step_size=30, gamma=0.1)

# Boucle d'entraînement
for epoch in range(epochs):
    modele.train()
    for x, y in train_loader:
        x, y = x.to(device), y.to(device)
        
        optimiseur.zero_grad()
        predictions = modele(x)
        perte = critere(predictions, y)
        perte.backward()
        optimiseur.step()
    
    scheduler.step()
```

---

## 6. Datasets et DataLoaders

```python
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, transforms

# Dataset personnalisé
class MonDataset(Dataset):
    """Dataset personnalisé pour données tabulaires."""
    
    def __init__(self, donnees: torch.Tensor, cibles: torch.Tensor):
        self.donnees = donnees
        self.cibles = cibles
    
    def __len__(self) -> int:
        return len(self.donnees)
    
    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.donnees[idx], self.cibles[idx]

# DataLoader
loader = DataLoader(
    dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,
    pin_memory=True,    # Accélère transfert CPU→GPU
    drop_last=True,     # Jeter le dernier batch incomplet
)

# Transformations (vision)
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

dataset = datasets.CIFAR10(
    root='./data', train=True,
    download=True, transform=transform,
)
```

---

## 7. Boucle d'Entraînement Complète

```python
def entrainer_epoch(
    modele: nn.Module,
    loader: DataLoader,
    optimiseur: torch.optim.Optimizer,
    critere: nn.Module,
    device: torch.device,
) -> float:
    """Exécute une époque d'entraînement."""
    modele.train()
    perte_totale = 0.0
    
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimiseur.zero_grad()
        predictions = modele(x)
        perte = critere(predictions, y)
        perte.backward()
        torch.nn.utils.clip_grad_norm_(modele.parameters(), 1.0)
        optimiseur.step()
        perte_totale += perte.item()
    
    return perte_totale / len(loader)


@torch.no_grad()
def evaluer(
    modele: nn.Module,
    loader: DataLoader,
    device: torch.device,
) -> tuple[float, float]:
    """Évalue le modèle (précision + perte)."""
    modele.eval()
    correct, total, perte_totale = 0, 0, 0.0
    critere = nn.CrossEntropyLoss()
    
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        predictions = modele(x)
        perte_totale += critere(predictions, y).item()
        _, predites = predictions.max(1)
        correct += predites.eq(y).sum().item()
        total += y.size(0)
    
    return correct / total, perte_totale / len(loader)
```

---

## 8. Sauvegarde et Chargement

```python
# Sauvegarder (checkpoint complet)
torch.save({
    'epoch': epoch,
    'model_state_dict': modele.state_dict(),
    'optimizer_state_dict': optimiseur.state_dict(),
    'perte': perte,
}, 'checkpoint.pt')

# Charger
checkpoint = torch.load('checkpoint.pt')
modele.load_state_dict(checkpoint['model_state_dict'])
optimiseur.load_state_dict(checkpoint['optimizer_state_dict'])
epoch = checkpoint['epoch']

# Sauvegarder juste les poids (inférence)
torch.save(modele.state_dict(), 'poids.pt')
modele.load_state_dict(torch.load('poids.pt'))
```

---

## 9. torch.compile (PyTorch 2.0+)

```python
# Compiler le modèle pour plus de performances
modele = torch.compile(modele)                    # Mode par défaut
modele = torch.compile(modele, mode='reduce-overhead')  # Grande perf
modele = torch.compile(modele, mode='max-autotune')     # Meilleure perf

# Avec options
modele = torch.compile(
    modele,
    backend='inductor',       # Backend par défaut (C++/Triton)
    dynamic=False,            # Formes statiques (plus rapide)
)

# Attention : première exécution lente (compilation), puis rapide
```

---

## 10. Architectures Courantes

```python
# CNN
class CNN(nn.Module):
    def __init__(self, nb_classes: int = 10):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(), nn.MaxPool2d(2),
        )
        self.fc = nn.Linear(64 * 8 * 8, nb_classes)
    
    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)

# RNN/LSTM
class LSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, nb_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, nb_classes)
    
    def forward(self, x):
        x = self.embedding(x)
        _, (hidden, _) = self.lstm(x)
        return self.fc(hidden[-1])

# Transformer (torch.nn.Transformer)
class PetitTransformer(nn.Module):
    def __init__(self, d_model=512, nhead=8, num_layers=6):
        super().__init__()
        self.transformer = nn.Transformer(
            d_model=d_model, nhead=nhead,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers,
        )
```

---

## 11. Déploiement

```python
# TorchScript (modèle sérialisé)
script = torch.jit.script(modele)
script.save('modele_script.pt')
modele_charge = torch.jit.load('modele_script.pt')

# ONNX (interopérabilité)
torch.onnx.export(
    modele,
    torch.randn(1, 3, 224, 224),
    'modele.onnx',
    input_names=['input'],
    output_names=['output'],
)

# Quantification
modele_q = torch.quantization.quantize_dynamic(
    modele, {nn.Linear}, dtype=torch.qint8
)
```

---

## Références
- PyTorch Docs : https://pytorch.org/docs/stable/
- PyTorch Tutorials : https://pytorch.org/tutorials/
- torch.compile : https://pytorch.org/docs/stable/torch.compiler.html