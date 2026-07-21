---
name: socmint-social-network-analysis
description: SOCMINT — analyse de graphes sociaux, cartographie d'influence, détection de communautés, analyse de réseaux d'abonnés et d'interactions.
category: cybersecurite
author: EVA
version: 1.0
tags: [socmint, social-graph, network-analysis, influence, community-detection, followers]
---

# SOCMINT : Analyse de Graphes Sociaux

## 🎯 Description

Analyse des relations et interactions entre comptes sur les réseaux sociaux : cartographie de l'écosystème social d'une cible, détection de communautés, identification d'influenceurs clés, analyse de la structure du réseau d'abonnés/abonnements, et traçage de la propagation de l'information.

Ce skill transforme les données relationnelles brutes (followers, followings, mentions, retweets, replies) en **intelligence exploitable** sur la structure sociale.

---

## 📊 Types de Graphes Sociaux

### 1. Graphe d'Amitié (Follow Graph)
```
           ┌─── B ─── D
           │
    A ─────┼─── C ─── E ─── G
           │
           └─── F ─── H ─── I
```
- **Nœuds** : comptes sociaux
- **Arêtes** : relation follower/following (dirigée)
- **Usage** : trouver les hubs, ponts, communautés isolées

### 2. Graphe d'Interaction
- **Nœuds** : comptes sociaux
- **Arêtes** : mentions, replies, retweets, likes (pondérées par fréquence)
- **Usage** : qui interagit vraiment avec qui (≠ simple abonnement)

### 3. Graphe de Propagation
- **Nœuds** : comptes + posts
- **Arêtes** : partage, citation, republication
- **Usage** : tracking de viralité, origine d'une campagne

---

## 🛠️ Outils d'Analyse de Graphe

### Desktop / Frameworks
| Outil | URL | Usage |
|-------|-----|-------|
| Gephi | https://gephi.org | Visualisation + analyse de graphes (force atlas) |
| Cytoscape | https://cytoscape.org | Analyse de réseaux biomédicaux/sociaux |
| NodeXL | https://www.smrfoundation.org/nodexl | Analyse réseaux sociaux (Excel) |
| Maltego | https://www.maltego.com | Transformations OSINT + graphes |

### Bibliothèques Python
| Library | Installation | Usage |
|---------|-------------|-------|
| NetworkX | `pip install networkx` | Analyse de graphe générique |
| igraph | `pip install igraph` | Analyse de graphe haute perf |
| PyVis | `pip install pyvis` | Visualisation interactive HTML |
| Netwulf | `pip install netwulf` | Visualisation style Gephi |
| Graph-tool | `conda install graph-tool` | Analyse C++ rapide |

### APIs Social Media (Collecte Graphe)
| Platform | Outil | Endpoint |
|----------|-------|----------|
| X/Twitter | Tweepy | `get_followers()`, `get_friends()` |
| Instagram | Instaloader | `get_followers()`, `get_followees()` |
| Reddit | PRAW | `get_subreddit()`, `get_subscriber()` |
| Telegram | Telethon | `get_participants()`, `get_dialogs()` |
| Discord | Discord.py | `fetch_members()`, `fetch_channel()` |
| GitHub | PyGithub | `get_followers()`, `get_stargazers()` |

---

## 🔬 Métriques d'Analyse

### Centralité (Qui est important ?)
| Métrique | Description | Formule (NetworkX) |
|----------|-------------|-------------------|
| Degree Centrality | Nombre de connexions directes | `nx.degree_centrality(G)` |
| Betweenness Centrality | Pont entre communautés | `nx.betweenness_centrality(G)` |
| Closeness Centrality | Proximité à tous les autres nœuds | `nx.closeness_centrality(G)` |
| Eigenvector Centrality | Connexion à des nœuds influents | `nx.eigenvector_centrality(G)` |
| PageRank | Algorithme Google adapté | `nx.pagerank(G)` |

### Détection de Communautés
| Algorithme | NetworkX | Usage |
|-----------|----------|-------|
| Louvain | `community_louvain.best_partition(G)` | Détection de clusters sociaux |
| Label Propagation | `nx.label_propagation_communities(G)` | Communautés rapides, large échelle |
| Girvan-Newman | `nx.algorithms.community.girvan_newman(G)` | Hiérarchique, précis |
| K-Clique | `nx.algorithms.community.k_clique_communities(G, k)` | Chevauchement de communautés |

### Structure du Réseau
| Métrique | Code | Interprétation |
|----------|------|----------------|
| Densité | `nx.density(G)` | 0.0-1.0, réseau serré ↔ lâche |
| Diamètre | `nx.diameter(G)` | Plus court chemin max |
| Coefficient de clustering | `nx.average_clustering(G)` | Tendance à former des triangles |
| Assortativité | `nx.degree_assortativity_coefficient(G)` | Hubs connectés à hubs ↔ hubs connectés à feuilles |
| Modularité | `community_louvain.modularity(partition, G)` | Qualité du partitionnement |

---

## 📋 Workflow d'Analyse

### Phase 1 : Collecte des Données
```python
import tweepy
import networkx as nx

# Exemple : collecte du graphe Twitter d'une cible
client = tweepy.Client(bearer_token="...")

# Récupérer les followers (limité par API)
followers = client.get_users_followers(id=target_id, max_results=100)
following = client.get_users_following(id=target_id, max_results=100)

# Construire le graphe
G = nx.DiGraph()
G.add_node("target")
for f in followers.data or []:
    G.add_edge(f.id, "target")  # follower → target
for f in following.data or []:
    G.add_edge("target", f.id)  # target → following
```

### Phase 2 : Analyse
```python
# Métriques de centralité
centrality = nx.betweenness_centrality(G)
top_bridges = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]

# Détection de communautés
import community as community_louvain
partition = community_louvain.best_partition(G.to_undirected())

# Identification des hubs
degrees = dict(G.degree())
top_hubs = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]

print("Top ponts (betweenness):", top_bridges)
print("Top hubs (degree):", top_hubs)
print("Communautés détectées:", len(set(partition.values())))
```

### Phase 3 : Visualisation
```python
import matplotlib.pyplot as plt
from pyvis.network import Network

# PyVis interactive HTML
net = Network(height="750px", width="100%", directed=True)
net.from_nx(G)
net.show("social_graph.html")
```

---

## 🔍 Cas d'Usage SOCMINT

### 1. Identifier les Comptes Relais (Bridge Accounts)
- Score de betweenness élevé = pont entre communautés
- Ces comptes sont critiques : les contrôler = contrôler le flux d'info
- Utiliser en investigation : qui connecte la cible à des cercles fermés ?

### 2. Détecter les Bot Networks
- Clustering coefficient anormalement bas (pas de vrais liens entre bots)
- Degré entrant/sortant déséquilibré (follow mass mais peu de followers)
- Topologie en étoile (un compte central, 1000 feuilles sans liens entre elles)

### 3. Cartographier l'Écosystème d'Influence
- Eigenvector centrality > PageRank = connecté aux vrais influenceurs
- Les nœuds avec forte closeness = propagateurs rapides
- Les ponts (betweenness) = gatekeepers d'information

### 4. Suivi de Propagation
```python
# BFS limité pour tracer la propagation
source = "compte_original"
max_depth = 3
bfs_edges = list(nx.bfs_edges(G, source, depth_limit=max_depth))
propagation_tree = nx.DiGraph(bfs_edges)
```

---

## 📊 Métriques pour Rapport SOCMINT

| Métrique | Valeur | Interprétation |
|----------|--------|----------------|
| Densité du réseau | 0.023 | Réseau très lâche (peu de connexions mutuelles) |
| Diamètre | 4 | 4 degrés de séparation max |
| Modularité | 0.72 | Forte structure communautaire |
| Clustering | 0.08 | Peu de triangles = liens instrumentaux |
| Assortativité | -0.31 | Hubs connectés à comptes de faible degré |
| Communautés | 7 | 7 clusters identifiés |
| Ponts (top-5) | @A, @B, @C, @D, @E | Gatekeepers d'information |

---

## ⚠️ Pitfalls

- **API Limits** : Twitter/X limite à 15 requêtes/15min pour followers, Instagram bloque le scraping
- **Graphe partiel** : sans le graphe complet, les métriques de centralité sont biaisées
- **Comptes privés** : invisibles dans le graphe d'interaction (mais visibles dans le follow graph)
- **Dormants** : les comptes inactifs depuis 1 an polluent les métriques
- **Bots** : faussent toutes les métriques si non filtrés
- **Directionnalité** : follower ≠ interaction réelle — toujours croiser avec le graphe d'interaction