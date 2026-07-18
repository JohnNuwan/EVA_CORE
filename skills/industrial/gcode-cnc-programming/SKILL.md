---
name: gcode-cnc-programming
description: "Programmer en G-Code pour les machines CNC."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, windows]
metadata:
  tags: [gcode, cnc, milling, turning, sinumerik, fanuc, machining, iso6983, macro-b]
  related_skills: [industrial-programming-languages, robotics]
---

# Programmation G-Code (ISO 6983) pour Machines-Outils et Commandes Numériques (CNC)

Cette compétence régit l'écriture, l'analyse et l'optimisation de programmes en G-Code utilisés pour piloter les machines d'usinage industrielles (fraisage, tournage, découpe laser, robots d'impression) contrôlées par des commandes numériques de type Siemens Sinumerik ou Fanuc.

---

## 1. Bloc de Sécurité et Séquence d'Initialisation Standard

En production, tout programme CNC doit impérativement démarrer par une séquence de sécurité réinitialisant les états de la machine afin de prévenir les collisions d'outils dues à des reliquats de cycles précédents.

```text
%
O2001 (EVA - INITIALISATION SECURITE CNC)
N10 G90 G21 G40 G80 G49 G17 G94 (Modes absolus, métriques, annulations)
```
* **G90** : Mode de coordonnées absolu.
* **G21** : Unités métriques (mm).
* **G40** : Annulation de la compensation de rayon d'outil (éviter les décalages inattendus lors de l'approche).
* **G80** : Annulation de tout cycle de perçage ou taraudage actif.
* **G49** : Annulation de la compensation de longueur d'outil active.
* **G17** : Sélection du plan de travail principal XY.
* **G94** : Avance exprimée en mm/min (par opposition à G95, mm/révolution, typique du tournage).

---

## 2. Interpolation Circulaire de Précision (G02 / G03)

L'interpolation circulaire décrit des arcs de cercles parfaits. Deux syntaxes de définition géométrique coexistent et doivent être maîtrisées par l'agent.

### Syntaxe par rayon (R)
Idéale pour les arcs simples inférieurs à 180° :
```text
N50 G02 X50.0 Y25.0 R12.5 F300
```
* Si $R > 0$, l'arc décrit est le plus court possible (inférieur ou égal à 180°).
* Si $R < 0$, l'arc décrit est le plus long possible (supérieur à 180°).

### Syntaxe par décalage de centre (I, J, K)
**Obligatoire pour les cercles complets (360°)** pour éviter toute ambiguïté géométrique. `I` et `J` indiquent les distances relatives signées entre le point de départ de l'arc et le centre géométrique du cercle, respectivement sur les axes X et Y.
```text
N60 G02 X50.0 Y25.0 I12.5 J0.0 F300
```

---

## 3. Programmation Paramétrique avancée : Fanuc Macro B

La programmation paramétrique permet d'écrire des cycles génériques réutilisables (ex. usinage de brides, poches circulaires de dimensions variables).

### Types de Variables Fanuc
* **#1 à #33** : Variables locales (propres à un appel de macro via `G65`).
* **#100 à #199** : Variables communes (conservées après l'arrêt d'un programme, réinitialisées à la mise hors tension).
* **#500 à #999** : Variables système persistantes (sauvegardées en mémoire permanente).

### Exemple : Macro paramétrique de poche circulaire avec pas de descente hélicoïdal
Ce sous-programme réalise le vidage d'une poche en effectuant des passes hélicoïdales progressives.

```text
O9010 (MACRO POCHE CIRCULAIRE PARAMETRIQUE)
(Arguments transmis via G65 : )
(X = #24 : Coordonnee X centre poche)
(Y = #25 : Coordonnee Y centre poche)
(Z = #26 : Profondeur finale de la poche)
(R = #18 : Rayon de la poche)
(D = #7  : Diametre de la fraise utilisee)
(F = #9  : Vitesse d'avance de travail)

#100 = #18 - [#7 / 2] (Calcul du rayon de trajectoire de l'outil)
#101 = 0.0            (Z actuel d'usinage)
#102 = 1.5            (Pas de descente vertical par passe)

N10 G00 X#24 Y#25     (Positionnement rapide au centre de la poche)
N20 G01 Z2.0 F[#9 * 0.5] (Descente lente au-dessus de la matiere)

(Boucle de descente helicoidale)
WHILE [#101 GT #26] DO 1
    #101 = #101 - #102
    IF [#101 LT #26] THEN #101 = #26 (Limitation a la profondeur finale)
    
    (Mouvement d'entree radiale)
    G01 X[#24 + #100] Y#25 F#9
    (Mouvement de descente helicoidale complete)
    G02 X[#24 + #100] Y#25 I[-#100] J0.0 Z#101 F#9
    (Retour au centre pour degager l'outil)
    G01 X#24 Y#25
END 1

(Passe finale de finition à profondeur constante)
G01 X[#24 + #100] Y#25 F#9
G02 X[#24 + #100] Y#25 I[-#100] J0.0 F#9
G01 X#24 Y#25

G00 Z25.0 M09         (Degagement rapide Z)
M99                   (Retour au programme principal)
```

Pour appeler cette macro depuis le programme principal :
```text
N200 G65 P9010 X100.0 Y50.0 Z-12.0 R35.0 D16.0 F450
```

---

## 4. Gestion Rigoureuse des Compensations d'Usure (Offsets)

* **Compensation de géométrie d'outil (D / H)** : Représente les dimensions physiques nominales de l'outil (mesurées au banc de réglage).
* **Compensation d'usure (Wear Offset)** : Correctif millimétrique ajusté par l'opérateur sur le pupitre de la CNC pour corriger les dérives de cotes pièce dues à l'usure de la matière de l'outil.
* **Point critique** : L'agent doit toujours s'assurer que l'activation de `G41` / `G42` se fait en effectuant un mouvement rectiligne d'approche linéaire d'une longueur supérieure au rayon de la fraise pour permettre à la CNC de calculer correctement la trajectoire corrigée (évite les erreurs de type *interference path*).
