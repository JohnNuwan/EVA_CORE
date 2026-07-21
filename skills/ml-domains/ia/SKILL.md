---
name: ia
description: Guide complet d'Intelligence Artificielle — machine learning, deep learning, NLP, RL, transformers, MLOps, et écosystème IA. En français.

---

# Intelligence Artificielle — Guide Complet (Français)

Panorama complet de l'IA : fondamentaux, algorithmes, architectures et mise en production.

---

## 1. Fondamentaux du Machine Learning

### Types d'apprentissage
- **Supervisé** : données étiquetées (classification, régression)
- **Non supervisé** : pas d'étiquettes (clustering, réduction de dimension)
- **Semi-supervisé** : peu de labels, beaucoup de données non étiquetées
- **Par renforcement** : agent ↔ environnement, récompenses
- **Auto-supervisé** : labels générés automatiquement (SSL, BERT, SimCLR)

### Pipeline ML classique
```
Données → Nettoyage → Features → Modèle → Évaluation → Déploiement
          (NaN, Outliers)  (Normalisation, (Train/Val/Test)
                            Encoding)
```

---

## 2. Scikit-learn — ML Classique

```python
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, classification_report

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Pipeline
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), ['age', 'salaire']),
    ('cat', OneHotEncoder(drop='first'), ['ville', 'profession']),
])

pipeline = Pipeline([
    ('preprocess', preprocessor),
    ('classifier', LogisticRegression()),
])

# Grid Search
param_grid = {
    'classifier__C': [0.01, 0.1, 1, 10],
    'classifier__penalty': ['l1', 'l2'],
}

grid = GridSearchCV(pipeline, param_grid, cv=5, scoring='f1')
grid.fit(X_train, y_train)

print(f"Meilleurs paramètres : {grid.best_params_}")
print(f"Score test : {grid.score(X_test, y_test):.3f}")
```

### Algorithmes clés

```python
from sklearn.linear_model import LogisticRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA

# Classification
rf = RandomForestClassifier(n_estimators=100, max_depth=10)
xgb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1)

# Régression
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Clustering
kmeans = KMeans(n_clusters=5, random_state=42)
dbscan = DBSCAN(eps=0.5, min_samples=5)

# Réduction de dimension
pca = PCA(n_components=0.95)  # Garder 95% de variance
X_reduit = pca.fit_transform(X)
```

---

## 3. Deep Learning

### Perceptron Multicouche (MLP)
```
Entrée → [FC + ReLU + Dropout] × N → FC → Softmax/Sigmoid
```

### CNN (Convolutional Neural Network)
```
Image → [Conv → BN → ReLU → Pool] × N → Flatten → FC → Output
```

### RNN / LSTM / GRU
```
Séquence → [LSTM → Dropout] × N → FC → Output
```

### Transformer
```
Tokens → Embedding + Positional Encoding → [Multi-Head Attention + FFN] × N → Output
```

### Architectures modernes (2024+)
- **ViT** : Transformer pour la vision
- **Mamba / SSM** : Alternative aux Transformers (linéaire en séquence)
- **MoE** : Mixture of Experts (Mixtral)
- **Diffusion** : Génération d'images (Stable Diffusion, DALL-E)
- **GAN** : Réseaux antagonistes génératifs

---

## 4. NLP (Natural Language Processing)

```python
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    AutoModelForCausalLM, pipeline,
)

# Pipeline HuggingFace
classifier = pipeline("sentiment-analysis")
resultat = classifier("J'adore ce produit !")

ner = pipeline("ner", model="Jean-Baptiste/camembert-ner")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Tokenizer + Modèle
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)

inputs = tokenizer("Texte à classifier", return_tensors="pt")
outputs = model(**inputs)
```

### Tâches NLP
- **Classification de texte** : sentiment, topic, spam
- **NER** : reconnaissance d'entités nommées
- **Résumé** : extractif, abstractif
- **Traduction** : seq2seq
- **Question Answering** : extractif, génératif
- **RAG** : Retrieval-Augmented Generation

---

## 5. Reinforcement Learning (RL)

```
Agent ──action──→ Environnement
  ↑                   │
  └──reward, obs──────┘

Concepts clés :
- Policy π(a|s) : probabilité d'action a dans l'état s
- Value V(s) : récompense future attendue depuis l'état s
- Q-value Q(s,a) : récompense future attendue de (s,a)
```

### Algorithmes principaux
| Famille | Algorithmes |
|---------|------------|
| Value-based | DQN, Double DQN, Rainbow |
| Policy-based | REINFORCE, A2C, A3C |
| Actor-Critic | PPO, SAC, TD3, DDPG |
| Model-based | Dreamer, MuZero, World Models |

---

## 6. Optimisation et Entraînement

### Techniques essentielles
```python
# Learning Rate Scheduling
CosineAnnealingLR, OneCycleLR, ReduceLROnPlateau, Warmup

# Régularisation
Dropout, Weight Decay, Label Smoothing, MixUp, CutMix

# Normalisation
BatchNorm, LayerNorm, GroupNorm, RMSNorm

# Optimiseurs
Adam, AdamW, SGD+Momentum, Lion, Sophia

# Initialisation
Kaiming (ReLU), Xavier (tanh/sigmoid)

# Mixed Precision (AMP)
with torch.cuda.amp.autocast():
    outputs = model(inputs)

# Gradient Accumulation
loss = loss / accumulation_steps
loss.backward()
if (step + 1) % accumulation_steps == 0:
    optimizer.step()
```

---

## 7. Évaluation et Métriques

```python
# Classification
accuracy, precision, recall, f1_score, roc_auc, confusion_matrix

# Régression
mse, mae, rmse, r2_score, mape

# Clustering
silhouette_score, adjusted_rand_score, davies_bouldin_score

# Cross-validation
cross_val_score, StratifiedKFold, TimeSeriesSplit
```

---

## 8. MLOps

```
Expérimentation → Entraînement → Validation → Déploiement → Monitoring
    (W&B, MLflow)   (GPU cluster)   (Test set)    (Docker, K8s)   (Prometheus)
```

### Outils essentiels
- **MLflow** : suivi d'expériences, registre de modèles
- **Weights & Biases** : visualisation, collaboration
- **DVC** : versionnement de données
- **Kubeflow** : pipelines ML sur Kubernetes
- **ONNX** : interchangeabilité de modèles
- **TorchServe / TF Serving / Triton** : serving de modèles

---

## 9. Frameworks

| Framework | Usage | Forces |
|-----------|-------|--------|
| PyTorch | Deep learning général | Flexibilité, écosystème |
| TensorFlow/Keras | Production, mobile | TF Serving, TF Lite |
| JAX | Recherche, calcul | JIT, vmap, grad |
| HuggingFace | NLP, multimodal | 100k+ modèles pré-entraînés |
| scikit-learn | ML classique | Simple, robuste |
| XGBoost / LightGBM | Données tabulaires | Performance, Kaggle |
| LangChain / LlamaIndex | LLM applications | RAG, agents, tools |

---

## Références
- Deep Learning Book : https://www.deeplearningbook.org/
- HuggingFace : https://huggingface.co/
- Papers With Code : https://paperswithcode.com/