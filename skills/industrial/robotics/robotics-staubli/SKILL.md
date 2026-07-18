---
name: robotics-staubli
description: "Utiliser quand l'utilisateur demande de programmer des robots Stäubli sous SRS (Stäubli Robotics Suite) en langage VAL 3, ou d'interfacer des contrôleurs CS8/CS9."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [staubli, robotics, val3, srs, industrial-robotics]
    related_skills: [industrial-protocols, ot-security]
---

# Programmation de Robots Stäubli (VAL 3 & SRS)

## Vue d'ensemble

Les robots **Stäubli** (séries TX, TX2, RX, SCARA TS2) équipés des baies de contrôle **CS8C** ou **CS9** se programment à l'aide du langage structuré propriétaire **VAL 3**. Ce langage, proche de la syntaxe du langage C, offre une structure orientée objet très modulaire et sécurisée.

Composants clés de l'écosystème Stäubli :
1.  **Stäubli Robotics Suite (SRS) :** Environnement de développement Windows officiel pour configurer la cellule 3D, programmer en VAL 3, transférer les projets vers les contrôleurs réels et émuler le pupitre de commande (MCP).
2.  **Modularité de VAL 3 (Applications) :** Un projet VAL 3 est découpé en applications distinctes. Chaque application contient :
    *   Les variables de données (types `point`, `jointRx`, `tool`, `frame`).
    *   Les programmes (procédures exécutables : `start()`, `stop()`, etc.).
    *   Les bibliothèques tierces intégrées.
3.  **Tâche de surveillance automatique (`motion`) :** Le contrôle des trajectoires est asynchrone par rapport au code logique. Le programme dépose des commandes dans une pile de mouvements (buffer de mouvements) que le processeur de trajectoire exécute en temps réel.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir, de lire ou d'éditer du code en langage VAL 3.
- D'implémenter des fonctions de synchronisation ou de contrôle de trajectoire (`movej`, `movel`, `appro`, `waitEndMove`).
- De configurer des tâches logiques parallèles non liées aux mouvements (tâches asynchrones via `taskCreate`).
- D'interfacer le contrôleur CS8/CS9 en OPC UA ou TCP/IP avec un SCADA ou un automate.

**Ne pas utiliser pour :**
- Les anciens contrôleurs Stäubli (comme la baie ADEPT ou les robots programmés en VAL II / V+).

---

## 1. Programmation en langage VAL 3

Voici la structure standard d'un programme VAL 3 d'inspection avec prise de pièce sous la forme d'un fichier source :

```pascal
// --- FICHIER PROGRAMME VAL 3 : start() ---
// Ce programme est appelé au démarrage de l'application robot.
program start()
begin
  // 1. Initialisations de la cellule
  title("Controle Cellule Actemium");
  cls();
  putln("Demarrage de l'application...");

  // Chargement de l'outil et de la vitesse
  tGripper.dPoints[0] = {0, 0, 120, 0, 0, 0} // Décalage de la pince en Z (120mm)
  mSpeed.vlim = 1000                         // Limite de vitesse à 1000 mm/s
  mSpeed.blend = blend.joint                 // Raccordement fluide des trajectoires

  // Déplacement initial vers la position d'attente (Home)
  // jHome est une variable globale de type jointRx
  movej(jHome, tGripper, mSpeed)

  // Boucle de cycle infinie
  bExitLoop := false
  while (bExitLoop == false)
    putln("Attente signal de cycle...")
    
    // Attente du signal de départ automate (Entrée logique)
    wait(diPLCStart == true)
    doRobotBusy := true
    doRobotDone := false

    // --- Séquence d'approche ---
    // Utilisation de la fonction appro() pour calculer un décalage vertical (Z-100)
    pApproach := appro(pPickPos, {0, 0, -100, 0, 0, 0})
    movej(pApproach, tGripper, mSpeed)
    
    // Déplacement linéaire vers le point de prise
    movel(pPickPos, tGripper, mSpeed)
    
    // Attendre que le robot ait fini de bouger physiquement
    waitEndMove()

    // --- Actionneur : Prise Pièce ---
    doCloseGripper := true
    wait(diGripperClosed == true)
    delay(0.5) // Temporisation d'attente en secondes

    // --- Dégagement et Dépose ---
    movel(pApproach, tGripper, mSpeed)
    
    pApproachDrop := appro(pDropPos, {0, 0, -100, 0, 0, 0})
    movej(pApproachDrop, tGripper, mSpeed)
    movel(pDropPos, tGripper, mSpeed)
    waitEndMove()

    // Relâcher la pièce
    doCloseGripper := false
    delay(0.5)

    // Dégagement et retour Home
    movel(pApproachDrop, tGripper, mSpeed)
    movej(jHome, tGripper, mSpeed)
    waitEndMove()

    // Signaux de fin de cycle
    doRobotBusy := false
    doRobotDone := true
    wait(diPLCStart == false)
  endWhile
end
```

---

## 2. Gestion des Tâches Asynchrones (Multitâches)

VAL 3 permet de lancer des processus en tâche de fond (par ex. pour vérifier des conditions thermiques ou communiquer via socket).

```pascal
program start_background()
begin
  // Lance la procédure 'monitor_status' dans une tâche nommée 'tMonitor'
  // avec une priorité de 10 (basse) et une période de 0.05 seconde.
  taskCreate "tMonitor", 0.05, monitor_status()
end

program monitor_status()
begin
  while (true)
    // Lecture de la température du contrôleur
    fControllerTemp := getControllerTemp()
    if (fControllerTemp > 65.0)
      doTempWarning := true
      putln("Alerte: temperature contrôleur élevée!")
    else
      doTempWarning := false
    endIf
    delay(1.0) // Pause de la tâche de surveillance
  endWhile
end
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Dépassement de la pile de mouvements (Motion Buffer Overflow) :**
    *   *Erreur :* Empiler des centaines d'instructions de déplacements courts dans une boucle `while` sans utiliser d'instruction d'attente. La pile de mouvements sature et le contrôleur lève une erreur système.
    *   *Correction :* Utiliser l'instruction `waitEndMove()` pour bloquer l'empilement ou gérer le flux avec la fonction `getOverrun()` pour vérifier si le tampon de trajectoire est plein.
2.  **Omission de l'attente physique avant l'activation d'un outil :**
    *   *Erreur :* Envoyer la commande d'ouverture de la pince (`doCloseGripper := false`) immédiatement après l'instruction de mouvement `movel()` sans attendre la fin du mouvement. Le robot relâchera la pièce *pendant* qu'il est en train de se déplacer vers le point, provoquant des chutes de pièces.
    *   *Correction :* Toujours insérer `waitEndMove()` avant toute commande d'actionneur qui nécessite que le robot soit à l'arrêt complet sur son point cible.

---

## Liste de vérification (Checklist)

- [ ] L'application VAL 3 est compilée sans erreur de syntaxe dans Stäubli Robotics Suite (SRS).
- [ ] L'instruction `waitEndMove()` est correctement positionnée avant chaque activation physique d'outil (pince, ventouse).
- [ ] Les décalages de points critiques utilisent la fonction `appro()` pour éviter les collisions directes de l'outil.
- [ ] Les variables de configuration de type `tool` et `mdesc` (motion descriptor) sont déclarées et initialisées avant les commandes de mouvement.

