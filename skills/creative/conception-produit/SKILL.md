---
name: conception-produit
title: "Conception Produit — Du brief au prototypage, DFM/DFA"
description: "Guide complet de conception de produit : cycle de développement, design for manufacturing (DFM), design for assembly (DFA), prototypage rapide, analyse fonctionnelle, cahier des charges"
category: creative
tags: [conception-produit, dfm, dfa, prototypage, industrial-design, cycle-developpement]
created: 2026-07-22
---

# Conception Produit

## 1. Processus de développement

### Phase 1 : Spécifications
- Cahier des Charges Fonctionnel : FP1 (usage), FP2 (secondaires), FC (contraintes)
- Performances : force, vitesse, précision, durée de vie
- Marché cible, gamme de prix, cycle de vie (prototype:50, série:10000)

### Phase 2 : Conception préliminaire
- Recherche de concepts : brainstorming, croquis, moodboard
- Esquisses 2D, maquette volume (carton/mousse/argile)
- Analyse fonctionnelle FAST, PoC simplifié

### Phase 3 : Conception détaillée
- Modélisation 3D paramétrique, calculs dimensionnement
- Choix matériaux, sous-traitance (moulage, usinage, tôlerie)
- Prototype fonctionnel (impression 3D)

### Phase 4 : Validation
- Tests fatigue/environnementaux/réglementaires (CE, UL, FCC)
- DFM (optimiser pour fabrication), DFA (réduire assemblage)
- Outillage (moules injection, matrices emboutissage)
- Process FMEA, prototype série (20-100 pcs)

### Phase 5 : Série
- Suivi production, Cpk, documentation (BOM, plans, gammes)
- ECO/ECN pour modifications, amélioration continue

## 2. Design for Manufacturing (DFM)

### Injection plastique
| Règle | Valeur |
|-------|--------|
| Draft angle | 1-2° par face |
| Épaisseur paroi | 2-3 mm constante |
| Ribs | ≤ 60% épaisseur paroi |
| Radius coins | ≥ 0.5 mm |
| Ratio L/t | ≤ 150 (PP) |

### Tôlerie
| Règle | Valeur |
|-------|--------|
| Bend radius | ≥ 1× épaisseur |
| Distance trou/pli | ≥ 2× épaisseur + rayon |
| K-factor | 0.33 (acier) à 0.5 (alu) |

### Usinage CNC
| Règle | Valeur |
|-------|--------|
| Profondeur poche | ≤ 4× diamètre outil |
| Coin intérieur | ≥ rayon outil (R3, R6) |
| Sous-découpes | à éviter |
| Parois fines | ≥ 2 mm (acier), ≥ 4 mm (alu) |

## 3. Design for Assembly (DFA)

Méthode Boothroyd-Dewhurst : compter pièces → évaluer manipulation → insertion → E_DFA

### Règles DFA
- Insertion verticale (gravité), accès libre
- Auto-alignement : chanfreins, cônes de centrage
- Éviter vis : clips, snap-fit, rivets
- Poka-Yoke : conception anti-erreur (connecteurs asymétriques)

## 4. Prototypage rapide

| Méthode | Délai | Coût | Usage |
|---------|-------|------|-------|
| FDM | 1-48h | € | Forme, ajustement |
| SLA | 4-72h | €€ | Finition, transparent |
| SLS | 8-48h | €€€ | Fonctionnel Nylon |
| CNC | 1-5j | €€-€€€ | Résistant |
| Silicone molding | 1-2 sem | €€ | Série 10-100 |
| Injection rapide | 2-4 sem | €€€€ | Moule alu |

## 5. Analyse de coûts

`Coût total = Matière + Fabrication + Assemblage + Overhead`

| Procédé | Volume min | Coût/pièce |
|---------|-----------|------------|
| FDM | 1 | 5-50 € |
| CNC | 1-100 | 10-500 € |
| Tôlerie | 10-1000 | 1-50 € |
| Injection | 10000+ | 0.10-2 € |
| Fonderie alu | 500+ | 2-10 € |

## Pitfalls

- **Sur-conception** : features inutiles = coût + complexité
- **Oublier maintenance** : comment réparer sans tout démonter ?
- **Tolérances irréalistes** : ±0.01 mm sur injecté = impossible ou ×10
- **Design sans DFM** : belle CAO mais infabriquable
- **Prototype ≠ série** : FDM ne valide pas l'injection (retrait, flux)

## Ressources

- [Boothroyd DFA](https://www.dfma.com/)
- [FMEA AIAG/VDA](https://www.aiag.org/)
- [Ashby Materials Selection](https://www.elsevier.com/books/engineering-materials/ashby)