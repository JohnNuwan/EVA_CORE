---
name: industrial-programming-languages
description: "Structurer, comparer et sélectionner les langages de programmation rencontrés en industrie : automates, SCADA/HMI, robotique, OT/IT, calcul scientifique et formats d’échange."
version: 2.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [industrial, programming-languages, iec61131-3, scada, hmi, robot, python, julia, rust, jax, sql, plcopen]
    related_skills: [iec61131-3-programming-standards, scada-hmi-programming-languages, ot-it-integration-languages, scientific-computing-for-industry, robot-programming-languages, industrial-exchange-formats]
---

# Langages de programmation industriels

## Vue d'ensemble

Cette compétence sert de portail professionnel pour cartographier, comparer et sélectionner les langages de programmation réellement rencontrés en industrie. Elle couvre les couches suivantes : automate, robot, supervision, intégration OT/IT, calcul scientifique, formats d’échange et contrats métier.

L’objectif n’est pas de faire un inventaire académique. L’objectif est d’aider à choisir le bon langage selon le runtime réel, la criticité du système, la maintenabilité atelier, la portabilité multi-constructeurs, la profondeur de calcul attendue et la trajectoire de vie du code.

## Quand l'utiliser
- Choisir une famille de langages pour un nouveau projet industriel.
- Arbitrer entre logique PLC, robot, SCADA, edge, backend ou notebook scientifique.
- Définir un standard logiciel multi-couches pour une usine, une machine ou une plateforme.
- Préparer une montée en compétence équipe ou une feuille de route d’industrialisation.
- Évaluer quels langages doivent rester propriétaires constructeur et lesquels doivent être transverses.

À proscrire pour :
- La rédaction d’un code très spécifique à un constructeur sans analyse transverse préalable : charger ensuite la skill dédiée.
- La simple conversion syntaxique entre deux outils sans réflexion d’architecture.

## Grands blocs de langages en industrie

### 1. Contrôle-commande temps réel
- IEC 61131-3 : ST, LD, FBD, SFC.
- variantes constructeurs : SCL, GRAPH, AOI, DFB, blocs motion, bibliothèques sécurité.
- enjeu principal : déterminisme, lisibilité maintenance, portabilité partielle.

### 2. Robotique
- RAPID, TP, Karel, KRL, VAL 3.
- enjeu principal : trajectoires, outils/repères, recovery, communication PLC, architecture cellule.

### 3. SCADA / HMI / reporting
- Jython, SQL, JavaScript/TypeScript, VB/VBScript legacy, expressions de binding.
- enjeu principal : séparation UI / données / logique / historisation.

### 4. OT / IT intégration
- Python, C#, Java, Go, Rust, Bash, PowerShell, SQL, APIs.
- enjeu principal : connectivité, services, ETL, gateways, edge, logs, sécurité, observabilité.

### 5. Calcul scientifique / optimisation / data industrielle
- Python, NumPy, Pandas, Jupyter, Julia, JAX, Cython, Rust.
- enjeu principal : simulation, estimation, optimisation, IA, jumeaux numériques, industrialisation de prototypes.

### 6. Formats d’échange et contrats métier
- PLCopen XML, L5X, XMY/XML, JSON métier, CSV SCADA, OPC UA models.
- enjeu principal : standardisation, génération, migration, sémantique, interopérabilité.

## Critères de choix professionnels

### Critère 1 — Où s’exécute le code ?
- PLC : IEC 61131-3 et variantes constructeur.
- Robot : langage propriétaire constructeur.
- SCADA : runtime scripting HMI/SCADA.
- Edge / serveur : langage OT/IT généraliste.
- Notebook / labo : langage de prototypage scientifique.

### Critère 2 — Quel est le niveau de criticité ?
- critique temps réel : PLC/robot.
- important mais non déterministe : SCADA / gateway.
- analytique / optimisation : Python, Julia, JAX, etc.

### Critère 3 — Qui maintient ?
- automaticien terrain ;
- roboticien ;
- intégrateur SCADA ;
- développeur OT/IT ;
- data scientist / ingénieur optimisation.

### Critère 4 — Quelle trajectoire de vie ?
- prototype court ;
- standard machine ;
- plateforme groupe ;
- outil d’audit ;
- composant produit long terme.

## Grille de décision macro

| Couche | Langages prioritaires | Motif principal |
|---|---|---|
| PLC | ST / LD / FBD / SFC | déterminisme et maintenabilité machine |
| Robot | RAPID / TP / KRL / VAL 3 / Karel | runtime constructeur et trajectoires |
| SCADA/HMI | Jython / SQL / JS / VBScript | supervision, data, UI, reporting |
| OT/IT | Python / C# / Java / Go / Rust / SQL | intégration, services, APIs, edge |
| Calcul scientifique | Python / Julia / JAX / Cython / Rust | simulation, optimisation, performance |
| Échange | PLCopen XML / L5X / XMY / JSON / CSV / OPC UA | portabilité, standardisation, génération |

## Architecture professionnelle recommandée

### Principe 1 — Le bon langage au bon niveau
- PLC : logique déterministe, états critiques, permissifs, sécurité liée process.
- Robot : trajectoire, cinématique, outillage, états robot internes.
- SCADA : visualisation, reporting, workflows opérateur, historisation légère.
- OT/IT : intégrations, ETL, APIs, gateways, services, consolidation.
- Data/science : simulation, calibration, optimisation, prévision, analyse.

### Principe 2 — Contrats d’interface explicites
Entre couches, toujours définir :
- structures de données ;
- tags / points exposés ;
- états standardisés ;
- mapping alarmes ;
- événements ;
- contrats API / messages ;
- versionnement.

### Principe 3 — Pas de dilution des responsabilités
- ne pas déplacer une logique temps réel critique dans le SCADA ;
- ne pas transformer un notebook d’étude en service de production sans redesign ;
- ne pas faire d’un format constructeur un standard transverse par erreur.

## Cas d’usage typiques

### Machine unitaire
- PLC : ST + Ladder.
- Robot éventuel : langage constructeur.
- HMI locale : logique minimale de supervision.
- Pas besoin immédiat de Julia/JAX/Rust sauf besoin spécifique.

### Ligne de production connectée
- PLC standards multi-équipements.
- SCADA : Jython + SQL + reporting.
- Backend : Python/C#/Java/Go.
- Contrat JSON métier et formats d’échange versionnés.

### Projet d’optimisation avancée
- acquisition OT/IT : Python/Go/Rust.
- exploration : Python/Jupyter.
- optimisation lourde : Julia ou JAX selon besoin.
- accélération ciblée : Cython ou Rust si goulot confirmé.

## Pièges Courants (Common Pitfalls)

1. Choisir un langage généraliste pour un problème qui demande du déterminisme PLC ou un runtime constructeur.
2. Multiplier les langages sans standard d’architecture ni règles d’interface.
3. Confondre format d’échange et langage d’exécution.
4. Remonter trop de logique de terrain dans les couches SCADA ou backend.
5. Croire qu’un prototype Python/Jupyter est déjà un livrable industriel exploitable.
6. Choisir Julia, JAX, Cython ou Rust sans analyse du vrai goulet de performance.

## Checklist de validation finale
- [ ] La couche d’exécution réelle est identifiée.
- [ ] Les contraintes de temps réel sont explicitées.
- [ ] Le profil des mainteneurs est connu.
- [ ] Les interfaces inter-couches sont documentées.
- [ ] Le niveau de portabilité attendu est défini.
- [ ] Le plan prototype → standard → production est clarifié.
- [ ] Les formats d’échange et contrats métier sont versionnés.
- [ ] Le choix technologique est justifié par usage, pas par mode ou préférence personnelle.
