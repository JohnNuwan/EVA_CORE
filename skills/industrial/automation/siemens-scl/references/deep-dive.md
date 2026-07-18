# Référence approfondie Siemens SCL

## Architecture recommandée
- FB pour logique à état
- FC pour calculs purs
- UDT pour contrat métier
- DB d'instance et paramètres séparés
- couche I/O séparée de la logique process

## Standard de blocs à viser
- FB_MotorStandard
- FB_ValveStandard
- FC_AnalogStandard
- FB_SequenceStandard
- FB_AlarmStandard

## Recommandations terrain
- centraliser permissifs et interlocks ;
- rendre les diagnostics lisibles pour maintenance ;
- exposer un contrat stable vers SCADA ;
- éviter les adresses absolues modernes sauf contrainte explicite.
