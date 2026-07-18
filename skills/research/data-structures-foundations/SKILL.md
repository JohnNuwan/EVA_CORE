---
name: data-structures-foundations
description: "Compétence en recherche sur les structures de données et fondements algorithmiques suivie sur arXiv sous cs.DS, cs.CC. Couvre les structures de données fondamentales, les algorithmes sur flux, les structures de données randomisées, les algorithmes de hachage, les dictionnaires, les files de priorité, les algorithmes online, et les algorithmes pour le big data."
category: research
arxiv_categories:
  - cs.DS
  - cs.CC
  - cs.DB
  - cs.IR
lang: fr
---

# Compétence : Structures de Données et Fondements Algorithmiques

## Présentation

Cette compétence couvre la veille de recherche sur les structures de données fondamentales et les fondements algorithmiques, avec un suivi régulier des publications sur arXiv dans les catégories cs.DS (Data Structures and Algorithms) et cs.CC (Computational Complexity). Elle englobe l'étude des structures classiques, des algorithmes probabilistes et randomisés, des techniques de streaming et sketch, ainsi que des algorithmes adaptés au big data.

## Domaines de Recherche

### Structures Fondamentales
- **Arbres** : arbres binaires de recherche, arbres équilibrés (AVL, rouge-noir, B-trees), arbres de segments, arbres de Fenwick, arbres binaires de décision
- **Tas (Heaps)** : tas binaires, tas de Fibonacci, tas binomiaux, tas à fusion paresseuse, tas de Brodal
- **Tables de Hachage** : sondage linéaire, hachage parfait, hachage dynamique, hachage extensible, hachage linéaire
- **B-Trees** : arbres B, B+, arbres B* avec variations et optimisations pour le stockage
- **Tries** : tries digitaux, tries compressés (Patricia tries), tries à tableaux, tries binaires, tries parfaitement équilibrés
- **Union-Find** : structures de partition avec compression de chemin et union par rang, algorithmes de Tarjan, analyse de la complexité inverse d'Ackermann

### Algorithmes sur Flux (Streaming)
- **Streaming Algorithms** : algorithmes en un passage, espace sous-linéaire, bornes inférieures de communication
- **Sketches** : sketches de Fourier, Count-Min Sketch, Count Sketch, sketches de moments d'ordre supérieur
- **Comptage Fréquent** : algorithmes de majority (Boyer-Moore), Lossy Counting, Sticky Sampling, Space-Saving
- **Heavy Hitters** : identification des éléments fréquents dans les flux, heavy hitters hiérarchiques, heavy hitters distribués
- **HyperLogLog** : estimation de cardinalité, HyperLogLog++, LogLog-Beta, HyperLogLog adaptatif, HyperLogLog avec biais réduits
- **Wavelet** : transformations en ondelettes pour flux de données, coefficients significatifs
- **Histogrammes** : histogrammes en streaming, échantillonnage adaptatif

### Algorithmes Online
- **Compétitivité** : ratio compétitif, analyse compétitive, algorithmes adversaires
- **Caching Online** : politiques de remplacement LRU, LFU, FIFO, Clock, ARC, 2Q, cache distribué, cache coopératif
- **Page Replacement** : algorithmes de remplacement de pages mémoire, OPT (clairvoyant), working set
- **Matching Online** : matching bipartite online, algorithme de Karp-Vazirani-Vazirani, ranking
- **Algorithmes de Ski-Rental, Online Knapsack, Online Set Cover** et autres problèmes classiques
- **Prédiction avec conseils (ML-Augmented Algorithms)** : algorithmes avec prédictions imparfaites, apprentissage pour l'optimisation online

### Hachage et Randomisation
- **Hachage Universel** : familles universelles, hachage k-universel, hachage fortement universel
- **Bloom Filter** : filtres de Bloom, filtres de Bloom compressés, filtres de Bloom à comptage, filtres de Bloom scalables
- **Cuckoo Hashing** : hachage coucou, variations à entrées multiples, hachage coucou spatial, hachage coucou avec cyclage
- **MinHash** : hachage par similarité de Jaccard, MinHash pondéré, MinHash b-bit, MinHash pour séquences
- **Locality-Sensitive Hashing (LSH)** : familles LSH pour distance cosinus, distance euclidienne, distance de Hamming
- **Filtres de Probabilité** : filtres quotient, filtres XOR, filtres de Bloom inversés, bloom filters génériques

### Structures pour Graphes
- **Représentations Compressées** : adjacency lists compressées, WebGraph, graph reordering, compression de graphes
- **Algorithmes de Graphes Fondamentaux** : BFS/DFS optimisés, chemins les plus courts (Dijkstra, Bellman-Ford, Floyd-Warshall, Johnson), arbres couvrants minimaux (Kruskal, Prim, Borůvka)
- **Flots et Coupes** : flot maximum (Ford-Fulkerson, Edmonds-Karp, Dinic, push-relabel), coupes minimales (Stoer-Wagner), flot à coût minimum
- **Graphes par Contraction** : Sparsification, coupes de Ramanujan
- **Graphes Dynamiques** : mise à jour de MST, connectivité dynamique, chemins les plus courts dynamiques, fermeture transitive dynamique
- **Sketch de Graphes** : spectral sparsification, embeddings de graphes, graph kernels

### Algorithmes pour Big Data
- **Algorithmes Distribués** : MapReduce, Spark, modèles MPC (Massively Parallel Computation), BSP (Bulk Synchronous Parallel)
- **Algorithmes Externes** : algorithmes avec mémoire externe, I/O-efficient algorithms, buffer trees, cache-oblivious algorithms
- **Échantillonnage** : réservoir sampling, échantillonnage à poids, échantillonnage adaptatif, échantillonnage de flux
- **Algorithmes Approximatifs** : algorithmes d'approximation temporelle et spatiale, FPTAS, PTAS
- **Algorithmes Parallèles** : algorithmes pour GPU, parallélisme mémoire partagée, parallélisme mémoire distribuée
- **Algorithmes Sublineaires** : algorithmes de test de propriétés, algorithmes avec accès aléatoire limité, algorithmes de streaming distribué

## Catégories arXiv Suivies

| Catégorie | Description |
|-----------|-------------|
| **cs.DS** | Data Structures and Algorithms |
| **cs.CC** | Computational Complexity |
| **cs.DB** | Databases (structures pour le stockage, indexation) |
| **cs.IR** | Information Retrieval (structures pour la recherche d'information) |

## Méthodologie de Veille

1. **Recherche hebdomadaire** sur arXiv dans les catégories listées ci-dessus
2. **Mots-clés prioritaires** : streaming algorithm, sketch, hash table, bloom filter, online algorithm, competitive ratio, data structure, cuckoo hashing, hyperloglog, heavy hitters, union-find, randomized algorithm
3. **Conférences cibles** : STOC, FOCS, SODA, ICALP, PODS, ESA, SPAA, WADS
4. **Revues cibles** : Journal of the ACM, SIAM Journal on Computing, ACM Transactions on Algorithms, Algorithmica, Information and Computation

## Ressources Associées

- [EATCS](https://eatcs.org/) — Bulletin de la communauté européenne d'informatique théorique
- [ArXiV cs.DS](https://arxiv.org/list/cs.DS/recent)
- [ArXiV cs.CC](https://arxiv.org/list/cs.CC/recent)