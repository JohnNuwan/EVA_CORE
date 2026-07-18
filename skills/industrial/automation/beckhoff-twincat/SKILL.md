---
name: beckhoff-twincat
description: "Programmer sous TwinCAT et utiliser le protocole ADS."
version: 1.2.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [beckhoff, twincat, ads, ethercat, plc, industrial-automation, pyads, multi-read]
    related_skills: [industrial-protocols, systematic-debugging]
---

# Beckhoff TwinCAT & Architecture PC Control

## Vue d'ensemble

L'approche de Beckhoff repose sur le concept de **PC Control** : transformer un PC industriel (IPC ou Embedded PC sous Windows ou TwinCAT/BSD) en contrôleur temps réel déterministe de haute performance. L'environnement de développement et de programmation est **TwinCAT 3** (intégré directement sous Microsoft Visual Studio).

Concepts fondamentaux de l'environnement :
1.  **Système Temps Réel (Real-Time Extension) :** TwinCAT s'approprie un ou plusieurs cœurs logiques du processeur de l'IPC pour exécuter les tâches automates de manière déterministe (sans interférence de l'OS hôte).
2.  **EtherCAT (Bus de terrain) :** Protocole Ethernet industriel ultra-rapide offrant des temps de cycle de tâche extrêmement faibles (< 100 microsecondes) et une synchronisation distribuée (Distributed Clocks).
3.  **ADS (Automation Device Specification) :** Protocole de messagerie standardisé client-serveur propre à Beckhoff. Il permet l'échange de données en local ou sur le réseau TCP/IP entre le runtime temps réel (PLC) et les applications du monde informatique (Python, C#, SCADA, bases de données).

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Écrire du code Texte Structuré (ST) conforme à la norme CEI 61131-3 3ème édition pour TwinCAT 3 (incluant la POO).
- Configurer les liaisons matérielles (I/O linking) via les pragmas automates dans Visual Studio.
- Établir une communication ADS entre un script externe (ex: Python via la bibliothèque `pyads`) et l'automate TwinCAT.
- Diagnostiquer des défauts de topologie EtherCAT ou des codes d'erreur ADS réseau.
- Structurer les tâches automates, la rétention mémoire (VAR_PERSISTENT / NOVRAM) et le monitoring temps réel.

---

## 1. Programmation TwinCAT 3 : Orientée Objet (POO) & Pragmas

TwinCAT 3 supporte pleinement la programmation orientée objet (POO) pour le Texte Structuré (ST).

### Exemple d'implémentation POO (Interface et Méthode) :

```pascal
// --- DÉFINITION DE L'INTERFACE ---
// Fichier : I_Sensor.TcIO
INTERFACE I_Sensor
METHOD ReadValue : REAL
END_METHOD

// --- DÉFINITION DE LA CLASSE D'IMPLÉMENTATION ---
// Fichier : FB_AnalogSensor.TcPOU
FUNCTION_BLOCK FB_AnalogSensor IMPLEMENTS I_Sensor
VAR
    rRawValue   : REAL;  (* Valeur brute du canal ADC *)
    rScalingMax : REAL := 100.0;
END_VAR

METHOD ReadValue : REAL
ReadValue := (rRawValue / 32767.0) * rScalingMax;
END_METHOD
```

### Utilisation des Attributs Pragmas
Les pragmas permettent de configurer le comportement du compilateur, de lier les variables aux E/S physiques ou d'exposer des tags à des services système (OPC UA, IHM).

```pascal
// Fichier : GVL_Exchange.TcGVL
{attribute 'qualified_only'}
VAR_GLOBAL
    // Rend cette variable visible par le serveur OPC UA intégré de TwinCAT
    {attribute 'OPC.UA.DA' := '1'}
    rTemperatureProcess : REAL;

    // Associe automatiquement la variable au canal d'E/S de la borne physique sans configuration manuelle
    {attribute 'TcLinkTo' := 'TIIB^Device 1 (EtherCAT)^Term 1 (EK1100)^Term 3 (EL3064)^Channel 1^Value'}
    iAnalogInputRaw      : INT;
    
    // Pragma pour forcer le monitoring en temps réel d'une propriété dans le debugger Visual Studio
    {attribute 'monitoring' := 'call'}
    bMotorRunningStatus  : BOOL;
END_VAR
```

---

## 2. Communication Python ↔ TwinCAT via `pyads` (Recettes Avancées)

Pour collecter des données à des fins d'analyse ou piloter l'automate depuis un script Python (comme l'agent EVA), la bibliothèque `pyads` est utilisée.

### Règle d'Or de Performance : La Lecture Groupée (Multi-Read)
Pour optimiser la bande passante et éviter de surcharger le routeur ADS, regroupez toujours vos requêtes en une seule trame réseau TCP au lieu de faire des boucles de requêtes individuelles.

### Abonnement Asynchrone aux Variables (Device Notifications)
Au lieu de poller (interroger périodiquement) des variables d'état (ex: alarmes), abonnez-vous aux notifications de changement envoyées par l'automate.

### Script Python de communication :

```python
import pyads
import time
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TwinCAT_ADS")

AMS_NET_ID = "192.168.1.50.1.1"  # NetID de l'automate cible
PLC_PORT = 851                   # Port par défaut de la tâche PLC 1 (TwinCAT 3)

def notification_callback(notification, name):
    """Fonction callback déclenchée sur changement d'état d'une variable abonnée."""
    value = notification.contents.data
    logger.info(f"[NOTIF] Variable '{name}' a changé de valeur : {value}")

def main():
    # Initialisation de la connexion ADS
    plc = pyads.Connection(AMS_NET_ID, PLC_PORT)
    
    try:
        plc.open()
        logger.info("Connexion ADS ouverte avec succès.")

        # 1. Exemple de Lecture/Écriture Groupée (Multi-Read)
        tags_to_read = [
            "GVL_Exchange.rTemperatureProcess",
            "MAIN.fbMotor.bMotorOn",
            "MAIN.fbMotor.bTimeoutError"
        ]
        
        # Lecture groupée
        read_results = plc.read_list_by_name(tags_to_read)
        logger.info(f"Résultats de lecture groupée : {read_results}")
        
        # Écriture groupée
        tags_to_write = {
            "MAIN.bStartCmd": True,
            "MAIN.rSpeedSetpoint": 45.5
        }
        plc.write_list_by_name(tags_to_write)
        logger.info("Écriture groupée effectuée.")

        # 2. Exemple d'Abonnement Asynchrone (Device Notification)
        # S'abonne au bit d'alarme de l'automate
        alarm_tag = "MAIN.fbMotor.bTimeoutError"
        attr = pyads.NotificationAttrib(sizeof=1) # 1 octet pour BOOL
        
        # Ajout de la notification (déclenchement en cas de changement de valeur)
        notification_handle = plc.add_device_notification(
            alarm_tag, 
            attr, 
            notification_callback, 
            user_handle=alarm_tag
        )
        logger.info(f"Abonnement actif sur '{alarm_tag}'. En attente d'événements...")

        # Simulation d'activité pendant 10 secondes
        time.sleep(10)

        # Suppression de l'abonnement
        plc.del_device_notification(notification_handle, attr)
        logger.info("Abonnement désactivé.")

    except pyads.ADSError as err:
        logger.error(f"Erreur ADS rencontrée [Code {err.errid}] : {err}")
    finally:
        plc.close()
        logger.info("Connexion ADS fermée.")

if __name__ == "__main__":
    main()
```

---

## Guide des Codes d'Erreur ADS Courants

| Code (Hex / Dec) | Signification | Cause possible & Résolution |
| :--- | :--- | :--- |
| **0x702 / 1794** | `Invalid Signature` | Mauvaise correspondance de type de données ou de structure de données. |
| **0x705 / 1797** | `Device not active` | L'automate n'est pas démarré (vérifier s'il est en mode RUN). |
| **0x710 / 1808** | `Symbol not found` | Chemin symbolique de la variable erroné (sensible à la casse). |
| **0x745 / 1861** | `Timeout` | Route ADS manquante ou ports bloqués par le pare-feu (TCP/UDP 48897). |

---

## Pièges Courants (Common Pitfalls)

1. **Licence d'évaluation expirée :**
   * *Erreur :* Le runtime refuse de démarrer ou s'arrête toutes les 7 secondes en mode configuration.
   * *Correction :* Ouvrir le projet TwinCAT dans Visual Studio ➔ Aller dans *System* ➔ *License* ➔ Cliquer sur *Generate 7 days Trial License* et saisir le code captcha de sécurité. Renouvelable indéfiniment.
2. **Route ADS à sens unique :**
   * *Erreur :* La connexion ADS échoue en timeout bien que l'IPC réponde au ping réseau standard.
   * *Correction :* Une route ADS doit impérativement être configurée **des deux côtés** (sur le client et sur l'IPC TwinCAT cible). Utiliser le gestionnaire de routes de TwinCAT ou le fichier `StaticRoutes.xml`.
3. **Variables persistantes non sauvegardées :**
   * *Erreur :* Les compteurs de production ou réglages d'étalonnage déclarés dans `VAR_PERSISTENT` reviennent à zéro lors d'une coupure brutale d'alimentation.
   * *Correction :* S'assurer que le PC industriel dispose d'une alimentation sans coupure (UPS) Beckhoff configurée dans le système pour déclencher l'écriture automatique de la mémoire rémanente en NOVRAM/Flash avant l'extinction, ou appeler la fonction `WritePersistentData` cycliquement dans le code.

---

## Liste de vérification (Checklist)

- [ ] La description frontmatter YAML fait moins de 60 caractères et se termine par un point.
- [ ] Les routes statiques ADS mutuelles sont configurées et testées entre les deux machines.
- [ ] Le port TCP `48897` de communication ADS est autorisé dans le pare-feu de l'IPC.
- [ ] La tâche automate (Task) est affectée à un cœur de processeur isolé (Isolated Core) dédié pour le temps réel dans Visual Studio.
- [ ] Les variables de type `VAR_PERSISTENT` sont associées à un module d'écriture sécurisé (NOVRAM ou UPS active).
- [ ] Les fonctions d'accès externe (scripts Python, SCADA) utilisent des requêtes de liste groupée (Multi-read/write) ou des abonnements asynchrones.
- [ ] Les pragmas d'attributs de mappage E/S (`{attribute 'TcLinkTo'}`) sont correctement formatés selon la topologie physique cible.

