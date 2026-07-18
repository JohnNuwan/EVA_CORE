---
name: aviation-aeronautics-ai
description: "Compétence niveau ingénieur/docteur en aviation et aéronautique computationnelles. Couvre aérodynamique ML, commandes de vol, systèmes embarqués avionique, maintenance prédictive aéronautique, optimisation de trajectoire, gestion du trafic aérien ATM, drones aviation, avions autonomes, et certification aéronautique DO-178C."
---

# Aviation et Aéronautique Computationnelles

## Présentation
Cette skill couvre l'intersection de l'intelligence artificielle, du machine learning et de l'ingénierie aéronautique. Elle s'adresse aux chercheurs et ingénieurs travaillant sur l'application de méthodes computationnelles avancées aux problèmes de conception, d'exploitation et de certification aéronautiques. Les domaines couverts incluent l'aérodynamique numérique, les systèmes embarqués critiques, la maintenance prédictive, la gestion du trafic aérien, les drones et les avions autonomes.

## Aérodynamique et CFD (Computational Fluid Dynamics)
- **Méthodes CFD** : Résolution des équations de Navier-Stokes (RANS, LES, DNS), solveurs OpenFOAM et SU2, méthodes de Volumes Finis et Éléments Finis
- **Mesh Refinement** : Raffinement de maillage adaptatif (AMR), maillage structuré/non-structuré, génération de maillage pour géométries complexes aéronautiques
- **Turbulence Modeling ML** : Modèles de turbulence améliorés par apprentissage profond (CNN, PINNs), correction de modèles RANS par ML, réduction d'ordre de modèle (ROM) pour CFD
- **Wing Optimization** : Optimisation de forme d'aile par adjoint continu/discret, optimisation multi-objectifs (portance/traînée), design d'aile transsonique, winglets, optimisation de profils par deep learning
- **Aeroacoustique** : Prédiction du bruit aérodynamique, méthodes Ffowcs Williams-Hawkings, réduction de bruit par optimisation géométrique

## Avionique et Systèmes Embarqués
- **Flight Control Systems** : Commandes de vol électriques (FBW), lois de commande, gain scheduling, commande robuste H∞, commande adaptative
- **ARINC 429/664** : Bus de données avionique, architectures AFDX, réseaux temps réel, protocoles de communication certifiés
- **DO-178C / DO-254** : Certification de logiciel et matériel aéronautique, niveaux de criticité (DAL A-E), processus de développement, vérification formelle
- **RTCA** : Standards RTCA DO-160 (environnement), DO-278 (systèmes au sol), DO-326 (cybersécurité)
- **Cockpit Systems** : Systèmes de visualisation, EFIS, glass cockpit, HUD, DAS, systèmes de navigation FMS, TCAS, EGPWS

## Maintenance Prédictive Aéronautique
- **Engine Health Monitoring (EHM)** : Surveillance des moteurs (turbines, compresseurs), analyse des vibrations, trend analysis, EGT margin, borescope inspection ML
- **APU Health** : Surveillance des groupes auxiliaires de puissance, cycles de démarrage, prédiction de défaillances
- **Fleet Management** : Gestion de flotte optimisée par ML, planification de maintenance, optimisation des intervalles, prognostics PHM
- **SHM Aéronautique** : Structural Health Monitoring, analyse de fatigue, détection de dommages par capteurs, CBM (Condition-Based Maintenance), analyse NDT par IA
- **CBM+** : Maintenance conditionnelle avancée, modèles de durée de vie résiduelle (RUL), prédiction de défaillances, PHM (Prognostics and Health Management)

## Trafic Aérien ATM (Air Traffic Management)
- **Sector Demand Prediction** : Prédiction de charge des secteurs de contrôle, prévision de trafic court/long terme, modèles spatio-temporels
- **Conflict Detection** : Détection et résolution de conflits aériens, modèles de séparation, ML pour l'anticipation de conflits, conformance monitoring
- **Flow Management (ATFM)** : Gestion des flux de trafic, régulation au sol (GDP), slot allocation, airspace configuration, collaborative decision-making (CDM)
- **Trajectory Optimization** : Optimisation de trajectoire 4D, trajectoires libre-service, User Preferred Routes, AI pour la planification de vol, optimisation multi-objectifs
- **SESAR / NextGen** : Programmes de modernisation ATM, système de gestion du trafic aérien paneuropéen, concepts de ciel unique, performance-based navigation (PBN), ADS-B

## Drones et eVTOL
- **Urban Air Mobility (UAM)** : Mobilité aérienne urbaine, gestion de flotte de taxis volants, vertiports, intégration urbaine
- **Delivery Drones** : Drones de livraison, optimisation de tournées, gestion de flotte B2B/B2C, last-mile delivery
- **BVLOS** : Opérations Beyond Visual Line of Sight, détection et évitement (DAA), senseurs pour drones, communications C2, command and control robuste
- **Vertiports** : Conception et gestion de vertiports, capacité, scheduling des décollages/atterrissages, recharge de batteries
- **Airspace Integration** : Intégration des drones dans l'espace aérien non-contrôlé et contrôlé, UTM (UAS Traffic Management), U-space européen

## Avions Autonomes
- **Autoland / Autoflight** : Systèmes d'atterrissage automatique (ILS, GLS, MLS), approche automatique, procédures de catégorie III, flare et decrab automatisés, Autoflight complet
- **Autonomous Taxi** : Roulage autonome, A-SMGCS, guidance au sol, détection d'obstacles sur tarmac
- **Single-Pilot Operations** : Opérations à pilote unique (SPO), réduction de charge de travail, assistance cognitive, redondance au sol via ground-based pilot
- **Autonomous Cargo** : Cargo autonome, certification d'avions cargo sans pilote, opérations de fret, conversion de flotte
- **Certification** : Certification d'avions autonomes, méthodes de vérification et validation, approches de certification basées sur les risques, EASA AI roadmap, FAA AI safety

## Catégories arXiv
- cs.RO (Robotics), cs.AI (Artificial Intelligence), cs.LG (Machine Learning), eess.SY (Systems and Control), physics.flu-dyn (Fluid Dynamics)

## Références Clés
- OpenFOAM User Guide, SU2 Documentation
- RTCA DO-178C / DO-254 Standards
- SESAR Joint Undertaking Publications
- EASA AI Roadmap for Aviation
- FAA Part 107 / Part 23 / Part 25 Regulations
- NASA UTM Project Publications
- Journal of Aircraft, IEEE Transactions on Aerospace and Electronic Systems
- Aerospace Science and Technology, Progress in Aerospace Sciences