---
name: industrial-python-jython-programming
description: "Structurer l’usage professionnel de Python et Jython en industrie pour intégration OT/IT, scripting SCADA, automatisation, génération et analytics."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, python, jython, ignition, scripting, automation, analytics, ot-it]
    related_skills: [ot-it-integration-languages, scada-hmi-programming-languages, scientific-computing-for-industry, scada-scripting-jython]
---

# Python et Jython en industrie

## Vue d'ensemble

Cette compétence couvre l’usage professionnel de Python et Jython en environnement industriel. Elle aide à décider quand utiliser Python moderne pour intégration, data, APIs, ETL, génération d’artefacts, tests, audits et services edge, et quand utiliser Jython dans un runtime SCADA comme Ignition pour scripting de supervision et automatisation côté JVM.

Le point clé est de ne jamais confondre :
- Python comme langage généraliste moderne d’intégration et de calcul ;
- Jython comme langage embarqué dans un runtime SCADA spécifique.

## Quand l'utiliser
- Choisir entre Python et Jython selon le runtime réel.
- Construire des outils OT/IT, ETL, parsers, APIs et reporting.
- Structurer des scripts Ignition gateway, Perspective ou Vision.
- Définir une trajectoire prototype → service outillé.
- Standardiser les usages Python d’équipe en environnement industriel.

À proscrire pour :
- Le contrôle temps réel dur ;
- les permissifs critiques qui doivent rester dans le PLC ;
- la data science moderne lourde dans un runtime Jython/Ignition.

## Positionnement professionnel

### Python
Usages typiques :
- ETL industriels ;
- passerelles OPC UA / Modbus / MQTT ;
- APIs ;
- reporting ;
- génération de code ;
- conversion L5X / XMY / CSV / JSON ;
- outils d’audit ;
- tests et qualification d’intégration.

Forces :
- écosystème énorme ;
- vitesse de développement ;
- bonne interopérabilité ;
- excellent pour outillage OT/IT et data légère à avancée.

### Jython
Usages typiques :
- scripts Ignition ;
- logique de supervision ;
- binding avancé ;
- reporting intégré ;
- automatisation côté gateway.

Forces :
- très utile dans son runtime JVM/SCADA ;
- permet d’automatiser proprement un environnement Ignition.

Limites :
- pas de pile Python moderne complète ;
- dépend du runtime SCADA ;
- à éviter pour architecture data/ML générale.

## Méthode de choix pas à pas

### Étape 1 — Identifier le runtime
- gateway SCADA Ignition ;
- serveur Linux/Windows ;
- edge PC ;
- backend API ;
- notebook d’analyse.

### Étape 2 — Classer l’usage
- script SCADA ;
- ETL ;
- API ;
- outillage qualité ;
- reporting ;
- analytics ;
- génération d’artefacts.

### Étape 3 — Choisir la bonne couche
- PLC : logique temps réel ;
- Jython : supervision et automatisation SCADA ;
- Python : intégration, data, APIs, services, outils.

### Étape 4 — Préparer l’industrialisation
Toujours décider :
- packaging ;
- logs ;
- gestion erreurs ;
- secrets ;
- tests ;
- supervision ;
- séparation config/code.

## Cas d’usage terrain

### Ignition + reporting + historian
- Jython pour scripts gateway et interaction SCADA ;
- SQL pour accès données ;
- Python externe si traitements plus lourds ou pipelines avancés.

### Outil de conversion multi-constructeurs
- Python prioritaire ;
- Jython non pertinent sauf exécution imposée dans Ignition.

### Agent edge industriel
- Python pertinent si environnement maîtrisé et besoin de delivery rapide ;
- sinon comparer à Go ou Rust.

## Pièges Courants (Common Pitfalls)

1. Essayer d’utiliser Jython comme un Python moderne généraliste.
2. Faire du Python industriel sans packaging, logs ni gestion d’erreurs.
3. Mettre des logiques critiques de contrôle temps réel dans le SCADA.
4. Écrire du code Ignition trop long et bloquant dans les événements UI.
5. Laisser des scripts Python devenir un “sac à scripts” sans architecture.

## Checklist de validation finale
- [ ] Le runtime cible est identifié.
- [ ] La frontière PLC / SCADA / backend est claire.
- [ ] Le niveau d’industrialisation Python attendu est défini.
- [ ] Les limitations Jython sont comprises.
- [ ] Les logs, erreurs, secrets et packaging sont traités.
- [ ] Les scripts SCADA ne portent pas de logique temps réel critique.
