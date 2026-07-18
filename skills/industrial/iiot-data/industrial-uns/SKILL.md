---
name: industrial-uns
description: "Concevoir une architecture UNS et des topics MQTT."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [uns, unified-namespace, mqtt, isa-95, broker, industrial-architecture]
    related_skills: [isa95-modelling, sparkplug-b, industrial-edge, opc-ua-scanner, mes-integration]
---

# Unified Namespace (UNS) & Architecture ISA-95

## Vue d'ensemble

Dans les architectures industrielles traditionnelles (la pyramide de l'automatisation), les données transitent verticalement étape par étape : Capteurs → Automates → SCADA → MES → ERP. Cela crée des silos de données.

Le **Unified Namespace (UNS)** propose une architecture plate centralisée en temps réel. C'est un tronc commun où tous les composants de l'entreprise (OT et IT) peuvent s'abonner et publier des données. Il repose généralement sur un courtier MQTT et suit la structure hiérarchique définie par la norme **ISA-95**.

Cette compétence guide l'agent Helios pour modéliser, concevoir et structurer l'architecture des données d'un UNS.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'organiser ou de structurer les sujets (topics) d'un broker MQTT pour une usine.
- D'intégrer des passerelles de données ou de configurer des ponts MQTT (Bridges) vers un UNS.
- D'appliquer le standard hiérarchique ISA-95 sur les échanges de données d'un atelier.
- De modéliser des payloads de messages décrivant l'état des lignes de production.

**Ne pas utiliser pour :**
- La programmation de bas niveau de cartes d'entrées/sorties ou de blocs automates (utiliser `siemens-scl` ou `rockwell-studio5000`).

---

## 1. Structure de Sujets (Topics) MQTT selon la norme ISA-95

L'UNS exige un nommage de sujet strict et standardisé représentant la structure physique de l'entreprise :

```text
[Entreprise]/[Site]/[Atelier]/[Ligne]/[Equipement]/[Namespace]/[Variable]
```

### Exemple pratique de topics MQTT :

* **Données d'état en temps réel d'un moteur :**
  `actemium/paris/embouteillage/ligne1/moteur1/state/speed`
* **Événements et alarmes de la ligne :**
  `actemium/paris/embouteillage/ligne1/events/alarm`
* **Indicateurs de performance agrégés par le MES :**
  `actemium/paris/embouteillage/ligne1/kpi/oee`

---

## 2. Payload Standardisé en JSON pour l'UNS

Dans l'UNS, chaque équipement doit publier son état sous un format JSON standardisé comprenant les valeurs, les unités, l'horodatage et la qualité de la mesure :

```json
{
  "timestamp": "2026-06-12T13:50:00Z",
  "metrics": {
    "speed": {
      "value": 1452.0,
      "unit": "RPM",
      "quality": "Good"
    },
    "temperature": {
      "value": 45.2,
      "unit": "C",
      "quality": "Good"
    },
    "status": {
      "value": "RUNNING",
      "unit": "state",
      "quality": "Good"
    }
  }
}
```

---

## 3. Configuration d'un Pont (Bridge) MQTT pour l'UNS (Mosquitto)

Pour relier un courtier local d'atelier au UNS de l'entreprise, on configure un pont réseau. Voici un exemple de configuration de pont dans le fichier `mosquitto.conf` :

```text
# Définition de la connexion vers le broker UNS Central
connection uns-central-bridge
address 192.168.1.10:1883
clientid bridge-atelier1

# Authentification (si nécessaire)
username user_bridge
password password_bridge

# Redirection des topics de l'atelier local vers le serveur central
# Topic local: atelier1/ligne1/# -> Central: actemium/paris/atelier1/ligne1/#
topic # out 2 local/ actemium/paris/
```

---

## Pièges Courants

1. **Création de sujets MQTT plats (Flat Topics) :**
   * *Erreur :* Publier toutes les variables au même niveau sans hiérarchie (ex: `moteur1_speed`, `moteur1_temp`). Cela rend la maintenance impossible dès que le nombre de capteurs augmente.
   * *Correction :* Suivre strictement la taxonomie ISA-95 par répertoires imbriqués.

2. **Absence de notion d'état de connexion (Last Will and Testament) :**
   * *Erreur :* Ne pas savoir si une machine s'est déconnectée brutalement du réseau car le dernier état publié reste figé sur le broker.
   * *Correction :* Configurer le paramètre *LWT (Last Will and Testament)* sur les clients MQTT pour forcer le broker à publier un statut `OFFLINE` sur le topic de l'équipement si la connexion TCP est coupée.

---

## Liste de vérification (Checklist)

- [ ] L'arbre des sujets (topics) suit la structure hiérarchique ISA-95 (Entreprise/Site/Atelier/Ligne/Machine).
- [ ] Les payloads JSON contiennent systématiquement l'horodatage (`timestamp`) et le statut de qualité des données (`quality`).
- [ ] Le broker MQTT central possède des politiques d'accès (ACL) configurées pour isoler et protéger les sujets en écriture.
- [ ] Les clients MQTT configurés utilisent le mécanisme de testament (*Last Will and Testament*) pour notifier les pertes de connexion.

