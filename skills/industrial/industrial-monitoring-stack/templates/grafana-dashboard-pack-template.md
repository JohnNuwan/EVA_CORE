# Template de dashboard Grafana industriel

## Variables globales
- `$site`
- `$atelier`
- `$ligne`
- `$machine`
- `$robot`
- `$period`

## Dashboard 1 — Maintenance machine
### Ligne 1
- Statut communication
- État machine actuel
- Défaut actif
- Temps depuis dernier cycle

### Ligne 2
- State timeline des états machine
- Table des 20 derniers défauts

### Ligne 3
- Températures critiques
- Courants / charges critiques
- Indicateur CPU / automate

## Dashboard 2 — Robot
### Ligne 1
- `Ready`
- `Busy`
- `Fault`
- `CycleDone`
- `InAuto`

### Ligne 2
- Timeline handshake robot ↔ PLC
- Top défauts robot

### Ligne 3
- Temps de cycle robot
- Temps d'attente robot
- Temps d'attente PLC / périphériques

## Dashboard 3 — Exploitation
### Ligne 1
- État de la ligne
- Cadence instantanée
- Compteur bonnes pièces
- Compteur rebuts

### Ligne 2
- Temps de cycle
- Répartition des états
- Top arrêts

## Dashboard 4 — OEE / Performance
### Ligne 1
- Disponibilité
- Performance
- Qualité
- OEE

### Ligne 2
- Micro-arrêts
- Top pertes
- Énergie / pièce

## Bonnes pratiques
- limiter le nombre de panels par vue ;
- utiliser les variables plutôt que du hardcoding ;
- favoriser `State timeline` pour les états ;
- agréger les données selon la période affichée ;
- séparer maintenance, exploitation et performance.
