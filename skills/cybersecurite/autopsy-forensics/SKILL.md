---
name: autopsy-forensics
description: Guide complet d'Autopsy et The Sleuth Kit (TSK) — analyse de disque, système de fichiers, ingestion de sources, modules, keyword search, timeline view, et automatisation CLI
tags: [forensics, autopsy, sleuthkit, tsk, disk-analysis, timeline]
version: 1.0
---

# Autopsy & The Sleuth Kit — Analyse Forensique Complète

Guide exhaustif de la plateforme Autopsy (GUI) et de son moteur CLI The Sleuth Kit (TSK) pour l'analyse forensique de supports de stockage.

---

## 1. The Sleuth Kit (TSK) — Outils CLI Fondamentaux

### Analyse de l'image disque

```bash
# Informations sur la partition
mmls disk.dd                           # Table de partitions (DOS/GPT)
mmstat disk.dd                         # Statistiques de l'image
mmcat disk.dd 2 > part2.raw            # Extraire une partition spécifique

# Analyse du système de fichiers
fsstat -o 2048 disk.dd                 # Statistiques du FS (taille, dates, UUID)
fsstat -t ntfs -o 2048 disk.dd        # Force NTFS
fsstat -t ext4 disk.dd                # Force ext4

# Lister les fichiers d'un répertoire
fls -o 2048 disk.dd                   # Fichiers de la racine
fls -o 2048 -r disk.dd                # Récursif
fls -o 2048 -d disk.dd                # Fichiers supprimés uniquement
fls -o 2048 -p disk.dd                # Chemins complets
fls -o 2048 -f ntfs disk.dd -r /Users/Admin/Documents
```

### Extraction de contenu

```bash
# Afficher le contenu d'un fichier
icat -o 2048 disk.dd 65-128-3 > extracted.pdf   # Par inode

# Afficher les blocs de données
blkcat disk.dd 4096 16 > block.dump              # Bloc 4096, 16 secteurs
blkstat disk.dd 4096                             # Statut d'un bloc

# MFT parser
istat -o 2048 disk.dd 65-128-3                   # Infos inode/MFT entry
istat -o 2048 disk.dd "$MFT"                     # Analyse MFT

# Timeline
fls -o 2048 -m / -r disk.dd > bodyfile.txt       # Créer un body file
mactime -b bodyfile.txt > timeline.csv            # Générer la timeline
```

### Recherche

```bash
# Recherche de strings dans l'image
sigfind -i 55 -o 0 2048 disk.dd                 # Trouver une signature

# Recherche par hash
hfind -i md5 /usr/share/sleuthkit/hash_db/nsrl-md5.txt "A1B2C3..."
```

---

## 2. Autopsy — Architecture et Workflow

### Installation

```bash
# Linux (deb)
sudo apt install autopsy sleuthkit
# Ou download du .zip depuis https://www.autopsy.com/download/

# Dépendances : Java 11+ (OpenJDK)
java -jar autopsy-4.21.0.jar --instdir /opt/autopsy

# Lancer
/opt/autopsy/bin/autopsy
```

### Création d'un cas (Case)

```txt
1. File → New Case
   - Case Name : incident_2024_001
   - Base Directory : /evidence/cases/
   - Case Type : Single-user / Multi-user

2. Add Data Source
   - Disk Image or VM File : disk.dd, disk.e01, disk.aff
   - Local Disk : /dev/sda (attention : écriture interdite)
   - Logical Files : dossier de fichiers
   - Unallocated Space Image Image : espace non alloué
   - Autopsy Logical Imager Results : .zip/.001 généré par l'imager

3. Configure Ingest Modules
   - Recent Activity : Web, USB, Documents
   - File Type Detection : classification par type MIME
   - Hash Lookup : NSRL (National Software Reference Library)
   - Keyword Search : recherche par mots-clés
   - Email Parser : PST, MBOX
   - Extension Mismatch Detector : falsification d'extension
   - PhotoRec Carver : récupération de fichiers
```

### Structure du cas Autopsy

```
/evidence/cases/incident_2024_001/
├── Autopsy/
│   ├── Config/                      # Configuration du cas
│   ├── Export/                      # Fichiers exportés
│   ├── Ingests/                     # Résultats d'ingestion
│   └── Reports/                     # Rapports générés
├── Data/
│   └── <hash>/                      # Base de données H2 SQL
└── Log/
    └── autopsy.log                  # Logs détaillés
```

---

## 3. Modules d'Ingestion — Approfondissement

### Recent Activity

Analyse l'activité récente utilisateur :
- **Web Bookmarks** : Chrome, Firefox, Edge, Safari, IE
- **Web Cookies** : identifiants de session
- **Web Downloads** : historique des téléchargements
- **Web History** : historique de navigation complet
- **Recent Documents** : MRU Windows + Jump Lists
- **USB Device Attached** : clés USB, disques externes (port USB, VID/PID, serial)
- **Installed Programs** : Uninstall registry key

### File Type Detection

```txt
Catégories détectées :
- Documents (PDF, DOCX, XLSX, PPTX)
- Images (JPEG, PNG, GIF, BMP, TIFF, RAW)
- Vidéos (MP4, AVI, MKV, MOV, WMV)
- Audio (MP3, WAV, FLAC, AAC, WMA)
- Archives (ZIP, RAR, 7Z, TAR, GZ)
- Exécutables (EXE, DLL, SYS, ELF, Mach-O)
- Emails (PST, OST, MBOX, EML, MSG)
- Databases (SQLite, MDB, FDB)
```

### Hash Lookup (NSRL)

```bash
# Télécharger NSRL (National Software Reference Library)
wget https://www.nsrl.nist.gov/rds/RDS_2024.06.zip
unzip RDS_2024.06.zip -d /usr/share/sleuthkit/hash_db/

# Base de hash connus = ignore
# Hash inconnus = suspects (focus investigation)
# Hash malveillants = flag (intégrer ses propres hash sets)

# Hash sets personnalisés
md5sum /path/to/known_malware/* >> /usr/share/sleuthkit/hash_db/malware.txt
```

### Keyword Search

```txt
Expressions régulières intégrées (Indexed Search) :
- IP addresses : \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}
- Email addresses : \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b
- Phone numbers : \b\d{3}[-.]?\d{3}[-.]?\d{4}\b
- Credit cards : \b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b
- URLs : https?://[^\s/$.?#].[^\s]*
- IPv6 : ([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}

Keywords personnalisés :
- Noms, pseudos, codes
- Identifiants de malware
- Mots de passe suspects
- Termes du domaine de l'incident
```

### Extension Mismatch Detector

```bash
# Détection de fichiers dont l'extension ne correspond pas au type MIME
# Exemple : malware.exe renommé en document.pdf
# Utilise la signature magique du fichier (magic bytes)

# Vérification manuelle
file document.pdf           # Regarde les magic bytes, pas l'extension
# Résultat : "PE32 executable" → mismatch flagué
```

### Email Parser

```bash
# Analyse des boîtes aux lettres
# Formats supportés : PST (Outlook), MBOX (Thunderbird), EML
# Extraction : 
#   - En-têtes (From, To, CC, Subject, Date)
#   - Pièces jointes (avec hash)
#   - Calendriers, contacts
```

### PhotoRec Carver

```bash
# Module intégré = PhotoRec (testdisk)
# Lance le carving après analyse du FS
# Récupère : JPEG, DOC, PDF, ZIP, etc. depuis l'espace non alloué
# Avantage : ne dépend pas du FS (signatures)
```

---

## 4. Navigation dans l'Interface Autopsy

### Tree View (Arborescence)

```txt
📂 Views
├── 📁 Data Sources
│   └── 📁 disk.dd
│       ├── 📁 volume_1 (NTFS - C:)
│       │   ├── 📁 $OrphanFiles
│       │   ├── 📁 Boot
│       │   ├── 📁 PerfLogs
│       │   ├── 📁 Program Files
│       │   ├── 📁 Users
│       │   └── 📁 Windows
│       ├── 📁 unalloc
│       └── 📁 volume_2 (FAT32 - System Reserved)
├── 📁 File Views
│   ├── All Files (tree)
│   ├── All Files (flat) - triable par colonne
│   ├── By Extension
│   ├── Deleted Files
│   └── By MIME Type
├── 📁 Results
│   ├── Keyword Hits
│   ├── Hash Set Hits
│   ├── Email Messages
│   ├── Interesting Items
│   ├── Accounts
│   ├── Occurrences
│   └── Tagged Results
└── 📁 Reports
    └── 📁 Generated Reports
```

### Colonnes du volet des fichiers (File Table)

| Colonne | Description |
|---------|-------------|
| Name | Nom du fichier |
| S | Supprimé (d) / Alloué (a) |
| Type | MIME type |
| Size | Taille |
| Modified | Date modification |
| Accessed | Date accès |
| Changed | Date changement MFT |
| Created | Date création |
| Met | META entry flags |
| Dir | Répertoire parent |
| Known | Known/Unknown/Notable (NSRL) |

### Timeline View

```txt
Visualisation chronologique des événements :
- Filtre par date (range selector + calendar)
- Catégories :
  - File System : fichier créé/modifié/supprimé
  - Web : historique, téléchargements
  - Email : envoi/réception
  - Registry : modifications
  - Application : traces logicielles
- Granularité : jour/heure/minute
- Export en CSV pour TimelineExplorer (EZ Tools)
```

---

## 5. Analyses Spécifiques

### Web Artifacts Analysis

```bash
# Chrome/Chromium
# Fichiers analysés automatiquement par Autopsy :
# - History (SQLite) : urls, visits, downloads
# - Bookmarks : répertoire et URL
# - Cookies : nom, valeur, domaine, expiration
# - Login Data : mots de passe (encryptés)
# - Web Data : autofill, search terms

# Firefox
# - places.sqlite (history + bookmarks)
# - favicons.sqlite
# - cookies.sqlite
# - signons.sqlite (passwords)

# Edge (Chromium-based)
# Même structure que Chrome dans le répertoire Edge/User Data/
```

### USB Device Analysis

```bash
# Artefacts USB extraits par Autopsy :
# - SYSTEM\CurrentControlSet\Enum\USB : VID/PID, serial
# - SYSTEM\CurrentControlSet\Enum\USBSTOR : clés USB
# - SOFTWARE\Microsoft\Windows Portable Devices\Devices
# - SetupAPI.dev.log : première connexion

# Informations récupérées :
# - Manufacturer, Product
# - Serial number (unique)
# - First/Last connection
# - Drive letter assigned
# - Volume name
```

### Email Analysis

```bash
# Outlook PST/OST parsing :
# - Email headers (Message-ID, In-Reply-To, References)
# - Thread reconstruction
# - Attachments extraction (hash + metadata)
# - Calendar entries
# - Contacts
# - Distribution lists
```

---

## 6. Keyword Lists et Regex

### Créer une liste de mots-clés

```bash
# Fichier texte : un mot-clé ou une regex par ligne
# Encodage : UTF-8 sans BOM

# Exemple : keywords.txt
motdepasse
confidentiel
secret
hack
backdoor
RAT
C2
192\.168\.
C:\\Users\\[^\\]+\\AppData
```

### Regex Intégrées (File Search)

```bash
# Parcours : Tools → Keyword Search
# Mode : Regex (vs Substring)
# Search in : Files / Unallocated / Slack space
# Encodings : UTF-8, UTF-16LE, Latin-1

# Regex avancées
\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b   # Emails (case insensitive)
(?:\d[ -]*?){13,16}                            # Cartes de crédit
\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b              # IP v4
[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}  # UUID
```

---

## 7. Rapports et Export

### Génération de rapport

```bash
# Tools → Generate Report
# Formats disponibles :
# - HTML Report : navigation web, links
# - Excel Report : tableaux filtrables
# - KML File : géolocalisation (Google Earth)
# - STIX : format CTI (structuré)
# - Body File : pour mactime (timeline)
# - Text Report : plaintext structuré

# Inclure dans le rapport :
# - Case information
# - File listing (all / tagged / deleted)
# - Keyword hits
# - Hash set hits
# - Timeline
# - Bookmarks
```

### Export de fichiers

```bash
# Selectionner fichiers → Right click → Export Files
# Options :
# - Export Native Format (fichier original)
# - Export Text (text content only)
# - Export as Body File (timeline)

# Structure de l'export :
/evidence/export/
├── 2024-07-22_15-30-00/
│   ├── volume_1_C/
│   │   ├── Users/
│   │   │   └── suspect/
│   │   │       ├── Documents/
│   │   │       ├── Desktop/
│   │   │       └── Downloads/
│   │   └── Windows/
│   │       └── Temp/
│   └── unalloc/
│       ├── carved_001.jpg
│       └── ...
```

---

## 8. Automatisation CLI (Sleuth Kit Scripts)

### Script d'analyse batch

```bash
#!/bin/bash
# Script : tsk_batch_analyze.sh
# Usage : ./tsk_batch_analyze.sh image.dd

IMAGE=$1
BASENAME=$(basename "$IMAGE" .dd)
OUTDIR="/evidence/analysis/$BASENAME"

mkdir -p "$OUTDIR"

# 1. Table de partitions
mmls "$IMAGE" > "$OUTDIR/partitions.txt"

# 2. Pour chaque partition NTFS
SECTORS=$(mmls "$IMAGE" | grep -E "NTFS|Microsoft" | awk '{print $3}')
for SECTOR in $SECTORS; do
  fsstat -o "$SECTOR" "$IMAGE" > "$OUTDIR/fsstat_${SECTOR}.txt"
  fls -o "$SECTOR" -r -m "/" "$IMAGE" > "$OUTDIR/bodyfile_${SECTOR}.txt"
  mactime -b "$OUTDIR/bodyfile_${SECTOR}.txt" > "$OUTDIR/timeline_${SECTOR}.csv"
  fls -o "$SECTOR" -d "$IMAGE" > "$OUTDIR/deleted_${SECTOR}.txt"
done

# 3. Timeline globale
cat "$OUTDIR"/bodyfile_*.txt > "$OUTDIR/bodyfile_global.txt"
mactime -b "$OUTDIR/bodyfile_global.txt" > "$OUTDIR/timeline_global.csv"

# 4. Hash du fichier image
sha256sum "$IMAGE" > "$OUTDIR/image_sha256.txt"

echo "Analyse terminée : $OUTDIR"
```

### Script de recherche de fichiers supprimés

```bash
#!/bin/bash
# tsk_find_deleted.sh
IMAGE=$1
SECTOR=$2
OUTDIR=$3

mkdir -p "$OUTDIR"

# Lister les fichiers supprimés avec leurs inodes
fls -o "$SECTOR" -rd "$IMAGE" | while read -r line; do
  echo "$line"
  INODE=$(echo "$line" | awk '{print $2}' | tr -d '[]')
  NAME=$(echo "$line" | awk '{print $NF}')
  icat -o "$SECTOR" "$IMAGE" "$INODE" > "$OUTDIR/recovered_${NAME}_${INODE}" 2>/dev/null || echo "FAIL: $NAME (inode $INODE)"
done
```

---

## 9. Dépannage et Erreurs Fréquentes

### Problèmes d'ingestion

```txt
1. "Out of memory" (Java heap)
   Solution : augmenter la mémoire Java
   export JAVA_OPTS="-Xmx8g"
   # Ou modifier autopsy.cfg

2. "Unsupported file system"
   Vérifier : fsstat -o <offset> image.dd
   Si RAW/unknown : ajouter -f (force type)
   Types : ntfs, fat, ext2, ext3, ext4, ufs, hfs

3. "Data source already exists"
   Utiliser un hash différent ou supprimer l'ancien cas

4. Image corrompue / bad sectors
   Utiliser dd_rescue pour recréer l'image
   ou "Add unallocated space only"
```

### Optimisation Performance

```bash
# Base de données H2
# Par défaut : /evidence/cases/<case>/Data/<hash>/
# Option : utiliser PostgreSQL (multi-user uniquement)

# Indexing
# - Keyword Search : l'indexation est CPU-intensive
# - Désactiver les modules non utilisés
# - Priorité : Recent Activity > File Type > Hash > Keywords

# Mémoire
# Recommandé : 8-16 GB RAM pour cas > 500 GB
# Java heap : -Xmx8g minimum
```

---

## 10. Workflows d'Investigation

### Investigation Standard

```txt
Phase 1 — Préparation
  □ Créer le cas (Case)
  □ Ajouter la source de données (Image)
  □ Configurer les modules d'ingestion
  □ Lancer l'ingestion

Phase 2 — Analyse Initiale
  □ Vérifier les Interesting Items
  □ Examiner les Known/Unknown dans File Views
  □ Analyser la Timeline pour les périodes suspectes
  □ Taguer les fichiers importants

Phase 3 — Recherche Ciblée
  □ Lancer Keyword Search (termes prédéfinis + contexte)
  □ Analyser les résultats de hash lookup
  □ Examiner les comptes utilisateur
  □ Vérifier les extensions mismatch

Phase 4 — Analyse Approfondie
  □ Extraire les fichiers tagués
  □ Analyser les fichiers suspects (VirusTotal, YARA)
  □ Examiner le registre (si ingéré)
  □ Reconstruire la timeline événementielle

Phase 5 — Rapport
  □ Generer le rapport (HTML/Excel)
  □ Exporter les fichiers de preuve
  □ Documenter la chaîne de custody
  □ Signer le rapport (checksum)
```

### Investigation Rapide (Triage)

```bash
# Analyse CLI en 5 minutes
mmls image.dd
fls -o 2048 -d image.dd | head -50
fls -o 2048 -rp image.dd | grep -iE "\.doc|\.pdf|\.xls|\.jpg"
sigfind -l image.dd
icat -o 2048 image.dd $(fls -o 2048 -d image.dd | head -1 | awk -F'[] []' '{print $2}')
```

---

## 11. Formats d'Image Supportés

| Format | Extension | Description | Taille |
|--------|-----------|-------------|--------|
| Raw/DD | .dd, .raw, .img | Bit-for-bit, simple | = disque |
| E01 (EWF) | .e01, .e02 | Expert Witness, compressé | 50-80% du disque |
| AFF | .aff, .afm | Advanced Forensic Format | compressé + métadonnées |
| AFF4 | .aff4 | Nouvelle génération AFF | compressé + metadata |
| VHD/VHDX | .vhd, .vhdx | Virtual Hard Disk (Hyper-V) | variable |
| VMDK | .vmdk | Virtual Machine Disk (VMware) | variable |
| QCOW2 | .qcow2 | QEMU Copy-On-Write | variable |

---

## 12. Ressources

- **Autopsy Documentation** : https://www.autopsy.com/docs/
- **Sleuth Kit Wiki** : https://wiki.sleuthkit.org/
- **Body File Format** : https://wiki.sleuthkit.org/index.php?title=Body_file
- **NSRL (NIST)** : https://www.nsrl.nist.gov/
- **SIFT Workstation** : https://www.sans.org/tools/sift-workstation/
- **Autopsy Community Forum** : https://groups.google.com/g/sleuthkit-users