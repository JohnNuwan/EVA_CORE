---
name: language-fortran
title: "Doctorat — Fortran"
description: "Compétence niveau docteur en Fortran. Couvre Fortran 90/95/2003/2008/2018/2023, array operations, coarrays, DO CONCURRENT, OOP, modules, interoperability with C, HPC, BLAS/LAPACK, MPI/OpenMP, et optimisation scientifique."
category: research
lang: fr
---

# Doctorat : Fortran

## Présentation
Fortran (FORmula TRANslation) est le plus ancien langage de programmation de haut niveau encore en usage intensif, créé par John Backus et son équipe chez IBM (1954-1957). Conçu pour le calcul scientifique et numérique, il reste le langage de référence en calcul haute performance (HPC), simulation physique, météorologie, dynamique des fluides computationnelle (CFD), et modélisation climatique. Sa force réside dans l'optimisation des opérations sur tableaux, la vectorisation automatique, les coarrays pour le parallélisme, et l'interopérabilité native avec les bibliothèques HPC (BLAS, LAPACK, FFTW).

## Histoire et Contexte
- 1954-1957 : Développement par John Backus (IBM)
- 1957 : Fortran I — compilateur optimisant (estimation : 50% d'efficacité C)
- 1958 : Fortran II — sous-programmes, fonctions séparées
- 1966 : Fortran 66 — premier standard ANSI
- 1977 : Fortran 77 — IF-THEN-ELSE, boucles DO, CHARACTER
- 1991 : Fortran 90 — modules, structures, ALLOCATABLE, free-form, WHERE
- 1995 : Fortran 95 — FORALL, PURE/ELEMENTAL procedures, derived type I/O
- 2004 : Fortran 2003 — OOP (héritage, polymorphisme), C interop (ISO_C_BINDING)
- 2010 : Fortran 2008 — Coarrays (parallélisme natif), DO CONCURRENT, submodules
- 2018 : Fortran 2018 — TS improvements, coarray collectives, teams
- 2023 : Fortran 2023 — améliorations DO CONCURRENT, arrays, I/O
- Compilateurs : GNU Fortran (gfortran), Intel Fortran (ifx/ifort), NVIDIA HPC SDK, IBM XL, Cray, Flang (LLVM)

## Architecture du Langage
- **Compilé** : Fortran est un langage compilé (pas d'interpréteur courant)
- **Free-form** (F90+) : Code libre (pas de colonnes fixes comme F77)
- **Fixed-form** (F77 legacy) : Colonnes 1-6 (commentaire, numéros), 7-72 (code)
- **Modules** (F90+) : Encapsulation, interface explicite, PRIVATE/PUBLIC
- **Submodules** (F2008) : Séparation implémentation/interface des modules
- **INTERFACE blocks** : Interfaces explicites pour les procédures externes
- **DO CONCURRENT** : Boucle parallèle sans dépendances
- **IMPLICIT NONE** : Toutes les variables doivent être déclarées (fortement recommandé)
- **INTENT** : INTENT(IN), INTENT(OUT), INTENT(INOUT) — contrôle des paramètres
- **PROCEDURE POINTERS** : Pointeurs de fonction (F2003+)
- **ABSTRACT INTERFACE** : Interfaces abstraites pour callbacks
- **BLOCK construct** : Portée locale dans un programme

## Système de Types
- **Types intrinsèques** : INTEGER, REAL (single/double), COMPLEX, LOGICAL, CHARACTER
- **KIND** : Précision — REAL(4), REAL(8), REAL(16) — via SELECTED_REAL_KIND
- **INTEGER kinds** : INTEGER(1), INTEGER(2), INTEGER(4), INTEGER(8)
- **Derived types** : TYPE, END TYPE — structures composées
- **Arrays** : Hiérarchie complète — tableau 1D, 2D, 3D, ..., 15D
- **ALLOCATABLE arrays** : Allocation dynamique — meilleure que les pointeurs
- **Automatic arrays** : Tableaux automatiques (taille basée sur les arguments)
- **Assumed-shape arrays** : Tableaux de forme implicite (interfaces explicites nécessaires)
- **POINTER** : Pointeurs Fortran (pas d'arithmétique)
- **CLASS** (F2003) : Polymorphisme (class vs type)
- **ABSTRACT** : Types abstraits pour l'héritage
- **BIND(C)** : Interopérabilité C — correspondance des types
- **C pointers** : TYPE(C_PTR), TYPE(C_FUNPTR) — pointeurs C

## Compilation et Interprétation
- **Chaîne de compilation** : .f90/.f95/.f03/.f08 → compilateur → .o → exécutable
- **gfortran** : GNU Fortran — standard complet, gratuit, nombreuses architectures
- **ifx/ifort** : Intel Fortran — compilateur de référence HPC, optimisations vectorielles
- **nfort** : NVIDIA HPC SDK — compilation GPU-aware
- **Flang** : LLVM-based Fortran (en développement)
- **Automatic vectorization** : Les compilateurs vectorisent automatiquement les boucles
- **Inline expansion** : Inlining de fonctions (MOVE_ALLOC, etc.)
- **Whole-program optimization** : IPO (Interprocedural Optimization)
- **Profile-guided optimization** : Instrumentation → profilage → recompilation
- **OpenMP** : Directives de compilateur pour le parallélisme
- **OpenACC** : Directives pour l'accélération GPU
- **Offloading** : GPU offloading via OpenMP/OpenACC (Intel, NVIDIA)

## Mémoire et Performances
- **Tableaux contigus** : Fortran stocke les tableaux en column-major (comme MATLAB, R)
- **Array slicing** : Slicing efficace avec des sections de tableau (x(1:n, :))
- **Contiguous memory** : Les tableaux sont garantis contigus — optimisations SIMD
- **ALLOCATABLE vs POINTER** : Les ALLOCATABLE sont généralement plus optimisables
- **ELEMENTAL** : Opérations scalaires appliquées aux tableaux automatiquement
- **WHERE / FORALL** : Masques et opérations vectorielles parallèles
- **PURE / ELEMENTAL** : Procédures sans effets de bord — plus d'optimisations
- **DO CONCURRENT** : Indique que les itérations sont indépendantes
- **TARGET** : Variables pouvant être pointées
- **CONTIGUOUS** : Garantie de contiguïté mémoire (F2008+)
- **ASSOCIATE** : Associé des noms à des expressions
- **Stack vs Heap** : Les variables locales (non ALLOCATABLE) sont sur la stack
- **Avoid pointers** : Les pointeurs Fortran limitent les optimisations

## Écosystème et Outils
- **BLAS** (Basic Linear Algebra Subprograms) : Opérations vectorielles et matricielles
- **LAPACK** (Linear Algebra PACKage) : Algèbre linéaire avancée
- **FFTW** : Fastest Fourier Transform in the West
- **NetCDF** : Stockage de données scientifiques (géo/physics)
- **HDF5** : Format de données hiérarchique
- **PETSc** : Parallel Extensible Toolkit for Scientific Computation
- **ScaLAPACK** : LAPACK distribué
- **OpenMP** : Directives de parallélisme mémoire partagée
- **MPI** : Message Passing Interface pour calcul distribué
- **Coarray Fortran (CAF)** : Parallélisme natif via coarrays
- **makedepf90** : Génération de dépendances
- **fpm** (Fortran Package Manager) : Gestionnaire de paquets moderne
- **FORD** : Générateur de documentation (style Doxygen)
- **Pluto.jl interoperability** : Fortran peut être appelé depuis Julia
- **PyFortran** : Interop Python
- **VS Code** : Modern Fortran extension, Fortran IntelliSense

## Concurrence et Parallélisme
- **Coarray Fortran** (F2008+) : Parallel programming natif — `x[*]` syntaxe
- **Teams** (F2018) : Hiérarchie d'images parallèles
- **DO CONCURRENT** (F2008+) : Boucles parallèles sans data race
- **OpenMP** : `!$OMP PARALLEL DO`, `!$OMP TASK`, `!$OMP TARGET OFFLOAD`
- **MPI** : `MPI_Init`, `MPI_Send`, `MPI_Recv`, `MPI_Allreduce`
- **OpenACC** : Directives GPU (NVIDIA/AMD)
- **CUDA Fortran** : NVIDIA CUDA dans Fortran (kernels, device)
- **Images (CAF)** : Chaque image est un processus avec sa propre mémoire
- **Collectives** (F2018) : CO_SUM, CO_MIN, CO_MAX, CO_BROADCAST, CO_REDUCE
- **SYNC ALL/IMAGES** : Synchronisation d'images
- **LOCK / UNLOCK** : Verrous critiques
- **ATOMIC** : Opérations atomiques (F2008+)
- **CRITICAL** : Section critique

## Patterns Avancés
- **Derived types with procedures** : Type-bound procedures (méthodes)
- **OOP in Fortran** : Héritage, polymorphisme, ABSTRACT types
- **Mixin via modules** : Composition via modules
- **Abstract interface** : Callbacks et fonction pointers
- **Operator overloading** : INTERFACE OPERATOR(+), ASSIGNMENT(=)
- **Defined I/O** : INTERFACE READ(FORMATTED), WRITE(UNFORMATTED)
- **Function overloading** : Generic interfaces (INTERFACE name)
- **Type extension** : EXTENDS — héritage OOP
- **Class default** : Polymorphisme avec CLASS(*) (unlimited polymorphic)
- **Select type** : Type guard for polymorphic objects
- **Storage association** : EQUIVALENCE, COMMON blocks (legacy, à éviter)
- **Namelist** : I/O simplifié pour les données de configuration
- **List-directed I/O** : READ(*,*), WRITE(*,*) — format libre
- **F2008 submodules** : Séparation module interface / implémentation

## Optimisation
- **Vectorization automatique** : Les compilateurs vectorisent le code array-op
- **SIMD** : Compiler auto-vectorisation SSE/AVX/AVX-512/NEON
- **Loop optimization** : Loop unrolling, fusion, interchange, tiling
- **Array copy elision** : Éviter les copies temporaires de tableaux
- **Contiguous memory** : Garantie que les tableaux sont contigus
- **ELEMENTAL** : Vectorisation automatique des opérations scalaires
- **PURE** : Permet plus d'optimisations (pas d'effets de bord)
- **DO CONCURRENT** : Hint pour le parallélisme (SIMD, GPU, threads)
- **INLINE** : Inlining de fonctions (avec directives)
- **ALIGN** : Directives d'alignement mémoire
- **Interprocedural optimization** : Optimisation à travers les appels de fonctions
- **Loop blocking** : Optimisation de la hiérarchie mémoire (cache blocking)
- **Algebraic simplification** : Reconnaissance de patterns mathématiques
- **Avoid POINTER** : Les pointeurs limitent l'optimisation

## Interopérabilité
- **ISO_C_BINDING** (F2003) : Module standard pour l'interop C
- **BIND(C)** : Liaison directe avec du code C
- **C_F_PROCPOINTER** : Conversion pointeur de fonction C ↔ Fortran
- **C_F_POINTER** : Conversion C pointer → Fortran pointer
- **C_LOC, C_FUNLOC** : Adresses C d'objets Fortran
- **Interop C** : Appel de bibliothèques C (BLAS, LAPACK, FFTW en sont)
- **Interop Python** : NumPy Fortran interface, f2py, ctypes, CFFI
- **Interop Julia** : ccall pour appeler Fortran depuis Julia
- **Interop R** : .Fortran() dans R
- **Interop MATLAB** : MEX files (Fortran)
- **gRPC** : Modern services via C interop
- **COBOL** : Interop via fichiers (legacy systems)
- **GPU interop** : CUDA Fortran, OpenACC, OpenMP offload

## Applications Industrielles
- **Météorologie** : ECMWF (IFS — Integrated Forecasting System), GFS, WRF
- **Climatologie** : CESM, HadGEM, MPI-ESM — modèles climatiques globaux
- **Dynamique des fluides (CFD)** : OpenFOAM, NASTRAN (core solver)
- **Aéronautique** : Airbus, Boeing — simulation structures et fluides
- **Automobile** : Crash tests, analyse éléments finis (Abaqus, Nastran)
- **Finance quantitative** : Pricing de produits dérivés (historique)
- **Recherche nucléaire** : Simulation de réacteurs, codes neutroniques
- **Cosmologie / Astrophysique** : Simulations N-corps (Gadget, RAMSES)
- **CAE / Simulation** : COMSOL Multiphysics (solver backend)
- **Géophysique** : Océanographie, sismologie, prospection pétrolière
- **Optimisation mathématique** : NAG Library, HSL Mathematical Software
- **Bioinformatique** : Analyse de séquences (les algorithmes plus anciens)
- **Défense** : Simulation et modélisation militaires

## Sécurité
- **Memory safety** : Pas de gestion mémoire manuelle (pas de malloc/free natif)
- **Bounds checking** : Optionnel dans les compilateurs (-fcheck=bounds)
- **Array bounds** : Les accès hors limites peuvent être détectés (à l'exécution)
- **Pointer safety** : Pas d'arithmétique de pointeur
- **ALLOCATABLE safety** : Allocation/désallocation automatique en sortie de portée
- **Intent safety** : INTENT(IN) protège les arguments d'entrée
- **Implicit none** : Force la déclaration explicite des variables
- **F2008 submodules** : Encapsulation renforcée
- **Fortran vs C** : Moins de UB que C (mais pas memory-safe complet)
- **Formal verification** : Code vérifié (NASA, aviation) — outils limités
- **Numerical safety** : IEEE 754 — comportement défini pour les exceptions

## Veille Technologique
- **Fortran Standards** : ISO/IEC JTC1/SC22/WG5 — groupe de normalisation Fortran
- **Fortran-lang.org** : Site communautaire moderne de Fortran
- **GitHub** : fortran-lang — stdlib, fpm, documentation
- **Compilateur news** : GNU Fortran, Intel ifx, NVIDIA HPC SDK, Flang (LLVM)
- **HPC conferences** : SC (Supercomputing), ISC High Performance, PASC
- **Fortran Conferences** : FortranCon (annuelle)
- **Fortran Discourse** : fortran-lang.discourse.group
- **Fortran newsletter** : Fortran Weekly
- **Évolutions clés** : Fortran 2023, fpm maturation, interop Python, Coarray maturity, GPU offloading