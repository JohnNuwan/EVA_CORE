---
name: language-rust
title: "Doctorat — Langage Rust"
description: "Compétence niveau docteur en Rust. Couvre ownership, borrowing, lifetimes, traits, async/await, unsafe, FFI, macros, allocateur, zero-cost abstractions, WASM, embedded, et le compilateur rustc."
category: research
lang: fr
---

# Doctorat : Langage Rust

## Présentation
Rust est un langage de programmation système conçu par Graydon Hoare (Mozilla Research, 2006-2010, stable 1.0 en 2015). Il garantit la sécurité mémoire sans ramasse-miettes grâce à un système de possession (ownership) vérifié statiquement par le compilateur (rustc). Rust offre des abstractions à coût zéro, une concurrence sans data races, et une interopérabilité native avec C. Il est utilisé dans les noyaux de systèmes d'exploitation, les navigateurs (Servo, Firefox), les moteurs de base de données, l'embarqué, et WebAssembly.

## Histoire et Contexte
- 2006 : Projet personnel de Graydon Hoare
- 2009 : Mozilla parraine le développement
- 2010 : Présentation publique ; compilateur initial en OCaml
- 2011 : Réécriture du compilateur en Rust (auto-hébergement)
- 2015 : Rust 1.0 — première version stable
- 2016-2018 : Édition 2018 — NLL (Non-Lexical Lifetimes), async/await, modules
- 2021 : Édition 2021 — closures disjointes, nouveau pattern match
- 2024 : Édition 2024 — impl Trait, RPITIT, GATs stables
- 2025+ : Rust 2027 edition, type-level programming, compile-time evaluation améliorée

## Architecture du Langage
- **Compilateur rustc** : Frontend (lexer, parser, AST, HIR, THIR, MIR) → Analyse emprunt/type → Backend LLVM (codegen)
- **MIR** (Mid-level Intermediate Representation) : Représentation intermédiaire pour l'analyse d'emprunt et les optimisations
- **HIR** (High-level IR) : AST simplifié après désucrage syntaxique
- **THIR** (Typed HIR) : HIR avec informations de types complètes
- **Polymorphisme** : Monomorphisation des génériques (pas de boxing générique)
- **Traits** : Système de classes de types (typeclasses) comme Haskell, avec résolution statique
- **Allocateur global** : `#[global_allocator]` permet de remplacer l'allocateur par défaut (jemalloc, mimalloc, etc.)
- **Modules et crates** : Système de paquets via Cargo ; arbre de dépendances résolu par le résolveur de Cargo

## Système de Types
- **Ownership** : Chaque valeur a exactement un propriétaire ; la propriété est transférée par move
- **Borrowing** : Références immuables (&T) multiples OU référence mutable unique (&mut T) — jamais simultanées
- **Lifetimes** : Annotations de durée de vie ('a) pour garantir que les références ne survivent pas à leurs données
- **NLL** (Non-Lexical Lifetimes) : Durées de vie calculées par analyse de flot de contrôle, pas lexicales
- **Types somme (enums)** : Pattern matching exhaustif ; variantes pouvant contenir des données
- **Types produit (structs)** : Nommés, tuples, unité — avec ou sans champs nommés
- **Generics** : Paramètres de type avec traits bounds ; higher-ranked trait bounds (HRTB)
- **GATs** (Generic Associated Types) : Types associés paramétrés (stables depuis 1.65)
- **RPIT/RPITIT** : Return Position Impl Trait (et dans les traits)
- **Pattern matching** : Exhaustif, irréfutable/réfutable, guards, destructuring
- **Never type** `!` : Fonction divergente
- **Dynamically Sized Types (DST)** : Slice `[T]`, trait objects `dyn Trait` — derrière un pointeur

## Compilation et Interprétation
- Rust est **compilé** : rustc produit du code natif via LLVM
- Chaîne de compilation : `.rs` → lexer → parser → AST → HIR → THIR → MIR → LLVM IR → code machine
- **Codegen units** : Partition du code en unités pour l'optimisation LLVM parallèle
- **LTO** (Link-Time Optimization) : Mono LTO, Thin LTO (fat/object)
- **Inlining** : Décisions d'inlining basées sur des heuristiques LLVM et des attributs `#[inline]`
- **Profile-guided optimization (PGO)** : Optimisation guidée par profilage
- **BOLT** : Optimisation binaire post-link (BOLT)
- **Cross-compilation** : Support natif via rustup targets ; cible triple (arch-vendor-os)
- **Cranelift backend** : Backend alternatif plus rapide pour le debug
- **Compilation incrémentale** : Réutilise les artefacts des compilations précédentes

## Mémoire et Performances
- **Pas de garbage collector** : La mémoire est libérée quand la variable sort de la portée (drop)
- **Ownership et drop** : Le compilateur insère les appels à `drop()` au moment de la dernière utilisation
- **Stack vs Heap** : Les variables sont sur la stack par défaut ; `Box<T>`, `Vec<T>`, `String` allouent sur le heap
- **Layout mémoire** : `#[repr(C)]`, `#[repr(align)]`, `#[repr(packed)]` — contrôle fin du layout
- **Spatial locality** : Les structures de données contiguës (Vec, array) optimisent le cache CPU
- **Zero-cost abstractions** : Les itérateurs, closures, et traits sont monomorphisés — pas de surcoût runtime
- **allocateur** : `alloc::GlobalAlloc` — remplaçable par jemalloc, mimalloc, snmalloc
- **Allocateur d'arène** : `bumpalo` pour des allocations bump allocator
- **Pinning** : `Pin<P>` pour garantir qu'une valeur ne bouge pas en mémoire (nécessaire pour async/await et self-referentiel)

## Écosystème et Outils
- **Cargo** : Build system, gestionnaire de paquets, test runner, documentation, benchmarking
- **crates.io** : Registre officiel de paquets (plus de 150 000 crates)
- **rustfmt** : Formateur de code officiel
- **clippy** : Linter officiel avec plus de 600 règles
- **rust-analyzer** : LSP (Language Server Protocol) — autocomplétion, refactoring, navigation
- **rustdoc** : Générateur de documentation markdown avec exemples testables
- **rustup** : Gestionnaire de versions du compilateur (stable, beta, nightly)
- **cargo-expand** : Expansion des macros pour debug
- **cargo-udeps** : Détection des dépendances inutilisées
- **cargo-audit** : Analyse de sécurité des dépendances
- **cargo-deny** : Politique de licences et sécurité
- **criterion.rs** : Benchmarking statistique
- **proptest** : Testing basé sur des propriétés (quickcheck-like)
- **miri** : Interpréteur MIR pour détecter les undefined behaviors
- **loom** : Model checker pour la concurrence

## Concurrence et Parallélisme
- **Fearless concurrency** : Garantie d'absence de data races par le type system
- **Send & Sync** : Traits auto-implementés marquant la sécurité thread-safe
- **std::thread** : Threads OS natifs avec `spawn`
- **async/await** : Futures et `poll` ; coopératif, single-threaded par défaut
- **Tokio / async-std** : Runtimes async multi-threaded (work-stealing scheduler)
- **async trait** : Traits avec méthodes async (nécessite des workarounds ou la nightly)
- **Channels** : `std::sync::mpsc` (multi-producer, single-consumer), `crossbeam-channel`, `tokio::sync::mpsc`
- **Mutex / RwLock** : Verrous du système d'exploitation avec poison semantics
- **Atomics** : `AtomicBool`, `AtomicU32`, `AtomicPtr` — barrières mémoire, ordering (Relaxed, Acquire, Release, AcqRel, SeqCst)
- **Rayon** : Parallélisme de données (parallel iterators, work-stealing)
- **SIMD** : `core::simd` (stable en nightly), `portable-simd`, `packed_simd`
- **Work-stealing** : Implémentations dans Tokio et Rayon

## Patterns Avancés
- **Borrow checker tricks** : Ghost cells, `Cell<T>`, `RefCell<T>`, `UnsafeCell<T>` pour la mutabilité intérieure
- **Typestate pattern** : Encodage d'états dans le type system (ex : protocole TCP : `TcpStream::connect() → TcpStream`)
- **Newtype pattern** : Wrap de types pour des garanties statiques sans surcoût
- **Builder pattern** : Construction d'objets complexes avec vérification au compile-time
- **Arena allocation** : Allocation groupée avec durée de vie contrôlée
- **Generational indices** : Index avec génération pour la sécurité mémoire dans les jeux/E CS
- **Ergonomic error handling** : `Result<T, E>`, `?` operator, `anyhow`, `thiserror`
- **Ecs pattern** : Entity-Component-System (specs, hecs, bevy_ecs)
- **Macros** : Declarative (`macro_rules!`) et proc macros (custom derive, attribute, function-like)
- **Pin + self-referential structs** : Construction de structures auto-référentielles avec `Pin`
- **Generics with const expressions** : `const N: usize` dans les paramètres de type
- **Inline assembly** : `core::arch::asm!` pour du code assembleur intégré

## Optimisation
- **Zero-cost abstractions** : Itérateurs, closures, `Option<T>` (discriminant niche), `Result<T, E>` — optimisés au compile-time
- **Niche optimization** : L'option niche (ex : `Option<&T>` utilise le pointeur nul comme `None`)
- **Branchless code** : Utilisation de select/compare pour éviter les branches
- **Restrict pointers** : `&mut [T]` as `restrict` — pas d'aliasing
- **Layout optimizations** : `#[repr(align)]`, padding, field reordering (compiler)
- **SIMD** : Autovectorisation LLVM ; intrinsèques manuelles pour SIMD
- **Constant evaluation** : `const fn`, `const generics` — évaluation au compile-time
- **Specialization** : `#[specialize]` pour des implémentations plus efficaces pour certains types
- **Inline thresholds** : Contrôle de l'inlining via `#[inline(always)]`, `#[inline(never)]`
- **Global Optimization** : LTO, PGO, BOLT, ThinLTO
- **Profile-guided** : Compilation avec instrumentation, exécution sur données réelles, recompilation
- **Bump allocation** : Dans les cas sans libération individuelle, un bump allocator est optimal

## Interopérabilité
- **FFI (Foreign Function Interface)** : `extern "C"`, `#[no_mangle]` pour lier avec C
- **cbindgen** : Génération de headers C à partir du code Rust
- **wasm-pack** : Compilation vers WebAssembly
- **wasm-bindgen** : Interop JS ↔ WASM
- **uniffi** : Génération de bindings multiplateformes (Kotlin, Swift, Python)
- **PyO3** : Extensions Python en Rust
- **napi-rs** : Modules Node.js natifs en Rust
- **ffmpeg-next / system-deps** : Liaison avec des bibliothèques systèmes C/C++
- **jemalloc allocator** : Utilisation de jemalloc comme allocateur global
- **Binary layout** : `#[repr(C)]` pour compatibilité ABI avec C
- **ABI stabilité** : Rust n'a pas d'ABI stable (à l'exception de `extern "C"`)

## Applications Industrielles
- **Firefox / Servo** : Moteur de rendu (Stylo, Pathfinder, WebRender)
- **Dropbox** : Moteur de synchronisation de fichiers (Nucleus)
- **Cloudflare** : Infrastructure réseau, HTTP/3, DDoS mitigation (Pingora)
- **Figma** : Serveur de rendu multi-threadé
- **AWS** : Lambda for Rust, Firecracker microVM, Bottlerocket OS
- **Microsoft** : Azure IoT Edge, Windows kernel components
- **Discord** : Services backend (gestion des états)
- **1Password** : Coeur du gestionnaire de mots de passe
- **nushell, fd, ripgrep, bat** : Outils modernes en Rust
- **Android** : Composants du système (binder, etc.)
- **Linux kernel** : Pilotes Rust (expérimental, depuis 6.1)
- **Automobile** : Volvo, Android Automotive — systèmes embarqués sécurisés

## Sécurité
- **Safety garantie** : Le compilateur garantit l'absence de : buffer overflow, use-after-free, null pointer dereference, double free, dangling pointers, data races
- **Unsafe** : Blocs qui désactivent certaines vérifications pour des opérations bas niveau ; responsabilité du programmeur
- **Sandboxing** : WebAssembly, Nix, bubblewrap
- **Cryptographie** : `ring`, `rustls`, `openssl` — implémentations vérifiées
- **Safe FFI** : `#[no_mangle]`, `extern "C"` — points d'entrée critiques
- **ASLR / NX / Stack cookies** : Reliés au compilateur et à l'OS
- **Format string safe** : `println!("{}", x)` — pas de format string vulnerabilities comme en C
- **Audit** : `cargo-audit`, `cargo-deny`, `RUSTSEC` database
- **Fuzzing** : `cargo-fuzz` (libFuzzer), `afl.rs`, `honggfuzz`
- **Formal verification** : Creusot (Why3 backend), Kani (model checking), Prusti (Viper)
- **Constant Time** : `ct-codecs` pour des primitives cryptographiques en temps constant

## Veille Technologique
- **RFCs Rust** : Toute évolution passe par le processus RFC (https://github.com/rust-lang/rfcs)
- **Inside Rust Blog** : https://blog.rust-lang.org/inside-rust/
- **This Week in Rust** : Newsletter hebdomadaire
- **Rust Compiler Team** : Archives des réunions, notes de design
- **Conférences** : RustConf, EuroRust, RustNL, RustLab
- **Langue** : `@rustlang` sur Twitter/X, `users.rust-lang.org`, `internals.rust-lang.org`
- **YouTube** : Rust Channel, Jon Gjengset, Ryan Levick, No Boilerplate
- **Évolutions majeures** : Trait aliases, type-level integers, const generics avancés, unsafe expressions, effet systeme
- **Livres** : "The Rust Programming Language" (Klabnik & Nichols), "Rust For Rustaceans" (Gjengset), "Programming Rust" (Blandy, Orendorff, Tindall)