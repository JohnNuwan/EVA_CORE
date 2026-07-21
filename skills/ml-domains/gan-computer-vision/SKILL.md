---
name: gan-computer-vision
description: GANs pour la vision par ordinateur — StyleGAN, CycleGAN, pix2pix, SRGAN, DCGAN, WGAN, GigaGAN, GANs conditionnels, super-résolution, inpainting, translation. En français.

---

# GANs pour la Vision par Ordinateur

Generative Adversarial Networks : deux réseaux en compétition (Générateur vs Discriminateur). Utilisés pour la génération d'images, super-résolution, translation, inpainting, et bien plus.

---

## 1. Fondamentaux GANs

### Loss Functions

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

# Loss GAN originale (BCE)
def gan_loss(disc_real, disc_fake):
    bce = nn.BCEWithLogitsLoss()
    real_loss = bce(disc_real, torch.ones_like(disc_real))
    fake_loss = bce(disc_fake, torch.zeros_like(disc_fake))
    return real_loss + fake_loss

# WGAN-GP (Wasserstein + Gradient Penalty)
def wgan_gp_loss(disc_real, disc_fake, interpolates, gradient_penalty_weight=10.0):
    d_loss = disc_fake.mean() - disc_real.mean()
    g_loss = -disc_fake.mean()
    
    # Gradient Penalty
    gradients = torch.autograd.grad(
        outputs=disc_interpolates,
        inputs=interpolates,
        grad_outputs=torch.ones_like(disc_interpolates),
        create_graph=True,
        retain_graph=True,
    )[0]
    gradients = gradients.view(gradients.size(0), -1)
    gradient_penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean() * gradient_penalty_weight
    
    d_loss += gradient_penalty
    return d_loss, g_loss

# LSGAN (Least Squares)
def lsgan_loss(disc_real, disc_fake):
    d_loss = 0.5 * (F.mse_loss(disc_real, torch.ones_like(disc_real)) +
                    F.mse_loss(disc_fake, torch.zeros_like(disc_fake)))
    g_loss = 0.5 * F.mse_loss(disc_fake, torch.ones_like(disc_fake))
    return d_loss, g_loss

# Hinge Loss
def hinge_loss(disc_real, disc_fake):
    d_loss = F.relu(1.0 - disc_real).mean() + F.relu(1.0 + disc_fake).mean()
    g_loss = -disc_fake.mean()
    return d_loss, g_loss
```

### Générateur DCGAN

```python
class Generator(nn.Module):
    """DCGAN Generator : latent → image 64×64"""
    def __init__(self, latent_dim=100, channels=3):
        super().__init__()
        self.model = nn.Sequential(
            # latent_dim → 4×4×1024
            nn.ConvTranspose2d(latent_dim, 1024, 4, 1, 0, bias=False),
            nn.BatchNorm2d(1024),
            nn.ReLU(True),
            # 4×4 → 8×8
            nn.ConvTranspose2d(1024, 512, 4, 2, 1, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(True),
            # 8×8 → 16×16
            nn.ConvTranspose2d(512, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            # 16×16 → 32×32
            nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(True),
            # 32×32 → 64×64
            nn.ConvTranspose2d(128, channels, 4, 2, 1, bias=False),
            nn.Tanh(),
        )
    
    def forward(self, z):
        z = z.view(z.size(0), -1, 1, 1)
        return self.model(z)
```

### Discriminateur DCGAN

```python
class Discriminator(nn.Module):
    def __init__(self, channels=3):
        super().__init__()
        self.model = nn.Sequential(
            # 64×64 → 32×32
            nn.Conv2d(channels, 128, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            # 32×32 → 16×16
            nn.Conv2d(128, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            # 16×16 → 8×8
            nn.Conv2d(256, 512, 4, 2, 1, bias=False),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),
            # 8×8 → 4×4
            nn.Conv2d(512, 1024, 4, 2, 1, bias=False),
            nn.BatchNorm2d(1024),
            nn.LeakyReLU(0.2, inplace=True),
            # 4×4 → 1
            nn.Conv2d(1024, 1, 4, 1, 0, bias=False),
            nn.Sigmoid(),
        )
    
    def forward(self, img):
        return self.model(img).view(-1, 1)
```

---

## 2. Entraînement GAN

```python
generator = Generator(latent_dim=100).cuda()
discriminator = Discriminator().cuda()

g_optim = torch.optim.Adam(generator.parameters(), lr=0.0002, betas=(0.5, 0.999))
d_optim = torch.optim.Adam(discriminator.parameters(), lr=0.0002, betas=(0.5, 0.999))

for epoch in range(epochs):
    for real_imgs, _ in dataloader:
        real_imgs = real_imgs.cuda()
        batch_size = real_imgs.size(0)
        
        # --- Entraîner Discriminateur ---
        # Images réelles
        d_real = discriminator(real_imgs)
        
        # Images fausses
        z = torch.randn(batch_size, 100).cuda()
        fake_imgs = generator(z).detach()
        d_fake = discriminator(fake_imgs)
        
        d_loss = (F.binary_cross_entropy(d_real, torch.ones_like(d_real)) +
                  F.binary_cross_entropy(d_fake, torch.zeros_like(d_fake)))
        
        d_optim.zero_grad()
        d_loss.backward()
        d_optim.step()
        
        # --- Entraîner Générateur ---
        # Label smoothing : 0.9 au lieu de 1.0
        valid = torch.full((batch_size, 1), 0.9, device="cuda")
        
        z = torch.randn(batch_size, 100).cuda()
        fake_imgs = generator(z)
        d_fake = discriminator(fake_imgs)
        
        g_loss = F.binary_cross_entropy(d_fake, valid)
        
        g_optim.zero_grad()
        g_loss.backward()
        g_optim.step()
```

---

## 3. StyleGAN (Style-Based Generator)

```python
# StyleGAN3 — Mapping Network + Synthesis Network
# pip install stylegan3-pytorch

# Concepts clés StyleGAN :
# 1. Mapping Network : z → w (espace latent intermédiaire)
# 2. Synthesis Network : w → image (AdaIN à chaque couche)
# 3. Mixing Regularization : mélanger deux latents
# 4. Style Mixing : contrôler différents niveaux de style
# 5. Truncation Trick : ψ ∈ [0, 1] pour qualité vs diversité

# StyleGAN2 — Version améliorée
# Supprime les artefacts "droplet"
# Path length regularization
# R1 (R1 gradient penalty)

# StyleGAN3 — Rotation/Translation équivariance
# Fourier features
# Aliasing-free

# Utilisation
import torch
import stylegan3

# Charger pré-entraîné (FFHQ)
device = torch.device('cuda')
G = stylegan3.load_network('stylegan3-r-ffhq-1024x1024.pkl')
G.eval().to(device)

# Générer
z = torch.randn(1, 512).to(device)
w = G.mapping(z, None)  # Latent intermédiaire
img = G.synthesis(w)     # Image 1024×1024

# Style mixing
z1 = torch.randn(1, 512).to(device)
z2 = torch.randn(1, 512).to(device)
w1 = G.mapping(z1, None)
w2 = G.mapping(z2, None)

# Mixer les styles : coarsestyle = w1, finestyle = w2
mix_style = torch.cat([w1[:, :4], w2[:, 4:]], dim=1)
img_mixed = G.synthesis(mix_style)

# Truncation trick
w_avg = G.mapping.w_avg  # Centre de l'espace W
truncation_psi = 0.7
w = w_avg + truncation_psi * (w - w_avg)
img = G.synthesis(w)
```

---

## 4. pix2pix (Image-to-Image Translation)

```python
# pix2pix : GAN conditionnel avec U-Net générateur + PatchGAN

# Générateur U-Net
class UNetGenerator(nn.Module):
    """U-Net avec skip connections pour pix2pix"""
    def __init__(self, in_channels=3, out_channels=3):
        super().__init__()
        # Encodeur
        self.down1 = self.down_block(in_channels, 64, norm=False)
        self.down2 = self.down_block(64, 128)
        self.down3 = self.down_block(128, 256)
        self.down4 = self.down_block(256, 512)
        self.down5 = self.down_block(512, 512)
        self.down6 = self.down_block(512, 512)
        self.down7 = self.down_block(512, 512)
        self.down8 = self.down_block(512, 512, norm=False)
        
        # Décodeur
        self.up1 = self.up_block(512, 512, dropout=True)
        self.up2 = self.up_block(1024, 512, dropout=True)
        self.up3 = self.up_block(1024, 512, dropout=True)
        self.up4 = self.up_block(1024, 512)
        self.up5 = self.up_block(1024, 256)
        self.up6 = self.up_block(512, 128)
        self.up7 = self.up_block(256, 64)
        self.up8 = nn.Sequential(
            nn.ConvTranspose2d(128, out_channels, 4, 2, 1),
            nn.Tanh(),
        )
    
    def forward(self, x):
        d1 = self.down1(x)
        d2 = self.down2(d1)
        d3 = self.down3(d2)
        d4 = self.down4(d3)
        d5 = self.down5(d4)
        d6 = self.down6(d5)
        d7 = self.down7(d6)
        d8 = self.down8(d7)
        u1 = self.up1(d8)
        u2 = self.up2(torch.cat([u1, d7], 1))
        u3 = self.up3(torch.cat([u2, d6], 1))
        u4 = self.up4(torch.cat([u3, d5], 1))
        u5 = self.up5(torch.cat([u4, d4], 1))
        u6 = self.up6(torch.cat([u5, d3], 1))
        u7 = self.up7(torch.cat([u6, d2], 1))
        return self.up8(torch.cat([u7, d1], 1))
    
    def down_block(self, in_c, out_c, norm=True):
        layers = [nn.Conv2d(in_c, out_c, 4, 2, 1), nn.LeakyReLU(0.2)]
        if norm:
            layers.append(nn.BatchNorm2d(out_c))
        return nn.Sequential(*layers)
    
    def up_block(self, in_c, out_c, dropout=False):
        layers = [nn.ConvTranspose2d(in_c, out_c, 4, 2, 1), nn.ReLU()]
        if dropout:
            layers.append(nn.Dropout(0.5))
        layers.append(nn.BatchNorm2d(out_c))
        return nn.Sequential(*layers)

# PatchGAN Discriminator
class PatchGAN(nn.Module):
    """70×70 PatchGAN — classe chaque patch localement"""
    def __init__(self, in_channels=6):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(in_channels, 64, 4, 2, 1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(64, 128, 4, 2, 1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2),
            nn.Conv2d(128, 256, 4, 2, 1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2),
            nn.Conv2d(256, 512, 4, 1, 1),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2),
            nn.Conv2d(512, 1, 4, 1, 1),
        )
    
    def forward(self, x):
        return self.model(x)

# Loss combinée : cGAN + L1
criterion_gan = nn.BCEWithLogitsLoss()
criterion_l1 = nn.L1Loss()
lambda_l1 = 100

# Loss générateur
g_loss = criterion_gan(d_fake, valid) + lambda_l1 * criterion_l1(fake, real)
```

---

## 5. CycleGAN (Unpaired Image Translation)

```python
# CycleGAN : translation sans paires (ex : cheval → zèbre, photo → Monet)

# Deux Générateurs : G_A→B, G_B→A
# Deux Discriminateurs : D_A, D_B

# Losses :
# 1. Adversarial (G_B→A, D_A) et (G_A→B, D_B)
# 2. Cycle Consistency : G_B→A(G_A→B(A)) ≈ A
# 3. Identity : G_B→A(B) ≈ B (optionnel)

# Cycle Consistency Loss
class CycleLoss(nn.Module):
    def __init__(self, lambda_cycle=10.0, lambda_identity=5.0):
        super().__init__()
        self.lambda_cycle = lambda_cycle
        self.lambda_identity = lambda_identity
        self.l1 = nn.L1Loss()
    
    def forward(self, real, reconstructed, identity=None):
        loss = self.lambda_cycle * self.l1(real, reconstructed)
        if identity is not None:
            loss += self.lambda_identity * self.l1(real, identity)
        return loss
```

### Applications pix2pix/CycleGAN

| Tâche | Entrée | Sortie | Type |
|-------|--------|--------|------|
| Colorisation | Gris | Couleur | pix2pix |
| Esquisse → Photo | Croquis | Réaliste | pix2pix |
| Carte → Satellite | Carte | Vue satellite | pix2pix |
| Jour → Nuit | Jour | Nuit | CycleGAN |
| Été → Hiver | Été | Hiver | CycleGAN |
| Photo → Style artistique | Photo | Monet/Van Gogh | CycleGAN |
| Défloutage | Flou | Net | pix2pix |
| Suppression objet | Avec objet | Sans objet | pix2pix |

---

## 6. Super-Résolution (SRGAN, ESRGAN, Real-ESRGAN)

```python
# SRGAN : Super-Resolution GAN
# Génère une image haute résolution à partir de basse résolution

# ESRGAN : Enhanced SRGAN
# - RRDB (Residual-in-Residual Dense Block)
# - Relativistic GAN
# - Perceptual loss (VGG features)

# Real-ESRGAN : pour vraies images basse résolution
# - High-order degradation model
# - Blur, noise, compression

# Utilisation Real-ESRGAN
# pip install realesrgan

from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

model = RealESRGANer(
    scale=4,
    model_path="RealESRGAN_x4plus.pth",
    model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4),
    tile=400,        # Traitement par tuiles pour éviter OOM
    tile_pad=10,
    pre_pad=0,
    half=True,       # FP16
)

# Upscale
output, _ = model.enhance(input_img, outscale=4)

# Perceptual Loss
class VGGLoss(nn.Module):
    """Perceptual loss basé sur VGG19"""
    def __init__(self):
        super().__init__()
        vgg = models.vgg19(pretrained=True).features
        self.layers = nn.Sequential(*list(vgg.children())[:35])
        self.layers.eval()
        for p in self.layers.parameters():
            p.requires_grad = False
        self.criterion = nn.L1Loss()
    
    def forward(self, pred, target):
        pred_features = self.layers(pred)
        target_features = self.layers(target)
        return self.criterion(pred_features, target_features)
```

---

## 7. Inpainting (EdgeConnect, LaMa)

```python
# Inpainting GAN : remplir les zones manquantes
# EdgeConnect : détection de contours + inpainting
# LaMa : Large Mask Inpainting (Fourier convolutions)

# LaMa
# pip install lama-cleaner

from lama_cleaner import LaMa

model = LaMa()
result = model(image, mask)  # mask = zones à remplir (blanc)

# EdgeConnect
# Générateur : Context Encoder
# Discriminateur : PatchGAN
# Loss : L1 + Adversarial + VGG (style)
```

---

## 8. GigaGAN / BigGAN (Large Scale)

```python
# BigGAN : GAN à grande échelle (ImageNet 512×512)
# Batch size 2048, Self-Attention, Spectral Norm
# Class-conditional (Embedding de classe)

# GigaGAN : Giga-scale GAN (3.8B params)
# 1 minute = 1000 images 1024×1024
# Architecture hybride CNN + Attention
# Text-to-image (ex: Stable Diffusion alternative)

# StyleGAN-XL : GAN pour ImageNet 256×512
# Combine StyleGAN + ViT (Vision Transformer)
# Meilleur FID que les modèles de diffusion pour ImageNet
```

---

## 9. Métriques GAN

```python
# FID (Fréchet Inception Distance)
# Plus bas = meilleur
from pytorch_fid import fid_score

fid_value = fid_score.calculate_fid_given_paths(
    ["path/to/real", "path/to/fake"],
    batch_size=50,
    device="cuda",
    dims=2048,
)

# IS (Inception Score)
# Plus haut = meilleur (diversité + qualité)
from torchmetrics.image.inception import InceptionScore
is_metric = InceptionScore()
is_metric.update(fake_images)
precision, recall = is_metric.compute()

# LPIPS (Learned Perceptual Image Patch Similarity)
# Similarité perceptuelle entre deux images
from lpips import LPIPS
lpips_fn = LPIPS(net="alex")
dist = lpips_fn(img1, img2)  # 0 = identique

# FID Benchmarks
# StyleGAN2 FFHQ 1024 → FID 2.8
# StyleGAN3 FFHQ 1024 → FID 2.4
# BigGAN ImageNet 512 → FID 3.9
# GigaGAN 1024 → FID 3.1
```

---

## 10. Techniques Avancées

### Spectral Normalization

```python
from torch.nn.utils import spectral_norm

# Ajouter à toutes les couches D et G
conv = spectral_norm(nn.Conv2d(256, 512, 3, 1, 1))
linear = spectral_norm(nn.Linear(512, 1024))
```

### Self-Attention (SA-GAN)

```python
class SelfAttention(nn.Module):
    """Auto-attention pour GAN (SA-GAN)"""
    def __init__(self, in_channels):
        super().__init__()
        self.query = nn.Conv1d(in_channels, in_channels // 8, 1)
        self.key = nn.Conv1d(in_channels, in_channels // 8, 1)
        self.value = nn.Conv1d(in_channels, in_channels, 1)
        self.gamma = nn.Parameter(torch.zeros(1))
    
    def forward(self, x):
        batch, C, H, W = x.shape
        Q = self.query(x.view(batch, C, -1))
        K = self.key(x.view(batch, C, -1))
        V = self.value(x.view(batch, C, -1))
        attention = F.softmax(torch.bmm(Q.transpose(1, 2), K), dim=-1)
        out = torch.bmm(V, attention.transpose(1, 2))
        out = out.view(batch, C, H, W)
        return self.gamma * out + x
```

### Progressive Growing

```python
# ProGAN : entraînement progressif
# 4×4 → 8×8 → 16×16 → ... → 1024×1024
# Nouveaux blocs ajoutés progressivement (fade-in)
# Stabilise l'entraînement haute résolution
```

---

## Références
- StyleGAN3 : https://github.com/NVlabs/stylegan3
- CycleGAN : https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix
- Real-ESRGAN : https://github.com/xinntao/Real-ESRGAN
- LaMa : https://github.com/saic-mdal/lama
- PapersWithCode GAN : https://paperswithcode.com/task/image-generation
- FID : https://github.com/mseitzer/pytorch-fid