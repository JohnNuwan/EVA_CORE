---
name: julia-programming
description: "Programmer en Julia pour le calcul scientifique."
version: 1.0.0
author: Actemium
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [julia, scientific-computing, multiple-dispatch, type-stability, dataframes, pythoncall]
  related_skills: [data-analysis-exploration, simplify-code]
---

# Programmation et Calcul Scientifique en Julia (julia-programming)

## Vue d'ensemble

Le langage **Julia** est conçu pour combiner la vitesse des langages compilés (C/Fortran) avec la flexibilité et la simplicité d'utilisation des langages dynamiques (Python/R). Il est particulièrement adapté pour le calcul scientifique, la simulation physique, l'optimisation mathématique et la manipulation de données volumineuses.

Cette compétence guide l'agent Helios pour écrire du code Julia performant, structurer les projets à l'aide de packages isolés, éliminer les instabilités de types, et interfacer des composants Julia avec des infrastructures Python existantes.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Écrire, optimiser ou déboguer des algorithmes de calcul ou de simulation en Julia.
- Structurer un projet Julia avec des fichiers de dépendances (`Project.toml`, `Manifest.toml`).
- Manipuler des données tabulaires volumineuses à l'aide de `DataFrames.jl`.
- Appeler du code Julia depuis Python (ou inversement via `PyCall`/`PythonCall`).
- Résoudre des problèmes de temps d'exécution ou d'allocations de mémoire à l'aide des outils de diagnostic de type Julia.

---

## 1. Concepts Avancés : Dispatch Multiple et Stabilité des Types

Julia utilise le **dispatch multiple** (surcharge de fonctions basée sur le type de tous les arguments) et compile le code de manière juste-à-temps (JIT) avec LLVM. Pour obtenir des performances optimales, le compilateur doit pouvoir déduire le type exact de chaque variable lors de la compilation : c'est la **stabilité des types** (Type Stability).

### Exemple de dispatch multiple et vérification de stabilité de type :
```julia
# 1. Définition de structures concrètes immuables
struct Point2D
    x::Float64
    y::Float64
end

struct Point3D
    x::Float64
    y::Float64
    z::Float64
end

# 2. Dispatch multiple : surcharge de la fonction distance
distance(p::Point2D) = sqrt(p.x^2 + p.y^2)
distance(p::Point3D) = sqrt(p.x^2 + p.y^2 + p.z^2)

# 3. Fonction type-stable (le type de retour dépend uniquement du type des arguments)
function compute_total_distance(points::Vector{T}) where {T}
    total = 0.0 # Initialisation avec le type de retour correct (Float64)
    for p in points
        total += distance(p)
    end
    return total
end

# 4. Diagnostic de stabilité de type avec la macro @code_warntype
# (Vérifie si le compilateur détecte des types dynamiques de type "Any" ou des allocations)
using InteractiveUtils
pts = [Point2D(1.0, 2.0), Point2D(3.0, 4.0)]
@code_warntype compute_total_distance(pts)
```

---

## 2. Gestion de l'Environnement Projet (`Pkg`)

Sous Julia, la gestion des paquets est intégrée et pilotée par le module système `Pkg`.

```julia
using Pkg

# Activer l'environnement dans le dossier courant (cherche Project.toml)
Pkg.activate(".")

# Installer des packages spécifiques
Pkg.add("DataFrames")
Pkg.add("CSV")
Pkg.add("PythonCall")

# Résoudre et télécharger toutes les dépendances définies dans le Manifest.toml
Pkg.instantiate()
```

---

## 3. Manipulation de Données avec `DataFrames.jl`

L'analogue de Pandas sous Julia est la bibliothèque `DataFrames.jl` associée à `CSV.jl` :

```julia
using DataFrames
using CSV

# 1. Lecture efficace d'un fichier CSV
df = CSV.read("data/sensor_logs.csv", DataFrame)

# 2. Filtrage et sélection
# Syntaxe de macro typique : filtre les lignes et sélectionne les colonnes
filtered_df = filter(row -> row.cycle_time > 0, df)

# 3. Calculs et nouvelles colonnes avec la syntaxe source => fonction => destination
transform!(filtered_df, :actual_speed => (s -> 100.0 ./ s) => :normalized_speed)

# 4. Groupement et agrégation statistique
grouped = groupby(filtered_df, :machine_id)
summary = combine(grouped, 
    :cycle_time => mean => :mean_cycle,
    :cycle_time => std => :std_cycle
)
println(summary)
```

---

## 4. Interopérabilité bidirectionnelle avec Python (`PythonCall.jl`)

Nous privilégions `PythonCall.jl` pour interfacer Julia avec les bibliothèques Python sans partage de processus lourd :

### Appeler des modules Python depuis Julia :
```julia
using PythonCall

# Importer un module Python
np = pyimport("numpy")
pd = pyimport("pandas")

# Créer un tableau NumPy via Julia
py_arr = np.array([1, 2, 3])
# Convertir un objet Julia en objet Python
jl_arr = pyconvert(Vector{Int}, py_arr)
```

### Appeler du code Julia depuis Python (via Python) :
```python
# Côté script Python :
from juliacall import Main as jl

# Charger un script Julia
jl.include("my_julia_algorithm.jl")

# Appeler une fonction Julia directement
result = jl.my_julia_function([1.0, 2.0, 3.0])
```

---

## Pièges Courants (Common Pitfalls)

1. **Variables globales non typées (Performance Killer) :**
   * *Erreur :* Déclarer une variable globale mutable sans type, ex : `x = 10.0` et l'utiliser dans une boucle de calcul. Le compilateur JIT ne peut pas garantir que `x` ne changera pas de type et désactive toutes les optimisations de type, ralentissant le code d'un facteur 100.
   * *Correction :* Toujours typer ou rendre constante les globales, ex : `const x = 10.0`, ou passer la variable en argument de fonction.

2. **Indexation à base 1 (1-based indexing) :**
   * *Erreur :* Essayer d'accéder au premier élément d'un tableau Julia en écrivant `arr[0]`, provoquant une erreur `BoundsError`.
   * *Correction :* Julia commence ses indexations à `1` (comme Matlab ou R). Le premier élément est `arr[1]` et le dernier est `arr[end]`.

3. **Le coût de la première compilation ("Time to first plot") :**
   * *Erreur :* Mesurer le temps d'exécution d'une fonction complexe sur son tout premier appel. Le premier appel intègre le temps de compilation LLVM, ce qui fausse les analyses de performance.
   * *Correction :* Toujours effectuer un appel d'échauffement ("warm-up") avec des données factices avant de mesurer le temps d'exécution réel (ou utiliser le package `BenchmarkTools.jl` avec la macro `@btime`).

4. **Allocations mémoire inutiles par création de copies :**
   * *Erreur :* Passer des sous-tableaux en argument (ex: `func(arr[1:100])`), ce qui force Julia à créer une copie physique des données en mémoire.
   * *Correction :* Utiliser des vues (Views) pour référencer la mémoire existante sans copie (ex : `func(@view arr[1:100])` ou `@views func(arr[1:100])`).

---

## Liste de Vérification (Checklist)

- [ ] L'environnement projet est activé au lancement du script via `Pkg.activate(".")` pour isoler les dépendances.
- [ ] Les variables globales modifiables utilisées dans les fonctions critiques sont déclarées avec `const` ou passées explicitement en argument.
- [ ] L'indexation des tableaux commence à `1` et utilise `arr[end]` pour cibler le dernier élément.
- [ ] L'analyse avec `@code_warntype` confirme l'absence d'instabilités de types (mots colorés en rouge dans la sortie du terminal ou type de retour `Any`).
- [ ] Les découpes de grands tableaux (slicing) dans les boucles de calcul intensives utilisent la macro `@view` pour éviter les allocations mémoires superflues.
- [ ] Les packages externes nécessaires sont listés et verrouillés dans le fichier `Project.toml`.
