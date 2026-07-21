# Multi-Persona Strategy — Lineup & Lessons (Juillet 2026)

## Résultat : 6 personas créés en 1 session

Méthode : `delegate_task` avec 4 agents parallèles (1 agent par persona) → création simultanée.

## Lineup complet

| # | Persona | Niche | Physique | Lignes | Fichier |
|---|---------|-------|----------|--------|---------|
| 1 | Lyra Amari | Fashion/Lifestyle | Brune sablier 1,67m 34C | 405 | 02_persona_lyra_amari.md |
| 2 | Sienna Delcourt | Fitness/Surf | Blonde fitness 1,68m 34B | 600 | 03_persona_sienna_delcourt.md |
| 3 | Valentina d'Almeida | Glamour/Luxe | Brune pulpeuse 1,62m 34D | 797 | 04_persona_valentina_dalmeida.md |
| 4 | Yuna Fontaine | Gaming/Art | Mèches roses 1,65m | 632 | 05_persona_yuna_fontaine.md |
| 5 | Maëlys Rivers | Travel/Bohème | Blonde élancée 1,70m 34B | 678 | 06_persona_maelys_rivers.md |
| 6 | Maeve Faure | Tech/IA | Rousse 95C 1,70m | 993 | 07_persona_maeve_faure.md |

## Stratégie de couverture

```
NICHES              PHYSIQUES             ORIGINES
Fashion      ●      Brune ×3       ●      Méditerranéenne ●
Fitness      ●      Blonde ×2      ●      Californienne   ●
Glamour      ●      Rousse ×1      ●      Brésilienne     ●
Gaming       ●                        Irlandaise       ●
Travel       ●                        Coréenne         ●
Tech/IA      ●                        Australienne     ●
```

## Leçons apprises

### 1. Images cloud = problème de réalisme et yeux
⚠️ **PIÈGE MAJEUR** : Les générateurs cloud (Gemini Pro Image, DALL-E) produisent des défauts récurrents :
- Yeux asymétriques, pupilles irrégulières
- Visage qui change d'une image à l'autre (zéro cohérence faciale)
- Rendu "plastique", pas de texture de peau naturelle

→ **Solution : ComfyUI local** avec pipeline Flux Dev → ReActor (face consistency) → ADetailer (yeux/visage) → ESRGAN 4x (upscale).
→ Le prototypage cloud est utile pour valider les prompts, mais la production exige du local.
→ Voir `influenceuses-ia` SKILL.md section 1 pour le pipeline complet + connexion SSH paramiko.

### 2. Connexion SSH au serveur distant (TheHive)
Si pas de clé SSH configurée, utiliser paramiko dans un venv temporaire :
```bash
python3 -m venv /tmp/sshenv --without-pip
curl -sL https://bootstrap.pypa.io/get-pip.py | /tmp/sshenv/bin/python3
/tmp/sshenv/bin/pip install paramiko
```
Puis `SSHClient().connect(host, username, password)` — pas besoin de sshpass ni de clé.

### 3. Délégation parallèle = 4× plus rapide
Chaque agent reçoit le contexte complet (analyse de marché + structure attendue) et travaille en isolation.
→ Temps total : ~7 minutes pour 4 personas vs ~30 min en série.

### 2. Niches à ne pas négliger
- **Rousse** : 7% du marché = différenciant extrême. Combinaison rousse + yeux verts = 0.6% population.
- **Tech/IA** : niche quasi vide, audience masculine tech, crédibilité obligatoire (pas juste "poser avec un laptop").
- **Gaming/E-girl** : sous-exploitée en France, audience jeune et engagée.
- **Surf** : post-JO 2024, aucune influenceuse fitness française ne surfe sérieusement.

### 3. Images : prompts intégrés aux personas
Chaque fiche persona contient 3 prompts ComfyUI/Flux prêts à l'emploi :
- Prompt 1 : portrait signature
- Prompt 2 : mise en situation niche
- Prompt 3 : lifestyle

Les prompts peuvent être utilisés directement avec `image_generate` (backend OpenRouter Gemini Pro Image).

### 4. Structure de fiche éprouvée
Les 9 sections fonctionnent : identité → physique justifié → personnalité → backstory 4 arcs → lifestyle 24h → style → contenu → monétisation → prompts.

## Images générées (14/07/2026)

8 images secondaires générées via Gemini Pro Image (cloud — défauts yeux/visage attendus, prototypes seulement) :
```
~/lab/data/osint/influenceuses-mondiales/images/
├── sienna_fitness.png    — Pull-up, vue océan Biarritz
├── sienna_surf.png       — Sortie de l'eau, planche, border collie
├── valentina_glamour.png — Dressing haussmannien, bodysuit dentelle
├── valentina_bresil.png  — Ipanema, bikini, coco, sunset
├── yuna_gaming.png       — Setup gaming LED purple, chat borgne
├── yuna_paris.png        — Ruelle parisienne automne, sketchbook
├── maelys_travel.png     — Falaise Méditerranée, robe lin
├── maelys_boheme.png     — Terrasse terracotta, café sunrise
├── maeve_portrait.png    — Rousse geek, triple écran coding
├── maeve_coding.png      — Setup code, chat roux, RGB
└── maeve_conference.png  — Scène conférence tech, Transformer slide
```

→ Ces images servent de **référence visuelle** pour le pipeline ComfyUI local.\n→ Les prompts exacts sont dans les sections ## PROMPTS DE GÉNÉRATION de chaque fiche persona.\n\n## Pipeline local validé (14/07/2026)\n\n**ComfyUI sur TheHive GPU1 (RTX 3090) — pipeline fonctionnel :**\n- Flux Dev fp8 → 1024×1024 : ~29s/image\n- Upscale 4x UltraSharp → 4096×4096 : ~3s\n- Pipeline complet : ~33s/image, sortie PNG ~19 Mo\n- VRAM : 11.3 Go Flux + 4.7 Go CLIP = 16 Go total\n\n**Références :**\n- `references/comfyui-local-pipeline.md` — setup complet + pièges corrigés\n- Maeve Faure (rousse Tech/IA) : premier portrait généré en local → `maeve_local_gen.png` (1.2 Mo)\n- Maeve 4K : premier pipeline complet testé → `maeve_4k_pipeline.png` (19 Mo)\n\n**Problèmes rencontrés et résolus :**\n- PyTorch cu130 incompatible driver 550 → fixé avec `--index-url` cu124\n- Flux Dev téléchargement corrompu (17 Go .incomplete) → re-téléchargé avec `curl -L`\n- ReActor non chargé (manque onnxruntime) → installé, mais nécessite CUDA 13.0 pour GPU\n- Workflow `_comment` key → retiré du JSON