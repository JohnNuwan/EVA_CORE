---
name: ot-security-skill-map
description: "Utiliser quand il faut orienter rapidement vers la bonne skill OT security/cyber parmi audit, architecture, incident, gouvernance et conformité."
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [ot-security, iec62443, incident-response, audit, skill-map, governance]
    related_skills: [ot-security, cybersecurity-iec62443, ot-cybersecurity-audit-playbook, ot-incident-response, industrial-cybersecurity-guidelines, iso-27001]
---

# OT Security Skill Map

## Vue d'ensemble

Cette compétence joue le rôle d'index pour éviter les recouvrements entre plusieurs skills OT security déjà présentes. Elle ne remplace pas les skills détaillées ; elle oriente vers la bonne selon le besoin.

## Quand l'utiliser

À utiliser quand l'utilisateur demande « sécurité OT » de façon large ou ambiguë, ou quand plusieurs skills pourraient convenir.

## Carte d'orientation

- `cybersecurity-iec62443` : architecture de zones/conduits, hardening, niveaux de sécurité.
- `ot-cybersecurity-audit-playbook` : déroulé d'audit structuré avec preuves.
- `ot-incident-response` : traitement d'incident et confinement/remédiation.
- `ot-security` : vision de résilience OT plus générale.
- `industrial-cybersecurity-guidelines` : bonnes pratiques synthétiques et garde-fous.
- `iso-27001` : gouvernance SMSI et convergence IT/OT.

## Règle d'usage

Toujours expliciter :
1. le périmètre (machine, ligne, site, groupe),
2. le type de besoin (audit, architecture, incident, conformité),
3. le niveau de profondeur attendu.

## Pièges Courants (Common Pitfalls)

1. Répondre « sécurité OT » avec une seule vision trop générique.
2. Mélanger audit et remédiation sans distinguer les livrables.
3. Oublier la différence entre gouvernance ISO et architecture IEC 62443.

## Liste de vérification (Checklist)

- [ ] Le besoin est classé : audit / architecture / incident / gouvernance.
- [ ] La skill détaillée adaptée est identifiée.
- [ ] Le périmètre OT est explicité.
- [ ] Les livrables attendus sont distingués.
