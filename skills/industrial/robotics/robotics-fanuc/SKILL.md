---
name: robotics-fanuc
description: "Générer et programmer du code robotique Fanuc."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [fanuc, robotics, tp, karel, trajectory, industrial-robotics, matrix-math]
  related_skills: [plc-robot-dialogue]
---

# Programmation Robotique Fanuc (TP & KAREL) : Trajectoires 3D & Calculs Matriciels

## Vue d'ensemble

Cette compétence régit le développement, l'édition, et la modélisation de programmes pour bras robotiques Fanuc. Elle fournit les algorithmes de palettisation dynamique en Teach Pendant (TP), la configuration de charge (Payload), et les calculs géométriques tridimensionnels complexes par manipulation de matrices homogènes en KAREL.

---

## Logique TP : Algorithme de Palettisation Dynamique

Pour palettiser des pièces sur une grille tridimensionnelle ($N \times M \times P$), on calcule un offset dynamique appliqué à une position de dépose de référence.

```text
/PROG  PROG_PALLETIZING
/ATTR
COMMENT     = "Palettisation Grille";
/APPL
/MN
  1:  !======================================== ;
  2:  ! CALCULS D'OFFSETS DE GRILLE DYNAMIQUES  ;
  3:  !======================================== ;
  4:  UTOOL_NUM=1 ;                            ! Outil Ventouse
  5:  UFRAME_NUM=3 ;                           ! Repère Palette
  6:  PAYLOAD[2] ;                             ! Charge ventouse pleine
  7:  ;
  8:  ! R[1]:IndexColonne, R[2]:IndexLigne, R[3]:IndexCouche ;
  9:  ! R[4]:DistCol (150mm), R[5]:DistLigne (200mm), R[6]:HautCouche (100mm) ;
 10:  ;
 11:  ! 1. Calcul de l'offset en X (Colonnes) ;
 12:  PR[10,1:OffsetPal]=R[1]*R[4] ;
 13:  ! 2. Calcul de l'offset en Y (Lignes) ;
 14:  PR[10,2:OffsetPal]=R[2]*R[5] ;
 15:  ! 3. Calcul de l'offset en Z (Couches) ;
 16:  PR[10,3:OffsetPal]=R[3]*R[6] ;
 17:  ;
 18:  ! Annulation des rotations dans l'offset ;
 19:  PR[10,4:OffsetPal]=0 ;
 20:  PR[10,5:OffsetPal]=0 ;
 21:  PR[10,6:OffsetPal]=0 ;
 22:  ;
 23:  ! Déplacement d'approche au-dessus de la case cible ;
 24:J P[1:RefDropPoint] 100% CNT50 Offset,PR[10:OffsetPal] Tool_Offset,PR[2:ApprochZ] ;
 25:  ;
 26:  ! Descente verticale vers le point de dépose exact ;
 27:L P[1:RefDropPoint] 250mm/sec FINE Offset,PR[10:OffsetPal] ;
 28:  ;
 29:  ! Commande de relâchement de pièce (Venturi) ;
 30:  RO[2:BlowOff]=ON ;
 31:  RO[3:VacuumOn]=OFF ;
 32:  WAIT RI[3:VacuumStatus]=OFF ;
 33:  WAIT 0.5sec ;
 34:  RO[2:BlowOff]=OFF ;
 35:  ;
 36:  ! Remontée verticale ;
 37:L P[1:RefDropPoint] 400mm/sec CNT30 Offset,PR[10:OffsetPal] Tool_Offset,PR[2:ApprochZ] ;
 38:  PAYLOAD[1] ;                             ! Charge outil vide
/END
```

---

## Programme KAREL : Transformation Homogène de Coordonnées Vision

En KAREL, la correction de coordonnées s'effectue en multipliant une position nominale par une matrice de transformation homogène $T$ ($4 \times 4$) représentant les écarts de translation ($X,Y,Z$) et de rotation (Yaw, Pitch, Roll) mesurés par une caméra.

```karel
PROGRAM KL_VisionCorrection
%ALPHABETIZE
%COMMENT = 'Correction Matrices'
%NOLOCKGROUP

VAR
    pos_nominal  : POSITION    -- Position de référence apprise
    pos_corrected: POSITION    -- Position recalculée
    mat_offset   : POSITION    -- Décalage mesuré par la vision (X,Y,Z, W,P,R)
    status       : INTEGER
    rX, rY, rZ   : REAL
    rW, rP, rR   : REAL

BEGIN
    -- 1. Récupération des décalages de vision depuis les registres réels R[11..16]
    GET_REG(11, FALSE, rX, status)
    GET_REG(12, FALSE, rY, status)
    GET_REG(13, FALSE, rZ, status)
    GET_REG(14, FALSE, rW, status)
    GET_REG(15, FALSE, rP, status)
    GET_REG(16, FALSE, rR, status)
    
    -- Construction de la position de décalage cartésien
    mat_offset := POS(rX, rY, rZ, rW, rP, rR, '')
    
    -- 2. Lecture de la position nominale globale de prise (P[5])
    pos_nominal := GET_POS_REG(5, status)
    
    -- 3. Multiplication matricielle pour appliquer la transformation vision :
    -- Formule homogène : Corrected = Nominal : Offset
    pos_corrected := pos_nominal : mat_offset
    
    -- 4. Écriture de la position corrigée finale dans le registre de position PR[5]
    SET_POS_REG(5, pos_corrected, status)
    
    WRITE('Recalage vision applique avec succes.', CR)
END KL_VisionCorrection
```

---

## Directives d'Ingénierie Fanuc

1. **Configuration Dynamique du Payload (PAYLOAD Schedule)** :
   * Le robot doit basculer de payload en cours d'exécution. L'activation se fait via l'instruction TP `PAYLOAD[id]`.
   * Le paramétrage d'un payload comprend : le poids (kg), les coordonnées du centre de gravité ($X_g, Y_g, Z_g$) et les moments d'inertie ($I_x, I_y, I_z$).
2. **Singularités d'Axes** :
   * Les mouvements linéaires (`L`) passant près de la singularité de poignet (axe 5 proche de 0°) provoquent une vitesse angulaire infinie sur les axes 4 et 6, mettant le robot en défaut de surcouple. Recommander l'utilisation du mode de mouvement de contournement `WJNT` (Joint au poignet) dans ces zones :
     ```text
     L P[5] 500mm/sec CNT50 WJNT ;
     ```
