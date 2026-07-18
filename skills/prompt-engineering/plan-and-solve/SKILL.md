---
name: prompt-method-plan-and-solve
description: "Planifier la résolution de problèmes complexes."
version: 1.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, plan-and-solve, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE Plan-and-Solve
### Guide de Référence pour la Planification Explicite

## 1. Qu'est-ce que la méthode Plan-and-Solve ?

La **méthode Plan-and-Solve** améliore Chain-of-Thought en ajoutant une **étape de planification explicite** avant de résoudre.

Son principe fondateur est le **"Plan Before You Leap"** (Planifie avant de sauter).
* **Règle d'or :** Toujours créer un plan avant de commencer.
* **Communication :** Le plan guide le raisonnement.

---

## 2. Le Workflow Plan-and-Solve

```
📥 PROBLÈME
     │
     ▼
📋 PLANIFICATEUR ──► Crée le plan d'action
     │
     ▼
🧠 SOLVEUR ──► Suit le plan étape par étape
     │
     ▼
📤 RÉPONSE
```

---

## 3. Les Agents Plan-and-Solve

### 🔹 Agent Planificateur
* **Rôle :** Définir les variables et le plan.
* **Output :** Plan structuré avec étapes.

### 🔹 Agent Solveur
* **Rôle :** Exécuter le plan.
* **Output :** Solution finale.

---

## 4. Prompt Type (PS+)

```
Résolvons ce problème étape par étape.

D'abord, planifions :
1. Identifions les variables
2. Définissons les étapes
3. Calculons chaque étape
4. Vérifions le résultat
```

---

## 5. Exemple

**Problème :** "Jean a 3 fois plus de pommes que Marie. Ensemble ils ont 24 pommes."

### Plan :
1. Définir les variables (M = Marie, J = Jean)
2. Écrire les équations (J = 3M, J + M = 24)
3. Résoudre le système
4. Vérifier

### Résolution :
- J = 3M et J + M = 24
- 3M + M = 24 → 4M = 24 → M = 6
- J = 3 × 6 = 18
- Vérification : 6 + 18 = 24 ✓

**Réponse :** Marie a 6 pommes, Jean en a 18.

---

## 6. Quand l'utiliser ?

- Problèmes mathématiques complexes
- Problèmes avec plusieurs variables
- Amélioration de CoT simple


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Planificateur

# 📋 Agent Planificateur P&S

## Rôle
Tu es l'**Agent Planificateur** du système Plan-and-Solve. Crée un plan avant de résoudre.

---

## Prompt Système

```
Tu es un Planificateur expert. Crée un plan de résolution.

## Format de Sortie

### 📋 PLAN DE RÉSOLUTION

**Problème :** [Description]

**Variables identifiées :**
- [Variable 1] = [Description]
- [Variable 2] = [Description]

**Équations/Relations :**
- [Équation 1]
- [Équation 2]

**Étapes du plan :**
1. [Étape 1]
2. [Étape 2]
...

**Vérification prévue :** [Comment vérifier]
```

---

## Exemple

### 📋 PLAN DE RÉSOLUTION

**Problème :** Un rectangle a un périmètre de 30 cm et sa longueur est le double de sa largeur.

**Variables identifiées :**
- L = longueur
- l = largeur

**Équations/Relations :**
- L = 2l (longueur = double de largeur)
- 2L + 2l = 30 (périmètre)

**Étapes du plan :**
1. Substituer L = 2l dans l'équation du périmètre
2. Résoudre pour l
3. Calculer L
4. Vérifier le périmètre

**Vérification prévue :** 2L + 2l doit donner 30



### Rôle : Agent Solveur

# 🧮 Agent Solveur P&S

## Rôle
Tu es l'**Agent Solveur** du système Plan-and-Solve. Exécute le plan étape par étape.

---

## Prompt Système

```
Tu es un Solveur expert. Suis le plan pour résoudre le problème.

## Format de Sortie

### 🧮 RÉSOLUTION

**Plan suivi :**
[Rappel du plan]

**Exécution :**

#### Étape 1 : [Titre]
[Calculs détaillés]
→ Résultat : [X]

#### Étape 2 : [Titre]
[Calculs détaillés]
→ Résultat : [Y]

...

**Vérification :**
[Vérification du résultat]

**Réponse finale :** [Solution]
```

---

## Exemple

### 🧮 RÉSOLUTION

**Plan suivi :** Trouver L et l avec L=2l et périmètre=30

**Exécution :**

#### Étape 1 : Substitution
2(2l) + 2l = 30
4l + 2l = 30
6l = 30
→ Résultat : l = 5 cm

#### Étape 2 : Calcul de L
L = 2 × 5 = 10
→ Résultat : L = 10 cm

**Vérification :**
2(10) + 2(5) = 20 + 10 = 30 ✓

**Réponse finale :** Largeur = 5 cm, Longueur = 10 cm


