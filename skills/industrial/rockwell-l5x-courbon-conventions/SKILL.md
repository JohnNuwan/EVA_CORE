---
name: rockwell-l5x-courbon-conventions
description: "Conventions Courbon/EVA pour projets Rockwell L5X."
version: 1.0.0
author: EVA
license: Privée EVA
metadata:
  EVA:
    tags: [rockwell, studio-5000, l5x, courbon, EVA, plc]
    related_skills: [rockwell-l5x-generation]
---

# Conventions Rockwell Courbon/EVA

## Architecture Projet

```
Projet 1756-L83E v33
├── UDT_GEN_*              ← UDTs génériques système
├── UDT_EM_*               ← UDTs Equipment Module (pattern 5 UDTs par EM)
├── UDT_RECIPE_*           ← UDTs de recette
├── UDT_PARAM_*            ← UDTs de paramétrage
├── UDT_BATCH_MGT_*        ← UDTs batch management MES
└── 46+ FCT_XX             ← Programmes indépendants
```

## Workflow recommandé (tiré des corrections)

### Étape 0 : Toujours demander les fichiers de référence AVANT de coder

PITFALL CRITIQUE : Ne JAMAIS générer du code Rockwell pour un projet Courbon/EVA sans avoir d'abord analysé les fichiers L5X existants fournis par les ingénieurs. La première version générée sans référence sera structurellement incorrecte et devra être réécrite.

**Process validé :**
1. DEMANDER : \"Avez-vous des fichiers L5X de référence de projets similaires ?\"
2. ANALYSER : parser les XML pour extraire les UDTs, tags, conventions de nommage
3. CATALOGUER : lister tous les UDT_EM_XXX avec leur pattern CMD/STA
4. GÉNÉRER : produire les FCT en suivant EXACTEMENT les conventions extraites
5. ARCHIVER : sauvegarder la version originale avant toute correction
6. VALIDER : comparer le nombre de FCT générés au nombre de FDS

## Fichiers de référence (support files)

Cette skill contient des fichiers de référence sous `references/` :
- `references/em_catalog.md` — Catalogue complet de tous les UDT_EM_XXX (150+ UDTs) des projets ROH et RGY
- `references/conversion_guide.md` — Guide pour convertir un projet zone-based/AOI-based vers les conventions FCT
- `templates/fct_template.l5x` — Template L5X complet pour un FCT standard

## Règles de génération de code

### 1. Tag Naming Conventions
```
IO_FCT          : UDT_GEN_FCT              # Interface fonction (OBLIGATOIRE)
IO_RECIPE       : UDT_RECIPE_XXX           # Recette
IO_BATCH_MGT_FROM_FCT : UDT_BATCH_MGT_FROM_FCT  # Batch vers MES
IO_BATCH_MGT_TO_FCT   : UDT_BATCH_MGT_TO_FCT    # Batch depuis MES
PLC_TASK_EXC    : UDT_GEN_PLC_TASK         # Task exchange
PLC_CONFIG      : UDT_GEN_PLC_CONFIG       # PLC configuration
L_EM_XXX        : UDT_EM_XXX               # Equipment Module instance
L_CURRENT_STEP  : DINT                      # Compteur d'étape
PARAM_XXX       : UDT_PARAM_XXX            # Paramètres fonction
I_SYN_XXX       : BOOL                      # Synoptique entrée
```

### 2. Equipment Module UDT Pattern (5 UDTs par EM)
```
UDT_EM_XXX: container {COMMAND, STATUS}
  COMMAND: UDT_EM_XXX_CMD
    ID_EM: DINT
    CMD: DINT           # 0=Idle, 1=Start, 10=Stop, 20=Abort, 30=Reset
    ID_FCT_RESERV: DINT
    SETPOINT: UDT_EM_XXX_SETPOINT (SP01..SP24: REAL)
  STATUS: UDT_EM_XXX_STA
    ID_EM: DINT
    STS: DINT           # 0=Idle, 1=Running, 2=Complete, 3=Aborted, 10=Fault
    ID_FCT_RESERV: DINT
    MEASURE: UDT_EM_XXX_STA_BOOL (18 booléens)
UDT_EM_XXX_REPORT: ID_EM + STS + 24 measures
```

### 3. Codes CMD/STS
```
CMD: 0=Idle, 1=Start, 10=Stop, 20=Abort, 30=Reset
STS: 0=Idle, 1=Running, 2=Complete, 3=Aborted, 10=Fault
```

### 4. Structure de routine (5 par FCT)
1. **Main** (SFC) — machine d'état principale INIT→IDLE→WAIT_CMD
2. **Running** (SFC) — séquence détaillée du procédé
3. **Logic** (StructuredText) — CASE step sequencer avec CDATA
4. **EnableInFalse** (RLL) — mise en sécurité sorties
5. **Prescan** (RLL) — initialisation tags

### 5. Step sequencer Logic (ST)
```
CASE L_CURRENT_STEP OF
    0:   // Idle
    10:  // Start sequence
    20:  // Step 1
    30:  // Step 2
    ...
    999: // Fault/Abort handling
END_CASE;
```

### 6. Prefixes tags
```
L_*   = Local (interne au FCT)
I_*   = Input (depuis extérieur)
IO_*  = Input/Output exchange
EXC_* = Exchange inter-systèmes
PLC_* = PLC system tags
```

### 7. Fichier L5X : éléments obligatoires
- `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`
- `<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="33.00">`
- `<Controller>` avec ProcessorType 1756-L83E
- `<DataTypes>` section avec TOUS les UDTs utilisés
- `<Program>` avec Name= FCT_XX_NAME
- Tags: IO_FCT, IO_BATCH_MGT_FROM/TO_FCT, PLC_TASK_EXC, L_CURRENT_STEP, L_EM_XXX
- Routines: Main(SFC), Running(SFC), Logic(ST CDATA), EnableInFalse(RLL), Prescan(RLL)
- Tout code ST dans `<![CDATA[...]]>`

### 8. Structure Noms de fichiers
- `FCT_XX_NAME.L5X` (ex: FCT_01_EXTRUSION)
- Zone sans FCT: `ROH_Zone_NAME.L5X`
- UDTs globaux: `ROH_UDT_Definitions.L5X`
- AOIs: `ROH_AOI_Definitions.L5X`
- Projet maître: `ROH_Master_Project.L5X`

### 9. Pièges / Problèmes fréquents
- Ne JAMAIS utiliser de UDT_Motor/Valve/Sensor génériques — toujours créer des UDT_EM_XXX
- Ne JAMAIS faire 1 fichier = 1 zone — découper en FCT (1 fonction = 1 programme)
- Toujours inclure IO_FCT, IO_BATCH_MGT, PLC_TASK_EXC dans chaque FCT
- Toujours utiliser le pattern CMD/STS (pas de booléens plats)
- Toujours inclure SFC (pas que du ST)
- Toujours utiliser les préfixes L_, I_, IO_, EXC_
- Vérifier que le nom du Program match le nom du fichier
- Vérifier que tous les UDTs référencés sont déclarés dans la section DataTypes
- Vérifier que le CDATA est bien fermé et équilibré

---

## Adaptation Siemens SCL (TIA Portal)

Les mêmes conventions logiques s'appliquent en Siemens SCL. Voici le mapping :

| Concept Rockwell | Équivalent Siemens |
|---|---|
| FCT_XX | FB_XX (Function Block) |
| UDT_EM_XXX | TYPE "UDT_EM_XXX" (PLC data type) |
| IO_FCT : UDT_GEN_FCT | Interface VAR_INPUT / VAR_OUTPUT du FB |
| L_EM_XXX : UDT_EM_XXX | VAR_IN_OUT (passage par référence REF_TO) |
| L_CURRENT_STEP : DINT | VAR L_Step : Int |
| Main(SFC) + Running(SFC) | CASE L_Step OF 0/10/20/.../999 |
| EnableInFalse / Prescan (RLL) | Pas nécessaire — géré par OB cycle + OB100 startup |
| CDATA | Source SCL direct (pas d'encapsulation XML) |
| CMD/STS codes | Identiques : 0/1/10/20/30 et 0/1/2/3/10 |

### Syntaxe SCL spécifique
- Variables locales : préfixe `#` (ex: `#L_Step`)
- Variables globales : guillemets `"` (ex: `"DB_GRINDER".EM`)
- Timers : multi-instance TON/TOF en VAR (ex: `tDelay : TON`)
- Step sequencer : `CASE #L_Step OF 0: ... 10: ... 999: ... END_CASE;`
- Pas de SFC en SCL pur — remplacer par CASE step sequencer

### Structure d'un FB SCL standard
```
FUNCTION_BLOCK "FB_XX_NAME"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1
   VAR_INPUT
      IO_CMD_START : Bool;   // CMD=1
      IO_CMD_STOP  : Bool;   // CMD=10
      IO_CMD_ABORT : Bool;   // CMD=20
      IO_CMD_RESET : Bool;   // CMD=30
   END_VAR
   VAR_OUTPUT
      STS_RUNNING  : Bool;   // STS=1
      STS_COMPLETE : Bool;   // STS=2
      STS_FAILURE  : Bool;   // STS=10
      STS_CODE     : Int;    // Valeur STS
   END_VAR
   VAR_IN_OUT
      EM : "UDT_EM_XXX";     // Equipment Module
   END_VAR
   VAR
      L_Step : Int;          // Step sequencer
      tDelay : TON;          // Multi-instance timer
   END_VAR
BEGIN
   // Command decoding + CASE step sequencer + Status update
END_FUNCTION_BLOCK
```

### Génération batch des FB SCL via Python
Pour 50+ FB, utiliser un template Python :

```python
template = '''FUNCTION_BLOCK "FB_{num:02d}_{name}"
...
   CASE #L_Step OF
      0:  // Idle
      10: // Start
      20: // Running
      50: // Complete
      999: // Fault/Abort
   END_CASE;
END_FUNCTION_BLOCK'''
```

Voir les projets ROH (46 FB) et RGY (54 FB) dans `output/ROH_DevAssite/siemens/fbs/` et `output/rockwell_gen/RGY_corrected/siemens/fbs/` pour des exemples complets.