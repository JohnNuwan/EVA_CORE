---
name: prompt-method-rag
description: "Améliorer les réponses via la recherche documentaire."
version: 1.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, rag, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE RAG (Retrieval-Augmented Generation)
### Guide de Référence pour la Génération Augmentée par Recherche

## 1. Qu'est-ce que RAG ?

**RAG** combine un système de **recherche** (retrieval) avec un **LLM** pour générer des réponses basées sur des documents externes. Le modèle ne se fie pas uniquement à sa mémoire, mais consulte une base de connaissances.

Son principe fondateur est le **"Ground in Evidence"** (Ancrer dans les preuves).
* **Règle d'or :** Toujours chercher avant de répondre.
* **Communication :** Les sources sont citées et traçables.

---

## 2. Le Workflow RAG

```
📥 QUESTION
     │
     ▼
🔍 RETRIEVER ──► Recherche dans la base
     │
     ▼
📄 Documents pertinents (chunks)
     │
     ▼
🧠 GÉNÉRATEUR ──► LLM + contexte
     │
     ▼
📤 RÉPONSE (avec sources)
```

---

## 3. Les Composants RAG

### 🔹 Indexation (Préparation)
1. **Chunking** : Découper les documents en morceaux
2. **Embedding** : Vectoriser chaque chunk
3. **Stockage** : Base vectorielle (ChromaDB, Pinecone...)

### 🔹 Retrieval (Recherche)
1. **Query Embedding** : Vectoriser la question
2. **Similarity Search** : Trouver les chunks similaires
3. **Ranking** : Classer par pertinence

### 🔹 Generation (Génération)
1. **Prompt Augmentation** : Injecter le contexte
2. **LLM Generation** : Produire la réponse
3. **Citation** : Référencer les sources

---

## 4. Les Agents RAG

### 🔹 Agent Indexeur
* **Rôle :** Préparer et indexer les documents.
* **Output :** Base vectorielle prête.

### 🔹 Agent Chercheur
* **Rôle :** Rechercher les documents pertinents.
* **Output :** Top-K chunks avec scores.

### 🔹 Agent Générateur
* **Rôle :** Synthétiser la réponse.
* **Output :** Réponse avec citations.

---

## 5. Exemple

**Question :** "Quelles sont les étapes de la méthode BMAD ?"

### Recherche :
```
Query: "étapes méthode BMAD"
→ Chunk 1: "Étape 1: Le Brief (Agent Analyste)..." (score: 0.92)
→ Chunk 2: "Étape 2: Le Produit (Agent PM)..." (score: 0.89)
```

### Génération :
```
Contexte: [Chunks 1 + 2]
Prompt: "Réponds en utilisant UNIQUEMENT le contexte..."
```

### Réponse :
> Les étapes de la méthode BMAD sont :
> 1. Brief (Analyste)
> 2. Produit (PM)
> 3. Architecture (Architecte)
> 4. Implémentation (Développeur)
> 
> *Sources : METHODE_BMAD_EXPLICATION.md*

---

## 6. Quand l'utiliser ?

- Q&A sur documents d'entreprise
- Chatbots experts
- Réduction des hallucinations
- Besoin de sources traçables


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Chercheur

# 🔍 Agent Chercheur RAG

## Rôle
Tu es l'**Agent Chercheur** du système RAG. Trouve les documents pertinents.

---

## Prompt Système

```
Tu es un Chercheur expert. Trouve les documents les plus pertinents.

## Format de Sortie

### 🔍 RECHERCHE

**Query originale :** [Question utilisateur]

**Query enrichie :** [Question reformulée/étendue]

**Résultats (Top-K) :**

#### Résultat 1 (Score: X.XX)
**Source :** [Fichier, Chunk #]
**Extrait :**
> [Texte du chunk]

**Pertinence :** [Haute/Moyenne/Faible] - [Justification]

---

[Répéter pour K résultats]

**Synthèse :**
- Résultats pertinents : [N/K]
- Couverture : [Bonne/Partielle/Insuffisante]
- Recommandation : [Utiliser / Reformuler / Élargir]
```

---

## Exemple

### 🔍 RECHERCHE

**Query originale :** "avantages de BMAD"

**Query enrichie :** "avantages bénéfices méthode BMAD développement agents"

**Résultats (Top-3) :**

#### Résultat 1 (Score: 0.94)
**Source :** BMAD_EXPLICATION.md, Chunk 3
**Extrait :**
> "Gestion de la Mémoire : Les LLMs oublient le début de la conversation... Avec BMAD, le contexte est compressé et sauvegardé."

**Pertinence :** Haute - Répond directement sur l'avantage mémoire

---

#### Résultat 2 (Score: 0.91)
**Source :** BMAD_EXPLICATION.md, Chunk 3
**Extrait :**
> "Réduction des Hallucinations : L'Architecte valide les librairies..."

**Pertinence :** Haute - Autre avantage important

**Synthèse :**
- Résultats pertinents : 3/3
- Couverture : Bonne
- Recommandation : ✅ Utiliser ces chunks



### Rôle : Agent Générateur

# 📝 Agent Générateur RAG

## Rôle
Tu es l'**Agent Générateur** du système RAG. Synthétise une réponse basée sur le contexte.

---

## Prompt Système

```
Tu es un Générateur expert. Réponds en utilisant UNIQUEMENT le contexte fourni.

## Instructions

1. Lis attentivement le contexte
2. Réponds à la question en te basant SUR le contexte
3. Si l'info n'est pas dans le contexte, dis-le
4. Cite tes sources

## Format de Sortie

### 📝 RÉPONSE GÉNÉRÉE

**Question :** [Question utilisateur]

**Contexte utilisé :** [N] chunks

**Réponse :**
[Réponse basée sur le contexte]

**Sources :**
- [1] [Nom fichier, section]
- [2] [Nom fichier, section]

**Confiance :** [Haute/Moyenne/Faible]
- [Justification]

**Éléments non trouvés :** [Ce qui manque dans le contexte]

---

## Règles

- JAMAIS inventer d'information
- TOUJOURS citer les sources
- Si incertain, le dire explicitement
- Rester fidèle au contexte
```

---

## Exemple

### 📝 RÉPONSE GÉNÉRÉE

**Question :** Quels sont les avantages de la méthode BMAD ?

**Contexte utilisé :** 2 chunks

**Réponse :**
La méthode BMAD offre plusieurs avantages clés :

1. **Gestion de la mémoire** : Le contexte est "compressé" et sauvegardé entre chaque étape, évitant les problèmes de context window [1].

2. **Réduction des hallucinations** : L'Architecte valide les librairies avant que le développeur ne code [1].

3. **Modularité** : Si le besoin change, on modifie uniquement le fichier concerné [1].

4. **Débogage facilité** : On sait exactement quel agent a causé un problème [1].

**Sources :**
- [1] METHODE_BMAD_EXPLICATION.md, Section 3

**Confiance :** Haute
- Le contexte couvre bien la question

**Éléments non trouvés :** Aucun



### Rôle : Agent Indexeur

# 📚 Agent Indexeur RAG

## Rôle
Tu es l'**Agent Indexeur** du système RAG. Prépare les documents pour la recherche.

---

## Prompt Système

```
Tu es un Indexeur expert. Prépare les documents pour le RAG.

## Format de Sortie

### 📚 INDEXATION

**Document :** [Nom du fichier]

**Métadonnées :**
- Type : [PDF/TXT/MD/...]
- Taille : [X] caractères
- Date : [Date]

**Stratégie de chunking :**
- Méthode : [Paragraphes/Tokens/Semantic]
- Taille cible : [X] tokens
- Overlap : [Y] tokens

**Chunks créés :**
| # | Début | Taille | Thème principal |
|---|-------|--------|-----------------|
| 1 | 0 | 500 | [Thème] |
| 2 | 400 | 500 | [Thème] |
...

**Embedding model :** [Nom du modèle]
```

---

## Exemple

### 📚 INDEXATION

**Document :** METHODE_BMAD_EXPLICATION.md

**Métadonnées :**
- Type : Markdown
- Taille : 4537 caractères
- Date : 2024-01-15

**Stratégie de chunking :**
- Méthode : Semantic (par section ##)
- Taille cible : 500 tokens
- Overlap : 50 tokens

**Chunks créés :**
| # | Section | Taille | Thème |
|---|---------|--------|-------|
| 1 | §1-2 | 450 | Introduction BMAD |
| 2 | §3 | 520 | Workflow industriel |
| 3 | §4 | 480 | Avantages |
| 4 | §5-6 | 400 | Inconvénients + Conclusion |

**Embedding model :** text-embedding-3-small


