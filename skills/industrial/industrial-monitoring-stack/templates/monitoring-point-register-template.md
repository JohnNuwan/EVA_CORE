# Modèle de registre des points de monitoring

| Zone | Équipement | Source | Protocole | Point / Tag / NodeId | Famille | Type | Unité | Fréquence | Historiser ? | Criticité | Usage principal | Commentaire |
|---|---|---|---|---|---|---|---|---:|---|---|---|---|
| Ligne 1 | PLC principal | S7-1500 | OPC UA | ns=3;s=Machine.State | Sts | Int | - | 500 ms | Oui | Haute | état machine | PackML simplifié |
| Ligne 1 | Robot 1 | PLC interface | EtherNet/IP | Robot1.Sts.Busy | Sts | Bool | - | 250 ms | Oui | Haute | cellule robot | handshake |
| Ligne 1 | Drive 1 | Variateur | Modbus TCP | 40021 | Ana | Float | Hz | 1 s | Oui | Moyenne | vitesse réelle | |
| Ligne 1 | Compteur énergie | PM5xxx | Modbus TCP | 3203 | Cnt | Float | kWh | 30 s | Oui | Moyenne | énergie cumulée | |
| Ligne 1 | PLC principal | S7-1500 | S7 | CPU.State | Meta | String | - | 60 s | Oui | Haute | santé automate | diagnostic |

## Règles de remplissage
- `Famille` : `Cmd`, `Sts`, `Alm`, `Ana`, `Cnt`, `Safe`, `Kpi`, `Meta`.
- `Historiser ?` : Oui seulement si le point a une valeur diagnostic, réglementaire ou de performance.
- `Criticité` : Haute, Moyenne, Basse.
- `Usage principal` : maintenance, exploitation, OEE, énergie, qualité, safety.
