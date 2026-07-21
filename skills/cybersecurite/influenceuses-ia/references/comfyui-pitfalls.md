# ComfyUI Pièges & Corrections (Flux + ReActor + LoRA)

## PyTorch CUDA : mismatch de version

**Problème** : `pip install torch` installe cu130, mais le driver NVIDIA 550 ne supporte que CUDA 12.4.
**Symptôme** : `torch.cuda.is_available() == False`
**Fix** :
```bash
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
# → PyTorch 2.6.0+cu124, CUDA available: True
```

## torchao incompatible PyTorch 2.6

**Problème** : `register_constant` n'existe pas dans `torch.utils._pytree` sous PyTorch 2.6.
**Symptôme** : `from diffusers import FluxPipeline` → AttributeError dans torchao
**Fix** : `pip uninstall -y torchao`

## ReActor : ONNX sans CUDA

**Problème** : onnxruntime-gpu 1.27.0 n'a pas de provider CUDA avec driver 12.4.
**Symptôme** : ReActor nodes absents du object_info, log: "ModuleNotFoundError: onnxruntime"
**Fix** :
```bash
pip uninstall -y onnxruntime onnxruntime-gpu
pip install onnxruntime-gpu==1.20.1
# → Providers: ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
```
Redémarrer ComfyUI après.

## CLIPTextEncodeFlux : inputs séparés

**Problème** : `CLIPTextEncodeFlux` prend `clip` (modèle), `clip_l` (texte), `t5xxl` (texte) — PAS un seul `text`.
**Erreur si mal fait** : HTTP 400 "Required input is missing: clip_l / t5xxl"
**Workflow correct** :
```json
"6": {"class_type": "CLIPTextEncodeFlux", "inputs": {
    "clip": ["11", 0],
    "clip_l": "le prompt textuel",
    "t5xxl": "le prompt textuel",
    "guidance": 3.5
}}
```

## DualCLIPLoader pour Flux

```json
"11": {"class_type": "DualCLIPLoader", "inputs": {
    "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",  // T5 d'abord
    "clip_name2": "clip_l.safetensors",             // CLIP L ensuite
    "type": "flux"
}}
```

## LoraLoaderModelOnly pour Flux

Flux n'a PAS de loader LoRA spécifique. Utiliser `LoraLoaderModelOnly` :
```json
"2": {"class_type": "LoraLoaderModelOnly", "inputs": {
    "model": ["12", 0],
    "lora_name": "flux_realism.safetensors",
    "strength_model": 1.0
}}
```
Chainer plusieurs LoRAs : `model` → LoRA1 → LoRA2 → scheduler/guider.

## ReActor face swap : source_image

`ReActorFaceSwapOpt` prend `source_image` en **optionnel** (pas required) :
```json
"40": {"class_type": "ReActorFaceSwapOpt", "inputs": {
    "enabled": true,
    "input_image": ["8", 0],      // image générée
    "source_image": ["1", 0],     // visage de référence (LoadImage)
    "swap_model": "inswapper_128.onnx",
    "facedetection": "retinaface_resnet50",
    "face_restore_model": "codeformer-v0.1.0.pth",
    "face_restore_visibility": 0.8,
    "codeformer_weight": 0.8
}}
```

## Téléchargement modèles HuggingFace

**wget échoue** car HuggingFace fait des redirections 302 vers CDN.
**Fix** : utiliser `curl -L` (suit les redirections) :
```bash
curl -L -o model.safetensors "https://huggingface.co/REPO/resolve/main/file.safetensors"
```

**Modèles gated (401)** : nécessite token HF. Alternatives :
- VAE Flux : `frankjoshua/FLUX.1-dev` (miroir public)
- CLIP/T5 : `comfyanonymous/flux_text_encoders` (public)

## Téléchargement CivitAI

Nécessite `?token=API_KEY` en paramètre URL :
```bash
curl -L -o lora.safetensors "https://civitai.com/api/download/models/{VERSION_ID}?token={KEY}"
```
⚠️ Utiliser l'ID de VERSION (pas l'ID du modèle).

## Fichier Flux corrompu

Si le téléchargement est interrompu (`.incomplete`), le fichier pèse la bonne taille mais est invalide.
**Symptôme** : `SafetensorError: Error while deserializing header: incomplete metadata`
**Fix** : re-télécharger, ne JAMAIS renommer un `.incomplete` en `.safetensors`.

## SSH down pendant gros téléchargements

Pendant le téléchargement Flux depuis HF (~24 Go) ou modèle lourd, SSH peut devenir non-répondant.
Le serveur reste UP (ping OK) mais SSH timeout. Normal — attendre la fin du téléchargement.
Cron job pour checker périodiquement recommandé.

## Workflow minimal Flux validé (1024×1024, 20 steps)

Nœuds : UNETLoader → LoraLoaderModelOnly → DualCLIPLoader → CLIPTextEncodeFlux → BasicGuider → BasicScheduler → KSamplerSelect → RandomNoise → EmptySD3LatentImage → SamplerCustomAdvanced → VAELoader → VAEDecode → [ReActorFaceSwapOpt] → [UpscaleModelLoader + ImageUpscaleWithModel] → SaveImage

## TrainLoraNode : OOM systématique sur Flux 24 Go

Le Trainer intégré ComfyUI (via Manager) ne tient PAS en 24 Go pour Flux, même avec :
- rank=8, résolution 64×64
- quantized_backward=True, offloading=True, gradient_checkpointing=True

**Raison** : Flux fp8 (~11 Go) + CLIP/T5 (~5 Go) + optimizer AdamW + gradients ≈ 32 Go minimum.

**Solutions** (par ordre de praticité) :
1. **CivitAI LoRA trainer** (cloud, gratuit) — uploader les images, télécharger le LoRA
2. **GPU 48 Go** (A6000, L40S)
3. **NF4 quantized Flux** — non testé, probablement plus lent

## ComfyUI safetensors ≠ HuggingFace diffusers

Les fichiers .safetensors utilisés par ComfyUI NE sont PAS chargeables par `diffusers.FluxPipeline.from_pretrained()`.

| Approche d'entraînement | Compatible ComfyUI ? |
|--------------------------|---------------------|
| `diffusers` + `peft` (Python) | ❌ Fichiers shardés + config.json requis |
| `TrainLoraNode` (ComfyUI) | ✅ Mais OOM sur 24 Go |
| Service CivitAI / Replicate | ✅ Indépendant du format |

**Ne pas essayer** : charger `ae.safetensors` via `AutoencoderKL.from_single_file()` → shape mismatch (Flux VAE ≠ SDXL VAE).

## Workflow JSON : pas de clés string

Les clés du workflow JSON DOIVENT être des IDs numériques (strings de chiffres).
Une clé `"_comment"` → HTTP 400 `AttributeError: 'str' object has no attribute 'get'`.
Toujours utiliser `{"prompt": {"1": {...}, "2": {...}}}` (pas de `_comment`).

## UNET Loader pour Flux : dossier models/unet/

Le `UNETLoader` de Flux cherche dans `models/unet/`, PAS `models/checkpoints/`.
Si le modèle est dans checkpoints, créer un symlink :
```bash
mkdir -p ~/ComfyUI/models/unet
ln -sf ~/ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors ~/ComfyUI/models/unet/flux1-dev-fp8.safetensors
```
