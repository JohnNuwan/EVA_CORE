---
name: industrial-edge
description: "Développer des scripts Edge et des flux Node-RED."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [edge, edge-computing, node-red, gateway, python, iot, industrial-automation]
    related_skills: [industrial-uns, plc-connectivity, industrial-protocols, opc-ua-scanner]
---

# Edge Computing & IoT Industrielle (Node-RED & Passerelles Edge)

## Vue d'ensemble

Le **Edge Computing** consiste à traiter les données directement au plus près de la source (l'atelier de fabrication), plutôt que de les envoyer brutes vers des serveurs cloud ou des serveurs IT distants. Cela permet d'économiser de la bande passante, de réduire la latence et d'assurer une continuité de service même en cas de coupure Internet.

Les passerelles Edge industrielles (ex: Siemens IOT2050, Raspberry Pi industriels, Advantech) exécutent souvent des applications conteneurisées (ex: Docker) combinant des scripts Python personnalisés et l'outil de programmation visuelle **Node-RED**.

Cette compétence guide l'agent EVA pour développer des flux Node-RED et concevoir des scripts de traitement à la périphérie du réseau (Edge).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir ou de modifier un script Python de filtrage de données s'exécutant sur une passerelle locale.
- De configurer ou d'écrire des scripts JavaScript pour des nœuds "Function" dans Node-RED.
- D'intégrer des flux d'acquisition d'entrées/sorties (ex: Modbus, OPC-UA) dans Node-RED et de les exporter.
- D'optimiser l'utilisation des ressources (RAM, CPU, stockage) sur un équipement Edge à ressources limitées.

**Ne pas utiliser pour :**
- Configurer les détails physiques d'une carte électronique ou d'un microcontrôleur bare-metal sans OS.

---

## 1. Programmation de Nœuds Function sous Node-RED

Dans Node-RED, le nœud *Function* permet d'exécuter du code JavaScript sur le message entrant (`msg`). Le code doit être rapide et non bloquant.

### Exemple de filtrage et de reformatage de payload dans Node-RED :

```javascript
// Le message d'entrée contient msg.payload (ex: valeur de capteur brute)
let rawValue = msg.payload.value;

// Filtrage : Éliminer les bruits ou fausses valeurs aberrantes
if (rawValue < 0 || rawValue > 100) {
    node.warn("Valeur rejetée car hors limites : " + rawValue);
    return null; // Stoppe le flux pour ce message
}

// Reformatage du message pour l'UNS
msg.payload = {
    timestamp: new Date().toISOString(),
    sensorName: "Sensor_Temp_01",
    temperature_celsius: parseFloat(rawValue.toFixed(2)),
    status: "OK"
};

// Transmettre le message au nœud suivant du flux
return msg;
```

---

## 2. Script Python Edge de Décimation de Données (Deadband)

Pour éviter de saturer le réseau avec des mesures redondantes (ex: une température constante à 20°C toutes les secondes), les scripts Edge appliquent une "zone morte" (Deadband). La donnée n'est envoyée au système central que si elle varie de plus d'un certain seuil par rapport à la dernière valeur envoyée.

```python
import time
import json
import paho.mqtt.client as mqtt

# Configuration
LAST_SENT_VALUE = None
DEADBAND_THRESHOLD = 0.5 # Envoyer si la température varie de +/- 0.5 °C
PUBLISH_INTERVAL = 60    # Forcer un envoi toutes les 60 secondes max (Heartbeat)
LAST_SENT_TIME = 0

client = mqtt.Client()
client.connect("192.168.1.10", 1883)

def process_sensor_value(current_value):
    global LAST_SENT_VALUE, LAST_SENT_TIME
    
    current_time = time.time()
    
    # Règle 1: Première valeur
    # Règle 2: Variation supérieure au seuil
    # Règle 3: Délai maximum atteint (Heartbeat)
    if (LAST_SENT_VALUE is None or 
        abs(current_value - LAST_SENT_VALUE) >= DEADBAND_THRESHOLD or 
        (current_time - LAST_SENT_TIME) >= PUBLISH_INTERVAL):
        
        payload = {
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "value": current_value
        }
        
        # Envoi au broker central
        client.publish("EVA/edge/sensor1", json.dumps(payload))
        
        # Mise à jour des états
        LAST_SENT_VALUE = current_value
        LAST_SENT_TIME = current_time
        print(f"Valeur envoyée : {current_value}")
```

---

## Pièges Courants

1. **Variables globales mal gérées dans Node-RED :**
   * *Erreur :* Déclarer une variable globale standard (`var x = 1;`) dans un nœud Function en espérant qu'elle persiste aux prochains messages. Elle est détruite à chaque exécution du nœud.
   * *Correction :* Utiliser l'API de contexte de Node-RED pour stocker des états persistants : `context.set('compteur', valeur)` et `context.get('compteur')`.

2. **Écritures disque intensives sur cartes SD :**
   * *Erreur :* Enregistrer des logs ou des bases de données locales directement sur la carte SD de la passerelle Edge toutes les secondes. Cela détruit la carte SD en quelques mois par usure des cycles d'écriture.
   * *Correction :* Écrire les fichiers temporaires dans la mémoire RAM (`/tmp` ou `tmpfs` sous Linux) ou utiliser des bases de données optimisées en écriture.

---

## Liste de vérification (Checklist)

- [ ] Les scripts JavaScript dans Node-RED renvoient toujours l'objet `msg` (ou `null` pour filtrer) et ne bloquent pas le thread principal.
- [ ] Les variables persistantes dans Node-RED utilisent les objets `context`, `flow`, ou `global`.
- [ ] Le script Python Edge applique un algorithme de zone morte (Deadband) ou d'échantillonnage pour ne pas saturer la bande passante réseau.
- [ ] Aucun stockage persistant à haute fréquence n'est réalisé directement sur un support fragile comme une carte SD classique (utiliser le stockage RAM /tmpfs).

