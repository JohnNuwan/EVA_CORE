---
name: ot-incident-response
description: "Répondre aux incidents de cybersécurité dans les environnements OT industriels."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - ot-incident-response
      - dfir-ot
      - iec-62443
      - mitre-attack-ics
      - forensics-ot
      - malware-ics
      - ransomware-ot
      - industrial-firewall
      - ot-security
      - forensics-plc
      - ot-soc
      - incident-response
      - disaster-recovery
      - threat-hunting
    related_skills:
      - cybersecurity-iec62443
      - industrial-risk-analysis-hazop
      - ot-audit
      - industrial-network-design
---

# Réponse à Incident Cybersécurité OT

## Vue d'ensemble

La **réponse à incident OT** diffère fondamentalement de l'IT : la disponibilité prime sur l'intégrité/confidentialité, les correctifs sont rares, et les conséquences peuvent être physiques (sécurité des personnes, arrêt production, dommages équipements).

Cette compétence couvre : MITRE ATT&CK ICS, collection de preuves OT, forensique PLC/DCS, containment d'urgence, remédiation, et post-incident.

## Quand l'utiliser

À utiliser lors de : suspicion de compromission OT, alerte SIEM industrielle, ransomware dans l'usine, incident de sécurité sur automate, investigation forensique OT, plan de reprise après incident OT.

---

## 1. MITRE ATT&CK for ICS

### 1.1 Tactiques principales

| Tactique | Description | Exemples techniques |
|:---------|:------------|:-------------------|
| TA0107 | **Initial Access** | Ingénierie sociale, VPN OT, clé USB, modem |
| TA0108 | **Execution** | Malware (Triton, Industroyer), scripts engineering |
| TA0109 | **Persistence** | Firmware modifié, user account, stub files |
| TA0110 | **Evasion** | Masquerade, process injection, rootkit PLC |
| TA0111 | **Discovery** | Network scan OT, engineering workstation recon |
| TA0104 | **Lateral Movement** | S7 protocol abuse, OPC UA discovery |
| TA0103 | **Collection** | Historian exfil, process value monitoring |
| TA0102 | **Command & Control** | Reverse connect, DNS tunneling |
| TA0106 | **Inhibit Response** | Safety system disable, process override |
| TA0105 | **Impact** | Process interruption, equipment damage |

### 1.2 Procédure d'intervention

1. **Détection & Analyse** (détection SIEM, alerte OT, remontée produit)
2. **Confirmation** (vérification incident, analyse forensique rapide)
3. **Containement** (zoning, firewall OT, désactivation liaisons)
4. **Éradication** (nettoyage malware, restauration firmware)
5. **Récupération** (redémarrage contrôlé, validation process)
6. **Post-incident** (lessons learned, mise à jour plan cybersécurité)

---

## 2. Collection de Preuves OT

### 2.1 Sources et méthodes

| Source | Méthode | Outil |
|:-------|:--------|:------|
| **Logs PLC** | Historique alarmes, buffer événements | Consult native, Wireshark |
| **Firmware** | Hash, version, signature | Compare with known good |
| **Trafic réseau OT** | PCAP files, ports 102/502/44818/4840 | Wireshark, TShark |
| **Engineering WS** | Memory, disk, registry | FTK Imager, Volatility |
| **SCADA logs** | Database logs, audit trail | SQL queries |
| **Historian** | Time-series data changes | Historian export |

### 2.2 Commandes de collecte (PowerShell)

```powershell
# Collecter logs Windows engineering workstation (en environnement OT)
Get-WinEvent -LogName Application,System,Security -MaxEvents 10000

# Collecter connexions réseau actives
netstat -ano

# Collecter processus et services
Get-Process | Export-Csv -Path ./process.csv
Get-Service | Export-Csv -Path ./services.csv
```

---

## 3. Outils et Références

- [MITRE ATT&CK for ICS](https://attack.mitre.org/techniques/ics/)
- [ICS-CERT Advisories](https://www.cisa.gov/ics)
- [Dragos ICS OT Threat Intelligence](https://www.dragos.com)
- [Nozomi Guardian](https://www.nozominetworks.com)
- [Claroty for OT Security](https://claroty.com)
- [GRASSMARLIN Network Mapping](https://github.com/nsacyber/GRASSMARLIN)
- [IEC 62443 Incident Response](https://www.isa.org/standards-and-publications/isa-standards/isa-62443-series-standards)
