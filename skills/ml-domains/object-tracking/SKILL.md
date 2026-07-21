---
name: object-tracking
description: Suivi d'objets (Object Tracking) — SORT, DeepSORT, ByteTrack, BoT-SORT, OC-SORT, MOT, tracking multi-caméra, Kalman, ré-identification. En français.

---

# Object Tracking — Suivi d'Objets

Tracking = assigner des ID uniques à des objets détectés à travers les frames vidéo. Problèmes : occlusions, réapparitions, mouvements rapides, objets identiques.

---

## 1. Taxonomie du Tracking

```
Tracking d'Objets
├── Tracking par Détection (Tracking-by-Detection)
│   ├── SORT              (Kalman + IoU, 2016)
│   ├── DeepSORT          (SORT + ReID, 2017)
│   ├── ByteTrack         (BYTE association, 2022)
│   ├── BoT-SORT          (SORT + Camera Motion, 2022)
│   ├── OC-SORT           (Observation-Centric, 2023)
│   └── StrongSORT        (DeepSORT + améliorations, 2023)
│
├── Tracking One-Shot (Joint Detection & Tracking)
│   ├── FairMOT           (CentreNet + ReID)
│   ├── TrackFormer       (Transformer)
│   ├── MOTR              (DETR-based)
│   └── DanceTrack        (Danse)
│
├── Tracking Visuel (Single Object)
│   ├── KCF, CSRT, MOSSE  (OpenCV classique)
│   └── SiamRPN, TransT   (Deep Learning)
│
└── Multi-Camera Tracking
    ├── Cross-camera ReID
    └── Global ID Fusion
```

---

## 2. Filtre de Kalman (Cœur du Tracking)

```python
import numpy as np
from filterpy.kalman import KalmanFilter

class KalmanBoxTracker:
    """
    Filtre de Kalman 8D pour un objet.
    État : [x, y, s, r, x', y', s']
    - x, y : centre de la boîte
    - s    : surface (w * h)
    - r    : ratio hauteur/largeur
    - x', y', s' : vitesses
    """
    def __init__(self, bbox):
        # bbox = [x1, y1, x2, y2]
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
        ])  # Matrice de transition
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
        ])  # Matrice d'observation
        self.kf.R[2:, 2:] *= 10.     # Bruit de mesure
        self.kf.P[4:, 4:] *= 1000.   # Incertitude initiale haute
        self.kf.P *= 10.
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[4:, 4:] *= 0.01
        
        self.kf.x[:4] = self._bbox_to_z(bbox)
        self.time_since_update = 0
        self.hits = 0
        self.id = KalmanBoxTracker._count
        KalmanBoxTracker._count += 1
    
    def update(self, bbox):
        self.time_since_update = 0
        self.hits += 1
        self.kf.update(self._bbox_to_z(bbox))
    
    def predict(self):
        if (self.kf.x[6] + self.kf.x[2]) <= 0:
            self.kf.x[6] *= 0.0
        self.kf.predict()
        self.time_since_update += 1
        return self._x_to_bbox()
    
    def _bbox_to_z(self, bbox):
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        return np.array([bbox[0] + w/2, bbox[1] + h/2, w * h, w / h]).reshape(4, 1)
    
    def _x_to_bbox(self):
        x, y, s, r = self.kf.x[:4].flatten()
        w = np.sqrt(s * r)
        h = s / w
        return [x - w/2, y - h/2, x + w/2, y + h/2]

KalmanBoxTracker._count = 0
```

---

## 3. SORT (Simple Online Realtime Tracking)

```python
from collections import defaultdict
import numpy as np
from scipy.optimize import linear_sum_assignment

class Sort:
    """SORT : Simple Online and Realtime Tracking"""
    def __init__(self, max_age=30, min_hits=3, iou_threshold=0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []
        self.frame_count = 0
    
    def update(self, detections):
        """
        detections : liste de [x1, y1, x2, y2, score]
        Retourne : [x1, y1, x2, y2, track_id]
        """
        self.frame_count += 1
        
        # Prédire les positions des trackers existants
        for tracker in self.trackers:
            tracker.predict()
        
        # Appariement (Hungarian algorithm)
        matched, unmatched_dets, unmatched_trks = self._associate(detections)
        
        # Mettre à jour les trackers matchés
        for match in matched:
            track_idx, det_idx = match
            self.trackers[track_idx].update(detections[det_idx])
        
        # Créer de nouveaux trackers
        for det_idx in unmatched_dets:
            tracker = KalmanBoxTracker(detections[det_idx])
            self.trackers.append(tracker)
        
        # Supprimer les trackers morts
        active_trackers = []
        results = []
        for tracker in self.trackers:
            if tracker.time_since_update > self.max_age:
                continue
            if tracker.hits < self.min_hits and self.frame_count > self.min_hits:
                continue
            active_trackers.append(tracker)
            # Résultat : [x1, y1, x2, y2, tracker.id]
            bbox = tracker.get_state()
            results.append([*bbox, tracker.id])
        
        self.trackers = active_trackers
        return results
    
    def _associate(self, detections):
        """Appariement par IoU + Hungarian Algorithm"""
        if not self.trackers:
            return [], list(range(len(detections))), []
        
        # Matrice IoU
        iou_matrix = np.zeros((len(self.trackers), len(detections)))
        for t, tracker in enumerate(self.trackers):
            for d, det in enumerate(detections):
                iou_matrix[t, d] = self._iou(tracker.get_state(), det)
        
        # Hungarian
        row_ind, col_ind = linear_sum_assignment(-iou_matrix)
        matched = []
        unmatched_dets = list(range(len(detections)))
        unmatched_trks = list(range(len(self.trackers)))
        
        for t, d in zip(row_ind, col_ind):
            if iou_matrix[t, d] < self.iou_threshold:
                continue
            matched.append((t, d))
            unmatched_dets.remove(d)
            unmatched_trks.remove(t)
        
        return matched, unmatched_dets, unmatched_trks
    
    def _iou(self, bbox1, bbox2):
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        return inter / (area1 + area2 - inter + 1e-6)
```

---

## 4. DeepSORT (SORT + Ré-Identification)

```python
import torch
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image

class ReIDNet(nn.Module):
    """Extracteur de features pour ré-identification"""
    def __init__(self, feature_dim=128):
        super().__init__()
        # Backbone : ResNet50 tronqué
        from torchvision.models import resnet50
        backbone = resnet50(pretrained=True)
        self.backbone = nn.Sequential(*list(backbone.children())[:-2])
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(2048, feature_dim)
        self.bn = nn.BatchNorm1d(feature_dim)
    
    def forward(self, x):
        x = self.backbone(x)
        x = self.gap(x).flatten(1)
        x = self.fc(x)
        x = self.bn(x)
        return nn.functional.normalize(x, dim=1)

class DeepSort:
    def __init__(self, reid_model_path, max_dist=0.2, max_age=30, nn_budget=100):
        self.reid = ReIDNet()
        self.reid.load_state_dict(torch.load(reid_model_path))
        self.reid.eval().cuda()
        self.max_dist = max_dist
        self.max_age = max_age
        self.nn_budget = nn_budget
        self.trackers = []
        self.frame_count = 0
        self.transform = T.Compose([
            T.Resize((256, 128)),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
    
    def extract_features(self, frame, bbox):
        x1, y1, x2, y2 = map(int, bbox)
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return None
        crop = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        crop = self.transform(crop).unsqueeze(0).cuda()
        with torch.no_grad():
            features = self.reid(crop)
        return features[0].cpu().numpy()
    
    def _associate(self, detections, features):
        """Appariement par distance cosinus + Mahalanobis + Hungarian"""
        # Matrice de coût (distance cosinus + porte IoU)
        cost_matrix = np.zeros((len(self.trackers), len(detections)))
        for t, tracker in enumerate(self.trackers):
            for d, feat in enumerate(features):
                # Distance cosinus des features
                cos_dist = np.dot(tracker.features, feat) / (
                    np.linalg.norm(tracker.features) * np.linalg.norm(feat))
                cost_matrix[t, d] = 1 - cos_dist
        
        # Gate de Mahalanobis (Kalman)
        # ...
        
        # Hungarian
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        matched = []
        unmatched_dets = []
        for t, d in zip(row_ind, col_ind):
            if cost_matrix[t, d] > self.max_dist:
                unmatched_dets.append(d)
            else:
                matched.append((t, d))
        
        return matched, unmatched_dets, []
```

---

## 5. ByteTrack (BYTE Association)

```python
class ByteTrack:
    """
    ByteTrack : associe les détections faible confiance avec les trackers.
    Principe : utiliser TOUTES les détections (high + low confidence)
    en deux tours d'association.
    """
    def __init__(self, track_thresh=0.5, match_thresh=0.8, track_buffer=30):
        self.track_thresh = track_thresh  # Seuil haute confiance
        self.match_thresh = match_thresh
        self.track_buffer = track_buffer
        self.tracks = []
        self.frame_id = 0
    
    def update(self, detections):
        """
        detections : [x1, y1, x2, y2, score, class_id]
        """
        self.frame_id += 1
        activated = []
        refined = []
        lost = []
        removed = []
        
        # Séparer hautes et basses confiances
        high_dets = [d for d in detections if d[4] >= self.track_thresh]
        low_dets = [d for d in detections if d[4] < self.track_thresh]
        
        # Premier tour : associer les hautes confiances
        matches, unmatched_high, unmatched_tracks = self._associate(high_dets)
        
        # Deuxième tour : associer les basses confiances
        matches2, unmatched_low, _ = self._associate(low_dets, unmatched_tracks)
        
        # Activer les nouvelles pistes
        for idx in unmatched_high:
            track = self._create_track(high_dets[idx])
            activated.append(track)
        
        # Gérer les trackers non matchés
        for idx in unmatched_tracks:
            track = self.tracks[idx]
            if not track.is_activated:
                track.mark_lost()
                lost.append(track)
            else:
                track.mark_removed()
                removed.append(track)
        
        return activated + refined, lost, removed
```

---

## 6. BoT-SORT (avec Compensation de Mouvement Caméra)

```python
import cv2

class BotSort:
    """
    BoT-SORT : Ajoute la compensation de mouvement caméra
    (ECC ou ORB) entre les frames.
    """
    def __init__(self, use_camera_motion=True):
        self.use_camera_motion = use_camera_motion
        self.prev_frame = None
        self.ecc = cv2.findTransformECC  # Registration
    
    def compensate_motion(self, curr_frame, prev_frame):
        if prev_frame is None:
            return np.eye(2, 3)
        
        # Convertir en gris
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # Estimation de mouvement (ECC)
        warp_matrix = np.eye(2, 3, dtype=np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1e-4)
        
        try:
            _, warp_matrix = cv2.findTransformECC(
                prev_gray, curr_gray, warp_matrix,
                cv2.MOTION_EUCLIDEAN, criteria
            )
        except:
            pass
        
        return warp_matrix
    
    def warp_bbox(self, bbox, homography):
        """Appliquer la transformation à la boîte prédite"""
        # Convertir les coins en points homogènes
        x1, y1, x2, y2 = bbox
        corners = np.array([[x1, y1, 1],
                           [x2, y1, 1],
                           [x1, y2, 1],
                           [x2, y2, 1]]).T
        # Appliquer ECC (2x3) aux coins
        warped = homography @ corners[:2, :]
        return [warped[0].min(), warped[1].min(),
                warped[0].max(), warped[1].max()]
```

---

## 7. Évaluation (MOT Metrics)

```python
# MOTA (Multiple Object Tracking Accuracy)
# MOTA = 1 - (FN + FP + IDSW) / GT
#   - FN : Faux négatifs (manqués)
#   - FP : Faux positifs
#   - IDSW : Changements d'ID

# MOTP (Multiple Object Tracking Precision)
# MOTP = somme(IoU) / matches_totaux

# HOTA (Higher Order Tracking Accuracy)
# Combine détection, association, localisation

# IDF1 : F1-score au niveau des identités

# Métriques complètes
from motmetrics import metrics, io

# Format MOT Challenge
# frame, id, x1, y1, w, h, conf, class, visibility
# 1, 1, 100, 200, 50, 80, 0.95, 1, 1.0
```

### Benchmarks

| Tracker | MOTA | IDF1 | HOTA | FPS | Année |
|---------|------|------|------|-----|-------|
| SORT | 59.8 | 53.8 | 34.0 | 600+ | 2016 |
| DeepSORT | 61.4 | 62.2 | 37.6 | 40 | 2017 |
| FairMOT | 73.7 | 72.3 | 48.8 | 25 | 2021 |
| ByteTrack | 80.3 | 77.3 | 54.5 | 30 | 2022 |
| BoT-SORT | 80.5 | 78.6 | 55.0 | 25 | 2022 |
| OC-SORT | 78.0 | 77.5 | 52.4 | 30 | 2023 |
| StrongSORT | 80.9 | 80.3 | 57.0 | 20 | 2023 |

---

## 8. Pipeline Complet Tracking + Détection YOLO

```python
import cv2
import numpy as np
from ultralytics import YOLO

class TrackingPipeline:
    def __init__(self, detector="yolo11x.pt", tracker="bytetrack.yaml"):
        self.detector = YOLO(detector)
        self.tracker_config = tracker
        self.track_history = {}
    
    def process_frame(self, frame, detections_only=False):
        if detections_only:
            results = self.detector(frame, conf=0.25)
        else:
            results = self.detector.track(
                frame, conf=0.25, persist=True, tracker=self.tracker_config
            )
        
        tracks = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                track = {
                    "bbox": box.xyxy[0].tolist(),
                    "conf": float(box.conf[0]),
                    "class": int(box.cls[0]),
                    "label": result.names[int(box.cls[0])],
                }
                if box.id is not None:
                    track["id"] = int(box.id[0])
                tracks.append(track)
        
        # Historique des trajectoires
        for track in tracks:
            if "id" in track:
                tid = track["id"]
                cx = (track["bbox"][0] + track["bbox"][2]) / 2
                cy = (track["bbox"][1] + track["bbox"][3]) / 2
                if tid not in self.track_history:
                    self.track_history[tid] = []
                self.track_history[tid].append((cx, cy))
                # Garder 30 dernières positions
                if len(self.track_history[tid]) > 30:
                    self.track_history[tid].pop(0)
        
        return tracks, results[0].plot() if results else frame
    
    def process_video(self, video_path, output_path=None):
        cap = cv2.VideoCapture(video_path)
        out = None
        if output_path:
            w = int(cap.get(3))
            h = int(cap.get(4))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 
                                  int(cap.get(5)), (w, h))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            tracks, annotated = self.process_frame(frame)
            if out:
                out.write(annotated)
            cv2.imshow("Tracking", annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
```

---

## 9. Multi-Camera Tracking

```python
class MultiCameraTracker:
    """
    Fusionne les pistes de plusieurs caméras.
    Utilise la ré-identification pour associer les IDs entre caméras.
    """
    def __init__(self, num_cameras, reid_model):
        self.cameras = [TrackingPipeline() for _ in range(num_cameras)]
        self.reid = reid_model
        self.global_id_map = {}
        
    def associate_across_cameras(self, tracks_per_camera):
        """
        Associe les pistes entre caméras via ReID.
        """
        global_tracks = []
        for cam_id, tracks in enumerate(tracks_per_camera):
            for track in tracks:
                if track["id"] in self.global_id_map:
                    track["global_id"] = self.global_id_map[track["id"]]
                else:
                    # Chercher correspondance ReID
                    matched = self.find_reid_match(track["features"], global_tracks)
                    if matched is not None:
                        track["global_id"] = matched
                    else:
                        track["global_id"] = len(self.global_id_map)
                        self.global_id_map[track["id"]] = track["global_id"]
                global_tracks.append(track)
        return global_tracks
```

---

## Références
- SORT : https://github.com/abewley/sort
- DeepSORT : https://github.com/nwojke/deep_sort
- ByteTrack : https://github.com/ifzhang/ByteTrack
- BoT-SORT : https://github.com/NirAharon/BoT-SORT
- OC-SORT : https://github.com/noahcao/OC_SORT
- MOT Challenge : https://motchallenge.net/
- BoxMOT : https://github.com/mikel-brostrom/yolo_tracking