---
name: vqgan-image-compression
title: Compression Extrême d'Images avec VQGAN
description: >-
  Implémenter une compression extrême d'images avec VQGAN (Vector Quantized
  GAN) pour atteindre des bitrates aussi faibles que 0.04 bpp tout en
  maintenant une haute qualité perceptuelle.
version: 2.0.0
author: EVA Agent / EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
dependencies:
  - torch>=2.0
  - torchvision>=0.15
  - numpy>=1.24
  - pillow>=10.0
  - matplotlib>=3.7
  - lpips>=0.1.4
metadata:
  EVA:
    tags:
      - vqgan
      - vqvae
      - gan
      - image-compression
      - generative-models
      - computer-vision
      - deep-learning
      - vector-quantization
      - codebook
    category: research
    related_skills:
      - ai-foundations-exploration
      - spatial-decodable-image-generation
      - comfyui
    requires_toolsets:
      - terminal
      - files
      - execute_code

---

# Compression d'Images Extrême avec VQGAN

## Vue d'Ensemble

Le **VQGAN** (Vector Quantized Generative Adversarial Network) est un modèle génératif capable de comprimer des images à des **bitrates extrêmement faibles** (jusqu'à **0.04 bpp** — bits par pixel) tout en préservant une **haute qualité perceptuelle**. 

VQGAN combine trois innovations clés :

1. **Quantification vectorielle (VQVAE)** : L'espace latent continu est discrétisé via un codebook d'embeddings appris. Chaque patch de l'image est représenté par l'indice de l'embedding le plus proche.
2. **Discriminateur adversarial (GAN)** : Un discriminateur apprend à distinguer les images reconstruites des images réelles, forçant le décodeur à produire des détails haute-fréquence crédibles.
3. **Modélisation autoregressive (optionnelle)** : Un Transformer (PixelSNAIL ou类似) modélise la distribution des indices du codebook pour la génération ou l'inpainting.

Applications typiques :
- **Compression extrême** pour la transmission satellite ou les archives.
- **Génération d'images conditionnée** (texte-to-image, inpainting).
- **Représentation latente discrète** pour la recherche d'images par similarité.

---

## Quand l'utiliser

| Situation | Bitrate cible | Justification |
|-----------|--------------|---------------|
| Archives d'images à très long terme | 0.04–0.10 bpp | Stockage massif avec qualité perceptuelle acceptable |
| Transmission satellite ou IoT | 0.02–0.06 bpp | Bande passante extrêmement limitée |
| Pré-encodage pour génération | 0.10–0.30 bpp | Représentation latente discrète pour Transformers |
| Expérimentation recherche | variable | Étude des compromis bitrate/qualité |
| Application temps réel | 0.20–0.50 bpp | Équilibre entre vitesse de décodage et compression |

---

## 1. Architecture VQGAN

### 1.1 Vue d'Ensemble du Pipeline

```
Image x (H×W×3)
    │
    ▼
┌─────────────────────────────────────────┐
│           Encodeur CNN                   │
│  Conv2d(3→128) → ReLU → Conv2d(128→256) │
│  → Conv2d(256→latent_dim)                │
│         Sortie : z (h×w×d)              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│     Quantification Vectorielle (VQ)     │
│  Pour chaque vecteur z_ij :             │
│    idx = argmin ‖z_ij - e_k‖²           │
│    z_q = e_idx                          │
│  Codebook : {e_1, ..., e_K} ⊂ ℝ^d       │
│         Sortie : z_q (h×w×d)           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│           Décodeur CNN                   │
│  ConvTranspose2d(latent→256) → ReLU →   │
│  ConvTranspose2d(256→128) → ReLU →      │
│  ConvTranspose2d(128→3) → Tanh          │
│         Sortie : x̂ (H×W×3)             │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│          Discriminateur                  │
│  PatchGAN CNN : Classification          │
│  réaliste / faux sur patches 70×70      │
│         Sortie : score D(x̂)            │
└─────────────────────────────────────────┘
```

### 1.2 Implémentation Complète PyTorch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Tuple

class VectorQuantizer(nn.Module):
    """Quantification vectorielle avec straight-through estimator.

    Implémente la quantification par plus proche voisin dans le codebook,
    avec passage straight-through du gradient pour permettre la
    rétropropagation à travers l'opération d'indexation discrète.

    Args:
        n_embeddings: Nombre d'entrées dans le codebook (taille K).
        embedding_dim: Dimension des vecteurs d'embedding.
        commitment_cost: Poids de la perte de commitment (β dans l'article).
    """

    def __init__(self, n_embeddings: int = 1024,
                 embedding_dim: int = 256,
                 commitment_cost: float = 0.25):
        super().__init__()
        self.n_embeddings = n_embeddings
        self.embedding_dim = embedding_dim
        self.commitment_cost = commitment_cost

        # Initialisation uniforme du codebook
        self.embedding = nn.Embedding(n_embeddings, embedding_dim)
        self.embedding.weight.data.uniform_(
            -1.0 / n_embeddings, 1.0 / n_embeddings
        )

    def forward(self, z: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor,
                                                 torch.Tensor, torch.Tensor]:
        """Quantifie les vecteurs latents z.

        Args:
            z: Tenseur d'entrée (B, D, H, W).

        Returns:
            Tuple (z_q, indices, perte_commitment, perplexité).
        """
        # Rearranger : (B, D, H, W) → (B*H*W, D)
        z_flat = z.permute(0, 2, 3, 1).reshape(-1, self.embedding_dim)

        # Calcul des distances euclidiennes
        distances = torch.cdist(z_flat, self.embedding.weight)  # (N, K)

        # Indexation : plus proche voisin
        indices = distances.argmin(dim=-1)  # (N,)

        # Quantification
        z_q = self.embedding(indices).view(z.shape)  # (B, D, H, W)

        # Perte de commitment
        commitment_loss = F.mse_loss(z_q.detach(), z) * self.commitment_cost

        # Straight-through estimator
        z_q = z + (z_q - z).detach()

        # Perplexité (mesure d'utilisation du codebook)
        encodings = F.one_hot(indices, self.n_embeddings).float()
        avg_probs = encodings.mean(dim=0)
        perplexity = torch.exp(-torch.sum(
            avg_probs * torch.log(avg_probs + 1e-10)
        ))

        return z_q, indices, commitment_loss, perplexity


class DiscriminateurPatchGAN(nn.Module):
    """Discriminateur PatchGAN 70×70.

    Classifie chaque patch 70×70 de l'image comme réel ou faux,
    forçant le décodeur à produire des détails haute-fréquence locaux.
    """

    def __init__(self, in_channels: int = 3):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=4, stride=2, padding=1),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(256, 1, kernel_size=4, stride=1, padding=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)


class VQGAN(nn.Module):
    """Modèle VQGAN complet avec encodeur, quantizer et décodeur.

    Args:
        in_channels: Nombre de canaux d'entrée (3 pour RGB).
        latent_dim: Dimension de l'espace latent.
        n_embeddings: Taille du codebook.
        commitment_cost: Poids de la perte de commitment.
    """

    def __init__(self, in_channels: int = 3, latent_dim: int = 256,
                 n_embeddings: int = 1024, commitment_cost: float = 0.25):
        super().__init__()
        self.latent_dim = latent_dim

        # Encodeur
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, latent_dim, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(latent_dim),
        )

        # Quantificateur vectoriel
        self.quantizer = VectorQuantizer(
            n_embeddings, latent_dim, commitment_cost
        )

        # Décodeur
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(latent_dim, 256,
                               kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(256, 128,
                               kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(128, in_channels,
                               kernel_size=4, stride=2, padding=1),
            nn.Tanh(),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor,
                                                 torch.Tensor, torch.Tensor]:
        """Passe avant complète : encodage → quantification → décodage.

        Args:
            x: Image d'entrée (B, 3, H, W), normalisée dans [-1, 1].

        Returns:
            Tuple (x_reconstruit, indices, perte_commitment, perplexité).
        """
        z = self.encoder(x)
        z_q, indices, commitment_loss, perplexity = self.quantizer(z)
        x_hat = self.decoder(z_q)
        return x_hat, indices, commitment_loss, perplexity

    def encode_to_indices(self, x: torch.Tensor) -> torch.Tensor:
        """Encode une image en indices du codebook.

        Args:
            x: Image d'entrée (B, 3, H, W).

        Returns:
            Indices du codebook (B, H/4 * W/4).
        """
        z = self.encoder(x)
        _, indices, _, _ = self.quantizer(z)
        return indices
```

### 1.3 Perte d'Entraînement

```python
def perte_vqgan(model: VQGAN, discriminateur: DiscriminateurPatchGAN,
                x: torch.Tensor, lambda_adv: float = 0.1,
                lambda_percept: float = 1.0) -> Tuple[torch.Tensor, dict]:
    """Calcule la perte combinée pour l'entraînement VQGAN.

    Args:
        model: Modèle VQGAN.
        discriminateur: Discriminateur PatchGAN.
        x: Images réelles (B, 3, H, W).
        lambda_adv: Poids de la perte adverse.
        lambda_percept: Poids de la perte perceptuelle.

    Returns:
        Tuple (perte_totale, dictionnaire des composantes de perte).
    """
    x_hat, indices, commitment_loss, perplexity = model(x)

    # Perte de reconstruction (L1 + L2)
    rec_loss_l1 = F.l1_loss(x_hat, x)
    rec_loss_l2 = F.mse_loss(x_hat, x)

    # Perte adverse (GAN)
    logits_fake = discriminateur(x_hat)
    adv_loss = F.binary_cross_entropy_with_logits(
        logits_fake, torch.ones_like(logits_fake)
    )

    # Perte totale
    total_loss = (rec_loss_l1 + rec_loss_l2
                  + commitment_loss
                  + lambda_adv * adv_loss)

    métriques = {
        'l1': rec_loss_l1.item(),
        'l2': rec_loss_l2.item(),
        'commitment': commitment_loss.item(),
        'adversarial': adv_loss.item(),
        'perplexité': perplexity.item(),
        'utilisation_codebook': perplexity.item() / model.quantizer.n_embeddings,
    }

    return total_loss, métriques
```

### 1.4 Calcul du Bitrate

```python
def calculer_bitrate(VQGAN, indices: torch.Tensor,
                     img_h: int, img_w: int) -> float:
    """Calcule le bitrate réel en bits par pixel (bpp).

    Args:
        indices: Indices du codebook (B, N).
        img_h, img_w: Dimensions de l'image originale.

    Returns:
        float: Bitrate en bpp.
    """
    n_indices = indices.shape[1]  # Nombre de tokens latents
    bits_par_indice = np.ceil(np.log2(VQGAN.quantizer.n_embeddings))
    total_bits = n_indices * bits_par_indice
    bpp = total_bits / (img_h * img_w)
    return bpp.item()


# Exemple d'utilisation
model = VQGAN(latent_dim=256, n_embeddings=1024)
img_h, img_w = 256, 256
x = torch.randn(1, 3, img_h, img_w)

with torch.no_grad():
    x_hat, indices, _, _ = model(x)

bpp = calculer_bitrate(model, indices, img_h, img_w)
print(f"Bitrate : {bpp:.3f} bpp")
# Pour 256×256 avec facteur de réduction 4, codebook 1024 (10 bits) :
#   n_indices = 64×64 = 4096
#   bpp = 4096 * 10 / (256 * 256) = 0.625 bpp
```

---

## 2. Performances vs Codecs Standards

| Codec | Bitrate (bpp) | PSNR (dB) | Usage |
|-------|--------------|-----------|-------|
| JPEG (qualité 75) | 0.50–0.80 | 32–36 | Usage général web |
| JPEG 2000 | 0.25–0.50 | 34–38 | Archives, médical |
| BPG (HEVC intra) | 0.10–0.25 | 36–40 | Compression moderne |
| **VQGAN standard** | **0.10–0.30** | **28–32** | Compression extrême |
| **VQGAN extrême** | **0.04–0.10** | **24–28** | Archives longue durée |
| FLIF | 0.15–0.40 | 35–39 | Compression sans perte proche |

> **Note :** Le PSNR du VQGAN est inférieur à celui des codecs standards car il optimise la **qualité perceptuelle** (LPIPS, FID), pas la fidélité pixel par pixel. À 0.04 bpp, un VQGAN produit une image reconnaissable là où JPEG produirait des artefacts de blocage massifs.

---

## 3. Métriques d'Évaluation

```python
import lpips

def évaluer_compression(VQGAN, dataloader: torch.utils.data.DataLoader,
                         device: str = 'cuda') -> dict:
    """Évalue la qualité de compression VQGAN sur un ensemble de test.

    Args:
        model: Modèle VQGAN entraîné.
        dataloader: DataLoader d'images de test.
        device: Périphérique de calcul.

    Returns:
        dict: Métriques moyennes (PSNR, SSIM, LPIPS, bitrate, FID si calculable).
    """
    model = VQGAN.to(device).eval()
    lpips_fn = lpips.LPIPS(net='alex').to(device)

    psnr_total = 0.0
    lpips_total = 0.0
    bitrates = []
    n = 0

    with torch.no_grad():
        for x, _ in dataloader:
            x = x.to(device)
            x_hat, indices, _, _ = model(x)

            # PSNR
            mse = F.mse_loss(x_hat, x).item()
            psnr = 10 * np.log10(4.0 / mse)  # images dans [-1, 1]
            psnr_total += psnr

            # LPIPS (similarité perceptuelle)
            lpips_val = lpips_fn(x, x_hat).mean().item()
            lpips_total += lpips_val

            # Bitrate
            for i in range(x.shape[0]):
                bpp = calculer_bitrate(model, indices[i:i+1],
                                       x.shape[2], x.shape[3])
                bitrates.append(bpp)

            n += x.shape[0]

    return {
        'PSNR (dB)': psnr_total / n,
        'LPIPS': lpips_total / n,
        'Bitrate moyen (bpp)': np.mean(bitrates),
        'Bitrate min (bpp)': np.min(bitrates),
        'Bitrate max (bpp)': np.max(bitrates),
    }
```

---

## 4. Boucle d'Entraînement

```python
def entraîner_vqgan(model: VQGAN, dataloader, n_epochs: int = 100,
                    lr: float = 1e-4, device: str = 'cuda'):
    """Boucle d'entraînement VQGAN complète.

    Args:
        model: Modèle VQGAN à entraîner.
        dataloader: DataLoader d'entraînement.
        n_epochs: Nombre d'époques.
        lr: Taux d'apprentissage.
        device: Périphérique de calcul.

    Note:
        Surveiller la perplexité du codebook : si elle descend
        en dessous de 10% de K (taille du codebook), activer l'EMA
        update ou réinitialiser les embeddings inutilisés.
    """
    model = model.to(device)
    disc = DiscriminateurPatchGAN().to(device)

    optim_g = torch.optim.Adam(model.parameters(), lr=lr)
    optim_d = torch.optim.Adam(disc.parameters(), lr=lr * 0.5)

    for epoch in range(n_epochs):
        for batch_idx, (x, _) in enumerate(dataloader):
            x = x.to(device)

            # --- Entraînement du générateur (VQGAN) ---
            optim_g.zero_grad()
            loss_g, métriques = perte_vqgan(model, disc, x)
            loss_g.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optim_g.step()

            # --- Entraînement du discriminateur ---
            optim_d.zero_grad()
            with torch.no_grad():
                x_hat, _, _, _ = model(x)
            logits_real = disc(x)
            logits_fake = disc(x_hat)

            loss_d_real = F.binary_cross_entropy_with_logits(
                logits_real, torch.ones_like(logits_real)
            )
            loss_d_fake = F.binary_cross_entropy_with_logits(
                logits_fake, torch.zeros_like(logits_fake)
            )
            loss_d = (loss_d_real + loss_d_fake) * 0.5
            loss_d.backward()
            optim_d.step()

            if batch_idx % 100 == 0:
                print(f"Epoch {epoch:3d} | Batch {batch_idx:4d} | "
                      f"G: {loss_g.item():.3f} | D: {loss_d.item():.3f} | "
                      f"Perplex: {métriques['perplexité']:.1f} | "
                      f"Codebook: {métriques['utilisation_codebook']:.1%}")

    torch.save({
        'state_dict': model.state_dict(),
        'disc_state_dict': disc.state_dict(),
        'optim_g': optim_g.state_dict(),
        'optim_d': optim_d.state_dict(),
    }, 'vqgan_entraîné.pt')
```

---

## 5. Pièges Courants

| Piège | Symptôme | Solution |
|-------|----------|----------|
| **Codebook collapse** | Perplexité < 5 % de K ; seuls quelques embeddings sont utilisés | Activer la mise à jour EMA du codebook ; réinitialiser les embeddings inactifs ; réduire le taux d'apprentissage |
| **Qualité insuffisante à très bas bitrate** | Image reconstruite floue, détails manquants | Augmenter `n_embeddings` ou la dimension latente `latent_dim` |
| **Discriminateur trop fort** | La perte GAN domine, la reconstruction s'effondre | Réduire `lambda_adv` (0.01–0.1) ; ajouter du gradient penalty (WGAN-GP) |
| **Discriminateur trop faible** | Images reconstruites lisses, pas de détails haute-fréquence | Augmenter `lambda_adv` ; améliorer l'architecture du discriminateur |
| **Mauvaise normalisation** | Les valeurs d'entrée ne sont pas dans [-1, 1] | Normaliser avec `(x / 127.5) - 1.0` avant l'encodeur |
| **Tail recursion du codebook** | Certains embeddings ne sont jamais utilisés (10-20% inactifs) | Normal : tant que l'utilisation > 70 %, c'est acceptable. Sinon, réinitialisation périodique |
| **Erreur de dimension latent** | Le facteur de réduction spatiale ne correspond pas | Vérifier que `H / 2^n × W / 2^n` donne la bonne grille latente |
| **Bitrate mal calculé** | Le bpp réel ne correspond pas à l'attendu | Compter les indices, pas la dimension du codebook ; inclure les overheads (entropy coding si applicable) |
| **Sur-optimisation pour PSNR** | Bon PSNR, mauvaise qualité perceptuelle | Évaluer avec LPIPS et FID, pas seulement PSNR |

---

## 6. Checklist d'Implémentation et d'Évaluation

- [ ] L'encodeur et le décodeur sont symétriques (facteur de réduction identique).
- [ ] La normalisation des entrées est dans [-1, 1] (Tanh en sortie du décodeur).
- [ ] La taille du codebook (K ≥ 1024) est adaptée à la complexité des images.
- [ ] La dimension latente (d ≥ 256) est suffisante pour la résolution cible.
- [ ] Le straight-through estimator est correctement implémenté (détach sur z_q).
- [ ] La perte de commitment (β = 0.25) est incluse dans la fonction de coût.
- [ ] Le discriminateur est entraîné alternativement avec le générateur.
- [ ] L'utilisation du codebook est surveillée (% d'embeddings utilisés ≥ 70 %).
- [ ] Le taux de compression réel est mesuré en bpp sur un lot de test.
- [ ] La qualité perceptuelle (LPIPS, FID) est évaluée en plus du PSNR.
- [ ] Un checkpoint est sauvegardé après chaque époque (pour reprise).
- [ ] Les images originales et reconstruites sont visualisées côte à côte.
- [ ] La courbe d'entraînement (loss G, loss D, perplexité) est tracée.
- [ ] Le codebook est inspecté visuellement (PCA ou t-SNE des embeddings).

---

## Références

1. Esser, P., Rombach, R., & Ommer, B. (2021). Taming Transformers for High-Resolution Image Synthesis. *CVPR 2021*. [arXiv:2012.09841](https://arxiv.org/abs/2012.09841)
2. Van Den Oord, A., & Vinyals, O. (2017). Neural Discrete Representation Learning. *NeurIPS 2017*. [arXiv:1711.00937](https://arxiv.org/abs/1711.00937)
3. Rombach, R., Blattmann, A., Lorenz, D., Esser, P., & Ommer, B. (2022). High-Resolution Image Synthesis with Latent Diffusion Models. *CVPR 2022*. [arXiv:2112.10752](https://arxiv.org/abs/2112.10752)
4. Isola, P., Zhu, J.-Y., Zhou, T., & Efros, A. A. (2017). Image-to-Image Translation with Conditional Adversarial Networks. *CVPR 2017*.
5. Zhang, R., Isola, P., Efros, A. A., Shechtman, E., & Wang, O. (2018). The Unreasonable Effectiveness of Deep Features as a Perceptual Metric. *CVPR 2018*.

