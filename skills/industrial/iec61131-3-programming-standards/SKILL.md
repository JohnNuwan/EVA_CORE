---
name: iec61131-3-programming-standards
description: "Concevoir, comparer et standardiser les langages IEC 61131-3 (ST, LD, FBD, SFC) et leurs variantes constructeurs pour automates industriels."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, iec61131-3, structured-text, ladder, fbd, sfc, plc, codesys, tia, logix]
    related_skills: [siemens-scl, rockwell-studio5000, schneider-unity, beckhoff-twincat, omron-sysmac, plcopen-xml]
---

# Langages IEC 61131-3

## Vue d'ensemble

Cette compétence structure un usage professionnel des langages IEC 61131-3 : Structured Text (ST), Ladder Diagram (LD), Function Block Diagram (FBD) et Sequential Function Chart (SFC). Elle aide à choisir le bon langage selon la logique métier, la maintenabilité, la lisibilité atelier et la portabilité multi-constructeurs.

## Quand l'utiliser
- Définir un standard de programmation automate.
- Choisir entre ST, Ladder, FBD ou SFC/GRAPH.
- Traduire une logique d’un constructeur vers un autre.
- Construire une bibliothèque standard multi-PLC.

## Guide de sélection rapide
- ST : calculs, tableaux, traitements de données, états, algorithmes.
- LD : maintenance terrain, interverrouillages simples, lisibilité électrotechnicien.
- FBD : chaînes fonctionnelles, analogiques, régulation, signaux continus.
- SFC : séquences machine, pas/transition, batch, démarrage/arrêt ordonné.

## Variantes constructeurs fréquentes
- Siemens : SCL / LAD / FBD / GRAPH
- Rockwell : ST / Ladder / FBD / AOI
- Schneider : ST / DFB / Ladder
- Beckhoff / WAGO / CODESYS : ST / LD / FBD / SFC
- Omron : ST / Ladder / motion blocks
- Mitsubishi / B&R / PLCnext : variantes IEC + extensions constructeur

## Méthode professionnelle
1. Définir le contrat de données (UDT/DDT/structures).
2. Séparer I/O, logique d’équipement, séquences, alarmes et supervision.
3. Choisir le langage par fonction, pas par habitude historique.
4. Normaliser les patterns (motor, valve, analog, sequence, alarm).
5. Préparer export/import via PLCopen XML quand pertinent.

## Pièges Courants (Common Pitfalls)
1. Faire des séquenceurs complexes en Ladder seul.
2. Mettre toute la logique métier en FBD par habitude outil.
3. Perdre la maintenabilité en mélangeant styles et conventions.

## Liste de vérification (Checklist)
- [ ] Le langage est choisi selon la nature de la logique.
- [ ] Les structures de données sont standardisées.
- [ ] La séparation I/O / logique / séquence / alarmes est explicite.
- [ ] La portabilité multi-constructeurs est évaluée.
