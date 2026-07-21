# ComfyUI Pipeline — Leçons terrain (Juillet 2026)

Leçons apprises lors du déploiement complet de ComfyUI sur serveur distant
(TheHive, 2× RTX 3090, Debian 13, driver NVIDIA 550, CUDA 12.4).

---

## 1. Installation ComfyUI sur serveur distant

### Connexion SSH via paramiko (Python)
```python
import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("IP", username="user", password="pass", timeout=10)

def run(cmd, timeout=120):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode() + stderr.read().decode()
```

### Installation manuelle (sans comfy-cli)
```bash
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI
python3 -m venv ~/ComfyUI/venv --without-pip
curl -sL https://bootstrap.pypa.io/get-pip.py | ~/ComfyUI/venv/bin/python3
~/ComfyUI/venv/bin/pip install -r requirements.txt
```

### ⚠️ Piège PyTorch CUDA — LE PIÈGE #1
```bash
# ❌ MAUVAIS — pip installe cu130 par défaut (incompatible driver 550)
pip install torch torchvision torchaudio

# ✅ BON — forcer CUDA 12.4 avec --index-url (PAS --extra-index-url!)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Vérifier :
python3 -c "import torch; print(torch.version.cuda, torch.cuda.is_available())"
# Doit afficher "12.4 True" — si "13.0 False" → driver trop vieux
```

### ⚠️ ComfyUI zombie — LE PIÈGE #2
```bash
# pkill ne marche pas toujours. Forcer par PID :
ss -tlnp | grep 8188           # trouver le PID
kill -9 <PID>                   # tuer directement
rm -f ~/ComfyUI/user/comfyui.db.lock  # nettoyer le lock
```

### Lancement sur GPU spécifique
```bash
cd ~/ComfyUI
CUDA_VISIBLE_DEVICES=1 nohup ~/ComfyUI/venv/bin/python3 main.py \
  --listen 0.0.0.0 --port 8188 > /tmp/comfyui.log 2>&1 &
```

---

## 2. Téléchargement de modèles

### Flux Dev fp8 (17 Go)
```bash
# ❌ hf_hub_download via paramiko timeout sur >10 Go
# ✅ curl -L suit les redirections HF et est fiable
curl -L --max-time 900 -o ~/ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors \
  "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors"
```

### ⚠️ Fichier corrompu — LE PIÈGE #3
```
Symptôme : SafetensorError: Error while deserializing header: incomplete metadata
Cause    : Téléchargement incomplet renommé manuellement (fichier .incomplete)
Solution : TOUJOURS vérifier que curl retourne 100% avant d'utiliser le fichier.
           curl -L imprime la progression. Attendre "100%" confirmé.
```

### UNET vs Checkpoints
```bash
# Flux Dev doit être dans models/unet/ (PAS models/checkpoints/)
# Solution : symlink
mkdir -p ~/ComfyUI/models/unet
ln -sf ~/ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors ~/ComfyUI/models/unet/flux1-dev-fp8.safetensors
```

### Flux VAE — pas gated
```bash
# La VAE Flux est gated sur black-forest-labs/FLUX.1-dev
# Utiliser le miroir public frankjoshua :
curl -L -o ~/ComfyUI/models/vae/ae.safetensors \
  "https://huggingface.co/frankjoshua/FLUX.1-dev/resolve/main/ae.safetensors"
```

### CLIP + T5 (Flux text encoders)
```bash
curl -L -o ~/ComfyUI/models/clip/clip_l.safetensors \
  "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
curl -L -o ~/ComfyUI/models/clip/t5xxl_fp8_e4m3fn.safetensors \
  "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors"
```

---

## 3. LoRAs — Sources et téléchargement

### HuggingFace (gratuit, sans auth)
```
XLabs-AI/flux-RealismLora → lora.safetensors (22 Mo)
  → URL : https://huggingface.co/XLabs-AI/flux-RealismLora/resolve/main/lora.safetensors
```

### CivitAI (nécessite API token)
```
Format URL : https://civitai.com/api/download/models/{MODEL_VERSION_ID}?token={API_KEY}

Modèles testés et fonctionnels (Juillet 2026) :

| ID Version | Nom | Taille | Usage |
|-----------|-----|--------|-------|
| 667086 | aidmaNSFWunlock | 55 Mo | Déverrouillage NSFW Flux |
| 1778764 | Fanvue/OnlyFans Woman033 | 37 Mo | Personnage influenceuse |
| 1219805 | Nude Style V2 | 292 Mo | Anatomie NSFW (à tester) |
| 2811484 | SexGod Female Nudity | 633 Mo | Anatomie féminine NSFW |

⚠️ Les IDs de modèles (pas de versions) échouent — toujours utiliser l'ID de VERSION.
```

---

## 4. ReActor — Face Swap

### Installation
```bash
git clone --depth 1 https://github.com/Gourieff/ComfyUI-ReActor.git custom_nodes/ComfyUI-ReActor
pip install -r custom_nodes/ComfyUI-ReActor/requirements.txt

# Modèle de face swap
mkdir -p models/insightface
wget -O models/insightface/inswapper_128.onnx \
  "https://github.com/facefusion/facefusion-assets/releases/download/models-3.0.0/inswapper_128.onnx"
```

### ⚠️ ONNX Runtime GPU — LE PIÈGE #4
```
Symptôme : ReActor ne charge pas dans ComfyUI
Cause    : onnxruntime-gpu 1.27.0 nécessite CUDA 13.x (driver 550 = CUDA 12.4)
Solution : pip install onnxruntime-gpu==1.20.1
Vérifier : python3 -c "import onnxruntime; print(onnxruntime.get_available_providers())"
           Doit afficher 'CUDAExecutionProvider'
```

### Workflow ReActor
```json
{
  "class_type": "ReActorFaceSwapOpt",
  "inputs": {
    "enabled": true,
    "input_image": ["generated_image_node", 0],
    "source_image": ["reference_face_node", 0],
    "swap_model": "inswapper_128.onnx",
    "facedetection": "retinaface_resnet50",
    "face_restore_model": "codeformer-v0.1.0.pth",
    "face_restore_visibility": 0.8,
    "codeformer_weight": 0.8
  }
}
```
⚠️ Utiliser `ReActorFaceSwapOpt` (avec `source_image` en optionnel) — PAS `ReActorFaceSwap`.

---

## 5. Workflow Flux Dev — Points clés

### CLIPTextEncodeFlux — LE PIÈGE #5
```json
// ❌ MAUVAIS — CLIPTextEncode normal ne marche pas pour Flux
{"class_type": "CLIPTextEncode", "inputs": {"text": "...", "clip": ["11", 0]}}

// ✅ BON — CLIPTextEncodeFlux prend clip_l ET t5xxl en STRING séparés
{"class_type": "CLIPTextEncodeFlux", "inputs": {
    "clip": ["11", 0],
    "clip_l": "votre prompt ici",
    "t5xxl": "votre prompt ici",
    "guidance": 3.5
}}
```

### LoRA avec Flux
```json
// Insérer LoraLoaderModelOnly entre UNETLoader et le scheduler/guider
{"class_type": "LoraLoaderModelOnly", "inputs": {
    "model": ["unet_node", 0],
    "lora_name": "flux_realism.safetensors",
    "strength_model": 1.0
}}
// La sortie MODEL de LoraLoaderModelOnly va dans BasicScheduler ET BasicGuider
```

### Pipeline complet validé
```
LoadImage (visage référence)
    ↓
UNETLoader → LoraLoaderModelOnly → BasicScheduler + BasicGuider
    ↓                                    ↑
CLIPTextEncodeFlux ──────────────────────┘
    ↓
SamplerCustomAdvanced → VAEDecode → IMAGE
    ↓
ReActorFaceSwapOpt (source_image = LoadImage)
    ↓
ImageUpscaleWithModel (4x_foolhardy_Remacri)
    ↓
SaveImage

⏱️ 85 secondes sur RTX 3090 (GPU1)
📦 Sortie : PNG 4096×4096, ~14 Mo
```

### Workflow minimal validé (Flux Dev + LoRA + Upscale)
```python
workflow = {
    "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["12", 0], "lora_name": "flux_realism.safetensors", "strength_model": 1.0}},
    "6": {"class_type": "CLIPTextEncodeFlux", "inputs": {"clip": ["11", 0], "clip_l": prompt, "t5xxl": prompt, "guidance": 3.5}},
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
    "30": {"class_type": "UpscaleModelLoader", "inputs": {"model_name": "4x_foolhardy_Remacri.pth"}},
    "31": {"class_type": "ImageUpscaleWithModel", "inputs": {"upscale_model": ["30", 0], "image": ["8", 0]}},
    "32": {"class_type": "SaveImage", "inputs": {"filename_prefix": "output", "images": ["31", 0]}}
}
```

---

## 6. Soumission de workflow via REST

```python
import urllib.request, json

data = json.dumps({"prompt": workflow}).encode()
req = urllib.request.Request("http://HOST:8188/prompt", data=data,
    headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())
pid = result["prompt_id"]

# Vérifier le résultat
import time; time.sleep(45)
resp = urllib.request.urlopen(f"http://HOST:8188/history/{pid}")
history = json.loads(resp.read())
# Chercher les images dans history["outputs"]
```

### ⚠️ 400 Bad Request
```
Cause 1 : Nom de modèle incorrect dans le workflow → vérifier object_info
Cause 2 : CLIPTextEncode au lieu de CLIPTextEncodeFlux pour Flux
Cause 3 : Champ requis manquant → lire les inputs exacts dans /object_info
```

---

## 7. Upload image de référence (ReActor source)

```python
# Via SFTP
sftp = client.open_sftp()
sftp.put("visage_reference.png", "/home/aza/ComfyUI/input/ref.png")
sftp.close()

# Dans le workflow
{"class_type": "LoadImage", "inputs": {"image": "ref.png"}}
```

---

## 8. Upscalers

```bash
# 4x-UltraSharp (général)
wget -O models/upscale_models/4x-UltraSharp.pth \
  "https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth"

# 4x-Remacri (optimisé visages)
wget -O models/upscale_models/4x_foolhardy_Remacri.pth \
  "https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth"
```

---

## 9. Diagnostic rapide

```bash
# Vérifier que ComfyUI tourne
curl -s http://HOST:8188/system_stats | python3 -m json.tool

# Lister les nœuds dispo (chercher un nœud spécifique)
curl -s http://HOST:8188/object_info | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print([k for k in d if 'ReActor' in k])"

# Voir les logs d'erreur
grep -i 'error\|fail\|exception' /tmp/comfyui.log | tail -20

# Vérifier l'utilisation GPU
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader

# Tuer un process zombie
ss -tlnp | grep 8188 && kill -9 $(ss -tlnp | grep 8188 | grep -oP 'pid=\K\d+')
```
