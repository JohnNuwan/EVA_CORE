---
name: multi-sector-industrial-standards
description: "Structurer et comparer les normes industrielles multi-secteurs : agroalimentaire, pharma, médical, électrique, CEM, ATEX et cybersécurité OT."
version: 1.1.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, standards, agrifood, pharma, medical, electrical, emc, atex, cybersecurity]
    related_skills: [agrifood-norms-haccp, iso-22000, gmp-pharmaceutical, iso-13485-medical-devices, electrical-schematics-eplan, emc-protection-grounding, atex-hazardous-areas, cybersecurity-iec62443, iso-27001]
---

# Normes industrielles multi-secteurs

## Vue d'ensemble

Cette compétence sert de skill transverse pour orienter rapidement le bon référentiel selon le secteur industriel visé : agroalimentaire, biologique, pharmaceutique, médical, électrique, CEM, ATEX et cybersécurité. Elle sert surtout à séparer correctement les familles d'exigences avant de les réassembler dans un cadre projet cohérent.

## Quand l'utiliser

À utiliser pour :
- cartographier les normes applicables à un site ou un projet ;
- comparer des exigences entre secteurs réglementés ;
- préparer un audit, un cahier des charges ou une architecture conforme ;
- identifier les écarts entre exigences process, qualité, sécurité et cybersécurité.

Ne pas utiliser pour :
- une question mono-secteur déjà couverte par une skill spécialisée ;
- une simple citation réglementaire hors contexte projet ;
- une réponse où l'on n'a pas besoin de distinguer les familles normatives.

## Grille de lecture rapide

- Agroalimentaire : HACCP, ISO 22000, BRC, IFS, FSSC 22000, traçabilité, allergènes.
- Biologique / Bio : référentiels bio/organic, traçabilité matière, séparation de flux, PMS/PPR adaptés.
- Pharmaceutique : GMP/BPF, FDA 21 CFR Part 11/210/211, ICH Q7/Q10, validation, data integrity.
- Médical : ISO 13485, FDA 21 CFR Part 820, ISO 14971, DHF/DMR/DHR, biocompatibilité.
- Électrique : IEC 60204-1, IEC 81346, IEC 61439, sélectivité, repérage, câblage.
- CEM / Terre : IEC 61000, blindages, PE/HF, filtres CEM, parafoudres, séparation des classes de câbles.
- ATEX : directives 2014/34/UE et 1999/92/CE, EN 60079, zones 0/1/2/20/21/22.
- Cybersécurité OT : IEC 62443, ISO 27001, zones & conduits, DMZ, hardening, accès distants.

## Domaines déjà solides

- agroalimentaire / HACCP / ISO 22000
- pharmaceutique / GMP
- médical / ISO 13485
- électrique / CEM / ATEX
- cybersécurité OT

## Domaines à renforcer ensuite

- pneumatique industrielle normative (ISO 4414, préparation d'air, sécurité pneumatique)
- hydraulique industrielle normative (ISO 4413, propreté fluide, sécurité circuits)
- référentiels biologiques spécialisés hors bio/organic générique selon filière

## Support files

- `references/sector-routing-matrix.md` : matrice d'orientation multi-domaines pour qualifier rapidement les familles normatives à mobiliser.

## Pièges Courants (Common Pitfalls)

1. Mélanger conformité qualité, sécurité machine et cybersécurité comme s'il s'agissait du même référentiel.
2. Appliquer une norme secteur sans vérifier les obligations documentaires locales/réglementaires.
3. Oublier les interfaces entre domaines : ex. GMP + 21 CFR Part 11 + IEC 62443 + validation SCADA.

## Liste de vérification (Checklist)

- [ ] Le secteur industriel cible est identifié.
- [ ] Les normes cœur de métier sont listées.
- [ ] Les contraintes qualité, sécurité, environnement et cybersécurité sont séparées.
- [ ] Les zones moins couvertes (pneumatique/hydraulique) sont traitées explicitement si le projet les implique.
