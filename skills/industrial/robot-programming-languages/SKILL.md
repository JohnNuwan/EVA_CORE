---
name: robot-programming-languages
description: "Structurer les langages de programmation robot rencontrés en industrie : RAPID, TP, Karel, KRL, VAL 3 et leurs usages professionnels."
version: 2.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [industrial, robotics, programming-languages, rapid, tp, karel, krl, val3]
    related_skills: [industrial-programming-languages, robotics-abb, robotics-fanuc, robotics-kuka, robotics-staubli, robot-plc-standard-interface]
---

# Langages de programmation robot industriels

## Vue d'ensemble

Cette compétence couvre les langages de programmation robot réellement rencontrés en industrie : ABB RAPID, Fanuc TP, Fanuc Karel, KUKA KRL, Stäubli VAL 3. Elle sert à choisir le bon niveau d’implémentation entre trajectoire, logique de cellule, services annexes, communications, diagnostics et standardisation robot ↔ PLC.

Le but n’est pas de lister des syntaxes, mais de raisonner comme un intégrateur robotique professionnel : quel langage porte la trajectoire, lequel porte les services, où placer la logique de recovery, comment limiter la dépendance à un constructeur, et comment organiser la cellule pour qu’elle reste maintenable après mise en service.

## Quand l'utiliser
- Choisir un langage robot selon le constructeur et le besoin.
- Structurer une architecture robot trajectoire / logique / services.
- Standardiser les patterns pick/place, home, recovery, défauts et handshake PLC.
- Préparer des migrations ou comparaisons multi-constructeurs.
- Définir ce qui doit vivre dans le robot, dans le PLC ou dans le SCADA.

À proscrire pour :
- Les seules interfaces robot ↔ automate sans travail sur les langages eux-mêmes : utiliser `robot-plc-standard-interface`.
- La seule analyse de sécurité cellule : utiliser `robot-safety-cell-design`.

## Positionnement détaillé des langages

### RAPID (ABB)
Usages typiques :
- trajectoires ;
- gestion d’outils/repères ;
- structuration modules ;
- multitâche ;
- intégration RobotStudio.

Forces :
- langage structuré et riche ;
- très bon pour architectures propres ;
- bonne séparation données / procédures.

### TP (Fanuc)
Usages typiques :
- trajectoires ;
- logique séquentielle de terrain ;
- mise au point atelier ;
- interventions directes opérateur/maintenance.

Forces :
- très lisible côté terrain Fanuc ;
- très adapté aux séquences robot simples et robustes.

Limites :
- moins adapté aux services complexes ou à la logique logicielle plus riche.

### Karel (Fanuc)
Usages typiques :
- fichiers ;
- calculs ;
- communications ;
- traitements plus structurés ;
- services arrière-plan.

Forces :
- complète TP pour les besoins hors trajectoire.

### KRL (KUKA)
Usages typiques :
- trajectoires PTP/LIN ;
- logique système ;
- interaction avec SPS.SUB ;
- architecture WorkVisual.

Forces :
- fort niveau de contrôle ;
- bonne articulation entre programme robot et logique système.

### VAL 3 (Stäubli)
Usages typiques :
- mouvements ;
- structuration modulaire ;
- tâches asynchrones ;
- intégration cellule.

Forces :
- bonne expressivité ;
- architecture modulaire claire.

## Critères de choix professionnels

### Critère 1 — Nature du besoin
- trajectoire pure ;
- logique applicative ;
- services de communication ;
- fichiers / reporting / diagnostics ;
- recovery et orchestration cellule.

### Critère 2 — Runtime réel
- contrôleur robot ;
- tâche de fond ;
- interaction PLC ;
- intégration offline engineering.

### Critère 3 — Qui maintient ?
- roboticien expert ;
- metteur au point terrain ;
- maintenance ;
- automaticien cellule.

### Critère 4 — Positionnement des responsabilités
- trajectoire dans le robot ;
- orchestration de cellule partagée avec le PLC ;
- supervision dans SCADA ;
- services externes en OT/IT si besoin.

## Architecture professionnelle recommandée

### Principe 1 — Séparer trajectoire et orchestration
- Le robot gère au plus près : positions, outils, trajectoires, états internes, défauts natifs.
- Le PLC gère : cycle global, permissifs externes, synchronisation machine, interverrouillages inter-équipements.
- Le SCADA/HMI gère : visualisation, recette, diagnostics haut niveau, reporting.

### Principe 2 — Standardiser les états externes
Quel que soit le langage constructeur, exposer au PLC un contrat homogène :
- Ready
- Busy
- CycleDone
- Fault
- AtHome
- InAuto
- InTeach
- ResetRequired

### Principe 3 — Ne pas surcharger le robot avec la logique usine entière
Beaucoup de cellules deviennent illisibles parce que :
- la logique process est remontée dans le robot ;
- les recovery ne sont pas standardisés ;
- le PLC n’a plus la main sur l’orchestration globale.

## Cas d’usage terrain

### Cellule pick & place standard
- langage de trajectoire prioritaire ;
- logique de cycle globale dans le PLC ;
- recovery partagé robot/PLC.

### Cellule avec services fichiers/communications
- trajectoire dans RAPID/TP/KRL/VAL 3 ;
- services complémentaires via Karel ou fonctions natives constructeur ;
- attention à ne pas mélanger trajectoire et middleware sans structure.

### Cellule multi-robots
- standardisation des états et défauts impérative ;
- langage constructeur inchangé, mais contrat externe unifié.

## Pièges Courants (Common Pitfalls)

1. Mettre trop de logique cellule dans le robot au lieu de la partager proprement avec le PLC.
2. Confondre langage de trajectoire et langage de service/communication.
3. Négliger la standardisation des états Home/Busy/Done/Fault entre marques.
4. Faire des recoveries dépendants d’opérations manuelles non documentées.
5. Laisser des repères/outils/positions sans gouvernance claire.

## Checklist de validation finale
- [ ] Le besoin est classé : trajectoire, logique cellule, services, communication.
- [ ] Le langage choisi correspond au runtime constructeur.
- [ ] Les interfaces robot ↔ PLC sont standardisées.
- [ ] Les responsabilités robot / PLC / SCADA sont définies.
- [ ] Les procédures de recovery et de défaut sont définies.
- [ ] Les outils, repères et états externes sont gouvernés proprement.
