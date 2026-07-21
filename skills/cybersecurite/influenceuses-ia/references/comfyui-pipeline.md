# Pipeline ComfyUI Local pour Influenceuses IA

Stack déployée sur TheHive (RTX 3090 GPU1, Debian 13, driver 550).

## Architecture

```
Flux Dev fp8 (UNET) + VAE + DualCLIP (T5 XXL + CLIP L)
       ↓
  Génération portrait 1024×1024 (~20 steps, euler/simple)
       ↓
  ReActor (inswapper_128.onnx) → face consistency
       ↓
  ADetailer (Impact Pack) → correction yeux/visage
       ↓
  4x-UltraSharp / 4x-Remacri → upscale
```

## Modèles déployés

| Modèle | Emplacement | Source |
|--------|------------|--------|
| flux1-dev-fp8.safetensors (15→11 Go) | checkpoints/ + unet/ (symlink) | Comfy-Org/flux1-dev |
| ae.safetensors (320 Mo) | vae/ | frankjoshua/FLUX.1-dev (miroir public) |
| clip_l.safetensors (235 Mo) | clip/ | comfyanonymous/flux_text_encoders |
| t5xxl_fp8_e4m3fn.safetensors (4.6 Go) | clip/ | comfyanonymous/flux_text_encoders |
| inswapper_128.onnx (530 Mo) | insightface/ | facefusion-assets (GitHub) |
| 4x-UltraSharp.pth (64 Mo) | upscale_models/ | lokCX/4x-Ultrasharp |
| 4x_foolhardy_Remacri.pth (64 Mo) | upscale_models/ | FacehugmanIII |

## Custom Nodes

- ComfyUI-Manager (V3.41)
- ComfyUI-Impact-Pack (V8.28.3) → ADetailer
- ComfyUI-ReActor → face swap
- ComfyUI_UltimateSDUpscale → upscale

## Lancement

```bash
cd /home/aza/ComfyUI
CUDA_VISIBLE_DEVICES=1 /home/aza/ComfyUI/venv/bin/python3 main.py --listen 0.0.0.0 --port 8188
```

## Pièges

1. **VAE gated** : black-forest-labs/FLUX.1-dev renvoie 401 → utiliser frankjoshua
2. **PyTorch CUDA** : driver 550 = CUDA 12.4 max → `--index-url .../cu124` (pas cu130)
3. **Téléchargements HF** : `curl -L` obligatoire (wget ne suit pas les redirects HF)
4. **Checkpoint corrompu** : ne jamais renommer un .incomplete → re-télécharger
5. **Symlink UNET** : Flux utilise models/unet/, pas models/checkpoints/
6. **Workflow API** : pas de clé `_comment`, `weight_dtype: "fp8_e4m3fn"`