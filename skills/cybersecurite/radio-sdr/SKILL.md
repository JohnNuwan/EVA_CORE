---
name: radio-sdr
description: Guide complet de radio logicielle (SDR) — RTL-SDR, HackRF, Gqrx, GNU Radio, analyse de signaux, capture et rejeu, ADS-B, sécurité RF.
---

# Radio Logicielle (SDR) — Guide Complet

---

## 1. Matériel SDR

| Appareil | Fréquences | Prix | Usage |
|----------|-----------|------|-------|
| **RTL-SDR** (RTL2832U) | 24 MHz – 1.7 GHz | ~25€ | Réception uniquement, débutant |
| **HackRF One** | 1 MHz – 6 GHz | ~300€ | Émission + réception, pro |
| **Airspy R2** | 24 MHz – 1.7 GHz | ~170€ | Haute qualité réception |
| **LimeSDR** | 100 kHz – 3.8 GHz | ~300€ | Full-duplex, 2×2 MIMO |
| **BladeRF** | 47 MHz – 6 GHz | ~400€ | 2×2 MIMO, FPGA |
| **USRP B200** | 70 MHz – 6 GHz | ~700€ | Professionnel |

---

## 2. Installation des outils

```bash
# Pilotes RTL-SDR
sudo apt install rtl-sdr

# Test : lister les appareils
rtl_test

# Gqrx (interface graphique SDR)
sudo apt install gqrx-sdr

# HackRF tools
sudo apt install hackrf

# GNU Radio (framework DSP)
sudo apt install gnuradio

# Outils ADS-B (aviation)
sudo apt install dump1090

# Analyse spectrale
sudo apt install spektrum
```

---

## 3. Gqrx — Récepteur SDR graphique

```bash
# Lancer Gqrx
gqrx

# Configuration rapide :
# 1. Sélectionner le device (RTL-SDR ou HackRF)
# 2. Choisir la fréquence (FM radio : 88-108 MHz)
# 3. Mode : NFM (FM bande étroite), WFM (FM broadcast), AM, SSB
# 4. Ajuster le gain
```

## 4. Commandes RTL-SDR

```bash
# Scanner les fréquences
rtl_power -f 88M:108M:100k -g 20 -i 1 scan.csv

# Écouter et enregistrer FM
rtl_fm -f 103.5M -M wbfm -s 200k -r 48k - | aplay -r 48k -f S16_LE

# Capturer des données brutes
rtl_sdr -f 433.92M -s 2048000 capture.iq

# ADS-B (trafic aérien)
dump1090 --interactive --net
# Puis ouvrir http://localhost:8080
```

---

## 5. HackRF — Émission + Réception

```bash
# Vérifier le HackRF
hackrf_info

# Capturer un signal
hackrf_transfer -r capture.iq -f 433920000 -s 8000000

# Rejouer un signal
hackrf_transfer -t capture.iq -f 433920000 -s 8000000

# Sweep de fréquences (spectrogramme)
hackrf_sweep -f 100:6000 -w 1000000 -l 32 -g 32

# Transmettre un fichier audio WAV
hackrf_transfer -t audio.wav -f 100000000 -s 2000000 -x 40
```

---

## 6. Fréquences utiles (France)

| Fréquence | Usage |
|-----------|-------|
| 87.5 – 108 MHz | FM Radio broadcast |
| 108 – 137 MHz | Bande aéronautique (AM) |
| 144 – 146 MHz | Radioamateur 2m |
| 433.05 – 434.79 MHz | LPD/ISM (domotique, télécommandes) |
| 446.0 – 446.2 MHz | PMR446 (talkie-walkies) |
| 868 – 868.6 MHz | ISM/SRD (capteurs, alarmes) |
| 925 – 960 MHz | GSM (downlink) |
| 1090 MHz | ADS-B (aviation) |
| 1575.42 MHz | GPS L1 |
| 1805 – 1880 MHz | GSM 1800 (downlink) |
| 2400 – 2483.5 MHz | WiFi 2.4 GHz, Bluetooth |
| 5150 – 5850 MHz | WiFi 5 GHz |

---

## 7. GNU Radio — Traitement de signal

```bash
# Lancer GNU Radio Companion (GUI)
gnuradio-companion

# Blocs typiques :
# - Osmocom Source → recevoir SDR
# - QT GUI Sink → afficher spectre/FFT
# - Low Pass Filter → filtrer
# - AM Demod, FM Demod → démoduler
# - File Sink → sauvegarder
# - Wav File Source → charger audio
```

---

## 8. Sécurité RF — Attaques courantes

### Replay attack (clés de voiture, télécommandes)
```bash
# 1. Capturer
hackrf_transfer -r telecommande.iq -f 433920000 -s 2000000 -n 20000000

# 2. Rejouer
hackrf_transfer -t telecommande.iq -f 433920000 -s 2000000 -x 40
```

### Interception GSM (réception uniquement, illégal sans licence)
```bash
# Capturer le downlink GSM
rtl_sdr -f 950M -s 2000000 capture_gsm.iq

# Démoduler avec gr-gsm (GNU Radio)
```

### WiFi / Bluetooth sniffing
```bash
# Le matériel RTL-SDR ne monte pas assez haut pour 2.4 GHz
# Utiliser HackRF ou LimeSDR
# WiFi : bandes 2.4 GHz et 5 GHz
# Bluetooth : 2.402 – 2.480 GHz
```

### ADS-B — Surveillance aérienne
```bash
# Lancer le décodeur
dump1090 --interactive --net --aggressive

# Interface web : http://localhost:8080
# Données : position, altitude, vitesse, cap, indicatif
```

### POCSAG / FLEX (pagers)
```bash
# Fréquences pagers France : 466 MHz
rtl_fm -f 466.075M -s 22050 | multimon-ng -a POCSAG512 -a POCSAG1200 -a POCSAG2400 -a FLEX -t raw -
```

---

## 9. Analyse de signaux

```bash
# Spectrogramme depuis un fichier IQ
sox -r 2000000 capture.iq -n spectrogram -o spectro.png

# Analyse avec inspectrum (GUI)
inspectrum capture.iq

# Universal Radio Hacker (analyse + génération de signaux)
# https://github.com/jopohl/urh
sudo apt install urh
```

---

## Cheatsheet rapide

```bash
# Tester le matériel
rtl_test

# Scanner les fréquences FM
rtl_power -f 88M:108M:100k scan.csv

# Capturer 433 MHz (télécommandes)
rtl_sdr -f 433920000 -s 2048000 capture.iq

# Capturer + rejouer (HackRF)
hackrf_transfer -r capture.iq -f 433920000 -s 8000000
hackrf_transfer -t capture.iq -f 433920000 -s 8000000 -x 40

# ADS-B aviation
dump1090 --interactive --net

# GUI
gqrx
gnuradio-companion
```

## Ressources
- **RTL-SDR Blog** : https://www.rtl-sdr.com
- **Signal Identification Wiki** : https://www.sigidwiki.com
- **RadioReference DB** : https://www.radioreference.com
- **GNU Radio Tutorials** : https://wiki.gnuradio.org
