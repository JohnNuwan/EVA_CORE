---
name: batch-process-isa88
description: "Modéliser des recettes et des phases batch ISA-88."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [isa-88, batch, s88, recipe, phase-manager, plc, scl, structured-text, industrial-automation]
    related_skills: [siemens-scl, mes-integration, packml-isa-tr88, isa95-modelling, process-pharma, process-agrifood]
---

# Contrôle par Lots & ISA-88 (Batch Control)

## Vue d'ensemble

La norme **ISA-88 (ANSI/ISA-88.01 / IEC 61512)** est le standard mondial pour le contrôle des procédés de fabrication par lots (batch). Elle est omniprésente dans les industries **agroalimentaire, pharmaceutique, chimique et cosmétique** — cœur de métier d'EVA.

ISA-88 sépare strictement :
- Le **modèle physique** (Cellule de procédé → Unité → Module d'équipement → Module de contrôle).
- Le **modèle procédural** (Procédure → Procédure d'unité → Opération → Phase).
- Le **modèle de recette** (Header, Formula, Equipment Requirements, Procedure).

Cette compétence guide l'agent EVA pour modéliser des procédures batch, concevoir des machines d'état de phases, et structurer des recettes conformes à ISA-88.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De modéliser un procédé de fabrication par lots selon le standard ISA-88.
- De concevoir un **Phase Manager** (bloc de gestion de phase) en SCL ou Structured Text.
- De structurer des **recettes de fabrication** (Header, Formula, Procedure) en JSON ou XML.
- D'implémenter la machine d'état ISA-88 (Idle → Running → Complete → Held → Aborted...).
- De concevoir l'interface entre un superviseur batch (ex: Siemens SIMATIC Batch, Wonderware InBatch) et les automates.

**Ne pas utiliser pour :**
- La programmation de logique continue sans notion de lots (utiliser `siemens-scl` ou `pid-tuning-control`).
- La gestion de production MES sans lien avec le contrôle batch (utiliser `mes-integration`).

---

## 1. Machine d'État ISA-88 d'une Phase

Chaque phase d'un procédé batch suit une machine d'état standardisée avec des transitions strictes :

```text
                    ┌──────────┐
         ┌─────────│   IDLE   │◄────────────────────┐
         │         └────┬─────┘                     │
         │              │ Start                     │ Reset
         │              ▼                           │
         │         ┌──────────┐     Hold       ┌────┴─────┐
         │         │ RUNNING  │───────────────▶│  HELD    │
         │         └────┬─────┘                └────┬─────┘
         │              │                           │ Restart
         │              │ Complete                  │
         │              ▼                      ─────┘
         │         ┌──────────┐
         │         │COMPLETING│
         │         └────┬─────┘
         │              │
         │              ▼
         │         ┌──────────┐
         └─────────│ COMPLETE │
                   └──────────┘

    (Depuis tout état sauf IDLE)
         │ Abort
         ▼
    ┌──────────┐      Reset     ┌──────────┐
    │ ABORTING │───────────────▶│ ABORTED  │──────▶ IDLE
    └──────────┘                └──────────┘

    (Depuis tout état sauf IDLE)
         │ Stop
         ▼
    ┌──────────┐      Reset     ┌──────────┐
    │ STOPPING │───────────────▶│ STOPPED  │──────▶ IDLE
    └──────────┘                └──────────┘
```

### Énumération des états en SCL (Siemens TIA Portal) :

```scl
TYPE "E_PhaseState" : INT
    // États de la machine d'état ISA-88 d'une phase
    IDLE       := 0;
    RUNNING    := 1;
    COMPLETING := 2;
    COMPLETE   := 3;
    HELD       := 4;
    HOLDING    := 5;
    RESTARTING := 6;
    STOPPING   := 7;
    STOPPED    := 8;
    ABORTING   := 9;
    ABORTED    := 10;
END_TYPE
```

---

## 2. Bloc de Phase Manager en SCL

Le Phase Manager est le bloc FB central qui pilote la machine d'état d'une phase :

```scl
FUNCTION_BLOCK "FB_PhaseManager"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0

VAR_INPUT
    i_CmdStart    : Bool;   // Commande de démarrage depuis le superviseur batch
    i_CmdHold     : Bool;   // Commande de mise en pause
    i_CmdRestart  : Bool;   // Commande de reprise après pause
    i_CmdStop     : Bool;   // Commande d'arrêt contrôlé
    i_CmdAbort    : Bool;   // Commande d'arrêt d'urgence
    i_CmdReset    : Bool;   // Commande de réinitialisation
    i_PhaseReady  : Bool;   // Retour : la phase a terminé son action
    i_PhaseFault  : Bool;   // Retour : la phase a détecté un défaut
END_VAR

VAR_OUTPUT
    q_State       : Int;    // État courant de la machine d'état (E_PhaseState)
    q_IsRunning   : Bool;   // Indique que la phase est en cours d'exécution
    q_IsComplete  : Bool;   // Indique que la phase a terminé avec succès
    q_IsAborted   : Bool;   // Indique que la phase a été interrompue
    q_IsFaulted   : Bool;   // Indique un défaut de la phase
END_VAR

VAR
    stat_State    : Int := 0;  // État interne persistant
END_VAR

BEGIN
    // Gestion des commandes d'arrêt prioritaires (depuis tout état sauf IDLE)
    IF #stat_State <> 0 THEN
        IF #i_CmdAbort THEN
            #stat_State := 9;  // ABORTING
        ELSIF #i_CmdStop AND #stat_State < 7 THEN
            #stat_State := 7;  // STOPPING
        END_IF;
    END_IF;

    CASE #stat_State OF
        0:  // IDLE — En attente de démarrage
            #q_IsRunning  := FALSE;
            #q_IsComplete := FALSE;
            #q_IsAborted  := FALSE;
            #q_IsFaulted  := FALSE;
            IF #i_CmdStart THEN
                #stat_State := 1;  // → RUNNING
            END_IF;

        1:  // RUNNING — Phase en cours d'exécution
            #q_IsRunning := TRUE;
            IF #i_PhaseFault THEN
                #q_IsFaulted := TRUE;
                #stat_State := 9;  // → ABORTING
            ELSIF #i_CmdHold THEN
                #stat_State := 5;  // → HOLDING
            ELSIF #i_PhaseReady THEN
                #stat_State := 2;  // → COMPLETING
            END_IF;

        2:  // COMPLETING — Finalisation en cours
            // Logique de nettoyage ou de purge ici
            #stat_State := 3;  // → COMPLETE

        3:  // COMPLETE — Phase terminée avec succès
            #q_IsRunning  := FALSE;
            #q_IsComplete := TRUE;
            IF #i_CmdReset THEN
                #stat_State := 0;  // → IDLE
            END_IF;

        4:  // HELD — Phase en pause
            #q_IsRunning := FALSE;
            IF #i_CmdRestart THEN
                #stat_State := 6;  // → RESTARTING
            END_IF;

        5:  // HOLDING — Transition vers pause
            #q_IsRunning := FALSE;
            #stat_State := 4;  // → HELD

        6:  // RESTARTING — Reprise en cours
            #stat_State := 1;  // → RUNNING

        7:  // STOPPING — Arrêt contrôlé en cours
            #q_IsRunning := FALSE;
            #stat_State := 8;  // → STOPPED

        8:  // STOPPED — Machine arrêtée proprement
            IF #i_CmdReset THEN
                #stat_State := 0;  // → IDLE
            END_IF;

        9:  // ABORTING — Arrêt d'urgence en cours
            #q_IsRunning := FALSE;
            // Couper toutes les sorties de la phase ici
            #stat_State := 10;  // → ABORTED

        10: // ABORTED — Phase interrompue
            #q_IsAborted := TRUE;
            IF #i_CmdReset THEN
                #q_IsAborted := FALSE;
                #q_IsFaulted := FALSE;
                #stat_State := 0;  // → IDLE
            END_IF;
    END_CASE;

    // Publier l'état courant sur la sortie
    #q_State := #stat_State;
END_FUNCTION_BLOCK
```

---

## 3. Structure de Recette ISA-88 en JSON

Une recette batch se décompose en Header, Formula et Procedure :

```json
{
  "recipe_id": "REC_YOGURT_NATURE_001",
  "header": {
    "name": "Yaourt Nature 500g",
    "version": "2.1",
    "author": "EVA Process",
    "product_code": "YN500",
    "batch_size": {"value": 5000, "unit": "kg"},
    "equipment_class": "Cuve de Maturation"
  },
  "formula": {
    "parameters": [
      {"name": "Température de pasteurisation", "value": 85.0, "unit": "°C", "min": 80.0, "max": 90.0},
      {"name": "Durée de pasteurisation", "value": 30, "unit": "min", "min": 25, "max": 35},
      {"name": "Température d'ensemencement", "value": 43.0, "unit": "°C", "min": 41.0, "max": 45.0},
      {"name": "Durée de maturation", "value": 360, "unit": "min", "min": 300, "max": 420},
      {"name": "Taux de ferments", "value": 2.5, "unit": "%", "min": 2.0, "max": 3.0}
    ],
    "materials": [
      {"name": "Lait entier pasteurisé", "quantity": 4850, "unit": "kg", "lot_tracking": true},
      {"name": "Ferments lactiques", "quantity": 125, "unit": "kg", "lot_tracking": true},
      {"name": "Poudre de lait écrémé", "quantity": 25, "unit": "kg", "lot_tracking": true}
    ]
  },
  "procedure": {
    "unit_procedures": [
      {
        "name": "UP_Pasteurisation",
        "operations": [
          {
            "name": "OP_Chauffage",
            "phases": [
              {"name": "PH_Remplissage", "type": "FILL", "params": {"target_volume": 5000}},
              {"name": "PH_Chauffage", "type": "HEAT", "params": {"target_temp": 85.0, "ramp_rate": 2.0}},
              {"name": "PH_Maintien", "type": "HOLD", "params": {"duration_min": 30}}
            ]
          },
          {
            "name": "OP_Refroidissement",
            "phases": [
              {"name": "PH_Refroidissement", "type": "COOL", "params": {"target_temp": 43.0, "ramp_rate": 1.5}}
            ]
          }
        ]
      },
      {
        "name": "UP_Maturation",
        "operations": [
          {
            "name": "OP_Ensemencement",
            "phases": [
              {"name": "PH_Dosage_Ferments", "type": "DOSE", "params": {"material": "Ferments lactiques", "quantity": 125}},
              {"name": "PH_Agitation", "type": "AGITATE", "params": {"speed_rpm": 60, "duration_min": 5}}
            ]
          },
          {
            "name": "OP_Fermentation",
            "phases": [
              {"name": "PH_Maturation", "type": "HOLD", "params": {"duration_min": 360, "temp_setpoint": 43.0}}
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 4. Intégration avec le Projet Automate EVA

Le Projet Automate génère des blocs fonctionnels (FB) par catégorie d'organe via des templates Jinja2. Le pattern de génération peut être étendu pour produire des blocs de phases ISA-88 :

```python
# Extension du générateur Jinja2 pour les phases batch
# Ajouter dans app/templates/plc/siemens/ un template fb_phase.scl.j2

TEMPLATE_PHASE = """
FUNCTION_BLOCK "{{ phase.name }}"
{ S7_Optimized_Access := 'TRUE' }
VERSION : {{ phase.version }}

VAR_INPUT
    i_CmdStart    : Bool;
    i_CmdHold     : Bool;
    i_CmdAbort    : Bool;
    i_CmdReset    : Bool;
    {% for param in phase.params %}
    i_{{ param.name }} : {{ param.plc_type }};  // {{ param.description }}
    {% endfor %}
END_VAR

VAR_OUTPUT
    q_State       : Int;
    q_IsComplete  : Bool;
    q_IsAborted   : Bool;
END_VAR

VAR
    stat_PhaseManager : "FB_PhaseManager";
    {% for actuator in phase.actuators %}
    stat_{{ actuator.name }} : Bool;
    {% endfor %}
END_VAR

BEGIN
    // Gestion de la machine d'état ISA-88
    #stat_PhaseManager(
        i_CmdStart   := #i_CmdStart,
        i_CmdHold    := #i_CmdHold,
        i_CmdAbort   := #i_CmdAbort,
        i_CmdReset   := #i_CmdReset,
        i_PhaseReady := #q_IsComplete,
        i_PhaseFault := FALSE
    );

    #q_State     := #stat_PhaseManager.q_State;
    #q_IsAborted := #stat_PhaseManager.q_IsAborted;

    // Logique spécifique de la phase
    IF #stat_PhaseManager.q_IsRunning THEN
        {% for action in phase.actions %}
        // {{ action.comment }}
        {{ action.code }};
        {% endfor %}
    END_IF;
END_FUNCTION_BLOCK
"""
```

---

## Pièges Courants

1. **Confondre les modèles physique et procédural :**
   * *Erreur :* Câbler en dur la séquence d'actions dans le programme automate de l'unité physique. Cela rend impossible de produire deux recettes différentes sur la même unité.
   * *Correction :* Séparer strictement : l'unité physique expose des **phases** (capacités), et la **recette** définit l'enchaînement des phases. Le superviseur batch orchestre la séquence.

2. **Oublier les transitions HOLDING/HELD :**
   * *Erreur :* La phase n'implémente pas l'état HELD, rendant impossible la pause/reprise d'un batch lors d'un intervenant de maintenance.
   * *Correction :* Implémenter systématiquement les 11 états de la machine d'état ISA-88, même si certains sont des transitions passantes.

3. **Paramètres de recette sans bornes de validation :**
   * *Erreur :* Envoyer une température de consigne de 500°C à un échangeur de chaleur dimensionné pour 120°C parce que la recette ne valide pas les limites.
   * *Correction :* Chaque paramètre de recette doit définir des bornes `min` et `max`. Le Phase Manager doit rejeter et alarmer toute valeur hors limites.

---

## Références

- **ISA-88.01 (ANSI/ISA-88.01-2010)** — Batch Control Part 1: Models and Terminology.
- **IEC 61512-1** — Batch Control, Part 1: Models and Terminology.
- **ISA-TR88.00.02-2015** — Machine and Unit States (PackML).
- **GAMP 5** — Guide for validation of automated systems (industrie pharmaceutique).

---

## Liste de vérification (Checklist)

- [ ] La machine d'état de chaque phase implémente les 11 états ISA-88 (IDLE à ABORTED).
- [ ] Les recettes séparent clairement le Header, la Formula et la Procedure.
- [ ] Chaque paramètre de recette définit des bornes min/max validées par le Phase Manager.
- [ ] Le modèle physique (unités, modules) est indépendant du modèle procédural (recettes).
- [ ] La traçabilité des lots de matières premières est assurée à chaque dosage (lien recette → lot).

