---
name: wireless-networking-advanced
description: Guide complet des réseaux sans-fil — WiFi 6/6E/7 (802.11ax/be), contrôleurs WLC, mesh, roaming fast (802.11r/k/v), sécurité (WPA3, 802.1X, RADIUS), site survey, QoS (WMM), antennes et dimensionnement.
tags: [wifi, wireless, 802-11, wifi6, wifi7, 802-11ax, 802-11be, wlc, wpa3, mesh, roaming, radio, site-survey, wmm]
---

# Réseaux Sans-Fil Avancés — WiFi 6/6E/7

## Présentation

Guide complet des technologies WiFi modernes : standards 802.11, architecture contrôleur/autonome, sécurité sans-fil, roaming, QoS, dimensionnement radio, et troubleshooting.

### Évolution des Standards WiFi

```
802.11b  (1999)  — 11 Mbps, 2.4 GHz
802.11a  (1999)  — 54 Mbps, 5 GHz
802.11g  (2003)  — 54 Mbps, 2.4 GHz
802.11n  (2009)  — WiFi 4: 600 Mbps, MIMO 4x4, 2.4+5 GHz
802.11ac (2013)  — WiFi 5: 6.9 Gbps, MU-MIMO DL, 5 GHz
802.11ax (2019)  — WiFi 6: 9.6 Gbps, OFDMA, MU-MIMO UL/DL, 2.4+5 GHz
802.11ax (2021)  — WiFi 6E: Extension 6 GHz
802.11be (2024)  — WiFi 7: 46 Gbps, 320 MHz, 4096-QAM, MLO
```

---

## WiFi 6/6E (802.11ax)

### Caractéristiques Techniques

| Technologie | WiFi 5 (ac) | WiFi 6 (ax) | WiFi 6E | WiFi 7 (be) |
|-------------|-------------|-------------|---------|-------------|
| Bande | 5 GHz | 2.4 + 5 GHz | +6 GHz | 2.4 + 5 + 6 GHz |
| Modulation | 256-QAM | 1024-QAM | 1024-QAM | 4096-QAM |
| OFDM | OFDM | OFDMA | OFDMA | OFDMA + MLO |
| MU-MIMO | DL (4x4) | UL+DL (8x8) | UL+DL (8x8) | 16x16 |
| Channel | 80/160 MHz | 80/160 MHz | 80/160 MHz | 80/160/320 MHz |
| Spatial streams | 4 | 8 | 8 | 16 |
| Target Wake Time | — | Oui | Oui | Oui |
| BSS Coloring | — | Oui | Oui | Oui |

### OFDMA vs OFDM

```text
OFDM (WiFi 5) — Un seul utilisateur par trame
┌─────────────────────────────────────────┐
│   Frame complète = 1 utilisateur        │
├─────────────────────────────────────────┤
│ Utilisateur 1 (toute la bande)          │
└─────────────────────────────────────────┘

OFDMA (WiFi 6) — Utilisateurs multiplexés
┌─────────────────────────────────────────┐
│ RU1 │ RU2 │ RU3 │ RU4 │ RU5 │ RU6 │ RU7  │
├─────┼─────┼─────┼─────┼─────┼─────┼──────┤
│ U1  │ U1  │ U2  │ U3  │ U4  │ U4  │ U5   │
└─────────────────────────────────────────┘
Resource Units (RU) = 26, 52, 106, 242, 484, 996 tones
```

### BSS Coloring (802.11ax)

```text
Essence : Marquer chaque trame avec une couleur (BSS Color)
pour identifier son appartenance à un AP, réduisant les
interférences entre BSS voisins.

Avant WiFi 6 :
  AP1 (Canal 36) ──┬── Trame ── Client AP1 ── Reçu
  AP2 (Canal 36) ──┘                       ── Attente (CAC)

Après WiFi 6 (BSS Coloring) :
  AP1 (Color=1) ──┬── Trame ── Client AP1 (Color=1) → Pas de CAC
  AP2 (Color=2) ──┘                        → Ignoré (couleur≠)
```

### Target Wake Time (TWT)

```text
TWT = Planification des réveils clients pour économiser batterie

┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
│Veille│    │Wake │    │Veille│    │Wake │
│ 1.28s│───>│10ms │───>│ 1.28s│───>│10ms │
└─────┘    └─────┘    └─────┘    └─────┘
   ↑          ↑          ↑          ↑
   └── TWT ───┘── TWT ───┘── TWT ───┘
   (intervalle négocié avec l'AP)
```

---

## WiFi 7 (802.11be) — Nouveautés

### Multi-Link Operation (MLO)

```text
MLO = Utilisation simultanée de plusieurs bandes

┌──────────────────────────────────────────────┐
│ Client WiFi 7                                │
├──────────┬──────────────────┬────────────────┤
│ 2.4 GHz  │ 5 GHz            │ 6 GHz          │
│ (20/40)  │ (40/80/160)      │ (80/160/320)   │
├──────────┼──────────────────┼────────────────┤
│  ┌────┐  │  ┌────┐  ┌────┐ │  ┌────┐  ┌────┐│
│  │STR │  │  │STR │  │STR │ │  │STR │  │STR ││
│  └────┘  │  └────┘  └────┘ │  └────┘  └────┘│
└──────────┴──────────────────┴────────────────┘
    3 liens simultanés = x3 throughput, x3 fiabilité
```

### 320 MHz Channels + 4096-QAM

```text
Canaux 320 MHz (6 GHz uniquement) :
┌────────────────────────────────────────────────┐
│ Canal 320 MHz = 4 x 80 MHz = 2 x 160 MHz      │
├─────────┬─────────┬─────────┬──────────────────┤
│  80 MHz  │  80 MHz  │  80 MHz  │  80 MHz        │
│  (e.g.  │  (e.g.  │  (e.g.  │  (e.g.          │
│   64125) │   64205) │   64285) │   64365)       │
└─────────┴─────────┴─────────┴──────────────────┘

4096-QAM = 12 bits par symbole (vs 10 bits en 1024-QAM)
  → +20% de débit dans le même canal
  → Nécessite SNR > 35 dB
```

### Preamble Puncturing (WiFi 7)

```text
Gestion des canaux partiellement occupés :

Sans Puncturing :
┌─────────┬─────────┬─────────┬─────────┐
│  Canal  |  OCCUPE │  Libre  │  Libre  │  → Pas de transmission
│  160 MHz│         │         │         │
└─────────┴─────────┴─────────┴─────────┘

Avec Puncturing :
┌─────────┬─────────┬─────────┬─────────┐
│  Cana    |  PUNCTURE│  Transm │  Transm │  → Transmission
│  160 MHz│         │         │         │     partielle OK
└─────────┴─────────┴─────────┴─────────┘
```

---

## Architecture Contrôleur WiFi (WLC)

### Architecture Cisco WLC

```text
                      +-----------+
                      |   WLC     |
                      | (Contrôleur|)
                      +-----+-----+
                            |
              +-------------+-------------+
              |             |             |
        +-----v-----+ +-----v-----+ +-----v-----+
        |   AP-1    | |   AP-2    | |   AP-3    |
        | (LWAPP/   | | (CAPWAP)  | |           |
        |  CAPWAP)  | |           | |           |
        +-----------+ +-----------+ +-----------+
              |             |             |
          [Clients]    [Clients]    [Clients]
```

### Modes AP (Cisco)

```text
Local Mode (par défaut)
  ├── Tunnel CAPWAP vers WLC
  ├── Toutes les fonctions sur le WLC
  └── Scanning 10% du temps (RRM)

FlexConnect Mode (Remote)
  ├── Trafic local si WLC distant
  ├── Fonctionne en mode dégradé sans WLC
  └── Connect & Ack (synchronisation périodique)

Monitor Mode (IDS/IPS)
  ├── Pas de trafic client
  ├── Scanning continu (tous canaux)
  └── Detection de Rogue APs

Sniffer Mode
  ├── Capture de paquets vers un serveur
  └── Utilisé pour debugging RF

Bridge Mode (Mesh)
  ├── Point-to-point ou point-to-multipoint
  └── Backhaul sans-fil vers AP parent
```

### Configuration Cisco WLC

```bash
# CLI Cisco WLC (via SSH ou console)
> config wlan create 1 "EVA-Corp" "corp-ssid"
> config wlan security wpa akm dot1x enable 1
> config wlan radius server add 1 192.168.100.10 1812 "radius_secret"
> config wlan radius acct add 1 192.168.100.10 1813 "radius_secret"
> config wlan ccx aironet-ie disable 1
> config wlan enable 1

# RRM (Radio Resource Management)
> config advanced 802.11a channel auto
> config advanced 802.11a txpower auto
> config advanced 802.11a coverage channel-mgmt enable

# RRM thresholds
> config advanced 802.11a coverage voice-rssi-threshold -70
> config advanced 802.11a coverage data-rssi-threshold -80
> config advanced 802.11a profile noise-interference enable

# Fast Roaming
> config wlan security mobility ft enable 1
> config wlan security mobility ft-reassociation-timeout 20

# Band Select (5 GHz prefer)
> config wlan band-select allow 1

# Client load balancing
> config advanced 802.11a load-balancing window 5
> config advanced 802.11a load-balancing denials 3

# Guest WLAN
> config wlan create 2 "EVA-Guest" "guest-ssid"
> config wlan security web-auth enable 2
> config wlan security web-auth redirect-url https://portal.example.com
> config wlan interface 2 guest-vlan
> config wlan limit 2 10000  # 10 Mbps limit per client
```

---

## Roaming et Mobilité

### Fast Roaming (802.11r/k/v)

```text
Roaming classique (Open Authentication) :
   Client → AP2 : Auth(Open) → Assoc Req → Assoc Resp → EAP(500ms)
   Total : ~500-1000ms (trop lent pour voix)

802.11r (Fast Transition) :
   Client → AP2 : FT-Auth → FT-Reassoc → 4-way handshake
   Total : ~20-50ms (utilise PMK caching)

802.11k (Neighbor Reports) :
   Client → AP1 : Demande liste des APs voisins
   AP1 → Client : Liste (canaux, RSSI, charges)
   Client → AP2 : Roaming optimisé (choisit meilleur AP)

802.11v (WNM - Wireless Network Management) :
   AP → Client : Recommande un AP cible pour roaming
   AP → Client : Recommande changement de bande (5→2.4 si trop loin)
```

### Configuration Fast Roaming (Cisco WLC)

```bash
# Activer 802.11r (Fast Transition)
config wlan security mobility ft enable 1
config wlan security mobility ft over-the-ds enable 1  # Over-the-DS (vs Air)

# Activer 802.11k
config wlan security neighbor-list enable 1
config advanced 802.11a neighbor-list enable

# Activer 802.11v
config wlan wnm enable 1
config wlan wnm bss-max-idle enable 1
config wlan wnm directed-multicast enable 1
config wlan wnm sleep-mode enable 1

# RSSI thresholds pour roaming
config advanced 802.11a voice-rssi-change-threshold 5
config advanced 802.11a txpower-rssi-change-threshold 10
```

### OKC (Opportunistic Key Caching)

```bash
# PMK Caching — roaming plus rapide sans 802.11r
config wlan security mobility pmk-cache enable 1
config wlan security mobility pmk-cache-timeout 600  # secondes
```

---

## Sécurité WiFi

### WPA3 (WiFi Protected Access 3)

```text
WPA3-Personal (SAE - Simultaneous Authentication of Equals)
  ├── Remplace PSK (WPA2-PSK)
  ├── Anti-dictionary attack (handshake impossible à cracker offline)
  ├── Forward secrecy (même si MDP connu, sessions passées protégées)
  └── 192-bit security mode

WPA3-Enterprise (suite 192-bit)
  ├── CNSA Suite (Commercial National Security Algorithm)
  ├── GCMP-256 (chiffrement)
  └── ECDHE + ECDSA (authentification)

OWE (Opportunistic Wireless Encryption) — "Enhanced Open"
  ├── Chiffrement pour réseaux ouverts (hotspots)
  ├── Pas de mot de passe mais chiffrement individuel
  └── RFC 8110

WiFi Enhanced Open (OWE + PMF)
  ├── PMF (Protected Management Frames) obligatoire
  └── Protection contre les attaques de déauthentification
```

### Configuration WPA3 (Cisco WLC)

```bash
# WPA3-Personal (SAE)
config wlan security wpa enable 1
config wlan security wpa wpa2 disable 1
config wlan security wpa wpa3 enable 1
config wlan security wpa wpa3 sae enable 1
config wlan security wpa wpa3 sae password "strong_password"
config wlan security pmf enable 1  # PMF=Required (1) ou Optional (0)

# WPA3-Enterprise 192-bit
config wlan security wpa enable 1
config wlan security wpa wpa2 disable 1
config wlan security wpa wpa3 enable 1
config wlan security wpa wpa3 11w 1  # PMF required
config wlan security wpa wpa3 ccmp256 enable 1
config wlan security wpa wpa3 gcmp256 enable 1
```

### RADIUS pour WiFi (FreeRADIUS)

```bash
# /etc/freeradius/3.0/clients.conf
client wlc-1 {
    ipaddr = 192.168.100.1
    secret = radius_secret
    shortname = wlc-corporate
    nas_type = cisco
}

# /etc/freeradius/3.0/mods-enabled/eap
eap {
    default_eap_type = peap
    timer_expire = 60
    ignore_unknown_eap_types = no
    tls-config tls-common {
        private_key_password = ""
        private_key_file = /etc/ssl/private/server.key
        certificate_file = /etc/ssl/certs/server.pem
        CA_file = /etc/ssl/certs/ca.pem
        dh_file = /etc/ssl/certs/dh.pem
        fragment_size = 1024
        include_length = yes
        check_crl = no
        cipher_list = "DEFAULT@STRENGTH"
    }
}

# /etc/freeradius/3.0/users
"alice" Cleartext-Password := "password"
    Tunnel-Type = VLAN,
    Tunnel-Medium-Type = IEEE-802,
    Tunnel-Private-Group-Id = "10",
    Idle-Timeout = 3600,
    Session-Timeout = 86400

# MAB (MAC Authentication Bypass) pour imprimantes/IP phones
# /etc/freeradius/3.0/clients.conf
client wlc-mab {
    ipaddr = 192.168.100.2
    secret = mab_secret
    nas_type = cisco
}
```

### Rogue AP Detection

```bash
# Cisco WLC — Rogue AP Detection
config rogue ap add 00:11:22:33:44:55
config rogue ap classification malcious 00:11:22:33:44:55
config rogue ap state containment 00:11:22:33:44:55 enable

# Active Rogue Detection
config advanced rogue ap-rssi-min -80
config advanced rogue ap-transmit-data enable
config advanced rogue ap-detection-report 60
config advanced rogue adhoc enable

# Auto-containment
config advanced rogue auto-contain enable
config advanced rogue auto-contain-client-count 5
```

---

## Site Survey et Dimensionnement

### Outils de Site Survey

```bash
# Ekahau HeatMapper (Windows)
# Télécharger : https://www.ekahau.com/products/ekahau-heatmapper/

# NetSpot (macOS/Windows)
# Analyse WiFi, heatmaps

# WiFi Explorer (macOS)
# Scan des réseaux, canaux, RSSI

# iperf sans-fil
iperf3 -c 10.0.1.10 -t 30 -P 4  # Test bande passante WiFi

# iPerf + WiFi
# Test UDP dédié pour évaluer pertes
iperf3 -c 10.0.1.10 -u -b 500M -t 30
```

### Calcul de Couverture

```bash
# Propagation en espace libre (Free Space Path Loss)
# FSPL(dB) = 20*log10(d) + 20*log10(f) + 32.44
# d = distance en km, f = fréquence en MHz

# Exemple: à 100m sur 5 GHz (5200 MHz)
# FSPL = 20*log10(0.1) + 20*log10(5200) + 32.44
#      = -20 + 74.32 + 32.44 = 86.76 dB

# Budget de liaison (Link Budget)
# TX Power: 20 dBm (100 mW)
# Antenna Gain: 6 dBi
# RX Sensitivity: -85 dBm (6 Mbps)
# Marge: 10 dB
#
# Budget = 20 + 6 - 86.76 + 6 - 10 = -64.76 dBm
# → Excellent signal (< -67 dBm)
```

### Recommandations de Densité

```text
Par AP (point d'accès WiFi 6, 4x4:4) :
  Clients légers (IoT, capteurs) : 100-150 clients
  Clients normaux (navigation)   : 50-80 clients
  Clients voix (VoWiFi)          : 15-25 clients
  Streaming vidéo HD             : 10-15 clients

Espacement des APs :
  Bureaux ouverts     : 12-15m
  Bureaux fermés      : 15-20m
  Entrepôts           : 20-25m
  Auditorium/salle    : 8-10m (densité élevée)

Seuils RSSI recommandés :
  -65 dBm : Voix/Vidéo (haute qualité)
  -67 dBm : Données nominales
  -70 dBm : Bord de cellule acceptable
  -75 dBm : Roaming déclenché
  -80 dBm : Perte de connectivité probable
```

### Canaux Recommandés

```text
2.4 GHz (bande encombrée) :
  Canaux : 1, 6, 11 (non-overlapping only)
  Largeur : 20 MHz seulement (pas de HT40 en 2.4 GHz)

5 GHz (bande principale) :
  Canaux : 36, 40, 44, 48 (UNII-1, indoor)
           52, 56, 60, 64 (UNII-2, DFS)
           100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140 (UNII-2e, DFS)
           149, 153, 157, 161, 165 (UNII-3, outdoor)
  Largeur : 80 MHz recommandé (160 MHz si DFS activé)

6 GHz (WiFi 6E/7, propre) :
  Canaux : 64125, 64285, 64365 (80 MHz)
           64125-64285 (160 MHz), 64285-64365 (160 MHz)
  Largeur : 160 MHz recommandé (320 MHz en WiFi 7)
  Pas de DFS, pas de radar
```

---

## QoS — WMM (WiFi Multimedia)

### Configuration WMM (Cisco WLC)

```bash
# Activer WMM sur un WLAN
config wlan wmm enable 1
config wlan wmm allow 1   # Allow U-APSD (battery saving)

# QoS Profiles
config qos create voice platinum
config qos voice-platinum bandwidth 20  # Mbps

config qos create video gold
config qos video-gold bandwidth 50

config qos create data-silver silver
config qos data-silver bandwidth 100

# Appliquer QoS aux WLANs
config qos wlan 1 average-data-rate 100000  # 100 Mbps
config qos wlan 1 burst-data-rate 200000    # 200 Mbps burst
config qos wlan 1 average-real-time-rate 20000  # 20 Mbps voix/video
config qos wlan 1 burst-real-time-rate 50000
```

### Classification QoS WiFi

```text
Classification 802.11e/WMM :
┌──────────────┬──────────────┬──────┬────────────┐
│ Access Class │ Applications │ DSCP │ 802.1p     │
├──────────────┼──────────────┼──────┼────────────┤
│ AC_VO (Voix) │ VoIP, conf   │ EF   │ 5 (101)    │
│ AC_VI (Video)│ Streaming    │ AF41 │ 4 (100)    │
│ AC_BE (Best) │ Navigation   │ DF   │ 0 (000)    │
│ AC_BK (Back) │ P2P, batch   │ AF11 │ 1 (001)    │
└──────────────┴──────────────┴──────┴────────────┘
```

---

## Troubleshooting WiFi

### Commandes CLI AP/WLC

```bash
# Cisco WLC — Diagnostic
> show ap summary
> show ap config general AP-01
> show ap stats ap AP-01

# Client
> show client summary
> show client detail <MAC>
> show client stats <MAC>

# RF & Radio
> show advanced 802.11a channel
> show advanced 802.11a txpower
> show ap auto-rf 802.11a
> show ap stats | include "Noise|Interference|Utilization"

# Roaming
> show client detail <MAC> | include "Roam"
> show ap stats ap AP-01 | include "Client Assoc"

# Rogue APs
> show rogue ap summary
> show rogue ap detail <BSSID>

# Interference
> show ap interference 802.11a AP-01
> show airtime-fairness stats AP-01
```

### Analyse WiFi avec tcpdump

```bash
# Capture 802.11 (mode monitor)
ip link set wlan0 down
iw dev wlan0 set type monitor
ip link set wlan0 up

# Capture trames WiFi
tcpdump -i wlan0 -nn -e -s 0 -w wifi-capture.pcap

# Filtrer uniquement les management frames
tcpdump -i wlan0 -nn subtype probe-req or probe-resp
tcpdump -i wlan0 -nn subtype auth or assoc-req

# Filtrer par BSSID
tcpdump -i wlan0 -nn ether host 00:11:22:33:44:55

# Analyser les déauthentications (attaque)
tcpdump -i wlan0 -nn subtype deauth
tcpdump -i wlan0 -nn 'type mgt subtype deauth' | wc -l

# Beacon frames (APs visibles)
tcpdump -i wlan0 -nn -e -s 0 subtype beacon | grep -oP 'SSID: \K[^)]+' | sort -u

# Afficher les canaux
iwlist wlan0 scan | grep -E "Channel|ESSID|Signal"
```

### iw et iwconfig

```bash
# Voir les interfaces WiFi
iw dev

# Scan des réseaux
iw wlan0 scan | grep -E "SSID|freq|signal|channel"

# Se connecter à un réseau (wpa_supplicant)
wpa_passphrase "MonSSID" "motdepasse" > /etc/wpa_supplicant/wpa.conf
wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa.conf

# Statistiques d'interface
iw dev wlan0 link
iw dev wlan0 station dump
iw dev wlan0 survey dump

# Channel utilization
iw dev wlan0 survey dump | grep -A5 "in use"

# Force channel
iw dev wlan0 set channel 36 HT40+

# Taux de transmission
iw dev wlan0 set bitrates legacy-2.4 54

# Signal qualité en temps réel
watch -n 1 "iw dev wlan0 link"
```

---

## Pièges et Bonnes Pratiques

- **DFS** : Éviter les canaux DFS si possible (radar → AP change de canal → coupure)
- **2.4 GHz** : Utiliser seulement pour IoT/legacy, 5/6 GHz pour tout le reste
- **Channel overlap** : Jamais 40 MHz en 2.4 GHz (trop d'interférences)
- **Power levels** : Ajuster pour que les cellules se chevauchent à -67 dBm (roaming)
- **Band steering** : Toujours activer pour pousser les clients 5 GHz capables vers 5 GHz
- **PMF** : Activer Protected Management Frames pour contrer les déauthentications
- **PSK** : Ne plus utiliser WPA2-PSK (faible), migrer vers WPA3-SAE ou 802.1X
- **Monitoring** : Mettre en place un système de monitoring continue (Prime Infrastructure, Ekahau)

## Ressources

- WiFi Alliance : https://www.wi-fi.org/
- Cisco WLC Guide : https://www.cisco.com/c/en/us/support/wireless/wireless-lan-controller-software/products-installation-and-configuration-guides-list.html
- 802.11ax Whitepaper (Cisco) : https://www.cisco.com/c/en/us/products/collateral/wireless/white-paper-c11-740788.html
- 802.11be (WiFi 7) Overview : https://www.wi-fi.org/discover-wi-fi/wi-fi-7
- Ekahau : https://www.ekahau.com/
- Wireshark WiFi Analysis : https://wiki.wireshark.org/Wi-Fi
- FreeRADIUS WiFi Auth : https://wiki.freeradius.org/guide/HotSpot-with-Mikrotik-and-WiFi