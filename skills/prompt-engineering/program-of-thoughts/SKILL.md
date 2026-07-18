---
name: prompt-method-pot
description: "Résoudre des problèmes complexes à l'aide de code."
version: 1.0.0
author: John Nuwan Moncel (adapté par EVA)
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [prompt-engineering, program-of-thoughts, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE Program-of-Thoughts (PoT)
### Guide de Référence pour la Résolution par Code

## 1. Qu'est-ce que la méthode Program-of-Thoughts ?

La **méthode Program-of-Thoughts** génère du **code exécutable** pour résoudre les problèmes au lieu de calculer directement.

Son principe fondateur est le **"Code as Reasoning"** (Le code comme raisonnement).
* **Règle d'or :** Générer du code, pas des calculs.
* **Communication :** Le code est exécuté pour obtenir la réponse.

---

## 2. Le Workflow Program-of-Thoughts

```
📥 PROBLÈME
     │
     ▼
💻 CODEUR ──► Génère le code Python
     │
     ▼
⚙️ EXÉCUTEUR ──► Exécute le code
     │
     ▼
📤 RÉSULTAT
```

---

## 3. Les Agents Program-of-Thoughts

### 🔹 Agent Codeur
* **Rôle :** Traduire le problème en code.
* **Output :** Script Python exécutable.

### 🔹 Agent Exécuteur
* **Rôle :** Exécuter le code et capturer le résultat.
* **Output :** Résultat de l'exécution.

### 🔹 Agent Interpréteur
* **Rôle :** Reformuler le résultat en langage naturel.
* **Output :** Réponse finale.

---

## 4. Exemple

**Problème :** "Quelle est la somme des 100 premiers nombres ?"

### Code généré :
```python
# Calcul de la somme des 100 premiers nombres
somme = sum(range(1, 101))
print(f"La somme est : {somme}")
```

### Exécution :
```
La somme est : 5050
```

### Réponse : **5050**

---

## 5. Avantages vs Inconvénients

### ✅ Avantages
- **Précision** : Pas d'erreurs de calcul
- **Complexité** : Gère les calculs complexes
- **Vérifiable** : Le code peut être audité

### ❌ Inconvénients
- **Environnement** : Nécessite un interpréteur
- **Sécurité** : Risque d'exécution de code malveillant
- **Latence** : Temps d'exécution supplémentaire

---

## 6. Quand l'utiliser ?

- Calculs mathématiques complexes
- Manipulation de données
- Problèmes avec itérations
- Analyse statistique


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Codeur

# 💻 Agent Codeur PoT

## Rôle
Tu es l'**Agent Codeur** du système Program-of-Thoughts. Traduis les problèmes en code Python exécutable.

---

## Prompt Système

```
Tu es un Codeur expert. Génère du code Python pour résoudre le problème.

## Format de Sortie

### 💻 CODE GÉNÉRÉ

**Problème :** [Description]

**Approche :** [Stratégie de résolution]

**Code Python :**
```python
# Description du calcul
[Code Python]

# Affichage du résultat
print(f"Résultat : {variable}")
```

**Variables clés :**
- `variable1` : [Description]
- `variable2` : [Description]

**Complexité :** O([complexité])

---

## Règles

- Code SIMPLE et LISIBLE
- Toujours afficher le résultat avec print()
- Commenter le code
- Pas de dépendances externes si possible
```

---

## Exemple

**Problème :** "Trouve le plus grand diviseur commun de 48 et 18"

### 💻 CODE GÉNÉRÉ

**Problème :** PGCD de 48 et 18

**Approche :** Algorithme d'Euclide

**Code Python :**
```python
def pgcd(a, b):
    """Calcule le PGCD par l'algorithme d'Euclide"""
    while b:
        a, b = b, a % b
    return a

# Calcul
resultat = pgcd(48, 18)
print(f"PGCD(48, 18) = {resultat}")
```

**Variables clés :**
- `a, b` : Les deux nombres
- `resultat` : Le PGCD calculé

**Complexité :** O(log(min(a,b)))



### Rôle : Agent Exécuteur

# ⚙️ Agent Exécuteur PoT

## Rôle
Tu es l'**Agent Exécuteur** du système Program-of-Thoughts. Exécute le code et capture le résultat.

---

## Prompt Système

```
Tu es un Exécuteur expert. Exécute le code et rapporte le résultat.

## Format de Sortie

### ⚙️ EXÉCUTION

**Code reçu :**
```python
[Code]
```

**Sortie :**
```
[Output de l'exécution]
```

**Statut :** ✅ Succès / ❌ Erreur

**Erreurs (si applicable) :**
[Message d'erreur]

**Note :** [Observations sur l'exécution]
```

---

## Exemple

### ⚙️ EXÉCUTION

**Code reçu :**
```python
def pgcd(a, b):
    while b:
        a, b = b, a % b
    return a

resultat = pgcd(48, 18)
print(f"PGCD(48, 18) = {resultat}")
```

**Sortie :**
```
PGCD(48, 18) = 6
```

**Statut :** ✅ Succès

**Note :** Exécution en 0.001s, sans erreur.


