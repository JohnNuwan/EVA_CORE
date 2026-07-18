# Contrat type Robot ↔ Historian

## 1. Portée
- robot / cellule :
- source principale : PLC interface / contrôleur robot / mixte
- fréquence :

## 2. Points minimum
- `Ready`
- `Busy`
- `Fault`
- `CycleDone`
- `AtHome`
- `InAuto`
- `InTeach`
- `ResetRequired`
- `FaultCode`
- `ProgramId`
- `CycleTime`

## 3. Règles de données
- historiser transitions d'états ;
- historiser défauts et resets ;
- conserver chronologie handshake ;
- horodater chaque cycle terminé ;
- séparer safety, process et défaut robot.

## 4. Critères d'acceptation
- possibilité de distinguer attente robot vs attente PLC ;
- possibilité de reconstruire un blocage ;
- possibilité de calculer temps de cycle et disponibilité robot.
