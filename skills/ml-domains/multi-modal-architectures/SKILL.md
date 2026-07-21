---
name: multi-modal-architectures
description: Guide complet des architectures multimodales — CLIP, LLaVA, Flamingo, BLIP, Qwen-VL, image+texte, vidéo+langage, audio+texte. En français.
---

# Architectures Multimodales — Guide Complet

Fusionner vision, langage, audio : CLIP, LLaVA, Flamingo, BLIP-2, Qwen-VL, architectures 2024-2025.

---

## 1. Pourquoi Multimodal ?

```python
# Un modèle qui ne voit que du texte ne peut pas :
# - Comprendre une image (diagramme, photo)
# - Lire un tableau dans une capture d'écran
# - Analyser une vidéo
# - Répondre à des questions sur une image (VQA)
# - Transcrire ou comprendre du contenu audio

# Bénéfices :
# - Compréhension plus riche du monde
# - Meilleur raisonnement spatial/visuel
# - Applications : VQA, captioning, robotique, accessibility
```

### Taxonomie

```
     Multimodal
     /    |    \
    /     |     \
Vision-   Audio-   Vidéo-
Langage   Langage  Langage
   |        |        |
CLIP     Whisper   VTimeLLM
LLaVA    Qwen-Audio Sora
Flamingo          Video-LLaVA
BLIP-2
Qwen-VL
```

---

## 2. CLIP (OpenAI, 2021)

### Architecture
```python
# CLIP = Contrastive Language-Image Pre-training
# 400M paires (image, texte) du web
# Encodeur image + encodeur texte, alignés par contrastive learning

class CLIP(nn.Module):
    """Contrastive Language-Image Pre-training."""
    def __init__(self, image_encoder='ViT-L/14', text_encoder='transformer'):
        super().__init__()
        self.visual = image_encoder       # Vision Transformer
        self.text = text_encoder          # Transformer text
        self.logit_scale = nn.Parameter(torch.ones([]) * np.log(1/0.07))
    
    def encode_image(self, image):
        return F.normalize(self.visual(image))
    
    def encode_text(self, text):
        return F.normalize(self.text(text))
    
    def forward(self, image, text):
        I = self.encode_image(image)  # (B, D)
        T = self.encode_text(text)    # (B, D)
        
        # Matrice de similarité cosinus
        logits = self.logit_scale.exp() * I @ T.T  # (B, B)
        
        # Labels = batch indices (paires correctes sur la diagonale)
        labels = torch.arange(len(I), device=I.device)
        loss_i = F.cross_entropy(logits, labels)
        loss_t = F.cross_entropy(logits.T, labels)
        return (loss_i + loss_t) / 2
```

### Utilisation CLIP
```python
# Zero-shot classification
def classify_zero_shot(model, image, class_names, templates):
    """CLIP zero-shot."""
    text_features = []
    for cls in class_names:
        texts = [t.format(cls) for t in templates]  # "a photo of a {cls}"
        text_emb = torch.stack([model.encode_text(t) for t in texts])
        text_features.append(text_emb.mean(dim=0))
    text_features = torch.stack(text_features)
    
    image_features = model.encode_image(image)
    similarities = image_features @ text_features.T
    return similarities.argmax(dim=-1)
```

---

## 3. BLIP-2 (Salesforce, 2023)

### Architecture : Q-Former

```python
# BLIP-2 = Query Transformer (Q-Former)
# Pont entre un vision encoder gelé et un LLM gelé
# Apprend seulement le Q-Former (188M params)

class QFormer(nn.Module):
    """Query Transformer : pont vision-langage.
    
    Composants :
    1. Vision encoder (ViT-g, gelé) : extrait features image
    2. Queries apprises (32 tokens) : interroge l'image
    3. Cross-attention entre queries et features image
    4. Self-attention entre queries et texte (optionnel)
    """
    def __init__(self, num_queries=32, d_model=768, n_heads=12):
        super().__init__()
        self.query_tokens = nn.Parameter(torch.randn(1, num_queries, d_model))
        self.self_attn = nn.MultiheadAttention(d_model, n_heads, batch_first=True)
        self.cross_attn = nn.MultiheadAttention(d_model, n_heads, batch_first=True)
        self.ffn = FeedForward(d_model)
        self.norm = nn.LayerNorm(d_model)
    
    def forward(self, image_features, text_embeds=None):
        B = image_features.size(0)
        queries = self.query_tokens.expand(B, -1, -1)
        
        # Self-attention (entre queries)
        queries = self.self_attn(queries, queries, queries)[0]
        
        # Cross-attention (queries → image features)
        queries = self.cross_attn(queries, image_features, image_features)[0]
        
        # Avec texte (fine-tuning)
        if text_embeds is not None:
            queries = torch.cat([queries, text_embeds], dim=1)
            queries = self.self_attn(queries, queries, queries)[0]
        
        return self.ffn(self.norm(queries))
```

---

## 4. Flamingo (DeepMind, 2022)

### Architecture

```python
# Flamingo : vision-langage in-context few-shot
# Architecture novatrice :
# 1. Vision encoder (NFNet-F6) → Perceiver Resampler
# 2. LLM frozen (Chinchilla 70B) 
# 3. GATED XATTN-DENSE blocks

class PerceiverResampler(nn.Module):
    """Compresse les features image en tokens fixes.
    
    Une vidéo fait 32 images × 256 tokens = 8192 tokens
    Le Perceiver les résume en 64 tokens (×100 compression)
    """
    def __init__(self, d_image=768, d_model=1024, n_latents=64):
        super().__init__()
        self.latents = nn.Parameter(torch.randn(1, n_latents, d_model))
        self.cross_attn = nn.MultiheadAttention(d_model, 8, batch_first=True,
                                                kdim=d_image, vdim=d_image)
    
    def forward(self, visual_features):
        # visual_features: (B, T, H*W, d)  — vidéo
        # Résumé en n_latents tokens via cross-attention
        latents = self.latents.expand(visual_features.size(0), -1, -1)
        visual = visual_features.flatten(1, 2)  # (B, T*H*W, d)
        return self.cross_attn(latents, visual, visual)[0]


class GatedCrossAttention(nn.Module):
    """Cross-attention avec gate (Flamingo).
    
    La gate apprend à quel point la vision influence le texte :
    - Au début : gate≈0 (pas d'influence, le LLM est seul)
    - Progressivement : gate augmente
    - Stabilité d'entraînement
    """
    def __init__(self, d_model):
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, 8, batch_first=True)
        self.gate = nn.Parameter(torch.zeros(d_model))
    
    def forward(self, text_hidden, vision_hidden):
        attn_out = self.attn(text_hidden, vision_hidden, vision_hidden)[0]
        return text_hidden + torch.tanh(self.gate.unsqueeze(0)) * attn_out
```

---

## 5. LLaVA (Large Language and Vision Assistant, 2023-2024)

### Architecture (LLaVA 1.5)

```python
# LLaVA : le modèle VLM open-source le plus populaire
# Architecture simple : CLIP ViT + MLP projector + LLM (Vicuna/LLaMA)
# Pas de Q-Former ou perceiver — projection linéaire directe

class LLaVA(nn.Module):
    """LLaVA : Vision-Language avec un simple MLP projecteur."""
    def __init__(self, vision_encoder, llm, proj_hidden=4096):
        super().__init__()
        self.vision_encoder = vision_encoder  # CLIP ViT-L/14 (gelé)
        self.mlp_projector = nn.Sequential(
            nn.Linear(vision_encoder.hidden_size, proj_hidden),
            nn.GELU(),
            nn.Linear(proj_hidden, llm.hidden_size),
        )
        self.llm = llm  # LLaMA/Qwen (pré-entraîné)
    
    def forward(self, images, input_ids, attention_mask):
        # 1. Encoder les images
        image_features = self.vision_encoder(images)  # (B, 256, 1024)
        image_tokens = self.mlp_projector(image_features)  # (B, 256, 4096)
        
        # 2. Projeter les tokens image dans l'espace du LLM
        # Les tokens image sont placés avant/entre les tokens texte
        # Format : <image> \n Texte de l'utilisateur
        inputs_embeds = self.interleave(image_tokens, input_ids)
        
        # 3. Forward dans le LLM
        outputs = self.llm(inputs_embeds=inputs_embeds)
        return outputs.logits
```

### LLaVA-NeXT (2024)
```python
# Améliorations LLaVA-NeXT :
# - Image haute résolution (336×336 → 672×672)
# - AnyRes : découpage en plusieurs crop (4×224×224)
# - Meilleur OCR et compréhension de graphiques
# - Données SFT de haute qualité (LLaVA-Instruct-150K → 1.2M)
```

---

## 6. Multi-Modal LLMs Modernes (2024-2025)

### Qwen2.5-VL
```python
# Qwen-VL : Vision-Language natif
# - Vision encoder (ViT dynamique) + Qwen2.5 LLM
# - Résolution variable (adaptée au contenu)
# - Support vidéo (entrée multi-frame)
# - Détection d'objets (bounding boxes)
# - GUI agent : comprendre les interfaces utilisateurs

class DynamicResolutionViT(nn.Module):
    """ViT à résolution dynamique (Qwen-VL).
    
    L'image n'est pas redimensionnée à une taille fixe.
    Elle est découpée en patches de taille fixe,
    mais le nombre de patches varie selon l'image.
    """
    def __init__(self, patch_size=14):
        super().__init__()
        self.patch_size = patch_size
    
    def forward(self, image):
        # image: (B, 3, H, W) — résolution native
        patches = image.unfold(2, self.patch_size, self.patch_size) \
                        .unfold(3, self.patch_size, self.patch_size)
        # Nombre variable de patches selon (H, W)
        return patches.flatten(1, 2)  # adaptatif
```

### LLaMA 3.2 Vision
```python
# Version 11B + 90B avec vision
# Intègre un ViT dans le modèle LLaMA 3.2
# Cross-attention adaptative image-texte
# Support multi-image et vidéo
```

### GPT-4o / Gemini 2 / Claude 3.5
```python
# Modèles propriétaires multimodaux natifs
# GPT-4o : vision, audio, texte en temps réel
# Gemini 2 : multimodal natif dès l'entraînement
# Claude 3.5 Sonnet : document understanding
```

---

## 7. Vision-Language Training Pipeline

```python
class VisionLanguageTraining:
    """Pipeline d'entraînement VLM en 3 étapes."""
    
    @staticmethod
    def stage_1_vision_language_alignment(model, data):
        """Étape 1 : aligner les embeddings vision-langage.
        
        Objectif : le projecteur apprend à mapper les features CLIP
        vers l'espace d'embedding du LLM.
        Données : paires (image, caption)
        Loss : cross-entropy (next token prediction) sur le caption
        LLM et vision encoder gelés, seulement projecteur entraîné
        """
        pass
    
    @staticmethod
    def stage_2_instruction_tuning(model, data):
        """Étape 2 : fine-tuning sur instructions visuelles.
        
        Objectif : comprendre des questions sur l'image
        Données : (image, question, réponse)
        Format : conversation multi-tour
        LLM entraîné, projecteur entraîné, vision gelé
        """
        pass
    
    @staticmethod
    def stage_3_rlhf(model, data):
        """Étape 3 : alignment avec préférences visuelles.
        
        RLHF sur données visuelles
        Reward model évalue la qualité des réponses visuelles
        """
        pass
```

---

## 8. Vidéo-Langage

### Video-LLaVA
```python
class VideoLLaVA(nn.Module):
    """Extension vidéo de LLaVA."""
    def __init__(self, n_frames=8):
        super().__init__()
        self.n_frames = n_frames
    
    def encode_video(self, frames):
        """frames: (B, T, C, H, W)"""
        # Échantillonner T frames
        # Chaque frame est encodée indépendamment
        # Concaténation temporelle des tokens
        frame_tokens = []
        for t in range(self.n_frames):
            tokens = self.vision_encoder(frames[:, t])
            frame_tokens.append(tokens)
        
        # Positional encoding temporel
        video_tokens = torch.cat(frame_tokens, dim=1)  # (B, T*256, D)
        return video_tokens
```

### Sora (OpenAI, 2024)
```python
# Sora : génération vidéo par diffusion
# Comprend la physique, la persistance 3D
# Architecture DiT (Diffusion Transformer) spatio-temporel
# Patches vidéo 3D (spatial + temporal)
```

---

## 9. Audio-Langage

### Whisper (OpenAI, 2022-2023)
```python
# Whisper : transcription et traduction audio
# Architecture encoder-decoder Transformer
# 680k heures de données multilingues
# Sortie : texte transcrit

# Large-v3 : meilleur modèle open-source STT
# Multilingue (99 langues)
# Robustesse au bruit
```

### Qwen-Audio
```python
# Qwen-Audio : compréhension audio complète
# Encoder audio (Whisper) + LLM
# Supporte : parole, musique, sons environnementaux
# Tasks : ASR, audio captioning, QA audio
```

---

## 10. Tableau Comparatif VLM

| Modèle | Vision Enc. | LLM | Liens | Taille | Année |
|--------|------------|-----|-------|--------|-------|
| CLIP | ViT-L | Transformer | Contrastif | 428M | 2021 |
| BLIP-2 | ViT-g | OPT/FlanT5 | Q-Former | 188M+12B | 2023 |
| Flamingo | NFNet | Chinchilla | Perceiver | 80B | 2022 |
| LLaVA 1.5 | ViT-L | Vicuna | MLP | 13B | 2023 |
| LLaVA-NeXT | ViT-L (AnyRes) | Vicuna | MLP | 13B | 2024 |
| Qwen2.5-VL | Dyn-ViT | Qwen2.5 | MLP | 72B | 2025 |
| LLaMA 3.2-V | ViT | LLaMA 3.2 | Cross-Attn | 11B | 2024 |
| GPT-4o | Custom | Custom | Native | ? | 2024 |

---

## 11. Applications

```python
# VQA (Visual Question Answering)
def vqa(model, image, question):
    """Répondre à une question sur une image."""
    pass

# Image Captioning
def caption(model, image):
    """Générer une description de l'image."""
    pass

# Document Understanding
def doc_qa(model, document_image, question):
    """Comprendre des documents, tableaux, graphiques."""
    pass

# OCR-Free Understanding
def ocr_free(model, image):
    """Lire du texte dans une image sans OCR séparé."""
    pass
```

---

## Références

- CLIP : https://arxiv.org/abs/2103.00020
- BLIP-2 : https://arxiv.org/abs/2301.12597
- Flamingo : https://arxiv.org/abs/2204.14198
- LLaVA : https://arxiv.org/abs/2304.08485
- LLaVA-1.5 : https://arxiv.org/abs/2310.03744
- Qwen-VL : https://arxiv.org/abs/2308.12966
- Video-LLaVA : https://arxiv.org/abs/2311.10122
- Whisper : https://arxiv.org/abs/2212.04356
- Sora : https://openai.com/sora