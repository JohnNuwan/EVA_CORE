# Matrice d'alertes monitoring industriel

| ID | Zone | Équipement | Condition | Persistance | Sévérité | Canal | Destinataire | Action attendue | Accusé requis ? | Commentaire |
|---|---|---|---|---|---|---|---|---|---|---|
| ALT-001 | Ligne 1 | PLC principal | CPU en STOP | immédiat | Critique | dashboard + mail | maintenance + automatisme | prise en charge immédiate | Oui | arrêt production |
| ALT-002 | Ligne 1 | Robot 1 | Busy > 120 s sans CycleDone | 3 cycles | Haute | dashboard | maintenance | vérifier blocage cellule | Oui | handshake robot/PLC |
| ALT-003 | Ligne 1 | Drive 1 | Température > 80 °C | 5 min | Haute | dashboard + Teams | maintenance | inspection refroidissement | Oui | |
| ALT-004 | Ligne 1 | Réseau OT | perte communication > 30 s | 30 s | Haute | dashboard | automatisme | vérifier switch / lien | Oui | |
| ALT-005 | Ligne 1 | Compteur énergie | puissance > baseline + 20 % | 10 min | Moyenne | dashboard | méthodes / énergie | analyser dérive | Non | dépend production |

## Règles
- Toujours définir une persistance pour éviter le bruit.
- Ne créer une alerte que si une action est attendue.
- Séparer les alertes critiques de sûreté, de production, de maintenance et d'énergie.
