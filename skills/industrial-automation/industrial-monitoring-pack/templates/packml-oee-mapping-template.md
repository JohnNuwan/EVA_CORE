# Template de mapping PackML → OEE

| État PackML | État OEE / TRS | Compter en disponibilité ? | Compter en performance ? | Commentaire |
|---|---|---|---|---|
| Stopped | arrêt planifié ou non selon contexte | selon règle | Non | |
| Starting | transition | Oui ou neutre selon règle | Non | |
| Idle | attente | Oui | Peut dégrader performance selon méthode | |
| Execute | production | Oui | Oui | |
| Held | arrêt mineur | Oui | Oui ou perte mineure | |
| Suspended | attente aval/amont | Oui | Oui ou perte | |
| Aborted | défaut | Non | Non | |
| Complete | cycle terminé | Oui | Oui | |

## Règles de gouvernance
- documenter la règle locale ;
- éviter de changer les mappings sans rebaseliner les KPI ;
- séparer arrêts planifiés et non planifiés.
