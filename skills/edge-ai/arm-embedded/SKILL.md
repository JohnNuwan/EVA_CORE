---
name: "arm-embedded"
description: "Architecture ARM embarquée — Cortex-M/R/A, programmation, debug, optimisation"
category: "edge-ai"
author: "E.V.A"
version: "1.0.0"
---

# Architecture ARM Embarquée

## Vue d'ensemble

Guide complet pour le développement sur architectures ARM en contexte embarqué (bare-metal, RTOS, Linux embarqué).

## Architectures

### Cortex-M (Microcontrôleur)
- **M0/M0+** : Von Neumann, 2-3 loads, pas de bit-banding, IT à 1 cycle
- **M3** : Harvard, 3 étages, bit-banding, division matérielle
- **M4** : M3 + FPU simple précision + DSP SIMD (SMLAD, SMLALD)
- **M7** : 6 étages, FPU double précision, cache L1 (I/D), TCM
- **M33/M55** : ARMv8-M, TrustZone, Helium (MVE)

### Cortex-R (Temps réel)
- **R4/R5** : Pipeline dual-issue, lockstep pour sécurité
- **R52** : ARMv8-R, hyperviseur, partitionnement temporel
- **R82** : 64-bit, MMU, Linux + RT sur même SoC

### Cortex-A (Application)
- **A5/A7/A8** : ARMv7-A, MMU, caches L1 séparés
- **A53/A55** : ARMv8-A, 64-bit, big.LITTLE
- **A72/A76/A78** : Haute performance, out-of-order
- **A78AE/X1** : Automobile/Edge, hétérogène

## Modes et Privilèges

```c
// Registre de contrôle (CONTROL) — Cortex-M
//   nPRIV  : 0=Thread privilégié, 1=Thread non privilégié
//   SPSEL  : 0=SP_main, 1=SP_process
//   FPCA  : 0=pas de frame FP actif

// Changement de mode via MSR (nécessite privilège)
__asm volatile("MSR CONTROL, %0" : : "r" (val) : "memory");
__asm volatile("ISB");
```

## Pipeline et Optimisation

### Cortex-M7
```
Étages : Fetch → Decode → Issue → Execute → Memory → Writeback
Branches : 2 cycles de pénalité (prédicteur BTB 512 entrées)
Load-use : 1 cycle de bulle (résolu par forwarding)
```

### Optimisations clés
1. **Alignement** : fonctions critiques sur 32-byte boundary
2. **IT blocks** : max 4 conditions, préférer if/else pour M7+
3. **TCM** : ISR et data temps réel dans TCM (0 wait-state)
4. **Section .text.ram** : code critique chargé en RAM au boot

```c
// Exemple : placer ISR en RAM
void __attribute__((section(".ramfunc"))) TIM2_IRQHandler(void) {
    // Code critique 0 wait-state
}
```

## Toolchain et Linker

### Startup et Linker Script

```ld
/* Régions mémoire typiques Cortex-M4 */
MEMORY {
    FLASH  (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
    RAM    (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
    CCMRAM (rw)  : ORIGIN = 0x10000000, LENGTH = 64K
}

SECTIONS {
    .vector_table : ALIGN(4) {
        LONG(ORIGIN(RAM) + LENGTH(RAM));  /* SP initial */
        LONG(Reset_Handler);              /* Reset */
        LONG(NMI_Handler);
        /* ... vecteurs ... */
    } > FLASH

    .text : {
        _stext = .;
        *(.text*)
        *(.rodata*)
        _etext = .;
    } > FLASH

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
}
```

### Startup Assembly

```assembly
    .syntax unified
    .cpu cortex-m4
    .thumb

    .global Reset_Handler
    .type Reset_Handler, %function

Reset_Handler:
    /* Copier .data de FLASH vers RAM */
    ldr   r0, =_sidata
    ldr   r1, =_sdata
    ldr   r2, =_edata
    subs  r2, r1
    ble   .L_zero_bss
.L_copy_data:
    ldrb  r4, [r0], #1
    strb  r4, [r1], #1
    subs  r2, #1
    bgt   .L_copy_data

.L_zero_bss:
    ldr   r1, =_sbss
    ldr   r2, =_ebss
    subs  r2, r1
    ble   .L_call_main
    movs  r3, #0
.L_zero_bss_loop:
    str   r3, [r1], #4
    subs  r2, #4
    bgt   .L_zero_bss_loop

.L_call_main:
    bl    main
    bkpt  #0
```

## Exception et Interruptions

### Table des vecteurs (Cortex-M)
```
Offset 0x00 : SP initial
Offset 0x04 : Reset
Offset 0x08 : NMI
Offset 0x0C : HardFault
Offset 0x10 : MemManage
Offset 0x14 : BusFault
Offset 0x18 : UsageFault
Offset 0x1C : (réservé)
...
Offset 0x40+ : IRQ 0..N (exceptions périphériques)
```

### NVIC (Nested Vectored Interrupt Controller)
```c
// Priorités — 4 bits (16 niveaux) sur M4
NVIC_SetPriority(USART1_IRQn, 0);  // Plus haute
NVIC_SetPriority(TIM2_IRQn, 10);   // Moyenne
NVIC_EnableIRQ(USART1_IRQn);
NVIC_EnableIRQ(TIM2_IRQn);

// PendSV — priorité minimale, déclenché par l'OS
NVIC_SetPriority(PendSV_IRQn, 15);
```

### Gestion des Faults
```c
void HardFault_Handler(void) {
    /* Lecture du CFSR (Configurable Fault Status Register) */
    uint32_t cfsr = SCB->CFSR;
    uint32_t hfsr = SCB->HFSR;
    uint32_t mmfar = SCB->MMFAR;
    uint32_t bfar = SCB->BFAR;

    if (cfsr & (1 << 0))  /* IACCVIOL — instruction fetch */
    if (cfsr & (1 << 8))  /* MSTKERR — stacking error */
    if (cfsr & (1 << 24)) /* DIVBYZERO — division par zéro */

    /* Sauvegarder le contexte pour debug */
    __asm volatile("TST LR, #4\n\t"
                   "ITE EQ\n\t"
                   "MRSEQ R0, MSP\n\t"
                   "MRSNE R0, PSP\n\t"
                   : : : "r0");
    // R0 pointe vers le frame empilé (R0-R3, R12, LR, PC, xPSR)
    while(1);
}
```

## FPU (Floating Point Unit)

### Activation (Cortex-M4/M7)
```c
/* Activer FPU dans CPACR */
SCB->CPACR |= (3 << 20) | (3 << 22);  // CP10 et CP11 full access
__asm volatile("DSB; ISB");

/* Modes FPU */
// LSPEN  : Lazy stacking (par défaut — frame FP empilé seulement si utilisé)
// ASPEN  : Automatic stacking (toujours empiler FP)
FPU->FPCCR |= (1 << 20);  // ASPEN=1, LSPEN=0
```

### Attributs pour forcer FP
```c
// Forcer l'utilisation de FPU dans une ISR
__attribute__((cmse_nonsecure_call)) void fpu_isr(void);
// Ou marquer la fonction avec attribut
__attribute__((__target__("fpu=fpv5-d16")))
```

## MPU (Memory Protection Unit)

```c
/* Configuration MPU — 8 régions, sous-régions */
void MPU_Config(void) {
    // Désactiver MPU
    MPU->CTRL = 0;

    // Région 0 : Flash (RO, privilégié seulement)
    MPU->RNR = 0;
    MPU->RBAR = 0x08000000;
    MPU->RASR = (0x1F << 1) |  // 512KB
                (0x1 << 16) |  // Full access (privilégié)
                (0x1 << 18) |  // XN: execute never
                (0x1 << 28);   // Enable

    // Région 1 : RAM (RW, user + privilégié)
    MPU->RNR = 1;
    MPU->RBAR = 0x20000000;
    MPU->RASR = (0x17 << 1) |  // 128KB
                (0x3 << 16) |  // RW full
                (0x1 << 28);

    // Activer MPU, background region = fault
    MPU->CTRL = (1 << 0) | (1 << 2);  // Enable + HFNMIENA
    __asm volatile("DSB; ISB");
}
```

## TrustZone (ARMv8-M)

### Séparation monde sécurisé / non-sécurisé
```c
// SAU — Security Attribution Unit
void SAU_Config(void) {
    SAU->CTRL = 0;  // Désactiver pendant config

    // Flash en non-sécurisé
    SAU->RNR = 0;
    SAU->RBAR = 0x08000000;
    SAU->RLAR = (0x0807FFFF) | 1;  // NS

    // RAM partagée
    SAU->RNR = 1;
    SAU->RBAR = 0x20000000;
    SAU->RLAR = (0x2001FFFF) | 1;

    // Périmètres sécurisés par défaut
    SAU->CTRL = 1;
}
```

## System Tick (SysTick)

```c
/* Timer 24-bit pour tick RTOS */
void SysTick_Config(uint32_t reload) {
    SysTick->LOAD = reload - 1;  // 1ms à 168MHz = 167999
    SysTick->VAL  = 0;
    SysTick->CTRL = (1 << 0) |  // ENABLE
                    (1 << 1) |  // TICKINT
                    (1 << 2);   // CLKSOURCE = core clock
}

void SysTick_Handler(void) {
    /* Incrémenter tick OS */
    uwTick++;
}
```

## Outils de Debug

### GDB + OpenOCD
```bash
# Lancer OpenOCD
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg

# GDB
arm-none-eabi-gdb build/firmware.elf
(gdb) target remote :3333
(gdb) monitor reset halt
(gdb) load
(gdb) continue
```

### Traces ITM/SWO
```c
// Activer ITM (Instrumentation Trace Macrocell)
ITM->LAR = 0xC5ACCE55;  // Unlock
ITM->TCR = (1 << 0) |   // ITM Enable
           (1 << 2) |   // SWO Enable
           (1 << 3);    // DWT Enable
ITM->TER[0] = 1;        // Port 0

// Envoyer caractère
void ITM_SendChar(char c) {
    while(!(ITM->STIM[0] & 1));
    ITM->STIM[0] = c;
}
```

## Pitfalls

1. **Stack Overflow** : Toujours configurer le MPU ou le stack guard (M3+)
2. **Data Alignment** : Cortex-M supporte l'accès non-aligné (sauf M0/M0+)
3. **Volatile** : Tous les registres mémoire-mappés doivent être `volatile`
4. **Section .data** : Vérifier que LOADADDR(.data) != ADDR(.data) dans le linker
5. **Interrupt Stacking** : 8 words minimum (M4 avec FPU = 26 words)
6. **Cortex-M0** : Pas de bit-banding, pas de divide hardware, 1 cycle IT
7. **MPU sur M7** : Utiliser le Data Side MPU (DMPU) pour le cache
8. **WFI/WFE** : Ne pas appeler WFI dans une boucle main sans event handler

## Ressources

- ARM Architecture Reference Manual ARMv7-M (DDI 0403)
- ARM Cortex-M7 Processor TRM (DDI 0489)
- ARMv8-M Architecture Reference Manual (DDI 0553)
- CMSIS-Core : https://github.com/ARM-software/CMSIS_5
- STM32Cube : https://github.com/STMicroelectronics/STM32Cube