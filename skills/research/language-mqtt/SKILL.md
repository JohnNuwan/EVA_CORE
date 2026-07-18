---
name: language-mqtt
title: "Doctorat — MQTT (Message Queuing Telemetry Transport)"
description: "Compétence niveau docteur en MQTT. Couvre MQTT 3.1.1/5.0, QoS, retained messages, wildcards, will messages, session state, broker internals (Mosquitto, EMQX, VerneMQ), topic design, security TLS/SSL, auth, bridging, clustering, et IoT patterns."
category: research
lang: fr
---

# Doctorat : MQTT

## Présentation
MQTT (Message Queuing Telemetry Transport) est un protocole de messagerie publish/subscribe léger, conçu pour les appareils contraints et les réseaux à faible bande passante. Développé par Andy Stanford-Clark (IBM) et Arlen Nipper (Cirrus Logic) en 1999, il est standardisé par OASIS depuis 2013 (MQTT 3.1.1), avec une version majeure 5.0 depuis 2019. MQTT est devenu le protocole standard pour l'IoT (Internet des Objets), la domotique, l'industrie 4.0, et la télémétrie.

## Histoire et Contexte
- 1999 : Développement par IBM et Cirrus Logic
- 2010 : Version 3.1 publique libre de droits
- 2013 : OASIS standard — MQTT 3.1.1
- 2017 : ISO/IEC 20922 — norme internationale
- 2019 : MQTT 5.0 — évolution majeure OASIS
- 2023-2025 : Adoption massive, Sparkplug pour l'industrie

## Architecture du Protocole
- **Architecture Publish/Subscribe** : Clients connectés à un broker
- **Broker** : Serveur central gérant connexions et routage
- **Clients** : Appareils ou applications qui publient/s'abonnent
- **Topics** : Hiérarchie de sujets (ex: sensor/temperature/room1)
- **TCP/IP** : Port 1883 (non chiffré), 8883 (TLS)
- **MQTT-SN** : Variante pour réseaux non TCP
- **CONNECT/CONNACK** : Handshake de connexion
- **PUBLISH/PUBACK/PUBREC/PUBREL/PUBCOMP** : Flux de publication
- **SUBSCRIBE/SUBACK** : Abonnement
- **PINGREQ/PINGRESP** : Keep-alive

## Types et Concepts
- **Message MQTT** : En-tête fixe + en-tête variable + payload
- **Packet types** : 14 types (3.1.1), 16 types (5.0)
- **Topic** : Chaîne UTF-8 hiérarchique (/ séparateur)
- **Wildcards** : + (un niveau), # (multi-niveaux)
- **QoS 0** : Au plus une fois — pas de garantie
- **QoS 1** : Au moins une fois — peut dupliquer
- **QoS 2** : Exactement une fois — le plus sûr
- **Session** : État persistant du client sur le broker
- **Will message** : Message de dernière volonté
- **Retained message** : Dernière valeur conservée
- **Properties (MQTT 5.0)** : Métadonnées supplémentaires

## Mémoire et Performances
- **Faible empreinte** : En-tête de 2 octets minimum
- **Broker memory** : Gestion des sessions et files d'attente
- **Persistent sessions** : Messages QoS 1/2 stockés
- **Throughput** : EMQX peut traiter des millions de msg/s
- **Message expiry** (MQTT 5.0) : Expiration automatique
- **Topic alias** (MQTT 5.0) : Alias pour réduire la taille

## Écosystème et Outils
- **Eclipse Mosquitto** : Broker Open Source de référence
- **EMQX** : Broker distribué haute disponibilité (Erlang)
- **VerneMQ** : Broker distribué haute performance (Erlang)
- **HiveMQ** : Broker enterprise (Java)
- **NanoMQ** : Broker léger pour edge
- **Mosquitto clients** : mosquitto_pub, mosquitto_sub
- **MQTTX** : Client GUI cross-platform
- **Node-RED** : Flow programming avec MQTT natif
- **Sparkplug** : Spécification Industrie 4.0

## Concurrence et Parallélisme
- **Pub/Sub async** : Modèle intrinsèquement asynchrone
- **Broker multi-threadé** : Tous les brokers majeurs
- **EMQX** : Millions de connexions par nœud
- **Shared subscriptions** (MQTT 5.0) : Load balancing
- **Session state** : État persistant par session
- **Offline queuing** : Messages stockés pour clients déconnectés
- **Flow control** (MQTT 5.0) : Limitation du throughput

## Patterns Avancés
- **Sparkplug** : Tag-driven Industrie 4.0
- **State via retained** : État actuel via messages retenus
- **Birth/Death certificates** : Messages de vie/mort
- **Request/Response** (MQTT 5.0) : Response topic
- **Bridging** : Connexion entre brokers
- **Cluster** : Plusieurs nœuds broker
- **Topic tree design** : Conception de l'arborescence
- **Edge filtering** : Filtrage en edge avant envoi cloud
- **Store and forward** : Stockage + transmission différée

## Sécurité
- **TLS/SSL** : Port 8883 (MQTT over TLS)
- **TLS mutual** : Client certificates (mTLS)
- **Username/Password** : Authentification basique
- **JWT / OAuth** : MQTT 5.0 — auth via propriétés
- **ACL** : Contrôle d'accès par topic
- **Payload encryption** : Chiffrement de bout en bout
- **Client ID spoofing** : Éviter IDs prévisibles
- **Rate limiting** : Limitation des messages par client

## Applications Industrielles
- **Industrie 4.0** : Capteurs, maintenance prédictive
- **Smart Home** : Home Assistant, ESPHome, TASMOTA
- **Smart City** : Éclairage, déchets, parkings
- **Agriculture connectée** : Capteurs de sol
- **Énergie** : Smart metering, réseaux électriques
- **Santé connectée** : Moniteurs médicaux
- **Automobile connectée** : Télémétrie, OTA
- **Logistique** : Suivi de flotte
- **Bâtiment intelligent** : CVC, éclairage, sécurité

## Veille Technologique
- **OASIS MQTT** : Comité technique officiel
- **MQTT.org** : Site officiel
- **Eclipse MQTT** : Paho, Mosquitto
- **HiveMQ Blog** : Articles techniques
- **EMQX Blog** : Nouvelles versions, benchmarks
- **Conférences** : MQTT Summit (Eclipse)
- **Standards** : MQTT 3.1.1 (ISO 20922), MQTT 5.0, Sparkplug