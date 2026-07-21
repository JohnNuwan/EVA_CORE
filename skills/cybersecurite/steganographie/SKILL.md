---
name: steganographie
description: Guide complet de stéganographie — zsteg, steghide, stegsolve, stegcracker, binwalk, strings, LSB, PNG, JPEG, WAV, extraction et dissimulation de données.
---

# Stéganographie — Guide Complet

## Définition

Art de dissimuler des données dans d'autres fichiers (images, audio, vidéo).
Contrairement à la cryptographie qui rend les données illisibles, la
stéganographie rend les données **invisibles**.

---

## 1. Analyse rapide — Premiers réflexes

```bash
# 1. Type de fichier
file image_suspecte.png

# 2. Strings (chaînes lisibles)
strings image_suspecte.png | less
strings -n 8 image_suspecte.png    # Chaînes de 8+ caractères

# 3. Hex dump (premiers octets)
xxd image_suspecte.png | head -20

# 4. Métadonnées
exiftool image_suspecte.png
exiftool -Comment image_suspecte.png

# 5. Taille suspecte ?
ls -lh image_suspecte.png
# Une image PNG de 10 MB pour 200×200 pixels = suspect
```

---

## 2. Images PNG — zsteg

```bash
# Analyse complète LSB
zsteg image.png

# Tous les bits
zsteg -a image.png

# Extraction forcée
zsteg -E b1,r,lsb,xy image.png > extrait.bin

# Format spécifique
zsteg --bits 1 --channel r --lsb --order xy image.png
```

---

## 3. Images JPEG/BMP/WAV — steghide

```bash
# Extraire des données
steghide extract -sf image.jpg
steghide extract -sf audio.wav -p password

# Dissimuler des données
steghide embed -cf image.jpg -ef secret.txt
steghide embed -cf image.jpg -ef secret.txt -p password

# Vérifier si une image contient des données
steghide info image.jpg
```

---

## 4. Bruteforce steghide — stegcracker / stegseek

```bash
# stegcracker (lent, Python)
stegcracker image.jpg rockyou.txt

# stegseek (rapide, C++)
stegseek image.jpg rockyou.txt
stegseek --crack image.jpg rockyou.txt resultat.txt
```

---

## 5. Analyse visuelle — Stegsolve (GUI Java)

```bash
# Lancer (nécessite Java)
java -jar Stegsolve.jar

# Techniques dans Stegsolve :
# - Frame browser : parcourir les plans de bits
# - Random colour map : révéler des motifs
# - XOR, AND, OR entre plans
# - File format analysis
```

---

## 6. Extraction de fichiers cachés — binwalk

```bash
# Scanner le fichier
binwalk image.png

# Extraire automatiquement
binwalk -e image.png
binwalk -Me image.png      # Extraction récursive

# Extraire tout type de fichier
binwalk --dd='.*' image.png

# Analyse d'entropie (détecter compression/chiffrement)
binwalk -E image.png
# Entropie proche de 1 → chiffré ou compressé
# Entropie basse → texte ou image normale
```

---

## 7. Extraction bas niveau — foremost / dd

```bash
# Extraire tous les fichiers détectables
foremost -i image.png -o /sortie/

# Extraire une plage d'octets
dd if=image.png of=extrait.bin bs=1 skip=<OFFSET> count=<TAILLE>

# Chercher des signatures de fichiers
strings -t x image.png | grep -E "PK|IHDR|ID3|RIFF|JFIF"
```

---

## 8. Images GIF animées

```bash
# Extraire les frames
convert image.gif frame_%d.png

# Analyser frame par frame
identify -verbose image.gif
```

---

## 9. Audio WAV/MP3 — stégano audio

```bash
# Spectrogramme (révéler du texte caché)
sox audio.wav -n spectrogram -o spectro.png

# Analyse avec Sonic Visualizer (GUI)

# DeepSound (Windows pour WAV/FLAC)

# LSB audio
# via Python : wave module, modifier le bit de poids faible
```

---

## 10. Texte / Whitespace

```bash
# stegsnow — dissimulation dans les espaces/blancs
snow -C fichier.txt
stegsnow -C -p password fichier.txt extrait.txt

# Zero-width characters (Unicode)
# Caractères invisibles : U+200B, U+200C, U+200D, U+FEFF
```

---

## 11. PDF / Documents

```bash
# Analyse de PDF
pdfinfo document.pdf
pdf-parser.py document.pdf
peepdf document.pdf

# Stégano dans les images d'un PDF
pdfimages -j document.pdf /sortie/
```

---

## Cheatsheet rapide

```bash
# 1. Première approche
file suspect.xxx
strings suspect.xxx | less
exiftool suspect.xxx
binwalk suspect.xxx

# 2. PNG
zsteg suspect.png

# 3. JPEG/WAV
steghide extract -sf suspect.jpg
steghide info suspect.jpg
stegseek suspect.jpg rockyou.txt

# 4. Extraction générique
binwalk -Me suspect.xxx
foremost -i suspect.xxx -o /sortie/

# 5. Audio
sox audio.wav -n spectrogram -o spec.png

# 6. Texte
snow -C fichier.txt
```

## Ressources
- **picoCTF** : https://picoctf.org — Challenges stégano CTF
- **Stegsolve** : https://github.com/zardus/ctf-tools
- **Aperi'Solve** : https://www.aperisolve.com — Stégano en ligne
- **StegOnline** : https://stegonline.georgeom.net — Analyse en ligne
