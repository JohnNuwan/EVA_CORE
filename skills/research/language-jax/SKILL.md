---
name: language-jax
title: "Doctorat — JAX (Just After eXecution)"
description: "Compétence niveau docteur en JAX. Couvre autograd, XLA compilation, JIT, vmap, pmap, shard_map, Pallas kernel, TPU/GPU, custom gradients, differential programming, et l'écosystème JAX/Flax/Haiku."
category: research
lang: fr
---

# Doctorat : JAX

## Présentation
JAX est une bibliothèque de calcul numérique et d'apprentissage automatique développée par Google Research (2018). Elle combine l'API de NumPy avec les transformations fonctionnelles : compilation JIT (XLA), différenciation automatique (autograd), vectorisation (vmap), parallélisme (pmap), et répartition distribuée (shard_map). Elle est conçue pour le calcul haute performance sur CPU, GPU et TPU. JAX suit une philosophie fonctionnelle pure : toutes les fonctions sont pures, les transformations sont composables, et l'état est explicitement géré.

## Histoire et Contexte
- 2017-2018 : Projet interne Google — fusion de HIPS Autograd et XLA
- 2019 : Publication de JAX comme projet open source
- 2019-2020 : Adoption par DeepMind (Haiku, Optax)
- 2021 : JAX 0.2 — pmap, sharded computation, TPU pods
- 2022 : JAX 0.3 — numpy API 1.23 complète
- 2023 : JAX 0.4 — Pallas (kernels personnalisés), shard_map
- 2024 : JAX 0.5 — Safe best-effort compilation, MPS backend

## Architecture du Langage
- **Python first** : JAX est une bibliothèque Python pure
- **Transformations fonctionnelles** : jit, grad, vmap, pmap, shard_map, remat, scan, cond
- **Pureté fonctionnelle** : Pas d'état global, pas de mutation
- **PRNG state** : Générateurs de nombres aléatoires explicites (Threefry, Philox)
- **XLA** : Accelerated Linear Algebra — compilateur optimisé pour tenseurs
- **jax.numpy** : API compatible NumPy (90%+ de compatibilité)
- **jax.lax** : Opérations de bas niveau (XLA ops)
- **Tracé (Tracing)** : JAX trace les fonctions via des pysymboliques

## Système de Types
- **Type dynamique** : Python typing + traçage XLA
- **Shapes** : Tableaux multidimensionnels avec shape, dtype
- **Tensors** : jax.Array — le type central, unifié
- **dtypes** : bfloat16, float8 (e4m3, e5m2), int4, fp8
- **Pytree** : Structures arborescentes de tableaux (tuples, listes, dicts)
- **Concrete/abstract** : Dimensions concrètes vs abstraites pendant le traçage

## Compilation et Interprétation
- **JIT compilation via XLA** : jit — compilation en HLO
- **Pipeline** : Python → traçage → HLO → XLA → LLVM → GPU/TPU code
- **AOT compilation** : jit(fn).lower(args).compile()
- **StableHLO** : Version portable de HLO
- **Pallas** : Langage de kernel personnalisé compilé via MLIR
- **Rematerialization** : remat/checkpoint — échange mémoire/calcul

## Mémoire et Performances
- **Buffer donation** : Réutilisation de buffers d'entrée
- **Device memory** : XLA gère les buffers GPU/TPU
- **Sharding** : Partitionnement des tableaux sur des devices
- **Host↔Device** : Transferts via device_put, device_get
- **JAX arrays** : jax.Array est immutable

## Écosystème et Outils
- **Flax** (Google) : Framework NN modulaire
- **Haiku** (DeepMind) : Framework NN orienté objet
- **Optax** : Bibliothèque d'optimisation
- **Orbax** : Checkpointing distribué
- **Pallas** : Langage pour kernels GPU/TPU
- **Equinox** : NN basé sur pytrees
- **Diffrax** : EDOs, CDEs, SDEs différentiables

## Concurrence et Parallélisme
- **pmap** : Parallélisme SPMD sur plusieurs devices
- **shard_map** : Contrôle explicite du sharding
- **vmap** : Vectorisation automatique
- **SPMD partitioner** : XLA SPMD auto-partitionne
- **Collectives** : psum, pmax, all_gather, all_to_all
- **Device mesh** : Topologie des devices (2D, 3D mesh)
- **FSDP** : Fully Sharded Data Parallelism

## Patterns Avancés
- **Scan** : lax.scan — boucles compilées
- **Cond / Switch** : Branchements conditionnels compilables
- **Custom gradients** : custom_vjp / custom_jvp
- **Implicit differentiation** : custom_root
- **Pallas cores** : Programmation de kernels avec pallas_call

## Optimisation
- **Operator fusion** : Fusion d'opérations en un seul kernel
- **Rematerialization** : checkpoint pour réduire la mémoire
- **Algebraic simplification** : Simplification d'expressions
- **Quantization** : fp8, int8
- **Mixed precision** : Contrôle de la précision matricielle
- **Pallas** : Kernels GPU/TPU hautement optimisés

## Interopérabilité
- **NumPy bridge** : jax.numpy suit l'API NumPy
- **PyTorch bridge** : jax2torch / torch2jax
- **HuggingFace** : Modèles via Flax
- **Keras** : JAX backend officiel de Keras 3
- **ONNX** : Export vers ONNX

## Applications Industrielles
- **DeepMind** : AlphaFold, AlphaZero, Gato, Gemini
- **Google Research** : PaLM, ViT, BERT
- **Waymo** : Perception et planification autonome
- **Recherche académique** : NLP, vision, RL, bio-informatique
- **Meteorology** : GraphCast

## Sécurité
- **Pure functions** : Améliore la prévisibilité
- **Determinism** : Sorties déterministes (PRNG séparé)
- **Device isolation** : Programmes isolés sur les devices
- **Checkpoint security** : Les checkpoints ne sont pas signés

## Veille Technologique
- **GitHub JAX** : github.com/google/jax
- **JAX documentation** : jax.readthedocs.io
- **Google JAX Blog** : Publications sur la JAX community
- **Conférences** : JAX Conference, MLIR Open Design Meetings
- **Évolutions clés** : JAX 0.4, Pallas stable, shard_map, OpenXLA