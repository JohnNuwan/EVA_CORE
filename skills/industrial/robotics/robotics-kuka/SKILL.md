---
name: robotics-kuka
description: "Générer et programmer du code robotique KUKA."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [kuka, krl, plc, robot, automation-engineering, sub-interpreter]
  related_skills: [plc-robot-dialogue]
---

# Programmation Robotique KUKA (KRL) : Palpage Rapide & Submit Interpreter

## Vue d'ensemble

Cette compétence régit la conception de programmes avancés sous KUKA System Software (KSS). Elle détaille l'implémentation de la tâche asynchrone d'arrière-plan **Submit Interpreter (`SPS.SUB`)**, l'utilisation d'entrées de palpage rapides (`$MEAS_PULSE`) pour le recalage de trajectoire, et la résolution de singularités de poignet.

---

## Le Submit Interpreter (SPS.SUB) : Logique d'Arrière-Plan Multitâche

Le **Submit Interpreter** est une tâche non liée aux mouvements qui tourne en boucle infinie en arrière-plan. Elle permet de surveiller la sécurité des équipements d'outillage (pressions, verrous), de gérer les mots d'échange avec l'automate en dehors du cycle cinématique, et de piloter les voyants de la cellule.

```kuka
; =======================================================
; EXTRAIT DU FICHIER SYSTEME SPS.SUB (Boucle Utilisateur)
; =======================================================
DEF  USER_LOOP ( )
  ; 1. Gestion de la sécurité et lubrification outil
  IF $OUT[1] AND NOT $IN[3] THEN
    ; Si l'outil est commandé fermé mais pas de retour pression
    $OUT[5] = TRUE ; Alarme voyant rouge
  ELSE
    $OUT[5] = FALSE
  END_IF

  ; 2. Heartbeat avec l'automate (Changement d'état d'un bit de vie)
  $OUT[10] = NOT $IN[10]

  ; 3. Forçage de l'acquittement de défauts système par le bouton HMI
  IF $IN[11] THEN
    $ERR_STATUS = 0 ; Reset des erreurs
  END_IF
END
```

---

## Palpage Tactile Rapide avec Entrée de Mesure

Pour recaler les trajectoires d'après la position réelle d'une pièce brute (ex: fonderie), on utilise la fonction de mesure rapide `$MEAS_PULSE` couplée à une interruption. Dès que le palpeur (connecté à l'entrée matérielle de mesure rapide) touche la pièce, le contrôleur KRC4 capture instantanément la coordonnée cartésienne exacte dans la variable système `$POS_INT`.

```kuka
; =======================================================
; FICHIER SOURCE : PRG_TOUCH_PROBE.SRC
; =======================================================
DEF PRG_TOUCH_PROBE()
  BAS (#INITMOV, 0)
  $TOOL = TOOL_DATA[1]
  $BASE = BASE_DATA[1]
  
  PTP XHOME ; Point de départ sécurisé
  
  ; 1. Déclaration de l'interruption rapide sur l'entrée de palpage ($IN[5])
  ; Dès que le palpeur touche la pièce (IN[5] = TRUE), appel de la routine RECORD_POS
  INTERRUPT DECL 15 WHEN $IN[5] == TRUE DO RECORD_POS()
  
  ; Point de départ d'approche au-dessus de la pièce
  PTP XStartSearch
  
  ; Activation de l'interruption
  INTERRUPT ON 15
  
  ; 2. Lancement du mouvement de descente linéaire lent (Recherche de contact)
  ; Le point XMaxSearch est situé sous la surface attendue de la pièce
  $VEL.CP = 0.05 ; Vitesse de palpage très lente (50 mm/s)
  LIN XMaxSearch
  
  ; Désactivation immédiate si le mouvement va au bout sans toucher (Défaut)
  INTERRUPT OFF 15
  HALT ; Si on arrive ici, le palpage a échoué (pièce absente)
END

; 3. ROUTINE DE GESTION DU CONTACT
DEF RECORD_POS()
  INTERRUPT OFF 15
  RESUME ; Arrête et annule le mouvement en cours (LIN XMaxSearch) de la fonction parente
  
  ; Récupère la coordonnée exacte du point de contact capturée lors de l'interruption
  XContactPoint = $POS_INT
  
  ; Calcul de l'offset en Z par rapport au point nominal
  rOffsetZ = XContactPoint.Z - XNominalPoint.Z
  
  ; Recalage de la base de dépose
  BASE_DATA[2].Z = BASE_DATA[2].Z + rOffsetZ
  
  ; Retour rapide sécurisé vers le point haut
  LIN XStartSearch
END
```

---

## Résolution des Singularités Mécaniques

Les robots 6 axes possèdent des configurations singulières où deux axes deviennent colinéaires (notamment l'axe 4 et l'axe 6 alignés lorsque l'axe 5 est à 0°). Le contrôleur KUKA ne peut plus déterminer l'orientation et l'un des axes doit tourner à une vitesse infinie, provoquant un arrêt de sécurité.

### Recommandations de contournement KRL :
1. **Régulation de singularité par le contrôleur** :
   Activer la fonction système `$SINGUL_ERR` pour lever une erreur explicite ou utiliser l'option de commande de mouvement interpolé `PTP_REL` ou `LIN` avec option d'orientation pour forcer l'axe 5 à garder un angle minimal de $\pm 5$°.
2. **Configuration du poignet ($S$ et $T$)** :
   Dans le fichier `.DAT`, renseigner précisément les paramètres d'état et de tour (`Status` et `Turn` de la structure `E6POS`) sur les points fixes pour forcer la configuration mécanique du robot et interdire le retournement de l'axe 5.
   * *Status (S)* : Définit la configuration géométrique (bras au-dessus/en-dessous, coude vers le haut/bas).
   * *Turn (T)* : Définit le sens de rotation individuel des axes pour les angles supérieurs à $180$°.
