---
name: computer-science
description: Guide complet d'Informatique Fondamentale — algorithmes, structures de données, complexité, systèmes d'exploitation, réseaux, bases de données, compilation, et théorie. En français.

---

# Computer Science — Guide Complet (Français)

Fondamentaux de l'informatique : algorithmique, structures de données, systèmes, réseaux, BD, compilation.

---

## 1. Complexité Algorithmique

### Notation de Landau

| Notation | Signification | Exemple |
|----------|--------------|---------|
| O(1) | Constant | Accès tableau |
| O(log n) | Logarithmique | Recherche binaire |
| O(n) | Linéaire | Parcours de liste |
| O(n log n) | Quasi-linéaire | Tri fusion |
| O(n²) | Quadratique | Tri bulle |
| O(2ⁿ) | Exponentiel | Force brute |
| O(n!) | Factoriel | Voyageur de commerce |

### Maîtriser les complexités

```python
# O(1) : accès direct
element = liste[5]

# O(log n) : recherche binaire
def recherche_binaire(liste, cible):
    gauche, droite = 0, len(liste) - 1
    while gauche <= droite:
        milieu = (gauche + droite) // 2
        if liste[milieu] == cible:
            return milieu
        elif liste[milieu] < cible:
            gauche = milieu + 1
        else:
            droite = milieu - 1
    return -1

# O(n) : parcours linéaire
maximum = max(liste)

# O(n log n) : tri fusion
def tri_fusion(liste):
    if len(liste) <= 1:
        return liste
    milieu = len(liste) // 2
    gauche = tri_fusion(liste[:milieu])
    droite = tri_fusion(liste[milieu:])
    return fusionner(gauche, droite)

# O(n²) : double boucle
for i in range(n):
    for j in range(n):
        ...

# Amorti : opérations coûteuses rares
# Exemple : agrandissement dynamique de liste (O(1) amorti)
```

---

## 2. Structures de Données

### Tableaux / Listes
- **Accès** : O(1), **Recherche** : O(n), **Insertion/Suppression** : O(n)
- Mémoire contiguë, cache-friendly

### Listes Chaînées
- **Accès** : O(n), **Insertion/Suppression** : O(1) (si on a le nœud)
- Pas de mémoire contiguë, pas de redimensionnement

### Piles (LIFO) / Files (FIFO)
```python
from collections import deque

pile = []
pile.append(1); pile.pop()

file = deque()
file.append(1); file.popleft()

file_priorite = []
heapq.heappush(file_priorite, (priorite, element))
```

### Tables de Hachage
- **Insertion, Recherche, Suppression** : O(1) amorti
- Collisions : chaînage ou adressage ouvert

```python
# Python dict/set = table de hachage
d = {"cle": "valeur"}
"cle" in d  # O(1)
```

### Arbres
- **Arbre Binaire de Recherche (BST)** : O(log n) équilibré → O(n) dégénéré
- **AVL / Rouge-Noir** : auto-équilibrés, O(log n) garanti
- **Trie (Arbre préfixe)** : O(k) pour chaîne de longueur k
- **Segment Tree / Fenwick Tree** : requêtes de plage O(log n)

### Graphes
- **Représentation** : matrice d'adjacence (O(V²)) ou liste d'adjacence (O(V+E))
- **Parcours** : BFS (file, plus court chemin non pondéré), DFS (pile, détection cycles)

```python
# BFS
def bfs(graphe, depart):
    visite = set()
    file = deque([depart])
    while file:
        noeud = file.popleft()
        if noeud not in visite:
            visite.add(noeud)
            file.extend(graphe[noeud])
    return visite

# DFS (récursif)
def dfs(graphe, noeud, visite=None):
    if visite is None:
        visite = set()
    visite.add(noeud)
    for voisin in graphe[noeud]:
        if voisin not in visite:
            dfs(graphe, voisin, visite)
    return visite
```

---

## 3. Algorithmes Classiques

### Tri
| Algorithme | Moyenne | Pire | Stable | In-place |
|-----------|---------|------|--------|----------|
| Quicksort | O(n log n) | O(n²) | Non | Oui |
| Mergesort | O(n log n) | O(n log n) | Oui | Non |
| Heapsort | O(n log n) | O(n log n) | Non | Oui |
| Timsort | O(n log n) | O(n log n) | Oui | Non |

### Recherche
- **Binaire** : O(log n), liste triée
- **A*** : heuristique, graphe pondéré
- **Dijkstra** : plus court chemin, poids positifs
- **Bellman-Ford** : accepte poids négatifs

### Graphes
- **MST** : Kruskal (O(E log E)), Prim (O(E log V))
- **Floyd-Warshall** : tous les plus courts chemins O(V³)
- **Topological Sort** : DAG uniquement
- **Union-Find** : composantes connexes, O(α(n)) quasi-constant

### Programmation Dynamique
```python
# Fibonacci DP (bottom-up)
def fibonacci(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# Knapsack 0/1
def knapsack(valeurs, poids, capacite):
    n = len(valeurs)
    dp = [[0] * (capacite + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacite + 1):
            if poids[i-1] <= w:
                dp[i][w] = max(
                    dp[i-1][w],
                    dp[i-1][w - poids[i-1]] + valeurs[i-1]
                )
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][capacite]
```

---

## 4. Systèmes d'Exploitation

### Processus vs Threads
| | Processus | Thread |
|---|---|---|
| Mémoire | Isolée | Partagée |
| Création | Lente | Rapide |
| Communication | IPC (pipes, sockets) | Mémoire partagée |
| Crash | Isolé | Tout le processus |

### Mémoire
- **Pile (Stack)** : variables locales, LIFO, rapide, limitée
- **Tas (Heap)** : allocation dynamique, malloc/free ou GC
- **Mémoire virtuelle** : pagination, segmentation, MMU
- **Cache** : L1 (32-64 KB), L2 (256-512 KB), L3 (8-32 MB)

### Concurrence
```python
# Race condition (sans verrou)
x = 0
# Thread 1: x += 1  → lit x, ajoute 1, écrit x
# Thread 2: x += 1  → lit x, ajoute 1, écrit x
# Résultat possible : x = 1 au lieu de 2 !

# Mutex / Lock : exclusion mutuelle
lock.acquire()
x += 1
lock.release()

# Sémaphore : limite N threads
semaphore = Semaphore(3)  # Max 3 accès simultanés

# Deadlock : A attend B, B attend A → blocage circulaire
# Conditions : exclusion mutuelle, hold-and-wait, pas de préemption, attente circulaire
```

---

## 5. Réseaux

### Modèle OSI
```
7. Application    (HTTP, FTP, SMTP, DNS)
6. Présentation   (SSL/TLS, encodage)
5. Session        (sockets, RPC)
4. Transport      (TCP, UDP)
3. Réseau         (IP, ICMP, routage)
2. Liaison        (Ethernet, WiFi, MAC)
1. Physique       (câble, ondes, bits)
```

### TCP vs UDP
| | TCP | UDP |
|---|---|---|
| Connexion | Oui (3-way handshake) | Non (fire-and-forget) |
| Fiabilité | Garantie | Non garantie |
| Ordre | Préservé | Non préservé |
| Vitesse | Plus lent | Plus rapide |
| Usage | Web, email, fichiers | Streaming, gaming, DNS |

### Adressage
- **IPv4** : 32 bits, 4 octets, 192.168.1.1
- **IPv6** : 128 bits, 2001:0db8::1
- **CIDR** : 192.168.1.0/24
- **NAT** : traduction d'adresses réseau
- **DNS** : résolution nom → IP (port 53)

---

## 6. Bases de Données

### SQL (Relationnel)
```sql
-- CRUD
SELECT colonne1, colonne2
FROM table
WHERE condition
ORDER BY colonne DESC
LIMIT 10;

INSERT INTO table (col1, col2) VALUES (val1, val2);
UPDATE table SET col1 = val1 WHERE condition;
DELETE FROM table WHERE condition;

-- Jointures
SELECT * FROM a
INNER JOIN b ON a.id = b.id_a;       -- Intersection
LEFT JOIN b ON a.id = b.id_a;        -- Tout de a
FULL OUTER JOIN b ON a.id = b.id_a;  -- Tout des deux

-- Agrégation
SELECT categorie, COUNT(*), AVG(valeur)
FROM table
GROUP BY categorie
HAVING COUNT(*) > 5;

-- Index
CREATE INDEX idx_nom ON table (colonne);
CREATE UNIQUE INDEX idx_unique ON table (colonne);
```

### NoSQL
| Type | Exemples | Usage |
|------|----------|-------|
| Document | MongoDB, CouchDB | JSON flexible |
| Clé-valeur | Redis, DynamoDB | Cache, sessions |
| Colonne large | Cassandra, HBase | Time-series, logs |
| Graphe | Neo4j, ArangoDB | Réseaux sociaux |

### ACID vs BASE
- **ACID** : Atomicité, Cohérence, Isolation, Durabilité (SQL)
- **BASE** : Basically Available, Soft state, Eventually consistent (NoSQL)

### Niveaux d'isolation
- Read Uncommitted → Read Committed → Repeatable Read → Serializable
- Phénomènes : Dirty Read, Non-Repeatable Read, Phantom Read

---

## 7. Compilation et Langages

### Phases de compilation
```
Code source → Analyse lexicale → Analyse syntaxique
→ Analyse sémantique → Code intermédiaire
→ Optimisation → Génération de code → Exécutable
```

### Paradigmes de programmation
- **Impératif** : séquence d'instructions (C, Python)
- **Fonctionnel** : fonctions pures, immutabilité (Haskell, OCaml)
- **Orienté Objet** : objets, classes, héritage (Java, C++)
- **Logique** : règles et faits (Prolog)
- **Déclaratif** : décrire le quoi, pas le comment (SQL)

### Typage
- **Statique vs Dynamique** : vérification à la compilation vs à l'exécution
- **Fort vs Faible** : conversions implicites autorisées ou non
- **Inférence de type** : déduction automatique (Rust, Haskell, TypeScript)

---

## 8. Théorie de l'Informatique

### Machines de Turing
- Modèle théorique de calcul universel
- Ruban infini + tête de lecture/écriture + états
- Problème de l'arrêt (Halting Problem) : indécidable

### Classes de Complexité
- **P** : résoluble en temps polynomial
- **NP** : vérifiable en temps polynomial
- **NP-Complet** : les plus durs de NP (SAT, TSP)
- **NP-Difficile** : au moins aussi dur que NP-Complet
- **P = NP ?** : problème ouvert (1M$)

### Calculabilité
- **Décidable** : existe un algorithme qui termine toujours
- **Semi-décidable** : termine si vrai, boucle si faux
- **Indécidable** : aucun algorithme ne peut résoudre

---

## 9. Cryptographie

### Symétrique
- Même clé pour chiffrer/déchiffrer
- AES (128, 192, 256 bits), ChaCha20
- Rapide, mais problème d'échange de clé

### Asymétrique
- Clé publique + clé privée
- RSA, ECC (Elliptic Curve)
- Lent, mais résout l'échange de clé

### Hachage
- SHA-256, SHA-3, BLAKE3
- Fonction à sens unique, résistance aux collisions

### Applications
- **TLS/SSL** : HTTPS, certificats X.509
- **Signature numérique** : authenticité + intégrité
- **HMAC** : intégrité + authentification

---

## Références
- CLRS (Introduction to Algorithms)
- SICP (Structure and Interpretation of Computer Programs)
- Operating Systems: Three Easy Pieces
- Computer Networking: A Top-Down Approach