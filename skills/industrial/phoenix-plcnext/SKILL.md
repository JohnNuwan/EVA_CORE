---
name: phoenix-plcnext
description: "Configurer PLCnext Engineer et concevoir des architectures PLCnext ouvertes et edge."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [plcnext, phoenix-contact, edge, software-defined-control, plcnext-engineer, virtual-plc, opc-ua, mqtt]
    related_skills: [industrial-protocols, industrial-communication-protocols, plcopen-xml, interoperability-of-industrial-systems]
---

# Phoenix Contact PLCnext

## Vue d'ensemble

Cette compétence couvre PLCnext Technology comme plateforme d'automatisation ouverte, edge et orientée software-defined control. Elle aide à structurer des projets PLCnext Engineer, à séparer logique automate et services edge, et à concevoir des intégrations propres vers OPC UA, MQTT et autres couches OT/IT.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Structurer un projet PLCnext Engineer.
- Concevoir une architecture PLC + edge computing.
- Préparer un usage Virtual PLCnext Control.
- Connecter PLCnext à OPC UA, MQTT ou services externes.
- Définir le comportement d'un contrôleur ouvert en cas de perte réseau.

## Architecture recommandée

- Contrôle temps réel local dans la couche automate.
- Services data et intégration dans la couche edge.
- Exposition externe via OPC UA / MQTT / API.
- Mode dégradé explicite si la connectivité IT disparaît.

## Bonnes pratiques

- Ne jamais faire dépendre le contrôle critique d'un service IT non déterministe.
- Isoler les dépendances logicielles externes et geler leurs versions.
- Documenter les flux entrants/sortants et les politiques de reprise.
- Penser cybersécurité OT/IT dès la conception.

## Cas d'usage typiques

- Passerelle OT/IT avancée.
- Nœud edge industriel.
- Contrôleur virtualisé ou software-defined.
- Intégration locale vers cloud, historian ou MES.

## Pièges Courants (Common Pitfalls)

1. Mélanger logique temps réel et appels externes non maîtrisés.
2. Sous-estimer la gouvernance logicielle des composants/packages.
3. Utiliser PLCnext comme simple PLC traditionnel sans tirer parti de son ouverture.
4. Oublier de définir un comportement sûr en mode dégradé réseau.

## Liste de vérification (Checklist)

- [ ] Le projet sépare logique automate et services edge.
- [ ] Les interfaces OPC UA / MQTT / API sont documentées.
- [ ] Le comportement en cas de perte réseau est défini.
- [ ] Les dépendances logicielles externes sont maîtrisées.
- [ ] L'architecture tient compte du potentiel virtual PLC/software-defined.
- [ ] Les contraintes de cybersécurité OT/IT sont intégrées.
