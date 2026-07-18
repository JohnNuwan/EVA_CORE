# Référence approfondie Rockwell Studio 5000

## Architecture recommandée
- Controller Tags pour l'interface externe
- Program Tags pour la logique encapsulée
- UDT pour standardiser les équipements
- AOI ou routines pour la logique récurrente

## Standard de blocs à viser
- AOI_MotorStandard
- AOI_ValveStandard
- Routine_AnalogStandard
- Diagnostic tags stabilisés pour HMI/SCADA

## Recommandations terrain
- garder les noms < 40 caractères ;
- centraliser Fault/Ready/Run ;
- isoler la couche SCADA des détails internes ;
- systématiser CDATA dans les fragments L5X générés.
