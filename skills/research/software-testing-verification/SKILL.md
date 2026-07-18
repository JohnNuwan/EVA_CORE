---
name: software-testing-verification
description: "Compétence en recherche en test et vérification de logiciels suivie sur arXiv sous cs.SE, cs.LO. Couvre le test automatisé, la vérification de modèles, l'exécution symbolique, le fuzzing, l'analyse statique, les oracles de test, la génération de cas de test, et la vérification de protocoles."
category: research
arxiv_categories:
  - cs.SE
  - cs.LO
  - cs.PL
  - cs.CR
lang: fr
---

# Compétence : Test et Vérification de Logiciels

## Présentation

Cette compétence couvre la veille de recherche en test et vérification de logiciels, avec un suivi régulier des publications sur arXiv dans les catégories cs.SE (Software Engineering) et cs.LO (Logic in Computer Science). Les domaines comprennent le test automatisé, l'exécution symbolique et concolique, la vérification de modèles, l'analyse statique, les oracles de test, le fuzzing, la vérification de protocoles, ainsi que l'application de l'IA aux techniques de test et vérification.

## Domaines de Recherche

### Test Automatisé
- **Génération de Tests** : génération automatique de cas de test, test basé sur des modèles, test par analyse syntaxique, test par analyse sémantique, test paramétré, test combinatorie
- **Test de Régression** : sélection de tests de régression, priorisation, minimisation, test de non-régression automatique, test de différence, delta debugging
- **Test d'Intégration** : test d'intégration de composants, test d'API, test de microservices, test de conteneurs, test d'orchestration, test d'intégration continue
- **Test de Systèmes** : test de bout en bout, test de performance, test de charge, test de stress, test de sécurité, test d'acceptation
- **Test de Mutations** : mutants, critères de mutation, mutant killing, mutation forte/faible, mutation syntaxique/sémantique
- **Test d'Intelligence Artificielle** : test de modèles ML, test de robustesse adversarial, test d'équité, test d'explicabilité, test de modèles LLM
- **Test par Propriétés (Property-Based Testing)** : QuickCheck/Hypothesis, génération aléatoire, shrinking, contrats, invariants

### Exécution Symbolique et Concolique
- **Exécution Symbolique** : exécution symbolique classique, symbolic paths, path constraints, path explosion, symbolic execution avec SMT
- **Exécution Concolique** : exécution concrète-symbolique, DART, CUTE, KLEE, angr, S2E, Driller, Mayhem
- **SMT Solvers** : Z3, CVC5, Yices, dReal, Bitwuzla, théories SMT (QF_BV, QF_LIA, QF_UF, strings, reals, floating-point)
- **Contraintes** : résolution de contraintes, simplification, réécriture, théorie des modèles pour SMT, solving de contraintes mixtes
- **Path Exploration** : stratégies d'exploration (DFS, BFS, coverage-guided, random), guidance par l'apprentissage, sélection de branche
- **Exécution Symbolique pour Programmes Complexes** : exécution symbolique modulaire, compositionnelle, inter-procédurale, pour programmes concurrents, pour programmes distribués
- **Limitations et Extensions** : path explosion, interaction avec l'environnement, modélisation de l'environnement, exécution symbolique sous-contrainte

### Vérification de Modèles (Model Checking)
- **Model Checking** : vérification exhaustive de modèles, automates, CTL (Computation Tree Logic), LTL (Linear Temporal Logic), CTL*, mu-calcul
- **LTL** : logique temporelle linéaire, opérateurs temporels, sémantique, automates de Büchi, model checking LTL
- **CTL** : logique arborescente, opérateurs de chemin, sémantique des arbres de calcul, algorithme de model checking CTL
- **SPIN** : vérificateur SPIN, Promela, vérification à la volée, réduction par ordre partiel, BFS/DFS, vérification on-the-fly
- **NuSMV** : NuSMV et nuXmv, SMV langage, vérification symbolique, BDD, SAT-based model checking (IC3, PDR), bounded model checking
- **Model Checking Symbolique** : BDD, diagrammes de décision binaires, SAT-based BMC (Bounded Model Checking), IC3/PDR
- **Model Checking Statistique** : SMC, Monte Carlo, échantillonnage, vérification statistique, vérification probabiliste
- **Vérification de Systèmes Concurrents** : interleaving, deadlock, race condition, mémoire transactionnelle, modèles de mémoire, réduction d'ordre partiel
- **Model Checking de Logiciels** : abstraction de prédicats, CEGAR, SLAM, BLAST, CPAchecker, SeaHorn

### Analyse Statique
- **Linting et Style** : analyse de code statique, linting (ESLint, Pylint, Clang-Tidy), conventions de code, refactoring automatique
- **Détection de Bugs** : null pointer dereference, buffer overflow, use-after-free, memory leak, division by zero, integer overflow, race condition
- **Analyse de Flot** : data-flow analysis, control-flow analysis, points-to analysis, alias analysis, escape analysis, constant propagation, reaching definitions, live variables, available expressions, very busy expressions
- **Null-Safety** : analyse de nullabilité, annotations @Nullable/@NonNull, Option/Maybe, analyse de flux de null, Kotlin null safety, Swift optionals
- **Abstract Interpretation** : interprétation abstraite, treillis, posts, points fixes, widening/narrowing, domaines abstraits (intervalles, polyèdres, octogones, signes)
- **Analyse de Sécurité** : taint analysis, analysis de flux d'information, analyse de permissions, analyse de vulnérabilités, SAST (Static Application Security Testing)
- **Analyse Compositionnelle** : analyse modulaire, contrats de fonction, résumé, analyse inter-procédurale, frameworks de résumé

### Oracles de Test
- **Test Oracles** : définition d'oracle, oracle parfait, oracle humain, oracle automatique, oracle de métamorphose
- **Metamorphic Testing** : relations métamorphiques, MT (Metamorphic Testing) pour l'IA, MT pour systèmes embarqués, MT pour réseaux, MT pour services web, métamorphic relations discovery
- **Test Oracle AI** : oracles par apprentissage, modèles de prédiction de sortie, oracles par IA générative, oracles par LLM
- **LogicHunter** : oracle de test basé sur LLM pour les frameworks d'agents IA, détection de bugs logiques dans les piles d'IA agentique, test de chaînes d'outils LLM
- **Oracles par Contrat** : assertions, Design by Contract (Eiffel, JML), pré/post-conditions, invariants, contrats pour langages modernes
- **Oracles par Différence** : différentiel, comparaison de versions, test de régression, test de non-régression visuelle

### Fuzzing et Découverte de Bugs
- **Coverage-Guided Fuzzing** : fuzzing guidé par couverture, AFL (American Fuzzy Lop), libFuzzer, Honggfuzz, coverage maximization, corpus minimization, feedback-driven fuzzing
- **Grammar-Based Fuzzing** : fuzzing par grammaire, génération de programmes, fuzzing de protocoles, fuzzing d'APIs REST, fuzzing d'entrées structurées
- **AFL** : instrumentation AFL, fork server, bitmap de couverture, evolution du corpus, AFL++, AFLFast, AFLGo, AFL-based fuzzing
- **libFuzzer** : fuzzing in-process, SanitizerCoverage, libFuzzer avec sanitizers (ASan, UBSan, MSan, TSan, LSan, CFI)
- **Hybrid Fuzzing** : combinaison fuzzing + exécution symbolique, Driller, QSYM, DigFuzz, hybrid concolic fuzzing
- **Fuzzing de Programmes** : fuzzing d'exécutables, binaires, fuzzing de systèmes, fuzzing de kernel, fuzzing de drivers, fuzzing natif
- **Fuzzing de Sécurité** : fuzzing pour vulnérabilités zero-day, fuzzing de navigateurs, fuzzing d'OS, fuzzing de protocoles réseau, fuzzing de cryptographie
- **Fuzzing pour l'IA** : fuzzing de modèles ML, adversarial fuzzing, fuzzing de LLM, fuzzing de systèmes agentiques

### Vérification de Protocoles et Sécurité
- **Vérification Formelle de Protocoles** : protocoles de sécurité, protocoles cryptographiques, protocol state machines, invariants de protocole
- **ProVerif / Tamarin** : vérification automatique de protocoles par ProVerif (calcul de processus), Tamarin (théorie d'équations), ACME, Dolev-Yao
- **Sécurité des Protocoles Réseau** : TLS 1.3, SSH, IPsec, WireGuard, QUIC, Signal Protocol, OAuth 2.0, OIDC, protocoles blockchain
- **Vérification de Smart Contracts** : vérification formelle de smart contracts (Solidity, Vyper), invariants, propriétés de sécurité, analyse statique, Slither, Solidity graph
- **Symbolic Model Checking de Protocoles** : model checking de protocoles à états finis/infinis, sized types, type-based verification, symbolic execution de protocoles

## Catégories arXiv Suivies

| Catégorie | Description |
|-----------|-------------|
| **cs.SE** | Software Engineering |
| **cs.LO** | Logic in Computer Science |
| **cs.PL** | Programming Languages |
| **cs.CR** | Cryptography and Security |

## Articles et Publications Clés

- **LogicHunter: Testing LLM Agent Frameworks** — oracle de test LLM pour la détection de bugs dans les frameworks d'agents IA
- **To Run or Not to Run** — ISSTA 2026, test et décision d'exécution pour infrastructures logicielles
- **CoCoMUT** — ISSTA 2026, test de mutations combinatoire pour systèmes complexes
- **Fuzzing: State of the Art** — IEEE Transactions on Software Engineering, survey des techniques de fuzzing
- **Model Checking at Microsoft** — applications industrielles du model checking

## Méthodologie de Veille

1. **Recherche hebdomadaire** sur arXiv dans les catégories listées ci-dessus
2. **Mots-clés prioritaires** : fuzzing, symbolic execution, model checking, static analysis, test oracle, metamorphic testing, SMT solver, LLM testing, coverage-guided fuzzing, verification, protocol verification, LogicHunter, concolic testing, software testing
3. **Conférences cibles** : ICSE, FSE/ESEC, ASE, ISSTA, PLDI, POPL, CAV, TACAS, VMCAI, SPIN, ICST, OOPSLA, SAS, LOPSTR
4. **Revues cibles** : ACM Transactions on Software Engineering and Methodology (TOSEM), IEEE Transactions on Software Engineering (TSE), Software Testing, Verification and Reliability (STVR), Formal Methods in System Design (FMSD)

## Ressources Associées

- [ArXiV cs.SE](https://arxiv.org/list/cs.SE/recent)
- [ArXiV cs.LO](https://arxiv.org/list/cs.LO/recent)
- [ArXiV cs.PL](https://arxiv.org/list/cs.PL/recent)
- [LLVM Fuzzing Resources](https://llvm.org/docs/LibFuzzer.html)
- [Symbolic Execution Resources (KLEE)](https://klee.github.io/)