---
name: ot-security
description: "Cybersécurité OT et résilience selon l'ISA/IEC 62443."
version: 1.2.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [security, ot-security, 62443, secrets, resilience, network, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Cybersécurité OT & Résilience Logicielle (ISA/IEC 62443)

## Vue d'ensemble

Le réseau de production (OT) a des priorités distinctes du réseau informatique (IT). En OT, la priorité absolue est la **Disponibilité** et la **Sécurité des personnes et équipements (Safety)**, suivies par l'Intégrité et la Confidentialité. Lors du développement d'applications ou de scripts d'interface avec des automates ou des supervisions, il est crucial d'appliquer les principes fondamentaux de la norme **ISA/IEC 62443** au niveau du code.

Cette compétence guide l'agent Helios pour écrire des scripts d'informatique industrielle hautement résilients aux pannes réseaux, et sécurisés contre les vulnérabilités courantes du monde OT.

Le script d'assistance associé à cette compétence est disponible sous [ot_security_scanner.py](scripts/ot_security_scanner.py).

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Gérer la connexion à des bases de données SQL ou des APIs industrielles nécessitant des mots de passe.
- Écrire des scripts de passerelle ou de synchronisation de données OT/IT.
- Implémenter des scripts d'écriture de variables critiques (consignes machine, seuils de vitesse, vannes).
- Assurer la tolérance aux pannes réseaux (reconnexion automatique de scripts d'acquisition).
- Réaliser un inventaire non destructif ou un audit de ports industriels sur le réseau OT.

---

## 1. Directives de Développement Sécurisé en OT

### A. Gestion Sécurisée des Mots de Passe & Identifiants (Secrets)
Ne jamais insérer des mots de passe de bases de données, de serveurs OPC-UA ou de brokers MQTT en dur dans les scripts.
- **Utilisation de variables d'environnement (.env) :** Stocker les informations sensibles dans un fichier `.env` non partagé sur les dépôts de code (ex: git).
- **Lecture des secrets en Python :**
```python
import os
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASS")

# Connexion sécurisée
# connect(user=db_user, password=db_password)
```

### B. Validation des Écritures Automate (Garde-fous / Range Checks)
Puisque les scripts Python peuvent écrire directement dans la mémoire des automates (via Modbus, Snap7, ou PyLogix), toute écriture de consigne doit être précédée d'un contrôle de cohérence des plages de valeurs (Range Check) au niveau applicatif pour éviter des dysfonctionnements physiques sur la machine.

```python
def safe_write_speed_limit(client_plc, speed_setpoint: float):
    # Seuils de sécurité mécanique définis par le process
    MIN_SPEED = 0.0
    MAX_SPEED = 1500.0
    
    if speed_setpoint < MIN_SPEED or speed_setpoint > MAX_SPEED:
        raise ValueError("Consigne de vitesse %.2f hors limites de sécurité [%.1f, %.1f]" 
                         % (speed_setpoint, MIN_SPEED, MAX_SPEED))
                         
    # Si OK, procéder à l'écriture physique
    # client_plc.write('Tag_Speed', speed_setpoint)
```

### C. Résilience Réseau & Reconnaissance de Déconnexion
Les coupures réseau de quelques secondes ou minutes sont courantes en atelier. Les scripts ne doivent pas planter à la première déconnexion mais tenter des reconnexions périodiques tout en alertant les superviseurs.

```python
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Actemium_OT_Monitor")

def communication_loop(plc_client):
    reconnect_delay = 5.0 # Attendre 5s avant de réessayer
    
    while True:
        try:
            if not plc_client.is_connected():
                logger.warning("Connexion perdue. Tentative de reconnexion...")
                plc_client.connect()
                time.sleep(1)
                continue
                
            # Lecture de données
            data = plc_client.read_all_tags()
            logger.info("Données récupérées avec succès.")
            
            # Temps de boucle nominal
            time.sleep(2.0)
            
        except Exception as e:
            logger.error("Erreur de communication : %s. Nouvelle tentative dans %s secondes." 
                         % (str(e), reconnect_delay))
            time.sleep(reconnect_delay)
```

---

## 2. Utilisation du Script d'Assistance (Scan de Ports OT)

Pour exécuter le scanner de ports industriels de manière non-intrusive sur une plage réseau, utilisez l'outil d'exécution de code (`execute_code`) avec le script suivant :

```python
import subprocess

# Plage réseau à scanner (ex : automate local et son réseau)
targets = "127.0.0.1,192.168.1.0/24"

cmd = [
    ".venv/Scripts/python.exe", 
    "skills/industrial/standards-security/ot-security/scripts/ot_security_scanner.py",
    "--targets", targets,
    "--ports", "102,502,4840,44818", # S7Comm, Modbus, OPC UA, EtherNet/IP
    "--timeout", "0.5" # Temps d'attente court pour rester discret
]

print(f"Lancement de l'audit de sécurité réseau sur : {targets}...")
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Erreurs :", result.stderr)
```

---

## Pièges Courants (Common Pitfalls)

1. **Commit de fichiers de configuration contenant des mots de passe :**
   * *Erreur :* Commiter un fichier de configuration contenant des identifiants administrateur de la base SQL de production sur le dépôt Git.
   * *Correction :* Ajouter les fichiers `.env` ou de configuration locale contenant des mots de passe au fichier `.gitignore` et distribuer un fichier modèle vide (ex: `.env.example`).

2. **Écritures aveugles en boucle infinie (surcharges PLC) :**
   * *Erreur :* Écrire en permanence (chaque 10ms) la même valeur de consigne dans l'automate. Cela peut user prématurément la mémoire Flash de l'automate ou surcharger son processeur de communication.
   * *Correction :* Écrire uniquement sur changement de valeur (Write on Change) ou réguler la boucle d'écriture.

3. **Scans de ports agressifs (type Nmap) en production :**
   * *Erreur :* Lancer un scan réseau avec des requêtes de type SYN agressives ou des payloads mal formés sur d'anciens automates (ex. Siemens S7-300 ou anciens coupleurs Modbus Schneider). Cela peut bloquer le module de communication (CP) et provoquer l'arrêt de la CPU (Stop).
   * *Correction :* Utiliser exclusivement des connexions asynchrones douces (comme celle implémentée dans le script d'assistance) avec un délai suffisant (semaphores) et sans envoi de payloads non documentés.

---

## Liste de vérification (Checklist)

- [ ] La description frontmatter YAML fait moins de 60 caractères et se termine par un point.
- [ ] Aucun mot de passe, clé privée ou secret n'est écrit directement dans le code source.
- [ ] Les fichiers contenant des secrets de production locaux (ex: `.env`) sont ajoutés au fichier `.gitignore`.
- [ ] Les écritures de consignes machine ou de paramètres critiques possèdent des garde-fous pour refuser les valeurs aberrantes ou dangereuses.
- [ ] Les boucles de communication possèdent des blocs d'exception robustes et des mécanismes de reconnexion automatique en cas de coupure de liaison Ethernet.
- [ ] Tout scan réseau en production utilise une approche passive ou asynchrone non-intrusive à faible cadence.

