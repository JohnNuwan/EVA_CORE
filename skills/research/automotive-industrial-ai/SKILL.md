---
name: automotive-industrial-ai
description: "Compétence niveau ingénieur/docteur en IA pour l'automobile et l'industrie. Couvre véhicules autonomes (perception, planification, contrôle), systèmes ADAS, simulation (CARLA, SUMO, AirSim, NVIDIA Drive), datasets autonomes (nuScenes, Waymo, KITTI, Argoverse), industrie 4.0 (digital twin, IIoT, predictive maintenance), et normes (ISO 26262, AUTOSAR, MISRA)."
category: research
tags: [vehicules-autonomes, adas, simulation, industrie-4.0, digital-twin, iiot, normes-automobile]
---

# IA pour l'Automobile et l'Industrie — Référence Ingénieur/Docteur

## Présentation

Ce skill couvre l'ensemble des domaines d'application de l'IA dans l'industrie automobile et la fabrication intelligente. Conçu pour un niveau ingénieur/docteur, il traite des véhicules autonomes (perception, planification, contrôle end-to-end), des simulateurs, des datasets de conduite autonome, de l'industrie 4.0 (digital twin, IIoT, maintenance prédictive), et des normes réglementaires.

---

## 1. Véhicules Autonomes

### Perception (Waymo, Tesla, NVIDIA)
- **Détection d'objets** : 3D object detection (LiDAR, camera, radar fusion)
- **Segmentation** : Semantic, instance, panoptic segmentation
- **Suivi** : Multi-object tracking (MOT), sort, deep sort
- **Prédiction** : Trajectory prediction, intention, motion forecasting
- **Approches** :
  - **Waymo** : Perception multi-capteurs, BEV (Bird's Eye View), transformers
  - **Tesla** : Vision-only (8 cameras, occupancy network, HydraNet)
  - **NVIDIA** : DriveWorks, DriveIX, perception SDK
- **Modèles clés** : BEVFormer, PETR, DETR3D, CenterPoint, VoxelNet, PointPillar

### End-to-End Driving
- **Approche** : Perception → Planning → Control en un seul réseau
- **UniAD** (OpenDriveLab) : Unified Autonomous Driving — planification, motion, tracking, mapping
- **VAD** (Vector Autonomous Driving) : Vectorized scene representation
- **DeepRoute** : End-to-end model, planning latent
- **InterDrive** : Interaction-aware driving
- **ST-P3** : Spatial-temporal feature learning
- **Methods** : Imitation learning, behavior cloning, RL, cost volume

### Planning & Control
- **Motion Planning** : RRT*, A*, Hybrid A*, Lattice planner
- **Trajectory Optimization** : MPC (Model Predictive Control), ILQR
- **Behavior Planning** : Rule-based, learning-based, POMDP
- **Control** : PID, LQR, MPC, adaptive control
- **Frameworks** :
  - **Apollo (Baidu)** : Open-source, perception → planning → control
  - **Autoware** : ROS2-based, AD stack complet
  - **OpenPilot (comma.ai)** : Open-source ADAS, end-to-end
  - **NVIDIA DRIVE** : Full-stack, simulation to deployment

### ADAS (Advanced Driver-Assistance Systems)
- **Fonctionnalités** : ACC, LKA, AEB, BSD, LCA, APA, TSR
- **Niveaux** : SAE L0-L5 (L0 : alerte, L1 : aide, L2 : partiel, L3 : conditionnel, L4 : haut, L5 : complet)
- **Sensor Suite** : Camera, radar, LiDAR, ultrason, IMU, GNSS
- **Frameworks** : OpenPilot (comma.ai), Autoware, Apollo

---

## 2. Simulation Automobile

### CARLA (Car Learning to Act)
- **Type** : Simulateur urbain open-source, Unreal Engine
- **Villes** : Town01-Town12, Town01-07 (classic), Town10-12 (modern)
- **Capteurs** : Camera RGB, depth, segmentation, LiDAR, radar, IMU, GNSS
- **Weather** : Pluie, brouillard, nuit, soleil, nuage
- **Traffic** : Traffic manager, véhicules, piétons, cyclistes
- **API** : Python API (client/server), ROS2 bridge
- **Scenarios** : ScenarioRunner, OpenSCENARIO, custom
- **Leaderboard** : CARLA Autonomous Driving Leaderboard
- **Benchmark** : CARLA AD Challenge, Longest6, NoCrash
- **Usage** : Perception, planning, control, sim-to-real, RL

### SUMO (Simulation of Urban MObility)
- **Type** : Simulation de trafic, microscopique/macroscopique
- **Réseaux** : OpenStreetMap import, custom
- **Fonctionnalités** : Traffic lights, routes, vehicle types, emissions
- **API** : TraCI (Python, C++, Java), Libsumo
- **Intégration** : CARLA co-simulation (CARLA-SUMO bridge)
- **Usage** : Traffic analysis, V2X, route planning, infrastructure

### AirSim (Microsoft)
- **Type** : Simulateur drone/voiture, Unreal Engine
- **Capteurs** : Camera, depth, LiDAR, IMU, GPS, barometer
- **API** : Python, C++, ROS, AirSim-PX4 bridge
- **Usage** : Autonomous driving, drone navigation, RL
- **Statut** : Maintien communautaire (Microsoft a arrêté le développement actif en 2024)

### NVIDIA Drive Sim
- **Type** : Simulation haute-fidélité, NVIDIA Omniverse
- **Rendu** : RTX ray tracing, PhysX, RTX AI
- **Fonctionnalités** : Sensor simulation, scenario editor, map import
- **Cloud** : NVIDIA Drive Sim Cloud, batch simulation
- **Usage** : Validation, test, verification, compliance

### MetaDrive
- **Type** : Simulateur RL pour conduite, Panda3D
- **Procédural** : Génération infinie de routes/scénarios
- **Tâches** : Conduite, navigation, overtake, intersection
- **API** : Gymnasium, RLlib, SB3
- **Usage** : RL, generalization, safety

### HighwayEnv
- **Type** : Environnements RL pour conduite, Pygame
- **Tâches** : Highway, merge, roundabout, parking, intersection
- **API** : Gymnasium, multi-agent, kinematic
- **Usage** : RL, behavior planning, multi-agent

---

## 3. Datasets Conduite Autonome

### Waymo Open Dataset
- **Échelle** : 1150 scènes, 200k+ frames, 5 capteurs LiDAR, 5 cameras
- **Données** : Segments 20s, annotations 3D boxes, tracking
- **Tâches** : Detection, tracking, motion prediction, 3D detection
- **Format** : TFRecord, protobuf
- **Waymo Open Dataset v2** : 2x plus de données, lidar range 75m
- **Waymo Motion Dataset** : 100k+ scènes, agent trajectories
- **Usage** : Standard industriel, benchmark perception

### nuScenes (Motional)
- **Échelle** : 1000 scènes, 1.4M images, 400k LiDAR sweeps
- **Capteurs** : 6 cameras, 5 radars, 1 LiDAR, IMU/GPS
- **Villes** : Boston, Singapour
- **Annotations** : 23 classes, 3D boxes, attributes, tracking
- **nuScenes-lidarseg** : Segmentation LiDAR
- **nuPlan** : Planning dataset, 1500h driving, 1200+ scénarios
- **Usage** : Detection, tracking, prediction, planning

### KITTI (Karlsruhe)
- **Échelle** : 15h de conduite, variété de scènes
- **Capteurs** : 2 cameras, 1 LiDAR, IMU/GPS
- **Benchmarks** : Stereo, flow, depth, object detection, tracking, road
- **Format** : Standards, large adoption académique
- **Usage** : Benchmark classique, CV, perception

### Argoverse 2 (Argo AI)
- **Échelle** : 1000+ scènes, 6 villes US
- **Capteurs** : 7 cameras, 2 LiDAR, 2 radar
- **Données** : HD maps, vectorized lanes, 3D annotations
- **Tâches** : 3D detection, forecasting, motion prediction
- **Argoverse 2 HD** : Haute-définition, annotations denses
- **Usage** : Detection, prediction, planning, mapping

### Lyft L5
- **Échelle** : 1000+ heures, Palo Alto
- **Capteurs** : 7 cameras, 3 LiDAR, IMU/GPS
- **Format** : nuScenes-compatible, Level 5 dataset
- **Usage** : Detection, tracking, prediction

### BDD100K (UC Berkeley)
- **Échelle** : 100k vidéos, 10k heures, diversité
- **Capteurs** : Camera, GPS
- **Annotations** : 10 tâches (detection, segmentation, lane, drivable, tracking)
- **Usage** : Multi-task, domain adaptation, diverse conditions

### Cityscapes
- **Échelle** : 5k images fines, 20k images grossières
- **Villes** : 50 villes allemandes
- **Annotations** : Semantic, instance, panoptic (30 classes)
- **Usage** : Segmentation urbaine, standard CV

---

## 4. Industrie 4.0

### Digital Twin
- **Définition** : Jumeau numérique — réplique virtuelle d'un système physique
- **Composants** : Modèle physique, capteurs, simulation, analytics
- **Types** : Produit, processus, système
- **Technologies** : IoT, simulation, ML, AR/VR, 3D mapping
- **Plateformes** :
  - **Siemens Xcelerator** : Digital twin industriel, simulation
  - **Microsoft Azure Digital Twins** : IoT + twin modeling
  - **AWS IoT TwinMaker** : Digital twin cloud
  - **NVIDIA Omniverse** : Simulation 3D, digital twin visuel
  - **GE Digital APM** : Asset performance management, digital twin
- **Usage** : Simulation, optimisation, monitoring, prédiction

### IIoT (Industrial Internet of Things)
- **Protocoles** :
  - **OPC-UA** : Unified Architecture, sécurisé, interopérabilité
  - **MQTT Sparkplug** : Industriel, état, tag, pub/sub
  - **Modbus/TCP** : Legacy, simple, large adoption
  - **PROFINET** : Ethernet industriel, temps réel
  - **EtherNet/IP** : CIP-based, industrie
- **PLC** : Siemens (S7), Allen-Bradley (ControlLogix), Schneider (Modicon), Beckhoff (TwinCAT)
- **Edge Computing** : NVIDIA Jetson, Siemens IOT2050, Advantech
- **Cloud** : AWS IoT Core, Azure IoT Hub, Siemens MindSphere

### Predictive Maintenance (PdM)
- **Approches** : RUL (Remaining Useful Life), anomaly detection, failure prediction
- **Signaux** : Vibration, température, courant, pression, acoustique
- **Modèles** :
  - **Deep Learning** : LSTM, CNN, Transformer, autoencoder
  - **Classiques** : Random Forest, XGBoost, SVM, ARIMA
  - **Time Series** : PatchTST, TimesNet, Informer, FEDformer
- **Frameworks** : PyTorch, TensorFlow, scikit-learn, Darts
- **Métriques** : MAE, RMSE, MAPE, F1, precision/recall, C-index
- **Use Cases** : Moteurs, pompes, turbines, convoyeurs, compresseurs

### FDIFormer (Smart Grid)
- **Approche** : Transformer pour fault detection dans smart grids
- **Données** : PMU, SCADA, smart meters, perturbation records
- **Tâches** : Fault detection, classification, localisation, diagnosis
- **Architecture** : Transformer, graph neural network, attention
- **Usage** : Réseaux électriques, smart grids, énergie

---

## 5. Normes et Standards

### ISO 26262 — Functional Safety (Automotive)
- **Portée** : Safety-related E/E systems in vehicles
- **ASIL** : A, B, C, D (Automotive Safety Integrity Level)
- **Processus** : Hazard analysis → Safety goals → Functional safety concept → Technical safety concept
- **Phases** : Management, concept, product development, production, operation
- **ISO 26262:2018** : Seconde édition, semiconducteurs, motorcycles, trucks
- **Outils** : ANSYS medini analyze, BTC EmbeddedPlatform, LDRA

### AUTOSAR (AUTomotive Open System ARchitecture)
- **Classic Platform** : ECUs, CAN, LIN, FlexRay, real-time
  - RTE (Runtime Environment), BSW (Basic Software), SWC (Software Component)
  - VFB (Virtual Functional Bus), COM stack, DEM, DCM, NVM
- **Adaptive Platform** : Processeurs hautes performances, POSIX, Linux
  - ARA (AUTOSAR Runtime for Adaptive), services, execution management
  - Communication, diagnostic, network management, update
- **AUTOSAR +** : REST, SOME/IP, DDS, MQTT
- **Outils** : Vector DaVinci, EB tresos, ETAS ISOLAR, KPIT

### MISRA (Motor Industry Software Reliability Association)
- **MISRA C** : Guidelines for the use of C in critical systems
  - MISRA C:2012 — 3rd edition, 143 rules, 16 directives
  - MISRA C:2023 — Amendment 4, C11/C17 support
- **MISRA C++** : MISRA C++:2023 — 233 rules, guidelines
- **MISRA Compliance** : Deviations, mandatory/recommended/advisory
- **Outils** : Coverity, Polyspace, QAC, PC-lint, cppcheck
- **Usage** : Automotive, aerospace, medical, railway

### ASPICE (Automotive SPICE)
- **Process Reference** : Software development, management, support
- **Niveaux** : Capability Level 0-5
- **Processes** : SYS.1-5, SWE.1-6, SUP.1-10, MAN.1-6, ACQ.1-4
- **Évaluation** : Intrast, Verband der Automobilindustrie
- **Outils** : PTC Integrity, Siemens Polarion, IBM DOORS, Jira

---

## 6. Catégories et Tableau Récapitulatif

| Domaine | Outils / Plateformes | Usage |
|---------|---------------------|-------|
| Véhicules Autonomes | Waymo, Tesla, UniAD, VAD, Apollo, Autoware, OpenPilot | Perception, planification, end-to-end |
| Simulation | CARLA, SUMO, AirSim, NVIDIA Drive Sim, MetaDrive, HighwayEnv | Entraînement, test, validation |
| Datasets | Waymo, nuScenes, KITTI, Argoverse 2, BDD100K, Cityscapes | Perception, planification, benchmarking |
| Industrie 4.0 | Siemens Xcelerator, Azure Digital Twins, NVIDIA Omniverse | Digital twin, IIoT, PdM |
| Normes | ISO 26262, AUTOSAR, MISRA, ASPICE | Safety, architecture, qualité |

---

## 7. Workflow de Recherche

### Pipeline Type pour Conduite Autonome
1. **Simulation** : CARLA + SUMO (co-simulation traffic + driving)
2. **Perception** : BEVFormer/CenterPoint sur Waymo/nuScenes
3. **Planning** : UniAD/VAD end-to-end, MPC pour contrôle
4. **Dataset** : Fine-tuning sur KITTI/Argoverse pour robustesse
5. **Validation** : CARLA Leaderboard, Waymo Open Dataset benchmark
6. **Safety** : ISO 26262, MISRA compliance

### Pipeline Type pour Industrie 4.0
1. **Sensors** : OPC-UA / MQTT Sparkplug → Edge device
2. **Digital Twin** : NVIDIA Omniverse / Azure Digital Twins
3. **Predictive Maintenance** : LSTM/Transformer sur données temps réel
4. **Monitoring** : Grafana, InfluxDB, MQTT broker
5. **Compliance** : ISO 26262, ASPICE, MISRA

### Exemple de Stack Python
```python
# Stack type pour recherche autonomous driving
import carla  # Simulation
import torch  # Deep learning
from mmdet3d import *  # 3D detection
from nuscenes import NuScenes  # Dataset
from stable_baselines3 import PPO  # RL control
```

---

## Ressources

- [CARLA Simulator](https://carla.org)
- [Waymo Open Dataset](https://waymo.com/open)
- [nuScenes](https://www.nuscenes.org)
- [Apollo (Baidu)](https://github.com/ApolloAuto/apollo)
- [OpenPilot (comma.ai)](https://github.com/commaai/openpilot)
- [UniAD](https://github.com/OpenDriveLab/UniAD)
- [ISO 26262 Overview](https://www.iso.org/standard/68383.html)
- [AUTOSAR](https://www.autosar.org)
- [MISRA](https://www.misra.org.uk)
- [NVIDIA Omniverse](https://www.nvidia.com/en-us/omniverse)
- [Siemens Xcelerator](https://www.sw.siemens.com/en-US/xcelerator)