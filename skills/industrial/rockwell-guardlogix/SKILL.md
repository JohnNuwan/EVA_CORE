---
name: rockwell-guardlogix
description: "Structurer les fonctions de sécurité Rockwell GuardLogix et les échanges sûrs avec la logique standard."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [rockwell, guardlogix, safety, logix, pl, sil, machine-safety]
    related_skills: [industrial-safety-sistema, rockwell-studio5000, functional-safety-iec61511]
---

# Rockwell GuardLogix

## Vue d'ensemble

Cette compétence couvre la structuration des fonctions de sécurité Rockwell GuardLogix et leur articulation avec la logique standard Logix. Elle aide à concevoir des arrêts sûrs, permissifs, resets, états de reprise et contrats clairs entre safety, motion et comportement machine.

## Quand l'utiliser

À utiliser pour :
- concevoir des fonctions safety Allen-Bradley ;
- séparer logique safety et logique standard ;
- formaliser E-stop, guard doors, resets et permissifs sûrs ;
- documenter le comportement machine post-défaut safety.

Ne pas utiliser pour :
- une logique machine non safety ;
- un simple besoin Studio 5000 sans composant sécurité ;
- une étude SIL/PL purement documentaire sans logique machine concrète.

## Axes de structuration

1. Séparer données safety et données standard.
2. Centraliser resets, acquittements et interverrouillages sûrs.
3. Définir les réactions machine après défaut ou perte de condition sûre.
4. Garder un mapping clair vers HMI, maintenance et supervision.
5. Préparer la validation terrain et les preuves de conformité.

## Livrables attendus

- cartographie fonctions safety ;
- matrice permissifs / resets / défauts ;
- contrat safety ↔ standard ;
- logique de reprise après défaut ;
- check-list FAT/SAT safety.

## Support files

- `templates/safety-function-template.md` : gabarit de fonction safety.
- `references/expert-pack.md` : points d'attention détaillés GuardLogix.

## Pièges Courants (Common Pitfalls)

1. Mélanger états safety et états standard sans contrat clair.
2. Réarmement mal séquencé.
3. Sortie de défaut non cohérente avec le comportement machine.
4. Sous-documenter la validation terrain des chaînes safety.

## Liste de vérification (Checklist)

- [ ] La logique safety est isolée.
- [ ] Les resets sont explicites.
- [ ] Les réactions machine sont documentées.
- [ ] Le lien avec PL/SIL est pris en compte.
- [ ] La validation safety terrain est prévue.
