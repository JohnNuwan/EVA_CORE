---
name: siemens-scl
description: "Générer, optimiser et déboguer du code Siemens SCL."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [siemens, scl, tia-portal, plc, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Programmation Siemens SCL (TIA Portal)

## Vue d'ensemble

Le Structured Control Language (SCL) est un langage textuel de haut niveau basé sur le Pascal, défini dans la norme CEI 61131-3 (Structured Text). Il est particulièrement adapté pour le traitement de données complexes, les calculs mathématiques, les algorithmes de tri et la manipulation de tableaux dans les automates Siemens (S7-1200, S7-1500, S7-300 et S7-400).

Cette compétence aide l'agent Helios à concevoir du code SCL propre, modulaire, optimisé pour TIA Portal, et conforme aux bonnes pratiques industrielles et aux standards Actemium.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De générer des blocs fonctionnels Siemens (`FB` ou `FC`) en SCL.
- De traduire du logique à contacts (LADDER/CONT) ou des logigrammes (LOG/FBD) en SCL.
- De concevoir des structures de données (UDT) ou des blocs de données (DB).
- D'optimiser des boucles de traitement de données ou des calculs dans TIA Portal.
- De déboguer des erreurs de syntaxe SCL.

**Ne pas utiliser pour :**
- Des automates d'autres marques (utiliser `rockwell-studio5000` pour Rockwell Allen-Bradley).
- De la configuration réseau pure ou du diagnostic matériel sans lien avec le code SCL.

---

## Règles de Conception et d'Architecture

### 1. Function Block (FB) vs Function (FC)

- **Function Block (FB) :** À utiliser lorsque le bloc nécessite une mémoire d'état entre deux cycles (ex. : un temporisateur interne, une alarme mémorisée, un séquenceur). Un FB est toujours associé à un bloc de données d'instance (Instance DB).
- **Function (FC) :** À utiliser pour des blocs de calculs purs, des conversions ou des opérations sans mémoire d'état. Les variables temporaires d'un FC perdent leur valeur à la fin de l'exécution du bloc.

### 2. Accès Optimisé (Optimized Block Access)

Pour les automates S7-1200 et S7-1500, toujours privilégier l'accès optimisé pour les DB et les blocs :
- Pas d'adresses absolues (ex. : éviter `%DB1.DBX0.0` ou `%MW10`).
- Accès uniquement par nom symbolique (ex. : `InstanceDB.StatusWord.Bit0`).
- Permet au compilateur d'organiser les données en mémoire de manière optimale et accélère l'exécution.

### 3. Standards de Nommage des Variables

Respecter le standard de nommage Actemium pour différencier la portée et le type de variable :

| Type de Variable | Préfixe | Exemple | Description |
| :--- | :--- | :--- | :--- |
| **Input** (Entrée) | `i_` ou `in_` | `i_StartSignal` | Paramètre d'entrée du bloc. |
| **Output** (Sortie) | `q_` ou `out_` | `q_MotorRunning` | Paramètre de sortie du bloc. |
| **InOut** (Entrée/Sortie) | `iq_` ou `io_` | `iq_ProcessValue` | Paramètre passé par référence. |
| **Static** (Statique) | `stat_` | `stat_CycleCounter` | Variable interne persistante (FB uniquement). |
| **Temp** (Temporaire) | `temp_` | `temp_LoopIndex` | Variable en pile, non persistante. |
| **Constant** | `c_` | `c_MaxLimit` | Valeur constante fixe. |

---

## Guide de Syntaxe SCL & Recettes

### 1. Déclaration d'un Bloc en SCL (Fichier Source `.scl`)

Voici le squelette d'un Function Block (FB) standard incluant les déclarations de variables et la logique :

```scl
FUNCTION_BLOCK "FB_Actemium_ControlMotor"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR_INPUT
      i_Start : Bool;   // Commande de démarrage
      i_Stop : Bool;    // Commande d'arrêt
      i_Fault : Bool;   // Signal de défaut matériel
   END_VAR

   VAR_OUTPUT
      q_Run : Bool;     // Sortie commande moteur
      q_Error : Bool;   // Indication de défaut
   END_VAR

   VAR
      stat_Active : Bool;  // État mémorisé de marche
   END_VAR

BEGIN
   // Logique de marche/arrêt avec sécurité défaut
   IF #i_Fault THEN
      #stat_Active := FALSE;
      #q_Error := TRUE;
   ELSIF #i_Stop THEN
      #stat_Active := FALSE;
      #q_Error := FALSE;
   ELSIF #i_Start AND NOT #q_Error THEN
      #stat_Active := TRUE;
   END_IF;

   // Assignation de la sortie physique
   #q_Run := #stat_Active;
END_FUNCTION_BLOCK
```

*Note : TIA Portal utilise le symbole `#` devant les variables locales au bloc.*

### 2. Instructions Logiques et Conditionnelles

- **IF / THEN / ELSIF / ELSE :**
```scl
IF #i_Temperature > 80.0 THEN
    #q_Overheating := TRUE;
    #q_FanSpeed := 100;
ELSIF #i_Temperature > 50.0 THEN
    #q_Overheating := FALSE;
    #q_FanSpeed := 50;
ELSE
    #q_Overheating := FALSE;
    #q_FanSpeed := 0;
END_IF;
```

- **CASE (Idéal pour les machines d'état) :**
```scl
CASE #stat_Step OF
    0:  // Étape Initiale
        #q_Motor := FALSE;
        IF #i_Start THEN
            #stat_Step := 10;
        END_IF;
        
    10: // Démarrage moteur
        #q_Motor := TRUE;
        IF #i_RunningFeedback THEN
            #stat_Step := 20;
        END_IF;
        
    20: // Surveillance
        IF NOT #i_RunningFeedback THEN
            #stat_Step := 99; // Erreur
        END_IF;
        
    99: // État Erreur
        #q_Motor := FALSE;
        #q_Alarm := TRUE;
        IF #i_Reset THEN
            #q_Alarm := FALSE;
            #stat_Step := 0;
        END_IF;
END_CASE;
```

### 3. Boucles de Traitement

- **Boucle FOR (Idéal pour parcourir les Tableaux / Arrays) :**
```scl
// Initialisation ou cumul sur un tableau
#temp_TotalVal := 0;
FOR #temp_Index := 0 TO 9 DO
    #temp_TotalVal := #temp_TotalVal + #iq_SensorData[#temp_Index];
END_FOR;
```

### 4. Utilisation des Temporisateurs (Timers IEC)

Toujours déclarer les Timers IEC dans les variables statiques du FB pour éviter l'allocation de DB de travail externes inutiles (concept de multi-instance) :

**Déclaration :**
```scl
VAR
    stat_TimerMotor : TON_TIME; // Ou IEC_TIMER
END_VAR
```

**Appel dans le code :**
```scl
#stat_TimerMotor(IN := #i_StartCmd,
                 PT := T#5s);

#q_DelayedStart := #stat_TimerMotor.Q;
```

---

## Pièges Courants (Common Pitfalls)

1. **Confusion sur la persistance des variables TEMP :**
   * *Erreur :* Écrire une valeur dans une variable `VAR_TEMP` (ex. : `#temp_State`) à la fin d'un cycle et s'attendre à la retrouver au cycle suivant.
   * *Correction :* Utiliser les variables `VAR` (statiques) pour stocker les informations persistantes entre deux cycles de tâche automate.

2. **Outil d'indexation hors limites (Array Out of Bounds) :**
   * *Erreur :* Utiliser une variable d'index dans une boucle FOR sans vérifier les bornes du tableau. Cela peut provoquer le crash de l'automate (CPU Stop) si le tableau n'a pas les bonnes dimensions.
   * *Correction :* Déclarer explicitement des constantes ou utiliser les fonctions Siemens `LOWER_BOUND` et `UPPER_BOUND` pour sécuriser les boucles dynamiques.

3. **Utilisation intensive de boucles WHILE non sécurisées :**
   * *Erreur :* Utiliser une boucle `WHILE` ou `REPEAT` dont la condition de sortie peut ne pas être atteinte. Cela augmente le temps de cycle de l'automate et déclenche le chien de garde (Watchdog) de la CPU (passage en STOP).
   * *Correction :* Toujours privilégier des boucles `FOR` ou ajouter un compteur de sécurité pour forcer la sortie de la boucle `WHILE`.

---

## Liste de vérification (Checklist)

- [ ] Les variables d'entrées ont le préfixe `i_`, les sorties `q_`, et les statiques `stat_`.
- [ ] Le bloc compile sans avertissements concernant les conversions de types implicites (utiliser `INT_TO_REAL`, `REAL_TO_INT` si nécessaire).
- [ ] Tous les index de tableaux (`Array`) sont sécurisés pour éviter un dépassement de limites en run-time.
- [ ] Les temporisateurs (Timers) sont déclarés comme variables d'instance statiques (`TON_TIME` ou `IEC_TIMER`) et non comme des DB globaux séparés.
- [ ] Le code est exempt de variables magiques (utiliser des `VAR CONSTANT` à la place).

