---
name: industrial-network-design
description: "Concevoir, dimensionner et diagnostiquer les réseaux Ethernet industriels."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags:
      - profinet
      - profinet-irt
      - profinet-rt
      - ethernet-ip
      - cip
      - modbus-tcp
      - profibus
      - network-design
      - ring-topology
      - dlr
      - mrp
      - lldp
      - snmp
      - industrial-switch
      - stratix
      - scalance
      - hirschmann
      - moxa
      - tsn
      - time-sensitive-networking
      - qos
      - vlan-industrial
      - iec-62443-3
      - cell-area-zone
      - ot-network
      - wireshark-industrial
      - industrial-firewall
    related_skills:
      - industrial-protocols
      - industrial-networks-ot
      - cybersecurity-iec62443
      - plc-connectivity
      - sparkplug-b
---

# Conception de Réseaux Industriels

## Vue d'ensemble

Les **réseaux Ethernet industriels** sont le système nerveux de l'usine connectée. Contrairement aux réseaux IT, ils imposent :

- **Déterminisme** — Latence bornée et répétable pour le contrôle
- **Redondance** — MRP, DLR, PRP, HSR pour une disponibilité continue
- **Robustesse** — EMI, température, vibrations, chocs
- **Sécurité** — Zones, conduits (IEC 62443-3), segmentation OT/IT
- **Convergence** — IT/OT convergence avec TSN et 5G privée

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir un réseau Ethernet pour une nouvelle usine ou ligne de production
- De diagnostiquer des problèmes de performance réseau (latence, perte de paquets)
- De configurer des switches industriels (Stratix, Scalance, Hirschmann, Moxa)
- De paramétrer des protocoles de redondance (MRP, DLR, PRP, HSR)
- De planifier des VLAN et QoS pour le trafic temps réel
- De configurer des pare-feux OT avec zones et conduits
- De capturer et analyser le trafic réseau industriel (Wireshark)

---

## 1. Protocoles Ethernet Industriels

### 1.1 PROFINET

**PROFINET RT** (Real-Time) — Latence typique < 1 ms

- **Standard RT** — Cycle 1–10 ms (TCP/IP stack)
- **IRT** (Isochronous Real-Time) — Cycle 31.25 µs–1 ms, matériel FPGA/ASIC
- **TSN-ready** — PROFINET over TSN (802.1Qbv, 802.1AS)

| PROFINET | RT (Real-Time) | IRT (Isochronous RT) |
|:---------|:---------------|:---------------------|
| Cycle time | ≥ 1 ms | ≥ 31.25 µs |
| Jitter | < 1 µs | < 1 µs |
| Application | Standard automation | Motion control, drives |
| Hardware | Switch standard | Switch+ASIC support |

**MRP** (Media Redundancy Protocol) — IEC 62439-2 :
- Topologie anneau, reconnexion < 200 ms
- MRM (Ring Manager) + MRC (Ring Client)
- Pour PROFINET RT uniquement (pas IRT)

```python
# Découverte PROFINET via DCP (Discovery and Configuration Protocol)
response = send_dcp_request(
    command="IDENTIFY_REQUEST",
    interface="eth0",
    timeout=2.0
)
devices = parse_dcp_response(response)
for device in devices:
    print(f"Device: {device['name']}, IP: {device['ip']}, MAC: {device['mac']}")
```

### 1.2 EtherNet/IP

**CIP** (Common Industrial Protocol) sur Ethernet :

- **Implicit messaging** — I/O data, cycle 1–50 ms, UDP (port 2222)
- **Explicit messaging** — Configuration/diagnostic, TCP (port 44818)
- **CIP Sync** — Precision Time Protocol (IEEE 1588) pour synchronisation
- **CIP Motion** — Drive synchronization over EtherNet/IP

**DLR** (Device Level Ring) — Redondance en anneau :
- Reconnexion < 3 ms (beacon-based)
- Compatible avec les switches non-manageables (anneau à base de superviseur)
- Supervisors (active/backup), participants, non-participants

```python
# Découverte EtherNet/IP via List Identity
identity = send_enip_command(
    command="LIST_IDENTITY",
    destination="192.168.1.100"
)
print(f"Vendor: {identity['vendor']}")
print(f"Device Type: {identity['device_type']}")
print(f"Serial: {identity['serial']}")
print(f"IP: {identity['ip']}")
```

### 1.3 Modbus TCP

- **Port** : 502
- **Pas de QoS natif** — Convient pour supervision non-temps réel
- **Topologies** : Étoile, ligne (avec switches non-manageables)
- **Performance** : Cycle 10–100 ms, pas de déterminisme garanti

### 1.4 PROFIBUS DP

- **RS-485** à 12 Mbps max
- **Topologie** : Bus linéaire avec répéteurs
- **Segment max** : 100 m à 12 Mbps, 1200 m à 93.75 kbps
- **Maître** (Classe 1 : contrôleur, Classe 2 : outil)
- **Esclaves** jusqu'à 126

---

## 2. Topologies Réseau

### 2.1 Étoile

```
         ┌──────────┐
         │  Switch   │
         │  Central  │
         └────┬─────┘
     ┌────────┼────────┐
     │        │        │
   PLC-1    PLC-2    HMI-1
```

**Avantages** : Simple, facile à diagnostiquer
**Inconvénients** : Point de défaillance unique
**Usage** : Petites cellules, îlots non-critiques

### 2.2 Anneau (Ring)

```
    PLC-1 ──── Switch1 ──── Switch2
      │                      │
      │                      │
    PLC-4 ──── Switch4 ──── Switch3
```

**Redondance** :
- **MRP** : ≤ 50 switches, reconnexion < 200 ms (PROFINET)
- **DLR** : ≤ 50 nœuds, reconnexion < 3 ms (EtherNet/IP)
- **RSTP** : IEEE 802.1w reconnexion < 2 s

### 2.3 Arbre (Tree)

```
              ┌────────┐
              │  Core   │
              └───┬────┘
         ┌────────┼────────┐
     ┌───┴───┐┌───┴───┐┌───┴───┐
     │Switch 1││Switch 2││Switch 3│
     └───────┘└───────┘└───────┘
```

### 2.4 PRP (Parallel Redundancy Protocol) — IEC 62439-3

```
       ┌────────────────┐
       │   LAN A (Eth)  │
   ┌───┴───┐        ┌───┴───┐
   │ DAN-A │────────│ DAN-B │
   └───┬───┘  PRP   └───┬───┘
       │   LAN B (Eth)   │
       └────────────────┘
```

- **Zero switchover** — Paquets dupliqués sur deux réseaux
- **Dan (Doubly Attached Node)** — Nœud avec deux interfaces

---

## 3. Conception d'Adressage IP et Segmentation

### 3.1 Plan d'adressage recommandé par cellule

| Segment | Plage IP | Usage |
|:--------|:---------|:------|
| Cell 1 – Automation | 10.50.1.0/24 | PLC, HMI, drives, I/O |
| Cell 1 – Supervision | 10.50.2.0/24 | SCADA, OPC, historiens |
| Cell 1 – Cameras | 10.50.10.0/24 | Vision, inspection |
| Cell 2 – Automation | 10.50.3.0/24 | PLC, HMI, drives, I/O |
| OT – Services | 10.50.250.0/24 | Engineering, DHCP, DNS |
| OT – DMZ | 10.50.254.0/24 | Historien bridges, firewall |
| IT – Corporate | 172.16.0.0/16 | Bureau, ERP, MES |

### 3.2 VLAN et QoS

#### VLAN recommandés par type de trafic :

| VLAN ID | Type | Priorité DSCP | Priorité 802.1p |
|:--------|:-----|:--------------|:----------------|
| 10 | Automation (PROFINET RT/IRT) | CS6 (48) | 6 |
| 20 | I/O (EtherNet/IP implicit) | CS5 (40) | 5 |
| 30 | Motion (CIP Sync) | CS6 (48) | 6 |
| 40 | Supervision / HMI | CS3 (24) | 3 |
| 50 | Engineering / OPC | CS2 (16) | 2 |
| 99 | IT / Corporate | — | 0 |

```python
# Exemple de configuration VLAN sur un switch Stratix
switch.configure_vlan(vlan_id=10, name="AUTOMATION", qos_cos=6)
switch.configure_vlan(vlan_id=20, name="SUPERVISION", qos_cos=3)
switch.configure_trunk(interface="Gi1/1", allowed_vlans=[10, 20, 99], native_vlan=99)
switch.configure_access(interface="Gi1/2", vlan=10)
```

### 3.3 Cell/Area Zones (IEC 62443-3-2)

```
┌────────────────────── IT Enterprise ──────────────────────┐
│  [Zone IT] — ERP, MES, Email, Web                          │
├────────────────────── DMZ ─────────────────────────────────┤
│  [Conduit] — Reverse proxy, Historian bridge, AD sync      │
├────────────────────── OT Zones ────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ Zone Cell 1      │  │ Zone Cell 2      │               │
│  │ - PLC (S7-1500)  │  │ - PLC (Compact)  │               │
│  │ - HMI (WinCC)    │  │ - HMI            │               │
│  │ - Drives         │  │ - Drives         │               │
│  │ - Vision system  │  │ - Robot (KUKA)   │               │
│  └──────────────────┘  └──────────────────┘               │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Zone Services (Engineering)                        │   │
│  │ - Engineering workstations                         │   │
│  │ - TIA Portal / Studio 5000                         │   │
│  │ - OPC UA clients                                   │   │
│  └────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

---

## 4. Switching Industriel

### 4.1 Constructeurs et gammes

| Constructeur | Gamme | Redondance | Environnement |
|:-------------|:------|:-----------|:--------------|
| **Cisco Stratix** | 5400, 5700, 5900 | DLR, RSTP, MRP | Industriel (-40 à +60 °C) |
| **Siemens Scalance** | XC-200, XR-300, XM-400 | MRP, RSTP, PRP | Industriel |
| **Hirschmann** | MACH, BOBCAT, OCTOPUS | MRP, RSTP, HIPER-Ring | Industriel, ferroviaire |
| **Moxa** | EDS-G, MDS-G, TN | MRP, RSTP, Turbo Ring | Industriel |

### 4.2 Configuration typique Scalance

```python
# Configuration Scalance XC-200 via CLI
scalance.configure_interface(name="Port 1.1", mode="trunk", native_vlan=1)
scalance.configure_mrp(role="manager", vlan=1, timeout=200)
scalance.configure_vlan(vlan_id=10, name="PROFINET_IO")
scalance.configure_vlan(vlan_id=20, name="HMI")
scalance.configure_profinet(role="switch", domain="cell-01")
```

### 4.3 VLAN et sécurité portuaire

```python
# Mesures de sécurité de base (IEC 62443-4-2)
switch.configure_port_security(
    interface="Gi1/1",
    max_mac=1,
    violation="shutdown",
    sticky_mac=True
)
switch.configure_dhcp_snooping(vlan=[10, 20, 30])
switch.configure_dynamic_arp_inspection(vlan=[10, 20, 30])
switch.configure_ip_source_guard(vlan=[10, 20, 30])
```

---

## 5. TSN (Time-Sensitive Networking)

TSN est l'avenir des réseaux industriels convergents. Standards clés :

| Standard IEEE | Nom | Fonction |
|:--------------|:----|:---------|
| **802.1AS** | gPTP | Synchronisation horaire < 1 µs |
| **802.1Qbv** | TAS | Time-Aware Shaper, fenêtres dédiées trafic temps réel |
| **802.1Qbu/802.3br** | Frame Preemption | Interruption paquets longs pour priorité trafic temps réel |
| **802.1CB** | Seamless Redundancy | Duplication de paquets, zéro perte |
| **802.1Qci** | PSFP | Filtrage et police par flux |
| **802.1Qcc** | CUC/UCC | Configuration centralisée des flux TSN |

```python
# Configuration TSN simplifiée
tsn_config = {
    "gate": {
        "open_windows": [
            {"start": 0, "duration_us": 500, "traffic_class": "time_critical"},
            {"start": 500, "duration_us": 9500, "traffic_class": "best_effort"}
        ],
        "cycle_time_us": 10000
    },
    "synchronization": {
        "domain": 0,
        "priority": 128,
        "sync_interval_ms": 125
    },
    "streams": [
        {"id": "PROFINET_IRT", "vlan": 10, "max_latency_us": 100},
        {"id": "CIP_MOTION", "vlan": 30, "max_latency_us": 50}
    ]
}
```

---

## 6. Diagnostic Réseau (Wireshark)

### 6.1 Filtres Wireshark pour réseaux industriels

```wireshark
# PROFINET
profinet
profinet.dce.suboption == 0x02   # DCP Identify
profinet.rt.frameid == 0x8000    # RT Cyclic data

# EtherNet/IP
enip
enip.cpf.vendor_id == 0x00E1     # Rockwell
enip.command == 0x0063           # List Identity

# Modbus TCP
modbus.tcp
modbus.func_code == 0x03         # Read Holding Registers
modbus.func_code == 0x10         # Write Multiple Registers

# Contrôle qualité
tcp.analysis.flags                # Problèmes TCP (retransmission, dup, window)
icmp || icmpv6                    # Ping / problèmes de connectivité
```

### 6.2 Métriques de performance

```python
# Analyse de capture réseau pour latence PROFINET
capture = read_pcap("network_trace.pcapng")
stats = {
    "min_latency_us": capture.filter("profinet.rt").min_latency(),
    "max_latency_us": capture.filter("profinet.rt").max_latency(),
    "avg_latency_us": capture.filter("profinet.rt").avg_latency(),
    "jitter_us": capture.filter("profinet.rt").jitter(),
    "packet_loss_pct": capture.packet_loss_rate(),
    "ring_recovery_ms": capture.filter("mrp").ring_recovery_time(),
    "top_errors": ["TCP Retransmissions", "CRC Errors", "Late Collisions"],
}
```

---

## 7. Références

- [IEC 62443-3-2 Security Zones and Conduits](https://www.isa.org/standards-and-publications/isa-standards/isa-62443-series-standards)
- [PROFINET System Description (PI)](https://www.profibus.com/technology/profinet)
- [EtherNet/IP CIP Specification (ODVA)](https://www.odva.org/technology/ethernetip)
- [IEEE 802.1 TSN Task Group](https://1.ieee802.org/tsn/)
- [Cisco / Rockwell Stratix Configuration Guides](https://www.cisco.com/c/en/us/support/switches/stratix-5400-industrial-ethernet-switches)
- [Siemens Scalance Configuration Manuals](https://support.industry.siemens.com/scalance)
- [Hirschmann Networking Guides (Belden)](https://www.belden.com/hirschmann)
- [IEC 62439-3 PRP/HSR Redundancy](https://www.iec.ch)
