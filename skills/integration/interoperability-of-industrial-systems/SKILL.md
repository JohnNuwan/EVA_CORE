---
name: interoperability-of-industrial-systems
description: "Concevoir des architectures industrielles intégrées combinant IA, RAG, protocoles OT/IT et normes ISO pour l'interopérabilité des systèmes connectés."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [interoperability, integration, it-ot, opcua, mqtt, iso, industry40, mes, erp, scada]
    related_skills: [industrial-communication-protocols, industry-4-0-advanced-architecture, combining-industry40-security-iso, iso-standards-for-industry]
---

# Interopérabilité des Systèmes Industriels

## Vue d'ensemble

Cette compétence fournit les **méthodes et architectures** pour assurer l'interopérabilité entre les systèmes industriels hétérogènes : MES, ERP, SCADA, PLC, capteurs IoT, IA/LLM. L'interopérabilité est le défi majeur de l'Industrie 4.0, où des équipements de différentes générations, protocoles et constructeurs doivent communiquer et échanger des données de manière fluide et sécurisée.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De faire communiquer des systèmes industriels hétérogènes (MES ↔ ERP, SCADA ↔ PLC).
- D'intégrer l'IA et les LLM dans un environnement de production existant.
- De normaliser les échanges de données entre partenaires industriels.
- De concevoir une architecture middleware pour l'unification des flux.
- D'auditer l'interopérabilité actuelle d'un site et de proposer des améliorations.

---

## 1. Niveaux d'Interopérabilité

### 1.1 Matrice d'Interopérabilité

| Niveau | Description | Technologie | Exemple |
|:---|:---|:---|:---|
| **Physique** | Connectivité des équipements | RS-485, Ethernet, IO-Link | Capteur ↔ PLC |
| **Réseau** | Transport des données | TCP/IP, Profinet, EtherNet/IP | PLC ↔ SCADA |
| **Protocole** | Format des messages | OPC-UA, Modbus, MQTT | SCADA ↔ MES |
| **Sémantique** | Signification des données | ISA-95, RAMI 4.0, B2MML | MES ↔ ERP (ordres de fabrication) |
| **Organisationnel** | Processus métier | BPMN, workflow | ERP ↔ Fournisseur (EDI) |

### 1.2 Problèmes Courants d'Interopérabilité

| Problème | Système A | Système B | Solution |
|:---|:---|:---|:---|
| **Protocole incompatible** | Modbus RTU (série) | OPC-UA (TCP) | Passerelle protocolaire |
| **Sémantique différente** | Unité °C | Unité °F | Transformation middleware |
| **Granularité temporelle** | Données toutes les 1s | Données toutes les 5min | Agrégation / interpolation |
| **Sécurité incompatible** | Aucune (Modbus) | TLS (MQTT) | Tunnel VPN + passerelle sécurisée |
| **Version de format** | XML (B2MML v4) | JSON (API REST) | Adaptateur format |

---

## 2. Architecture d'Intégration

### 2.1 Architecture Middleware Unifiée

```
┌─────────┐ ┌─────────┐ ┌─────────┐
│  PLC A  │ │  PLC B  │ │  IoT    │
│ (Modbus)│ │(Profinet)│ │ (MQTT)  │
└────┬────┘ └────┬────┘ └────┬────┘
     │           │           │
     └───────────┼───────────┘
                 ▼
     ┌─────────────────────┐
     │   PASSELLE / BUS    │
     │  OPC-UA Gateway     │
     │  Kafka / MQTT       │
     └──────────┬──────────┘
                 │ OPC-UA / REST
     ┌───────────┼───────────┐
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ SCADA   │ │ MES     │ │ IA/LLM  │
│ (OPC-UA)│ │(REST)   │ │ (REST)  │
└─────────┘ └─────────┘ └─────────┘
```

### 2.2 Exemple : Passerelle Modbus → MQTT avec Python

```python
import paho.mqtt.client as mqtt
from pymodbus.client import ModbusTcpClient
import json
import time

class IndustrialGateway:
    """Passerelle de données industrielles Modbus → MQTT."""

    def __init__(self, modbus_host: str, mqtt_broker: str):
        self.modbus = ModbusTcpClient(modbus_host, port=502)
        self.mqtt = mqtt.Client()
        self.mqtt.connect(mqtt_broker, 1883, 60)

    def read_and_publish(self, register_map: dict, topic_prefix: str):
        """Lit des registres Modbus et publie sur MQTT."""
        for tag, (unit_id, address, count) in register_map.items():
            result = self.modbus.read_holding_registers(address, count, unit=unit_id)
            if not result.isError():
                payload = json.dumps({
                    "tag": tag,
                    "value": result.registers[0] if count == 1 else result.registers,
                    "timestamp": time.time()
                })
                self.mqtt.publish(f"{topic_prefix}/{tag}", payload, qos=1)

    def run(self, register_map: dict, topic_prefix: str, interval: float = 5.0):
        """Boucle principale de lecture/publication."""
        self.modbus.connect()
        try:
            while True:
                self.read_and_publish(register_map, topic_prefix)
                time.sleep(interval)
        finally:
            self.modbus.close()
            self.mqtt.disconnect()
```

---

## 3. Normalisation des Échanges

### 3.1 Standard ISA-95 (IEC 62264)

ISA-95 définit les interfaces entre les niveaux entreprise et contrôle :

| Interface | Flux | Standard |
|:---|:---|:---|
| **ERP → MES** | Ordres de fabrication, ressources | B2MML (XML) |
| **MES → ERP** | État de production, traçabilité | B2MML |
| **MES → SCADA** | Consignes de production | OPC-UA |
| **SCADA → MES** | Mesures, alarmes, TRS | OPC-UA |

### 3.2 Modèle de Données Standardisé

```yaml
Donnée: OrdreFabrication
  Standards:
    - B2MML: ProductionRequest
    - ISA-95: SegmentRequirement
  Champs obligatoires:
    - id: string
    - product: string
    - quantity: float
    - unit: string
    - due_date: datetime
    - priority: integer
  Champs optionnels:
    - bom: list[Component]
    - routing: list[Operation]
    - quality_plan: list[Inspection]
```

---

## 4. Intégration IA/LLM dans les Flux Industriels

### 4.1 Architecture LLM + RAG + Données Temps Réel

```python
from langchain.agents import create_openai_functions_agent
from langchain_community.agent_toolkits import OPCUAConnector
from langchain_community.llms import Ollama

# Connexion aux données temps réel via OPC-UA
opc_tool = OPCUAConnector(
    url="opc.tcp://plc.actemium.local:4840",
    nodes=["ns=2;i=1001", "ns=2;i=1002"]  # Température, Pression
)

# Agent LLM capable d'interroger les données industrielles
tools = [opc_tool]
llm = Ollama(model="mistral")
agent = create_openai_functions_agent(llm, tools)

# Exécution
result = agent.run("Quelle est la température actuelle du four ? Est-elle dans les limites ?")
```

---

## 5. Pièges Courants

1. **Point-à-point non maintenable :**
   - *Erreur* : Connecter chaque système directement aux autres (architecture spaghetti).
   - *Correction* : Utilisez un bus middleware (Kafka, OPC-UA aggregation) comme point central.

2. **Normes propriétaires :**
   - *Erreur* : Utiliser des protocoles ou formats propriétaires sans passerelle standard.
   - *Correction* : Préférez les standards ouverts (OPC-UA, MQTT, B2MML, ISA-95).

3. **Latence d'intégration non spécifiée :**
   - *Erreur* : Un système temps réel (PLC) connecté à un système batch (ERP) sans tampon.
   - *Correction* : Définissez des niveaux de service (SLA) pour chaque interface.

---

## Liste de vérification

- [ ] Tous les systèmes (PLC, SCADA, MES, ERP, IA) sont inventoriés avec leurs protocoles.
- [ ] Les points d'intégration sont documentés (système A → système B, protocole, données).
- [ ] Un middleware/un bus de données (Kafka, OPC-UA gateway) centralise les échanges.
- [ ] Les formats de données sont normalisés (B2MML, JSON Schema, OPC-UA info model).
- [ ] Les SLA de latence sont définis pour chaque interface.
- [ ] La sécurité des échanges (TLS, authentification) est en place pour chaque connexion.
