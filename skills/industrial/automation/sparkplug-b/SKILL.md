---
name: sparkplug-b
description: "Implémenter et configurer des architectures Sparkplug B."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [mqtt, sparkplug-b, uns, iiot, industrial-automation, protobuf, edge-computing, tahu, scada, mqtt-sparkplug]
    related_skills: [industrial-protocols, industrial-uns, industrial-edge, opc-ua-scanner, plc-diagnostic]
---

# MQTT Sparkplug B & Gestion d'État OT

## Vue d'ensemble

Le protocole **MQTT Sparkplug B** est une spécification ouverte (développée par Cirrus Link Solutions, désormais sous l'égide de l'Eclipse Foundation) qui définit un format de données standardisé et un mécanisme robuste de gestion d'état pour les architectures **IIoT (Industrial Internet of Things)**.

Contrairement au MQTT vanilla qui est neutre vis-à-vis du format du payload, **Sparkplug B** impose :

1. **Une structure de Topic rigide et normalisée** : `spBv1.0/group_id/message_type/edge_node_id/[device_id]`.
2. **Un payload binaire encodé en Protobuf** (Protocol Buffers) hautement compressé et optimisé pour le réseau.
3. **Un mécanisme de gestion de l'état de connexion** grâce aux certificats de naissance/décès (Birth/Death) : `NBIRTH`, `NDEATH`, `DBIRTH`, `DDEATH`.
4. **Une séquence temporelle (`seq`) garantissant l'intégrité de l'ordre des messages** (compteur 0–255, rollover).
5. **Une gestion intégrée du Primary Host Status (`STATE`)** pour restaurer l'historique après une coupure réseau.

Cette standardisation est la **clé de voûte pour l'alimentation dynamique d'un Unified Namespace (UNS)** en contexte industriel.

### Architecture typique Sparkplug B

```
[PLC / Capteurs] → [Edge Gateway (Passerelle)]
                          │
                          ▼
            [Broker MQTT (ex: Mosquitto, HiveMQ)]
                          │
                          ▼
            [SCADA / Historien / Cloud (Primary Host)]
```

L'Edge Gateway publie les données des équipements en suivant strictement le format Sparkplug B. Le Primary Host (SCADA) s'abonne et garantit la cohérence des données.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Structurer des **topics MQTT** pour un projet SCADA ou IIoT selon le standard industriel.
- Configurer ou dépanner un **broker MQTT** avec des passerelles Sparkplug B (ex: Ignition MQTT Engine, Opto 22 groov, Node-RED).
- Concevoir ou analyser des **payloads Protobuf Sparkplug B** (décodage de fichiers binaires).
- Mettre en place des **certificats de naissance/décès** (Birth/Death certificates) pour surveiller la santé des connexions automate.
- Déployer un **Unified Namespace (UNS)** en usine en utilisant Sparkplug B comme protocole de transport OT.

### Ne pas utiliser pour

- Les échanges MQTT entre microservices dans le cloud (préférer MQTT vanilla, JSON, Avro).
- Le transport de fichiers volumineux (> 100 Mo) — Sparkplug B est conçu pour les données de télémétrie.
- Les architectures nécessitant de l'historisation longue durée côté Edge (utiliser une base de données locale).

---

## 1. Structure de Topic Sparkplug B

Chaque message Sparkplug B doit suivre **exactement** la structure suivante :

```text
spBv1.0 / group_id / message_type / edge_node_id / [device_id]
```

### Hiérarchie des segments

| Segment | Obligatoire | Description | Exemple |
|---------|------------|-------------|---------|
| `spBv1.0` | Oui | Version du protocole (fixe, ne pas modifier) | `spBv1.0` |
| `group_id` | Oui | Identifiant logique d'un groupe d'équipements | `Usine_Lyon`, `Site_01` |
| `message_type` | Oui | Type de message Sparkplug | `NBIRTH`, `NDATA`, `NCMD` |
| `edge_node_id` | Oui | Identifiant unique de la passerelle Edge | `Gateway_IQAN_01` |
| `device_id` | Non | Identifiant de l'équipement connecté | `Automate_Filtre`, `Vanne_01` |

### Types de messages clés

| Message | Sens | Description |
|---------|------|-------------|
| **NBIRTH** | Edge → Broker | Envoyé par la passerelle Edge lors de sa connexion pour s'enregistrer et lister toutes ses variables/métriques. |
| **NDEATH** | Broker → Subscribers | Publié par le broker via le testament MQTT (Last Will) si la passerelle perd la connexion de manière inattendue. |
| **DBIRTH** | Edge → Broker | Annonce la présence et les variables d'un équipement (ex: PLC) raccordé à la passerelle. |
| **DDEATH** | Broker → Subscribers | Testament pour un équipement spécifique perdu. |
| **NDATA** | Edge → Broker | Envoi régulier des valeurs de la passerelle (sur variation/deadband). |
| **DDATA** | Edge → Broker | Envoi régulier des valeurs d'un équipement (sur variation/deadband). |
| **NCMD** | SCADA → Edge | Commande destinée à la passerelle (ex: redémarrage). |
| **DCMD** | SCADA → Edge | Commande destinée à un équipement (ex: activation vanne). |

### Exemples de topics valides

```text
spBv1.0/Usine_Lyon/NBIRTH/Gateway_IQAN_01
spBv1.0/Usine_Lyon/DBIRTH/Gateway_IQAN_01/Automate_Filtre
spBv1.0/Usine_Lyon/DDATA/Gateway_IQAN_01/Automate_Filtre
spBv1.0/Usine_Lyon/DCMD/Gateway_IQAN_01/Automate_Filtre
```

---

## 2. Payload Protobuf Sparkplug B

Le payload Sparkplug B est encodé en **Protocol Buffers** (Protobuf) en utilisant le schéma officiel de l'Eclipse Tahu project.

### Structure simplifiée du message

```protobuf
// Extrait du schéma Sparkplug B (tahu.proto)
message Payload {
  uint64 timestamp = 1;           // Timestamp UNIX en millisecondes
  repeated Metric metrics = 2;    // Liste des métriques
  uint64 seq = 3;                 // Numéro de séquence 0-255
  string uuid = 8;                // Identifiant unique du message
  bytes body = 9;                 // Corps optionnel
}

message Metric {
  string name = 1;                // Nom complet de la métrique
  uint64 alias = 2;               // Alias numérique (optimisation bande passante)
  uint64 timestamp = 3;           // Timestamp de la mesure
  DataType datatype = 4;          // Type de données (Int32, Float, Boolean, String...)
  bool is_historical = 15;        // Flag données historiques
  oneof value {
    uint64 int_value = 7;
    uint64 long_value = 8;
    float float_value = 9;
    double double_value = 10;
    bool boolean_value = 11;
    string string_value = 12;
    bytes bytes_value = 13;
  }
}
```

### Types de données Sparkplug B

| Alias Type | Nom | Protobuf Type |
|-----------|------|---------------|
| 0 | `Int8` | `int_value` (uint64) |
| 1 | `Int16` | `int_value` (uint64) |
| 2 | `Int32` | `int_value` (uint64) |
| 3 | `Int64` | `long_value` |
| 4 | `UInt8` | `int_value` (uint64) |
| 5 | `UInt16` | `int_value` (uint64) |
| 6 | `UInt32` | `int_value` (uint64) |
| 7 | `UInt64` | `long_value` |
| 8 | `Float` | `float_value` |
| 9 | `Double` | `double_value` |
| 10 | `Boolean` | `boolean_value` |
| 11 | `String` | `string_value` |
| 12 | `DateTime` | `long_value` (epoch ms) |
| 13 | `Text` | `string_value` |
| 14 | `UUID` | `string_value` |
| 15 | `DataSet` | `bytes_value` |
| 16 | `Bytes` | `bytes_value` |
| 17 | `File` | `bytes_value` |
| 18 | `Template` | `bytes_value` |

---

## 3. Utilisation du Script d'Assistance

Le script [`sparkplug_client.py`](scripts/sparkplug_client.py) implémente un client Sparkplug B complet capable de publier des messages NBIRTH, DBIRTH et NDATA/DDATA.

### 3.1 Publication d'un message de naissance (Birth)

```python
import subprocess
import json

# Métriques à envoyer avec leurs types officiels Sparkplug
metrics = {
    "Convoyeur/Vitesse":        {"value": 145.2, "type": "Float"},
    "Convoyeur/Etat_Marche":    {"value": True,  "type": "Boolean"},
    "Cuve/Niveau":              {"value": 2.35,  "type": "Float"},
    "Cuve/Alarme_Haute":        {"value": 0,     "type": "Int32"},
    "Cuve/Commentaire_Op":      {"value": "Cycle standard", "type": "String"}
}

cmd = [
    ".venv/Scripts/python.exe",
    "skills/industrial/automation/sparkplug-b/scripts/sparkplug_client.py",
    "--broker", "localhost",
    "--port", "1883",
    "--group-id", "Usine_Lyon",
    "--node-id", "Gateway_Passerelle_01",
    "--action", "birth",
    "--metrics", json.dumps(metrics),
    "--debug",        # Activer le mode verbose
]

print("Publication NBIRTH...")
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Erreurs :", result.stderr)
```

### 3.2 Publication d'une mise à jour (Data)

```python
import subprocess
import json

new_metrics = {
    "Convoyeur/Vitesse": {"value": 148.7, "type": "Float"},
    "Cuve/Niveau":       {"value": 2.41,  "type": "Float"},
}

cmd = [
    ".venv/Scripts/python.exe",
    "skills/industrial/automation/sparkplug-b/scripts/sparkplug_client.py",
    "--broker", "localhost",
    "--port", "1883",
    "--group-id", "Usine_Lyon",
    "--node-id", "Gateway_Passerelle_01",
    "--action", "data",
    "--metrics", json.dumps(new_metrics),
]

print("Publication NDATA...")
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
```

### 3.3 Vérification de l'état avec un abonné MQTT

```bash
# S'abonner à tous les topics Sparkplug B
mosquitto_sub -h localhost -t "spBv1.0/#" -v
```

---

## 4. Gestion de l'État et du Séquenceur

### 4.1 Règles de séquence (`seq`)

- Le compteur `seq` commence à **0** lors d'un message `NBIRTH` ou `DBIRTH`.
- Il s'incrémente de **1** à chaque message `NDATA`, `DDATA`, `NCMD`, `DCMD` suivant.
- Il **reboucle** à 0 après avoir atteint **255** (byte unsigned rollover).
- Un client primaire qui reçoit un `seq` hors séquence doit **rejeter le message** et demander un nouveau Birth.

### 4.2 La métrique obligatoire `bdSeq`

Le message **NBIRTH** doit contenir la métrique `bdSeq` (Birth/Death Sequence Number). Cette métrique permet au Primary Host de savoir :

- Si l'Edge Node a redémarré (`bdSeq` a changé depuis la dernière connexion).
- Si des données historiques sont manquantes et doivent être demandées.

```json
{
  "name": "bdSeq",
  "type": "Int64",
  "value": 15
}
```

### 4.3 Primary Host (STATE)

Le Primary Host (souvent un SCADA comme Ignition) maintient un topic `STATE` :

```text
spBv1.0/Usine_Lyon/STATE/Gateway_Passerelle_01
```

Ce message est publié avec le flag **RETAIN** pour indiquer quel client est l'hôte primaire actif. Si le Primary Host tombe, un nouveau host peut reprendre en publiant un message STATE avec ses propres identifiants.

---

## Pièges Courants (Common Pitfalls)

1. **Mauvaise gestion du compteur de séquence (`seq`) :**
   * *Erreur :* Ne pas incrémenter le numéro de séquence pour chaque message `NDATA`/`DDATA` consécutif, ou ne pas le réinitialiser à `0` lors d'un `NBIRTH`. Le client primaire (SCADA) rejette tous les messages hors séquence.
   * *Correction :* Gérer un compteur local de 0 à 255. Incrémenter à chaque envoi et réinitialiser à 0 au rebouclage ou à la reconnexion (Birth).

2. **Utilisation du flag RETAIN sur les messages de données :**
   * *Erreur :* Configurer `retain=True` sur les messages `NDATA`/`DDATA`. Cela provoque la relecture de données périmées au redémarrage d'un client.
   * *Correction :* Seuls les messages d'état de connexion (`STATE`) utilisent le flag RETAIN. Les messages de données utilisent QoS 1 sans RETAIN.

3. **Absence de la métrique `bdSeq` dans NBIRTH :**
   * *Erreur :* Le message NBIRTH ne contient pas `bdSeq`. Le Primary Host ne peut pas déterminer si l'Edge a redémarré ou si des données historiques sont perdues.
   * *Correction :* Toujours inclure `bdSeq` dans le NBIRTH. Incrémenter `bdSeq` à chaque redémarrage de l'Edge.

4. **Non-respect de l'ordre Birth → Data :**
   * *Erreur :* Publier des messages `NDATA` avant d'avoir envoyé le `NBIRTH`. Le Primary Host ignore tous les messages de données sans Birth préalable.
   * *Correction :* Toujours envoyer NBIRTH en premier. Attendre que le Primary Host accuse réception (ou simplement envoyer Birth avant tout Data).

5. **Confusion entre Node et Device dans le topic :**
   * *Erreur :* Publier un `DBIRTH` avec un topic qui n'inclut pas le `device_id` : `spBv1.0/group/DBIRTH/node/` (manque le dernier segment).
   * *Correction :* Le topic DBIRTH DOIT avoir exactement 5 segments : `spBv1.0/group_id/DBIRTH/edge_node_id/device_id`.

---

## Liste de vérification (Checklist)

- [ ] La structure du topic respecte strictement le format `spBv1.0/group_id/message_type/edge_node_id/device_id`.
- [ ] Le payload est encodé en binaire Protobuf et respecte le schéma officiel Eclipse Tahu.
- [ ] Le compteur de séquence (`seq`) commence à `0` lors de NBIRTH/DBIRTH et s'incrémente à chaque message suivant.
- [ ] La métrique obligatoire `bdSeq` est incluse dans le message NBIRTH.
- [ ] Un testament MQTT (Last Will and Testament) est configuré sur le broker pour NDEATH/DDEATH.
- [ ] Le message STATE est publié avec RETAIN par le Primary Host.
- [ ] Les messages de données (NDATA/DDATA) n'utilisent pas le flag RETAIN.
- [ ] La passerelle Edge envoie NBIRTH avant tout NDATA.
- [ ] Le type de données Protobuf de chaque métrique correspond à son type réel (Float, Int32, Boolean, etc.).
- [ ] La bibliothèque `sparkplug-python` ou `tahu` est installée dans l'environnement.

