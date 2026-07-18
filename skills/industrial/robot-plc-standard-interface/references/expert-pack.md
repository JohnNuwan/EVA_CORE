# Pack Expert Interface Robot ↔ PLC

## Objectif
Standardiser les échanges cellule robotisée ↔ automate pour éviter les variantes projet par projet.

## Blocs recommandés
- Cmd
- Sts
- Safe
- Fault
- Mode
- Cycle

## Etats minimaux
- Ready
- Busy
- CycleDone
- Fault
- AtHome
- InAuto
- InTeach

## Sécurité
- FenceClosed
- EStopOk
- RobotSafe
- ResetRequired

## Règle clé
Le contrat doit rester identique quelle que soit la marque robot. Seule la couche d'adaptation constructeur change.