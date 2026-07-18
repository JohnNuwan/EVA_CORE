# Session Example: Découverte Exhaustive des 7 Variantes JEPA

## Contexte

Session du 2 juillet 2026. L'utilisateur demande : « oui sur tout ce qui est JEPA ».
Aucune skill JEPA n'existe localement. Application du protocole Web-First.

## Étapes de la Recherche

### 1. Première approche (superficielle — corrigée)
- Navigation vers le blog Meta AI I-JEPA → découverte de I-JEPA uniquement
- L'utilisateur corrige : « peut etre car tu regarde pas tout les declinaison des JEPA ? »

### 2. Recherche exhaustive (correcte)
- Navigation vers `github.com/orgs/facebookresearch/repositories?q=jepa`
- **Résultat : 7 repos**, pas 2 comme supposé initialement :

| # | Repo | Stars | Description |
|---|---|---|---|
| 1 | `ijepa` | 3.5k | I-JEPA (Images, CVPR 2023) |
| 2 | `jepa` | 4k | V-JEPA (Vidéo, 2024) |
| 3 | `eb_jepa` | 729 | Energy-Based JEPA (Apache 2.0, janv 2026) |
| 4 | `jepa-wms` | 419 | World Models (robotique DROID/RoboCasa) |
| 5 | `jepa-intuitive-physics` | 262 | Physique intuitive émergente |
| 6 | `td_jepa` | 45 | Temporal Difference, RL zero-shot |
| 7 | `locate-3d` | 449 | 3D-JEPA, localisation objets 3D |

### 3. Techniques de contournement utilisées
- **Blocage Google** → navigué vers GitHub directement
- **Blocage arXiv (UTF-8)** → utilisé `execute_code` avec `urllib` pour les abstracts
- **Snapshot vide sur raw GitHub** → utilisé `browser_console` avec `document.querySelector('article')?.innerText`
- **Blog Meta tronqué** → `browser_console` avec `document.body.innerText.substring(0, 5000)`

## Leçons Apprises

1. **Toujours chercher l'organisation GitHub complète** : `github.com/orgs/<org>/repositories?q=<topic>` avant de conclure
2. **Ne jamais s'arrêter au premier résultat** : le repo principal (jepa, 4k stars) n'est que la partie émergée
3. **La licence change tout** : EB-JEPA (Apache 2.0) est le seul utilisable commercialement — information critique qu'on aurait manquée sans recherche exhaustive
4. **Le snapshot navigateur est peu fiable** : toujours avoir un fallback `browser_console` pour les pages statiques