---
name: siemens-scl-generation
description: "Générer et structurer du code SCL Siemens."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [siemens, TIA-Portal, scl, plc, automation-engineering]
  related_skills: [industrial-plc-connectivity, rockwell-l5x-courbon-conventions]
---

# Génération et Structure de Code Siemens SCL (TIA Portal)

## Vue d'ensemble

Cette compétence guide l'agent pour écrire, structurer et documenter du code source au format Structured Control Language (SCL) pour les automates Siemens (S7-1200 et S7-1500) sous TIA Portal. Le langage SCL est conforme à la norme IEC 61131-3 (Structured Text) avec des spécificités d'accès au système Siemens.

---

## Outils Associés

Les outils de communication directe suivants peuvent être mobilisés :
- `` `siemens_s7_get_cpu_info` `` : Lecture de l'identité et du statut de la CPU.
- `` `siemens_s7_read_tag` `` : Lecture en direct de variables DB ou Merker.
- `` `siemens_s7_write_tag` `` : Écriture en direct de variables DB ou Merker.

---

## Guide d'Ingénierie & Patterns de Code SCL

### 1. Traitement des Mesures Analogiques (NORM_X / SCALE_X)
Dans TIA Portal, les entrées analogiques (ex: cartes 4-20mA ou 0-10V) renvoient des valeurs brutes de type `INT` sur une plage de `0` à `27648`. La conversion en valeur physique (ex: `0.0` à `100.0` °C) s'effectue en deux étapes.

```pascal
FUNCTION "FC_ScaleAnalog" : Real
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR_INPUT 
      iRawValue : Int;       // Valeur brute de l'entrée analogique (0 - 27648)
      rMinPhys  : Real;      // Borne minimale de l'échelle physique (ex: 0.0)
      rMaxPhys  : Real;      // Borne maximale de l'échelle physique (ex: 100.0)
   END_VAR

   VAR_TEMP
      rNormalized : Real;    // Valeur intermédiaire normalisée (0.0 - 1.0)
   END_VAR

BEGIN
    // 1. Normalisation de la valeur brute (0 à 27648) vers une échelle de 0.0 à 1.0
    #rNormalized := NORM_X(MIN := 0, VALUE := #iRawValue, MAX := 27648);
    
    // 2. Mise à l'échelle de la valeur normalisée vers la plage physique finale
    #FC_ScaleAnalog := SCALE_X(MIN := #rMinPhys, VALUE := #rNormalized, MAX := #rMaxPhys);
END_FUNCTION
```

### 2. Temporisateurs Système en Multi-Instance (TON)
Pour éviter de multiplier les blocs de données (DB) d'instance individuels pour chaque temporisateur, les timers (`TON`, `TOF`) doivent être déclarés en **multi-instance** dans la section `VAR` (statique) du bloc fonctionnel parent (`FB`).

```pascal
FUNCTION_BLOCK "FB_ConveyorControl"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR_INPUT 
      bSensorStart : Bool;   // Détecteur présence colis début convoyeur
      bSensorEnd   : Bool;     // Détecteur présence colis fin convoyeur
   END_VAR

   VAR_OUTPUT 
      bMotorRun : Bool;      // Commande de démarrage moteur
   END_VAR

   VAR 
      instTimerStart : TON;  // Temporisateur de retard au démarrage (Multi-instance)
      instTimerEnd   : TON;  // Temporisateur de sécurité arrêt (Multi-instance)
   END_VAR

BEGIN
    // Temporisateur de retard de 2 secondes avant démarrage
    #instTimerStart(IN := #bSensorStart, PT := T#2s);
    
    // Démarrage moteur si retard validé et pas de colis en fin
    IF #instTimerStart.Q AND NOT #bSensorEnd THEN
        #bMotorRun := TRUE;
    END_IF;
    
    // Temporisateur de sécurité : arrêt moteur après 10s si le capteur de fin n'est pas activé
    #instTimerEnd(IN := #bMotorRun, PT := T#10s);
    
    IF #instTimerEnd.Q OR #bSensorEnd THEN
        #bMotorRun := FALSE;
    END_IF;
END_FUNCTION_BLOCK
```

---

## Règles de Conception et Bonnes Pratiques Siemens

1. **Syntaxe de Variables locales et globales** :
   * **Variables locales** (entrées, sorties, temporaires, statiques) : Toujours préfixées par le hashtag `#` (ex: `#iRawValue`, `#instTimerStart`).
   * **Variables globales** (déclarées dans un DB global) : Toujours entourées de guillemets doubles (ex: `"DB_GlobalData".MoteurVitesse`).
2. **Structures de Contrôle et Sélections** :
   * Pour les machines d'états (Step/GraFCET), utiliser l'instruction `CASE` plutôt qu'une suite de `IF-ELSE` :
     ```pascal
     CASE #iState OF
         0: // Initialisation
             #bMotorRun := FALSE;
             IF #bStart THEN
                 #iState := 10;
             END_IF;
         10: // En cours
             #bMotorRun := TRUE;
             IF #bSensorEnd THEN
                 #iState := 20;
             END_IF;
         ELSE
             #iState := 0;
     END_CASE;
     ```
3. **Format du fichier source** :
   * Les blocs doivent être clairement séparés par leur définition de bloc (`FUNCTION_BLOCK` ou `FUNCTION`) et se terminer par `END_FUNCTION_BLOCK` ou `END_FUNCTION`.
