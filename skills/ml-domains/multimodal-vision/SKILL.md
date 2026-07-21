---
name: multimodal-vision
description: Modèles vision-langage multimodaux — CLIP, BLIP-2, LLaVA, Florence-2, GPT-4V, Qwen-VL, InstructBLIP, ImageBind, pipelines, fine-tuning, benchmarks. En français.

---

# Modèles Multimodaux Vision-Langage

Modèles qui comprennent à la fois images et texte : CLIP (embeddings communs), LLaVA (chat image+texte), Florence-2 (tasks visuelles), ImageBind (6 modalités). De l'embedding à la génération.

---

## 1. Taxonomie des Modèles Multimodaux

```
Multimodal Vision-Langage
├── Embedding Conjoint (Contrastif)
│   ├── CLIP (OpenAI)            — Image + Texte contrastif
│   ├── SigLIP (Google)          — Sigmoid Loss
│   └── OpenCLIP (Community)     — LAION-5B trained
│
├── Image Captioning (Génération)
│   ├── BLIP / BLIP-2            — Bootstrapping Language-Image
│   ├── GIT (Microsoft)          — Generative Image-to-Text
│   └── Kosmos-2                 — Grounding + Captioning
│
├── Vision-Language QA (Chat)
│   ├── LLaVA (1.5, 1.6, NeXT)  — Visual Instruction Tuning
│   ├── Qwen-VL (Qwen2-VL)      — Alibaba VLM
│   ├── InstructBLIP             — BLIP-2 + instruction tuning
│   └── InternVL (1.2, 2.0)     — Vision-Language 6B-34B
│
├── Universal Vision Tasks
│   ├── Florence-2 (Microsoft)   — 16 tasks visuelles
│   └── GPT-4V (OpenAI)          — API fermée
│
└── Multi-Modalités (6+)
    └── ImageBind (Meta)         — Texte, image, audio, depth, IMU, thermal
```

---

## 2. CLIP (Contrastive Language-Image Pre-training)

### Architecture

```
Image Encoder (ViT/ResNet) ──┐
                             ├──→ Image Embeddings (I)
                             │
Texte Encoder (Transformer) ─┘
                             └──→ Text Embeddings (T)

Loss : Contrastive (InfoNCE)
max(cos(I, T))   # Images et textes appariés
min(cos(I, T'))  # Images et textes non-appariés
```

### Utilisation

```python
import torch
import open_clip

# Modèle + préparation
model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-H-14",                     # Modèle
    pretrained="laion2b_s32b_b79k", # Pré-entraînement LAION-5B
    device="cuda",
)
tokenizer = open_clip.get_tokenizer("ViT-H-14")

# Image
from PIL import Image
image = preprocess(Image.open("photo.jpg")).unsqueeze(0).cuda()

# Texte
texts = ["un chat", "un chien", "une voiture", "un paysage"]
text = tokenizer(texts).cuda()

# Forward
with torch.no_grad(), torch.cuda.amp.autocast():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)
    
    # Normaliser
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)
    
    # Similarité cosinus
    logits_per_image = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    
    # Résultat
    probs = logits_per_image[0].cpu()
    for i, (text, prob) in enumerate(zip(texts, probs)):
        print(f"{text}: {prob:.2%}")

# Zero-shot classification
# Avec les 80 classes COCO
class_names = ["personne", "vélo", "voiture", ...]
text_prompts = [f"une photo d'une {c}" for c in class_names]
```

### Modèles CLIP disponibles

```python
# open_clip (LAION)
# ViT-B-32 : 63.2% ImageNet zero-shot
# ViT-L-14 : 75.3% ImageNet zero-shot
# ViT-H-14 : 78.0% ImageNet zero-shot (meilleur)
# ConvNext-XXL : 80.1% ImageNet zero-shot

# Multi-lingual
# xlm-roberta-base-ViT-B-32 : supporte français
```

### Modèles dérivés de CLIP

```python
# SigLIP (Sigmoid Loss for Language Image Pre-training)
# Loss sigmoid au lieu de softmax = batch size plus petit
model, _, _ = open_clip.create_model_and_transforms(
    "ViT-B-16-SigLIP", pretrained="webli",
)

# EVA-CLIP (EVA amélioré)
# CLIP avec EVA (Evolving Vision Attention)
# EVA02-CLIP-L-14 : 80.4% ImageNet zero-shot

# DFN (Data Filtering Networks)
# CLIP filtré par réseau DFN
# ViT-H-14-DFN : 81.4% ImageNet zero-shot
```

---

## 3. BLIP-2 (Bootstrapping Language-Image Pre-training)

### Architecture

```
Image → ViT → Q-Former → LLM → Texte
              ↑
         Requêtes (learnable queries)

Q-Former : pont entre l'encodeur visuel et le LLM
- N requêtes apprises (32 tokens)
- Cross-attention sur les features visuelles
- Compréhension de l'image sans fine-tuner le LLM
```

```python
from transformers import Blip2Processor, Blip2ForConditionalGeneration

processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b",
    torch_dtype=torch.float16,
).to("cuda")

# Image Captioning
image = Image.open("photo.jpg")
inputs = processor(images=image, return_tensors="pt").to("cuda", torch.float16)

out = model.generate(**inputs, max_new_tokens=50)
caption = processor.decode(out[0], skip_special_tokens=True)
print(caption)

# Visual Question Answering
prompt = "Question : Quel est l'objet principal ? Réponse :"
inputs = processor(images=image, text=prompt, return_tensors="pt").to("cuda", torch.float16)

out = model.generate(**inputs, max_new_tokens=50)
answer = processor.decode(out[0], skip_special_tokens=True)
print(answer)
```

---

## 4. LLaVA (Large Language and Vision Assistant)

### Architecture

```
Image → ViT (CLIP) → Projection MLP → LLM (LLaMA/Vicuna/Mistral)
                                        ↑
                                  Texte utilisateur

Entraînement en 2 étapes :
1. Pré-entraînement : geler ViT + LLM, seule la projection s'entraîne
2. Fine-tuning : ViT gelé, projection + LLM s'entraînent
```

### LLaVA 1.6 / NeXT

```python
# pip install llava
from llava.model.builder import load_pretrained_model
from llava.mm_utils import get_model_name_from_path
from llava.eval.run_llava import eval_model

# LLaVA-1.6 34B (Hermes-2 Yi-34B backbone)
model_path = "liuhaotian/llava-v1.6-34b"
tokenizer, model, image_processor, context_len = load_pretrained_model(
    model_path, None, get_model_name_from_path(model_path),
    device="cuda", device_map="auto",
)

# Prompt
prompt = "Décris cette image en détail"
image = Image.open("photo.jpg")
inputs = processor(prompt, image, return_tensors="pt").to("cuda")

output = model.generate(**inputs, max_new_tokens=512)
print(tokenizer.decode(output[0], skip_special_tokens=True))

# Conversation multi-tour
messages = [
    {"role": "user", "content": "Que vois-tu dans cette image ?"},
    {"role": "assistant", "content": "Je vois un paysage de montagne..."},
    {"role": "user", "content": "Quelle saison est-ce ?"},
]
```

### LLaVA via Transformers

```python
from transformers import LlavaForConditionalGeneration, AutoProcessor

model = LlavaForConditionalGeneration.from_pretrained(
    "llava-hf/llava-1.5-7b-hf",
    torch_dtype=torch.float16,
).to("cuda")
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")

prompt = "USER: <image>\nDécris cette image en français\nASSISTANT:"
inputs = processor(images=image, text=prompt, return_tensors="pt").to("cuda", torch.float16)

output = model.generate(**inputs, max_new_tokens=200)
print(processor.decode(output[0][2:], skip_special_tokens=True))
```

---

## 5. Qwen2-VL (Alibaba)

```python
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# Qwen2-VL : compréhension fine, OCR, multilingue
model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2-VL-7B-Instruct",
    torch_dtype=torch.float16,
).to("cuda")
processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")

# Supporte images, vidéos, documents
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": "document.jpg"},
            {"type": "text", "text": "Résume ce document"},
        ],
    },
]
text = processor.apply_chat_template(messages, tokenize=False)
inputs = processor(text=text, images=image, return_tensors="pt").to("cuda", torch.float16)

output = model.generate(**inputs, max_new_tokens=512)
```

---

## 6. Florence-2 (Microsoft Universal Vision)

```python
from transformers import AutoProcessor, AutoModelForCausalLM

# Florence-2 : 16 tâches visuelles en un seul modèle
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-large",
    trust_remote_code=True,
    torch_dtype=torch.float16,
).to("cuda")
processor = AutoProcessor.from_pretrained(
    "microsoft/Florence-2-large",
    trust_remote_code=True,
)

# Tâches supportées (une par prompt) :
# <CAPTION>             → Description générale
# <DETAILED_CAPTION>    → Description détaillée
# <MORE_DETAILED_CAPTION> → Description très détaillée
# <OD>                  → Détection d'objets
# <DENSE_REGION_CAPTION> → Description par région
# <CAPTION_TO_PHRASE_GROUNDING> → Grounding
# <OCR>                 → Texte dans l'image
# <OCR_WITH_REGION>     → OCR avec régions

task = "<CAPTION>"
inputs = processor(text=task, images=image, return_tensors="pt").to("cuda", torch.float16)

generated_ids = model.generate(
    input_ids=inputs["input_ids"],
    pixel_values=inputs["pixel_values"],
    max_new_tokens=1024,
    num_beams=3,
)
result = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
print(result)
```

---

## 7. ImageBind (Meta — 6 Modalités)

```python
# ImageBind : embedding commun pour 6 modalités
# Image, Texte, Audio, Profondeur, Thermique, IMU (mouvement)

# pip install imagebind
from imagebind.models.imagebind_model import imagebind_huge
from imagebind.data import load_and_transform_vision_data, load_and_transform_text
import torch

model = imagebind_huge(pretrained=True).eval().cuda()

# Embeddings alignés
inputs = {
    "image": load_and_transform_vision_data(["photo.jpg"], "cuda"),
    "text": load_and_transform_text(["un chien qui aboie", "une cascade"], "cuda"),
    "audio": load_and_transform_audio_data(["bruit.wav"], "cuda"),
}

with torch.no_grad():
    embeddings = model(inputs)

# Similarité cross-modale
image_feat = embeddings["image"]
text_feat = embeddings["text"]
audio_feat = embeddings["audio"]

# Trouver le meilleur texte pour une image
similarities = (image_feat @ text_feat.T).softmax(dim=-1)
```

---

## 8. Fine-Tuning Multimodal

### LoRA sur LLaVA

```python
from peft import LoraConfig, get_peft_model, TaskType

# Configuration LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

# Appliquer au LLM (pas au ViT)
model.language_model = get_peft_model(model.language_model, lora_config)

# Entraînement sur dataset de paires (image, instruction, réponse)
# Format LLaVA :
# {
#   "id": "1",
#   "image": "photo.jpg",
#   "conversations": [
#     {"from": "human", "value": "<image>\nQue vois-tu ?"},
#     {"from": "gpt", "value": "Je vois un chat."}
#   ]
# }
```

### Entraînement CLIP adapté

```python
import open_clip

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32", pretrained="laion2b_s34b_b79k",
)
tokenizer = open_clip.get_tokenizer("ViT-B-32")

# Ajouter des classes personnalisées
# Fine-tuning sur dataset spécialisé
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)

for images, texts in dataloader:
    images = images.cuda()
    texts = tokenizer(texts).cuda()
    
    image_features = model.encode_image(images)
    text_features = model.encode_text(texts)
    
    # Loss contrastive
    logits = (image_features @ text_features.T) * model.logit_scale
    labels = torch.arange(len(images)).cuda()
    
    loss_i = F.cross_entropy(logits, labels)
    loss_t = F.cross_entropy(logits.T, labels)
    loss = (loss_i + loss_t) / 2
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

---

## 9. Datasets Multimodaux

| Dataset | Paires | Description |
|---------|--------|-------------|
| LAION-5B | 5B | Texte-image web |
| COCO Captions | 600k | Captions 5 par image |
| CC3M / CC12M | 3M / 12M | Conceptual Captions |
| SBU Captions | 1M | Captions Flickr |
| Visual Genome | 108k | QA + régions |
| LLaVA-Instruct | 150k | Instructions visuelles |
| ShareGPT4V | 100k | Captions GPT-4V |
| MMMU | 11.5k | Examens multi-disciplinaires |
| MMBench | 3k | Évaluation VLM chinois |
| SEED-Bench | 19k | Benchmark multimodal |
| MathVista | 6k | Raisonnement mathématique visuel |

---

## 10. Évaluation et Benchmarks

```python
# Benchmarks VLM
# MMMU : compréhension académique
# MMBench : capacités fines
# SEED-Bench : 9 dimensions
# MathVista : raisonnement mathématique
# POPE : hallucinations
# TextVQA : texte dans l'image
# GQA : compositionnalité

# Évaluation
# Exact Match (EM)
# CIDEr (captions)
# BLEU / ROUGE (textes générés)
# Accuracy (VQA)

# API d'évaluation (lmms-eval)
# pip install lmms-eval
# lmms-eval --model llava --model_args ... --tasks mmmu,mmbench
```

### Benchmarks SOTA (juillet 2025)

| Modèle | MMMU | MMBench | MathVista | POPE |
|--------|------|---------|-----------|------|
| GPT-4V | 69.1 | 83.7 | 49.9 | 86.2 |
| LLaVA-1.6 34B | 62.8 | 81.9 | 43.2 | 83.7 |
| Qwen2-VL 72B | 68.7 | 85.5 | 54.1 | 86.9 |
| InternVL2-76B | 67.5 | 84.3 | 52.8 | 85.5 |
| Florence-2 Large | 48.5 | 75.2 | 35.1 | 78.9 |

---

## 11. Déploiement

```python
# vLLM avec support multimodal
# pip install vllm[multimodal]

from vllm import LLM, SamplingParams

llm = LLM(
    model="liuhaotian/llava-v1.6-34b",
    tensor_parallel_size=4,
    max_model_len=4096,
    trust_remote_code=True,
)

# Inférence
prompt = "Décris cette image en détail"
image_path = "photo.jpg"

outputs = llm.generate({
    "prompt": prompt,
    "multi_modal_data": {"image": image_path},
})

# API OpenAI-compatible
# python -m vllm.entrypoints.openai.api_server \
#     --model liuhaotian/llava-v1.6-34b \
#     --tensor-parallel-size 4
```

---

## Références
- CLIP : https://github.com/openai/CLIP
- OpenCLIP : https://github.com/mlfoundations/open_clip
- LLaVA : https://llava-vl.github.io/
- BLIP-2 : https://huggingface.co/Salesforce/blip2-opt-2.7b
- Florence-2 : https://huggingface.co/microsoft/Florence-2-large
- Qwen-VL : https://huggingface.co/Qwen/Qwen2-VL-7B-Instruct
- ImageBind : https://imagebind.metademolab.com/
- LMMS-eval : https://github.com/EvolvingLMMs-Lab/lmms-eval