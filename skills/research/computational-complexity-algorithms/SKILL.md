---
name: computational-complexity-algorithms
description: "Compétence en recherche en complexité computationnelle et algorithmes suivie sur arXiv sous cs.CC et cs.DS. Couvre les classes de complexité, les algorithmes d'approximation, les algorithmes randomisés, l'optimisation combinatoire, les algorithmes de graphes, la théorie de l'apprentissage algorithmique, et la complexité paramétrée."
category: research
---

# Compétence en Recherche — Complexité Computationnelle et Algorithmes (cs.CC & cs.DS)

## Présentation

Cette compétence assure une veille scientifique sur la **complexité computationnelle** (cs.CC) et les **structures de données et algorithmes** (cs.DS) via arXiv. Elle couvre les fondements théoriques de l'informatique : classes de complexité, algorithmes d'approximation, randomisation, optimisation combinatoire, algorithmes de graphes, ainsi que les connexions avec la théorie de l'apprentissage automatique.

---

## Classes de Complexité

- **Classes classiques** — P, NP, PSPACE, EXPTIME, NEXPTIME, les relations d'inclusion et les conjectures d'inégalité
- **NP-complétude et réductions** — Réductions polynomiales (Karp, Cook-Levin), problèmes NP-complets canoniques (SAT, 3SAT, Clique, Vertex Cover, Subset Sum, TSP)
- **Complexité des circuits** — AC⁰, TC⁰, NC, P/poly, lower bounds pour circuits, fonctions booléennes, barrières (natural proofs, relativization, algebrization)
- **Complexité de la communication** — Protocoles de communication, lower bounds, rang de matrices, jeux d'intersection, streaming
- **Complexité de la preuve** — Systèmes de preuve, Frege, Extended Frege, PHP, pigeonhole principle
- **Complexité quantique** — BQP, QMA, algorithmes quantiques, oracle separation

---

## Algorithmes d'Approximation

- **Schémas PTAS et FPTAS** — Approximation polynomiale, schémas d'approximation en temps polynomial, schémas totalement polynomiaux
- **Algorithmes randomisés** — Approximation randomisée, amplification, garanties probabilistes, derandomization (method of conditional expectations)
- **Garanties d'approximation** — Facteur d'approximation, ratio de performance, inapproximabilité (PCP theorem, Unique Games Conjecture)
- **Problèmes NP-difficiles approchés** — Max-Cut, Vertex Cover, Set Cover, Steiner Tree, k-Center, k-Median, Facility Location
- **Approximations pour problèmes de flots et coupes** — Min-cut, sparsest cut, balanced cut, flow-based methods

---

## Algorithmes de Graphes

- **Plus court chemin** — Dijkstra, Bellman-Ford, Floyd-Warshall, Johnson, A*, shortest path dans des graphes dynamiques
- **Flots et couplages** — Ford-Fulkerson, Edmonds-Karp, Dinic, Push-Relabel, Gomory-Hu trees, flots de coût min
- **Coloration de graphes** — Coloration de sommets, arêtes, graphes planaires, bornes chromatiques
- **Algorithmes de streaming et sublinéaires** — Streams de graphes, algorithmes sublinéaires en espace, sketchs, sparsification
- **Algorithmes pour grands graphes** — Algorithmes distribués (MapReduce, Pregel), algorithmes en mémoire externe, I/O efficient
- **Graphes dynamiques** — Mise à jour d'arbres couvrants, composantes connexes, plus courts chemins dynamiques

---

## Algorithmes Randomisés et Probabilistes

- **Méthodes probabilistes** — Lovász Local Lemma, concentration (Chernoff, Hoeffding, Azuma), martingales
- **Tests d'identité polynomiale** — Schwartz-Zippel, vérification d'égalité de polynômes
- **Algorithmes de Monte Carlo et Las Vegas** — Algorithmes randomisés avec et sans erreur, amplification
- **Marches aléatoires et chaînes de Markov** — Coupling, mixing time, PageRank, MCMC
- **Hachage et fingerprinting** — Hachage universel et parfait, Karp-Rabin, Bloom filters, MinHash

---

## Complexité Paramétrée

- **FPT (Fixed-Parameter Tractable)** — Problèmes FPT, kernelisation, bounded search tree, branching
- **W-hiérarchie** — W[1], W[2],..., réductions paramétrées, problèmes W[1]-complets (Clique paramétrée)
- **Kernelisation** — Noyaux polynomiaux, lossy kernelization, théorème de kernelisation bidirectionnelle
- **Algorithmes exponentials exacts** — Meet-in-the-middle, inclusion-exclusion, branch & bound, BBK
- **Applications** — Problèmes de graphes paramétrés (Vertex Cover, Feedback Vertex Set), problèmes de satisfiabilité paramétrés

---

## Algorithmes pour l'Apprentissage Automatique

- **Théorie de l'apprentissage PAC** — Probablely Approximately Correct, échantillonnage, VC-dimension, Rademacher complexity
- **Boosting et agrégation** — AdaBoost, Gradient Boosting, XGBoost, théorie du boosting, ensemble methods
- **List-Decodable codes et apprentissage** — Codes correcteurs d'erreurs, apprentissage avec bruit, list-decodable learning
- **Algorithmes pour les réseaux de neurones** — Convergence de SGD, initialization, landscape analysis, NTK (Neural Tangent Kernel)
- **Apprentissage non supervisé algorithmique** — k-means, k-median, clustering approximation, spectral clustering

---

## Catégories arXiv surveillées

| Catégorie | Description |
|-----------|-------------|
| **cs.CC** | Computational Complexity |
| **cs.DS** | Data Structures and Algorithms |
| **cs.LG** | Machine Learning |
| **math.CO** | Combinatorics |
| **stat.ML** | Machine Learning (Statistics) |
| **cs.GT** | Computer Science and Game Theory |

---

## Articles notables et tendances

- **Boosting with List-Decodable Codes (COLT 2026)** — Nouveaux résultats en boosting utilisant des codes correcteurs d'erreurs list-decodables, reliant théorie du codage et apprentissage
- **Lower Bounds for Private Information Retrieval (STOC 2026)** — Bornes inférieures pour PIR, progrès sur la complexité de la récupération d'information privée
- **Lower Bounds for Approximating Vietoris-Rips** — Bornes inférieures pour l'approximation de la filtration de Vietoris-Rips en topologie computationnelle
- **NewGraph algorithms for maximum matching** — Algorithmes récents pour le couplage maximum en temps quasi-linéaire
- **Complexity of neural network learning** — Résultats sur la complexité d'apprentissage des réseaux de neurones profonds

---

## Requêtes arXiv recommandées

```bash
# Complexité computationnelle
# cat:cs.CC

# Algorithmes et structures de données
# cat:cs.DS

# Algorithmes d'approximation
# cat:cs.DS AND (approximation OR PTAS OR FPTAS)

# Complexité paramétrée
# cat:cs.DS AND (parameterized OR FPT OR kernelization)

# Théorie de l'apprentissage
# cat:cs.LG AND (PAC OR boosting OR VC-dimension)
```
