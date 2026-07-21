---
name: iot-jtag-swd
title: "JTAG & SWD Debug — Accès Debug des SoC/MCU"
description: "Guide complet pour l'identification, la connexion et l'exploitation des interfaces de débogage JTAG et SWD sur les dispositifs IoT. Couvre l'énumération de pinout, la configuration OpenOCD, l'extraction de firmware via debug, le contournement de Secure Boot, et le debugging en temps réel."
category: cybersecurite
---

# JTAG & SWD Debug — Accès Debug des SoC/MCU

## Vue d'Ensemble

JTAG (IEEE 1149.1) et SWD (Serial Wire Debug) sont les interfaces de débogage standard utilisées dans l'industrie pour programmer et débugger les microcontrôleurs et SoCs. Sur les dispositifs IoT, ces interfaces sont souvent laissées actives en production, offrant un accès complet à la mémoire du dispositif.

### Objectifs
- Identifier et cartographier les pads JTAG/SWD
- Lire / écrire la mémoire du SoC (RAM, Flash, registres)
- Extraire le firmware complet via la DCC (Debug Communication Channel)
- Contourner Secure Boot en stoppant l'exécution
- Débugger le firmware en temps réel (breakpoints, watchpoints)
- Programmer / reflasher le dispositif

---

## Outils Essentiels

### Interfaces Hardware
| Outil | Description |
|-------|-------------|
| **FT232H / FT4232H** | Adaptateur USB-JTAG/SWD via MPSSE, open-source |
| **J-Link (SEGGER)** | Debugger ARM professionnel, support SWO (Serial Wire Output) |
| **ST-Link V2/V3** | Debugger STM32, abordable, openocd-compatible |
| **Bus Pirate** | Interface JTAG basique (lente) pour identification |
| **Raspberry Pi / Orange Pi** | GPIO → JTAG via `openocd` ou `pyOCD` |
| **ChipWhisperer (Pro/FOB)** | JTAG + glitching combinés |
| **Black Magic Probe** | Debugger ARM natif (GDB over USB), autonome |

### Logiciels
| Outil | Usage |
|-------|-------|
| `openocd` | Standard de l'industrie : support large (800+ targets) |
| `pyOCD` | CMSIS-DAP Python, ARM Cortex uniquement |
| `JTAGenum` | Énumération du pinout JTAG |
| `UrJTAG` | JTAG boundariescan (BSDL) |
| `GDB` | Debugging via la target remote de OpenOCD |
| `STM32CubeProgrammer` | Programmation STM32 (option Read Protection) |
| `J-Flash` (SEGGER) | Programmation J-Link |

---

## Méthodologie

### Phase 1 : Identifier et Énumérer les Pins JTAG/SWD

#### Pinout Standard JTAG (20-pin ARM)
```
Pin 1  — VREF       Pin 2  — VCC (target)
Pin 3  — nTRST      Pin 4  — GND
Pin 5  — TDI        Pin 6  — GND
Pin 7  — TMS        Pin 8  — GND
Pin 9  — TCK        Pin 10 — GND
Pin 11 — RTCK       Pin 12 — GND
Pin 13 — TDO        Pin 14 — GND
Pin 15 — nSRST      Pin 16 — GND
Pin 17 — DBGRQ      Pin 18 — GND
Pin 19 — DBGACK     Pin 20 — GND
```

#### Pinout SWD (2 pins + 1 clock)
```
SWDIO — Data I/O (équivalent TMS)
SWCLK — Clock (équivalent TCK)
SWO   — Serial Wire Output (trace, optionnel)
```

#### Énumération Automatique avec JTAGenum
```bash
# 1. Connecter GND du Bus Pirate au GND du device
# 2. Lister les connexions candidates (pads suspects)
# 3. Lancer JTAGenum
python3 JTAGenum.py /dev/ttyUSB0 gpio 2 3 4 5 6 7
# Les GPIO 2-7 sont connectés aux pads suspects
# JTAGenum va identifier TCK, TMS, TDI, TDO
```

#### Énumération Manuelle
```bash
# Étape par étape avec oscilloscope :
# 1. TCK (clock) = signal carré à fréquence fixe (10-100 MHz)
#    Probe chaque pad sous tension
# 2. TMS / SWDIO = signal qui change d'état (transactions de debug)
# 3. TDO = sortie data (actif pendant les transactions JTAG)
# 4. TDI = entrée data (souvent pull-up ou pulldown)

# Avec multimètre en continuité :
# - TCK, TMS, TDI, TDO ont souvent des pull-ups vers VCC
# - GND = continuité avec le plan de masse
```

### Phase 2 : Connexion OpenOCD

#### Configuration Interface
```tcl
# ft232h.cfg — adaptateur FT232H
interface ftdi
ftdi_vid_pid 0x0403 0x6014
ftdi_channel 0
ftdi_layout_init 0x0018 0x00fb
adapter_khz 1000
adapter_nsrst_delay 100
```

#### Configuration Target
```tcl
# stm32f4.cfg — target STM32F4
set CHIPNAME STM32F4xx
set ENDIAN little
source [find target/stm32f4x.cfg]
```

#### Connexion
```bash
# Lancer OpenOCD
openocd -f interface/ft232h.cfg -f target/stm32f4x.cfg

# Dans un autre terminal, se connecter en Telnet
telnet localhost 4444

# Ou via GDB
gdb-multiarch -ex "target remote :3333"
```

### Phase 3 : Extraction du Firmware

```bash
# Dans OpenOCD Telnet :
# 1. Stopper le CPU
halt

# 2. Lire la mémoire flash
#   Option A : dump complet
flash read_bank 0 firmware.bin 0x08000000 $SIZE

#   Option B : dump via MDW (memory display word)
mdw 0x08000000 0x1000  # dump 4K words

#   Option C : sauvegarde avec GDB
(gdb) dump binary memory firmware.bin 0x08000000 0x080FFFFF

# 3. Lire la RAM
dump_image ram_dump.bin 0x20000000 0x20010000

# 4. Lire les registres
reg
arm semihosting enable
```

### Phase 4 : Bypass de Protection

#### Secure Boot / Code Readout Protection
```bash
# Niveaux de protection STM32 (RDP) :
# RDP Level 0 — pas de protection
# RDP Level 1 — debug désactivé (mass erase pour revenir à 0)
# RDP Level 2 — protection irréversible

# Bypass potentiels :
# 1. Voltage glitching sur la broche de reset pendant le démarrage
#    (le SoC démarre avec RDP level 0 avant que le bootrom check)
# 2. Cold boot attack : refroidir la RAM (-40°C) pour geler les données
# 3. Fault injection sur la vérification RDP dans le bootrom
```

#### Locked JTAG (ARM DAP Lock)
```bash
# Si JTAG/SWD refuse la connexion, vérifier :
# 1. Pull-up sur /RESET et SRST
# 2. Pull-up sur TMS/SWDIO
# 3. Délai de connexion suffisant
# 4. Fréquence réduite (100 kHz) pour éviter les interférences

# Avec openocd :
# Activer les signaux de reset
reset_config trst_and_srst
adapter_khz 100
```

### Phase 5 : Debugging en Temps Réel

```bash
# Breakpoints hardware (limités — 4-6 selon SoC)
(gdb) break *0x08001234
(gdb) continue

# Watchpoints
(gdb) watch *(int*)0x20000100

# Modifier la mémoire en vol
(gdb) set {int}0x20000100 = 0x41414141

# Semihosting — sorties printf sur GDB
# Dans le code : retarget fputc vers ITM/SWO
# Activer dans openocd :
arm semihosting enable
```

---

## Techniques Avancées

### SWO / ITM Trace (STM32, nRF52, etc.)
```bash
# SWO : trace à très haut débit sans impacter le timing
# Config openocd + SWO :
tpiu config internal swo.log uart off 115200

# Visualisation :
openocd -f ... | grep SWO
# ou utiliser un analyseur dédié (J-Scope, SEGGER SystemView)
```

### Boundary Scan (BSDL)
```bash
# Test des connexions entre composants (fabrication)
# Charger le fichier BSDL du composant
# Tester les interconnexions sans firmware
urjtag -c cable ft2232
urjtag> detect
urjtag> bsdl path ./bsdl/
urjtag> read
urjtag> svf vectest.svf
```

### Attaque par Réinitialisation + Halt
```bash
# Contourner Secure Boot en stoppant le CPU AVANT le bootloader
# Technique : reset + halt
openocd -f ... -c "transport select swd" -c "adapter_khz 1000" \
  -c "reset halt" -c "flash read_bank 0 firmware.bin 0x08000000 0x100000"
# Si le CPU s'arrête avant le code du bootroom, la flash n'est pas protégée
```

### DAP (Debug Access Port) Bruteforce
```bash
# Certains SoC ont un mot de passe AP (Access Port) activé
# Bruteforce possible si le key est court (< 32 bits)
# Utiliser openocd avec script custom pour tester les clés
```

---

## Pièges & ASTUCES

⚠️ **Pull-up requis** : TMS/SWDIO et TCK/SWCLK ont besoin de pull-up 10kΩ vers VCC pour fonctionner
⚠️ **Fréquence** : commencer à 100 kHz, monter progressivement. Trop haut → corruption de la communication
⚠️ **Tensions** : vérifier la tension de la target (1.8V, 3.3V). Ne pas connecter un debugger 5V à une cible 1.8V
⚠️ **nSRST** : le reset est nécessaire pour arrêter le CPU avant Secure Boot
⚠️ **SWD vs JTAG** : beaucoup de SoCs modernes (ARM Cortex M) n'ont que SWD, pas JTAG
⚠️ **RTCK** : si présent, adapter la fréquence au signal de retour
⚠️ **Câbles longs** : les signaux haute fréquence se dégradent sur des câbles > 20cm
⚠️ **NVRAM avec Lock** : certaines cartes ont leurs points JTAG effacés en production (laser-cut)

### Check-list Rapide
```bash
# 1. Vérifier présence JTAG/SWD
#    - Tester les pads suspects avec oscilloscope (TCK = clock)
#    - Ou utiliser JTAGenum

# 2. Connecter avec openocd
openocd -f interface/ft232h.cfg -f target/stm32f4x.cfg

# 3. Halt + read flash
echo "halt; flash read_bank 0 dump.bin 0x08000000 0x100000" | nc localhost 4444

# 4. Vérifier le dump
binwalk dump.bin
```

---

## Références

- **OpenOCD** : https://openocd.org/
- **pyOCD** : https://github.com/pyocd/pyOCD
- **JTAGenum** : https://github.com/cyphunk/JTAGenum
- **Black Magic Probe** : https://github.com/blacksphere/blackmagic
- **ARM Debug Interface v5 (ADIv5)** : ARM IHI 0031
- **SEGGER J-Link** : https://www.segger.com/products/debug-probes/j-link/
- **JTAG / Boundary Scan Wiki** : https://www.jtag.com/
- **Hardware Hacking Handbook** : Ch 6 & 7 (JTAG/SWD)