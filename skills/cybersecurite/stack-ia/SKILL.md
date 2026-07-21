---
name: stack-ia
description: Architecture IA complète — OpenRouter (texte/images propres), llama.cpp local (texte +18), ComfyUI/Flux local (images/vidéos +18), répartition GPU, et choix de modèles par usage.
---

# Stack IA — Architecture Complète

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      REQUEST                             │
│                  (texte ou image)                        │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │ SFW ?   │   │ NSFW ?  │   │ NSFW ?  │
    │ Texte   │   │ Texte   │   │ Image   │
    └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │OpenRoute│   │llama.cpp│   │ ComfyUI │
    │  (API)  │   │ (GPU 1) │   │ (GPU 0) │
    └─────────┘   └─────────┘   └─────────┘
```

---

## Répartition GPU (2× RTX 3090)

| GPU | Usage | VRAM |
|-----|-------|------|
| **GPU 0** | ComfyUI (Stable Diffusion/Flux) + birefnet | 2.8 GB + libre |
| **GPU 1** | llama.cpp (LLM local) | 13 MB → 4-5 GB après chargement modèle |

---

## Choix des modèles par usage

| Usage | Où | Modèle | Coût |
|-------|----|--------|------|
| Chatbot clean | OpenRouter | **Qwen 2.5 72B** (gratuit) | 🆓 |
| Chatbot premium | OpenRouter | **DeepSeek V3** | $ |  
| Chatbot +18 | llama.cpp GPU1 | **Qwen 2.5 7B Q4** (local) | Gratuit |
| Images propres | OpenRouter | Gemini Pro Image | $ |
| Images +18 | ComfyUI GPU0 | Flux Dev + LoRA | Gratuit |
| Vidéos +18 | ComfyUI GPU0 | AnimateDiff | Gratuit |

### Modèles open-source recommandés (GGUF pour llama.cpp)

| Modèle | Taille Q4 | VRAM | Points forts |
|--------|-----------|------|-------------|
| **Qwen 2.5 7B Instruct** | 4.7 GB | ~5 GB | 🇫🇷 Excellent français, roleplay |
| **Qwen 2.5 14B Instruct** | 8.5 GB | ~9 GB | 🇫🇷 Meilleur français, plus intelligent |
| **DeepSeek V2 Lite** | 8 GB | ~9 GB | Raisonnement, code |
| **Mistral 7B v0.3** | 4.5 GB | ~5 GB | Standard, fiable |
| **Llama 3.1 8B** | 5 GB | ~5.5 GB | Polyvalent, instruct |

---

## Avantages de cette architecture

- **Pas de censure** sur le contenu +18 (tout en local)
- **Pas cher** pour le contenu propre (OpenRouter gratuit)
- **Rapide** pour le texte (API cloud < 1s vs local 5-10s)
- **GPU utilisé intelligemment** : 1 pour l'image, 1 pour le texte
- **Scalable** : on peut ajouter des GPU ou passer plus sur le cloud
