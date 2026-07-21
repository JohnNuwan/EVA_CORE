# Pipeline ComfyUI — Flux + ReActor + LoRA + Upscale

## Stack recommandée pour TheHive (GPU1, RTX 3090)

```
CUDA_VISIBLE_DEVICES=1 python3 main.py --listen 0.0.0.0 --port 8188
```

### Modèles nécessaires

| Fichier | Emplacement | Source |
|---------|-------------|--------|
| `flux1-dev-fp8.safetensors` | `models/checkpoints/` + symlink dans `models/unet/` | Comfy-Org/flux1-dev |
| `ae.safetensors` | `models/vae/` | frankjoshua/FLUX.1-dev |
| `clip_l.safetensors` | `models/clip/` | comfyanonymous/flux_text_encoders |
| `t5xxl_fp8_e4m3fn.safetensors` | `models/clip/` | comfyanonymous/flux_text_encoders |
| `inswapper_128.onnx` | `models/insightface/` | facefusion/facefusion-assets |

### LoRAs utiles (CivitAI, token requis)

| LoRA | Model ID | Taille | Usage |
|------|----------|--------|-------|
| nsfw_unlock | 667086 | 55 Mo | aidmaNSFWunlock trigger |
| sexgod_female | 2811484 | 633 Mo | Anatomie NSFW |
| fanvue_model | 1778764 | 37 Mo | Style influenceuse |
| flux_realism | — (HF) | 22 Mo | Photoréalisme |

### Pipeline workflow (JSON API)

Structure minimale pour Flux Dev + LoRA + ReActor + Upscale :

```
DualCLIPLoader → CLIPTextEncodeFlux (clip_l + t5xxl séparés)
UNETLoader → LoraLoaderModelOnly → BasicScheduler + BasicGuider
                                    → SamplerCustomAdvanced
                                    → VAEDecode
LoadImage(ref) + VAEDecode → ReActorFaceSwapOpt
                           → ImageUpscaleWithModel
                           → SaveImage
```

**Piège CLIPTextEncodeFlux** : nécessite 2 entrées string (`clip_l` et `t5xxl`), pas 1 comme CLIPTextEncode standard.

### ReActor face swap

Pour cohérence faciale sans entraînement LoRA : générer une image de référence par persona, puis l'appliquer à toutes les générations via `ReActorFaceSwapOpt` avec `source_image` pointant vers la référence. CodeFormer après swap pour restaurer les détails.

### Temps de génération (GPU1 RTX 3090)

| Pipeline | Temps |
|----------|-------|
| Flux seul | 30-35s |
| Flux + ReActor + Upscale | 80-85s |

### Problème connu — Entraînement LoRA local

Le format ComfyUI (safetensors uniques pour VAE/UNET) est incompatible avec l'écosystème d'entraînement diffusers (fichiers shardés + configs JSON). Toute tentative d'entraînement local via `from_pretrained("black-forest-labs/FLUX.1-dev")` ou `from_single_file` locale échoue.

**Solutions** :
1. **CivitAI LoRA Trainer** — Upload des images, LoRA prêt en 30 min
2. **FluxGym** — Interface web pour entraînement Flux
3. **Attendre le téléchargement complet HF** (24 Go, token nécessaire)
