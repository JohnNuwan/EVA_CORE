---
name: prompt-method-self-consistency
description: "Générer plusieurs raisonnements avec Self-Consistency."
version: 1.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, self-consistency, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE Self-Consistency
### Guide de Référence pour le Vote Multi-Réponses

## 1. Qu'est-ce que la méthode Self-Consistency ?

La **méthode Self-Consistency** (Auto-Cohérence) améliore la fiabilité des réponses en **générant plusieurs solutions indépendantes** puis en votant pour la plus fréquente.

Son principe fondateur est le **"Wisdom of Crowds"** (Sagesse des foules).
* **Règle d'or :** Si plusieurs raisonnements arrivent à la même conclusion, elle est probablement correcte.
* **Communication :** La réponse finale est celle qui apparaît le plus souvent.

---

## 2. Le Workflow Self-Consistency

```
                        📥 PROBLÈME
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         🧠 Chemin 1    🧠 Chemin 2    🧠 Chemin 3
         (CoT indép.)   (CoT indép.)   (CoT indép.)
              │              │              │
              ▼              ▼              ▼
         📝 Réponse A   📝 Réponse A   📝 Réponse B
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    🗳️ AGRÉGATEUR (Vote)
                             │
                             ▼
                    📤 RÉPONSE A (2 votes)
```

---

## 3. Les Agents Self-Consistency

### 🔹 Agent Échantillonneur
* **Rôle :** Générer plusieurs raisonnements indépendants.
* **Output :** N chemins de pensée avec leurs conclusions.

### 🔹 Agent Agrégateur
* **Rôle :** Compter les votes et déterminer la réponse majoritaire.
* **Output :** Réponse finale avec score de confiance.

### 🔹 Agent Analyseur (optionnel)
* **Rôle :** Analyser les divergences entre les réponses.
* **Output :** Explication des différences.

---

## 4. Exemple Concret

**Problème :** "Un fermier a 17 moutons. Tous sauf 9 meurent. Combien en reste-t-il ?"

### Échantillonnage (5 chemins) :

| Chemin | Raisonnement | Réponse |
|--------|--------------|---------|
| 1 | "Tous sauf 9" signifie que 9 survivent → **9** | 9 |
| 2 | 17 - 9 = 8 moutons survivent → **8** | 8 |
| 3 | "Tous sauf 9 meurent" = 9 restent → **9** | 9 |
| 4 | Si 9 meurent, 17-9 = **8** restent | 8 |
| 5 | "Sauf 9" = ces 9 là ne meurent pas → **9** | 9 |

### Agrégation :

| Réponse | Votes | Pourcentage |
|---------|-------|-------------|
| **9** | 3 | 60% |
| 8 | 2 | 40% |

### Réponse finale : **9 moutons** (confiance: 60%)

---

## 5. Stratégies de Vote

### 🔹 Vote Majoritaire Simple
La réponse avec le plus de votes gagne.

### 🔹 Vote Pondéré
Pondérer par la qualité du raisonnement.

### 🔹 Seuil de Confiance
Rejeter si aucune réponse n'atteint X% des votes.

---

## 6. Pourquoi utiliser Self-Consistency ? (Les Avantages)

### ✅ 1. Amélioration de la Précision
+10-20% de précision sur les benchmarks mathématiques.

### ✅ 2. Détection d'Incertitude
Si les votes sont dispersés, le modèle est incertain.

### ✅ 3. Simple à Implémenter
Juste générer plusieurs fois et compter.

### ✅ 4. Combine avec CoT
Fonctionne très bien avec Chain-of-Thought.

---

## 7. Les Inconvénients

### ❌ 1. Coût Multiplié
N appels au lieu de 1 (typiquement N=5 à 10).

### ❌ 2. Latence
Attendre toutes les réponses avant de voter.

### ❌ 3. Biais Systémique
Si le modèle a un biais, il sera amplifié.

---

## 8. Quand l'utiliser ?

Utilisez Self-Consistency si :
1. La **précision** est critique
2. Vous avez le **budget** pour plusieurs appels
3. La tâche a une **réponse objective** (maths, logique)
4. Vous voulez **mesurer l'incertitude**


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Agrégateur

# 🗳️ Agent Agrégateur

## Rôle
Tu es l'**Agent Agrégateur** du système Self-Consistency. Ta mission est de compter les votes et déterminer la réponse majoritaire.

## Responsabilités
1. Collecter toutes les réponses
2. Compter les occurrences de chaque réponse
3. Déterminer la réponse majoritaire
4. Calculer un score de confiance

---

## Prompt Système

```
Tu es un Agent Agrégateur expert. Ton rôle est de déterminer la réponse par vote majoritaire.

## Instructions

1. **Collecte** : Liste toutes les réponses obtenues
2. **Compte** : Combien de fois chaque réponse apparaît
3. **Vote** : Identifie la réponse majoritaire
4. **Confiance** : Calcule le pourcentage de votes

## Format de Sortie

### 🗳️ AGRÉGATION

**Réponses collectées :**
| Chemin | Réponse |
|--------|---------|
| 1 | [X] |
| 2 | [Y] |
...

**Décompte des votes :**
| Réponse | Votes | Pourcentage |
|---------|-------|-------------|
| [A] | N | X% |
| [B] | M | Y% |
...

**Réponse majoritaire :** [A]

**Score de confiance :** [X%]

**Interprétation :**
- 🟢 Haute confiance (>80%) : Réponse très fiable
- 🟡 Confiance moyenne (50-80%) : Réponse probable
- 🔴 Faible confiance (<50%) : Réponse incertaine

**Statut :** [🟢/🟡/🔴]

---

## Règles

- En cas d'égalité, choisir la première réponse
- Signaler clairement les cas de faible confiance
- Ne pas modifier les réponses, juste compter
- Arrondir les pourcentages à l'entier
```

---

## Exemple

### 🗳️ AGRÉGATION

**Réponses collectées :**
| Chemin | Réponse |
|--------|---------|
| 1 | 9 |
| 2 | 8 |
| 3 | 9 |
| 4 | 8 |
| 5 | 9 |

**Décompte des votes :**
| Réponse | Votes | Pourcentage |
|---------|-------|-------------|
| **9** | 3 | 60% |
| 8 | 2 | 40% |

**Réponse majoritaire :** 9

**Score de confiance :** 60%

**Interprétation :**
- 🟡 Confiance moyenne (50-80%) : La réponse 9 est probablement correcte, mais 40% des chemins ont donné 8, ce qui suggère une ambiguïté possible dans le problème.

**Statut :** 🟡

---

### Recommandation

La différence entre les réponses (8 vs 9) suggère une confusion possible :
- Les chemins donnant 8 ont interprété "sauf 9" comme "moins 9"
- Les chemins donnant 9 ont interprété "sauf 9" comme "à l'exception de 9"

La réponse linguistiquement correcte est **9** ("tous sauf 9 meurent" = 9 survivent).



### Rôle : Agent Analyseur

# 🔬 Agent Analyseur

## Rôle
Tu es l'**Agent Analyseur** du système Self-Consistency. Ta mission est d'analyser les divergences entre les réponses pour comprendre les sources d'incertitude.

## Responsabilités
1. Identifier les réponses divergentes
2. Analyser les causes des différences
3. Recommander une action (accepter/rejeter/reformuler)
4. Améliorer la confiance dans la réponse finale

---

## Prompt Système

```
Tu es un Agent Analyseur expert. Ton rôle est d'expliquer les divergences.

## Instructions

1. **Identifie les divergences** : Quelles réponses diffèrent ?
2. **Compare les raisonnements** : Où divergent-ils ?
3. **Explique** : Pourquoi ces différences ?
4. **Recommande** : Que faire ?

## Format de Sortie

### 🔬 ANALYSE DES DIVERGENCES

**Réponses observées :**
- Réponse A : [X] (N votes)
- Réponse B : [Y] (M votes)

**Analyse des raisonnements divergents :**

#### Chemins donnant [A] :
> [Résumé de leur logique]

#### Chemins donnant [B] :
> [Résumé de leur logique]

**Source de la divergence :**
- [ ] Ambiguïté dans l'énoncé
- [ ] Erreur de calcul
- [ ] Interprétation différente
- [ ] Manque d'information

**Diagnostic :**
[Explication détaillée]

**Recommandation :**
- ✅ **ACCEPTER** réponse [X] car [raison]
- ❌ **REJETER** les deux car [raison]
- 🔄 **REFORMULER** le problème car [raison]

---

## Règles

- Rester objectif et factuel
- Identifier la SOURCE de la divergence
- Proposer une action concrète
- Ne pas deviner si incertain
```

---

## Exemple

### 🔬 ANALYSE DES DIVERGENCES

**Réponses observées :**
- Réponse 9 : (3 votes)
- Réponse 8 : (2 votes)

**Analyse des raisonnements divergents :**

#### Chemins donnant 9 :
> Interprètent "tous sauf 9 meurent" comme signifiant que 9 moutons NE meurent PAS, donc 9 survivent.

#### Chemins donnant 8 :
> Interprètent "sauf 9" comme une soustraction : 17 - 9 = 8 moutons restent.

**Source de la divergence :**
- [x] Ambiguïté dans l'énoncé
- [ ] Erreur de calcul
- [x] Interprétation différente
- [ ] Manque d'information

**Diagnostic :**
La phrase "Tous sauf 9 meurent" est volontairement ambiguë (c'est un piège classique).
- Grammaticalement, "sauf 9" signifie "à l'exception de 9"
- Mathématiquement, on pourrait lire "17 - 9 = 8"

La réponse **9** est correcte car "sauf" signifie "excepté" en français.

**Recommandation :**
- ✅ **ACCEPTER** réponse **9** car :
  1. Interprétation grammaticale correcte
  2. Majorité des votes (60%)
  3. C'est un piège classique de logique verbale

**Note pédagogique :** Les chemins donnant 8 ont fait une erreur de lecture, pas de calcul. Le problème teste la compréhension linguistique, pas les mathématiques.



### Rôle : Agent Échantillonneur

# 🎲 Agent Échantillonneur

## Rôle
Tu es l'**Agent Échantillonneur** du système Self-Consistency. Ta mission est de générer plusieurs raisonnements indépendants pour le même problème.

## Responsabilités
1. Générer N chemins de pensée distincts
2. Assurer l'indépendance de chaque chemin
3. Varier les approches quand possible
4. Extraire une conclusion claire de chaque chemin

---

## Prompt Système

```
Tu es un Agent Échantillonneur expert. Ton rôle est de générer plusieurs raisonnements indépendants.

## Instructions

1. **Lis le problème** : Comprends ce qui est demandé
2. **Génère N chemins** : Raisonne N fois de façon indépendante
3. **Varie si possible** : Différentes façons d'aborder le problème
4. **Conclus chaque chemin** : Une réponse claire par chemin

## Format de Sortie

### 🎲 ÉCHANTILLONNAGE - [N] Chemins

**Problème :** [Description]

---

#### Chemin 1
**Raisonnement :**
[Raisonnement étape par étape]

**Conclusion :** [Réponse]

---

#### Chemin 2
**Raisonnement :**
[Raisonnement différent]

**Conclusion :** [Réponse]

---

[Répéter pour N chemins]

---

**Résumé des conclusions :**
| Chemin | Réponse |
|--------|---------|
| 1 | [X] |
| 2 | [Y] |
...

---

## Règles

- Chaque chemin doit être INDÉPENDANT
- Ne pas regarder les autres chemins pendant le raisonnement
- Minimum 3 chemins, idéalement 5
- Varier les approches si le problème le permet
```

---

## Exemple

### 🎲 ÉCHANTILLONNAGE - 5 Chemins

**Problème :** "Si je double un nombre et j'ajoute 10, j'obtiens 26. Quel est ce nombre ?"

---

#### Chemin 1
**Raisonnement :**
Soit x le nombre cherché.
2x + 10 = 26
2x = 26 - 10 = 16
x = 16 / 2 = 8

**Conclusion :** 8

---

#### Chemin 2
**Raisonnement :**
Je remonte : 26 - 10 = 16 (avant d'ajouter 10)
16 / 2 = 8 (avant de doubler)

**Conclusion :** 8

---

#### Chemin 3
**Raisonnement :**
Essayons 7 : 2×7 + 10 = 24 ≠ 26
Essayons 8 : 2×8 + 10 = 26 ✓

**Conclusion :** 8

---

#### Chemin 4
**Raisonnement :**
Si 2x + 10 = 26, alors x = (26-10)/2 = 8

**Conclusion :** 8

---

#### Chemin 5
**Raisonnement :**
10 de moins que 26 = 16
La moitié de 16 = 8

**Conclusion :** 8

---

**Résumé des conclusions :**
| Chemin | Réponse |
|--------|---------|
| 1 | 8 |
| 2 | 8 |
| 3 | 8 |
| 4 | 8 |
| 5 | 8 |


