---
name: siemens-safety
description: "Programmer et structurer les fonctions de sécurité Siemens Safety Integrated sous TIA Portal."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [siemens, safety, safety-integrated, tia-portal, failsafe, pl, sil]
    related_skills: [industrial-safety-sistema, siemens-scl, functional-safety-iec61511]
---

# Siemens Safety Integrated

## Vue d'ensemble

Cette compétence couvre les architectures de sécurité Siemens dans TIA Portal avec Safety Integrated. Elle aide à structurer les fonctions failsafe, les réarmements, interverrouillages, EDM et échanges sûrs entre logique de sécurité, motion et logique standard.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- structurer une logique safety Siemens ;
- définir des fonctions d'arrêt d'urgence, porte, reset et permissifs sûrs ;
- séparer logique standard et logique failsafe ;
- préparer une validation safety cohérente avec l'architecture TIA.

Ne pas utiliser pour :
- une simple logique automate sans exigence de sécurité ;
- une étude SIL procédés sans architecture machine ;
- une correction locale sans enjeu de standardisation safety.

## Axes de structuration

1. Isoler clairement la logique failsafe.
2. Centraliser reset, EDM, acquittements et interlocks sûrs.
3. Définir explicitement les transitions après défaut sécurité.
4. Documenter le lien entre safety, motion et séquence machine.
5. Préparer les preuves de validation FAT/SAT et de calcul PL/SIL.

## Livrables attendus

- cartographie des fonctions de sécurité ;
- contrat safety ↔ standard ;
- stratégie de reset et d'acquittement ;
- réactions machine après défaut safety ;
- check-list de validation terrain.

## Support files

- `templates/safety-function-template.md` : gabarit de fonction safety.
- `references/expert-pack.md` : points d'attention détaillés.
- `references/fat-sat-checklist.md` : validation terrain minimale.

## Pièges Courants (Common Pitfalls)

1. Mélanger safety et logique standard sans frontière claire.
2. Réarmement mal défini ou ambigu.
3. Défaut de cohérence entre safety et état machine.
4. Validation terrain insuffisante des chaînes d'arrêt.

## Liste de vérification (Checklist)

- [ ] La frontière safety / standard est claire.
- [ ] Les fonctions de reset et EDM sont documentées.
- [ ] Les réactions machine après défaut sécurité sont définies.
- [ ] Le lien avec PL/SIL demandé est pris en compte.
- [ ] La validation terrain est explicitée.
