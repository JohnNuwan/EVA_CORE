# Référence approfondie Schneider Control Expert

## Architecture recommandée
- DDT pour structures métier
- DFB pour équipements réutilisables
- variables localisées uniquement pour échanges legacy si nécessaire
- variables non localisées pour la logique interne

## Standard de blocs à viser
- DFB_MotorStandard
- DFB_ValveStandard
- DDT_AnalogStandard
- tables d'échange clairement séparées du métier

## Recommandations terrain
- maîtriser les adresses %MW ;
- rendre les DFB lisibles pour maintenance ;
- documenter le mapping HMI/SCADA ;
- préparer les exports XMY sans ambiguïté de types.
