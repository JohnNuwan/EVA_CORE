---
name: operations-research-management
description: "Compétence niveau ingénieur/docteur en recherche opérationnelle et sciences de gestion. Couvre l'optimisation linéaire/non-linéaire, la programmation stochastique, la simulation, la théorie des files d'attente, la gestion de la chaîne logistique, l'ordonnancement (scheduling), le revenue management, les supply chains, la planification de production, et le decision analysis."
category: research
tags: [operations-research, optimization, simulation, supply-chain, scheduling, revenue-management]
---

# Recherche Opérationnelle & Sciences de Gestion — Compétence Recherche

## Présentation

Cette compétence couvre l'état de l'art en recherche opérationnelle et sciences de gestion computationnelles, à destination d'ingénieurs et chercheurs. Domaines clés : optimisation, programmation stochastique, simulation, files d'attente, supply chain, scheduling, revenue management, decision analysis.

## Optimisation

- **LP (Linear Programming)** — simplex, points intérieurs, dualité
- **MILP (Mixed-Integer Linear Programming)** — branch-and-bound, branch-and-cut, cutting planes
- **QP / SOCP** — Quadratic Programming, Second-Order Cone Programming
- **Convex optimization** — optimisation convexe, SDP, applications ML
- **Gurobi** — solveur MILP haute performance, industrial standard
- **CPLEX** — solveur IBM, optimisation quadratique, constraint programming
- **SCIP** — solveur open source, branch-and-cut, MIP
- **OR-Tools (Google)** — framework CP-SAT, routing, network flow
- **Pyomo / JuMP** — langages de modélisation algébrique (Python, Julia)
- **Decomposition** — Benders, Dantzig-Wolfe, Lagrangian relaxation
- **Non-convex optimization** — optimisation globale, branch-and-reduce

## Programmation Stochastique

- **Two-stage stochastic programming** — recours simple, formulation extensive
- **Multi-stage stochastic programming** — arbres de décision multi-périodes
- **Scenario generation** — génération de scénarios, réduction, moment matching
- **SP models** — newsvendor stochastique, capacity planning, finance
- **Chance constraints** — contraintes probabilistes, Value-at-Risk, CVaR
- **Robust optimization** — optimisation robuste, incertitude bornée, ellipsoïdale
- **SDDP** — Stochastic Dual Dynamic Programming, hydroélectricité
- **Sample Average Approximation (SAA)** — approximation par échantillonnage

## Simulation

- **Discrete-event simulation (DES)** — processus stochastiques, événements discrets
- **Monte Carlo simulation** — échantillonnage aléatoire, variance reduction
- **Agent-based modeling (ABM)** — agents autonomes, emergence, systèmes complexes
- **AnyLogic** — plateforme multi-méthodes (DES + ABM + SD)
- **SimPy** — framework DES en Python
- **Arena / FlexSim** — logiciels de simulation industrielle
- **System Dynamics** — causal loop diagrams, stocks and flows, Vensim
- **Simulation optimization** — optimisation par simulation, response surfaces
- **Digital twin simulation** — jumeaux numériques pour simulation temps réel

## Théorie des Files d'Attente

- **Queueing theory** — modèles M/M/1, M/M/c, M/G/1, G/G/1
- **Queueing networks** — réseaux de files d'attente, produit-forme
- **Jackson networks** — réseaux ouverts à produit-forme, théorème de Jackson
- **Polling systems** — systèmes cycliques, applications IoT et réseaux
- **Applications** — télécommunications, manufacturing, call centers
- **Heavy traffic** — approximation Brownienne, Halfin-Whitt regime
- **Priority queues** — files prioritaires, preemption, HOL
- **Queueing game theory** — files stratégiques, pricing

## Supply Chain

- **Inventory optimization** — (s, S), (Q, r), periodic review, base stock
- **Newsvendor model** — problème du marchand de journaux, extensions multi-produits
- **Bullwhip effect** — effet coup de fouet, amplification de la variance
- **Facility location** — localisation d'entrepôts, p-median, p-center, coverage
- **Vehicle routing (VRP)** — tournées de véhicules, CVRP, VRPTW, VRPB
- **CVRP** — Capacitated Vehicle Routing Problem
- **VRPTW** — Vehicle Routing with Time Windows
- **Multi-echelon inventory** — stocks multi-échelons, supply chain design
- **Resilient supply chains** — robustesse, disruptions, reshoring
- **Green logistics** — supply chains durables, émissions, reverse logistics

## Scheduling

- **Job shop scheduling** — problème job shop, disjunctive graph, shifting bottleneck
- **Flow shop scheduling** — permutation, hybrid flow shop, makespan
- **Project scheduling** — PERT/CPM, resource-constrained project scheduling (RCPSP)
- **Resource-constrained** — ressources limitées, multi-modes, calendarization
- **Employee scheduling** — workforce scheduling, shift assignment, breaks
- **Parallel machine scheduling** — machines parallèles, Rm || Cmax
- **Open shop** — open shop scheduling, flexible manufacturing
- **Constraint programming** — CP-SAT, cumulative resource constraints

## Revenue Management

- **Dynamic pricing** — prix dynamique, écrémage, pénétration, markdown
- **Capacity control** — contrôle de capacité, Littlewood's rule, EMSR, bid prices
- **Overbooking** — gestion des surréservations, no-shows, cancellations
- **Yield management** — gestion de rendement, hôtellerie, transport aérien
- **Markdown optimization** — optimisation des démarques, retail pricing
- **Assortment optimization** — optimisation de l'assortiment, MNL, nested logit
- **Price elasticity** — estimation de l'élasticité-prix par ML
- **Customer segmentation** — segmentation clients pour pricing différencié

## Decision Analysis

- **MCDA (Multi-Criteria Decision Analysis)** — méthodes multi-critères
- **AHP (Analytic Hierarchy Process)** — hiérarchisation des critères, comparaisons par paires
- **MAUT (Multi-Attribute Utility Theory)** — théorie de l'utilité multi-attribut
- **Decision trees / Influence diagrams** — arbres de décision, valeur de l'information
- **ELECTRE / PROMETHEE** — méthodes de surclassement, outranking
- **TOPSIS / VIKOR** — méthodes de compromis, ranking alternatives
- **Portfolio optimization** — optimisation de portefeuille, Markowitz, Sharpe
- **Risk analysis** — analyse de risque, minmax, regret, sensitivity

## Catégories arXiv

- math.OC (Optimization and Control)
- cs.DS (Data Structures and Algorithms)
- cs.GT (Computer Science and Game Theory)
- cs.AI (Artificial Intelligence)
- econ.EM (Econometrics)
- stat.ML (Machine Learning)

## Conférences et Journaux Clés

- INFORMS Journal on Computing
- Operations Research (INFORMS)
- Management Science
- Mathematical Programming (A/B)
- European Journal of Operational Research (EJOR)
- INFORMS Annual Meeting
- CPAIOR / ICAPS — scheduler conferences
- TRO / TSL (Transportation Science)

## Ressources et Outils

- **Gurobi / CPLEX / SCIP / HiGHS** — solveurs optimisation
- **OR-Tools (Google)** — CP-SAT, routing
- **Pyomo / JuMP** — modeling languages (Python/Julia)
- **SimPy / AnyLogic** — simulation
- **LEMON / NetworkX** — graph algorithms
- **OR-Library / MIPLIB / TSPLIB** — benchmarks
- **NEOS Server** — optimisation à distance
- **COIN-OR** — open source OR ecosystem

## Articles de Référence

- **The Newsvendor Problem** — article fondateur, extensions modernes
- **Vehicle Routing: 65 years** — revue complète des variantes VRP
- **CP-SAT (Google OR-Tools)** — benchmark et algorithmes modernes
- **Stochastic Programming** — Birge & Louveaux (1997), manuel de référence