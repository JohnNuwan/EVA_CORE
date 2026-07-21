---
name: "risc-v-embedded"
description: "Architecture RISC-V embarquée — ISA, noyaux, toolchain, programmation bas niveau"
category: "edge-ai"
author: "E.V.A"
version: "1.0.0"
---

# RISC-V Embarqué

## Vue d'ensemble

Architecture RISC-V (ISA ouverte) pour systèmes embarqués : RV32I, extensions, noyaux (SiFive, Bouffalo, GD32V), toolchain, optimisation.

## ISA RISC-V

### RV32I — Base Integer (32-bit, 47 instructions)

```
Registres 32 × x0-x31
  x0 (zero) : toujours 0
  x1 (ra)   : return address
  x2 (sp)   : stack pointer
  x3 (gp)   : global pointer
  x4 (tp)   : thread pointer
  x5-7, x28-31 : temporaires (t0-t6)
  x8-9 (s0/s1) : sauvegardés (frame pointer)
  x10-17 : arguments (a0-a7) et retour (a0)
  x18-27 : sauvegardés (s2-s11)
```

#### Instructions clés

```assembly
# Arithmetic
add rd, rs1, rs2        # rd = rs1 + rs2
sub rd, rs1, rs2        # rd = rs1 - rs2
addi rd, rs1, imm       # immédiat signé 12-bit

# Logical
and/or/xor rd, rs1, rs2
andi/ori/xori rd, rs1, imm
slli/srli/srai           # shifts (imm 5-bit)

# Memory
lw rd, imm(rs1)          # load word (16-bit imm signé)
sw rs2, imm(rs1)         # store word
lb/lbu/lh/lhu/sb/sh

# Branches (compare + branch en une instr)
beq/bne/ blt/bge/bltu/bgeu rs1, rs2, offset

# Jumps
jal rd, offset           # jump and link (pc += offset, rd = pc+4)
jalr rd, rs1, imm        # indirect jump (rd = pc+4, pc = rs1+imm)
```

### Extensions standard (pour embarqué)

| Extension | Description | Noyaux typiques |
|-----------|-------------|-----------------|
| **M** | Multiplication/division matérielle | E31, GD32VF103 |
| **A** | Atomiques (LR/SC, AMO) | U54, BM25x |
| **F** | Flottant simple précision | FE310, GD32V |
| **D** | Flottant double précision | U74, E76 |
| **C** | Instructions compressées (16-bit) | Tous sauf micro |
| **Zb*X** | Bit manipulation (B) | E76, P550 |
| **Zicsr** | CSR (Control Status Registers) | Tous |
| **Zifencei** | Fence pour I-cache | Tous |

### Niveaux de privilèges

```
Machine (M)  : mode le plus privilégié — boot, ISR, gestion power
Supervisor (S) : MMU, pagination, OS (Linux)
User (U)     : applications utilisateur
```

Pour MCU embarqué : **M-mode seulement** (pas de S/U, pas de MMU).
Pour SoC avec Linux : **M+S+U**.

## CSR (Control and Status Registers)

### Accès

```assembly
csrr rd, csr            # read CSR → rd
csrw csr, rs1           # write rs1 → CSR
csrs/csrc csr, rs1      # set/clear bits via mask
csrrw rd, csr, rs1      # atomic read-write
```

### CSRs essentiels

```c
// Machine-mode
#define MSTATUS   0x300   // Status: MIE, MPIE, MPP, FS, XS
#define MIE       0x304   // Interrupt enable
#define MTVEC     0x305   // Trap vector base
#define MEPC      0x341   // Exception program counter
#define MCAUSE    0x342   // Cause
#define MTVAL     0x343   // Trap value (adresse mémoire/instruction)
#define MSCRATCH  0x340   // Scratch

// Machine-mode CSRs supplémentaires
#define MCYCLE    0xB00   // Cycle counter
#define MINSTRET  0xB02   // Instructions retired
#define MHPMCOUNTER3-31   // Performance counters matériels
```

### Vecteur de traps (MTVEC)

```c
// Mode Direct : base + cause * 4 (toutes les exceptions au même handler)
MTVEC_ADDR &= ~3;  // Mode Direct

// Mode Vectored : base alignée 256, chaque exception a son slot
MTVEC_ADDR = BASE | 1;  // Mode Vectored
```

## Startup RV32

```assembly
.section .init, "ax"
.globl _start
.type _start, @function

_start:
    /* Initialiser gp (global pointer) */
    la gp, __global_pointer$

    /* Initialiser sp (stack pointer) */
    la sp, _sp
    la tp, _sp       /* thread pointer = top of stack */

    /* Copier .data de LMA → VMA */
    la a0, _sidata
    la a1, _sdata
    la a2, _edata
    bgeu a1, a2, 2f
1:  lw t0, 0(a0)
    sw t0, 0(a1)
    addi a0, a0, 4
    addi a1, a1, 4
    bltu a1, a2, 1b

    /* Zéro .bss */
2:  la a0, _sbss
    la a1, _ebss
    bgeu a0, a1, 3f
    sw zero, 0(a0)
    addi a0, a0, 4
    j 2b

    /* Jump to main (via la pour éviter PC-relative limit) */
3:  la t0, main
    jr t0
    .size _start, .-_start
```

## Linker Script RISC-V

```ld
OUTPUT_ARCH(riscv)
ENTRY(_start)

MEMORY {
    FLASH (rx)  : ORIGIN = 0x20000000, LENGTH = 512K
    RAM   (rwx) : ORIGIN = 0x80000000, LENGTH = 128K
}

SECTIONS {
    .text : ALIGN(4) {
        KEEP(*(.init))
        *(.text*)
        *(.rodata*)
    } > FLASH

    /* Global pointer section — gp pointe ici */
    .sdata : ALIGN(4) {
        __global_pointer$ = . + 0x800;
        *(.sdata*)
    } > RAM AT > FLASH

    .data : ALIGN(4) {
        _sdata = .;
        *(.data*)
        _edata = .;
    } > RAM AT > FLASH
    _sidata = LOADADDR(.data);

    .bss : ALIGN(4) {
        _sbss = .;
        *(.bss*)
        *(COMMON)
        _ebss = .;
    } > RAM

    /* Stack */
    .stack : ALIGN(16) {
        _stack_start = .;
        . += 4K;
        _sp = .;
    } > RAM
}
```

## Interruptions (CLINT/PLIC)

### CLINT — Core Local Interruptor (tous les noyaux RISC-V)

```c
/* Registres CLINT */
#define CLINT_BASE      0x02000000
#define MSIP(hart)      (CLINT_BASE + 0x0000 + (hart * 4))
#define MTIMECMP(hart)  (CLINT_BASE + 0x4000 + (hart * 8))
#define MTIME           (CLINT_BASE + 0xBFF8)

/* Machine Timer Interrupt */
void timer_init(uint64_t interval_us) {
    uint64_t now = *((volatile uint64_t*)MTIME);
    uint64_t ticks = interval_us * (CPU_FREQ / 1000000);
    *((volatile uint64_t*)MTIMECMP(0)) = now + ticks;

    // Activer MTIE dans MIE
    asm volatile("csrsi mie, 0x80");
}

void timer_irq_handler(void) __attribute__((interrupt));
void timer_irq_handler(void) {
    /* Ack: reprogrammer cmp pour prochain tick */
    uint64_t now = *((volatile uint64_t*)MTIME);
    *((volatile uint64_t*)MTIMECMP(0)) = now + TICK_INTERVAL;
}
```

### PLIC — Platform Level Interrupt Controller

```c
/* PLIC pour 31 sources, 7 priorités */
#define PLIC_BASE        0x0C000000
#define PLIC_PRIORITY(i) (PLIC_BASE + (i * 4))
#define PLIC_ENABLE(h)   (PLIC_BASE + 0x2000 + (h * 0x80))
#define PLIC_THRESH      (PLIC_BASE + 0x200000 + (h * 0x1000))
#define PLIC_CLAIM(h)    (PLIC_BASE + 0x200004 + (h * 0x1000))

void plic_enable(int source, int priority) {
    volatile uint32_t* prio = (uint32_t*)(PLIC_PRIORITY(source));
    *prio = priority & 0x7;

    // Activer pour hart 0
    volatile uint32_t* en = (uint32_t*)(PLIC_ENABLE(0));
    *en |= (1 << source);
}

int plic_claim(void) {
    volatile uint32_t* claim = (uint32_t*)(PLIC_CLAIM(0));
    return *claim;
}

void plic_complete(int source) {
    volatile uint32_t* claim = (uint32_t*)(PLIC_CLAIM(0));
    *claim = source;
}
```

## Pipeline et Optimisation (RISC-V)

### Pipeline classique sur RV32IMAC

```
Fetch → Decode → Issue → ALU → Memory → Writeback
        ↑                   ↑
    Predicteur BTB     Forwarding
```

### Optimisations code

1. **gp-relative addressing** : `.sdata`/`.sbss` — accès 1 instr (addi) vs 2 (lui+addi)
2. **Instruction compressée C** : économise 30-40% de code flash
3. **Alignement** : target de branches sur 4-byte boundary
4. **Divisions** : éviter `div`/`rem` si possible (12-35 cycles vs 1 cycle add)
5. **Load/Store pairing** : regrouper lw/sw adjacents (pipeline)
6. **Zero register** : utiliser `addi rd, x0, imm` (pseudo = `li rd, imm`)

```c
// Avant (sous-optimal) :
int sum_tab(int *tab, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) s += tab[i];   // 1 lw, 1 add par iteration
    return s;
}

// Après (optimisé — déroulage) :
int sum_tab_fast(int *tab, int n) {
    int s0 = 0, s1 = 0, s2 = 0, s3 = 0;
    int i = 0;
    for (; i + 3 < n; i += 4) {
        s0 += tab[i];   // Peut être pipeline : chaque lw indépendant
        s1 += tab[i+1];
        s2 += tab[i+2];
        s3 += tab[i+3];
    }
    for (; i < n; i++) s0 += tab[i];
    return s0 + s1 + s2 + s3;
}
```

## Toolchain RISC-V

```bash
# Installation
# GCC
sudo apt install gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf

# Ou build manuel
git clone https://github.com/riscv-collab/riscv-gnu-toolchain
cd riscv-gnu-toolchain
./configure --prefix=/opt/riscv --with-arch=rv32imac --with-abi=ilp32
make -j$(nproc)

# Compilation
riscv64-unknown-elf-gcc -march=rv32imac -mabi=ilp32 -O2 -c main.c -o main.o
riscv64-unknown-elf-gcc -T linker.ld main.o -o firmware.elf
riscv64-unknown-elf-objcopy -O binary firmware.elf firmware.bin

# OpenOCD + GDB
openocd -f board/sifive-hifive1.cfg
riscv64-unknown-elf-gdb firmware.elf -ex "target remote :3333" -ex "load"
```

## Noyaux RISC-V Embarqués

| Noyau | ISA | Fabriquant | Cas d'usage |
|-------|-----|-----------|-------------|
| SiFive E21 | RV32IMAC | SiFive/QuickLogic | IoT basse conso |
| SiFive E31 | RV32IMAC | SiFive | MCU généraliste |
| SiFive U54 | RV64IMAFDC | SiFive | Linux embarqué |
| GD32VF103 | RV32IMAC | GigaDevice | MCU (remplace STM32F1) |
| BL602/BL702 | RV32IMAF | Bouffalo | WiFi/BLE IoT |
| Bouffalo M1s | RV32IMFC | Bouffalo | Audio/Display |
| P550 | RV64IMAFDC | Andes Tech | Auto/Industriel |
| V85xx | RV32IMC | WCH (WCH) | MCU bas coût |
| Kendryte K210 | RV64IMAFDC | Canaan | Vision/ML Edge |

## Pitfalls

1. **gp (Global Pointer)** : Doit pointer au bon endroit dans `.sdata` pour que gp-relative addressing fonctionne
2. **Stack** : Vérifier _sp dans le linker — aucun stack overflow détection sans MPU
3. **Multiplication (M)** : Les noyaux sans extension M n'ont que mulh/mulhu — vérifier -march
4. **CSR atomique csrs/csrc** : Nécessite extension Zicsr (présente partout en pratique)
5. **Misaligned access** : RV32I supporte les accès non-alignés (mais plus lents). Certains noyaux (K210) ne les supportent PAS
6. **Zifencei** : Le Fence pour instruction cache est optionnel dans certaines implémentations
7. **Interrupt stacking** : Pas de hardware stacking automatique comme ARM — le handler doit push/pop manuellement
8. **Wait for Interrupt (WFI)** : Pas d'instruction dédiée — `wfi` est une pseudo-instr qui fait csrrc avec MIE=0

## Ressources

- RISC-V Unprivileged Spec v20191213 : https://riscv.org/technical/specifications/
- RISC-V Priviledged Spec v20211203
- SiFive FE310-G000 Manual
- GD32VF103 User Manual
- BLE BL602 Reference Manual