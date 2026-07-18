# Roadmap de maturité du monitoring industriel

## Niveau 0 — Visibilité minimale
Objectif : savoir si l'équipement vit ou non.

Capacités :
- ping / port / connectivité ;
- état machine global ;
- défaut général ;
- quelques analogiques critiques.

Critère de sortie :
- une équipe maintenance peut confirmer à distance si la machine tourne, est stoppée ou est en défaut.

## Niveau 1 — Monitoring opérationnel
Objectif : lire les bons points sans saturer le terrain.

Capacités :
- registre de points ;
- acquisition structurée ;
- historisation court terme ;
- dashboard temps réel.

Critère de sortie :
- les états, défauts et mesures clés sont lisibles avec horodatage cohérent.

## Niveau 2 — Diagnostic maintenance
Objectif : réduire le temps de diagnostic.

Capacités :
- chronologie des événements ;
- état CPU / communication ;
- top défauts ;
- codes défauts robot et drives ;
- vues maintenance dédiées.

Critère de sortie :
- un arrêt peut être analysé avec chronologie et cause probable en quelques minutes.

## Niveau 3 — Performance / OEE
Objectif : transformer le monitoring en levier de performance.

Capacités :
- états machine consolidés ;
- cadence ;
- temps de cycle ;
- OEE / TRS ;
- micro-arrêts ;
- top pertes.

Critère de sortie :
- la production peut identifier les pertes dominantes sur une ligne ou cellule.

## Niveau 4 — Énergie & optimisation croisée
Objectif : relier performance, énergie et qualité d'exploitation.

Capacités :
- énergie par lot / pièce ;
- comparaison baseline vs réel ;
- corrélation défauts / dérives / consommation ;
- dashboard multi-vues maintenance + méthodes.

Critère de sortie :
- les dérives énergétiques et de cadence sont visibles et actionnables.

## Niveau 5 — Prédictif ciblé
Objectif : anticiper certaines défaillances.

Capacités :
- dérives lentes ;
- modèles simples d'anomalies ;
- vibration / température / courant ;
- priorisation maintenance conditionnelle.

Critère de sortie :
- certains défauts récurrents peuvent être anticipés avant arrêt complet.

## Règle de progression
Ne jamais sauter directement au prédictif si :
- les timestamps sont faux ;
- les états machine sont mal définis ;
- les défauts ne sont pas historisés proprement ;
- la qualité des données n'est pas stabilisée.
