---
name: multi-vendor-industrial-automation
description: "Use when the task spans multiple PLC/DCS vendors or the user wants a cross-vendor automation comparison, learning path, or standardization approach."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, automation, plc, dcs, siemens, rockwell, beckhoff, omron, schneider, ignition, interoperability]
    related_skills: [industrial-communication-protocols, interoperability-of-industrial-systems]
---

# Multi-vendor Industrial Automation

## Vue d'ensemble

Cette compétence sert de cadre quand une demande dépasse un seul constructeur automate et demande une lecture transversale de l'écosystème industriel. Elle aide à comparer, cartographier et standardiser plusieurs plateformes : Siemens, Rockwell, Beckhoff, Omron, Schneider, DCS de procédé et couches SCADA/OT-IT comme Ignition.

Le but n'est pas de remplacer les compétences constructeur spécialisées, mais de fournir :
- une vue d'ensemble cohérente par famille technologique ;
- une méthode pour comparer des plateformes sans les confondre ;
- une stratégie de standardisation multi-vendeurs ;
- une base pour décider quoi apprendre, quoi déployer, et quoi interfacer.

Référence utile : voir `references/vendor-coverage-matrix.md` pour la matrice de couverture et les axes d'approfondissement.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- d'"apprendre les autres automates" ou d'élargir la couverture au-delà d'un constructeur ;
- de comparer plusieurs familles PLC/DCS/SCADA ;
- de préparer un standard multi-constructeurs ;
- de concevoir une architecture Siemens + Rockwell + Ignition + autres ;
- de bâtir une feuille de route de montée en compétence industrielle ;
- de traduire un besoin entre plusieurs environnements d'ingénierie.

Ne pas utiliser pour :
- une question purement mono-constructeur déjà couverte par une skill dédiée ;
- une simple lecture/écriture protocolaire isolée sans enjeu multi-vendeur.

## Familles à distinguer explicitement

### 1. PLC machine / automatisme discret
- Siemens TIA Portal / S7
- Rockwell Studio 5000 / Logix
- Beckhoff TwinCAT / PC Control
- Omron Sysmac / NJ-NX
- Schneider Control Expert / M340-M580

### 2. DCS / procédé continu
- Emerson DeltaV
- Yokogawa CENTUM
- Honeywell Experion
- ABB 800xA
- Siemens PCS 7 / PCS neo

### 3. SCADA / couche supervision et données
- Ignition
- WinCC / Historian / MES adjacents
- MQTT / Sparkplug B / UNS
- OPC UA / interop OT-IT

## Méthode de réponse recommandée

### Étape 1 — classifier la demande
Toujours commencer par classer le besoin dans une ou plusieurs catégories :
- logique machine ;
- motion ;
- batch / procédé ;
- supervision ;
- protocole ;
- standardisation / migration.

### Étape 2 — nommer les environnements d'ingénierie
Toujours citer l'outil ou l'écosystème cible, pas seulement la marque :
- Siemens → TIA Portal / PCS 7 / PCS neo ;
- Rockwell → Studio 5000 ;
- Beckhoff → TwinCAT 3 ;
- Omron → Sysmac Studio ;
- Schneider → Control Expert ;
- DCS → DeltaV / CENTUM / Experion / 800xA.

### Étape 3 — séparer 3 couches
Structurer l'analyse en trois couches :
1. plateforme de contrôle ;
2. protocole / bus / interop ;
3. exposition SCADA / MES / data platform.

### Étape 4 — conclure par une recommandation d'usage
Toujours finir par :
- quoi garder ;
- quoi standardiser ;
- quoi surveiller ;
- quoi apprendre ensuite.

## Axes d'analyse multi-vendeurs

### A. Logique et modèle de programmation
Comparer :
- IEC 61131-3 pur vs extensions constructeur ;
- approche tag-based vs adressage mémoire ;
- FB/AOI/DFB/UDT/DDT ;
- séquenceurs, motion, batch.

### B. Réseau et interopérabilité
Comparer :
- PROFINET, EtherNet/IP, EtherCAT, FINS, ADS ;
- OPC UA, MQTT, Sparkplug B ;
- field level vs data layer OT-IT.

### C. Architecture projet
Comparer :
- mono-machine ;
- ligne multi-machines ;
- site multi-ateliers ;
- process continu / batch ;
- architecture UNS / Historian / MES.

## Standards de formulation à respecter

Quand l'utilisateur demande une montée en compétence globale :
- présenter d'abord les grandes familles ;
- ensuite la couverture déjà acquise ;
- enfin les zones encore à approfondir.

Quand l'utilisateur demande "apprends tout" :
- ne jamais prétendre couvrir littéralement 100 % du marché ;
- expliciter les écosystèmes désormais couverts ;
- lister les familles encore manquantes ou à creuser ;
- proposer une progression en vagues ou priorités.

## Pièges Courants (Common Pitfalls)

1. **Confondre PLC, DCS et SCADA.**
   * Correction : toujours préciser s'il s'agit de contrôle machine, contrôle procédé ou supervision/data.

2. **Comparer des protocoles terrain et des couches data comme s'ils jouaient le même rôle.**
   * Correction : séparer clairement temps réel machine (PROFINET, EtherNet/IP, EtherCAT) et couche données/interop (OPC UA, MQTT, Sparkplug B).

3. **Répondre par marque sans nommer l'outil d'ingénierie.**
   * Correction : citer systématiquement Studio 5000, TIA Portal, TwinCAT, Sysmac, Control Expert, etc.

4. **Sur-promettre la couverture.**
   * Correction : annoncer ce qui est bien couvert, ce qui est partiellement couvert et ce qui reste à approfondir.

5. **Donner une comparaison abstraite sans recommandation opérationnelle.**
   * Correction : finir avec "à garder / à déployer / à préparer / à apprendre ensuite".

## Liste de vérification (Checklist)

- [ ] La réponse distingue bien PLC, DCS et SCADA.
- [ ] Les protocoles terrain et les protocoles d'interop sont séparés.
- [ ] Chaque constructeur est associé à son environnement d'ingénierie.
- [ ] Les points forts/faibles sont formulés par usage, pas par préférence vague.
- [ ] La réponse indique explicitement les prochaines priorités d'apprentissage ou d'adoption.
- [ ] La couverture restante ou les manques sont signalés honnêtement.
