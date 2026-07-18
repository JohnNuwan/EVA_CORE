---
name: rockwell-l5x-generation
description: "Générer et éditer des fichiers L5X Studio 5000."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [rockwell, studio-5000, l5x, plc, xml, automation-engineering]
  related_skills: [industrial-plc-connectivity, rockwell-l5x-courbon-conventions]
---

# Génération et Ingestion de Fichiers L5X Rockwell (Studio 5000)

## Vue d'ensemble

Cette compétence guide l'agent pour créer, modifier, parser et valider des fichiers de configuration et de code au format `.L5X` (Rockwell Automation Studio 5000 Logix Designer). Ce format XML décrit l'intégralité du projet PLC ou des éléments spécifiques (UDT, AOI, Programmes, Routines).

---

## Outils Associés

Les outils natifs suivants doivent être utilisés pour manipuler les fichiers :
- `` `l5x_editor_analyze` `` : Extraire la structure (UDTs, AOIs, programmes, variables).
- `` `l5x_editor_validate` `` : Vérifier la syntaxe XML et détecter les tags orphelins.
- `` `l5x_editor_rename_tags` `` : Renommer en bloc les préfixes de variables (scope-aware).

---

## Guide d'Ingénierie & Structures XML Détaillées

### 1. Structure d'un type de données utilisateur (UDT)
Les UDT (User-Defined Types) définissent des structures de données réutilisables pour les équipements (moteurs, vannes, instruments). Lors de la génération d'un UDT dans le L5X, l'agent doit formater le XML comme suit :

```xml
<UserDefinedTypes>
  <UserDefinedType Name="UDT_Motor" Family="" Class="User">
    <Description>Structure de contrôle standard pour moteur asynchrone</Description>
    <Members>
      <Member Name="CmdStart" DataType="BOOL" Dimension="0" Radix="Decimal" Hidden="false">
        <Description>Commande de démarrage (Impulsion)</Description>
      </Member>
      <Member Name="CmdStop" DataType="BOOL" Dimension="0" Radix="Decimal" Hidden="false">
        <Description>Commande d'arrêt (Impulsion)</Description>
      </Member>
      <Member Name="StsRunning" DataType="BOOL" Dimension="0" Radix="Decimal" Hidden="false">
        <Description>Retour de marche moteur</Description>
      </Member>
      <Member Name="StsFault" DataType="BOOL" Dimension="0" Radix="Decimal" Hidden="false">
        <Description>Retour de défaut moteur (Thermique ou Disjoncteur)</Description>
      </Member>
      <Member Name="SpeedCons" DataType="REAL" Dimension="0" Radix="Float" Hidden="false">
        <Description>Consigne de vitesse en Hz (0.0 à 50.0)</Description>
      </Member>
      <Member Name="SpeedFeedback" DataType="REAL" Dimension="0" Radix="Float" Hidden="false">
        <Description>Retour de vitesse mesuré en Hz</Description>
      </Member>
    </Members>
  </UserDefinedType>
</UserDefinedTypes>
```

### 2. Structure d'une Add-On Instruction (AOI)
L'AOI (Add-On Instruction) est un bloc logique encapsulé. Elle s'appuie sur des paramètres d'entrée/sortie et des variables locales.

```xml
<AddOnInstructionDefinitions>
  <AddOnInstructionDefinition Name="AOI_MotorControl" Revision="1.0" ExecuteMode="Block" Class="Standard">
    <Description>Logique de commande et sécurité pour moteur asynchrone</Description>
    <Parameters>
      <Parameter Name="EnableIn" DataType="BOOL" Usage="Input" Required="true" Visible="true"/>
      <Parameter Name="EnableOut" DataType="BOOL" Usage="Output" Required="false" Visible="true"/>
      <Parameter Name="Ctrl" DataType="UDT_Motor" Usage="InOut" Required="true" Visible="true">
        <Description>Structure UDT de l'équipement</Description>
      </Parameter>
      <Parameter Name="ResetFault" DataType="BOOL" Usage="Input" Required="false" Visible="true">
        <Description>Commande de réarmement du défaut</Description>
      </Parameter>
    </Parameters>
    <LocalTags>
      <LocalTag Name="TmrStartTimeout" DataType="TIMER" Radix="Null">
        <Description>Timer de contrôle de retour de marche</Description>
      </LocalTag>
    </LocalTags>
    <Routines>
      <Routine Name="Logic" Type="ST">
        <Description>Logique de commande en Structured Text</Description>
        <StructureText>
          <Line Number="0"><![CDATA[// Gestion du défaut thermique / disjoncteur]]></Line>
          <Line Number="1"><![CDATA[IF Ctrl.StsFault AND ResetFault THEN]]></Line>
          <Line Number="2"><![CDATA[    Ctrl.StsFault := FALSE;]]></Line>
          <Line Number="3"><![CDATA[END_IF;]]></Line>
          <Line Number="4"><![CDATA[]]></Line>
          <Line Number="5"><![CDATA[// Contrôle de marche / arrêt]]></Line>
          <Line Number="6"><![CDATA[IF Ctrl.CmdStart AND NOT Ctrl.CmdStop AND NOT Ctrl.StsFault THEN]]></Line>
          <Line Number="7"><![CDATA[    Ctrl.StsRunning := TRUE;]]></Line>
          <Line Number="8"><![CDATA[ELIF Ctrl.CmdStop OR Ctrl.StsFault THEN]]></Line>
          <Line Number="9"><![CDATA[    Ctrl.StsRunning := FALSE;]]></Line>
          <Line Number="10"><![CDATA[END_IF;]]></Line>
        </StructureText>
      </Routine>
    </Routines>
  </AddOnInstructionDefinition>
</AddOnInstructionDefinitions>
```

---

## 3. Validation des Fichiers L5X Générés

Avant de livrer un fichier L5X à l'import dans Studio 5000, vérifier systématiquement :

### 3.1 Vérification CDATA
Tout code Structured Text dans `<Content>` ou `<STText>` doit être enveloppé dans `<![CDATA[...]]>`. Un fichier L5X sans CDATA provoque des erreurs de parsing XML à l'import.

```bash
# Vérifier que tous les L5X contiennent du CDATA
grep -l 'CDATA' *.L5X | wc -l          # Nb de fichiers avec CDATA
grep -L 'CDATA' *.L5X                   # Lister ceux qui en manquent
```

### 3.2 Vérification de contenu
Un fichier L5X valide ne doit pas avoir de balises `<Content>` vides :

```bash
# Vérifier qu'aucun fichier n'a de Content vide
grep -c '<Content/>\|<Content></Content>' *.L5X
```

### 3.3 Vérification structurelle
Un fichier L5X complet contient :
- `<?xml version="1.0" encoding="UTF-8"?>`
- `<RSLogix5000Content ...>`
- Au moins une routine ou une AOI avec du code ST
- Des balises fermées correctement

### 3.4 Vérification de cohérence nommage
- Les noms de tags/routines/AOI ≤ 40 caractères
- Pas de tirets `-` dans les noms (les remplacer par `_`)
- Les noms des fichiers .st correspondent à ceux des .L5X associés

---

## 4. Génération Par Projet Multi-FDS (Workflow Validé)

### 4.1 Approche : Sous-agents → L5X complets (pas .st uniquement)

L'approche la plus robuste, validée sur le projet ROH DevAssist (29 FDS, 6 zones), est de **déléguer chaque zone à un sous-agent qui génère un fichier L5X complet** (pas un .st partiel). Le parent fournit :

- Les UDTs de base (fichier L5X UDT template)
- Les AOIs communes (template L5X AOI)
- La structure de tags et les conventions de nommage
- Un fichier de zone existant comme exemple de format (passé via `context`)

```
Workflow validé :

1. CRÉER les UDTs et AOIs communs → 2 fichiers L5X de base
2. DÉLÉGUER chaque zone en parallèle (delegate_task toolsets=[file,terminal]) :
   - title clair : "ROH_Zone_{NAME} — complete Rockwell L5X"
   - context : CPU type, conventions, UDTs disponibles, exemple de tags
   - goal : générer un L5X complet avec Routine ST dans CDATA
3. VALIDER (parent) : compter CDATA, vérifier Content non vide, lister lignes
4. ASSEMBLER : créer le Master_Project.L5X qui référence tous les fichiers
```

### 4.2 Problèmes connus et corrections (empiriques)

| Problème | Cause | Correction |
|----------|-------|------------|
| `<Content></Content>` vide | Sous-agent génère le XML mais oublie le code ST | Chaque sous-agent DOIT écrire le L5X en un seul fichier complet. Vérifier avec `grep -c CDATA` |
| Pas de balises `<![CDATA[...]]>` | Le code ST écrit brut dans le XML casse les caractères `<`, `>`, `&` | Passer un exemple de L5X existant dans `context` comme format référence |
| Tags/Programs manquants | Sous-agent ne définit que la Routine, pas les Tags | Structure minimale : Tags (UDT instances + I/O aliases) + Program + Routine |
| Noms de fichiers avec tirets | Incompatible Rockwell (max 40 chars, underscores only) | Remplacer `-` par `_` dans les noms de tags et fichiers |
| Machine d'état absente ou incomplète | Sous-agent écrit juste une logique séquentielle | Forcer un pattern de state machine (Idle → Starting → Running → Complete) |

### 4.3 Contenu minimum d'un L5X de zone (template de référence)

Un L5X de zone généré par sous-agent contient toujours :

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="33.00" 
  TargetName="ROH_Zone_{NAME}" TargetType="Program">
  <Controller UseAsFolder="true">
    <Programs>
      <Program Name="Zone_{NAME}">
        <Tags>...</Tags>
        <Routines>
          <Routine Name="Main" Type="StructuredText">
            <Content><![CDATA[
// 1. I/O Mapping - physical to UDT fields
// 2. Equipment Control - AOI calls for each device
// 3. Permissives & Interlocks
// 4. Equipment Phase State Machine (Idle→Running→Complete→Aborted)
// 5. UDT sync for AOI compatibility
            ]]></Content>
          </Routine>
        </Routines>
      </Program>
    </Programs>
  </Controller>
</RSLogix5000Content>
```

La section Structured Text doit toujours contenoir 5 sections dans l'ordre :
1. **I/O Mapping** — Mapping des entrées/sorties physiques (DI, DO, AI, AO) vers les champs UDT
2. **Equipment Control** — Appels aux AOIs (AOI_MotorControl, AOI_ValveControl, etc.)
3. **Permissives & Interlocks** — Conditions de zone (portes, E-Stop, safe temp, etc.)
4. **Phase State Machine** — Machine d'état à 5+ états séquentiels
5. **UDT Sync** — Synchronisation des tags zone vers UDT composite pour compatibilité AOI

### 4.4 Validation post-génération

```bash
# Vérification CDATA : doit être 100%
cd output/ROH_DevAssite/l5x/
for f in *.L5X; do
  lines=$(wc -l < "$f")
  cdata=$(grep -c 'CDATA' "$f")
  echo "$f: ${cdata} CDATA, ${lines} lines"
done

# Vérification contenu vide : doit être 0
grep -r '<Content/>' . --include="*.L5X" | wc -l
```

### 4.5 Exemple concret : Projet ROH DevAssist (29 FDS, 6 zones)

Voir le fichier `references/roh-devassist-worked-example.md` pour le détail complet du projet Royal Canin extrusion line, incluant :
- Structure des UDTs industriels (8 définitions)
- AOIs équipement (Motor, Valve, Coater, Dryer)
- Architecture des 6 zones avec machines d'état
- Tags naming convention (préfixes EX_, CO_, DR_, ASPI_, etc.)

---

## Règles de Conception Logix/Studio 5000

1. **Structured Text (ST) Rockwell** :
   * Les fins de lignes logiques doivent obligatoirement se terminer par un point-virgule `;`.
   * L'accès aux membres de structures s'effectue avec le point `.` (ex: `Ctrl.CmdStart`).
   * Les commentaires s'écrivent avec une double barre oblique `//` pour une ligne, ou `/* ... */` pour des blocs de commentaires.
2. **Conventions de nommage standards** :
   * **Tags globaux/locaux** : PascalCase (ex: `MainConveyor`).
   * **Variables de commande / états** : Préfixes standards (`Cmd` pour les commandes, `Sts` pour les status, `Cfg` pour les configurations, `Alm` pour les alarmes).
   * **Types de données (UDT/AOI)** : Majuscule avec préfixe explicite (ex: `UDT_AnalogInput`, `AOI_PID_Loop`).
3. **Optimisation XML L5X** :
   * Toujours inclure la section `<![CDATA[...]]>` pour envelopper le code Structured Text.
   * Veiller à ce que l'attribut `DataType` pointe vers des types standards Logix (`BOOL`, `SINT`, `INT`, `DINT`, `REAL`, `TIMER`, `COUNTER`) ou des UDT existants.

---

## 5. Conventions Réelles Courbon/Actemium (Projets Industriels)

⚠️ **SECTION CRITIQUE** — Les sections 1-4 ci-dessus donnent une base générique, mais les projets réels de Courbon/Actemium Saint-Étienne utilisent une architecture **structurellement différente**. 

**Avant de générer du code pour un projet Courbon, charger impérativement la skill `rockwell-l5x-courbon-conventions` et analyser les fichiers de référence ingénieurs.**

### 5.1 Architecture Equipment Module (EM) — 5 UDTs par équipement

Chaque équipement est représenté par **5 UDTs** :

```
UDT_EM_{ZONE}_{EQ}                        ← Conteneur: {COMMAND, STATUS}
  UDT_EM_{ZONE}_{EQ}_CMD                  ← {ID_EM, CMD, ID_FCT_RESERV, SETPOINT}
    UDT_EM_{ZONE}_{EQ}_SETPOINT           ← SP01..SP24 (REAL)
  UDT_EM_{ZONE}_{EQ}_STA                  ← {ID_EM, STS, ID_FCT_RESERV, MEASURE}
    UDT_EM_{ZONE}_{EQ}_STA_BOOL           ← 18 bits (RUNNING,COMPLETE,FAILURE...)
  UDT_EM_{ZONE}_{EQ}_REPORT               ← Mesures (REAL)
```

**CMD values** : 0=Idle, 1=Start, 10=Stop, 20=Abort, 30=Reset
**STS values** : 0=Idle, 1=Running, 2=Complete, 3=Aborted, 10=Fault

### 5.2 Structure FCT (Fonction) — Interface Standard

Chaque FCT est un programme avec ces tags obligatoires :
```
IO_FCT:UDT_GEN_FCT | IO_BATCH_MGT_FROM_FCT | IO_BATCH_MGT_TO_FCT
PLC_TASK_EXC:UDT_GEN_PLC_TASK | PLC_CONFIG:UDT_GEN_PLC_CONFIG
L_CURRENT_STEP:DINT | PARAM_{ZONE}:UDT_PARAM_{ZONE}
L_EM_{ZONE}_{EQ}:UDT_EM_{ZONE}_{EQ}  (une par équipement)
```

**UDT_GEN_FCT** = {ID_FCT, CMD: GEN_FCT_CMD_BOOL{START,STOP,ABORT,RESET,HOLD,RESTART}, STA: GEN_FCT_STA_BOOL{RUNNING,COMPLETE,FAILURE,ABORTED,IDLE,...}, WRK, CFG}

### 5.3 Routines : SFC + ST + RLL

Chaque FCT a **5 routines** : Main(SFC) → Running(SFC) → Logic(ST) → EnableInFalse(RLL) → Prescan(RLL)

### 5.4 Tag Prefixes (obligatoire)

| Préfixe | Rôle | Exemple |
|---------|------|---------|
| `IO_FCT` | Interface générique | `IO_FCT : UDT_GEN_FCT` |
| `IO_RECIPE` | Recette | `IO_RECIPE : UDT_RECIPE_EXTRU` |
| `IO_BATCH_MGT_*` | Batch MES | `IO_BATCH_MGT_FROM_FCT` |
| `PLC_TASK_EXC` | Échange tâche | `PLC_TASK_EXC : UDT_GEN_PLC_TASK` |
| `L_EM_*` | EM local | `L_EM_EXTRU_MAG : UDT_EM_EXTRU_MAG` |
| `L_CURRENT_STEP` | Step DINT | `L_CURRENT_STEP : DINT` |
| `I_SYN_*` | Entrée IHM | `I_SYN_AUTHOR_START : BOOL` |
| `PARAM_*` | Paramètres | `PARAM_EXTRU : UDT_PARAM_EXTRU` |
| `EXC_*` | Échange système | `EXC_C_TO_G : Comm_From_Courbon_To_Geelen` |

### 5.5 NE PAS utiliser l'approche UDT plat (CmdStart/StsRunning)

Les ingénieurs Courbon n'utilisent **JAMAIS** de UDTs comme `UDT_Motor` avec des champs plats `CmdStart`, `StsRunning`. Ils utilisent exclusivement le pattern **EM 5-UDT** (COMMAND/STATUS avec ID_EM, CMD, STS binaire).

PITFALL : Ne pas générer de code avec `UDT_Motor`, `UDT_Valve`, `UDT_Sensor` génériques. Toujours créer `UDT_EM_{ZONE}_{EQ}` avec le pattern CMD/STA même si l'équipement est "juste un moteur".

Voir `references/engineer-convention-details.md` pour la liste complète des UDTs réels, la nomenclature des 46 FCT, et les structures RECIPE/PARAM extraites des fichiers ingénieurs.

### 5.6 Workflow Reverse-Engineering depuis Fichiers Ingénieurs

Quand des L5X ingénieurs existent (ex: ~45 FCT), ne PAS générer avant d'avoir extrait leurs conventions :

1. **Parser** les XML : `findall('.//DataType')` pour les UDTs, `findall('.//Tag')` pour les tags, `findall('.//Routine')` pour les routines
2. **Analyser** : pattern 5-UDT par EM, conventions IO_FCT/L_EM_/PARAM_, routines SFC+ST+RLL obligatoires
3. **Compter** : le nb de FCT doit correspondre au nb de FDS
4. **PITFALL** : les ingénieurs Courbon utilisent exclusivement le pattern COMMAND/STATUS binaires (ID_EM/CMD/STS/SETPOINT). Jamais de UDTs plats CmdStart/StsRunning. Toute génération hors pattern sera rejetée.
