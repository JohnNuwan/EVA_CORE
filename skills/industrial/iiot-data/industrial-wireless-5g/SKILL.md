---
name: industrial-wireless-5g
description: "Concevoir des réseaux sans fil industriels incluant 5G privée, Wi-Fi 6E et WirelessHART."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - 5g-private
      - wi-fi-6e
      - wirelesshart
      - isa-100
      - 5g-lan
      - tsn-wireless
      - industrial-wireless
      - private-network
      - iot-lpwan
      - lorawan
      - lte-m
    related_skills:
      - industrial-networks-ot
      - industrial-network-design
      - sparkplug-b
      - industrial-edge
---

# Réseaux Sans Fil Industriels et 5G Privée

## Vue d'ensemble

Cette compétence couvre les technologies sans fil modernes pour l'industrie :
- **5G privée (3GPP R16/R17)** — Faible latence (uRLLC), slicing, MEC
- **Wi-Fi 6E / 7** — Haute capacité, roaming rapide, 6 GHz
- **WirelessHART / ISA-100** — Réseaux mesh capteurs process
- **LPWAN** — LoRaWAN, NB-IoT, LTE-M pour IoT longue distance

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir un réseau 5G privé pour AGV/AMR ou mobile panels
- De dimensionner un réseau Wi-Fi 6E pour une ligne de production
- De déployer WirelessHART pour des capteurs sans fil
- De configurer un MEC (Multi-access Edge Computing)
- De faire un audit de couverture RF industrielle

---

## 1. 5G Privée (3GPP R16/R17)

### 1.1 Architecture

```
┌──────────────────────────────────────────────────┐
│                    5GC (5G Core)                  │
│  ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │ UPF (User  │ │ AMF/SMF    │ │ PCF/AUSF     │  │
│  │ Plane Fn)  │ │ Control    │ │ Auth/POLICY  │  │
│  └─────┬──────┘ └────────────┘ └──────────────┘  │
│        │              ┌────────────┐              │
│        │              │ MEC Edge   │              │
│        │              │ (Applications) │          │
│        │              └────────────┘              │
└────────┼────────────────────┬─────────────────────┘
         │ N3 interface       │
    ┌────┴────┐          ┌────┴────┐
    │  gNB    │          │  gNB    │
    │  CU/DU  │          │  CU/DU  │
    └────┬────┘          └────┬────┘
   ┌─────┼─────────────────────┼──────┐
   │ ┌───┴───┐          ┌────┴────┐  │
   │ │ AGV   │          │ Mobile  │  │
   │ │ (UE)  │          │ Panel   │  │
   │ └───────┘          └─────────┘  │
   │        Factory Floor           │
   └──────────────────────────────────┘
```

### 1.2 Network Slicing

| Slice | URLLC | eMBB | mMTC |
|:------|:------|:-----|:-----|
| Application | Motion ctrl, safety | Vidéo, AR/VR | Capteurs, tracking |
| Latence | < 1 ms | 10-20 ms | 50-100 ms |
| Débit | 100 Mbps | 10 Gbps | 100 kbps |
| Densité | 10^5/km² | 10^4/km² | 10^6/km² |
| S-NSSAI (SST) | SST=2 (URLLC) | SST=1 (eMBB) | SST=3 (mIoT) |

### 1.3 5G-LAN (TSN over 5G)

La 5G peut étendre les réseaux TSN (Time-Sensitive Networking) au sans fil :
- IEEE 802.1AS (gPTP) synchronisation horaire < 1 µs
- IEEE 802.1Qbv (Time-Aware Shaper) au niveau 5G
- 5G TSN Translators (TT) pour pont TSN physique ↔ sans fil
- Stream Identification et QoS Flow granularité 5G

---

## 2. Wi-Fi 6E / 7 pour l'Industrie

| Caractéristique | Wi-Fi 6 (ax) | Wi-Fi 6E (ax) | Wi-Fi 7 (be) |
|:----------------|:-------------|:--------------|:-------------|
| Bande | 2.4/5 GHz | Ajout 6 GHz | 2.4/5/6 GHz |
| Canaux | 20/40/80 MHz | 160 MHz | 320 MHz |
| OFDMA | Oui | Oui | Oui |
| MU-MIMO | DL | DL+UL | DL+UL + Multi-RU |
| Roaming rapide (802.11r/k/v) | Oui | Oui | Oui + 802.11be EMLSR |
| Latence typique | 5-10 ms | 2-5 ms | < 1 ms |

---

## 3. WirelessHART / ISA-100

- **Topologie mesh** — Chaque appareil est routeur
- **Channel Hopping** — Sauts de fréquence (2.4 GHz, 16 canaux)
- **TDMA** — Time Division Multiple Access, slots garantis
- **TSMP** — Time Synchronized Mesh Protocol
- **Coexistence** — Wi-Fi, Bluetooth, ZigBee
- **Sécurité** — AES-128, keys rotation, join key

---

## 4. Références

- [3GPP Release 16/17](https://www.3gpp.org)
- [5G-ACIA Alliance](https://www.5g-acia.org)
- [WirelessHART (IEC 62591)](https://fieldcommgroup.org)
- [Wi-Fi Alliance 6E](https://www.wi-fi.org)
- [ISA-100.11a](https://www.isa.org)
- [GSMA 5G for Industry](https://www.gsma.com/5g)
