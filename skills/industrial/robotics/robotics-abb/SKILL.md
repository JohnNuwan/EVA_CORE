---
name: robotics-abb
description: "Générer et programmer du code robotique ABB RAPID."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [abb, rapid, robot, trajectory, industrial-robotics, automation, external-axes]
  related_skills: [plc-robot-dialogue]
---

# Programmation Robotique ABB (RAPID) : Axes Externes & Mouvements Circulaires

## Vue d'ensemble

Cette compétence régit l'écriture avancée de programmes en langage RAPID d'ABB pour les applications complexes. Elle traite de l'asservissement d'axes externes coordonnés (rails de translation, tables d'orientation), de l'interpolation circulaire (`MoveC`) et de l'architecture multitâche RobotWare.

---

## Intégration d'Axes Externes Coordonnés (`extjoint`)

Pour les robots montés sur un rail linéaire de translation (axe externe `Eax_a`), le type de données géométriques `robtarget` doit définir la position de cet axe dans sa structure `extjoint`.

### Structure d'une coordonnée avec axe externe :
```rapid
! robtarget: [ [X, Y, Z], [q1, q2, q3, q4], [robconf], [eax_a, eax_b, eax_c, eax_d, eax_e, eax_f] ]
! eax_a à eax_f représentent les positions des axes externes (en mm ou en degrés)
```

---

## Exemple de Cordon de Colle Circulaire avec Axe Externe (RAPID)

Cette procédure réalise un cordon de colle circulaire parfait autour d'une pièce. Le robot est monté sur un portique linéaire (axe externe `eax_a` positionné à 1500 mm). La buse de colle doit maintenir une orientation constante (normale à la surface).

```rapid
MODULE Mod_GlueApplication
    ! 1. PERSISTANCES ET CONFIGURATIONS D'OUTIL ET PRODUIT
    PERS tooldata tGlueGun:=[TRUE,[[0,0,250],[1,0,0,0]],[3.2,[0,0,100],[1,0,0,0],0,0,0]];
    PERS wobjdata wobjTable:=[FALSE,TRUE,"",[[1500,600,0],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
    
    ! Points géométriques intégrant la position du rail linéaire (eax_a = 1500mm)
    CONST robtarget pHome:=[[0,400,600],[1,0,0,0],[0,0,0,0],[1500,9E9,9E9,9E9,9E9,9E9]];
    CONST robtarget pStartGlue:=[[0,200,50],[1,0,0,0],[0,0,0,0],[1500,9E9,9E9,9E9,9E9,9E9]];
    CONST robtarget pCircleMid:=[[100,300,50],[1,0,0,0],[0,0,0,0],[1500,9E9,9E9,9E9,9E9,9E9]];
    CONST robtarget pCircleEnd:=[[0,400,50],[1,0,0,0],[0,0,0,0],[1500,9E9,9E9,9E9,9E9,9E9]];
    
    VAR speeddata vGlueSpeed:=[200,50,200,20]; ! Vitesse de dépose de colle (200 mm/s)
    
    ! 2. PROCÉDURE PRINCIPALE
    PROC ApplyGlueCircular()
        ! Déplacement linéaire vers la position de départ de colle
        MoveL pStartGlue, vGlueSpeed, fine, tGlueGun \WObj:=wobjTable;
        
        ! Déclenchement de l'électrovanne de colle
        SetDO doStartGlueGun, 1;
        WaitTime 0.2; ! Temps de pressuration buse
        
        ! Interpolation Circulaire MoveC
        ! Nécessite 2 points : le point milieu (pCircleMid) et le point d'arrivée (pCircleEnd)
        MoveC pCircleMid, pCircleEnd, vGlueSpeed, z5, tGlueGun \WObj:=wobjTable;
        
        ! Arrêt de la dépose de colle
        SetDO doStartGlueGun, 0;
        
        ! Dégagement vertical
        MoveL Offs(pCircleEnd, 0, 0, 100), v1000, fine, tGlueGun \WObj:=wobjTable;
        
        ! Retour à la position d'origine
        MoveJ pHome, v1000, fine, tGlueGun;
    ENDPROC
ENDMODULE
```

---

## Le Multitâche RobotWare (Multitasking)

Le contrôleur IRC5 d'ABB permet d'exécuter plusieurs tâches en parallèle (jusqu'à 20 tâches en tâche de fond, configurées dans les paramètres système du contrôleur).
* **Tâche principale (`T_ROB1`)** : Gère les mouvements et les instructions cinématiques du bras.
* **Tâches d'arrière-plan (`T_BG_DIAG`, etc.)** : S'exécutent en boucle parallèle asynchrone (type `STATIC` ou `SEMISTATIC`) pour surveiller les interfaces de communication, les capteurs analogiques environnementaux ou collecter des métriques de maintenance sans ralentir le cycle de trajectoire du robot.

### Exemple de tâche d'arrière-plan asynchrone :
```rapid
MODULE Mod_BackgroundMonitor
    ! Tâche statique exécutée de façon autonome en arrière-plan
    PROC MonitorCycle()
        WHILE TRUE DO
            ! Si la température de l'outil dépasse un seuil de sécurité
            IF aiToolTemperature > 85.0 THEN
                SetDO doTempAlarm, 1;
            ELSE
                SetDO doTempAlarm, 0;
            END_IF;
            WaitTime 1.0; -- Échantillonnage de surveillance toutes les secondes
        ENDWHILE
    ENDPROC
ENDMODULE
```
