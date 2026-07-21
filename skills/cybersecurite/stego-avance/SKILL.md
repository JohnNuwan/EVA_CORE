---
name: stego-avance
description: Stéganographie avancée — LSB, DCT/JPG, WAV/MP3, vidéo, réseau, polyglottes, détection forensique, et outils de dissimulation/détection
tags: [stego, forensics, LSB, DCT, WAV, polyglot, detection, exfiltration]
version: 1.0
---

# Stéganographie Avancée

Guide de stéganographie offensive et détection — dissimulation et extraction de données dans tous types de médias.

## 1. Image — LSB (Least Significant Bit)

### LSB Basique (PNG/BMP)
```python
# Cacher dans les LSBs des pixels
import numpy as np
from PIL import Image

def hide_lsb(image_path, message, output_path):
    img = Image.open(image_path)
    arr = np.array(img).flatten()
    
    # Ajouter delimiter pour l'extraction
    message += "#####"
    bits = ''.join(format(ord(c), '08b') for c in message)
    
    if len(bits) > len(arr):
        raise ValueError("Message trop long")
    
    # Modifier les LSBs
    arr[:len(bits)] = (arr[:len(bits)] & 0xFE) | [int(b) for b in bits]
    
    result = Image.fromarray(arr.reshape(img.size[1], img.size[0], -1))
    result.save(output_path)

def extract_lsb(image_path):
    img = Image.open(image_path)
    arr = np.array(img).flatten()
    bits = [str(b & 1) for b in arr]
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        char = chr(int(''.join(byte), 2))
        chars.append(char)
        if ''.join(chars[-5:]) == '#####':
            return ''.join(chars[:-5])
    return ''.join(chars)
```

### Palette-Based (GIF)
```python
# Manipuler l'ordre des couleurs dans la palette
# Chaque pixel = index dans palette
# Changer ordre palette sans affecter visuel
```

## 2. Image — Transform Domain (JPEG)

### DCT (Discrete Cosine Transform)
```python
# JPEG utilise DCT + quantification
# Modifier les coefficients DCT les moins significatifs
# Outils : stegdetect, stegbreak, outguess

import jpeglib

def hide_jpeg(input_jpg, message, output_jpg, quality=85):
    """JPEG stego via DCT coefficient manipulation"""
    im = jpeglib.read_dct(input_jpg)
    coeffs = im.Y  # Coefficients Y (luminance)
    
    # Modifier les coefficients AC les plus petits
    bits = ''.join(format(ord(c), '08b') for c in message)
    idx = 0
    for i in range(coeffs.shape[0]):
        for j in range(coeffs.shape[1]):
            for k in range(1, 64):  # Skip DC
                if idx >= len(bits):
                    break
                if abs(coeffs[i,j,k]) <= 2:  # Petit coefficient
                    coeffs[i,j,k] = (abs(coeffs[i,j,k]) & 0xFE) | int(bits[idx])
                    idx += 1
    
    im.Y = coeffs
    im.write_dct(output_jpg)
```

### F5 Algorithm (JPEG Stego)
```bash
# F5 : matrix encoding + permutation
# Moins détectable que JSteg/JPHide
# Outil : 
# - F5 standalone (Java)
# - stegbreak : F5 detection
```

## 3. Audio Steganography

### WAV (LSB on samples)
```python
# PCM samples 16-bit → modifier LSB
# 44100 Hz × 16 bits × 2 canaux = ~172 KB/s disponible

import wave

def hide_wav(wav_path, message, output_path):
    with wave.open(wav_path, 'rb') as wav:
        frames = bytearray(wav.readframes(wav.getnframes()))
    
    message += '#####'
    bits = ''.join(format(ord(c), '08b') for c in message)
    
    if len(bits) > len(frames):
        raise ValueError("Message trop long")
    
    for i, b in enumerate(bits):
        frames[i] = (frames[i] & 0xFE) | int(b)
    
    with wave.open(output_path, 'wb') as out:
        out.setparams(wav.getparams())
        out.writeframes(bytes(frames))
```

### Spread Spectrum
```python
# Étaler le signal sur toute la bande audio
# Résistant aux compressions
# Méthode : DSSS (Direct Sequence Spread Spectrum)
# Pseudo-random sequence + message → bruit difficilement détectable
```

### Echo Hiding
```python
# Cacher dans les échos (délais < 1ms)
# Deux délais : 0 = bit 0, 1 = bit 1
# Imperceptible à l'oreille humaine
```

### MP3 Steganography
```python
# Modifier les frames MP3
# Outils : MP3Stego (public), UnderMP3Cover
# mp3stego-encode -E hidden.txt -P password cover.mp3 output.mp3
```

## 4. Video Steganography

### Frame-wise
```python
# Chaque frame vidéo → image individuelle
# LSB sur chaque frame
# 30fps × 1920×1080 × 3 × 8bit = ~1.4 Gbps

# Utiliser frames I (intra-coded) pour fiabilité
# Frames P/B peuvent être perdues (compression)
```

### Motion Vector Stego
```python
# Modifier légèrement les vecteurs de mouvement
# Subpel motion estimation : altérer demi-pixel
# Imperceptible à l'œil
```

## 5. Network Steganography

### TCP/IP Headers
```python
# Cacher dans :
# - IP Identification field (16 bits par paquet)
# - TCP Sequence Number (initial)
# - TCP Timestamp option
# - TCP ISN (Initial Sequence Number)
# - IP Fragment Offset
# - HTTP headers (order, custom headers)

# Example : IP ID field
# LSB de IP ID = bit du message
# Non fiable (NAT, routeurs changent IP ID)
```

### DNS Tunneling
```bash
# Encoder données dans les requêtes DNS
# subdomain.data.attacker.com
# Base32 → DNS labels
# Récupération via DNS server contrôlé

# Outils
# - dnscat2
# - iodine
# - dns2tcp
```

### ICMP Covert Channel
```python
# Data dans ICMP echo request
# Ping tunnel
# ptunnel : ICMP tunneling tool
```

## 6. File System Steganography

### Alternate Data Streams (NTFS)
```cmd
# Cacher fichier dans ADS
echo "hidden message" > normal.txt:hidden.txt
type normal.txt:hidden.txt

# Lister ADS
dir /R
streams.exe -s C:\
```

### Metadata
```bash
# EXIF : comment, copyright
# Document properties : author, company
# Slack space : entre fin de fichier et fin de cluster
```

### Polyglot Files
```bash
# Fichier valide dans deux formats simultanément
# GIFAR : GIF + JAR
# PDF + ZIP
# PNG + HTML (comment block)
```

## 7. Hardware Steganography

### EEPROM / Firmware
```bash
# Cacher dans :
# - Unused firmware bytes
# - Comment blocks (microcode)
# - FPGA bitstream padding
# - GPU shader constants
```

## 8. Détection Forensique

### Statistical Analysis
```bash
# Chi-square test (LSB detection)
# - Paires de valeurs (PoV)
# - RS Analysis (regular/singular groups)
# - Sample Pairs Analysis (SPA)

stegdetect -t jopi -s 100.0 image.jpg
```

### Outils de Détection
```bash
# zsteg : LSB detection PNG/BMP
zsteg -a image.png
zsteg -E 'b1,bgr,lsb' image.png

# Stegdetect : JPEG stego
stegdetect -t jopi image.jpg
stegdetect -t jopi -s 100.0 image.jpg  # Haute sensibilité

# Stegbreak : brute-force extraction
stegbreak -d wordlist.txt -t jpg -F image.jpg

# Aperi'Solve : online + multiple tools
# https://www.aperisolve.com

# stegsolve.jar : GUI analysis
java -jar stegsolve.jar
```

### Entropy Analysis
```bash
# Mesurer l'entropie des LSBs
# Normal : aléatoire (0.5 average)
# Stego : tend vers 0 ou 1 (corrélation)

# Outil : binwalk entropy
binwalk -E image.png
```

## 9. Blind Steganography

### Bruteforce Keys
```bash
# Si stego password-protected
# steghide : --crack mode
steghide extract -sf image.jpg -p password
steghide extract -sf image.jpg -xf extracted.txt -p "password"
```

### Known Cover & Known Message
```bash
# Comparer l'original (cover) et le stego
# Diff → extraire le message
# Outil : compare (ImageMagick)
compare cover.png stego.png diff.png
```

## 10. Tools Compendium

| Outil | Formats | Usage |
|-------|---------|-------|
| **zsteg** | PNG/BMP | `zsteg -a image.png` |
| **steghide** | JPEG/BMP/WAV | `steghide embed -cf cover -ef secret` |
| **stegsolve** | Multi | GUI analysis tool |
| **stegdetect** | JPEG | `stegdetect -t jopi image.jpg` |
| **outguess** | JPEG | `outguess -r image.jpg output.txt` |
| **jsteg** | JPEG | `jsteg hide cover.jpg secret.txt` |
| **binwalk** | Multi | `binwalk -E image.png` |
| **mp3stego** | MP3 | `mp3stego-decode` |
| **stegbreak** | JPEG | Brute-force password |
| **Aperi'Solve** | Multi | Web-based analysis |
| **OpenStego** | Multi | GUI + CLI |
| **SilentEye** | Multi | GUI (image + audio) |

## 11. Ressources

- **Steganography CTF** : https://0xrick.github.io/lists/stego/
- **Aperi'Solve** : https://aperisolve.com
- **CrackStation Stego** : https://crackstation.net
- **CTF Stego Reference** : https://github.com/DominicBreuker/stego-toolkit
- **Information Hiding** : Petitcolas, Anderson
- **Steganography Tutorials** : https://trailofbits.github.io/ctf/forensics
- **zsteg** : https://github.com/zed-0xff/zsteg