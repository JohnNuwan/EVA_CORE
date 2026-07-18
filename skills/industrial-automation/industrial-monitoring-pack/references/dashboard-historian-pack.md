# Pack dashboard & historian

## Objectif
Définir la couche de stockage, de restitution et d'alerte pour transformer les données terrain en vues maintenance, exploitation et performance.

## 1. Choix de la base temporelle
### InfluxDB
À privilégier si :
- priorité au time-series natif ;
- intégration rapide avec Grafana ;
- pipeline simple Edge → InfluxDB ;
- forte volumétrie de points temporels.

### TimescaleDB
À privilégier si :
- besoin SQL fort ;
- jointures avec référentiels ou données production ;
- reporting structuré ;
- équipe déjà à l'aise avec PostgreSQL.

## 2. Architecture cible
```text
Collecteur terrain
     │
     ├─ cache local / store & forward
     ▼
Historian (InfluxDB ou TimescaleDB)
     │
     ├─ données brutes
     ├─ données agrégées
     ├─ tables / mesures KPI
     ▼
Grafana
     ├─ maintenance
     ├─ exploitation
     ├─ robot
     └─ OEE / énergie
```

## 3. Stratégie de stockage recommandée
### Niveau brut
- états ;
- défauts ;
- analogiques critiques ;
- compteurs ;
- données robot utiles.
Rétention type : 7 à 30 jours.

### Niveau agrégé
- moyennes minute / heure ;
- max / min ;
- temps passés par état ;
- énergie consolidée.
Rétention type : 3 à 12 mois.

### Niveau KPI
- OEE / TRS ;
- top défauts ;
- MTBF / MTTR ;
- énergie par lot / pièce.
Rétention type : 1 à 5 ans.

## 4. Dashboards minimum
### Dashboard maintenance
- statut communication ;
- derniers défauts ;
- chronologie des événements ;
- dépassements de seuil ;
- santé CPU / robot / drive ;
- temps depuis dernier cycle valide.

### Dashboard robot
- statut `Ready/Busy/Fault/CycleDone` ;
- top défauts robot ;
- durée de blocage ;
- temps d'attente robot / PLC ;
- programme actif ;
- temps de cycle robot.

### Dashboard exploitation
- état machine ;
- cadence ;
- temps de cycle ;
- compteurs ;
- temps d'arrêt ;
- causes majeures d'arrêt.

### Dashboard OEE / performance
- disponibilité ;
- performance ;
- qualité ;
- TRS / OEE ;
- micro-arrêts ;
- top pertes.

## 5. Variables Grafana recommandées
Toujours prévoir des variables dynamiques :
- site ;
- atelier ;
- ligne ;
- machine ;
- robot ;
- période ;
- famille de défaut.

## 6. Panels recommandés
- State timeline pour états machine ;
- trend analogique ;
- table des défauts ;
- stat panels pour KPI ;
- bar chart top défauts ;
- heatmap si densité d'événements ;
- gauge pour statut synthétique uniquement si utile.

## 7. Règles d'alerte recommandées
Créer une alerte seulement si une action est attendue.
Exemples :
- CPU en STOP ;
- perte communication > 30 s ;
- robot `Busy` trop longtemps ;
- température moteur ou drive > seuil pendant N minutes ;
- temps de cycle > nominal + tolérance ;
- puissance > baseline + 20 % à production comparable.

## 8. Gouvernance de dashboard
- un dashboard n'est pas un fourre-tout ;
- une vue = un usage métier clair ;
- éviter les dizaines de courbes inutiles ;
- garder des noms d'équipements et d'états stables ;
- versionner les dashboards si possible.

## 9. Critères d'acceptation
- un mainteneur comprend la source d'un défaut en moins de quelques minutes ;
- un automaticien peut corréler défaut, état machine et analogiques ;
- un responsable production peut lire rapidement les pertes majeures ;
- les requêtes restent rapides sur de longues périodes ;
- les alertes sont peu bruyantes et réellement actionnables.
