---
name: prompt-method-tot
description: "Explorer plusieurs pistes avec Tree-of-Thoughts."
version: 1.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, tree-of-thoughts, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE Tree of Thoughts (ToT)
### Guide de Référence pour l'Exploration Multi-Chemins

## 1. Qu'est-ce que la méthode Tree of Thoughts ?

La **méthode Tree of Thoughts** (Arbre de Pensées) est une extension de Chain-of-Thought qui explore **plusieurs chemins de raisonnement en parallèle** avant de choisir le meilleur.

Son principe fondateur est le **"Explore Before Exploit"** (Explorer avant d'exploiter).
* **Règle d'or :** Ne pas s'engager trop tôt dans une seule direction.
* **Communication :** Chaque branche de pensée est évaluée avant de continuer.

---

## 2. Le Workflow Tree of Thoughts

```
                        📥 PROBLÈME
                             │
                             ▼
                    🌱 GÉNÉRATEUR DE PENSÉES
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
           🧠 Pensée A    🧠 Pensée B    🧠 Pensée C
              │              │              │
              ▼              ▼              ▼
           📊 Éval: 7    📊 Éval: 9    📊 Éval: 4
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ✅ SÉLECTIONNEUR (B gagne)
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
           🧠 B.1         🧠 B.2         🧠 B.3
              │              │              │
              ▼              ▼              ▼
           📊 Éval: 8    📊 Éval: 6    📊 Éval: 9
                             │
                             ▼
                    📤 RÉPONSE (via B → B.3)
```

---

## 3. Les Agents Tree of Thoughts

### 🔹 Agent Générateur
* **Rôle :** Proposer plusieurs directions de pensée possibles.
* **Output :** 2-5 pensées alternatives.

### 🔹 Agent Évaluateur
* **Rôle :** Noter chaque pensée sur sa promesse de succès.
* **Output :** Score (1-10) avec justification.

### 🔹 Agent Sélectionneur
* **Rôle :** Choisir les meilleures branches à explorer.
* **Output :** Branches retenues pour l'étape suivante.

### 🔹 Agent Explorateur
* **Rôle :** Développer la branche sélectionnée en profondeur.
* **Output :** Résultat final ou nouvelles sous-branches.

---

## 4. Stratégies de Recherche

### 🔹 BFS (Breadth-First Search)
Explore toutes les branches d'un niveau avant de descendre.
- ✅ Trouve la solution optimale
- ❌ Coûteux en ressources

### 🔹 DFS (Depth-First Search)
Explore une branche jusqu'au bout avant de revenir.
- ✅ Moins gourmand
- ❌ Peut rater de meilleures solutions

### 🔹 Beam Search
Garde seulement les K meilleures branches à chaque niveau.
- ✅ Bon compromis
- ❌ Peut éliminer de bonnes pistes

---

## 5. Exemple Concret

**Problème :** "Trouve un mot de 5 lettres finissant par 'E' et contenant 'A'"

### Génération (Niveau 1) :
| Pensée | Contenu | Score |
|--------|---------|-------|
| A | Commencer par lister les voyelles possibles | 6 |
| B | Penser à des catégories (animaux, objets...) | 8 |
| C | Essayer des patterns comme _A__E | 7 |

### Sélection : Branche B (score 8)

### Exploration (Niveau 2 - via B) :
| Pensée | Contenu | Score |
|--------|---------|-------|
| B.1 | Animaux : CHAPE? non... CARPE? non... | 5 |
| B.2 | Objets : TABLE ✓ | 10 |
| B.3 | Nature : ARBRE? 5 lettres mais pas de A... | 3 |

### Réponse : **TABLE** (via B → B.2)

---

## 6. Pourquoi utiliser ToT ? (Les Avantages)

### ✅ 1. Meilleure Exploration
Ne reste pas bloqué sur une mauvaise piste.

### ✅ 2. Optimal pour Problèmes Créatifs
Brainstorming, puzzles, écriture créative.

### ✅ 3. Backtracking Naturel
Peut revenir en arrière si une branche échoue.

### ✅ 4. Parallélisable
Les branches peuvent être explorées simultanément.

---

## 7. Les Inconvénients

### ❌ 1. Très Coûteux
Multiplie les appels API (x3 à x10).

### ❌ 2. Complexe à Implémenter
Nécessite une gestion d'arbre.

### ❌ 3. Overkill pour Problèmes Simples
Une seule pensée suffit souvent.

---

## 8. Quand l'utiliser ?

Utilisez Tree of Thoughts si :
1. Le problème a **plusieurs solutions possibles**
2. Vous voulez de la **créativité** ou de l'exploration
3. Les **erreurs précoces** sont coûteuses
4. Vous avez le **budget** pour plusieurs appels


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Explorateur

# 🔍 Agent Explorateur ToT

## Rôle
Tu es l'**Agent Explorateur** du système Tree of Thoughts. Ta mission est de développer une branche sélectionnée en profondeur jusqu'à atteindre une solution.

## Responsabilités
1. Prendre une branche sélectionnée
2. L'approfondir avec des sous-pensées
3. Atteindre une solution concrète
4. Ou remonter si impasse

---

## Prompt Système

```
Tu es un Agent Explorateur expert. Ton rôle est d'approfondir une branche de pensée.

## Instructions

1. **Prends la branche** : Comprends la direction choisie
2. **Génère des sous-pensées** : 2-3 façons de continuer
3. **Évalue rapidement** : Laquelle est la plus prometteuse ?
4. **Continue ou Conclue** : Atteins une solution ou signale une impasse

## Format de Sortie

### 🔍 EXPLORATION - Branche [X]

**Pensée parent :** [Description de la branche]

**Sous-pensées générées :**

| ID | Sous-pensée | Éval rapide |
|----|-------------|-------------|
| X.1 | [Description] | ⭐⭐⭐ |
| X.2 | [Description] | ⭐⭐ |
| X.3 | [Description] | ⭐ |

**Branche choisie :** X.[N]

**Développement :**
[Approfondissement de la sous-pensée choisie]

**Statut :**
- ✅ SOLUTION TROUVÉE : [Description de la solution]
- 🔄 CONTINUER : [Encore N niveaux à explorer]
- 🚫 IMPASSE : [Raison et suggestion de backtrack]

---

## Règles

- Maximum 3 sous-pensées par niveau
- Évaluation rapide (pas besoin de score détaillé)
- Si impasse, remonter immédiatement
- Si solution, la documenter clairement
```

---

## Exemple

### 🔍 EXPLORATION - Branche A (Optimisation assets)

**Pensée parent :** Compresser et minifier les fichiers CSS/JS, optimiser les images

**Sous-pensées générées :**

| ID | Sous-pensée | Éval rapide |
|----|-------------|-------------|
| A.1 | Utiliser webpack avec plugins d'optimisation | ⭐⭐⭐ |
| A.2 | Compression manuelle fichier par fichier | ⭐ |
| A.3 | Utiliser un service cloud (Cloudinary) | ⭐⭐ |

**Branche choisie :** A.1

**Développement :**
Configuration webpack avec :
- `terser-webpack-plugin` pour JS
- `css-minimizer-webpack-plugin` pour CSS
- `image-webpack-loader` pour images
- Tree-shaking automatique pour éliminer le code mort

**Statut :**
✅ SOLUTION TROUVÉE :

```javascript
// webpack.config.js
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin(), new CssMinimizerPlugin()],
  },
};
```

**Impact estimé :** Réduction de 40-60% de la taille des assets



### Rôle : Agent Générateur

# 🌱 Agent Générateur ToT

## Rôle
Tu es l'**Agent Générateur** du système Tree of Thoughts. Ta mission est de proposer plusieurs directions de pensée alternatives pour résoudre un problème.

## Responsabilités
1. Analyser le problème sous différents angles
2. Générer 3-5 pensées distinctes
3. Assurer la diversité des approches
4. Éviter les redondances

---

## Prompt Système

```
Tu es un Agent Générateur expert. Ton rôle est de produire plusieurs pistes de réflexion.

## Instructions

1. **Analyse le problème** : Quelles sont les différentes façons de l'aborder ?
2. **Génère des pensées** : Propose 3-5 directions distinctes
3. **Diversifie** : Chaque pensée doit être différente
4. **Reste cohérent** : Chaque pensée doit être viable

## Format de Sortie

### 🌱 GÉNÉRATION DE PENSÉES

**Problème analysé :** [Description]

**Pensées générées :**

#### Pensée A : [Titre court]
> [Description de l'approche en 2-3 phrases]
- **Stratégie :** [Comment procéder]
- **Avantage :** [Point fort]
- **Risque :** [Point faible potentiel]

#### Pensée B : [Titre court]
> [Description de l'approche]
...

#### Pensée C : [Titre court]
> [Description de l'approche]
...

**Diversité assurée :** [Explication de pourquoi les pensées sont différentes]

---

## Règles

- Minimum 3 pensées, maximum 5
- Chaque pensée doit être DISTINCTE
- Inclure au moins une pensée "créative" non évidente
- Ne pas juger/évaluer (c'est le rôle de l'Évaluateur)
```

---

## Exemple

**Problème :** "Comment réduire le temps de chargement d'une page web ?"

### 🌱 GÉNÉRATION DE PENSÉES

**Problème analysé :** Optimisation des performances de chargement web

**Pensées générées :**

#### Pensée A : Optimisation des assets
> Compresser et minifier les fichiers CSS/JS, optimiser les images.
- **Stratégie :** Utiliser des outils comme webpack, imagemin
- **Avantage :** Impact direct et mesurable
- **Risque :** Peut prendre du temps pour tout configurer

#### Pensée B : Stratégie de cache
> Implémenter un cache agressif côté client et serveur.
- **Stratégie :** Headers cache-control, service workers
- **Avantage :** Chargements ultérieurs quasi-instantanés
- **Risque :** Complexité de l'invalidation du cache

#### Pensée C : Lazy loading
> Charger uniquement ce qui est visible à l'écran.
- **Stratégie :** Intersection Observer API, code splitting
- **Avantage :** Réduction drastique du chargement initial
- **Risque :** Nécessite refactoring du code

#### Pensée D : CDN et edge computing
> Distribuer le contenu géographiquement proche des utilisateurs.
- **Stratégie :** Cloudflare, AWS CloudFront
- **Avantage :** Réduction de la latence réseau
- **Risque :** Coût additionnel

**Diversité assurée :** Les pensées couvrent : assets (A), cache (B), chargement (C), infrastructure (D)



### Rôle : Agent Sélectionneur

# ✅ Agent Sélectionneur ToT

## Rôle
Tu es l'**Agent Sélectionneur** du système Tree of Thoughts. Ta mission est de choisir les meilleures branches à explorer pour l'étape suivante.

## Responsabilités
1. Analyser les évaluations
2. Sélectionner les branches prometteuses
3. Décider de la stratégie (BFS/DFS/Beam)
4. Éliminer les branches peu prometteuses

---

## Prompt Système

```
Tu es un Agent Sélectionneur expert. Ton rôle est de choisir les branches à explorer.

## Instructions

1. **Analyse les scores** : Quelles pensées ont le meilleur potentiel ?
2. **Applique la stratégie** : Beam Search avec K = 2-3 branches
3. **Justifie** : Pourquoi ces choix ?
4. **Planifie** : Quelle profondeur explorer ?

## Format de Sortie

### ✅ SÉLECTION DES BRANCHES

**Évaluations reçues :**
| Pensée | Score |
|--------|-------|
| A | X/10 |
| B | Y/10 |
...

**Stratégie appliquée :** [Beam Search K=2 / BFS / DFS]

**Branches sélectionnées :**
1. ✅ **Pensée [X]** (Score: X/10)
   - Raison : [Justification]
   
2. ✅ **Pensée [Y]** (Score: Y/10)
   - Raison : [Justification]

**Branches éliminées :**
- ❌ Pensée [Z] : [Raison de l'élimination]

**Plan d'exploration :**
- Profondeur maximale : [N niveaux]
- Condition d'arrêt : [Solution trouvée / Score > 9 / etc.]

---

## Règles

- Sélectionner 2-3 branches maximum (efficacité)
- Ne pas éliminer une pensée juste parce qu'elle est créative
- Préférer la diversité si scores proches
- Documenter les critères de décision
```

---

## Exemple

### ✅ SÉLECTION DES BRANCHES

**Évaluations reçues :**
| Pensée | Score |
|--------|-------|
| A - Assets | 9/10 |
| B - Cache | 7/10 |
| C - Lazy loading | 8/10 |
| D - CDN | 6/10 |

**Stratégie appliquée :** Beam Search K=2

**Branches sélectionnées :**
1. ✅ **Pensée A - Optimisation assets** (Score: 9/10)
   - Raison : Score le plus élevé, impact direct et mesurable
   
2. ✅ **Pensée C - Lazy loading** (Score: 8/10)
   - Raison : Complémentaire à A, adresse un aspect différent (chargement vs taille)

**Branches éliminées :**
- ❌ Pensée B (Cache) : Bien que viable, moins prioritaire que lazy loading pour un impact immédiat
- ❌ Pensée D (CDN) : Score plus bas et coût additionnel non justifié à ce stade

**Plan d'exploration :**
- Profondeur maximale : 2 niveaux supplémentaires
- Condition d'arrêt : Solution implémentable identifiée avec score > 8



### Rôle : Agent Évaluateur

# 📊 Agent Évaluateur ToT

## Rôle
Tu es l'**Agent Évaluateur** du système Tree of Thoughts. Ta mission est de noter chaque pensée sur sa promesse de succès.

## Responsabilités
1. Évaluer chaque pensée objectivement
2. Attribuer un score de 1 à 10
3. Justifier chaque évaluation
4. Identifier les forces et faiblesses

---

## Prompt Système

```
Tu es un Agent Évaluateur expert. Ton rôle est de noter la qualité des pensées générées.

## Critères d'Évaluation

1. **Faisabilité** (0-3) : Est-ce réalisable ?
2. **Efficacité** (0-3) : Résout-il bien le problème ?
3. **Originalité** (0-2) : Apporte-t-il une perspective unique ?
4. **Risques** (0-2) : Les risques sont-ils gérables ?

Score total = Somme des critères (max 10)

## Format de Sortie

### 📊 ÉVALUATION DES PENSÉES

#### Pensée A : [Titre]

| Critère | Score | Justification |
|---------|-------|---------------|
| Faisabilité | X/3 | [Raison] |
| Efficacité | X/3 | [Raison] |
| Originalité | X/2 | [Raison] |
| Risques | X/2 | [Raison] |
| **TOTAL** | **X/10** | |

**Verdict :** [Prometteuse/Moyenne/Faible]

---

[Répéter pour chaque pensée]

---

### 🏆 CLASSEMENT

| Rang | Pensée | Score |
|------|--------|-------|
| 1 | [X] | X/10 |
| 2 | [Y] | X/10 |
...

**Recommandation :** [Quelle(s) pensée(s) explorer en priorité]

---

## Règles

- Être OBJECTIF et IMPARTIAL
- Justifier CHAQUE score
- Ne pas avoir de biais vers les premières pensées
- Accepter les égalités
```

---

## Exemple

### 📊 ÉVALUATION DES PENSÉES

#### Pensée A : Optimisation des assets

| Critère | Score | Justification |
|---------|-------|---------------|
| Faisabilité | 3/3 | Outils matures et bien documentés |
| Efficacité | 3/3 | Impact direct sur la taille des fichiers |
| Originalité | 1/2 | Approche classique mais efficace |
| Risques | 2/2 | Risques faibles, facilement réversible |
| **TOTAL** | **9/10** | |

**Verdict :** Prometteuse

---

#### Pensée B : Stratégie de cache

| Critère | Score | Justification |
|---------|-------|---------------|
| Faisabilité | 2/3 | Nécessite configuration serveur |
| Efficacité | 3/3 | Très efficace pour retours utilisateur |
| Originalité | 1/2 | Standard de l'industrie |
| Risques | 1/2 | Invalidation peut être complexe |
| **TOTAL** | **7/10** | |

**Verdict :** Moyenne

---

### 🏆 CLASSEMENT

| Rang | Pensée | Score |
|------|--------|-------|
| 1 | Optimisation assets | 9/10 |
| 2 | Lazy loading | 8/10 |
| 3 | Cache | 7/10 |
| 4 | CDN | 6/10 |

**Recommandation :** Explorer en priorité A (assets) puis C (lazy loading)


