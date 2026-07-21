---
name: iot-firmware-analysis
title: "Analyse de Firmware IoT"
description: "Guide complet pour l'extraction, l'analyse statique/dynamique, la modification et le reconditionnement de firmware de dispositifs IoT. Couvre les formats binaires, le reverse engineering, l'extraction par flash, OTA et debug, et la détection de backdoors/vulnérabilités."
category: cybersecurite
---

# Analyse de Firmware IoT

## Vue d'Ensemble

L'analyse de firmware IoT consiste à extraire le logiciel embarqué d'un dispositif, l'analyser pour y trouver des vulnérabilités, des secrets, des backdoors, ou comprendre son fonctionnement interne. C'est la première étape de tout pentest IoT sérieux.

### Objectifs
- Extraire le firmware (flash physique, OTA, debug interface)
- Analyser statiquement (strings, binwalk, Ghidra)
- Analyser dynamiquement (émulation QEMU, exécution partielle)
- Modifier et reflasher (persistance, backdoor)
- Détecter : hardcoded credentials, API endpoints, protocoles propriétaires

---

## Outils Essentiels

### Extraction
| Outil | Usage |
|-------|-------|
| `binwalk` | Analyse d'empreintes, extraction de systèmes de fichiers |
| `dd` / `flashrom` | Dump raw de flash SPI |
| `openocd` | Extraction via JTAG/SWD |
| `esptool` | ESP8266/ESP32 extraction |
| `chipsec` | Extraction SPI firmware x86 |
| `adb` | Extraction depuis Android Things / Linux embarqué |

### Analyse Statique
| Outil | Usage |
|-------|-------|
| `strings` | Extraction de chaînes (credentials, paths, URLs) |
| `file` / `binwalk -E` | Identification du type de fichier, entropie |
| `Ghidra` | Reverse engineering complet (MIPS, ARM, Xtensa, RISC-V) |
| `radare2` / `rizin` | Reverse engineering en CLI |
| `firmwalker` | Scan automatisé de firmware |
| `FACT` (Firmware Analysis and Comparison Tool) | Framework complet d'analyse |
| `sasquatch` | Extraction SquashFS non-standard |

### Émulation
| Outil | Usage |
|-------|-------|
| `QEMU` (user + system mode) | Émulation de binaires cross-arch |
| `Firmadyne` | Émulation complète de firmware Linux embarqué |
| `FirmAE` | Fork amélioré de Firmadyne avec instrumentation |
| `Avatar²` | Framework d'analyse hybride (émulation + hardware) |

### Modification & Reflash
| Outil | Usage |
|-------|-------|
| `mksquashfs` / `mkfs.jffs2` | Reconstruction de filesystem |
| `ubinize` / `mkfs.ubifs` | Images UBIFS |
| `fastboot` / `heimdall` | Flash via bootloader |
| `flashrom` | Flash SPI hardware |

---

## Méthodologie

### Phase 1 : Collecte et Extraction

```bash
# 1. Identification du fichier
file firmware.bin

# 2. Analyse d'entropie (repérer compression, chiffrement)
binwalk -E firmware.bin

# 3. Scanner les signatures
binwalk -Me firmware.bin

# 4. Extraction manuelle si binwalk rate
# SquashFS
dd if=firmware.bin bs=1 skip=$OFFSET | unsquashfs -d ./extracted -

# JFFS2
jefferson -d ./extracted firmware.bin

# CramFS
cramfsck -x ./extracted firmware.bin

# UBIFS
ubireader_extract_images -w ./extracted firmware.bin

# 5. Extraction des chaînes intéressantes
strings -n 6 firmware.bin | grep -iE '(pass|key|secret|token|http|api|admin|root|ssh|telnet)'
```

### Phase 2 : Analyse Statique

```bash
# Architecture CPU
binwalk -Y firmware.bin | head -20

# Liste des endpoints HTTP/HTTPS
strings firmware.bin | grep -E 'https?://' | sort -u

# Certificats embarqués
extractcert firmware.bin

# Scan automatisé avec firmwalker
./firmwalker.sh extracted/

# Analyse des binaires critiques
# - busybox : lister les commandes disponibles
# - dropbear/openssh : versions, config
# - httpd/lighttpd/nginx : config serveur web
# - libcrypto/libssl : version OpenSSL
```

### Phase 3 : Reverse Engineering (Ghidra)

1. Charger le binaire dans Ghidra
2. Sélectionner l'architecture (ARM/MIPS/Xtensa/RISC-V)
3. Analyse automatique (auto-analysis)
4. Rechercher :
   - `main()` et `init()` du firmware
   - `system()`, `popen()`, `exec()` — injection commande
   - `strcpy()`, `sprintf()`, `gets()` — buffer overflow
   - `malloc()` sans `free()` — fuites mémoire
   - `hardcoded credentials` en strings
5. Cross-reference sur les endpoints réseau (bind(), listen(), accept())

### Phase 4 : Émulation

```bash
# Firmadyne / FirmAE — émulation complète
sudo ./scripts/makeImage.sh $ID firmware.bin
sudo ./scripts/run.sh $ID
# Accès web : http://192.168.0.100:80 (IP attribuée)

# Émulation binaire seul (QEMU user)
qemu-arm-static -L ./extracted/ ./extracted/bin/busybox

# Émulation système minimal
qemu-system-arm -M virt -kernel vmlinuz -drive file=rootfs.ext2,format=raw \
  -append "root=/dev/sda console=ttyAMA0" -nographic
```

### Phase 5 : Analyse de Sécurité

- **Hardcoded secrets** : clés API, tokens OAuth, mots de passe root
- **Services exposés** : telnet, SSH, HTTP sans auth, UPnP, CoAP
- **Version des bibliothèques** : vieux OpenSSL/Kernel (CVE connues)
- **Permissions** : binaires setuid root, world-writable files
- **Bootloader** : pas de Secure Boot, console UART exposée
- **Update OTA** : signature non vérifiée, clé publique embarquée

---

## Techniques Avancées

### Détection de Firmware Chiffré
- Entropie élevée uniforme sur tout le fichier → probablement chiffré
- Analyser le bootloader pour trouver la clé de déchiffrement
- Méthode : extraire le bootloader, trouver la routine de déchiffrement

### Firmware OTA
```bash
# Proxy mitm : capturer la mise à jour OTA
mitmproxy -p 8080 --mode transparent

# Analyser le protocole : HTTP, MQTT, CoAP custom ?
# Vérifier TLS : certificat pinning ? validation ?
# Chercher la clé publique dans le firmware courant
```

### Hooking Dynamique
```bash
# LD_PRELOAD sur binaire émulé
# Hooker malloc/free/libc
gcc -shared -fPIC -o myhook.so hook.c
LD_PRELOAD=./myhook.so qemu-arm-static ./bin/httpd
```

### Attaque sur Update
- **Downgrade attack** : forcer le device à accepter une ancienne version vulnérable
- **Man-in-the-middle** : intercepter la mise à jour, injecter un firmware backdooré
- **Rollback protection bypass** : trouver le compteur de version dans la flash

---

## Pièges & ASTUCES

⚠️ **Entropie ≠ chiffrement** : compression haute (xz, lzma) donne aussi une entropie élevée
⚠️ **binwalk peut rater** : certains firmwares ont des signatures non standard (vérifier hexdump manuellement)
⚠️ **Endianness** : ARM est bi-endian, bien configurer Ghidra
⚠️ **Chargement décalé** : les firmwares ont souvent un header avant le code exécutable (utiliser la base address correcte)
⚠️ **Squashfs non standard** : `sasquatch` supporte plus de variantes que `unsquashfs`
⚠️ **Bootloader protégé** : certains bootloaders verrouillent la flash après le boot (nécessite glitching)

### Check-list de Sécurité Rapide
```bash
# 1. Entropie
binwalk -E firmware.bin

# 2. Strings sensibles
strings firmware.bin | grep -iE '(password|secret|key|token|admin)' | grep -v '^\.'

# 3. Binaires setuid
find extracted/ -perm -4000 -type f

# 4. Ports ouverts (après émulation)
nmap -sT -p- 192.168.0.100

# 5. Version kernel
strings extracted/boot/vmlinuz | grep 'Linux version'

# 6. Certificats expirés / self-signed
openssl x509 -in extracted/etc/ssl/certs/ca.pem -text
```

---

## Références

- **FACT (Firmware Analysis Comparison Tool)** : https://github.com/fkie-cad/FACT_core
- **Firmadyne** : https://github.com/firmadyne/firmadyne
- **FirmAE** : https://github.com/pr0v3rbs/FirmAE
- **Ghidra** : https://ghidra-sre.org/
- **Embedded Security CTF** : https://microcorruption.com
- **OWASP Firmware Security Testing** : https://owasp.org/www-project-firmware-security-testing-methodology/