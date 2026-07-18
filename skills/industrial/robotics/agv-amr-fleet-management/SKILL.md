---
name: agv-amr-fleet-management
description: "Coordonner des flottes de robots mobiles (AGV/AMR), configurer les règles de trafic, gérer l'évitement de collisions et de blocages, et intégrer le gestionnaire de flotte aux WMS/MES."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [agv, amr, fleet-management, mobile-robotics, vda-5050, navigation, logistics, robotics]
  EVA:
    related_skills: [logistics-wms-inventory, cobot-human-collaboration]
---

# Gestion de Flottes de Robots Mobiles (AGV / AMR)

## Vue d'ensemble

Cette compétence guide le déploiement, la configuration et l'optimisation de flottes de véhicules guidés automatiquement (**AGV - Automated Guided Vehicles**) et de robots mobiles autonomes (**AMR - Autonomous Mobile Robots**) utilisés pour la manutention de charges en usine. Elle couvre l'implémentation du protocole d'échange standard **VDA 5050** entre les robots et le superviseur de flotte, la gestion des règles de circulation et de priorité aux intersections, l'évitement de situations de blocage (Deadlocks), et l'interfaçage du gestionnaire de flotte avec le WMS (gestion d'entrepôt) ou le MES (exécution de production) pour commander les ordres de transfert.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Choisir ou configurer un protocole de communication standardisé pour le pilotage d'une flotte multi-marques de robots mobiles (ex: **VDA 5050**).
- Définir des zones de priorité de passage, des couloirs de circulation à sens unique ou des zones d'exclusion (No-Go zones) sur la carte de navigation.
- Résoudre des problèmes d'embouteillage, de collisions évitées tardivement ou de blocages mutuels aux intersections.
- Interfacer un gestionnaire de flotte (Fleet Manager) avec les ordres logistiques d'un WMS ou les appels de matières d'un MES.
- Configurer les cycles de charge automatique de batterie (opportunistic charging) des robots.

## AGV vs AMR et Standard de Communication VDA 5050

*   **AGV (Véhicule Guidé)** : Suit une trajectoire fixe prédéfinie au sol (bande magnétique, fil de guidage, réflecteurs laser). S'arrête devant un obstacle et attend qu'il soit retiré.
*   **AMR (Robot Autonome)** : Calcule sa propre trajectoire à la volée à l'aide de capteurs embarqués (LiDAR, caméras 3D - SLAM). Capable de contourner de manière autonome un obstacle imprévu.

### Le protocole VDA 5050
Le standard de communication **VDA 5050** (élaboré par les constructeurs automobiles) utilise le protocole de messagerie léger **MQTT** avec des payloads JSON pour uniformiser les commandes de flottes multi-constructeurs :

```text
  ┌─────────────────┐                 Ordres de Transfert              ┌───────────────┐
  │   Système WMS   │ ───────────────────────────────────────────────► │ Fleet Manager │
  └─────────────────┘                                                  └───────┬───────┘
                                                                               │ MQTT
                         ┌───────────────────┬───────────────────┬─────────────┘
                         ▼ (JSON VDA 5050)   ▼ (JSON VDA 5050)   ▼ (JSON VDA 5050)
                   [ Robot AMR 1 ]     [ Robot AMR 2 ]     [ Robot AMR 3 ]
```

*   **Topics MQTT VDA 5050 standardisés** :
    *   `uagv/v2/Manufacturer/SerialNumber/order` : Envoi d'une séquence de points de passage (Nodes et Edges) au robot.
    *   `uagv/v2/Manufacturer/SerialNumber/state` : Le robot renvoie régulièrement son état (position X/Y, batterie, erreurs, avancement).
    *   `uagv/v2/Manufacturer/SerialNumber/visualization` : Position haute fréquence pour l'affichage cartographique 3D.

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Situations d'interblocage (Deadlocks) aux intersections :**
    *   *Erreur :* Laisser deux robots mobiles s'engager simultanément dans un couloir étroit à sens unique ou une intersection en même temps, chacun bloquant le passage de l'autre de manière indéfinie.
    *   *Correction :* Configurer des **ressources partagées exclusives (mutexes géographiques)** dans le gestionnaire de flotte. Un robot ne doit pas être autorisé à entrer dans une zone d'intersection si un autre robot possède déjà le droit d'accès (token) pour la traverser.

2.  **Perte de connexion Wi-Fi dans les allées métalliques de stockage :**
    *   *Erreur :* Le robot s'arrête en plein milieu d'une allée et se met en sécurité dès qu'il perd la connexion Wi-Fi à cause de l'effet cage de Faraday des racks métalliques.
    *   *Correction :* Installer des points d'accès Wi-Fi industriels de manière redondante avec un temps de transition (roaming) inférieur à 50ms, et configurer le robot pour qu'il puisse terminer sa tâche en cours (Order de nœuds déjà reçus) de manière autonome même en cas de perte réseau temporaire.

## Liste de vérification (Checklist)

- [ ] Les messages MQTT échangés respectent scrupuleusement la structure JSON de la norme VDA 5050.
- [ ] Les zones d'intersection critiques de la carte de circulation intègrent des règles d'exclusion mutuelle pour éviter les deadlocks.
- [ ] L'arrêt d'urgence de sécurité physique (SICK laser scanner de sécurité certifié) fonctionne indépendamment du logiciel de navigation.
- [ ] Les seuils de charge de batterie opportuniste (ex: rechargement dès que batterie < 30% et pas de tâche en cours) sont paramétrés.
- [ ] La communication du Fleet Manager est testée lors des phases de transition réseau (roaming Wi-Fi) dans tout l'entrepôt.

