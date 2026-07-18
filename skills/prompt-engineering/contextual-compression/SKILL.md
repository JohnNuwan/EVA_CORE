---
name: prompt-method-contextual-compression
description: "Réduire la taille du contexte d'un document long en n'en conservant que les informations pertinentes pour une question cible."
version: 2.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, contextual-compression, biblio-ia, methods, document-processing, rag-optimization]
    related_skills: [python-pep8, simplify-code, plan, generated-knowledge, prompt-chaining]
---

# La méthode Contextual Compression

## Guide de référence pour la compression intelligente de contexte documentaire

---

## 1. Vue d'ensemble

La méthode **Contextual Compression** consiste à réduire la taille du contexte fourni à un LLM en n'en conservant que les **passages pertinents** par rapport à une question ou une tâche cible. Plutôt que de transmettre l'intégralité d'un document volumineux — au risque de saturer la fenêtre de contexte, d'augmenter les coûts et de diluer la pertinence — on applique une phase de compression préalable qui filtre, résume et structure l'information utile.

### Principe fondateur

Le cœur de la méthode repose sur le principe **« Less is More »** (Moins c'est plus) :

- **Pertinence sélective** : le bruit documentaire est éliminé, seuls les passages utiles sont conservés
- **Efficacité économique** : moins de tokens consommés → coût API réduit, latence améliorée
- **Précision accrue** : un contexte réduit et ciblé réduit les hallucinations et les erreurs d'attention
- **Scalabilité** : des documents de taille arbitraire peuvent être traités dans des fenêtres limitées

### Architecture conceptuelle

```
                    ┌──────────────────────────────────┐
                    │   Document original (N tokens)    │
                    │   Ex: 10 000 tokens, 50 pages     │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │      Phase de compression         │
                    │                                   │
                    │  ┌────────────────────────┐       │
                    │  │ Extraction des passages │       │
                    │  │ pertinents              │       │
                    │  └────────────────────────┘       │
                    │  ┌────────────────────────┐       │
                    │  │ Résumé des sections     │       │
                    │  │ importantes             │       │
                    │  └────────────────────────┘       │
                    │  ┌────────────────────────┐       │
                    │  │ Élimination du bruit    │       │
                    │  │ et des redondances      │       │
                    │  └────────────────────────┘       │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Contexte compressé (M tokens)    │
                    │  Ex: 1 000 tokens (90% réduction) │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │   LLM + Question cible            │
                    │   Réponse basée sur le contexte   │
                    │   compressé                       │
                    └──────────────────────────────────┘
```

---

## 2. Quand l'utiliser ?

### Cas d'usage recommandés

| Contexte | Description | Priorité |
|----------|-------------|----------|
| Documents longs | Rapports, articles scientifiques, documentation technique > fenêtre de contexte | Élevée |
| Optimisation des coûts API | Réduction significative du nombre de tokens par requête | Élevée |
| RAG (Retrieval-Augmented Generation) | Compression des documents récupérés avant passage au LLM | Élevée |
| Amélioration de la pertinence | Éliminer le bruit pour que le LLM se concentre sur l'essentiel | Élevée |
| Traitement par lots de documents | Multi-documents à analyser dans un budget de tokens limité | Moyenne |
| Applications temps réel | Latence réduite grâce à un contexte plus court | Moyenne |

### Situations à éviter

- **Documents très courts (< 500 tokens)** : le surcoût de compression dépasse le bénéfice
- **Documents hautement condensés** : un résumé exécutif déjà dense ne peut pas être compressé sans perte d'information
- **Questions nécessitant le document intégral** : analyse juridique exhaustive, revue de code complète
- **Documents avec une forte densité d'information** : chaque phrase est potentiellement utile

---

## 3. Procédure pas à pas

### Étape 1 : Définir la question ou l'intention cible

La compression doit être guidée par un objectif précis. Sans question cible, la compression est aveugle.

```
Question cible : « Quels sont les avantages de la méthode BMAD
par rapport aux approches traditionnelles de développement ? »
```

### Étape 2 : Segmenter le document original

Découpez le document en sections logiques (paragraphes, titres, sections) pour faciliter l'analyse.

```
Document : METHODE_BMAD_EXPLICATION.md (4500 caractères)

Segments identifiés :
§1. Introduction (400 car.) — Présentation de BMAD
§2. Contexte historique (600 car.) — Pourquoi BMAD a été créé
§3. Workflow détaillé (1200 car.) — Les étapes de BMAD
§4. Avantages comparatifs (1000 car.) — Bénéfices vs méthodes classiques
§5. Inconvénients et limites (800 car.) — Quand ne pas utiliser BMAD
§6. Conclusion (500 car.) — Recommandations finales
```

### Étape 3 : Analyser la pertinence de chaque segment

Pour chaque segment, évaluez sa pertinence par rapport à la question cible selon trois critères :

1. **Pertinence directe** : le segment contient-il une réponse partielle à la question ?
2. **Pertinence contextuelle** : le segment est-il nécessaire pour comprendre la réponse ?
3. **Redondance** : l'information est-elle déjà couverte par un autre segment ?

**Matrice de pertinence :**

| Segment | Pertinence directe | Pertinence contextuelle | Redondance | Décision |
|---------|-------------------|------------------------|------------|----------|
| §1 Intro | Faible | Moyenne | Non | Résumer (1 phrase) |
| §2 Contexte | Faible | Faible | Oui (§1) | Supprimer |
| §3 Workflow | Faible | Haute | Non | Résumer (3 phrases) |
| §4 Avantages | Haute | Haute | Non | Garder intégral |
| §5 Limites | Faible | Moyenne | Non | Résumer (1 phrase) |
| §6 Conclusion | Faible | Faible | Oui (§1, §4) | Supprimer |

### Étape 4 : Appliquer la compression

Pour chaque segment, appliquez l'action décidée :

```
§1 INTRO → Résumé :
« BMAD est une méthodologie de développement structurée. »

§3 WORKFLOW → Résumé :
« BMAD suit 4 étapes : Planification Architecte, Révision Validation,
Développement Dev, et Tests Intégration. Chaque étape est isolée
avec un contexte compressé transmis entre les phases. »

§4 AVANTAGES → Gardé intégralement :
« Les avantages de BMAD incluent :
1. Gestion optimisée de la mémoire : contexte compressé entre étapes
2. Réduction des hallucinations : l'Architecte valide avant le Dev
3. Modularité : modification d'un fichier sans tout refaire
4. Débogage simplifié : identification précise de l'agent fautif »

§5 LIMITES → Résumé :
« BMAD est moins adapté aux petites tâches simples où le surcoût
d'architecture dépasse le bénéfice. »
```

### Étape 5 : Assembler le contexte compressé

Concaténez les segments conservés et résumés en un document cohérent.

```
📄 CONTEXTE COMPRESSÉ (280 caractères)

BMAD est une méthodologie de développement structurée qui suit
4 étapes : Planification, Validation, Développement, Tests.

Les avantages incluent :
- Gestion mémoire optimisée (contexte compressé entre étapes)
- Réduction des hallucinations (Architecte valide avant Dev)
- Modularité et débogage facilité

BMAD est moins adapté aux petites tâches simples.

--- Statistiques ---
Original   : 4500 caractères
Compressé  :  280 caractères
Réduction  :   94%
Pertinence :   Haute (tous les passages sur les avantages conservés)
```

---

## 4. Workflow complet

```
                    ┌──────────────────────────────┐
                    │   Document original long      │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  Segmentation du document     │
                    │  en unités logiques           │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  Pour chaque segment :        │
                    │  Évaluation de pertinence     │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
     ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
     │  Haute       │   │  Moyenne     │   │  Faible      │
     │  pertinence  │   │  pertinence  │   │  pertinence  │
     └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
            │                 │                    │
            ▼                 ▼                    ▼
     ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
     │  Garder      │   │  Résumer     │   │  Supprimer   │
     │  intégral    │   │  (condenser) │   │              │
     └──────┬───────┘   └──────┬───────┘   └──────────────┘
            │                 │
            └─────────────────┘
                    │
                    ▼
     ┌──────────────────────────────┐
     │  Assemblage du contexte      │
     │  compressé final             │
     └──────────────┬───────────────┘
                    │
                    ▼
     ┌──────────────────────────────┐
     │  Transmission au LLM avec    │
     │  la question cible           │
     └──────────────┬───────────────┘
                    │
                    ▼
     ┌──────────────────────────────┐
     │  ✅ Réponse précise basée   │
     │     sur le contexte réduit   │
     └──────────────────────────────┘
```

---

## 5. Exemples concrets de code et prompts

### Exemple 1 : Compression pour analyse de documentation technique

**Prompt compresseur :**

```
Tu es un expert en compression de contexte documentaire.

Document original :
{{document_technique}}

Question cible : « Comment configurer l'authentification OAuth2
dans ce système ? »

Analyse le document section par section. Pour chaque section,
attribue une note de pertinence (⭐⭐⭐ = haute, ⭐⭐ = moyenne,
⭐ = faible) par rapport à la question.

Produis :
1. Un tableau d'analyse section par section
2. Le contexte compressé (max 500 tokens)
3. Les métriques de compression
```

**Sortie attendue :**

```
🗜️ COMPRESSION CONTEXTUELLE

🔍 ANALYSE DU DOCUMENT
| Section | Contenu | Pertinence | Décision |
|---------|---------|------------|----------|
| §1. Introduction | Présentation générale | ⭐ | Supprimer |
| §2. Prérequis | Python 3.8+, pip | ⭐⭐ | Résumer |
| §3. Installation | pip install package | ⭐ | Supprimer |
| §4. Configuration OAuth2 | Client ID, Secret, Redirect URIs | ⭐⭐⭐ | Garder |
| §5. Exemples d'usage | Code d'authentification | ⭐⭐⭐ | Garder |
| §6. Dépannage | Erreurs courantes | ⭐⭐ | Résumer |

📄 CONTEXTE COMPRESSÉ :
Pour configurer OAuth2 :
1. Obtenez un Client ID et Client Secret via le portail admin
2. Définissez l'URI de redirection : http://localhost:8080/callback
3. Utilisez le package authlib :

   from authlib.integrations.requests_client import OAuth2Session
   session = OAuth2Session(client_id, client_secret,
                           redirect_uri=redirect_uri)

4. Générez l'URL d'autorisation et échangez le code contre un token

📊 MÉTRIQUES :
- Original : 3 200 tokens
- Compressé : 180 tokens
- Réduction : 94.4%
```

### Exemple 2 : Compression multi-documents pour synthèse comparative

**Prompt :**

```
Tu dois comparer trois documents pour répondre à la question :

« Quelles sont les différences d'approche entre les méthodes
SCRUM, Kanban et Waterfall pour la gestion de projet logiciel ?»

Documents :
{{doc_scrum}} (3k tokens)
{{doc_kanban}} (2.5k tokens)
{{doc_waterfall}} (2k tokens)

Consigne :
1. Pour chaque document, extrais UNIQUEMENT les sections qui
   décrivent l'approche, les cérémonies/processus, et les
   indicateurs de succès.
2. Compresse chaque document en max 300 tokens.
3. Produis un tableau comparatif final.
```

---

## 6. Pièges courants (Pitfalls)

### ⚠️ Piège n°1 : Sur-compression avec perte d'information critique

**Erreur :** En cherchant à maximiser le taux de réduction, on supprime ou résume trop, perdant des nuances importantes.

```
❌ Objectif : 95% de réduction
   → Résultat : il ne reste que 5% du document
   → La réponse du LLM est incomplète ou erronée
   → Économie de tokens, mais réponse inutilisable
```

**✅ Correction :** Fixez un taux de réduction maximum et vérifiez la couverture :

```
Règles :
- Ne jamais descendre en dessous de X tokens (seuil de couverture)
- Pour chaque concept clé de la question, vérifier qu'au moins
  un segment pertinent subsiste
- Après compression, le contexte doit permettre de répondre
  complètement à la question
```

### ⚠️ Piège n°2 : Absence de question cible (compression aveugle)

**Erreur :** Compression sans question directrice, résultant en un résumé générique qui ne sert pas la question spécifique.

```
❌ Sans question : « Résume ce document. »
   → Résultat : résumé équilibré mais pas orienté
   → Si la question est « Quels sont les risques ? », le résumé
     a peut-être omis la section des risques au profit d'autre chose
```

**✅ Correction :** Toujours fournir une question cible explicite :

```
Question cible : « [Question spécifique] »

Compresse le document en fonction de CETTE question uniquement.
Ignore les sections qui n'y répondent pas. Donne la priorité
aux sections qui y répondent directement.
```

### ⚠️ Piège n°3 : Mauvaise segmentation du document

**Erreur :** Segments trop grands (la pertinence varie à l'intérieur du segment) ou trop petits (contexte perdu).

```
❌ Segments trop grands : un segment de 3000 tokens avec un mix
   d'info pertinente et non pertinente
   → Décision binaire difficile (garder/supprimer/résumer tout le bloc)
❌ Segments trop petits : découpage phrase par phrase
   → Contexte perdu, difficulté à comprendre le sens global
```

**✅ Correction :** Segmentez par blocs sémantiques cohérents :

```
Taille de segment recommandée : 200-500 tokens
Critères de segmentation : un titre de section, un paragraphe
complet, ou une idée autonome (pas de coupure en milieu de phrase).
```

### ⚠️ Piège n°4 : Compression uniquement extractive sans reformulation

**Erreur :** Se contenter d'extraire des phrases existantes sans les reformuler, résultant en un texte décousu.

**✅ Correction :** Combinez extraction et résumé :

```
Pour les segments à « Garder » : extraction textuelle
Pour les segments à « Résumer » : reformulation par le LLM
(condensation avec conservation du sens)

Assemblage final : rédiger des phrases de transition entre
les segments pour garantir la cohérence.
```

---

## 7. Checklist d'utilisation

### Avant la compression

- [ ] La question cible est-elle clairement formulée ?
- [ ] La segmentation du document est-elle adaptée à sa structure ?
- [ ] Le seuil minimal de tokens pour le contexte compressé est-il défini ?
- [ ] La méthode de compression (extraction, résumé, mixte) est-elle choisie ?

### Pendant la compression

- [ ] Chaque segment a-t-il été évalué individuellement ?
- [ ] Les segments à haute pertinence ont-ils été conservés intégralement ?
- [ ] Les segments résumés contiennent-ils toujours l'essentiel ?
- [ ] Les segments supprimés sont-ils réellement non pertinents (vérification croisée) ?

### Après la compression

- [ ] Le contexte compressé permet-il de répondre complètement à la question ?
- [ ] Le taux de réduction est-il réaliste (pas de sur-compression) ?
- [ ] La cohérence du texte compressé est-elle maintenue ?
- [ ] Les métriques (tokens avant/après, réduction, pertinence) sont-elles documentées ?

### Pour un pipeline de production

- [ ] Le processus de compression est-il automatisé et reproductible ?
- [ ] Un mécanisme de fallback (document complet si compression insuffisante) est-il prévu ?
- [ ] Les métriques de compression sont-elles collectées pour analyse ?
- [ ] Le temps de compression est-il acceptable pour l'application visée ?

---

## 8. Variantes avancées

| Variante | Description | Quand l'utiliser |
|----------|-------------|-----------------|
| Compression hiérarchique | Compression à plusieurs niveaux (section → document → corpus) | Documents très longs (>50k tokens) |
| Compression avec LLM itératif | Compression en plusieurs passes : d'abord grossière, puis fine | Qualité de compression maximale |
| Compression + RAG hybride | RAG pour la récupération, compression pour le passage au LLM | Systèmes RAG en production |
| Compression conditionnelle | Compresser plus ou moins selon la complexité de la question | Budget tokens variable |
| Compression multi-question | Un seul document compressé pour plusieurs questions simultanées | Dashboard / analyse multidimensionnelle |

---

> **Note importante :** Contextual Compression est une technique essentielle pour tout système manipulant des documents longs. Son efficacité dépend crucialement de la qualité de la question cible. Plus la question est précise, plus la compression peut être agressive sans perte d'information utile. De plus, il est important de noter que cette méthode introduit un appel LLM supplémentaire pour la compression, ce qui doit être pris en compte dans le budget de latence et de coût global.

