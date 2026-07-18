# Scénarios de diagnostic robot à surveiller

## Scénario 1 — Robot prêt mais jamais démarré
Signes :
- `Ready = 1`
- `Busy = 0`
- pas de `StartCycle` utile

Hypothèses :
- PLC n'envoie pas la commande ;
- permissif cellule absent ;
- séquence amont non validée.

## Scénario 2 — Robot Busy trop longtemps
Signes :
- `Busy = 1` prolongé
- pas de `CycleDone`
- temps de cycle au-dessus du nominal

Hypothèses :
- blocage trajectoire ;
- attente pince / vision / convoyeur ;
- attente acquittement PLC.

## Scénario 3 — Défauts suivis de resets répétés
Signes :
- `Fault` fréquent
- `ResetRequired` fréquent
- reprise rapide sans suppression de cause

Hypothèses :
- défaut récurrent masqué ;
- traitement symptomatique ;
- dégradation progressive d'un sous-ensemble.

## Scénario 4 — Robot absent de la performance ligne
Signes :
- disponibilité robot correcte
- OEE faible
- temps d'attente robot élevé

Hypothèses :
- robot sous-alimenté par la ligne ;
- goulot ailleurs ;
- mauvaise synchronisation PLC / périphérie.
