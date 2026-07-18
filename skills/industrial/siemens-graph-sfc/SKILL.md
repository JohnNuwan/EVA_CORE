---
name: siemens-graph-sfc
description: "Programmer les séquences machine en Siemens S7-GRAPH et SFC."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, windows]
metadata:
  tags: [siemens, graph, s7-graph, sfc, grafcet, sequences, step-control, TIA-portal, interlocks, supervisions]
  related_skills: [iec61131-3-programming-standards, siemens-scl-generation]
---

# Programmation Séquentielle sous Siemens S7-GRAPH (SFC) dans TIA Portal

Cette compétence encadre la conception, la programmation et la maintenance de graphes séquentiels de commande (Grafcet / SFC) sous l'environnement Siemens S7-GRAPH pour automates S7-1500 et S7-300/400.

---

## 1. Structures de Séquences Complexes (Aiguillages et Parallélismes)

Dans la modélisation SFC (Sequential Function Chart) de la norme IEC 61131-3, les séquences réelles de machines ne sont pas purement linéaires. Deux structures fondamentales doivent être maîtrisées par l'agent.

### Divergence et Convergence en "OU" (Aiguillage / Sélectif)
* **Divergence en OU (Alternative / OR-split)** : Permet de choisir une trajectoire parmi plusieurs selon les transitions. Les conditions de transition doivent être mutuellement exclusives pour éviter des activations simultanées de branches divergentes.
* **Convergence en OU (OR-join)** : Regroupe les branches alternatives vers une étape commune.

### Divergence et Convergence en "ET" (Séquences Simultanées / Parallèles)
* **Divergence en ET (AND-split - Double trait horizontal)** : Active simultanément plusieurs branches parallèles à partir d'une seule transition.
* **Convergence en ET (AND-join - Double trait horizontal)** : Synchronise les branches parallèles. L'étape suivante ne s'active que si toutes les étapes finales des branches parallèles sont actives ET que la transition commune de sortie est vraie (`TRUE`).

---

## 2. Variables d'Éléments Internes GRAPH et Adressage Symbolique

Le DB d'instance généré automatiquement pour un bloc S7-GRAPH contient des variables d'état normalisées décrivant le statut des étapes et des sécurités.

* **S[x].X** : Bit d'activité de l'étape $x$ (ex: `S2.X = TRUE` signifie que l'étape 2 est active).
* **S[x].T** : Temps d'activité actuel de l'étape $x$ (de type `TIME`). Remis à `T#0s` lors de l'activation.
* **S[x].LA** : Bit de défaut d'interverrouillage (Interlock alarm active).
* **S[x].SA** : Bit de défaut de supervision (Supervision alarm active).
* **S[x].U** : Statut logique de la condition d'interverrouillage de l'étape $x$.
* **S[x].V** : Statut logique de la condition de supervision de l'étape $x$.

---

## 3. Exemple de Code SCL pour Interagir avec un Bloc S7-GRAPH

En programmation structurée d'atelier, on écrit souvent un bloc SCL externe pour lire le statut d'un graphe GRAPH, remonter les temps de cycle ou forcer une transition en mode manuel.

```pascal
FUNCTION_BLOCK "FB_Actemium_SequenceManager"
VAR_INPUT
    StartSequence : BOOL;
    StopSequence : BOOL;
    AcknowledgeFaults : BOOL;
END_VAR
VAR_OUTPUT
    CurrentActiveStep : INT;
    SequenceFaultActive : BOOL;
    StepExecutionTime : TIME;
END_VAR
VAR_IN_OUT
    (* Instance du bloc GRAPH passe en reference *)
    GraphDb : "DB_CycleUsinage";
END_VAR
VAR
    (* Memoire interne *)
    PrevStep : INT := -1;
END_VAR

    // 1. Gestion des commandes de base du graphe
    IF StartSequence THEN
        GraphDb.INIT_SQ := TRUE; // Force le retour a l'etape initiale S1
    ELSE
        GraphDb.INIT_SQ := FALSE;
    END_IF;

    IF StopSequence THEN
        GraphDb.OFF_SQ := TRUE;  // Arrete l'execution de la sequence complete
    ELSE
        GraphDb.OFF_SQ := FALSE;
    END_IF;

    // Acquittement des defauts de supervision du graphe
    GraphDb.ACK_EF := AcknowledgeFaults;

    // 2. Extraction des informations de diagnostic
    SequenceFaultActive := GraphDb.ERR_FLT; // Le bit ERR_FLT est vrai en cas de defaut de supervision
    
    // Identification de l'etape active actuelle (Lecture du registre interne)
    CurrentActiveStep := GraphDb.S_NO;
    
    // Recuperation du temps d'execution de l'etape 3 (par exemple)
    IF GraphDb.S003.X THEN
        StepExecutionTime := GraphDb.S003.T;
    ELSE
        StepExecutionTime := T#0s;
    END_IF;

END_FUNCTION_BLOCK
```

---

## 4. Exemple de Code Source Textuel S7-GRAPH Complexe (Divergence en ET)

Ce code source textuel montre une divergence en ET activant deux opérations parallèles (la rotation d'un plateau diviseur et la lubrification d'un outil) convergées ensuite vers une étape de dégagement.

```pascal
ORGANIZATION_BLOCK "Sequence_Parallele"
CLASS ="S7-GRAPH"
BEGIN
    STEP S1 (Initial := TRUE)
    TITLE := "Attente Piece"
    END_STEP
    
    TRANSITION T1
    FROM S1 TO (S2, S3) // Divergence en ET (AND-split) : active S2 et S3 en meme temps
    CONDITION := "Cellule_Piece_Presente" AND "Commande_Cycle";
    END_TRANSITION
    
    // Branche 1 : Usinage / Rotation
    STEP S2
    TITLE := "Action_Plateau"
    ACTION
        N : "Motor_Rotation_Plateau";
    END_ACTION
    END_STEP
    
    TRANSITION T2
    FROM S2 TO S4
    CONDITION := "Plateau_En_Position";
    END_TRANSITION
    
    STEP S4
    TITLE := "Attente_Synchronisation_Branche_1"
    END_STEP
    
    // Branche 2 : Lubrification / Refroidissement
    STEP S3
    TITLE := "Action_Lubrification"
    ACTION
        N : "Electrovanne_Huile";
    END_ACTION
    INTERLOCK := "Niveau_Huile_Correct"; // Condition d'interlock
    END_STEP
    
    TRANSITION T3
    FROM S3 TO S5
    CONDITION := "Pression_Lubrification_Atteinte";
    END_TRANSITION
    
    STEP S5
    TITLE := "Attente_Synchronisation_Branche_2"
    END_STEP
    
    // Convergence en ET (AND-join)
    // S4 et S5 doivent etre TOUTES LES DEUX actives pour franchir la transition T4
    TRANSITION T4
    FROM (S4, S5) TO S6
    CONDITION := "Autorisation_Ejection";
    END_TRANSITION
    
    STEP S6
    TITLE := "Ejection_Piece"
    ACTION
        N : "Verin_Ejecteur";
    END_ACTION
    SUPERVISION := "Capteur_Ejection_Ok" NOT ATTAINED AFTER T#5s;
    END_STEP
    
    TRANSITION T5
    FROM S6 TO S1
    CONDITION := "Capteur_Ejection_Ok";
    END_TRANSITION
END_ORGANIZATION_BLOCK
```
