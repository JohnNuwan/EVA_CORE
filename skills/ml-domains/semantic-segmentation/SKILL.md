---
name: semantic-segmentation
description: Segmentation sémantique et d'instance — UNet, DeepLab, Mask R-CNN, SAM, YOLO-seg, Panoptic FPN, datasets, entraînement, déploiement. En français.

---

# Segmentation — Sémantique, d'Instance et Panoptique

Segmentation = classification pixel par pixel. Trois niveaux : sémantique (même classe = même couleur), instance (chaque objet distinct), panoptique (les deux combinés).

---

## 1. Types de Segmentation

```
Segmentation Sémantique       Segmentation d'Instance       Segmentation Panoptique
┌──────────────┐             ┌──────────────┐              ┌──────────────┐
│░░░░ ████ ░░░░│             │░░░░ AAAA ░░░░│              │░░░░ AAAA ░░░░│
│░░ ████████ ░░│             │░ AAAAAAAA ░░░│              │░ AAAAAAAA ░░░│
│░░ ████████ ░░│             │░░ AAAA BBBB ░│              │░░ AAAA ░░░░░░│
│░░░░ ████ ░░░░│             │░░░░ ████ BBBB│              │░░░░ ████ BBBB│
└──────────────┘             └──────────────┘              └──────────────┘
Tous les pixels              Chaque objet                  Stuff + Things
"voiture" = rouge             A=voiture1, B=voiture2       (ciel, route, voitures)
```

---

## 2. Architectures Clés

### UNet (Biomedical, général)

```python
import torch
import torch.nn as nn

class UNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=1):
        super().__init__()
        # Encodeur (contracting path)
        self.enc1 = self.double_conv(in_channels, 64)
        self.enc2 = self.double_conv(64, 128)
        self.enc3 = self.double_conv(128, 256)
        self.enc4 = self.double_conv(256, 512)
        self.pool = nn.MaxPool2d(2)
        
        # Bottleneck
        self.bottleneck = self.double_conv(512, 1024)
        
        # Décodeur (expansive path)
        self.up4 = nn.ConvTranspose2d(1024, 512, 2, 2)
        self.dec4 = self.double_conv(1024, 512)
        self.up3 = nn.ConvTranspose2d(512, 256, 2, 2)
        self.dec3 = self.double_conv(512, 256)
        self.up2 = nn.ConvTranspose2d(256, 128, 2, 2)
        self.dec2 = self.double_conv(256, 128)
        self.up1 = nn.ConvTranspose2d(128, 64, 2, 2)
        self.dec1 = self.double_conv(128, 64)
        self.out = nn.Conv2d(64, out_channels, 1)
    
    def double_conv(self, in_c, out_c):
        return nn.Sequential(
            nn.Conv2d(in_c, out_c, 3, padding=1),
            nn.BatchNorm2d(out_c),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_c, out_c, 3, padding=1),
            nn.BatchNorm2d(out_c),
            nn.ReLU(inplace=True),
        )
    
    def forward(self, x):
        # Encode
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))
        b = self.bottleneck(self.pool(e4))
        # Decode
        d4 = self.dec4(torch.cat([self.up4(b), e4], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.out(d1)
```

### DeepLabV3+ (Atrous Spatial Pyramid Pooling)

```python
# Avec segmentation_models_pytorch
import segmentation_models_pytorch as smp

# DeepLabV3+
model = smp.DeepLabV3Plus(
    encoder_name="efficientnet-b3",      # Backbone
    encoder_weights="imagenet",           # Poids pré-entraînés
    in_channels=3,
    classes=21,                           # COCO
    activation="softmax",                 # ou "sigmoid" pour binaire
)

# DeepLabV3
model = smp.DeepLabV3(encoder_name="resnet101", encoder_weights="imagenet", classes=21)

# UNet avec différents backbones
model = smp.Unet(encoder_name="resnet34", encoder_weights="imagenet", classes=1)
model = smp.UnetPlusPlus(encoder_name="timm-efficientnet-b0", classes=21)

# FPN (Feature Pyramid Network)
model = smp.FPN(encoder_name="resnet50", encoder_weights="imagenet", classes=21)

# PSPNet
model = smp.PSPNet(encoder_name="resnet50", encoder_weights="imagenet", classes=21)

# MAnet
model = smp.MAnet(encoder_name="resnet50", encoder_weights="imagenet", classes=21)

# Linknet
model = smp.Linknet(encoder_name="resnet50", encoder_weights="imagenet", classes=21)
```

### Mask R-CNN (Instance Segmentation)

```python
import torchvision
from torchvision.models.detection import maskrcnn_resnet50_fpn

model = maskrcnn_resnet50_fpn(weights="COCO_V1")
model.eval()

# Inférence
with torch.no_grad():
    predictions = model([image_tensor])

# Résultats
for pred in predictions:
    boxes = pred['boxes']       # [N, 4]
    labels = pred['labels']     # [N]
    scores = pred['scores']     # [N]
    masks = pred['masks']       # [N, 1, H, W]
```

---

## 3. SAM — Segment Anything Model (Meta)

```python
from segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator

# Charger
sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
sam.to("cuda")

# Prédicteur manuel (points, boxes)
predictor = SamPredictor(sam)
predictor.set_image(image_np)

# Par points
masks, scores, logits = predictor.predict(
    point_coords=np.array([[x, y], [x2, y2]]),
    point_labels=np.array([1, 0]),  # 1=foreground, 0=background
    multimask_output=True,          # Top 3 masques
)

# Par boîte
masks, scores, _ = predictor.predict(
    box=np.array([x1, y1, x2, y2]),
    multimask_output=False,
)

# Générateur automatique
mask_generator = SamAutomaticMaskGenerator(
    sam,
    points_per_side=16,          # Grille de points
    pred_iou_thresh=0.86,        # Seuil IoU prédit
    stability_score_thresh=0.92,  # Stabilité du masque
    stability_score_offset=0.5,
    box_nms_thresh=0.7,          # NMS
    crop_n_layers=0,             # Recadrage multi-échelle
    crop_nms_thresh=0.7,
    crop_overlap_ratio=0.1,
    crop_n_points_downscale_factor=1,
    min_mask_region_area=100,    # Supprimer les petites régions
)

masks = mask_generator.generate(image_np)

# Résultat SAM
for mask in masks:
    print(mask['segmentation'])  # Masque booléen (H×W)
    print(mask['area'])          # Aire en pixels
    print(mask['bbox'])          # Boîte englobante
    print(mask['predicted_iou']) # IoU prédit
    print(mask['point_coords'])  # Point de prompt
    print(mask['stability_score'])
```

### SAM 2 (Video + Image)

```python
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
from sam2.sam2_video_predictor import SAM2VideoPredictor

# Image
sam2 = build_sam2("sam2_hiera_large.yaml", "sam2_hiera_large.pt")
predictor = SAM2ImagePredictor(sam2)
predictor.set_image(image)
masks, scores, _ = predictor.predict(point_coords=np.array([[x, y]]), point_labels=np.array([1]))

# Vidéo
predictor = SAM2VideoPredictor(sam2)
with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
    state = predictor.init_state(video_path="video.mp4")
    frame_idx, object_ids, masks = predictor.add_new_points_or_box(
        inference_state=state,
        frame_idx=0,
        obj_id=1,
        points=np.array([[x, y]]),
        labels=np.array([1]),
    )
    for frame_idx, object_ids, masks in predictor.propagate_in_video(state):
        # Masques pour chaque frame
        pass
```

---

## 4. YOLO Segmentation

```python
from ultralytics import YOLO

# Modèle segmentation
model = YOLO("yolo11n-seg.pt")

# Inférence
results = model("image.jpg")
for result in results:
    # Masques
    if result.masks:
        for mask, box in zip(result.masks.data, result.boxes):
            mask_np = mask.cpu().numpy()  # (H, W) masque binaire
            x1, y1, x2, y2 = box.xyxy[0]
            cls = int(box.cls[0])
            conf = float(box.conf[0])
    
    # Image segmentée
    annotated = result.plot()

# Entraînement
model.train(
    data="dataset.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
)
```

---

## 5. Données et Datasets

### Datasets Populaires

| Dataset | Classes | Images | Type | Tâche |
|---------|---------|--------|------|-------|
| COCO | 80 | 330k | Instance | Standard |
| Cityscapes | 19 | 5k urbain | Sémantique | Urbain |
| ADE20K | 150 | 25k | Sémantique | Intérieur |
| Pascal VOC | 20 | 2k | Sémantique | Classique |
| Mapillary | 37 | 25k | Sémantique | Urbain |
| KITTI | 8 | 200 | Instance | Conduite |
| SA-1B (SAM) | 1.1B | 11M | Instance | Masques |

### Format Dataset COCO (JSON)

```json
{
  "images": [{"id": 1, "file_name": "img.jpg", "width": 640, "height": 480}],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "segmentation": [[x1, y1, x2, y2, ...]],  // Polygon
      "area": 1000,
      "bbox": [x, y, w, h],
      "iscrowd": 0
    }
  ],
  "categories": [{"id": 1, "name": "personne"}]
}
```

### Format Dataset Segmentation (PNG)

```
images/train/img001.jpg
masks/train/img001.png  # Chaque pixel = ID de classe (0, 1, 2, ...)
```

---

## 6. Entraînement Segmentation

```python
import torch
import segmentation_models_pytorch as smp
from torch.utils.data import Dataset, DataLoader
import albumentations as A

class SegmentationDataset(Dataset):
    def __init__(self, images, masks, transform=None):
        self.images = images
        self.masks = masks
        self.transform = transform
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = cv2.imread(self.images[idx])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mask = cv2.imread(self.masks[idx], 0)
        
        if self.transform:
            transformed = self.transform(image=image, mask=mask)
            image = transformed['image']
            mask = transformed['mask']
        
        image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
        mask = torch.from_numpy(mask).long()
        return image, mask

# Augmentations
transform = A.Compose([
    A.RandomResizedCrop(512, 512, scale=(0.5, 1.0)),
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.2),
    A.HueSaturationValue(p=0.2),
    A.GaussNoise(p=0.1),
    A.ElasticTransform(p=0.1),
])

# Modèle
model = smp.Unet(
    encoder_name="timm-efficientnet-b3",
    encoder_weights="imagenet",
    in_channels=3,
    classes=21,
    activation="softmax2d",
)

# Loss
criterion = smp.losses.DiceLoss(mode='multiclass')
# Ou combinaison
criterion = smp.losses.DiceLoss(mode='multiclass') + nn.CrossEntropyLoss()

# Optimiseur
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)

# Entraînement
for epoch in range(100):
    model.train()
    for images, masks in dataloader:
        images, masks = images.cuda(), masks.cuda()
        logits = model(images)
        loss = criterion(logits, masks)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

---

## 7. Métriques

```python
import torch
import numpy as np

def iou_score(pred, target, num_classes=21):
    """Intersection over Union par classe"""
    ious = []
    pred = pred.view(-1)
    target = target.view(-1)
    for cls in range(num_classes):
        pred_inds = (pred == cls)
        target_inds = (target == cls)
        intersection = (pred_inds & target_inds).sum().float()
        union = (pred_inds | target_inds).sum().float()
        if union == 0:
            ious.append(float('nan'))  # Classe absente
        else:
            ious.append(float(intersection / union))
    return ious

def dice_score(pred, target, smooth=1e-6):
    """Dice Coefficient (F1)"""
    pred = pred.contiguous().view(-1)
    target = target.contiguous().view(-1)
    intersection = (pred * target).sum()
    return (2. * intersection + smooth) / (pred.sum() + target.sum() + smooth)

def pixel_accuracy(pred, target):
    """Accuracy pixel"""
    correct = (pred == target).sum()
    total = target.numel()
    return correct.float() / total

# mIoU (Mean IoU)
miou = np.nanmean(iou_score(pred, target, num_classes=21))
```

### Métriques de Référence

| Modèle | mIoU COCO | mIoU Cityscapes | FPS |
|--------|-----------|-----------------|-----|
| UNet (ResNet34) | 55.2 | 72.5 | 45 |
| DeepLabV3+ (R101) | 62.8 | 81.3 | 25 |
| Mask R-CNN | 58.0 | 76.8 | 15 |
| YOLOv8x-seg | 55.2 | - | 120 |
| SAM (ViT-H) | - | 82.6 | 3 |
| SAM2 | - | 84.1 | 6 |

---

## 8. Segmentation Panoptique

```python
from detectron2.config import get_cfg
from detectron2.modeling import build_model
from detectron2.checkpoint import DetectionCheckpointer

# PanopticFPN (Detectron2)
cfg = get_cfg()
cfg.merge_from_file("detectron2/configs/COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml")
cfg.MODEL.WEIGHTS = "model_final.pth"
model = build_model(cfg)
DetectionCheckpointer(model).load(cfg.MODEL.WEIGHTS)

# Inférence
with torch.no_grad():
    outputs = model([image])
    panoptic_seg, segments_info = outputs["panoptic_seg"]
    # segments_info = [{'id': 0, 'isthing': True, 'category_id': 3}, ...]
```

---

## 9. Post-Traitement

```python
import cv2
import numpy as np

# CRF (Conditional Random Fields) — Affiner les bords
import pydensecrf.densecrf as dcrf
from pydensecrf.utils import unary_from_softmax, create_pairwise_bilateral

def apply_crf(image, softmax_probs):
    """CRF pour lisser les prédictions"""
    h, w = image.shape[:2]
    n_labels = softmax_probs.shape[0]
    
    d = dcrf.DenseCRF2D(w, h, n_labels)
    U = unary_from_softmax(softmax_probs)
    d.setUnaryEnergy(U)
    
    d.addPairwiseGaussian(sxy=3, comp=3, kernel=dcrf.DIAG_KERNEL,
                          normalization=dcrf.NORMALIZE_SYMMETRIC)
    
    d.addPairwiseBilateral(sxy=80, srgb=13, rgbim=image,
                           kernel=dcrf.DIAG_KERNEL,
                           normalization=dcrf.NORMALIZE_SYMMETRIC)
    
    Q = d.inference(5)
    return np.argmax(Q, axis=0).reshape((h, w))

# Nettoyage des masques
def clean_mask(mask, min_area=100):
    """Supprimer les petites régions"""
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8))
    cleaned = np.zeros_like(mask)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            cleaned[labels == i] = mask[labels == i]
    return cleaned
```

---

## Références
- segmentation_models_pytorch : https://github.com/qubvel/segmentation_models.pytorch
- SAM : https://segment-anything.com/
- SAM2 : https://github.com/facebookresearch/sam2
- Detectron2 : https://github.com/facebookresearch/detectron2
- Cityscapes : https://www.cityscapes-dataset.com/
- Papers : https://paperswithcode.com/task/semantic-segmentation