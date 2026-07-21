---
name: stl-step-iges
title: "Formats STL / STEP / IGES — Échange et conversion de fichiers CAO"
description: "Guide complet des formats d'échange CAO : STL (mesh), STEP (BREP AP203/AP214/AP242), IGES (legacy), conversion, bonnes pratiques, outils ligne de commande et API"
category: creative
tags: [stl, step, iges, format, conversion, echange, cad, brep]
created: 2026-07-22
---

# STL / STEP / IGES

## 1. STL (Standard Tessellation Language)

**Type :** Mesh triangulaire | **Année :** 1987 (3D Systems) | **Précision :** Approximative

### Variantes
- **ASCII** : lisible, fichier volumineux (×5)
- **Binary** : compact, standard impression 3D
- **Color** : pas de standard officiel

### Structure binaire
```
Header (80 bytes) | Nb triangles (uint32) | Triangle × N (normale + 3 sommets + attribut)
```

### Limitations
- Pas de couleur (sauf extensions non standard)
- Pas d'unités : mm/cm/inches devinés par l'importeur
- Pas de topologie : triangles non connectés (doublons sommets)
- Pas de BREP : arrondi = facettage visible

### Export paramètres

| Paramètre | Valeur | Effet |
|-----------|--------|-------|
| Deviation | 0.01-0.1 mm | Écart BREP→mesh |
| Angle | 5-15° | Angle entre normales |
| Unit | mm | Toujours exporter en mm |

### CLI
```bash
openscad -o piece.stl modele.scad
freecadcmd -c "import FreeCAD,Mesh; Mesh.export(doc.Objects, 'piece.stl')"
blender --background piece.blend --export-format stl --output piece.stl
```

## 2. STEP (ISO 10303)

**Type :** BREP exact | **Année :** 1994 | **Fidélité :** Élevée

### Application Protocols

| AP | Contenu | Recommandation |
|----|---------|---------------|
| AP203 | BREP solide + assemblage | Universel |
| AP214 | + Couleurs, couches | Automobile |
| AP242 | + PMI, GD&T, maillage | **Moderne (recommandé)** |

**Fichiers :** .stp, .step, .p21 (Part 21 text encoding)

### Ce qui est conservé
| Élément | AP203 | AP214 | AP242 |
|---------|-------|-------|-------|
| Géométrie exacte | ✅ | ✅ | ✅ |
| Assemblages | ✅ | ✅ | ✅ |
| Couleurs | ❌ | ✅ | ✅ |
| PMI/GD&T | ❌ | ❌ | ✅ |
| Matériaux | ❌ | ❌ | ✅ |

## 3. IGES (Initial Graphics Exchange Specification)

**Type :** BREP + filaire | **Année :** 1979 | **Standard :** ASME Y14.26M | **Statut :** Obsolète

### Problèmes connus
- Doublons de faces, orientation inverse des normales
- Gaps entre faces adjacentes (tolérances non spécifiées)
- Unité implicite (mm/pouces par convention)
- 80% des problèmes d'import CAO viennent d'IGES

## 4. Tableau comparatif

| Critère | STL | STEP | IGES |
|---------|-----|------|------|
| Type | Mesh | BREP | BREP |
| Précision | Approx. | Exacte | Exacte |
| Couleur | ❌ | ✅ (AP214+) | ✅ |
| Assemblage | ❌ | ✅ | ✅ (limité) |
| Impression 3D | ✅ Standard | ⚠️ (tessellé) | ❌ |
| Échange CAO | ❌ (perte) | ✅ Standard | ⚠️ (legacy) |
| Poids | Lourd | Léger | Moyen |

## 5. Recommandations par cas

| Vous avez... | Voulez... | Utilisez |
|-------------|----------|----------|
| Partenaire CAO | Échanger modifiable | **STEP AP242** |
| Imprimante 3D | Imprimer | **STL binaire** |
| Scanner 3D | Retravailler | **STL** → refaire BREP |
| Fournisseur | Fabriquer | **STEP AP203** |
| Legacy | Lire vieux fichier | **IGES** (dernier recours) |
| Documentation | PMI/tolérances | **STEP AP242** |

## 6. Vérification

```bash
# STL — compter triangles (binary)
python3 -c "with open('f.stl','rb') as f: f.seek(80); \
  n=int.from_bytes(f.read(4),'little'); print(f'{n} triangles')"

# STEP — compter entités BREP
grep -c "MANIFOLD_SOLID_BREP" piece.stp

# Réparation STL
admesh --print-statistics piece.stl
```

## Pitfalls

- **STL mm vs inches** : pièce 25.4× trop grande si mal exportée
- **STEP AP203 shell-based** : pas couleur, pas matériau
- **IGES** : si choix possible, **ne jamais utiliser** IGES. STEP est strictement meilleur
- **STL avec erreurs** : admesh/netfabb avant impression
- **Perte historique** : STEP exporte géométrie finale, PAS l'historique

## Ressources

- [ISO 10303-242](https://www.iso.org/standard/57620.html)
- [Admesh](https://github.com/admesh/admesh)
- [pythonOCC](https://github.com/tpaviot/pythonocc-core)
- [CadQuery](https://cadquery.readthedocs.io/)