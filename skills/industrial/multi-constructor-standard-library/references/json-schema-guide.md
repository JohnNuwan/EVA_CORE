# Exemple de schéma JSON riche

## Champs principaux
- `device_type`
- `name`
- `vendors`
- `io`
- `alarms`
- `permissives`
- `timers`
- `units`
- `scada`
- `mes`
- `safety`
- `packml`

## safety
Exemple :
- `enabled`
- `zone`
- `plr`
- `sil`
- `sto`
- `ss1`
- `sls`
- `reset_required`

## packml
Exemple :
- `enabled`
- `mode`
- `state_model`
- `unit_mode`

## Sorties HMI/SCADA associées
Le même contrat alimente :
- Ignition tags/UDT/sequence
- WinCC faceplate XML
- InTouch CSV tags
- faceplate safety et mapping HMI standardisé

## Batch
Utiliser `equipment: [...]` pour générer une bibliothèque complète.
