---
name: schneider-unity
description: "Programmer sous Control Expert et manipuler les fichiers XMY."
version: 1.2.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [schneider, unity-pro, control-expert, plc, st, m340, m580, industrial-automation, ddt, dfb, xmy]
    related_skills: [simplify-code, plan]
---

# Programmation Schneider Electric (Unity Pro / Control Expert)

## Vue d'ensemble

**EcoStruxure Control Expert** (anciennement connu sous le nom de **Unity Pro**) est l'environnement de développement et de programmation pour les contrôleurs logiques programmables (API/PLC) de la gamme Schneider Electric, notamment les Modicon M340, M580, Premium et Quantum. 

Le langage **Texte Structuré (ST)** y est privilégié pour l'implémentation de calculs complexes, de boucles et de blocs logiques algorithmiques. Control Expert utilise également un format d'exportation/importation standardisé basé sur le XML (fichiers `.XMY`) pour stocker et transférer les structures de données (DDT), les sections de code et les Blocs Fonctionnels Dérivés (DFB) créés par l'utilisateur.

Cette compétence permet à l'agent EVA de générer du code ST valide pour Schneider Control Expert et de lire, analyser ou générer des fichiers XML d'importation `.XMY` conformes aux spécifications de l'éditeur.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Générer des sections de code logique ou des blocs de fonctions personnalisés (DFB) en Structured Text (ST) pour Control Expert.
- Créer ou structurer des Types de Données Dérivés (DDT - équivalents de structures) sous forme de déclarations de type ou de balises XML.
- Manipuler, exporter ou concevoir des structures XML de type `.XMY` (fichiers de DFB) ou `.FEF` (fichiers d'export globaux).
- Traduire de la logique d'automatisme (Ladder, SFC/Grafcet) vers le ST de Schneider.
- Analyser et cartographier les variables d'échange (localisées sur `%MW` ou non localisées).

---

## Règles de Syntaxe Structured Text (ST) Schneider

Le langage ST de Schneider Electric implémente la norme CEI 61131-3 avec les spécificités de compilation suivantes :

### 1. Variables et affectation
- L'opérateur d'affectation est impérativement `:=`.
- Les variables locales, contrairement à TIA Portal (Siemens), ne portent **aucun préfixe** tel que `#`. Les noms de variables s'écrivent directement.
- Les commentaires s'écrivent avec `(* commentaire *)` pour les blocs multi-lignes et `//` pour les lignes simples (supporté sur les versions récentes).

### 2. Nommage standardisé EVA
Pour différencier la portée des variables et maintenir un code propre :

| Type de Variable | Préfixe | Exemple | Description |
| :--- | :--- | :--- | :--- |
| **Input** (Entrée DFB) | `i_` | `i_Cmd_Start` | Signal physique ou commande logique entrant. |
| **Output** (Sortie DFB) | `q_` | `q_Motor_On` | Signal physique ou commande logique sortant. |
| **InOut** (Entrée/Sortie) | `iq_` | `iq_Settings` | Référence passée en lecture/écriture. |
| **Static** (Mémoire interne) | `stat_` | `stat_Feedback_Timer` | Instance de bloc temporisateur ou mémoire. |
| **Temp** (Temporaire) | `temp_` | `temp_Index` | Variable de calcul locale non persistante. |

### 3. Exemple d'implémentation DFB : Commande de Moteur avec Surveillance de Retour de Marche (`DFB_Motor_Advanced`)

Voici le code ST de logique interne pour un DFB de contrôle de moteur :

```pascal
(* ==========================================================================
   LOGIQUE DE COMMANDE ET DIAGNOSTIC MOTEUR ADVANCED
   ========================================================================== *)

(* 1. Gestion des modes Auto / Manuel *)
IF i_Cmd_Mode_Auto THEN
    stat_Mode_Auto := TRUE;
ELSIF i_Cmd_Mode_Man THEN
    stat_Mode_Auto := FALSE;
END_IF;

(* 2. Logique de commande de démarrage *)
IF stat_Mode_Auto THEN
    stat_Run_Request := i_Cmd_Auto_Start AND NOT i_Cmd_Auto_Stop;
ELSE
    stat_Run_Request := (stat_Run_Request OR i_Cmd_Man_Start) AND NOT i_Cmd_Man_Stop;
END_IF;

(* 3. Application des sécurités (Interlock prioritaires) *)
IF NOT i_Safety_Interlock OR i_Fault_Reset_Cmd THEN
    stat_Run_Request := FALSE;
END_IF;

(* 4. Gestion de la temporisation de retour de marche (TON standard) *)
(* Note: L'instance 'stat_Timer_Feedback' (type TON) doit être déclarée dans le dictionnaire DFB *)
stat_Timer_Feedback(IN := q_Motor_Run AND NOT i_Feedback_Run, PT := t#3s);

(* 5. Logique de défaut *)
IF stat_Timer_Feedback.Q THEN
    stat_Fault_Active := TRUE;
ELSIF i_Fault_Reset_Cmd THEN
    stat_Fault_Active := FALSE;
END_IF;

(* 6. Affectation des sorties du DFB *)
q_Motor_Run := stat_Run_Request AND NOT stat_Fault_Active;
q_Fault_Active := stat_Fault_Active;
q_Mode_Auto_Active := stat_Mode_Auto;
```

---

## Architecture de Mémoire M340 / M580 (%MW vs Variables Non-Localisées)

Les automates Schneider Modicon gèrent la mémoire selon deux concepts :

### 1. Variables Localisées (%MW - Mots de mémoire interne)
- Représentées par une adresse physique en mémoire (ex: `%MW100` pour un mot de 16 bits, `%MX100.0` pour un bit localisé).
- **Règles d'utilisation :**
  - **Obligatoires** pour les tables d'échange avec des HMI/SCADA utilisant des protocoles traditionnels (Modbus RTU, Modbus TCP non symbolique).
  - L'adressage doit être structuré de manière ordonnée pour éviter le chevauchement de mémoire (ex: un type `REAL` occupe 2 mots consécutifs, `%MW100` et `%MW101`).

### 2. Variables Non-Localisées (Variables Symboliques)
- Pas d'adresse physique fixée manuellement. L'allocateur mémoire du compilateur gère dynamiquement l'emplacement.
- **Règles d'utilisation :**
  - **Recommandées** pour toute la logique interne des programmes et la structure interne des DFB.
  - Permettent une modularité totale et évitent les conflits d'adresses en cas de modification de l'application.
  - Rendent la programmation indépendante du matériel physique de la CPU (facilite la migration M340 vers M580).

---

## Structure de Données Dérivées (DDT)

Les DDT permettent de regrouper des variables de types hétérogènes pour structurer l'information (ex: état d'une vanne, mesures d'une sonde).

### Déclaration d'une structure de type DDT :
```pascal
TYPE T_Valve_Control :
STRUCT
    bOpen_Cmd    : BOOL;  (* Commande d'ouverture *)
    bClose_Cmd   : BOOL;  (* Commande de fermeture *)
    bLimit_Open  : BOOL;  (* Fin de course ouverte *)
    bLimit_Close : BOOL;  (* Fin de course fermée *)
    rPosition    : REAL;  (* Position de recopie 0-100% *)
    bFault       : BOOL;  (* Défaut de positionnement *)
END_STRUCT
END_TYPE
```

---

## Structure XML des Fichiers d'Export XMY

Pour importer un DFB ou des variables dans Control Expert sans saisie manuelle, on utilise le format XML d'import/export Schneider (`.XMY`).

### Spécification du format XML pour un DFB (`.XMY`) :

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<FBExchangeFile>
  <!-- En-tête officiel Control Expert -->
  <fileHeader company="Schneider Automation" product="Unity Pro" version="14.1"/>
  <contentHeader name="DFB_Valve_Control" version="1.0.0">
    <comment>Contrôle de vanne standardisé EVA</comment>
  </contentHeader>
  
  <FBBlock nameType="DFB_Valve_Control" FBKind="UserAssociated">
    <!-- Paramètres d'Entrée (i_...) -->
    <parameters name="i_Cmd_Open" connectionType="Read" typeName="BOOL">
      <comment>Commande ouverture vanne</comment>
    </parameters>
    <parameters name="i_Cmd_Close" connectionType="Read" typeName="BOOL">
      <comment>Commande fermeture vanne</comment>
    </parameters>
    <parameters name="i_FBC_Open" connectionType="Read" typeName="BOOL">
      <comment>Retour fin de course ouverte</comment>
    </parameters>
    <parameters name="i_FBC_Close" connectionType="Read" typeName="BOOL">
      <comment>Retour fin de course fermée</comment>
    </parameters>
    
    <!-- Paramètres de Sortie (q_...) -->
    <parameters name="q_Valve_Open" connectionType="Write" typeName="BOOL">
      <comment>Commande de bobine ouverture physique</comment>
    </parameters>
    <parameters name="q_Fault" connectionType="Write" typeName="BOOL">
      <comment>Indication de défaut de la vanne</comment>
    </parameters>
    
    <!-- Variables Statiques Internes (stat_...) -->
    <privateVariables name="stat_Timer_Check" typeName="TON">
      <comment>Timer de contrôle de mouvement</comment>
    </privateVariables>
    <privateVariables name="stat_Fault_State" typeName="BOOL">
      <comment>Mémoire interne de l'état de défaut</comment>
    </privateVariables>
    
    <!-- Code source en Texte Structuré (ST) enveloppé dans CDATA -->
    <STSource name="Logic">
      <![CDATA[
      (* Logique du temporisateur de mouvement *)
      stat_Timer_Check(IN := (q_Valve_Open AND NOT i_FBC_Open) OR (NOT q_Valve_Open AND NOT i_FBC_Close), PT := t#5s);
      
      (* Détection du défaut *)
      IF stat_Timer_Check.Q THEN
          stat_Fault_State := TRUE;
      END_IF;
      
      (* Commande d'ouverture *)
      IF i_Cmd_Open AND NOT i_Cmd_Close AND NOT stat_Fault_State THEN
          q_Valve_Open := TRUE;
      ELSIF i_Cmd_Close OR stat_Fault_State THEN
          q_Valve_Open := FALSE;
      END_IF;
      
      q_Fault := stat_Fault_State;
      ]]>
    </STSource>
  </FBBlock>
</FBExchangeFile>
```

---

## Pièges Courants (Common Pitfalls)

1. **Variables non déclarées dans le dictionnaire :**
   * *Erreur :* Écrire du code ST en utilisant une variable sans l'avoir préalablement déclarée dans la table globale de Control Expert ou dans l'interface locale du DFB. Control Expert refuse de compiler le code.
   * *Correction :* S'assurer que le script de génération produit également le fichier XML de variables (`.XMY` de type variables) pour l'importer avant de charger le code ST.

2. **Index de tableaux dynamiques non bornés :**
   * *Erreur :* Parcourir un tableau `ARRAY [0..9] OF INT` à l'aide d'une variable d'index non sécurisée. Un dépassement d'indice provoque l'arrêt immédiat (CPU Halt) de l'automate.
   * *Correction :* Mettre en place des conditions de verrouillage strictes sur l'index de boucle avant d'accéder aux données du tableau.

3. **Chevauchement d'adresses %MW :**
   * *Erreur :* Déclarer une variable de type `DINT` (32 bits) sur `%MW10` et une variable `INT` (16 bits) sur `%MW11`. La modification de `%MW10` altérera la valeur de `%MW11` de manière silencieuse.
   * *Correction :* Utiliser des variables non-localisées pour la logique interne, et réserver l'adressage `%MW` pour l'échange de données HMI avec des écarts d'adresse stricts (+2 pour les variables de 32 bits et floats).

---

## Liste de vérification (Checklist)

- [ ] La description frontmatter YAML fait moins de 60 caractères et se termine par un point.
- [ ] Tous les blocs d'instruction (`IF`, `FOR`, `CASE`) sont fermés avec leur mot-clé de clôture (`END_IF;`, `END_FOR;`, `END_CASE;`).
- [ ] Le code ST ne contient pas de caractères `#` devant les variables locales (spécificité Siemens).
- [ ] Les commentaires respectent la syntaxe officielle `(* ... *)` ou `//`.
- [ ] Les instances de Blocs Fonctionnels standards (ex: `TON`, `TOF`, `R_TRIG`) sont déclarées dans la section `<privateVariables>` ou déclarées globalement.
- [ ] Les sections XML d'importation `.XMY` contiennent des balises racines `<FBExchangeFile>` ou `<variablesExchangeFile>` valides avec des namespaces conformes.
- [ ] Les types de base CEI 61131-3 dans le XML sont écrits en majuscules (ex: `BOOL`, `INT`, `REAL`).
- [ ] Le codage de caractères du fichier d'export XML est explicitement défini en UTF-8 (`<?xml version="1.0" encoding="UTF-8"...`).

