---
name: prompt-method-generated-knowledge
description: "Générer des connaissances pertinentes avant de répondre pour améliorer la précision et la fiabilité des réponses."
version: 2.0.0
author: John Nuwan Moncel (adapté par EVA)
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [prompt-engineering, generated-knowledge, biblio-ia, methods, self-context, rag-alternative]
    related_skills: [python-pep8, simplify-code, plan, contextual-compression, prompt-chaining]
---

# La méthode Generated Knowledge

## Guide de référence pour l'auto-génération de contexte factuel avant réponse

---

## 1. Vue d'ensemble

La méthode **Generated Knowledge** est une technique de prompt engineering qui consiste à demander au modèle de langage (LLM) de **générer explicitement des faits pertinents** avant de produire une réponse finale. Au lieu de répondre directement à partir de ses paramètres internes de façon implicite, le modèle est invité à externaliser son processus de rappel de connaissances, créant ainsi un **contexte auto-généré** (« Self-Context ») qui sert de base au raisonnement.

### Principe fondateur

Le cœur de la méthode repose sur le **« Self-Context »** (auto-contexte). En matérialisant les connaissances sous-jacentes avant de raisonner, le modèle :

- **Réduit les hallucinations** : les faits sont vérifiables avant d'être utilisés
- **Améliore la traçabilité** : chaque assertion peut être attribuée à un fait généré
- **Structure le raisonnement** : les connaissances servent de squelette logique à la réponse
- **Augmente la couverture** : le modèle explore systématiquement les dimensions pertinentes

### Architecture conceptuelle

```
                    ┌──────────────────────┐
                    │   Question entrante   │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌──────────────────────────────┐
              │  Phase 1 : Génération des    │
              │  connaissances (extraction   │
              │  des faits pertinents)        │
              └──────────────┬───────────────┘
                               │
                               ▼
              ┌──────────────────────────────┐
              │  Phase 2 : Validation et     │
              │  structuration des faits     │
              └──────────────┬───────────────┘
                               │
                               ▼
              ┌──────────────────────────────┐
              │  Phase 3 : Raisonnement sur  │
              │  la base des faits générés   │
              └──────────────┬───────────────┘
                               │
                               ▼
              ┌──────────────────────────────┐
              │  Phase 4 : Production de la  │
              │  réponse finale informée     │
              └──────────────────────────────┘
```

---

## 2. Quand l'utiliser ?

### Cas d'usage recommandés

| Contexte | Description | Priorité |
|----------|-------------|----------|
| Questions factuelles complexes | Le sujet nécessite une revue systématique des connaissances avant réponse | Élevée |
| Absence de sources externes | Aucun accès à une base documentaire, RAG, ou recherche web | Élevée |
| Domaines à forte exigence de précision | Médecine, droit, finance, ingénierie, conformité | Élevée |
| Sujets controversés ou nuancés | Le modèle doit peser les avantages et inconvénients | Moyenne |
| Apprentissage et pédagogie | Générer des explications structurées pour l'enseignement | Moyenne |
| Évaluation de la fiabilité | Vérifier ce que le modèle « sait » avant d'utiliser sa réponse | Moyenne |

### Situations à éviter

- **Questions triviales** : « Quelle est la capitale de la France ? » — la génération de connaissances est superflue
- **Tâches créatives pures** : la génération de poèmes ou d'histoires n'a pas besoin de faits structurés
- **Contextes à latence critique** : la double phase génération + raisonnement double le temps de réponse
- **Modèles non instruction-following** : les petits modèles peuvent mal comprendre la consigne en deux étapes

---

## 3. Procédure pas à pas

### Étape 1 : Formuler la question d'origine

Partez d'une question spécifique et clairement délimitée.

```
Question : « Quels sont les impacts de l'IA générative sur le marché
de l'emploi dans le secteur tertiaire d'ici 2030 ? »
```

### Étape 2 : Générer les connaissances préalables

Demandez au modèle de produire une liste structurée de faits pertinents sans encore répondre à la question.

**Prompt générateur :**

```
Avant de répondre à la question suivante, génère une liste structurée
de faits pertinents qui seront nécessaires pour formuler une réponse
complète et précise.

Question : « Quels sont les impacts de l'IA générative sur le marché
de l'emploi dans le secteur tertiaire d'ici 2030 ? »

Pour chaque fait, fournis :
1. Le fait lui-même
2. Une catégorie (Étude, Tendance, Statistique, Opinion d'expert)
3. Un niveau de confiance (Élevé / Moyen / Faible)
```

**Sortie attendue :**

```
📚 CONNAISSANCES GÉNÉRÉES

1. [Étude] Une étude McKinsey (2023) estime que 30% des tâches
   du tertiaire pourraient être automatisées d'ici 2030.
   (Confiance : Élevée ⭐⭐⭐)

2. [Tendance] L'IA générative crée de nouveaux métiers :
   prompt engineer, auditeur d'IA, spécialiste en alignement.
   (Confiance : Élevée ⭐⭐⭐)

3. [Statistique] 65% des emplois de la génération Z n'existent
   pas encore (Dell Technologies, 2022).
   (Confiance : Moyenne ⭐⭐)

4. [Opinion] Certains économistes prédisent un « effet rebond » :
   l'IA détruit des emplois mais en crée davantage indirectement.
   (Confiance : Moyenne ⭐⭐)

5. [Tendance] Le secteur tertiaire représente 78% de l'emploi
   en France (INSEE, 2023), amplifiant l'impact potentiel.
   (Confiance : Élevée ⭐⭐⭐)
```

### Étape 3 : Valider la pertinence des faits

Pour un usage critique, triez les faits générés :

- **Conserver** : faits à confiance élevée, directement utiles
- **Résumer** : faits à confiance moyenne, périphériques mais utiles
- **Éliminer** : faits redondants, non pertinents, ou à confiance faible

### Étape 4 : Produire le raisonnement informé

Utilisez explicitement les faits validés comme fondation pour la réponse.

**Prompt raisonneur :**

```
En utilisant UNIQUEMENT les faits suivants, réponds à la question
d'origine. Cite explicitement chaque fait utilisé.

Faits :
1. McKinsey 2023 : 30% des tâches tertiaires automatisables d'ici 2030
2. Création de nouveaux métiers IA (prompt engineer, auditeur, etc.)
3. Prévisions économistes : effet rebond possible
4. Secteur tertiaire = 78% de l'emploi en France

Question : Quels sont les impacts de l'IA générative sur le marché
de l'emploi dans le secteur tertiaire d'ici 2030 ?
```

### Étape 5 : Synthétiser la réponse finale

La réponse finale doit montrer clairement le lien entre les faits et la conclusion.

---

## 4. Workflow complet

```
                    ┌───────────────────────────┐
                    │   Question utilisateur    │
                    └───────────┬───────────────┘
                                │
                    ┌───────────▼───────────────┐
                    │  Évaluer si Generated     │
            Non ───►│  Knowledge est pertinent  │
                    └───────────┬───────────────┘
                                │ Oui
                    ┌───────────▼───────────────┐
                    │  Phase 1 : GÉNÉRATION      │
                    │  des connaissances brutes  │
                    └───────────┬───────────────┘
                                │
                    ┌───────────▼───────────────┐
                    │  Phase 2 : FILTRAGE        │
                    │  et validation des faits   │
                    └───────────┬───────────────┘
                                │
                    ┌───────────▼───────────────┐
                    │  Phase 3 : RAISONNEMENT    │
                    │  à partir des faits retenus│
                    └───────────┬───────────────┘
                                │
                    ┌───────────▼───────────────┐
                    │  Phase 4 : RÉPONSE         │
                    │  finale avec citations     │
                    └───────────┬───────────────┘
                                │
                    ┌───────────▼───────────────┐
                    │  Vérification : chaque     │
                    │  assertion est-elle        │◄── Si non, retour phase 2
                    │  soutenue par un fait ?    │
                    └───────────┬───────────────┘
                                │ Oui
                    ┌───────────▼───────────────┐
                    │  ✅ Réponse livrée         │
                    └───────────────────────────┘
```

---

## 5. Exemples concrets de code et prompts

### Exemple 1 : Analyse comparative (Python vs JavaScript)

**Prompt générateur :**

```
Génère une liste de faits pertinents pour comparer Python et
JavaScript dans le contexte du développement backend.
Inclus : performance, écosystème, courbe d'apprentissage,
marché de l'emploi, et cas d'usage typiques.
```

**Réponse générée :**

```
📚 CONNAISSANCES GÉNÉRÉES

1. Performance brute : JavaScript (Node.js) est 2-3x plus rapide
   que Python pour les opérations I/O grâce à son event-loop.
   (Confiance : Élevée)

2. Écosystème backend : Python → Django, FastAPI, Flask.
   JavaScript → Express, NestJS, Fastify.
   (Confiance : Élevée)

3. Marché : Python domine la data science et le ML.
   JavaScript domine le fullstack et les startups.
   (Confiance : Élevée)

4. Apprentissage : Python réputé plus accessible aux débutants.
   (Confiance : Élevée)

🧠 RAISONNEMENT :
Les deux langages sont viables pour le backend. Python excelle
pour les applications data-centrées (ML, API, ETL). JavaScript
est préféré pour les architectures temps réel, microservices,
et les équipes fullstack homogènes.

📤 RÉPONSE :
Choix recommandé :
- Python si : data science, ML, équipe hétérogène, lisibilité
- JavaScript si : temps réel, fullstack JS, haute performance I/O
```

### Exemple 2 : Question médicale (avec niveau de confiance)

```
Question : « Le café est-il bénéfique pour la santé cardiovasculaire ? »

📚 CONNAISSANCES GÉNÉRÉES
1. [Étude] La consommation modérée (3-4 tasses/jour) est associée
   à une réduction de 15% du risque cardiovasculaire (ESC 2022).
   (Confiance : Élevée)
2. [Mécanisme] Les polyphénols du café améliorent la fonction
   endothéliale.
   (Confiance : Moyenne)
3. [Risque] La consommation excessive (>5 tasses/jour) augmente
   le risque d'hypertension.
   (Confiance : Élevée)
```

---

## 6. Pièges courants (Pitfalls)

### ⚠️ Piège n°1 : Faits inventés par le modèle

**Erreur :** Le modèle génère des « faits » qui sont en réalité des hallucinations, puis les utilise comme base de sa réponse, créant une cascade d'erreurs.

```
❌ Élève : « Je te génère les faits, puis je réponds à partir d'eux »
   → Le modèle cite une étude qui n'existe pas (« Research Institute
      of Cognitive Science, 2024 »), puis construit sa réponse
      entièrement sur cette base fictive.
```

**✅ Correction :** Ajoutez une instruction de vérification de la véracité et de la confiance :

```
Pour chaque fait, indique ton niveau de confiance :
- 🔒 Élevé : fait bien établi, non controversé
- ⚠️ Moyen : tendance ou opinion probable
- ❓ Faible : spéculation ou information incertaine

N'invente PAS d'études ou de statistiques. Préfère dire
« Je ne dispose pas de donnée précise sur ce point ».
```

### ⚠️ Piège n°2 : Génération trop volumineuse

**Erreur :** Le modèle génère une liste de 20+ faits, ce qui dilue l'information pertinente et alourdit le contexte.

**✅ Correction :** Limitez explicitement le nombre de faits :

```
Génère au maximum 5 à 7 faits pertinents. Si tu estimes avoir
besoin de plus, priorise-les par importance décroissante.
```

### ⚠️ Piège n°3 : Non-utilisation des faits dans la réponse

**Erreur :** La réponse finale ignore les faits générés et revient à une réponse directe et non structurée.

```
❌ Faits générés : A, B, C
   Réponse : « Voici la réponse... » (sans référence à A, B ou C)
```

**✅ Correction :** Contraignez le lien entre faits et réponse :

```
Dans ta réponse finale, cite chaque fait entre crochets [Fait n°X]
et montre explicitement comment tu l'utilises pour ta conclusion.
```

### ⚠️ Piège n°4 : Confusion avec le RAG (Retrieval-Augmented Generation)

**Erreur :** Generated Knowledge **n'est pas** une alternative au RAG. Le RAG récupère des documents externes ; Generated Knowledge extrait de la mémoire paramétrique du modèle. Les deux peuvent être combinés mais ne sont pas interchangeables.

---

## 7. Checklist d'utilisation

### Avant d'utiliser Generated Knowledge

- [ ] La question nécessite-t-elle une exploration structurée des connaissances ?
- [ ] Le sujet est-il suffisamment complexe pour justifier la double phase ?
- [ ] Le temps de réponse (double appel) est-il acceptable ?
- [ ] Le modèle utilisé est-il capable de suivre des instructions en deux étapes ?

### Pendant la génération des connaissances

- [ ] Les faits sont-ous catégorisés (étude, tendance, statistique, opinion) ?
- [ ] Chaque fait comporte-t-il un niveau de confiance explicite ?
- [ ] Le nombre de faits est-il limité (5-7 maximum) ?
- [ ] Les faits sont-ils réellement pertinents par rapport à la question ?

### Pendant le raisonnement et la réponse

- [ ] Chaque assertion de la réponse est-elle soutenue par un fait généré ?
- [ ] Les faits sont-ils cités explicitement dans la réponse ?
- [ ] Les limites et incertitudes sont-elles mentionnées ?
- [ ] La réponse finale apporte-t-elle une valeur ajoutée par rapport à une réponse directe ?

### Après la réponse

- [ ] La qualité de la réponse est-elle objectivement meilleure qu'avec une méthode directe ?
- [ ] Les hallucinations ont-elles été réduites ?
- [ ] La structure (faits → raisonnement → réponse) est-elle claire pour l'utilisateur final ?

---

## 8. Variantes avancées

| Variante | Description | Quand l'utiliser |
|----------|-------------|-----------------|
| Generated Knowledge + RAG | Combiner faits générés + documents récupérés | Sources externes + mémoire du modèle |
| Generated Knowledge multi-tour | Générer des faits, les valider, puis générer des faits complémentaires | Sujets très complexes |
| Generated Knowledge collaboratif | Plusieurs agents génèrent des faits indépendamment, puis les fusionnent | Réduction des biais |
| Generated Knowledge avec débat | Générer des faits pour et contre une position, puis trancher | Questions controversées |

---

> **Note importante :** Generated Knowledge est une méthode puissante mais coûteuse en tokens. Réservez-la aux questions qui bénéficient réellement d'une exploration structurée des connaissances. Pour les questions simples, une réponse directe est plus efficace.

