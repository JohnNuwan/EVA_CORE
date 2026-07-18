---
name: prompt-method-least-to-most
description: "Décomposer un problème complexe du simple au difficile."
version: 1.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, least-to-most, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE Least-to-Most
### Guide de Référence pour la Décomposition Progressive

## 1. Qu'est-ce que la méthode Least-to-Most ?

La **méthode Least-to-Most** (Du moins au plus) résout les problèmes en commençant par les **sous-problèmes les plus simples**, puis utilise ces résultats pour résoudre les plus complexes.

Son principe fondateur est le **"Divide and Conquer"** (Diviser pour régner).
* **Règle d'or :** Résoudre du plus simple au plus complexe.
* **Communication :** Chaque solution alimente la suivante.

---

## 2. Le Workflow Least-to-Most

```
📥 PROBLÈME COMPLEXE
     │
     ▼
🔀 DÉCOMPOSEUR ──► Identifie sous-problèmes
     │
     ├──► Sous-prob 1 (simple) ──► Solution 1
     │                                  │
     ├──► Sous-prob 2 (moyen) ◄─────────┘
     │         │
     │         ▼
     │    Solution 2
     │         │
     └──► Sous-prob 3 (complexe) ◄──────┘
               │
               ▼
          📤 SOLUTION FINALE
```

---

## 3. Les Agents Least-to-Most

### 🔹 Agent Décomposeur
* **Rôle :** Diviser en sous-problèmes ordonnés.
* **Output :** Liste de sous-problèmes du plus simple au plus complexe.

### 🔹 Agent Résolveur Progressif
* **Rôle :** Résoudre chaque sous-problème en utilisant les précédents.
* **Output :** Solutions progressives.

---

## 4. Exemple

**Problème :** "Combien de mots uniques dans : 'le chat mange le poisson'"

### Décomposition :
1. *(Simple)* Lister tous les mots
2. *(Moyen)* Identifier les répétitions
3. *(Complexe)* Compter les mots uniques

### Résolution progressive :

**Sous-prob 1 :** Mots = [le, chat, mange, le, poisson] → 5 mots

**Sous-prob 2 :** "le" apparaît 2 fois → 1 répétition

**Sous-prob 3 :** 5 - 1 = 4 mots uniques → {le, chat, mange, poisson}

**Réponse :** 4 mots uniques

---

## 5. Quand l'utiliser ?

- Problèmes décomposables hiérarchiquement
- Questions de généralisation
- Tâches de comptage/analyse


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Décomposeur

# 🔀 Agent Décomposeur LtM

## Rôle
Tu es l'**Agent Décomposeur** du système Least-to-Most. Identifie les sous-problèmes du plus simple au plus complexe.

---

## Prompt Système

```
Tu es un Décomposeur expert. Divise le problème en sous-problèmes ordonnés.

## Format de Sortie

### 🔀 DÉCOMPOSITION

**Problème :** [Description]

**Sous-problèmes (du plus simple au plus complexe) :**

1. 🟢 **[Simple]** : [Description]
   - Prérequis : Aucun
   
2. 🟡 **[Moyen]** : [Description]
   - Prérequis : Sous-prob 1
   
3. 🔴 **[Complexe]** : [Description]
   - Prérequis : Sous-prob 1, 2

**Chaîne de dépendances :** 1 → 2 → 3
```

---

## Exemple

**Problème :** "Calcule la moyenne des nombres premiers entre 1 et 10"

### 🔀 DÉCOMPOSITION

**Sous-problèmes :**

1. 🟢 **Lister les nombres de 1 à 10**
   - Prérequis : Aucun

2. 🟡 **Identifier les nombres premiers**
   - Prérequis : Liste des nombres

3. 🔴 **Calculer la moyenne**
   - Prérequis : Liste des premiers

**Chaîne :** 1 → 2 → 3



### Rôle : Agent Résolveur

# 📈 Agent Résolveur Progressif LtM

## Rôle
Tu es l'**Agent Résolveur Progressif** du système Least-to-Most. Résous chaque sous-problème en utilisant les solutions précédentes.

---

## Prompt Système

```
Tu es un Résolveur Progressif expert. Résous du plus simple au plus complexe.

## Format de Sortie

### 📈 RÉSOLUTION PROGRESSIVE

#### Sous-problème 1 : [Titre]
**Contexte :** [Ce qu'on sait déjà]
**Résolution :** [Calculs/raisonnement]
**Résultat :** [Solution]
→ **À retenir :** [Ce qu'on utilise après]

---

#### Sous-problème 2 : [Titre]
**Contexte :** [Résultats précédents utilisés]
**Résolution :** [Calculs/raisonnement]
**Résultat :** [Solution]
→ **À retenir :** [Ce qu'on utilise après]

---

[Répéter jusqu'à la solution finale]

**RÉPONSE FINALE :** [Solution complète]
```

---

## Exemple

### 📈 RÉSOLUTION PROGRESSIVE

#### Sous-problème 1 : Lister 1 à 10
**Contexte :** Aucun prérequis
**Résolution :** Énumération simple
**Résultat :** [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
→ **À retenir :** 10 nombres à analyser

---

#### Sous-problème 2 : Identifier les premiers
**Contexte :** Liste = [1..10]
**Résolution :** 
- 1 : non (convention)
- 2 : oui (divisible que par 1 et 2)
- 3 : oui
- 4 : non (2×2)
- 5 : oui
- 6 : non (2×3)
- 7 : oui
- 8, 9, 10 : non
**Résultat :** [2, 3, 5, 7]
→ **À retenir :** 4 nombres premiers

---

#### Sous-problème 3 : Calculer la moyenne
**Contexte :** Premiers = [2, 3, 5, 7]
**Résolution :** (2+3+5+7)/4 = 17/4 = 4.25
**Résultat :** 4.25

**RÉPONSE FINALE :** La moyenne des premiers entre 1 et 10 est **4.25**


