---
name: rockwell-studio5000
description: "Programmer en ST Rockwell et manipuler des fichiers L5X."
version: 1.3.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [rockwell, studio5000, logix-designer, plc, l5x, industrial-automation]
  related_skills: [simplify-code, plan]
---

# Programmation Rockwell Automation (Studio 5000 & L5X)

## Vue d'ensemble

L'environnement **Studio 5000 Logix Designer** d'Allen-Bradley (Rockwell Automation) est la référence pour programmer les contrôleurs ControlLogix et CompactLogix.

*Référence technique :* Voir `references/rockwell-generation-workflow.md` pour le workflow de génération automatisée depuis des FDS, `references/rgy-project-structure.md` pour un exemple concret de projet RGY multi-FDS, `references/roh-project-structure.md` pour un exemple de projet PDF-only (ROH), `references/parallel-subagent-generation.md` pour la génération parallèle multi-zone par sous-agents, et `references/l5x-consolidation-workflow.md` pour le script de post-traitement qui consolide les sorties de sous-agents en fichiers L5X valides avec CDATA.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De générer des blocs de code ou des routines en Structured Text (ST) pour Studio 5000.
- D'analyser ou de générer des structures XML L5X pour importer des Add-On Instructions (AOI), des routines, des types de données définis par l'utilisateur (UDT), ou des programmes complets.
- De structurer des variables selon les portées locales (Program Tags) et globales (Controller Tags).
- D'implémenter des régulations ou des traitements analogiques (mises à l'échelle).
- De traduire des schémas à contacts (Ladder) en Structured Text Logix.

---

## 1. Portées des Variables (Controller Tags vs Program Tags)

Dans les architectures Logix, la gestion de la mémoire est divisée en deux portées fondamentales :

### Controller Tags (Portée Globale)
- **Définition** : Variables partagées au niveau de l'ensemble du contrôleur.
- **Usage recommandé** : 
  - Échanges HMI/SCADA.
  - Communications inter-automates (Produce/Consume, instructions MSG).
  - Échanges de données globaux entre différents programmes de l'automate.
- **Accès** : Accessible directement par n'importe quelle routine de n'importe quel programme en écrivant simplement le nom du tag (ex : `HMI_Start_Button`).

### Program Tags (Portée Locale)
- **Définition** : Variables encapsulées à l'intérieur d'un programme spécifique (contenant un ou plusieurs ensembles de routines).
- **Usage recommandé** :
  - Variables de calcul temporaire, mémoires d'état internes, variables locales de routine.
  - Encapsulation logique pour s'assurer qu'un autre programme ne modifie pas accidentellement des données internes.
  - Réutilisation de structures logiques identiques dans des programmes différents.
- **Accès interne** : Accessible directement par toutes les routines du même programme.
- **Accès externe (Syntaxe de référence croisée)** : Pour accéder à un tag local depuis un autre programme ou un équipement externe, la syntaxe qualifiée est `\ProgramName.TagName` (introduite sur les versions de firmware récentes).

---

## 2. Structure Hiérarchique des Fichiers XML L5X

Les fichiers L5X sont des structures XML strictes et ordonnées représentant le projet ou des sous-composants (AOI, Routines, UDTs, Programmes). 

### Structure globale d'un fichier L5X complet :
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="33.00" TargetName="MyProject" TargetType="Controller">
  <Controller Name="MyController">
    <!-- Définition des types de données utilisateur (UDT) -->
    <DataTypes>
      <DataType Name="UDT_AnalogInput">
        <Members>
          <Member Name="RawValue" DataType="INT" Dimension="0" Radix="Decimal" Access="Read/Write"/>
          <Member Name="ScaledValue" DataType="REAL" Dimension="0" Radix="Float" Access="Read/Write"/>
          <Member Name="Fault" DataType="BOOL" Dimension="0" Radix="Decimal" Access="Read/Write"/>
        </Members>
      </DataType>
    </DataTypes>
    
    <!-- Définition des Add-On Instructions (AOI) -->
    <AddOnInstructionDefinitions>
      <AddOnInstructionDefinition Name="AOI_Scale" Revision="1.0">
        <Parameters>
          <Parameter Name="Input" Usage="Input" DataType="REAL"/>
          <Parameter Name="Scaled" Usage="Output" DataType="REAL"/>
        </Parameters>
        <LocalTags>
          <LocalTag Name="Temp_Val" DataType="REAL"/>
        </LocalTags>
        <Routines>
          <Routine Name="Logic" Type="StructuredText">
            <Content>
              <![CDATA[
              // Logique de l'AOI
              Temp_Val := Input;
              Scaled := Temp_Val * 10.0;
              ]]>
            </Content>
          </Routine>
        </Routines>
      </AddOnInstructionDefinition>
    </AddOnInstructionDefinitions>

    <!-- Définitions des Tags Globaux (Controller Tags) -->
    <Tags>
      <Tag Name="HMI_Heartbeat" TagType="Base" DataType="DINT"/>
    </Tags>

    <!-- Définition des Programmes et Routines -->
    <Programs>
      <Program Name="MainProgram">
        <Tags>
          <!-- Program Tags locaux -->
          <Tag Name="Local_Step" TagType="Base" DataType="INT"/>
        </Tags>
        <Routines>
          <Routine Name="MainRoutine" Type="StructuredText">
            <Content>
              <![CDATA[
              // Appel de logique de routine
              Local_Step := 10;
              ]]>
            </Content>
          </Routine>
        </Routines>
      </Program>
    </Programs>
  </Controller>
</RSLogix5000Content>
```

> [!IMPORTANT]
> - **Entités XML** : Les caractères spéciaux dans le code ST (`<`, `>`, `&`) provoquent des erreurs de parsing XML s'ils sont insérés bruts.
> - **Solution** : Envelopper systématiquement le code Structured Text dans des sections `<![CDATA[ ... ]]>` à l'intérieur de l'élément `<Content>`.

---

## 3. Structure des Temporisateurs (TIMER) et Mathématiques Associées

Sous Logix, les temporisations utilisent le type prédéfini `TIMER` qui possède une structure de registres interne fixe et s'exprime exclusivement en **millisecondes (ms)**.

### Propriétés de la Structure `TIMER` :
- **`.PRE`** (Preset) : DINT (32 bits), valeur de cible ou consigne de temps.
- **`.ACC`** (Accumulator) : DINT (32 bits), valeur de temps écoulé actuelle.
- **`.EN`** (Enable) : BOOL, indique si l'instruction de temporisation est activée.
- **`.TT`** (Timer Timing) : BOOL, indique que le timer est en cours d'accumulation (`.EN` actif et `.ACC` < `.PRE`).
- **`.DN`** (Done) : BOOL, passe à TRUE lorsque `.ACC` >= `.PRE`.

### Utilisation opérationnelle en ST :

```pascal
// Appel et exécution d'un Timer TON (On-Delay)
MyTimer.PRE := 5000;              // Consigne de 5.0 secondes (5000 ms)
MyTimer.TimerEnable := Run_Cmd;   // Condition d'activation
TON(MyTimer);                     // Exécution de l'instruction système

// Récupération de l'état
Timer_Done := MyTimer.DN;         // TRUE après 5 secondes d'activation continue
Timer_Active := MyTimer.TT;       // TRUE pendant l'écoulement du temps

// Calcul du temps restant (Mathématiques sur temporisateurs)
Time_Remaining := MyTimer.PRE - MyTimer.ACC; // Temps restant en ms
```

### Comportements de Réinitialisation :
- **TON (Timer On Delay)** : Se réinitialise automatiquement (`.ACC := 0`, `.DN := 0`) dès que la condition d'entrée (`.TimerEnable` / `Run_Cmd`) repasse à FALSE.
- **TOF (Timer Off Delay)** : S'active lorsque la condition d'entrée passe de TRUE à FALSE, et se réinitialise lorsque la condition repasse à TRUE.
- **RTO (Retentive Timer On)** : Conserve la valeur de `.ACC` même si `.TimerEnable` repasse à FALSE. Pour remettre à zéro un RTO, il faut exécuter explicitement l'instruction de réinitialisation `RES` :
  ```pascal
  IF Reset_Cmd THEN
      RES(MyRTO); // Remet MyRTO.ACC à 0 et MyRTO.DN à FALSE
  END_IF;
  ```

---

## 4. Conventions de Nommage et Algorithme de Mise à l'Échelle (Scaling)

### Conventions de Nommage Rockwell :
- **Longueur maximale** : 40 caractères pour tous les noms de tags, de routines, de programmes ou de types de données.
- **Caractères valides** : Lettres (`A-Z`, `a-z`), chiffres (`0-9`) et caractères de soulignement (`_`).
- **Règles d'écriture** : 
  - Doit obligatoirement commencer par une lettre.
  - Interdiction d'avoir des caractères de soulignement consécutifs (ex : `Pump__Start` est invalide).
  - Ne doit pas se terminer par un caractère de soulignement (ex : `Pump_Start_` est invalide).
  - Les espaces et caractères accentués sont strictement interdits.

### Algorithme Standardisé de Mise à l'Échelle (Scaling) en ST :
Les automates Rockwell ne disposent pas d'une instruction native simple de mise à l'échelle (comme l'instruction `SCALE` sur d'autres plateformes). On implémente souvent cet algorithme sous forme d'AOI ou de fonction Structured Text.

```pascal
// Formule mathématique linéaire :
// Output = ((Input - Raw_Min) / (Raw_Max - Raw_Min)) * (EU_Max - EU_Min) + EU_Min

// Implémentation robuste en ST Rockwell
Span_Raw := Raw_Max - Raw_Min;
Span_EU := EU_Max - EU_Min;

IF Span_Raw <> 0.0 THEN
    // Calcul de la valeur brute proportionnelle
    Scaled_Temp := ((Input_Raw - Raw_Min) / Span_Raw) * Span_EU + EU_Min;
    
    // Écrêtage (Clamping) pour éviter les valeurs hors limites physiques
    IF Scaled_Temp > EU_Max THEN
        Output_Scaled := EU_Max;
    ELSIF Scaled_Temp < EU_Min THEN
        Output_Scaled := EU_Min;
    ELSE
        Output_Scaled := Scaled_Temp;
    END_IF;
    
    Scale_Fault := FALSE;
ELSE
    // Erreur de configuration (Division par zéro évitée)
    Output_Scaled := EU_Min;
    Scale_Fault := TRUE;
END_IF;
```

---

## 5. Génération Multi-FDS depuis un Répertoire Projet

Lorsqu'un projet industriel contient plusieurs dizaines de FDS répartis par zone fonctionnelle (réception, broyage, extrusion, conditionnement, etc.), le traitement doit être systématisé.

### Convention de nommage des FDS projet

```
{PREFIX}-FDS-{ZONE}-{FEATURE}-{VERSION}.{ext}
```

Exemple concret (projet RGY — recyclage plastique) :
```
RGY-FDS-RECEPTION-UNLOAD-G.pdf     ← Zone Réception, déchargement, version G
RGY-FDS-GRINDING-DOSING-F.pdf      ← Zone Broyage, dosage, version F
RGY-FDS-EXTRUSION_L2-GENERALITIES-B.pdf  ← Zone Extrusion Ligne 2, généralités, version B
```

### Arborescence projet type

```
client_data/{PROJET}/FDS/
├── 00-GENERAL/           ← FDS transverses (supervision, calibration, chauffage, agitation)
├── 01-{ZONE_A}/          ← FDS spécifiques à la zone A
├── 02-{ZONE_B}/          ← FDS spécifiques à la zone B
│   ├── 1-LINE_1/         ← Sous-lignes si la zone est divisée
│   └── 2-LINE_2/
├── .../                  ← 8 à 12 zones max
├── RGY-FS-LIST-{DATE}.xls  ← Fichier de liste des E/S (I/O List) complémentaire
└── Master/               ← Dossiers masters contenant les originaux non révisés
```

### Workflow de génération

1. **Scanner le répertoire** : Lister tous les fichiers `.pdf` et `.docx` valides (ignorer `~$*` fichiers temporaires Office).
2. **Traiter les généralités d'abord** : Les FDS `GENERALITIES` ou `GENERAL` définissent les blocs génériques (UDT, AOI, routines standard) qui s'appliquent à toute la zone.
3. **Traiter les FDS spécifiques** : Chaque FDS produit une AOI et/ou une routine ST.
4. **Injecter le skid** : Utiliser le flag `--skid` du script `generate_rockwell_from_fds.py` pour remplacer les patterns `SKXX` par le numéro de skid réel.
5. **Cross-check avec l'I/O List** : Le fichier XLS (liste des E/S) sert à valider que tous les tags utilisés dans le code ST correspondent à des entrées/sorties physiques déclarées.

### Piège spécifique multi-FDS

- **Ne pas mélanger les versions** : Un même projet peut avoir des FDS à des révisions différentes (A, B, C...). Toujours prendre la version la plus récente (lettre la plus haute dans l'ordre alphabétique).
- **Fichiers temporaires Office** : Les fichiers `~$*.docx` sont des verrous temporaires — les ignorer systématiquement.
- **Répertoires Master** : Contiennent souvent des originaux non révisés — ne pas les traiter si les FDS officiels existent dans le dossier parent.

---

## Pièges Courants (Common Pitfalls)

1. **Unité de temps incorrecte dans les Timers :**
   * *Erreur* : Affecter directement une valeur en secondes au champ `.PRE` (ex: `MyTimer.PRE := 5;` pour 5 secondes).
   * *Correction* : Les timers Logix s'expriment uniquement en millisecondes. Toujours multiplier la valeur en secondes par 1000 (ex: `MyTimer.PRE := 5000;`).
2. **Utilisation erronée de `.Q` ou `.IN` (réflexes Siemens/Codesys) :**
   * *Erreur* : Essayer de lire la variable de sortie `.Q` ou d'assigner l'activation sur `.IN`.
   * *Correction* : Utiliser exclusivement `.DN` (Done) pour la sortie de temporisation et `.TimerEnable` ou le paramètre de l'instruction TON pour l'activation.
3. **Limites de caractères des étiquettes (Tags) :**
   * *Erreur* : Dépasser accidentellement la limite des 40 caractères lors de la génération automatique d'étiquettes à partir d'un fichier d'audit.
   * *Correction* : Implémenter une routine de troncature intelligente garantissant que tous les tags générés font maximum 40 caractères et se terminent proprement par un caractère alphanumérique.
4. **Génération L5X par sous-agents délégués (delegate_task) :**
   * *Erreur :* Déléguer la génération complète de fichiers L5X (avec code ST, CDATA, XML) à des sous-agents. Les sous-agents produisent des L5X avec des `<Content>` vides, sans CDATA, ou avec des structures XML incohérentes entre zones.
   * *Cause :* Le script `generate_rockwell_from_fds.py` utilise `async_call_llm` depuis l'infrastructure EVA — les sous-agents n'y ont pas accès et reconstruisent leur propre logique de génération XML de façon non standardisée.
   * *Correction :*
     a) Déléguer uniquement la lecture des FDS et la génération des fichiers `.st` (Structured Text) aux sous-agents.
     b) Centraliser la génération des L5X (AOI + Routine) dans un script de post-traitement unique qui :
        - Parcourt tous les `.st` générés
        - Embarque le code ST dans des blocs CDATA
        - Produit des fichiers L5X avec une structure XML cohérente
        - Valide qu'aucun `<Content>` n'est vide
     c) Voir `rockwell-l5x-generation` section 4 pour le détail du workflow de consolidation.

5. **Calculs arithmétiques sur types mixtes :**
   * *Erreur* : Tenter d'effectuer une division ou une multiplication directe entre un `INT` (brut de carte d'I/O) et un `REAL` (coefficient d'échelle).
   * *Correction* : Utiliser des fonctions de conversion de type explicites pour garantir des types homogènes avant calcul (ex : `REAL_Val := ANY_TO_REAL(INT_Val);`).

---

## Liste de Vérification (Checklist)

- [ ] Les noms de tags générés contiennent uniquement des caractères alphanumériques et des underscores, ne dépassent pas 40 caractères et ne finissent pas par un underscore.
- [ ] Tout code inséré dans une routine ou une AOI d'un fichier L5X est enveloppé dans un bloc `<![CDATA[ ... ]]>`.
- [ ] Les temporisateurs utilisent bien `.PRE` en millisecondes et exploitent le bit `.DN` comme indicateur de fin de temporisation.
- [ ] L'algorithme de mise à l'échelle intègre une protection contre la division par zéro (vérification que `Raw_Max <> Raw_Min`) et un écrêtage (clamping) de la sortie.
- [ ] Les portées de variables (Controller Tags pour les HMI/Global, Program Tags pour la logique interne) sont respectées lors des déclarations.
- [ ] Après génération parallèle par sous-agents : exécuter le script de consolidation (voir `references/l5x-consolidation-workflow.md`) et valider que 100% des L5X contiennent du CDATA et qu'aucun `<Content>` n'est vide.
- [ ] Les noms de fichiers .st et .L5X utilisent des underscores (`_`) et non des tirets (`-`) pour rester compatibles avec les conventions de nommage Rockwell.

