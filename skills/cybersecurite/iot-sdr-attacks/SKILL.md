---
name: iot-sdr-attacks
title: "SDR (Software-Defined Radio) — Attaques sans Fil"
description: "Guide complet pour l'utilisation de la radio logicielle (SDR) dans le cadre de l'audit de sécurité IoT. Couvre l'analyse de signaux, le reverse engineering de protocoles RF, l'attaque sur les liaisons radio ISM (433/868/915 MHz, 2.4 GHz), le déchiffrement de télécommandes, le jamming, la rejeu (replay), et la récupération de données télémétriques."
category: cybersecurite
---

# SDR (Software-Defined Radio) — Attaques sans Fil

## Vue d'Ensemble

La radio logicielle (SDR) permet d'émettre et de recevoir sur une large gamme de fréquences avec un matériel peu coûteux. Dans le contexte IoT, c'est l'outil central pour analyser, décoder, et attaquer les communications sans fil : télécommandes, capteurs, compteurs intelligents, badges, liaisons radio propriétaires.

### Objectifs
- Capturer et analyser des signaux RF (OOK, FSK, GFSK, LoRa, MSK)
- Reverse engineer des protocoles radio propriétaires
- Rejouer des trames (replay attack)
- Décoder des télécommandes de garage/volet/porte
- Intercepter des données télémétriques (capteurs, compteurs)
- Attaquer des systèmes de contrôle sans fil (KEELOQ, Hopping)
- Bypasser des systèmes anti-rejeu (rolling code)

---

## Outils Essentiels

### Hardware SDR
| Matériel | Bande | Prix | Usage |
|----------|-------|------|-------|
| **RTL-SDR (R820T2)** | 24MHz-1.7GHz | ~$25 | Réception seule, entrée de gamme |
| **HackRF One** | 1MHz-6GHz | ~$350 | Émission + réception, 20Msps |
| **LimeSDR** | 100k-3.8GHz | ~$300 | Full duplex, FPGA |
| **BladeRF 2.0** | 47MHz-6GHz | ~$650 | Large bande, 61.44Msps |
| **ADALM-PLUTO** | 325MHz-3.8GHz | ~$200 | Éducation, portable |
| **USRP B210** | 70MHz-6GHz | ~$1500 | Pro, haute performance |
| **YardStick One** | 300-928MHz | ~$200 | Réception + émission ISM |
| **FLipper Zero** | Sub-1GHz, RFID, NFC, BT | ~$200 | Multi-protocole portable |

### Antennes
| Type | Usage |
|------|-------|
| Dipôle (1/4λ, 1/2λ) | Usage général, fréquence spécifique |
| Log-périodique | Large bande, directionnelle |
| Yagi | Haute directivité, longue portée |
| PCB / Patch | Intégré, compact |
| Loop magnétique | Proximité, décodage champ proche |
| Antenne active (LNA) | Signaux faibles, préamplifié |

### Logiciels
| Outil | Usage |
|-------|-------|
| **GNU Radio** | Traitement de signal, flowgraphs, décodage custom |
| **GQRX** | Analyse spectrale, réception FM/AM/SSB |
| **Universal Radio Hacker (URH)** | Analyse et décodage de protocoles (best tool IoT RF) |
| **rtl_433** | Décodage de capteurs IoT (433/868/915 MHz) |
| **Inspectrum** | Analyse de signaux bruts (waterfall, constellations) |
| **RFcat** | Prototypage rapide d'attaques RF (YardStick) |
| **gr-ieee802-11** | Décodage WiFi 802.11 (nécessite carte compatible) |
| **Wireshark** | Analyse de trames (BT, Zigbee, Z-Wave via adaptateur) |
| **FLipper Zero FW** | BadUSB, RFID, Sub-1GHz, iButton |
| **TempestSDR** | Capture d'émissions électromagnétiques d'écrans |

---

## Méthodologie

### Phase 1 : Reconnaissance du Spectre

```bash
# 1. Lancement de GQRX
gqrx &

# 2. Scanner les bandes ISM populaires
#    - 315 MHz (télécommandes asiatiques)
#    - 433.05-434.79 MHz (télécommandes, capteurs Europe)
#    - 868-870 MHz (ISM Europe, LoRa, Sigfox)
#    - 902-928 MHz (ISM US, Zigbee, Z-Wave)
#    - 2.400-2.4835 GHz (WiFi, BT, Zigbee)

# 3. Identifier le type de signal
#    - OOK (On-Off Keying) : impulsions visibles, télécommandes simples
#    - FSK (Frequency Shift) : sauts de fréquence, data modulée
#    - LoRa : chirp spread spectrum, SSB-like
#    - DSSS : bruit large bande (Zigbee, WiFi)

# 4. Capturer un échantillon (IQ file)
#    Dans GQRX : File → Save IQ
#    ou en CLI :
rtl_sdr capture.iq -f 433920000 -s 2500000 -n 10000000
```

### Phase 2 : Analyse avec Universal Radio Hacker (URH)

```bash
# URH est l'outil le plus puissant pour reverse engineering RF
pip3 install urh

# 1. Charger le fichier IQ
urh

# 2. Ouvrir le fichier .complex (IQ)
#    File → Open → capture.complex

# 3. Démodulation automatique
#    - URH détecte automatiquement OOK, FSK, PSK, ASK
#    - Ajuster les paramètres si nécessaire

# 4. Découpage en symboles
#    - Utiliser la vue "Project" pour définir les séquences
#    - Identifier les patterns : préambule, sync word, payload

# 5. Définition du protocole
#    - Bits → hex → interprétation
#    - Chercher des champs : ID, commande, checksum, rolling code

# 6. Interprétation des trames
#    - Appuyer sur la télécommande plusieurs fois
#    - Observer les différences entre les trames
#    - Identifier les champs fixes vs dynamiques (rolling code)
```

### Phase 3 : Replay Attack

```bash
# Si le protocole n'a pas d'anti-rejeu :
# 1. Capturer une trame valide (bouton appuyé)
# 2. La rejouer avec URH ou HackRF

# Avec URH :
# - Sélectionner la trame → "Send" → avec HackRF/USRP
# - Ou exporter en fichier binaire et rejouer

# Avec HackRF :
hackrf_transfer -r capture.cfile -f 433920000 -a 1 -x 40
# Réémission :
hackrf_transfer -t capture.cfile -f 433920000 -a 1 -x 40

# Avec rpitx (Raspberry Pi) :
# Simple émetteur sur GPIO
sudo rpitx -m RF -i capture.wav -f 433920000
```

### Phase 4 : Attaque sur Rolling Code (KEELOQ / Hopping)

```bash
# 1. Capturer plusieurs trames successives
#    Au moins 3-5 appuis sur le même bouton

# 2. Analyser le rolling code
#    - OUI à 48 bits de données
#     - ID du device (28 bits, fixe)
#     - Encrypted counter (16 bits, incrémente)
#     - Serial number (32 bits, fixe)
#     - Checksum / status

# 3. Si KEELOQ (Microchip) :
#    - Algorithme propriétaire, mais vulnérabilités connues
#    - Clé dérivée du serial number (souvent 000000h)
#    - Attaque : capturer + désynchroniser

# 4. Technique de désynchronisation :
#    - Bloquer le récepteur (jammer)
#    - Envoyer une trame capturée dans le futur
#    - Le récepteur avance son compteur
#    - La télécommande légitime est désynchronisée

# 5. Replay hopping codes :
#    - Certains protocoles (Somfy RTS) utilisent un
#      rolling code avec une crypto symétrique
#    - Attaque Known Answer : capturer + décoder via clé
#      trouvée (documentée, parfois brute-forcée)
```

---

## Techniques Avancées

### Jamming Sélectif
```bash
# Brouillage ciblé (ne pas interférer tout le spectre)
# Avec HackRF :
hackrf_sweep -f 433900000:434000000 -w 100000 -g 40

# Avec GNU Radio :
# Créer un flowgraph qui écoute et bloque SEULEMENT
# une fréquence spécifique (blanqueur sélectif)

# Jamming intelligent :
# 1. Écouter la fréquence cible
# 2. Détecter le début d'une trame (energy detection)
# 3. Bloquer immédiatement (~10µs de latence)
# → Désynchronisation efficace
```

### Décodage LoRa
```bash
# LoRa n'est pas déchiffrable sans clé réseau (AppKey/NwkKey)
# Mais on peut :
# 1. Démoduler le signal LoRa (CSS)
# 2. Extraire les métadonnées : SF, BW, CR, timestamp
# 3. Analyser le trafic : taille des trames, fréquence, puissance
# 4. Attaquer par rejeu si pas de counter/encryption

# Avec gr-lora (GNU Radio) :
# Installer le module OOT
# Créer un flowgraph pour démoduler LoRa
# Nécessite un SDR avec bonne sensibilité
```

### Reverse de Protocole Propriétaire
```bash
# 1. Capturer des trames dans différentes conditions
#    - Bouton A vs Bouton B
#    - Appui long vs Appui court
#    - Plusieurs devices (même modèle)
#    - Device A vs Device B (communication bidirectionnelle)

# 2. Analyser les patterns
#    - XOR avec un masque fixe ?
#    - Addition d'un compteur ?
#    - Données mélangées (interleaving) ?

# 3. Si crypto symétrique, chercher :
#    - Initialisation vector fixe
#    - Clé trouvable dans strings du firmware
#    - Algorithme identifiable par le format de la trame

# 4. Bruteforce partiel
#    - Si le rolling code est sur 16 bits : 65536 combinaisons
#    - Automatiser le test avec un SDR et un récepteur
```

### Tempest / Van Eck Phreaking
```bash
# Capturer les émissions EM d'un écran
# Avec TempestSDR :
# 1. Antenne directionnelle pointée vers l'écran
# 2. Syntoniser la fréquence de l'horloge pixel
# 3. Démoduler le signal vidéo
# 4. Reconstruire l'image de l'écran (VGA/DVI/HDMI)

# Utilité IoT : capturer l'affichage d'un terminal, d'une interface
```

---

## Pièges & ASTUCES

⚠️ **Légalité** : l'émission radio est régulée. Ne pas émettre sans licence sur des fréquences non ISM. Même sur ISM, respecter les limites de puissance
⚠️ **Antenne adaptée** : une antenne 433 MHz fonctionne mal à 868 MHz. Utiliser une antenne accordée ou large bande
⚠️ **Bruit de fond** : les environnements urbains sont saturés (WiFi, BT, micro-ondes). Préférer un endroit calme pour les captures
⚠️ **Gain** : trop de gain → saturation ADC → signaux déformés. Trop peu → signaux noyés dans le bruit
⚠️ **HackRF One full duplex** : non, half-duplex seulement (ne peut pas émettre et recevoir en même temps)
⚠️ **Dérive de quartz** : les RTL-SDR chauffent et dérivent en fréquence. Laisser chauffer 10 min avant les mesures précises
⚠️ **Sample rate** : 2 Msps (RTL-SDR) → bande passante de 2 MHz. Pour signaux > 2 MHz de large, besoin de HackRF (20 Msps)
⚠️ **Rolling code n'est pas inviolable** : certains protocoles ont des failles cryptographiques connues (KEELOQ, Megamos)
⚠️ **Flipper Zero Sub-GHz** : émission limitée à certaines fréquences selon la région (modifiable, mais illégal)

### Check-list Rapide
```bash
# 1. Identifier la fréquence (GQRX scanner)
# 2. Capturer un échantillon IQ
rtl_sdr -f 433920000 -s 2500000 capture.iq

# 3. Analyser avec URH
urh

# 4. Décoder les trames
# 5. Tester le replay
# 6. Si rolling code → capturer 5+ trames → analyser
```

---

## Références

- **Universal Radio Hacker** : https://github.com/jopohl/urh
- **GNU Radio** : https://www.gnuradio.org/
- **Great Scott Gadgets (HackRF)** : https://greatscottgadgets.com/hackrf/
- **RTL-SDR Blog** : https://www.rtl-sdr.com/
- **rpitx** : https://github.com/F5OEO/rpitx
- **gr-lora** : https://github.com/rpp0/gr-lora
- **KEELOQ Analysis** : https://www.cs.ox.ac.uk/people/andrew.paverd/lockdown/
- **Attacking IoT with SDR** : DEF CON / YouTube (LiveOverflow, Cybergibbons)
- **The Car Hacker's Handbook** : Craig Smith (RF section)