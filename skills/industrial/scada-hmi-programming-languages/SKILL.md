---
name: scada-hmi-programming-languages
description: "Structurer les langages de scripting SCADA/HMI : Jython, SQL, JavaScript web HMI, VB/VBScript legacy, expressions et logique de supervision."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, scada, hmi, jython, sql, javascript, vbscript, ignition, wincc]
    related_skills: [scada-scripting-jython, ignition-scada, industrial-reporting, industrial-databases]
---

# Langages SCADA / HMI

## Vue d'ensemble

Cette compétence couvre les langages réellement utilisés dans les couches SCADA/HMI : Jython, SQL, JavaScript/TypeScript pour HMIs modernes, VB/VBScript dans les environnements legacy, expressions de tags et logique de reporting. Elle sert à choisir le bon niveau d’implémentation entre automate, supervision et backend, et à professionnaliser les pratiques de scripting de supervision.

Le but est d’éviter deux dérives fréquentes :
- remonter dans le SCADA ce qui devrait rester dans le PLC ;
- transformer la supervision en couche logicielle confuse mélangeant UI, data, alarmes, SQL et logique métier sans frontières.

## Quand l'utiliser
- Choisir où implémenter une logique métier entre PLC et SCADA.
- Écrire des scripts de supervision, reporting, historisation ou intégration MES.
- Standardiser les pratiques de scripting HMI/SCADA.
- Reprendre des environnements legacy WinCC/VBScript ou migrer vers Ignition/web HMI.
- Définir la frontière entre expressions, scripts, SQL et backend.

## Positionnement détaillé des langages

### Jython
Usages :
- Ignition gateway ;
- logique de tags ;
- scripts Perspective/Vision ;
- automatisation reporting.

Forces :
- très pertinent dans le runtime Ignition.

Limite :
- ne pas lui demander le rôle d’un backend data ou d’un moteur scientifique moderne.

### SQL
Usages :
- historian ;
- OEE ;
- traçabilité ;
- rapports ;
- named queries.

Force :
- langage clé de la supervision industrielle dès qu’il y a données, agrégations ou reporting.

### JavaScript / TypeScript
Usages :
- HMIs web modernes ;
- dashboards ;
- logique UI ;
- interactions frontend ;
- composants custom.

### VB / VBScript
Usages :
- environnements legacy ;
- scripts WinCC historiques ;
- parcs installés anciens.

Règle :
- à maintenir proprement si nécessaire, mais à encadrer pour éviter l’explosion technique legacy.

### Expressions SCADA
Usages :
- bindings ;
- visibilité ;
- états visuels ;
- petites règles simples.

Règle :
- excellent pour du simple ;
- dangereux si on leur confie une logique métier trop dense.

## Architecture professionnelle recommandée

### Principe 1 — Garder le déterminisme dans le PLC
Le SCADA ne doit pas devenir le lieu des permissifs critiques, séquences vitales ou sécurités process.

### Principe 2 — Séparer 4 couches
- UI / HMI ;
- logique de supervision ;
- accès données / SQL ;
- backend / intégrations externes.

### Principe 3 — Favoriser les scripts courts, traçables et testables
- fonctions réutilisables ;
- logs ;
- gestion d’erreurs ;
- pas de code spaghetti dans les événements écran.

## Cas d’usage terrain

### Ignition + Historian + reporting
- Jython pour orchestration légère ;
- SQL pour données ;
- logique critique conservée côté PLC.

### Web HMI moderne
- JavaScript/TypeScript pour UI ;
- API ou backend pour traitements lourds.

### Parc legacy WinCC
- VB/VBScript maintenu avec périmètre contrôlé ;
- plan de migration progressif vers une architecture plus saine.

## Pièges Courants (Common Pitfalls)

1. Déplacer dans le SCADA une logique qui devrait rester dans le PLC.
2. Faire des scripts longs et bloquants côté IHM.
3. Mélanger requêtes SQL, logique métier et UI sans séparation.
4. Laisser le legacy VBScript se multiplier sans gouvernance.
5. Construire des dashboards sans politique de nommage, logs et erreurs.

## Checklist de validation finale
- [ ] La frontière PLC / SCADA / backend est claire.
- [ ] Les requêtes et scripts sont dimensionnés pour l’environnement runtime.
- [ ] Les logiques critiques restent côté contrôle-commande.
- [ ] Les conventions de nommage, logs et gestion d’erreurs sont définies.
- [ ] Les écrans n’embarquent pas de logique métier trop lourde.
- [ ] Les accès SQL sont structurés et sécurisés.
