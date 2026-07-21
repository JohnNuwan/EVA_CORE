---
name: computer-vision
description: Guide complet de Computer Vision — CNN, segmentation, détection, GANs, ViT, diffusion, 3D vision, tracking, OCR, et pipelines modernes. En français.

---

# Computer Vision — Guide Complet (Français)

Vision par ordinateur : des fondamentaux aux modèles modernes (ViT, diffusion, SAM).

---

## 1. Concepts Fondamentaux

### Pipeline classique
```
Image → Prétraitement → Features → Modèle → Prédiction
         (resize,        (HOG,     (CNN,
          normalize)      SIFT)     ViT)
```

### Tâches principales
- **Classification** : quelle classe ? (ResNet, ViT, ConvNeXt)
- **Détection** : où sont les objets ? (YOLO, Faster R-CNN, DETR)
- **Segmentation** : quels pixels pour chaque objet ? (Mask R-CNN, SAM, UNet)
- **Génération** : créer des images (GAN, VAE, Diffusion)
- **Tracking** : suivre un objet dans le temps
- **Reconstruction 3D** : estimer la profondeur / structure 3D
- **OCR** : reconnaissance de texte

---

## 2. Traitement d'Images (OpenCV)

```python
import cv2
import numpy as np

# Chargement
img = cv2.imread("image.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Redimensionnement
img = cv2.resize(img, (224, 224))
img = cv2.resize(img, None, fx=0.5, fy=0.5)

# Filtres
blur = cv2.GaussianBlur(img, (5, 5), 0)
edges = cv2.Canny(img, 100, 200)
median = cv2.medianBlur(img, 5)

# Morphologie
kernel = np.ones((5, 5), np.uint8)
dilated = cv2.dilate(edges, kernel, iterations=1)
eroded = cv2.erode(edges, kernel, iterations=1)
opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

# Seuillage
_, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
thresh = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, 11, 2,
)

# Contours
contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
```

---

## 3. Classification (CNN Modernes)

```python
import torch
import torchvision.models as models
from torchvision import transforms
import timm  # PyTorch Image Models

# ResNet pré-entraîné
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
model.eval()

# ConvNeXt
model = models.convnext_tiny(weights="IMAGENET1K_V1")

# ViT (Vision Transformer)
model = models.vit_b_16(weights="IMAGENET1K_V1")

# Avec timm (700+ modèles)
model = timm.create_model("efficientnet_b3", pretrained=True)

# Inférence
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

img = transform(image).unsqueeze(0)
with torch.no_grad():
    predictions = model(img)
```

---

## 4. Détection d'Objets

### YOLO (Ultralytics)

```python
from ultralytics import YOLO

# Entraînement
model = YOLO("yolov8n.pt")  # Charger pré-entraîné
results = model.train(
    data="dataset.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
)

# Inférence
results = model("image.jpg")
for result in results:
    boxes = result.boxes.xyxy    # Coordonnées [x1, y1, x2, y2]
    confs = result.boxes.conf    # Confiance
    classes = result.boxes.cls   # Classes
```

### DETR (Detection Transformer)

```python
from transformers import DetrImageProcessor, DetrForObjectDetection

processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)

# Post-traitement
target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(
    outputs, target_sizes=target_sizes, threshold=0.9
)
```

---

## 5. Segmentation

### SAM (Segment Anything Model)

```python
from segment_anything import sam_model_registry, SamPredictor

sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h.pth")
predictor = SamPredictor(sam)

predictor.set_image(image)

# Segmentation par points
masks, scores, _ = predictor.predict(
    point_coords=np.array([[x, y]]),
    point_labels=np.array([1]),  # 1 = foreground
    multimask_output=True,
)

# Meilleur masque
best_mask = masks[np.argmax(scores)]

# Segmentation par boîte
masks, _, _ = predictor.predict(
    box=np.array([x1, y1, x2, y2]),
    multimask_output=False,
)
```

### UNet (Segmentation sémantique)

```python
import segmentation_models_pytorch as smp

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights="imagenet",
    in_channels=3,
    classes=1,  # Segmentation binaire
)

model = smp.DeepLabV3Plus(
    encoder_name="efficientnet-b3",
    classes=21,
)
```

---

## 6. Modèles de Diffusion

### Stable Diffusion

```python
from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-1",
    torch_dtype=torch.float16,
)
pipe = pipe.to("cuda")

image = pipe(
    "Une maison futuriste au coucher du soleil",
    num_inference_steps=50,
    guidance_scale=7.5,
).images[0]
```

### Contrôle (ControlNet)

```python
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/sd-controlnet-canny"
)
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    controlnet=controlnet,
)

# Conditionner sur une carte de contours
image = pipe(
    prompt="Un château médiéval",
    image=canny_image,  # Image canny comme conditionnement
).images[0]
```

---

## 7. GANs

```python
# Générateur simple
class Generator(nn.Module):
    def __init__(self, latent_dim=100, img_shape=(3, 64, 64)):
        super().__init__()
        self.model = nn.Sequential(
            # latent_dim → 64*64*3
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, int(np.prod(img_shape))),
            nn.Tanh(),
        )
    
    def forward(self, z):
        return self.model(z).view(z.size(0), *img_shape)


# Entraînement GAN (boucle)
for epoch in range(epochs):
    for real_imgs in dataloader:
        # Entraîner le discriminateur
        z = torch.randn(batch_size, latent_dim)
        fake_imgs = generator(z)
        
        # Entraîner le générateur
        z = torch.randn(batch_size, latent_dim)
        fake_imgs = generator(z)
        g_loss = adversarial_loss(discriminator(fake_imgs), valid)
```

---

## 8. Multimodal (CLIP, BLIP)

```python
import open_clip

# CLIP (texte ↔ image)
model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32", pretrained="laion2b_s34b_b79k"
)
tokenizer = open_clip.get_tokenizer("ViT-B-32")

image = preprocess(Image.open("photo.jpg")).unsqueeze(0)
text = tokenizer(["un chat", "un chien", "une voiture"])

with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)
    similarity = (image_features @ text_features.T).softmax(dim=-1)
```

---

## 9. Pipelines de Production

```python
# TorchServe (déploiement)
# handler.py
class VisionHandler:
    def preprocess(self, data):
        image = data[0].get("data")
        image = Image.open(io.BytesIO(image))
        return transform(image).unsqueeze(0)
    
    def inference(self, inputs):
        with torch.no_grad():
            return model(inputs)
    
    def postprocess(self, outputs):
        return outputs.softmax(dim=1).tolist()

# ONNX Runtime
import onnxruntime as ort
session = ort.InferenceSession("model.onnx")
outputs = session.run(None, {"input": input_array})
```

---

## Références
- OpenCV : https://docs.opencv.org/
- Ultralytics : https://docs.ultralytics.com/
- HuggingFace Diffusers : https://huggingface.co/docs/diffusers/
- timm : https://huggingface.co/docs/timm/
- SAM : https://segment-anything.com/