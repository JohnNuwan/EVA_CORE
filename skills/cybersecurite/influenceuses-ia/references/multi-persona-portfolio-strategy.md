# Stratégie Multi-Personas — Portfolio d'Influenceuses IA

## Pourquoi plusieurs personas ?

Un seul persona = un seul public. Un PORTFOLIO de 5 personas = couverture de marché maximale :
- Chaque persona cible une niche différente (Fashion, Fitness, Glamour, Gaming, Travel)
- Chaque persona a un physique distinct justifié par les données
- Chaque persona a une origine ethnique et un backstory uniques
- Les personas ne se cannibalisent PAS entre eux

## Les 5 archétypes data-driven (juillet 2026)

Basés sur l'analyse des 30+ influenceuses les plus performantes (Instagram, TikTok, OnlyFans, MYM).

| # | Archétype | Niche | Physique signature | Origine | Hook émotionnel |
|---|-----------|-------|-------------------|---------|-----------------|
| 1 | Muse Moderne | Fashion/Lifestyle | Brune, sablier athlétique, 1,67m, 34C | Franco-italo-marocaine | Rupture → reconstruction |
| 2 | Athlète Inspirante | Fitness/Wellness | Blonde yeux bleus, surf, 1,68m, 6-pack | Franco-américaine | Blessure → comeback |
| 3 | It-Girl Luxe | Glamour/Mode | Brune pulpeuse, 1,62m, 34D | Franco-brésilienne | Rupture toxique → indépendance |
| 4 | Hackeuse Artistique | Gaming/E-girl | Mèches roses, yeux verts, 1,65m, mince | Franco-coréenne | Burnout → communauté |
| 5 | Voyageuse Libre | Travel/Bohème | Blonde ondulée, 1,70m, élancée | Franco-australienne | Mère malade → cause caritative |

## Workflow de création multi-personas

### Étape 1 : Analyse de marché (Phase 0 du skill)
→ Fichier : `01_analyse_marche.md`
→ Identifier les 5 niches les plus porteuses
→ Extraire les patterns physiques par niche

### Étape 2 : Création parallèle avec delegation
Utiliser `delegate_task` en mode batch pour créer tous les personas EN PARALLÈLE.
Chaque subagent reçoit :
- Le contexte de l'analyse de marché
- Les specs précises du persona (niche, physique, origine, âge)
- La structure complète à suivre (9 sections)
- La langue (français)

```python
# Pattern de delegation batch
delegate_task(tasks=[
    {"goal": "Créer persona FITNESS...", "context": "Analyse marché + specs...", "role": "leaf"},
    {"goal": "Créer persona GLAMOUR...", "context": "Analyse marché + specs...", "role": "leaf"},
    {"goal": "Créer persona E-GIRL...", "context": "Analyse marché + specs...", "role": "leaf"},
    {"goal": "Créer persona TRAVEL...", "context": "Analyse marché + specs...", "role": "leaf"},
])
# ~6 minutes pour 4 personas en parallèle
```

### Étape 3 : Vérification et consolidation
- Vérifier que chaque fichier fait 300+ lignes
- Corriger les conflits de nommage (les subagents peuvent choisir le même préfixe)
- Renommer si nécessaire : `mv 03_persona_X.md 04_persona_X.md`

### Pièges
- **Conflit de numérotation** : les subagents ne se coordonnent pas sur les préfixes de fichier → toujours vérifier les noms et renommer si conflit
- **Qualité variable** : certains subagents produisent 400 lignes, d'autres 800 → donner des consignes de longueur explicites (300+ minimum)
- **Langue** : spécifier EXPLICITEMENT "Écris TOUT en français" dans le contexte, sinon les subagents peuvent dériver vers l'anglais

## Structure de fichier standard

Chaque persona suit exactement les 9 sections :
1. Fiche d'identité (nom, pseudo, âge, origines, villes, langues, animal)
2. Caractéristiques physiques + tableau "Pourquoi ce physique ?"
3. Personnalité & archétype (5 piliers, voix/ton)
4. Backstory (4 arcs : enfance, émergence, crise, futur)
5. Lifestyle 24h (matin, après-midi, soir)
6. Style & Aesthetic (palette, garde-robe, beauté)
7. Stratégie de contenu (piliers, calendrier, plateformes)
8. Monétisation (revenus projetés, positionnement, marques cibles)
9. Prompts de génération (3 prompts ComfyUI/Flux)

## Résultats attendus

```
rapports/
├── 01_analyse_marche.md           ← Fondation data-driven
├── 02_persona_[nom1].md           ← 400-800 lignes
├── 03_persona_[nom2].md           ← 400-800 lignes
├── 04_persona_[nom3].md           ← 400-800 lignes
├── 05_persona_[nom4].md           ← 400-800 lignes
└── 06_persona_[nom5].md           ← 400-800 lignes

Total typique : 2500-4000 lignes pour 5 personas
```

## Exemple concret

Session du 14 juillet 2026 — 5 personas créés en ~12 minutes :
- 4 personas délégués en parallèle (6 min) + 1 persona existant (Lyra Amari)
- Total : 3112 lignes, 5 niches, 5 origines ethniques, 5 physiques distincts
- Fichiers dans `~/lab/data/osint/influenceuses-mondiales/rapports/`