---
name: isa88-batch-control
description: "Structurer le code PLC selon le standard ISA-88."
version: 1.3.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [isa-88, batch, phase, state-model, process-automation, standard]
  related_skills: [siemens-scl-generation, beckhoff-ads-integration]
---

# Organisation et Structuration ISA-88 (Batch Control) dans les Automates

## Vue d'ensemble

Cette compétence régit l'organisation du code d'automatisation des procédés de type "Batch" (discontinus) selon les standards internationaux **ANSI/ISA-88 (IEC 61512)**. Elle détaille la modélisation complète des 17 états logiques d'une phase de procédé et l'interaction sécurisée avec les modules de commande (Control Modules).

---

## Modèle d'États de l'ISA-88 (S88 State Model)

Chaque Phase d'Équipement doit implémenter un automate fini gérant 17 états. Le tableau ci-dessous explicite le rôle et la nature de chaque état :

| État | Nature | Rôle fonctionnel |
| :--- | :--- | :--- |
| **IDLE** | Stable | Attente d'un ordre de démarrage (`START`). Équipement à l'arrêt sécurisé. |
| **STARTING** | Transitoire | Initialisation de la phase, vérification des permissives et démarrage. |
| **RUNNING** | Stable | Exécution de la logique principale de production (ex: chauffe, dosage). |
| **COMPLETING** | Transitoire | Fin de cycle (ex: vidange, refroidissement de ligne). |
| **COMPLETED** | Stable | Tâche terminée avec succès. Attente de l'ordre de réinitialisation (`RESET`). |
| **PAUSING** | Transitoire | Décélération ou mise en attente temporaire de l'équipement. |
| **PAUSED** | Stable | Arrêt temporaire. Permet de reprendre immédiatement l'état `RUNNING`. |
| **HOLDING** | Transitoire | Transition d'arrêt sécurisé suite à un défaut process ou une commande `HOLD`. |
| **HELD** | Stable | Phase suspendue et figée dans un état sûr. Attente de `RESTART` ou `ABORT`. |
| **RESTARTING** | Transitoire | Vérification des permissives avant reprise de la production. |
| **STOPPING** | Transitoire | Transition d'arrêt ordonné du procédé. |
| **STOPPED** | Stable | Procédé arrêté proprement. Attente d'un ordre `RESET` pour nettoyage. |
| **ABORTING** | Transitoire | Transition d'arrêt d'urgence instantané de tous les actionneurs. |
| **ABORTED** | Stable | Sécurité maximale. Attente d'un ordre `RESET` manuel après réarmement. |
| **RESETTING** | Transitoire | Initialisation des variables, compteurs et nettoyage physique. |

---

## Modèle de Dialogue Asynchrone Sécurisé Phase / CM (Structured Text)

Dans une architecture ISA-88, une Phase ne pilote jamais directement les I/O physiques de l'automate. Elle envoie des requêtes à un **Control Module (CM)** (ex: une vanne motorisée ou un variateur) et surveille ses états de retour.
Si le CM n'atteint pas l'état requis dans un délai imparti (Timeout), la phase doit lever un défaut et passer de manière autonome en mode de repli (`Holding`).

```pascal
TYPE UDT_Phase_Control :
STRUCT
    bStart          : BOOL;     // Lancement de la phase
    bHold           : BOOL;     // Demande de mise en pause
    bRestart        : BOOL;     // Demande de reprise
    bAbort          : BOOL;     // Demande d'arrêt d'urgence
    bReset          : BOOL;     // Réinitialisation après fin ou défaut
    rTargetQty      : REAL;     // Consigne quantité à transférer (Litres)
END_STRUCT
END_TYPE

TYPE UDT_Phase_Status :
STRUCT
    iState          : INT;      // État S88 courant
    bActive         : BOOL;     // Phase en cours
    bFault          : BOOL;     // Défaut actif de la phase
    rTransferredQty : REAL;     // Quantité déjà transférée (Litres)
END_STRUCT
END_TYPE

PROGRAM PRG_Phase_Transfert
VAR_INPUT
    Ctrl            : UDT_Phase_Control;
    rFlowRate       : REAL;     // Mesure de débit courant (L/s)
    
    (* Interfaces vers les Control Modules (CM) *)
    bStsValveOpened : BOOL;     // Retour d'état ouverte de la vanne de transfert
    bStsValveFault  : BOOL;     // Défaut matériel de la vanne
END_VAR

VAR_OUTPUT
    Status          : UDT_Phase_Status;
    bCmdValveOpen   : BOOL;     // Commande logique vers le Control Module Vanne
END_VAR

VAR
    tmrValveTimeout : TON;      // Surveillance du temps d'ouverture vanne
    rQtyAccumulated : REAL;     // Volume accumulé (Litres)
    iCurrentState   : INT := 0; // S88 State interne
END_VAR

VAR_TEMP
    dT              : REAL;     // Pas de temps de la tâche (s)
END_VAR

BEGIN
    dT := 0.1; // Supposons un cycle fixe de 100ms
    
    // 1. GESTION DES TRANSITIONS DE SÉCURITÉ PRIORITAIRES (ABORT / STOP)
    IF Ctrl.bAbort THEN
        iCurrentState := 60; // ABORTING
    END_IF;

    // 2. MACHINE D'ÉTAT S88
    CASE iCurrentState OF
        0:  // IDLE
            bCmdValveOpen := FALSE;
            Status.bActive := FALSE;
            Status.bFault := FALSE;
            rQtyAccumulated := 0.0;
            IF Ctrl.bStart THEN
                iCurrentState := 10; // RUNNING
            END_IF;
            
        10: // RUNNING
            Status.bActive := TRUE;
            bCmdValveOpen := TRUE; // Demande d'ouverture au CM
            
            // Intégration du volume transféré (bilan)
            rQtyAccumulated := rQtyAccumulated + (rFlowRate * dT);
            
            // Sécurité : Surveillance du temps de réponse du CM vanne (Timeout 5.0 secondes)
            tmrValveTimeout(IN := NOT bStsValveOpened, PT := T#5s);
            
            IF bStsValveFault OR tmrValveTimeout.Q THEN
                tmrValveTimeout(IN := FALSE);
                Status.bFault := TRUE;
                iCurrentState := 20; // HOLDING (Défaut)
            ELIF Ctrl.bHold THEN
                iCurrentState := 20; // HOLDING (Volontaire)
            ELIF rQtyAccumulated >= Ctrl.rTargetQty THEN
                iCurrentState := 30; // COMPLETING (Objectif atteint)
            END_IF;
            
        20: // HOLDING (Mise en sécurité)
            bCmdValveOpen := FALSE; // Demande de fermeture de sécurité de la vanne
            
            // Attente de l'arrêt effectif ou de l'acquittement
            IF NOT bStsValveOpened THEN
                iCurrentState := 21; // HELD
            END_IF;
            
        21: // HELD (Sécurité acquise / En attente)
            bCmdValveOpen := FALSE;
            IF Ctrl.bRestart AND NOT bStsValveFault THEN
                iCurrentState := 22; // RESTARTING
            END_IF;
            
        22: // RESTARTING
            // Réinitialisation des diagnostics avant retour en RUNNING
            tmrValveTimeout(IN := FALSE);
            iCurrentState := 10; // Retour en RUNNING
            
        30: // COMPLETING
            bCmdValveOpen := FALSE;
            iCurrentState := 31; // COMPLETED
            
        31: // COMPLETED
            bCmdValveOpen := FALSE;
            Status.bActive := FALSE;
            IF Ctrl.bReset THEN
                iCurrentState := 70; // RESETTING
            END_IF;
            
        60: // ABORTING (Urgence)
            bCmdValveOpen := FALSE; // Coupure physique immédiate
            iCurrentState := 61; // ABORTED
            
        61: // ABORTED
            bCmdValveOpen := FALSE;
            Status.bActive := FALSE;
            IF Ctrl.bReset THEN
                iCurrentState := 70; // RESETTING
            END_IF;
            
        70: // RESETTING
            rQtyAccumulated := 0.0;
            Status.bFault := FALSE;
            tmrValveTimeout(IN := FALSE);
            iCurrentState := 0; // Retour à IDLE
    END_CASE;
    
    // Copie vers la structure externe de statut
    Status.iState := iCurrentState;
    Status.rTransferredQty := rQtyAccumulated;
END_PROGRAM
```
