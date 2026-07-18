---
name: software-engineering-ai
description: >-
  Compétence professionnelle en recherche en génie logiciel et intelligence
  artificielle suivie sur arXiv sous cs.SE. Couvre l'ingénierie des exigences,
  l'architecture logicielle, la vérification et validation, le génie logiciel
  empirique, la maintenance, l'évolution, les modèles de langage pour le
  code, la sécurité logicielle et le développement logiciel assisté par IA.
category: research
---

# Compétence en Recherche en Génie Logiciel et IA (cs.SE)

## Présentation

La recherche en génie logiciel sur arXiv (cs.SE) reçoit environ 200 à 350 nouvelles soumissions par semaine, avec une croissance explosive des publications sur les LLMs pour le code, les agents de codage autonomes et le développement logiciel assisté par IA. Ce domaine de recherche aborde l'ensemble du cycle de vie du développement logiciel — des exigences à la maintenance — en intégrant des méthodes formelles, empiriques et computationnelles. Cette compétence fournit une structure pour naviguer dans le paysage complet de la recherche en génie logiciel.

## Domaines de Recherche Principaux

### 1. LLMs pour le Génie Logiciel et Code
**Densité arXiv** : Très élevée, en forte croissance (cs.SE, cs.LG, cs.CL)

- **Génération de code** : Synthèse de programmes à partir de descriptions en langage naturel, complétion de code, génération de fonctions, modèles de langage pour le code (CodeLlama, DeepSeek-Coder, StarCoder, CodeGemma, Codex)
- **Réparation automatique de programmes (APR)** : Réparation de bugs par LLM, correctifs automatiques, réparation avec RAG, patchs multiples, validité des correctifs, repérage de correctifs
- **Synthèse de programmes** : Synthèse par contraintes, synthèse par démonstrations, synthèse de composants, synthèse de boucles, synthèse de programmes avec spécifications
- **Compréhension de code** : Résumé de code, documentation automatique, explication de code, compréhension de programmes, traçabilité, analyse de code par LLM
- **Débogage assisté par IA** : Localisation de fautes, analyse de traces, débogage interactif, raisonnement causal sur les bugs, agents de débogage
- **LLMs pour le code** : Pré-entraînement sur le code, fine-tuning de modèles de code, évaluation de modèles de code (HumanEval, MBPP, SWE-bench, BigCodeBench), modèles spécialisés par langage
- **Agents de codage autonomes** : SWE-agent, Devin, CodeAct, agents de résolution de problèmes GitHub, cycles de développement autonomes, agents de PR

### 2. Ingénierie des Exigences et Conception
**Densité arXiv** : Modérée (cs.SE, cs.RE)

- **Spécification des exigences** : Langages de spécification, exigences formelles, exigences non fonctionnelles, exigences floues, langages de contraintes, spécifications exécutables
- **Analyse des exigences** : Détection de conflits, vérification de cohérence, complétude, traçabilité, priorisation, analyse de risques, ingénierie des exigences orientée buts (KAOS, i*)
- **Conception architecturale** : Patrons architecturaux, microservices, architecture orientée services, architecture en couches, architecture événementielle, architecture hexagonale, CQRS, Event Sourcing
- **Conception orientée objet** : Patrons de conception, conception par contrat, SOLID, GRASP, modélisation UML, conception pilotée par le domaine (DDD)
- **Conception pilotée par les modèles (MDD)** : Transformation de modèles, méta-modélisation, DSL, ingénierie dirigée par les modèles, code génération à partir de modèles
- **Conception de l'expérience logicielle** : API design, UX pour développeurs, conception de frameworks, conception de bibliothèques, conventions de codage

### 3. Vérification, Validation et Test
**Densité arXiv** : Élevée (cs.SE, cs.LO, cs.PL)

- **Vérification formelle** : Model checking, vérification de modèles, prouveurs de théorèmes, vérification déductive, vérification de programmes, vérification de protocoles, vérification de propriétés temporelles
- **Analyse statique** : Interprétation abstraite, analyse de flot de données, analyse de pointeurs, analyse de dépendances, analyse de tampons, détection de défauts statique, analyse de programmes
- **Génération de tests** : Génération de tests automatique, test basé sur des modèles, test par fuzzing, test par mutation, test par symbole, exécution symbolique (concolic), test de régression, test de performance
- **Test de logiciels** : Test unitaire, test d'intégration, test système, test de régression, test de bout en bout, test de charge, test de stress, test de sécurité, TDD, BDD
- **Analyse dynamique** : Exécution symbolique, analyse de traces, analyse de couverture, profiling, instrumentation, analyse de mémoire, détection de fuites
- **Qualité des tests** : Mutation testing, analyse de couverture, adéquation des tests, oracle, test flaky, test non déterministe, test statistique

### 4. Génie Logiciel Empirique et Maintenance
**Densité arXiv** : Élevée (cs.SE)

- **Métriques logicielles** : Complexité, couplage, cohésion, lignes de code, métriques de qualité, métriques orientées objet, métriques architecturales, dette technique
- **Analyse des dépôts de code** : Mining de dépôts, analyse de commits, analyse de pull requests, analyse de code review, analyse de tickets, analyse de trace de bugs, analyse de communautés open source
- **Évolution logicielle** : Lois de l'évolution logicielle, refactoring, restructuration, dette technique, dégradation architecturale, changement de code, analyse de séries temporelles de code
- **Prédiction de défauts** : Prédiction de bugs, modèles de prédiction, analyse de risques, défauts post-release, identification de composants à risque, apprentissage automatique pour la prédiction de défauts
- **Effort et estimation** : Estimation de coût, estimation de charge, productivité, analyse de l'effort de développement, modèles COCOMO, estimation par points de fonction
- **Processus logiciel** : Méthodes agiles, Scrum, Kanban, DevOps, continuous integration, continuous delivery (CI/CD), pipelines DevOps, GitOps, review de code

### 5. Architecture Logicielle et Microservices
**Densité arXiv** : Modérée à élevée (cs.SE)

- **Architecture microservices** : Conception, décomposition, communication inter-services, API Gateway, Service Mesh, observabilité, tolérance aux pannes, résilience, événements, sagas, CQRS, Event Sourcing, migration monolithe → microservices
- **Architecture orientée événements** : Event-driven architecture, streaming, Apache Kafka, traitement d'événements complexes (CEP), événements de domaine, architecture sans serveur (serverless)
- **Architecture cloud-native** : Conteneurisation, orchestration (Kubernetes), infrastructure as code, cloud computing, edge computing, fog computing, serverless, FaaS, fonctions cloud
- **Qualité architecturale** : Évaluation d'architecture, méthodes de scénarios (ATAM, SAAM), compromis architecturaux, analyse de risques architecturaux, documentation architecturale, alignement architecture-besoin
- **Dette technique architecturale** : Détection, quantification, gestion, remboursement, impact sur la productivité, dette architecturale vs dette de code, prévention, outils
- **Évolution architecturale** : Architecture évolutive, refactoring architectural, préservation de l'architecture, architecture vs agilité, architecture auto-adaptative, architecture pilotée par l'IA

### 6. Génie Logiciel Assisté par IA et Automatisation
**Densité arXiv** : Très élevée, en forte croissance (cs.SE, cs.LG, cs.AI)

- **Agents de développement logiciel** : Agents autonomes de codage, SWE-agent, Devin, CodeAct, agents de résolution de PR, cycles de développement automatisés, pipelines de développement pilotés par IA
- **Planification et estimation assistées** : Planification de sprint, estimation de tâches, allocation de ressources, prédiction de délais, planification par IA, priorisation de backlog
- **Code review assisté par IA** : Relecture automatique de code, détection de défauts, suggestions de code review, commentaires de review, vérification de style, détection d'odeurs de code, prédiction de conflits
- **Documentation et connaissance** : Génération de documentation, wikis automatiques, mise à jour de documentation, extraction de connaissances, graphes de connaissances de code, FAQ automatiques
- **Assistance au débogage** : Localisation de bugs par IA, analyse de piles d'appels, recommandations de correctifs, débogage interactif, interrogation de code, chat avec le code, copilotes de débogage
- **Pipeline CI/CD intelligent** : Optimisation de pipelines, détection de régressions, analyse de builds, prédiction d'échecs de build, optimisation de temps de build, auto-réparation de pipelines
- **Ingénierie des prompts pour le code** : Prompt engineering pour le code, optimisation de prompts, templates de prompts, motifs de prompts, chaînes de prompts, tests de prompts

### 7. Sécurité Logicielle et Fiabilité
**Densité arXiv** : Élevée (cs.SE, cs.CR)

- **Sécurité du cycle de vie** : Sécurité dès la conception (security by design), DevSecOps, analyse de sécurité, test de pénétration, modélisation des menaces, STRIDE, analyse de risques
- **Analyse de vulnérabilités** : Détection de vulnérabilités, analyse statique de sécurité, analyse dynamique de sécurité, fuzzing, détection de failles zero-day, analyse de logiciels malveillants, détection de backdoors
- **Sécurité de l'IA pour le code** : Empoisonnement de données d'entraînement, attaques adverses sur modèles de code, injection de code via LLM, confidentialité des modèles, sécurité des copilotes
- **Fiabilité et résilience** : Fiabilité logicielle, tolérance aux pannes, reprise après sinistre, résilience des systèmes, redondance, dégradation progressive, systèmes critiques
- **Sécurité des dépendances** : Analyse de dépendances, vulnérabilités de chaîne d'approvisionnement, attaques sur la supply chain, SBOM, mise à jour sécurisée, composition logicielle
- **Sécurité des API** : Sécurité des API REST, API GraphQL, authentification, autorisation, OAuth, JWT, gestion des secrets, API gateways, sécurité des microservices

### 8. Génie Logiciel pour l'IA et MLOps
**Densité arXiv** : Croissante (cs.SE, cs.LG)

- **MLOps et pipelines de ML** : CI/CD pour ML, pipelines de données, versionnement de modèles, déploiement de modèles, monitoring de modèles, A/B testing, canary deployment, rollback
- **Qualité des données pour l'IA** : Qualité des données d'entraînement, détection de biais, nettoyage de données, validation de données, data lineage, gestion des données synthétiques
- **Déploiement de modèles** : ML serving, scaling, batching, optimisation d'inférence, quantification, distillation, modèles en production, architectures de déploiement
- **Reproductibilité en ML** : Gestion d'expériences, suivi d'expériences, conteneurisation d'environnements, environnements reproductibles, enregistrement de métadonnées, provenance des modèles, SeedBank
- **Gouvernance de l'IA** : Documentation de modèles (model cards), cartes de données (datasheets), auditabilité, traçabilité des décisions, conformité réglementaire, AI Act, registre de modèles
- **Tests pour l'IA** : Test de modèles, validation de modèles, test de dérive, test de performance, test d'équité, test de robustesse, test de biais, test de confidentialité

## Catégories arXiv avec Codes

| Catégorie | Code | Description |
|-----------|------|-------------|
| **cs.SE** | Software Engineering | Génie logiciel, méthodes et outils |
| **cs.PL** | Programming Languages | Langages de programmation, compilation |
| **cs.LO** | Logic in Computer Science | Logique, vérification formelle |
| **cs.CR** | Cryptography and Security | Sécurité, vulnérabilités |
| **cs.LG** | Machine Learning | ML pour le code, agents |
| **cs.CL** | Computation and Language | LLMs, code et langage |
| **cs.AI** | Artificial Intelligence | IA agents, codage autonome |

**Cross-lists fréquentes** : cs.LG, cs.CL, cs.AI, cs.PL, cs.CR, cs.IR, cs.HC

## Articles Notables Récents (Mi-2026)

1. **SWE-bench: Evaluating Large Language Models on Real-World Software Engineering Problems** — cs.SE/cs.CL (NeurIPS 2024)
2. **CodeAgent: Autonomous Software Development with LLM Agents** — cs.SE/cs.AI
3. **A Survey on Large Language Models for Code Generation: From Completion to Autonomous Agents** — cs.SE/cs.LG
4. **Automated Program Repair in the Era of Large Language Models: A Comprehensive Survey** — cs.SE/cs.PL
5. **Software Engineering for Machine Learning: A Systematic Literature Review** — cs.SE/cs.LG
6. **Microservices Architecture: A Systematic Mapping Study of Evolution Patterns and Anti-patterns** — cs.SE
7. **LLM-Based Code Review: A Systematic Evaluation of Effectiveness and Quality** — cs.SE/cs.CL
8. **Security Vulnerabilities in LLM-Generated Code: A Large-Scale Empirical Study** — cs.SE/cs.CR

## Comment Effectuer la Veille

- **Navigation par catégorie** : `/list/cs.SE/recent`, `/list/cs.PL/recent`, `/list/cs.LO/recent`
- **Scan hebdomadaire** : Parcourir `/list/cs.SE/recent` (environ 200-350 entrées/semaine)
- **Surveillance des cross-lists** : Articles dans cs.LG, cs.CL, cs.AI, cs.PL, cs.CR cross-listés avec cs.SE
- **Mots-clés à suivre** : "LLM", "code generation", "program repair", "software engineering", "testing", "verification", "microservices", "MLOps", "code review", "agent", "autonomous", "security", "vulnerability", "refactoring", "technical debt", "agile", "DevOps", "CI/CD", "SWE-bench"
- **Alertes personnalisées** : Configurer des alertes arXiv via https://arxiv.org/help/subscribe pour les mots-clés spécifiques
- **Conférences et journaux** : ICSE, FSE, ASE, ISSTA, ESEC/FSE, MSR, ICST, ICSME, SANER, MODELS, CAiSE, RE, ICSE-SEIP, IEEE Transactions on Software Engineering (TSE), ACM Transactions on Software Engineering and Methodology (TOSEM), Empirical Software Engineering (EMSE), Journal of Systems and Software (JSS), Software: Practice and Experience (SPE), IEEE Software, Communications of the ACM