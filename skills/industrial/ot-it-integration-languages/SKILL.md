---
name: ot-it-integration-languages
description: "Structurer les langages d’intégration OT/IT utilisés en industrie : Python, C#, Java, Go, Rust, Bash, PowerShell, SQL et APIs."
version: 2.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [industrial, integration, python, csharp, java, go, rust, bash, powershell, sql, api]
    related_skills: [industrial-programming-languages, industrial-protocols, industrial-databases, mes-integration]
---

# Langages d’intégration OT / IT

## Vue d'ensemble

Cette compétence couvre les langages généralistes réellement utilisés pour relier le monde industriel à l’IT : Python, C#, Java, Go, Rust, Bash, PowerShell, SQL et la logique API/JSON. Elle aide à choisir le bon langage selon le service à construire : gateway, ETL, API, audit, conversion d’exports PLC, edge agent, synchronisation SCADA/MES/ERP, reporting ou maintenance automatisée.

Le but n’est pas de comparer des langages en théorie, mais de déterminer quel compromis industriel est le plus solide entre vitesse de développement, robustesse, déploiement, observabilité, sécurité et coût de maintenance.

## Quand l'utiliser
- Construire des passerelles PLC ↔ MES/ERP.
- Écrire des outils d’audit, migration, qualification ou génération de code.
- Choisir un langage pour une application edge industrielle.
- Définir une pile d’intégration OT/IT pérenne.
- Répartir les responsabilités entre scripts, services, bases et APIs.

## Familles et positionnement professionnel

### Python
Usages typiques :
- ETL industriels ;
- APIs rapides ;
- parsers d’exports L5X/XMY/CSV/JSON ;
- outils d’audit ;
- génération de code ;
- passerelles OPC UA / MQTT / Modbus ;
- analytics légers.

Forces :
- vitesse de développement ;
- écosystème énorme ;
- très bon pour prototypage et industrialisation légère.

Limites :
- performance CPU pure ;
- packaging parfois fragile si mal géré ;
- scripts vite incontrôlables sans discipline architecture.

### C#
Usages typiques :
- intégration Windows ;
- services usine sous .NET ;
- HMIs/outils desktop ;
- interfaçage avec environnements Microsoft et certains stacks OPC UA .NET.

Forces :
- excellente intégration entreprise Windows ;
- bonne maintenabilité ;
- outillage mature.

### Java
Usages typiques :
- middleware industriels ;
- services JVM historiques ;
- stacks de supervision ou backends déjà existants en Java.

Forces :
- robustesse ;
- écosystème entreprise ;
- portabilité mature.

### Go
Usages typiques :
- agents ;
- microservices ;
- outils réseau ;
- services distribués à faible empreinte.

Forces :
- binaire simple à déployer ;
- concurrence lisible ;
- très bon pour agents et services d’usine.

### Rust
Usages typiques :
- agents critiques ;
- parsers performants ;
- bibliothèques robustes ;
- composants nécessitant sûreté mémoire et performance.

Forces :
- sûreté mémoire ;
- très bonne performance ;
- excellent candidat pour composants sensibles et durables.

Limites :
- courbe d’apprentissage ;
- surcoût si l’équipe n’est pas prête.

### Bash / PowerShell
Usages typiques :
- automatisation système ;
- installation ;
- packaging ;
- déclenchement de jobs ;
- maintenance récurrente.

Règle :
- utile pour l’orchestration simple ;
- à éviter comme couche métier principale d’un système critique.

### SQL
Usages typiques :
- historian ;
- reporting ;
- traçabilité ;
- OEE ;
- agrégations ;
- vues de contrôle qualité.

Règle :
- SQL est un langage cœur en industrie dès qu’il y a MES, historian, traçabilité ou reporting.

## Méthode de choix pas à pas

### Étape 1 — Classer le service
Demander si le besoin est :
- script ponctuel ;
- ETL ;
- API ;
- agent edge ;
- batch ;
- outil d’audit ;
- service durable.

### Étape 2 — Identifier le runtime cible
- Windows atelier ;
- Linux edge ;
- serveur data center ;
- conteneur ;
- poste maintenance ;
- jump host.

### Étape 3 — Définir la contrainte dominante
- temps de dev ;
- déploiement ;
- performance ;
- sécurité ;
- maintenabilité locale ;
- interop Windows ;
- footprint mémoire ;
- disponibilité 24/7.

### Étape 4 — Séparer scripts et services
Décider explicitement :
- ce qui reste script d’exploitation ;
- ce qui devient service versionné ;
- ce qui mérite tests, logs, supervision, packaging, secrets management.

## Cas d’usage terrain

### Outil d’audit d’actifs OT
- Python ou Go en priorité.
- Rust si exigence forte de robustesse et diffusion long terme.

### Passerelle SCADA ↔ MES
- Python, C# ou Java selon SI existant.
- SQL comme couche de requête et de persistance.

### Agent edge léger multi-sites
- Go ou Rust très pertinents.
- Python si vitesse de delivery prime et environnement maîtrisé.

### Outil interne Windows atelier
- C# souvent très bon choix.
- PowerShell possible si le besoin reste purement système.

## Pièges Courants (Common Pitfalls)

1. Choisir un langage sans considérer OS cible, runtime et maintenance locale.
2. Mettre trop de logique métier dans des scripts système fragiles.
3. Négliger la sécurité des échanges, des secrets et des logs.
4. Faire de Python un “sac à scripts” sans structure de packaging.
5. Utiliser Rust ou Go sans besoin réel juste pour suivre une mode technique.
6. Oublier l’observabilité : logs, métriques, alertes, retries, timeout, reprise.

## Checklist de validation finale
- [ ] L’environnement cible est identifié.
- [ ] Le type de service est classé.
- [ ] Le langage est choisi selon la contrainte dominante.
- [ ] Les secrets, logs, erreurs et métriques sont prévus.
- [ ] Les interfaces OT/IT sont documentées.
- [ ] Le mode de déploiement et de mise à jour est défini.
- [ ] La maintenance locale par l’équipe cible est réaliste.
