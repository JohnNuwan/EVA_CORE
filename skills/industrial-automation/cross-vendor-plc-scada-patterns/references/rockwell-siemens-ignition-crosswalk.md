# Crosswalk Rockwell / Siemens / Ignition

## Objectif

Cette note sert de mémo rapide pour transformer un besoin fonctionnel unique en livrable cohérent sur trois couches : automate Rockwell, automate Siemens, supervision Ignition.

## Équivalences de base

| Intention | Rockwell | Siemens | Ignition |
|---|---|---|---|
| Variable globale | Controller Tag | DB global / variable accessible symboliquement | Tag provider / tag projet |
| Variable locale | Program Tag | Variable locale de bloc / statique FB | propriété de vue, script local, mémoire de session |
| Logique avec mémoire | AOI ou routine avec tags persistants | FB + DB d'instance | script gateway + tags persistants / DB |
| Calcul pur | routine ST / logique sans persistance | FC | fonction script / Named Query / transformation |
| Temporisation | TIMER avec `.PRE/.ACC/.DN/.TT` | TON/TOF/TP IEC avec `.Q` | temporisation côté script à éviter pour sécurité critique |
| Type structuré | UDT | UDT / STRUCT | JSON/tag folders/object model côté projet |
| Import/export logique | L5X | blocs TIA / sources SCL | JSON tags / ressources projet |

## Règle d'architecture

- La sûreté, les interlocks, la logique critique et les séquences déterministes restent côté PLC.
- Ignition consomme des états propres, horodate, historise, orchestre les interactions opérateur et expose les diagnostics.
- Les noms PLC doivent être pensés dès le départ pour être lisibles dans SCADA, historien et alarmes.

## Mapping minimum PLC ↔ SCADA

Toujours prévoir au moins :
- `Cmd_Start`
- `Cmd_Stop`
- `Cmd_Reset`
- `Sts_Run`
- `Sts_Auto`
- `Sts_Fault`
- `Alm_Active`
- `Permissive_OK`
- `Interlock_OK`
- `PV`
- `SP`
- `Heartbeat`
- `Comm_Quality`

## Différences à ne pas masquer

### Timers
- Rockwell : lecture habituelle via `.DN`, `.TT`, `.ACC`, `.PRE`.
- Siemens : usage typique IEC avec `.Q` et durée `T#...`.
- Ignition : ne pas déplacer une logique de temporisation de sécurité depuis PLC vers script SCADA.

### Portée des données
- Rockwell : attention à Controller Tags vs Program Tags.
- Siemens : distinguer FB/DB d'instance, FC sans mémoire, DB globaux.
- Ignition : distinguer tags, propriétés de vue, scripts gateway, Named Queries.

### Types et conversions
- Rockwell : conversions explicites recommandées sur calculs analogiques.
- Siemens : surveiller les conversions implicites et les bornes de tableaux.
- Ignition/Jython : penser qualité de tag, dataset, types Java/Jython 2.7.

## Patterns à décliner systématiquement

1. Moteur simple
2. Vanne simple
3. Mesure analogique scalée
4. Défaut mémorisé avec reset
5. Séquenceur d'étapes
6. Commande manuelle/auto
7. Heartbeat PLC↔SCADA
8. Perte communication / qualité mauvaise

## Format de réponse conseillé

Pour chaque pattern demandé :
1. intention fonctionnelle
2. version Rockwell
3. version Siemens
4. exposition Ignition
5. tags minimums
6. pièges de mise en œuvre
