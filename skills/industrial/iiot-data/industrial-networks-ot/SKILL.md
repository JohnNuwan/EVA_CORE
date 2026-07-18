---
name: industrial-networks-ot
description: "Utiliser quand l'utilisateur demande de concevoir, de sécuriser ou de dépanner des architectures réseau industrielles (OT) selon le modèle Purdue ou les spécifications CPwE."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [industrial-networks, ot-networks, cpwe, routing, switch-config, industrial-automation]
  related_skills: [iso-27001, ot-security]
---

# Réseaux Industriels OT (Architecture & Sécurité)

## Vue d'ensemble

Le réseau de production (**OT** - Operational Technology) d'une usine possède des contraintes très différentes du réseau de bureau (**IT**) : la priorité absolue est la **disponibilité** et le **déterminisme** (les paquets de commande automate doivent arriver à temps constant pour éviter l'arrêt d'urgence), tandis que le réseau IT privilégie la confidentialité des données.

Pour structurer un réseau industriel de manière sécurisée et performante, on applique l'architecture de référence **CPwE (Converged Plantwide Ethernet)** co-développée par Cisco et Rockwell Automation, basée sur le **Modèle Purdue (ISA-99)**.

Les concepts réseaux OT incontournables :
1.  **Le Modèle Purdue (Segmentation) :** Découpage du réseau en niveaux logiques (Niveau 0-Capteurs, Niveau 1-Automates, Niveau 2-Supervision SCADA, Niveau 3.5-DMZ industrielle, Niveau 4-Réseau entreprise).
2.  **Les VLANs (Virtual LAN) :** Segmenter logiquement les machines pour limiter le trafic de diffusion (Broadcast storm) propre aux protocoles comme Ethernet/IP ou Profinet.
3.  **Le NAT (Network Address Translation) / 1:1 NAT :** Permettre l'intégration de machines OEM possédant les mêmes adresses IP d'usine internes (ex: `192.168.1.10`) dans le réseau global de l'usine sans conflits.
4.  **Les commutateurs industriels :** Matériel renforcé supportant les protocoles d'anneau de secours rapides (DLR - Device Level Ring, ou MRP - Media Redundancy Protocol) pour pallier la rupture physique d'une fibre optique sans perte de communication.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir le schéma d'adressage IP ou le plan de VLANs pour une usine ou un nouvel atelier.
- De configurer ou de documenter des règles de NAT 1:1 sur un commutateur ou un pare-feu industriel (ex: Stratix, Hirschmann).
- De dépanner des problèmes de tempêtes de broadcast ou de perte de ping sur des équipements d'usine.
- D'appliquer les recommandations de sécurité de la norme IEC 62443 / ISA-99.

**Ne pas utiliser pour :**
- La configuration de serveurs d'entreprise IT non liés aux équipements d'usine (AD, DNS IT).

---

## 1. Table de Translation NAT 1:1 (Exemple de Configuration)

Le **1:1 NAT** associe une adresse IP publique réseau usine (WAN-side) à une adresse IP privée machine interne (LAN-side). Cela permet d'avoir 5 machines identiques construites par un constructeur étranger avec les mêmes IP internes sans collision réseau.

### Table de mapping NAT pour la Ligne de Conditionnement :

| Équipement | IP Interne LAN (Constructeur) | IP Publique WAN (Réseau Usine) | Port Externe autorisé |
|---|---|---|---|
| Automate Emballeuse (PLC) | `192.168.1.10` | `10.45.12.10` | 44818 (EtherNet/IP) |
| Console IHM Emballeuse | `192.168.1.11` | `10.45.12.11` | 5900 (VNC pour prise en main) |
| Automate Palettiseur (PLC) | `192.168.1.10` | `10.45.12.20` | 44818 (EtherNet/IP) |
| Console IHM Palettiseur | `192.168.1.11` | `10.45.12.21` | 5900 (VNC) |

### Exemple de configuration CLI de translation NAT (Syntaxe type Cisco IOS) :
```text
! Configuration du NAT 1:1 pour le PLC de l'emballeuse
ip nat inside source static 192.168.1.10 10.45.12.10
! Configuration du NAT 1:1 pour l'IHM de l'emballeuse
ip nat inside source static 192.168.1.11 10.45.12.11
```

---

## 2. Configuration et bonnes pratiques des protocoles d'anneau (DLR / MRP)

Pour assurer une disponibilité réseau maximale (Tolérance aux pannes), les commutateurs industriels raccordés en boucle fermée physique ne doivent pas provoquer de boucle logique réseau (bloquée par STP). On utilise les protocoles industriels :

*   **DLR (Device Level Ring) :** Spécifique EtherNet/IP. Commutation rapide < 3 ms. Requiert des équipements possédant des puces switch intégrées à double port.
*   **MRP (Media Redundancy Protocol) :** Standard international (IEC 62439-2) typiquement utilisé sous Profinet. Commutation en < 20 ms.

### Règle de configuration :
Pour chaque anneau physique, il faut configurer **un seul et unique équipement** comme Maître de l'anneau (Ring Supervisor ou Ring Manager). Tous les autres équipements de l'anneau doivent être configurés comme clients de l'anneau. Si deux maîtres sont configurés par erreur, le réseau s'effondre.

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Absence de IGMP Snooping sur le réseau EtherNet/IP :**
    *   *Erreur :* Ne pas activer le protocole IGMP Snooping sur les switches administrables. Les données de scrutation automate (Implicit I/O) sont envoyées en Multicast. Sans IGMP Snooping, le switch traite le multicast comme du broadcast et l'envoie sur tous ses ports, submergeant les petits composants ou caméras IP qui s'échauffent et plantent.
    *   *Correction :* Toujours activer **IGMP Snooping** et définir un commutateur central comme **IGMP Querier** pour filtrer intelligemment le trafic multicast.
2.  **Utilisation de switches non administrables (Unmanaged Switches) :**
    *   *Erreur :* Installer des switches bas de gamme non configurables dans l'armoire électrique d'une machine critique. Ils ne supportent pas la gestion des VLANs, le diagnostic SNMP, ni le filtrage de paquets.
    *   *Correction :* Utiliser exclusivement des commutateurs durcis administrables (Managed Switches) pour le cœur du réseau machine.

---

## Liste de vérification (Checklist)

- [ ] L'architecture réseau respecte les niveaux de segmentation du modèle Purdue (séparation IT/OT).
- [ ] Le protocole **IGMP Snooping** est activé sur tous les commutateurs véhiculant du trafic EtherNet/IP (Multicast).
- [ ] Dans chaque anneau physique DLR ou MRP, un seul équipement est configuré en tant que superviseur/maître de l'anneau.
- [ ] Les adresses IP de toutes les machines constructeurs identiques (OEM) sont isolées et traduits via des passerelles NAT 1:1.

