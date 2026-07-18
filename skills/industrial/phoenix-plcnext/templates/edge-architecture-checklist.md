# Template checklist architecture PLCnext edge

## Couches
- logique automate locale
- services edge
- publication OPC UA/MQTT
- dépendances externes
- mode dégradé

## Questions clés
- Que fait la machine si le réseau IT tombe ?
- Quelles données sont bufferisées ?
- Quels services sont critiques / non critiques ?
- Quelles versions de composants sont gelées ?
- Quelles interfaces sont exposées vers SCADA/MES/cloud ?
