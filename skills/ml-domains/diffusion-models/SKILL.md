---
name: diffusion-models
description: Guide complet des modèles de diffusion — DDPM, score matching, DDIM, Stable Diffusion, FLUX, Latent Diffusion, flow matching, implémentations. En français.
---

# Modèles de Diffusion — Guide Complet

DDPM, score matching, modèles latents, génération d'images, vidéo et audio.

---

## 1. Les Modèles Génératifs en 2025

```python
# Approches génératives :
# - GANs : rapides mais instables (mode collapse)
# - VAEs : stables mais images floues
# - Autoregressive (PixelCNN, Transformers) : lents
# - Normalizing Flows : contraints topologiquement
#
# ★ Diffusion : meilleur compromis qualité/stabilité
#   Utilisé par : Stable Diffusion, DALL-E 3, Midjourney,
#                Sora, FLUX, Imagen
```

---

## 2. DDPM — Denoising Diffusion Probabilistic Models (Ho et al., 2020)

### Forward Process (Diffusion)
```python
# Détruit progressivement les données en ajoutant du bruit
# q(x_t | x_{t-1}) = N(√(1-β_t) · x_{t-1}, β_t · I)
# Après T étapes : x_T ≈ N(0, I)

# Formule fermée (échantillonnage direct à n'importe quel t) :
# α_t = 1 - β_t
# α¯_t = ∏_{s=1}^{t} α_s
# q(x_t | x_0) = N(√α¯_t · x_0, (1 - α¯_t) · I)
# x_t = √α¯_t · x_0 + √(1 - α¯_t) · ε,  ε ~ N(0, I)

def forward_diffusion(x_0, t, alpha_bar):
    """Ajoute du bruit jusqu'au timestep t.
    x_0: (B, C, H, W)  — image originale normalisée [-1, 1]
    """
    noise = torch.randn_like(x_0)
    noisy = torch.sqrt(alpha_bar[t]) * x_0 + torch.sqrt(1 - alpha_bar[t]) * noise
    return noisy, noise
```

### Reverse Process (Denoising)
```python
# Apprend à inverser la diffusion :
# p_θ(x_{t-1} | x_t) = N(μ_θ(x_t, t), Σ_θ(x_t, t))
# On prédit le bruit ε_θ ajouté à x_0

# Loss : L_simple = E_{t, x_0, ε} ||ε - ε_θ(√α¯_t·x_0 + √(1-α¯_t)·ε, t)||²
```

### Implémentation DDPM Complète
```python
import torch
import torch.nn as nn
import math


def cosine_beta_schedule(timesteps, s=0.008):
    """Scheduler beta du bruit (cosine, plus stable que linear)."""
    steps = timesteps + 1
    x = torch.linspace(0, timesteps, steps)
    alphas_cumprod = torch.cos(((x / timesteps) + s) / (1 + s) * math.pi * 0.5) ** 2
    alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
    betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
    return torch.clamp(betas, 0, 0.999)


class SinusoidalTimeEmbedding(nn.Module):
    """Positional encoding pour le timestep (comme les Transformers)."""
    def __init__(self, dim):
        super().__init__()
        self.dim = dim
    
    def forward(self, t):
        half_dim = self.dim // 2
        emb = math.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, device=t.device) * -emb)
        emb = t[:, None] * emb[None, :]
        return torch.cat([emb.sin(), emb.cos()], dim=-1)


class UNetBlock(nn.Module):
    """Block de base U-Net avec attention."""
    def __init__(self, in_ch, out_ch, time_dim, has_attn=False):
        super().__init__()
        self.norm1 = nn.GroupNorm(32, in_ch)
        self.conv1 = nn.Conv2d(in_ch, out_ch, 3, padding=1)
        self.time_mlp = nn.Linear(time_dim, out_ch)
        self.norm2 = nn.GroupNorm(32, out_ch)
        self.conv2 = nn.Conv2d(out_ch, out_ch, 3, padding=1)
        
        self.attn = nn.MultiheadAttention(out_ch, 4, batch_first=True) if has_attn else None
        self.residual = nn.Conv2d(in_ch, out_ch, 1) if in_ch != out_ch else nn.Identity()
    
    def forward(self, x, t):
        h = self.conv1(F.silu(self.norm1(x)))
        h = h + self.time_mlp(F.silu(t))[:, :, None, None]
        h = self.conv2(F.silu(self.norm2(h)))
        
        if self.attn is not None:
            B, C, H, W = h.shape
            h_flat = h.view(B, C, H * W).transpose(1, 2)
            h_attn, _ = self.attn(h_flat, h_flat, h_flat)
            h = h + h_attn.transpose(1, 2).view(B, C, H, W)
        
        return h + self.residual(x)


class SimpleUNet(nn.Module):
    """U-Net simplifié pour diffusion."""
    def __init__(self, img_channels=3, base_channels=128, time_dim=256):
        super().__init__()
        self.time_mlp = nn.Sequential(
            SinusoidalTimeEmbedding(time_dim),
            nn.Linear(time_dim, time_dim * 4),
            nn.SiLU(),
            nn.Linear(time_dim * 4, time_dim),
        )
        
        # Encoder
        self.inc = UNetBlock(img_channels, base_channels, time_dim)
        self.down1 = UNetBlock(base_channels, base_channels * 2, time_dim)
        self.down2 = UNetBlock(base_channels * 2, base_channels * 4, time_dim, has_attn=True)
        self.down3 = UNetBlock(base_channels * 4, base_channels * 4, time_dim)
        
        # Bottleneck
        self.bot = UNetBlock(base_channels * 4, base_channels * 4, time_dim, has_attn=True)
        
        # Decoder
        self.up3 = UNetBlock(base_channels * 8, base_channels * 2, time_dim)
        self.up2 = UNetBlock(base_channels * 4, base_channels, time_dim, has_attn=True)
        self.up1 = UNetBlock(base_channels * 2, base_channels, time_dim)
        self.outc = nn.Conv2d(base_channels, img_channels, 3, padding=1)
    
    def forward(self, x, t):
        t = self.time_mlp(t)
        
        x1 = self.inc(x, t)
        x2 = self.down1(F.avg_pool2d(x1, 2), t)
        x3 = self.down2(F.avg_pool2d(x2, 2), t)
        x4 = self.down3(F.avg_pool2d(x3, 2), t)
        
        x4 = self.bot(x4, t)
        
        x = F.interpolate(x4, scale_factor=2)
        x = self.up3(torch.cat([x, x3], dim=1), t)
        x = F.interpolate(x, scale_factor=2)
        x = self.up2(torch.cat([x, x2], dim=1), t)
        x = F.interpolate(x, scale_factor=2)
        x = self.up1(torch.cat([x, x1], dim=1), t)
        
        return self.outc(x)


class DDPM(nn.Module):
    """Denoising Diffusion Probabilistic Model."""
    def __init__(self, model, timesteps=1000):
        super().__init__()
        self.model = model
        self.T = timesteps
        
        # Scheduler
        betas = cosine_beta_schedule(timesteps)
        self.register_buffer('betas', betas)
        self.register_buffer('alphas', 1 - betas)
        self.register_buffer('alpha_bars', torch.cumprod(self.alphas, dim=0))
    
    def forward(self, x_0):
        """Entraînement : prédire le bruit."""
        t = torch.randint(0, self.T, (x_0.size(0),), device=x_0.device)
        noise = torch.randn_like(x_0)
        x_t = torch.sqrt(self.alpha_bars[t, None, None, None]) * x_0 \
              + torch.sqrt(1 - self.alpha_bars[t, None, None, None]) * noise
        
        pred_noise = self.model(x_t, t)
        return F.mse_loss(pred_noise, noise)
    
    @torch.no_grad()
    def sample(self, batch_size=4, img_size=32, channels=3, device='cpu'):
        """Génération : débruiter de x_T ~ N(0,I) à x_0."""
        x = torch.randn(batch_size, channels, img_size, img_size, device=device)
        
        for t in reversed(range(self.T)):
            t_tensor = torch.full((batch_size,), t, device=device)
            
            # Prédiction du bruit
            pred_noise = self.model(x, t_tensor)
            
            # Dénombrage (formule DDPM)
            alpha = self.alphas[t]
            alpha_bar = self.alpha_bars[t]
            
            coef1 = 1 / torch.sqrt(alpha)
            coef2 = (1 - alpha) / torch.sqrt(1 - alpha_bar)
            
            x_mean = coef1 * (x - coef2 * pred_noise)
            
            if t > 0:
                noise = torch.randn_like(x)
                sigma = torch.sqrt((1 - alpha_bar / self.alpha_bars[t-1]) 
                                   * (1 - alpha) / (1 - alpha_bar))
                x = x_mean + sigma * noise
            else:
                x = x_mean
        
        return torch.clamp(x, -1, 1)
```

---

## 3. DDIM — Denoising Diffusion Implicit Models (Song et al., 2021)

```python
# DDIM : accélère l'échantillonnage (step 1000 → 50)
# Principe : processus non-markovien déterministe
# x_{t-1} = √α¯_{t-1} · x_0_pred + √(1-α¯_{t-1}) · ε_pred
#
# Où x_0_pred = (x_t - √(1-α¯_t) · ε_θ(x_t, t)) / √α¯_t
#     ε_pred = ε_θ(x_t, t)

@torch.no_grad()
def sample_ddim(model, batch_size, img_size, channels, device, ddim_steps=50):
    """Échantillonnage DDIM (50x plus rapide que DDPM)."""
    T = 1000
    step_ratio = T // ddim_steps
    times = torch.linspace(0, T - 1, ddim_steps, dtype=torch.long)
    
    x = torch.randn(batch_size, channels, img_size, img_size, device=device)
    
    for i, t in enumerate(reversed(times)):
        t_tensor = torch.full((batch_size,), t, device=device)
        alpha_bar = model.alpha_bars[t]
        alpha_bar_prev = model.alpha_bars[t - step_ratio] if i < ddim_steps - 1 else torch.tensor(1.0)
        
        pred_noise = model.model(x, t_tensor)
        
        # x_0 prediction
        x0_pred = (x - torch.sqrt(1 - alpha_bar) * pred_noise) / torch.sqrt(alpha_bar)
        
        # DDIM step
        sigma_t = 0  # 0 = déterministe, >0 = stochastic
        noise = torch.randn_like(x) if sigma_t > 0 else 0
        
        x = torch.sqrt(alpha_bar_prev) * x0_pred + \
            torch.sqrt(1 - alpha_bar_prev - sigma_t**2) * pred_noise + \
            sigma_t * noise
    
    return torch.clamp(x, -1, 1)
```

---

## 4. Score Matching & SDE (Song et al., 2021)

### Score-Based Generative Models
```python
# Concept : le modèle apprend le score (gradient de la log-probabilité)
# s_θ(x, t) = ∇_x log p_t(x)
# Une fois le score appris, on échantillonne via l'équation de Langevin :
# x_{t+1} = x_t + ε · s_θ(x_t, t) + √(2ε) · z

# Score Matching = DDPM avec une autre formulation
# Diffusion DDPM = prédire le bruit ε
# Score Matching = prédire le score ∇log p = -ε/σ
```

### Variance Exploding / Preserving SDE
```python
# Variance Exploding (VE) : σ² croît avec t
# Variance Preserving (VP) : σ² borné entre 0 et 1 (=DDPM)

# SDE stochastique (vecteur de Langevin) :
# dx = f(x, t) · dt + g(t) · dw
# (f : drift, g : diffusion)
```

---

## 5. Latent Diffusion (Rombach et al., 2022)

### Architecture Stable Diffusion

```
Texte → CLIP Text Encoder → Text Embeddings
                                │
                                ▼
Bruit z_T ──→ U-Net (denoise) ──→ z_0 ──→ VAE Decoder ──→ Image
          ↑              ↑                (768×768)
          │              │
          └────── t ─────┘
           Timestep embedding
           + Cross-attention texte
```

```python
class LatentDiffusion(nn.Module):
    """Stable Diffusion : diffusion dans l'espace latent VAE.
    
    Pourquoi dans le latent ?
    - VAE encode 256×256×3 → 32×32×4 (compressé ×192)
    - Diffusion sur 32×32 au lieu de 256×256
    - ~4x plus rapide, moins de mémoire
    - Qualité préservée (perceptual loss + GAN)
    """
    def __init__(self, vae, unet, text_encoder):
        super().__init__()
        self.vae = vae              # Compresse/décompresse les images
        self.unet = unet            # Denoise dans l'espace latent
        self.text_encoder = text_encoder  # CLIP text encoder
    
    def encode(self, images):
        """Compresse l'image dans l'espace latent."""
        with torch.no_grad():
            return self.vae.encode(images).mode()  # 256² → 32²
    
    def decode(self, latents):
        """Décompresse le latent en image."""
        with torch.no_grad():
            return self.vae.decode(latents)  # 32² → 256²
    
    def train_step(self, images, captions):
        """Entraîne le U-Net dans l'espace latent."""
        latents = self.encode(images)
        text_embeddings = self.text_encoder(captions)
        
        # Diffusion dans l'espace latent
        noise = torch.randn_like(latents)
        t = torch.randint(0, self.T, (latents.size(0),))
        noisy = sqrt_alpha_bar[t] * latents + sqrt(1 - alpha_bar[t]) * noise
        
        # Prédiction du bruit avec conditionnement texte (cross-attention)
        pred = self.unet(noisy, t, text_embeddings)
        return F.mse_loss(pred, noise)
```

### Conditionnement par texte
```python
class CrossAttnUNet(nn.Module):
    """U-Net avec cross-attention pour le conditionnement texte."""
    def __init__(self, d_model=320, text_dim=768, n_heads=8):
        # cross-attention entre les features U-Net et le texte
        self.cross_attn = nn.MultiheadAttention(d_model, n_heads,
                                                kdim=text_dim, vdim=text_dim,
                                                batch_first=True)
    
    def forward(self, x, t, text_emb):
        # x: (B, C, H, W) features U-Net
        # text_emb: (B, L, D) embeddings CLIP
        B, C, H, W = x.shape
        x_flat = x.flatten(2).transpose(1, 2)  # (B, H*W, C)
        x_attn, _ = self.cross_attn(x_flat, text_emb, text_emb)
        x = x + x_attn.transpose(1, 2).reshape(B, C, H, W)
        return x
```

---

## 6. FLUX (Black Forest Labs, 2024)

```python
# FLUX : l'état de l'art 2024-2025 de la génération d'images
# Basé sur flow matching (pas de diffusion classique)

# Architecture :
# - 12B paramètres (text encoder + transformer)
# - T5-XXL text encoder
# - Dual-stream attention (images + texte séparés puis fusion)
# - Rotational Position Embedding

# Types de modèles :
# - FLUX.1-dev : 12B, guidage, bonne qualité
# - FLUX.1-schnell : 12B, distillation step (4 étapes !)
# - FLUX.2-pro : 12B, qualité pro
```

---

## 7. Flow Matching (Lipman et al., 2023)

```python
# Alternative à DDPM/Score Matching
# Principe : apprentissage d'un champ de vecteurs (vector field)
# qui transporte la distribution du bruit vers les données

# Flux :
# ψ_t(x) = (1 - t) · x_0 + t · ε   pour t ∈ [0,1]

# Champ de vecteurs cible :
# u_t(x | ε, x_0) = d/dt ψ_t(x) = ε - x_0

# Loss : L = E_{t, x_0, ε} [ ||v_θ(ψ_t(x), t) - (ε - x_0)||² ]

# Avantages :
# 1. Convergence plus rapide (trajectoires rectilignes)
# 2. Moins d'étapes d'inférence
# 3. Plus stable que le score matching
```

---

## 8. Guidance (Classifier-Free Guidance)

```python
# CFG — Classifier-Free Guidance (Ho & Salimans, 2021)
# Mélange les prédictions conditionnées et non conditionnées
# ε_θ = ε_uncond + w · (ε_cond - ε_uncond)
# w = guidance scale (typiquement 7.5)

def cfg_sample(unet, latent, t, text_emb, uncond_emb, guidance_scale=7.5):
    with torch.no_grad():
        # Prédiction non conditionnée
        noise_uncond = unet(latent, t, uncond_emb)
        # Prédiction conditionnée
        noise_cond = unet(latent, t, text_emb)
        # Guidance
        return noise_uncond + guidance_scale * (noise_cond - noise_uncond)
```

---

## 9. Applications Multimodales (2024-2025)

| Domaine | Modèle | Architecture |
|---------|--------|-------------|
| Image | SD 3.5 | MMDiT (DiT + Text) |
| Image | FLUX | Flow Matching + T5 |
| Image | DALL-E 3 | Pixel diffusion |
| Vidéo | Sora | DiT spacetime |
| Vidéo | Stable Video Diff | Latent video |
| Audio | AudioLDM 2 | Latent audio |
| Music | MusicGen | Diffusion + EnCodec |
| 3D | Point-E | Diffusion points |
| 3D | DreamFusion | 2D→3D (SDS loss) |

---

## 10. Implémentation Complète (Petite échelle)

```python
# Exemple : DDPM sur MNIST (32×32)
# $ pip install torch torchvision einops
# $ python train_ddpm.py

def train_ddpm():
    model = SimpleUNet(img_channels=1, base_channels=64)
    ddpm = DDPM(model, timesteps=200)
    
    optimizer = torch.optim.Adam(ddpm.parameters(), lr=2e-4)
    dataset = torchvision.datasets.MNIST(root='./data', transform=transforms.ToTensor())
    
    for epoch in range(100):
        for x, _ in dataset:
            x = x * 2 - 1  # normalize to [-1, 1]
            loss = ddpm(x)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    
    samples = ddpm.sample(batch_size=16, img_size=28, channels=1)
    # samples: torch.Tensor shape (16, 1, 28, 28) dans [-1, 1]
```

---

## Références

- DDPM (Ho et al., 2020) : https://arxiv.org/abs/2006.11239
- DDIM (Song et al., 2021) : https://arxiv.org/abs/2010.02502
- Score-Based SDE (Song et al., 2021) : https://arxiv.org/abs/2011.13456
- Latent Diffusion (Rombach et al., 2022) : https://arxiv.org/abs/2112.10752
- FLUX (2024) : https://github.com/black-forest-labs/flux
- Flow Matching (Lipman et al., 2023) : https://arxiv.org/abs/2210.02747
- CFG (Ho & Salimans, 2021) : https://arxiv.org/abs/2207.12598
- Stable Diffusion 3 : https://arxiv.org/abs/2403.03206
- Sora (OpenAI, 2024) : https://openai.com/sora