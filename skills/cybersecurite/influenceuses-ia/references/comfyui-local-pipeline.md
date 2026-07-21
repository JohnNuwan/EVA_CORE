# Pipeline ComfyUI Local pour Influenceuses IA — Recette Complète

Session du 14 Juillet 2026 — Setup vérifié sur TheHive (Debian 13, 2× RTX 3090).

---

## Pourquoi un pipeline local ?

Les API cloud (Gemini, DALL-E) produisent des défauts récurrents :
- **Yeux** : asymétriques, pupilles irrégulières, reflets incohérents
- **Visage** : change d'une image à l'autre (zéro cohérence faciale)
- **Réalisme** : texture "plastique", pas de grain de peau naturel
- **Mains** : doigts fusionnés ou surnuméraires

Le pipeline local corrige TOUT via 4 étapes chaînées.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                COMFYUI WORKFLOW                       │
│                GPU 1 — RTX 3090 24 Go                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Étape 1 : Flux Dev fp8                              │
│  └─ Base photorealism, prompt détaillé               │
│                                                      │
│  Étape 2 : ReActor (inswapper_128)                   │
│  └─ Face swap : applique le visage de référence       │
│  └─ MÊME visage sur TOUTES les images du persona     │
│                                                      │
│  Étape 3 : ADetailer (Impact Pack)                   │
│  └─ Détecte et corrige yeux, iris, symétrie faciale  │
│  └─ Passe automatique, pas de retouche manuelle       │
│                                                      │
│  Étape 4 : ESRGAN 4x-UltraSharp / 4x-Remacri         │
│  └─ Upscale HD sans perte de qualité                 │
│  └─ Remacri optimisé pour les visages                 │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Installation complète (serveur Linux Debian + NVIDIA)

### Prérequis
- GPU NVIDIA ≥12 Go VRAM (RTX 3090 recommandé)
- Python 3.10+, git, wget
- ~20 Go disque libre (modèles)

### Step 1 : Cloner ComfyUI et créer venv

```bash
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI
mkdir -p ~/ComfyUI/models/{checkpoints,vae,loras,upscale_models,controlnet,clip,unet,insightface}

python3 -m venv ~/ComfyUI/venv --without-pip
curl -sL https://bootstrap.pypa.io/get-pip.py | ~/ComfyUI/venv/bin/python3

# PyTorch CUDA
~/ComfyUI/venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Dépendances ComfyUI
~/ComfyUI/venv/bin/pip install -r ~/ComfyUI/requirements.txt
```

### Step 2 : Modèles obligatoires

| Modèle | Taille | Rôle | Source |
|--------|--------|------|--------|
| **Flux Dev fp8** | 11 Go | Base photorealism | `Comfy-Org/flux1-dev` sur HuggingFace |
| **Flux VAE** | 330 Mo | Encodeur/décodeur | `frankjoshua/FLUX.1-dev` (miroir public) |
| **CLIP L** | 240 Mo | Encodage prompt | `comfyanonymous/flux_text_encoders` |
| **T5 XXL fp8** | 5 Go | Encodage prompt | `comfyanonymous/flux_text_encoders` |

Téléchargement via huggingface_hub (depuis le venv ComfyUI) :
```python
from huggingface_hub import hf_hub_download
hf_hub_download('Comfy-Org/flux1-dev', 'flux1-dev-fp8.safetensors',
                local_dir='/home/aza/ComfyUI/models/checkpoints')
```

### Step 3 : Custom nodes

```bash
CN="$HOME/ComfyUI/custom_nodes"

# Manager (gestion modèles)
git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager.git $CN/ComfyUI-Manager

# Impact Pack (ADetailer)
git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Impact-Pack.git $CN/ComfyUI-Impact-Pack
cd $CN/ComfyUI-Impact-Pack && ~/ComfyUI/venv/bin/pip install -r requirements.txt

# ReActor (face swap)
git clone --depth 1 https://github.com/Gourieff/ComfyUI-ReActor.git $CN/ComfyUI-ReActor
cd $CN/ComfyUI-ReActor && ~/ComfyUI/venv/bin/pip install -r requirements.txt

# Ultimate SD Upscale
git clone --depth 1 https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git $CN/ComfyUI_UltimateSDUpscale
```

### Step 4 : Modèles complémentaires

```bash
# ReActor face model (530 Mo)
wget -O ~/ComfyUI/models/insightface/inswapper_128.onnx \
  'https://github.com/facefusion/facefusion-assets/releases/download/models-3.0.0/inswapper_128.onnx'

# Upscalers
wget -O ~/ComfyUI/models/upscale_models/4x-UltraSharp.pth \
  'https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth'

wget -O ~/ComfyUI/models/upscale_models/4x_foolhardy_Remacri.pth \
  'https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth'
```

### Step 5 : Lancer sur GPU spécifique

```bash
# GPU 1 pour ComfyUI (GPU 0 réservé pour Ollama/LLM)
CUDA_VISIBLE_DEVICES=1 ~/ComfyUI/venv/bin/python ~/ComfyUI/main.py --listen 0.0.0.0 --port 8188
```

---

## Workflow par persona

### 1. Générer le visage de référence

Utiliser le **Prompt 1 (portrait signature)** de la fiche persona avec Flux Dev.
→ Générer 5-10 variations, sélectionner la meilleure comme référence.

### 2. Générer les images secondaires

Utiliser les **Prompts 2 et 3** de la fiche persona (fitness, lifestyle, travel...).
→ Chaque image passe par ReActor avec le visage de référence.

### 3. Pipeline complet

```
[Prompt persona] → Flux Dev → [image brute]
                              ↓
                    ReActor (visage référence) → [visage cohérent]
                              ↓
                    ADetailer (auto-fix yeux) → [yeux corrigés]
                              ↓
                    ESRGAN 4x → [image finale HD]
```

---

## Connexion SSH au serveur distant

Quand le serveur est accessible uniquement par mot de passe (pas de clé SSH) :

```python
# Installer paramiko dans un venv temporaire
python3 -m venv /tmp/sshenv --without-pip
curl -sL https://bootstrap.pypa.io/get-pip.py | /tmp/sshenv/bin/python3
/tmp/sshenv/bin/pip install paramiko

# Utiliser
import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("IP", username="user", password="pass", timeout=10)

def run(cmd, timeout=180):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.read().decode() + stderr.read().decode()
```

Pièges :\n- `sshpass` n'est pas toujours installable sans sudo\n- `pexpect` est instable avec SSH\n- `paramiko` est la solution la plus fiable pour l'automatisation\n- ⚠️ `exec_command(cmd + ' &')` NE FONCTIONNE PAS de manière fiable avec paramiko :\n  le processus meurt quand la connexion SSH se ferme. Utiliser `nohup ... &`\n  ou écrire un script Python sur le serveur et le lancer avec `nohup`.\n- Les téléchargements volumineux (>5 Go) peuvent faire timeout le canal SSH\n  paramiko (le processus continue mais paramiko perd la connexion).\n  → Lancer les téléchargements en arrière-plan avec un script `nohup`.\n\n### Récupération d'un téléchargement HuggingFace interrompu\n\nQuand `hf_hub_download` est interrompu (timeout SSH, crash réseau), le fichier\npartiellement téléchargé reste dans le cache HuggingFace avec l'extension\n`.incomplete`. Si le fichier a la bonne taille, on peut le récupérer :\n\n```bash\n# Trouver le fichier incomplet\nls ~/ComfyUI/models/checkpoints/.cache/huggingface/download/*.incomplete\n\n# Vérifier sa taille (Flux Dev fp8 = ~15 Go)\nstat -c%s fichier.incomplete\n\n# Si la taille est correcte, renommer\nmv fichier.incomplete ~/ComfyUI/models/checkpoints/flux1-dev-fp8.safetensors\nrm -f ~/ComfyUI/models/checkpoints/.cache/huggingface/download/*.lock\n```\n\n### Source alternative pour inswapper_128.onnx\n\nLe téléchargement depuis HuggingFace (`ezioruan/inswapper_128.onnx`) échoue\nsouvent (fichier vide). Utiliser la source GitHub facefusion-assets :\n\n```bash\n# ✅ Source fiable (530 Mo)\nwget -O ~/ComfyUI/models/insightface/inswapper_128.onnx \\\n  'https://github.com/facefusion/facefusion-assets/releases/download/models-3.0.0/inswapper_128.onnx'\n\n# ❌ Source instable (souvent 0 octets)\n# wget -O ... 'https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx'

---

## Prototypage rapide (avant le pipeline local)

Pour itérer VITE avant de lancer le pipeline lourd :

```python
# image_generate (Hermes) — 3 images en parallèle, ~15s chaque
image_generate(prompt="...", aspect_ratio="landscape")
```

Organiser dans `images/[prenom]_[contexte].png`.

**ATTENTION** : les images cloud servent UNIQUEMENT au prototypage et aux images "secondaires" (paysage, ambiance). Les portraits principaux DOIVENT passer par le pipeline local pour la cohérence faciale.

---

## Pièges critiques découverts en conditions réelles

### ⛔ PyTorch CUDA : `--extra-index-url` installe la MAUVAISE version
Le flag `--extra-index-url` AJOUTE l'URL sans forcer l'index → pip préfère la version la plus récente (cu130) qui ne fonctionne PAS avec le driver 550 (CUDA 12.4 max).
**Fix :** `--index-url` (pas `--extra-index-url`) pour FORCER l'index exact.
**Vérification obligatoire :** `python -c "import torch; print(torch.version.cuda)"` doit afficher `12.4`.

### ⛔ wget échoue sur HuggingFace → utiliser curl -L
`wget` ne suit pas la chaîne de redirections CDN de HuggingFace → retourne HTTP 401 ou fichiers de 0 octets.
**Fix :** `curl -L` (suit les redirections) pour TOUS les téléchargements HF :
```bash
curl -L -o model.safetensors "https://huggingface.co/REPO/resolve/main/FILE.safetensors"
```

### ⛔ Flux VAE gated sur black-forest-labs
`black-forest-labs/FLUX.1-dev` et `FLUX.1-schnell` retournent HTTP 401 pour le VAE.
**Fix :** utiliser le miroir public `frankjoshua/FLUX.1-dev`.

### ⛔ Flux Dev fp8 = 17 Go sur disque (pas 11 Go)
La taille réelle du fichier `flux1-dev-fp8.safetensors` est de ~17 Go.

### ⛔ Workflow JSON : pas de clé `_comment`
ComfyUI plante avec `AttributeError: 'str' object has no attribute 'get'` si le workflow contient une clé string au top-level. Supprimer TOUS les `_comment`.

### ⛔ ReActor nécessite CUDA 13.0 pour le GPU
ReActor v0.7.0 exige PyTorch CUDA 13.0 pour l'accélération GPU. Sur CUDA 12.4, il tombe en CPU avec un warning. Fonctionnel mais plus lent.

### ⛔ hf_hub_download peut laisser un .incomplete récupérable
Si le téléchargement est interrompu, le fichier `.incomplete` dans `.cache/huggingface/download/` peut être intact. Vérifier sa taille et le renommer.