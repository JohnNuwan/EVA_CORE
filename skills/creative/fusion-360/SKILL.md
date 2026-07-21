---
name: fusion-360
title: "Fusion 360 — CAO paramétrique, FAO et conception générative"
description: "Guide complet Autodesk Fusion 360 : modélisation paramétrique 3D, conception générative, FAO (fraisage/tournage), simulation éléments finis, gestion de données cloud"
category: creative
tags: [fusion-360, autodesk, cao, fao, conception-generative, simulation, parametrique]
created: 2026-07-22
---

# Fusion 360

## Vue d'ensemble

Autodesk Fusion 360 est une plateforme unifiée de CAO/FAO/IAO cloud-native. Contrairement aux outils traditionnels (SolidWorks, CATIA), Fusion combine modélisation paramétrique et directe, conception générative, FAO 2.5-5 axes, simulation FEA et gestion de projet cloud.

## 1. Modélisation paramétrique

### Corps (Bodies) vs Composants (Components)

| Concept | Description |
|---------|-------------|
| **Body** | Géométrie continue (un seul maillage BREP) — pas de timeline de position |
| **Component** | Entité indépendante avec son propre origine, timeline, propriétés physiques — **toujours préférer Components** |
| **Assemblage** | Hiérarchie de Components (joints, contacts, rigid groups) |

### Esquisses (Sketches)

- Plan de base : `Construct → Offset Plane` pour décaler
- Contraintes : coïncident, colinéaire, parallèle, perpendiculaire, concentrique, tangent
- **Toujours contraindre complètement** — pas de degrés de liberté bleus
- Palette F8 / Ctrl+F8 pour afficher/masquer les contraintes

### Timeline (Design History)

- Chronologie linéaire des opérations (features)
- **Rollback bar** : glisser pour insérer une feature au bon endroit
- Éviter les dépendances cycliques (une feature A référencée par B qui dépend de A)
- Renommer chaque feature (`F2`) — `Extrude1` → `Extrude-CorpsPrincipal`

### Types de features

- **Extrude** : nouvelle, jointe, coupée, intersection
- **Revolve** : révolution autour d'un axe
- **Loft** : transition entre profils (rails optionnels)
- **Sweep** : extrusion le long d'une trajectoire
- **Rib** : nervure (coque directionnelle)
- **Shell** : évidement (face à enlever)
- **Pattern** : rectangular, circular, mirror (sur une feature ou un corps)

## 2. Conception générative (Generative Design)

Utilisable uniquement avec licence commerciale/startup (pas la version perso).

1. Définir les **surfaces de contrainte** (fixations)
2. Définir les **surfaces de charge** (forces, pressions, moments)
3. Définir l'**obstacle geometry** (zones à éviter)
4. Choisir le **matériau cible** (aluminium, acier, titane, plastique)
5. Lancer l'étude → Fusion explore des milliers de topologies
6. Exporter le mesh résultat → remaillage → conversion BREP (fusion)

**Limitations :** nécessite cloud credits, temps de calcul variable (30 min – 24h)

## 3. FAO (Manufacturing)

### Modes d'usinage

| Mode | Description | Axes |
|------|-------------|------|
| **2D** | Poche, contour, perçage (surfaces planes) | 2.5 axes |
| **3D** | Surfaces complexes, zones de pente | 3 axes |
| **Multiaxis** | Surfaces complexes avec orientation outil variable | 4-5 axes |
| **Tournage** | Opérations de tour CNC (OD, ID, groove, thread) | 2 axes |

### Workflows types

- **Setup** : définition stock, orientation pièce, MCS
- **Tool library** : outils HSM, Toroid, Ball end, Drill, Thread mill
- **Adaptive Clearing** : stratégie HSM — engagement radial constant, moins d'usure outil
- **Passes** : roughing → semi-finishing → finishing
- **Simulation** : vérifier collision, survitesse, engagement

## 4. Simulation FEA

- **Stress Analysis** : contrainte von Mises, déplacement, facteur de sécurité
- **Modal Analysis** : fréquences naturelles, modes de vibration
- **Thermal** : conduction, convection
- **Shape Optimization** : allègement topologique (pré-générative)

## 5. Gestion de données cloud

- Projets Fusion **cloud-only** (sauf export local)
- **Versioning** automatique à chaque sauvegarde
- **Sharing** : lien public + commentaires
- **Export** : F3D (natif), STEP, IGES, STL, SAT, OBJ, DXF, PDF

## 6. API et scripting

- **Python API** (Fusion 360 API) : scripts pour automatiser
- **Add-ins** : extensions en C++/Python
- Exemple extraction BOM :
```python
import adsk.core, adsk.fusion
app = adsk.core.Application.get()
design = app.activeProduct
for occ in design.rootComponent.occurrences:
    print(occ.component.name)
```

## Pitfalls

- **Performance** : assemblages de +500 components ralentissent → utiliser Derived Components
- **Timeline** : ne pas accepter "Compute All" sauf si nécessaire (Ctrl+Shift+B)
- **Cloud** : pas de travail hors-ligne prolongé — prévoir cache local pour déplacements
- **Contraintes** : si un sketch devient rouge, une côte ou contrainte est conflictuelle — supprimer la dernière ajoutée

## Ressources

- [Fusion 360 API Reference](https://help.autodesk.com/view/fusion360/ENU/)
- [HSM Advisor](https://hsmadvisor.com/) — paramètres coupe