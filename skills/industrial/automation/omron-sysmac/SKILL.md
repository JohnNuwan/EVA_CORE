---
name: omron-sysmac
description: "Programmer sous Sysmac Studio et intégrer EtherCAT."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [omron, sysmac-studio, ethercat, fins, plc, industrial-automation, nj, nx, motion-control, iec-61131-3, servomoteur, cip]
    related_skills: [industrial-protocols, systematic-debugging, plc-converter, automation-linter]
---

# Automates Omron NJ/NX & Sysmac Studio

## Vue d'ensemble

Les contrôleurs de machine Omron des gammes **NJ (Machine Automation Controller)** et **NX (NX7, NX5)** représentent la plateforme d'automatisation moderne d'Omron, en remplacement des anciennes séries CJ1/CS1/C200H. Ils se programment via l'environnement unifié **Sysmac Studio**, conforme à la norme **CEI 61131-3** avec des extensions propriétaires Omron.

### Architecture Sysmac

```
    [IHM (NA Series)]       [SCADA / ERP]
          │                       │
          ▼                       ▼
    ┌─────────────────────────────────┐
    │         Sysmac Studio           │  ← Environnement de développement
    │  (Programmation, Configuration)  │
    └─────────────────────────────────┘
          │                       │
          ▼                       ▼
    ┌─────────────────────────────────┐
    │     NJ/NX Controller            │  ← Logique API + Motion + Sécurité
    │  ┌──────────┬──────────┐        │
    │  │ EtherCAT │ EtherNet │        │  ← Réseaux de terrain
    │  │ (Servos, │ /IP (CIP)│        │
    │  │  E/S NX) │ (SCADA)  │        │
    │  └──────────┴──────────┘        │
    └─────────────────────────────────┘
```

### Caractéristiques clés

1. **Moteur de mouvement et logique intégré** : Gestion conjointe de la logique API, des axes de mouvement (Motion Control) et de la sécurité fonctionnelle.
2. **Réseau machine EtherCAT** : Utilisation d'EtherCAT en standard pour la communication déterministe avec les servovariateurs (gamme 1S, G5), E/S déportées (série NX) et capteurs intelligents.
3. **Variables globales partagées (Tag-based)** : Plus d'adresses mémoire fixes (comme `D0`, `HR0` des anciennes gammes). Utilisation de tags textuels nommés typés.
4. **Communication externe** : Support natif d'EtherNet/IP (CIP) et du protocole historique FINS pour l'accès aux variables depuis les SCADA/IHM.

---

## Quand l'utiliser

### Cas d'usage

À utiliser lorsque l'utilisateur demande :

- D'écrire des scripts ou de la logique de programmation en **Texte Structuré (ST)** pour les automates Omron NJ/NX.
- De configurer ou dépanner des **nœuds de communication** ou des **topologies réseau EtherCAT** dans Sysmac Studio.
- De mettre en place des **connexions de tags** via le protocole EtherNet/IP ou FINS vers des supervisions.
- D'implémenter des **blocs fonctionnels de contrôle de mouvement** (Motion MC Blocks) pour piloter des servomoteurs (positionnement, vitesse, couple).
- De diagnostiquer des **problèmes de performance** de tâche EtherCAT (dépassement de temps de cycle).

### Ne pas utiliser pour

- La programmation de vieux automates Omron (séries C200H, CQM1, CJ1, CS1) programmés sous CX-Programmer (adresses mémoire directes DM/HR/CIO).
- La configuration avancée de sécurité fonctionnelle Omron (utiliser Sysmac Studio Safety).

---

## 1. Programmation en Texte Structuré (ST) sous Sysmac Studio

### 1.1 Règles de déclaration des variables

Sous Sysmac Studio, les variables doivent être **déclarées dans la table des variables** (Data Type : BOOL, INT, DINT, REAL, STRING, etc.) avant d'être utilisées en ST, contrairement à d'autres plateformes CEI 61131-3.

| Portée | Déclaration | Préfixe recommandé | Exemple |
|--------|------------|-------------------|---------|
| Globale | Global Variable Table | g_ | `g_Conv_Start_Cmd` |
| Locale à un POU | VAR | (aucun) | `Temp_Counter` |
| Entrée | VAR_INPUT | in_ | `in_Start_Command` |
| Sortie | VAR_OUTPUT | out_ | `out_Motor_Run` |
| Entrée/Sortie | VAR_IN_OUT | io_ | `io_Status_Word` |
| Interne | VAR | stat_ | `stat_Timer_Active` |
| Constante | VAR CONSTANT | c_ (UPPER) | `c_MAX_SPEED` |

### 1.2 Exemple : Logique d'asservissement de convoyeur

```pascal
// --- LOGIQUE DE DÉMARRAGE ET SÉCURITÉ CONVOYEUR ---
// Variables globales préalablement déclarées dans la table :
//   g_Conv_Start_Cmd   : BOOL ; Commande marche depuis IHM
//   g_Conv_Stop_Cmd    : BOOL ; Commande arrêt depuis IHM
//   g_Conv_Interlock   : BOOL ; Verrouillage sécurité machine
//   g_Conv_Fault       : BOOL ; Défaut thermique ou retour vitesse
//   g_Conv_Motor_Out   : BOOL ; Sortie physique relais moteur
//   g_Conv_Running     : BOOL ; Retour d'état marche (capteur)
PROGRAM Convoyeur_Control
VAR
    Timer_Running_Fault : TON;   // Temporisation défaut retour vitesse
    Fault_Count         : INT := 0;
END_VAR

// Auto-maintien de la commande de marche
IF (g_Conv_Start_Cmd OR g_Conv_Motor_Out)
   AND NOT g_Conv_Stop_Cmd
   AND g_Conv_Interlock
   AND NOT g_Conv_Fault THEN
    g_Conv_Motor_Out := TRUE;
ELSE
    g_Conv_Motor_Out := FALSE;
END_IF;

// Diagnostic : si commande active mais pas de retour moteur
IF g_Conv_Motor_Out AND NOT g_Conv_Running THEN
    Timer_Running_Fault(IN := TRUE, PT := T#3s);
ELSE
    Timer_Running_Fault(IN := FALSE);
END_IF;

IF Timer_Running_Fault.Q THEN
    g_Conv_Fault := TRUE;
    Fault_Count := Fault_Count + 1;
END_IF;
```

### 1.3 Exemple : Contrôle de mouvement avec blocs MC (Motion Control)

```pascal
// --- MOUVEMENT ABSOLU D'UN SERVOMOTEUR VERS UNE POSITION ---
// Configuration préalable dans Sysmac Studio :
// - Axe : Servo_Axe_X (type : Servo Drive, raccordé EtherCAT)
// - Unité : mm, vitesse max : 500 mm/s, accélération : 1000 mm/s²

MC_Power_Instance(
    Axis         := Servo_Axe_X,
    Enable       := TRUE,
    Enable_Positive := TRUE,
    Enable_Negative := TRUE,
    Busy         => MC_Power_Busy,
    Status       => MC_Power_Status,
    Error        => MC_Power_Error
);

// Positionnement absolu
MC_MoveAbsolute_Instance(
    Axis         := Servo_Axe_X,
    Execute      := g_Demande_Position,
    Position     := g_Position_Cible,   // En mm (variable DINT)
    Velocity     := 300.0,              // Vitesse en mm/s
    Acceleration := 1000.0,             // Accélération mm/s²
    Deceleration := 1000.0,             // Décélération mm/s²
    Jerk         := 5000.0,             // Jerk mm/s³ (optionnel)
    Done         => g_Move_Done,
    Busy         => g_Move_Busy,
    Active       => g_Move_Active,
    CommandAborted => g_Move_Aborted,
    Error        => g_Move_Error
);
```

---

## 2. Communication externe : FINS vs EtherNet/IP

### 2.1 Tableau comparatif

| Critère | EtherNet/IP (CIP) | FINS (Omron propriétaire) |
|---------|------------------|---------------------------|
| Standard | Ouvert (ODVA) | Propriétaire Omron |
| Découverte de tags | Automatique (CIP Path) | Manuelle (adresses mémoire) |
| Performances | Élevé (implicite/explicite) | Modéré |
| Configuration Sysmac | Aucune (import direct) | Allocation AT mémoire requise |
| Idéal pour | SCADA moderne (Ignition, Kepware) | Systèmes legacy, échange simple |

### 2.2 Connexion via EtherNet/IP (recommandée pour NJ/NX)

```python
# Exemple : Lecture de tags NJ/NX via pylogix (CIP)
from pylogix import PLC

with PLC() as comm:
    comm.IPAddress = "192.168.250.1"

    # Lecture d'une variable globale
    result = comm.Read("g_Conv_Motor_Out")
    print(f"g_Conv_Motor_Out = {result.Value}")

    # Lecture d'un programme structure
    result = comm.Read("Convoyeur_Control.Fault_Count")
    print(f"Fault_Count = {result.Value}")
```

### 2.3 Connexion via FINS (mode compatibilité)

Sur NJ/NX, le protocole FINS nécessite une allocation explicite via l'onglet **Memory Settings** de Sysmac Studio :

```text
Exemple : Associer la variable g_Recipe_ID à l'adresse D100
1. Dans Sysmac Studio, ouvrir Controller Settings → Memory Settings
2. Ajouter l'entrée : g_Recipe_ID  AT %D100
3. Télécharger la configuration vers le contrôleur
```

```python
# Exemple de lecture FINS via Python (bibliothèque omron-fins)
# pip install omron-fins
from omron_fins import OmronFins

conn = OmronFins("192.168.250.1", port=9600)
conn.destination_node = 1  # Node ID du NJ/NX configuré dans Sysmac

# Lecture de D100 (FINS address)
value = conn.read("D100", dtype="int16")
print(f"D100 = {value}")
```

---

## 3. Configuration EtherCAT

### 3.1 Règles de topologie EtherCAT

1. **Topologie en ligne (daisy-chain)** : Chaque esclave se connecte au précédent. C'est la topologie recommandée.
2. **Distance max** : 100 m entre deux nœuds (câble Ethernet standard CAT5e/CAT6).
3. **Nombre max d'esclaves** : Jusqu'à 192 esclaves par maître EtherCAT NJ/NX.
4. **Adresses de nœud** : Configurées via les switchs rotatifs sur les esclaves NX.
5. **Tâche synchrone** : La logique de mouvement (MC blocks) DOIT s'exécuter dans la tâche synchrone primaire (Primary Periodic Task).

### 3.2 Réglages de temps de tâche

| Configuration | Période | Usage typique |
|--------------|---------|---------------|
| Primaire (Primary) | 0.5–4 ms | Logique de mouvement, régulation |
| Secondaire (Secondary) | 5–50 ms | Logique machine, communication MES |
| Tâche d'initialisation | — | Code exécuté au démarrage |

---

## Pièges Courants (Common Pitfalls)

1. **Dépassement du temps de tâche EtherCAT (Task Period Exceeded) :**
   * *Erreur :* Configurer trop d'esclaves EtherCAT ou une logique de mouvement trop lourde pour un temps de cycle défini trop court (ex: tâche primaire réglée à 500 µs), provoquant un défaut de « Task Period Exceeded » et l'arrêt d'urgence du contrôleur (ER 0x4350).
   * *Correction :* Augmenter la période de la tâche primaire (ex: passer de 1 ms à 2 ms) ou déporter la logique non critique dans une tâche périodique secondaire de priorité inférieure. Utiliser le **moniteur de performance** dans Sysmac Studio pour identifier les blocs consommateurs.

2. **Incompatibilité de version de firmware (SD Memory Card Backup) :**
   * *Erreur :* Tenter de restaurer un projet Sysmac Studio compilé pour une version spécifique de CPU (ex: v1.40) sur un contrôleur physique possédant une version de firmware inférieure (ex: v1.12). La CPU refuse de démarrer.
   * *Correction :* Mettre à jour le firmware physique du contrôleur (via carte SD Omron) ou modifier la version cible du projet dans les paramètres du contrôleur sous Sysmac Studio avant de télécharger.

3. **Mauvaise gestion des adresses FINS allouées (AT) :**
   * *Erreur :* Associer deux variables différentes à la même adresse AT, ou oublier de déclarer une variable dans Memory Settings. Le contrôleur ne signale pas toujours l'erreur au téléchargement.
   * *Correction :* Vérifier soigneusement la table d'allocation AT dans Sysmac Studio. Utiliser des commentaires pour documenter chaque correspondance.

4. **Absence de terminaison EtherCAT :**
   * *Erreur :* Ne pas configurer le dernier esclave EtherCAT en mode « Terminated » (le switch DIP ou le logiciel). Le maître détecte une topologie ouverte et refuse de passer en RUN.
   * *Correction :* Configurer le dernier nœud EtherCAT avec le flag de terminaison (via les paramètres EtherCAT de l'esclave dans Sysmac Studio).

5. **Confusion entre déplacement relatif et absolu (MC Blocks) :**
   * *Erreur :* Utiliser `MC_MoveAbsolute` quand la position cible dépend de la position courante (il faut `MC_MoveRelative`). L'axe se positionne toujours au même point absolu, quel que soit son point de départ.
   * *Correction :* Bien différencier :
     - `MC_MoveAbsolute` : Position absolue dans le repère machine (ex: 150.0 mm).
     - `MC_MoveRelative` : Incrément de position (ex: avancer de +50.0 mm).
     - `MC_MoveVelocity` : Vitesse constante sans position cible.

---

## Liste de vérification (Checklist)

- [ ] Toutes les variables utilisées dans le code ST sont déclarées avec des types de données appropriés dans la table des variables Sysmac Studio.
- [ ] Le réseau EtherCAT est configuré sans erreur de topologie (chaque esclave correspond à l'adresse configurée).
- [ ] Le dernier esclave EtherCAT est configuré avec la terminaison active.
- [ ] Si le protocole FINS est requis, les variables globales ont été associées à des zones mémoire AT (ex: `%D100`).
- [ ] Les blocs MC (Motion Control) sont bien exécutés dans la tâche synchrone primaire (Primary Periodic Task).
- [ ] Les serveurs EtherNet/IP (CIP) sont activés dans les paramètres du contrôleur pour la communication SCADA.
- [ ] Le temps de cycle EtherCAT ne dépasse pas 80% de la période configurée.
- [ ] Les variables de diagnostic (`ErrorID`, `ErrorIDEx`) des blocs MC sont systématiquement vérifiées.
- [ ] Les versions de firmware du contrôleur et du projet Sysmac Studio correspondent.

