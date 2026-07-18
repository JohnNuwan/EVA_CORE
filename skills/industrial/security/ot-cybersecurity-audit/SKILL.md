---
name: ot-cybersecurity-audit
description: "Diagnostiquer la sécurité des réseaux et automates OT."
version: 1.2.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [cybersecurity, ot, plc, security-audit, pcap, port-scan, industrial-networks]
  related_skills: [industrial-protocols, plc-connectivity]
---

# Cybersécurité Industrielle (OT) et Durcissement d'Automates (IEC 62443)

## Vue d'ensemble

Cette compétence régit l'audit de sécurité des systèmes de contrôle industriels (IACS) selon la norme internationale **IEC 62443**. Elle fournit les méthodes pour analyser de manière passive ou active le trafic réseau (PCAP) et configurer des dispositifs de filtrage réseau industriel (pare-feu DPI de niveau 7) pour protéger les automates.

---

## Outils Associés

Les outils de diagnostic réseau suivants peuvent être mobilisés :
- `` `industrial_connectivity_analyze_pcap` `` : Analyser le trafic capturé pour lister les protocoles et équipements.
- `` `industrial_connectivity_probe_target` `` : Scanner les ports d'un automate pour identifier les services ouverts.

---

## Cadre Normatif IEC 62443 et Rôles

La norme **IEC 62443** structure la sécurité des architectures industrielles en plusieurs sections selon les acteurs :
* **IEC 62443-2-4** : Exigences de sécurité pour les prestataires de services d'intégration (rôle d'Actemium lors de la mise en service).
* **IEC 62443-3-3** : Exigences de sécurité système et niveaux de sécurité.
* **IEC 62443-4-2** : Exigences de sécurité détaillées pour les composants (CPU automate, commutateur, HMI).

### Les Niveaux de Sécurité (Security Levels)
La norme définit 4 niveaux de sécurité (SL, de 1 à 4) selon l'attaquant visé :
* **SL 1** : Protection contre l'exposition accidentelle ou occasionnelle.
* **SL 2** : Protection contre une attaque intentionnelle avec des moyens simples.
* **SL 3** : Protection contre une attaque intentionnelle avec des moyens modérés (pirates équipés, hacktivisme).
* **SL 4** : Protection contre une attaque intentionnelle avec des moyens sophistiqués (ressources étatiques).

L'audit vise à comparer le **SL-A (Achieved Level - Niveau atteint)** par rapport au **SL-T (Target Level - Niveau cible)** requis par l'exploitant de l'usine.

---

## Configuration d'un Pare-feu Industriel L7 (DPI)

Pour sécuriser un **Conduit** reliant une zone supervision (IT) à une zone automate (OT), l'usage d'un pare-feu industriel de niveau 7 avec Inspection Profonde de Paquets (DPI - *Deep Packet Inspection*) est requis.

### Exemple de configuration : Pare-feu Hirschmann Eagle40 (Modbus TCP)
Afin d'éviter qu'un poste de supervision ou un intrus ne modifie des consignes critiques tout en autorisant la lecture des états de production, nous mettons en place des règles DPI basées sur les **codes fonctions Modbus (FC)**.

#### Configuration des ACLs de niveau 7 :
1. **Règle d'autorisation de lecture seule** :
   * *Source* : Zone Supervision (IP SCADA)
   * *Destination* : Zone Automates (Plage IP Automates)
   * *Protocole/Port* : TCP / Port 502
   * *Filtre L7 (DPI)* : Autoriser uniquement les codes fonctions Modbus :
     * `FC 1` : Read Coils
     * `FC 2` : Read Discrete Inputs
     * `FC 3` : Read Holding Registers
     * `FC 4` : Read Input Registers
2. **Règle de blocage/alerte d'écriture** :
   * *Source* : * (Toutes sources)
   * *Destination* : Zone Automates
   * *Protocole/Port* : TCP / Port 502
   * *Filtre L7 (DPI)* : Bloquer et journaliser (Log & Drop) les codes fonctions d'écriture :
     * `FC 5` : Write Single Coil
     * `FC 6` : Write Single Register
     * `FC 15` : Write Multiple Coils
     * `FC 16` : Write Multiple Registers
3. **Règle par défaut** :
   * Bloquer tout autre trafic Modbus (ex: FC 43 Read Device Identification pour éviter la reconnaissance passive/active).

---

## Méthodologie d'Audit de Réseau OT

Les réseaux industriels temps réel (ex: boucle Profinet ou anneau EtherNet/IP) sont extrêmement sensibles. Un scan agressif (ex: scan de ports rapide via Nmap) peut faire saturer les anciennes cartes réseaux (comme les processeurs de communication de S7-300 ou de SLC500), entraînant un arrêt de production.

### Étape 1 : Découverte Passive (Recommandée)
* Configurer un port miroir (**SPAN / Mirror Port**) sur le commutateur principal de cellule.
* Connecter la sonde Helios pour capturer le trafic (outil `` `industrial_connectivity_analyze_pcap` ``) sans envoyer un seul paquet sur le réseau.
* Analyser les requêtes ARP, les annonces broadcast/multicast (Profinet DCP, EtherNet/IP CIP) pour dresser l'inventaire matériel sans perturbation.

### Étape 2 : Découverte Active Contrôlée
Si la découverte passive est insuffisante, l'audit actif doit respecter les consignes de prudence suivantes :
1. Ne jamais scanner en mode "balayage rapide". Utiliser des délais d'attente importants entre les paquets (paramètre `-T2` ou `-T1` sous Nmap).
2. Interroger en priorité les ports protocolaires spécifiques des automates (ex: `102` pour Siemens S7, `44818` pour Ethernet/IP, `502` pour Modbus TCP) plutôt qu'un scan complet de 65535 ports.
3. Éviter d'envoyer des paquets de taille anormale ou mal formés, car les piles TCP/IP des anciens OS d'automates n'ont pas de protection contre les débordements de tampon (Buffer Overflow).
