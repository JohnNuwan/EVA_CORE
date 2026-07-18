# ROH DevAssist — Projet complet (29 FDS, 6 zones)

## Contexte
Projet Royal Canin (Mars Inc.) — ligne d'extrusion, site Lewisburg Ohio.
Ingénierie : EVA Saint-Étienne (ex Courbon SAS).
CPU : 1756-L83E v33. 29 FDS (Functional Design Specifications).

## Structure du projet L5X

```
output/ROH_DevAssite/
├── l5x/
│   ├── ROH_Master_Project.L5X          ← UDTs + référencement des fichiers
│   ├── ROH_AOI_Definitions.L5X         ← 4 AOIs (Motor, Valve, Coater, Dryer)
│   ├── ROH_Zone_Extrusion.L5X          ← 1 238 lignes
│   ├── ROH_Zone_Coater.L5X             ← 1 348 lignes
│   ├── ROH_Zone_Dryer.L5X              ← 2 689 lignes
│   ├── ROH_Zone_Aspiration.L5X         ← 336 lignes
│   ├── ROH_Zone_Filling_Dosing.L5X     ← 430 lignes
│   └── ROH_Zone_Support.L5X            ← 561 lignes
├── st/ROH_DevAssist_Types.st           ← UDTs en .st
└── reports/ROH_Project_Report.md       ← Documentation
```

## UDTs définis (8)

| UDT | Membres clés | Usage |
|-----|-------------|-------|
| UDT_Motor | CmdStart, CmdStop, CmdSpeedRef, StsRunning, StsFault, StsAtSpeed, StsLocal, AlmFault, PermissiveOK, InterlockOK | Tout moteur VSD ou ON/OFF |
| UDT_Valve | CmdOpen, CmdClose, StsOpened, StsClosed, StsFault, StsInTransit | Vannes tout-ou-rien |
| UDT_Sensor | ProcessValue, RawValue, StsHigh, StsLow, StsFault, SetPoint | Capteurs analogiques |
| UDT_Diverter | CmdSelect, StsPosition, StsFault, PermissiveOK | Vannes pneumatiques diverters |
| UDT_AnalogInput | RawMin/Max, ScaledMin/Max, ProcessValue, StsFault | Entrées 4-20mA avec scaling |
| UDT_Phase | CmdRun/Abort/Stop/Reset, StsIdle/Running/Complete/Aborted, StatusSeq | Machine d'état Equipment Phase |
| UDT_Coater | MotorDrum(UDT_Motor), MotorSpray, TempProduct, FlowOil, SpeedConsign | Équipement coater complet |
| UDT_Dryer | Conveyor(UDT_Motor), Fan, TempZone1/2, HumidityExhaust | Équipement dryer complet |

## AOIs (4)

| AOI | Paramètres | Fonction |
|-----|-----------|----------|
| AOI_MotorControl | Motor(UDT_Motor), ResetFault, PermissiveConditions, InterlockConditions, CmdStart/Stop | Start/stop, fault handling, timeout monitoring |
| AOI_ValveControl | Valve(UDT_Valve), CmdOpen/Close | Open/close, transit detection, timeout fault |
| AOI_CoaterControl | Coater(UDT_Coater), DrumSpeedSP, TempHighLimit, FlowLowLimit | Drum rotation, spray, temp/flow monitoring |
| AOI_DryerControl | Dryer(UDT_Dryer), ConveyorSpeedSP, TempZone1SP/2SP | Conveyor, fan, 2-zone temp control |

## Zones fonctionnelles

### 1. Extrusion
- Modules : Magnet, Sieve, Extruder, Cutter
- Tags : 13 UDT instances + 50+ I/O aliases
- State machine : 6 états (Idle → Starting → Running → Completing → Complete → Aborted)
- Séquence : cascade 5 étapes avec fan start sequencing

### 2. Coater
- Modules : Drum, Spray, BD Heating, Vacuum Checking, Ventilation
- Tags : 60+ (8 control modules, 34 I/O aliases)
- Séquence : Jog/Run drum, Spray 3s delay, Vacuum 4-step, Ventilation purge

### 3. Dryer/HWT
- Modules : Dryer, Dryer Output, HWT Production, HWT Cleaning, Sifter
- Tags : 6 zones température, belt tracking
- Séquence : HWT Production 5-step, HWT Cleaning 7-step, Sifter jam detection

### 4. Aspiration
- Modules : Coater Hopper, Dryer Sifter, Elevator Hospital
- State machine : 5 états (Idle → Conveying → FilterCleaning → Standby → Alarm)

### 5. Filling & Dosing
- Modules : Feeder, Powder, Kibble Batching, Liquid Dosing, Powder Dosing
- State machine : 6 états (Idle → FastFill → Dribble → Stabilize → Discharge → Alarm)

### 6. Support
- 15 sous-systèmes : Cleaning, Fines Recycling, FP Transport, Hot Air Clean, Load Powder, OPRP, NAOX, WWR, Calibration, etc.
- 4 états maître + sous-séquences indépendantes

## Conventions de nommage

| Type | Format | Exemple |
|------|--------|---------|
| Tags UDT | {ZONE}_{EQ}_{TYPE} | EX_MG01_M01, CO_DRUM_M01 |
| Tags I/O | DI/DO/AI/AO_{NAME} | DI_EX_MG01_LSH01 |
| Programmes | Zone_{NAME} | Zone_Extrusion |
| Routines | Main | Main |
| AOIs | AOI_{NAME} | AOI_MotorControl |
| Fichiers L5X | ROH_Zone_{Name}.L5X | ROH_Zone_Coater.L5X |

## Pattern de state machine (template)

```structuredtext
CASE PhaseSts OF
    0: (* Idle *)
        IF CmdRun THEN
            PhaseSts := 10;
        END_IF;
    
    10: (* Starting *)
        // Séquence de démarrage
        IF AllStarted THEN
            PhaseSts := 20;
        END_IF;
    
    20: (* Running *)
        IF CmdStop THEN
            PhaseSts := 30;
        END_IF;
        IF Fault THEN
            PhaseSts := 50;
        END_IF;
    
    30: (* Completing *)
        // Ramp-down / purge
        IF AllStopped THEN
            PhaseSts := 40;
        END_IF;
    
    40: (* Complete *)
        IF CmdReset THEN
            PhaseSts := 0;
        END_IF;
    
    50: (* Aborted *)
        IF CmdReset THEN
            PhaseSts := 0;
        END_IF;
END_CASE;
```

## Leçons apprises
1. Les sous-agents génèrent plus facilement des L5X complets (tags + routine + CDATA) que des .st partiels
2. Passer un L5X existant dans `context` du `delegate_task` garantit un format homogène entre zones
3. La validation parente (CDATA count, Content check) est indispensable — les sous-agents oublient parfois le CDATA
4. Les machines d'état CASE sont plus fiables que les IF/THEN séquentiels pour les phases complexes
5. Préférer les UDT composites (UDT_Coater, UDT_Dryer) aux UDT atomiques pour les équipements complexes