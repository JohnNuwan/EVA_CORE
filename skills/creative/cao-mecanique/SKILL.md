---
name: cao-mecanique
title: "CAO Mécanique — Tolérancement, GD&T, matériaux et cotation"
description: "Guide complet de CAO mécanique : tolérances dimensionnelles et géométriques (GD&T), cotation ISO/ASME, matériaux, liaisons mécaniques, états de surface, normes de dessin"
category: creative
tags: [cao-mecanique, gdt, tolerance, cotation, dessin-technique, iso, asme]
created: 2026-07-22
---

# CAO Mécanique

## 1. Tolérances dimensionnelles (ISO 286 / ASME Y14.5)

| Qualité IT | Usage | Précision |
|-----------|-------|-----------|
| IT01-IT4 | Calibres, jauges | < 1 µm |
| IT5-IT6 | Roulements, ajustements précis | 2-5 µm |
| IT7-IT8 | Usinage standard | 10-20 µm |
| IT9-IT10 | Usinage courant | 30-60 µm |
| IT11-IT16 | Fonderie, brut, grossier | 0.1-3 mm |

### Ajustements ISO
| Type | Exemple | Application |
|------|---------|-------------|
| Jeux | H7/g6 | Axe tournant dans palier |
| Incertain | H7/js6 | Centrage sans mouvement |
| Serrage | H7/p6 | Goupille, roulement sur arbre |

**Lecture** : `H7/g6` → alésage H7 IT7, arbre g6 IT6

## 2. GD&T (ISO 1101 / ASME Y14.5)

| Catégorie | Symbole | Signification |
|-----------|---------|---------------|
| Forme | ⏤ ⏥ ⏣ ⌭ | Flatness, Straightness, Circularity, Cylindricity |
| Profil | ⌓ ⌔ | Profile of a line / surface |
| Orientation | ∥ ⟂ ∠ | Parallelism, Perp., Angularity |
| Position | ⌖ ◎ ⎔ | Position, Concentricity, Symmetry |
| Battement | ↗ ⇗ | Circular / Total runout |

### Feature Control Frame
```
┌────────┬───────────┬──────────┐
│   ⌖    │  Ø0.1 M   │  A B M C │
└────────┴───────────┴──────────┘
```
Vraie position ≤ Ø0.1 en MMC, réf. datums A, B (MMC), C.

## 3. États de surface (ISO 1302)

- **Ra** : écart moyen — standard général
- **Rz** : hauteur moyenne 10 points — frottement
- **Rmax** : profondeur max — étanchéité

## 4. Matériaux mécaniques

**Aciers :** S235JR (construction), S355J2 (méca), C45 (arbres), 42CrMo4 (haute résistance), 304 inox
**Alu :** 1050A (tôlerie), 5083 (marine), 6060 (profilés), 6082 (structure), 7075 (aéro)
**Plastiques :** PA6/66 (engrenages), POM (coulissant), PEEK (HT/médical), PTFE (joints)

## 5. Liaisons mécaniques

**Démontables :** boulon M6, vis à métaux, goupille, clavette, cannelure
**Permanentes :** soudure, rivet, collage, frein filet
**Mobiles :** roulement (billes/rouleaux/aiguilles), palier lisse, glissière

## 6. Normes de dessin

- Formats : A0 (841×1189) à A4 (210×297)
- Cartouche : désignation, n° plan, matière, échelle, tolérance générale, état de surface, révision
- Hachures à 45°, fond noir pour pièces pleines minces

## Pitfalls

- **Surtolérance** : IT7 partout = coût ×10 inutile
- **Datums non fonctionnels** : choisir selon l'assemblage, pas le brut
- **Chaîne de cotes** : 5 cotes ±0.1 mm = ±0.5 mm au total
- **MMC/LMC** : comprendre "condition la plus défavorable pour l'assemblage"

## Ressources

- [ISO 286](https://www.iso.org/standard/45979.html)
- [ASME Y14.5](https://www.asme.org/codes-standards/find-codes-standards/y14-5-dimensioning-tolerancing)
- [Engineering Toolbox](https://www.engineeringtoolbox.com/)