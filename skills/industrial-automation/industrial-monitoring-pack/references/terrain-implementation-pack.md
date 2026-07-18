# Pack implémentation terrain

## Objectif
Donner une recette concrète de déploiement du monitoring au plus près des équipements, avant la couche historian et dashboard. Ce document sert à passer d'une idée de monitoring à une architecture de collecte exploitable sur ligne.

## 1. Architecture terrain cible
```text
PLC / Robot / Drive / Meter
        │
        ├─ OPC UA / S7 / EtherNet-IP / ADS / Modbus TCP
        │
        ▼
Collecteur Edge / VM atelier
        │
        ├─ mapping canonique des points
        ├─ cache local / store & forward
        ├─ logs de collecte
        └─ publication vers historian
```

## 2. Recette de cadrage initial
Pour chaque équipement, relever :
- constructeur, modèle, firmware ;
- protocole réellement disponible ;
- IP / port / endpoint ;
- droits d'accès ;
- tags / NodeIds / DB / adresses ;
- criticité ;
- fréquence de variation ;
- besoin métier : maintenance, diagnostic, OEE, énergie, robot.

## 3. Choix protocolaire par famille d'équipement
### OPC UA
À privilégier si l'équipement expose déjà un modèle de données exploitable et stable.
Utiliser pour :
- lecture de tags standards ;
- abonnement ;
- intégration multi-constructeurs ;
- collecte supervision / historian.

### Siemens S7
À privilégier quand l'OPC UA n'est pas disponible ou incomplet.
Vérifications préalables :
- accès PUT/GET autorisé ;
- DB non optimisés si lecture absolue ;
- rack/slot corrects ;
- portée limitée aux données utiles.

### Rockwell EtherNet/IP
À privilégier quand on veut lire les tags Logix de manière native.
Vérifications préalables :
- slot processeur ;
- tags stables et non dépendants d'une arborescence fragile ;
- limites de polling sur grands automates.

### Beckhoff ADS
À privilégier dans les architectures TwinCAT quand les variables internes sont directement utiles.
Vérifications préalables :
- AMS Net ID ;
- port runtime ;
- noms de variables stabilisés.

### Modbus TCP
À privilégier pour compteurs, variateurs, utilités et petits équipements.
Vérifications préalables :
- mapping registre validé ;
- endianness ;
- unité / scaling ;
- fréquence de collecte raisonnable.

## 4. Recette par constructeur / protocole
### OPC UA — recette type
1. Explorer depuis `Objects` et limiter la profondeur.
2. Identifier les NodeIds complets des points réellement utiles.
3. Séparer polling et subscription.
4. Ranger chaque point dans `Sts`, `Alm`, `Ana`, `Cnt`, `Safe`, `Meta`.
5. Historiser d'abord un périmètre court, puis élargir.

### Siemens — recette type
1. Identifier CPU, rack, slot.
2. Valider port 102 et accès PUT/GET.
3. Lister DB et offsets ou tags exposés via OPC UA.
4. Lire d'abord état CPU, défaut général, mode, compteurs, analogiques critiques.
5. Ajouter ensuite buffers diagnostic et temps de cycle.

### Rockwell — recette type
1. Identifier châssis, slot, IP.
2. Lister tags de cellule / machine réellement stables.
3. Créer une table de mapping tag → famille canonique.
4. Commencer par états machine, défauts, compteurs, cycle, interface robot.
5. Ajouter ensuite les métadonnées CPU et tâches si besoin maintenance.

### Beckhoff — recette type
1. Identifier AMS Net ID et port runtime.
2. Lire variables `GVL` ou structures stables exposées au monitoring.
3. Éviter de collecter des variables internes transitoires sans valeur métier.
4. Prioriser états machine, alarmes, analogiques, motion et défauts.

## 5. Registre minimal des points à lire
### États de base machine
- mode machine ;
- état global ;
- défaut général ;
- permissif production ;
- arrêt d'urgence OK ;
- temps de cycle ;
- compteur pièces bonnes ;
- compteur rebuts.

### Maintenance / diagnostic
- état CPU ;
- qualité communication ;
- dernier code défaut ;
- défauts actifs ;
- heures moteur / pompe / axe ;
- températures critiques ;
- surcharges / courants si disponibles.

### Robot
- `Ready`, `Busy`, `Fault`, `CycleDone`, `AtHome`, `InAuto`, `InTeach` ;
- code défaut robot ;
- programme actif ;
- temps de cycle robot ;
- signal de blocage handshake.

## 6. Règle de fréquence de collecte
- états et défauts : 250 ms à 1 s ;
- analogiques process : 1 s à 10 s ;
- énergie : 5 s à 60 s ;
- CPU / diagnostic : 30 s à 5 min ;
- statistiques / KPI : calcul par lot, minute ou cycle.

## 7. Déploiement MVP recommandé
### Étape 1
Une machine ou cellule robotisée unique.

### Étape 2
20 à 50 points maximum, classés par criticité.

### Étape 3
Validation des horodatages, unités, changements d'états et valeurs extrêmes.

### Étape 4
Connexion au historian.

### Étape 5
Création d'un dashboard maintenance puis exploitation.

## 8. Critères d'acceptation terrain
- les équipements répondent de manière stable ;
- les valeurs sont cohérentes physiquement ;
- les timestamps sont corrects ;
- les coupures réseau ne provoquent pas de perte silencieuse ;
- les états machine et robot restituent bien la réalité terrain ;
- le périmètre est compréhensible par maintenance et automatisme.
