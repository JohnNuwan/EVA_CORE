---
name: ftk-imager-forensics
description: Guide complet de FTK Imager — acquisition forensique, création d'images E01/DD, montage virtuel, analyse de preuves, mémoire RAM, cache, et export de données judiciaires
tags: [forensics, ftk-imager, acquisition, imaging, e01, ewf, ram-dump]
version: 1.0
---

# FTK Imager — Acquisition et Analyse Forensique

Guide exhaustif de FTK Imager (AccessData / Exterro) pour l'acquisition et l'analyse forensique de supports numériques.

---

## 1. Présentation et Installation

### Qu'est-ce que FTK Imager ?

FTK Imager est un outil d'imagerie forensique développé par AccessData (aujourd'hui Exterro). Il permet de :
- Créer des images forensiques (E01, DD, AFF, SMART) avec hash
- Monter des images en lecture seule (mount)
- Capturer la mémoire RAM (Windows)
- Prévisualiser le contenu des disques, fichiers et registres
- Exporter des fichiers de preuve
- Générer des rapports d'acquisition

### Installation

```bash
# Windows — Téléchargement depuis exterro.com
# License : Gratuit pour usage forensique
# Installation standard : FTK Imager.exe

# Linux — Alternatives équivalentes
# Pas de version native Linux, utiliser via Wine :
wine FTK_Imager_4.7.3.exe
# Ou utiliser guymager (GUI) + ewfacquire (CLI)
```

---

## 2. Acquisition Disque — Workflow Complet

### Création d'une Image Disque (Disk Image)

```txt
File → Create Disk Image

Step 1: Select Source
┌─────────────────────────────────────┐
│ ○ Physical Drive                    │ ← Disque physique entier
│ ○ Logical Drive                     │ ← Partition logique (C:, D:)
│ ○ Image File                        │ ← Convertir un format vers un autre
│ ○ Contents of a Folder              │ ← Acquisition logique de dossier
│ ○ Femto Controller Device           │ ← Périphérique spécialisé
└─────────────────────────────────────┘

Step 2: Select Drive
  Choisir le disque source dans la liste
  Vérifier : Manufacturer, Model, Size, Serial Number

Step 3: Destination Image
┌─────────────────────────────────────┐
│ Image Type :                        │
│ ● SMART (Segmented)                 │
│ ○ E01 (Compressed)                  │ ← Recommandé
│ ○ AFF (Advanced Forensic)           │
│ ○ RAW (dd)                          │
│ ──────────────────────────────────  │
│ Evidence Item Identifier : INC-001  │
│ Description : PC Suspect Principal  │
│ Examiner : EVA-MASTER               │
│ Notes : Acquisition live, Win11     │
└─────────────────────────────────────┘

Step 4: Image Destination
  Folder : /mnt/nas/evidence/
  Image Filename : INC-001-C-DRIVE

Step 5: Verification
  □ Verify images after they are created  ← RECOMMANDÉ
  □ Create directory hash lists
  □ Pre-calculate progress statistics

Step 6: Fragment Size
  ○ No fragmentation
  ● 650 MB (CD)               ← Pour transfert physique
  ○ Custom : 2000 MB          ← Pour stockage sur disque

→ START (Création de l'image : hash lecture → copie → hash écriture)
```

### Paramètres Critiques

```txt
┌──────────────────────────────────────────────────────────────┐
│ Image Type : E01 (Expert Witness Format)                     │
│                                                              │
│ Avantages :                                                  │
│ ✓ Compression intégrée (taille réduite 30-50%)               │
│ ✓ Métadonnées encapsulées (cas, examinateur, notes)          │
│ ✓ Hash MD5 + SHA1 intégré à l'image                          │
│ ✓ Segmentation automatique (fragments)                       │
│ ✓ Standard judiciaire accepté partout                        │
│                                                              │
│ Inconvénients :                                              │
│ - Lecture sans FTK/EWF tools nécessite décompression         │
│ - Plus lent que DD (compress + hash en continu)              │
│ - Limitation 2 TiB par segment (E01)                         │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Capture de Mémoire RAM

### Acquisition RAM (Windows)

```txt
File → Capture Memory

┌─────────────────────────────────────┐
│ Destination Path :                  │
│   D:\ram_captures\                      │
│ Destination Filename :              │
│   INC-001-RAM                    │
│                                     │
│ □ Include pagefile                  │ ← Capture aussi pagefile.sys
│ □ Create AddrNoMem callback         │ ← Entrées mémoire non mappée
│                                     │
│ Type de capture :                   │
│ ● Raw Memory                        │ ← .mem / .bin
│ ○ Microsoft Crash Dump              │ ← .dmp (WinDbg compatible)
│                                     │
│ Compression :                       │
│ ○ None (plus rapide)                │
│ ● Fast (recommandé)                 │
│ ○ Best (lent)                       │
└─────────────────────────────────────┘
```

### Analyse de la capture mémoire

```bash
# Après acquisition, ouvrir le fichier .mem dans FTK Imager
# File → Add Evidence Item → Image File → INC-001-RAM.mem

# Puis analyser avec Volatility :
vol -f INC-001-RAM.mem windows.info
vol -f INC-001-RAM.mem windows.pslist
vol -f INC-001-RAM.mem windows.netscan
```

### Limitations

```txt
- Maximum 64 Go RAM en 32-bit
- 64-bit : limite = mémoire physique disponible
- Windows 10/11 : nécessite privilèges admin + SeDebugPrivilege
- Windows Secure Boot + Virtualization-Based Security (VBS) :
  Certaines pages mémoire peuvent être protégées
- DMA attack / FireWire : contourne le verrouillage écran
```

---

## 4. Acquisition Logique (Logical / Folder)

### Contenu d'un dossier

```txt
File → Add Evidence Item → Contents of a Folder

Usage : Capturer un dossier entier sans imager le disque
Utile pour :
- Cloud storage (OneDrive, Google Drive)
- Dossier utilisateur spécifique
- Éléments réseau (NAS, partage)
- Acquisition rapide pour triage

Format de sortie :
- Custom Content Image (.ad1) : format propriétaire AccessData
- Avec métadonnées, timestamps, permissions
```

### Acquisition Logique via AD1

```bash
# Format .ad1 = AccessData Logical Image
# Monte comme un conteneur dans FTK Imager
# Avantages :
# - Taille réduite (seulement les fichiers sélectionnés)
# - Métadonnées conservées
# - Ouverture dans FTK, Autopsy (via plugin)
# - Mot de passe optionnel
```

---

## 5. Montage d'Image (Mount)

### Monter une image en lecture seule

```txt
File → Image Mounting...

┌─────────────────────────────────────┐
│ Image File : INC-001-C-DRIVE.E01    │
│                                     │
│ ● Mount remotely (webdav)           │
│ ● Mount locally                     │
│                                     │
│ ○ Read-Only (recommandé) ←          │
│ ○ Write-Block (FW/FT)               │
│ ○ Read/Write (⚠ altération)         │
│                                     │
│ Drive Letter : M:                    │
│ ──────────────────────────────────  │
│ Mounted successfully                 │
└─────────────────────────────────────┘

# L'image est accessible comme un disque normal
# Toutes les modifications sont bloquées (read-only)
# Parfait pour :
# - Analyse avec des outils non-forensiques
# - Antivirus scan
# - Recherche Windows (Everything)
```

### Montage avancé

```txt
Options de montage :
- Physical Drive : image montée comme /dev/sdX (Linux via FTK)
- Drive Letter : attribution lettre Windows
- Network Share : accès réseau SMB
- WebDAV : accès HTTP (analyse distante)

Limitations :
- E01 fragmenté : nécessite tous les segments (.e01, .e02, ...)
- Pas d'écriture (read-only), mais intégrité garantie
```

---

## 6. Interface de Prévisualisation

### Vue d'ensemble

```txt
┌─────────────────────────────────────────────────────────────┐
│ FTK Imager — INC-001-C-DRIVE.E01                           │
│ ┌───────────────────────────────────┐  ┌───────────────────┐│
│ │ [INC-001-C-DRIVE]                │  │ Name      | Size  ││
│ │  ├─ $MFT                         │  │ document | 120KB  ││
│ │  ├─ $LogFile                     │  │ photo.jpg | 2MB   ││
│ │  ├─ $Volume                      │  │ zip.rar   | 5MB   ││
│ │  ├─ Boot                         │  │           |       ││
│ │  ├─ Program Files                │  │           |       ││
│ │  ├─ Users                        │  │           |       ││
│ │  │  └─ suspect                   │  │           |       ││
│ │  │     ├─ Desktop                │  │           |       ││
│ │  │     ├─ Documents              │  │           |       ││
│ │  │     └─ Downloads              │  │           |       ││
│ │  └─ Windows                      │  └───────────────────┘│
│ └───────────────────────────────────┘                      │
│ Hex View  |  Text View  |  File Properties                │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00   │   │
│ │ ...                                                 │   │
│ └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Panneaux d'affichage

```txt
Hex View      : Affichage hexadécimal + ASCII du fichier sélectionné
Text View     : Contenu texte extrait (strings-like)
File Properties : Métadonnées complètes (timestamps, permissions, hash)
Picture View  : Aperçu des images (JPEG, PNG, BMP, GIF)
File Summary  : Résumé des propriétés + hash + signatures
```

### File Properties détaillées

```txt
Nom du fichier : malware.exe
Chemin         : C:\Users\suspect\Downloads\
Taille         : 245,760 bytes (240 KB)
Type MIME      : application/x-msdownload
Extension      : .exe

Timestamps Windows (MACE) :
  Modified   : 2024-07-20 14:23:05 UTC
  Accessed   : 2024-07-21 09:15:30 UTC
  Created    : 2024-07-20 14:23:01 UTC
  Entry Modified : 2024-07-20 14:23:05 UTC (MFT)

$FILE_NAME (NTFS) :
  Modified   : 2024-07-20 14:23:05 UTC
  Accessed   : 2024-07-21 09:15:30 UTC
  Created    : 2024-07-20 14:23:01 UTC

MD5    : A1B2C3D4E5F6...
SHA1   : 1234567890AB...
SHA256 : ABCDEF0123456789...

Attributes :
  Archive, Not Content Indexed
  ADS : Zone.Identifier ($DATA)  ← Marqueur de téléchargement web
```

---

## 7. Export de Preuves

### Export de fichiers individuels

```txt
Right-click → Export Files

Options :
- Export File(s)               → Fichier original
- Export File Hash List        → Liste des hash uniquement
- Export File Info             → Métadonnées en CSV
- Export in Original Format    → Mêmes dates/permissions
- Export as Plain Text         → Contenu texte uniquement
- Export Tab-separated Values  → Pour analyse dans Excel
```

### Export de liste de fichiers

```bash
# File → Export File List
# Génère un CSV complet avec toutes les métadonnées

# Colonnes exportées :
# | Name | Path | Size | Created | Modified | Accessed | MD5 | SHA1 | SHA256 | Extension | Attributes |

# Utile pour :
# - Analyse dans Excel / Timeline Explorer
# - Rapport d'investigation
# - Preuve documentaire
```

### Export de rapport

```txt
File → Report...

Contenu du rapport :
- Informations du cas (Case Info)
- Résumé de l'image (Image Summary)  
- Liste des fichiers (File List)
- Fichiers marqués (Bookmarked Items)
- Hash checks (Image Verification)
- Custom Notes

Format : HTML (avec CSS embarqué)
```

---

## 8. Vérification et Intégrité

### Vérification d'image

```txt
Tools → Verify Image

┌─────────────────────────────────────┐
│ Image File : INC-001-C-DRIVE.E01    │
│                                     │
│ Verification Method :               │
│ ● Full (re-read entire image)       │
│ ○ Fast (verify segments CRC only)   │
│                                     │
│ Status : VERIFIED                    │
│ MD5 Original  : A1B2... (match ✓)   │
│ MD5 Verified  : A1B2... (match ✓)   │
│ SHA1 Original : C3D4... (match ✓)   │
│ SHA1 Verified : C3D4... (match ✓)   │
└─────────────────────────────────────┘

# Si mismatch : l'image est corrompue → recommencer l'acquisition
```

### Comparaison de hash

```bash
# Comparaison manuelle (CLI)
ewfinfo INC-001-C-DRIVE.E01 | grep -E "MD5|SHA1"

# Vérification avec ewftools
ewfverify INC-001-C-DRIVE.E01

# Vérification avec dd + hash
dd if=/dev/sda bs=4M status=progress | tee >(sha256sum > image.sha256) > image.dd
sha256sum -c image.sha256
```

---

## 9. Acquisition Spécifiques

### Acquisition CD/DVD/Blu-ray

```txt
File → Create Disk Image → Optical Device
- Support : CD, DVD, BD, HD-DVD
- Format : ISO, NRG, MDS/MDF
- Hash automatique
- Attention aux erreurs de lecture (scratch)
```

### Acquisition de carte SD / USB

```txt
File → Create Disk Image → Removable Drive
- Carte SD, microSD, CompactFlash
- Clé USB, SSD externe
- Format : E01 (recommandé) ou DD
- Write-blocker OBLIGATOIRE
- Vérifier le serial number du fabricant
```

### Acquisition à chaud (Live System)

```txt
PRÉCAUTIONS :
1. Utiliser un write-blocker hardware (Tableau, WiebeTech)
2. Booter sur un Live CD forensique (SIFT, CAINE)
3. Capturer la RAM en premier (volatile !)
4. Capturer le disque en second
5. Hasher TOUT immédiatement
```

---

## 10. Chaîne de Custody avec FTK Imager

### Journal d'acquisition

```txt
┌─────────────────────────────────────┐
│ ACQUISITION LOG                      │
│ ─────────────────────────────────── │
│ Case Number   : INC-2024-001        │
│ Evidence ID   : INC-001-C-DRIVE     │
│ Device        : Samsung SSD 870     │
│ Serial        : S3Z7NB0M12345       │
│ Capacity      : 500 GB (465 GiB)    │
│ Interface     : SATA III (USB-SATA) │
│                                      │
│ Write Blocker : Tableau T8u         │
│ Hash Blocker  : Verified ✓          │
│                                      │
│ Acquisition Date : 2024-07-22       │
│ Start Time      : 14:30:00 UTC      │
│ End Time        : 15:45:00 UTC      │
│ Duration        : 1h 15m            │
│                                      │
│ Image Type     : E01 (fragmented)   │
│ Fragments      : 2 (E01, E02)       │
│ Compression    : Fast (deflate)      │
│                                      │
│ Acquisition MD5 : A1B2C3D4E5...      │
│ Verification   : PASS               │
│                                      │
│ Examiners      : EVA-MASTER         │
│ Organization   : The Hive            │
│ Signature      : [hash signé]        │
└─────────────────────────────────────┘
```

### Document de Chaîne de Custody

```txt
┌─────────────────────────────────────────┐
│ CHAIN OF CUSTODY FORM                    │
├─────────────────────────────────────────┤
│ Item # : INC-001-C-DRIVE                 │
│ Desc   : Samsung SSD 870 500GB           │
│ Serial : S3Z7NB0M12345                   │
├──────────────┬────────────┬──────────────┤
│ FROM         │ TO         │ DATE/TIME    │
├──────────────┼────────────┼──────────────┤
│ Lieu du crime│ Agent A    │ 22/07 14:00  │
│ Agent A      │ Labo EVA   │ 22/07 14:30  │
│ Labo EVA     │ Analyste X │ 22/07 16:00  │
└──────────────┴────────────┴──────────────┘
Signatures + Hash à chaque transfert
```

---

## 11. Commandes CLI Équivalentes

### Linux CLI

```bash
# DD (raw)
sudo dd if=/dev/sda of=/evidence/image.dd bs=4M status=progress conv=noerror,sync
sudo sha256sum /evidence/image.dd

# EWF (E01) avec ewfacquire
sudo ewfacquire /dev/sda -t /evidence/image.e01 \
  -C "INC-2024-001" \
  -N "C Drive du suspect" \
  -e "EVA-MASTER" \
  -d sha256 \
  -S 650MB \
  -c fast

# Vérification
ewfverify /evidence/image.e01

# Guymaker (GUI Linux)
guymager
# Interface graphique E01/DD/AFF, hash MD5+SHA256
```

### Windows CLI

```batch
:: FTK Imager CLI (FTK Imager Lite)
:: Pas de CLI officielle, mais scripting via AutoIT/Sikuli

:: Équivalent PowerShell (dd-like)
:: Nécessite Write-Blocker
:: Utiliser Win32DiskImager CLI
Win32DiskImager.exe /image evidence.img /device \\.\PhysicalDrive1 /hash SHA256

:: EWFacquire pour Windows
:: Cygwin + libewf
```

---

## 12. Dépannage

### Erreurs fréquentes

```txt
1. "Unable to read sector X"
   → Disque physique avec bad sectors
   → Solution : dd_rescue + mode ignore errors

2. "Image file size exceeds limit"
   → Limite FAT32 (4 GB) sur la destination
   → Solution : fragmenter en 650MB ou utiliser NTFS/exFAT

3. "Hash mismatch during verification"
   → Corruption pendant le transfert
   → Solution : refaire l'acquisition, changer de câble

4. "Drive not detected / no permissions"
   → Privilèges administrateur requis
   → Drivers write-blocker manquants
   → BitLocker / FileVault verrouillé

5. "E01 segment missing (.e02 not found)"
   → Tous les fragments doivent être dans le même dossier
   → Solution : copier tous les .e0*
```

### BitLocker / Chiffrement

```txt
FTK Imager ne peut PAS acquérir un disque BitLocker verrouillé :
1. Demander la clé de récupération (48 chiffres)
2. Déverrouiller via BitLocker Recovery dans Windows
3. Puis acquérir le disque déverrouillé (logical drive)

Ou :
1. Acquérir l'image avec BitLocker verrouillé
2. Utiliser Elcomsoft Forensic Disk Decryptor
3. Ou Passware Kit Forensic pour attaque

Alternatives :
- FOX (Forensic Operating System eXtractor) 
- Arsenal Image Mounter (monte E01 + BitLocker)
```

---

## 13. Ressources

- **FTK Imager Download** : https://www.exterro.com/ftk-imager
- **Documentation AccessData** : https://support.exterro.com/
- **libewf (EWF Tools)** : https://github.com/libyal/libewf
- **guymager** : https://guymager.sourceforge.io/
- **ddrescue** : https://www.gnu.org/software/ddrescue/
- **Forensic Disk Decryptor** : https://www.elcomsoft.com/efdd.html