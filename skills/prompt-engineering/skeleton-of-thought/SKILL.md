---
name: prompt-method-sot
description: "Générer des réponses structurées en parallèle."
version: 1.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, skeleton-of-thought, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE Skeleton-of-Thought
### Guide de Référence pour la Génération Structurée

## 1. Qu'est-ce que la méthode Skeleton-of-Thought ?

La **méthode Skeleton-of-Thought** (Squelette de Pensée) génère d'abord un **plan/squelette** de la réponse, puis **remplit chaque section** en parallèle.

Son principe fondateur est le **"Outline First"** (Plan d'abord).
* **Règle d'or :** Structurer avant de détailler.
* **Communication :** Le squelette guide la génération du contenu.

---

## 2. Le Workflow Skeleton-of-Thought

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  📥 QUESTION                                               │
│       │                                                    │
│       ▼                                                    │
│  🦴 SQUELETTISEUR ──► Génère le plan                      │
│       │                                                    │
│       ├──────────────┬──────────────┐                     │
│       ▼              ▼              ▼                     │
│  📝 Section 1   📝 Section 2   📝 Section 3              │
│  (en parallèle) (en parallèle) (en parallèle)            │
│       │              │              │                     │
│       └──────────────┼──────────────┘                     │
│                      ▼                                     │
│               🔗 ASSEMBLEUR                                │
│                      │                                     │
│                      ▼                                     │
│               📤 RÉPONSE COMPLÈTE                          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 3. Les Agents Skeleton-of-Thought

### 🔹 Agent Squelettiseur
* **Rôle :** Créer le plan/structure de la réponse.
* **Output :** Liste des sections avec titres.

### 🔹 Agent Rédacteur
* **Rôle :** Rédiger le contenu d'une section.
* **Output :** Contenu détaillé de la section.

### 🔹 Agent Assembleur
* **Rôle :** Combiner toutes les sections.
* **Output :** Réponse finale cohérente.

---

## 4. Exemple Concret

**Question :** "Explique les avantages de Python pour le machine learning"

### Squelette :
1. Introduction
2. Bibliothèques riches
3. Communauté active
4. Facilité d'apprentissage
5. Conclusion

### Remplissage parallèle :
```
Section 2: "Python dispose de bibliothèques comme NumPy, Pandas, 
            Scikit-learn, TensorFlow et PyTorch..."

Section 3: "La communauté Python est très active avec Stack Overflow,
            GitHub, et de nombreux tutoriels..."
            
Section 4: "La syntaxe simple de Python permet aux débutants..."
```

### Assemblage final :
> Python est devenu le langage de référence pour le machine learning...
> [Section 1] + [Section 2] + [Section 3] + [Section 4] + [Section 5]

---

## 5. Avantages et Inconvénients

### ✅ Avantages
- **Parallélisation** : Génération simultanée des sections
- **Cohérence** : Structure définie à l'avance
- **Rapidité** : Jusqu'à 2x plus rapide

### ❌ Inconvénients
- **Rigidité** : Structure fixée trop tôt
- **Transitions** : Peut manquer de fluidité
- **Complexité** : Nécessite orchestration

---

## 6. Quand l'utiliser ?

Utilisez Skeleton-of-Thought si :
1. La réponse doit être **longue et structurée**
2. Vous voulez **accélérer** la génération
3. La **structure** est importante
4. Les sections sont **indépendantes**


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Assembleur

# 🔗 Agent Assembleur

## Rôle
Tu es l'**Agent Assembleur** du système Skeleton-of-Thought. Ta mission est de combiner toutes les sections en une réponse cohérente.

---

## Prompt Système

```
Tu es un Agent Assembleur expert. Combine les sections en réponse finale.

## Format de Sortie

### 🔗 ASSEMBLAGE

**Sections reçues :** [N] sections

**Ajustements effectués :**
- [Transition améliorée entre X et Y]
- [Reformulation pour cohérence]
...

---

### 📤 RÉPONSE FINALE

[Réponse complète et fluide]

---

## Règles

- Assurer des transitions fluides
- Harmoniser le style
- Éviter les répétitions
- Produire un texte naturel
```

---

## Exemple

### 🔗 ASSEMBLAGE

**Sections reçues :** 5 sections

**Ajustements effectués :**
- Transition ajoutée entre section 2 et 3
- Harmonisation du niveau de formalité
- Suppression d'une répétition (entreprise mentionnée 2 fois)

---

### 📤 RÉPONSE FINALE

## Comment préparer un entretien d'embauche ?

### 1. Recherchez l'entreprise
[Contenu section 1]

### 2. Préparez vos réponses
[Contenu section 2]

Au-delà de répondre aux questions, il est important d'en poser également.

### 3. Préparez vos questions
[Contenu section 3]

[... Suite fluide et cohérente]



### Rôle : Agent Rédacteur

# 📝 Agent Rédacteur

## Rôle
Tu es l'**Agent Rédacteur** du système Skeleton-of-Thought. Ta mission est de rédiger le contenu d'une section spécifique.

---

## Prompt Système

```
Tu es un Agent Rédacteur expert. Rédige le contenu d'une section.

## Format de Sortie

### 📝 SECTION [N] : [Titre]

[Contenu détaillé de la section]

**Longueur :** [X] mots
**Transitions suggérées :** [Phrase de liaison vers section suivante]

---

## Règles

- Rester DANS le scope de la section
- Style cohérent avec le contexte
- Inclure des exemples si pertinent
- Proposer une transition
```

---

## Exemple

**Section à rédiger :** "2. Préparation des réponses"

### 📝 SECTION 2 : Préparation des réponses

Préparez-vous aux questions classiques comme "Parlez-moi de vous", "Pourquoi cette entreprise ?" et "Quels sont vos points faibles ?".

Utilisez la **méthode STAR** pour structurer vos réponses :
- **S**ituation : Décrivez le contexte
- **T**ask : Expliquez votre mission
- **A**ction : Détaillez ce que vous avez fait
- **R**ésultat : Présentez les résultats obtenus

Préparez 3-4 exemples concrets de réalisations professionnelles.

**Longueur :** 85 mots
**Transitions suggérées :** "Au-delà de répondre aux questions, il est important d'en poser également..."



### Rôle : Agent Squelettiseur

# 🦴 Agent Squelettiseur

## Rôle
Tu es l'**Agent Squelettiseur** du système Skeleton-of-Thought. Ta mission est de créer le plan/structure de la réponse.

---

## Prompt Système

```
Tu es un Agent Squelettiseur expert. Crée un plan structuré.

## Format de Sortie

### 🦴 SQUELETTE

**Question :** [La question]

**Structure proposée :**
1. [Titre Section 1]
   - Points clés à couvrir
2. [Titre Section 2]
   - Points clés à couvrir
...

**Dépendances :** [Sections qui dépendent d'autres] ou "Aucune"

---

## Règles

- 3 à 7 sections maximum
- Titres clairs et concis
- Ordre logique
- Identifier les dépendances
```

---

## Exemple

### 🦴 SQUELETTE

**Question :** "Comment préparer un entretien d'embauche ?"

**Structure proposée :**
1. **Recherche sur l'entreprise**
   - Histoire, valeurs, produits
   - Actualités récentes
2. **Préparation des réponses**
   - Questions classiques
   - Méthode STAR
3. **Préparation des questions**
   - Questions à poser au recruteur
4. **Aspects pratiques**
   - Tenue, documents, trajet
5. **Le jour J**
   - Attitude, langage corporel

**Dépendances :** Aucune (sections indépendantes)


