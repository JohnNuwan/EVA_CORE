# Registre complet des points de monitoring

| Site | Atelier | Ligne | Équipement | Sous-équipement | Source | Protocole | Point / Tag / NodeId | Famille | Type | Unité | Fréquence | Historiser | Criticité | Dashboard cible | Alerte associée | KPI associé | Commentaire |
|---|---|---|---|---|---|---|---|---|---|---|---:|---|---|---|---|---|---|
| Site A | Atelier 1 | Ligne 1 | PLC principal | CPU | S7-1500 | S7 | CPU.State | Meta | String | - | 60 s | Oui | Haute | maintenance | ALT-001 | disponibilité | |
| Site A | Atelier 1 | Ligne 1 | Robot 1 | Interface | PLC | EtherNet/IP | Robot1.Sts.Busy | Sts | Bool | - | 250 ms | Oui | Haute | robot | ALT-002 | attente robot | |
| Site A | Atelier 1 | Ligne 1 | Drive 1 | Axe X | Drive | Modbus TCP | 40021 | Ana | Float | Hz | 1 s | Oui | Moyenne | exploitation | ALT-003 | cycle | |

## Règles
- Une ligne = un point utile réellement gouverné.
- Toujours renseigner famille, fréquence, criticité et dashboard cible.
- Ne pas historiser sans usage métier, diagnostic ou KPI clair.
