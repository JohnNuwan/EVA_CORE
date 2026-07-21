---
name: retro-conception-3d
title: "Rétro-conception 3D — Scan, photogrammétrie et reconstruction surfacique"
description: "Guide complet de rétro-conception 3D : scan laser, photogrammétrie, reconstruction CAO surfacique, nuages de points, alignment, mesh-to-BREP, inspection et reverse engineering"
category: creative
tags: [retro-conception, scan-3d, photogrammetrie, reverse-engineering, lidar, nuage-points, reconstruction]
created: 2026-07-22
---

# Rétro-conception 3D

## 1. Technologies de capture

### Scan laser
| Technologie | Précision | Portée |
|-------------|-----------|--------|
| Triangulation laser | ±0.01-0.1 mm | 0.1-1 m |
| LIDAR ToF | ±1-10 mm | 1-1000 m |
| LIDAR Phase shift | ±1-3 mm | 1-100 m |
| LIDAR iPhone dToF | ±1-3 cm | 0.1-5 m |

**Marques :** FARO, Leica, Creaform (HandySCAN), Artec

### Photogrammétrie
- Photos multiples → triangulation points homologues
- Précision : ±0.05-2 mm (selon caméra et échelle)
- Logiciels : RealityCapture, Metashape, Meshroom (OSS)
- Avantages : texture couleur, pas de matériel coûteux
- Inconvénients : surfaces réfléchissantes/transparentes

### Scan structuré (lumière bleue)
- Projection motifs (frange, Gray code)
- Précision : ±0.005-0.05 mm
- Idéal : pièces mécaniques petites
- Marques : GOM ATOS, EinScan

### CT scan (tomographie)
- Rayons X → volume 3D complet (interne inclus)
- Précision : ±0.01-0.1 mm, coût : €€€€€

## 2. Workflow

```
1. PRÉPARATION : nettoyage, matification, cibles, calibration
2. CAPTURE : multiples vues, zones fonctionnelles haute résolution
3. NUAGE DE POINTS : alignment, filtrage outliers, registration ICP
4. MESH : Poisson reconstruction, remaillage, réparation trous
5. CAO : primitives fitting, NURBS, features BREP
6. INSPECTION : deviation map, GD&T, jeu fonctionnel
```

## 3. Algorithmes clés

### ICP (Iterative Closest Point)
```python
import open3d as o3d
reg = o3d.pipelines.registration.registration_icp(
    source, target, threshold, init_pose,
    o3d.pipelines.registration.TransformationEstimationPointToPlane(),
    o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=200)
)
```

### Poisson Surface Reconstruction
```python
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd, depth=10, scale=1.1, linear_fit=False
)
```

### RANSAC primitive fitting
```python
plane_model, inliers = pcd.segment_plane(
    distance_threshold=0.01, ransac_n=3, num_iterations=1000
)
```

## 4. Inspection dimensionnelle

### Deviation map
```python
distances = scan_mesh.compute_point_cloud_distance(ref_mesh.sample_points_uniformly(100000))
print(f"Écart moyen: {np.mean(distances)*1000:.2f} mm")
print(f"Écart max: {np.max(distances)*1000:.2f} mm")
```

### GD&T sur scan
- Flatness, Position, Roundness, Cylindricity via best-fit

## 5. Stratégies par type d'objet

| Type | Technologie | Résolution |
|------|------------|-----------|
| Pièce mécanique petite (5-200 mm) | Structuré / laser triang. | 0.01-0.1 mm |
| Pièce mécanique grande (0.2-2 m) | Laser LIDAR | 0.1-1 mm |
| Bâtiment (1-100 m) | LIDAR phase shift | 1-10 mm |
| Organique (sculpture, corps) | Photogrammétrie | 0.1-1 mm |
| Assemblage complet | CT scan | 0.01-0.1 mm |

## 6. Réparation de mesh

| Problème | Solution |
|----------|----------|
| Trous (holes) | Fill holes (MeshLab, Blender) |
| Non-manifold edges | Cleanup (Netfabb, Blender) |
| Spike / outliers | Statistical outlier removal |
| Normales inversées | Unify normals |
| Auto-intersections | Auto-repair |
| High poly count | Décimation quadric edge collapse |

## 7. Formats de sortie

PLY (intermédiaire), STL (impression), OBJ (texture), STEP (CAO après reconstruction), E57 (LIDAR), LAS/LAZ, DXF (plans)

## Pitfalls

- **Surfaces réfléchissantes** : chrome/verre/miroir = impossible sans matification
- **Noir** : absorption laser = bruit. Utiliser poudre de contraste
- **Sous-détails** : angles vifs, trous < 1 mm peuvent être lissés
- **Dérive alignment** : grands scans → l'ICP peut diverger. Utiliser cibles
- **Temps post-traitement** : 4-10× le temps de scan pour un mesh propre
- **Mesh→STEP** : jamais de reconstruction paramétrique parfaite automatique

## Ressources

- [CloudCompare](https://www.cloudcompare.org/)
- [Open3D](https://www.open3d.org/)
- [MeshLab](https://www.meshlab.net/)
- [GOM Inspect](https://www.gom.com/en/products/gom-inspect-suite)
- [Blender](https://www.blender.org/) (retopo + sculpt)