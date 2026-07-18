# Catalogue des Equipment Modules (EM) — Projets ROH & RGY

Ce catalogue référence tous les UDT_EM_XXX utilisés dans les projets
Courbon/Actemium pour Royal Canin (ROH) et Gimje (RGY).

Chaque EM = 5 UDTs :
  UDT_EM_XXX            (conteneur COMMAND/STATUS)
  UDT_EM_XXX_CMD        (ID_EM, CMD, ID_FCT_RESERV)
  UDT_EM_XXX_SETPOINT   (SP01..SP24: REAL)
  UDT_EM_XXX_STA        (ID_EM, STS, ID_FCT_RESERV)
  UDT_EM_XXX_STA_BOOL   (18 bits status)
  UDT_EM_XXX_REPORT     (24 measures REAL)

---

## Projet ROH (Royal Canin Lewisburg — Extrusion)

### EXTRU — Extrusion Zone

| EM Code | Description | ID_EM | SETPOINT members |
|---------|-------------|-------|-------------------|
| EXTRU_MAG | Extrusion magnet | 1001 | SP01=MagnetTimer, SP02=VibeFreq |
| EXTRU_SIEVE | Extrusion sieve | 1002 | SP01=SieveSpeed, SP02=BlowerSpeed |
| EXTRU_SILO_XX | Extrusion silo (generic) | 1003..1004 | SP01=FillLevel, SP02=EmptyLevel |
| EXTRU_EXTRUDER | Extruder motor | 1010 | SP01=SpeedRef, SP02=LoadLimit, SP03=TempZone1 |
| EXTRU_CUTTER | Cutter knife | 1011 | SP01=KnifeSpeed, SP02=CutLength |

### COATING — Coating Zone

| EM Code | Description | ID_EM | SETPOINT members |
|---------|-------------|-------|-------------------|
| COATING_COATER | Coating drum | 2001 | SP01=DrumSpeed, SP02=SprayDelay, SP03=TempSP |
| COATING_EMPT | Coating empty | 2002 | SP01=EmptyTime, SP02=PurgePressure |
| COATING_VACUUM | Coating vacuum check | 2003 | SP01=VacuumSP, SP02=HoldTime, SP03=LeakLimit |
| COATING_VENTIL | Coating ventilation | 2004 | SP01=FanSpeed, SP02=DamperPos, SP03=FilterDP |
| COATING_BD_HEAT | Bottom drive heating | 2005 | SP01=TempSP01, SP02=TempSP02, SP03=Hysteresis |

### DRYER / HWT — Drying & Hot Water

| EM Code | Description | ID_EM | SETPOINT members |
|---------|-------------|-------|-------------------|
| DRYER_CONV | Dryer conveyor | 3001 | SP01=SpeedRef, SP02=BeltTension |
| DRYER_FAN | Dryer fan | 3002 | SP01=FanSpeed, SP02=ExhaustSpeed |
| DRYER_ZONE | Dryer temperature zone | 3010..3015 | SP01=TempSP, SP02=HeaterBand |
| HWT_PUMP | HWT circulation pump | 3020 | SP01=PumpSpeed |
| HWT_HEATER | HWT electric heater | 3021 | SP01=TempSP, SP02=HeatRate |
| HWT_LEVEL | HWT level control | 3022 | SP01=LevelSP, SP02=FillTime |

### DOSING — Dosing & Weighing

| EM Code | Description | ID_EM | SETPOINT members |
|---------|-------------|-------|-------------------|
| STATION_SCALE | Weighing station | 4001 | SP01=TargetWeight, SP02=FastFill, SP03=Dribble, SP04=Tolerance |
| LIQUID_DOSING | Liquid dosing | 4002 | SP01=FlowSP, SP02=DoseVolume, SP03=DoseTime |
| LIQ_DOSING_BLOW | Liquid blow-out | 4003 | SP01=BlowPressure, SP02=BlowTime |
| GRIND_TRF_BLOW | Pneumatic transfer | 4004 | SP01=BlowPressure, SP02=BlowTime, SP03=DwellTime, SP04=PulseCount |
| DOSING_SCREW | Dosing screw | 4005 | SP01=ScrewSpeed, SP02=FeedRate |

### GRINDING — Grinding Area

| EM Code | Description | ID_EM | SETPOINT members |
|---------|-------------|-------|-------------------|
| GEN_GRINDER | Grinding general | 5001 | SP01=TotalLoad, SP02=CoordTimeout |
| GRIND_GRINDER | Main grinder mill | 5002 | SP01=SpeedRef, SP02=LoadLimit, SP03=OverloadDelay |
| GRIND_SIEVE | Grinding sieve | 5003 | SP01=VibeFreq, SP02=SieveSpeed |
| GRIND_REGUL | Grinding regulation | 5004 | SP01=FeedRate, SP02=RegulationMode |
| GRIND_REJECT_SIEVE | Reject sieve | 5005 | SP01=RejectRate, SP02=SieveFreq |
| GRIND_ASPI | Grinding aspiration | 5006 | SP01=FanSpeed, SP02=FilterDP, SP03=PulseInterval, SP04=PulseDuration |
| MIX_MIXER | Main mixer | 5010 | SP01=MixSpeed, SP02=MixTime, SP03=DischargeSpeed |
| MIX_STOCK_MACRO | Macro stock mixer | 5011 | SP01=LowLevel, SP02=EmptyLevel |
| PMIX_HOPPER | Premixer hopper | 5020 | SP01=FillLevel, SP02=DischargeRate, SP03=AgitatorSpeed |
| PMIX_EMPT | Premixer empty | 5021 | SP01=EmptyTime, SP02=PurgePressure, SP03=CycleCount |
| XX_STOCK_MICRO | Micro stock generic | 5030 | SP01=LowLevel, SP02=EmptyLevel, SP03=FillTime |

### GENERIC / SYSTEM

| EM Code | Description | ID_EM | Notes |
|---------|-------------|-------|-------|
| INTERFACE | External interface | 8001 | KSE, WMS, printer, etc. |
| KPI_MONITOR | KPI tracking | 8002 | Production OEE counters |
| PACKAGING | Packaging line | 8003 | Bagging, sealing, palletizing |
| RECEPTION | Raw material reception | 9001 | Truck dock, silo assignment |

---

## Projet RGY (Gimje — Recycling/Plastics)

### GENERAL — Common Functions

| EM Code | Description | ID_EM | SETPOINT members |
|---------|-------------|-------|-------------------|
| SUPERVISION | System supervision | 1 | SP01=Heartbeat, SP02=ScanTime |
| AGIT_LI06A | Agitator tank LI06A | 2 | SP01=SpeedRef, SP02=RampTime |
| AGIT_LI06B | Agitator tank LI06B | 3 | SP01=SpeedRef, SP02=RampTime |
| TANK_AGITATOR | General tank agitation | 4..6 | SP01=SpeedRef, SP02=RunTime |
| PIPE_HEATING | Pipe heating | 7..9 | SP01=TempSP, SP02=HeaterPower |
| TANK_HEATING | Tank heating | 10..12 | SP01=TempSP01, SP02=TempSP02, SP03=Hysteresis |
| LEVEL_CONTROL | Level control | 13..14 | SP01=LevelSP, SP02=Deadband |

### RECEPTION — Raw Materials

| EM Code | Description | ID_EM | Notes |
|---------|-------------|-------|-------|
| RECEPTION | Reception general | 100 | Truck dock, silo assignment, weighbridge |

### GRINDING (same EM as ROH but different ID_EM range)

Same UDT_EM structures as ROH project, ID_EM starting at 200.

### EXTRUSION (same EM as ROH)

Same UDT_EM structures, ID_EM starting at 300.

---

## Note d'implémentation

Quand vous créez une nouvelle UDT_EM pour un projet :
1. Copier le pattern depuis un EM existant (ex: GRIND_TRF_BLOW)
2. Adapter les SETPOINT aux besoins spécifiques de l'équipement
3. Ajuster les STA_BOOL si des status particuliers sont requis
4. Assigner un ID_EM unique dans la plage du projet
5. Déclarer **tous** les UDTs dans la section DataTypes du fichier L5X ou dans le fichier UDT global
