---
name: wago-codesys
description: "Programmer les contrôleurs WAGO sous CODESYS et migrer depuis e!COCKPIT."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [wago, codesys, iec61131-3, ecockpit, pfc200, opc-ua, modbus, plcopen]
    related_skills: [plcopen-xml, beckhoff-twincat, industrial-protocols, industrial-communication-protocols]
---

# WAGO & CODESYS V3.5

## Vue d'ensemble

Cette compétence couvre les contrôleurs WAGO modernes, leur usage sous CODESYS V3.5, la migration depuis e!COCKPIT et les architectures OT/IT compactes ou edge. Elle est utile pour structurer des applications IEC 61131-3 portables, exposer des données via OPC UA/Modbus/MQTT et standardiser des projets WAGO maintenables.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Programmer un contrôleur WAGO sous CODESYS V3.5.
- Migrer ou reprendre un projet e!COCKPIT.
- Structurer une application IEC 61131-3 portable.
- Exposer des variables via OPC UA, Modbus TCP ou MQTT depuis un PFC.
- Concevoir un nœud edge ou une passerelle OT/IT WAGO.

## Architecture recommandée

- `GVL_*` pour constantes et échanges.
- `DUT_*` pour structures métier.
- `FB_*` pour équipements réutilisables.
- `PRG_*` pour orchestration de zones.
- `PLC_PRG` minimal, limité aux appels de haut niveau.

## Bonnes pratiques

- Séparer clairement les variables internes des variables exposées au SCADA.
- Structurer les échanges OPC UA/Modbus sur un modèle stable par équipement.
- Revalider bibliothèques, mapping I/O et tâches lors d'une migration e!COCKPIT.
- Tirer parti du rôle passerelle/edge du contrôleur si le cas d'usage le justifie.

## Cas d'usage typiques

- Télégestion utilités/énergie.
- Agrégation de données terrain.
- Passerelle Modbus ↔ OPC UA ↔ MQTT.
- Automatisme compact avec supervision légère.

## Pièges Courants (Common Pitfalls)

1. Penser qu'une migration e!COCKPIT vers CODESYS est purement mécanique.
2. Exposer trop de variables brutes au lieu d'un contrat d'échange structuré.
3. Oublier les dépendances bibliothèques/runtime.
4. Sous-estimer les besoins de cybersécurité et de comportement en mode dégradé réseau.

## Liste de vérification (Checklist)

- [ ] Le projet est structuré en GVL / DUT / FB / PRG.
- [ ] Les variables exposées sont séparées des variables internes.
- [ ] Les bibliothèques CODESYS/WAGO requises sont identifiées.
- [ ] Les interfaces OPC UA / Modbus / MQTT sont documentées.
- [ ] Les tâches et performances runtime sont cohérentes avec la charge réelle.
