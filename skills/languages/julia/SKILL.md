---
name: julia
description: Guide complet du langage Julia — syntaxe, types, multiple dispatch, performances, macros, packages, data science et calcul scientifique. En français.
---

# Julia — Guide Complet (Français)

Langage de calcul scientifique haute performance. Julia 1.10+.

---

## 1. Installation et Démarrage

```bash
# Installation via juliaup (recommandé)
curl -fsSL https://install.julialang.org | sh

# Lancer le REPL
julia

# Mode package
# Dans le REPL : taper ]
```

---

## 2. Syntaxe de Base

```julia
# Variables et types
x = 42                # Int64
y = 3.14              # Float64
z = 2 + 3im           # Complex{Int64}
nom = "Julia"         # String
actif = true          # Bool

# Type annotations
x::Int64 = 42
function ma_fonction(a::Float64)::Float64
    return a * 2
end

# Chaînes
"Bonjour $nom"        # Interpolation
"""Chaîne multiligne""" # Triple quotes
raw"pas\nd'interpolation" # Chaîne brute

# Tuples et paires
t = (1, 2, 3)
paire = :cle => "valeur"
```

---

## 3. Structures de Contrôle

```julia
# Conditions
if x > 0
    println("positif")
elseif x < 0
    println("négatif")
else
    println("zéro")
end

# Opérateur ternaire
resultat = x > 0 ? "ok" : "non"

# Boucles
for i in 1:10
    println(i)
end

for (index, valeur) in enumerate(["a", "b", "c"])
    println("$index → $valeur")
end

while condition
    # ...
end

# Compréhensions
carres = [x^2 for x in 1:10]
carres_2 = [x^2 for x in 1:10 if x % 2 == 0]
dico = Dict(i => i^2 for i in 1:5)
```

---

## 4. Fonctions et Multiple Dispatch

```julia
# Fonction simple
function additionner(a::Int, b::Int)::Int
    return a + b
end

# Syntaxe compacte
additionner(a, b) = a + b

# Multiple dispatch — LA force de Julia
function traiter(x::Int)
    return "entier : $x"
end

function traiter(x::Float64)
    return "flottant : $x"
end

function traiter(x::String)
    return "chaîne : $x"
end

# Dispatch sur plusieurs arguments
function combiner(a::Int, b::Int)
    return a + b
end

function combiner(a::String, b::String)
    return a * b
end

# Arguments nommés et par défaut
function configurer(; host::String="localhost", port::Int=8080)
    return "http://$host:$port"
end

# Fonctions anonymes
doubler = x -> x * 2
somme = (a, b) -> a + b

# Opérateur pipe
resultat = 1:10 |> collect |> 
    x -> filter(isodd, x) |> 
    x -> sum(x)
```

---

## 5. Types et Structures

```julia
# Types concrets
struct Point
    x::Float64
    y::Float64
end

p = Point(1.0, 2.0)
p.x  # 1.0

# Types mutables
mutable struct Compteur
    valeur::Int
end

c = Compteur(0)
c.valeur += 1

# Types paramétriques
struct Vecteur{T}
    x::T
    y::T
end

v1 = Vecteur{Int}(1, 2)
v2 = Vecteur{Float64}(1.5, 2.5)

# Types abstraits
abstract type Animal end

struct Chien <: Animal
    nom::String
end

struct Chat <: Animal
    nom::String
end

function cri(a::Chien)
    return "Woof!"
end

function cri(a::Chat)
    return "Miaou!"
end

# Constructeurs personnalisés
struct Fraction
    num::Int
    den::Int
    
    function Fraction(num::Int, den::Int)
        if den == 0
            throw(DomainError(den, "dénominateur nul"))
        end
        g = gcd(num, den)
        new(div(num, g), div(den, g))
    end
end
```

---

## 6. Collections

```julia
# Arrays (tableaux multidimensionnels)
v = [1, 2, 3]                    # Vector{Int}
m = [1 2 3; 4 5 6]              # Matrix{Int} 2×3
z = zeros(3, 3)                  # Matrice de zéros
ones(5)                          # Vecteur de uns
I(3)                            # Matrice identité
rand(3, 3)                      # Aléatoire uniforme

# Indexation
v[1]                            # Premier élément (1-based!)
v[1:2]                          # Slice
v[[1, 3]]                       # Indexation par indices
m[1, :]                         # Première ligne
m[:, 2]                         # Deuxième colonne

# Dictionnaires
d = Dict("a" => 1, "b" => 2)
d["c"] = 3
get(d, "z", 0)                  # Avec valeur par défaut
keys(d), values(d), pairs(d)

# Sets
s = Set([1, 2, 2, 3])           # Set{Int} avec {1, 2, 3}
push!(s, 4)
union(s, Set([5, 6]))

# NamedTuples
nt = (nom="Alice", age=30)
nt.nom                           # Accès par point
```

---

## 7. Performances et Typage

```julia
# Éviter les variables globales dans les fonctions
const PI_APPROX = 3.14159  # Constante globale typée

# Fonction type-stable
function somme_stable(v::Vector{Float64})
    s = 0.0                     # Float64 dès le début
    for x in v
        s += x
    end
    return s
end

# @code_warntype pour détecter les instabilités
@code_warntype somme_stable(rand(10))

# Benchmark
using BenchmarkTools
@benchmark somme_stable($(rand(1000)))

# In-place (évite les allocations)
function normaliser!(v::Vector{Float64})
    v .= v ./ sum(v)            # .= modifie en place
end
```

---

## 8. Macros et Métaprogrammation

```julia
# Macros communes
@time somme(1:1_000_000)         # Temps + allocations
@elapsed somme(1:1_000_000)      # Juste le temps
@allocated somme(1:1_000_000)    # Juste les allocations
@show x                          # Affiche x = valeur

# Définir une macro
macro dire_bonjour(nom)
    return :(println("Bonjour ", $nom))
end

@dire_bonjour "Julia" 
```

---

## 9. Packages et Environnements

```julia
# Mode Pkg (dans le REPL : ])
# add DataFrames CSV Plots
# rm DataFrames
# status
# update
# activate .

# Programmatiquement
import Pkg
Pkg.add("DataFrames")
Pkg.status()
```

---

## 10. Data Science avec Julia

```julia
using DataFrames, CSV, Statistics

## Charger des données
df = CSV.read("data.csv", DataFrame)

## Manipuler
select(df, :colonne1, :colonne2)
filter(row -> row.colonne1 > 10, df)
transform(df, :colonne1 => (x -> x .* 2) => :double)

## GroupBy + Agrégation
gdf = groupby(df, :categorie)
combine(gdf, :valeur => mean => :moyenne)

## Missing values
dropmissing(df)
coalesce.(df.colonne, 0)

# Plots
using Plots
plot(rand(100))
scatter(rand(50), rand(50))
```

---

## 11. Calcul Scientifique

```julia
using LinearAlgebra, SparseArrays

## Algèbre linéaire
A = rand(3, 3)
b = rand(3)
x = A \ b                       # Résolution Ax = b
det(A), inv(A), eigvals(A)

## Optimisation
using Optim

rosenbrock(x) = (1.0 - x[1])^2 + 100.0 * (x[2] - x[1]^2)^2
resultat = optimize(rosenbrock, [0.0, 0.0])

## Intégration numérique
using QuadGK
integral, erreur = quadgk(x -> exp(-x^2), -Inf, Inf)

## Équations différentielles
using DifferentialEquations

function f!(du, u, p, t)
    du[1] = u[2]
    du[2] = -u[1]
end

u0 = [1.0, 0.0]
prob = ODEProblem(f!, u0, (0.0, 10.0))
sol = solve(prob)
```

---

## 12. Parallélisme

```julia
# Threads
Threads.@threads for i in 1:1000
    # Travail parallèle
end

# Tâches asynchrones
@sync for i in 1:10
    @async begin
        println("Tâche $i")
    end
end

# Distributed computing
using Distributed
addprocs(4)

@everywhere function travail(n)
    return sum(1:n)
end

futures = [@spawnat pid travail(1000) for pid in workers()]
resultats = fetch.(futures)
```

---

## 13. Interopérabilité Python/C/R

```julia
# Python
using PyCall
np = pyimport("numpy")
arr = np.array([1, 2, 3])

# C
t = ccall((:clock, "libc"), Int32, ())

# R
using RCall
R"mean(1:10)"
```

---

## Références
- Docs Julia : https://docs.julialang.org/
- JuliaHub : https://juliahub.com/
- Discourse Julia : https://discourse.julialang.org/