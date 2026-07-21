---
name: python-performances
description: Optimisation de performances Python — profiling, caching, vectorisation, compilation (Cython/Numba), multiprocessing, et bonnes pratiques. En français.
---

# Performances Python — Guide Complet (Français)

Ce skill couvre les techniques d'optimisation et de profiling en Python. À charger pour toute tâche de performance.

---

## 1. Profiling : Trouver les Goulots

### cProfile (profilage déterministe)

```bash
# Profiler un script
python -m cProfile -s cumulative mon_script.py

# Sortie triée par temps cumulé
python -m cProfile -s tottime mon_script.py
```

```python
import cProfile
import pstats
from pstats import SortKey

def fonction_a_profiler():
    ...

# Profilage programmatique
profiler = cProfile.Profile()
profiler.enable()
fonction_a_profiler()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats(SortKey.CUMULATIVE)
stats.print_stats(20)  # Top 20
```

### timeit (micro-benchmarks)

```python
import timeit

# Comparer deux approches
temps_liste = timeit.timeit(
    "[x**2 for x in range(1000)]",
    number=10000,
)
temps_map = timeit.timeit(
    "list(map(lambda x: x**2, range(1000)))",
    number=10000,
)

print(f"Compréhension : {temps_liste:.4f}s")
print(f"map()         : {temps_map:.4f}s")
```

```bash
# En ligne de commande
python -m timeit -s "xs = list(range(1000))" "[x**2 for x in xs]"
```

### Scalene (profiling CPU + mémoire)

```bash
pip install scalene
scalene --html --outfile profil.html mon_script.py
```

### py-spy (profiling de processus en cours)

```bash
pip install py-spy
py-spy top --pid 12345           # Top en direct
py-spy record -o profil.svg --pid 12345  # Flamegraph
```

---

## 2. Structures de Données Performantes

```python
# ✅ collections.deque : O(1) aux deux bouts
from collections import deque
file = deque()
file.append(1)        # O(1)
file.appendleft(0)    # O(1)
file.pop()            # O(1) vs list.pop(0) qui est O(n)

# ✅ array.array : tableaux typés (plus compacts)
from array import array
entiers = array("i", [1, 2, 3])  # int 4 octets

# ✅ heapq : file de priorité
import heapq
tas = [3, 1, 4, 1, 5]
heapq.heapify(tas)     # O(n)
heapq.heappush(tas, 0)  # O(log n)

# ❌ Compréhensions plutôt que boucles avec append
# LENT
resultat = []
for x in range(1000):
    resultat.append(x ** 2)

# RAPIDE (~2x)
resultat = [x ** 2 for x in range(1000)]
```

---

## 3. Optimisation de Chaînes

```python
# ❌ Concaténation dans une boucle (O(n²))
resultat = ""
for mot in mots:
    resultat += mot + " "

# ✅ join() (O(n))
resultat = " ".join(mots)

# ✅ Formatage avec f-strings (le plus rapide)
nom, age = "Alice", 30
message = f"{nom} a {age} ans"

# ✅ str.startswith / endswith
if nom_de_fichier.endswith((".py", ".pyw")):  # Tuple accepté !
    ...

# ✅ Traduction de caractères (str.translate)
table = str.maketrans("éèêë", "eeee")
resultat = texte.translate(table)
```

---

## 4. NumPy : Vectorisation

```python
import numpy as np

# ❌ Boucle Python lente
donnees = list(range(1_000_000))
carres = [x ** 2 for x in donnees]  # ~200ms

# ✅ Vectorisation NumPy
arr = np.arange(1_000_000)
carres = arr ** 2  # ~5ms — 40x plus rapide !
```

### Conversion des boucles en opérations vectorisées

```python
# ❌ Boucle
resultat = []
for i in range(len(a)):
    if a[i] > 0:
        resultat.append(a[i] * 2)

# ✅ Masque booléen
mask = a > 0
resultat = a[mask] * 2

# ✅ np.where
resultat = np.where(a > 0, a * 2, a)

# ✅ np.select (conditions multiples)
conditions = [a < 0, (a >= 0) & (a < 10), a >= 10]
choix = [0, a * 2, a ** 2]
resultat = np.select(conditions, choix)
```

---

## 5. Mise en Cache

### lru_cache (fonctions pures)

```python
from functools import lru_cache, cache

# Cache avec limite de taille
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Calcule le n-ième terme de Fibonacci avec cache.
    
    Args:
        n: Position dans la suite.
    
    Returns:
        Le terme correspondant.
    """
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Cache illimité (Python 3.9+)
@cache
def factorielle(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorielle(n - 1)

# Voir les stats du cache
print(fibonacci.cache_info())
# CacheInfo(hits=28, misses=11, maxsize=128, currsize=11)
fibonacci.cache_clear()
```

### Dict de cache manuel

```python
from typing import Any

_cache: dict[tuple, Any] = {}

def calcul_couteux(x: int, y: int) -> float:
    cle = (x, y)
    if cle not in _cache:
        _cache[cle] = x ** y + y ** x  # Calcul coûteux
    return _cache[cle]
```

---

## 6. Itérations Efficaces

```python
# ✅ itérateurs plutôt que listes intermédiaires
# Éviter :
somme = sum([x**2 for x in range(1_000_000)])  # Crée une liste de 1M

# Préférer :
somme = sum(x**2 for x in range(1_000_000))    # Générateur, pas de liste

# ✅ any/all avec court-circuit
if any(x < 0 for x in grande_liste):  # S'arrête au premier True
    ...

# ✅ enumerate plutôt que range(len())
for i, valeur in enumerate(sequence):
    ...

# ✅ zip plutôt que indexation parallèle
for a, b in zip(liste_a, liste_b):
    ...

# ✅ items() plutôt que keys() + lookup
for cle, valeur in dico.items():
    ...
```

---

## 7. Cython et Numba

### Numba (compilation JIT)

```python
from numba import jit, njit, prange
import numpy as np

@njit
def somme_numba(arr: np.ndarray) -> float:
    """Somme d'un tableau compilée avec Numba.
    
    Args:
        arr: Tableau NumPy 1D.
    
    Returns:
        Somme des éléments.
    """
    total = 0.0
    for x in arr:  # Boucle pure, mais compilée → rapide !
        total += x
    return total

# Avec parallélisation
@njit(parallel=True)
def somme_parallele(arr: np.ndarray) -> float:
    total = 0.0
    for i in prange(len(arr)):
        total += arr[i]
    return total
```

### Cython (.pyx)

```cython
# mon_module.pyx
# Compilation : cythonize -i mon_module.pyx

def fibonacci_cython(int n):
    """Version Cython de Fibonacci."""
    cdef int a = 0, b = 1, i
    for i in range(n):
        a, b = b, a + b
    return a
```

```python
# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("mon_module.pyx"))
```

---

## 8. Multiprocessing

```python
from multiprocessing import Pool, cpu_count
from concurrent.futures import ProcessPoolExecutor


def calcul_intensif(param: int) -> float:
    """Fonction intensive CPU à paralléliser."""
    return sum(i ** 2 for i in range(param))


# Avec ProcessPoolExecutor (recommandé)
def traiter_en_parallele(
    parametres: list[int],
    max_workers: int | None = None,
) -> list[float]:
    """Traite une liste de paramètres en parallèle.
    
    Args:
        parametres: Liste des paramètres d'entrée.
        max_workers: Nombre de processus (par défaut : CPU count).
    
    Returns:
        Résultats dans l'ordre.
    """
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        resultats = list(executor.map(calcul_intensif, parametres))
    return resultats
```

---

## 8. Lazy Evaluation

```python
# ✅ Générateurs : produire à la demande
def lire_grand_fichier(chemin: str) -> Generator[str, None, None]:
    """Lit un fichier ligne par ligne sans tout charger.
    
    Args:
        chemin: Chemin du fichier.
    
    Yields:
        Chaque ligne (sans le saut de ligne).
    """
    with open(chemin) as f:
        for ligne in f:
            yield ligne.rstrip("\n")


# ✅ itertools : pipelines paresseux
from itertools import islice, chain, groupby

# Prendre N éléments sans créer de liste
premiers_10 = list(islice(generateur_infini(), 10))

# Chaîner sans copier
tous = chain(liste_a, liste_b, generateur_c())  # Passeur, pas copie
```

---

## 9. Entrées/Sorties Optimisées

```python
import json
import pickle
from pathlib import Path

# ✅ Lire tout le fichier d'un coup (si taille raisonnable)
contenu = Path("fichier.json").read_text()
donnees = json.loads(contenu)

# ✅ json.load() directement depuis le fichier
with open("fichier.json") as f:
    donnees = json.load(f)

# ✅ pickle (binaire, plus rapide que JSON)
with open("cache.pkl", "wb") as f:
    pickle.dump(donnees, f, protocol=pickle.HIGHEST_PROTOCOL)

# ✅ mmap pour les très gros fichiers
import mmap
with open("enorme_fichier.bin", "r+b") as f:
    with mmap.mmap(f.fileno(), 0) as mm:
        # Accès direct à la mémoire mappée
        print(mm[1000:1100])
```

---

## 10. Règles d'Or de l'Optimisation

1. **Profiler avant d'optimiser** — ne devinez pas, mesurez
2. **La complexité algorithmique prime** — O(n) > micro-optimisations
3. **Vectoriser avec NumPy** quand on manipule des tableaux
4. **Cache pour les fonctions pures** — `@lru_cache`
5. **Générateurs > listes** pour les grandes séquences
6. **join() > +=** pour les chaînes
7. **locals > globals** — accès plus rapide
8. **`.copy()` > copie manuelle** — implémenté en C
9. **sets/dicts > listes** pour les tests d'appartenance (O(1) vs O(n))
10. **Multiprocessing** pour le CPU-bound, **asyncio** pour l'I/O-bound

---

## Références
- Python Performance Tips : https://wiki.python.org/moin/PythonSpeed/PerformanceTips
- NumPy : https://numpy.org/doc/stable/
- Numba : https://numba.pydata.org/
- Cython : https://cython.readthedocs.io/