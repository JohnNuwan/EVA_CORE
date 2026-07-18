---
name: industrial-protocols
description: "Programmer sous protocoles OPC-UA, Modbus-TCP et MQTT."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [opc-ua, modbus, mqtt, sparkplug-b, pycomm3, pymodbus, asyncua, industrial-automation]
  related_skills: [simplify-code, plan]
---

# Communication et Protocoles Industriels (OPC-UA, Modbus, MQTT)

## Vue d'ensemble

L'informatique industrielle (OT) repose sur des protocoles de communication standardisés pour faire communiquer les automates, les capteurs, les IHM et les systèmes informatiques (SCADA, MES, Cloud). 

Cette compétence guide l'agent EVA pour écrire des scripts d'intégration robustes en Python pour collecter et distribuer des données en temps réel en utilisant :
- **OPC-UA** (Unified Architecture) via `asyncua`.
- **Modbus-TCP** via `pymodbus`.
- **MQTT / Sparkplug B** via `paho-mqtt` pour les architectures IIoT.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire un script de collecte de données depuis un serveur OPC-UA ou un automate.
- De lire ou d'écrire des registres sur un appareil via Modbus-TCP.
- De publier des données industrielles vers un broker MQTT ou de configurer des payloads au format Sparkplug B.
- De diagnostiquer des problèmes de connexion ou de désynchronisation de paquets sur ces protocoles.

---

## 1. Intégration OPC-UA & Profils de Sécurité (asyncua)

OPC-UA est le standard moderne orienté objet. En production, les liaisons sont sécurisées par chiffrement et certificats d'authentification (PKI client/serveur).

### Profils et Politiques de Sécurité OPC UA :
- **Security Mode :** `None`, `Sign` (signature de paquets uniquement), `SignAndEncrypt` (signature et chiffrement complet des données).
- **Security Policy :** Politiques d'algorithmes de clés de chiffrement (ex: `Basic256Sha256`, `Aes128_Sha256_RsaOaep`, `Aes256_Sha256_RsaOaep`).

```python
import asyncio
from asyncua import Client
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256

async def read_secure_opc_ua():
    url = "opc.tcp://192.168.1.100:4840"
    client = Client(url=url)
    
    # Configuration de la sécurité avec certificats PKI
    # (Requis pour la politique SignAndEncrypt)
    try:
        await client.set_security(
            SecurityPolicyBasic256Sha256,
            certificate_path="pki/client_cert.pem",
            private_key_path="pki/client_key.pem",
            server_certificate_path="pki/server_cert.der"
        )
        
        async with client:
            node_var = client.get_node("ns=3;s=Moteurs/Moteur1/Vitesse")
            valeur = await node_var.get_value()
            print("Vitesse actuelle lue de manière sécurisée : ", valeur)
    except Exception as e:
        print(f"Erreur de sécurité OPC UA : {e}")

if __name__ == "__main__":
    asyncio.run(read_secure_opc_ua())
```

---

## 2. Intégration Modbus-TCP & Boutisme (Endianness)

Modbus-TCP utilise des tables d'adresses physiques indexées (Holding Registers, Input Registers, Coils, Discrete Inputs) :
- **Function Code 3** : Lecture de Holding Registers (Lecture/Écriture).
- **Function Code 4** : Lecture de Input Registers (Lecture seule).
- **Function Code 16 (0x10)** : Écriture de registres multiples.

### Gestion de l'ordre des mots (Word Swap) et des octets (Byte Swap) :
Modbus transmet les données par mots de 16 bits (Word). Les variables 32-bit (Real/Float, DInt) ou 64-bit nécessitent de fusionner plusieurs registres consécutifs et d'adapter le boutisme (Endianness).

```python
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

def read_modbus_float():
    client = ModbusTcpClient('192.168.1.150', port=502, timeout=2.0)
    client.connect()
    
    # Lire 2 registres consécutifs (32 bits au total) à l'offset 100
    result = client.read_holding_registers(address=100, count=2, slave=1)
    
    if not result.isError():
        # Décodeur de payload binaire
        # Configuré pour Big Endian (mots et octets) - Standard Modicon classique
        decoder = BinaryPayloadDecoder.fromRegisters(
            result.registers, 
            byteorder=Endian.BIG, 
            wordorder=Endian.BIG
        )
        # Décoder en valeur Float 32-bit (Real)
        vitesse = decoder.decode_32bit_float()
        print(f"Vitesse décodée : {vitesse:.2f} Hz")
    else:
        print("Erreur de communication Modbus :", result)
        
    client.close()

if __name__ == "__main__":
    read_modbus_float()
```

---

## 3. MQTT et Standard Sparkplug B

Sparkplug B est une spécification IIoT définissant un format de payload binaire léger (Protobuf) pour MQTT et assurant le suivi de l'état de connexion des nœuds (NBIRTH, DBIRTH, NDATA, DDATA, NDEATH).

### Structure d'une Payload Sparkplug B (JSON-equivalent structure) :
Chaque message contient un horodatage (`timestamp`), un numéro de séquence (`seq`) pour valider la continuité des trames, et un tableau d'éléments (`metrics`) contenant le type de données :

```json
{
  "timestamp": 1623956100000,
  "seq": 42,
  "metrics": [
    {
      "name": "Atelier1/Moteur1/Vitesse",
      "timestamp": 1623956100000,
      "type": "Float",
      "value": 1450.5
    },
    {
      "name": "Atelier1/Moteur1/Defaut",
      "timestamp": 1623956100000,
      "type": "Boolean",
      "value": false
    }
  ]
}
```

Pour publier ou souscrire à ces structures, les scripts d'acquisition utilisent des encodeurs/décodeurs Protobuf basés sur le dictionnaire de tags du site.

---

## Pièges Courants (Common Pitfalls)

1. **Tentatives de connexions bloquantes sans Timeout :**
   * *Erreur :* Instancier un client Modbus ou OPC-UA sans définir de timeout. Si l'automate est hors ligne, le script Python se bloque indéfiniment.
   * *Correction :* Toujours spécifier un timeout raisonnable (ex: `timeout=2.0` secondes) et encapsuler la connexion dans un bloc `try/except`.
2. **Mauvais décodage de mots (Float/Real) Modbus :**
   * *Erreur :* Récupérer une valeur aberrante ou géante (ex : `1.45e-38`) à la place d'une valeur attendue (ex : `50.0`).
   * *Correction :* Inverser l'ordre des mots (`wordorder=Endian.LITTLE`) ou des octets (`byteorder=Endian.LITTLE`) dans le décodeur de payload binaire.

---

## Liste de vérification (Checklist)

- [ ] Les connexions réseau spécifient toutes un délai d'expiration (Timeout) pour éviter de bloquer le script.
- [ ] Les exceptions de connexion réseau (ex: `ConnectionRefusedError`, exceptions `pymodbus` et `asyncua`) sont attrapées et gérées.
- [ ] Les lectures de registres Modbus de plus de 16 bits (Real/DInt) utilisent un décodeur de payload configuré avec le bon boutisme (Endianness) du constructeur.
- [ ] Les ressources réseau (sockets, clients) sont correctement fermées en fin d'exécution (`client.close()` ou utilisation de `with` / `async with`).
- [ ] Les certificats SSL de sécurité client OPC UA sont configurés si le serveur requiert la politique `Sign` ou `SignAndEncrypt`.

