---
name: osint-document-metadata
description: Analyse de métadonnées de documents — extraction EXIF, PDF, Office, analyse forensique de fichiers, stéganographie et chasse aux informations cachées.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, métadonnées, documents, exif, pdf, office, stéganographie]
---

# Analyse de Métadonnées de Documents

## 🎯 Description

Extraction et analyse des métadonnées de documents : fichiers PDF, Office (Word, Excel, PowerPoint), images, archives, et autres formats. Découverte d'informations cachées : auteur, historique de modifications, chemins de fichiers, données GPS, commentaires supprimés, et contenu stéganographié.

---

## 📋 Outils Essentiels

### Analyse Générale de Métadonnées
| Outil | URL | Usage |
|-------|-----|-------|
| ExifTool | https://exiftool.org | Analyse multi-format (images, PDF, Office, audio, vidéo) |
| ExifLooter | https://github.com/aydinnyunus/exiflooter | CLI léger |
| Metadata Viewer | https://kriztalz.sh/metadata-viewer/ | Visualisation en ligne |
| ChronoVerify | https://chronoverify.com | Vérification C2PA et XMP |

### Analyse PDF
| Outil | URL | Usage |
|-------|-----|-------|
| pdfinfo | (poppler-utils) | Métadonnées PDF via CLI |
| pdf-parser.py | https://github.com/DidierStevens/DidierStevensSuite | Analyse structure PDF |
| PDFiD | https://github.com/DidierStevens/DidierStevensSuite | Détection d'objets suspects |
| Origami | https://github.com/gdelugre/origami | Framework analyse PDF |
| Peepdf | https://github.com/jesparza/peepdf | Analyse de sécurité PDF |

### Analyse Documents Office
| Outil | URL | Usage |
|-------|-----|-------|
| olemeta | (python-olefile) | Métadonnées OLE |
| oletools | https://github.com/decalage2/oletools | Suite analyse OLE/Office |
| python-pptx | https://python-pptx.readthedocs.io | Analyse PowerPoint |
| python-docx | https://python-docx.readthedocs.io | Analyse Word |

### Analyse d'Images
| Outil | URL | Usage |
|-------|-----|-------|
| ExifTool | https://exiftool.org | EXIF complet |
| JPEGsnoop | https://sourceforge.net/projects/jpegsnoop | Analyse JPEG |
| Forensically | https://29a.ch/photo-forensics/ | Analyse forensique |
| FotoForensics | https://www.fotoforensics.com | ELA et autres |
| ImgOps | https://imgops.com/ | Multi-outils image |

### Stéganographie
| Outil | URL | Usage |
|-------|-----|-------|
| Steghide | http://steghide.sourceforge.net | Cache/révèle dans images/audio |
| Stegseek | https://github.com/RickdeJager/stegseek | Brute-force steghide |
| Zsteg | https://github.com/zed-0xff/zsteg | Détection stégano PNG/BMP |
| StegSolve | https://github.com/eugenekolo/sec-tools/tree/master/stego/stegsolve | Analyse stégano visuelle |
| binwalk | https://github.com/ReFirmLabs/binwalk | Analyse firmware/images |

---

## 🔧 Commandes CLI

### ExifTool - Multi-Format
```bash
# Installation
sudo apt install exiftool -y

# Toutes les métadonnées
exiftool document.pdf
exiftool document.docx
exiftool image.jpg
exiftool video.mp4
exiftool audio.mp3

# Sélection spécifique
exiftool -Author -Creator -Producer -CreateDate -ModifyDate document.pdf

# Extraction en JSON
exiftool -json document.pdf > metadata.json

# Extraction GPS
exiftool -GPS* photo.jpg

# Fichier de sortie
exiftool -csv *.pdf > all_pdfs.csv

# Suppression des métadonnées
exiftool -all= document.pdf
exiftool -all= image.jpg
```

### Analyse PDF
```bash
# pdfinfo (poppler-utils)
sudo apt install poppler-utils -y
pdfinfo document.pdf

# pdf-parser (Didier Stevens)
wget https://raw.githubusercontent.com/DidierStevens/DidierStevensSuite/master/pdf-parser.py
python3 pdf-parser.py document.pdf

# PDFiD
python3 pdfid.py document.pdf

# Recherche d'objets JavaScript
python3 pdf-parser.py -s javascript document.pdf

# Extraction de flux
python3 pdf-parser.py -f document.pdf > streams.txt
```

### Analyse Documents Office
```bash
# oletools
pip install oletools

# Métadonnées OLE
olemeta document.doc
olemeta document.xls

# VBA macros
olevba document.docm

# Analyse de liens DDE
oledump.py document.docx

# MRU (Most Recently Used)
python3 -c "
import olefile
ole = olefile.OleFileIO('document.doc')
if ole.exists('\x05SummaryInformation'):
    print('Summary info:', ole.getproperties('\x05SummaryInformation'))
"
```

## 📊 Techniques d'Extraction

### 1. Métadonnées PDF
```text
Informations extractibles d'un PDF :

- Author / Creator / Producer
- CreationDate / ModDate
- Title / Subject
- PDF version
- Page count
- Encryption status
- Embedded files
- JavaScript actions
- Fonts used
- Software de création (Adobe, Word, LibreOffice, etc.)
- XMP metadata
- ID de document (identifiant unique)
```

### 2. Métadonnées Office
```text
Informations extractibles des fichiers Office :

- Author (créateur du document)
- Last Modified By
- Company
- Manager
- Creation Date
- Last Modified Date
- Last Printed
- Total Editing Time
- Revision Number
- Template
- Comments
- Hidden rows/columns (Excel)
- Track changes (Word)
- Comments in margins
- Embedded objects/images
- URLs dans les hyperliens
- Serveurs de templates
```

### 3. Stéganographie - Détection
```bash
# Zsteg (PNG, BMP)
pip install zsteg
zsteg image.png
zsteg -a image.png  # tous les tests

# Steghide
steghide extract -sf image.jpg -p "" 2>/dev/null
# Si mot de passe requis:
# stegseek image.jpg wordlist.txt

# Binwalk (analyse de fichiers cachés)
sudo apt install binwalk -y
binwalk image.png
binwalk -Me image.png  # extraction

# Strings basique
strings document.pdf | grep -i "password\|secret\|hidden\|user\|admin"
strings image.jpg | tail -50
```

---

## 🛠️ Script d'Analyse Complet

```bash
#!/bin/bash
# document_metadata.sh
FILE="$1"

echo "=== Analyse complète de: $FILE ==="

# Type de fichier
echo "--- Type ---"
file "$FILE"

# Taille et hash
echo "--- Identifiants ---"
stat --format="Taille: %s bytes" "$FILE"
sha256sum "$FILE" | cut -d' ' -f1
md5sum "$FILE" | cut -d' ' -f1

# Métadonnées (si exiftool disponible)
if command -v exiftool &>/dev/null; then
    echo "--- Métadonnées ---"
    exiftool "$FILE" 2>/dev/null | \
      grep -E "Author|Creator|Producer|Date|Time|Software|Title|Subject|Company|Manager" | head -20
fi

# Strings sensibles
echo "--- Strings sensibles ---"
strings "$FILE" | grep -iE \
  "password|secret|hidden|confidential|admin|user|login|email|@|http|https|192\.168|10\.|172\." | \
  sort -u | head -20
```

---

## 📝 Recherche d'Informations Spécifiques

### Chemins de Fichiers (Paths)
```bash
# Les chemins révèlent :
# - Nom d'utilisateur
# - Structure de répertoires
# - Nom du poste
# - Logiciels installés

exiftool document.pdf | grep -i "path\|folder\|directory"
strings document.docx | grep -E "^[A-Z]:\\\\|[A-Z]:/"
```

### Historique de Versions
```bash
# Nombre de révisions
exiftool -RevisionNumber document.docx

# Temps d'édition total
exiftool -TotalEditTime document.docx

# Dernière impression
exiftool -LastPrinted document.docx
```

### Serveurs et Réseaux
```bash
# URLs dans les documents
strings document.pdf | grep -oP 'https?://[^ )"\'>]+' | sort -u

# Adresses IP
strings document.docx | grep -oP '\b(?:\d{1,3}\.){3}\d{1,3}\b' | sort -u

# Noms de serveurs
strings document.pdf | grep -i "server\|sql\|database\|api\|dev\|staging\|prod"
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Nettoyage** : La plupart des réseaux sociaux et plateformes de partage suppriment les métadonnées (mais pas tous).
- **Conversion** : La conversion de format (DOCX → PDF) peut préserver ou supprimer des métadonnées selon la méthode.
- **Compression** : Les images compressées perdent certaines métadonnées EXIF.
- **Droit d'auteur** : Les métadonnées peuvent révéler des violations de copyright.
- **Preuve légale** : Les métadonnées peuvent servir de preuve médico-légale. Documenter la chaîne de conservation.
- **Falsification** : Les métadonnées peuvent être falsifiées. Toujours croiser avec d'autres sources.

---

## 🔗 Références

- https://exiftool.org
- https://github.com/DidierStevens/DidierStevensSuite
- https://github.com/decalage2/oletools
- https://29a.ch/photo-forensics/