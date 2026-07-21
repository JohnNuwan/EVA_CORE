---
name: file-carving-recovery
description: Guide complet de file carving et récupération de données — Foremost, Scalpel, Photorec/TestDisk, Bulk Extractor, binwalk, signatures de fichiers, carving avancé (fragmentation, carving GPU, carving cross-drive), et reconstruction de fichiers
tags: [forensics, file-carving, foremost, scalpel, photorec, bulk-extractor, binwalk, data-recovery]
version: 1.0
---

# File Carving et Récupération — Guide Complet

Guide exhaustif des techniques d'extraction de fichiers depuis l'espace non alloué, la mémoire, et les supports endommagés.

---

## 1. Principes Fondamentaux

### Qu'est-ce que le File Carving ?

Le file carving est la technique de récupération de fichiers sans utiliser le système de fichiers (filesystem). On se base uniquement sur les **signatures magiques** (magic bytes) pour identifier et extraire les fichiers.

### Quand l'utiliser ?

```txt
✓ Système de fichiers corrompu ou effacé
✓ Fichiers supprimés (MFT/FAT entries effacées)
✓ Espace non alloué (unallocated space)
✓ Slack space (espace entre la fin du fichier et la fin du cluster)
✓ Mémoire RAM (processus, pages)
✓ Firmware images (binwalk)
✓ Supports formatés
✓ Données résiduelles après TRIM (partiellement)
✓ Acquisition réseau (pcap → fichiers)
```

### Limitations

```txt
✗ Fichiers fragmentés (plusieurs fragments non contigus)
✗ Fichiers écrasés (overwritten)
✗ TRIM sur SSD (effacement physique des cellules)
✗ Chiffrement (données chiffrées = signatures invisibles)
✗ Petits fichiers (moins que la taille de l'en-tête)
✗ Fichiers sans signature connue
✗ RAID sans striping connu
```

---

## 2. Foremost

### Installation

```bash
sudo apt install foremost
# ou compilation
git clone https://github.com/kmmiles/foremost.git && cd foremost && make
```

### Usage de Base

```bash
# Extraction de TOUS les types configurés
foremost -i disk.dd -o /evidence/carved/

# Types spécifiques
foremost -t jpg,png,gif -i disk.dd -o /evidence/images/

# Avec configuration personnalisée
foremost -c /etc/foremost.conf -i disk.dd -o /evidence/carved/

# Depuis une image partitionnée (offset)
foremost -i disk.dd -o /evidence/ -s 2048   # Start sector 2048
```

### Configuration Foremost

```conf
# /etc/foremost.conf (ou custom.conf)
# Format :
# type | extension | case-sensitive | size_min | size_max | header_pattern | footer_pattern

# Images
jpg      y   20000000   \xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01    \xff\xd9
png      y   20000000   \x89\x50\x4e\x47\x0d\x0a\x1a\x0a                     \x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82
gif      y   5000000    \x47\x49\x46\x38\x39\x61                              \x00\x3b
bmp      y   5000000    \x42\x4d                                              
tiff     y   50000000   \x49\x49\x2a\x00                                      \x00\x00\x00\x00\x00\x00\x00\x00

# Documents
pdf      y   50000000   \x25\x50\x44\x46                                       \x0a\x25\x25\x45\x4f\x46\x0a
doc      y   50000000   \xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1                      
xls      y   50000000   \xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1                      
ppt      y   50000000   \xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1                      

# Archives
zip      y   100000000  \x50\x4b\x03\x04                                       \x50\x4b\x05\x06
rar      y   100000000  \x52\x61\x72\x21\x1a\x07\x00                           \x00\x00\x00\x00\x00\x00\x00\x00
7z       y   100000000  \x37\x7a\xbc\xaf\x27\x1c                              

# Audio/Video
mp3      y   50000000   \xff\xfb\x90\x00                                       \x00\x00\x00\x00\x00\x00\x00\x00
mp4      y   500000000  \x00\x00\x00\x1c\x66\x74\x79\x70\x6d\x70\x34\x32       
avi      y   500000000  \x52\x49\x46\x46                                       \x00\x00\x00\x00\x00\x00\x00\x00

# Executables
exe      y   50000000   \x4d\x5a                                               
elf      y   50000000   \x7f\x45\x4c\x46                                       
```

### Foremost Avancé

```bash
# Extraction depuis la mémoire RAM
foremost -t jpg,png,doc,pdf -i memory.raw -o /evidence/mem_carved/

# Depuis une image distante (pipe)
ssh user@host "dd if=/dev/sda bs=4M" | foremost -t jpg -o /evidence/ -

# Vérifier ce qui a été trouvé
foremost -V -i disk.dd -o /evidence/  # Verbose

# Statistiques
cat /evidence/carved/audit.txt
# Résultat :
# Foremost finished at Mon Jul 22 15:30:00 2024
# 125 files carved
# 115 files recovered (92% recovery)
# 10 files failed (checksum mismatch)
```

---

## 3. Scalpel

### Installation

```bash
sudo apt install scalpel
```

### Configuration

```conf
# /etc/scalpel/scalpel.conf
# Activer/désactiver les types en décommentant les lignes

# Format :
# extension | case-sensitive | size | header pattern | footer pattern

# Activer pour les images JPEG
jpg        y   30000000  \xff\xd8\xff\xe0      \xff\xd9
png        y   30000000  \x89\x50\x4e\x47      \x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82
pdf        y   50000000  \x25\x50\x44\x46      \x0a\x25\x25\x45\x4f\x46\x0a
zip        y   100000000 \x50\x4b\x03\x04      \x50\x4b\x05\x06
doc(x)     y   50000000  \xd0\xcf\x11\xe0      \x00\x00\x00\x00\x00\x00\x00\x00
exe        y   50000000  \x4d\x5a              \x00\x00\x00\x00\x00\x00\x00\x00
```

### Usage

```bash
# Extraction basique
scalpel -o /evidence/scalpel_out/ disk.dd

# Configuration personnalisée
scalpel -c custom.conf -o /evidence/scalpel_out/ disk.dd

# Extraction depuis la RAM
scalpel -o /evidence/scalpel_ram/ memory.raw

# Extraction depuis un répertoire (tous les fichiers)
scalpel -o /evidence/scalpel_dir/ /evidence/files/
```

### Scalpel vs Foremost

```bash
# Différences :
# Foremost : plus rapide, meilleur pour les fichiers contigus
# Scalpel : plus configurable, meilleur pour les formats rares

# Recommandations :
# - Foremost en premier (rapide, 90% des cas)
# - Scalpel pour les types exotiques
# - Toujours essayer les deux pour les cas critiques
```

---

## 4. PhotoRec / TestDisk

### Installation

```bash
sudo apt install testdisk
# Contient : testdisk (partition recovery) + photorec (file carving)
```

### PhotoRec — Interface Interactive

```bash
# Lancer PhotoRec
sudo photorec /evidence/disk.dd

# Étapes :
# 1. Selectionner le support
#    → disk.dd (ou /dev/sda)
#
# 2. Selectionner la table de partitions
#    → [Proceed] si partition table OK
#    → [None] si inconnue ou formatée
#
# 3. Selectionner la partition
#    → [Search] → [Whole partition]
#    → [Free] → Espace non alloué seulement (plus rapide)
#
# 4. Type de filesystem
#    → [Other] = FAT/NTFS/ext2/ext3/ext4
#    → [ext2/ext3] = Linux
#    → [FAT/NTFS/HFS+] = Windows/Mac
#
# 5. Choisir la destination (dossier de sortie)
#
# 6. File formats
#    → File Opt → sélectionner les formats
#    → Default = tous (500+ formats)
#
# 7. [Search] → Démarrer

# Résultat :
# /evidence/recovered/
# ├── recup_dir.1/
# │   ├── f12345678.jpg
# │   ├── f12345679.png
# │   └── ...
# ├── recup_dir.2/
# └── ...
```

### PhotoRec en CLI (Non-interactive)

```bash
# Mode non-interactif (scriptable)
# Écrire les réponses dans un fichier
cat > photorec_answers.txt << 'EOF'
disk.dd
[Proceed]
[Search]
[Free]
[Other]
File Opt
jpg, png, pdf, doc, zip, exe
q
/recovery/
Y
EOF

# Lancer avec les réponses pré-écrites
sudo photorec < photorec_answers.txt
```

### TestDisk — Récupération de Partitions

```bash
# TestDisk = récupération de tables de partitions effacées
# Lancement
sudo testdisk /evidence/disk.dd

# Workflow :
# 1. [Create] → nouveau log file
# 2. Choisir le type de partition (Intel/EFI/Mac/None)
# 3. [Analyse] → Current partition structure
# 4. [Quick Search] → recherche rapide
# 5. Lister les partitions trouvées
# 6. [Write] → écrire la nouvelle table (sur l'image)
# 7. Montez l'image → les partitions sont visibles

# TestDisk peut récupérer :
# - Table MBR effacée
# - Table GPT corrompue
# - Superblock ext4 perdu
# - Partition FAT/NTFS supprimée
# - Boot sector corrompu
```

---

## 5. Bulk Extractor

### Installation

```bash
sudo apt install bulk-extractor
# ou compilation
git clone https://github.com/simsong/bulk_extractor.git
cd bulk_extractor && make && sudo make install
```

### Usage de Base

```bash
# Extraction de TOUS les artefacts
bulk_extractor -o /evidence/bulk_out/ disk.dd
# Résultat :
# /evidence/bulk_out/
# ├── email.txt          # Emails trouvés
# ├── email_histogram.txt  # Statistiques emails
# ├── url.txt            # URLs
# ├── telephone.txt      # Numéros de téléphone
# ├── credit_card.txt    # Cartes de crédit
# ├── ssn.txt            # Numéros de sécurité sociale
# ├── domain.txt         # Domaines DNS
# ├── ethernet.txt       # Adresses MAC
# ├── ip.txt             # Adresses IP
# ├── zip.txt            # Archives ZIP trouvées
# ├── base64.txt         # Base64 patterns
# ├── aes_keys.txt       # Clés AES potentielles
# ├── wordlist.txt       # Mots de passe potentiels
# └── report.xml         # Rapport XML
```

### Scanners Spécifiques

```bash
# Scanner emails uniquement (rapide)
bulk_extractor -e net -o /evidence/email_only/ disk.dd

# Scanner URLs + Emails + ZIP
bulk_extractor -e net -e zip -o /evidence/combined/ disk.dd

# Scanner base64 (détection de données encodées)
bulk_extractor -e base64 -o /evidence/base64_out/ disk.dd

# Scanner AES/RSA keys
bulk_extractor -e aes -e rsakey -o /evidence/crypto_keys/ disk.dd

# Depuis la RAM
bulk_extractor -o /evidence/memory_bulk/ memory.raw

# Avec limites de taille
bulk_extractor -S max_size=100000000 -o /evidence/limited/ disk.dd
```

### Bulk Extractor Avancé

```bash
# Regex personnalisée
bulk_extractor -R /evidence/custom_regex.txt -o /evidence/custom_out/ disk.dd

# Format du fichier de regex :
# # Comment line
# FindPattern  /regex/ flags
# Exemple :
FindPattern /[A-Z]{3}-\d{4}-\d{4}-\d{4}-\d{3}/I  # Code type "ABC-1234-5678-9012-345"

# Avec exclusion de certaines zones
bulk_extractor -o /evidence/out/ \
   -e net -e zip \
   -E export_only  # Exporte seulement les artefacts, pas de carving

# Light mode (RAM optimization)
bulk_extractor -o /evidence/light/ -S light_mode=1 disk.dd
```

---

## 6. Binwalk — Analyse de Firmware

### Installation

```bash
sudo apt install binwalk
git clone https://github.com/ReFirmLabs/binwalk.git
cd binwalk && sudo python3 setup.py install
```

### Usage

```bash
# Scanner les signatures
binwalk firmware.bin
# Résultat :
# DECIMAL    HEX        DESCRIPTION
# 0          0x0        U-Boot version 2023.07
# 262144     0x40000    LZMA compressed data
# 1048576    0x100000   Squashfs filesystem, little endian
# 20971520   0x1400000  JPEG image data

# Extraction automatique
binwalk -e firmware.bin
# Crée : _firmware.bin.extracted/

# Extraction récursive (firmware dans firmware)
binwalk -Me firmware.bin

# Analyse d'entropie (sections compressées = haute entropie)
binwalk -E firmware.bin
# Affichage graphique de l'entropie par offset

# Détection d'instructions CPU
binwalk -A firmware.bin
# Résultat : ARM, MIPS, x86, etc.

# Analyse des opcodes
binwalk -Y firmware.bin

# Extraction avec délai minimum
binwalk -D 'type:extension:cmd' firmware.bin
# Exemple : binwalk -D 'squashfs:squashfs:unsquashfs -d %d %f' firmware.bin
```

---

## 7. Signatures de Fichiers (Magic Bytes)

### Signatures d'En-tête

```hex
=== IMAGES ===
JPEG       : FF D8 FF E0 (JFIF) / FF D8 FF E1 (Exif)
PNG        : 89 50 4E 47 0D 0A 1A 0A
GIF87a     : 47 49 46 38 37 61
GIF89a     : 47 49 46 38 39 61
BMP        : 42 4D
TIFF (LE)  : 49 49 2A 00
TIFF (BE)  : 4D 4D 00 2A
RIFF/WEBP  : 52 49 46 46 ... 57 45 42 50

=== AUDIO ===
MP3 (ID3v2): 49 44 33
MP3 (no ID3): FF FB / FF F2 / FF F3
WAV        : 52 49 46 46 ... 57 41 56 45
FLAC       : 66 4C 61 43
OGG        : 4F 67 67 53

=== VIDEO ===
MP4         : 00 00 00 1C 66 74 79 70 [6D 70 34 32 / 69 73 6F 6D]
AVI         : 52 49 46 46 ... 41 56 49 20
MKV/WebM    : 1A 45 DF A3
FLV         : 46 4C 56 01
WMV/ASF     : 30 26 B2 75 8E 66 CF 11

=== DOCUMENTS ===
PDF         : 25 50 44 46
OLE2 (doc/xls/ppt) : D0 CF 11 E0 A1 B1 1A E1
OOXML (docx/xlsx/pptx) : 50 4B 03 04 ... [Content_Types]
RTF         : 7B 5C 72 74 66

=== ARCHIVES ===
ZIP        : 50 4B 03 04 (empty: 50 4B 05 06, spanned: 50 4B 07 08)
RAR        : 52 61 72 21 1A 07 00 (v5: 52 61 72 21 1A 07 01)
7-Zip      : 37 7A BC AF 27 1C
GZIP       : 1F 8B 08
BZ2        : 42 5A 68
TAR        : (200×00) ou fichiers ASCII
LZMA       : 5D 00 00 ...

=== EXECUTABLES ===
PE (exe/dll) : 4D 5A (MZ)
ELF        : 7F 45 4C 46
Mach-O     : FE ED FA CE / FE ED FA CF / CE FA ED FE / CF FA ED FE
Java Class : CA FE BA BE

=== BASE DE DONNÉES ===
SQLite     : 53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00
```

### Footer Signatures

```hex
JPEG       : FF D9
PNG        : 00 00 00 00 49 45 4E 44 AE 42 60 82
GIF        : 00 3B
ZIP        : 50 4B 05 06 (End of Central Directory)
PDF        : 0A 25 25 45 4F 46 0A
RIFF       : (varies — calculer depuis le header)
```

### Vérification Manuelle

```bash
# Vérifier les magic bytes d'un fichier
xxd -l 16 suspect.file
hexdump -C -n 20 suspect.file

# Chercher une signature dans une image disque
xxd disk.dd | grep "ffd8ffe0" | head -5   # JPEG header
xxd disk.dd | grep "ffd9" | head -5       # JPEG footer

# Avec sigfind (Sleuth Kit)
sigfind -l disk.dd                        # Lister toutes les signatures
sigfind -i ffd8 -o ffe0 disk.dd          # Trouver JPEG
sigfind -i 25504446 disk.dd              # Trouver PDF
```

---

## 8. Carving Avancé

### Carving Fragmente

```bash
# Les fichiers fragmentés (non contigus) sont le défi du carving

# Détection de fragmentation :
# 1. Examiner le bitmap MFT pour les clusters non contigus
# 2. Calculer la distance entre les fragments
# 3. Utiliser un carver intelligent

# Outils pour la fragmentation :
# - SmartCarver : réordonnancement des fragments
# - Defraser (MPEG only) : reconstruction vidéo
# - PhotoRec : support de base pour la fragmentation

# Méthode manuelle (recherche des parties manquantes) :
# 1. Identifier les gaps dans la reconstruction
# 2. Chercher les fragments dans l'espace non alloué
# 3. Tenter de les réassembler par taille
```

### Carving sur RAM

```bash
# Depuis un dump mémoire
foremost -t jpg,png,zip -i memory.raw -o /evidence/memory_carved/
bulk_extractor -o /evidence/memory_bulk/ memory.raw

# Artefacts spécifiques qu'on trouve dans la RAM :
# - Mots de passe en clair
# - Images non sauvegardées (viewer, browser)
# - Documents ouverts (modifications non sauvegardées)
# - URLs visitées
# - Conversation de messagerie
# - Codes d'authentification (tokens)
```

### Carving Cross-Drive

```bash
# Corrélation entre plusieurs images
# Rechercher des fragments liés entre plusieurs disques

# 1. Extraire tous les fichiers de chaque image
for img in /evidence/*.dd; do
    foremost -i "$img" -o "/evidence/carved_$(basename $img)/"
done

# 2. Dédupliquer par hash
find /evidence/carved_*/ -type f -exec sha256sum {} \; | \
    sort -u -k1 > all_hashes.txt

# 3. Trouver les fichiers uniques à chaque image
# Les doublons = fichiers système ou applications
# Les uniques = preuves potentielles

# 4. Analyse croisée (présence d'un même fichier suspect sur 2 machines)
```

### Carving GPU (accéléré)

```bash
# Pour les très gros volumes (> 1 TB)
# Utiliser CUDA pour paralléliser

# Outils :
# - GPU-Foremost (recherche parallèle sur GPU)
# - gpu-carver (projets académiques)

# Limitation : peu d'outils matures, overhead de transfert RAM↔GPU
# Utile principalement pour les signatures simples (JPEG, PNG)
```

---

## 9. Reconstruction de Fichiers

### Réparation de JPEG Corrompu

```bash
# JPEG avec mauvais footer
python3 << 'EOF'
import struct

def fix_jpeg(infile, outfile):
    with open(infile, 'rb') as f:
        data = f.read()
    
    # Trouver le dernier marker SOS (start of scan)
    sos_idx = data.rfind(b'\xff\xda')
    if sos_idx == -1:
        print("No SOS marker found")
        return
    
    # Le scan data va jusqu'à FF D9 (ou FF xx si partiel)
    eoi_idx = data.find(b'\xff\xd9', sos_idx)
    
    if eoi_idx == -1:
        # Pas de EOI → ajouter
        data += b'\xff\xd9'
        print("Added missing EOI marker")
    
    with open(outfile, 'wb') as f:
        f.write(data)
    print(f"Fixed JPEG saved to {outfile}")

fix_jpeg('broken.jpg', 'repaired.jpg')
EOF
```

### Réparation de ZIP/RAR

```bash
# ZIP partiel — en-tête de fin manquant
# Utiliser zipfix ou zzip

# Test intégrité
zip -T suspect.zip

# Réparation
zip -F suspect.zip --out repaired.zip
zip -FF suspect.zip --out deep_repaired.zip

# RAR repair
unrar t suspect.rar   # Test
unrar r suspect.rar  # Repair
```

### Extraction de Données Depuis un Document Partiel

```bash
# Strings extraction
strings broken.pdf | grep -E "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
strings broken.docx | grep -E "https?://"
strings memory.raw | grep -E "password|secret|token" | sort -u
```

---

## 10. Validation des Fichiers Carvés

### Vérification d'Intégrité

```bash
# Vérification par type
# JPEG
identify -verbose carved_image.jpg 2>/dev/null && echo "Valid JPEG" || echo "Corrupt JPEG"

# PNG
pngcheck carved_image.png && echo "Valid PNG" || echo "Corrupt PNG"

# PDF
pdfinfo carved_doc.pdf 2>/dev/null && echo "Valid PDF" || echo "Corrupt PDF"

# ZIP
unzip -t carved_archive.zip 2>/dev/null && echo "Valid ZIP" || echo "Corrupt ZIP"

# Batch validation
for f in /evidence/carved/*; do
    case $(file -b "$f") in
        *JPEG*)     identify "$f" 2>/dev/null || echo "BAD: $f" ;;
        *PNG*)      pngcheck "$f" 2>/dev/null || echo "BAD: $f" ;;
        *PDF*)      pdfinfo "$f" 2>/dev/null || echo "BAD: $f" ;;
        *Zip*)      unzip -t "$f" 2>/dev/null || echo "BAD: $f" ;;
    esac
done > validation_report.txt
```

### Déduplication par Hash

```bash
# Supprimer les doublons (même fichier carvé plusieurs fois)
find /evidence/carved/ -type f -exec sha256sum {} \; | \
    sort | \
    uniq -w 64 -d | \
    cut -d' ' -f3- | \
    while read f; do rm "$f"; done

# Statistiques
find /evidence/carved/ -type f | wc -l   # Nombre de fichiers
du -sh /evidence/carved/                # Taille totale
file /evidence/carved/* | awk -F: '{print $2}' | sort | uniq -c | sort -rn  # Par type
```

---

## 11. Script d'Extraction Automatisée

```bash
#!/bin/bash
# batch_carving.sh — Extraction multi-outils automatisée

IMAGE="$1"
OUTDIR="/evidence/carved_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

echo "=== BATCH CARVING ==="
echo "Image: $IMAGE"
echo "Output: $OUTDIR"
echo ""

# Stage 1: Foremost
echo "[1/4] Foremost..."
mkdir -p "$OUTDIR/foremost"
foremost -t jpg,png,gif,bmp,pdf,doc,docx,xls,xlsx,ppt,pptx,zip,rar,exe -i "$IMAGE" -o "$OUTDIR/foremost"

# Stage 2: Scalpel
echo "[2/4] Scalpel..."
mkdir -p "$OUTDIR/scalpel"
scalpel -o "$OUTDIR/scalpel" "$IMAGE"

# Stage 3: Bulk Extractor
echo "[3/4] Bulk Extractor..."
mkdir -p "$OUTDIR/bulk"
bulk_extractor -o "$OUTDIR/bulk" "$IMAGE"

# Stage 4: Photorec
echo "[4/4] PhotoRec..."
# Auto-réponse pour PhotoRec (non-interactive)
# (normallement interactif — soit utiliser expect, soit lancer manuellement)
echo "Run: sudo photorec $IMAGE"
echo "Output dir: $OUTDIR/photorec"
echo ""

# Validation
echo "=== VALIDATION ==="
for tool in foremost scalpel; do
    count=$(find "$OUTDIR/$tool" -type f 2>/dev/null | wc -l)
    echo "$tool: $count files carved"
done

# Hash list
find "$OUTDIR" -type f -exec sha256sum {} \; > "$OUTDIR/hashes.txt"

echo ""
echo "=== DONE ==="
```

---

## 12. Dépannage

```txt
PROBLÈME : Foremost ne trouve aucun fichier
SOLUTION :
   - Vérifier que l'image n'est pas chiffrée (high entropy partout)
   - Vérifier les signatures dans la config
   - Essayer avec -v (verbose) pour voir ce qu'il scanne
   - Essayer un autre outil (Photorec, Scalpel)

PROBLÈME : Photorec récupère des fichiers corrompus
SOLUTION :
   - Fragmentation (le fichier n'est pas contigu)
   - Utiliser un carver avancé (Recuva, R-Studio)
   - Essayer de reconstruire manuellement

PROBLÈME : Trop de faux positifs
SOLUTION :
   - Affiner les signatures (headers + footers)
   - Filtrer par taille minimale
   - Vérifier les fichiers ouverts avec identifications

PROBLÈME : TRIM sur SSD → rien à carver
SOLUTION :
   - Vérifier l'état TRIM (S.M.A.R.T.)
   - Chercher dans le pagefile.sys / hiberfile.sys
   - Chercher dans les Volume Shadow Copies
```

---

## 13. Ressources

- **Foremost** : https://github.com/kmmiles/foremost
- **Scalpel** : https://github.com/sleuthkit/scalpel
- **TestDisk/PhotoRec** : https://www.cgsecurity.org/
- **Bulk Extractor** : https://github.com/simsong/bulk_extractor
- **Binwalk** : https://github.com/ReFirmLabs/binwalk
- **Magic Bytes DB** : https://www.garykessler.net/library/file_sigs.html
- **SANS SIFT** : https://www.sans.org/tools/sift-workstation/
- **Digital Corpora** : https://digitalcorpora.org/ (images test pour carving)