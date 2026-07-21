---
name: 3d-vision
description: Vision 3D — estimation de profondeur, nuages de points, NeRF, 3D Gaussian Splatting, reconstruction, stéréo, SLAM, MVS, mesh processing. En français.

---

# Vision 3D — Profondeur, Nuages de Points, Reconstruction 3D

Vision 3D : de la reconstruction stéréo aux NeRF et 3D Gaussian Splatting. Couvre les fondamentaux (géométrie épipolaire, stéréo) jusqu'aux modèles génératifs 3D.

---

## 1. Géométrie de la Vision 3D

### Projection Caméra

```
Point 3D (X, Y, Z) → 2D (u, v)

[ u ]   [fx   0  cx] [R | t] [X]
[ v ] = [ 0  fy  cy] [     ] [Y]
[ 1 ]   [ 0   0   1] [     ] [Z]
                       [     ] [1]
       = K            · [R|t] · P
       Matrice        Matrice   Point 3D
       intrinsèque    extrinsèque
```

### Géométrie Épipolaire

```python
import cv2
import numpy as np

# Matrice fondamentale (non calibrée)
F, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, 1.0, 0.99)

# Matrice essentielle (calibrée)
E, mask = cv2.findEssentialMat(pts1, pts2, K, cv2.RANSAC, 0.999, 1.0)

# Décomposer E en R, t
_, R, t, mask = cv2.recoverPose(E, pts1, pts2, K)

# Rectification stéréo
R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
    K1, d1, K2, d2, img_size, R, t,
    flags=cv2.CALIB_ZERO_DISPARITY,
    alpha=-1,
)

# Cartes de rectification
map1, map2 = cv2.initUndistortRectifyMap(K1, d1, R1, P1, img_size, cv2.CV_32FC1)
```

---

## 2. Estimation de Profondeur

### Stéréo Classique

```python
# BM (Block Matching) — rapide
stereo_bm = cv2.StereoBM_create(numDisparities=16*5, blockSize=15)
disparity = stereo_bm.compute(img_left_gray, img_right_gray)

# SGBM (Semi-Global Block Matching) — précis
stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=128,
    blockSize=5,
    P1=8 * 3 * 5**2,      # Penalty sur le gradient
    P2=32 * 3 * 5**2,     # Penalty sur le saut
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=32,
    preFilterCap=63,
    mode=cv2.StereoSGBM_MODE_SGBM_3WAY,
)
disparity = stereo.compute(img_left_gray, img_right_gray)

# Normaliser pour visualisation
disp_norm = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
disp_norm = np.uint8(disp_norm)

# Profondeur : Z = (fx * baseline) / disparity
depth = (K[0, 0] * baseline) / (disparity + 1e-6)
```

### MiDaS (Monocular Depth Estimation)

```python
import torch
import cv2

# MiDaS v3.1
model_type = "DPT_Large"  # Meilleure qualité
# model_type = "MiDaS_small"  # Rapide
midas = torch.hub.load("intel-isl/MiDaS", model_type)
midas.to("cuda").eval()

# Transformation
transform = torch.hub.load("intel-isl/MiDaS", "transforms")
if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
    transform = transform.dpt_transform
else:
    transform = transform.small_transform

# Inférence
img = cv2.cvtColor(cv2.imread("image.jpg"), cv2.COLOR_BGR2RGB)
input_batch = transform(img).to("cuda")
with torch.no_grad():
    depth = midas(input_batch)
    depth = torch.nn.functional.interpolate(
        depth.unsqueeze(1),
        size=img.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze().cpu().numpy()

# Normaliser
depth_norm = (depth - depth.min()) / (depth.max() - depth.min())
```

### Depth Anything V2

```python
# Depth Anything V2 (meilleur que MiDaS)
import torch
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

processor = AutoImageProcessor.from_pretrained("depth-anything/Depth-Anything-V2-Large")
model = AutoModelForDepthEstimation.from_pretrained(
    "depth-anything/Depth-Anything-V2-Large"
).to("cuda").eval()

inputs = processor(images=image, return_tensors="pt").to("cuda")
with torch.no_grad():
    outputs = model(**inputs)
    depth = outputs.predicted_depth.squeeze().cpu().numpy()
```

### ZoeDepth

```python
# ZoeDepth — profondeur métrique (pas relative)
from zoedepth.models.builder import build_model
from zoedepth.utils.config import get_config

conf = get_config("zoedepth", "infer")
model = build_model(conf).to("cuda").eval()

depth = model.infer_pil(image)  # Profondeur en mètres
```

---

## 3. Nuages de Points (Point Clouds)

### Triangulation → Nuage 3D

```python
# Convertir disparité → nuage de points
# Q = matrice de reprojection 4×4
points_3d = cv2.reprojectImageTo3D(disparity, Q)

# Filtrer les points valides
mask = disparity > 0
points = points_3d[mask]
colors = img_left[mask]

# Open3D — Visualisation et manipulation
import open3d as o3d

# Créer le nuage
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points.reshape(-1, 3))
pcd.colors = o3d.utility.Vector3dVector(colors.reshape(-1, 3) / 255.0)

# Voxel downsampling (1cm)
pcd = pcd.voxel_down_sample(voxel_size=0.01)

# Estimer les normales
pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

# Supprimer les outliers
cl, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
pcd = pcd.select_by_index(ind)

# Visualiser
o3d.visualization.draw_geometries([pcd])
```

### Open3D — ICP (Registration)

```python
# ICP : aligner deux nuages
source = o3d.io.read_point_cloud("source.pcd")
target = o3d.io.read_point_cloud("target.pcd")

# ICP point-to-point
threshold = 0.02
reg_p2p = o3d.pipelines.registration.registration_icp(
    source, target, threshold, np.eye(4),
    o3d.pipelines.registration.TransformationEstimationPointToPoint(),
    o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=200),
)
print(reg_p2p.transformation)
print(reg_p2p.fitness)  # Qualité de l'alignement

# ICP point-to-plane (meilleur)
source.estimate_normals()
reg_p2l = o3d.pipelines.registration.registration_icp(
    source, target, threshold, np.eye(4),
    o3d.pipelines.registration.TransformationEstimationPointToPlane(),
)

# Global registration (RANSAC + ICP)
result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
    source, target, source_fpfh, target_fpfh,
    mutual_filter=True,
    max_correspondence_distance=0.075,
    estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
    ransac_n=3,
    checkers=[
        o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
        o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(0.075),
    ],
    criteria=o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999),
)
```

---

## 4. NeRF (Neural Radiance Fields)

```python
# NeRF classique
# Représentation : MLP (x, y, z, θ, φ) → (R, G, B, σ)

# Installation du framework Nerfstudio
# pip install nerfstudio

# Traitement des données
ns-process-data images --data images/ --output-dir data/nerf_dataset

# Entraînement
# ns-train nerfacto --data data/nerf_dataset

# NeRF avec PyTorch (implémentation simplifiée)
class NeRF(nn.Module):
    def __init__(self, D=8, W=256, input_ch=3, input_ch_views=3, output_ch=4):
        super().__init__()
        # Positional encoding
        self.embed_fn = None
        
        # Volume MLP
        self.pts_linears = nn.ModuleList(
            [nn.Linear(input_ch, W)] +
            [nn.Linear(W, W) for _ in range(D-1)]
        )
        self.pts_feature_linear = nn.Linear(W, W)
        self.pts_output_linear = nn.Linear(W, 1)  # σ (densité)
        
        # View MLP (couleur dépendante de la direction)
        self.views_linear = nn.Linear(input_ch_views + W, W//2)
        self.feature_linear = nn.Linear(W//2, W//2)
        self.output_linear = nn.Linear(W//2, 3)  # RGB
    
    def forward(self, x, direction):
        # Volume
        h = x
        for layer in self.pts_linears:
            h = F.relu(layer(h))
        sigma = self.pts_output_linear(h)
        h = self.pts_feature_linear(h)
        
        # View
        h = torch.cat([h, direction], dim=-1)
        h = F.relu(self.views_linear(h))
        h = F.relu(self.feature_linear(h))
        rgb = torch.sigmoid(self.output_linear(h))
        
        return torch.cat([rgb, sigma], dim=-1)
```

### Instant NGP (CUDA-accelerated)

```python
# Instant Neural Graphics Primitives
# GitHub : https://github.com/NVlabs/instant-ngp

# Via nerfstudio
ns-train instant-ngp --data data/nerf_dataset

# Extraction mesh
ns-extract-mesh --load-config outputs/nerf_dataset/nerfacto/config.yml \
    --output-path mesh.ply

# Rendu vidéo
ns-render --load-config outputs/nerf_dataset/nerfacto/config.yml \
    --camera-path-filename camera_path.json \
    --output-path output.mp4
```

---

## 5. 3D Gaussian Splatting

```python
# 3DGS : représentation par ellipsoïdes gaussiens 3D
# État de l'art reconstruction 3D (2023-2025)

# Installation
# git clone https://github.com/graphdeco-inria/gaussian-splatting
# pip install -r requirements.txt

# Entraînement sur COLMAP
# python train.py -s <path_to_colmap_dataset>

# Format : chaque Gaussian = (x, y, z, qx, qy, qz, qw, s, rgb, α)
# - Position 3D
# - Rotation (quaternion)
# - Échelle (3D covariance)
# - Couleur (SH : spherical harmonics)
# - Opacité α

# SuperSplat (éditeur web)
# https://playcanvas.com/supersplat
```

### Structure du Pipeline

```
Images (multi-vues)
    ↓
SfM (COLMAP) → Points 3D clairsemés + poses caméra
    ↓
Initialisation Gaussienne
    ↓
Rendu différentiable (α-blending)
    ↓
Optimisation (L1 + D-SSIM)
    ↓
Adaptive Density Control (split/clone)
    ↓
3D Gaussians entraînés
```

---

## 6. COLMAP (Structure from Motion + MVS)

```bash
# SfM (structure from motion) — poses caméra + points clairsemés
colmap feature_extractor --database_path database.db --image_path images/
colmap exhaustive_matcher --database_path database.db
colmap mapper --database_path database.db --image_path images/ --output_path sparse/

# MVS (Multi-View Stereo) — nuage dense
colmap image_undistorter --image_path images/ --input_path sparse/0/ --output_path dense/
colmap patch_match_stereo --workspace_path dense/
colmap stereo_fusion --workspace_path dense/ --output_path dense/fused.ply

# Poisson mesh
colmap poisson_mesher --input_path dense/fused.ply --output_path dense/mesh.ply
```

```python
# COLMAP via Python
import pycolmap

# Reconstruction
output_path = "output/"
reconstruction = pycolmap.Reconstruction()

# Feature extraction
options = pycolmap.SiftExtractionOptions()
pycolmap.extract_features("./images", "./database.db", options)

# Matching
options = pycolmap.SiftMatchingOptions()
pycolmap.match_exhaustive("./database.db", options)

# Mapper
mapper_options = pycolmap.MapperOptions()
result = pycolmap.incremental_mapping("./database.db", "./images", "./output")
```

---

## 7. SLAM Visuel (ORB-SLAM, DroidSLAM)

```python
# ORB-SLAM3
# https://github.com/UZ-SLAMLab/ORB_SLAM3

# DroidSLAM (Deep SLAM)
# https://github.com/princeton-vl/DroidSLAM

# Exemple DroidSLAM
import torch
from droid import Droid

droid = Droid(args)
# stream = video_stream()  # Flux vidéo
for t, image in enumerate(stream):
    droid.track(t, image)
    # Récupérer la carte
    with torch.no_grad():
        droid.visualize()
```

---

## 8. Mesh Processing (PyTorch3D)

```python
import torch
import pytorch3d
from pytorch3d.io import load_obj, save_obj
from pytorch3d.structures import Meshes
from pytorch3d.renderer import (
    MeshRenderer, RasterizationSettings, MeshRasterizer,
    PointLights, SoftPhongShader, TexturesVertex,
    look_at_view_transform
)

# Charger
verts, faces, aux = load_obj("mesh.obj")
faces = faces.verts_idx
mesh = Meshes(verts=[verts], faces=[faces])

# Rendu
R, T = look_at_view_transform(dist=2.7, elev=20, azim=45)
lights = PointLights(device="cuda")
raster_settings = RasterizationSettings(image_size=512, blur_radius=0, faces_per_pixel=1)
renderer = MeshRenderer(
    rasterizer=MeshRasterizer(raster_settings=raster_settings),
    shader=SoftPhongShader(device="cuda", cameras=None, lights=lights),
)

images = renderer(mesh, cameras=...)  # (B, H, W, 4) RGBA

# Loss 3D
from pytorch3d.loss import chamfer_distance, mesh_edge_loss, mesh_normal_consistency

# Chamfer distance (nuage à nuage)
loss_chamfer, _ = chamfer_distance(pred_points, gt_points)

# Régularisation mesh
loss_edge = mesh_edge_loss(mesh)
loss_normal = mesh_normal_consistency(mesh)
```

---

## 9. Modèles Génératifs 3D

### Zero-1-to-3 (Image → 3D)

```python
from transformers import CLIPTextModel, CLIPTokenizer
from diffusers import StableDiffusionImg2ImgPipeline

# Zero-1-to-3 transforme une image en 3D conditionné par l'angle de vue
# image → (R, T) → nouvelle vue 3D
# Idéal pour générer des vues multiples à partir d'une seule image
```

### TripoSR / InstantMesh (Image → Mesh 3D)

```python
# TripoSR : reconstruction 3D rapide depuis une image
# pip install trimesh
# python -m scripts.run_triposr --image input.png --output output.obj

# InstantMesh : reconstruction 3D multi-vue
# git clone https://github.com/TencentARC/InstantMesh
```

### Point-E / Shap-E (OpenAI, Texte → 3D)

```python
import torch
import shap_e
from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config

# Shap-E : texte → mesh 3D
model = load_model("transmitter", device="cuda")
diffusion = diffusion_from_config(load_config("diffusion"))

latents = sample_latents(
    batch_size=1,
    model=model,
    diffusion=diffusion,
    guidance_scale=15.0,
    model_kwargs=dict(texts=["un chat"]),
    progress=True,
    clip_denoised=True,
    use_fp16=True,
    use_karras=True,
    karras_steps=64,
    sigma_min=1e-3,
    sigma_max=160,
    s_churn=0,
)

# Exporter
from shap_e.util.notebooks import decode_latent_mesh
decode_latent_mesh(latents[0]).write_obj("output.obj")
```

---

## 10. Datasets 3D

| Dataset | Type | Taille | Description |
|---------|------|--------|-------------|
| ShapeNet | Mesh | 51k | Objets 3D catégorisés |
| ModelNet40 | Mesh | 12k | Classification 3D |
| ScanNet | RGB-D | 1.5k | Scènes intérieures |
| Matterport3D | RGB-D | 90 | Bâtiments |
| KITTI | Stereo | 200 | Conduite |
| DTU MVS | MVS | 124 | Reconstruction |
| BlendedMVS | MVS | 17k | MVS mixte |
| CO3D | Multi-view | 36k | Objets tournants |
| MegaDepth | Depth | 1M | Profondeur extérieure |

---

## Références
- Open3D : https://www.open3d.org/
- PyTorch3D : https://pytorch3d.org/
- NeRF Studio : https://docs.nerf.studio/
- 3D Gaussian Splatting : https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/
- COLMAP : https://colmap.github.io/
- MiDaS : https://github.com/isl-org/MiDaS
- Depth Anything : https://depth-anything.github.io/
- PapersWithCode 3D : https://paperswithcode.com/task/3d-reconstruction