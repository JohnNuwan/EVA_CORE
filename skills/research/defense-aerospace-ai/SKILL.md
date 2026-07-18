---
name: defense-aerospace-ai
description: "Compétence niveau ingénieur/docteur en IA pour la défense et l'aérospatial. Couvre drones autonomes, systèmes d'armes, C4ISR, simulation militaire, space systems, satellite AI, missile defense, cyber warfare, electronic warfare, et dual-use AI."
category: research
tags: [defense, aerospace, drones, C4ISR, cyber-warfare, satellite, autonomous-systems, military-simulation, dual-use]
arxiv_categories: [cs.RO, cs.CR, cs.AI, cs.CY, eess.SY]
---

# Compétence : IA pour la Défense et l'Aérospatial (Defense & Aerospace AI)

## Présentation

Cette compétence de niveau ingénieur/docteur couvre l'application de l'intelligence artificielle aux domaines de la défense nationale et des systèmes aérospatiaux. Elle embrasse les systèmes autonomes (drones, swarm robotics), le C4ISR (Command, Control, Communications, Computers, Intelligence, Surveillance, Reconnaissance), la simulation militaire multispectre, les systèmes spatiaux, la guerre électronique et informatique, ainsi que les cadres éthiques et juridiques des systèmes d'armes autonomes.

---

## 1. Drones Autonomes et UAS (Unmanned Aircraft Systems)

### Swarm Drones
- **Algorithmes de vol en essaim** : flocking (Reynolds Boids), consensus protocol, formation control, collision avoidance (ORCA, VO).
- **Multi-Agent Reinforcement Learning (MARL)** : CTDE (Centralized Training Decentralized Execution), MAPPO, QMIX, VDN, COMA.
- **Application** : ISR distribué, relay communication, saturation attack, coordinated target tracking.
- **Delay-Aware MARL pour Counter-UAS (IROS 2026)** : méthodes RL tenant compte des délais de communication dans la neutralisation d'essaims adverses. Prise en compte de la latence réseau, buffering temporaire, prédiction d'état retardé.

### Autonomie Tactique
- **BVLOS (Beyond Visual Line of Sight)** : navigation autonome sans pilote visuel, sense-and-avoid, detect-and-avoid (DAA) sous DO-365.
- **Niveaux d'autonomie (SAE / DoD)** : L1 (téléopéré) → L5 (autonomie totale) — décision tactique, mission planning dynamique.
- **Hardware** : Pixhawk/ArduPilot, PX4, ROS 2, Mavlink protocol.

### Contre-UAS (CUAS)
- **Détection** : radar, RF sensing, EO/IR camera, acoustic arrays, fusion multimodale.
- **Neutralisation** : jamming RF, GNSS spoofing, kinetic interceptors (drone-net, laser DEW, projectile), cyber take-over.
- **AI-driven** : classification adversaire/reconnaissance, prédiction de trajectoire, décision de neutralisation.

---

## 2. C4ISR (Command, Control, Communications, Computers, Intelligence, Surveillance, Reconnaissance)

### Fusion de Données
- **JDL Data Fusion Model** : niveaux 0–5 (sub-object → estimation → impact → refinement).
- **Kalman & Particle Filters** : tracking multi-cible, fusion hétérogène (radar, EO/IR, SIGINT), track-to-track fusion.
- **Bayesian & Dempster-Shafer** : incertitude, conflit de capteurs, fusion avec ignorance.

### Battle Management
- **Decision Support Systems** : course of action (COA) analysis, wargaming automatisé, OODA loop (Observe-Orient-Decide-Act).
- **C2 Systems** : COP (Common Operating Picture), blue-force tracking, red-force estimation, NCTI (Non-Cooperative Target Identification).
- **NATO C2 Taxonomy** : niveau stratégique, opératif, tactique — C2 Approach Maturity Model.

### Intelligence & Reconnaissance
- **SIGINT (Signals Intelligence)** : COMINT (communications), ELINT (electronic), FISINT (foreign instrumentation), classification automatique des signaux, emitter geolocation.
- **GEOINT (Geospatial Intelligence)** : satellite imagery analysis, change detection, automated target recognition (ATR).
- **MASINT (Measurement & Signature Intelligence)** : radar signatures, acoustic signatures, seismic, magnetic, nuclear radiation.

---

## 3. Simulation Militaire (Military Simulation)

### Plateformes de Simulation
- **OneSAF (One Semi-Automated Forces)** : simulation constructive modulaire, comportements de combat, CGF (Computer Generated Forces), M&S interoperability.
- **VR-Forces (VT MAK)** : simulation constructive tactique, DIS/HLA protocol, terrain server, behaviour authoring.
- **AFSIM (Advanced Framework for Simulation, Integration & Modeling)** : framework USAF pour analyse de mission, modélisation de systèmes, scénarios multi-domaine.
- **STK (Systems Tool Kit, AGI/Ansys)** : simulation orbitale, propagation, accès satellites, chaine de communication, jam analysis.

### Battle Labs
- **Modeling & Simulation (M&S)** : constructive, virtual, live — HLA (IEEE 1516), DIS (IEEE 1278), TENA.
- **Mission Planning** : route optimization, threat avoidance, fuel/weapon constraints, time-on-target.
- **Digital Twin** : système réel jumelé pour maintenance prédictive, entraînement, test d'algorithme.

### Wargaming & Automated Adversaries
- **Adversarial AI en simulation** : red team automatisé, blue team AI, course of action scoring.
- **Monte Carlo wargaming** : distribution probabiliste des engagements, pertes, logistique.

---

## 4. Systèmes Spatiaux (Space Systems)

### Satellite Tasking & Operations
- **AI pour scheduling satellite** : optimisation multi-objectif (science, defense, commercial), contraintes ressources, contraintes orbitales, visibilité sol.
- **Edge AI embarqué** : FPGA/ASIC pour inference à bord, compression modèle, transfer learning embarqué.
- **Constellation Management** : Starlink/GPS/etc. — swarm coordination, inter-satellite links (ISL), lasercom, slot allocation.

### Orbital Machine Learning
- **Prédiction orbitale** : ML pour propagation orbitale, SGP4/SDP4 amélioré par réseaux de neurones, atmospheric drag modelling.
- **Space Situational Awareness (SSA)** : RSO (Resident Space Object) tracking, classification (débris vs actif), maneuver detection, uncorrelated track resolution.
- **Débris Avoidance** : collision probability estimation, covariant analysis, automated CDM (Conjunction Data Message) processing, STM (State Transition Matrix).

### Missile Defense
- **Kill Chain & Sensor Fusion** : early warning (SBIRS, HBTSS), mid-course discrimination (lethals vs decoys), terminal engagement.
- **AI for Discrimination** : target signature classification, TBM/ICBM discrimination complexe, countermeasure evaluation.
- **THAAD / Patriot / Arrow / Iron Dome** : architecture battlement, AI-aided threat prioritization.

---

## 5. Cyber Warfare (Guerre Informatique)

### Offensive Cyber
- **Penetration Testing Autonome** : Strix AI (38k+ GitHub stars) — framework AI-driven penetration testing, automated vulnerability discovery, exploitation chaining.
- **Adversarial ML for Cyber** : évasion de détection, adversarial examples pour IDS/IPS, polymorphic malware generation, command & control evasion.
- **Autonomous Red Teaming** : reinforcement learning pour prise de décision offensive, privilege escalation automatisée, lateral movement.

### Defensive Cyber
- **Intrusion Detection (ML)** : réseau neuronal pour NIDS, host-based IDS, anomaly detection sur logs système et réseau, graph-based attack detection.
- **Active Defense** : honeypots intelligents, cyber deception, moving target defense, adaptive firewall.
- **Threat Intelligence** : TTP extraction automatique, MITRE ATT&CK mapping automatique, kill chain analysis, indicator of compromise (IoC) enrichment.

### Electronic Warfare (EW)
- **AI for Jamming** : cognitive electronic warfare, reinforcement learning pour selection de fréquence, adaptive jamming, LPI (Low Probability of Intercept) radar.
- **Signals Classification** : AMC (Automatic Modulation Classification), spécifique mil-std (Link 11/16/22, JTRS, SINCGARS, HAVE QUICK).
- **EW Battle Management** : spectrum situational awareness, deconfliction amis-adversaires, intelligent frequency hopping.

---

## 6. Dual-Use AI & Ethics (IA Dual-Use et Éthique)

### AI in Weapons Systems
- **Lethal Autonomous Weapons Systems (LAWS)** : définition CCW/GGE des systèmes d'armes létaux autonomes, meaningful human control (MHC), human-on-the-loop vs human-in-the-loop.
- **Autonomie dans la boucle de décision** : fire control autonomy, weapon release authority, target identification & engagement.
- **Dilemmes éthiques** : accountability gaps, trolley problem in warfare, proportionality, distinction, military necessity (DIH).

### Cadres Juridiques
- **Conventions de Genève & DIH** : principe de distinction, de proportionnalité, de précaution (Article 36 du Protocole I).
- **AI in Warfare & International Humanitarian Law** : Customary IHL study, Martens clause, ICRC position on autonomous weapons.
- **Dual-Use AI Ethics** : US DoD AI Ethical Principles (2020), EU Military AI guidelines, UNODA, CCW/GGE discussions.

### Governance
- **Human-on-the-Loop Architecture** : levels of human supervision, veto power, fail-deadly/fail-safe design.
- **AI Auditing in Defense** : certification des systèmes d'armes intelligents, red teaming éthique, assurance algorithmique.
- **NATO AI Strategy** : principles of responsible use, interoperability, data governance, AI assurance for operations.

---

## Références et Lectures

- **IROS 2026** : *Delay-Aware Multi-Agent Reinforcement Learning for Counter-UAS Operations*.
- **Strix AI** : *Autonomous Penetration Testing Framework* (38k+ stars GitHub).
- **ArXiv** : cs.RO (Robotics), cs.CR (Cryptography/Security), cs.AI, cs.CY (Computers & Society), eess.SY (Systems & Control).
- **RAND Corporation** : rapports sur l'IA dans la défense, autonomous systems assessment.
- **CNA Corporation / CSIS** : analyses stratégiques AI défense.
- **MIT Lincoln Laboratory / DARPA ACE** : programme AI for air combat, autonomous dogfighting.
- **US Department of Defense** : *Summary of the 2023 DoD AI Adoption Strategy*, *Autonomy in Weapon Systems (DoDD 3000.09)*.
- **NATO Science & Technology Organization** : rapports AI, TRL (Technology Readiness Levels).