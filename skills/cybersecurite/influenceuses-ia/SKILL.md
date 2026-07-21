---
name: influenceuses-ia
description: Guide complet sur les influenceuses IA — génération d'images (Stable Diffusion, Flux, ComfyUI), plateformes (Fanvue, OnlyFans, Patreon), automatisation Instagram/TikTok, OSINT sur créateurs, et monétisation.
---

# Influenceuses IA — Guide Complet

---

## 0. Phase Stratégique — Recherche de Marché & Création de Persona

**À FAIRE AVANT TOUTE GÉNÉRATION D'IMAGE.** Ne pas sauter cette étape.

### Workflow
1. **Collecte** — Rechercher les 20-30 influenceuses réelles les plus performantes (Instagram + TikTok)
2. **Analyse statistique** — Compiler les caractéristiques physiques en tableaux avec pourcentages
3. **Extraction des patterns** — Identifier les niches rentables, archétypes qui percent
4. **Design du persona** — Chaque attribut doit être justifié par les données, pas l'intuition

### Références
→ [[references/market-research-persona-creation.md]] — méthodologie détaillée, templates, pièges
→ [[references/onlyfans-top-earners-physique-2026.md]] — données physiologiques du top 10 OnlyFans
→ [[references/multi-persona-portfolio-strategy.md]] — stratégie de création d'un PORTFOLIO de 5 personas complémentaires

### Mode Multi-Personas (recommandé)

Ne pas créer UN seul persona, mais un PORTFOLIO de 4-5 personas complémentaires :
- Chaque persona cible une niche différente (Fashion, Fitness, Glamour, Gaming, Travel, Tech/IA)
- Chaque persona a un physique et une origine ethnique distincts
- Création parallèle avec `delegate_task` en batch (~6 min pour 4 personas)

Pièges :
- Les subagents ne se coordonnent pas sur les préfixes de fichiers → vérifier et renommer si conflit
- Spécifier explicitement "Écris TOUT en français" dans le contexte de chaque subagent
- Exiger 300+ lignes minimum dans les consignes

### Niches sous-exploitées (fort potentiel)

| Niche | Pourquoi | Physique gagnant |
|-------|----------|-----------------|
| **Tech/IA** | Concurrence quasi nulle, audience masculine tech, boom IA 2026 | Rousse = différenciant ultime (0.6% pop) |
| **Gaming/E-girl** | Sous-exploitée en France, audience jeune + engagée | Mince, look alternatif, yeux rares (verts) |
| **Surf/Fitness outdoor** | Post-JO 2024, aucune influenceuse fitness FR ne surfe | Blonde bronzée, corps athlétique naturel |

### Line-up éprouvé (14 Juillet 2026)

6 personas data-driven créés et testés en une session :

| # | Persona | Niche | Physique | Lignes |
|---|---------|-------|----------|--------|
| 1 | Lyra Amari | Fashion/Lifestyle | Brune sablier 1,67m | 405 |
| 2 | Sienna Delcourt | Fitness/Surf | Blonde yeux bleus 1,68m | 600 |
| 3 | Valentina d'Almeida | Glamour/Luxe | Brune pulpeuse 95C 1,62m | 797 |
| 4 | Yuna Fontaine | Gaming/Art | Mèches roses yeux verts 1,65m | 632 |
| 5 | Maëlys Rivers | Travel/Bohème | Blonde ondulée 1,70m | 678 |
| 6 | Maeve Faure | Tech/IA | Rousse 95C yeux verts 1,70m | 993 |

→ [[references/multi-persona-lineup-2026.md]] pour les fiches détaillées

### Génération rapide d'images (prototypage)

Avant de passer par ComfyUI/Flux (lourd), utiliser `image_generate` (Hermes) pour prototyper :
- Les prompts secondaires des fiches personas sont directement utilisables
- Génération par lots de 3 images en parallèle
- Organiser les images dans `images/` avec nom cohérent : `[prenom]_[contexte].png`

**⚠️ Limite** : les images cloud NE SONT PAS fiables pour les portraits. Les yeux/visages changent d'une génération à l'autre. Réserver le prototypage cloud aux :
- Images de contexte (paysage, ambiance, décor)
- Tests rapides de composition
- Variations de style

Pour les portraits → pipeline local ComfyUI obligatoire ([[references/comfyui-local-pipeline.md]]).
→ [[references/comfyui-pipeline-lessons.md]] — pièges PyTorch CUDA, ReActor ONNX, CLIPTextEncodeFlux, IDs LoRA CivitAI, workflow complet validé
→ [[references/comfyui-workflow-api-patterns.md]] — workflow JSON complet (Flux + LoRA + ReActor + Upscale), soumission API, erreurs de validation, stacking LoRAs
→ [[references/comfyui-pitfalls.md]] — corrections rapides : CUDA mismatch, torchao, ReActor ONNX, CLIPTextEncodeFlux, téléchargements

### LoRAs recommandés (CivitAI + HuggingFace)

Téléchargement CivitAI nécessite un token API :
```
URL : https://civitai.com/api/download/models/{VERSION_ID}?token={API_KEY}
⚠️ Utiliser l'ID de VERSION, pas l'ID du modèle
```

| LoRA | Source | ID Version | Taille | Usage |
|------|--------|-----------|--------|-------|
| flux_realism | HF XLabs-AI | — | 22 Mo | Photoréalisme base |
| aidmaNSFWunlock | CivitAI | 667086 | 55 Mo | Déverrouillage NSFW Flux |
| Fanvue Woman033 | CivitAI | 1778764 | 37 Mo | Personnage influenceuse |
| SexGod Female | CivitAI | 2811484 | 633 Mo | Anatomie féminine NSFW |
| Nude Style V2 | CivitAI | 1219805 | 292 Mo | Anatomie NSFW (à vérifier) |

→ [[references/flux-lora-training.md]] — entraînement LoRA custom Flux pour chaque persona

---

## 1. Génération d'images — Outils

| Outil | Type | Force |
|-------|------|-------|
| **Stable Diffusion** | Open-source local | Gratuit, customisable, ComfyUI |
| **Flux (Black Forest Labs)** | Open-source | Hyper-réalisme, meilleur que SD |
| **Midjourney** | SaaS payant | Qualité artistique, cohérence |
| **DALL-E 3 / GPT Image** | SaaS OpenAI | Intégré ChatGPT, simple |
| **Leonardo.ai** | SaaS | Interface simple, fine-tuning |
| **ComfyUI** | GUI local | Workflows visuels, nœuds |

### Stack recommandée (gratuite, locale)
```
ComfyUI + Flux Dev + LoRA custom + ReActor + ADetailer
→ Génération locale sur RTX 3090
→ ReActor : même visage sur toutes les images
→ ADetailer : correction automatique yeux/visage
→ Export automatique vers Instagram/Fanvue
```

### ⚠️ Piège : génération cloud vs locale

Les générateurs cloud (Gemini/DALL-E via API) ont des **défauts récurrents** :
- **Yeux** : asymétriques, pupilles irrégulières, reflets incohérents ← #1 point d'échec
- **Visage** : change d'une image à l'autre (pas de cohérence faciale)
- **Mains** : doigts fusionnés ou surnuméraires
- **Réalisme** : rendu "plastique" sans texture de peau naturelle

**Solution : PIPELINE LOCAL ComfyUI** — recette complète → [[references/comfyui-local-pipeline.md]]
```
Flux Dev fp8 (base photorealism, 11 Go)
  → ReActor + inswapper_128 (face swap — même visage)
  → ADetailer / Impact Pack (auto-fix yeux, visage)
  → ESRGAN 4x-UltraSharp / 4x-Remacri (upscale)
```
Setup sur serveur distant : utiliser paramiko (Python) si pas de clé SSH.
→ `python3 -m venv /tmp/sshenv && /tmp/sshenv/bin/pip install paramiko`
→ Connecter : `SSHClient().connect(host, username, password)`
→ GPU 1 libre en standard pour ComfyUI, GPU 0 pour Ollama/LLM.
→ Lancer : `CUDA_VISIBLE_DEVICES=1 ~/ComfyUI/venv/bin/python main.py --listen 0.0.0.0`

**Quand utiliser quoi :**
| Usage | Outil | Pourquoi |
|-------|-------|----------|
| Prototypage rapide | `image_generate` (Hermes) | Itération immédiate, 3 images en // |
| Images secondaires | `image_generate` | Paysages, ambiances — les défauts se voient moins |
| Portraits principaux | Pipeline local ComfyUI | Cohérence faciale OBLIGATOIRE |
| Variations d'un persona | Pipeline local ReActor | Même visage, poses/tenues différentes |

### LoRAs recommandés (CivitAI + HuggingFace)

Téléchargement CivitAI nécessite un token API :
```
URL : https://civitai.com/api/download/models/{VERSION_ID}?token={API_KEY}
⚠️ Utiliser l'ID de VERSION, pas l'ID du modèle
⚠️ curl -L pour suivre les redirections
```

| LoRA | Source | ID Version | Taille | Usage |
|------|--------|-----------|--------|-------|
| flux_realism | HF XLabs-AI | — | 22 Mo | Photoréalisme base |
| aidmaNSFWunlock | CivitAI | 667086 | 55 Mo | Déverrouillage NSFW Flux |
| Fanvue Woman033 | CivitAI | 1778764 | 37 Mo | Personnage influenceuse |
| SexGod Female | CivitAI | 2811484 | 633 Mo | Anatomie féminine NSFW |

### Prompt engineering pour réalisme
```
"hyperrealistic 8k photograph of a 25-year-old french woman,
 natural lighting, golden hour, casual outfit,
 shot on Canon EOS R5, 85mm f/1.2, sharp focus,
 photorealistic skin texture, subsurface scattering"
```

---

## 2. Plateformes de monétisation

| Plateforme | Commission | IA-friendly | Public cible |
|------------|-----------|-------------|-------------|
| **Fanvue** | 15% | ✅ Oui (officiellement) | Early adopters, tech |
| **OnlyFans** | 20% | ⚠️ Toléré mais pas officiel | Mainstream |
| **Patreon** | 5-12% | ✅ Oui | Contenu artistique |
| **MYM** | 25% | ⚠️ France, non documenté | Marché français |
| **Instagram** | 0% (subs) | ⚠️ Toléré | Brand deals |

### Stratégie Fanvue (2026)
1. Créer un compte avec photos IA cohérentes (>50 posts)
2. Prix d'abonnement : 5-15$/mois
3. Contenu : photos lifestyle + exclusivités
4. Promotion croisée Instagram → Fanvue
5. DM automatisés pour upsell

---

## 3. Automatisation Instagram

### Outils
| Outil | Usage |
|-------|-------|
| **instagrapi** (Python) | API privée, upload, messages, stories |
| **Instaloader** (Python) | Scraping, download, metadata |
| **InstaPy** (Python) | Like/follow/unfollow automatisé |
| **ManyChat** | DMs automatisés |
| **Buffer / Later** | Planification de posts |

### instagrapi — Commandes clés
```python
from instagrapi import Client
cl = Client()
cl.login("username", "password")

# Upload photo
cl.photo_upload("photo.jpg", "Caption avec hashtags")

# Upload story
cl.video_upload_to_story("story.mp4")

# Envoyer un DM
cl.direct_send("Message automatique", user_ids=[12345])

# Récupérer followers
followers = cl.user_followers(cl.user_id)
```

### Instaloader — Scraping
```bash
instaloader profile cible --no-videos
instaloader --login=USER --password=PASS profile cible
```

---

## 4. Automatisation TikTok

| Outil | Usage |
|-------|-------|
| **TikTokApi** (Python) | Upload, analytics |
| **gallery-dl** | Download contenu |
| **CapCut API** | Montage automatique |

---

## 5. Stack technique complète

```
┌─────────────────────────────────────────────┐
│  ComfyUI (génération images)                 │
│  │                                            │
│  ├─→ images/                                 │
│  │                                            │
│  ├─→ instagrapi (upload Instagram)            │
│  ├─→ TikTokApi (upload TikTok)                │
│  ├─→ Fanvue API (upload Fanvue)              │
│  │                                            │
│  └─→ monitoring/ (analytics, logs)           │
│       ├─ followers.csv                        │
│       ├─ engagement.csv                       │
│       └─ revenue.csv                          │
│                                                │
│  Docker + Traefik (reverse proxy)              │
│  Cron jobs (posts planifiés)                   │
└─────────────────────────────────────────────┘
```

---

## 6. OSINT sur influenceuses IA

### Détection d'influenceuses IA
- **Mains** : doigts mal formés, 6 doigts
- **Arrière-plans** : incohérences, flou anormal
- **Yeux** : reflets asymétriques, pupilles irrégulières
- **Métadonnées** : absence de données EXIF réelles
- **Paternité** : pas de vidéos spontanées
- **Historique** : apparition soudaine sans passé

### Outils de détection
```bash
# Analyse d'image
exiftool image.jpg | grep -i "software\|make\|model"
# Une image IA n'aura pas de "Camera Model Name"

# AI or Not (API)
curl -X POST https://api.aiornot.com/v1/detect -F "image=@photo.jpg"

# Sightengine (détection nudité + IA)
curl -X POST https://api.sightengine.com/1.0/check.json \
  -F "media=@photo.jpg" \
  -F "models=genai,nudity"
```

---

## 7. Fanvue — API et automatisation

```python
import requests

# Récupérer le profil
def get_profile(username):
    r = requests.get(f"https://fanvue.com/api/v1/{username}")
    return r.json()

# Envoyer un post (nécessite token)
def post_content(token, image_path, caption):
    with open(image_path, 'rb') as f:
        r = requests.post(
            "https://fanvue.com/api/v1/post",
            headers={"Authorization": f"Bearer {token}"},
            files={"media": f},
            data={"caption": caption}
        )
    return r.json()
```

---

## 8. Analytics & Monitoring

```python
import pandas as pd
from datetime import datetime

# Suivi quotidien des métriques
metrics = {
    "date": datetime.now().isoformat(),
    "instagram_followers": 0,
    "instagram_engagement": 0,
    "fanvue_subs": 0,
    "fanvue_revenue": 0,
    "tiktok_views": 0,
}

df = pd.DataFrame([metrics])
df.to_csv("metrics.csv", mode='a', header=False)
```

---

---

## 10. Projet influenceur_IA_fanvue (GitHub JohnNuwan)

**Stack technique** :
```
Docker Compose :
├── Frontend (React/Vue.js :3000)
├── Backend (FastAPI :8000)
├── PostgreSQL (:5432)
├── Redis (:6379)
├── Ollama (:11434)
├── MinIO (:9000)
├── Prometheus (:9090)
├── Grafana (:3001)
└── Traefik (reverse proxy)
```

**Fonctionnalités** :
- Génération IA : Stable Diffusion + Midjourney + Pika Labs
- Voix : ElevenLabs
- Chatbot : Ollama local
- Réseaux : Twitter/X, Instagram, Reddit, Fanvue, OnlyFans
- Analytics : Prometheus + Grafana
- Multi-influenceuses : dashboard admin

- **ComfyUI** : https://github.com/comfyanonymous/ComfyUI
- **Flux** : https://github.com/black-forest-labs/flux
- **instagrapi** : https://github.com/subzeroid/instagrapi
- **Fanvue** : https://fanvue.com
- **CivitAI** (modèles/embeddings) : https://civitai.com
- **Aitrepreneur** : https://www.youtube.com/@Aitrepreneur
