---
name: industrial-plc-connectivity
description: "Écrire des scripts de connexion Snap7, pycomm3 et ADS."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [siemens, rockwell, ethernet-ip, s7-protocol, cip, serial, rs232, rs485, pycomm3, snap7, pylogix, pyserial, modbus-rtu, bacnet, canopen, pyvisa, opc-da, ads, industrial-automation]
  related_skills: [industrial-protocols, industrial-edge]
---

# Connectivité Automate et Protocoles Industriels Étendus

## Vue d'ensemble

L'acquisition de données à la source (le capteur, l'automate, la centrale de mesure ou l'instrumentation) nécessite d'utiliser des protocoles propriétaires, bas niveau ou spécialisés par domaine (GTB, automobile, laboratoire).

Cette compétence guide l'agent Helios pour écrire des scripts d'intégration robustes pour :
1. **Rockwell Automation** via EtherNet/IP (CIP) avec `pycomm3` ou `pylogix`.
2. **Siemens S7** via S7 Protocol avec `python-snap7`.
3. **Liaisons série (COM, RS-232, RS-485)** avec `pyserial`.
4. **Modbus RTU (Série)** avec `pymodbus`.
5. **BACnet (CVC / GTB)** avec `BAC0`.
6. **CAN bus & CANopen** avec `python-can` et `canopen`.
7. **Instrumentation scientifique (GPIB, LXI)** avec `pyvisa` et les commandes SCPI.
8. **OPC-DA (Classic / Windows COM)** avec `OpenOPC`.
9. **TwinCAT ADS (Beckhoff / EtherCAT)** avec `pyads`.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire des scripts de communication avec des équipements de divers réseaux industriels (automates, compteurs, GTB, variateurs).
- De lire/écrire des variables sur des contrôleurs via Ethernet ou liaison série.
- De collecter des mesures depuis des appareils de laboratoire ou de test.
- De diagnostiquer des couches physiques RS-485, bus CAN, ou réseaux IP industriels.

---

## Guide de Diagnostic des Ports Réseau Industriels Standard

Lorsqu'une connexion échoue, l'agent doit valider si le port TCP/UDP standard est ouvert sur l'adresse IP de destination en utilisant des outils de diagnostic :

| Protocole | Port par Défaut | Type de Socket | Constructeur / Standard |
| :--- | :--- | :--- | :--- |
| **S7 Protocol (S7Comm)** | `102` | TCP | Siemens S7-300/400/1200/1500 |
| **Modbus TCP** | `502` | TCP | Schneider Modicon, variateurs, compteurs |
| **EtherNet/IP (CIP)** | `44818` | TCP & UDP | Rockwell ControlLogix/CompactLogix, Omron |
| **TwinCAT ADS** | `48898` | TCP | Beckhoff TwinCAT Runtime |
| **OPC UA** | `4840` | TCP | Standard Universel (OPC Foundation) |
| **BACnet/IP** | `47808` (0xBAC0) | UDP | GTB / CVC (Chauffage, Ventilation) |

---

## 1. Rockwell Automation via EtherNet/IP & CIP

Les automates Rockwell modernes (Logix5000) utilisent le protocole **CIP (Common Industrial Protocol)** basé sur des noms de variables textuels (Tags).

### Gestion Robuste de Connexion et Lecture Groupée (pycomm3) :

```python
import time
from pycomm3 import LogixDriver, RequestError

PLC_IP = '192.168.1.10'

def read_rockwell_tags_safely():
    # Connexion à l'automate. Le chemin par défaut pour le slot processeur est 0.
    plc = LogixDriver(PLC_IP)
    
    # Tentative de connexion avec gestion d'erreurs
    try:
        plc.open()
        print(f"Connecté à l'automate Rockwell ({PLC_IP})")
        
        # Lecture multiple (optimise les requêtes réseau)
        tags = ['Moteur1_Vitesse', 'Moteur1_Defaut', 'Machine_Statut']
        results = plc.read(*tags)
        
        for res in results:
            if res.error is None:
                print(f"Tag '{res.tag}' = {res.value} (Qualité: Good)")
            else:
                print(f"Tag '{res.tag}' - Erreur de lecture : {res.error}")
                
        # Écriture d'un Tag avec validation de retour
        write_res = plc.write('Moteur1_Consigne', 1500.0)
        if write_res.error:
            print(f"Échec d'écriture : {write_res.error}")
            
    except RequestError as err:
        print(f"Erreur CIP de l'automate : {err}")
    except Exception as e:
        print(f"Erreur générale de connexion : {e}")
    finally:
        # Toujours fermer la session explicitement
        plc.close()

if __name__ == "__main__":
    read_rockwell_tags_safely()
```

---

## 2. Siemens via S7 Protocol (python-snap7)

Le protocole Siemens S7 est basé sur des adresses physiques directes organisées en **Data Blocks (DB)**.

### Configuration préalable cruciale dans TIA Portal :
1. **Désactiver l'accès optimisé au bloc** dans les propriétés de chaque Data Block (DB) cible (décochez "Optimized block access" afin de faire apparaître les offsets physiques).
2. **Autoriser l'accès PUT/GET** dans les propriétés de la CPU (Protection & Sécurité -> Mécanismes de connexion -> cochez "Permit access with PUT/GET communication...").

### Script d'intégration avec Boucle de Reconnexion Automatique :

```python
import time
import snap7
from snap7.util import get_real, set_real
from snap7.exceptions import Snap7Exception

PLC_IP = '192.168.1.100'
DB_NUMBER = 10

def connect_and_read_s7():
    client = snap7.client.Client()
    connected = False
    
    # Boucle de reconnexion (tentatives toutes les 5 secondes en cas de défaillance)
    while not connected:
        try:
            print(f"Tentative de connexion au Siemens S7 ({PLC_IP})...")
            # IP, Rack (0), Slot (1 pour S7-1200/1500, 2 pour S7-300/400)
            client.connect(PLC_IP, 0, 1)
            connected = client.get_connected()
        except Snap7Exception as err:
            print(f"Échec de connexion : {err}. Retentative dans 5 secondes...")
            time.sleep(5)
            
    print("Connecté au Siemens S7.")
    try:
        # Lire 4 octets dans le DB à partir de l'offset 0 (ex: un Real/Float)
        buffer = client.db_read(DB_NUMBER, 0, 4)
        vitesse = get_real(buffer, 0)
        print("Vitesse lue :", vitesse)
        
        # Écrire un Real (50.5) dans le DB à l'offset 4
        write_buffer = bytearray(4)
        set_real(write_buffer, 0, 50.5)
        client.db_write(DB_NUMBER, 4, write_buffer)
        print("Écriture réussie de 50.5 à l'offset 4")
        
    except Snap7Exception as e:
        print(f"Erreur d'échange protocole S7 : {e}")
    finally:
        client.disconnect()
        print("Déconnecté.")

if __name__ == "__main__":
    connect_and_read_s7()
```

---

## 3. Communication Série COM (RS-232 / RS-485) via `pyserial`

```python
import serial

ser = serial.Serial(
    port='COM3',            # '/dev/ttyUSB0' sous Linux
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1.5             # Timeout de lecture en secondes
)

try:
    if not ser.is_open:
        ser.open()
        
    ser.write(b'GET_WEIGHT\r\n')
    ligne = ser.readline().decode('ascii').strip()
    print("Donnée reçue :", ligne)
    
finally:
    if ser.is_open:
        ser.close()
```

---

## 4. Modbus RTU (Liaison Série)

```python
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    port='COM3',
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=2.0
)

if client.connect():
    result = client.read_holding_registers(address=0, count=10, slave=3)
    if not result.isError():
        print("Registres Modbus RTU :", result.registers)
    else:
        print("Erreur Modbus RTU :", result)
    client.close()
```

---

## 5. BACnet (Building Automation & HVAC)

Le protocole **BACnet** est le standard de la GTB/GTC (Gestion Technique du Bâtiment).

```python
import BAC0

# Initialisation locale du client BACnet (port UDP standard 47808 / 0xBAC0)
bacnet = BAC0.connect(ip='192.168.1.50')

# Lecture d'un point analogique (Analog Input 1) sur un automate de ventilation (ID 100)
temp = bacnet.read('192.168.1.150 analogInput 1 presentValue')
print(f"Température lue : {temp} °C")

# Écriture d'une consigne sur une sortie analogique (Analog Output 2, priorité 8)
bacnet.write('192.168.1.150 analogOutput 2 presentValue 21.0 - 8')

bacnet.disconnect()
```

---

## 6. CAN bus & CANopen (Liaisons embarquées & Variateurs)

### Lecture/Écriture brute CAN (`python-can`) :
```python
import can

bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=250000)

# Envoi d'une trame CAN standard (ID 0x181, 8 octets)
msg = can.Message(arbitration_id=0x181, data=[0x01, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00], is_extended_id=False)
bus.send(msg)

# Lecture d'un message avec un timeout de 2.0s
msg_recu = bus.recv(timeout=2.0)
if msg_recu:
    print(f"Trame reçue - ID: {hex(msg_recu.arbitration_id)} - Data: {list(msg_recu.data)}")

bus.shutdown()
```

### Profil CANopen (`canopen`) :
```python
import canopen

network = canopen.Network()
network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=125000)

# Déclaration d'un nœud (ID 2) et chargement de son dictionnaire d'objets EDS
node = network.add_node(2, 'profile_moteur.eds')

# Lecture d'un objet (Index 0x1018, Sub-index 1 : Vendor ID) via SDO
vendor_id = node.sdo[0x1018][1].raw
print("Vendor ID :", vendor_id)

# Écriture d'une vitesse cible (Index 0x60FF)
node.sdo[0x60FF].raw = 3000

network.disconnect()
```

---

## 7. Instrumentation Scientifique & Test (PyVISA / SCPI)

Permet de communiquer avec des appareils de mesure (multimètres, oscilloscopes, générateurs) via GPIB, USB ou Ethernet (LXI) en utilisant des commandes standardisées **SCPI**.

```python
import pyvisa

rm = pyvisa.ResourceManager()
scope = rm.open_resource('TCPIP0::192.168.1.80::inst0::INSTR')

scope_id = scope.query('*IDN?')
print("Appareil détecté :", scope_id.strip())

scope.write('AUTOSCALE')
scope.write('ACQUIRE:TYPE NORMAL')

scope.close()
```

---

## 8. OPC-DA (OPC Classic)

Le standard historique basé sur la couche DCOM de Microsoft Windows.

```python
import OpenOPC

opc = OpenOPC.client()
opc.connect('Matrikon.OPC.Simulation.1')

valeur, qualite, timestamp = opc.read('Random.Int4')
print(f"Valeur : {valeur} (Qualité: {qualite})")

opc.write(('Bucket Brigade.Real4', 15.6))

opc.close()
```

---

## 9. TwinCAT ADS (Beckhoff / EtherCAT)

```python
import pyads

plc = pyads.Connection('192.168.1.10.1.1', 851)
plc.open()

vitesse = plc.read_by_name('Main.fVitesseActuelle', pyads.PLCTYPE_REAL)
print("Vitesse Beckhoff ADS :", vitesse)

plc.write_by_name('Main.bDemarrageMoteur', True, pyads.PLCTYPE_BOOL)

plc.close()
```

---

---

## Nouveau : Outils Helios intégrés pour connectivité PLC temps réel

Depuis juillet 2026, Helios Agent dispose d'**outils intégrés** pour la communication PLC en temps réel. Contrairement aux scripts standalone ci-dessus, ces outils s'appellent directement depuis l'agent via `registry.register()`.

### Outils disponibles

| Outil | Description | Dépendance |
|-------|-------------|------------|
| `plc_read(plc_type, endpoint, tag_path)` | Lecture temps réel de tag | python-snap7 (S7), pylogix (Rockwell), pycomm3 (EIP) |
| `plc_write(plc_type, endpoint, tag_path, value)` | Écriture temps réel | (idem) |
| `plc_probe(endpoint, timeout)` | Détection auto du type PLC | socket (stdlib) |

### Constructeurs supportés

| `plc_type` | Librairie | Constructeurs |
|------------|-----------|---------------|
| `s7` | `python-snap7` | Siemens S7-1200/1500/300/400 |
| `rockwell` | `pylogix` | Rockwell ControlLogix / CompactLogix |
| `eip` | `pycomm3` | Allen-Bradley via EtherNet/IP |

### Formats de tags supportés

**Siemens S7** — adressage physique (nécessite accès optimisé désactivé) :
- `DB1.DBX0.0` → DB 1, Byte 0, Bit 0
- `DB1.DBD2` → DB 1, Double Word à offset 2
- `DB1.DBW6` → DB 1, Word à offset 6
- `MW100` → Merker Word 100
- `MB50` → Merker Byte 50

**Rockwell / EIP** — adressage par nom :
- `MyProgram.MyTag` (tag structuré)
- `Moteur1_Vitesse` (tag simple)

### Quand utiliser quel outil

- **Script autonome** → Utiliser les patterns `python-snap7` / `pylogix` / `pycomm3` ci-dessus (quand le code doit tourner sur une machine sans Helios ou dans un pipeline CI/CD).
- **Interaction agent temps réel** → Utiliser `plc_read` / `plc_write` / `plc_probe` (quand l'agent a besoin de lire/écrire pendant une conversation).
- **Découverte réseau** → `plc_probe` en premier pour détecter le type, puis `plc_read` avec le bon `plc_type`.

---

## Pièges Courants (Common Pitfalls)

1. **PUT/GET non configuré ou accès DB optimisé (Siemens) :**
   * *Erreur :* Le script renvoie des erreurs d'accès refusé (`Access Denied` ou erreur hexadécimale `0x20000003`).
   * *Correction :* Configurer la CPU Siemens pour autoriser PUT/GET et décocher "Optimized block access" sur le DB cible dans TIA Portal avant de recompiler et charger la configuration matérielle.
2. **Confusion entre les index de Rack/Slot (Siemens S7) :**
   * *Erreur :* La connexion TCP réussit mais le protocole S7 échoue.
   * *Correction :* Utiliser Slot `1` pour les gammes S7-1200/1500, et Slot `2` pour les gammes historiques S7-300/400.
3. **Absence de délai d'attente (Timeout) sur la liaison série :**
   * *Erreur :* L'application reste bloquée indéfiniment sur `ser.readline()` ou `ser.read()` si l'équipement série n'envoie rien.
   * *Correction :* Toujours spécifier `timeout=1.0` (ou supérieur) lors de l'instanciation de `serial.Serial`.
4. **Conflit de port série (COM) occupé :**
   * *Erreur :* Erreur de permission refusée (`AccessDenied` ou port COM indisponible).
   * *Correction :* S'assurer qu'aucun autre outil n'utilise déjà le port COM. Libérer la ressource avant de lancer le script.

---

## Liste de vérification (Checklist)

- [ ] L'accès PUT/GET est autorisé et l'accès optimisé est désactivé si la cible est un automate Siemens S7-1200/1500.
- [ ] Le slot CPU correct (1 ou 2) est configuré dans les paramètres du client Snap7.
- [ ] Tous les ports COM ouverts via `pyserial` définissent une valeur de `timeout` explicite.
- [ ] Les connexions série et sockets automates sont encapsulées dans des blocs `try/finally` ou gérées via des gestionnaires de contexte (`with`) pour s'assurer que les connexions soient proprement fermées en fin de script.
- [ ] Les exceptions d'écriture et de déconnexion réseau sont capturées pour éviter les plantages applicatifs.
- [ ] L'état réseau de la cible (ping et ouverture du port standard via socket TCP) a été testé avant de lancer le script.

