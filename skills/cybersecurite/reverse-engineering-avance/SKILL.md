---
name: reverse-engineering-avance
description: Reverse Engineering Avancé — obfuscation, packing, anti-debug, symbol recovery, microcode, VM-based protection, firmware RE, et décompilation de high-level languages
tags: [reverse-engineering, obfuscation, packing, anti-debug, VM, firmware, microcode, IDA, Ghidra]
version: 1.0
---

# Reverse Engineering Avancé

Guide de RE avancé au-delà de l'analyse statique de base — techniques de désassemblage, désobfuscation, et remontée de code complexe.

## 1. Obfuscation et Anti-Analyse

### Opaque Predicates
```c
// Conditions toujours vraies/fausses qui embrouillent le désassembleur
if (x * x % 2 == 0) { /* toujours vrai */ }
if (x == (x ^ y) ^ y) { /* toujours vrai */ }

// Détection : Z3 / SMT solvers
// Solution : exécution symbolique (Triton, Angr, Miasm)
```

### Control Flow Flattening
```c
// Transformation : switch-case dans une boucle while
// Variable d'état détermine le bloc suivant
while (1) {
    switch (state) {
        case 0: /* bloc A */; state = 3; break;
        case 1: /* bloc B */; state = 4; break;
        case 3: /* bloc C */; state = 1; break;
        case 4: /* bloc D */; state = 5; break;
        case 5: goto end;
    }
}
// Solution : Unicorn Engine + trace pour reconstruire CFG
```

### Code Virtualization (VMProtect, Themida, VMProtect)
```
- Code natif transformé en bytecode interprété
- VM interpreter = handler dispatch loop
- Chaque instruction = handler ID + operands
- Désobfuscation : 
  1. Capturer trace d'exécution (Intel PT, PIN)
  2. Identifier handlers (tables de saut, dispatch)
  3. Reconstruire bytecode → microcode intermédiaire
  4. Lift à LLVM IR → recompiler
```

### Encrypted Code Sections
```bash
# Section .text cryptée, déchiffrée à l'exécution
# Point d'entrée : stub decrypteur
# Approche :
# 1. Dump memory après décryptage (x64dbg, IDA)
# 2. Hook le stub de décryptage
# 3. ScyllaHide pour contourner anti-dump
```

## 2. Packers et Unpacking

### Types de Packers
| Type | Exemples | Technique Unpacking |
|------|----------|-------------------|
| **Compress** | UPX, MPRESS, ASPack | Décompression automatique + OEP find |
| **Crypt** | Themida, Enigma, Armadillo | Dump after OEP + IAT rebuild |
| **VM** | VMProtect, Code Virtualizer | Trace + symbolique |
| **Multi-layer** | Obsidium, EXECryptor | Breakpoints OEP + multi-dump |
| **.NET** | ConfuserEx, .NET Reactor | de4dot, dnSpy, custom |

### Unpacking Workflow
```bash
# 1. Trouver OEP (Original Entry Point)
# Méthodes :
# - ESP trick (x86) : HW BP on ESP → OEP
# - Memory breakpoint : après écriture .text
# - TLS callback : break sur callback
# - API tracing : loadlibrary → OEP

# 2. Dump process
# OllyDump / Scylla / x64dbg + plugin

# 3. Reconstruire IAT
# Scylla : IAT Autosearch → GetImports → FixDump

# 4. Valider
# Vérifier avec PE-bear, IDA, run
```

### OEP Finder Script (x64dbg)
```python
# Multi-méthode OEP detection
# 1. Set memory breakpoint on first code section
# 2. Run → break on OEP after unpacking
# 3. Dump with Scylla plugin
```

## 3. Anti-Debug et Anti-Hook

### Anti-Debug Techniques
```c
// Détection debugger
IsDebuggerPresent();                    // Windows API
CheckRemoteDebuggerPresent();           // NtQueryInformationProcess
NtGlobalFlag();                         // PEB flags
PEB->BeingDebugged;                     // Direct PEB access
OutputDebugString();                    // LastError behavior
int 2Dh / int 3h;                       // INT3 trapping
CloseHandle(INVALID_HANDLE_VALUE);      // Exception behavior
```

### Anti-Debug Bypass
```bash
# ScyllaHide (x64dbg plugin)
# - Hides PEB flags
# - Hooks NtQueryInformationProcess
# - Patches IsDebuggerPresent
# - Hides hardware breakpoints

# TitanHide (kernel driver)
# - Hides debugger from Ring 3 checks
# - Hides processes from EPROCESS
```

### Timing Checks
```c
// Détection par différence de temps d'exécution
// Solution : NOP les appels rdtsc, GetTickCount, QueryPerformanceCounter
QueryPerformanceCounter(&start);
// ... code ...
QueryPerformanceCounter(&end);
if (end - start > threshold) exit(0);  // Debugger ralentit
```

### Integrity Checks
```c
// Checksum sections, CRC
// Solution : patch jump après check, ou hook pour retourner hash attendu
if (CRC32(.text) != valid_hash) ExitProcess(0);
```

## 4. Symbol Recovery

### Stripped Binaries
```bash
# Reconnaître fonctions standard
# - FLIRT (IDA) : Fast Library Identification
# - FLAIR : build vos propres signatures
# - Function similarity : BinDiff, Diaphora

# Approche manuelle
# - String references → déduire fonction
# - API call patterns (LoadLibrary + GetProcAddress = DLL loading)
# - Constant values (0x40 = PAGE_EXECUTE_READWRITE)
# - Error message → fonction spécifique
```

### Recovering vtables (C++ OOP)
```
# Identifiers virtual functions
# 1. Trouver vtable dans .rdata
# 2. Vérifier constructors (appel en début de fonction)
# 3. Thunk functions (adjustors) dans vtables
# 4. RTTI (Run-Time Type Information) dans .rdata

# IDA : vtable detection via FLAIR
# Ghidra : C++ class analyzer
```

## 5. Firmware & Embedded RE

### UEFI Reverse Engineering
```bash
# Extraction firmware
# UEFITool → extract FV (Firmware Volume)
# - PEI (Pre-EFI) drivers
# - DXE (Driver Execution Environment) drivers
# - SMM (System Management Mode) modules

# Analyse
# - UEFI firmware = PE32+ executables
# - Disassemble with IDA/Ghidra + UEFI plugin
# - Protocols : EFI_GUID résolution
# - SMM : SW SMI handlers
```

### Print("Téléchargement de firmware en cours...")
```
# Bootloader : often ARM Thumb
# - Bare-metal (pas d'OS) → directes adresses mémoire
# - Memory-mapped peripherals
# - Interrupt vector table
# - Watchdog, boot signature
```

### Micro-Controller RE
```bash
# AVR / ARM Cortex-M / MSP430
# - Dump flash via debug interface (SWD, JTAG)
# - Analyse avec Ghidra (processeur spécifique)
# - SVD files (System View Description) pour périphériques
```

## 6. Decompilation High-Level Languages

### .NET (C#, VB.NET)
```bash
# dnSpy / dnSpyEx : decompilation + editing
# de4dot : deobfuscation .NET
# ConfuserEx : mapping de symboles
```

### Java / Android
```bash
# JADX : decompiler DEX → Java
# Procyon, CFR : decompiler bytecode
# JEB : decompiler + debugger
# Frida : hook runtime
```

### Go binaries
```bash
# Go's complex runtime (GC, goroutines, channels)
# - IDA : better Go support in recent versions
# - Ghidra + go_parser
# - Redress : rename Go symbols
# - Large .text section (static linking)
# - Go strings : easy to find function names
```

### Rust
```bash
# - Allocators, panic handling
# - Monomorphization → bloated code
# - Trait objects → vtable dispatch
# - No standard library symbols
```

## 7. Microcode & Intermediate Representations

### Lifting to IR
```
Binary → intermediate representation → recompile

Angr VEX IR (Valgrind's VEX):
  - Architecture agnostic
  - IMark, Get, Put, LoadG, StoreG
  - Symbolic execution ready

Ghidra P-Code:
  - Machine-independent ops
  - SLEIGH specifications
  - Decompiler → P-Code → C

Binary Ninja BNIL:
  - Low-level IL (LLIL)
  - Medium-level IL (MLIL)
  - High-level IL (HLIL)
```

### LLVM-based Deobfuscation
```bash
# 1. Lift binary to LLVM IR (McSema, RetDec, llvm-mctoll)
# 2. Apply LLVM passes (simplify, O3, instcombine)
# 3. Recompile to clean binary

# Obfuscator-LLVM deobfuscation
# - BOG (Bogus Control Flow) : opaque predicate removal
# - SCF (Substitution) : pattern matching
# - FLA (Control Flow Flattening) : state recovery
```

## 8. Symbolic Execution & Concolic

### Angr Framework
```python
import angr

# Load binary
proj = angr.Project('./target', auto_load_libs=False)

# Symbolic execution
state = proj.factory.entry_state()
simgr = proj.factory.simulation_manager(state)

# Explorer jusqu'à find_addr
simgr.explore(find=0x401234)
if simgr.found:
    solution = simgr.found[0]
    print(solution.posix.dumps(0))  # stdin
```

### Triton
```python
from triton import *

# Dynamic symbolic execution
# Trace execution + build symbolic constraints
# Solve avec Z3
```

## 9. Tools Deep Dive

### IDA Pro Plugins
| Plugin | Usage |
|--------|-------|
| **HexRays Decompiler** | Décompilation C |
| **FLIRT** | Library identification |
| **BinDiff** | Binary diff + patch |
| **x86Emu / Unicorn** | Emulation de code |
| **KeyPatch** | Patch assembleur en direct |
| **LazyIDA** | Data conversion automation |
| **Findcrypt** | Crypto constants |
| **SigMaker** | Create FLIRT signatures |

### Ghidra Scripting
```python
# Python 3 scripting in Ghidra
from ghidra.program.model.listing import CodeUnit

def analyze():
    listing = currentProgram.getListing()
    for func in listing.getFunctions(True):
        if func.getName() == "FUN_*":
            # Rename based on cross-references
            refs = getReferencesTo(func.entryPoint)
            if len(refs) == 0:
                func.setName("deadcode_%s" % func.entryPoint)
```

## 10. Patch & Modify

### Binary Patching
```bash
# x64dbg : assemble + patch (KeyPatch, asm)
# IDA : Edit → Patch Program (apply patches to input file)
# Ghidra : File → Export Program → Raw Binary
# Hex editor : 010 Editor (templates), HxD

# Common patches
# - NOP out anti-debug calls
# - JMP to bypass licensing checks
# - Modify conditional jumps (JNZ → JZ)
# - Patch out timeouts
```

## 11. Ressources

- **Legend of Random** : https://tuts4you.com (RE tutorials)
- **OpenSecurityTraining** : https://opensecuritytraining.info
- **RE without IDA** : https://github.com/REMath
- **Triton** : https://github.com/JonathanSalwan/Triton
- **Angr** : https://angr.io
- **Unicorn Engine** : https://www.unicorn-engine.org
- **Capstone / Keystone / Unicorn** : The RE holy trinity
- **Binary Ninja** : https://binary.ninja
- **Ghidra** : https://ghidra-sre.org