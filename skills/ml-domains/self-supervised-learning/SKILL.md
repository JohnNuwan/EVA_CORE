---
name: self-supervised-learning
description: Guide complet de l'apprentissage auto-supervisé (SSL) — contrastive, MAE, JEPA, SimCLR, BYOL, VICReg, BERT-style MLM, DINO, I-JEPA. En français.
---

# Self-Supervised Learning — Guide Complet

Apprendre des représentations sans étiquettes humaines : contrastive, prédictive, non-contrastive.

---

## 1. Pourquoi Self-Supervised Learning ?

```python
# Problème : des millions d'images/texte, presque sans étiquettes
# Solution SSL : créer des labels automatiquement à partir des données
#
# Types d'objectifs SSL :
# 1. **Contrastif** : rapprocher les positifs, éloigner les négatifs
# 2. **Génératif** : reconstruire l'entrée (MAE, BERT MLM)
# 3. **Prédictif (Joint Embedding)** : prédire la représentation d'une vue
# 4. **Distillation** : un modèle enseignant → modèle étudiant
```

```
                    SSL
               /     |     \
         Contrastif  Génératif  Prédictif
         SimCLR      MAE        BYOL
         MoCo        BERT       JEPA
         CLIP        DALL-E     DINO
         SwAV        GPT        I-JEPA
```

---

## 2. Apprentissage Contrastif

### SimCLR (Chen et al., 2020)

```python
# Principe : pour chaque image, 2 augmentations random = 2 vues
# Les vues d'une même image sont positives
# Les vues d'images différentes sont négatives
# Loss : NT-Xent (Normalized Temperature-Scaled Cross Entropy)

class SimCLR(nn.Module):
    """Simple Framework for Contrastive Learning of Visual Representations."""
    def __init__(self, encoder, proj_dim=128):
        super().__init__()
        self.encoder = encoder
        self.projection = nn.Sequential(
            nn.Linear(encoder.output_dim, 2048),
            nn.ReLU(),
            nn.Linear(2048, proj_dim),
        )
    
    def forward(self, x_i, x_j):
        """x_i, x_j: deux vues augmentées du même batch."""
        # Encodage
        h_i = self.encoder(x_i)  # (B, D)
        h_j = self.encoder(x_j)  # (B, D)
        
        # Projection (l'espace où on applique la contrastive loss)
        z_i = F.normalize(self.projection(h_i), dim=1)  # (B, 128)
        z_j = F.normalize(self.projection(h_j), dim=1)  # (B, 128)
        
        return z_i, z_j


def nt_xent_loss(z_i, z_j, temperature=0.5):
    """Normalized Temperature-scaled Cross Entropy Loss.
    
    Loss = -log( exp(sim(i,j)/τ) / Σ_k exp(sim(i,k)/τ) )
    Où k ∈ {vues positives et négatives du batch}
    """
    B = z_i.size(0)
    z = torch.cat([z_i, z_j], dim=0)  # (2B, D)
    
    # Matrice de similarité cosinus
    sim = torch.mm(z, z.t()) / temperature  # (2B, 2B)
    
    # Masque : diagonale = self-similarité, i=B+j = positive pair
    mask = torch.eye(2 * B, device=z.device).bool()
    sim = sim.masked_fill(mask, -1e9)
    
    # Pour chaque élément, sa paire positive est à l'index i+B ou i-B
    positive = torch.cat([
        torch.arange(B, 2 * B, device=z.device),
        torch.arange(0, B, device=z.device),
    ])  # (2B,) — index de la paire positive
    
    loss = F.cross_entropy(sim, positive)
    return loss


# Augmentations SimCLR
transform_simclr = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.08, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.8, 0.8, 0.8, 0.2),
    transforms.RandomGrayscale(p=0.2),
    transforms.GaussianBlur(kernel_size=23),
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
])
```

### MoCo v3 (Momentum Contrast, He et al., 2021)

```python
# Innovation : Queue dynamique + momentum encoder
# Au lieu de batch entier pour les négatifs, utilise une queue
# Permet de grands batchs de négatifs sans augmenter le batch size

class MoCo(nn.Module):
    """Momentum Contrast."""
    def __init__(self, encoder, queue_size=65536, momentum=0.999, dim=128):
        super().__init__()
        self.encoder_q = encoder            # Query encoder (entraîné)
        self.encoder_k = copy.deepcopy(encoder)  # Key encoder (momentum)
        
        # Ne pas entraîner le key encoder
        for p in self.encoder_k.parameters():
            p.requires_grad = False
        
        self.register_buffer("queue", F.normalize(
            torch.randn(queue_size, dim), dim=1))
        self.register_buffer("queue_ptr", torch.zeros(1, dtype=torch.long))
    
    @torch.no_grad()
    def _momentum_update(self):
        """Momentum update du key encoder."""
        for param_q, param_k in zip(self.encoder_q.parameters(),
                                     self.encoder_k.parameters()):
            param_k.data = self.momentum * param_k.data + \
                          (1 - self.momentum) * param_q.data
```

---

## 3. BYOL — Bootstrap Your Own Latent (Grill et al., 2020)

```python
# Révolution : pas besoin de paires négatives !
# Pourquoi ça marche ? La dynamique empêche l'effondrement.
# Target encoder = momentum du online encoder.

class BYOL(nn.Module):
    """Bootstrap Your Own Latent — SSL sans négatifs."""
    def __init__(self, encoder, pred_dim=256, proj_dim=256, momentum=0.996):
        super().__init__()
        self.online_encoder = encoder
        self.online_projector = MLP(encoder.output_dim, proj_dim)
        self.online_predictor = MLP(proj_dim, pred_dim)
        
        self.target_encoder = copy.deepcopy(encoder)
        self.target_projector = copy.deepcopy(self.online_projector)
        
        # Gelé
        for p in self.target_encoder.parameters():
            p.requires_grad = False
        for p in self.target_projector.parameters():
            p.requires_grad = False
        
        self.momentum = momentum
    
    def forward(self, x1, x2):
        """x1, x2: deux vues augmentées."""
        # Online : prédit la cible
        z1 = self.online_predictor(self.online_projector(self.online_encoder(x1)))
        z2 = self.online_predictor(self.online_projector(self.online_encoder(x2)))
        
        # Target : cible gelée
        with torch.no_grad():
            h1 = self.target_projector(self.target_encoder(x1))
            h2 = self.target_projector(self.target_encoder(x2))
        
        # MSE loss entre les prédictions normalisées
        loss = F.mse_loss(F.normalize(z1), F.normalize(h2)) + \
               F.mse_loss(F.normalize(z2), F.normalize(h1))
        return loss / 2
    
    @torch.no_grad()
    def update_target(self):
        for param_o, param_t in zip(self.online_encoder.parameters(),
                                     self.target_encoder.parameters()):
            param_t.data = self.momentum * param_t.data + \
                          (1 - self.momentum) * param_o.data
```

---

## 4. VICReg (Bardes et al., 2022)

```python
# Variance-Invariance-Covariance Regularization
# Loss triple : variance (ne pas s'effondrer) + 
#              invariance (vues similaires) + 
#              covariance (décorréler les dimensions)

class VICRegLoss(nn.Module):
    def __init__(self, sim_coef=25, var_coef=25, cov_coef=1):
        super().__init__()
        self.sim_coef = sim_coef
        self.var_coef = var_coef
        self.cov_coef = cov_coef
    
    def forward(self, z1, z2):
        # Invariance : MSE entre les représentations
        sim_loss = F.mse_loss(z1, z2)
        
        # Variance : hinge loss sur l'écart-type
        std_z1 = torch.sqrt(z1.var(dim=0) + 1e-4)
        std_z2 = torch.sqrt(z2.var(dim=0) + 1e-4)
        var_loss = torch.mean(F.relu(1 - std_z1)) + torch.mean(F.relu(1 - std_z2))
        
        # Covariance : décorrélation (diag=1, hors-diag=0)
        z1 = z1 - z1.mean(dim=0)
        z2 = z2 - z2.mean(dim=0)
        cov_z1 = (z1.T @ z1) / (z1.size(0) - 1)
        cov_z2 = (z2.T @ z2) / (z2.size(0) - 1)
        cov_loss = (cov_z1.pow(2).sum() - cov_z1.diag().pow(2).sum()) / z1.size(1) + \
                   (cov_z2.pow(2).sum() - cov_z2.diag().pow(2).sum()) / z2.size(1)
        
        return (self.sim_coef * sim_loss + 
                self.var_coef * var_loss + 
                self.cov_coef * cov_loss)
```

---

## 5. MAE — Masked Autoencoder (He et al., 2022)

```python
# Principe : masquer 75% des patches d'une image → reconstruire
# Architecture ViT encodeur (seulement patches visibles)
# Decoder léger (reconstruit tous les patches)
# 75% masqués → 4x moins de compute → entraînement rapide

class MAE(nn.Module):
    """Masked Autoencoder."""
    def __init__(self, vit_encoder, decoder, mask_ratio=0.75):
        super().__init__()
        self.encoder = vit_encoder      # ViT (seulement tokens visibles)
        self.decoder = decoder          # Léger
        self.mask_ratio = mask_ratio
    
    def random_masking(self, x, mask_ratio):
        """Masque aléatoire des patches.
        x: (B, N, D) — tous les tokens
        Retourne : tokens visibles + masque
        """
        B, N, D = x.shape
        len_keep = int(N * (1 - mask_ratio))
        
        noise = torch.rand(B, N, device=x.device)
        ids_shuffle = torch.argsort(noise, dim=1)
        ids_keep = ids_shuffle[:, :len_keep]
        
        x_masked = torch.gather(x, dim=1, index=ids_keep.unsqueeze(-1).repeat(1, 1, D))
        
        # Masque binaire
        mask = torch.ones([B, N], device=x.device)
        mask[:, :len_keep] = 0
        mask = torch.gather(mask, dim=1, index=ids_shuffle)
        
        return x_masked, mask, ids_restore
    
    def forward(self, imgs):
        patches = self.patchify(imgs)  # (B, N, P² × C)
        x, mask, ids_restore = self.random_masking(patches, self.mask_ratio)
        
        # Encodeur : seulement les patches visibles
        latent = self.encoder(x)
        
        # Decodeur : reconstruit l'image entière
        pred = self.decoder(latent, ids_restore)
        
        # Loss : MSE sur les patches masqués seulement
        target = self.patchify(imgs)
        loss = (pred - target) ** 2
        loss = loss.mean(dim=-1)  # (B, N)
        loss = (loss * mask).sum() / mask.sum()  # seulement masqués
        
        return loss
```

---

## 6. JEPA — Joint Embedding Predictive Architecture (LeCun et al., 2022-2024)

```python
# JEPA : prédire des représentations (pas les pixels !)
# Critique de MAE : reconstruire les pixels force à capturer 
# des détails non pertinents (bruit, texture)
# JEPA : prédire les embeddings d'une région masquée

class I_JEPA(nn.Module):
    """Image-based Joint Embedding Predictive Architecture.
    
    Composants :
    - Context encoder : encode la région visible
    - Target encoder : encode la région cible (momentum)
    - Predictor : prédit l'embedding cible depuis le contexte
    """
    def __init__(self, context_encoder, target_encoder, predictor):
        super().__init__()
        self.context_encoder = context_encoder
        self.target_encoder = target_encoder
        self.predictor = predictor
        
        # Target encoder : momentum
        for p in self.target_encoder.parameters():
            p.requires_grad = False
    
    def forward(self, x):
        # x: image complète
        # 1. Masquer aléatoirement des régions cibles
        # 2. Encodeur contextuel : seulement régions visibles
        # 3. Encodeur cible (momentum) : régions masquées
        # 4. Predictor : prédit les embeddings cibles depuis le contexte
        # 5. Loss : similarité cosinus entre prédiction et cible
        
        # I-JEPA : l'état de l'art en SSL image (2024)
        # Meilleur que MAE pour transfert few-shot
        # Meilleur que contrastif pour segmentation
        pass
    
    @torch.no_grad()
    def update_target(self, momentum=0.996):
        for p_c, p_t in zip(self.context_encoder.parameters(),
                            self.target_encoder.parameters()):
            p_t.data = momentum * p_t.data + (1 - momentum) * p_c.data
```

### V-JEPA (Video-JEPA, 2024)
```python
# Extension à la vidéo
# Masquer des clips spatio-temporels
# Prédire les embeddings des clips masqués
# Apprendre des représentations vidéo sans labels
# Excellent pour : tracking, action recognition, anticipation
```

---

## 7. DINO — Self-Distillation with No Labels (Caron et al., 2021-2023)

### DINO v1 (2021)
```python
# Self-distillation : un modèle enseignant → modèle étudiant
# Les deux voient des augmentations différentes de la même image
# L'étudiant apprend à prédire la sortie de l'enseignant

class DINO(nn.Module):
    """Self-Distillation with No Labels."""
    def __init__(self, student, teacher, center_momentum=0.9):
        super().__init__()
        self.student = student
        self.teacher = teacher  # momentum de student
        
        # Centre pour éviter l'effondrement
        self.register_buffer('center', torch.zeros(1, teacher.output_dim))
        self.center_momentum = center_momentum
    
    def forward(self, images):
        # Global views (224×224) + local views (96×96)
        global_views, local_views = images
        
        # Teacher : seulement global views
        with torch.no_grad():
            teacher_out = self.teacher(global_views)
            teacher_out = teacher_out - self.center
        
        # Student : global + local views
        student_out = self.student(torch.cat([global_views, local_views]))
        
        # Cross-entropy loss (soft labels)
        loss = -torch.sum(F.softmax(teacher_out / 0.04, dim=-1) * 
                          F.log_softmax(student_out / 0.1, dim=-1), dim=-1).mean()
        
        return loss
    
    @torch.no_grad()
    def update_teacher(self):
        for p_s, p_t in zip(self.student.parameters(), self.teacher.parameters()):
            p_t.data = 0.996 * p_t.data + 0.004 * p_s.data
    
    @torch.no_grad()
    def update_center(self, teacher_out):
        self.center = self.center_momentum * self.center + \
                      (1 - self.center_momentum) * teacher_out.mean(dim=0, keepdim=True)
```

### DINO v2 (2023)
```python
# Innovations DINOv2 :
# 1. Entraînement à grande échelle (142M images)
# 2. Objectifs multiples : iBOT + DINO + SwAV
# 3. KoLeo regularizer (évite l'effondrement)
# 4. Head sharing entre objectifs
# 5. Résultats : SOTA en segmentation, depth estimation
#    Sans fine-tuning (linear probing)
```

---

## 8. SSL pour le NLP

### BERT MLM (Masked Language Model)
```python
# Masque 15% des tokens → prédire les tokens masqués
# Bidirectionnel (pas comme GPT qui est causal)
# Apprend des représentations contextuelles riches

class MLMLoss(nn.Module):
    def forward(self, logits, labels):
        # logits: (B, L, V)  — prédictions
        # labels: (B, L)     — tokens originaux (-100 pour ignorés)
        return F.cross_entropy(logits.view(-1, logits.size(-1)), 
                               labels.view(-1), ignore_index=-100)
```

### SimCSE (Gao et al., 2021)
```python
# Contrastive learning pour les phrases
# Même phrase → 2 forward passes (différents dropout = augmentation)
# Phrases différentes → négatives
# SOTA en similarité de phrases
```

---

## 9. CLIP (Radford et al., 2021)

```python
# CLIP : apprentissage cross-modal (texte → image)
# 400M paires (image, texte) du web
# Loss contrastive : aligner les embeddings image/texte

class CLIP(nn.Module):
    """Contrastive Language-Image Pre-training."""
    def __init__(self, image_encoder, text_encoder):
        super().__init__()
        self.image_encoder = image_encoder  # ViT ou ResNet
        self.text_encoder = text_encoder    # Transformer
        self.logit_scale = nn.Parameter(torch.ones([]) * np.log(1 / 0.07))
    
    def forward(self, images, texts):
        # Encodage
        image_emb = F.normalize(self.image_encoder(images), dim=-1)
        text_emb = F.normalize(self.text_encoder(texts), dim=-1)
        
        # Matrice de similarité
        logit_scale = self.logit_scale.exp()
        logits_per_image = logit_scale * image_emb @ text_emb.t()
        logits_per_text = logits_per_image.t()
        
        # Cross-entropy loss (les paires correctes = diagonale)
        labels = torch.arange(len(images), device=images.device)
        loss_i = F.cross_entropy(logits_per_image, labels)
        loss_t = F.cross_entropy(logits_per_text, labels)
        
        return (loss_i + loss_t) / 2
```

---

## 10. Tableau Comparatif

| Méthode | Négatifs | Momentum | Batch req. | Type | Année | Top-1 (ImageNet) |
|---------|----------|----------|------------|------|-------|------------------|
| SimCLR | ✓ | Non | 4096 | Contrastif | 2020 | 76.5% |
| MoCo v3 | ✓ | ✓ | 256 | Contrastif | 2021 | 76.7% |
| BYOL | ✗ | ✓ | 2048 | Prédictif | 2020 | 77.4% |
| SwAV | ✗ | Non | 256 | Clustering | 2020 | 78.1% |
| VICReg | ✗ | Non | 2048 | Régularisation | 2022 | 78.5% |
| MAE | ✗ | ✓ | 4096 | Génératif | 2022 | 80.6% |
| I-JEPA | ✗ | ✓ | 2048 | Prédictif | 2023 | 79.3% |
| DINO v2 | ✗ | ✓ | 1024 | Distillation | 2023 | 81.1% |

---

## Références

- SimCLR : https://arxiv.org/abs/2002.05709
- MoCo v3 : https://arxiv.org/abs/2104.02057
- BYOL : https://arxiv.org/abs/2006.07733
- SwAV : https://arxiv.org/abs/2006.09882
- VICReg : https://arxiv.org/abs/2105.04906
- MAE : https://arxiv.org/abs/2111.06377
- I-JEPA : https://arxiv.org/abs/2301.08243
- V-JEPA : https://arxiv.org/abs/2404.08471
- DINO : https://arxiv.org/abs/2104.14294
- DINO v2 : https://arxiv.org/abs/2304.07193
- CLIP : https://arxiv.org/abs/2103.00020
- SimCSE : https://arxiv.org/abs/2104.08821
- BERT : https://arxiv.org/abs/1810.04805