---
name: hardware-architecture
description: Compétence niveau docteur en architecture matérielle — microarchitecture CPU/GPU/TPU, FPGA, ASIC, systèmes embarqués, hiérarchies mémoire, interconnexions, et co-design matériel-logiciel pour l'IA.
category: research
---

# Architecture Matérielle et Systèmes Informatiques

## Présentation

Compétence de recherche couvrant l'architecture des systèmes informatiques à tous les niveaux d'abstraction : de la microarchitecture des processeurs jusqu'aux centres de données, en passant par les accélérateurs matériels pour l'IA (GPU, TPU, NPU, FPGA), les architectures mémoire, les interconnexions, et le co-design matériel-logiciel. Couvre les catégories arXiv cs.AR, cs.ET, et partiellement cs.OS et physics.ins-det.

## Domaines de Recherche Principaux

### Microarchitecture des Processeurs
- Architectures superscalaires, pipelines profonds, exécution dans le désordre (*out-of-order*)
- Prédiction de branchement, exécution spéculative, *branch target buffers*
- Architectures VLIW/EPIC (Itanium, DSP)
- Cœurs RISC-V (variantes, extensions vectorielles/superscalaires)
- Architectures multi-cœurs, cache cohérent (MESI/MOESI/ directory-based)
- *Simultaneous Multithreading* (SMT/Hyper-Threading)
- Mécanismes de sécurité matériels : MPK, CET, TDX, SEV-SNP, CHERI
- Attaques microarchitecturales (Spectre, Meltdown, Rowhammer) et contre-mesures

### Mémoire et Hiérarchies de Stockage
- Hiérarchies mémoire : L1/L2/L3, cache inclusif vs exclusif, *prefetching*
- Mémoires non-volatiles : Intel Optane, CXL.mem, Samsung Z-NAND
- Architectures NUMA/UMA, protocoles de cohérence
- HBM (High Bandwidth Memory), GDDR, DDR5, LPDDR
- *Memory-centric computing* et *processing-in-memory* (PIM)
- CXL (Compute Express Link) 2.0/3.0, CXL.io, CXL.cache, CXL.mem
- Unified Memory Architectures (UMA dans GPU, NVIDIA Grace Hopper)

### Accélérateurs Matériels pour l'IA
- Architectures GPU : NVIDIA CUDA Cores/Tensor Cores, AMD CDNA, Intel Xe
- TPU (Tensor Processing Unit) : MXU, systolic arrays
- NPU (Neural Processing Unit) : Apple Neural Engine, Qualcomm Hexagon, Samsung NPU
- FPGA pour l'IA : Xilinx Versal AI, Intel Stratix, Vitis AI, FINN
- ASIC IA : Groq (TSP), Cerebras (wafer-scale), SambaNova (RDU)
- Architectures neuromorphiques : Intel Loihi 2, IBM TrueNorth, SpiNNaker
- Quantification matérielle : INT4, INT8, FP8 (OCP Microscaling), BF16, FP16

### Interconnexions et Réseaux de Données
- Topologies d'interconnexion : mesh, torus, fat-tree, dragonfly
- NVLink/NVSwitch (NVIDIA), Infinity Fabric (AMD), Xe Link (Intel)
- InfiniBand (Mellanox/Nvidia ConnectX-7/8), RoCEv2
- PCI Express 5.0/6.0, CXL, UCIe (Universal Chiplet Interconnect Express)
- Network-on-Chip (NoC) : architectures, routage, QoS
- Interconnexions optiques pour centres de données, co-packaged optics

### Systèmes Embarqués et IoT
- Microcontrôleurs : ARM Cortex-M, RISC-V (SiFive, Espressif), AVR
- SoC (System-on-Chip) : hiérarchies bus, DMA, périphériques
- Architectures temps réel : périphériques de timing, vecteurs d'interruption
- *Energy-efficient computing* : DVFS, near-threshold computing, *harvesting*
- *TinyML* déploiement matériel (CMSIS-NN, TensorFlow Lite Micro)

### Centres de Données et *Warehouse-Scale Computing*
- Architectures de centres de données : refroidissement liquide, power distribution
- *Disaggregated computing* : SmartNIC, DPU (BlueField), IPU
- *Composable infrastructure* : Liqid, Intel Rack Scale Design
- Efficacité énergétique : PUE, TDP, *power capping*, *thermal throttling*
- *Optical interconnects*, co-packaged optics, silicon photonics

## Catégories

| Catégorie | Description |
|-----------|-------------|
| **cs.AR** | Architecture matérielle, systèmes, organisation |
| **cs.ET** | Technologies émergentes (nouveaux paradigmes matériels) |
| **cs.OS** | Systèmes d'exploitation, gestion mémoire, pilotes |
| **cs.PF** | Performance, benchmarks, modélisation |
| **physics.ins-det** | Instrumentation, détecteurs, accélérateurs |
| **B.0** (ACM) | Matériel, général |
| **B.1** (ACM) | Architecture de contrôle/logique |
| **B.2** (ACM) | Unités arithmétiques et logiques |
| **B.3** (ACM) | Mémoire |
| **B.4** (ACM) | Entrées/sorties et communications |
| **B.7** (ACM) | Circuits intégrés |
| **C.0** (ACM) | Général systèmes informatiques |
| **C.1** (ACM) | Architectures de processeurs |

## Articles Notables Récents

| Titre | Année | Conférence/Journal |
|-------|-------|--------------------|
| "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness" | 2022 | NeurIPS |
| "Cerebras Wafer-Scale Engine: Why We Need Big Chips" | 2021 | IEEE Micro |
| "A Compute-in-Memory Chip Based on Resistive Random-Access Memory" | 2022 | Nature |
| "The Microarchitecture of the NVIDIA Grace Hopper Superchip" | 2023 | Hot Chips |
| "Gem5: Twenty Years of Computer Architecture Research" | 2024 | ISCA |
| "RISC-V: An Open Standard for a New Era of Computing" | 2023 | Communications of the ACM |
| "CXL 3.0: Accelerating Memory Pooling and Sharing" | 2024 | IEEE Micro |

## Comment Effectuer la Veille

- **arXiv cs.AR** : https://arxiv.org/list/cs.AR/recent
- **ISCA / MICRO / HPCA / ASPLOS** : actes de conférences (IEEE/ACM)
- **Hot Chips** : https://hotchips.org (présentations architecturales des nouveaux processeurs/accélérateurs)
- **IEEE Micro** : revue bimestrielle
- **RISC-V International Newsletter** : https://riscv.org
- **OCP (Open Compute Project)** : spécifications matérielles open-source
- **Mots-clés** : *computer architecture*, *microarchitecture*, *hardware accelerator*, *memory hierarchy*, *cache coherence*, *RISC-V*, *CXL*, *chiplet*, *3D stacking*, *neuromorphic hardware*, *sparse accelerator*
