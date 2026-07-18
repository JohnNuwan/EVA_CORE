---
name: multi-constructor-standard-library
description: "Standardiser des patterns automates multi-constructeurs pour moteurs, vannes, analogiques et échanges SCADA."
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [plc, standard-library, multi-constructor, motor, valve, analog, scada, reusable-patterns]
    related_skills: [industrial-generator, siemens-scl, rockwell-studio5000, schneider-unity, beckhoff-twincat, wago-codesys]
---

# Bibliothèque standard multi-constructeurs

## Vue d'ensemble

Cette compétence définit une bibliothèque logique transverse pour standardiser les objets d'automatisation au-delà des marques. Elle fournit des patterns communs pour moteurs, vannes, analogiques, séquenceurs et échanges PLC ↔ SCADA, puis aide à les décliner par constructeur.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Créer une bibliothèque standard multi-marques.
- Définir des patterns réutilisables moteurs, vannes, analogiques.
- Uniformiser les échanges PLC ↔ SCADA.
- Préparer une base commune Siemens / Rockwell / Beckhoff / Omron / Schneider / WAGO / etc.

## 1. Objets standards recommandés

- `MotorStandard`
- `ValveStandard`
- `AnalogStandard`
- `SequenceStandard`
- `AlarmStandard`
- `ExchangeStandard`

## 2. Contrat minimal par objet

### MotorStandard
- Cmd.Start
- Cmd.Stop
- Cmd.Reset
- Sts.Run
- Sts.Ready
- Sts.Fault
- Sts.Local
- Alm.Summary

### ValveStandard
- Cmd.Open
- Cmd.Close
- Sts.Opened
- Sts.Closed
- Sts.Moving
- Sts.Fault

### AnalogStandard
- RawValue
- Pv
- Sp
- Unit
- Fault
- HiAlarm
- LoAlarm

## 3. Règles de déclinaison par constructeur

- Garder le même sens fonctionnel, même si la syntaxe change.
- Isoler les détails constructeur dans une couche d'adaptation.
- Exposer au SCADA une structure stable, jamais des détails internes instables.
- Documenter les équivalences tag/UDT/FB/AOI/DFB par plateforme.

## 4. Pattern PLC ↔ SCADA

Le SCADA doit consommer un modèle stable :
- commandes montantes dédiées ;
- états synthétiques ;
- alarmes résumées ;
- analogiques normalisés ;
- qualité/diagnostic clairement exposés.

## 5. Utilisation pratique

- créer un objet standard de référence ;
- définir sa structure métier ;
- produire ensuite une implémentation Siemens, Rockwell, Beckhoff, etc. ;
- conserver un mapping documentaire unique.

## Pièges Courants (Common Pitfalls)

1. Créer des bibliothèques différentes par marque sans noyau commun.
2. Exposer au SCADA des détails internes différents selon chaque plateforme.
3. Mélanger contrat métier et implémentation constructeur.
4. Oublier de documenter les équivalences de champs.

## Liste de vérification (Checklist)

- [ ] Un contrat standard transverse est défini avant l'implémentation constructeur.
- [ ] Les objets moteurs, vannes, analogiques et séquenceurs ont chacun leur pattern.
- [ ] Le SCADA consomme un modèle stable multi-marques.
- [ ] Les détails constructeur sont isolés dans une couche d'adaptation.
- [ ] Le mapping entre plateformes est documenté.
