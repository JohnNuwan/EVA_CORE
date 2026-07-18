---
name: prompt-method-graphrag
description: "Effectuer des recherches sémantiques sur graphes."
version: 1.0.0
author: John Nuwan Moncel (adapté par EVA)
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [prompt-engineering, graphrag, biblio-ia, methods]
    related_skills: [python-pep8, simplify-code, plan]
---

# LA MÉTHODE GraphRAG
### Guide de Référence pour RAG avec Graphes de Connaissances

## 1. Qu'est-ce que GraphRAG ?

**GraphRAG** combine RAG avec un **graphe de connaissances** pour capturer les relations entre entités, permettant des requêtes plus complexes.

Son principe fondateur est le **"Entities and Relationships"** (Entités et Relations).
* **Règle d'or :** Les relations comptent autant que les faits.
* **Communication :** Traversée du graphe + génération.

---

## 2. Le Workflow GraphRAG

```
📥 QUESTION
     │
     ▼
🔍 Entity Extraction ──► Identifie les entités
     │
     ▼
🕸️ Graph Traversal ──► Parcourt les relations
     │
     ▼
📄 Subgraph + Documents
     │
     ▼
🧠 GÉNÉRATEUR
     │
     ▼
📤 RÉPONSE
```

---

## 3. Structure du Graphe

```
      ┌─────────┐
      │ BMAD    │
      └────┬────┘
           │ utilise
    ┌──────┴──────┐
    ▼             ▼
┌───────┐    ┌───────┐
│Analyste│   │  PM   │
└───┬───┘    └───┬───┘
    │ produit    │ produit
    ▼            ▼
┌───────┐    ┌───────┐
│ Brief │    │  PRD  │
└───────┘    └───────┘
```

---

## 4. Les Agents GraphRAG

### 🔹 Agent Extracteur d'Entités
* **Rôle :** Identifier les entités dans la question.

### 🔹 Agent Traverseur
* **Rôle :** Parcourir le graphe pour trouver les infos.

### 🔹 Agent Générateur
* **Rôle :** Synthétiser depuis le sous-graphe.

---

## 5. Exemple

**Question :** "Quels documents produit l'Analyste dans BMAD ?"

### Extraction :
- Entités : [Analyste, BMAD, documents]

### Traversée :
```
BMAD → utilise → Analyste → produit → Brief
```

### Réponse :
> L'Analyste dans BMAD produit le **Brief** (01_project_brief.md).

---

## 6. Quand l'utiliser ?

- Questions impliquant des relations
- Données structurées (organigrammes, dépendances)
- Q&A multi-hop ("A qui appartient X qui fait Y ?")


## Modèles de Prompts (Rôles des Agents)


### Rôle : Agent Extracteur

# 🔎 Agent Extracteur d'Entités

## Rôle
Tu es l'**Agent Extracteur** du système GraphRAG. Identifie les entités et relations.

---

## Prompt Système

```
Tu extrais les entités et relations des questions.

## Format de Sortie

### 🔎 EXTRACTION

**Question :** [Question]

**Entités identifiées :**
| Entité | Type | Confiance |
|--------|------|-----------|
| [X] | [Personne/Concept/Document] | Haute/Moyenne |
...

**Relations recherchées :**
- [Entité1] → [relation] → [Entité2]
...

**Requête graphe :**
```cypher
MATCH (a)-[r]->(b)
WHERE a.name = "X"
RETURN a, r, b
```
```

---

## Exemple

**Question :** "Qui supervise le Développeur dans BMAD ?"

### 🔎 EXTRACTION

**Entités identifiées :**
| Entité | Type | Confiance |
|--------|------|-----------|
| Développeur | Rôle | Haute |
| BMAD | Méthode | Haute |

**Relations recherchées :**
- [?] → supervise → [Développeur]
- [Développeur] → appartient_à → [BMAD]

**Requête graphe :**
```cypher
MATCH (sup)-[:SUPERVISE]->(dev:Role {name:"Développeur"})
WHERE (dev)-[:APPARTIENT_A]->(:Methode {name:"BMAD"})
RETURN sup
```



### Rôle : Agent Traverseur

# 🕸️ Agent Traverseur

## Rôle
Tu es l'**Agent Traverseur** du système GraphRAG. Parcours le graphe de connaissances.

---

## Prompt Système

```
Tu parcours le graphe pour trouver les informations.

## Format de Sortie

### 🕸️ TRAVERSÉE

**Requête :** [Description]

**Chemin parcouru :**
```
[Noeud1] ──relation1──► [Noeud2] ──relation2──► [Noeud3]
```

**Résultats trouvés :**
| Noeud | Propriétés | Distance |
|-------|------------|----------|
| [X] | [Props] | 1 hop |
...

**Sous-graphe extrait :**
[Description du contexte trouvé]

**Contexte pour génération :**
> [Texte synthétisé du sous-graphe]
```

---

## Exemple

### 🕸️ TRAVERSÉE

**Requête :** Trouver qui supervise le Développeur dans BMAD

**Chemin parcouru :**
```
[BMAD] ──contient──► [Architecte] ──précède──► [Développeur]
```

**Résultats trouvés :**
| Noeud | Rôle | Distance |
|-------|------|----------|
| Architecte | Décide tech | 1 hop |
| PM | Définit besoins | 2 hops |

**Contexte pour génération :**
> Dans BMAD, le Développeur suit les spécifications de l'Architecte. L'Architecte lit le PRD du PM et décide de la solution technique. Le Développeur ne fait qu'exécuter le plan.


