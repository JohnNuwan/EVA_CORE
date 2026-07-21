---
name: disk-forensics-imaging
description: Guide complet d'imagerie disque forensique — dd, dcfldd, ddrescue, EWF, AFF, formats d'image, write-blockers, acquisition réseau, chaîne de custody, et vérification d'intégrité
tags: [forensics, disk-imaging, dd, ewf, aff, write-blocker, chain-of-custody, acquisition]
version: 1.0
---

# Imagerie Disque Forensique — Guide Complet

Guide exhaustif des techniques d'acquisition et d'imagerie de supports de stockage pour l'investigation numérique.

---

## 1. Principes Fondamentaux

### Règles d'Or de l'Acquisition

```txt
RÈGLE #1 : NE JAMAIS TRAVAILLER SUR L'ORIGINAL
Toujours travailler sur une copie forensique (image bit-à-bit)

RÈGLE #2 : HASHER AVANT ET APRÈS
Hash lecture (source) = Hash écriture (image)

RÈGLE #3 : WRITE-BLOCKER OBLIGATOIRE
Aucune écriture sur le disque source, même accidentelle

RÈGLE #4 : DOCUMENTER
Chaîne de custody, outil, date, personne, hash
```

### Types d'Acquisition

```txt
1. Acquisition physique (bit-for-bit)
   → Copie chaque secteur du disque, y compris l'espace non alloué
   → Inclut les fichiers supprimés, slack space, MFT résiduel
   → Taille = taille totale du disque

2. Acquisition logique
   → Copie seulement les fichiers visibles
   → Ne capture pas les fichiers supprimés
   → Taille = somme des fichiers

3. Acquisition par fichier (targeted)
   → Copie des fichiers spécifiques
   → Utile pour le cloud/partage réseau
   → Format .ad1 (AccessData)
```

---

## 2. Write-Blockers (Protection en Écriture)

### Hardware Write-Blockers

```bash
# Tableau — Standards de l'industrie
┌────────────────────────────────────┐
│ Tableau T8u                     │
│ SATA / SAS / USB 3.0 / IDE         │
│ USB 3.0 host interface              │
│ Display LCD avec statut             │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ WiebeTech Forensic UltraDock       │
│ SATA / SAS / USB / eSATA           │
│ Hot-swappable, HDD/SSD             │
│ Write-block confirmé par LED        │
└────────────────────────────────────┘

# Vérifier que le write-blocker est actif :
# - LED "Blocked" ou "Write-Protect" allumée
# - Le système hôte voit le disque en READ-ONLY
# - Impossible de créer un fichier sur le disque source

# Test :
mount | grep /dev/sdb
# Flags : ro (read-only) OK
```

### Software Write-Blockers

```bash
# Linux : noyau intégré
# Monter avec option ro obligatoire
sudo mount -o ro /dev/sdb1 /mnt/evidence/
sudo mount -o ro,noexec,loop image.dd /mnt/loop/

# Windows : outils logiciels
# - FTK Imager (read-only par défaut)
# - Arsenal Image Mounter
# - OSF Mount

# Linux + Windows :
# Utiliser d'abord un hardware blocker
# Software blocker = backup seulement
# Ne JAMAIS faire confiance à un software blocker seul
```

---

## 3. Outils CLI d'Acquisition

### dd — L'outil fondateur

```bash
# Syntaxe de base
dd if=/dev/sda of=/evidence/image.dd bs=4M conv=noerror,sync status=progress

# Paramètres essentiels :
# if=      : source (fichier, disque, partition)
# of=      : destination (image, fichier, - pour stdout)
# bs=      : block size (4M = optimal performance)
# conv=noerror,sync : continue sur erreur, padding des secteurs défectueux
# status=progress : affiche la progression

# Acquisition complète d'un disque
dd if=/dev/sda of=/mnt/nas/evidence/case001.dd \
   bs=4M conv=noerror,sync status=progress

# Acquisition d'une partition spécifique
dd if=/dev/sda2 of=/evidence/partition_c.dd \
   bs=4M conv=noerror,sync status=progress

# Combinaison avec hash en temps réel
dd if=/dev/sda bs=4M conv=noerror,sync | \
   tee >(sha256sum > /evidence/image.sha256) \
   > /evidence/image.dd

# Vérification
dd if=/evidence/image.dd bs=4M | sha256sum
```

### dcfldd — dd amélioré (US DoD)

```bash
# dcfldd = dd + hash multiple + progression + sortie multiple
sudo apt install dcfldd

# Acquisition avec hash MD5 + SHA256 simultanés
dcfldd if=/dev/sda of=/evidence/image.dd \
   hash=md5,sha256 \
   hashlog=/evidence/hashlog.txt \
   bs=4M \
   conv=noerror,sync \
   status=on

# Sortie vers plusieurs destinations (redondance)
dcfldd if=/dev/sda \
   of=/evidence/image.dd \
   of=/mnt/nas/backup/image.dd \
   hash=sha256 \
   hashlog=/evidence/hashlog.txt

# Progression détaillée
dcfldd if=/dev/sda of=/evidence/image.dd \
   bs=4M \
   hash=sha256 \
   hashwindow=100M \
   hashlog=hashlog.txt \
   statusinterval=1
```

### ddrescue — Sauvetage de disques défectueux

```bash
# ddrescue = pour disques avec bad sectors
sudo apt install gddrescue

# Phase 1 : acquisition rapide (bonnes zones)
sudo ddrescue -d /dev/sda /evidence/image.dd /evidence/rescue.log

# Phase 2 : tentative de récupération des zones difficiles
sudo ddrescue -d -r3 /dev/sda /evidence/image.dd /evidence/rescue.log

# Phase 3 : récupération agressive (peut endommager le disque)
sudo ddrescue -d -r5 -T 1m /dev/sda /evidence/image.dd /evidence/rescue.log

# Statistiques
ddrescue --show-status /evidence/rescue.log
# Résultat : rescued=X%, errsize=Y%, errstatus=Z

# Options importantes :
# -d        : accès direct (contourne le cache OS)
# -rN       : N tentatives de retry
# -T 1m     : timeout 1 minute par secteur
# -b 512    : block size (secteurs)
# -v        : verbose
```

---

## 4. Formats d'Image Forensique

### RAW/DD (.dd, .raw, .img)

```bash
# Avantages :
# - Simple, universel
# - Lecture directe sans outil spécialisé
# - Plus rapide en écriture/lecture

# Inconvénients :
# - Aucune compression (taille = disque)
# - Pas de métadonnées intégrées
# - Pas de segmentation automatique

# Usage :
dd if=/dev/sda of=/evidence/image.dd bs=4M
```

### EWF (Expert Witness Format) — .E01

```bash
# Format standard judiciaire (EnCase)
# Compression + métadonnées + hash

# Création avec ewfacquire
ewfacquire /dev/sda -t /evidence/image.e01 \
   -C "INC-2024-001" \              # Case number
   -N "Disk suspect - PC Principal" # Description
   -e "EVA-MASTER" \                # Examiner
   -d sha256 \                       # Digest hash
   -S 650MB \                        # Segment size (650MB pour CD)
   -c fast                           # Compression (fast/best/none)

# Informations sur l'image
ewfinfo /evidence/image.e01
# Résultat :
#   Case Number: INC-2024-001
#   Description: Disk suspect - PC Principal
#   MD5: a1b2c3d4e5f6...
#   SHA1: 1234567890ab...
#   Compression: deflate (fast)
#   Segments: 5 (e01, e02, e03, e04, e05)

# Vérification
ewfverify /evidence/image.e01
# Vérifie tous les hash intégrés (segment + global)

# Extraction vers RAW
ewfexport /evidence/image.e01 /evidence/exported.dd

# Montage (read-only)
ewfmount /evidence/image.e01 /mnt/ewf/
```

### AFF (Advanced Forensic Format)

```bash
# Format ouvert, compressé, avec métadonnées XML
# Alternative libre à E01

# Création avec aimage ou affconvert
aimage /dev/sda /evidence/image.aff

# Métadonnées
affinfo /evidence/image.aff

# Vérification
affverify /evidence/image.aff

# Conversion E01 → AFF
affconvert -i /evidence/image.e01 -o /evidence/image.aff

# Avantages AFF4 (nouvelle version) :
# - Compression LZMA
# - Chiffrement AES
# - Segmentation
# - Métadonnées RDF/XML
```

### SMART (Segmented)

```bash
# Format propriétaire AccessData (FTK Imager)
# Segmentation intégrée
# Compression, hash, métadonnées

# Création via FTK Imager (GUI uniquement)
# File → Create Disk Image → SMART
```

### Comparaison des Formats

| Format | Compression | Hash intégré | Métadonnées | Segmentation | Universel |
|--------|-------------|--------------|-------------|--------------|-----------|
| RAW/DD | Non | Non | Non | Non | Oui ✓ |
| E01 | Oui (deflate) | MD5+SHA1 | Oui | Oui (650MB) | Oui (ewftools) |
| AFF | Oui (LZMA) | SHA256 | Oui (XML) | Oui | Oui |
| AFF4 | Oui (LZMA) | SHA256 | Oui (RDF) | Oui | Partiel |
| SMART | Oui | SHA1 | Oui | Oui | Non (FTK) |

---

## 5. Acquisition en Réseau

### Acquisition via Netcat

```bash
# Sur le poste d'acquisition (receveur) :
nc -l -p 9999 | tee image.dd | sha256sum > image.sha256

# Sur le poste source (avec write-blocker) :
sudo dd if=/dev/sda bs=4M conv=noerror,sync | nc 192.168.1.100 9999

# Alternative avec cryptcat (chiffré)
cryptcat -l -p 9999 -k "password" > image.dd
```

### Acquisition via SSH

```bash
# SSH avec redirection (ne JAMAIS utiliser sur source non protégée)
# Write-blocker OBLIGATOIRE

ssh examiner@forensic-box "dd if=/dev/sda bs=4M" | \
  tee /evidence/image.dd | sha256sum

# Via netcat dans SSH
ssh target "./nc 192.168.1.100 9999 < /dev/sda" &
nc -l -p 9999 | tee image.dd | sha256sum
```

### Acquisition via iSCSI / SAN

```bash
# Connexion à un LUN SAN en read-only
# Configuration du write-blocker au niveau SAN

iscsiadm -m discovery -t st -p 192.168.1.50
iscsiadm -m node -T iqn.2005-08:target -l

# Vérifier qu'il est en read-only
echo 1 > /sys/block/sdX/device/read-only

# Acquisition
dd if=/dev/sdX of=/evidence/san_image.dd bs=4M
```

---

## 6. Acquisition de Supports Spécifiques

### SSD NVMe

```bash
# Attention au TRIM !!!
# Le TRIM efface physiquement les secteurs supprimés
# → les données supprimées sont IRRÉCUPÉRABLES

# Contournement :
# 1. NE PAS booter sur le SSD
# 2. Utiliser un write-blocker NVMe (Tableau T8u)
# 3. Si possible, cloner avant que le contrôleur n'exécute le TRIM

# Vérifier l'état TRIM :
sudo nvme id-ctrl /dev/nvme0 | grep -i trim

# Acquisition standard
dd if=/dev/nvme0n1 of=/evidence/ssd_image.dd bs=4M conv=noerror,sync
```

### RAID (Hardware + Software)

```bash
# RAID matériel
# L'image se fait du volume logique (pas des disques individuels)
# Sauf si l'enquête nécessite l'analyse des disques séparés

# RAID logiciel (MD/LVM)
# Sur le système source (write-blocker) :
mdadm --detail /dev/md0
dd if=/dev/md0 of=/evidence/raid_image.dd bs=4M

# LVM
lvdisplay
dd if=/dev/vg01/lv_root of=/evidence/lvm_image.dd bs=4M

# Meilleure pratique :
# 1. Capturer chaque disque physique individuellement
# 2. Capturer le volume logique assemblé
# 3. Documenter la configuration RAID
```

### RAM Disk (ImDisk, RAMDrive)

```bash
# Si le suspect utilise un RAM disk :
# 1. Capturer la RAM en premier (avant extinction)
# 2. Le RAM disk est perdu à l'extinction
# 3. Rechercher dans memory dump les données du RAM disk
```

### Cloud Storage (OneDrive, Google Drive, Dropbox)

```bash
# Acquisition logique uniquement
# Pas d'accès physique aux disques

# 1. Capturer le cache local (C:\Users\<user>\AppData\Local\...\!)
# 2. Capturer les fichiers synchronisés
# 3. Demander une export légale auprès du fournisseur cloud
# 4. Pour OneDrive : capture du répertoire OneDrive + base de données sync

# Les fichiers "cloud-only" ne sont pas stockés localement
# → Nécessite accès au compte cloud
```

---

## 7. Acquisition Multiple et Redondance

### Workflow de Double Acquisition

```bash
# Pour les cas critiques, toujours 2 images :

# Image 1 : RAW pour analyse immédiate
dd if=/dev/sda of=/evidence/image_dd.dd bs=4M conv=noerror,sync status=progress

# Image 2 : E01 pour chaîne de custody
ewfacquire /dev/sda -t /evidence/image_e01 \
   -C "INC-001" -e "EVA" -d sha256 -S 650MB -c fast

# Hash de l'image RAW
sha256sum /evidence/image_dd.dd > /evidence/image_dd.sha256

# Vérification E01
ewfverify /evidence/image_e01.e01

# Comparer les hash des 2 images
# hash(source) = hash(raw) = hash(e01 après extraction)
```

### Image à Tiroirs (Multi-Copie)

```bash
# Pour preuve légale et analyse
# 3 tirages recommandés :

# 1. Copie maître (cachetée)
#    - Stockée dans un coffre
#    - Ne JAMAIS ouvrir
#    - Servira de preuve en cas de contestation

# 2. Copie de travail (pour analyse)
#    - Celle qu'on analyse, monte, modifie
#    - On peut la "casser" sans conséquence

# 3. Copie de backup (si la 2 est perdue)
#    - Même hash que la 1
#    - Stockée dans un endroit différent
```

---

## 8. Chaîne de Custody Documentée

### Formulaire d'Acquisition

```txt
┌────────────────────────────────────────────────────────────┐
│ FORMULAIRE D'ACQUISITION FORENSIQUE                        │
├────────────────────────────────────────────────────────────┤
│                                                             │
│ CAS : INC-2024-001                                          │
│ DATE : 22/07/2024                                           │
│                                                             │
│ ── SOURCE ──                                                │
│ Type   : Disque SSD                                         │
│ Modèle : Samsung 870 EVO                                    │
│ SN     : S3Z7NB0M12345                                      │
│ Capacité : 500 GB (465 GiB)                                 │
│ Interface : SATA III                                         │
│ Partitions : 2 (NTFS + FAT32)                                │
│ Estime état : Fonctionnel, 0 bad sectors                    │
│                                                             │
│ ── WRITE-BLOCKER ──                                         │
│ Modèle   : Tableau T8u                                       │
│ SN       : T8U-12345                                        │
│ Firmware : v3.2.5                                           │
│ Testé    : Oui (fichier.txt écrit → refusé ✓)               │
│                                                             │
│ ── ACQUISITION ──                                           │
│ Outil    : ewfacquire v20230705                              │
│ Image    : INC-001-C-DRIVE.E01                              │
│ Format   : EWF (Expert Witness)                              │
│ Segments : 1 (E01)                                          │
│ Compression : fast (deflate)                                 │
│ Hash     : SHA256                                            │
│                                                             │
│ ── HASH (SOURCE) ──                                         │
│ SHA256   : A1B2C3D4E5F6...                                  │
│                                                             │
│ ── HASH (IMAGE) ──                                          │
│ SHA256   : A1B2C3D4E5F6... (MATCH ✓)                        │
│                                                             │
│ ── CHRONOLOGIE ──                                           │
│ 14:00 : Réception du disque (Agent X)                        │
│ 14:05 : Test write-blocker                                   │
│ 14:10 : Début acquisition                                    │
│ 15:25 : Fin acquisition                                      │
│ 15:30 : Hash vérifié (match)                                 │
│ 15:35 : Copie rangée dans le coffre                          │
│                                                             │
│ EXAMINATEUR : EVA-MASTER                                     │
│ SIGNATURE : [signé numériquement]                            │
└────────────────────────────────────────────────────────────┘
```

### Registre de Chaîne de Custody

```txt
┌──────────┬───────────────┬────────────┬──────────────┐
│ DATE     │ DE            │ À          │ HASH (SHA256)│
├──────────┼───────────────┼────────────┼──────────────┤
│ 22/07/14 │ Scène         │ Agent X    │ A1B2...      │
│ 22/07/14 │ Agent X       │ Labo EVA   │ A1B2...      │
│ 22/07/15 │ Coffre EVA    │ Analyste Y │ A1B2...      │
│ 22/08/01 │ Analyste Y    │ Coffre EVA │ A1B2...      │
└──────────┴───────────────┴────────────┴──────────────┘

À chaque transfert :
✓ Hash vérifié (identique)
✓ Signature des 2 parties
✓ Date/heure notée
✓ Raison du transfert
```

---

## 9. Vérification et Validation

### Tests d'Intégrité

```bash
# Test 1 : Hash source = hash image
# Après lecture du disque source (avant copie) :
sudo sha256sum /dev/sda > source.sha256

# Après création de l'image :
sha256sum image.dd > image.sha256
diff source.sha256 image.sha256

# Test 2 : EWF verify
ewfverify image.e01
# Vérifie : CRC segment + MD5 global + SHA1 global

# Test 3 : AFF verify
affverify image.aff

# Test 4 : Montage et vérification
ewfmount image.e01 /mnt/ewf/
sudo dd if=/mnt/ewf/ewf1 bs=4M count=100 | sha256sum
```

### Erreurs d'Acquisition

```txt
ERREURS CRITIQUES (image invalide) :
- Hash mismatch → corruption
- Taille différente → secteurs manquants
- CRC segment E01 invalide → fragment corrompu

ERREURS GÉRABLES (image partielle) :
- Bad sectors (ddrescue log)
- S.M.A.R.T. errors (read errors)
- Bitlocker verrouillé (image chiffrée)
- HPA/DCO (Host Protected Area / Device Configuration Overlay)

QUE FAIRE EN CAS D'ERREUR ?
1. Noter l'erreur dans le rapport
2. Ne PAS supprimer la preuve
3. Essayer ddrescue pour les bad sectors
4. Documenter tout
```

---

## 10. Script d'Acquisition Automatisé

```bash
#!/bin/bash
# disk_acquire.sh — Acquisition disque complète

set -e

SOURCE_DEVICE="$1"
OUTPUT_DIR="$2"
CASE_ID="$3"
EXAMINER="${4:-EVA-MASTER}"

if [ -z "$SOURCE_DEVICE" ] || [ -z "$OUTPUT_DIR" ] || [ -z "$CASE_ID" ]; then
    echo "Usage: $0 <device> <output_dir> <case_id> [examiner]"
    echo "Ex: $0 /dev/sda /mnt/evidence INC-001"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
DATE=$(date +%Y%m%d_%H%M%S)
DEVICE_NAME=$(basename "$SOURCE_DEVICE")

echo "=== DISK ACQUISITION ==="
echo "Device    : $SOURCE_DEVICE"
echo "Output    : $OUTPUT_DIR"
echo "Case      : $CASE_ID"
echo "Examiner  : $EXAMINER"
echo "Date      : $(date)"
echo ""

# 1. Device info
echo "[1] Device info..."
udevadm info --query=all --name="$SOURCE_DEVICE" > "$OUTPUT_DIR/${DEVICE_NAME}_info.txt"
lsblk "$SOURCE_DEVICE" > "$OUTPUT_DIR/${DEVICE_NAME}_lsblk.txt"
sudo smartctl -a "$SOURCE_DEVICE" > "$OUTPUT_DIR/${DEVICE_NAME}_smart.txt" 2>/dev/null

# 2. Partitions
echo "[2] Partition table..."
sudo fdisk -l "$SOURCE_DEVICE" > "$OUTPUT_DIR/${DEVICE_NAME}_fdisk.txt"
sudo mmls "$SOURCE_DEVICE" > "$OUTPUT_DIR/${DEVICE_NAME}_mmls.txt" 2>/dev/null

# 3. Hash source (pré-acquisition)
echo "[3] Source hash..."
sudo dd if="$SOURCE_DEVICE" bs=4M count=0 2>/dev/null
sudo sha256sum "$SOURCE_DEVICE" | tee "$OUTPUT_DIR/${DEVICE_NAME}_source.sha256"

# 4. Acquisition
echo "[4] Acquiring disk (E01)..."
sudo ewfacquire "$SOURCE_DEVICE" \
    -t "${OUTPUT_DIR}/${CASE_ID}_${DEVICE_NAME}" \
    -C "$CASE_ID" \
    -N "Physical disk ${DEVICE_NAME}" \
    -e "$EXAMINER" \
    -d sha256 \
    -S 2000MB \
    -c fast -q

# 5. Vérification
echo "[5] Verifying..."
sudo ewfverify "${OUTPUT_DIR}/${CASE_ID}_${DEVICE_NAME}.e01"
echo ""

# 6. Hash post-acquisition
echo "[6] Post-acquisition hash..."
sha256sum "${OUTPUT_DIR}/${CASE_ID}_${DEVICE_NAME}.e01" > "${OUTPUT_DIR}/${CASE_ID}_${DEVICE_NAME}.sha256"

echo ""
echo "=== ACQUISITION COMPLETE ==="
echo "Source hash : $(cat "${OUTPUT_DIR}/${DEVICE_NAME}_source.sha256")"
echo "Image hash  : $(cat "${OUTPUT_DIR}/${CASE_ID}_${DEVICE_NAME}.sha256")"
echo "Files:"
ls -lh "${OUTPUT_DIR}/${CASE_ID}_${DEVICE_NAME}"*
```

---

## 11. Dépannage et Erreurs Fréquentes

```txt
PROBLÈME : "Permission denied" sur /dev/sda
SOLUTION : Utiliser sudo ou ajouter l'utilisateur au groupe disk
    sudo usermod -a -G disk user

PROBLÈME : "dd: error reading: Input/output error" (bad sector)
SOLUTION : Utiliser conv=noerror (ignore l'erreur) + ddrescue

PROBLÈME : Write-blocker non détecté
SOLUTION : Vérifier le câble, l'alimentation, les drivers
    dmesg | tail -20 → logs noyau

PROBLÈME : BitLocker / FileVault verrouillé
SOLUTION : Demander la clé de récupération
    → Acquisition de l'image chiffrée
    → Déchiffrement logiciel (Elcomsoft, Passware)

PROBLÈME : SSD NVMe non reconnu par write-blocker
SOLUTION : Certains T8u nécessitent un adaptateur NVMe → USB 3.0

PROBLÈME : Espace insuffisant sur la destination
SOLUTION : 
    - Compression E01/AFF (30-50% de réduction)
    - Segmentation sur plusieurs disques
    - Montage réseau (NFS, iSCSI)
```

---

## 12. Bonnes Pratiques Checklist

```txt
PRÉ-ACQUISITION :
□ Vérifier le write-blocker (test écriture)
□ Noter l'état du disque (S.M.A.R.T.)
□ Vérifier HPA/DCO
□ Documenter le matériel
□ Prendre des photos du disque + setup
□ Calculer le hash source

ACQUISITION :
□ Utiliser E01 ou AFF (compressé + métadonnées)
□ Segmenter pour transfert (650 MB ou 2 GB)
□ Vérifier l'absence d'erreur après acquisition
□ Calculer le hash final

POST-ACQUISITION :
□ Vérifier hash source = hash image
□ Générer le rapport d'acquisition
□ Signer numériquement le rapport
□ Remplir la chaîne de custody
□ Ranger l'original dans un endroit sécurisé
□ Créer une copie de travail
```

---

## 13. Ressources

- **libewf (EWF Tools)** : https://github.com/libyal/libewf
- **libaff (AFF Library)** : https://github.com/afflib/afflib
- **ddrescue** : https://www.gnu.org/software/ddrescue/
- **dcfldd** : https://sourceforge.net/projects/dcfldd/
- **Sleuth Kit** : https://sleuthkit.org/
- **Tableau Write Blockers** : https://www.tableau.com/
- **NIST CFTT** (Disk Imaging Tool Testing) : https://www.cftt.nist.gov/disk_imaging.htm