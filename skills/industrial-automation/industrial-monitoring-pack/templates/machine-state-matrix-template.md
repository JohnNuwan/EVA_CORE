# Matrice d'états machine

| État canonique | Source terrain | Condition d'entrée | Condition de sortie | Historiser | Impact KPI | Commentaire |
|---|---|---|---|---|---|---|
| Arrêt | PLC state | machine non en marche | démarrage autorisé | Oui | disponibilité | |
| Démarrage | PLC state | séquence start active | passage en production | Oui | performance | |
| Production | PLC state | cycle automatique nominal | arrêt, défaut, attente | Oui | OEE | |
| Attente | PLC state | machine prête sans produire | reprise flux | Oui | perte mineure | |
| Défaut | PLC/alarm | défaut bloquant | reset + reprise | Oui | disponibilité | |
| Manuel | mode machine | mode manuel actif | auto ou arrêt | Oui | hors OEE selon règle | |
| Maintenance | mode machine | maintenance déclarée | retour exploitation | Oui | arrêt planifié | |

## Règle
Stabiliser cette matrice avant tout calcul OEE ou dashboard de performance.
