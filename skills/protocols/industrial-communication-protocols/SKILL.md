---
name: industrial-communication-protocols
description: "Mettre en œuvre et optimiser les protocoles de communication industrielle (OPC-UA, MQTT, Modbus, Profinet) pour l'interopérabilité et l'automatisation des systèmes connectés."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [protocols, opcua, mqtt, modbus, profinet, industrial-communication, iot, automation]
    related_skills: [industry-4-0-advanced-architecture, plc-connectivity, interoperability-of-industrial-systems]
---

# Protocoles de Communication Industrielle

## Vue d'ensemble

Cette compétence couvre les **protocoles de communication industrielle** essentiels à l'intégration des systèmes automatisés et connectés : OPC-UA, MQTT, Modbus, Profinet, EtherNet/IP et IO-Link. Elle fournit les bases théoriques, les configurations pratiques, les bonnes pratiques de sécurité et les cas d'usage pour chaque protocole.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De configurer une communication entre un PLC et un SCADA via OPC-UA.
- D'intégrer des capteurs IoT via MQTT dans un système de supervision existant.
- De lire/écrire des données Modbus depuis un script Python.
- De sécuriser les communications industrielles (TLS, authentification).
- De choisir le protocole adapté à un cas d'usage (latence, volume, sécurité).

---

## 1. Tableau Comparatif des Protocoles

| Protocole | Type | Topologie | Transport | Sécurité | Latence | Volume |
|:---|:---|:---|:---|:---|:---|:---|
| **Modbus RTU/TCP** | Requête/Réponse | Maître/Esclave | Série (RS-485) ou TCP | Faible (aucune native) | < 10 ms | Faible |
| **OPC-UA** | Client/Serveur ou Pub/Sub | Flexible | TCP (port 4840) | Haute (X.509, Auth) | < 50 ms | Moyen |
| **MQTT** | Publication/Souscription | Broker centralisé | TCP (port 1883/8883) | Haute (TLS + Auth) | < 100 ms | Élevé |
| **Profinet** | Cyclique/acyclique | RT/IRT | Ethernet dédié | Faible (segmenté) | < 1 ms (IRT) | Moyen |
| **EtherNet/IP** | CIP (Common Industrial Protocol) | Producteur/Consommateur | Ethernet standard | Moyenne | < 10 ms | Moyen |
| **IO-Link** | Point-à-point | Maître/Device | 3 fils (M12) | Faible (physique) | < 5 ms | Très faible |

---

## 2. OPC-UA (IEC 62541)

### 2.1 Architecture

```
[PLC / Capteur] ←→ [Serveur OPC-UA] ←→ [Client OPC-UA (SCADA/MES)]
                         ↓
               [Découverte, Historisation,
                Alarmes, Méthodes]
```

### 2.2 Configuration d'un Serveur OPC-UA avec open62541

```bash
# Installation de la librairie C
git clone https://github.com/open62541/open62541.git
cd open62541 && mkdir build && cd build
cmake .. -DUA_ENABLE_AMALGAMATION=ON
make && sudo make install
```

**Client OPC-UA en Python :**

```python
from opcua import Client

client = Client("opc.tcp://plc.actemium.local:4840")
client.connect()
print("Connecté au serveur OPC-UA")

# Lecture d'une variable
var = client.get_node("ns=2;i=1001")  # Identifiant du nœud
value = var.get_value()
print(f"Valeur lue : {value}")

# Écriture
var.set_value(42.5)
print("Écriture réussie")

client.disconnect()
```

### 2.3 Modèle d'Information OPC-UA

```yaml
ObjectTypes:
  MotorType:
    Variables:
      - Speed: { type: DOUBLE, access: R/W }
      - Temperature: { type: DOUBLE, access: R }
      - Status: { type: StatusEnum, access: R }
    Methods:
      - Start(): { }
      - Stop(): { }
      - SetSpeed(Speed: DOUBLE): { }
```

---

## 3. MQTT (Message Queuing Telemetry Transport)

### 3.1 Configuration Broker Mosquitto

```bash
# Installation
sudo apt install mosquitto mosquitto-clients

# Configuration TLS (mosquitto.conf)
listener 8883
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
require_certificate true
allow_anonymous false
password_file /etc/mosquitto/passwd
```

### 3.2 Publication MQTT avec Sparkplug B

```python
import paho.mqtt.client as mqtt
from sparkplug_b import *

def publish_sensor_data(client, sensor_id, temperature, pressure):
    """Publie les données capteur au format Sparkplug B."""
    payload = SparkplugBPayload()
    payload.add_metric("temperature", MetricDataType.Double, temperature)
    payload.add_metric("pressure", MetricDataType.Double, pressure)
    payload.add_metric("timestamp", MetricDataType.DateTime, int(time.time() * 1000))

    topic = f"spBv1.0/actemium/NDATA/{sensor_id}"
    client.publish(topic, payload.serialize(), qos=1)
```

---

## 4. Modbus (RTU / TCP)

**Exemple de lecture Modbus TCP avec pymodbus :**

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient("192.168.1.100", port=502)
client.connect()

# Lecture de 10 registres (holding registers) à partir de l'adresse 0
result = client.read_holding_registers(0, 10, unit=1)
if not result.isError():
    print(f"Registres : {result.registers}")

# Écriture d'un registre
client.write_register(5, 1500, unit=1)

client.close()
```

---

## 5. Sécurité des Communications

| Protocole | Mesure de Sécurité | Implémentation |
|:---|:---|:---|
| **Modbus TCP** | Tunnel VPN ou TLS | OpenVPN, stunnel |
| **OPC-UA** | Certificats X.509 + Auth | Gérer dans le serveur UA |
| **MQTT** | TLS + Auth client | Certificats + fichier passwd |
| **Profinet** | Segmentation physique | VLAN, pare-feu OT |
| **IO-Link** | Sécurité physique | Câble blindé, armoire verrouillée |

---

## 6. Pièges Courants

1. **Modbus sans sécurité :**
   - *Erreur* : Modbus TCP ouvert sur le réseau IT sans protection.
   - *Correction* : Tunnel VPN ou passerelle OPC-UA sécurisée.

2. **MQTT avec QoS inadapté :**
   - *Erreur* : QoS 2 pour tous les messages (surcharge réseau).
   - *Correction* : QoS 0 pour les mesures, QoS 1 pour les alarmes, QoS 2 pour les ordres.

3. **Namespaces OPC-UA non structurés :**
   - *Erreur* : Variables publiées avec des identifiants numériques sans signification.
   - *Correction* : Adoptez une structure hiérarchique claire avec noms lisibles (ex: `Line1/Motor3/Temperature`).

---

## Liste de vérification

- [ ] Le protocole est choisi selon les critères (latence, volume, sécurité, compatibilité matérielle).
- [ ] La communication est testée (lecture/écriture) entre client et serveur.
- [ ] Les mesures de sécurité (TLS, VPN, certificats) sont en place pour l'accès externe.
- [ ] Les noms de variables OPC-UA sont structurés de manière hiérarchique et lisible.
- [ ] Les topics MQTT suivent une convention de nommage standardisée (Sparkplug B recommandé).
- [ ] Les timeouts et mécanismes de reconnexion sont configurés.
- [ ] La redondance (serveur secondaire, broker cluster) est implémentée si nécessaire.
