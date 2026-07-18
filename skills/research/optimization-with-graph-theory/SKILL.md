---
name: optimization-with-graph-theory
title: Optimisation par la Théorie des Graphes
description: >-
  Exploiter la théorie des graphes pour optimiser des structures algorithmiques,
  des systèmes multi-agents complexes et des réseaux distribués.
version: 2.0.0
author: EVA Agent
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
dependencies:
  - networkx>=3.1
  - numpy>=1.24
  - scipy>=1.11
  - python-louvain>=0.16
metadata:
  EVA:
    tags:
      - graph-theory
      - optimization
      - network-flow
      - multi-agent
      - graph-partitioning
      - spectral-clustering
    category: research
    related_skills:
      - calculus-of-variations-ai
      - multi-agent-systems-research
      - ai-foundations-exploration
    requires_toolsets: [terminal, files, execute_code]
---

# Optimisation par la Théorie des Graphes

## Vue d'Ensemble

La **théorie des graphes** est un outil fondamental pour modéliser et résoudre des problèmes d'optimisation dans des systèmes complexes. Cette compétence couvre les concepts clés — partitionnement, flots, couplages, marches aléatoires — et leurs applications en **systèmes multi-agents**, **réseaux distribués**, **transport**, et **apprentissage automatique**.

Les problèmes d'optimisation sur graphes apparaissent dans de nombreux contextes :

- **Partitionnement de graphes** : diviser un réseau en communautés ou clusters équilibrés.
- **Flot maximal / coupe minimale** : optimiser le routage dans un réseau de transport.
- **Couplage optimal** : assigner des tâches à des agents de manière optimale.
- **Marches aléatoires et PageRank** : classer l'importance des nœuds dans un graphe.
- **Graphes de connaissances** : raisonner sur des entités et leurs relations.

---

## Quand l'utiliser

| Situation | Modélisation | Algorithme clé |
|-----------|-------------|----------------|
| Partitionner un réseau en communautés | Graphe de similarité | Louvain, Spectral Clustering |
| Optimiser le routage dans un réseau | Graphe orienté pondéré | Dijkstra, A*, Flot max |
| Assigner des tâches à des agents | Graphe biparti | Hungarian algorithm |
| Détecter des communautés dans un réseau social | Graphe non orienté | Girvan-Newman, Label Propagation |
| Compresser un graphe tout en préservant sa structure | Graphe avec degrés | Graphitour, fusion de nœuds |
| Planifier des chemins pour une flotte de véhicules | Graphe temporel | VRP, Christofides |

---

## 1. Partitionnement de Graphes

### 1.1 Partitionnement en Étoiles

Le partitionnement en **étoiles** consiste à diviser un graphe en sous-ensembles centrés autour d'un nœud pivot. Chaque étoile est définie par un sommet central connecté à ses voisins directs.

```python
import networkx as nx

def partition_en_etoiles(G: nx.Graph, max_voisins: int = 3):
    """Partitionne un graphe en sous-graphes en forme d'étoile.

    Args:
        G: Graphe NetworkX à partitionner.
        max_voisins: Nombre maximum de voisins par étoile.

    Returns:
        list: Liste des étoiles (chaque étoile est une liste de nœuds).
    """
    G = G.copy()
    etoiles = []

    # Trier les nœuds par degré décroissant (centres prioritaires)
    nœuds_triés = sorted(G.nodes(), key=lambda n: G.degree(n), reverse=True)

    for centre in nœuds_triés:
        if centre not in G:
            continue

        voisins = list(G.neighbors(centre))[:max_voisins]
        etoile = [centre] + voisins
        etoiles.append(etoile)

        # Retirer les nœuds de l'étoile du graphe restant
        G.remove_node(centre)
        for v in voisins:
            if v in G:
                G.remove_node(v)

    return etoiles


# Exemple : partition d'un graphe biparti complet
G = nx.complete_bipartite_graph(4, 5)
etoiles = partition_en_etoiles(G)
print(f"Nombre d'étoiles : {len(etoiles)}")
for i, etoile in enumerate(etoiles):
    print(f"  Étoile {i+1} : {etoile}")
```

### 1.2 Détection de Communautés (Louvain)

L'algorithme de **Louvain** optimise la modularité pour trouver des communautés dans un grand graphe :

```python
import networkx as nx
import community as community_louvain  # python-louvain
import matplotlib.pyplot as plt

def detecter_communautes(G: nx.Graph):
    """Détecte les communautés via l'algorithme de Louvain.

    Args:
        G: Graphe non orienté.

    Returns:
        dict: Mapping {nœud: id_communauté}
    """
    partition = community_louvain.best_partition(G)

    # Statistiques
    n_communautes = len(set(partition.values()))
    modularité = community_louvain.modularity(partition, G)

    print(f"Nombre de communautés détectées : {n_communautes}")
    print(f"Modularité : {modularité:.4f}")

    for com_id in set(partition.values()):
        membres = [n for n, c in partition.items() if c == com_id]
        print(f"  Communauté {com_id} : {len(membres)} membres")

    return partition
```

### 1.3 Compression de Graphes (Perte Nulle)

L'idée du *Graphitour* et des méthodes de compression sans perte : réduire la taille d'un graphe tout en conservant ses propriétés structurelles (connectivité, diamètre, centralité).

```python
def compresser_graphe(G: nx.Graph, seuil_degre: int = 2):
    """Compresse un graphe en fusionnant les nœuds de faible degré.

    Args:
        G: Graphe à compresser.
        seuil_degre: Degré maximum pour qu'un nœud soit fusionné.

    Returns:
        nx.Graph: Graphe compressé.
    """
    G_comp = G.copy()

    fusionne = True
    while fusionne:
        fusionne = False
        for nœud in list(G_comp.nodes()):
            if G_comp.degree(nœud) <= seuil_degre and G_comp.degree(nœud) > 0:
                voisins = list(G_comp.neighbors(nœud))
                if len(voisins) == 1:
                    # Fusionner avec l'unique voisin
                    G_comp = nx.contracted_nodes(G_comp, voisins[0], nœud,
                                                  self_loops=False)
                    fusionne = True
                    break  # Recommencer depuis le début

    return G_comp


# Démonstration
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (5, 6), (6, 3)])
print(f"Taille originale : {G.number_of_nodes()} nœuds")

G_comp = compresser_graphe(G)
print(f"Taille compressée : {G_comp.number_of_nodes()} nœuds")
```

---

## 2. Flots et Couplages

### 2.1 Flot Maximum et Coupe Minimale

Le problème du **flot maximum** consiste à trouver le débit maximal pouvant circuler d'une source $s$ vers un puits $t$ dans un graphe orienté avec capacités.

```python
import networkx as nx

def flot_maximum(G: nx.DiGraph, source: str, puits: str):
    """Calcule le flot maximum entre source et puits.

    Args:
        G: Graphe orienté avec attribut 'capacity' sur les arêtes.
        source: Nœud source.
        puits: Nœud puits.

    Returns:
        tuple: (valeur_du_flot, dictionnaire_de_flot)
    """
    valeur_flot, dict_flot = nx.maximum_flow(G, source, puits)

    print(f"Flot maximum de '{source}' à '{puits}' : {valeur_flot}")
    for (u, v), flot in dict_flot.items():
        if flot > 0:
            capacité = G[u][v]['capacity']
            print(f"  {u} → {v} : {flot}/{capacité}")

    return valeur_flot, dict_flot


# Exemple : réseau de distribution
G = nx.DiGraph()
G.add_edge('usine', 'entrepôt_A', capacity=20)
G.add_edge('usine', 'entrepôt_B', capacity=30)
G.add_edge('entrepôt_A', 'client_1', capacity=15)
G.add_edge('entrepôt_A', 'client_2', capacity=10)
G.add_edge('entrepôt_B', 'client_2', capacity=25)
G.add_edge('entrepôt_B', 'client_3', capacity=20)
G.add_edge('client_1', 'marché', capacity=15)
G.add_edge('client_2', 'marché', capacity=30)
G.add_edge('client_3', 'marché', capacity=20)

flot_maximum(G, 'usine', 'marché')
```

### 2.2 Couplage Maximum dans un Graphe Biparti

Le **couplage** (matching) trouve l'ensemble d'arêtes sans sommets communs de cardinalité maximale.

```python
def affectation_optimale(gains: list[list[float]]):
    """Résout un problème d'affectation avec l'algorithme hongrois.

    Args:
        gains: Matrice n×n des gains (agents × tâches).

    Returns:
        list: Affectation optimale (agent → tâche).
    """
    from scipy.optimize import linear_sum_assignment
    import numpy as np

    gains = np.array(gains)
    lignes, colonnes = linear_sum_assignment(-gains)  # - pour maximiser

    gain_total = gains[lignes, colonnes].sum()
    print(f"Gain total de l'affectation : {gain_total:.2f}")
    for agent, tâche in zip(lignes, colonnes):
        print(f"  Agent {agent} → Tâche {tâche} (gain : {gains[agent, tâche]:.2f})")

    return lignes, colonnes


# Exemple : 5 agents, 5 tâches
gains = [[9, 5, 7, 3, 2],
         [6, 8, 4, 5, 7],
         [3, 4, 9, 8, 5],
         [7, 6, 5, 9, 4],
         [2, 3, 6, 4, 8]]

affectation_optimale(gains)
```

---

## 3. Marches Aléatoires et PageRank

### 3.1 PageRank Personnalisé

Le **PageRank** mesure l'importance des nœuds dans un graphe dirigé. La version personnalisée permet de biaser l'importance vers certains nœuds.

```python
def pagerank_personnalise(G: nx.DiGraph, graines: list[str],
                          alpha: float = 0.85):
    """Calcule le PageRank personnalisé à partir de nœuds sources.

    Args:
        G: Graphe orienté.
        graines: Nœuds sources (seed nodes).
        alpha: Facteur d'amortissement.

    Returns:
        dict: Mapping {nœud: score}
    """
    perso = {n: 1.0 / len(graines) if n in graines else 0.0
             for n in G.nodes()}
    pr = nx.pagerank(G, alpha=alpha, personalization=perso)

    # Trier par score décroissant
    classement = sorted(pr.items(), key=lambda x: -x[1])
    print("Classement PageRank personnalisé :")
    for nœud, score in classement[:10]:
        print(f"  {nœud} : {score:.4f}")

    return pr
```

### 3.2 Centralité et Marches Aléatoires

```python
def analyser_centralites(G: nx.Graph):
    """Calcule et compare différentes mesures de centralité.

    Args:
        G: Graphe non orienté.
    """
    centralites = {
        'Degré': nx.degree_centrality(G),
        'Proximité': nx.closeness_centrality(G),
        'Intermédiarité': nx.betweenness_centrality(G),
        'Eigenvector': nx.eigenvector_centrality(G, max_iter=1000),
    }

    for nom, cent in centralites.items():
        top = sorted(cent.items(), key=lambda x: -x[1])[:3]
        print(f"Centralité de {nom} (top 3) :")
        for nœud, score in top:
            print(f"  {nœud} : {score:.4f}")
        print()
```

---

## 4. Applications Multi-Agents

### 4.1 Planification de Chemins pour une Flotte

```python
def planifier_tournees(points: list[tuple[float, float]],
                       n_vehicules: int = 1):
    """Planification naive de tournées (Clarke-Wright simplifié).

    Args:
        points: Liste des points (x, y) à visiter.
        n_vehicules: Nombre de véhicules disponibles.

    Returns:
        list: Tournées pour chaque véhicule.
    """
    import numpy as np

    def distance(p1, p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    n = len(points)
    depôt = points[0]
    non_visites = list(range(1, n))
    tournees = [[0] for _ in range(n_vehicules)]

    while non_visites:
        meilleur_gain = -float('inf')
        meilleur_vehicule = 0
        meilleur_point = None

        for v in range(n_vehicules):
            dernier = points[tournees[v][-1]]
            for p in non_visites:
                gain = distance(dernier, depôt) - distance(dernier, points[p])
                if gain > meilleur_gain:
                    meilleur_gain = gain
                    meilleur_vehicule = v
                    meilleur_point = p

        if meilleur_point is not None:
            tournees[meilleur_vehicule].append(meilleur_point)
            non_visites.remove(meilleur_point)
        else:
            break

    return tournees


# Exemple
points = [(0, 0), (1, 2), (3, 1), (4, 3), (2, 4), (5, 2)]
tournees = planifier_tournees(points, n_vehicules=2)
for i, tour in enumerate(tournees):
    print(f"Véhicule {i+1} : {tour}")
```

### 4.2 Consensus Distribué sur Graphe

```python
import numpy as np

def consensus_distribue(adjacence: np.ndarray, valeurs_init: np.ndarray,
                        iterations: int = 100):
    """Algorithme de consensus distribué sur un graphe.

    Chaque nœud met à jour sa valeur comme moyenne pondérée de ses voisins.

    Args:
        adjacence: Matrice d'adjacence (n×n).
        valeurs_init: Valeurs initiales des nœuds.
        iterations: Nombre d'itérations.

    Returns:
        np.ndarray: Évolution des valeurs (iterations × n).
    """
    n = len(valeurs_init)
    # Normaliser la matrice (matrice laplacienne normalisée)
    degres = np.sum(adjacence, axis=1)
    P = adjacence / degres[:, np.newaxis]
    np.fill_diagonal(P, 1 - np.sum(P, axis=1))

    valeurs = np.zeros((iterations, n))
    valeurs[0] = valeurs_init

    for t in range(1, iterations):
        valeurs[t] = P.T @ valeurs[t-1]

    print(f"Valeurs initiales : {valeurs_init}")
    print(f"Consensus atteint  : {valeurs[-1, 0]:.4f} " +
          f"(moyenne : {np.mean(valeurs_init):.4f})")

    return valeurs
```

---

## 5. Pièges Courants

| Piège | Symptôme | Solution |
|-------|----------|----------|
| **Graphe non connexe** | Partitionnement impossible ou absurde | Vérifier la connexité avec `nx.is_connected()` ; traiter chaque composante séparément |
| **Mauvaise modélisation des capacités** | Flot maximum irréaliste | Vérifier que les capacités sont cohérentes avec la physique du problème |
| **Oubli de l'orientation des arêtes** | Dijkstra échoue sur graphe non orienté | Utiliser `nx.DiGraph()` pour les flux dirigés, `nx.Graph()` pour les réseaux sociaux |
| **Complexité exponentielle** | Algorithme ne termine pas pour n>20 | Utiliser des heuristiques (recuit simulé, glouton) au lieu de l'exact |
| **Surapprentissage du partitionnement** | Communautés non pertinentes | Ajuster la résolution de Louvain ; valider avec des métriques de qualité (silhouette) |
| **PageRank non convergent** | Erreur de convergence | Vérifier que le graphe n'a pas de nœuds sans arêtes sortantes ; ajouter des téléports |
| **Métriques de centralité abusives** | Interprétation erronée des scores | Toujours comparer plusieurs mesures ; la centralité de degré n'est pas l'importance |
| **Matrice d'adjacence non symétrique** | Erreurs pour les graphes non orientés | Vérifier que `adj[i][j] == adj[j][i]` pour les graphes non orientés |

---

## 6. Checklist d'Implémentation

- [ ] Le problème est modélisé comme un graphe (nœuds, arêtes, poids).
- [ ] Le type de graphe est choisi (orienté / non orienté, pondéré / non pondéré).
- [ ] La bibliothèque NetworkX est installée (`pip install networkx`).
- [ ] Les algorithmes de base sont validés sur des graphes de test simples.
- [ ] Le partitionnement est évalué avec une métrique objective (modularité, silhouette).
- [ ] Les flots sont vérifiés avec la conservation du débit.
- [ ] Les couplages sont optimaux (vérification par enumeration pour petits cas).
- [ ] La complexité algorithmique est adaptée à la taille du graphe.
- [ ] Le code gère les graphes non connexes.
- [ ] Les visualisations sont produites (`nx.draw()`, `plt.savefig()`).
- [ ] Les résultats sont reproductibles (fixer `random.seed()` et `np.random.seed()`).
- [ ] La documentation précise la signification de chaque métrique.

---

## Références

1. Newman, M. E. J. (2010). *Networks: An Introduction*. Oxford University Press.
2. Bondy, J. A., & Murty, U. S. R. (2008). *Graph Theory*. Springer.
3. Barabási, A.-L. (2016). *Network Science*. Cambridge University Press.
4. Brandes, U., & Erlebach, T. (2005). *Network Analysis: Methodological Foundations*. Springer.
5. Lovász, L. (1993). *Combinatorial Problems and Exercises*. AMS Chelsea.

