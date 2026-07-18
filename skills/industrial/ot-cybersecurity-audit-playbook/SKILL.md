---
name: ot-cybersecurity-audit-playbook
description: "Auditer un système OT par étapes : inventaire, segmentation, accès distants, durcissement, sauvegardes et preuves de conformité."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [industrial, cybersecurity, ot, audit, iec-62443, iso-27001, hardening]
    related_skills: [cybersecurity-iec62443, iso-27001, multi-sector-industrial-standards, ot-security-skill-map]
---

# Playbook d'audit cybersécurité OT

## Vue d'ensemble

Cette compétence structure un audit OT en séquences opérables : cadrage, inventaire, analyse de flux, segmentation, accès distants, durcissement, sauvegardes, réponse à incident et preuves documentaires. Elle sert à produire un audit exploitable, pas seulement une liste de recommandations génériques.

## Quand l'utiliser

À utiliser pour :
- préparer un audit IEC 62443 ou ISO 27001 orienté OT ;
- construire une feuille de route de remédiation cybersécurité usine ;
- structurer une campagne d'inventaire et de segmentation ;
- évaluer le niveau de maîtrise d'un site industriel.

Ne pas utiliser pour :
- une réponse à incident temps réel déjà engagé sans pilotage de crise ;
- un audit IT pur sans actifs OT ;
- un scan agressif sans cadre d'autorisation et sans analyse de risque.

## Étapes d'audit

1. Inventaire des actifs.
2. Cartographie réseau et flux.
3. Contrôle accès et comptes.
4. Durcissement et mots de passe par défaut.
5. Sauvegardes et restauration.
6. Accès distants et MFA.
7. Journalisation, détection, réponse à incident.
8. Preuves documentaires et priorisation des écarts.

## Livrables attendus

- registre d'actifs ;
- matrice flux / zones / conduits ;
- synthèse accès distants et comptes sensibles ;
- état des sauvegardes et tests de restauration ;
- registre d'écarts priorisés avec preuves.

## Support files

- `templates/ot-audit-checklist.md` : checklist d'audit terrain.
- `references/audit-plan-template.md` : plan type de campagne d'audit.

## Pièges Courants (Common Pitfalls)

1. Scanner trop agressivement le réseau OT.
2. Oublier les accès prestataires et laptops maintenance.
3. Confondre preuves documentaires et réalité terrain.
4. Produire des écarts sans priorisation ni justification métier.

## Liste de vérification (Checklist)

- [ ] Inventaire réalisé.
- [ ] Flux documentés.
- [ ] Comptes par défaut éliminés.
- [ ] Sauvegardes testées.
- [ ] Accès distants sécurisés.
- [ ] Les écarts sont priorisés avec preuves.
