---
name: memory-forensics-acquisition
description: Guide complet d'acquisition mémoire volatile — WinPMEM, DumpIt, LiME, fmem, OSXPMem, hiberfil, pagefile, acquisition à chaud, acquisition à froid, DMA, et analyse comparative
tags: [forensics, memory, acquisition, ram-dump, winpmem, lime, hiberfil, dma]
version: 1.0
---

# Acquisition Mémoire Volatile — Guide Complet

Guide exhaustif des techniques d'acquisition de la mémoire RAM : outils, méthodes, limitations et contre-mesures.

---

## 1. Principes Fondamentaux

### Pourquoi capturer la RAM ?

La mémoire volatile contient des preuves qui disparaissent à l'extinction :
- Processus en cours (même rootkités/cachés)
- Connexions réseau actives (C2, beacons)
- Clés de chiffrement en clair (BitLocker, VeraCrypt)
- Mots de passe, tokens, cookies de session
- Commandes shell non enregistrées
- Fichiers temporaires (mémoire seulement)
- Code injecté (shellcode)
- Fenêtres ouvertes, presse-papier

### Ordre de volatilité (RFC 3227)

```txt
1. Registres CPU / Cache               ← Le plus volatil
2. RAM physique
3. Fichier d'hibernation (hiberfil.sys)
4. Fichier d'échange (pagefile.sys / swap)
5. Fichiers temporaires
6. Disque dur                           ← Le moins volatil
```

### Précautions avant acquisition

```txt
□ 1. PREPARER LE SUPPORT DE DESTINATION
   - Disque/SSD externe formaté en NTFS/exFAT
   - Espace suffisant (RAM × 1.5 pour image + metadata)
   - Hash du support vierge (avant copie)

□ 2. OUTILS PRÊTS SUR CLÉ USB
   - WinPMEM / DumpIt / FTK Imager portable
   - Write-blocker software désactivé (on va écrire en RAM, pas sur disque)
   - NE PAS installer sur le système cible

□ 3. DOCUMENTER L'ÉTAT DU SYSTÈME
   - Heure système (comparer avec NTP)
   - Processus visibles (taskmgr)
   - Connexions réseau (netstat)
   - Utilisateurs connectés
   - Applications ouvertes

□ 4. EXÉCUTION
   - Capturer la RAM avant toute autre action
   - Ne pas éteindre/redémarrer le système
```

---

## 2. Acquisition sous Windows

### WinPMEM (Open Source, Recommandé)

```bash
# Télécharger WinPMEM depuis GitHub
# https://github.com/google/win-pmem/releases

# Installation du driver
winpmem_mini_v3.2.rc4.exe -l       # Lister la mémoire
winpmem_mini_v3.2.rc4.exe memory.raw   # Acquisition vers fichier RAW

# Avec compression
winpmem_mini_v3.2.rc4.exe -o output.raw
# Format par défaut : RAW (traitement Volatility compatible)

# Driver signé Microsoft (Windows 10/11 compatible)
# --driver : spécifier un driver personnalisé si nécessaire

# Acquisition vers un support réseau
winpmem_mini_v3.2.rc4.exe \\network\share\case\memory.raw
```

### DumpIt (Magnet Forensics, Simple)

```bash
# DumpIt.exe — Un seul exécutable, interface console
# Usage : double-clic ou ligne de commande
DumpIt.exe
# Génère : <HOSTNAME>_<DATE>_<TIME>.raw

# Accepte les arguments :
DumpIt.exe /outpath=D:\RAM_CAPTURES\ /filename=incident_001.raw

# Avantages :
# - Pas d'installation, driver embarqué
# - Interface simple (Y/n)
# - Compatible toutes versions Windows
```

### FTK Imager (AccessData)

```bash
# GUI : File → Capture Memory
# Options :
#   - Include pagefile : capture aussi pagefile.sys
#   - Créer un crash dump : .dmp (WinDbg compatible)
#   - Compression : Fast / Best

# Avantages :
# - Interface graphique complète
# - Capture RAM + pagefile en une passe
# - Rapport d'acquisition automatique
```

### Belkasoft Live RAM Capturer

```bash
# Petit outil, très rapide
# Supporte Windows 10/11, 32/64-bit
# Driver signé

RAMCapturer.exe /output D:\RAM_CAPTURES\ /filename case1
# Format : .mem
```

### MDD (Memory DD)

```bash
# Simple, léger
mdd.exe -o memory.dmp
# Format : .dmp (identique RAW)
```

### Acquisition via PowerShell (limité)

```powershell
# Méthode limitée : ne capture QUE l'espace du processus courant
# Utile seulement pour debug, pas pour forensics

# Win32_Process — ne donne pas la RAM physique
# Alternatives : appels kernel non documentés (Zer0mem)
```

---

## 3. Acquisition sous Linux

### LiME (Linux Memory Extractor) — Recommandé

```bash
# Compilation
git clone https://github.com/504ensicsLabs/LiME.git
cd LiME/src
make

# Acquisition
insmod lime.ko "path=/evidence/memory.lime format=lime"
# ou via dd après chargement
# Formats :
#   lime : format LiME natif (recommandé, compressé)
#   raw : RAW (plus gros, plus rapide)
#   padded : RAW avec padding pour adresses manquantes

# Acquisition vers réseau
insmod lime.ko "path=tcp://192.168.1.100:4444 format=lime"

# Dégager le module
rmmod lime
```

### fmem

```bash
# fmem — Module noyau, crée /dev/fmem
# Alternative à LiME, plus simple

git clone https://github.com/NateBrune/fmem.git
cd fmem
make
insmod fmem.ko
dd if=/dev/fmem of=memory.raw bs=1M status=progress
```

### avml (Acquisition via /proc/kcore)

```bash
# AVML — Acquire Volatile Memory for Linux
# https://github.com/microsoft/avml
# Fonctionne sans module noyau (utilise /proc/kcore)

avml output.raw
avml --compress output.lz4  # Avec compression LZ4
avml --format lime output.lime  # Format LiME
```

### LiGURIO (Forensic Artifact Collector)

```bash
# Collecte RAM + autres artefacts (bash history, logs, ...)
ligurio --output /evidence/
```

### Acquisition distante

```bash
# Via netcat
# Serveur :
nc -l -p 4444 > memory.lime
# Client :
insmod lime.ko "path=tcp://192.168.1.100:4444 format=lime"

# Via SSH
ssh root@target "dd if=/dev/fmem bs=1M" | dd of=memory.raw bs=1M
```

---

## 4. Acquisition sous macOS

### osxpmem

```bash
# Version macOS de PMEM
# https://github.com/google/rekall/releases

osxpmem.app/Contents/MacOS/osxpmem -o memory.raw

# Limitation : SIP (System Integrity Protection)
# SIP doit être désactivé pour /dev/mem :

# Vérifier SIP
csrutil status

# Désactiver SIP (nécessite redémarrage en Recovery)
# Cmd+R au boot → Terminal :
csrutil disable
```

### macOS Memory Acquisition (avml)

```bash
# avml supporte aussi macOS (Intel + Apple Silicon)
avml-macos memory.raw
```

### Acquisition via FireWire (DMA)

```bash
# Contourne SIP/FileVault
# Utilise le port Thunderbolt/FireWire
# Outils : Inception, MacForensicsLab

# L'adaptateur DMA (PCIe-Thunderbolt) donne accès direct à la RAM
# Même sur système verrouillé !
```

---

## 5. Acquisition Hibernation et Swap

### Hiberfil.sys (Windows)

```bash
# Fichier d'hibernation = snapshot RAM compressé
# C:\hiberfil.sys — présent si hibernation activée

# Capturer :
copy C:\hiberfil.sys D:\evidence\

# Analyser avec Volatility :
# ATTENTION : format compressé ! Décompresser d'abord :
# Volatility 3 gère automatiquement (hibernation mode)

# V2 : profile spécifique
volatility -f hiberfil.sys --profile=Win10x64 imageinfo

# V3 : auto-détection
python3 vol.py -f hiberfil.sys windows.info

# Limitations :
# - Pas d'état réseau (connexions fermées)
# - Pas de threads actifs
# - Certaines pages mémoire non incluses
```

### Pagefile.sys (Windows)

```bash
# Fichier d'échange — contient des fragments mémoire
# C:\pagefile.sys

# Toujours capturer avec la RAM !
# Peut contenir :
#   - Mots de passe
#   - Clés de chiffrement
#   - Données de processus terminés

# Analyse :
# strings pagefile.sys | grep -E "password|key|secret|token"
# Volatility ne peut pas parser directement → extraction strings

# Plusieurs pagefiles possibles (C:, D:, ...)
# pagefile.sys, swapfile.sys (Windows 8+)
```

### Swap Linux

```bash
# Partition swap séparée
# swapon --show  # Voir les partitions swap

# Capturer la partition
dd if=/dev/sda5 of=/evidence/swap.dd bs=1M   # Partition swap

# Analyse
strings swap.dd | grep -E "password|key|https?://"
volatility -f swap.dd linux.banner  # Limitée
```

---

## 6. Acquisition à Chaud vs à Froid

### Acquisition à chaud (Live)

```txt
AVANTAGES :
✓ Capture l'état exact du système en fonctionnement
✓ Connexions réseau actives conservées
✓ Processus en mémoire non pertes
✓ Pas de risque de corruption disque (contenu RAM intact)

INCONVÉNIENTS :
✗ Modification minimale de la RAM (outil ajoute des pages)
✗ Pas possible sur système crypté (sauf si déjà déverrouillé)
✗ Risque de détection par malware (anti-forensics)
✗ Système doit rester allumé
```

### Acquisition à froid (Cold Boot Attack)

```txt
PRINCIPE :
La mémoire RAM conserve ses données quelques secondes/minutes
après coupure d'alimentation (notamment à basse température).

MÉTHODE :
1. Rebooter à froid depuis un périphérique USB
2. Lancer un mini-OS qui capture la RAM résiduelle
3. Analyser les données (notamment clés de chiffrement)

OUTILS :
- Cold Boot Toolkit (Passware)
- FROST (FPGA-based cold boot)
- Air quotes (refroidir la RAM avec azote liquide)

LIMITATIONS :
✗ DDR4/DDR5 : données se dégradent en <10 secondes
✗ Soudure RAM (soudé sur la carte mère)
✗ TRIM sur SSD efface les données avant capture
✗ BitLocker avec TPM 2.0 : clé disparaît au redémarrage

AVANTAGES :
✓ Contourne le verrouillage OS
✓ Capture même sans droits admin
✓ Idéal pour machines avec Full Disk Encryption déverrouillée
```

---

## 7. Acquisition DMA (Direct Memory Access)

### PCIe / Thunderbolt DMA

```bash
# Attaque DMA via Thunderbolt/PCIe pour capturer RAM
# Fonctionne même sur système verrouillé !

# Outils matériels :
# - PCILeech (FPGA, ~300€)
# - Inception (FireWire)
# - Acquisitor (USB3)

# Avec PCILeech :
# 1. Brancher le dispositif FPGA
# 2. Lancer PCILeech
python leech.py -device fpga -target ram -out memory.raw

# Contourne :
# - BitLocker (clé en mémoire après déverrouillage)
# - Écran verrouillé
# - Absence de droits admin

# Protection :
# - Kernel DMA Protection (Windows 10 1803+)
# - IOMMU (VT-d / AMD-Vi)
# - Désactiver Thunderbolt en BIOS
```

---

## 8. Vérification de l'Intégrité

### Hash de l'image mémoire

```bash
# Après acquisition, hasher immédiatement
sha256sum memory.raw > memory.raw.sha256
md5sum memory.raw >> memory.raw.sha256

# Si l'outil le supporte, le hash est intégré
# FTK Imager : hash dans le rapport
# WinPMEM : pas de hash natif → manuel
```

### Validation de l'intégrité

```bash
# Vérifier que Volatility reconnaît l'image
python3 vol.py -f memory.raw windows.info

# Vérifier que les structures KDBG sont cohérentes
python3 vol.py -f memory.raw windows.pdbscan

# Détection de corruption :
# - Banners incomplets
# - Processus sans parent
# - Adresses mémoire invalides
```

---

## 9. Formats de Sortie Comparaison

| Format | Description | Compression | Volatility | Taille |
|--------|-------------|-------------|------------|--------|
| RAW | Binaire brut | Aucune | Oui ✓ | = RAM |
| LIME | LiME natif | Oui (lzo) | Oui ✓ | ~50% RAM |
| Crash Dump | .dmp (WinDbg) | Oui | Oui ✓ | Variable |
| Hibernation | .sys compressé | Oui | Oui ✓ (V3) | ~60% RAM |
| ELF | Core dump Linux | Non | Légèrement | = RAM |
| Mach-O | Core dump macOS | Non | Légèrement | = RAM |

---

## 10. Script d'Acquisition Automatisée

### Script Windows Batch

```batch
@echo off
REM acquire_ram.bat — Acquisition mémoire automatisée

set OUTDIR=D:\RAM_CAPTURES\%COMPUTERNAME%_%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
mkdir %OUTDIR%

echo === RAM ACQUISITION ===
echo Target: %COMPUTERNAME%
echo Output: %OUTDIR%
echo Date: %DATE% %TIME%
echo.

REM 1. Système info
echo [1] System info...
systeminfo > %OUTDIR%\systeminfo.txt

REM 2. Liste des processus
echo [2] Process list...
tasklist /v > %OUTDIR%\tasklist.txt

REM 3. Connexions réseau
echo [3] Network connections...
netstat -anob > %OUTDIR%\netstat.txt

REM 4. Capture RAM
echo [4] Capturing RAM with DumpIt...
DumpIt.exe /outpath=%OUTDIR% /quiet

REM 5. Capturer pagefile
echo [5] Copying pagefile.sys...
copy C:\pagefile.sys %OUTDIR%\pagefile.sys

REM 6. Capturer hiberfil (si présent)
if exist C:\hiberfil.sys (
    echo [6] Copying hiberfil.sys...
    copy C:\hiberfil.sys %OUTDIR%\hiberfil.sys
)

REM 7. Hash
echo [7] Hashing...
certutil -hashfile %OUTDIR%\*.raw SHA256 > %OUTDIR%\hashes.txt

echo === ACQUISITION COMPLETE ===
echo Files saved to: %OUTDIR%
```

### Script Linux Bash

```bash
#!/bin/bash
# acquire_ram_linux.sh

OUTDIR="/evidence/ram_$(hostname)_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

echo "=== RAM ACQUISITION ==="
echo "Target: $(hostname)"
echo "Output: $OUTDIR"

# 1. Info système
echo "[1] System info..."
uname -a > "$OUTDIR/uname.txt"
cat /proc/cpuinfo > "$OUTDIR/cpuinfo.txt"
free -h > "$OUTDIR/memory.txt"
lshw -short > "$OUTDIR/hardware.txt"

# 2. Processus
echo "[2] Process list..."
ps auxf > "$OUTDIR/ps_aux.txt"
lsmod > "$OUTDIR/lsmod.txt"

# 3. Réseau
echo "[3] Network..."
ss -tupan > "$OUTDIR/ss.txt"
netstat -rn > "$OUTDIR/routes.txt"

# 4. RAM via LiME (si chargé)
echo "[4] LiME acquisition..."
if lsmod | grep -q lime; then
    dd if=/dev/liME of="$OUTDIR/memory.lime" bs=1M 2>/dev/null && echo "LiME OK"
elif [ -f /dev/fmem ]; then
    dd if=/dev/fmem of="$OUTDIR/memory.raw" bs=1M status=progress
elif [ -r /proc/kcore ]; then
    # AVML style — fallback
    dd if=/proc/kcore of="$OUTDIR/memory.raw" bs=1M status=progress 2>/dev/null
fi

# 5. Swap
echo "[5] Swap capture..."
swapon --show | tail -n +2 | awk '{print $1}' | while read swapdev; do
    dd if="$swapdev" of="$OUTDIR/$(basename $swapdev).swap" bs=1M status=progress 2>/dev/null
done

# 6. Hash
echo "[6] Hashing..."
sha256sum "$OUTDIR"/memory.* "$OUTDIR"/*.swap > "$OUTDIR/hashes.txt" 2>/dev/null

echo "=== DONE ==="
echo "Files: $OUTDIR"
```

---

## 11. Contre-Mesures Anti-Forensics

### Détection d'acquisition mémoire

```bash
# Un malware peut détecter qu'on capture la RAM :
# - Driver inconnu chargé
# - /dev/mem ou /dev/fmem ouvert
# - Taille de la mémoire modifiée
# - Ralentissement système

# Signes d'alerte pour l'enquêteur :
# - Suppression de l'outil après acquisition
# - Crash du système pendant acquisition
# - Image vide ou corrompue

# Techniques anti-forensics mémoire :
# - Mémoire chiffrée (VBS, enclave Intel SGX)
# - Hooking des appels de dump mémoire
# - Mémoire paginée volontairement
# - Détection DMA (IOMMU)
```

---

## 12. Bonnes Pratiques

```txt
□ TOUJOURS capturer la RAM en premier
□ Utiliser un support de destination propre (formaté + hash)
□ Documenter l'heure système avant acquisition
□ Noter tout changement d'état (fenêtres fermées ?)
□ Hasher l'image immédiatement après création
□ Conserver une copie de travail (travailler sur la copie)
□ Stocker l'original dans un coffre (write-once media)
□ Utiliser un write-blocker pour la destination si possible
□ Faire au moins 2 acquisitions si possible
□ Chaîne de custody documentée
```

---

## 13. Ressources

- **WinPMEM** : https://github.com/google/win-pmem
- **LiME** : https://github.com/504ensicsLabs/LiME
- **AVML** : https://github.com/microsoft/avml
- **DumpIt** : https://www.magnetforensics.com/resources/magnet-dumpit/
- **FTK Imager** : https://www.exterro.com/ftk-imager
- **PCILeech** : https://github.com/ufrisk/pcileech
- **Cold Boot Toolkit** : https://www.passware.com/cold-boot/
- **Volatility + LiME Tutorial** : https://www.13cubed.com/downloads/memory_triage.pdf