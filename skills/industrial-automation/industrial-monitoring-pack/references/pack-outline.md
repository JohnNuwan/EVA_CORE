# Plan détaillé du Pack Monitoring Industriel

## 1. Cadrage initial
- Site / ligne / machine / cellule concernée
- Parties prenantes : maintenance, automatisme, production, méthodes
- Objectif prioritaire : maintenance, diagnostic, performance, énergie, robot, conformité
- Fenêtre de collecte acceptable et contraintes cybersécurité OT

## 2. Inventaire technique minimal
Pour chaque équipement :
- nom canonique ;
- constructeur / modèle ;
- protocole ;
- adresse ou endpoint ;
- propriétaire du point de données ;
- accès lecture seule ou lecture/écriture ;
- criticité ;
- fréquence utile de mise à jour.

## 3. Livrables minimum attendus
1. Registre des points
2. Schéma d'architecture de collecte
3. Politique d'historisation et de rétention
4. Dashboard maintenance
5. Dashboard exploitation / performance
6. Matrice d'alertes
7. Guide de diagnostic premier niveau

## 4. Couche de données canonique
Familles recommandées :
- `Cmd` : commandes
- `Sts` : états
- `Alm` : alarmes / défauts
- `Ana` : analogiques et mesures
- `Cnt` : compteurs
- `Kpi` : indicateurs calculés
- `Safe` : sécurité
- `Meta` : métadonnées techniques

## 5. Vues de dashboard minimales
### Vue maintenance
- disponibilité équipement ;
- derniers défauts ;
- qualité communication ;
- dérives mesures critiques ;
- temps depuis dernier cycle valide.

### Vue exploitation
- état machine ;
- cadence ;
- pièces / lot ;
- temps de cycle ;
- temps d'arrêt ;
- consommation ou utilities si utile.

### Vue performance
- OEE / TRS ;
- répartition états ;
- top micro-arrêts ;
- top causes d'arrêt ;
- tendance énergie / pièce.

## 6. Questions de conception à trancher
- Polling ou subscription ?
- Traitement au collecteur ou au dashboard ?
- Historisation brute continue ou événementielle ?
- Buffer local nécessaire ?
- Qui maintient les seuils d'alertes ?
- Qui est propriétaire du dictionnaire de tags ?

## 7. Règle pratique de déploiement
Commencer par un MVP sur un équipement ou une cellule, puis standardiser avant d'élargir au reste du site.
