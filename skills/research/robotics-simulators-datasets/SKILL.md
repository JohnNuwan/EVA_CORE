---
name: robotics-simulators-datasets
description: "Compétence niveau ingénieur/docteur en robotique, simulateurs et datasets. Couvre MuJoCo, Isaac Sim, Gazebo, PyBullet, Habitat, AI2Thor, MetaWorld, ManiSkill, MimicGen, datasets robotiques (Open X-Embodiment, RH20T, DROID), frameworks d'apprentissage (RLlib, Stable-Baselines3, DQN Zoo), ROS/ROS2, et robot software."
category: research
tags: [robotique, simulation, reinforcement-learning, datasets-robotiques, ros, manipulation, navigation]
---

# Robotique, Simulateurs et Datasets — Référence Ingénieur/Docteur

## Présentation

Ce skill couvre l'écosystème complet de la robotique moderne : simulateurs physiques, benchmarks de Reinforcement Learning, datasets robotiques à grande échelle, frameworks ROS, et outils de perception/localisation. Conçu pour un niveau ingénieur/docteur en robotique, IA, ou apprentissage par renforcement.

---

## 1. Simulateurs Physiques

### MuJoCo (Multi-Joint dynamics with Contact)
- **Moteur** : Physique, contrôle continu, contacts
- **Acquisition** : DeepMind → open-source (2021), licence Apache 2.0
- **Format** : MJCF (XML), assets 3D, tendeurs, moteurs, capteurs
- **Performance** : Optimisé, compute shader, simulation rapide
- **Fonctionnalités** : Contact, friction, déformation, elasticité
- **MuJoCo MPC** : Model Predictive Control intégré
- **Bindings** : Python, C/C++, Unity plugin
- **Usage** : RL, contrôle, biomécanique, animation

### Isaac Sim / Isaac Orbit (NVIDIA)
- **Plateforme** : Simulation robotique sur GPU NVIDIA
- **Moteur** : Physique NVIDIA PhysX, rendu RTX (ray tracing)
- **Isaac Orbit** : Framework RL, scalable, distribution GPU
- **Assets** : Isaac Sim Assets (robots, environnements, capteurs)
- **ROS2 Bridge** : Intégration native ROS2
- **Fonctionnalités** : Sim-to-real, domain randomization, synthetic data
- **Capteurs** : LIDAR, RGB-D, IMU, force/torque, tactile
- **Usage** : Manipulation, navigation, mobile manipulation, humanoïdes

### Gazebo (classic + Ignition/Harmony)
- **Moteur** : Physique ODE/Bullet/DART, ROS-intégré
- **Gazebo Classic** : Legacy, ROS1, mature
- **Gazebo Ignition/Harmony** : ROS2 natif, plugins, physics engine pluggable
- **SDFormat** : Format de description de simulation
- **Intégration** : ROS2, navigation stack, MoveIt
- **Usage** : Standard ROS, robots mobiles, drones, manipulation

### PyBullet
- **Moteur** : Physique Bullet, Python-native
- **Performance** : Rapide, GPU-accelerated, licences permissive
- **Fonctionnalités** : Inverse kinematics, collision detection, ray casting
- **Gym Environments** : Ant, HalfCheetah, Humanoid, KUKA
- **Usage** : RL, prototypage rapide, éducation, recherche

### SAPIEN
- **Moteur** : Physique, manipulation, interaction
- **Spécificité** : Part-level segmentation, articulated objects
- **Fonctionnalités** : Render, physical simulation, interaction
- **Datasets** : PartNet, ShapeNet, SAPIEN Asset
- **Usage** : Manipulation fine, assembly, démontage

### Habitat / HabitatLab (Meta)
- **Moteur** : Navigation, simulation 3D, RGB-D
- **Habitat Sim** : Rendu, physique, capteurs, scènes 3D
- **Habitat Lab** : Framework RL, benchmark, dataset
- **Scènes** : Matterport3D, Gibson, Replica, HM3D
- **Tâches** : PointGoal, ObjectNav, ImageNav, Exploration
- **Usage** : Navigation embarquée, SLAM, exploration

### AI2-THOR (Allen Institute)
- **Simulateur** : Environnements intérieurs interactifs
- **Scènes** : Cuisines, salons, chambres, salles de bain
- **Objets** : Interactables (ouvrir, fermer, déplacer)
- **Fonctionnalités** : Changement d'état, physique, rendu
- **Usage** : Manipulation, navigation, interaction objet

### Autres Simulateurs
- **MetaWorld** : 50 tâches de manipulation (voir Benchmarks)
- **Drake** (MIT) : Contrôle robotique, analyse, optimisation
- **Webots** : Open-source, multi-robot, ROS2
- **CoppeliaSim** (ex-VREP) : Simulation robotique, API distante
- **Unity ML-Agents** : Unity-based RL, 3D environments
- **NVIDIA Isaac Gym** : GPU RL, déprécié → Isaac Orbit

---

## 2. Benchmarks RL Robotique

### MetaWorld
- **Tâches** : 50 tâches de manipulation variées
- **Catégories** : Reach, push, pick-and-place, assembly, peg-insertion
- **Environnements** : ML1 (multi-task), ML10/ML45 (meta-learning)
- **Observations** : Proprioceptive, vision (RGB + depth)
- **Métriques** : Success rate, reward, generalization
- **Usage** : Multi-task learning, meta-RL, generalization

### DM Control (DeepMind Control Suite)
- **Tâches** : Cheetah, Walker, Humanoid, Quadruped, Cartpole, Acrobot
- **Domaines** : Locomotion, manipulation, balance
- **Observations** : État, pixels, proprioception
- **Évaluation** : Reward standardisé, épisodes
- **Usage** : RL continu, locomotion, contrôle

### ManiSkill
- **Tâches** : Manipulation (pick, push, open, pour, assemble)
- **Simulateur** : SAPIEN-based
- **Observations** : RGB, point cloud, state
- **Métriques** : Success rate, generalization, sim-to-real
- **Dataset** : Démonstrations expertes, motion planning
- **Usage** : Manipulation visuelle, imitation learning, RL

### D4RL (Offline RL)
- **Datasets** : Offline RL pour robotique, locomotion, navigation
- **Environnements** : MuJoCo, Adroit, AntMaze, Kitchen, Flow
- **Modes** : Medium, medium-replay, medium-expert, expert
- **Métriques** : Normalized score, cumulative reward
- **Usage** : Offline RL, offline-to-online, imitation learning

### Gymnasium API
- **Standard** : API unifiée pour RL (successeur de OpenAI Gym)
- **Fonctionnalités** : Spaces, wrappers, vector environments
- **Environnements** : Classic, MuJoCo, Box2D, Atari, Toy Text
- **Intégration** : SB3, RLlib, CleanRL, Acme
- **Usage** : API standard pour RL, prototypage, benchmark

---

## 3. Datasets Robotiques

### Open X-Embodiment (OXE)
- **Échelle** : 1M+ épisodes, 60+ datasets, 22 robots
- **Embodiments** : Franka, KUKA, UR5, Sawyer, Google Robot, Bridge
- **Tâches** : Pick, place, push, open, close, fold, pour
- **Format** : RLDS (TensorFlow Datasets)
- **Usage** : Cross-embodiment learning, robot foundation model, RT-2
- **Paper** : "Open X-Embodiment: Robotic Learning Datasets and RT-X Models"

### DROID (Distributed Robot Interaction Dataset)
- **Échelle** : 350+ heures, 1M+ étapes, 10+ robots
- **Tâches** : Manipulation fine (drawer, cabinet, washer, etc.)
- **Collecte** : Téléopération distribuée, 50+ collecteurs
- **Observations** : RGB, depth, joint states, wrist camera
- **Usage** : Imitation learning, manipulation, generalization

### RH20T (Robot Human 20 Tasks)
- **Échelle** : 20 tâches, 100k+ démonstrations
- **Tâches** : Pick, place, pour, open, close, assemble
- **Collecte** : Téléopération humaine, 10+ scénarios
- **Usage** : Imitation learning, task generalization

### BridgeData v2
- **Échelle** : 60k+ épisodes, 2+ robots (WidowX)
- **Tâches** : Manipulation de table, pick-and-place, push
- **Collecte** : Téléopération, 10+ environnements
- **Usage** : Image-based RL, robot learning, data augmentation

### Autres Datasets
- **FurnitureBench** : Assemblage de meubles, 800+ démos
- **RoboTurk** : Téléopération crowdsourcée, 100+ tâches
- **NIST Assembly** : Assemblage industriel, précision
- **TACO** : Task-oriented robot control
- **Language-Table** : Instruction following, visuomotor

---

## 4. Frameworks Robotique (ROS)

### ROS 2 Humble/Iron/Rolling
- **Architecture** : DDS (Data Distribution Service), nodes, topics, services
- **Communication** : Publish/subscribe, RPC (services), actions
- **Outils** : RViz2, rqt, ros2cli, tf2
- **Navigation** : Nav2 (navigation stack), SLAM toolbox
- **Manipulation** : MoveIt 2, ros2_control
- **Build** : colcon, ament, CMake
- **Langages** : C++, Python, Rust

### MoveIt / MoveIt 2
- **Framework** : Planification de mouvement, manipulation
- **Planificateurs** : OMPL, STOMP, CHOMP, Pilz Industrial
- **Fonctionnalités** : Inverse kinematics, collision avoidance, trajectory
- **ROS2** : MoveIt 2 natif, ros2_control, perception
- **Usage** : Bras robotiques, manipulation industrielle, pick-and-place

### RViz / RViz2
- **Visualisation** : 3D, robots, capteurs, maps, paths
- **Plugins** : Custom displays, panels, tools
- **Usage** : Debug, monitoring, visualisation temps réel

### TF2
- **Framework** : Transformations, frames, arbre de coordonnées
- **Fonctionnalités** : Broadcast, lookup, time travel
- **API** : C++, Python
- **Usage** : Toute application ROS nécessitant des coordonnées spatiales

### URDF / SDF
- **URDF** : Unified Robot Description Format (XML)
- **SDF** : Simulation Description Format (Gazebo)
- **Éléments** : Link, joint, geometry, inertia, collision, visual
- **Outils** : `check_urdf`, `urdf_to_graphiz`, `gz sdf`
- **Usage** : Description de robots, simulation, visualisation

---

## 5. RL pour Robotique

### RLlib (Ray)
- **Framework** : RL distribué, scalable
- **Algorithmes** : PPO, DQN, SAC, DDPG, APEX, IMPALA, A3C
- **Fonctionnalités** : Multi-agent, offline RL, model-based
- **Distribution** : Ray cluster, multi-GPU/multi-node
- **Intégration** : Gymnasium, environments custom
- **Usage** : RL à grande échelle, robotique, jeux

### Stable-Baselines3 (SB3)
- **Framework** : RL Python, stable, bien documenté
- **Algorithmes** : PPO, A2C, DQN, SAC, TD3, DDPG, ARS, TRPO
- **Fonctionnalités** : Callbacks, wrappers, monitoring, vector envs
- **Intégration** : Gymnasium, custom envs, WandB
- **Usage** : RL standard, prototypage, benchmark

### SBX (Stable-Baselines3 + JAX)
- **Variante** : SB3 algorithms implémentés en JAX
- **Performance** : x10-100 accélération, JIT compilation
- **Algorithmes** : PPO, SAC, DQN, TD3 (JAX)
- **Usage** : RL rapide, recherche, hyperparameter sweeping

### CleanRL
- **Framework** : RL implémentations propres, éducatives
- **Approche** : Single-file algorithm implementations
- **Contenu** : PPO, DQN, A2C, SAC, DDPG, IMPALA, etc.
- **Usage** : Apprentissage, recherche, debugging

### Acme (DeepMind)
- **Framework** : RL modulaire, composable
- **Acteurs/Optimiseurs** : Distributed, TF/JAX backend
- **Algorithmes** : DQN, D4PG, R2D2, MPO, PPO
- **Usage** : RL research, agents complexes

---

## 6. Perception et Localisation

### Cartographer (Google)
- **Framework** : SLAM, LIDAR, IMU, 2D/3D
- **ROS2** : cartographer_ros
- **Fonctionnalités** : Real-time, loop closure, submaps
- **Usage** : Navigation, mapping, localisation

### ORB-SLAM3
- **Framework** : Visual SLAM, monocular/stereo/RGB-D
- **Fonctionnalités** : IMU integration, visual-inertial, loop closure
- **Usage** : Navigation, localisation, mapping

### AprilTag
- **Fiducial** : Tags visuels, détection, pose estimation
- **Familles** : 36h11, 25h9, 16h5, Standard41h12
- **Usage** : Localisation, calibration, AR

### OpenCV + ROS
- **Bridge** : cv_bridge (ROS ↔ OpenCV)
- **Modules** : Calibration, feature detection, tracking, stitching
- **Usage** : Vision robotique, perception, tracking

---

## 7. Catégories et Tableau Récapitulatif

| Catégorie | Outils | Usage |
|-----------|--------|-------|
| Simulateurs | MuJoCo, Isaac Sim, Gazebo, PyBullet, Habitat, SAPIEN | Physique, contrôle, rendu |
| Benchmarks RL | MetaWorld, DM Control, ManiSkill, D4RL, Gymnasium | Évaluation, comparaison |
| Datasets | OXE, DROID, RH20T, BridgeData v2 | Imitation, fondation |
| ROS | ROS2, MoveIt2, Nav2, RViz2, TF2 | Robotique logicielle |
| RL | RLlib, SB3, CleanRL, Acme, SBX | Apprentissage |
| Perception | Cartographer, ORB-SLAM3, AprilTag, OpenCV | SLAM, localisation |
| Formats | URDF, SDF, MJCF | Description robot |

---

## 8. Workflow de Recherche en Robotique

### Pipeline Type pour Robot Learning
1. **Simulation** : MuJoCo/Isaac Sim pour entraînement RL
2. **RL Training** : SB3/RLlib avec Gymnasium API
3. **Dataset** : OXE/DROID pour imitation learning pré-entraînement
4. **ROS2** : Déploiement réel, perception, planification
5. **SLAM** : Cartographer/ORB-SLAM3 pour localisation
6. **Évaluation** : Success rate, sim-to-real transfer, generalization

### Exemple de Stack
```python
# Stack type pour robot learning
import gymnasium as gym
from stable_baselines3 import PPO
from mani_skill.utils import gym_wrapper
import mujoco
import rclpy  # ROS2
```

---

## Ressources

- [MuJoCo Docs](https://mujoco.readthedocs.io)
- [Isaac Sim](https://docs.omniverse.nvidia.com/isaacsim)
- [Gazebo Documentation](https://gazebosim.org/docs)
- [ROS 2 Documentation](https://docs.ros.org)
- [Stable-Baselines3](https://stable-baselines3.readthedocs.io)
- [RLlib](https://docs.ray.io/en/latest/rllib)
- [Open X-Embodiment](https://robotics-transformer-x.github.io)
- [DROID Dataset](https://droid-dataset.github.io)
- [MetaWorld](https://meta-world.github.io)
- [ManiSkill](https://maniskill.ai)