---
name: sql-for-industrial-systems
description: "Structurer l’usage professionnel de SQL en industrie pour historian, OEE, traçabilité, reporting, MES et consolidation OT/IT."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, sql, historian, oee, traceability, mes, reporting, scada]
    related_skills: [scada-hmi-programming-languages, industrial-databases, industrial-reporting, ot-it-integration-languages]
---

# SQL pour systèmes industriels

## Vue d'ensemble

Cette compétence couvre l’usage professionnel de SQL dans les systèmes industriels : historian, OEE, traçabilité, rapports de production, MES, consolidation de données d’usine et audit. Elle aide à concevoir des requêtes, modèles de données et patterns d’accès adaptés aux contraintes industrielles.

SQL doit être traité comme un langage industriel de premier plan dès qu’il existe historian, MES, reporting, audit qualité ou traçabilité. La qualité des timestamps, des clés de lot, des index, des statuts qualité et des conventions temporelles y est aussi importante que la syntaxe elle-même.

## Quand l'utiliser
- Historiser et exploiter des données industrielles.
- Construire des rapports OEE, traçabilité ou qualité.
- Structurer les accès SQL entre SCADA, MES et reporting.
- Définir des standards requêtes et performance.
- Préparer des modèles de données auditables pour opérations, qualité et process.

## Positionnement professionnel

### Historian / séries temporelles
Usages :
- tendances ;
- états machines ;
- temps de marche/arrêt ;
- agrégations de cycles ;
- consolidations par période.

### Traçabilité / lots
Usages :
- lien lot entrant ↔ lot process ↔ lot fini ;
- consommations matières ;
- généalogie de production ;
- contrôles qualité.

### OEE / performance
Usages :
- availability ;
- performance ;
- quality ;
- micro-arrêts ;
- causes d’arrêt ;
- comparaisons lignes/équipes/produits.

### Reporting / audit
Usages :
- rapports qualité ;
- audits ;
- revue de production ;
- exports réglementaires ou clients.

## Méthode de travail pas à pas

### Étape 1 — Définir le modèle métier
Identifier explicitement :
- équipement ;
- lot ;
- ordre ;
- produit ;
- événement ;
- alarme ;
- mesure ;
- statut qualité.

### Étape 2 — Définir le temps
Toujours préciser :
- timezone ;
- source timestamp ;
- granularité ;
- horodatage événement vs enregistrement ;
- gestion des retards de collecte.

### Étape 3 — Définir la gouvernance des requêtes
Séparer :
- requêtes temps réel ;
- reporting ;
- consolidation ;
- audit ;
- maintenance DB.

### Étape 4 — Définir la performance
- index ;
- volumétrie ;
- archivage ;
- partitionnement si besoin ;
- limites de latence ;
- séparation lecture/écriture.

## Cas d’usage terrain

### OEE multi-lignes
SQL central pour calculs agrégés, causes d’arrêt, tendances par équipe/produit.

### Traçabilité alimentaire/pharma
SQL central pour relier lot matière, batch, contrôles qualité et expéditions.

### Historian SCADA
SQL pour requêtes analytiques, reporting et audit, avec soin particulier sur timestamps et qualité de données.

## Pièges Courants (Common Pitfalls)

1. Mélanger logique métier, UI et SQL sans séparation.
2. Écrire des requêtes lourdes sans penser volumétrie et indexation.
3. Négliger la traçabilité des modifications et la qualité des timestamps.
4. Concevoir le schéma autour de l’écran HMI au lieu du besoin métier.
5. Oublier la gouvernance de la qualité des données.

## Checklist de validation finale
- [ ] Le modèle de données est aligné avec les usages métier.
- [ ] Les requêtes critiques sont identifiées et optimisées.
- [ ] Les conventions temporelles et de qualité de données sont définies.
- [ ] Les accès SQL sont sécurisés et gouvernés.
- [ ] Les besoins OEE, traçabilité, historian et audit sont clairement séparés.
- [ ] La stratégie de volumétrie, indexation et archivage est connue.
