# Utilisation du générateur avancé multi-constructeurs

## But
Générer des artefacts multi-constructeurs à partir d'un même JSON métier riche.

## Types supportés
- motor
- valve
- analog

## Vendors supportés
- siemens
- rockwell
- schneider
- beckhoff
- omron
- wago

## Schéma riche pris en compte
- I/O
- alarmes
- permissifs
- timers
- unités
- mapping SCADA
- mapping MES
- safety metadata
- packml

## Entrées d'exemple
- `templates/example-motor-contract.json`
- `templates/example-valve-contract.json`
- `templates/example-analog-contract.json`
- `templates/example-batch-contract.json`

## Commande type
```bash
python skills/industrial/multi-constructor-standard-library/scripts/generate_standard_blocks.py contract.json
```

## Sorties générées
### Siemens
- `FB_<name>.scl`
- `UDT_<name>.scl`
- `FB_<name>.xml` (PLCopen XML)
- `FB_<name>_PackML.scl` si PackML activé

### Rockwell
- `AOI_<name>.st`
- `UDT_<name>.st`
- `AOI_<name>.l5x`
- `UDT_<name>.l5x`
- `AOI_<name>_PackML.st` si PackML activé

### Schneider
- `DFB_<name>.st`
- `DDT_<name>.st`
- `DFB_<name>.xmy`
- `DFB_<name>_PackML.st` si PackML activé

### Beckhoff / Omron / WAGO
- `FB_<name>.st`
- `ST_<VENDOR>_<name>.st`
- `FB_<name>.xml` (PLCopen XML)
- `FB_<name>_PackML.st` si PackML activé

### Ignition / SCADA
- `ignition/tags_<name>.json`
- `ignition/udt_<name>.json`
- `ignition/sequence_<name>.md`

### WinCC / InTouch / HMI safety
- `wincc/faceplate_<name>.xml`
- `wincc/alarm_classes_<name>.xml`
- `wincc/navigation_<name>.xml`
- `wincc/oee_view_<name>.xml`
- `wincc/historian_view_<name>.xml`
- `intouch/tags_<name>.csv`
- `intouch/alarm_classes_<name>.csv`
- `intouch/navigation_<name>.csv`
- `intouch/oee_view_<name>.csv`
- `intouch/historian_view_<name>.csv`
- `hmi/safety_faceplate_<name>.md`
- `hmi/mapping_<name>.md`

### Commun
- `mapping_<name>.md`

## Mode batch
Si le JSON contient une clé `equipment`, le script génère une bibliothèque complète avec un sous-dossier par équipement.

## Safety metadata
Les métadonnées safety sont injectées dans :
- les structures UDT/DDT/ST
- les mappings Markdown
- les tags Ignition
- les faceplates safety HMI

## PackML
Si `packml.enabled=true`, le générateur ajoute des squelettes de séquenceurs PackML par constructeur, les tags PackML côté Ignition et les compteurs OEE standards (Processed/Defective/RunTime/StopTime/Availability/Performance/Quality/OEE).
