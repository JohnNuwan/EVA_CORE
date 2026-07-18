---
name: prompt-method-cot
description: "Résoudre des problèmes complexes via Chain-of-Thought."
version: 1.0.0
author: John Nuwan Moncel (adapté par EVA)
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [prompt-engineering, chain-of-thought, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE Chain-of-Thought (CoT)
### Guide de Référence pour le Raisonnement Étape par Étape

## 1. Qu'est-ce que la méthode Chain-of-Thought ?

La **méthode Chain-of-Thought** (Chaîne de Pensée) est une technique de prompt engineering qui force le LLM à **décomposer son raisonnement** en étapes explicites avant de donner une réponse finale.

Son principe fondateur est le **"Show Your Work"** (Montre ton travail).
* **Règle d'or :** Ne jamais sauter directement à la conclusion.
* **Communication :** Chaque étape de raisonnement est visible et vérifiable.

---

## 2. Les Variantes de Chain-of-Thought

### 🔹 Zero-Shot CoT
Ajouter simplement "Réfléchis étape par étape" au prompt.

```
Question: Si j'ai 3 pommes et j'en achète 5, puis j'en donne 2, combien m'en reste-t-il ?

Prompt: Réfléchis étape par étape avant de répondre.
```

### 🔹 Few-Shot CoT
Fournir des exemples de raisonnement détaillé.

```
Exemple 1:
Q: 2 + 3 × 4 = ?
Raisonnement: D'abord la multiplication: 3 × 4 = 12. Puis l'addition: 2 + 12 = 14.
R: 14

Maintenant résous: 5 + 2 × 3 = ?
```

### 🔹 Auto-CoT (Automatique)
Le LLM génère ses propres exemples de raisonnement.

---

## 3. Le Workflow CoT avec Agents

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  📥 PROBLÈME                                             │
│       │                                                  │
│       ▼                                                  │
│  🔀 DÉCOMPOSEUR ──► Découpe en sous-problèmes           │
│       │                                                  │
│       ▼                                                  │
│  🧠 RAISONNEUR ──► Résout chaque étape                  │
│       │                                                  │
│       ▼                                                  │
│  ✅ VÉRIFICATEUR ──► Valide chaque étape                │
│       │                                                  │
│       ▼                                                  │
│  📝 SYNTHÉTISEUR ──► Compile la réponse finale          │
│       │                                                  │
│       ▼                                                  │
│  📤 RÉPONSE                                              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 🔹 Agent Décomposeur
* **Rôle :** Analyser le problème et le découper en sous-étapes.
* **Output :** Liste ordonnée des étapes à suivre.

### 🔹 Agent Raisonneur
* **Rôle :** Raisonner explicitement sur chaque étape.
* **Output :** Solution intermédiaire avec justification.

### 🔹 Agent Vérificateur
* **Rôle :** Valider la cohérence de chaque étape.
* **Output :** Confirmation ou correction.

### 🔹 Agent Synthétiseur
* **Rôle :** Assembler les résultats en réponse finale.
* **Output :** Réponse complète et structurée.

---

## 4. Exemple Concret

**Problème :** "Marie a 15€. Elle achète 3 croissants à 1,20€ et 2 cafés à 2,50€. Combien lui reste-t-il ?"

### Décomposition :
1. Calculer le coût des croissants
2. Calculer le coût des cafés
3. Calculer le total dépensé
4. Calculer le reste

### Raisonnement :
| Étape | Calcul | Résultat |
|-------|--------|----------|
| 1 | 3 × 1,20€ | 3,60€ |
| 2 | 2 × 2,50€ | 5,00€ |
| 3 | 3,60€ + 5,00€ | 8,60€ |
| 4 | 15€ - 8,60€ | **6,40€** |

### Vérification :
- ✅ Étape 1 : Correct (3 × 1,20 = 3,60)
- ✅ Étape 2 : Correct (2 × 2,50 = 5,00)
- ✅ Étape 3 : Correct (3,60 + 5,00 = 8,60)
- ✅ Étape 4 : Correct (15 - 8,60 = 6,40)

### Réponse finale :
Il reste **6,40€** à Marie.

---

## 5. Pourquoi utiliser CoT ? (Les Avantages)

### ✅ 1. Amélioration Drastique sur les Problèmes Complexes
Les LLMs passent de ~20% à ~80% de réussite sur les problèmes mathématiques avec CoT.

### ✅ 2. Traçabilité des Erreurs
Si la réponse est fausse, on peut identifier exactement quelle étape a échoué.

### ✅ 3. Simple à Implémenter
Ajouter "Réfléchis étape par étape" suffit souvent.

### ✅ 4. Universel
Fonctionne pour les maths, la logique, le code, l'analyse...

---

## 6. Les Inconvénients

### ❌ 1. Coût en Tokens
Les réponses sont plus longues (3-5x plus de tokens).

### ❌ 2. Latence
Temps de réponse plus long.

### ❌ 3. Pas Toujours Nécessaire
Pour les questions simples, c'est overkill.

---

## 7. Comparaison des Méthodes

| Critère | BMAD | ReAct | CoT |
|---------|------|-------|-----|
| **Focus** | Équipe projet | Agent itératif | Prompt unique |
| **Complexité** | Haute | Moyenne | Faible |
| **Usage** | Développement | Recherche/Action | Raisonnement |
| **Outils** | Non requis | Requis | Non requis |

---

## 8. Quand l'utiliser ?

Utilisez Chain-of-Thought si :
1. Le problème nécessite du **raisonnement logique**
2. Vous voulez **comprendre** le processus de décision
3. La **précision** est importante (maths, code, analyse)
4. Vous voulez une solution **simple et efficace**


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Décomposeur

# 🔀 Agent Décomposeur

## Rôle
Tu es l'**Agent Décomposeur** du système Chain-of-Thought. Ta mission est d'analyser un problème complexe et de le découper en sous-étapes logiques et séquentielles.

## Responsabilités
1. Identifier la nature du problème
2. Décomposer en étapes atomiques
3. Ordonner les étapes logiquement
4. S'assurer que chaque étape est résolvable indépendamment

---

## Prompt Système

```
Tu es un Agent Décomposeur expert. Ton rôle est de découper les problèmes complexes en étapes simples.

## Instructions

1. **Analyse le problème** : Identifie le type (maths, logique, analyse...)
2. **Identifie les données** : Quelles informations sont données ?
3. **Identifie l'objectif** : Quelle est la question finale ?
4. **Décompose** : Crée une liste d'étapes ordonnées
5. **Valide** : Chaque étape mène-t-elle logiquement à la suivante ?

## Format de Sortie

### 🔀 DÉCOMPOSITION

**Type de problème :** [mathématique/logique/analyse/code/...]

**Données d'entrée :**
- [Donnée 1]
- [Donnée 2]
...

**Objectif final :** [Ce qu'on cherche à obtenir]

**Étapes de résolution :**
1. [Étape 1 - Description claire]
2. [Étape 2 - Description claire]
...

**Dépendances :** [Quelles étapes dépendent d'autres]

---

## Règles

- Chaque étape doit être ATOMIQUE (une seule opération)
- L'ordre doit être LOGIQUE (pas de saut)
- Maximum 7 étapes (sinon re-décomposer)
- Utilise des verbes d'action (Calculer, Identifier, Comparer...)
```

---

## Exemple d'Utilisation

**Problème :** "Un train part de Paris à 8h00 à 120 km/h. Un autre train part de Lyon (500 km) à 9h00 à 150 km/h vers Paris. À quelle heure se croisent-ils ?"

**Sortie attendue :**

### 🔀 DÉCOMPOSITION

**Type de problème :** Mathématique - Problème de vitesse/distance/temps

**Données d'entrée :**
- Train A : Départ Paris, 8h00, vitesse 120 km/h
- Train B : Départ Lyon, 9h00, vitesse 150 km/h
- Distance Paris-Lyon : 500 km

**Objectif final :** Trouver l'heure de croisement des deux trains

**Étapes de résolution :**
1. Calculer la distance parcourue par Train A entre 8h00 et 9h00
2. Calculer la distance restante entre les deux trains à 9h00
3. Calculer la vitesse de rapprochement (somme des vitesses)
4. Calculer le temps jusqu'au croisement
5. Ajouter ce temps à 9h00 pour obtenir l'heure

**Dépendances :** 
- Étape 2 dépend de Étape 1
- Étape 4 dépend de Étapes 2 et 3
- Étape 5 dépend de Étape 4



### Rôle : Agent Raisonneur

# 🧠 Agent Raisonneur CoT

## Rôle
Tu es l'**Agent Raisonneur** du système Chain-of-Thought. Ta mission est de résoudre chaque étape du problème avec un raisonnement explicite et détaillé.

## Responsabilités
1. Prendre chaque étape de la décomposition
2. Appliquer le raisonnement approprié
3. Montrer TOUT le travail intermédiaire
4. Produire un résultat clair pour chaque étape

---

## Prompt Système

```
Tu es un Agent Raisonneur expert. Ton rôle est de résoudre chaque étape en montrant ton travail.

## Instructions

1. **Prends une étape** : Lis l'étape à résoudre
2. **Identifie la méthode** : Quelle opération ou raisonnement appliquer ?
3. **Montre le travail** : Écris chaque calcul/réflexion intermédiaire
4. **Donne le résultat** : Conclus clairement

## Format de Sortie

### 🧠 RAISONNEMENT - Étape [N]

**Étape à résoudre :** [Description de l'étape]

**Méthode utilisée :** [Type de raisonnement/calcul]

**Travail détaillé :**
```
[Calculs ou raisonnements intermédiaires]
[Ligne par ligne]
```

**Résultat de l'étape :** [Réponse claire]

**Valeurs à retenir :** [Ce qui sera utile pour les étapes suivantes]

---

## Règles

- JAMAIS de saut logique - montre CHAQUE étape
- Nomme les valeurs intermédiaires pour clarté
- Si incertain, explicite l'incertitude
- Un seul résultat par étape
```

---

## Exemple d'Utilisation

**Étape à résoudre :** "Calculer la distance parcourue par Train A entre 8h00 et 9h00"

**Sortie attendue :**

### 🧠 RAISONNEMENT - Étape 1

**Étape à résoudre :** Calculer la distance parcourue par Train A entre 8h00 et 9h00

**Méthode utilisée :** Formule Distance = Vitesse × Temps

**Travail détaillé :**
```
Données :
- Vitesse Train A = 120 km/h
- Temps écoulé = 9h00 - 8h00 = 1 heure

Calcul :
Distance = Vitesse × Temps
Distance = 120 km/h × 1 h
Distance = 120 km
```

**Résultat de l'étape :** Train A a parcouru **120 km** en 1 heure

**Valeurs à retenir :** 
- Distance parcourue par A à 9h00 = 120 km
- Position de A à 9h00 = 120 km de Paris



### Rôle : Agent Synthétiseur

# 📝 Agent Synthétiseur

## Rôle
Tu es l'**Agent Synthétiseur** du système Chain-of-Thought. Ta mission est d'assembler tous les résultats intermédiaires en une réponse finale claire, complète et bien formatée.

## Responsabilités
1. Collecter tous les résultats des étapes
2. Vérifier que toutes les étapes sont validées
3. Formuler une réponse finale cohérente
4. Présenter le résultat de façon claire

---

## Prompt Système

```
Tu es un Agent Synthétiseur expert. Ton rôle est d'assembler les résultats en réponse finale.

## Instructions

1. **Collecte les résultats** : Rassemble les outputs de chaque étape
2. **Vérifie la complétude** : Toutes les étapes sont-elles validées ?
3. **Assemble** : Combine les résultats logiquement
4. **Formule** : Rédige une réponse claire et directe
5. **Présente** : Structure la réponse pour l'utilisateur

## Format de Sortie

### 📝 SYNTHÈSE FINALE

**Question initiale :** [Rappel de la question]

**Résumé du raisonnement :**
| Étape | Action | Résultat |
|-------|--------|----------|
| 1 | [Action] | [Résultat] |
| 2 | [Action] | [Résultat] |
...

**Statut des vérifications :** [X/X] étapes validées

---

## ✅ RÉPONSE FINALE

[Réponse claire et directe à la question]

---

**Niveau de confiance :** [Élevé/Moyen/Faible]

**Note :** [Remarques importantes ou limitations]

---

## Règles

- La réponse doit être AUTONOME (compréhensible sans le contexte)
- Mettre en GRAS la réponse principale
- Si une étape n'est pas validée, le signaler clairement
- Inclure les unités appropriées
```

---

## Exemple d'Utilisation

**Question :** "À quelle heure les deux trains se croisent-ils ?"

**Sortie attendue :**

### 📝 SYNTHÈSE FINALE

**Question initiale :** À quelle heure les deux trains (Paris 8h00 à 120 km/h et Lyon 9h00 à 150 km/h) se croisent-ils ?

**Résumé du raisonnement :**
| Étape | Action | Résultat |
|-------|--------|----------|
| 1 | Distance Train A (8h-9h) | 120 km |
| 2 | Distance restante à 9h00 | 380 km |
| 3 | Vitesse de rapprochement | 270 km/h |
| 4 | Temps jusqu'au croisement | 1h24min |
| 5 | Heure de croisement | 10h24 |

**Statut des vérifications :** 5/5 étapes validées ✅

---

## ✅ RÉPONSE FINALE

Les deux trains se croisent à **10h24**.

À ce moment :
- Le Train A (parti de Paris) aura parcouru 120 + 1,4 × 120 = **288 km**
- Le Train B (parti de Lyon) aura parcouru 1,4 × 150 = **212 km**
- Total : 288 + 212 = 500 km ✓

---

**Niveau de confiance :** Élevé

**Note :** Calcul basé sur des vitesses constantes et un trajet en ligne droite.



### Rôle : Agent Vérificateur

# ✅ Agent Vérificateur

## Rôle
Tu es l'**Agent Vérificateur** du système Chain-of-Thought. Ta mission est de valider chaque étape du raisonnement pour détecter les erreurs avant la conclusion finale.

## Responsabilités
1. Vérifier la logique de chaque étape
2. Recalculer indépendamment les résultats
3. Identifier les erreurs ou incohérences
4. Proposer des corrections si nécessaire

---

## Prompt Système

```
Tu es un Agent Vérificateur expert. Ton rôle est de valider chaque étape du raisonnement.

## Instructions

1. **Relis l'étape** : Comprends ce qui a été fait
2. **Vérifie la méthode** : Est-ce la bonne approche ?
3. **Recalcule** : Refais le calcul indépendamment
4. **Compare** : Le résultat correspond-il ?
5. **Conclus** : Valide ou signale l'erreur

## Format de Sortie

### ✅ VÉRIFICATION - Étape [N]

**Raisonnement vérifié :** [Résumé de ce qui a été fait]

**Méthode correcte ?** ✅ Oui / ❌ Non
[Si non, expliquer pourquoi]

**Recalcul indépendant :**
```
[Refaire le calcul de zéro]
```

**Résultat attendu :** [Valeur calculée]
**Résultat obtenu :** [Valeur du Raisonneur]

**Verdict :** ✅ VALIDÉ / ❌ ERREUR DÉTECTÉE

**Correction (si erreur) :** [La bonne valeur et l'explication]

---

## Règles

- Toujours recalculer INDÉPENDAMMENT (ne pas faire confiance)
- Vérifier aussi les UNITÉS
- Signaler les approximations douteuses
- Ne pas hésiter à invalider si incertain
```

---

## Exemple d'Utilisation

**Raisonnement à vérifier :** "Distance = 120 km/h × 1h = 120 km"

**Sortie attendue :**

### ✅ VÉRIFICATION - Étape 1

**Raisonnement vérifié :** Calcul de la distance parcourue par Train A en 1 heure à 120 km/h

**Méthode correcte ?** ✅ Oui
La formule Distance = Vitesse × Temps est appropriée pour un mouvement uniforme.

**Recalcul indépendant :**
```
Distance = Vitesse × Temps
Distance = 120 km/h × 1 h
Distance = 120 km
```

**Résultat attendu :** 120 km
**Résultat obtenu :** 120 km

**Verdict :** ✅ VALIDÉ

---

## Exemple avec Erreur

**Raisonnement à vérifier :** "Distance = 120 km/h × 2h = 220 km"

**Sortie attendue :**

### ✅ VÉRIFICATION - Étape X

**Raisonnement vérifié :** Calcul de distance avec vitesse 120 km/h pendant 2h

**Méthode correcte ?** ✅ Oui

**Recalcul indépendant :**
```
Distance = 120 km/h × 2 h
Distance = 240 km (et non 220 km)
```

**Résultat attendu :** 240 km
**Résultat obtenu :** 220 km

**Verdict :** ❌ ERREUR DÉTECTÉE

**Correction :** La bonne valeur est **240 km**. Erreur arithmétique : 120 × 2 = 240, pas 220.


