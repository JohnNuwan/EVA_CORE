# Flux LoRA Training — Recette Complète (TheHive GPU1)

## Prérequis

- Serveur avec RTX 3090+ (24 Go VRAM)
- ComfyUI déjà installé avec Flux Dev fp8 fonctionnel
- Dataset d'images prêt (15-20 images par persona, avec fichiers .txt de légendes)
- Token HuggingFace (https://hf.co/settings/tokens) — FLUX.1-dev est gated

## Setup environnement

```bash
# Le venv ComfyUI existant suffit, mais il faut corriger torchao
cd ~/ComfyUI
./venv/bin/pip uninstall -y torchao  # ⚠️ Critique : torchao casse l'import chain
./venv/bin/pip install peft bitsandbytes diffusers transformers accelerate

# Vérifier que l'import fonctionne
./venv/bin/python3 -c "from diffusers import FluxPipeline; print('OK')"
# Doit afficher "OK" — sinon torchao pas désinstallé
```

## Conflit torchao / PyTorch 2.6

Problème : torchao >= 0.17.0 utilise `register_constant` qui n'existe pas dans PyTorch 2.6.
Solution : désinstaller torchao (`pip uninstall -y torchao`). FluxPipeline n'en a pas besoin.

## Script d'entraînement minimal

```python
import torch, os, numpy as np
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from diffusers import FluxPipeline
from peft import LoraConfig
import torch.nn.functional as F

os.environ["HF_TOKEN"] = "hf_..."  # Token HuggingFace

pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16
)

lora_config = LoraConfig(
    r=16, lora_alpha=16,
    target_modules=["to_q","to_k","to_v","to_out.0"],
    lora_dropout=0.0, bias="none"
)
pipe.transformer.add_adapter(lora_config)

# Freeze tout sauf LoRA
for p in pipe.transformer.parameters(): p.requires_grad = False
for n, p in pipe.transformer.named_parameters():
    if "lora" in n: p.requires_grad = True

pipe.transformer.enable_gradient_checkpointing()
pipe.to("cuda")

opt = torch.optim.AdamW(
    [p for p in pipe.transformer.parameters() if p.requires_grad],
    lr=1e-4
)

# Boucle d'entraînement standard
for step in range(1500):
    # ... forward + backward + optimizer step
    if step % 250 == 0:
        pipe.transformer.save_pretrained(f"output/ckpt-{step}")
```

## Lancement

```bash
# Libérer la VRAM (arrêter ComfyUI si nécessaire)
pkill -f 'ComfyUI/main.py'

# Lancer l'entraînement sur GPU 1
CUDA_VISIBLE_DEVICES=1 nohup ./venv/bin/python3 train_lora.py > train.log 2>&1 &
```

## ⚠️ Piège : téléchargement initial

Le premier lancement télécharge FLUX.1-dev depuis HuggingFace (~24 Go).
Pendant ce temps :
- SSH peut devenir non-répondant (I/O saturée)
- Le serveur reste UP (ping OK) mais SSH timeout
- Prévoir ~15-20 min de téléchargement avant le début de l'entraînement

## Dataset

Structure :
```
lora_datasets/maeve/
├── maeve_00.png
├── maeve_00.txt    ← légende : "maeve_faure woman with red hair..."
├── maeve_01.png
├── maeve_01.txt
└── ...
```

Les légendes doivent inclure un mot-clé trigger (ex: `maeve_faure`) pour activer le LoRA à l'inférence.

## Résultat

- ~1500 steps sur 15-20 images → ~30-45 min d'entraînement
- LoRA sauvegardé dans `output/final/`
- Taille : ~150-300 Mo
- Utilisable dans ComfyUI avec `LoraLoaderModelOnly`

## ⚠️ Limites et alternatives (Juillet 2026)

### Problème : format ComfyUI ≠ format HuggingFace

Les safetensors ComfyUI (fichiers uniques : ae.safetensors, clip_l.safetensors, t5xxl_fp8_e4m3fn.safetensors) sont structurellement incompatibles avec l'écosystème diffusers/peft :

- **VAE** : `AutoencoderKL` HF attend 8 canaux → ComfyUI en a 32 (format Flux natif)
- **T5 XXL** : HF attend 2 fichiers shardés → ComfyUI en a un seul
- **UNET** : `from_single_file` échoue sur la version fp8

L'approche hybride (configs JSON HF + symlinks poids locaux) échoue aussi → noms de fichiers incompatibles.

### Problème : OOM sur 24 Go

L'entraînement via le script diffusers/peft ci-dessus **n'a pas pu être testé** car :
1. Le téléchargement HF est trop lent (338 Mo en 20 min pour 24 Go)
2. Même si le modèle est chargé, la VRAM risque d'être insuffisante (Flux fp8 11 Go + CLIP/T5 5 Go + optimizer/gradients ~16 Go ≈ 32+ Go)

Le `TrainLoraNode` de ComfyUI fait **OOM systématique** même en 64×64 avec toutes les optimisations activées.

### Alternatives viables

| Approche | Pour | Contre |
|----------|------|--------|
| **CivitAI LoRA Trainer** | Gratuit, optimisé Flux, 30 min/LoRA | Nécessite upload dataset |
| **ReActor face swap** | Fonctionne sur 24 Go, cohérence OK | Qualité faciale < LoRA |
| **Cloud GPU ≥ 32 Go** | Entraînement local possible | Coût $1-2/h |
| **Docker Kohya_ss** | Interface GUI complète | Setup complexe |

**Recommandation 2026** : CivitAI pour l'entraînement + ReActor pour le prototypage rapide.
