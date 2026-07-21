---
name: image-classification
description: Classification d'images — ResNet, EfficientNet, ConvNeXt, ViT, Swin, architectures modernes, fine-tuning, entraînement, benchmarks ImageNet, data augmentations. En français.

---

# Classification d'Images — Architectures Modernes

De ResNet (2015) aux Vision Transformers (2024). Couvre les architectures classiques CNN, les Transformers (ViT, Swin, MaxViT), les ConvNeXt hybrides, et les pipelines d'entraînement modernes.

---

## 1. Taxonomie des Architectures

```
Classification d'Images
├── CNN Classiques
│   ├── ResNet (ResNet50, 101, 152)          — Skip connections
│   ├── DenseNet (121, 169, 201)             — Dense connections
│   ├── EfficientNet (B0-B7)                 — Compound scaling
│   └── ResNeXt (50, 101)                    — Group convolutions
│
├── CNN Modernes
│   ├── ConvNeXt (T, S, B, L)               — CNN modernisé
│   ├── EfficientNetV2 (S, M, L)             — Amélioré + Fused-MBConv
│   └── RegNet (X, Y, Z)                     — Design space
│
├── Vision Transformers
│   ├── ViT (T, S, B, L, H)                 — Patch embedding
│   ├── DeiT (T, S, B, III)                 — Data-efficient ViT
│   └── Swin (T, S, B, L)                   — Hierarchical + windows
│
└── Hybrides
    ├── MaxViT                              — MBConv + attention
    ├── CoAtNet                             — Conv + attention
    └── EfficientFormer                      — Pure ViT speed
```

---

## 2. Benchmarks ImageNet-1k

| Modèle | Top-1 | Top-5 | Params | GMACs | Résolution |
|--------|-------|-------|--------|-------|------------|
| ResNet-50 | 76.2 | 92.9 | 25.6M | 4.1 | 224 |
| EfficientNet-B3 | 81.7 | 95.7 | 12.0M | 1.8 | 300 |
| EfficientNetV2-M | 85.1 | 97.2 | 54.1M | 10.0 | 480 |
| ConvNeXt-B | 85.8 | 97.5 | 88.6M | 15.4 | 224 |
| ConvNeXt-L | 86.6 | 98.1 | 198M | 34.4 | 224 |
| ViT-B/16 | 81.1 | 95.4 | 86.6M | 55.5 | 384 |
| DeiT-III-B | 84.7 | 96.8 | 86.6M | 55.5 | 384 |
| Swin-B | 85.4 | 97.2 | 87.8M | 15.4 | 224 |
| Swin-L | 86.4 | 98.0 | 197M | 34.5 | 224 |
| MaxViT-B | 86.1 | 97.5 | 76.3M | 13.0 | 224 |
| CoAtNet-3 | 86.0 | 97.6 | 167M | 22.6 | 384 |
| EVA-02 (ViT) | 88.0 | 98.3 | 304M | 103 | 448 |

---

## 3. Implémentations (PyTorch)

```python
import torch
import torch.nn as nn
import torchvision.models as models
import timm  # PyTorch Image Models (700+ modèles)

# --- torchvision (simple, stable) ---
resnet50 = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
resnet101 = models.resnet101(weights="IMAGENET1K_V1")
resnext101 = models.resnext101_64x4d(weights="IMAGENET1K_V1")
densenet121 = models.densenet121(weights="IMAGENET1K_V1")
efficientnet_b7 = models.efficientnet_b7(weights="IMAGENET1K_V1")
convnext_base = models.convnext_base(weights="IMAGENET1K_V1")
swin_t = models.swin_t(weights="IMAGENET1K_V1")
vit_b_16 = models.vit_b_16(weights="IMAGENET1K_V1")
maxvit_t = models.maxvit_t(weights="IMAGENET1K_V1")

# --- timm (complet, recherche) ---
# EfficientNets
effnet_b3 = timm.create_model('efficientnet_b3', pretrained=True)
effnetv2_l = timm.create_model('efficientnetv2_l', pretrained=True)

# ConvNeXt
convnext_t = timm.create_model('convnext_tiny', pretrained=True)
convnext_l = timm.create_model('convnext_large', pretrained=True)

# ViT
vit_l = timm.create_model('vit_large_patch16_224', pretrained=True)
vit_h = timm.create_model('vit_huge_patch14_224', pretrained=True)

# Swin
swin_b = timm.create_model('swin_base_patch4_window7_224', pretrained=True)

# DEiT
deit_b = timm.create_model('deit_base_distilled_patch16_224', pretrained=True)

# EVA (ViT amélioré)
eva02_l = timm.create_model('eva02_large_patch14_448', pretrained=True)
```

---

## 4. Pipeline d'Entraînement Complet

```python
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
from torchvision.datasets import ImageFolder
from torch.cuda.amp import autocast, GradScaler
import wandb

# --- Transformations +++
class EfficientNetAugmentation:
    """Augmentations pour State-of-the-Art"""
    def train_transform(resize=256, crop=224):
        return T.Compose([
            T.RandomResizedCrop(crop, scale=(0.08, 1.0)),
            T.RandomHorizontalFlip(),
            T.RandAugment(num_ops=2, magnitude=9),
            T.TrivialAugmentWide(),
            T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225]),
            T.RandomErasing(p=0.25),
        ])
    
    def val_transform(resize=256, crop=224):
        return T.Compose([
            T.Resize(resize),
            T.CenterCrop(crop),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225]),
        ])

# --- Data Pipeline ---
train_dataset = ImageFolder("data/train", transform=EfficientNetAugmentation.train_transform(256, 224))
val_dataset = ImageFolder("data/val", transform=EfficientNetAugmentation.val_transform(256, 224))

train_loader = DataLoader(
    train_dataset, batch_size=256, shuffle=True,
    num_workers=8, pin_memory=True, prefetch_factor=2,
    persistent_workers=True,
)
val_loader = DataLoader(
    val_dataset, batch_size=256, shuffle=False,
    num_workers=8, pin_memory=True,
)

# --- Modèle + Optimiseur ---
model = timm.create_model('convnext_base', pretrained=True, num_classes=100)
model = model.cuda()

# Layer-wise learning rate decay (LLRD)
# Adapté du training DeiT/ConvNeXt
param_groups = []
for i, (name, param) in enumerate(model.named_parameters()):
    decay = 0.85 ** (12 - i // 4)  # Décroissance par bloc
    if 'bias' in name or 'norm' in name or 'bn' in name:
        param_groups.append({'params': param, 'weight_decay': 0.0, 'lr': 1e-4 * decay})
    else:
        param_groups.append({'params': param, 'weight_decay': 0.05, 'lr': 1e-4 * decay})

optimizer = torch.optim.AdamW(param_groups, betas=(0.9, 0.999))
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=300, eta_min=1e-6)

# Mixup / Cutmix
def mixup_data(x, y, alpha=0.8):
    """Mixup + CutMix"""
    lam = np.random.beta(alpha, alpha)
    batch_size = x.size()[0]
    index = torch.randperm(batch_size).cuda()
    mixed_x = lam * x + (1 - lam) * x[index]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam

# Loss avec label smoothing
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

# AMP
scaler = GradScaler()

# --- Boucle d'Entraînement ---
for epoch in range(300):
    model.train()
    for i, (inputs, targets) in enumerate(train_loader):
        inputs, targets = inputs.cuda(), targets.cuda()
        
        # Mixup aléatoire
        if np.random.random() < 0.5:
            inputs, targets_a, targets_b, lam = mixup_data(inputs, targets)
        
        with autocast():
            outputs = model(inputs)
            if 'mixup' in dir():
                loss = lam * criterion(outputs, targets_a) + (1 - lam) * criterion(outputs, targets_b)
            else:
                loss = criterion(outputs, targets)
        
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()
    
    scheduler.step()
    
    # Validation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs, targets = inputs.cuda(), targets.cuda()
            with autocast():
                outputs = model(inputs)
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
    
    acc = 100. * correct / total
    print(f"Epoch {epoch}: Acc={acc:.2f}%")
```

---

## 5. Fine-Tuning (Transfer Learning)

```python
import timm

# Méthodes de fine-tuning
class FineTune:
    @staticmethod
    def linear_probe(model, num_classes=100):
        """Geler tout sauf la tête de classification"""
        for param in model.parameters():
            param.requires_grad = False
        
        if hasattr(model, 'head'):
            in_features = model.head.in_features
            model.head = nn.Linear(in_features, num_classes)
        elif hasattr(model, 'fc'):
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, num_classes)
        elif hasattr(model, 'classifier'):
            if isinstance(model.classifier, nn.Linear):
                in_features = model.classifier.in_features
                model.classifier = nn.Linear(in_features, num_classes)
        
        return model
    
    @staticmethod
    def full_finetune(model, num_classes=100, lr=1e-4):
        """Fine-tuning complet"""
        # Adapter la tête
        if hasattr(model, 'head'):
            model.reset_classifier(num_classes)
        else:
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        
        # Tous les paramètres entraînables
        for param in model.parameters():
            param.requires_grad = True
        
        return model
    
    @staticmethod
    def discriminative_lrs(model, num_classes=100, base_lr=1e-4, ratio=10.0):
        """LRs différenciées : tête = base_lr, backbone = base_lr/ratio"""
        # Geler le backbone d'abord
        FineTune.linear_probe(model, num_classes)
        
        # Entraîner la tête
        head_params = []
        backbone_params = []
        for name, param in model.named_parameters():
            if 'head' in name or 'fc' in name or 'classifier' in name:
                head_params.append(param)
            else:
                backbone_params.append(param)
        
        optimizer = torch.optim.AdamW([
            {'params': head_params, 'lr': base_lr},
            {'params': backbone_params, 'lr': base_lr / ratio, 'weight_decay': 0.05},
        ])
        
        # Étape 1 : entraîner la tête seule
        # Étape 2 : dégeler et fine-tune complet
        
        return model, optimizer
```

---

## 6. Augmentations Avancées

```python
import albumentations as A
from albumentations.pytorch import ToTensorV2

# AutoAugment / RandAugment
# pip install autoalbument
from autoalbument import AutoAugment

# Timm's RandAugment (intégré)
from timm.data import rand_augment_transform
rand_aug = rand_augment_transform('rand-m9-mstd0.5', {})

# AugMix (threeM)
from timm.data import augment
augmix = augment.AugMixAugment()

# Albumentations pipeline complet
train_transform = A.Compose([
    A.RandomResizedCrop(224, 224, scale=(0.05, 1.0), p=1.0),
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=30, p=0.3),
    A.OneOf([
        A.RandomBrightnessContrast(p=0.5),
        A.HueSaturationValue(p=0.5),
        A.CLAHE(p=0.5),
    ], p=0.5),
    A.OneOf([
        A.GaussNoise(p=0.3),
        A.GaussianBlur(p=0.3),
        A.MotionBlur(p=0.3),
    ], p=0.3),
    A.CoarseDropout(max_holes=8, max_height=32, max_width=32, p=0.3),
    A.Normalize(),
    ToTensorV2(),
])

# Exemple : test-time augmentation (TTA)
def tta_inference(model, image, augmentations):
    """Test-Time Augmentation : moyenne de N prédictions augmentées"""
    predictions = []
    for aug_fn in augmentations:
        aug_img = aug_fn(image)
        with torch.no_grad():
            pred = model(aug_img.unsqueeze(0))
            predictions.append(F.softmax(pred, dim=1))
    return torch.stack(predictions).mean(dim=0)
```

---

## 7. EMA (Exponential Moving Average)

```python
class ModelEMA:
    """Exponential Moving Average des poids du modèle"""
    def __init__(self, model, decay=0.9999):
        self.ema_model = timm.utils.ModelEmaV2(model, decay=decay)
    
    def update(self, model):
        self.ema_model.update(model)
    
    def state_dict(self):
        return self.ema_model.state_dict()

# Utilisation
ema = ModelEMA(model, decay=0.9999)
for epoch in range(epochs):
    train_one_epoch(model, loader, optimizer)
    ema.update(model)

# Validation avec EMA
model_eval = ema.ema_model
validate(model_eval, val_loader)
```

---

## 8. Évaluation et Interprétation

```python
import torchcam
from torchcam.methods import GradCAM, GradCAMpp, SmoothGradCAMpp

# GradCAM
cam_extractor = GradCAMpp(model, target_layer='model.features[-1]')
with torch.no_grad():
    out = model(image.unsqueeze(0))
    activation_map = cam_extractor(out.squeeze(0).argmax().item(), out)
    cam = activation_map[0].cpu().numpy()

# Confusion Matrix
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay

y_true = []
y_pred = []
model.eval()
with torch.no_grad():
    for inputs, targets in val_loader:
        outputs = model(inputs.cuda())
        _, preds = outputs.max(1)
        y_true.extend(targets.cpu().numpy())
        y_pred.extend(preds.cpu().numpy())

cm = confusion_matrix(y_true, y_pred)
report = classification_report(y_true, y_pred, target_names=class_names)
print(report)
```

---

## 9. Distillation de Connaissances

```python
class KnowledgeDistillation:
    """Distillation d'un gros modèle (teacher) vers un petit (student)"""
    def __init__(self, teacher, student, T=3.0, alpha=0.5):
        self.teacher = teacher.eval()
        self.student = student
        self.T = T
        self.alpha = alpha
        self.kl_loss = nn.KLDivLoss(reduction='batchmean')
        self.ce_loss = nn.CrossEntropyLoss()
    
    def loss(self, student_logits, teacher_logits, targets):
        # Distillation loss (soft targets)
        soft_student = F.log_softmax(student_logits / self.T, dim=1)
        soft_teacher = F.softmax(teacher_logits / self.T, dim=1)
        distill_loss = self.kl_loss(soft_student, soft_teacher) * (self.T ** 2)
        
        # Hard loss (vraies labels)
        hard_loss = self.ce_loss(student_logits, targets)
        
        return self.alpha * hard_loss + (1 - self.alpha) * distill_loss
    
    def train_step(self, inputs, targets):
        with torch.no_grad():
            teacher_logits = self.teacher(inputs)
        student_logits = self.student(inputs)
        return self.loss(student_logits, teacher_logits, targets)
```

---

## 10. Export et Déploiement

```python
# TorchScript
model.eval()
example = torch.randn(1, 3, 224, 224)
traced = torch.jit.trace(model, example)
traced.save("model.pt")

# ONNX
import torch.onnx as onnx
onnx.export(
    model, example, "model.onnx",
    input_names=['input'], output_names=['output'],
    dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}},
    opset_version=17,
)

# CoreML (macOS)
import coremltools as ct
model.train()  # CoreML requires train mode
mlmodel = ct.convert(
    traced,
    inputs=[ct.ImageType(name="input", shape=(1, 3, 224, 224))],
)
mlmodel.save("Model.mlpackage")
```

---

## Références
- timm : https://github.com/huggingface/pytorch-image-models
- torchvision : https://pytorch.org/vision/stable/models.html
- PapersWithCode : https://paperswithcode.com/task/image-classification
- ImageNet Benchmarks : https://imagenet.stanford.edu/
- ConvNeXt : https://github.com/facebookresearch/ConvNeXt