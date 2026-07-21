---
name: robot-perception
description: Perception robotique — vision par ordinateur, LiDAR, fusion de capteurs, détection d'objets, segmentation, estimation de pose, RGB-D
---

# Robot Perception — Vision et Fusion Capteurs pour Robotique

## Quand l'utilisateur
Quand l'utilisateur demande de traiter des données de capteurs pour robotique, de faire de la vision industrielle, de la détection d'objets, de la segmentation, de la localisation d'objets (pose estimation), de la reconstruction 3D, ou de la fusion LiDAR/Caméra.

## Pipeline Générique de Perception Robotique

```
Capteurs bruts
├── Caméra RGB (1280×720 @ 30fps)
├── Caméra RGB-D (RealSense, Kinect, Zed)
├── LiDAR 2D/3D (Velodyne, Ouster, SICK)
├── Sonar (milieu sous-marin)
├── Radar (voitures autonomes)
└── Capteurs tactiles (GelSight, force sensors)
    │
    ▼
Prétraitement (calibration, undistort, filtrage)
    │
    ▼
Extraction de features (SIFT, ORB, SuperPoint, FPN)
    │
    ▼
Perception de haut-niveau
├── Détection d'objets (YOLO, DETR, Faster R-CNN)
├── Segmentation (U-Net, Mask R-CNN, SAM)
├── Estimation de pose (PnP, ICP, PoseCNN)
├── Tracking (SORT, DeepSORT, Kalman Filters)
├── Suivi de personnes
└── Reconnaissance activites
    │
    ▼
Représentation de l'environnement
├── Grid mapping (occupancy grid)
├── Semantic mapping (segmentation sémantique)
├── SDF (Signed Distance Fields)
├── Octree (OctoMap, TSDF)
└── Object map (listes d'instances)
```

## Calibration de Caméra

### Modèle Pinhole + Distorsion
```python
import cv2
import numpy as np

# Calibration à partir d'un pattern échiquier
def calibrate_camera(image_paths, pattern_size=(9, 6), square_size=0.025):
    """
    Calibre une caméra avec un pattern échiquier
    pattern_size : nombre de coins intérieurs (cols, rows)
    square_size : taille d'un carré en mètres
    """
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)

    # Points 3D du pattern
    objp = np.zeros((pattern_size[0]*pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
    objp *= square_size

    objpoints = []  # points 3D monde
    imgpoints = []  # points 2D image

    for fname in image_paths:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)

    # Calibration
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    return camera_matrix, dist_coeffs
```

### Matrice de Projection
```
K = | fx   0   cx |
    |  0  fy   cy |
    |  0   0    1 |

Projection : u = K · [R|t] · X_world

Undistort :
  x_corrected = x(1 + k₁r² + k₂r⁴ + k₃r⁶) + [2p₁xy + p₂(r²+2x²)]
  y_corrected = y(1 + k₁r² + k₂r⁴ + k₃r⁶) + [p₁(r²+2y²) + 2p₂xy]
```

```python
# Correction de distorsion
def undistort_image(img, camera_matrix, dist_coeffs):
    h, w = img.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(
        camera_matrix, dist_coeffs, (w, h), 1, (w, h)
    )
    mapx, mapy = cv2.initUndistortRectifyMap(
        camera_matrix, dist_coeffs, None, new_camera_matrix, (w,h), cv2.CV_32FC1
    )
    dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
    return dst, new_camera_matrix
```

## Détection d'Objets (Deep Learning)

### YOLOv8 — Inference (Ultralytics)
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # nano, small, medium, large, xlarge

# Détection
results = model('image.jpg')
boxes = results[0].boxes.xyxy.cpu().numpy()   # [x1, y1, x2, y2]
scores = results[0].boxes.conf.cpu().numpy()  # confiance
classes = results[0].boxes.cls.cpu().numpy()  # classes COCO

# Pour la robotique : filtre basse confiance + tracking
detections = []
for box, score, cls in zip(boxes, scores, classes):
    if score > 0.5:
        detections.append({
            'bbox': box,
            'score': score,
            'class': int(cls),
            'class_name': model.names[int(cls)],
            'center': [(box[0]+box[2])/2, (box[1]+box[3])/2]
        })
```

### DETR (Detection Transformer) — End-to-End
```python
import torch
from transformers import DetrImageProcessor, DetrForObjectDetection

processor = DetrImageProcessor.from_pretrained('facebook/detr-resnet-50')
model = DetrForObjectDetection.from_pretrained('facebook/detr-resnet-50')

inputs = processor(images=image, return_tensors='pt')
outputs = model(**inputs)

# Décodage des prédictions
target_sizes = torch.tensor([image.shape[:2]])
results = processor.post_process_object_detection(outputs,
                                                    target_sizes=target_sizes,
                                                    threshold=0.7)[0]

for score, label, box in zip(results['scores'], results['labels'], results['boxes']):
    print(f"Détection : {model.config.id2label[label.item()]} à {box.tolist()}")
```

### SAM (Segment Anything) — Segmentation Universelle
```python
from segment_anything import sam_model_registry, SamPredictor

sam = sam_model_registry['vit_h'](checkpoint='sam_vit_h.pth')
predictor = SamPredictor(sam)

predictor.set_image(rgb_image)

# Segmentation avec points prompts
input_point = np.array([[500, 375]])  # x, y dans l'image
input_label = np.array([1])  # 1=foreground, 0=background
masks, scores, logits = predictor.predict(
    point_coords=input_point,
    point_labels=input_label,
    multimask_output=True
)

# Plus grande confiance
mask = masks[scores.argmax()]
```

## Estimation de Pose 3D (PnP)

### Solveur PnP (Perspective-n-Point)
```python
def estimate_pose_pnp(keypoints_2d, keypoints_3d, camera_matrix, dist_coeffs):
    """
    Estime la pose [R|t] d'un objet à partir de correspondances 2D-3D
    keypoints_2d : points image [N×2]
    keypoints_3d : points modèle 3D [N×3]
    """
    success, rvec, tvec, inliers = cv2.solvePnPRansac(
        keypoints_3d, keypoints_2d, camera_matrix, dist_coeffs,
        iterationsCount=100, reprojectionError=8.0, confidence=0.99
    )

    if success:
        R, _ = cv2.Rodrigues(rvec)  # rotation vector → matrix
        return R, tvec, inliers
    return None, None, None

# Transformation homogène
def pose_to_transform(R, t):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t.flatten()
    return T
```

### PoseCNN — Détection + Pose 6-DOF
```python
# Utilisation via BOP toolkit (Benchmark for 6D Object Pose Estimation)
# Inference du modèle PoseCNN ou GDR-Net
from bop_toolkit_lib import inout

# Format standard BOP
pose_gt = inout.load_pose('path/to/pose.txt')
# pose 4×4 ∈ SE(3)

# Métrique d'évaluation
def compute_add(pose_est, pose_gt, model_points):
    """
    ADD : Average Distance of Model Points
    ADD-S : avec symétrie (objets symétriques)
    """
    # Transforme les points du modèle avec les deux poses
    est = (pose_est[:3, :3] @ model_points.T + pose_est[:3, 3:4]).T
    gt  = (pose_gt[:3, :3] @ model_points.T + pose_gt[:3, 3:4]).T

    # Distance moyenne entre les points correspondants
    dists = np.linalg.norm(est - gt, axis=1)
    return np.mean(dists)  # ADD < seuil (souvent 10% du diamètre) = correct
```

## Fusion de Capteurs (Sensor Fusion)

### Kalman Filter Multi-capteurs
```python
class SensorFusionKalman:
    """
    Fusionne : odométrie + IMU + GPS + LiDAR
    État : [x, y, θ, v, ω]^T
    """
    def __init__(self):
        # État
        self.x = np.zeros(5)
        self.P = np.eye(5) * 100.0

        # Matrices
        self.F = np.array([
            [1, 0, 0, 1, 0],
            [0, 1, 0, 0, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1]
        ])  # modèle de mouvement
        self.Q = np.eye(5) * 0.01  # bruit de procédé

    def predict(self, u, dt):
        """u = [v_cmd, ω_cmd]"""
        v, omega = u
        theta = self.x[2]
        self.x[0] += v * np.cos(theta) * dt
        self.x[1] += v * np.sin(theta) * dt
        self.x[2] += omega * dt
        self.x[3] = v
        self.x[4] = omega

        # Jacobienne du modèle non-linéaire
        G = np.eye(5)
        G[0, 2] = -v * np.sin(theta) * dt
        G[1, 2] = v * np.cos(theta) * dt
        self.P = G @ self.P @ G.T + self.Q

    def update_odometry(self, z_odom, R_odom):
        """Mise à jour depuis l'odométrie des roues"""
        H = np.eye(5)
        K = self.P @ H.T @ np.linalg.inv(H @ self.P @ H.T + R_odom)
        self.x += K @ (z_odom - H @ self.x)
        self.P = (np.eye(5) - K @ H) @ self.P

    def update_gps(self, z_gps, R_gps):
        """Mise à jour GPS (x, y uniquement)"""
        H = np.array([[1, 0, 0, 0, 0],
                      [0, 1, 0, 0, 0]])
        y = z_gps - H @ self.x
        S = H @ self.P @ H.T + R_gps
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x += K @ y
        self.P = (np.eye(5) - K @ H) @ self.P

    def update_scan_match(self, z_scan, R_scan):
        """Mise à jour scan matching (LiDAR ICP)"""
        # z_scan = [dx, dy, dθ] depuis scan matching
        H = np.eye(3, 5)
        y = z_scan - H @ self.x
        S = H @ self.P @ H.T + R_scan
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x += K @ y
        self.P = (np.eye(5) - K @ H) @ self.P
```

### Calibration Caméra-LiDAR (Extrinsics)
```python
def calibrate_camera_lidar(
    camera_matrix, dist_coeffs,
    image, point_cloud,
    checkerboard_size=(9, 6), square_size=0.025
):
    """
    Calibration extrinsèque Caméra ↔ LiDAR
    Trouve la transformation T_lidar^camera (4×4)
    """
    import cv2
    from scipy.optimize import minimize

    # 1. Détection des coins d'échiquier dans l'image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)
    if not ret:
        return None

    # 2. Extraction du plan du checkerboard dans le nuage LiDAR
    # Segmentation RANSAC du plan
    from sklearn.linear_model import RANSACRegressor

    # 3. Optimisation de la transformation
    def projection_error(T_params):
        T = T_params.reshape(4, 4)
        # Projeter les points LiDAR sur le plan du checkerboard (caméra)
        # Erreur de reprojection des points au sol
        return error

    result = minimize(projection_error, T_init, method='BFGS')
    return result.x.reshape(4, 4)  # T_lidar_camera
```

## LiDAR 3D — Traitement

### Point Cloud Processing (Open3D / PCL)
```python
import open3d as o3d

# Chargement
pcd = o3d.io.read_point_cloud('scan.pcd')
print(f"Points: {len(pcd.points)}")

# Filtrage (voxel downsampling)
pcd_down = pcd.voxel_down_sample(voxel_size=0.05)

# Suppression du plan du sol (RANSAC)
plane_model, inliers = pcd_down.segment_plane(
    distance_threshold=0.01, ransac_n=3, num_iterations=1000
)
pcd_objects = pcd_down.select_by_index(inliers, invert=True)

# Clustering (DBSCAN / Euclidean Clustering)
labels = pcd_objects.cluster_dbscan(eps=0.1, min_points=10)
max_label = labels.max()
print(f"Nombre d'objets : {max_label+1}")

# Bounding boxes pour détection
geometries = []
for i in range(max_label+1):
    obj = pcd_objects.select_by_index(np.where(labels == i)[0])
    bbox = obj.get_axis_aligned_bounding_box()
    bbox.color = (1, 0, 0)  # rouge
    geometries.append(bbox)
    # Centre de l'objet
    center = obj.get_center()
    print(f"Objet {i}: centre={center}, points={len(obj.points)}")

# Visualisation
o3d.visualization.draw_geometries([pcd_objects] + geometries)
```

### ICP (Iterative Closest Point) — Registration
```python
def icp_registration(source, target, max_correspondence=0.1):
    """ICP point-to-plane pour aligner deux nuages"""
    # Préparation
    source_down = source.voxel_down_sample(0.02)
    target_down = target.voxel_down_sample(0.02)
    source_down.estimate_normals()
    target_down.estimate_normals()

    # ICP point-to-plane
    reg_p2p = o3d.pipelines.registration.registration_icp(
        source_down, target_down, max_correspondence,
        np.eye(4),  # initial guess
        o3d.pipelines.registration.TransformationEstimationPointToPlane(),
        o3d.pipelines.registration.ICPConvergenceCriteria(
            max_iteration=200, relative_fitness=1e-6, relative_rmse=1e-6
        )
    )

    # Évaluation
    return reg_p2p.transformation, reg_p2p.fitness, reg_p2p.inlier_rmse
```

## Reconstruction 3D — RGB-D / TSDF

### Truncated Signed Distance Function (TSDF)
```python
import open3d as o3d

class TSDFVolume:
    """Reconstruction 3D à partir de flux RGB-D (KinectFusion-style)"""
    def __init__(self, volume_size=3.0, voxel_size=0.005):
        self.volume = o3d.pipelines.integration.ScalableTSDFVolume(
            voxel_length=voxel_size,
            sdf_trunc=0.04,
            color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8
        )

    def integrate_frame(self, color_image, depth_image, intrinsic, pose):
        """Intègre une frame RGB-D dans le volume TSDF"""
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color_image, depth_image,
            depth_trunc=4.0,
            convert_rgb_to_intensity=False
        )
        self.volume.integrate(rgbd, intrinsic, pose)

    def extract_mesh(self):
        """Extrait le maillage par marching cubes"""
        mesh = self.volume.extract_triangle_mesh()
        mesh.compute_vertex_normals()
        return mesh
```

## Deep Learning pour Perception Robotique

### Architectures Clés
```python
# ResNet / EfficientNet — backbone extraction de features
model = torchvision.models.resnet50(pretrained=True)
# Remove classification head
features = torch.nn.Sequential(*list(model.children())[:-2])

# Feature Pyramid Network (FPN) — détection multi-échelle
# Utile pour robots mobiles (objets proches/lointains)

# U-Net — segmentation dense (semantic/instance)
import segmentation_models_pytorch as smp
model = smp.Unet('resnet34', encoder_weights='imagenet', classes=21)

# DeepLabV3+ — segmentation sémantique état-de-l'art
model = smp.DeepLabV3Plus('efficientnet-b4', classes=num_classes)
```

### Détection 3D (PointPillars, VoxelNet)
```python
# PointPillars : points → pillars (colonnes) → 2D CNN → détection
# Format : nuage de points (N×4 : x, y, z, reflectance)

# Utilisation via MMDetection3D
import mmdet3d

config = 'configs/pointpillars/pointpillars_hv_secfpn_8xb6-160e_kitti-3d-car.py'
checkpoint = 'pointpillars_kitti.pth'
model = mmdet3d.init_model(config, checkpoint, device='cuda')

results = model.infer('point_cloud.bin')
# 3D bboxes : [x, y, z, w, l, h, θ]
# Scores + classes (piéton, véhicule, cycliste)
```

## RGB-Depth — Projection et Nuage de Points

```python
def depth_to_pointcloud(depth_image, camera_matrix, rgb_image=None):
    """
    Convertit une image de profondeur en nuage de points 3D
    depth_image : array (H×W), depth en mètres
    camera_matrix : K 3×3
    """
    h, w = depth_image.shape
    fx = camera_matrix[0, 0]
    fy = camera_matrix[1, 1]
    cx = camera_matrix[0, 2]
    cy = camera_matrix[1, 2]

    # Grille de pixels (u, v)
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    z = depth_image

    # Back-projection
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy

    # Concaténer en points 3D
    points = np.stack([x, y, z], axis=-1)  # (H, W, 3)

    # Filtrer les points invalides (z=0 ou NaN)
    valid = (z > 0.1) & (z < 10.0) & ~np.isnan(z)
    points_valid = points[valid]

    if rgb_image is not None:
        colors = rgb_image[valid] / 255.0
    else:
        colors = None

    return points_valid, colors
```

## Pièges et Bonnes Pratiques

- **Calibration caméra** : une seule calibration ne suffit pas si la caméra est re-fixée ou (dé)focalisée. Recalibrer après tout changement mécanique. Vérifier la reprojection error (< 0.5 px).
- **Détection en environnement industriel** : métal brillant, verre, surfaces réfléchissantes → profondeur RGB-D bruitée (holes). Fusionner plusieurs vues ou utiliser un LiDAR pour ces surfaces.
- **Sync temporelle** : Caméra @30fps ≠ LiDAR @10Hz ≠ IMU @200Hz. Toujours timestamp et interpoler. Utiliser le buffer ROS2 TimeSynchronizer.
- **YOLO sur GPU embarqué** : passer à YOLOv8-nano + TensorRT (INT8) pour inference en temps réel sur Jetson (30+ fps). Quantification FP16 sur GPU.
- **ICP divergence** : si l'initial guess est mauvais, ICP converge vers un minimum local. Utiliser des descripteurs globaux (FPFH, RANSAC initial alignment) avant ICP fin.
- **Pose estimation avec objets symétriques** : ADD-S au lieu de ADD pour l'évaluation. Utiliser aussi le degré de symétrie pour pondérer l'erreur (≥3 rotations discrètes).
- **Segment Anything pour robotique** : SAM est lent (≥1s par image). Utiliser SAM2 (vidéo, plus rapide) ou FastSAM. Pour temps réel, préférer Mask R-CNN.

## Références

- Hartley, R. & Zisserman, A. (2004). *Multiple View Geometry in Computer Vision*. Cambridge. ISBN 978-0521540513
- Szeliski, R. (2010). *Computer Vision: Algorithms and Applications*. Springer. ISBN 978-1848829343
- Newcombe, R.A. et al. (2011). KinectFusion: Real-Time 3D Reconstruction and Interaction. *ISMAR 2011*.
- Redmon, J. & Farhadi, A. (2018). YOLOv3: An Incremental Improvement. *arXiv:1804.02767*.
- Zhou, Y. & Tuzel, O. (2018). VoxelNet: End-to-End Learning for Point Cloud Based 3D Object Detection. *CVPR 2018*.
- Lang, A. et al. (2019). PointPillars: Fast Encoders for Object Detection from Point Clouds. *CVPR 2019*.
- Carion, N. et al. (2020). End-to-End Object Detection with Transformers (DETR). *ECCV 2020*.
- Kirillov, A. et al. (2023). Segment Anything (SAM). *ICCV 2023*.