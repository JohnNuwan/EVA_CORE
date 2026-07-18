---
name: plc-backup-versioning-recovery
description: "Utiliser quand l'utilisateur doit structurer sauvegarde, versionning, golden copy, restauration et reprise après incident pour automates, HMIs et SCADA."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [backup, versioning, recovery, plc, scada, hmi, disaster-recovery, golden-copy]
    related_skills: [iso-quality, industrial-cybersecurity-guidelines, industrial-maintenance-reliability]
---

# PLC Backup Versioning Recovery

## Vue d'ensemble

Cette compétence structure la gouvernance des sauvegardes et restaurations en environnement OT : golden copy, périodicité, preuves de restauration, écarts online/offline, et reprise après incident ou corruption projet.

## Quand l'utiliser

À utiliser pour :
- définir une stratégie de sauvegarde automates/HMI/SCADA ;
- préparer un PRA/PCA OT ;
- organiser le versionning des projets de contrôle ;
- formaliser les tests de restauration.

Ne pas utiliser pour :
- une simple copie manuelle non gouvernée ;
- un dépôt Git sans politique de restauration ;
- un besoin purement documentaire sans actifs réels à protéger.

## Axes de gouvernance

1. Sauvegarde projet offline.
2. Sauvegarde online / upload depuis équipement si possible.
3. Golden copy validée.
4. Journal de versions et écarts.
5. Test périodique de restauration.

## Support files

- `references/recovery-governance-matrix.md` : matrice minimale pour gouverner golden copy, preuves et restauration effective.

## Pièges Courants (Common Pitfalls)

1. Conserver des archives sans test réel de restauration.
2. Mélanger versions projet et versions déployées sans traçabilité.
3. Sauvegarder le PLC mais oublier HMI, recettes, historiques ou paramètres drive.
4. Oublier les preuves d'intégrité et la localisation des sauvegardes.

## Liste de vérification (Checklist)

- [ ] Les actifs OT critiques à sauvegarder sont listés.
- [ ] Une golden copy est identifiée.
- [ ] Les versions offline/online sont comparées.
- [ ] Un test de restauration est planifié.
- [ ] Les preuves de sauvegarde et restauration sont archivées.
