---
name: plc-instruction-list
description: "Programmer en Liste d'Instructions (IL/AWL) pour PLCs."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, windows]
metadata:
  tags: [il, awl, stl, plc, siemens, s7-300, s7-400, legacy, assembler, migration]
  related_skills: [iec61131-3-programming-standards, siemens-scl-generation]
---

# Programmation en Liste d'Instructions (IL / AWL) et Migration de Code Legacy

Cette compétence encadre la lecture, le diagnostic, la modification et la migration de programmes écrits en Liste d'Instructions (norme IEC 61131-3 IL ou langage d'assemblage AWL/STL spécifique aux gammes Siemens S7-300/400 legacy).

---

## 1. Logique Booléenne en Liste d'Instructions (IL / AWL)

La logique binaire s'exécute séquentiellement en empilant les résultats intermédiaires dans le registre d'état (RLO - Résultat Logique d'Opération).

### Instructions Binaires Standard (Équivalence IEC et Siemens)
* **A (And) / U (Und)** : ET logique.
* **AN (And Not) / UN (Und Nicht)** : ET logique avec inversion du bit d'entrée.
* **O (Or) / O (Oder)** : OU logique.
* **ON (Or Not) / ON (Oder Nicht)** : OU logique avec inversion.
* **= (Assign) / = (Zuweisung)** : Affectation du RLO à la variable cible.

### Exemple : Démarrage Moteur avec Auto-maintien
```pascal
U   "Bouton_Marche"     // Si appui sur Marche
O   "Contacteur_Moteur" // OU si le moteur est deja en auto-maintien
UN  "Bouton_Arret"      // ET pas d'appui sur Arret
UN  "Defaut_Thermique"  // ET pas de defaut thermique
=   "Contacteur_Moteur" // Activer le contacteur
```

---

## 2. Manipulation des Accumulateurs et des Registres (Siemens S7 AWL)

Le processeur de l'automate utilise deux accumulateurs principaux de 32 bits (`ACCU1` et `ACCU2`) pour exécuter les opérations de chargement, transfert, et calculs arithmétiques.

* **L (Load)** : Décale la valeur de `ACCU1` dans `ACCU2`, puis charge la donnée dans `ACCU1`.
* **T (Transfer)** : Copie le contenu de `ACCU1` vers l'adresse mémoire cible (le contenu de `ACCU1` reste inchangé).

### Exemple : Calcul mathématique de conversion d'une pression
```pascal
L   "Pression_Brute"    // Charge la valeur brute de l'automate (ex: INT de 0 a 27648) dans ACCU1
ITD                     // Convertit le INT (16 bits) en DINT (32 bits) dans ACCU1
DTR                     // Convertit le DINT en REAL (virgule flottante 32 bits)
L   2.764800e+04        // Charge la valeur de mise a l'echelle max dans ACCU1 (ACCU1 precedent glisse dans ACCU2)
/R                      // Divise ACCU2 (valeur brute) par ACCU1 (constante) -> resultat dans ACCU1
L   1.000000e+01        // Charge l'echelle physique max (ex: 10.0 bars) dans ACCU1
*R                      // Multiplie ACCU2 par ACCU1 -> resultat final dans ACCU1
T   "Pression_Bars"     // Transfert la pression convertie vers la variable REAL
```

---

## 3. Rétro-ingénierie et Migration Systématique vers le SCL / Structured Text

La majorité du travail sur les programmes AWL consiste à les traduire vers des langages modernes et maintenables comme le **SCL (Siemens Structured Control Language)** ou le Structured Text (ST).

### Traduction des Sauts et Conditions (SPB / SPBN)
En AWL, la structure conditionnelle s'effectue via des sauts conditionnels vers des étiquettes (labels) selon la valeur du RLO.
* **SPB** : Saut si RLO = 1 (Jump if true).
* **SPBN** : Saut si RLO = 0 (Jump if false).

#### Exemple de Structure Conditionnelle en AWL :
```pascal
      U   "Capteur_Niveau_Haut"
      SPB M001
      L   0.0
      T   "Consigne_Vitesse_Pompe"
      SPA M002                  // Saut inconditionnel (Else)
M001: L   50.0
      T   "Consigne_Vitesse_Pompe"
M002: NOP 0
```

#### Traduction correcte en SCL :
L'agent doit réécrire ce réseau sous la forme propre d'un bloc conditionnel `IF/THEN/ELSE` :
```pascal
IF "Capteur_Niveau_Haut" THEN
    "Consigne_Vitesse_Pompe" := 50.0;
ELSE
    "Consigne_Vitesse_Pompe" := 0.0;
END_IF;
```

---

## 4. Adressage Indirect et Pointeurs de Zone (AR1 / AR2)

Le code AWL complexe utilise l'adressage indirect pour indexer des tableaux de données via les registres d'adresse `AR1` et `AR2`.
* **LAR1** : Charge le registre d'adresse `AR1` avec un pointeur (ex: `LAR1 P#DBX 0.0`).
* **Format Pointeur** : `P# [Zone memoire] [Octet] . [Bit]` (ex: `P#DBX 10.2`).
* **Recommandation de migration** : Ne jamais traduire l'adressage indirect mot à mot en SCL. Les accès indirects par pointeur physique (ex: `L DBW [AR1, P#0.0]`) doivent être migrés en SCL en utilisant des indexations de tableaux claires (`Tableau[index]`) ou des structures de données de type UDT (User Defined Types) avec accès symbolique pour préserver l'intégrité et la lisibilité du programme.
