---
name: language-cpp
title: "Doctorat — Langage C++"
description: "Compétence niveau docteur en C++. Couvre C++20/23/26, templates, concepts, constexpr, coroutines, modules, RAII, move semantics, SFINAE, CRTP, policy-based design, STL internals, allocators, RTTI, ABI, et optimisation."
category: research
lang: fr
---

# Doctorat : Langage C++

## Présentation
C++ est un langage de programmation compilé, multi-paradigme (procédural, orienté objet, générique, fonctionnel), créé par Bjarne Stroustrup (Bell Labs, 1979-1985). Conçu comme un C avec des classes, C++ a évolué pour devenir un langage extrêmement puissant et complexe, offrant abstraction à coût zéro, programmation générique, métaprogrammation par templates, et un contrôle total du matériel. Standardisé par l'ISO (C++98, C++03, C++11, C++14, C++17, C++20, C++23, C++26 en préparation).

## Histoire et Contexte
- 1979 : "C with Classes" par Bjarne Stroustrup (Bell Labs)
- 1985 : Première version commerciale (Cfront — compilateur C++ vers C)
- 1998 : ISO C++98 — premier standard (STL incluse)
- 2005 : TR1 — Technical Report 1 (shared_ptr, regex, random)
- 2011 : C++11 — auto, move semantics, lambdas, constexpr, variadic templates
- 2014 : C++14 — generic lambdas, relaxed constexpr
- 2017 : C++17 — if constexpr, structured bindings, filesystem, variant, optional
- 2020 : C++20 — concepts, ranges, coroutines, modules, chrono, span
- 2023 : C++23 — std::print, std::expected, std::out_ptr, flat_map, mdspan
- 2024-2025 : C++26 — pattern matching, contracts, reflection, executors

## Architecture du Langage
- **Compilé** : Source (.cpp/.cc/.cxx) → Préprocesseur → Compilation → Assemblage → Link
- **One Definition Rule (ODR)** : Chaque entité définie exactement une fois
- **Translation unit** : Unité de compilation (.cpp + headers inclus)
- **Compilation model** : #include model traditionnel, modules (C++20) nouveau
- **ABI** : Itanium C++ ABI (Linux), MSVC ABI (Windows) — name mangling, vtable layout
- **Compilateurs** : GCC (g++), Clang (clang++), MSVC, EDG (frontend), Intel (icx)
- **STL implementations** : libstdc++ (GCC), libc++ (LLVM), Microsoft STL

## Système de Types
- **Types fondamentaux** : Hérités de C + bool, wchar_t, char8_t/16_t/32_t
- **Références** : T& (lvalue), T&& (rvalue) — move semantics, perfect forwarding
- **Pointeurs** : T* (C-style), smart pointers (unique_ptr, shared_ptr, weak_ptr)
- **Classes/Structs** : Héritage (multiple, virtual), polymorphisme, encapsulation
- **Templates** : Paramètres de type, paramètres non-type (NTTP), variadic templates
- **Concepts** (C++20) : Contraintes de template — std::same_as, std::derived_from
- **Enums** : enum (C-legacy), enum class (scoped, type-safe)
- **Unions** : union, variant (C++17) — type-safe union
- **optional, variant, any** (C++17) : Types somme et option
- **expected** (C++23) : Type résultat avec erreur
- **RTTI** : typeid, dynamic_cast — informations de type à l'exécution
- **auto** : Déduction de type à la compilation
- **decltype** : Type d'une expression
- **typedef / using** : Alias de type (using est plus puissant)

## Compilation et Interprétation
- **Compilation** : GCC/Clang/MSVC — pas d'interpréteur natif (sauf Cling, CERN)
- **Modules** (C++20) : Remplacement des headers — compilation plus rapide, meilleure isolation
- **Precompiled headers** : Accélération de la compilation des headers
- **constexpr / consteval / constinit** : Évaluation à la compilation (compile-time)
- **Instantiation** : Les templates sont instanciés au compile-time
- **Two-phase lookup** : Recherche de noms en deux phases pour les templates
- **SFINAE** : Substitution Failure Is Not An Error — filtrage de templates
- **LTO** (Link-Time Optimization) : Optimisation inter-modulaire
- **Inlining** : Décisions du compilateur + inline/always_inline
- **Coroutines** (C++20) : Fonctions suspendables avec co_await, co_yield, co_return

## Mémoire et Performances
- **RAII** : Resource Acquisition Is Initialization — constructeur acquiert, destructeur libère
- **Smart pointers** : unique_ptr (exclusive ownership), shared_ptr (reference counting), weak_ptr
- **Move semantics** : Déplacement de ressources (std::move) — évite les copies coûteuses
- **Copy elision** : NRVO / RVO — élimination des copies temporaires
- **STL containers** : vector, deque, list, forward_list, map, set, unordered_map
- **Allocators** : std::allocator, stateful allocators, polymorphic allocators (pmr)
- **Small String Optimization (SSO)** : Petites chaînes stockées dans l'objet string
- **SOO/SBO** : Small Object/Buffer Optimization
- **Memory mapping** : mmap — fichiers mappés en mémoire
- **Cache-friendly** : Contiguous storage (vector), struct of arrays (SoA)
- **Placement new** : Construction d'objets dans une mémoire pré-allouée

## Écosystème et Outils
- **Compilateurs** : GCC (g++), Clang (clang++), MSVC, Intel C++ Compiler
- **Build systems** : CMake (standard), Meson, Bazel, Conan, vcpkg
- **Package managers** : Conan, vcpkg, spack
- **Testing** : Google Test, Catch2, Boost.Test
- **Profiling** : perf, Valgrind (callgrind), gperftools, VTune, Tracy
- **Sanitizers** : AddressSanitizer, UndefinedBehaviorSanitizer, ThreadSanitizer, MemorySanitizer
- **Static analysis** : clang-tidy, PVS-Studio, Coverity, CppDepend
- **Debugging** : GDB, LLDB, WinDbg
- **Build time** : ccache, distcc, ninja
- **Documentation** : Doxygen, Sphinx/Breathe
- **ABI compliance** : abi-compliance-checker, abi-dumper
- **C++ Standard Library** : std:: (libstdc++, libc++, MSVC STL)

## Concurrence et Parallélisme
- **std::thread** (C++11) : Threads natives avec RAII
- **std::jthread** (C++20) : Threads avec auto-join et stop_token
- **std::async / std::future** : Asynchronisme avec promesses et futurs
- **std::mutex, std::shared_mutex** : Verrous exclusifs et partagés
- **std::lock_guard, std::scoped_lock, std::unique_lock** : RAII locking
- **std::condition_variable** : Variables conditionnelles
- **std::atomic** / **std::atomic_ref** : Opérations atomiques, memory ordering
- **std::latch, std::barrier** (C++20) : Barrières de synchronisation
- **std::semaphore** (C++20) : Sémaphores (counting, binary)
- **std::stop_token** (C++20) : Mécanisme d'arrêt coopératif
- **OpenMP** : #pragma omp — parallélisme de haut niveau
- **TBB** (Intel Threading Building Blocks) : Parallélisme avec flow graph
- **OpenCL / CUDA / SYCL** : Calcul GPU/hétérogène
- **Coroutines** (C++20) : Coopératif, sans threads

## Patterns Avancés
- **CRTP** (Curiously Recurring Template Pattern) : Polymorphisme statique
- **Policy-based design** : Templates avec paramètres de politique (ex: allocator, deleter)
- **SFINAE / enable_if** : Contrôle d'activation de templates
- **Concepts** (C++20) : Contrat sur les paramètres de template
- **RAII** : Gestion automatique des ressources
- **PImpl** (Pointer to Implementation) : Encapsulation, ABI stability
- **Type erasure** : Suppression de type (std::function, std::any)
- **Expression templates** : Expressions lazy, optimisées (ex: Eigen, Blitz++)
- **Mixins** : Composition via héritage template
- **NVI** (Non-Virtual Interface) : Template method pattern en C++
- **Curiously Recurring CRTP** : Static polymorphism
- **Property system** : std::map<string, any>, boost.property_tree
- **Tag dispatch** : std::forward_iterator_tag, etc.
- **Static polymorphism** : CRTP vs virtual dispatch

## Optimisation
- **Zero-cost abstraction** : Principe de conception C++ — pas de surcoût pour ce qui n'est pas utilisé
- **Inlining** : Fonctions courtes inlinées, forceinline
- **Move semantics** : Évite les copies superflues
- **Copy elision** : RVO, NRVO (garanti depuis C++17)
- **Small object optimization** : Petits objets stockés inline
- **SSO** (Small String Optimization) : std::string petites chaînes locales
- **EBO** (Empty Base Optimization) : Classe vide n'occupe pas d'espace
- **Static polymorphism** : CRTP au lieu de virtual (pas de vtable)
- **constexpr** : Calculs déplacés au compile-time
- **STL algorithm optimization** : Algorithmes SIMD dans les STL modernes
- **SIMD** : std::experimental::simd (Parallelism TS 2), intrinsèques
- **Profile-guided optimization** : Compilation + profilage + recompilation
- **LTO / WPO** : Whole Program Optimization
- **Cache optimization** : SoA, AoS, cache line padding, false sharing évité

## Interopérabilité
- **extern "C"** : Liaison C — pas de name mangling
- **C ABI** : Les fonctions exportées avec extern "C" sont appelables depuis tout langage
- **COM/COM+** : Microsoft Component Object Model
- **Python** : pybind11, Boost.Python, Cython
- **Java** : JNI (Java Native Interface) — via extern "C"
- **C#/.NET** : C++/CLI, P/Invoke
- **Rust** : Bindings via cbindgen, CXX
- **WASM** : Compilation vers WebAssembly via Emscripten
- **RPC** : gRPC (via protobuf), Thrift
- **IPC** : Sockets, pipes, shared memory (shm_open, mmap), D-Bus
- **ABI** : Itanium C++ ABI, MSVC ABI — fragile, sujet à changement
- **DLL/SO** : Bibliothèques dynamiques avec dllexport/dllimport

## Applications Industrielles
- **Google Chrome** : Navigateur — C++ pour le moteur de rendu (Blink)
- **Microsoft Office** : Suite bureautique
- **Adobe Creative Suite** : Photoshop, Premiere, After Effects
- **Unreal Engine** : Moteur de jeu AAA
- **Qt** : Framework GUI multiplateforme
- **MongoDB** : Base de données NoSQL
- **TensorFlow (core)** : Framework ML (performances critiques)
- **LLVM/Clang** : Infrastructure de compilation
- **Bloomberg** : Infrastructure financière (realtime)
- **Mozilla Firefox** : Servo, Gecko (transition vers Rust)
- **MySQL / MariaDB** : Bases de données relationnelles
- **Autodesk Maya** : Logiciel 3D
- **Flight simulators** : Microsoft Flight Simulator
- **Jeux AAA** : La majorité des moteurs de jeux
- **Robotique** : ROS (Robot Operating System)
- **Automobile** : AUTOSAR, systèmes d'infotainment

## Sécurité
- **Memory safety** : Problème historique — buffer overflows, use-after-free, dangling pointers
- **RAII** : Réduit les fuites de ressources
- **Smart pointers** : Éliminent beaucoup de fuites mémoire
- **std::span** (C++20) : Vues bornées (bounds-safe)
- **std::gsl** : Guidelines Support Library — spans, not_null, multi_span
- **Sanitizers** : ASan, UBSan, TSan, MSan, LSan
- **Static analysis** : clang-tidy, PVS-Studio, Coverity
- **SEI CERT C++** : Coding standards sécurisés
- **AUTOSAR C++** : Coding standards pour l'automobile
- **C++ Core Guidelines** : Recommandations de Stroustrup/Sutter
- **Fuzzing** : libFuzzer, AFL++
- **Format string** : std::format (C++20) — type-safe
- **Bounds safety** : at() vs [], std::span, gsl::span
- **Integer safety** : SafeInt, Boost.SafeNumerics
- **Contracts** (C++26) : Préconditions, postconditions, invariants

## Veille Technologique
- **ISO C++ Committee (WG21)** : isocpp.org — évolution du standard
- **CppCon / C++Now** : Conférences annuelles majeures
- **isocpp.org** : Site officiel, blog, FAQ
- **WG21 papers** : open-std.org/jtc1/sc22/wg21
- **Compiler Explorer** : godbolt.org — test de code en ligne
- **CppReference** : en.cppreference.com — documentation complète
- **Meeting C++** : meetingcpp.com — nouvelles et blog
- **Reddit** : r/cpp
- **YouTube** : CppCon, C++Now, Jason Turner, Nicolai Josuttis
- **Livres** : The C++ Programming Language (Stroustrup), Effective Modern C++ (Meyers), C++ Templates (Vandevoorde)