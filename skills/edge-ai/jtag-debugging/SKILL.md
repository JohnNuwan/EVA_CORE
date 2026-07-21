---
name: "jtag-debugging"
description: "Debug embarqué — JTAG, SWD, OpenOCD, GDB, trace, boundary scan, analyse de crash"
category: "edge-ai"
author: "E.V.A"
version: "1.0.0"
---

# Debug Embarqué — JTAG, SWD, Trace

## Vue d'ensemble

Infrastructure de debug pour systèmes embarqués : JTAG (IEEE 1149.1), SWD (Serial Wire Debug), OpenOCD, GDB, trace ETM/ITM, boundary scan, analyse de crash sur ARM et RISC-V.

## JTAG (IEEE 1149.1)

### Signaux

```
JTAG — 5 signaux essentiels
┌──────────┐
│   TDI    │ Test Data In — entrée série
│   TDO    │ Test Data Out — sortie série
│   TCK    │ Test Clock — horloge (10-100 MHz)
│   TMS    │ Test Mode Select — contrôle de la machine d'états
│   nTRST  │ Reset (optionnel) — reset TAP controller
└──────────┘

ARM SWD (2 fils) : SWDIO (bi-directionnel), SWCLK (horloge)
```

### TAP (Test Access Port) — Machine d'états

```
                ┌─────────────┐
                │  Test-Logic │
                │   -Reset    │
                └──────┬──────┘
                       │ TMS=1
                ┌──────▼──────┐
                │   Run-Test  │
                │   /-Idle    │
                └──────┬──────┘
          ┌─────────────┼─────────────┐
          │ TMS=1       │ TMS=0       │ TMS=1
    ┌─────▼────┐  ┌─────▼────┐  ┌─────▼────┐
    │ Select-  │  │ Select-  │  │  Capture-│
    │ DR-Scan  │  │ IR-Scan  │  │    DR    │
    └─────┬────┘  └─────┬────┘  └─────┬────┘
          │             │             │
    ┌─────▼────┐  ┌─────▼────┐  ┌─────▼────┐
    │ Capture- │  │ Capture- │  │ Shift-   │
    │   DR     │  │   IR     │  │   DR     │
    └─────┬────┘  └─────┬────┘  └─────┬────┘
          │             │             │
    ┌─────▼────┐  ┌─────▼────┐  ┌─────▼────┐
    │ Shift-   │  │ Shift-   │  │ Exit1-   │
    │   DR     │  │   IR     │  │   DR     │
    └─────┬────┘  └─────┬────┘  └─────┬────┘
          │             │             │
    ┌─────▼────┐  ┌─────▼────┐  ┌─────▼────┐
    │ Exit1-   │  │ Exit1-   │  │ Update-  │
    │   DR     │  │   IR     │  │   DR     │
    └─────┬────┘  └─────┬────┘  └─────┬────┘
          │             │             │
    ┌─────▼────┐     ┌──▼──┐
    │ Update-  │     │ ... │
    │   DR     │     └─────┘
    └─────┬────┘
          │
          └──→ Run-Test/Idle
```

### Boundary Scan

```c
// Test de connectivité entre BGA — pas de sonde
// Pattern : EXTEST → vérifier interconnexions
// Pattern : SAMPLE → capturer l'état des pins sans stopper
// Pattern : BYPASS → chaîne 1-bit pour les composants non testés

// Exemple BSDL (Boundary Scan Description Language)
-- STM32F407 Boundary Scan
entity STM32F407 is
    generic (PHYSICAL_PIN_MAP : string := "LQFP176");
    port (
        TDI : in bit;
        TDO : out bit;
        TMS : in bit;
        TCK : in bit;
        -- Pins périphériques
        PA0 : inout bit;
        PA1 : inout bit;
        ...
    );
    attribute BOUNDARY_LENGTH of STM32F407 : entity is 144;
    attribute BOUNDARY_REGISTER of STM32F407 : entity is
        -- cell 0 (PA0) : control=0, disable=0, safe=Z
        "0 (BC_1, PA0, input, X)," &
        "1 (BC_1, PA0, output3, X, 2, 0, Z)," &
        ...
    ;
end STM32F407;
```

## SWD (Serial Wire Debug) — ARM spécifique

### Protocole

```
SWDIO : bi-directionnel (données + contrôle)
SWCLK : horloge

Paquet SWD :
┌──────────────────────────────────────────────────┐
│ Start │ APnDP │ RnW  │ A[2:3]│ Parity │ Stop │ Park│
│   1   │  1    │  1   │   2   │   1    │  0   │  1  │
└───────┴───────┴──────┴───────┴────────┴──────┴─────┘
┌──────────────────────────────────────────────────┐
│ ACK[2:0] │ Data[32] │ Parity │  (réponse)       │
│  3 bits  │  32 bits │   1    │                   │
└──────────┴──────────┴────────┘

ACK : OK=001, WAIT=010, FAULT=100
```

### AP (Access Port) et DP (Debug Port)

```c
// DP (Debug Port) — registres
#define DP_IDCODE   0x00  // Identification
#define DP_ABORT    0x00  // Annulation
#define DP_CTRL_STAT 0x04 // Contrôle
#define DP_WCR      0x04  // Wire Control Register
#define DP_RESEND   0x08  // Resend last data
#define DP_RDBUFF   0x0C  // Read buffer

// AP (Access Port) — mémoires
// MEM-AP : accès mémoire via APB-AP ou AHB-AP
// Le SELECT (DP 0x08) choisit l'AP
// Puis CSW (0x00), TAR (0x04), DRW (0x0C)

// Lecture mémoire via SWD (deux phases) :
// 1. Write TAR (Target Address Register)
// 2. Read DRW (Data Read/Write) — lecture différée
```

## OpenOCD

### Configuration

```tcl
# openocd.cfg — STM32F4 + ST-Link
source [find interface/stlink.cfg]
transport select hla_swd  # ou hla_jtag

source [find target/stm32f4x.cfg]

# Reconfiguration ad-hoc
set CHIPNAME stm32f407
set WORKAREASIZE 0x4000

# Debug avec reset halt
reset_config srst_only srst_nogate

# Vars
$_TARGETNAME configure -event gdb-attach {
    echo "GDB attaché, halt..."
    halt
}
```

### Commandes OpenOCD utiles

```tcl
# Debug
reset halt                     # Reset puis stop
halt                           # Arrêter CPU
resume                         # Reprendre
step                           # Pas à pas
reg                            # Afficher tous les registres
reg r0 0x42                    # Modifier registre
mdw 0x20000000 16              # Memory display word
mww 0x20000000 0xDEAD          # Memory write word

# Flash
flash write_image erase build/firmware.elf
flash write_bank 0 firmware.bin 0x08000000
flash erase_sector 0 0 3       # Effacer secteurs 0-3
flash protect 0 0 3 off        # Déprotéger

# JTAG chain
jtag newtap stm32 cpu -irlen 4 -expected-id 0x2BA01477
scan_chain                     # Voir la chaîne JTAG
tapdisable                     # Désactiver un TAP

# Profiling
profile 1000                   # Échantillonner PC pendant 1s
reset; profile 5000            # Profiler le boot
```

## GDB Intégré

### Fichier .gdbinit

```gdb
# .gdbinit — Debug embarqué
set pagination off
set confirm off
set print pretty on
set architecture armv7e-m

target extended-remote :3333
monitor reset halt
monitor flash write_image erase build/firmware.elf
load

# Hardware breakpoints (ARM Cortex-M : 6 HW breakpoints)
set breakpoint auto-hw
break main
break HardFault_Handler
break SysTick_Handler

# Watchpoints (4 HW watchpoints)
watch *(uint32_t*)0x40020000  # GPIOA ODR

# Profiling
set $pc_sample = 0
define profile
    while $pc_sample < 1000
        stepi
        set $pc_sample = $pc_sample + 1
    end
    info registers r0 r15
end
```

### Scripts GDB avancés

```gdb
# Analyse HardFault
define hardfault_analyze
    # Récupérer le frame empilé
    set $lr = $lr
    if ($lr & 0x4)
        # PSP (Process Stack Pointer)
        set $sp = $psp
    else
        # MSP (Main Stack Pointer)
        set $sp = $msp
    end

    printf "R0  = 0x%08X\n", *(uint32_t*)($sp + 0)
    printf "R1  = 0x%08X\n", *(uint32_t*)($sp + 4)
    printf "R2  = 0x%08X\n", *(uint32_t*)($sp + 8)
    printf "R3  = 0x%08X\n", *(uint32_t*)($sp + 12)
    printf "R12 = 0x%08X\n", *(uint32_t*)($sp + 16)
    printf "LR  = 0x%08X\n", *(uint32_t*)($sp + 20)
    printf "PC  = 0x%08X\n", *(uint32_t*)($sp + 24)
    printf "xPSR= 0x%08X\n", *(uint32_t*)($sp + 28)

    # Lire les registres de fault
    set $cfsr = *(uint32_t*)0xE000ED28
    printf "CFSR = 0x%08X\n", $cfsr
    if ($cfsr & 0x0001) printf "  -> IACCVIOL (instruction fetch fault)\n"
    if ($cfsr & 0x0002) printf "  -> DACCVIOL (data access violation)\n"
    if ($cfsr & 0x0100) printf "  -> MSTKERR (stacking error)\n"
    if ($cfsr & 0x0200) printf "  -> UNSTKERR (unstacking error)\n"
    if ($cfsr & 0x10000) printf "  -> DIVBYZERO (division by zero)\n"
    if ($cfsr & 0x20000) printf "  -> UNALIGNED (unaligned access)\n"
end
```

## Trace (ETM/ITM/SWO)

### ETM (Embedded Trace Macrocell)

```
ETM — trace d'instruction complète (cycle-level)
- Compression sur 4 bits (instruction + data)
- Sortie : 4-16 bits parallèle (Trace Port) ou série
- Nécessite : Trace Port Analyzer (TPA) hardware
- Buffer : 2-4 KB FIFO, jusqu'à 200 Mbit/s

Connexion : ETM → TPIU → Trace Port → TPA → USB → PC
```

### ITM (Instrumentation Trace Macrocell)

```c
// ITM — trace logicielle (SWO sur 1 pin)
// Similaire à printf, mais via SWO (pas d'UART)

void ITM_Init(void) {
    // Activer horloge DBG
    DBGMCU->CR |= DBGMCU_CR_TRACE_IOEN;

    // Configurer TPIU (Trace Port Interface Unit)
    TPIU->SPPR = 2;                  // SWO (NRZ)
    TPIU->ACPR = (SystemCoreClock / 2000000) - 1;  // SWO = 2 MHz

    // Activer ITM
    ITM->LAR = 0xC5ACCE55;           // Unlock
    ITM->TCR = (1 << 0) |            // ITM Enable
               (1 << 2) |            // SWO Enable
               (1 << 3) |            // DWT Enable
               (1 << 4);             // Sync enable
    ITM->TER[0] = 1;                 // Port 0 (stimulus)
}

void ITM_Send(const char *str) {
    while (*str) {
        while (!(ITM->STIM[0] & 1));  // Wait ready
        ITM->STIM[0] = *str++;
    }
}

// DWT (Data Watchpoint and Trace) — compteurs de performance
void DWT_Init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

uint32_t DWT_GetCycles(void) {
    return DWT->CYCCNT;
}

// Mesurer cycles d'une fonction
#define MEASURE_CYCLES(fn) do { \
    uint32_t t0 = DWT_GetCycles(); \
    fn; \
    uint32_t t1 = DWT_GetCycles(); \
    ITM_Printf("Cycles: %lu\n", t1 - t0); \
} while(0)
```

### OpenOCD + SWO

```tcl
# openocd.cfg — SWO trace
source [find interface/stlink.cfg]
transport select hla_swd

set CPUSPEED 168000000
source [find target/stm32f4x.cfg]

# Config SWO
stm32f4x.tpiu configure -protocol uart -traceclk 168000000 -pin-switching 0
stm32f4x.tpiu enable -output swo.log -formatter itm
stm32f4x.itm ports 0 enable
```

```bash
# Réception SWO sur PC
# Avec ST-Link V2 (pas de support SWO direct)
# Utiliser : SEGGER J-Link + J-Trace pour SWO full speed
# Ou : OpenOCD + tcp port 5324 pour streaming SWO

# Afficher trace en temps réel
openocd -f openocd.cfg &
arm-none-eabi-gdb firmware.elf -ex "target remote :3333" -ex "load" -ex "continue"

# Côté console : view swo.log
tail -f swo.log | itm_decode
```

## Analyse de Crash (Post-mortem)

### Core Dump

```c
// Dans une ISR HardFault, sauvegarder le contexte dans Backup SRAM
void HardFault_Handler(void) {
    // Copier les registres dans Backup SRAM
    __asm volatile(
        "TST LR, #4\n\t"
        "ITE EQ\n\t"
        "MRSEQ R0, MSP\n\t"
        "MRSNE R0, PSP\n\t"
        "LDR R1, =crash_dump\n\t"
        "STM R1, {R0-R11}\n\t"
        "MRS R2, CONTROL\n\t"
        "STR R2, [R1, #48]\n\t"
    );

    // Marquer que le crash a eu lieu
    crash_dump.magic = 0xDEADCAFE;
    crash_dump.pc = *(uint32_t*)(crash_dump.sp + 24);
    crash_dump.cfsr = SCB->CFSR;
    crash_dump.hfsr = SCB->HFSR;
    crash_dump.mmfar = SCB->MMFAR;
    crash_dump.bfar = SCB->BFAR;

    // Reset
    NVIC_SystemReset();
}
```

### Analyse offline

```bash
# Extraire crash dump via GDB
arm-none-eabi-gdb firmware.elf -ex "target remote :3333" -ex "dump binary memory crash.bin 0x40024000 0x40025000" -ex "quit"

# Analyser
arm-none-eabi-objdump -S firmware.elf > firmware.lst
# Chercher PC dans le dump
```

## Debug RISC-V

```tcl
# OpenOCD RISC-V
source [find interface/ftdi.cfg]
adapter speed 10000

# SiFive HiFive1
set _CHIPNAME riscv
jtag newtap $_CHIPNAME cpu -irlen 5 -expected-id 0x10e31913

target create $_CHIPNAME.cpu riscv -chain-position $_CHIPNAME.cpu
$_CHIPNAME.cpu configure -work-area-phys 0x80000000 -work-area-size 0x4000

# Trigger
flash bank spi0 fespi 0x20000000 0 0 0 $_TARGETNAME
init
targets
reset halt
```

## Pitfalls

1. **SWD vs JTAG** : SWD seulement 2 fils, mais pas de boundary scan ni de chaîne multi-TAP
2. **Reset types** : SYSRESETREQ (software) vs nRST (hardware) — ne pas confondre
3. **Voltage** : Debugger et cible doivent avoir la même référence de tension
4. **SWO fréquence** : Doit être < 1/4 de la fréquence SWCLK sur ST-Link
5. **Hardware breakpoints** : Cortex-M a 6 HW breakpoints max — ne pas les gaspiller sur des boucles
6. **Watchpoints** : 4 max (2 sur M0), utiliser pour les corruptions de variables
7. **Flash lock** : Certains MCU (STM32) ont RDP (Read Protection) — désactiver avant debug
8. **Low power** : Les modes STOP/STANDBY coupent SWD — nécessite reset pour re-connecter

## Ressources

- ARM Debug Interface v5 (ADIv5) : https://developer.arm.com/documentation/ihi0031
- IEEE 1149.1-2013 JTAG Standard
- OpenOCD User's Guide : https://openocd.org/doc/html/
- SEGGER J-Link / J-Trace : https://www.segger.com/products/debug-probes/
- RISC-V Debug Specification : https://github.com/riscv/riscv-debug-spec