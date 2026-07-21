# Pipeline ComfyUI Fonctionnel — Génération d'Influenceuses IA

Dernière mise à jour : 14 Juillet 2026 — Testé sur TheHive (2× RTX 3090, Debian 13).

---

## Architecture matérielle

- **GPU 1** (RTX 3090, 24 Go) : ComfyUI dédié — Flux Dev fp8 + LoRAs + ReActor
- **GPU 0** (RTX 3090, 24 Go) : Libre pour autres tâches (entraînement, etc.)
- **Lancement** : `CUDA_VISIBLE_DEVICES=1 python3 main.py --listen 0.0.0.0 --port 8188`
- **VRAM utilisée** : ~17 Go (Flux 11 Go + CLIP 5 Go + ReActor 1 Go)

---

## Stack logicielle

| Composant | Version | Notes |
|-----------|---------|-------|
| ComfyUI | 0.27.0 | Installé via git clone |
| PyTorch | 2.6.0+cu124 | CUDA 12.4, attention : ne PAS installer cu130 |
| ONNX Runtime | 1.20.1-gpu | Version spécifique pour CUDA 12.4 |
| Python | 3.13.5 | — |

---

## Pipeline de génération (workflow validé)

```
LoadImage (visage référence)
    ↓
UNETLoader (flux1-dev-fp8.safetensors)
    ↓
LoraLoaderModelOnly (flux_realism.safetensors, strength=1.0)
    ↓
DualCLIPLoader (t5xxl_fp8_e4m3fn + clip_l)
    ↓
CLIPTextEncodeFlux (clip_l: prompt, t5xxl: prompt, guidance: 3.5)
    ↓
BasicScheduler + BasicGuider + RandomNoise + EmptySD3LatentImage (1024²)
    ↓
SamplerCustomAdvanced (euler, 20 steps)
    ↓
VAEDecode (ae.safetensors)
    ↓
ReActorFaceSwapOpt (inswapper_128.onnx, retinaface_resnet50, codeformer 0.8)
    ↓
UpscaleModelLoader (4x_foolhardy_Remacri.pth)
    ↓
ImageUpscaleWithModel
    ↓
SaveImage

⏱️ ~35-40s/image en 1024² (Flux + ReActor)
⏱️ ~85s en 4096² (avec Upscale 4K)
```

---

## ReActor — Configuration qui marche

- **Node** : `ReActorFaceSwapOpt` (PAS `ReActorFaceSwap` — le modèle Opt accepte `source_image`)
- **Face model** : `inswapper_128.onnx` (530 Mo, téléchargé depuis GitHub facefusion assets)
- **Détection** : `retinaface_resnet50`
- **Restauration** : `codeformer-v0.1.0.pth`, visibility 0.8, weight 0.8
- **Piège** : ONNX Runtime GPU doit être en v1.20.1 pour CUDA 12.4. La v1.27.0 ne fournit que CPU.

---

## LoRAs installés sur TheHive

| Fichier | Taille | Source | Usage |
|---------|--------|--------|-------|
| `flux_realism.safetensors` | 22 Mo | XLabs-AI (HF) | Photoréalisme général |
| `nsfw_unlock.safetensors` | 55 Mo | CivitAI #667086 | Déverrouillage NSFW (trigger: `aidmaNSFWunlock`) |
| `fanvue_model.safetensors` | 37 Mo | CivitAI #1778764 | Personnage Fanvue/OnlyFans |
| `sexgod_female.safetensors` | 633 Mo | CivitAI #2811484 | Anatomie féminine améliorée |

### Téléchargement CivitAI

Format : `https://civitai.com/api/download/models/{VERSION_ID}?token={API_KEY}`

⚠️ Les IDs sont des **version IDs** (ex: 2811484), PAS des model IDs (ex: 2439952).

---

## Modèles sur TheHive

| Modèle | Emplacement | Taille |
|--------|------------|--------|
| Flux Dev fp8 | `models/unet/flux1-dev-fp8.safetensors` | 17 Go |
| VAE | `models/vae/ae.safetensors` | 320 Mo |
| CLIP L | `models/clip/clip_l.safetensors` | 235 Mo |
| T5 XXL fp8 | `models/clip/t5xxl_fp8_e4m3fn.safetensors` | 4.6 Go |
| Remacri 4x | `models/upscale_models/4x_foolhardy_Remacri.pth` | 64 Mo |
| UltraSharp 4x | `models/upscale_models/4x-UltraSharp.pth` | 64 Mo |

---

## Pièges rencontrés

1. **Flux Dev corrompu** : le téléchargement initial (hf_hub_download tué) a produit un fichier .incomplete de 15 Go inutilisable. Re-télécharger avec `curl -L` depuis HuggingFace. Toujours vérifier avec `safetensors` que le fichier est valide.

2. **PyTorch cu130 incompatible** : le driver NVIDIA 550 ne supporte que CUDA 12.4. Forcer `--index-url https://download.pytorch.org/whl/cu124` (pas `--extra-index-url`).

3. **torchao casse tout** : si installé, il empêche l'import de `FluxPipeline`. Désinstaller : `pip uninstall torchao`.

4. **Entraînement LoRA bloqué** : Python 3.13 + PyTorch 2.6 est incompatible avec ai-toolkit, kohya_ss, et diffusers pour le training. Solution : venv séparé avec PyTorch 2.5.1 ou attendre màj des outils.

5. **CLIPTextEncodeFlux** : prend `clip` (DualCLIPLoader), `clip_l` (STRING prompt), `t5xxl` (STRING prompt). PAS comme CLIPTextEncode classique.

6. **CivitAI model ID vs version ID** : l'API attend `models/{VERSION_ID}`, pas `models/{MODEL_ID}`. Une version peut avoir plusieurs fichiers (SDXL, Flux, etc.).

7. **SSH timeout sur téléchargements longs** : utiliser `nohup` + log fichier plutôt que d'attendre dans paramiko.

---

## Datasets générés

52 images réparties sur 6 personas dans `/home/aza/lora_datasets/` :
- Chaque image a son fichier `.txt` de légende associé
- Les visages sont cohérents grâce à ReActor (même visage de référence)
- Prêtes pour entraînement LoRA dès qu'un environnement compatible est disponible
