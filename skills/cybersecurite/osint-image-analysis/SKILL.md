---
name: osint-image-analysis
description: Analyse d'images et reconnaissance visuelle — EXIF, métadonnées, analyse forensique, reverse image search, deepfake detection.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, image, analyse, EXIF, forensique, métadonnées, reverse-image]
---

# Analyse d'Images et Reconnaissance Visuelle

## 🎯 Description

Analyse forensique d'images : extraction de métadonnées EXIF, analyse de la composition, détection de manipulations, reverse image search, vérification d'authenticité, géolocalisation et identification de personnes/objets.

---

## 📋 Outils Essentiels

### Analyse EXIF et Métadonnées
| Outil | URL | Usage |
|-------|-----|-------|
| ExifTool | https://exiftool.org | Analyse EXIF complète (CLI) |
| Jeffrey's Viewer | https://exif.regex.info/ | Visualisation EXIF en ligne |
| JIMPL | https://jimpl.com/ | Lecteur EXIF en ligne |
| EXIFEditor.io | https://exifeditor.io | Éditeur/analyseur EXIF |
| Metadata Viewer | https://kriztalz.sh/metadata-viewer/ | Visualisation métadonnées |
| ExifLooter | https://github.com/aydinnyunus/exiflooter | CLI EXIF |
| ExifTool GUI | https://exiftool.org/gui.html | Interface graphique |

### Reverse Image Search
| Outil | URL | Usage |
|-------|-----|-------|
| Google Images | https://images.google.com | Reverse image search |
| Google Lens | https://lens.google.com/ | Recherche visuelle IA |
| TinEye | https://tineye.com | Reverse image search |
| Yandex Images | https://www.yandex.com/images | Reverse image search |
| Bing Images | https://www.bing.com/images | Reverse image search |
| Baidu Images | https://image.baidu.com | Reverse image search Chine |
| Dupli Checker | https://www.duplichecker.com/reverse-image-search.php | Recherche doublons |
| Image Raider | https://www.imageraider.com | Recherche multi-sources |
| Lenso.ai | https://lenso.ai | Recherche + reconnaissance faciale |

### Reconnaissance Faciale
| Outil | URL | Usage |
|-------|-----|-------|
| PimEyes | https://pimeyes.com | Recherche faciale |
| FaceCheck.ID | https://facecheck.id | Reconnaissance faciale |
| Search4faces | https://search4faces.com | Recherche par visage |
| Surfface | https://surfface.com | Face search + réseaux |
| Faceagle | https://faceagle.com | Moteur de recherche faciale |
| Betaface | https://www.betaface.com/demo.html | API reconnaissance |
| PicTriev | https://www.pictriev.com | Recherche faciale |

### Analyse Forensique
| Outil | URL | Usage |
|-------|-----|-------|
| FotoForensics | https://www.fotoforensics.com | ELA + analyse |
| Forensically | https://29a.ch/photo-forensics/ | Suite forensique |
| forensics.media | https://forensics.media/tools/ | Outils forensiques gratuits |
| JPEGsnoop | https://sourceforge.net/projects/jpegsnoop | Analyse JPEG |
| ImpulseAdventure | https://www.impulseadventure.com/photo/jpeg-snoop.html | Analyse JPEG |
| DiffChecker | https://www.diffchecker.com/image-diff/ | Comparaison d'images |
| ChronoVerify | https://chronoverify.com | Vérification C2PA Content Credentials |

### Géolocalisation d'Images
| Outil | URL | Usage |
|-------|-----|-------|
| GeoSpy | https://geospy.web.app/ | Géolocalisation par IA |
| GeoInfer | https://geoinfer.com | Géolocalisation sans EXIF |
| Pic2Map | https://www.pic2map.com/ | Localisation depuis photo |
| ReverseImageLocation | https://reverseimagelocation.com | Géolocalisation par IA |
| TracePoint | https://kluter.github.io/TracePoint/ | Géolocalisation par rayons |

---

## 🔧 Commandes CLI

### ExifTool - Analyse Complète
```bash
# Installation
sudo apt install exiftool -y

# Toutes les métadonnées
exiftool photo.jpg

# Métadonnées GPS uniquement
exiftool -GPS* photo.jpg

# Métadonnées de l'appareil
exiftool -Make -Model -LensID -FocalLength photo.jpg

# Date et heure
exiftool -DateTimeOriginal -CreateDate -ModifyDate photo.jpg

# Supprimer les métadonnées
exiftool -all= photo.jpg

# Exporter en JSON
exiftool -json photo.jpg
```

### Extraction de Données Cachées
```bash
# Strings dans l'image
strings photo.jpg | grep -i "exif\|gps\|copyright\|author"

# Analyse de stéganographie basique
# Steghide
steghide extract -sf photo.jpg -p "" 2>/dev/null || echo "Pas de données cachées"
```

---

## 📊 Techniques d'Analyse

### 1. Analyse EXIF - Que Chercher
```text
# Informations critiques EXIF :
- GPSLatitude / GPSLongitude → Localisation
- DateTimeOriginal → Date et heure de prise
- Make / Model → Appareil photo
- Software → Logiciel d'édition
- FocalLength / FNumber → Conditions de prise
- ISO → Sensibilité
- Flash → Flash utilisé
- ImageUniqueID → Identifiant unique
- Copyright → Droits d'auteur
- Artist → Photographe
- UserComment → Commentaires
- Thumbnail → Vignette (peut contenir des infos cachées)
```

### 2. Reverse Image Search - Stratégie
```bash
# 1. Google Images
# Naviguer vers https://images.google.com -> icône appareil photo

# 2. Yandex (meilleur pour les visages)
# Naviguer vers https://www.yandex.com/images

# 3. TinEye (meilleur pour les correspondances exactes)
# Naviguer vers https://tineye.com

# 4. Baidu (bon pour les sources chinoises)
# Naviguer vers https://image.baidu.com

# 5. Lenso.ai (reconnaissance faciale)
# Naviguer vers https://lenso.ai
```

### 3. Analyse Forensique
```bash
# Error Level Analysis (ELA) - détection de manipulation
# FotoForensics: https://www.fotoforensics.com

# Clone Detection - détection de copier-coller
# Forensically: https://29a.ch/photo-forensics/

# Analyse des niveaux JPEG
# JPEGsnoop: analyse des artefacts de compression
```

### 4. Vérification d'Authenticité
```bash
# ChronoVerify - Vérification C2PA Content Credentials
# Naviguer sur https://chronoverify.com

# ProfileImageIntel - date de téléchargement d'image de profil
# Naviguer sur https://profileimageintel.com/
```

---

## 🛠️ Script d'Analyse Automatisé

```bash
#!/bin/bash
# analyze_image.sh
IMAGE="$1"

echo "=== Analyse de: $IMAGE ==="

# Métadonnées EXIF
echo "--- EXIF ---"
exiftool "$IMAGE" 2>/dev/null | grep -E "GPS|Date|Time|Make|Model|Software|Artist|Copyright|UserComment"

# Taille et dimensions
echo "--- Dimensions ---"
identify "$IMAGE" 2>/dev/null || file "$IMAGE"

# Hachage
echo "--- Hash ---"
sha256sum "$IMAGE"
md5sum "$IMAGE"

# Strings sensibles
echo "--- Strings sensibles ---"
strings "$IMAGE" | grep -iE "gps|lat|lon|location|author|creator|artist|copyright|@"
```

---

## 📝 Détection de Deepfakes et IA

### Indices de Manipulation
```text
- Artefacts de compression JPEG incohérents
- Ombres incohérentes avec la source lumineuse
- Reflets dans les yeux anormaux
- Bornes floues entre le sujet et l'arrière-plan
- Détails manquants (dents, doigts mal formés)
- Métadonnées EXIF absentes ou incohérentes
- Dates de création/modification incohérentes
```

### Vérification d'Authenticité
```bash
# 1. Vérifier les métadonnées EXIF (date, appareil, logiciel)
# 2. Analyser les niveaux d'erreur JPEG (ELA)
# 3. Reverse image search (traçage de l'image)
# 4. Vérifier les ombres et l'éclairage
# 5. Analyser les reflets dans les yeux
# 6. Vérifier la cohérence des pixels au niveau des bordures
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **EXIF stripping** : Les réseaux sociaux (Twitter, Facebook, Instagram) suppriment les EXIF. L'image originale peut en avoir.
- **Ré-encodage** : Chaque téléchargement/re-upload modifie les métadonnées et les artefacts de compression.
- **Fausses correspondances** : La recherche d'images peut donner des faux positifs. Vérifier le contexte.
- **Deepfakes** : Les images générées par IA deviennent difficiles à détecter. Toujours chercher des sources indépendantes.
- **Légalité** : La reconnaissance faciale est réglementée (RGPD, BIPA).

---

## 🔗 Références

- https://exiftool.org
- https://github.com/jivoi/awesome-osint#image-search
- https://29a.ch/photo-forensics/
- https://fotoforensics.com/