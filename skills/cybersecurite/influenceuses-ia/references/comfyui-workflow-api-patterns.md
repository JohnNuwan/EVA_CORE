# ComfyUI Workflow API — Patterns et pièges

## Workflow validé (Flux + LoRA + ReActor + Upscale)

```json
{
  "1": {"class_type": "LoadImage", "inputs": {"image": "ref_face.png"}},
  "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["12", 0], "lora_name": "flux_realism.safetensors", "strength_model": 1.0}},
  "6": {"class_type": "CLIPTextEncodeFlux", "inputs": {"clip": ["11", 0], "clip_l": "PROMPT", "t5xxl": "PROMPT", "guidance": 3.5}},
  "8": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["10", 0]}},
  "10": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
  "11": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "t5xxl_fp8_e4m3fn.safetensors", "clip_name2": "clip_l.safetensors", "type": "flux"}},
  "12": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux1-dev-fp8.safetensors", "weight_dtype": "fp8_e4m3fn"}},
  "13": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["25", 0], "guider": ["22", 0], "sampler": ["16", 0], "sigmas": ["17", 0], "latent_image": ["27", 0]}},
  "16": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
  "17": {"class_type": "BasicScheduler", "inputs": {"scheduler": "simple", "steps": 20, "denoise": 1.0, "model": ["2", 0]}},
  "22": {"class_type": "BasicGuider", "inputs": {"model": ["2", 0], "conditioning": ["6", 0]}},
  "25": {"class_type": "RandomNoise", "inputs": {"noise_seed": 42}},
  "27": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
  "40": {"class_type": "ReActorFaceSwapOpt", "inputs": {
    "enabled": true, "input_image": ["8", 0], "source_image": ["1", 0],
    "swap_model": "inswapper_128.onnx", "facedetection": "retinaface_resnet50",
    "face_restore_model": "codeformer-v0.1.0.pth", "face_restore_visibility": 0.8,
    "codeformer_weight": 0.8, "detect_gender_input": "no", "detect_gender_source": "no",
    "input_faces_index": "0", "source_faces_index": "0", "console_log_level": 0
  }},
  "30": {"class_type": "UpscaleModelLoader", "inputs": {"model_name": "4x_foolhardy_Remacri.pth"}},
  "31": {"class_type": "ImageUpscaleWithModel", "inputs": {"upscale_model": ["30", 0], "image": ["40", 0]}},
  "32": {"class_type": "SaveImage", "inputs": {"filename_prefix": "output", "images": ["31", 0]}}
}
```

⏱️ ~85s/image sur RTX 3090 — ~35s sans ReActor

## Soumission et monitoring

```python
import json, urllib.request, time

data = json.dumps({"prompt": workflow}).encode()
req = urllib.request.Request("http://HOST:8188/prompt", data=data, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())
pid = result["prompt_id"]

# Attendre et récupérer le résultat
time.sleep(45)
resp = urllib.request.urlopen(f"http://HOST:8188/history/{pid}")
history = json.loads(resp.read())
for nid, out in history.get("outputs", {}).items():
    if "images" in out:
        for img in out["images"]:
            print(img["filename"])  # → /ComfyUI/output/filename
```

## Erreurs de validation fréquentes

Quand `400 Bad Request`, les logs ComfyUI (`/proc/PID/fd/1`) donnent les valeurs acceptées :

```
[ERROR] Value not in list: optimizer: 'adamw' not in ['AdamW', 'Adam', 'SGD', 'RMSprop']
[ERROR] Value not in list: algorithm: 'lora' not in ['LoRA', 'LoHa', 'LoKr', 'OFT']
[ERROR] Value not in list: lora_dtype: 'fp16' not in ['bf16', 'fp32']
[ERROR] Value 0 smaller than min of 1: checkpoint_depth
```

→ Corriger la casse et les valeurs selon la liste exacte donnée dans l'erreur.

## Pièges CLIPTextEncodeFlux

- ❌ `"clip": ["11", 0]` avec `"text": "..."` → erreur silencieuse
- ✅ `"clip": ["11", 0], "clip_l": "PROMPT", "t5xxl": "PROMPT", "guidance": 3.5`

Le nœud prend `clip_l` et `t5xxl` comme textes SÉPARÉS, pas un champ `text` unique.

## Stacking de LoRAs

Les LoRAs se chaînent via `LoraLoaderModelOnly` en série :

```
UNETLoader → LoraLoaderModelOnly(LoRA1) → LoraLoaderModelOnly(LoRA2) → LoraLoaderModelOnly(LoRA3)
                                                                          ↓
                                                              BasicScheduler + BasicGuider
```

Exemple de stacking NSFW : `flux_realism(1.0) → nsfw_unlock(0.8) → sexgod_female(0.6)`

## Upload de référence ReActor

```python
sftp = client.open_sftp()
sftp.put("local_face.png", "/home/aza/ComfyUI/input/ref_face.png")
```

Le fichier doit être dans `ComfyUI/input/` — le nœud `LoadImage` le trouve sans chemin.
