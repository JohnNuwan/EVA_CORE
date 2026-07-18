---
name: performance-optimization
description: "Compétence niveau expert en optimisation de performance couvrant cs.PF et cs.OS : analyse, benchmarking, profilage, optimisation code/OS/GPU, modélisation"
category: research
---

# Optimisation de Performance

## Présentation

Compétence avancée en analyse et optimisation de performance des systèmes informatiques, couvrant l'intersection des domaines **cs.PF** (Performance) et **cs.OS** (Operating Systems). Cette compétence traite des méthodes systématiques pour mesurer, analyser, modéliser et améliorer les performances à tous les niveaux d'un système : matériel, système d'exploitation, runtime et code applicatif.

**Domaines ACM :** cs.PF (Performance), cs.OS (Operating Systems), cs.AR (Architecture), cs.DC (Distributed, Parallel, and Cluster Computing)

## Domaines

### 1. Analyse de Performance

Méthodologies et métriques fondamentales pour quantifier et comprendre la performance système.

- **Métriques essentielles :** latence, débit (throughput), utilisation, temps de réponse, overhead, scalability (speedup, efficiency), tail latency (p99, p999)
- **Approches :** analyse descendante (top-down), ascendante (bottom-up), analyse de goulots d'étranglement (bottleneck analysis), analyse par couches
- **Outils système :** `top`/`htop`, `iostat`, `vmstat`, `mpstat`, `sar`, `dstat`, `nethogs`, `iftop`, `iotop`, `pidstat`
- **Tracing :** `ftrace`, `trace-cmd`, `bpftrace`, `eBPF`, `perf-trace`, `LTTng`, SystemTap
- **Méthode USE (Utilization, Saturation, Errors) :** approche systématique de Brendan Gregg pour identifier les goulots
- **Méthode RED (Rate, Errors, Duration) :** approche Tom Wilkie pour les services microservices
- **Analyse de dépendances :** flame graphs, heat maps, latency distribution, waterfall charts

### 2. Benchmarking

Évaluation quantitative de performance via des suites de benchmarks standardisées.

#### SPEC (Standard Performance Evaluation Corporation)

- **SPEC CPU 2017 :** suite de référence pour CPU/mémoire — 10 benchmarks SPECspeed (4 integer, 6 FP) + 13 SPECrate (9 integer, 4 FP). Mesures : temps d'exécution (SPECspeed), débit (SPECrate). Métriques : SPECspeed 2017 Integer/Floating Point, SPECrate 2017 Integer/Floating Point
- **SPEC CPU 2006 :** prédécesseur — 12 integer (CINT2006), 17 FP (CFP2006). Encore utilisé pour comparaisons historiques
- **SPECjbb 2015 :** benchmark de middleware Java — charge transactionnelle (facturation, entrepôt) avec métriques de débit (max-jOPS, critical-jOPS)
- **SPECvirt :** virtualisation — consolidation machines virtuelles
- **SPECpower :** efficacité énergétique (performance par watt)
- **SPEC Cloud :** benchmarking de cloud IaaS — élasticité, déploiement multi-instance

#### Autres suites

- **lmbench :** microbenchmarks UNIX — latence mémoire (L1/L2/L3/RAM), bande passante mémoire, latence pipe/context switch/file system, signal handler overhead, mmap latency
- **Phoronix Test Suite :** plateforme de benchmarking open-source — 500+ tests couvrant CPU, GPU, mémoire, stockage, réseau, base de données. Tests notables : pts/cpu, pts/memory, pts/disk, pts/gpu, pts/network
- **Geekbench :** benchmark cross-platform (CPU/GPU compute) — tests single-core et multi-core, charge mixte (encryption, compression, HTML5, SQLite, physics, etc.)
- **UnixBench :** benchmark POSIX — Dhrystone, Whetstone, execl throughput, pipe throughput, context switching, shell scripting, system call overhead
- **Stream :** benchmark bande passante mémoire — Copy, Scale, Add, Triad
- **stress-ng :** stress test + microbenchmark pour noyau Linux — 300+ stressor (CPU, cache, mémoire, I/O, lock, scheduler)

### 3. Profilage

Analyse dynamique de code pour identifier les goulots d'étranglement.

#### Linux perf

- `perf stat` : compteurs matériels (cycles, instructions, cache-misses, branches, branch-misses, stalled-cycles)
- `perf record` / `perf report` : échantillonnage (sampling) — profiling CPU avec call-graph (--call-graph dwarf/fp/lbr)
- `perf top` : profiling en temps réel
- `perf annotate` : analyse instruction par instruction
- `perf mem` : analyse mémoire (chargements, stockages, latence)
- `perf c2c` : analyse false-sharing cache-line
- `perf sched` : analyse de scheduling (context switches, wakeups, latence)
- `perf stat --per-core --per-socket` : topologie NUMA
- Événements avancés : `perf list` pour découvrir — branch-misses, cache-misses, LLC-load-misses, L1-dcache-load-misses, frontend-retired, backend-retired

#### Intel VTune Profiler

- Analyse détaillée par micro-architecture (pipelines, ports, uops)
- **Hotspots :** identification des fonctions/vortex coûteux
- **Microarchitecture Exploration :** analyse d'issues — front-end bound, bad speculation, back-end bound, retiring
- **Memory Access :** analyse hiérarchie mémoire — bande passante, latence, cache misses, NUMA
- **Threading/HPC :** analyse parallélisme, synchronisation, threading
- **I/O :** analyse entrées/sorties bloc et réseau
- **HPC Performance Characterization :** roofline analysis (lié compute vs lié mémoire)
- **LBR (Last Branch Record) :** profilage précis avec stack hardware

#### Google gperftools

- **CPU Profiler :** échantillonnage statistique (SIGPROF) — `pprof` pour visualisation (text, graph, flamegraph, callgrind)
- **Heap Profiler :** allocation mémoire, fuites — `HEAPPROFILE` / `pprof --heap`
- **Heap Checker :** détection fuites mémoire (définies et flottantes)
- **tcmalloc :** allocateur mémoire performant (thread-caching, low fragmentation)

#### Valgrind

- **Memcheck :** détection erreurs mémoire — lectures invalides, writes out-of-bounds, use-after-free, fuites mémoire. Ralentissement ~10-30×
- **Cachegrind :** simulation cache I1/D1/L2 — misses, taux de hit. Ralentissement ~20×
- **Callgrind :** comme Cachegrind + call graph + event counting. Peut générer des profils compatibles KCachegrind
- **Helgrind/DRD :** détection data races, deadlocks dans programmes threadés
- **Massif :** profiling heap — évolution mémoire dans le temps, pics, fragmentation
- **BBV (Basic Block Vector) :** génération traces pour simulateur architectural
- **Nulgrind :** exécution sans instrumentation (validation overhead minimal)
- **DHAT :** type de fuite + allocation lifetimes

#### strace / ltrace

- **strace :** tracing appels système — fichiers, processus, réseau, signaux. Options clés : `-c` (statistiques), `-p` (PID attach), `-f` (suivi forks), `-e` (filtre), `-T` (timestamps syscall), `-r` (timestamps relatifs)
- **ltrace :** tracing appels bibliothèque — libc, libm, bibliothèques dynamiques

#### Profilage GPU

- **NVIDIA Nsight Compute (ncu) :** profiling kernel CUDA — occupancy, memory bandwidth, instruction mix, stall reasons
- **NVIDIA Nsight Systems (nsys) :** profiling système CPU+GPU — timeline kernel launches, memcpy, API calls
- **AMD ROCProfiler :** profiling ROCm/HIP
- **NVIDIA Visual Profiler / Nsight Graphics :** analyse visuelle GPU

### 4. Optimisation de Code

Techniques d'optimisation au niveau du code source et du compilateur.

#### Optimisation de Boucles

- **Loop unrolling** : déroulage pour réduire overhead de contrôle et améliorer ILP. Compromis : taille code vs vitesse
- **Loop tiling / blocking** : diviser en blocs pour améliorer locality cache. Paramètre clé : taille de bloc (taille cache L1/L2)
- **Loop interchange** : inverser boucles imbriquées pour accès mémoire contigu
- **Loop fusion / fission** : fusionner (réduire overhead) ou diviser (améliorer locality, faciliter vectorisation)
- **Loop invariant code motion (LICM)** : extraire calculs invariants hors boucle
- **Loop peeling** : extraire itérations irrégulières
- **Software pipelining** : réorganiser itérations pour chevaucher latences
- **Induction variable elimination** : remplacer variables d'induction par relations linéaires
- **Strength reduction** : remplacer opérations coûteuses par moins coûteuses (mul→shift/add, division→multiplication inverse)

#### Vectorisation SSE / AVX / NEON

- **SSE (Streaming SIMD Extensions) :** Intel — SSE (128-bit), SSE2, SSE3, SSSE3, SSE4.1, SSE4.2. Types : __m128 (float), __m128d (double), __m128i (int/char)
- **AVX (Advanced Vector Extensions) :** Intel/AMD — AVX (256-bit), AVX2 (256-bit entiers). Types : __m256, __m256d, __m256i
- **AVX-512 :** 512-bit — 32 registres ZMM. Sous-ensembles : F, CD (conflict detection), BW (byte/word), DQ (double/quad), VL (vector length), IFMA (integer FMA), VBMI (permute), VNNI (neural)
- **ARM NEON :** 128-bit SIMD — registres Q (128-bit) / D (64-bit). Types : float32x4_t, int32x4_t, uint8x16_t
- **SVE/SVE2 (Scalable Vector Extension) :** ARM — longueur vectorielle variable (128-2048 bits), prédication par vecteur
- **Auto-vectorisation :** flags GCC : `-O3 -ftree-vectorize -fopt-info-vec-missed`. Clang : `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize`
- **Intrinsics :** contrôle explicite — `<x86intrin.h>` (x86 SSE/AVX), `<arm_neon.h>` (ARM NEON), `<smmintrin.h>` (SSE4.1), `<immintrin.h>` (AVX/AVX2/AVX-512)
- **Alignement mémoire :** `__attribute__((aligned(64)))`, `_mm_malloc`, `posix_memalign` — alignement aux limites de cache line (64 octets)
- **Pragmas :** `#pragma GCC ivdep`, `#pragma omp simd`, `#pragma clang loop vectorize(enable)`
- **Considerations :** alignment, stride d'accès, gather/scatter (AVX2/AVX-512), masque, reduction, diviseurs vectoriels

#### Cache Locality

- **Principes de localité :** temporelle (réutilisation récente) et spatiale (accès contigus)
- **Hiérarchie mémoire :** L1 (32KB, latence ~1ns), L2 (256KB, ~4ns), L3 (8-32MB, ~10ns), RAM (~50-100ns), SSD (~50μs), disque (~10ms)
- **Cache line :** 64 octets (x86), alignement, false-sharing entre threads
- **Stride d'accès :** préférer stride=1 (contigu) — stride>1 gaspillage cache
- **Structure-oriented :** AoS (Array of Structs) → SoA (Struct of Arrays) pour accès par champ
- **Prefetching matériel :** détection stride, région de préchargement. Préchargement logiciel : `__builtin_prefetch`, `_mm_prefetch`
- **Cache blocking :** taille bloc adaptée à capacité cache L1/L2
- **NUMA (Non-Uniform Memory Access) :** latence variable selon socket. `numactl`, politiques `first-touch`/`bind`/`interleave`
- **TLB (Translation Lookaside Buffer) :** tailles de page (4KB vs 2MB huge pages), `transparent_hugepage`, `hugetlbfs`
- **Cache profiling :** `perf stat -e cache-misses`, Cachegrind, `perf c2c` pour false-sharing
- **Padded structs :** éviter false-sharing — `__attribute__((aligned(64)))`, padding `char _pad[60]`

#### Optimisations Compilateur

- **Niveaux d'optimisation GCC/Clang :** `-O0` (debug), `-O1` (basique), `-O2` (recommandé), `-O3` (agressif, vectorisation), `-Os` (taille), `-Og` (debug optimisé)
- **Flags avancés :** `-funroll-loops`, `-ftree-vectorize`, `-flto` (Link Time Optimization), `-fprofile-generate`/`-fprofile-use` (PGO), `-march=native`, `-mtune=native`
- **PGO (Profile-Guided Optimization) :** exécution instrumentée → optimisation orientée données réelles
- **BOLT (Binary Optimization and Layout Tool) :** post-link optimization de Facebook — réorganisation du code binaire
- **Optimisation de procédure :** inlining (`-finline-functions`), devirtualisation, constant propagation, dead code elimination, common subexpression elimination (CSE)
- **LTO (Link-Time Optimization) :** optimisations inter-modulaires — inlining cross-fichier, analyse globale
- **Branche prediction :** `__builtin_expect` / `[[likely]]` / `[[unlikely]]` (C++20), alignement de code chaud/froid

### 5. Systèmes d'Exploitation — Linux Kernel

Performance au niveau du noyau Linux.

#### Ordonnanceur (Scheduler)

- **CFS (Completely Fair Scheduler) :** politique SCHED_OTHER. Arbre rouge-noir de vruntime. Équité proportionnelle, nice values (-20 à 19). Latence cible (sched_latency_ns), granularité minimale (sched_min_granularity_ns)
- **EEVDF (Earliest Eligible Virtual Deadline First) :** remplacement de CFS dans Linux 6.6+. Ordonnancement basé sur échéance — meilleure isolation des charges de travail, latence prévisible pour tâches temps réel souples
- **Classes de scheduling :** SCHED_FIFO (priorité fixe, temps réel), SCHED_RR (round-robin, temps réel), SCHED_DEADLINE (EDF, latence garantie), SCHED_IDLE (basse priorité), SCHED_BATCH (batch, moins de preemptions), SCHED_EXT (sched_ext — BPF extensible, Linux 6.12+)
- **Group Scheduling :** groupes cgroup, hiérarchie CPU, partage équitable entre groupes
- **Cgroup v2 cpu controller :** configuration `cpu.weight`, `cpu.max` (limitation), `cpu.stat` (utilisation group/usage)
- **Métriques scheduler :** `perf sched`, `/proc/schedstat`, `/proc/PID/sched` (nr_switches, nr_voluntary_switches), `trace_sched_switch`, `trace_sched_wakeup`
- **Noyau temps réel :** PREEMPT_RT (Linux 6.12+), spinlock en mutex, gestion d'interruptions, priority inheritance
- **SMP / Affinité CPU :** `sched_setaffinity`, `taskset`, isolcpus, `nohz_full`, `rcu_nocbs` pour charges dédiées
- **Latence scheduler :** `sched_wakeup_granularity_ns`, wake-affine, `schbench`, `cyclictest` (rt-tests), `hackbench`

#### Gestion de la Mémoire (MM)

- **Allocation de pages :** buddy allocator (ordre 0-10), slab allocator (objets petits), kmem_cache, vmalloc
- **MMU / Pagination :** table des pages à 4 niveaux (PGD→PUD→PMD→PTE). Page faults, TLB misses, huge pages (2MB/1GB)
- **Swap :** mécanisme de swapping, `swappiness`, zswap/zram/zcache
- **OOM Killer :** surcharge mémoire — `oom_score`, `oom_score_adj`, `oom_adj`, politique `panic_on_oom`
- **NUMA mémoire :** politiques d'allocation (bind/preferred/local/interleave), `numad` démon, autonuma
- **Transparent Hugepages :** `always`/`madvise`/`never`, défragmentation, compactation mémoire
- **cgroup v2 memory controller :** `memory.max`, `memory.high`, `memory.low`, `memory.min`, `memory.current`, `memory.swap.max`, `memory.zswap.current`
- **Métriques MM :** `/proc/meminfo`, `/proc/buddyinfo`, `/proc/pagetypeinfo`, `/proc/zoneinfo`, `/sys/kernel/mm/transparent_hugepage/`
- **Outils :** `numactl`, `numastat`, `slabtop`, `procmem`, `/proc/PID/smaps`, `/proc/PID/numa_maps`
- **Memory reclaim :** kswapd, LRU (active/inactive), cgroup LRU, refault, PSI (Pressure Stall Information)

#### VFS (Virtual File System)

- **Architecture :** 4 couches — syscall VFS (open/read/write), namespace VFS, cache VFS (dentry, inode), filesystem (ext4, XFS, btrfs)
- **Dentry cache (dcache) :** cache des entrées de répertoires — hit rate, taille `nr_dentry`
- **Inode cache :** métadonnées de fichiers — hit rate, taille `nr_inode`
- **Page cache :** cache des pages de données — pages dirty vs clean, ratio hit/miss, writeback
- **Buffer cache :** métadonnées bloc — (sur Linux, intégré au page cache depuis 2.4)
- **Inodes :** search : éléments dans le dcache, hit rate via `/proc/sys/fs/dentry-state`
- **Sync / Writeback :** paramètres `dirty_ratio`, `dirty_background_ratio`, `dirty_expire_centisecs`, `dirty_writeback_centisecs`
- **Options mount :** `noatime`, `nodiratime`, `relatime`, `strictatime` — impact significant sur performance
- **io_uring :** interface async moderne (Linux 5.1+) — SQ (submission queue) + CQ (completion queue), zero-copy, sqpoll mode
- **Outils VFS :** `iostat -x`, `/proc/self/mountstats`, `fsstat`, `bcc/vfsstat.py`, `bpftrace` scripts VFS

#### Entrées/Sorties (I/O)

- **Modèles d'E/S :** synchrone, asynchrone (AIO/libaio), non-bloquant, io_uring, mmap, sendfile, splice
- **Stack bloc :** VFS → page cache → block layer → I/O scheduler → device driver
- **I/O Schedulers :**
  - **mq-deadline** : priorité lecture, fusion, deadline. Bon compromis général
  - **BFQ (Budget Fair Queueing) :** équité par processus, latence faible, idéal interactif/desktop
  - **Kyber :** contrôle de latence adaptatif, faible overhead
  - **none :** pas de réordonnancement (NVMe/SSD haut performance)
- **I/O metrics :** iops, throughput, latency (avg, p99, p999), queue depth, await, svctm, %util
- **NVMe :** files de soumission/complétion par cœur, polling mode, HP (HMB), SR-IOV
- **Multi-queue (blk-mq) :** files par CPU — `scsi_mod.use_blk_mq=1`, `nvme.poll_queues`
- **Outils I/O :** `fio`, `iostat -x 1`, `iotop`, `blktrace`, `blkparse`, `btt`, `seekwatcher`, `ioping`, `vdbench`
- **Storage tiers :** NVMe (3-10μs), SSD SATA (100μs), HDD (5-15ms), réseau (latence variable)
- **RAID :** RAID 0 (striping), RAID 1 (mirror), RAID 5/6 (parité), RAID 10 (striped mirror)
- **Filesystems :** ext4 (standard général), XFS (scale, fichiers gros), btrfs (COW, snapshots, compression), ZFS (COW, ARC, checksums), F2FS (flash), bcachefs

#### cgroups et Namespaces

- **cgroups v1 vs v2 :** v2 simplifié, hiérarchie unifiée, interface cohérente par `cgroup.controllers`/`cgroup.subtree_control`
- **Contrôleurs cgroup v2 :**
  - **cpu :** `cpu.weight` (poids relatif), `cpu.max` (limite dure — `quota period`)
  - **memory :** `memory.max`, `memory.high`, `memory.low`, `memory.min`, `memory.swap.max`, `memory.zswap.max`
  - **io :** `io.weight`, `io.max` (BPS iops par device)
  - **cpuset :** affinité CPU + mémoire NUMA, isolation
  - **pids :** limite de processus
  - **rdma :** contrôle RDMA
  - **hugetlb :** limite hugetlb
- **PSI (Pressure Stall Information) :** métriques temps réel de pression — `cpu`, `io`, `memory`. `some` (certains threads bloqués), `full` (tous bloqués)
- **Namespaces :** pid, net, mnt, uts, ipc, user, cgroup, time. Isolation conteneur (Docker/Podman/containerd)
- **Monitoring cgroup :** `systemd-cgtop`, `/sys/fs/cgroup/<path>/`, `podman stats`, `docker stats`, `cadvisor`

### 6. Performance GPU

#### GPU Computing

- **Architecture NVIDIA CUDA :** streaming multiprocessor (SM), warp (32 threads), block (grid de threads), global memory, shared memory, registers, constant memory, texture memory
- **Architecture AMD ROCm/HIP :** Compute Unit (CU), wavefront (64 threads — GCN; 32 — RDNA)
- **Modèle d'exécution :** host (CPU) ↔ device (GPU), kernel launches, stream/cudaStream, event/cudaEvent, synchronisation implicite/explicite
- **Transfère mémoire :** PCIe Gen4 (32 GB/s), Gen5 (64 GB/s). Coûteux — masquer par double buffering, streams asynchrones
- **Unified Memory :** `cudaMallocManaged` — migration automatique pages, prefetching (`cudaMemPrefetchAsync`). Overhead sur accès
- **CUDA Graphs :** capture kernel launches en graphe (réutilisation, optimisation overhead lancement)
- **Tensor Cores :** opérations matrix (D = A×B + C) — FP64, FP32, TF32, FP16, BF16, INT8, INT4. Idéal deep learning, HPC. `wmma` (warp matrix multiply-accumulate)

#### CUDA Occupancy

- **Définition :** ratio warps actifs / warps maximum par SM. Haute occupancy → meilleure latence hiding
- **Facteurs limitants :** registres par thread (max 255/thread, 65536/SM), shared memory par block, block size, warps per SM
- **Calculateur :** NVIDIA CUDA Occupancy Calculator / Nsight Compute occupancy section
- **Theoretical occupancy :** calcul basé sur ressources — `cudaOccupancyMaxActiveBlocksPerMultiprocessor`
- **Occupancy vs IPC :** haute occupancy ne garantit pas haute performance — IPC peut saturer avant. Équilibre à trouver
- **Optimisation :** réduire registres (`__launch_bounds__`), ajuster shared memory, choisir block size (256-512 commun)
- **Wavefront occupancy (AMD) :** similar — wavefronts simultanés par CU

#### Mémoire GPU et Bande Passante

- **Global memory :** principale mémoire GPU — haute bande passante (HBM2e ~2 TB/s A100, HBM3 ~3.35 TB/s H100), latence ~200-800 cycles
- **Shared memory :** mémoire on-chip rapide (L1 ~192KB/SM max). Utiliser pour données partagées intra-block. Latence ~30 cycles
- **Registers :** plus rapide — allocation par thread, taille limitée (65536/SM). Compilateur optimise automatiquement
- **Coalesced access :** threads consécutifs d'un warp accèdent à adresses mémoire contiguës → un seul transaction. Essentiel pour bande passante
- **Memory stride :** stride=1 idéal. Stride > 1 → transactions multiples. Stride large → gaspillage cache line
- **Constant memory :** 64KB, cache broadcast, idéal pour coefficients/filtres partagés par tous threads
- **Texture memory :** mise en cache optimisée pour accès spatial 2D/3D, interpolation hardware
- **HBM (High Bandwidth Memory) :** HBM2, HBM2e, HBM3. Large bus (1024-8192 bits), haute bande passante
- **L2 cache :** partagé par tous SMs — taille (40MB H100, 20MB A100). Band passante ~plus faible que L1
- **Outils mesure bande passante :** `bandwidthTest`, `cudaMemcpy` benchmarks, `cudaEvent` timers, Nsight Compute roofline analysis

### 7. Modélisation de Performance

#### Loi d'Amdahl

- **Formule :** `S(N) = 1 / ((1-P) + P/N)` où P = fraction parallélisable, N = nombre processeurs
- **Limite asymptotique :** `S(∞) = 1 / (1-P)` — le speedup maximum est limité par la partie séquentielle
- **Cas concret :** même 5% séquentiel → max 20× speedup
- **Interprétation :** pour accélérer un système, optimiser d'abord la partie séquentielle (non parallélisable)
- **Gustafson-Barsis :** contrepoint — « scaled speedup », le problème grandit avec les ressources : `S(N) = N - (N-1)×P`

#### Loi de Little

- **Formule :** `L = λ × W` — Longueur file = Taux arrivée × Temps service
- **Interprétation systèmes :** nombre moyen de requêtes dans le système = débit entrant × temps de réponse moyen
- **Applications :**
  - Dimensionnement capacité : requêtes simultanées = débit × latence
  - Calcul temps de réponse : `W = L / λ`
  - Validation mesure : cohérence entre débit mesuré, latence mesurée, concurrence observée
- **Cas file d'attente :** valide pour tout système en équilibre stationnaire, indépendant de la distribution

#### Théorie des Files d'Attente

- **Notation de Kendall :** A/S/c/K/m/Z — A=distribution arrivées (M=Markovien, D=Déterministe, G=Général), S=distribution service, c=nombre serveurs
- **Modèles clés :**
  - **M/M/1 :** arrivées Poisson, service exponentiel, 1 serveur. `W = 1/(μ-λ)`, ρ = λ/μ (utilisation), L = ρ/(1-ρ)
  - **M/M/c :** c serveurs parallèles. Probabilité attente = Erlang-C. Utilisation ρ = λ/(c·μ)
  - **M/D/1 :** service constant. `W = (2-ρ)/(2μ(1-ρ))` — meilleur que M/M/1 même arrival rate
  - **M/G/1 (Pollaczek-Khinchine) :** service général. `W = (λ(σ²+1/μ²))/(2(1-ρ)) + 1/μ`
  - **G/G/1 :** arrivées et service généraux — approximations (Kingman, Allen-Cuneen, Marchal)
- **Métriques :** ρ (utilisation), λ (taux arrivée), μ (taux service), W (temps dans système), Wq (temps attente), L (système), Lq (file), P(block), P(wait)
- **Réseaux de files :** Jackson networks (produit-forme), BCMP theorem, queuing network models (QNM)
- **Open vs closed :** systèmes ouverts (arrivées externes) vs fermés (utilisateurs limités, think time)

#### Analyse de Goulots

- **Resource utilization law :** `Ui = Xi × Si` (utilisation = débit × temps service)
- **Bottleneck identification :** ressource avec `Ui` le plus élevé ou avec le plus grand `Di` (demand service time)
- **Operational laws :** Forced Flow Law (`Xk = X0 × Vk`), Service Demand Law (`Di = Ui / X0`), Interactive Response Time Law (`R = N/X0 - Z`)
- **Asymptotic bounds :**
  - Limite débit : `X(N) ≤ min(1/Dmax, N/(D + Z))`
  - Limite temps de réponse : `R(N) ≥ max(D, N×Dmax - Z)`
- **Techniques :**
  - Shadow prices / bottleneck analysis
  - Roofline model (lié compute vs lié memory)
  - Balanced systems : `Dmax ≈ moyenne Di` → meilleur use des ressources
  - **Top-Down Analysis (microarchitecture) :** front-end bound, bad speculation, back-end bound, retiring — Intel VTune + PMU counters
- **Outils analyse goulots :** perf, VTune, flame graphs (CPU/off-CPU), USE method, RED method, Apollo (Uber), Jaeger (tracing distribué)

## Articles de Référence

### Analyse et Mesure

1. **Gregg, B. — "The USE Method: A Methodology for Performing an Exam of Utilization, Saturation, and Errors in a System"** — http://www.brendangregg.com/usemethod.html. Méthode systématique pour identification de goulots système.

2. **Gregg, B. — "Flame Graphs"** — http://www.brendangregg.com/flamegraphs.html. Visualisation de profilage CPU/off-CPU/memory/hot/cold.

3. **McDougall, R. et Mauro, J. — "Solaris™ Performance and Tools: DTrace and MDB"** (Prentice Hall, 2006). Fondations du tracing dynamique, concepts universels.

4. **Gregg, B. — "BPF Performance Tools"** (Addison-Wesley, 2019). Guide eBPF pour analyse performance Linux — bcc, bpftrace, flame graphs.

### Benchmarking

5. **Hennessy, J. et Patterson, D. — "Computer Architecture: A Quantitative Approach"** 6th ed. (Morgan Kaufmann, 2019). Chapitres 1-2 : benchmarks, Amdahl's law, CPU performance, SPEC.

6. **Dixit, K. — "The SPEC Benchmarks"** — Communications of the ACM, Vol. 34, No. 10, 1991. Fondations de la méthodologie SPEC.

7. **McVoy, L. et Staelin, C. — "lmbench: Portable Tools for Performance Analysis"** — USENIX 1996. Microbenchmarks système UNIX.

8. **Larus, J. — "Whole-Program Optimization with BOLT"** — ACM SIGPLAN Notices, Vol. 50, No. 6, 2015. Optimisation binaire post-link.

### Profilage

9. **Weidendorfer, J. et al. — "Cachegrind: A Cache Simulator for Performance Analysis"** — dans "Tools for High Performance Computing" (Springer, 2008). Simulation cache détaillée.

10. **Nethercote, N. et Seward, J. — "Valgrind: A Framework for Heavyweight Dynamic Binary Instrumentation"** — PLDI 2007. Architecture et instrumentation Valgrind.

11. **Intel Corporation — "Intel® 64 and IA-32 Architectures Optimization Reference Manual"** — Détails microarchitecture, compteurs hardware, optimisation assembly.

12. **Linux Man Pages — perf(1), perf stat(1), perf record(1), perf report(1)** — Documentation officielle Linux perf.

### Optimisation Code

13. **Intel Corporation — "Intel® 64 and IA-32 Architectures Software Developer Manuals"** — Volumes 1-4. Instructions SSE/AVX/AVX-512.

14. **ARM Ltd. — "ARM Cortex-A Series Programmer's Guide for ARMv8-A"** — Chapitres vectorisation NEON, cache, prefetching.

15. **Lam, M. et al. — "The Cache Performance and Optimizations of Blocked Algorithms"** — ASPLOS 1991. Loop tiling et blocking optimisés cache.

16. **GCC Team — "GCC Optimization Options"** — https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html. Flags et pragmas GCC.

### Systèmes d'Exploitation

17. **Love, R. — "Linux Kernel Development"** 3rd ed. (Addison-Wesley, 2010). Noyau Linux — scheduler, MM, VFS.

18. **Corbet, J. et al. — "Linux Device Drivers"** 3rd ed. (O'Reilly, 2005). Chapitre I/O, block drivers, mmap.

19. **Bovet, D. et Cesati, M. — "Understanding the Linux Kernel"** 3rd ed. (O'Reilly, 2005). Architecture interne, pagination, cache, I/O.

20. **Riegel, P. — "EEVDF Scheduler: A New Scheduling Policy for Linux"** — LWN.net, 2023. Analyse CFS→EEVDF, deadlines virtuels.

21. **Corbet, J. — "The v2 cgroup interface"** — LWN.net, 2015. Documentation cgroups v2, PSI.

22. **Axboe, J. — "io_uring: A New Asynchronous I/O Framework for Linux"** — Linux Foundation, 2019. Présentation du framework io_uring.

### Performance GPU

23. **NVIDIA Corporation — "CUDA C++ Programming Guide"** — https://docs.nvidia.com/cuda/cuda-c-programming-guide/. Architecture CUDA, optimisation mémoire, occupancy.

24. **NVIDIA Corporation — "CUDA Best Practices Guide"** — https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/. Stratégies optimisation kernels, coalescing, shared memory.

25. **Cook, S. — "CUDA Programming: A Developer's Guide to Parallel Computing with GPUs"** (Morgan Kaufmann, 2012). Fondamentaux GPU computing.

26. **AMD Corporation — "ROCm Programming Guide"** — Guide HIP/HCC, optimisation GPU AMD.

27. **Williams, S. et al. — "Roofline: An Insightful Visual Performance Model for Multicore Architectures"** — Communications of the ACM, 2009. Roofline model pour analyse compute vs memory bound GPU/CPU.

28. **Volkov, V. et Demmel, J. — "Benchmarking GPUs to Tune Dense Linear Algebra"** — SC 2008. Occupancy vs ILP, registres et bande passante CUDA.

### Modélisation

29. **Amdahl, G. — "Validity of the Single Processor Approach to Achieving Large-Scale Computing Capabilities"** — AFIPS 1967. Loi d'Amdahl.

30. **Gustafson, J. — "Reevaluating Amdahl's Law"** — Communications of the ACM, 1988. Gustafson-Barsis law, scaled speedup.

31. **Little, J. — "A Proof for the Queuing Formula: L = λW"** — Operations Research, Vol. 9, No. 3, 1961. Loi de Little.

32. **Kleinrock, L. — "Queueing Systems, Volume 1: Theory"** (Wiley, 1975). Théorie complète des files d'attente — M/M/1, M/G/1, réseaux.

33. **Lazowska, E. et al. — "Quantitative System Performance: Computer System Analysis Using Queueing Network Models"** (Prentice Hall, 1984). Analyse performance systèmes avec modèles de files.

34. **Gunther, N. — "Analyzing Computer System Performance with Perl::PDQ"** (Springer, 2011). Modèles de files pour systèmes modernes.

## Veille et Surveillance

### Sources académiques

- **arXiv cs.PF** : https://arxiv.org/list/cs.PF/recent — Performance (benchmarking, profilage, optimisation)
- **arXiv cs.OS** : https://arxiv.org/list/cs.OS/recent — Operating Systems (scheduler, MM, VFS, I/O)
- **ACM SIGMETRICS** : conférence internationale sur la mesure et modélisation de performance
- **USENIX ATC / OSDI / NSDI** : systèmes, OS, réseaux — articles de recherche appliquée
- **IEEE ISPASS** : analyse de performance et characterization de systèmes
- **IEEE HPCA / MICRO / ISCA** : architecture, performance hardware, microarchitecture
- **SC (Supercomputing)** : HPC, GPU computing, benchmarks haute performance
- **PACT** : Parallel Architectures and Compilation Techniques

### Communautés et conférences

- **Linux Kernel Mailing List (LKML)** : discussions scheduler, MM, VFS, io_uring, cgroups
- **LWN.net** : Linux Weekly News — analyses kernel, nouvelles fonctionnalités, performances
- **Brendan Gregg Blog** : https://www.brendangregg.com/ — analyse performance Linux, flame graphs, USE method, eBPF
- **Phoronix** : https://www.phoronix.com/ — benchmarks Linux, nouvelles hardware/drivers
- **Stack Overflow Performance** : tag [performance], [optimization], [c], [cuda]
- **NVIDIA Developer Blog** : optimisation CUDA, nouvelles architectures GPU
- **The New Stack / Performance** : articles performance conteneurs, cloud, microservices
- **Reddit r/programming** et r/cpp : optimisations code, benchmarking

### Outils de veille

- **arXiv API** : `curl -s "http://export.arxiv.org/api/query?search_query=all:performance+AND+all:benchmarking&sortBy=submittedDate&sortOrder=descending&max_results=10"`
- **LWN.net RSS** : https://lwn.net/headlines/ — kernel, performance, sécurité
- **Phoronix RSS** : https://www.phoronix.com/rss.php — benchmarks, hardware Linux
- **BlogWatcher (blogwatcher)** : surveiller blogs Brendan Gregg, LWN, Phoronix

### Mots-clés de surveillance

- `performance`, `benchmarking`, `profiling`, `optimization`
- `CPU scheduling`, `CFS`, `EEVDF`, `Linux kernel`, `NUMA`
- `CUDA occupancy`, `GPU optimization`, `vectorization`, `SIMD`
- `cache locality`, `cache misses`, `memory bandwidth`
- `Amdahl's law`, `Little's law`, `queueing theory`, `bottleneck analysis`
- `cgroups v2`, `io_uring`, `eBPF`, `perf events`, `flame graph`
- `SPEC CPU`, `SPECjbb`, `lmbench`, `Phoronix`, `Geekbench`
- `HPC`, `roofline model`, `latency`, `throughput`, `tail latency`