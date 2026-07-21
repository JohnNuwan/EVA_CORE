# Pipeline ComfyUI Flux — Guide Complet (Juillet 2026)

Guide éprouvé pour installer et faire tourner Flux Dev + ReActor + Upscale sur une RTX 3090 (24 Go), dans le cadre du projet influenceuses IA.

## Stack validée

```
GPU1 RTX 3090 (24 Go) — CUDA 12.4, driver 550.163.01
PyTorch 2.6.0+cu124 (pip install --index-url https://download.pytorch.org/whl/cu124)
ComfyUI 0.27.0 — port 8188 — CUDA_VISIBLE_DEVICES=1
```

## Modèles — où les mettre

| Fichier | Dossier | Taille | Source |
|---------|---------|--------|--------|
| flux1-dev-fp8.safetensors | models/unet/ | 17 Go | Comfy-Org/flux1-dev |
| ae.safetensors (VAE) | models/vae/ | 320 Mo | frankjoshua/FLUX.1-dev (miroir public) |
| clip_l.safetensors | models/clip/ | 235 Mo | comfyanonymous/flux_text_encoders |
| t5xxl_fp8_e4m3fn.safetensors | models/clip/ | 4.6 Go | comfyanonymous/flux_text_encoders |
| 4x_foolhardy_Remacri.pth | models/upscale_models/ | 64 Mo | HuggingFace |
| 4x-UltraSharp.pth | models/upscale_models/ | 64 Mo | HuggingFace |
| inswapper_128.onnx | models/insightface/ | 530 Mo | facefusion assets |

⚠️ **Flux Dev se met dans models/unet/**, pas models/checkpoints/. Si déjà dans checkpoints → symlink.

## Téléchargement fiable depuis HuggingFace

```bash
# ✅ curl -L suit les redirections HF → CDN
curl -L -o models/unet/flux1-dev-fp8.safetensors \
  "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors"

# ❌ wget ne suit PAS les redirections HF → fichier 301/302 html
# ❌ huggingface_hub Python library → SSH timeout → fichier .incomplete CORROMPU
# ❌ Un .incomplete de la bonne taille (15 Go) est QUAND MÊME corrompu
```

## Nœuds critiques pour Flux

### CLIPTextEncodeFlux — piège #1
```json
{
  "class_type": "CLIPTextEncodeFlux",
  "inputs": {
    "clip": ["11", 0],        // DualCLIPLoader → un SEUL objet CLIP
    "clip_l": "le prompt",     // STRING — le texte lui-même
    "t5xxl": "le prompt",      // STRING — même texte
    "guidance": 3.5            // FLOAT
  }
}
```
❌ NE PAS utiliser CLIPTextEncode normal avec Flux.
❌ NE PAS essayer de splitter les sorties de DualCLIPLoader.

### DualCLIPLoader
```json
{
  "class_type": "DualCLIPLoader",
  "inputs": {
    "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
    "clip_name2": "clip_l.safetensors",
    "type": "flux"
  }
}
```

### UNETLoader
```json
{
  "class_type": "UNETLoader",
  "inputs": {
    "unet_name": "flux1-dev-fp8.safetensors",
    "weight_dtype": "fp8_e4m3fn"   // indispensable pour fp8
  }
}
```

### LoraLoaderModelOnly (stacking LoRAs)
```json
// Flux n'a pas besoin de loader LoRA spécifique
// Stack en série : UNET → Lora1 → Lora2 → Lora3
"2a": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["12", 0], "lora_name": "flux_realism.safetensors", "strength_model": 1.0}},
"2b": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["2a", 0], "lora_name": "nsfw_unlock.safetensors", "strength_model": 0.8}},
// Le dernier → Scheduler + Guider
```

### ReActorFaceSwapOpt — piège #2
```json
{
  "class_type": "ReActorFaceSwapOpt",  // PAS ReActorFaceSwap
  "inputs": {
    "enabled": true,
    "input_image": ["8", 0],
    "source_image": ["1", 0],  // visage de référence
    "swap_model": "inswapper_128.onnx",
    "facedetection": "retinaface_resnet50",
    "face_restore_model": "codeformer-v0.1.0.pth",
    "face_restore_visibility": 0.8,
    "codeformer_weight": 0.8
  }
}
```

## ONNX Runtime GPU — piège #3

```bash
# ❌ onnxruntime-gpu==1.27.0 → CPU only sur CUDA 12.4
# ✅ onnxruntime-gpu==1.20.1 → CUDAExecutionProvider
pip install onnxruntime-gpu==1.20.1
python -c "import onnxruntime; print(onnxruntime.get_available_providers())"
# Doit afficher : ['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider']
```

## Pipeline complet validé

```
LoadImage(ref_face) ─────────────────────────────┐
                                                  │ source_image
UNETLoader → LoraLoader(realism) → LoraLoader(nsfw) → Scheduler + Guider
                                                  │
DualCLIPLoader → CLIPTextEncodeFlux ──────────────┤
                                                  │
VAELoader → VAEDecode ← SamplerCustomAdvanced ────┘
             │
             ├→ ReActorFaceSwapOpt (input_image)
             │      │
             │      └→ UpscaleModelLoader → ImageUpscaleWithModel → SaveImage
```

⏱️ ~85 secondes/image en 4K sur RTX 3090 (20 steps, euler, guidance 3.5)

## LoRAs recommandés (CivitAI)

| LoRA | Model ID | Poids | Trigger |
|------|----------|-------|---------|
| NSFW Unlock | 667086 | 0.5-1.0 | aidmaNSFWunlock |
| Fanvue/OnlyFans | 1778764 | 1.0 | — |
| SexGod Female | 2811484 | 0.4-0.8 | — |
| Flux Realism (HF) | XLabs-AI | 1.0 | — |

Téléchargement CivitAI : `curl -L "https://civitai.com/api/download/models/{ID}?token={API_KEY}"`

## Port bloqué / process zombie

```bash
# pkill -f 'ComfyUI/main.py' peut échouer
kill -9 $(ss -tlnp | grep 8188 | grep -oP 'pid=\K\d+')
rm -f user/comfyui.db.lock
```
