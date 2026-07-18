---
name: pilz-safety
description: "Concevoir et documenter les architectures de sécurité machine de type Pilz et leurs fonctions opératoires."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [pilz, safety, machine-safety, pl, sil, reset, interlock]
    related_skills: [industrial-safety-sistema, functional-safety-iec61511, iso-safety]
---

# Pilz Safety

## Vue d'ensemble

Cette compétence couvre la structuration d'architectures safety typées Pilz et plus largement les dispositifs dédiés sécurité machine. Elle aide à formaliser fonctions, resets, interlocks, zones, effets machine et validation terrain.

## Quand l'utiliser

À utiliser pour :
- concevoir des architectures safety dédiées ;
- définir les fonctions de sécurité machine ;
- formaliser reset, E-stop, portes et zones ;
- préparer une validation cohérente entre analyse normative et comportement réel.

Ne pas utiliser pour :
- une simple logique automate sans fonction de sécurité ;
- une note réglementaire sans architecture machine ;
- un petit ajustement sans enjeu de standardisation safety.

## Axes de structuration

1. Décrire chaque fonction de sécurité et son effet machine.
2. Isoler resets et conditions de reprise.
3. Lier analyse normative et comportement réel terrain.
4. Définir clairement zones, permissifs et états opératoires.
5. Prévoir les preuves de validation et de reprise en service.

## Livrables attendus

- cartographie des fonctions safety ;
- matrice zones / fonctions / resets ;
- logique de reprise après défaut ;
- contrat avec états machine et supervision ;
- check-list FAT/SAT safety.

## Support files

- `templates/safety-function-template.md` : gabarit de fonction safety.
- `references/expert-pack.md` : points d'attention détaillés Pilz.
- `references/version-validation-matrix.md` : matrice de validation rapide.

## Pièges Courants (Common Pitfalls)

1. Fonction sécurité documentée trop vaguement.
2. Conditions de reprise mal définies.
3. Validation terrain incomplète.
4. Effet machine réel insuffisamment décrit.

## Liste de vérification (Checklist)

- [ ] Chaque fonction sécurité a un effet machine défini.
- [ ] Les resets et préconditions sont documentés.
- [ ] La validation terrain couvre les cas de reprise.
- [ ] Le lien avec PL/SIL est explicite.
- [ ] Les états opératoires après défaut sont clarifiés.
