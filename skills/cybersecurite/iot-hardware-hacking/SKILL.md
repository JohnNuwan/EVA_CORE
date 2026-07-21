---
name: iot-hardware-hacking
title: "Hardware Hacking IoT — Analyse Physique de Circuits"
description: "Guide complet pour le hacking physique de dispositifs IoT : identification de composants, probing de bus, analyse de PCB, identification de points de test, extraction de données par accès direct, et techniques de mesure avancées (oscilloscope, multimètre, microscope)."
category: cybersecurite
---

# Hardware Hacking IoT — Analyse Physique de Circuits

## Vue d'Ensemble

Le hardware hacking est l'art d'attaquer un dispositif électronique par son interface physique. Contrairement à l'analyse logicielle, on manipule directement le circuit imprimé (PCB), les composants, et les signaux électriques pour contourner les protections logicielles.

### Objectifs
- Identification des composants et points d'intérêt
- Accès aux bus de communication (UART, SPI, I²C, JTAG, SWD)
- Extraction de données depuis la mémoire flash
- Mesure et analyse de signaux
- Localisation de points de test pour flashing, debugging, glitching

---

## Outils Essentiels

### Équipement de Base
| Outil | Usage |
|-------|-------|
| Multimètre numérique | Test de continuité, mesure de tension, identification GND/VCC |
| Fer à souder (temp contrôlée) | Soudure/Dessoudure de composants (TS80, Hakko FX-888) |
| Station air chaud | Dessoudure de composants CMS (QFP, QFN, BGA) |
| Pince à dissection | Manipulation de jumpers, probes |
| Loupe / Microscope | Inspection de PCB, lecture de marquages |
| Pinces de test | Connection aux points de test, bootleg clips |

### Équipement Avancé
| Outil | Usage |
|-------|-------|
| Oscilloscope (4 voies, 100MHz+) | Analyse de signaux série, timing, glitch |
| Analyseur logique (24MHz+) | Décodage de protocoles (Saleae, DSLogic, Kingst) |
| Générateur de signal (AWG) | Injection de signaux, clock glitching |
| Alimentation stabilisée | Power profiling, voltage glitching |
| Pince SPI / SOIC clip | Connection flash SPI sans dessoudure |
| Bus Pirate v4/v6 | Interface universelle pour bus série |
| ChipWhisperer / CW-Lite | Glitching et side-channel attacks |
| FT232H / USB-Programmer | SPI, I²C, JTAG bridge |

### Consommables
- Fil d'enrobage (30 AWG Kynar) pour bodge wires
- Flux, tresse à dessouder, pâte à souder
- Jumpers Dupont (M/M, M/F, F/F)
- ISO/alcool isopropylique pour nettoyage

---

## Méthodologie

### Phase 1 : Reconnaissance Visuelle

1. **Examiner le PCB des deux côtés** : composants, vias, points de test
2. **Identifier le SoC / MCU principal** : chercher les marquages, photo + recherche
3. **Cartographier les bus** : repérer les points de test près du SoC (souvent des pads de 2-6 pins alignés)
4. **Identifier la flash SPI** : composants 8-pins (SOIC-8), marquages 25xx, W25Q, MX25, GD25
5. **Localiser JTAG/SWD** : repérer les pads de 5, 10, ou 20 pins avec pull-ups sur TMS/SWDIO
6. **Chercher UART** : points de test groupés par 3-4 pins, souvent près du SoC avec via de GND

### Phase 2 : Cartographie des Signaux

```bash
# Avec multimètre
# 1. Trouver GND : chercher le plan de masse (grande zone de cuivre)
#    Test continuité sur vis USB, blindage, pad large
# 2. Trouver VCC : points qui donnent 3.3V ou 1.8V par rapport à GND
# 3. Pro志向 les pads suspects : continuité vers les pins du SoC
#    Si un pad a continuité avec un pin du SoC, c'est probablement un bus

# Avec oscilloscope
# 4. Proposer plusieurs voies sur les pads suspects
# 5. Mettre sous tension, observer :
#    - Signal 3.3V constant = VCC
#    - GND = 0V constant
#    - UART TX = signal 3.3V qui pulse au boot (activité)
#    - SPI = activité haute fréquence pendant le boot
#    - JTAG TCK = clock continue (typiquement 10-50 MHz)
```

### Phase 3 : Probing UART

```bash
# Identifier TX/RX
# 1. Brancher oscilloscope sur chaque pad suspect
# 2. Mettre sous tension
# 3. TX = signal qui passe de idle (VCC) à actif (pulsations) au boot
# 4. RX = souvent silencieux (pull-up) ou idle à VCC
# 5. GND = 0V constant
# 6. VCC = 3.3V constant

# Une fois TX/RX/GND identifiés :
screen /dev/ttyUSB0 115200
# Si baudrate inconnu, essayer communs : 9600, 19200, 38400, 57600, 115200
# Ou utiliser auto-baud :
stty -F /dev/ttyUSB0 115200 raw -echo
```

### Phase 4 : Probing SPI Flash

```bash
# Identifier les pins SPI sur la flash (SOIC-8 standard)
# Pin 1 = /CS (Chip Select) — marqué par un point ou encoche
# Pin 2 = MISO / DO
# Pin 3 = WP / HOLD
# Pin 4 = GND
# Pin 5 = MOSI / DI
# Pin 6 = CLK
# Pin 7 = /HOLD / RESET
# Pin 8 = VCC (3.3V)

# Avec flashrom (en circuit)
flashrom -p linux_spi:dev=/dev/spidev0.0 -r dump.bin

# Avec Bus Pirate
# 1. Alimenter la cible
# 2. Connecter les probes SPI du Bus Pirate
# 3. Utiliser flashrom avec buspirate_spi
flashrom -p buspirate_spi:dev=/dev/ttyUSB0 -r dump.bin
```

### Phase 5 : Identification des Points de Test

- **Pads numérotés** : souvent alignés sur les pins du SoC (datasheet)
- **Pads avec vias** : connexion directe au plan interne
- **Pads sérigraphiés** : TP1, TP2, TEST, DEBUG, SWD, JTAG, UART
- **Pads près du connecteur** : souvent pour programmation en production
- **Pads non connectés** : peut-être un port debug non assemblé (populate yourself)

---

## Techniques Avancées

### Dumping Flash en Circuit avec Hot-Air
1. Chauffer légèrement la flash (200°C) pour liquéfier le flux
2. Insérer des fils d'enrobage sous les pins
3. Refroidir, les fils sont soudés aux pins
4. Connecter via SOIC-8 clip à un programmateur

### Lecture de Flash Protégée
- **NVRAM / EEPROM** : pas de protection, lecture directe
- **Flash avec Security Register** :可能需要 commande spécifique SFDP
- **Flash avec OTP** : verrouillée définitivement après écriture
- **Flash avec Read Protect** : utiliser un programmateur qui supporte l'unprotect
  - Certaines flashes se déverrouillent par commande (EAh pour W25Q)
  - D'autres nécessitent un effacement complet pour déverrouiller

### Mesh / Bus de Test non Documenté
```bash
# Boundary Scan / JTAG
# Pour les SoC avec JTAG, utiliser openocd
openocd -f interface/ftdi.cfg -f target/mcu.cfg

# Si le pinout JTAG est inconnu :
# - Identifier TCK (clock) : probe avec oscillo, chercher signal carré
# - TMS / SWDIO : probe les pads suspects, utiliser JTAGenum
python3 JTAGenum.py /dev/ttyUSB0
```

### Side-Channel sur PCB
- **Mesure de courant** : résistance shunt sur l'alimentation, amplifier
- **Electromagnetic** : sonde EM près du SoC pendant le chiffrement
- **Timing** : mesurer le temps d'exécution d'opérations cryptographiques
- **Power Analysis** (SPA/DPA) : analyser la consommation pendant AES/RSA

---

## Pièges & ASTUCES

⚠️ **Ne pas alimenter à l'envers** : vérifier la polarité avant de brancher
⚠️ **Tensions** : les dispositifs IoT peuvent être en 1.8V, 2.5V, ou 3.3V. Un probe 5V peut griller le composant
⚠️ **Probing actif** : une sonde d'oscilloscope peut charger la ligne et perturber le signal (utiliser 10x)
⚠️ **Condensateurs de découplage** : peuvent masquer les signaux haute fréquence (mesurer après)
⚠️ **Soudure froide** : vérifier les points de soudure au microscope
⚠️ **Flash en circuit** : d'autres composants sur le bus SPI peuvent interférer (débrancher si possible)
⚠️ **Anti-tamper** : certains dispositifs ont des switches, des mesh ou de la résine époxyde qui protègent les points sensibles. La résine se dissout à l'acétone (attention aux composants plastiques)
⚠️ **Alimentation dédiée** : ne pas alimenter via USB du PC si le device est à 12V/24V — utiliser l'alim du device ou une alim de labo

### Check-list d'Identification Rapide
```bash
# Composants critiques à repérer avant toute connexion
# 1. SoC / MCU principal (cœur du système)
# 2. Flash SPI (mémoire de stockage)
# 3. RAM (SDRAM/DDR)
# 4. Régulateur de tension (alimentation)
# 5. Connecteurs debug (JTAG, SWD, UART)
# 6. Antenne (Bluetooth, WiFi, Zigbee)
# 7. Crystals (horloge principale, horloge RTC)
```

---

## Références

- **JTAGenum** : https://github.com/cyphunk/JTAGenum
- **Bus Pirate** : http://dangerousprototypes.com/docs/Bus_Pirate
- **ChipWhisperer** : https://github.com/newaetech/chipwhisperer
- **Saleae Logic Analyzer** : https://www.saleae.com/
- **Flashrom** : https://flashrom.org/
- **Hacking the IoT (Youtube)** : Joe Grand, Mike Ossmann
- **The Hardware Hacking Handbook** : Jasper van Woudenberg, Colin O'Flynn (No Starch Press)