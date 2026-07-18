---
name: br-automation-studio
description: "Programmer sous B&R Automation Studio avec motion, safety et visualisation intégrés."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [br, b-and-r, automation-studio, motion, safety, mapp, visualization, st-oop, machine-oem]
    related_skills: [drive-motion-control, industrial-safety-sistema, plcopen-xml, industrial-protocols]
---

# B&R Automation Studio

## Vue d'ensemble

Cette compétence couvre B&R Automation Studio comme environnement unifié pour le contrôle, le motion, la safety, la méchatronique et la visualisation. Elle est adaptée aux machines OEM à haute performance et aux architectures modulaires où il faut garder une forte cohérence entre axes, sécurité, IHM et logique machine.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Structurer un projet B&R sous Automation Studio.
- Programmer une machine avec forte composante motion.
- Intégrer safety, visualisation et logique dans le même environnement.
- Concevoir une architecture OEM modulaire.

## Architecture recommandée

- Blocs équipements.
- Blocs axes / motion.
- Couche safety.
- Couche HMI/visualisation.
- Couche paramètres/recettes.
- Couche diagnostic unifiée.

## Bonnes pratiques

- Modulariser fortement le projet.
- Séparer clairement orchestration machine, commande axe et diagnostic axe.
- Éviter que la visualisation reconstruise la logique machine.
- Concevoir motion et safety ensemble dès l'architecture.

## Cas d'usage typiques

- Lignes d'emballage.
- Machines rapides synchronisées.
- Cellules multi-axes.
- Equipements OEM avec HMI unifiée.

## Pièges Courants (Common Pitfalls)

1. Projet trop monolithique, peu réutilisable.
2. Motion et safety conçus séparément.
3. HMI qui duplique les états machine.
4. Sous-utilisation de la dimension plateforme intégrée d'Automation Studio.

## Liste de vérification (Checklist)

- [ ] Le projet est modulaire et réutilisable.
- [ ] Les couches motion, safety et visualisation sont séparées mais cohérentes.
- [ ] Les axes ont des états, diagnostics et séquences définis.
- [ ] La visualisation consomme des états synthétiques.
- [ ] Les fonctions safety sont documentées avec leurs effets machine.
- [ ] Les standards OEM/bibliothèques sont identifiés.
