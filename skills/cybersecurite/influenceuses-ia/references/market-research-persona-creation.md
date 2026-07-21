# Market Research & Persona Creation Methodology

## Objectif

Avant de générer la moindre image, il faut une **phase de recherche stratégique** pour
concevoir un persona data-driven — pas un personnage "au feeling".

---

## Workflow en 4 phases

### Phase 1 — Collecte de données

```
Objectif : identifier les 20-30 influenceuses réelles les plus performantes
Sources  : Wikipedia (most-followed Instagram), SocialPilot, Ranker,
           InfluencerMarketingHub, SocialBlade
Méthode  : Requêtes parallèles (web_search × 4-5) pour couvrir
           Instagram, TikTok, YouTube, et les niches cibles
```

**Requêtes types :**
- `"most followed female influencers Instagram 2025 2026 top 50"`
- `"top female TikTok influencers most followed 2025 2026"`
- `"most popular female influencers physical appearance trends hair color body type"`
- `"[nom influenceuse] height weight body measurements"`
- `"top influencer niches 2025 2026 most profitable"`

**Pièges :**
- DuckDuckGo backend (par défaut) ne supporte pas `web_extract` — contourner avec `browser_navigate` ou `execute_code` + `urllib`
- Les sites de stats people (healthyceleb, celebritytall) sont les plus fiables pour les mensurations
- Ranker permet d'avoir le "pouls du public" (votes), pas juste les chiffres bruts

---

### Phase 2 — Analyse statistique

Extraire et compiler dans un tableau pour 30+ influenceuses :

| Attribut | Catégories | Ce qu'on cherche |
|----------|-----------|------------------|
| **Cheveux** | Brun, Blond, Roux, Autre | Couleur dominante, tendances |
| **Yeux** | Marron, Bleu, Vert | Cross-cultural appeal |
| **Silhouette** | Sablier, Athlétique, Mince, Pulpeuse | Forme dominante + tendance |
| **Poitrine** | A-B, B-C, D+, Augmentée | Sweet spot naturel vs artificiel |
| **Taille** | Plage min-max, médiane, moyenne | Hauteur optimale |
| **Origine** | Caucasienne, Latina, Afro, Asiatique | Mix gagnant |
| **Âge** | Plage, médiane | Peak influencer age |
| **Niche** | Fashion, Fitness, Travel, Beauty... | Niches les plus rentables |

**Format de sortie :** tableaux Markdown avec pourcentages + "barres ASCII" pour visualiser
les proportions (ex: `████████ Brun : 60%`).

---

### Phase 3 — Extraction des patterns de succès

Au-delà du physique, analyser CE QUI FAIT LE SUCCÈS :

1. **Authenticité perçue** — l'influenceuse doit sembler "vraie" (coulisses, moments bruts)
2. **Consistance visuelle** — feed cohérent, palette de couleurs
3. **Narratif personnel** — une "vie" avec des hauts et des bas
4. **Multi-plateforme** — Instagram (vitrine) + TikTok (viralité) + Fanvue (monétisation)
5. **Luxe accessible** — aspirationnel mais pas inatteignable
6. **Corps crédible** — pas de chirurgie visible excessive
7. **Fréquence** — minimum 1 post/jour
8. **Engagement** — répondre aux commentaires, créer une communauté

---

### Phase 4 — Design du persona

Chaque attribut physique et narratif doit être **justifié par les données**, pas par l'intuition.

**Structure du persona :**

```
FICHE D'IDENTITÉ
├── Nom complet (mémorisable, international, 2 mots max)
├── Pseudo (cohérent multi-plateforme)
├── Âge (médiane du top 30 pour la niche visée)
├── Origines (mix ethnique = exotisme accessible)
├── Villes (base + secondaire crédible)
└── Animal de compagnie (humanise, crée du contenu)

CARACTÉRISTIQUES PHYSIQUES
├── Tableau détaillé (cheveux, yeux, peau, taille, mensurations)
└── Tableau "Pourquoi ce physique ?" (chaque attribut justifié par une stat)

PERSONNALITÉ & ARCHÉTYPE
├── Archétype principal (nom + description)
├── 5 piliers de personnalité (l'Esthète, la Curieuse, la Sportive...)
└── Voix & Ton (style d'écriture, hashtags, émojis)

BACKSTORY
├── Arc 1 — Enfance et adolescence
├── Arc 2 — Émergence (comment elle a percé)
├── Arc 3 — Hook émotionnel actuel (rupture, échec, reconstruction)
└── Arc 4 — Futur (objectifs 6-12 mois)

LIFESTYLE — 24H type
├── Matin (réveil → déjeuner)
├── Après-midi (admin → shooting)
└── Soir (événements → coucher)

STYLE & AESTHETIC
├── Palette Instagram (couleurs + ambiance)
├── Garde-robe signature (basics + pièces fortes + ce qu'elle ne porte JAMAIS)
└── Beauté signature (maquillage, cheveux, skincare)

STRATÉGIE DE CONTENU
├── Piliers (4 colonnes avec % et fréquence)
└── Calendrier type (lundi → dimanche)

MONÉTISATION
├── Revenus projetés (tableau par source, Année 1)
└── Positionnement prix (nano → macro)

PROMPTS DE GÉNÉRATION
└── 3 prompts prêts pour ComfyUI/Flux (portrait, fitness, lifestyle)
```

---

## Contre-exemples (ce qu'il NE FAUT PAS faire)

- **Corps refait visible** → le marché 2026 punit le "fake look" (sauf niche assumée)
- **Nom trop long ou complexe** → Lil Miquela, Aitana Lopez, Emily Pellegrini = 2-3 mots max
- **Pas de backstory** → une influenceuse IA sans histoire = un PNG sur internet
- **Niches trop larges** → "lifestyle" tout court ne suffit plus, il faut une spécialité
- **Aucune vulnérabilité** → la perfection tue l'engagement. Il faut une faille assumée
- **Une seule plateforme** → le reach multi-canal est critique pour la monétisation

---

## Inspiration : AI influencers existantes

| Nom | Followers | Point fort | Leçon |
|-----|-----------|------------|-------|
| Lil Miquela | 2.5M | Narrative + musique | L'histoire > l'image |
| Aitana Lopez | 350K+ | Monétisation Fanvue | Le modèle fitness paie |
| Emily Pellegrini | 543K | Croissance rapide | Le glamour "tease" fonctionne |
| Shudu Gram | 240K | Photographie pro | La qualité visuelle est non-négociable |