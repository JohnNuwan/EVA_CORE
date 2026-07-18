---
name: industrial-wireshark-diagnostics
description: "Utiliser quand l'utilisateur demande d'analyser une capture réseau OT avec Wireshark/tshark pour identifier protocoles industriels, latences, conversations et signatures de panne."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [wireshark, tshark, ot, diagnostics, pcap, profinet, modbus, ethernet-ip, opc-ua]
    related_skills: [industrial-network-design, industrial-protocols, industrial-networks-ot]
---

# Industrial Wireshark Diagnostics

## Vue d'ensemble

Cette compétence cadre l'analyse de captures réseau OT pour en tirer un diagnostic exploitable : protocoles observés, conversations dominantes, défauts de cyclicité, retransmissions, comportements anormaux et preuves à intégrer dans un rapport d'incident ou d'audit.

## Quand l'utiliser

À utiliser pour :
- diagnostiquer une panne réseau industrielle ;
- qualifier les protocoles présents dans une cellule ou une ligne ;
- produire des preuves d'audit OT ;
- analyser un PCAP en complément d'un incident automate, SCADA ou historian.

Ne pas utiliser pour :
- un simple inventaire réseau sans capture ;
- une action intrusive sur le réseau de production ;
- un diagnostic purement logique automate sans symptôme réseau.

## Workflow recommandé

1. Identifier le contexte : fenêtre horaire, ligne, équipement, symptôme.
2. Lister les protocoles attendus et les comparer aux protocoles observés.
3. Analyser les conversations dominantes et les ports critiques.
4. Relever les anomalies : pertes, trames rares, bursts, sessions instables.
5. Conclure avec preuves et hypothèses ordonnées par probabilité.

## Filtres et preuves

Voir `references/protocol-filter-matrix.md` pour une matrice rapide de filtres Wireshark/tshark par protocole.

## Pièges Courants (Common Pitfalls)

1. Tirer des conclusions sans relier la capture au symptôme métier.
2. Regarder uniquement les protocoles applicatifs sans vérifier la couche IP/TCP/UDP.
3. Oublier les flux périodiques cycliques et leurs écarts temporels.
4. Fournir un diagnostic sans preuves exportables ni horodatage.

## Liste de vérification (Checklist)

- [ ] Le contexte de capture est documenté.
- [ ] Les protocoles attendus et observés sont comparés.
- [ ] Les conversations critiques sont identifiées.
- [ ] Les anomalies sont liées au symptôme métier.
- [ ] Les preuves sont exploitables dans un rapport.
