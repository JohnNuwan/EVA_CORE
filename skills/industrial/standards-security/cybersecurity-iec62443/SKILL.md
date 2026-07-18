---
name: cybersecurity-iec62443
description: "Auditer, segmenter et durcir les réseaux OT (Operational Technology) selon la norme IEC 62443 : zones et conduits, niveaux de sécurité SL, durcissement d'automates Siemens/Rockwell/Schneider, audit réseau non-intrusif, et conformité réglementaire."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [cybersecurity, iec-62443, ot-security, hardening, firewall, vlan, network-audit, industrial-automation, scada-security, plc-security, zone-conduit, purdue-model]
    related_skills: [ot-security, industrial-networks-ot, hardware-security-firmware, isa95-modelling, iso-27001]
    difficulty: advanced
    industry_sectors: [manufacturing, energy, oil-gas, chemical, pharmaceutical, water-treatment, critical-infrastructure]
---

# Cybersécurité Industrielle IEC 62443 — Guide Opérationnel

## Vue d'ensemble

La norme **IEC 62443** (anciennement ISA/IEC 62443) est le standard de référence mondial pour la cybersécurité des systèmes d'automatisme et de contrôle industriel (IACS - Industrial Automation and Control Systems). Contrairement à l'ISO 27001 (orientée IT), l'IEC 62443 cible spécifiquement les environnements **OT (Operational Technology)** où la disponibilité, l'intégrité et la sûreté de fonctionnement priment sur la confidentialité.

### Contexte : Pourquoi une norme spécifique OT ?

Dans un environnement IT classique, la confidentialité des données est le premier objectif de sécurité (triade CIA : Confidentialité, Intégrité, Disponibilité). Dans l'industrie OT, la hiérarchie est inversée :

| Objectif de sécurité | IT (Bureautique) | OT (Industriel) |
|:---|---|:---|
| **1er** | Confidentialité | **Disponibilité** (un arrêt de production coûte des millions) |
| **2ème** | Intégrité | **Intégrité** (une commande erronée peut détruire un équipement) |
| **3ème** | Disponibilité | **Confidentialité** (protection des données process) |

Les spécificités OT qui compliquent la sécurité :
- Équipements avec une durée de vie de 15 à 25 ans (obsolescence logicielle).
- Systèmes d'exploitation propriétaires ou verrouillés (VxWorks, RTOS).
- Impossibilité d'appliquer des correctifs de sécurité (patch) sans arrêt de production.
- Protocoles industriels historiquement non sécurisés (Modbus, Profibus, CIP).

Cette compétence fournit à l'agent EVA des outils **opérationnels** pour :
1. Réaliser un **audit réseau OT non-intrusif** (scan Nmap adapté aux équipements industriels).
2. Appliquer des **guides de durcissement (hardening)** pour automates Siemens, Rockwell et Schneider.
3. Concevoir une **segmentation réseau en Zones et Conduits** conforme à IEC 62443-3-2.
4. Configurer les **règles de pare-feu industriel** de base.
5. Évaluer la conformité d'un site au regard des niveaux de sécurité (SL) de la norme.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :

- De réaliser un audit de cybersécurité OT ou un inventaire réseau d'atelier (inventaire des équipements, des ports ouverts, des protocoles).
- De durcir (hardening) la configuration d'un automate PLC (Siemens S7, Rockwell ControlLogix, Schneider M340/M580) ou d'un serveur SCADA.
- De concevoir la segmentation réseau (Zones & Conduits) d'un site industriel conformément au modèle Purdue (ISA-95).
- De configurer des règles de pare-feu pour l'isolation IT/OT ou entre zones OT de niveaux différents.
- De préparer un dossier de conformité IEC 62443 pour un audit ou une certification.
- De mettre en place une gestion des accès et des connectivités à distance sécurisées (VPN, MFA, Jump Host).

**Ne pas utiliser pour :**
- La mise en place d'un SMSI ISO 27001 généraliste (utiliser la compétence `iso-27001`).
- La programmation de fonctions de sécurité automate SIL/PL (utiliser `industrial-safety-sistema`).

## 1. Niveaux de Sécurité IEC 62443 (Security Levels - SL)

L'IEC 62443 définit 5 niveaux de sécurité (SL) croissants qui déterminent le niveau de protection requis en fonction de la criticité de l'installation et de la menace :

| Niveau | Menace ciblée | SL-T (Target) | Exemples de mesures techniques et organisationnelles |
|:---:|:---|---:|:---|
| **SL 0** | Aucune exigence particulière | 0 | Aucune protection spécifique. Réseau ouvert, pas de mot de passe. Concerne uniquement des équipements non critiques et isolés. |
| **SL 1** | Erreur involontaire, accident | 1 | Mots de passe par défaut changés, antivirus à jour, politique de sauvegarde. Protection contre les violations accidentelles. |
| **SL 2** | Attaque ciblée avec ressources limitées | 2 | Segmentation VLAN, authentification forte, journalisation des accès, gestion des vulnérabilités. C'est le niveau minimal recommandé pour la majorité des sites industriels. |
| **SL 3** | Attaque sophistiquée (APT, état-nation, hacktivistes) | 3 | Chiffrement des communications (TLS), IDS/IPS industriel, gestion centralisée des certificats (PKI), audits réguliers, durcissement système d'exploitation. |
| **SL 4** | Attaque coordonnée avec ressources illimitées | 4 | Systèmes redondants, air-gap physique complet, analyse forensique, équipe de réponse aux incidents dédiée (CSIRT). Réservé aux infrastructures critiques nationales. |

> **Recommandation pratique :** La majorité des sites industriels (usines de production, sites chimiques, eau) visent un **SL 2** comme objectif réaliste et prioritaire. Atteindre un SL 3 nécessite des investissements significatifs en matériel et en compétences.

## 2. Script d'Audit Réseau OT Non-Intrusif

Ce script Python utilise Nmap en mode non-intrusif (pas de scan de vulnérabilités agressif, débit limité) pour inventorier les équipements OT sur un réseau :

```python
import subprocess
import json
import xml.etree.ElementTree as ET
from datetime import datetime


def scan_ot_network(subnet: str, output_dir: str = ".") -> dict:
    """Réalise un scan réseau OT non-intrusif avec Nmap.

    ATTENTION : Ce scan est conçu pour être le moins intrusif possible
    sur les équipements industriels. Il utilise :
    - Un débit limité (--max-rate 50) pour ne pas surcharger les automates
    - Un scan TCP SYN (-sS) qui ne complète pas les connexions
    - Les ports industriels standards uniquement

    Args:
        subnet: Sous-réseau à scanner (ex: '192.168.1.0/24').
        output_dir: Répertoire de sortie pour le rapport.

    Returns:
        dict: Inventaire des équipements détectés avec leurs ports ouverts.
    """
    # Ports industriels standards (OT + services de base)
    ports = "22,80,102,443,502,1883,4840,4843,8080,8443,20000,44818,47808,48898"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    xml_output = f"{output_dir}/ot_scan_{timestamp}.xml"

    cmd = [
        "nmap",
        "-sS",              # TCP SYN scan (semi-ouvert, moins intrusif)
        "-sV",              # Détection de version des services
        "--version-light",  # Mode léger de détection (moins de sondes)
        "-O",               # Détection d'OS
        "--max-rate", "50", # Limiter le débit pour ne pas perturber les automates
        "-p", ports,
        "-oX", xml_output,
        subnet,
    ]

    print(f"Scan OT en cours sur {subnet} (ports: {ports})...")
    print("⚠ Mode non-intrusif : débit limité à 50 paquets/seconde")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    if result.returncode != 0:
        return {"error": result.stderr}

    # Parsing du résultat XML
    inventory = parse_nmap_xml(xml_output)
    inventory["scan_date"] = timestamp
    inventory["subnet"] = subnet

    return inventory


def parse_nmap_xml(xml_path: str) -> dict:
    """Parse le fichier XML de sortie Nmap en inventaire structuré.

    Args:
        xml_path: Chemin vers le fichier XML Nmap.

    Returns:
        dict: Inventaire structuré des hôtes et services détectés.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    hosts = []
    for host in root.findall("host"):
        if host.find("status").get("state") != "up":
            continue

        ip = host.find("address").get("addr")
        os_match = ""
        os_elem = host.find(".//osmatch")
        if os_elem is not None:
            os_match = os_elem.get("name", "")

        services = []
        for port in host.findall(".//port"):
            state = port.find("state").get("state")
            if state != "open":
                continue
            service = port.find("service")
            services.append({
                "port": int(port.get("portid")),
                "protocol": port.get("protocol"),
                "service": service.get("name", "") if service is not None else "",
                "product": service.get("product", "") if service is not None else "",
                "version": service.get("version", "") if service is not None else "",
            })

        # Classification automatique du type d'équipement
        device_type = classify_ot_device(services, os_match)

        hosts.append({
            "ip": ip,
            "os": os_match,
            "device_type": device_type,
            "open_ports": services,
        })

    return {"hosts_count": len(hosts), "hosts": hosts}


def classify_ot_device(services: list, os_hint: str) -> str:
    """Classifie un équipement OT en fonction de ses ports ouverts.

    Args:
        services: Liste des services ouverts.
        os_hint: Indication du système d'exploitation détecté.

    Returns:
        str: Type d'équipement estimé.
    """
    ports = {s["port"] for s in services}

    if 102 in ports:
        return "Automate Siemens (S7 Protocol)"
    if 44818 in ports:
        return "Automate Rockwell (EtherNet/IP)"
    if 502 in ports:
        return "Équipement Modbus TCP (compteur, variateur, API)"
    if 48898 in ports:
        return "Contrôleur Beckhoff (TwinCAT ADS)"
    if 4840 in ports:
        return "Serveur OPC-UA"
    if 47808 in ports:
        return "Contrôleur BACnet (GTB/CVC)"
    if 1883 in ports:
        return "Broker MQTT"
    if 80 in ports or 443 in ports:
        if "Siemens" in os_hint:
            return "IHM Siemens (Web Server)"
        return "Équipement avec interface Web"

    return "Non classifié"


if __name__ == "__main__":
    # Exemple d'utilisation
    result = scan_ot_network("192.168.1.0/24")
    print(json.dumps(result, indent=2))
```

## 3. Checklist de Durcissement Automate (Hardening)

### Siemens S7-1200 / S7-1500 (TIA Portal)

| # | Mesure de durcissement | Paramètre TIA Portal | Criticité |
|:---:|---|---|:---:|
| 1 | Changer le mot de passe par défaut de la CPU | Configuration CPU → Protection & Security → Password | Critique |
| 2 | Activer la protection en écriture de la CPU | Protection → "Full protection (access level: No access)" | Haute |
| 3 | Désactiver PUT/GET si non utilisé | CPU Properties → Protection → Décocher "Permit access with PUT/GET" | Haute |
| 4 | Activer le journal des accès (Access Log) | CPU Properties → Web Server → Enable access logging | Moyenne |
| 5 | Restreindre les protocoles de communication | Désactiver les protocoles non nécessaires (HTTP, SNMP, FTP, etc.) | Haute |
| 6 | Configurer le pare-feu intégré CP/CM | Module de communication → Security → Firewall | Critique |
| 7 | Utiliser des communications chiffrées (TLS) | OPC-UA Server → Security → Certificate-based authentication | Haute |
| 8 | Sauvegarder la configuration de référence | Projet → Archive → Create reference backup (avant et après modification) | Critique |

### Rockwell ControlLogix / CompactLogix (Studio 5000)

| # | Mesure de durcissement | Paramètre Studio 5000 | Criticité |
|:---:|---|---|:---:|
| 1 | Activer CIP Security (EtherNet/IP) | Controller Properties → Security → Enable CIP Security | Haute |
| 2 | Configurer le verrouillage du contrôleur | Controller Properties → Security → Lock Controller | Critique |
| 3 | Restreindre les accès par adresse IP source | Module Properties → Connection → Allowed IP ranges | Haute |
| 4 | Activer la journalisation d'audit | FactoryTalk → Security → Audit logging | Moyenne |
| 5 | Désactiver les ports et services non utilisés | Module → Port Configuration → Disable unused ports | Haute |
| 6 | Changer le mot de passe utilisateur par défaut | Controller Properties → Security → Change password | Critique |

### Schneider Electric M340 / M580 (EcoStruxure Control Expert)

| # | Mesure de durcissement | Paramètre Control Expert | Criticité |
|:---:|---|---|:---:|
| 1 | Activer la protection par mot de passe du projet | Edit → Project Settings → Password Protection | Critique |
| 2 | Configurer les droits d'accès (R/W) par utilisateur | Security → User Management → Access rights | Haute |
| 3 | Activer la journalisation des événements de sécurité | Security → Audit Trail → Enable | Moyenne |
| 4 | Restreindre les connexions Ethernet autorisées | Module → Ethernet → Connection Filter → IP whitelist | Haute |
| 5 | Désactiver les services non nécessaires (DHCP, HTTP, FTP) | Module → Services → Disable unused | Haute |

## 4. Modèle Zones & Conduits (IEC 62443-3-2)

Le modèle de segmentation "Zones & Conduits" est la pierre angulaire de l'IEC 62443. Une **Zone** est un regroupement logique ou physique d'actifs partageant les mêmes exigences de sécurité. Un **Conduit** est un canal de communication sécurisé entre deux zones.

### Architecture de Référence (Modèle Purdue / ISA-95 adapté)

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                     ZONE 4 : RÉSEAU ENTREPRISE (IT)                    │
│                     SL cible : SL 1                                    │
│     [Serveur ERP]     [Messagerie]     [Bureautique]     [Internet]    │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                            ┌──────┴──────┐
                            │  CONDUIT 1  │  ← Pare-feu industriel DMZ
                            │  (IT ↔ OT)  │  ← Règles restrictives (allow-list)
                            └──────┬──────┘
                                   │
┌──────────────────────────────────┴───────────────────────────────────────┐
│                     ZONE 3 : RÉSEAU SUPERVISION (DMZ)                  │
│                     SL cible : SL 2-3                                  │
│     [Serveur SCADA]     [Historien]     [Serveur MES]     [OPC-UA]    │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                            ┌──────┴──────┐
                            │  CONDUIT 2  │  ← Switch manageable + ACL VLAN
                            │ (SCADA↔PLC) │  ← Ports autorisés uniquement
                            └──────┬──────┘
                                   │
┌──────────────────────────────────┴───────────────────────────────────────┐
│                     ZONE 2 : RÉSEAU AUTOMATES (OT)                     │
│                     SL cible : SL 2-3                                  │
│                                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐             │
│  │ VLAN 10 │    │ VLAN 20 │    │ VLAN 30 │    │ VLAN 40 │             │
│  │ Ligne 1 │    │ Ligne 2 │    │Utilités │    │ Énergie│             │
│  │ PLC+HMI │    │ PLC+HMI │    │ PLC     │    │Compteurs│             │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘             │
│                                                                         │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
                            ┌──────┴──────┐
                            │  CONDUIT 3  │  ← Câblage direct capteurs
                            │ (PLC↔I/O)   │  ← Bus de terrain (Profinet, AS-i)
                            └──────┬──────┘
                                   │
┌──────────────────────────────────┴───────────────────────────────────────┐
│                     ZONE 1 : PÉRIPHÉRIE (CAPTEURS / ACTIONNEURS)       │
│                     SL cible : SL 1-2                                  │
│     [Variateurs]     [Capteurs]     [Actionneurs]     [Robots]         │
└──────────────────────────────────────────────────────────────────────────┘
```

### Règles de Segmentation Fondamentales

1. **Isolation IT/OT obligatoire** : Un pare-feu industriel (ex : MGuard, Tofino, Hirschmann) doit filtrer tous les flux entre le réseau d'entreprise et le réseau de production. Aucune route directe sans passer par la DMZ.
2. **Micro-segmentation OT** : À l'intérieur du réseau OT, séparer les lignes de production en VLANs distincts. Même si un attaquant compromet une ligne, il ne peut pas atteindre les autres lignes.
3. **DMZ industrielle** : Tous les services partagés (Historian, serveur OPC-UA, serveur d'authentification) doivent être placés dans une DMZ. Les automates ne doivent jamais être directement accessibles depuis le réseau IT.
4. **Principe du moindre privilège réseau** : N'autoriser que les flux réseau strictement nécessaires à l'exploitation. Bloquer tout le reste par défaut (Allow-List).

## Pièges Courants (Common Pitfalls)

1. **Scanner le réseau OT avec un outil IT agressif :**
   - *Erreur :* Lancer un scan Nessus ou un scan Nmap complet (-A -T5) sur un réseau d'automates. Certains PLC anciens (S7-300, Modicon Quantum) peuvent planter ou redémarrer sous la charge de paquets (déni de service involontaire).
   - *Correction :* Utiliser un débit limité (`--max-rate 50`), scanner uniquement les ports industriels connus, informer le responsable d'exploitation avant tout scan et le réaliser de préférence pendant un arrêt de production planifié.

2. **Segmenter le réseau sans plan de flux préalable :**
   - *Erreur :* Mettre en place des VLANs et un pare-feu sans avoir documenté tous les flux de données existants (OPC-UA, Modbus, Profinet, NTP, DNS, DHCP, etc.). Résultat immédiat : la production s'arrête par blocage de flux légitimes.
   - *Correction :* Capturer le trafic réseau (Wireshark sur un port mirror / SPAN du switch) pendant au moins 48 à 72 heures (cycle de production complet) avant toute segmentation pour identifier tous les flux légitimes.

3. **Confondre sécurité IT et sécurité OT :**
   - *Erreur :* Appliquer des mises à jour Windows automatiques sur un serveur SCADA en production, ou installer un antivirus qui met en quarantaine un driver de communication automate (ex : driver OPC, driver CP).
   - *Correction :* Les mises à jour OT doivent être testées en environnement de pré-production (usine test/plateforme de simulation) et appliquées lors de fenêtres de maintenance planifiées avec validation préalable.

4. **Identifiants par défaut conservés sur les équipements OT :**
   - *Erreur :* Laisser les mots de passe par défaut (ex : `admin`/`admin`, `1234`, `Siemens` sur les HMI, `root`/`root` sur les switches gérés) sur des équipements connectés au réseau.
   - *Correction :* Établir une politique de gestion des identifiants : tous les mots de passe par défaut doivent être changés avant la mise en service. Utiliser un gestionnaire de mots de passe centralisé pour le stockage sécurisé.

5. **Absence de sauvegarde des configurations avant modification :**
   - *Erreur :* Modifier les règles de pare-feu ou la configuration d'un automate sans avoir sauvegardé la configuration courante. En cas de problème, impossible de revenir en arrière rapidement.
   - *Correction :* Toujours réaliser une sauvegarde complète (configuration active + projet source) avant toute modification. Documenter la configuration de référence dans un outil de gestion des configurations réseau (RANCID, Oxidized, SolarWinds NCM).

## Références

- **IEC 62443-2-1** (Ed. 1.0) : Exigences pour un programme de sécurité IACS (Management System).
- **IEC 62443-3-2** (Ed. 1.0) : Évaluation de risques et conception de la segmentation (Zones & Conduits).
- **IEC 62443-3-3** (Ed. 1.0) : Exigences de sécurité système (SR) pour les IACS.
- **IEC 62443-4-1** : Exigences de cycle de développement sécurisé (Secure Development Lifecycle).
- **IEC 62443-4-2** : Exigences de sécurité technique pour les composants IACS.
- **ANSSI — Guide de la cybersécurité des systèmes industriels** : https://www.ssi.gouv.fr/guide/cybersecurite-des-systemes-industriels/
- **NIST SP 800-82 Rev.3** : Guide to Industrial Control System (ICS) Security.
- **Clause 10 — ISO 27001:2022 Annexe A** : Contrôles applicables à la sécurité OT (A.8.25, A.8.29, A.8.32).

## Liste de vérification (Checklist)

- [ ] Les **mots de passe par défaut** de tous les automates, IHM, switches et serveurs SCADA sont changés avant la mise en service.
- [ ] Les **protocoles de communication non utilisés** sont désactivés sur chaque automate (ex : PUT/GET sur Siemens, services inutiles sur Rockwell).
- [ ] Le **réseau OT est segmenté** en VLANs avec un pare-feu industriel entre les zones IT et OT (architecture DMZ).
- [ ] Un **inventaire réseau complet** (adresses IP, protocoles utilisés, versions firmware) est documenté et tenu à jour.
- [ ] Les **flux réseau légitimes** ont été capturés (Wireshark, port mirror) et documentés avant la mise en place des règles de pare-feu.
- [ ] Les **mises à jour de sécurité** (patches) sont testées en environnement de pré-production avant déploiement sur les systèmes OT en production.
- [ ] Les **connexions à distance** (télémaintenance) passent par une passerelle VPN avec authentification multifacteur (MFA) et session journalisée.
- [ ] Un **plan de réponse aux incidents** (Incident Response Plan) spécifique OT est documenté et testé (simulation annuelle).
- [ ] Les **firmwares** des équipements OT sont répertoriés et une veille sur les CVE (Common Vulnerabilities and Exposures) affectant ces versions est en place.
- [ ] Les **sauvegardes** des configurations des équipements OT (automates, switches, pare-feu) sont réalisées automatiquement et stockées hors ligne.

