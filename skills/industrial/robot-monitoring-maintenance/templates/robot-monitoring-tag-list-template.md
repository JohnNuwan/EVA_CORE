# Modèle de registre des points robot pour monitoring

| Cellule | Robot | Source | Point | Famille | Type | Historiser ? | Fréquence | Criticité | Usage | Commentaire |
|---|---|---|---|---|---|---|---:|---|---|---|
| Cellule A | Robot 1 | PLC interface | Robot1.Sts.Ready | Sts | Bool | Oui | 250 ms | Haute | exploitation | |
| Cellule A | Robot 1 | PLC interface | Robot1.Sts.Busy | Sts | Bool | Oui | 250 ms | Haute | cycle | |
| Cellule A | Robot 1 | PLC interface | Robot1.Sts.CycleDone | Sts | Bool | Oui | 250 ms | Haute | cycle | |
| Cellule A | Robot 1 | PLC interface | Robot1.Sts.Fault | Alm | Bool | Oui | 250 ms | Haute | maintenance | |
| Cellule A | Robot 1 | PLC interface | Robot1.Meta.FaultCode | Meta | Int | Oui | événementiel | Haute | diagnostic | |
| Cellule A | Robot 1 | PLC interface | Robot1.Meta.ProgramId | Meta | String | Oui | événementiel | Moyenne | recette | |
| Cellule A | Robot 1 | PLC calculé | Robot1.Kpi.CycleTime | Kpi | Float | Oui | par cycle | Haute | performance | s |
| Cellule A | Robot 1 | PLC interface | Robot1.Safe.RobotSafe | Safe | Bool | Oui | 250 ms | Haute | safety | |

## Règles
- Les temps de cycle sont à historiser par cycle, pas seulement en valeur instantanée.
- Les codes défauts doivent être conservés avec horodatage et acquittement associé.
- Les modes `Auto`, `Teach`, `Manual` doivent être explicités séparément.
