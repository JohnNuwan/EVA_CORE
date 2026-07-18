---
name: language-assembly
title: "Doctorat — Assembleur"
description: "Compétence niveau docteur en assembleur. Couvre x86, x86-64, ARM64, RISC-V, AArch64, instruction encoding, calling conventions, stack frames, SIMD SSE/AVX/NEON, system calls, linker scripts, shellcode, reverse engineering, et optimisation."
category: research
lang: fr
---

# Doctorat : Assembleur

## Présentation
L'assembleur (ou langage d'assemblage) est le plus bas niveau de langage de programmation lisible par l'humain, correspondant directement au code machine exécuté par le processeur. Chaque architecture de CPU a son propre langage d'assemblage. L'assembleur est utilisé pour les parties les plus critiques des systèmes : bootloaders, noyaux de systèmes d'exploitation, drivers, code optimisé à la main, shellcode, reverse engineering, et firmware. Il offre un contrôle total du matériel : registres, mémoire, instructions, interruptions, et pipelines d'exécution.

## Histoire et Contexte
- 1940s : Premiers assembleurs pour les ordinateurs à tubes (EDSAC, ENIAC)
- 1950s : Assembleurs symboliques (FIT, SAP, SOAP)
- 1960s : MACRO-11 (PDP-11), IBM System/360 assembler
- 1970s : 8080, Z80, 6502 — microprocesseurs 8-bit
- 1978 : 8086/8088 (x86 16-bit) — début de l'architecture x86
- 1985 : 80386 — extension 32-bit (IA-32)
- 1997 : MMX — premières instructions SIMD
- 1999 : SSE (Streaming SIMD Extensions)
- 2000-2008 : SSE2, SSE3, SSSE3, SSE4
- 2003 : AMD64 (x86-64) — extension 64-bit
- 2008 : AVX (Advanced Vector Extensions)
- 2011 : ARMv8 (AArch64) — support 64-bit
- 2013 : AVX-512 (Xeon Phi puis Skylake Xeon)
- 2015 : RISC-V (architecture ouverte)
- 2020-2025 : AVX10, RISC-V maturation, ARM SVE/SVE2, custom extensions

## Architecture du Langage
- **Instructions** : Opcode + opérandes (registres, mémoire, immédiats)
- **Registres** : Banques de registres d'usage général et spécialisés
- **x86-64** : RAX, RBX, RCX, RDX, RSI, RDI, RBP, RSP, R8-R15
- **ARM64** : X0-X30 (registres généraux 64-bit), SP, PC, XZR
- **RISC-V** : x0-x31 (x0 est toujours zéro)
- **Flags/Status** : EFLAGS (x86), CPSR/NZCV (ARM), CSR (RISC-V)
- **Mémoire** : Adressage, segmentation (x86 legacy), pagination
- **Stack** : RSP (x86), SP (ARM), sp (RISC-V) — push/pop/call/ret
- **Program Counter** : RIP (x86-64), PC (ARM), pc (RISC-V)
- **Directives** : .data, .text, .bss, .align, .byte, .word, .quad

## Système de Types (Assembleur)
- **Bits** : Taille des opérandes (8-bit, 16-bit, 32-bit, 64-bit, 128-bit, 256-bit, 512-bit)
- **Immédiats** : Valeurs constantes dans l'instruction
- **Registres** : Types implicites par la largeur du registre
- **Mémoire** : Adresses, décalages, indexation
- **Étiquettes (labels)** : Symboles pour les adresses
- **x86 operand modifiers** : BYTE PTR, WORD PTR, DWORD PTR, QWORD PTR
- **ARM operand** : #imm (immédiat), {condition} (conditional execution)
- **RISC-V** : Immediate encoding variée (I, S, B, U, J types)
- **SIMD types** : __m128i (SSE), __m256i (AVX), __m512i (AVX-512)
- **Predicate registers** : ARM SVE, AVX-512 mask registers (k0-k7)

## Compilation et Interprétation
- **Assemblage** : .asm/.s → assembleur → .o (objet)
- **NASM** : Netwide Assembler — syntaxe Intel (x86/x86-64)
- **GAS** : GNU Assembler — syntaxe AT&T par défaut, Intel avec .intel_syntax
- **MASM** : Microsoft Macro Assembler — syntaxe Intel, Windows
- **FASM** : Flat Assembler — assembleur en assembleur, auto-hébergé
- **YASM** : Yet Another Assembler — NASM-compatible, support complet x86-64
- **Linker** : ld (GNU), lld (LLVM), LINK (MSVC) — édition de liens, résolution de symboles
- **Linker scripts** : Contrôle du layout binaire (adresses de sections, alignement)
- **objdump / readelf / nm** : Analyse de binaires
- **Disassembleur** : objdump -d, Ghidra, IDA Pro, Radare2
- **Inline assembly** : asm() en C/C++, __asm en MSVC

## Mémoire et Performances
- **Cache hierarchy** : L1 (32KB-64KB), L2 (256KB-1MB), L3 (8MB-64MB), L4 (optional)
- **Cache lines** : 64 octets — alignement critique pour les performances
- **TLB** : Translation Lookaside Buffer — cache de traduction d'adresses
- **Pipeline** : Fetch → Decode → Execute → Memory → Writeback
- **Out-of-order execution** : Exécution dans le désordre (Tomasulo algorithm)
- **Speculative execution** : Exécution spéculative — Spectre, Meltdown
- **Branch prediction** : Prédiction de branchement (BTB, RAS)
- **Memory types** : WB (Write-Back), WC (Write-Combine), UC (Uncacheable)
- **Prefetch** : PREFETCHT0/T1/T2, prefetchnta (x86)
- **NUMA** : Non-Uniform Memory Access — latence mémoire variable
- **Alignment** : Alignement des données sur les frontières de cache
- **False sharing** : Données de threads différents sur la même cache line

## Écosystème et Outils
- **Assembleurs** : NASM, GAS, MASM, FASM, YASM
- **Debuggers** : GDB (debug en assembleur), WinDbg, LLDB
- **Disassembleurs** : Ghidra (NSA), IDA Pro (Hex-Rays), Radare2 / rizin
- **Binary analysis** : Binary Ninja, Hopper, angr
- **Intel SDE** : Software Development Emulator (émulation d'instructions futures)
- **Compiler Explorer** : godbolt.org — visualisation du code assembleur
- **Intel Intrinsics Guide** : Documentation complète des instructions SIMD
- **uops.info** : Latence et throughput pour chaque instruction x86
- **Agner Fog's optimization manuals** : Référence pour l'optimisation x86
- **objdump / readelf / nm / size** : Outils de manipulation de binaires
- **Perf** : Linux perf — compteurs matériels (PMU)
- **Valgrind** : Cachegrind (cache simulation), Callgrind
- **LIEF** : Manipulation de binaires (PE, ELF, Mach-O)
- **RISC-V tools** : spike (simulateur), riscv-gnu-toolchain

## Concurrence et Parallélisme
- **SIMD (Single Instruction, Multiple Data)** : SSE, AVX, AVX-512, NEON, SVE
- **SSE** : 128-bit — float, double, int (SSE2)
- **AVX** : 256-bit — float, double, int (AVX2)
- **AVX-512** : 512-bit + masques — 32 registres (zmm0-zmm31)
- **AVX10** : AVX-512 simplifié pour tous les cœurs (P-cores + E-cores)
- **ARM NEON** : 128-bit SIMD (adv SIMD)
- **ARM SVE/SVE2** : Vector length agnostic — taille variable (128-2048 bits)
- **RISC-V V (Vector)** : Extension vectorielle (VLEN variable)
- **VLIW** (Very Long Instruction Word) : Itanium (IA-64), DSPs
- **SMT** (Simultaneous Multithreading) : Hyper-Threading
- **GPU assembly** : PTX (NVIDIA), GCN/CDNA (AMD), SPIR-V
- **Multi-core** : Caches cohérents (MESI, MOESI protocol)
- **Lock prefixes** : LOCK CMPXCHG, LOCK XADD — atomicité sur x86
- **Memory barriers** : MFENCE, SFENCE, LFENCE (x86) ; DMB, DSB (ARM)

## Patterns Avancés
- **Shellcode** : Code auto-suffisant sans null bytes, position-independent
- **NOP sled** : Série de NOP pour les exploits buffer overflow
- **ROP gadgets** : Return-Oriented Programming — chaînage de gadgets existants
- **PIC (Position Independent Code)** : Code relocalisable (GOT, PLT)
- **Trampoline** : Saut vers une fonction via un intermédiaire
- **Inline hooking** : Remplacement de code à l'exécution
- **TLS (Thread Local Storage)** : Accès aux variables par thread
- **VTable patching** : Détournement de tables virtuelles C++
- **Custom calling conventions** : Passer des paramètres dans des registres non standard
- **Self-modifying code** : Code qui se modifie à l'exécution (rare, déprécié)
- **Procedure Linkage Table** : Résolution dynamique de symboles (PLT/GOT)
- **Exception handling** : Tableaux d'exceptions (LSDA, SJLJ, DWARF)

## Optimisation
- **Instruction selection** : Choix de l'instruction la plus efficace
- **Register allocation** : Coloration de graphe, allocation de registres
- **Scheduling** : Ordonnancement des instructions pour le pipeline
- **Loop unrolling** : Déroulage de boucles pour réduire les branches
- **SIMD vectorization** : Instructions SIMD manuelles
- **Branch elimination** : CMOV (x86), CSEL (ARM), select (RISC-V)
- **Addressing modes** : Utilisation des modes d'adressage avancés
- **Prefixes** : REP, LOCK, xacquire/xrelease
- **Alignement** : Alignement des boucles et des sauts
- **Caching** : Prefetch manuel, cache blocking, streaming stores
- **Masked operations** : AVX-512 mask registers, ARM predicate
- **Constant folding** : Calcul de constantes à l'assemblage
- **Dead code elimination** : Suppression des instructions inutiles
- **Strength reduction** : Remplacement d'opérations coûteuses (mul → lea+add+shift)
- **VLIW scheduling** : Ordonnancement pour architectures VLIW

## Interopérabilité
- **Inline assembly in C/C++** : asm(), __asm__, __asm{} (MSVC)
- **Calling conventions** : System V AMD64 ABI (Linux), Microsoft x64 (Windows)
- **cdecl** : C declaration — paramètres sur stack (x86 32-bit legacy)
- **stdcall** : Callee cleanup (Win32 API)
- **fastcall** : Premiers paramètres dans registres (ecx, edx sur x86)
- **SysV AMD64** : RDI, RSI, RDX, RCX, R8, R9 (arguments), RAX (retour)
- **Microsoft x64** : RCX, RDX, R8, R9 (arguments), shadow space
- **ARM64 AAPCS** : X0-X7 (arguments), X0 (retour)
- **RISC-V** : A0-A7 (arguments), A0 (retour)
- **System calls** : syscall (x86-64), SVC (ARM), ecall (RISC-V)
- **Trap/Interrupt handlers** : IDT (x86), vector table (ARM), mtvec/stvec (RISC-V)
- **COM** : Interface binaire standard Microsoft
- **UEFI** : Firmware ABI (64-bit calling convention spécifique)

## Applications Industrielles
- **Noyaux de systèmes d'exploitation** : Linux, Windows, macOS — parties critiques en asm
- **Bootloaders** : GRUB, UEFI, BIOS — code de démarrage
- **Drivers** : Pilotes de périphériques (mode noyau)
- **Firmware** : BIOS/UEFI, microcontrôleurs, EC
- **Cryptographie** : Optimisation AES, SHA, RSA, ECC (instructions dédiées)
- **Codec media** : SSE/AVX pour vidéo (x264, x265, FFmpeg, dav1d)
- **Traitement d'images** : Filtres, transformations avec SIMD
- **Bases de données** : Optimisation de requêtes avec SIMD (ClickHouse, DuckDB)
- **Jeux vidéo** : Moteurs de rendu, calculs physiques optimisés
- **Reverse engineering** : Analyse de binaires, rétro-conception
- **Sécurité** : Shellcode, exploits, ROP chains, antivirus
- **Emulateurs** : QEMU, VirtualBox — traduction d'instructions
- **Moteurs JavaScript** : Génération de code assembleur (JIT)
- **Networking** : Paquets processing à haute vitesse (DPDK, XDP)
- **Spatial computing** : AR/VR — rendu optimisé
- **Automobile** : ECU — microcontrôleurs (ARM Cortex)

## Sécurité
- **Memory safety** : Aucune — l'assembleur permet d'écrire n'importe où
- **NX bit** : Non-Executable stack — empêche l'exécution de code sur la stack
- **ASLR** : Address Space Layout Randomization — randomisation des adresses
- **Stack canaries** : Protection stack overflow (GS, SSP)
- **CFG** : Control Flow Guard (Windows) — validation de cibles indirectes
- **CFI** : Control Flow Integrity — vérification des appels indirects
- **CET** : Control-flow Enforcement Technology (Intel) — shadow stack, IBT
- **PAC** : Pointer Authentication Code (ARMv8.3+)
- **BTI** : Branch Target Identification (ARMv8.5+)
- **Spectre / Meltdown** : Failles de sécurité des CPUs spéculatifs
- **MDS / L1TF / Fallout** : Side-channel attacks sur les CPUs
- **ROP / JOP prevention** : Protection contre Return-Oriented Programming
- **SEHOP** : Structured Exception Handling Overwrite Protection
- **Fuzzing** : libFuzzer, AFL — test des chemins d'exécution assembleur
- **Binary analysis** : Analyse de vulnérabilités dans le binaire

## Veille Technologique
- **Intel Architecture Manuals** : SDM (Software Developer's Manuals) — référence x86
- **AMD Programmer's Manuals** : Architecture x86-64 reference
- **ARM Architecture Reference Manual** : ARMv8-A, ARMv9-A
- **RISC-V Specification** : riscv.org — ISA specification
- **Agner Fog's manuals** : Optimisation x86
- **Intel Intrinsics Guide** : Instructions SIMD
- **WikiChip** : Encyclopédie des microprocesseurs
- **comp.arch** : Usenet newsgroup sur l'architecture
- **GCC / LLVM** : Release notes — nouveaux backends, optimisations
- **Hot Chips / ISSCC / MICRO** : Conférences architecture processeurs
- **YouTube** : Computerphile, Low Byte Productions, Tsoding
- **Livres** : "The Art of Assembly Language" (Hyde), "Assembly Language for x86 Processors" (Irvine), "Computer Organization and Design" (Patterson & Hennessy)
- **Évolutions clés** : AVX10, RISC-V extensions (Vector, Crypto), ARM SVE2, CHERI, memory tagging (MTE)