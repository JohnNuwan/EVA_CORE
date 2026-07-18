---
name: local-ai-stack
description: >-
  Infrastructure IA locale multi-services avec Docker Compose — vLLM pour
  le serving de LLMs, ComfyUI pour la génération d'images, Portainer pour
  la gestion. Configuration multi-GPU, profils de modèles, et bonnes
  pratiques pour machines avec plusieurs RTX 3090.
category: devops
---

# Stack IA Local avec Docker

## Présentation

Ce skill documente la configuration et la gestion d'une infrastructure IA
locale basée sur Docker Compose. Conçu pour des machines multi-GPU
(2× RTX 3090, 126GB RAM, 32 CPUs) avec des services IA modulaires qu'on
allume et éteint selon les besoins.

## Architecture

```
docker-compose.yml (profils: big, small, uncensored, comfyui)
├── portainer      — UI web de gestion (port 9443), toujours actif
├── vllm-big       — Qwen2.5-32B-Instruct AWQ (~18GB VRAM, port 8001)
├── vllm-small     — Qwen2.5-7B-Instruct AWQ (~5GB VRAM, port 8002)
├── vllm-uncensored — dolphin-2.9-llama3-8b (~6GB VRAM, port 8003)
└── comfyui        — Génération d'images Flux (port 8188)
```

## Principe clé : profils Docker Compose

Chaque service utilise un `profile` Docker Compose. Un seul modèle vLLM
à la fois sur un GPU (sauf small + uncensored qui peuvent cohabiter ~11GB).
On allume/éteint les services via Portainer ou CLI.

```bash
docker compose up -d portainer                              # Manager (toujours)
docker compose --profile small up -d vllm-small             # Petit modèle
docker compose --profile big up -d vllm-big                 # Gros modèle
docker compose --profile uncensored up -d vllm-uncensored   # Non censuré
docker compose --profile big down                           # Éteindre gros
docker compose ps                                           # État des services
```

## Critère de choix : vLLM vs llama.cpp vs Ollama

L'utilisateur préfère vLLM pour le serving de LLMs sur GPU :
- **vLLM** : continuous batching, PagedAttention, quantification AWQ/GPTQ
  native, tensor parallelism multi-GPU. Optimal pour GPU serving.
- **llama.cpp** : optimisé CPU, pas fait pour tourner sur GPU de façon
  performante. Bon pour des setups CPU-only.
- **Ollama** : wrapper simplifié de llama.cpp, trop limité pour un usage
  multi-agent 24/7 avec contrôle fin de la configuration.

## Pitfall critique : mismatch version CUDA Docker vs driver hôte

**Symptôme** : Le container vLLM crash au démarrage avec :
`Error 804: forward compatibility was attempted on non supported HW`

**Cause** : L'image `vllm/vllm-openai:latest` peut inclure CUDA 13.0
qui nécessite un driver récent. Si le driver hôte est plus ancien
(ex: 550.163.01 = CUDA 12.4 max), le container ne peut pas initialiser CUDA.

**Solution** : Utiliser une image vLLM plus ancienne qui embarque CUDA 12.x :
```bash
# Vérifier la version CUDA dans l'image
docker image inspect vllm/vllm-openai:latest --format '{{.Config.Env}}' | tr ' ' '\n' | grep CUDA

# Si CUDA >= 13.0 et driver hôte < 560, utiliser une image plus ancienne
docker pull vllm/vllm-openai:v0.8.4  # CUDA 12.x
```

**Vérification** : Driver hôte avec `nvidia-smi`, version CUDA du container
avec `docker image inspect`. Le container doit avoir CUDA <= version supportée
par le driver hôte.

## Configuration GPU

Chaque container déclare ses besoins GPU via `deploy.resources` :
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ["1"]    # GPU 1 (GPU 0 réservé à l'entraînement)
          capabilities: [gpu]
```

**Assignation flexible** : Au lieu d'attribuer des GPUs fixes, on peut
changer le `device_ids` selon les besoins. Quand l'entraînement est fini,
on peut relancer vLLM avec `device_ids: ["0", "1"]` et `tensor-parallel-size: 2`.

## Pitfall : « GPU non utilisé » ≠ GPU libre (processus idle vs calcul)

**Symptôme** : L'utilisateur rapporte « les 2 GPUs ne sont pas utilisés »,
mais `nvidia-smi` montre des processus avec de la mémoire allouée et 0%
d'utilisation.

**Diagnostic** : `nvidia-smi` affiche l'occupation **mémoire** ET
l'utilisation **compute** séparément. Un processus peut détenir plusieurs
GB de VRAM tout en étant à 0% de calcul (idle, en attente de requêtes).

Exemple réel (The Hive) :
```
GPU 0 : birefnet_ml_backend (Label Studio) — 2.8 GB, 0% util
GPU 1 : vllm-small (API OpenAI)            — 5.8 GB, 0% util
```

Les deux GPUs sont **réservés** par des services Docker actifs mais ne
calculent rien. Pour l'entraînement, il faut soit :
- Arrêter les services : `docker stop vllm-small` (ou via Portainer)
- Ou cohabiter si la VRAM restante suffit (vLLM small laisse ~19 GB libres)

**Vérification avant entraînement** :
```bash
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=table
docker ps --format "table {{.Names}}\t{{.Status}}"
```
Ne pas confondre « mémoire allouée » et « GPU en train de calculer ».

## Modèles recommandés par cas d'usage

| Profil | Modèle | VRAM | Cas d'usage |
|--------|--------|------|-------------|
| small | Qwen2.5-7B-Instruct-AWQ | ~5GB | Petites tâches rapides |
| big | Qwen2.5-32B-Instruct-AWQ | ~18GB | Raisonnement complexe, FR excellent |
| uncensored | dolphin-2.9-llama3-8b | ~6GB | Non censuré, créatif |
| comfyui | Flux1-dev-fp8 | ~8GB | Génération d'images |

**Évolution multi-machine** : Quand on relie plusieurs machines (Wireguard
VPN + Docker Swarm), on peut viser des modèles plus gros :
- 2 GPUs (48GB) : Llama 3.1 70B AWQ
- 6 GPUs (144GB) : Llama 3.1 405B quantifié, ou plusieurs modèles spécialisés

## API OpenAI-compatible

vLLM expose une API OpenAI-compatible sur le port du container :
```bash
# Tester le modèle
curl http://localhost:8002/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-7B-Instruct-AWQ",
    "messages": [{"role": "user", "content": "Bonjour"}]
  }'
```

Les agents (bug bounty, influenceuse IA, agents autonomes) consomment
cette API comme s'ils parlaient à OpenAI, mais en local.

## Check-list de déploiement

1. [ ] Vérifier `nvidia-smi` : driver version et CUDA version supportée
2. [ ] Vérifier que le runtime NVIDIA Docker est installé (`docker info | grep nvidia`)
3. [ ] Tester : `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi`
4. [ ] Vérifier les ports disponibles (`ss -tlnp`) — MinIO occupe 9000 par défaut,
      ne pas utiliser 9000 pour Portainer (utiliser 9443 à la place)
5. [ ] Choisir l'image vLLM avec la bonne version CUDA (cf. pitfall ci-dessus)
6. [ ] Monter les volumes : `~/.cache/huggingface` pour les modèles, `ComfyUI/models` pour les checkpoints
7. [ ] Démarrer Portainer en premier, puis les services selon les besoins
8. [ ] Vérifier que le GPU cible est libre (`nvidia-smi`) avant de lancer un service

## Fichiers de référence

- `templates/docker-compose.yml` — Template complet avec profils
