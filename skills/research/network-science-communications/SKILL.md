---
name: network-science-communications
description: "Compétence en recherche en science des réseaux et communications suivie sur arXiv sous cs.NI, physics.soc-ph. Couvre l'architecture des réseaux, les protocoles de communication, les réseaux sans fil, les SDN, NFV, les réseaux IoT, la qualité de service, la fiabilité, le routage et la topologie des réseaux."
category: research
arxiv_categories:
  - cs.NI
  - eess.SY
  - cs.DC
  - cs.CR
  - physics.soc-ph
lang: fr
---

# Compétence : Science des Réseaux et Communications

## Présentation

Cette compétence couvre la veille de recherche en science des réseaux et systèmes de communication, avec un suivi régulier des publications sur arXiv dans les catégories cs.NI (Networking and Internet Architecture) et physics.soc-ph (Physics and Society — réseaux complexes). Les domaines comprennent l'architecture des réseaux, les protocoles de communication émergents, les réseaux sans fil de nouvelle génération, la virtualisation des fonctions réseau, l'Internet des objets, la qualité de service et la sécurité réseau.

## Domaines de Recherche

### Architectures et Protocoles
- **TCP/IP** : évolution de TCP (CUBIC, BBR, QUIC), congestion control, AQM (Active Queue Management), ECN, TCP variants (Vegas, Westwood, Illinois, BBRv3)
- **QUIC** : protocole de transport basé sur UDP, multiplexage, 0-RTT, migration de connexion, QUIC version 2, multipath QUIC
- **HTTP/3** : HTTP sur QUIC, prioritization, server push, évolution HTTP
- **Routage** : protocoles IGP (OSPF, IS-IS), EGP (BGP, BGP-LS), routage segment routing (SRv6, SR-MPLS), routage inter-domaine, BGP security (RPKI, BGPsec)
- **Commutation** : MPLS, VXLAN, EVPN, commutation optique, commutation de paquets, commutation de circuits
- **Architectures Réseau Émergentes** : Information-Centric Networking (ICN), Named Data Networking (NDN), Delay-Tolerant Networking (DTN), Time-Sensitive Networking (TSN)

### Réseaux Sans Fil
- **5G/6G** : architecture 5G NR, network slicing, massive MIMO, beamforming, mmWave, 6G vision, THz communications, ISAC (Integrated Sensing and Communication), cell-free massive MIMO
- **WiFi** : IEEE 802.11be (WiFi 7), 802.11ax (WiFi 6), OFDMA, MU-MIMO, WiFi sensing, WiFi HaLow
- **LoRa** : LoRaWAN, modulation CSS, ADR (Adaptive Data Rate), LoRaWAN Class B/C, LR-FHSS
- **LTE-M / NB-IoT** : LTE Cat-M1, NB-IoT, mode in-band/guard-band/standalone, eDRX, PSM
- **mmWave** : canaux à ondes millimétriques, 60 GHz, réseaux 5G mmWave, WiGig, beamforming, blockage, handover
- **Réseaux Satellitaires** : LEO/MEO/GEO, Starlink, OneWeb, satellite IoT, NTN (Non-Terrestrial Networks), 3GPP NTN

### SDN et NFV
- **Software-Defined Networking (SDN)** : architecture, plan de contrôle séparé, OpenFlow, P4, ONOS, OpenDaylight, SDN WAN, SDN pour data centers
- **Network Function Virtualization (NFV)** : virtualisation des fonctions réseau, chaînage de services (SFC), MANO (Management and Orchestration), VNF placement, scaling
- **OpenFlow** : protocole, tables de flux, groupes, meters, OpenFlow versions, extensions
- **P4** : langage de programmation de data plane, compilateur P4, cibles (BMv2, Tofino, FPGA)
- **Network Slicing** : découpage réseau 5G, isolation, orchestrations, slice subnet, RAN slicing
- **Edge Computing** : MEC (Multi-access Edge Computing), fog computing, cloudlets, edge AI, serveur edge

### Réseaux IoT
- **LPWAN (Low-Power Wide-Area Networks)** : LoRaWAN, Sigfox, NB-IoT, LTE-M, comparison des technologies
- **Réseaux Mesh** : Zigbee, Thread, 6LoWPAN, RPL (Routing Protocol for Low-Power and Lossy Networks), Bluetooth Mesh
- **Protocoles Contraints** : CoAP (Constrained Application Protocol), MQTT-SN, LwM2M, protocoles pour environnements contraints, DTLS, OSCORE, EDHOC
- **CoAP** : REST pour contraintes, observations, block-wise transfer, CoAP over TCP/TLS, CoAP over QUIC
- **MQTT** : MQTT 3.1.1, MQTT 5.0, QoS, topic, sessions persistantes, MQTT-SN, bridge MQTT
- **IoT Security** : protocoles de sécurité légers, authentication pour IoT, key management, secure boot, TPM pour IoT, firmware update

### IoT Industriel et Automatisation
- **IIoT (Industrial IoT)** : Industrie 4.0, OPC UA, communication machine-machine, architecture de référence RAMI 4.0
- **TSN (Time-Sensitive Networking)** : IEEE 802.1Qbv (gating), 802.1Qci (policing), 802.1CB (redondance), 802.1AS (time sync), 802.1Qch (cyclic scheduling)
- **Profinet** : protocole de communication industrielle, RT (Real-Time), IRT (Isochronous Real-Time), Profinet over TSN
- **EtherCAT** : automation temps réel, EtherCAT sur TSN, synchronisation distribuée
- **OPC UA** : architecture unifiée, pub/sub, OPC UA over TSN, sécurité OPC UA, information models
- **Déterminisme Temps Réel** : ordonnancement temps réel, réseaux temps réel, horloge distribuée, synchronisation

### Qualité de Service et Fiabilité
- **QoS (Quality of Service)** : IntServ, DiffServ, RSVP-TE, garantie de bande passante, latence, gigue, Integrated QoS
- **QoE (Quality of Experience)** : métriques QoE, modèles QoE, QoE pour streaming vidéo, QoE pour jeux en ligne, ML pour QoE
- **SLA (Service Level Agreements)** : définition et contrôle de SLA, vérification de SLA, SLA pour réseaux virtualisés, SLA multi-opérateurs
- **Fiabilité Réseau** : résilience, reconfiguration rapide, protection 1+1/1:1, Fast Reroute, TI-LFA, redondance réseau, self-healing networks
- **Ordonnancement et File d'Attente** : WFQ, CBQ, RED, CoDel, PIE, FQ-CoDel, CAKE

### Sécurité Réseau
- **NAC (Network Access Control)** : 802.1X, EAP, RADIUS, contrôle d'accès réseau, posture assessment, BYOD security
- **Segmentation Réseau** : micro-segmentation, segmentation zero trust, VLAN, VXLAN, Network Policy, segmentation SDN
- **Zero Trust** : architecture zero trust (ZTA), NIST SP 800-207, BeyondCorp, Zero Trust pour IoT, Zero Trust pour réseaux 5G
- **Détection d'Intrusion** : NIDS/NIPS, signatures, anomalies, ML/DL pour détection, analyse de flux réseau (NetFlow, sFlow, IPFIX)
- **Cryptographie Réseau** : TLS 1.3, IPsec, WireGuard, MACsec, SSH

## Catégories arXiv Suivies

| Catégorie | Description |
|-----------|-------------|
| **cs.NI** | Networking and Internet Architecture |
| **eess.SY** | Systems and Control |
| **cs.DC** | Distributed, Parallel, and Cluster Computing |
| **cs.CR** | Cryptography and Security |
| **physics.soc-ph** | Physics and Society (réseaux complexes) |

## Articles et Publications Clés

- **MCP-Enabled Agentic AI for Network Automation** — ECOC 2026, agentification des réseaux via Model Context Protocol
- **5G-Advanced / 6G Visions** — 3GPP Releases 18-21
- **P4-based Network Telemetry** — INT (In-band Network Telemetry) avancée
- **Zero Trust Architecture for IoT and 5G** — NIST/NISTIR publications

## Méthodologie de Veille

1. **Recherche hebdomadaire** sur arXiv dans les catégories listées ci-dessus
2. **Mots-clés prioritaires** : 5G, 6G, SDN, NFV, IoT, IIoT, TSN, QUIC, HTTP/3, network slicing, zero trust, MEC, edge computing, LoRaWAN, WiFi 7, P4, OPC UA
3. **Conférences cibles** : ACM SIGCOMM, IEEE INFOCOM, ACM CoNEXT, IETF meetings, IEEE ICC/Globecom, USENIX NSDI, ACM MobiCom, EWSN, IEEE LCN
4. **Normalisation** : IETF, 3GPP, IEEE 802, oneM2M, OPC Foundation, O-RAN Alliance

## Ressources Associées

- [ArXiV cs.NI](https://arxiv.org/list/cs.NI/recent)
- [ArXiV physics.soc-ph](https://arxiv.org/list/physics.soc-ph/recent)
- [IETF Datatracker](https://datatracker.ietf.org/)
- [3GPP Specifications](https://www.3gpp.org/)