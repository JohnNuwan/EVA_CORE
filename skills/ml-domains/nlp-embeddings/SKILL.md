---
name: nlp-embeddings
description: Use when working with word or token embeddings — Word2Vec, GloVe, FastText, contextual embeddings (ELMo, BERT), embedding visualization, projection, similarity search, et intégration dans des pipelines NLP.
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [nlp, embeddings, word2vec, glove, fasttext, elmo, contextual, representation-learning]
    related_skills: [nlp-tokenizers, nlp-transformers, nlp-bert, llm]
---

# Embeddings NLP — Représentations Vectorielles de Texte

## Vue d'ensemble

Les embeddings sont des représentations vectorielles denses de mots, tokens ou phrases qui capturent la sémantique et la syntaxe dans un espace latent continu. Ils sont le fondement de toute architecture NLP moderne, depuis les embeddings statiques (Word2Vec) jusqu'aux embeddings contextuels des Transformers.

Ce skill couvre l'ensemble du spectre : embeddings statiques (Word2Vec, GloVe, FastText), embeddings contextuels (ELMo, BERT embeddings), techniques de visualisation (t-SNE, UMAP), similarité sémantique, et intégration dans les pipelines modernes.

## Quand l'utiliser

- Vous devez convertir du texte en vecteurs pour un modèle ML classique ou un réseau.
- Vous analysez des relations sémantiques entre mots (analogie, similarité).
- Vous visualisez ou explorez la structure d'un espace de représentation.
- Vous comparez des approches d'embedding pour une tâche spécifique.
- Vous voulez comprendre la différence entre embeddings statiques et contextuels.

## Embeddings Statiques

### 1. Word2Vec

**Architectures :**

**Skip-gram :** Prédire les mots contextuels à partir du mot cible.
```
P(w_t+j | w_t)  →  softmax(encodeur(w_t) · decodeur(w_t+j))
```

**CBOW :** Prédire le mot cible à partir de la moyenne des mots contextuels.
```
P(w_t | w_t-2, w_t-1, w_t+1, w_t+2)
```

**Entraînement :**
```python
import gensim.downloader as api
from gensim.models import Word2Vec

# Sur un corpus personnalisé
sentences = [["phrase1", "tokenisée"], ["phrase2", "tokenisée"]]
model = Word2Vec(
    sentences,
    vector_size=300,
    window=5,
    min_count=5,
    workers=4,
    sg=1,          # 0=CBOW, 1=Skip-gram
    negative=15,   # échantillonnage négatif
    epochs=20,
)

# Similarité
model.wv.most_similar("réseau", topn=10)
model.wv.similarity("réseau", "neuronal")
model.wv.most_similar(positive=["roi", "femme"], negative=["homme"], topn=1)
# → "reine" (analogie classique)

# Chargement pré-entraîné
word_vectors = api.load("glove-wiki-gigaword-300")
```

**Optimisations :**
- **Negative Sampling** (Mikolov 2013) : échantillonne des mots négatifs au lieu de softmax complet
- **Hierarchical Softmax** : arbre de Huffman pour vocabulaire large
- **Subsampling** : ignore les mots très fréquents (dans les corpus massifs)

**Limites :** embedding unique par mot → pas de désambiguïsation sémantique ("banque" = institution financière ou berge de rivière).

### 2. GloVe (Global Vectors)

**Principe :** Apprentissage sur les statistiques de co-occurrence globale de la matrice mot-mot, combinant les avantages de la factorisation de matrice et du contexte local.

**Fonction objectif :**
```
J = Σ f(X_ij) · (w_i · w̃_j + b_i + b̃_j - log(X_ij))²
```
Où `X_ij` est le nombre de co-occurrences, `w_i` le vecteur mot, `w̃_j` le vecteur contexte, et `f` une fonction de pondération.

**Implémentation :**
```python
import numpy as np
from glove import Corpus, Glove

# Construction de la matrice de co-occurrence
corpus = Corpus()
corpus.fit(sentences, window=10)

# Entraînement GloVe
glove = Glove(no_components=300, learning_rate=0.05)
glove.fit(corpus.matrix, epochs=50, no_threads=4, verbose=True)
glove.add_dictionary(corpus.dictionary)

# Résultat
glove.most_similar("réseau", number=10)
```

**Avantages :** meilleure performance sur les tâches de similarité que Word2Vec pour des corpus de taille modérée. Convergence plus rapide.

**Modèles pré-entraînés disponibles :** `glove.6B.50d`, `glove.6B.100d`, `glove.6B.300d`, `glove.840B.300d`

### 3. FastText

**Principe :** Enrichit Word2Vec avec des **sous-mots (character n-grams)**. Chaque mot est représenté comme la somme de ses n-grammes de caractères.

**Avantage clé :** peut générer des embeddings pour des mots **inconnus (OOV)** en sommant leurs sous-mots.
Excellent pour les langues morphologiquement riches et les domaines techniques.

**Implémentation :**
```python
from gensim.models import FastText

model = FastText(
    sentences,
    vector_size=300,
    window=5,
    min_count=1,        # min_count=1 pour capturer les mots rares
    min_n=3,
    max_n=6,            # n-grammes de 3 à 6 caractères
    sg=1,
    epochs=50,
)

# Embedding d'un mot OOV
vec_inconnu = model.wv["néologismeinconnu"]  # fonctionne quand même !

# Similarité
model.wv.most_similar("transformateur")
```

**Langues bénéficiant le plus de FastText :** allemand, finnois, turc, coréen, arabe (morphologie riche), domaine médical (termes composés).

## Embeddings Contextuels

### ELMo (Embeddings from Language Models)

**Principe :** Embeddings contextuels profonds à partir d'un LSTM bidirectionnel pré-entraîné.

- 2 couches BiLSTM, embeddings de caractères → CNN pour les sous-mots
- Génère 3 vecteurs par token (couche 1 + couche 2 + couche d'entrée)
- Les poids de combinaison (γ, α₁, α₂, α₃) sont appris pour chaque tâche

```python
# Avec AllenNLP
from allennlp.modules.elmo import Elmo, batch_to_ids

options_file = "https://allennlp.s3.amazonaws.com/models/elmo/2x4096_512_2048cnn_2xhighway_5.5B_options.json"
weight_file = "https://allennlp.s3.amazonaws.com/models/elmo/2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5"

elmo = Elmo(options_file, weight_file, 2, dropout=0.5)

sentences = [["Les", "réseaux", "de", "neurones", "."]]
character_ids = batch_to_ids(sentences)
embeddings = elmo(character_ids)
# → embeddings['elmo_representations'][0].shape: [1, 5, 1024]
```

**État :** ELMo est aujourd'hui historiquement important mais largement remplacé par les embeddings Transformer.

### Embeddings BERT et Transformers

```python
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
model = AutoModel.from_pretrained("bert-base-multilingual-cased")

inputs = tokenizer("Le transformateur a révolutionné le NLP", return_tensors="pt")
outputs = model(**inputs)

# Embedding de la couche cachée finale
last_hidden = outputs.last_hidden_state  # [1, seq_len, 768]
cls_embedding = last_hidden[:, 0, :]     # token [CLS]

# Moyenne de tous les tokens
mean_embedding = last_hidden.mean(dim=1)  # [1, 768]

# Pooling des 4 dernières couches (recommandé pour BERT)
from transformers import AutoModelForMaskedLM
import torch

model = AutoModel.from_pretrained("bert-base-uncased",
                                   output_hidden_states=True)
outputs = model(**inputs)
hidden_states = outputs.hidden_states  # tuple des 12 couches + embedding layer

# Concaténer les 4 dernières couches
concat_emb = torch.cat(hidden_states[-4:], dim=-1)  # [1, seq_len, 3072]
# ou les moyenner
avg_emb = torch.mean(torch.stack(hidden_states[-4:]), dim=0)  # [1, seq_len, 768]
```

**Embeddings de phrases (Sentence Transformers) :**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer("intfloat/multilingual-e5-large")  # meilleur multilingue

embeddings = model.encode([
    "Les réseaux de neurones sont puissants.",
    "L'apprentissage profond transforme l'industrie.",
])
similarity = embeddings[0] @ embeddings[1].T / (
    torch.norm(embeddings[0]) * torch.norm(embeddings[1])
)
```

## Visualisation d'Embeddings

```python
import numpy as np
from sklearn.manifold import TSNE
import umap.umap_ as umap
import matplotlib.pyplot as plt

# t-SNE (perte locale)
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
emb_2d = tsne.fit_transform(embeddings_np)

# UMAP (scalable, préserve mieux la structure globale)
umap_model = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1)
emb_2d = umap_model.fit_transform(embeddings_np)

# PCA (rapide pour première inspection)
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
emb_2d = pca.fit_transform(embeddings_np)
```

## Recherche de Similarité

```python
import faiss

# Index plat pour similarité cosinus
d = 768  # dimension des embeddings
index = faiss.IndexFlatIP(d)  # Inner Product (cosinus après normalisation)
faiss.normalize_L2(embeddings_np)
index.add(embeddings_np)

# Recherche
faiss.normalize_L2(query_np)
D, I = index.search(query_np, k=10)
```

## Pièges Courants (Common Pitfalls)

1. **Embeddings statiques sans désambiguïsation.** Utiliser des embeddings contextuels pour des tâches où la polysémie est critique.
2. **Normalisation oubliée pour la similarité cosinus.** Toujours normaliser les vecteurs avant le produit scalaire.
3. **Trop grande dimension pour le nombre d'exemples.** Risque de surapprentissage. Réduire à 50-100 dimensions pour les petits datasets.
4. **GloVe/Word2Vec pré-entraînés en anglais seul.** Utiliser FastText multilingue ou des modèles multilingues pour le français.
5. **Combinaison incorrecte des couches BERT.** La meilleure pratique dépend de la tâche : dernière couche pour classification, 4 dernières pour similarité sémantique.
6. **Oubli du token_type_ids pour les paires de phrases** dans BERT.

## Liste de vérification (Checklist)

- [ ] Choix du type d'embedding adapté à la tâche (statique vs contextuel)
- [ ] Dimension de l'embedding adaptée au volume de données
- [ ] Normalisation des vecteurs pour similarité cosinus
- [ ] Modèle multilingue si le corpus n'est pas en anglais
- [ ] Visualisation de l'espace d'embedding avant entraînement
