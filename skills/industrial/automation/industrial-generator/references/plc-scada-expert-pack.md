# Pack Expert Intégration PLC ↔ SCADA (Siemens / Rockwell / Ignition)

## Objectif

Ce pack expert sert de socle commun pour concevoir une architecture homogène entre automates Siemens ou Rockwell et supervision Ignition, avec un contrat de tags stable, une philosophie commande/retour claire et une base exploitable pour Historian, MES et OEE.

## 1. Principe directeur

Le PLC reste la source de vérité métier temps réel.
Le SCADA orchestre l'interaction opérateur, l'affichage, la traçabilité, les rapports et l'intégration IT.

Conséquence directe :
- la logique machine vit dans l'automate ;
- la logique d'affichage vit dans Ignition ;
- les règles de mapping et de nommage sont définies une fois et réutilisées partout.

## 2. Contrat de données canonique par équipement

### 2.1 Sous-ensembles standard
- `Cmd` : commandes montantes
- `Sts` : états synthétiques
- `Alm` : alarmes et défauts
- `Ana` : mesures / consignes analogiques
- `Meta` : informations statiques ou de classification

### 2.2 Exemple canonique
- `Cmd.Start`
- `Cmd.Stop`
- `Cmd.Reset`
- `Sts.Run`
- `Sts.Ready`
- `Sts.Fault`
- `Sts.Local`
- `Sts.ModeAuto`
- `Sts.StepNo`
- `Alm.Summary`
- `Alm.Code`
- `Ana.Pv`
- `Ana.Sp`
- `Meta.EquipmentId`

## 3. Mapping Siemens / Rockwell / Ignition

| Canonique | Siemens | Rockwell | Ignition |
|---|---|---|---|
| Start commande | `Cmd.StartAuto` | `Cmd_Start` | `/Cmd/Start` |
| Etat marche | `Fb.Run` | `Sts_Run` | `/Sts/Run` |
| Défaut résumé | `Alm.FaultGeneral` | `Alm_Summary` | `/Alm/Summary` |
| Pas séquence | `stat_Step` exposé | `StepNo` | `/Sts/StepNo` |
| Valeur process | `Ana.Pv` | `Pv` | `/Ana/Pv` |

Le nom exact peut varier selon projet, mais la structure logique doit rester stable.

## 4. Philosophie de commande opérateur

### 4.1 Règles
- Une commande opérateur écrit dans un emplacement dédié.
- Le PLC arbitre permissifs, interlocks et priorité local/dist.
- Le SCADA ne force jamais un feedback.
- Les resets alarmes, resets défauts process et acquits opérateur sont distincts si le procédé l'exige.

### 4.2 Pattern recommandé
1. Ignition écrit une impulsion `Cmd.Start`
2. Le PLC consomme la commande
3. Le PLC publie `Sts.Run`, `Sts.Ready`, `Sts.Fault`
4. Ignition affiche et historise

## 5. Standard alarmes

### 5.1 Dans le PLC
- Construire les conditions de défaut primaire
- Mémoriser si besoin
- Publier un résumé et un code d'aide

### 5.2 Dans Ignition
- Afficher le texte opérateur
- Gérer les pipelines de notification / accusé / shelving si déployés
- Historiser les occurrences sans recalculer la logique défaut

## 6. Historisation et données

### 6.1 Historiser côté SCADA
- valeurs analogiques utiles
- états de marche/arrêt
- alarmes et événements
- changements de mode
- temps de cycle ou compteurs si pertinents

### 6.2 Ne pas historiser aveuglément
- bits de debug internes
- variables temporaires de séquence
- diagnostics verbeux non exploités
- duplicatas de variables déjà synthétisées

## 7. Structure de documentation minimale

Pour chaque équipement standard, livrer :
- description fonctionnelle
- mapping des signaux
- conditions de permissif
- alarmes et réactions machine
- variables exposées au SCADA
- scénarios de test FAT/SAT

## 8. Matrice FAT / SAT type

### 8.1 FAT logique
- démarrage nominal
- arrêt nominal
- perte permissif en marche
- défaut terrain simulé
- reset défaut
- passage auto ↔ manuel
- qualité des valeurs analogiques

### 8.2 SAT intégration
- écriture commande depuis Ignition
- cohérence des retours PLC
- affichage synoptique correct
- alarmes remontées avec bon texte
- historisation en base ou historian
- comportement au redémarrage automate / gateway

## 9. Règles de nommage interopérables

- Même taxonomie pour tous les équipements similaires.
- Noms courts, sans accents, stables dans le temps.
- La sémantique doit être identique d'une marque automate à l'autre.
- La couche SCADA ne doit pas inventer un second vocabulaire métier.

## 10. Cas d'emploi de ce pack
- Conception d'une bibliothèque commune Siemens + Rockwell.
- Déploiement d'un standard Ignition multi-lignes.
- Audit d'interfaces PLC ↔ SCADA.
- Préparation d'un dossier de standardisation EVA.

## 11. Checklist de revue experte
- [ ] Le PLC porte la logique métier temps réel.
- [ ] Le SCADA n'écrit que dans des tags de commande dédiés.
- [ ] Les états publiés sont synthétiques, stables et exploitables.
- [ ] Les alarmes sont calculées en amont puis correctement supervisées.
- [ ] Le mapping Siemens / Rockwell / Ignition est documenté.
- [ ] Les scénarios FAT/SAT sont définis avant mise en service.
