---
name: iot-uart
title: "UART / Série IoT — Accès Console et Analyse de Protocole"
description: "Guide complet pour l'identification, la connexion et l'exploitation des interfaces UART (Universal Asynchronous Receiver-Transmitter) sur les dispositifs IoT. Couvre la recherche de points de test, la détermination du baudrate, l'accès console shell, l'analyse de protocoles propriétaires, et l'injection de commandes."
category: cybersecurite
---

# UART / Série IoT — Accès Console et Analyse de Protocole

## Vue d'Ensemble

L'UART (Universal Asynchronous Receiver-Transmitter) est l'interface série la plus répandue sur les dispositifs IoT. Elle fournit souvent un accès console (shell root, bootloader, diagnostic) sans authentification. C'est généralement le point d'entrée le plus facile pour un pentest hardware.

### Objectifs
- Localiser les points UART sur le PCB
- Déterminer le baudrate (vitesse de communication)
- Accéder à la console (shell, bootloader, debug)
- Analyser les protocoles propriétaires sur UART
- Intercepter / injecter des trames
- Contourner l'authentification console

---

## Outils Essentiels

### Adaptateurs USB-UART
| Outil | Tension | Prix |
|-------|---------|------|
| **FTDI TTL-232R** | 3.3V / 5V (jumper) | ~$20 — standard, fiable |
| **CP2102** | 3.3V | ~$5 — basique, fonctionnel |
| **CH340G** | 3.3V / 5V | ~$2 — pas cher, instable |
| **PL2303** | 3.3V / 5V | ~$3 — compatible large |
| **FT232RL** | 3.3V / 5V | ~$10 — le classique |
| **Bus Pirate** | 0-5.5V (configurable) | ~$30 — UART + SPI + I²C |

### Logiciels Terminal
| Outil | OS | Fonctionnalités |
|-------|-----|----------------|
| `screen` | Linux/macOS | Minimal, simple |
| `minicom` | Linux/macOS | Plus configurable |
| `picocom` | Linux/macOS | Léger, pratique |
| `PuTTY` | Windows | Mode série |
| `TeraTerm` | Windows | Macro support |
| `Serial` (Arduino IDE) | Tous | Debug rapide |
| `CuteCom` / `GtkTerm` | Linux | GUI |

### Analyse
| Outil | Usage |
|-------|-------|
| `logic` (Saleae) | Décodage UART avec horodatage |
| `pulseview` (sigrok) | Analyseur logique open-source |
| `sigrok-cli` | Décodage UART en CLI |
| `baudrate.py` | Détermination automatique du baudrate |
| `uart_transmitter.py` | Injection de trames custom |

---

## Méthodologie

### Phase 1 : Localisation des Points UART

#### Indices Visuels
```bash
# Sur le PCB, chercher :
# 1. Pads de 3, 4, ou 5 pins alignés, souvent avec vias
# 2. Marquage "UART", "RXD", "TXD", "DEBUG", "TST", "CONSOLE"
# 3. Pads près du SoC/MCU (pins UART du datasheet)
# 4. Points de test près du connecteur RJ45/USB
# 5. Résistance 0Ω (zero ohm jumper) qui relie le SoC à un pad
# 6. Pins étamés (carrés argentés) sur le PCB — souvent points de test

# Vérifier avec multimètre en continuité :
# - GND = continuité vers plan de masse
# - VCC = 3.3V par rapport à GND
# - TX = activité électrique (oscillo) ou test de tension :
#   En idle : TX reste à VCC (logique 1 en TTL)
#   Activité : pulses négatifs lors des transmissions
```

#### Identification TX/RX/GND avec Oscilloscope
```bash
# Méthode :
# 1. Mettre la sonde GND à la masse
# 2. Prober chaque pad suspect
# 3. Mettre sous tension / redémarrer
# 4. Observer les signaux :

# GND = 0V constant
# VCC = 3.3V constant (ou 1.8V / 5V)
# TX = signal à 3.3V qui pulse au boot (activité série)
#      Idle à VCC (high), pulses vers 0V (start bit + data)
# RX = pull-up à VCC constant (ou légère activité si le device attend)
```

### Phase 2 : Connexion et Baudrate

#### Schéma de Connexion
```
Device              USB-UART
┌─────────┐       ┌──────────┐
│ TX (pin) ───────▶ RX       │
│ RX (pin) ◀─────── TX       │
│ GND ───────────── GND      │
│ VCC ───────────── (PAS)    │
└─────────┘       └──────────┘
# ATTENTION : NE PAS connecter VCC device au VCC de l'adaptateur
#              ≠ cross-connection qui grillerait les deux
```

#### Détermination du Baudrate

```bash
# Méthode 1 : baudrates communs
for baud in 9600 19200 38400 57600 115200 230400 460800 921600; do
  echo "Testing $baud:" 
  screen /dev/ttyUSB0 $baud 2>/dev/null &
  sleep 0.5
  kill %1 2>/dev/null
done

# Méthode 2 : avec picocom
picocom -b 115200 /dev/ttyUSB0
# Ctrl+A Ctrl+X pour quitter
# Essayer chaque baudrate jusqu'à voir du texte lisible

# Méthode 3 : détection automatique avec sigrok
sigrok-cli -i capture.sr -p -P uart:baudrate=auto

# Méthode 4 : avec baudrate.py
python3 baudrate.py /dev/ttyUSB0
```

#### Connexion Terminal
```bash
# screen
screen /dev/ttyUSB0 115200 8N1
# 8N1 = 8 data bits, No parity, 1 stop bit (standard UART)

# picocom
picocom -b 115200 -d 8 -p n -s 1 /dev/ttyUSB0

# minicom
minicom -D /dev/ttyUSB0 -b 115200
```

### Phase 3 : Exploitation de la Console

#### Types de Console
```bash
# 1. Bootloader (U-Boot, Barebox, RedBoot)
#    Appuyer rapidement sur une touche (Espace, Entrée, '0')
#    Pendant le boot : "Hit any key to stop autoboot"
#    Si accès bootloader : modifier les paramètres de boot

#    Commandes U-Boot utiles :
printenv        # Afficher les variables d'environnement
setenv bootargs console=ttyS0,115200 root=/dev/mtdblock1
saveenv         # Sauvegarder (peut briquer le device)
boot            # Démarrer normalement
md 0x80000000   # Lire la mémoire
flinfo          # Info sur la flash
bdi             # Info sur le boot device

# 2. Shell Linux
#    Si login prompt : essayer admin/admin, root/root, admin/<vide>
#    Si pas de login : shell root direct (brut de sécurité)

# 3. Shell propriétaire (VxWorks, FreeRTOS, ThreadX)
#    Commandes souvent limitées (help, ?)
#    Chercher des commandes de debug, de dump mémoire

# 4. Menu de diagnostic (test hardware)
#    Souvent : test RAM, test flash, test réseau
#    Peut permettre le dump de firmware ou la modification de paramètres
```

#### Si Login Requis
```bash
# Essayer identifiants par défaut :
# admin / admin, admin / password, root / root
# admin / <vide>, root / <vide>, admin / 1234
# admin / default, support / support, user / user

# Essayer les identifiants trouvés dans strings du firmware
# Ou chercher un fichier /etc/passwd, /etc/shadow dans le dump

# Si authentification HTTP/HTTPS, essayer les endpoints de debug
# (ex: /debug, /shell, /cmd.cgi)
```

### Phase 4 : Analyse de Protocole Propriétaire

```bash
# 1. Capture des trames avec analyseur logique
#    Branché sur TX et RX du dispositif lors d'une opération
#    Exemple : communication entre deux modules via UART

# 2. Décodage avec Saleae / PulseView
#    - Configurer UART decode (baudrate, data bits, parity)
#    - Observer la structure des trames
#    - Repérer : headers, length, checksum, payload

# 3. Reverse Engineering du protocole
#    - Intercepter les échanges pendant différentes actions
#    - Faire varier les entrées, observer les réponses
#    - Chercher des motifs : longueur fixe, magic bytes, CRC
```

---

## Techniques Avancées

### Attaque par Injection de Trames
```bash
# 1. Écouter le trafic RX/TX avec un analyseur
# 2. Identifier les trames de commande
# 3. Modifier et réinjecter des trames
#    Avec un deuxième UART connecté en parallèle :

# Script d'injection avec FTDI (python)
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200)

# Envoyer une trame modifiée
ser.write(b'\xAA\x55\x01\x00\x10\x00\x00\x00\x00\x42')
response = ser.read(100)
print(response)
```

### Sniffing UART Passif
```bash
# Sniffer silencieux avec écoute seule (sans TX)
# Ne connecter QUE l'analyseur logique ou RX-only sur 3ème UART
# Permet d'observer sans perturber

# Avec sigrok-cli en live :
sigrok-cli --device=0 --config samplerate=10M \
  -C D0,D1 --protocol-decoder uart --channels D0=RX,D1=TX \
  --continuous
```

### Console Silencieuse (Pas d'Output au Boot)
```bash
# Si pas de boot message, possible que :
# - Console désactivée dans le noyau (console=tty0)
# - Baudrate non standard (<9600 ou >921600)
# - Console attend un signal (RTS/CTS hardware handshake)
# - Console sur un autre port (ttyS1, ttyAM1, ttyPS0)
# - Messages envoyés APRÈS le boot (press Enter pour activer)
```

---

## Pièges & ASTUCES

⚠️ **Ne JAMAIS connecter VCC-device au VCC de l'adaptateur** : les deux alimentations en conflit → court-circuit
⚠️ **Tensions** : vérifier 3.3V vs 1.8V vs 5V. Les GPIO des SoC modernes sont souvent 1.8V ou 3.3V
⚠️ **TX ↔ RX** : connecter TX device → RX adaptateur et vice versa (cross-connection)
⚠️ **GND en premier** : toujours connecter GND avant les signaux pour éviter les boucles de masse
⚠️ **Pins non soudés** : certains pads n'ont pas de connecteur mais des holes pour header pins (souder un header)
⚠️ **Pas de boot messages** : appuyer sur Entrée/Reset après connexion pour voir le boot complet
⚠️ **Baudrate non standard** : certains devices utilisent des baudrates rares (14400, 28800, 76800, 250000)
⚠️ **Firmware qui désactive UART** : après le boot, le noyau peut désactiver le port série (vérifier avant)
⚠️ **Anti-tampon** : résine époxyde sur les pads (dissoudre à l'acétone avec précaution)

### Check-list Rapide
```bash
# 1. Identifier TX/RX/GND sur le PCB
# 2. Connecter USB-UART (GND d'abord)
# 3. Tester baudrate : 115200 → 57600 → 38400 → 19200 → 9600
# 4. Ouvrir terminal
screen /dev/ttyUSB0 115200

# 5. Redémarrer le device pour voir boot log
# 6. Appuyer sur Entrée si shell, ou chercher prompt bootloader
# 7. Si login : tester identifiants par défaut
```

---

## Références

- **UART Communication Basics** : https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter
- **Picocom** : https://github.com/npat-efault/picocom
- **Sigrok / PulseView** : https://sigrok.org/
- **Saleae Logic Analyzer** : https://www.saleae.com/
- **Baudrate Detection** : https://github.com/devttys0/baudrate
- **Hardware Hacking Handbook** : Ch 5 (UART)