---
name: impression-3d
title: "Impression 3D — FDM, SLA, SLS, post-traitement et matériaux"
description: "Guide complet de l'impression 3D : technologies FDM/FFF, SLA/DLP, SLS/SLM, slicers (Cura, PrusaSlicer, Orca), matériaux, paramètres, supports, post-traitement, troubleshooting"
category: creative
tags: [impression-3d, fdm, sla, sls, slicer, materiaux, post-traitement]
created: 2026-07-22
---

# Impression 3D

## 1. Technologies

### FDM/FFF
- Principe : filament fondu déposé couche par couche
- Précision : ±0.1-0.3 mm, couche 0.05-0.4 mm
- Coût : très bas (15-40 €/kg)
- Marques : Bambu Lab, Prusa, Creality, Voron

### SLA/DLP
- Principe : polymérisation UV de résine liquide
- Précision : ±0.01-0.05 mm, couche 0.01-0.1 mm
- Coût : moyen (résine 25-60 €/L)
- Marques : Formlabs, Anycubic, Elegoo

### SLS/SLM
- Principe : fusion sélective de poudre (polymère/métal) par laser
- Précision : ±0.05-0.2 mm
- Pas de supports (poudre auto-portante)

## 2. Slicers

| Slicer | Points forts |
|--------|-------------|
| Cura | Open source, profils extensibles |
| PrusaSlicer | Paint-on supports, multi-matériaux |
| OrcaSlicer | Calibration intégrée, Pressure Advance |
| Bambu Studio | Intégration cloud, auto-calibration |
| Simplify3D | Contrôle fin des supports |

### Paramètres FDM critiques
- **Layer height** : 0.2 mm (std), 0.12 (fine), 0.3 (rapide)
- **Temp nozzle** : 190-220°C (PLA), 230-250°C (PETG), 250-270°C (ABS)
- **Bed temp** : 60°C (PLA), 80°C (PETG), 100°C (ABS)
- **Infill** : 15-20% (std), 100% (résistance)
- **Supports** : Tree vs Organic vs Grid
- **Retraction** : 0.5-2 mm (Bowden), 0.2-0.8 mm (Direct Drive)

## 3. Matériaux FDM

| Matériau | Température | Usage |
|----------|------------|-------|
| PLA | 190-220°C | Prototypes |
| PLA+ | 200-225°C | Mécanique légère |
| PETG | 230-250°C | Fonctionnel, eau |
| ABS | 250-270°C | Pièces auto, boîtiers |
| ASA | 240-260°C | Extérieur UV |
| TPU | 210-240°C | Joints, poignées |
| PC | 260-300°C | Structurel |
| Nylon | 250-280°C | Engrenages |
| PEEK | 370-410°C | Médical, aéro |
| Composites | Variable | Effet de matière |

## 4. Troubleshooting FDM

| Problème | Solution |
|----------|----------|
| Stringing | Augmenter retraction distance + speed |
| Warping | Augmenter bed temp, brim, enclosure |
| Underextrusion | Cold pull, calibrer flow rate |
| Layer shifting | Tendre courroie, réduire accélération |
| First layer bad | Calibrer Z offset |
| Elephant foot | Compensation elephant foot |
| Blobs/zits | Calibrer Pressure Advance / K-value |

## 5. DFAM (Design for Additive Manufacturing)

- **Bridges** : max 10-20 mm sans support
- **Overhangs** : ≤45° sans support
- **Trous** : ≥2 mm (verticaux), ≥4 mm (horizontaux)
- **Parois** : ≥0.8 mm (0.4 mm nozzle × 2 périmètres)
- **Tolerance** : 0.2-0.3 mm entre pièces mobiles

## 6. Post-traitement

**FDM :** retrait supports → ponçage (120→240→400→800→1000) → lissage acétone (ABS) → apprêt → peinture
**SLA :** lavage IPA → post-cure UV → retrait supports → ponçage → vernis/peinture

## Pitfalls

- **Hygroscopie** : PETG/Nylon/TPU → sécher 4-6h à 65-80°C
- **Chamber** : ABS/ASA nécessitent enclosure chauffée (40-60°C)
- **Ventilation** : ABS (styrène), résine SLA (toxique) → espace ventilé
- **First layer** : 90% des échecs FDM

## Ressources

- [Teaching Tech Calibration](https://teachingtechyt.github.io/calibration.html)
- [Ellis' Print Tuning Guide](https://ellis3dp.com/)
- [CNC Kitchen](https://www.cnckitchen.com/)