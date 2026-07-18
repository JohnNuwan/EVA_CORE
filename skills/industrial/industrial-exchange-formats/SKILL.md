---
name: industrial-exchange-formats
description: "Structurer les formats d’échange industriels : PLCopen XML, L5X, XMY/XML, JSON métier, CSV SCADA, OPC UA models et exports techniques."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, exchange-formats, plcopen, l5x, xmy, json, csv, opc-ua, xml]
    related_skills: [industrial-programming-languages, plcopen-xml, rockwell-studio5000, schneider-unity, industrial-generator]
---

# Formats d’échange industriels

## Vue d'ensemble

Cette compétence couvre les formats d’échange structurants utilisés en industrie pour transporter du code, des modèles, des tags et des contrats de données entre outils, constructeurs et couches OT/IT : PLCopen XML, L5X, XMY/XML, JSON métier, CSV d’import SCADA et modèles OPC UA.

Le sujet central n’est pas le fichier lui-même. Le sujet central est la manière dont un format sert la migration, la standardisation, l’automatisation, la portabilité et la sémantique du système industriel.

## Quand l'utiliser
- Choisir un format d’échange pour migration, génération ou standardisation.
- Définir un contrat métier commun PLC ↔ SCADA ↔ MES.
- Construire des générateurs multi-constructeurs.
- Préparer des imports/exports de bibliothèques et de tags.
- Arbitrer entre un format outil propriétaire et un format neutre transverse.

À proscrire pour :
- Les seuls besoins de logique d’exécution sans échange entre outils.
- Les discussions de syntaxe XML/JSON sans réflexion de contrat métier.

## Positionnement détaillé des formats

### PLCopen XML
Usages :
- interchange IEC 61131-3 multi-constructeurs ;
- blocs, structures, bibliothèques ;
- portabilité relative sur écosystèmes compatibles.

Force :
- meilleur candidat neutre pour logique automate structurée.

### L5X
Usages :
- Rockwell Studio 5000 ;
- AOI, UDT, tags, routines ;
- automatisation autour de Logix.

Force :
- très utile dans l’écosystème Rockwell.

Limite :
- format constructeur, portabilité faible hors cible.

### XMY / XML Schneider
Usages :
- exports Control Expert / Unity ;
- DFB, DDT, structures projet.

Limite :
- format fortement lié à l’outil.

### JSON métier
Usages :
- contrat transverse ;
- génération multi-constructeurs ;
- mapping PLC ↔ SCADA ↔ MES ;
- intégration OT/IT ;
- standardisation.

Force :
- très bon pivot d’automatisation et de gouvernance sémantique.

### CSV SCADA
Usages :
- imports massifs tags/alarmes ;
- échanges simples ;
- consolidation rapide.

Limite :
- faible richesse sémantique si on le laisse sans contrat clair.

### Modèles OPC UA
Usages :
- interopérabilité sémantique ;
- modèles d’information ;
- structuration orientée UNS / IA / intégration.

Force :
- très pertinent pour architectures ouvertes et sémantiques.

## Critères de choix professionnels

### Critère 1 — Format neutre ou constructeur ?
- neutre : PLCopen XML, JSON métier, OPC UA ;
- constructeur : L5X, XMY/XML.

### Critère 2 — Import direct dans l’outil cible ?
- oui : L5X, XMY/XML, CSV selon outil, parfois PLCopen XML ;
- non direct : JSON métier, certains modèles OPC UA intermédiaires.

### Critère 3 — Richesse sémantique attendue
- faible à moyenne : CSV ;
- moyenne : L5X/XMY ;
- forte : JSON métier bien défini, OPC UA model, PLCopen XML structuré.

### Critère 4 — Vrai besoin
- migration ;
- génération ;
- standardisation ;
- contrat transverse ;
- intégration data.

## Architecture professionnelle recommandée

### Principe 1 — Séparer structure métier et rendu outil
- structure métier : JSON / modèle sémantique ;
- rendu outil : L5X / XMY / PLCopen XML / CSV / imports SCADA.

### Principe 2 — Versionner le contrat
Toujours versionner :
- schéma ;
- champs ;
- conventions ;
- mappings ;
- compatibilité ascendante.

### Principe 3 — Ne pas prendre un export outil pour un modèle canonique
Un export constructeur reflète la logique d’un outil. Ce n’est pas automatiquement un bon pivot transverse.

## Cas d’usage terrain

### Bibliothèque standard multi-constructeurs
- contrat JSON métier comme pivot ;
- génération vers PLCopen XML / L5X / XMY ;
- CSV ou SCADA import pour la supervision.

### Migration d’un constructeur à un autre
- format constructeur source pour l’extraction ;
- contrat métier intermédiaire ;
- génération vers la cible.

### Standard PLC ↔ SCADA ↔ MES
- JSON métier ou modèle OPC UA comme couche sémantique ;
- rendus spécifiques par outil côté exécution.

## Pièges Courants (Common Pitfalls)

1. Utiliser un format constructeur en pensant qu’il est portable.
2. Oublier le contrat sémantique derrière le format.
3. Mélanger structure technique et structure métier sans versionnement clair.
4. Vouloir tout faire passer par CSV alors que la richesse métier l’interdit.
5. Générer des artefacts sans stratégie d’import, de validation et de relecture dans l’outil cible.

## Checklist de validation finale
- [ ] Le format cible est choisi selon le vrai besoin d’import/export.
- [ ] Le versionnement du contrat est explicite.
- [ ] La distinction structure métier / structure outil est claire.
- [ ] Les mappings PLC ↔ SCADA ↔ MES sont documentés.
- [ ] La stratégie d’import et de validation dans l’outil cible est prévue.
- [ ] Le format choisi correspond au niveau de richesse sémantique attendu.
