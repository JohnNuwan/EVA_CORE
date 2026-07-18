---
name: packml-isa-tr88
description: "Implémenter des machines d'état PackML en SCL/ST."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [packml, isa-tr88, state-machine, plc, scl, structured-text, oem, industrial-automation]
    related_skills: [siemens-scl, batch-process-isa88, mes-integration, oee-performance, rockwell-studio5000]
---

# PackML / ISA-TR88.00.02 — Machine d'État Standardisée

## Vue d'ensemble

**PackML (Packaging Machine Language)** est le standard industriel ISA-TR88.00.02 qui définit une machine d'état universelle pour piloter les machines de production. Développé à l'origine pour l'emballage (OEM packaging), PackML est aujourd'hui adopté dans tous les secteurs (agroalimentaire, pharmaceutique, automobile, logistique).

PackML normalise :
1. **17 états de machine** répartis en 3 modes (Production, Maintenance, Manuel).
2. **Les tags d'interface standardisés** (PackTags) pour l'échange de données entre la machine et le système de supervision/MES.
3. **Le calcul de TRS/OEE** directement depuis les compteurs PackML.

Pour un intégrateur comme Actemium, PackML garantit l'interopérabilité entre les machines de différents OEM sur une même ligne de production.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'implémenter une **machine d'état PackML** dans un automate (Siemens, Rockwell, Schneider, Beckhoff).
- De concevoir les **PackTags** (interface standardisée machine → supervision).
- De calculer le **TRS/OEE** à partir des compteurs PackML (temps de marche, arrêt, défaut).
- De concevoir un **faceplate HMI PackML** pour les opérateurs.
- De spécifier les interfaces machine pour un cahier des charges OEM.

**Ne pas utiliser pour :**
- Les procédés batch complexes avec recettes et gestion de lots (utiliser `batch-process-isa88`).
- La programmation de logique séquentielle simple sans besoin de standardisation (utiliser `siemens-scl`).

---

## 1. Machine d'État PackML Complète

Le diagramme d'état PackML définit 17 états avec des transitions strictes :

```text
                              ┌──────────────────────────────┐
                              │     ÉTATS ACTING (verbes)    │
                              │  (transitions automatiques)  │
                              └──────────────────────────────┘

    ┌─────────┐  SC:Start  ┌───────────┐  SC:Complete  ┌────────────┐
    │ STOPPED │───────────▶│ STARTING  │──────────────▶│  EXECUTE   │
    └────┬────┘            └───────────┘               └─────┬──────┘
         │                                                    │
         │ SC:Reset                                          │ SC:Complete
         │                                                    ▼
    ┌────┴─────┐           ┌───────────┐               ┌────────────┐
    │  IDLE    │◄──────────│ RESETTING │◄──────────────│ COMPLETING │
    └──────────┘           └───────────┘               └────────────┘
                                ▲                            │
                                │ SC:Reset                   │
                           ┌────┴─────┐                      ▼
                           │ COMPLETE │◄─────────────────────┘
                           └──────────┘

    ── Depuis tout état EXECUTE : ──

    SC:Hold     → HOLDING → HELD
    SC:Unhold   → UNHOLDING → EXECUTE (reprise)

    SC:Suspend  → SUSPENDING → SUSPENDED
    SC:Unsuspend→ UNSUSPENDING → EXECUTE (reprise)

    ── Depuis tout état (sauf ABORTING/ABORTED) : ──

    SC:Abort    → ABORTING → ABORTED → (SC:Clear) → STOPPED

    ── Depuis tout état (sauf STOPPING/STOPPED) : ──

    SC:Stop     → STOPPING → STOPPED
```

### Différence clé entre HELD et SUSPENDED :

| Concept | HELD | SUSPENDED |
|---|---|---|
| **Cause** | Interne à la machine (défaut récupérable, attente opérateur) | Externe à la machine (amont/aval de la ligne arrêté) |
| **Exemple** | Plus de film d'emballage → opérateur doit recharger | La machine en amont a stoppé → plus de produits entrants |
| **Reprise** | SC:Unhold (action opérateur) | SC:Unsuspend (condition externe résolue) |

---

## 2. Implémentation Complète en SCL (Siemens TIA Portal)

```scl
FUNCTION_BLOCK "FB_PackML_StateMachine"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0

VAR_INPUT
    // Commandes d'état (State Commands)
    i_SC_Reset     : Bool;
    i_SC_Start     : Bool;
    i_SC_Stop      : Bool;
    i_SC_Hold      : Bool;
    i_SC_Unhold    : Bool;
    i_SC_Suspend   : Bool;
    i_SC_Unsuspend : Bool;
    i_SC_Abort     : Bool;
    i_SC_Clear     : Bool;
    // Signaux de fin d'état (retours internes)
    i_StateComplete : Bool;  // La logique de l'état courant a terminé
END_VAR

VAR_OUTPUT
    q_CurrentState  : Int;    // État courant (numéro PackML)
    q_StateName     : String; // Nom de l'état en texte
    q_IsExecute     : Bool;   // Indique que la machine est en production
    q_IsIdle        : Bool;   // Indique que la machine est prête
    q_IsStopped     : Bool;   // Indique que la machine est arrêtée
    q_IsAborted     : Bool;   // Indique que la machine est en défaut
    q_IsHeld        : Bool;   // Indique que la machine est en pause interne
    q_IsSuspended   : Bool;   // Indique que la machine est en pause externe
END_VAR

VAR
    stat_State : Int := 1;  // État initial : STOPPED
END_VAR

VAR CONSTANT
    // Constantes PackML (numérotation standard OMAC)
    c_UNDEFINED   : Int := 0;
    c_STOPPED     : Int := 2;
    c_STARTING    : Int := 3;
    c_IDLE        : Int := 4;
    c_SUSPENDED   : Int := 5;
    c_EXECUTE     : Int := 6;
    c_STOPPING    : Int := 7;
    c_ABORTING    : Int := 8;
    c_ABORTED     : Int := 9;
    c_HOLDING     : Int := 10;
    c_HELD        : Int := 11;
    c_UNHOLDING   : Int := 12;
    c_SUSPENDING  : Int := 13;
    c_UNSUSPENDING: Int := 14;
    c_RESETTING   : Int := 15;
    c_COMPLETING  : Int := 16;
    c_COMPLETE    : Int := 17;
END_VAR

BEGIN
    // ═══════════════════════════════════════════
    // Commandes prioritaires (Abort et Stop)
    // ═══════════════════════════════════════════
    IF #stat_State <> #c_ABORTING AND #stat_State <> #c_ABORTED THEN
        IF #i_SC_Abort THEN
            #stat_State := #c_ABORTING;
        END_IF;
    END_IF;

    IF #stat_State <> #c_STOPPING AND #stat_State <> #c_STOPPED
       AND #stat_State <> #c_ABORTING AND #stat_State <> #c_ABORTED THEN
        IF #i_SC_Stop THEN
            #stat_State := #c_STOPPING;
        END_IF;
    END_IF;

    // ═══════════════════════════════════════════
    // Machine d'état PackML principale
    // ═══════════════════════════════════════════
    CASE #stat_State OF

        2: // ── STOPPED ──
            IF #i_SC_Reset THEN
                #stat_State := #c_RESETTING;
            END_IF;

        3: // ── STARTING ──
            IF #i_StateComplete THEN
                #stat_State := #c_EXECUTE;
            END_IF;

        4: // ── IDLE ──
            IF #i_SC_Start THEN
                #stat_State := #c_STARTING;
            END_IF;

        5: // ── SUSPENDED ──
            IF #i_SC_Unsuspend THEN
                #stat_State := #c_UNSUSPENDING;
            END_IF;

        6: // ── EXECUTE ──
            IF #i_SC_Hold THEN
                #stat_State := #c_HOLDING;
            ELSIF #i_SC_Suspend THEN
                #stat_State := #c_SUSPENDING;
            ELSIF #i_StateComplete THEN
                #stat_State := #c_COMPLETING;
            END_IF;

        7: // ── STOPPING ──
            IF #i_StateComplete THEN
                #stat_State := #c_STOPPED;
            END_IF;

        8: // ── ABORTING ──
            IF #i_StateComplete THEN
                #stat_State := #c_ABORTED;
            END_IF;

        9: // ── ABORTED ──
            IF #i_SC_Clear THEN
                #stat_State := #c_STOPPING;
            END_IF;

        10: // ── HOLDING ──
            IF #i_StateComplete THEN
                #stat_State := #c_HELD;
            END_IF;

        11: // ── HELD ──
            IF #i_SC_Unhold THEN
                #stat_State := #c_UNHOLDING;
            END_IF;

        12: // ── UNHOLDING ──
            IF #i_StateComplete THEN
                #stat_State := #c_EXECUTE;
            END_IF;

        13: // ── SUSPENDING ──
            IF #i_StateComplete THEN
                #stat_State := #c_SUSPENDED;
            END_IF;

        14: // ── UNSUSPENDING ──
            IF #i_StateComplete THEN
                #stat_State := #c_EXECUTE;
            END_IF;

        15: // ── RESETTING ──
            IF #i_StateComplete THEN
                #stat_State := #c_IDLE;
            END_IF;

        16: // ── COMPLETING ──
            IF #i_StateComplete THEN
                #stat_State := #c_COMPLETE;
            END_IF;

        17: // ── COMPLETE ──
            IF #i_SC_Reset THEN
                #stat_State := #c_RESETTING;
            END_IF;

    END_CASE;

    // ═══════════════════════════════════════════
    // Mise à jour des sorties
    // ═══════════════════════════════════════════
    #q_CurrentState := #stat_State;
    #q_IsExecute    := (#stat_State = #c_EXECUTE);
    #q_IsIdle       := (#stat_State = #c_IDLE);
    #q_IsStopped    := (#stat_State = #c_STOPPED);
    #q_IsAborted    := (#stat_State = #c_ABORTED);
    #q_IsHeld       := (#stat_State = #c_HELD);
    #q_IsSuspended  := (#stat_State = #c_SUSPENDED);

    // Nom de l'état en texte pour l'IHM
    CASE #stat_State OF
        2:  #q_StateName := 'STOPPED';
        3:  #q_StateName := 'STARTING';
        4:  #q_StateName := 'IDLE';
        5:  #q_StateName := 'SUSPENDED';
        6:  #q_StateName := 'EXECUTE';
        7:  #q_StateName := 'STOPPING';
        8:  #q_StateName := 'ABORTING';
        9:  #q_StateName := 'ABORTED';
        10: #q_StateName := 'HOLDING';
        11: #q_StateName := 'HELD';
        12: #q_StateName := 'UNHOLDING';
        13: #q_StateName := 'SUSPENDING';
        14: #q_StateName := 'UNSUSPENDING';
        15: #q_StateName := 'RESETTING';
        16: #q_StateName := 'COMPLETING';
        17: #q_StateName := 'COMPLETE';
    ELSE
        #q_StateName := 'UNDEFINED';
    END_CASE;

END_FUNCTION_BLOCK
```

---

## 3. PackTags — Interface Standardisée Machine ↔ Supervision

Les PackTags définissent les variables d'échange entre la machine et le système MES/SCADA :

### Administration Tags :

| Tag | Type | Description |
|---|---|---|
| `Admin.ProdConsumedCount[n]` | DINT[8] | Compteurs de consommation matière par produit |
| `Admin.ProdProcessedCount[n]` | DINT[8] | Compteurs de pièces produites conformes |
| `Admin.ProdDefectiveCount[n]` | DINT[8] | Compteurs de pièces rebutées |
| `Admin.MachDesignSpeed` | REAL | Cadence nominale de la machine (pièces/min) |
| `Admin.CurMachSpeed` | REAL | Cadence instantanée actuelle |

### Status Tags :

| Tag | Type | Description |
|---|---|---|
| `Status.StateCurrent` | INT | État PackML courant (numéro OMAC) |
| `Status.UnitModeCurrent` | INT | Mode actif (1=Production, 2=Maintenance, 3=Manuel) |
| `Status.MachSpeed` | REAL | Vitesse courante |
| `Status.EquipmentInterlock` | BOOL | Verrouillage de sécurité actif |

### Calcul TRS/OEE depuis les PackTags :

```python
def calculate_oee_from_packtags(
    planned_production_time_min: float,
    run_time_min: float,
    total_produced: int,
    good_produced: int,
    ideal_cycle_time_sec: float,
) -> dict:
    """Calcule le TRS/OEE à partir des compteurs PackML.

    Args:
        planned_production_time_min: Temps de production planifié (minutes).
        run_time_min: Temps de marche effectif (minutes).
        total_produced: Nombre total de pièces produites (bonnes + rebutées).
        good_produced: Nombre de pièces conformes.
        ideal_cycle_time_sec: Temps de cycle idéal par pièce (secondes).

    Returns:
        dict: Disponibilité, Performance, Qualité et TRS global.
    """
    # Disponibilité = Temps de marche / Temps planifié
    availability = run_time_min / planned_production_time_min if planned_production_time_min > 0 else 0

    # Performance = (Pièces produites × Temps de cycle idéal) / Temps de marche
    performance = (total_produced * ideal_cycle_time_sec / 60) / run_time_min if run_time_min > 0 else 0

    # Qualité = Pièces conformes / Total produites
    quality = good_produced / total_produced if total_produced > 0 else 0

    # TRS = Disponibilité × Performance × Qualité
    oee = availability * performance * quality

    return {
        "availability_pct": round(availability * 100, 1),
        "performance_pct": round(performance * 100, 1),
        "quality_pct": round(quality * 100, 1),
        "oee_pct": round(oee * 100, 1),
        "total_produced": total_produced,
        "good_produced": good_produced,
        "rejected": total_produced - good_produced,
    }
```

---

## 4. Faceplate HMI PackML (Spécification)

L'IHM opérateur doit afficher :

```text
┌────────────────────────────────────────────┐
│  MACHINE : Conditionneuse L1               │
│  État : ██ EXECUTE ██    Mode : Production │
│  Vitesse : 120 / 150 ppm                  │
├────────────────────────────────────────────┤
│  [START] [STOP] [HOLD] [RESET] [ABORT]    │
├────────────────────────────────────────────┤
│  Disponibilité : 94.2%  ████████████░░    │
│  Performance   : 87.5%  ██████████░░░░    │
│  Qualité       : 99.1%  █████████████░    │
│  TRS / OEE     : 81.6%  ████████████░░    │
├────────────────────────────────────────────┤
│  Produites: 12,450  Rebutées: 112 (0.9%) │
│  Temps marche: 6h 23m  Arrêt: 0h 28m     │
└────────────────────────────────────────────┘
```

---

## Pièges Courants

1. **Implémenter seulement 6 états au lieu des 17 :**
   * *Erreur :* Ne coder que STOPPED, IDLE, EXECUTE, HELD, ABORTING, ABORTED. Les états transitoires (STARTING, COMPLETING, RESETTING...) sont omis.
   * *Correction :* Les états transitoires sont essentiels pour que la supervision sache que la machine est en phase de montée en régime ou de vidange. Les 17 états doivent être implémentés.

2. **Confondre HELD et SUSPENDED :**
   * *Erreur :* Utiliser HELD pour toutes les pauses, qu'elles soient internes ou externes à la machine.
   * *Correction :* HELD = cause interne (opérateur, manque de consommable). SUSPENDED = cause externe (la ligne amont/aval est arrêtée).

3. **Ne pas implémenter i_StateComplete :**
   * *Erreur :* Les états ACTING (STARTING, STOPPING, HOLDING...) passent instantanément à l'état suivant sans attendre la fin réelle de l'action.
   * *Correction :* Le signal `i_StateComplete` doit être piloté par la logique métier spécifique de chaque état (ex: la rampe de démarrage moteur est terminée, la purge est finie).

---

## Références

- **ISA-TR88.00.02-2015** — Machine and Unit States: An Implementation Example.
- **OMAC PackML** — https://www.omac.org/packml
- **Siemens Application Example** — PackML State Machine for S7-1500.
- **Rockwell Application Code** — PackML Implementation for ControlLogix.

---

## Liste de vérification (Checklist)

- [ ] Les 17 états PackML sont implémentés dans le bloc de machine d'état.
- [ ] Les transitions HELD ↔ SUSPENDED sont correctement différenciées (cause interne vs externe).
- [ ] Les PackTags d'administration (compteurs de production) sont mis à jour en temps réel.
- [ ] Le signal `i_StateComplete` est piloté par la logique métier et non câblé en dur à TRUE.
- [ ] Le faceplate HMI affiche l'état courant, la vitesse, et les indicateurs TRS/OEE.
- [ ] La numérotation des états utilise le standard OMAC (2=STOPPED, 6=EXECUTE, etc.).

