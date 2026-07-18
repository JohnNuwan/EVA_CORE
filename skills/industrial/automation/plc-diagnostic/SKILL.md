---
name: plc-diagnostic
description: "Diagnostiquer l'état CPU et le tampon d'un automate."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [industrial, diagnostic, plc, cpu-status, cycle-time, snap7, pylogix, troubleshooting, siemens, rockwell, s7-1500, controllogix, tampon-diagnostic]
    related_skills: [plc-connectivity, opc-ua-scanner, ot-security, siemens-audit, automation-linter]
---

# Audit et Diagnostics de Processeurs Automates (PLC)

## Vue d'ensemble

Le **diagnostic à distance d'un automate programmable (PLC)** est une étape de dépannage cruciale en informatique industrielle. Lors d'un dysfonctionnement d'usine (arrêt de production, surchauffe CPU, perte de communication, erreur d'adressage mémoire), l'extraction en temps réel des indicateurs CPU et la lecture du **tampon de diagnostic (Diagnostic Buffer)** permettent d'isoler rapidement le défaut.

Cette compétence fournit à l'agent Helios les directives et commandes pour interroger un automate **Siemens** (S7-300/400/1200/1500) ou **Rockwell** (ControlLogix/CompactLogix) et en extraire un bilan de santé matériel et logiciel structuré.

### Indicateurs clés extraits

| Indicateur | Siemens (S7) | Rockwell (CIP) | Utilité |
|------------|-------------|----------------|---------|
| État CPU | RUN / STOP / STARTUP | RUN / STOP / FAULT | État de fonctionnement actuel |
| Temps de cycle | Scan Cycle Time (ms) | Task Scan Rate | Détection de surcharge processeur |
| Occupation mémoire | Work Memory / Load Memory | Used / Total Bytes | Détection de saturation mémoire |
| Type CPU | Module ID | Catalog Number | Vérification de conformité matérielle |
| Version firmware | Firmware Version | Revision | Vérification de compatibilité |
| Dernières erreurs | Diagnostic Buffer (SZL) | Fault Log | Traçabilité des incidents |
| Tâches actives | OB priorities | Tasks states | Connaissance de l'architecture logicielle |

---

## Quand l'utiliser

### Cas d'usage typiques

À utiliser lorsque l'utilisateur demande de :

- Vérifier si un automate physique ou virtuel est en **RUN, en STOP ou en défaut**.
- Extraire la liste des **derniers événements consignés** dans la CPU (tampon de diagnostic).
- Diagnostiquer des problèmes de **performance liés à une surcharge de temps de cycle** de tâche automate.
- Obtenir **l'inventaire matériel** d'un processeur (type, modèle, révision de firmware).
- Vérifier la **consommation mémoire** (travail, chargement, rétention) d'une CPU Siemens.
- Suivre l'évolution du **compteur de redémarrages** (power-on count) et de la durée de fonctionnement.

### Ne pas utiliser pour

- L'édition ou la modification de programme automate (lecture seule).
- Le diagnostic de bus de terrain (Profinet, EtherNet/IP) — utiliser les outils constructeur dédiés.
- L'analyse de code source (utiliser la compétence `automation-linter`).

---

## 1. Protocoles et Bibliothèques d'Accès

### 1.1 Siemens : Snap7 et S7Comm

Snap7 est une bibliothèque open source qui implémente le protocole **S7Comm** (Siemens S7 Communication) sur le port **TCP 102**. Elle permet :

- La lecture/écriture de zones mémoire (DB, M, I, Q, T, C).
- La lecture du **tampon de diagnostic** via les requêtes SZL (System Status List).
- La lecture des **propriétés CPU** (état, version, nom de station).

**Installation :**

```bash
pip install python-snap7
```

**Exemple d'extraction d'état CPU :**

```python
import snap7

client = snap7.client.Client()
client.connect("192.168.1.100", rack=0, slot=1)

# Lecture de l'état CPU (RUN/STOP)
cpu_state = client.get_cpu_state()
print(f"État CPU : {cpu_state}")

# Lecture de la date/heure système
datetime = client.get_date_time()
print(f"Date/Heure automate : {datetime}")

# Lecture de l'identification du module (Order Number, Version)
module_info = client.read_module_types()
print(f"CPU : {module_info[0].ModuleTypeName}")
print(f"Order Number : {module_info[0].OrderNumber}")
print(f"Firmware : {module_info[0].Version}.{module_info[0].SubVersion}")

client.disconnect()
```

### 1.2 Rockwell : pylogix et EtherNet/IP

pylogix implémente le protocole **CIP (Common Industrial Protocol)** sur EtherNet/IP (port **TCP 44818**). Elle permet :

- La lecture/écriture de tags typés (BOOL, DINT, REAL, STRING).
- La lecture des attributs du processeur (état, modèle, firmware).
- La lecture des propriétés de tâche.

**Installation :**

```bash
pip install pylogix
```

**Exemple d'extraction d'état CPU :**

```python
from pylogix import PLC

with PLC() as comm:
    comm.IPAddress = "192.168.1.105"

    # Lecture du nom du processeur
    product_name = comm.GetProductName()
    print(f"Modèle : {product_name.Value}")

    # Lecture de l'état (mode)
    cpu_mode = comm.GetCPUStatus()
    print(f"État : {cpu_mode.Value}")

    # Lecture de la liste des tags
    tag_list = comm.GetTagList(program="MainProgram")
    print(f"Nombre de tags : {len(tag_list.Value)}")
```

### 1.3 Structure du Tampon de Diagnostic Siemens (SZL/SSL)

Chez Siemens, la CPU consigne tous les événements dans un **tampon circulaire** accessible via des requêtes SZL (System Status List) :

- **SZL ID 0x00A0** : Lecture des entrées du tampon de diagnostic (événements horodatés).
- **SZL ID 0x0013** : Répartition et occupation mémoire (Work Memory, Load Memory, Retain Memory).
- **SZL ID 0x001C** : Zones de protection et niveaux d'accès.
- **SZL ID 0x0019** : Intervalles de temps de cycle (min, max, actuel).

---

## 2. Utilisation du Script d'Assistance

Le script [`plc_diagnostic.py`](scripts/plc_diagnostic.py) automatise ces requêtes complexes et traduit les résultats en rapports JSON exploitables.

### 2.1 Dialogue complet Siemens S7-1500

```python
import subprocess
import json

cmd = [
    ".venv/Scripts/python.exe",
    "skills/industrial/automation/plc-diagnostic/scripts/plc_diagnostic.py",
    "--type", "siemens",
    "--ip", "192.168.1.100",
    "--rack", "0",
    "--slot", "1",       # Slot 1 pour S7-1200/1500, Slot 2 pour S7-300/400
    "--diagnostic",      # Inclure le tampon de diagnostic
    "--memory",          # Inclure l'occupation mémoire
    "--json",            # Sortie JSON structurée
]

print("Extraction des diagnostics Siemens...")
result = subprocess.run(cmd, capture_output=True, text=True)

# Analyse du résultat JSON
data = json.loads(result.stdout)
print(f"État CPU : {data['cpu_state']}")
print(f"Temps de cycle : {data['scan_time']} ms")
print(f"Mémoire travail utilisée : {data['memory']['work_memory_percent']}%")

# Affichage des entrées du tampon de diagnostic
for entry in data['diagnostic_buffer'][:5]:
    print(f"[{entry['timestamp']}] {entry['event']} - {entry['description']}")
```

### 2.2 Dialogue Rockwell ControlLogix

```python
import subprocess

cmd = [
    ".venv/Scripts/python.exe",
    "skills/industrial/automation/plc-diagnostic/scripts/plc_diagnostic.py",
    "--type", "rockwell",
    "--ip", "192.168.1.105",
    "--slot", "0",        # Slot du processeur dans le châssis
]

print("Extraction des diagnostics Rockwell...")
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
```

---

## 3. Analyse des Résultats

### 3.1 Interprétation du tampon de diagnostic Siemens

Chaque entrée du tampon de diagnostic contient :

```json
{
  "id": 42,
  "timestamp": "2026-03-15 14:23:18.452",
  "event_type": "ERROR",
  "event_id": "16#02A1",
  "source": "OB121 (Program Cycle)",
  "description": "Erreur d'accès bloc de données DB100",
  "resolved": false
}
```

**Catégories d'événements typiques :**

| Type | Signification | Action recommandée |
|------|---------------|-------------------|
| `INFO` | Événement normal (passage en RUN) | Surveillance |
| `WARNING` | Condition anormale (batterie faible) | Planifier maintenance |
| `ERROR` | Défaut actif (arrêt CPU, erreur accès) | Analyse immédiate |
| `FAULT` | Défaut matériel (carte défectueuse) | Remplacement nécessaire |

### 3.2 Seuils d'alerte de temps de cycle

| Niveau | Siemens S7-1500 | Rockwell ControlLogix |
|--------|----------------|----------------------|
| Normal | < 50% de la watchdog | < 75% du taux de tâche |
| Surveillé | 50–80% | 75–90% |
| Critique | > 80% | > 90% → défaut majeur |

---

## Pièges Courants (Common Pitfalls)

1. **Tentative de connexion Snap7 sur S7-1200/1500 sans configuration :**
   * *Erreur :* La connexion Snap7 échoue avec une erreur `ISO Connection Error` (errno 0x6102).
   * *Correction :* Dans TIA Portal, au niveau des propriétés de la CPU, il faut impérativement :

     1. Cocher la case **« Permettre l'accès via la communication PUT/GET du partenaire distant »** (dans Protection & Sécurité → Accès distants).
     2. Configurer le niveau d'accès en mode **« Accès complet (pas de protection) »**.
     3. S'assurer que les blocs de données (DB) interrogés ne possèdent pas l'attribut **« Optimized Block Access »** (accès optimisé) si l'on souhaite lire des adresses absolues.
     4. Désactiver le pare-feu Windows sur le poste de diagnostic (ou configurer une règle pour le port 102).

2. **Châssis multi-slots (Rockwell) - mauvais slot processeur :**
   * *Erreur :* Le script renvoie une erreur de timeout ou se connecte à une carte réseau (ex: 1756-EN2T) au lieu de la CPU.
   * *Correction :* Identifier le slot correct du processeur ControlLogix dans le châssis (généralement slot 0). Utiliser `RSLinx Classic` pour visualiser la carte du châssis (mode DH+ ou Ethernet) et confirmer l'emplacement.

3. **Dépassement de la watchdog de communication :**
   * *Erreur :* Le script expire après 30 secondes sur les grands automates avec des centaines de blocs DB.
   * *Correction :* Augmenter le timeout de connexion : `--timeout 120`. Si le réseau est lent, réduire le périmètre de lecture avec `--no-memory` et `--no-diagnostic`.

4. **Mode simulation activé sans bibliothèques :**
   * *Erreur :* Le script bascule en mode simulation et renvoie des données factices, ce qui peut masquer un réel échec de connexion.
   * *Correction :* Vérifier l'installation des bibliothèques avec :

     ```bash
     pip show python-snap7 pylogix
     ```

     Forcer le mode réel avec `--no-simulate`.

5. **Différence de slot entre S7-300 et S7-1500 :**
   * *Erreur :* Utiliser slot=1 pour un S7-300 (lequel utilise slot=2).
   * *Correction :* Respecter la règle :
     | Gamme | Rack | Slot |
     |-------|------|------|
     | S7-300 | 0 | 2 |
     | S7-400 | 0 | 3 (variable selon châssis) |
     | S7-1200 | 0 | 1 |
     | S7-1500 | 0 | 1 |

---

## Liste de vérification (Checklist)

- [ ] La bibliothèque `python-snap7` est installée pour les diagnostics Siemens.
- [ ] La bibliothèque `pylogix` est installée pour les diagnostics Rockwell.
- [ ] Le port `102` (Siemens S7Comm) ou `44818` (Rockwell EtherNet/IP) est ouvert et accessible depuis le poste de diagnostic.
- [ ] La fonction PUT/GET est activée dans la configuration matérielle de la CPU Siemens.
- [ ] Le slot du processeur spécifié correspond à la topologie physique réelle du châssis.
- [ ] Le script gère gracieusement le fallback vers le mode simulation si les bibliothèques ne sont pas installées (`--no-simulate` pour forcer le mode réel).
- [ ] Le temps de cycle de la CPU est extrait et comparé aux seuils d'alerte.
- [ ] Le tampon de diagnostic est lu (Siemens) ou le journal d'erreurs fautes (Rockwell) et analysé pour les événements non résolus.
- [ ] L'occupation mémoire (travail et chargement) est extraite et documentée.
- [ ] Les compteurs de redémarrages et la durée de fonctionnement sont consignés dans le rapport.

