# Mapping détaillé PLC ↔ SCADA ↔ MES

## Objectif

Décrire comment un objet standard métier est décliné dans le PLC, consommé par le SCADA et agrégé vers le MES, sans dérive sémantique entre les couches.

## 1. Principe

Le PLC publie la vérité temps réel.
Le SCADA rend l'information exploitable pour l'opérateur.
Le MES consomme des données agrégées, qualifiées et contextualisées.

## 2. Exemple MotorStandard

| Couche | Champ | Usage |
|---|---|---|
| PLC | Cmd.Start / Stop / Reset | Commandes montantes dédiées |
| PLC | Sts.Run / Ready / Fault / Local | Vérité temps réel de l'équipement |
| PLC | Alm.Summary / Code | Résumé alarme/motif |
| SCADA | Boutons opérateur | Écriture uniquement dans Cmd.* |
| SCADA | Synoptique état | Lecture de Sts.* |
| SCADA | Historique alarme | Consomme Alm.* |
| MES | Etat agrégé | Run/Ready/Fault consolidés |
| MES | KPI disponibilité | Basé sur Sts.Run/Fault et temps |

## 3. Exemple AnalogStandard

| Couche | Champ | Usage |
|---|---|---|
| PLC | RawValue | Diagnostic ou bas niveau |
| PLC | Pv / Sp / Unit | Contrat process normalisé |
| PLC | Fault / Quality | Validité de la mesure |
| SCADA | Affichage tendance | Pv / Sp / Unit |
| SCADA | Alarmes Hi/Lo | Depuis statut/alarmes publiés |
| MES | Calcul KPI | Valeurs agrégées et qualifiées |

## 4. Règles de mapping

- Le SCADA n'invente pas de seconde sémantique.
- Les champs MES doivent dériver de données déjà qualifiées.
- Les noms doivent rester stables dans le temps.
- Les données de diagnostic internes ne doivent pas polluer le contrat externe.

## 5. Recommandations

- Versionner les mappings.
- Utiliser des identifiants d'équipements stables.
- Séparer données temps réel, alarmes et KPI agrégés.
- Documenter les unités et les états qualité.
