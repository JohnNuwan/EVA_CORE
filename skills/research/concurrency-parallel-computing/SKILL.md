---
name: concurrency-parallel-computing
description: Compétence en calcul parallèle et haute performance suivie sur arXiv sous cs.DC et cs.PF. Couvre le calcul parallèle, les architectures GPU, la programmation distribuée, le calcul haute performance, les frameworks de parallélisme, la compilation parallèle et l'optimisation de performance.
---

# Calcul Parallèle et Haute Performance — arXiv

## Présentation
Ce skill guide la veille sur le calcul parallèle et haute performance via arXiv (cs.DC, cs.PF et domaines connexes). Il couvre les architectures HPC, le calcul GPU, les frameworks de parallélisme pour l'apprentissage profond et l'optimisation de performance.

## Calcul Haute Performance (HPC)
- **Supercalculateurs** — systèmes TOP500, Fugaku, Frontier, Aurora.
- **Architectures de clusters** — InfiniBand, interconnexions, stockage parallèle.
- **Scheduling et orchestration** — Slurm, PBS, Kubernetes pour HPC.
- **Modèles de coût** — loi d'Amdahl, loi de Gustafson, roofline model.

## GPU Computing et CUDA
- **GPU kernels** — parallélisme massif, warp/wavefront, occupancy.
- **Mémoire GPU** — hiérarchie : global, shared, registers, texture.
- **Optimisation pour deep learning** — fused kernels, FlashAttention, operator fusion.
- **CUDA et alternatives** — ROCm, oneAPI, Vulkan Compute.
- **GPU memory efficiency** — gradient checkpointing, activation recomputation.

## Programmation Parallèle
- **MPI** — communication collective, point-to-point, topologies.
- **OpenMP** — parallélisme à mémoire partagée, directives de compilation.
- **Frameworks distribués** — Apache Spark, Ray, Dask.
- **Modèles de parallélisme** — SIMD, SIMT, MIMD, dataflow.

## Frameworks de Parallélisme pour ML
- **Parallélisme de données** — FSDP, DDP, ZeRO (Stages 1-3).
- **Parallélisme de modèles** — pipe parallelism (GPipe, PipeDream), tensor parallelism (Megatron-LM).
- **Parallélisme de pipeline** — micro-batching, schedule 1F1B, interleaved.
- **Parallélisme contextuel** — Design-CP : parallélisme contextuel pour nanoparticules protéiques.
- **Sequence parallelism** — Ring Attention, context parallelism.
- **Expert parallelism** — Mixture-of-Experts dispersé.

## Calcul Distribué pour l'IA
- **Design-CP** — parallélisme contextuel pour simulation de nanoparticules protéiques multi-échelle.
- **Entraînement distribué** — orchestration, communication collective, gradient compression.
- **Inférence distribuée** — vLLM, TensorRT-LLM, déploiement multi-nœud.

## Optimisation de Performance
- **Profiling** — NVIDIA Nsight, perf, gprof, roofline analysis.
- **Bottlenecks** — compute-bound, memory-bound, communication-bound.
- **Optimisations automatiques** — compilation JIT, auto-tuning (TVM, XLA).
- **Opérateurs fusionnés** — kernel fusion, réduction des lancements GPU.

## Catégories arXiv
- `cs.DC` — calcul distribué, parallèle, cluster.
- `cs.PF` — performance, analyse de performance.
- `cs.AR` — architecture hardware.
- `cs.LG` — parallélisme pour ML, frameworks distribués.

## Articles Notables
- "Design-CP: Context Parallelism for Protein Nanoparticles" (arXiv)
- "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM" (Narayanan et al., SC 2021)
- "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness" (Dao et al., NeurIPS 2022)
- "GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism" (Huang et al., NeurIPS 2019)
- "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models" (Rajbhandari et al., SC 2020)
