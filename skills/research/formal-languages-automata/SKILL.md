---
name: formal-languages-automata
description: Compétence niveau expert en langages formels et automates (cs.FL) — automates finis, automates à pile, machines de Turing, grammaires de Chomsky, parsing, vérification formelle et model checking.
category: research
---

# Langages Formels et Automates — cs.FL

## Présentation

Compétence couvrant l'ensemble du domaine **cs.FL (Formal Languages and Automata Theory)** : théorie des automates, hiérarchie de Chomsky, langages formels, algorithmes de parsing, logique temporelle et vérification formelle. Cette compétence constitue une base fondamentale pour la compilation, l'analyse statique, la vérification de modèles, et la conception de langages de programmation.

## Domaines

### 1. Automates Finis (Finite Automata — FA)
- **Automates finis déterministes (DFA)** : définition, construction, minimisation (algorithmes de Moore, Hopcroft)
- **Automates finis non-déterministes (NFA)** : définition, ε-transitions, construction de sous-ensembles (subset construction)
- **Équivalence DFA/NFA** : conversion NFA → DFA, complexité exponentielle dans le pire cas
- **Automates finis alternants (AFA)** : quantification universelle/existentielle des états
- **Automates de Büchi** : acceptation sur mots infinis (ω-automates), complémentation
- **Automates de Muller, Rabin, Streett, Parity** : conditions d'acceptation pour ω-langages
- **Propriétés de clôture** : union, intersection, complément, concaténation, étoile de Kleene
- **Lemme de pompage (pumping lemma)** pour langages réguliers
- **Théorème de Myhill-Nerode** : relation d'équivalence, minimalité, quotient automatique

### 2. Automates à Pile (Pushdown Automata — PDA)
- **Définition et composants** : pile, fonction de transition, configurations
- **PDA déterministes (DPDA)** vs **non-déterministes (NPDA)**
- **Équivalence PDA / Grammaires hors-contexte** : algorithme de conversion (LL(1), forme normale de Greibach)
- **Lemme de pompage pour langages hors-contexte (CFL)**
- **Automates à pile visibles** (visibly pushdown automata / VPA) : équilibrage des appels/retours
- **Automates à plusieurs piles** : équivalence avec les machines de Turing

### 3. Machines de Turing (Turing Machines — TM)
- **Définition formelle** : ruban infini, alphabet, fonction de transition
- **Variantes** : multi-rubans, non-déterministes, à ruban bidimensionnel
- **Thèse de Church-Turing** : équivalence des modèles de calcul
- **Machine de Turing universelle (UTM)**
- **Problème de l'arrêt (Halting Problem)** : indécidabilité
- **Décidabilité vs semi-décidabilité** : langages récursifs vs récursivement énumérables (RE)
- **Hiérarchie arithmétique** : ensembles Σₙ, Πₙ, Δₙ
- **Réductibilités** : many-one (≤ₘ), Turing (≤ₜ), Cook, Karp
- **Théorèmes de Rice** : propriétés non-triviales des langages RE
- **Transducteurs** : fonctions calculables, machines de Turing avec sortie

### 4. Grammaires Formelles (Hiérarchie de Chomsky)

| Type | Nom | Grammaire | Automate | Exemples |
|------|-----|-----------|----------|----------|
| Type 0 | **Sans restriction** | α → β (α,β ∈ (V∪T)*, α non-vide) | Machine de Turing | Langages RE |
| Type 1 | **Context-sensitive (CSG)** | αAβ → αγβ (γ ≠ ε) | Automate linéairement borné (LBA) | {aⁿbⁿcⁿ} |
| Type 2 | **Hors-contexte (CFG)** | A → γ | Automate à pile (PDA) | {aⁿbⁿ} |
| Type 3 | **Régulière (RG)** | A → aB / A → a | Automate fini (FA) | {aⁿ} |

- **Formes normales** : Chomsky (CNF), Greibach (GNF), Kuroda (pour CSG)
- **Grammaires attribuées** (attribute grammars) : attributs synthétisés/hérités
- **Grammaires de dépendances** (dependency grammars)
- **Grammaires catégorielles** (categorial grammars, Lambek calculus)

### 5. Langages Réguliers, Hors-contexte et Context-sensitive

- **Langages réguliers** : expressions régulières, étoile de Kleene, théorème de Kleene (FA ↔ expressions régulières), algèbre de Kleene (A*, demi-anneaux)
- **Langages hors-contexte** : arbres de dérivation, ambiguïté, inherent ambiguity, lemme d'Ogden
- **Langages context-sensitive** : LBA, lemme de pompage pour CSL, problèmes PSPACE-complets
- **Hiérarchie des langages** : inclusions strictes (Réguliers ⊂ CFL ⊂ CSL ⊂ RE)
- **Langages déterministes hors-contexte (DCFL)** : propriétés, ambiguïté non-inhérente
- **Langages algébriques** : séries formelles, séries rationnelles

### 6. Algorithmes de Parsing

- **Analyse descendante (Top-down)** : LL(k), analyse récursive descendante, élimination de la récursivité gauche et factorisation gauche
- **Analyse ascendante (Bottom-up)** :
  - **LR(k), SLR, LALR** : tables d'action et de goto, conflits shift/reduce et reduce/reduce
  - **Génération de parseurs** : Yacc/Bison, ANTLR, Tree-sitter
- **Analyse universelle (universal parsing)** :
  - **Earley** : O(n³) pour CFG générale, O(n²) pour grammaires non-ambiguës, O(n) pour LR(0)
  - **CYK (Cocke–Younger–Kasami)** : O(n³ · |G|), nécessite CNF
  - **GLR (Generalized LR)** : Tomita, forêts d'analyse
  - **GLL (Generalized LL)** : descente récursive généralisée
  - **Valiant** : O(n^ω) via multiplication matricielle rapide
- **Parsing de langages context-sensitive** : algorithmes pour CSG
- **Parsing de langages naturels** : chart parsing, statistical parsing, PCFG, CYK probabiliste

### 7. Automates Temporisés (Timed Automata)

- **Définition** : automates finis avec horloges réelles (clocks), contraintes de temps (gards, invariants)
- **Sémantique** : transitions discrètes + passage du temps continu, zones et régions
- **Région graph** : équivalence de temps, construction du quotient fini
- **Zone graph et DBMs (Difference Bound Matrices)** : représentation symbolique des zones
- **Vérification de réseaux d'automates temporisés** : produit synchronisé
- **UPPAAL** : outil de vérification pour automates temporisés, propriétés CTL ⊆ A⊲TCTL
- **Automates temporisés avec urgence, deadlines, invariants**
- **Extensions** : automates à coûts/poids (weighted/priced timed automata), automates hybrides linéaires
- **Décidabilité** : problème d'accessibilité (PSPACE-complet), langages temporisés

### 8. Automates d'Arbres (Tree Automata)

- **Automates d'arbres ascendants (bottom-up NTA/DFA)** : régularité sur les arbres
- **Automates d'arbres descendants (top-down NTA)** : équivalence avec bottom-up pour NTA
- **Automates d'arbres alternants (alternating tree automata)**
- **Grammaires d'arbres réguliers (regular tree grammars)** : équivalence avec NTA
- **Automates de mots sur les arbres** : logique MSO sur les arbres
- **Applications** : vérification de programmes (logique du temps du programme, pointeurs), types XML (Schémas, Relax NG), réécriture de termes
- **Automates d'arbres d'ordres supérieurs (higher-order tree automata)**

### 9. Logique Temporelle et Model Checking

- **LTL (Linear Temporal Logic)** : opérateurs G, F, X, U, R ; sémantique sur mots infinis
- **CTL (Computation Tree Logic)** : opérateurs branchants EX, AX, EF, AF, EG, AG, EU, AU
- **CTL\*** : fusion de LTL et CTL, expressivité supérieure
- **STL (Signal Temporal Logic)** : propriétés sur signaux continus, contraintes de temps dense, opérateurs temporels paramétrés
  - Sémantique quantitative (robustness degree)
  - Monitoring temps-réel, falsification
  - Breach, S-TaLiRo, UPPAAL STRATEGO
- **TCTL (Timed CTL)** : propriétés temporisées pour automates temporisés
- **µ-calcul (modal µ-calculus)** : points fixes (µ, ν), expressivité maximale (inclut LTL, CTL, CTL*)
- **MITL (Metric Interval Temporal Logic)** : contraintes d'intervalle sans ponctualité
- **MTL (Metric Temporal Logic)** : opérateurs temporisés avec intervalles
- **Propriétés de correction** : sûreté (safety, AG ¬bad), vivacité (liveness, GF good), équité (fairness)
- **Techniques de model checking** :
  - **Graphes d'états explicites** (explicit-state model checking) : reachability, emptiness check (Nested DFS, SCC)
  - **Model checking symbolique** (symbolic model checking) : BDD (diagrammes de décision binaire), SAT-solvers (bounded model checking, BMC)
  - **Abstraction** : CEGAR (Counterexample-Guided Abstraction Refinement), abstraction par prédicats
  - **Partial order reduction (POR)** : élimination des entrelacements redondants
  - **Symmetry reduction** : élimination des états symétriques
  - **Exploration dirigée** : heuristiques de parcours, guidage par distance

### 10. Outils de Vérification Formelle

- **Spin** : model checking explicite pour processus asynchrones (Promela), LTL, never claims, vérification on-the-fly, partial order reduction, IS0:26262 niv. Langage d'entrée : Promela
- **NuSMV / nuXmv** : model checking symbolique (BDD, SAT), LTL, CTL, vérification inductive, IC3/PDR, systèmes synchrones à variables finies, modules, SMV
- **Z3 (Microsoft Research)** : SMT-solver (théories : bitvectors, arithmétique, tableaux, chaînes, datatypes) — preuves de programmes, analyse de programmes symbolique, résolution de contraintes. API Python/C/C++/Java/OCaml/.NET. Théories : QF_LIA, QF_LRA, QF_BV, QF_S, QF_FP, etc.
- **Coq** : assistant de preuve basé sur le Calcul des Constructions Inductives (CIC), logique d'ordre supérieur, tactiques, extraction de programmes, Math Components, SSReflect
- **Isabelle/HOL** : assistant de preuve générique (HOL, ZF), Isar (langage structuré de preuve), locale et type classes, Archive of Formal Proofs (AFP)
- **UPPAAL** : vérification d'automates temporisés et hybrides, TCTL, réseaux d'automates
- **PRISM** : model checking probabiliste, DTMC/CTMC/MDP, logique PCTL/CSL, évaluation quantitative

## Catégories

- `cs.FL` — Formal Languages and Automata Theory
- `cs.LO` — Logic in Computer Science (pour logique temporelle, µ-calcul)
- `cs.SE` — Software Engineering (vérification formelle, model checking)
- `cs.PL` — Programming Languages (parsing, grammaires, compilation)
- `cs.CC` — Computational Complexity (décidabilité, complexité du parsing)
- `cs.LG` — Machine Learning (PCFG, parsing statistique)

## Articles

1. **Huffman (1954)** — "The Synthesis of Sequential Switching Circuits" (DFA minimization, fondation)
2. **Chomsky (1956/1959)** — "Three models for the description of language" / "On certain formal properties of grammars" (hiérarchie de Chomsky)
3. **Rabin & Scott (1959)** — "Finite Automata and Their Decision Problems" (NFA, subset construction)
4. **Earley (1970)** — "An Efficient Context-Free Parsing Algorithm" (Earley parser, O(n³))
5. **Cocke & Schwartz (1970)** / **Younger (1967)** / **Kasami (1965)** — CYK algorithm
6. **Knuth (1965)** — "On the Translation of Languages from Left to Right" (LR parsing)
7. **DeRemer (1971)** — "Simple LR(k) Grammars" (SLR, LALR)
8. **Alpern & Schneider (1985)** — "Defining Liveness" (safety / liveness classification)
9. **Pnueli (1977)** — "The Temporal Logic of Programs" (LTL fondateur)
10. **Clarke & Emerson (1981)** — "Design and Synthesis of Synchronization Skeletons Using Branching Time Temporal Logic" (CTL, model checking)
11. **Queille & Sifakis (1982)** — "Specification and Verification of Concurrent Systems in CESAR"
12. **McMillan (1993)** — *Symbolic Model Checking* (BDD, NuSMV foundations)
13. **Alur & Dill (1994)** — "A Theory of Timed Automata" (automates temporisés)
14. **Bryant (1986)** — "Graph-Based Algorithms for Boolean Function Manipulation" (ROBDD)
15. **Biere et al. (1999)** — "Bounded Model Checking" (SAT-based BMC)
16. **Clarke et al. (2000)** — "Counterexample-Guided Abstraction Refinement" (CEGAR)
17. **Holzmann (1997)** — "The Model Checker Spin" (Spin, Promela, verification algorithm)
18. **de Moura & Bjørner (2008)** — "Z3: An Efficient SMT Solver"
19. **Coquand & Huet (1988)** — "The Calculus of Constructions" (Coq)
20. **Paulson (1994)** — "Isabelle: A Generic Theorem Prover"
21. **Bengtsson & Yi (2003)** — "Timed Automata: Semantics, Algorithms and Tools" (UPPAAL)

## Veille

- **Conférences** : LICS (Logic in Computer Science), CAV (Computer Aided Verification), TACAS (Tools and Algorithms for Construction and Analysis of Systems), CONCUR (Concurrency Theory), POPL (Principles of Programming Languages), PLDI, ICALP, STTT (Software Tools for Technology Transfer)
- **Journaux** : Information and Computation, Theoretical Computer Science (TCS), Journal of the ACM (JACM), Logical Methods in Computer Science (LMCS), Formal Methods in System Design (FMSD), ACM Transactions on Computational Logic (TOCL)
- **ArXiv** : suivre `cs.FL`, `cs.LO`, `cs.SE`, `cs.PL`, `cs.CC`
- **Communautés** : EATCS (European Association for Theoretical Computer Science), ACM SIGLOG, IFIP WG 1.3 (Foundations of System Specification)
- **Logiciels/Outils (github)** : dernier commit de Spin, NuSMV/nuXmv, Z3Prover/z3, coq/coq, isabelle-prover, UPPAAL, PRISM, Tree-sitter, ANTLR
- **Blogs/Veille technique** : *The TCS Blog* (LiCS), *SMT-LIB* updates, *Coq-Club* mailing list, Isabelle users mailing list
