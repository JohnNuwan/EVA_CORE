# Courbon/Actemium Engineer UDT Patterns — ROH Project References

Extracted from 46 FCT L5X files provided by engineers for ROH DevAssist (Royal Canin Lewisburg, extrusion + grinding pet food line, CPU 1756-L83E v33).

## Generic Interface UDTs (in every FCT)

### UDT_GEN_FCT (14 members)
```
ID_FCT:DINT
├── CMD:UDT_GEN_FCT_CMD
│   └── W:UDT_GEN_FCT_CMD_BOOL
│       ├── START: BIT / STOP: BIT / ABORT: BIT / RESET: BIT
│       └── HOLD: BIT / RESTART: BIT / SPARE1/2: BIT
├── STA:UDT_GEN_FCT_STA
│   └── W:UDT_GEN_FCT_STA_BOOL (13 bits)
│       ├── RUNNING | COMPLETE | FAILURE | ABORTED
│       ├── IDLE | HELD | STOPPING | STARTING
│       └── AUTO | ALARMED | INHIBITED | PROD | CLEAN
├── WRK:UDT_GEN_FCT_WRK └── CFG:UDT_GEN_FCT_CONFIG
```

### UDT_GEN_EM_STA_BOOL (18 bits — identical for EVERY EM)
```
ST_RUNNING | ST_COMPLETE | ST_FAILURE | ST_ABORTED
ST_IDLE | ST_HELD | ST_STOPPING | ST_STARTING
AUTO | ALARMED | INHIBITED | FORBIDDEN
CONNECTED | DEMAND | CHAIN_OK | PERMISSIVE_OK
INTERLOCK_OK | SPARE
```

### Standard Interface Tags (every FCT)
```
IO_FCT:UDT_GEN_FCT
IO_BATCH_MGT_FROM_FCT | IO_BATCH_MGT_TO_FCT
PLC_TASK_EXC:UDT_GEN_PLC_TASK | PLC_CONFIG:UDT_GEN_PLC_CONFIG
L_CURRENT_STEP:DINT | L_EM_{ZONE}_{EQ}:UDT_EM_{ZONE}_{EQ}
PARAM_{ZONE}:UDT_PARAM_{ZONE}
```

## EM 5-UDT Pattern (every equipment)
```
UDT_EM_{ZONE}_{EQ}        → {COMMAND:CMD, STATUS:STA}
  UDT_EM_{ZONE}_{EQ}_CMD  → {ID_EM:DINT, CMD:DINT, ID_FCT_RESERV:DINT, SETPOINT:EM_SETPOINT}
  UDT_EM_{ZONE}_{EQ}_STA  → {ID_EM:DINT, STS:DINT, ID_FCT_RESERV:DINT, MEASURE:EM_STA_BOOL}
  UDT_EM_{ZONE}_{EQ}_SETPOINT → SP01..SP24 (REAL)
  UDT_EM_{ZONE}_{EQ}_REPORT → MS01..MS24 (REAL)
```
CMD: 0=Idle 1=Start 10=Stop 20=Abort 30=Reset
STS: 0=Idle 1=Running 2=Complete 3=Aborted 10=Fault

## Tag Prefixes
| Prefix | Role | Example |
|--------|------|---------|
| IO_FCT | Function interface | IO_FCT : UDT_GEN_FCT |
| IO_RECIPE | Recipe | IO_RECIPE : UDT_RECIPE_EXTRU |
| IO_BATCH_MGT_* | Batch MES | IO_BATCH_MGT_FROM_FCT |
| PLC_TASK_EXC | Task exchange | PLC_TASK_EXC : UDT_GEN_PLC_TASK |
| L_EM_* | Local EM | L_EM_EXTRU_MAG : UDT_EM_EXTRU_MAG |
| L_CURRENT_STEP | Step counter | L_CURRENT_STEP : DINT |
| I_SYN_* | HMI input | I_SYN_AUTHOR_START : BOOL |
| PARAM_* | Parameters | PARAM_EXTRU : UDT_PARAM_EXTRU |
| EXC_* | System exchange | EXC_C_TO_G : Comm_Courbon_To_Geelen |

## Complete FCT Inventory (46 files)
| File | Area | Description |
|------|------|-------------|
| FCT_01_EXTRUSION | Extrusion | Magnet, Sieve, Extruder, Cutter |
| FCT_02_FINES_RECYCL | Fines | Fines recycling |
| FCT_03_EMPTY_HB_FINES_TO_RW | Fines | Empty hospital bin fines to rework |
| FCT_10_DRYER_TRANSPORT | Dryer | Dryer output transport |
| FCT_11_EMPTY_HOSPITAL | Hospital | Empty hospital bin |
| FCT_12_KIBBLE_BATCHING | Batching | Kibble batching before coating |
| FCT_21_COATING | Coating | Drum, Spray, BD Heating, Vacuum, Ventilation |
| FCT_22_LIQUID_DOSING | Dosing | Liquid dosing |
| FCT_24_VENTILATION_COATER | Ventilation | Coater ventilation |
| FCT_25_HOT_AIR_CLEANING | Cleaning | Hot air cleaning |
| FCT_26_COATER_VACUUM_CHECKING | Vacuum | Coater vacuum checking |
| FCT_28_HEAT_BD_HOPPER_COATER | Heating | BD hopper heating |
| FCT_30_POWDER_DOSING_01 | Dosing | Powder dosing station |
| FCT_40_CALIBRATION_LIQUID_NAOX | Calibration | NAOX liquid calibration |
| FCT_41_CALIBRATION_LIQUID_FAT_02 | Calibration | FAT 02 liquid calibration |
| FCT_41_TRF_MACRO_PREMIXER_1 | Transfer | Macro transfer to premixer |
| FCT_42_CALIBRATION_LIQUID_FAT_03 | Calibration | FAT 03 calibration |
| FCT_43_STOCK_MACRO_PREMIXER | Stock | Macro stock premixer |
| FCT_45_CALIBRATION_LIQUID_AROMA_01 | Calibration | Aroma calibration |
| FCT_48_TRF_MICRO_PREMIXER | Transfer | Micro transfer to premixer |
| FCT_49_STOCK_MICRO_PREMIXER | Stock | Micro stock premixer |
| FCT_50_PREMIXER | Premixer | Main premixer |
| FCT_50_PRIMING_LIQUID_NAOX | Priming | NAOX liquid priming |
| FCT_51_HOPPER_PREMIXER | Hopper | Premixer hopper |
| FCT_52_GRINDER | Grinding | Grinder, Sieve, Regulator |
| FCT_53_PMIX_REGRIND | Regrind | Premixer regrind |
| FCT_54_PMIX_REGRIND_ASPI | Aspiration | Regrind aspiration |
| FCT_58_TRF_MICRO_MIXER | Transfer | Micro transfer to mixer |
| FCT_59_STOCK_MICRO_MIXER | Stock | Micro stock mixer |
| FCT_60_MIXER | Mixer | Main mixer |
| FCT_61_COOLER_PACKAGING_OPRP_DELTA_T | OPRP | Cooler/packaging HACCP |
| FCT_61_TRF_UNDER_MIXER | Transfer | Transfer under mixer |
| FCT_70_FINAL_PRODUCT_TRANSPORT | Transport | Final product transport |
| FCT_81_FILLING_FEEDER_01 | Feeder | Filling feeder station |
| FCT_90_ASPIRATION_ELEV_HOSP | Aspiration | Elevator/hospital aspiration |
| FCT_91_ASPIRATION_COATER_HOPPER | Aspiration | Coater hopper aspiration |
| FCT_92_ASPIRATION_SIFTER | Aspiration | Sifter aspiration |
| FCT_100_WWR_PRODUCTION | WWR | Waste water recovery production |
| FCT_101_CALIBR_LIQUID_01 | Calibration | Liquid calibration 01 |
| FCT_101_WWR_CLEANING | WWR | WWR cleaning |
| FCT_102_HWT_PRODUCTION | HWT | Hot water treatment production |
| FCT_103_HWT_CLEANING | HWT | HWT cleaning/CIP |
| FCT_111_CLEANING_SIEVE | Cleaning | Sieve cleaning |
| FCT_111_CLEANING_SIEVE_GR01 | Cleaning | Sieve cleaning GR01 |