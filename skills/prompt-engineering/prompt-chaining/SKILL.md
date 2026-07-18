---
name: prompt-method-prompt-chaining
description: "Décomposer une tâche complexe en une séquence de prompts spécialisés dont les sorties s'enchaînent."
version: 2.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, prompt-chaining, biblio-ia, methods, pipeline, orchestration]
    related_skills: [python-pep8, simplify-code, plan, generated-knowledge, delegate_task]
---

# La méthode Prompt Chaining

## Guide de référence pour l'enchaînement structuré de prompts séquentiels

---

## 1. Vue d'ensemble

La méthode **Prompt Chaining** consiste à décomposer une tâche complexe en une **séquence de prompts individuels** connectés en pipeline, où la sortie de chaque étape sert d'entrée — partielle ou totale — à l'étape suivante. Chaque maillon de la chaîne est spécialisé dans une sous-tâche atomique, ce qui permet un contrôle granulaire sur le processus global.

### Principe fondateur

Le cœur de la méthode repose sur le concept de **« Pipeline »** (chaîne de traitement) :

- **Diviser pour régner** : chaque prompt traite une seule responsabilité
- **Contrôle intermédiaire** : possibilité d'inspecter, valider ou corriger chaque sortie avant de passer à l'étape suivante
- **Réduction de charge cognitive** : le modèle n'a pas à gérer l'intégralité de la complexité en un seul tour
- **Traçabilité** : chaque erreur peut être localisée au maillon qui l'a produite

### Architecture conceptuelle

```
Tâche originale (complexe)
       │
       ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    Prompt #1     │────►│    Prompt #2     │────►│    Prompt #3     │
│  Spécialisé A    │     │  Spécialisé B    │     │  Spécialisé C    │
│                  │     │                  │     │                  │
│ Sortie :         │     │ Sortie :         │     │ Sortie :         │
│ Résultat A       │────►│ Résultat B       │────►│ Résultat final   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
       │                        │                        │
       ▼                        ▼                        ▼
  Validation              Validation              Validation
  optionnelle             optionnelle             finale
```

---

## 2. Quand l'utiliser ?

### Cas d'usage recommandés

| Contexte | Description | Priorité |
|----------|-------------|----------|
| Tâches multi-étapes | Génération d'article, analyse de document, rapport structuré | Élevée |
| Contrôle qualité strict | Chaque étape doit être validée avant de passer à la suivante | Élevée |
| Workflows reproductibles | Le pipeline doit être exécuté de façon identique à chaque utilisation | Élevée |
| Débogage de prompts | Isoler quelle étape produit des résultats erronés | Élevée |
| Génération longue forme | Rédaction de livres, rapports, documentation complète | Moyenne |
| Transformation progressive | Nettoyage → Analyse → Synthèse → Présentation | Moyenne |

### Situations à éviter

- **Tâches simples** : une question-réponse directe ne justifie pas une chaîne
- **Besoins de latence minimale** : chaque maillon ajoute un appel API
- **Processus hautement itératifs** : si les étapes s'influencent mutuellement (feedback loops), préférez une méthode non séquentielle
- **Modèles instables** : si le modèle dérive entre les étapes, l'erreur se propage

---

## 3. Procédure pas à pas

### Étape 1 : Analyser la tâche et identifier les sous-tâches

Décomposez la tâche principale en étapes atomiques — chaque étape doit avoir un **objectif unique et mesurable**.

```
Tâche : « Analyser un CV et rédiger une lettre de motivation personnalisée »

Sous-tâches identifiées :
1. Extraire les compétences clés du CV
2. Analyser l'offre d'emploi cible
3. Identifier les correspondances compétences/exigences
4. Rédiger la lettre de motivation
5. Relire et optimiser la lettre
```

### Étape 2 : Définir le contrat d'interface de chaque étape

Pour chaque maillon, spécifiez :

- **Entrée** : ce qu'il reçoit (tâche originale ou sortie de l'étape précédente)
- **Traitement** : instruction précise du prompt
- **Sortie** : format attendu

**Exemple avec la tâche CV → Lettre :**

| Étape | Entrée | Prompt | Sortie |
|-------|--------|--------|--------|
| 1 Extraction | Texte du CV | « Extrais les compétences techniques, soft skills et expériences clés au format JSON » | JSON structuré |
| 2 Analyse offre | Texte de l'offre | « Extrais les exigences obligatoires et optionnelles au format JSON » | JSON structuré |
| 3 Matching | Sorties 1 + 2 | « Identifie les correspondances et lacunes » | Tableau de matching |
| 4 Rédaction | Sortie 3 | « Rédige une lettre de motivation personnalisée » | Lettre complète |
| 5 Relecture | Sortie 4 | « Vérifie le ton, la grammaire, et l'impact » | Version optimisée |

### Étape 3 : Implémenter chaque maillon avec des prompts spécialisés

**Prompt 1 — Extraction CV :**

```json
{
  "role": "system",
  "content": "Tu es un extracteur de compétences. Tu analyses les CV et produis un JSON structuré."
}
{
  "role": "user",
  "content": "Analyse ce CV et extrais au format JSON :\n- compétences_techniques (liste)\n- soft_skills (liste)\n- expériences (liste avec titre, entreprise, durée)\n- formations (liste)\n\nCV :\n{{texte_du_cv}}"
}
```

**Prompt 2 — Analyse offre :**

```
Analyse cette offre d'emploi et extrais au format JSON :
- exigences_obligatoires (liste)
- exigences_optionnelles (liste)
- missions_principales (liste)

Offre :
{{texte_de_l_offre}}
```

**Prompt 3 — Matching :**

```
À partir des données suivantes :

Compétences du candidat : {{sortie_1}}
Exigences de l'offre : {{sortie_2}}

Produis un tableau de matching avec :
| Compétence | Exigence | Correspondance | Écart |
Chaque écart doit être accompagné d'une suggestion de formulation.
```

**Prompt 4 — Rédaction :**

```
En utilisant le tableau de matching ci-dessous, rédige une lettre
de motivation personnalisée de 250-300 mots. Mets en avant les
correspondances et transforme chaque écart en point positif.

{{sortie_3}}
```

**Prompt 5 — Relecture :**

```
Relis cette lettre de motivation et vérifie :
1. Orthographe et grammaire
2. Ton professionnel mais pas trop formel
3. Impact des premières phrases
4. Longueur (250-300 mots)
5. Appel à l'action final

Propose des améliorations si nécessaire.

Lettre : {{sortie_4}}
```

### Étape 4 : Exécuter la chaîne avec validation intermédiaire

Pour chaque étape, avant de passer à la suivante :

1. Vérifiez que la sortie est au format attendu
2. Validez que le contenu est cohérent et complet
3. Corrigez ou relancez l'étape si nécessaire
4. Passez la sortie validée à l'étape suivante

---

## 4. Workflow complet

```
                    ┌────────────────────────────┐
                    │   Tâche complexe initiale   │
                    └───────────┬────────────────┘
                                │
                    ┌───────────▼────────────────┐
                    │  Analyse et décomposition   │
                    │  en sous-tâches atomiques   │
                    └───────────┬────────────────┘
                                │
                    ┌───────────▼────────────────┐
                    │  Définition des contrats    │
                    │  d'interface entrée/sortie  │
                    └───────────┬────────────────┘
                                │
              ┌─────────────────┬──────────────────┐
              │                 │                  │
              ▼                 ▼                  ▼
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
      │  Étape 1     │  │  Étape 2     │  │  Étape N     │
      │  Prompt      │  │  Prompt      │  │  Prompt      │
      └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
             │                 │                 │
             ▼                 ▼                 ▼
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
      │  Validation  │  │  Validation  │  │  Validation  │
      │  intermédiaire│  │  intermédiaire│  │  finale      │
      └──────────────┘  └──────────────┘  └──────────────┘
             │                 │                 │
             └─────────────────┴─────────────────┘
                                │
                    ┌───────────▼────────────────┐
                    │   Résultat final livré      │
                    └────────────────────────────┘
```

---

## 5. Exemples concrets de code et prompts

### Exemple 1 : Pipeline de génération d'article de blog

**Étape 1 : Recherche et plan**
```
Tu es un stratège de contenu. À partir du sujet suivant, génère :
1. Un angle éditorial original
2. Un plan détaillé en 5 sections avec sous-sections
3. 3 mots-clés SEO principaux

Sujet : « L'impact de l'IA générative sur le développement logiciel »

Format : JSON
```

**Étape 2 : Rédaction section par section**
```
Tu es un rédacteur technique. Rédige la section suivante de l'article
en 200-300 mots. Utilise un ton professionnel mais accessible.

Plan : {{sortie_1}}
Section à rédiger : « Les outils d'IA générative pour le code »
Section précédente (si applicable) : {{section_précédente}}
```

**Étape 3 : Assemblage et harmonisation**
```
Tu es un éditeur. Assemble les sections suivantes en un article cohérent.
Assure-toi que :
- La transition entre chaque section est fluide
- Le ton est uniforme
- Il n'y a pas de répétitions
- L'introduction et la conclusion sont percutantes

Sections : {{sortie_2_a}}, {{sortie_2_b}}, {{sortie_2_c}}, ...
```

**Étape 4 : Optimisation SEO**
```
Tu es un expert SEO. Optimise cet article pour le référencement :
- Vérifie la densité des mots-clés (1-2% recommandé)
- Optimise les balises H1, H2, H3
- Ajoute une meta-description de 155 caractères
- Suggère 5 balises

Article : {{sortie_3}}
```

### Exemple 2 : Pipeline de refactoring de code

**Prompt 1 — Analyse de code :**
```
Analyse ce code Python et identifie :
1. Les violations PEP8
2. Les code smells (fonctions trop longues, duplication, etc.)
3. Les problèmes de performance potentiels
4. Les opportunités de refactoring

Code :
```python
{{code_source}}
```

Format : Liste par catégorie
```

**Prompt 2 — Génération du code refactoré :**
```
À partir de l'analyse suivante, génère le code refactoré.

Analyse : {{sortie_1}}

Instructions :
- Corrige toutes les violations PEP8
- Extrais les fonctions trop longues en sous-fonctions
- Élimine la duplication de code
- Ajoute des docstrings
- Maintiens la compatibilité ascendante
```

**Prompt 3 — Revue de code :**
```
Fais une revue de code du refactoring proposé :

Code original : {{code_source}}
Code refactoré : {{sortie_2}}

Vérifie :
1. Le comportement est-il préservé ?
2. Les noms de fonction sont-ils explicites ?
3. La couverture de docstrings est-elle complète ?
4. Y a-t-il des régressions potentielles ?
```

---

## 6. Pièges courants (Pitfalls)

### ⚠️ Piège n°1 : Propagation d'erreur en cascade

**Erreur :** Une erreur produite par un maillon précoce se propage à tous les maillons suivants, dégradant la qualité finale.

```
❌ Étape 1 extrait des compétences erronées
   → Étape 2 match sur des compétences erronées
   → Étape 3 rédige une lettre basée sur un matching faux
   → Résultat : lettre inutilisable, difficile à déboguer
```

**✅ Correction :** Ajoutez des points de validation intermédiaires :

```
Après chaque étape, valide la sortie avant de la transmettre :
- Vérifie le format attendu (JSON, liste, etc.)
- Vérifie la cohérence interne
- Si le score de confiance est < 80%, relance l'étape
- En cas d'échec après 3 tentatives, arrête la chaîne et signale l'erreur
```

### ⚠️ Piège n°2 : Mauvaise granularité des étapes

**Erreur :** Les étapes sont soit trop grossières (un seul prompt pour toute la tâche), soit trop fines (dizaines de micro-étapes).

```
❌ Étape trop large : « Génère tout l'article » → pas de contrôle
❌ Étape trop fine : « Écris la première phrase de l'introduction »
                  → surcharge de tokens et de latence
```

**✅ Correction :** Appliquez la règle des 3 critères :

Une étape a la bonne granularité si :
1. **Atomique** : elle fait une seule chose
2. **Validable** : on peut objectivement juger si elle est réussie
3. **Significative** : sa complexité justifie un appel API (pas une simple transformation)

### ⚠️ Piège n°3 : Perte de contexte entre les étapes

**Erreur :** Les maillons avals de la chaîne manquent d'informations cruciales parce que le contexte se réduit progressivement.

```
❌ Étape 1 reçoit : document entier de 5000 mots
   Étape 2 reçoit : résumé de 500 mots (perte de 90% du contexte)
   Étape 3 reçoit : synthèse du résumé de 100 mots
   → Information critique perdue entre les étapes
```

**✅ Correction :** Utilisez un contexte cumulatif :

- Transmettez **toujours** la tâche originale en plus de la sortie de l'étape précédente
- Ou utilisez une structure comme : `{tâche_originale} + {sortie_étape_précédente}`
- Pour les chaînes longues, prévoyez une étape de « récapitulatif » qui résume l'état

### ⚠️ Piège n°4 : Absence de format de sortie standardisé

**Erreur :** Chaque étape produit un format différent (paragraphe, liste, JSON, XML), forçant l'étape suivante à s'adapter.

**✅ Correction :** Définissez un format de sortie uniforme dès la conception de la chaîne :

```
Toutes les étapes produisent du JSON avec la structure suivante :
{
  "etape": "nom_etape",
  "statut": "succes" | "echec",
  "donnees": { ... },
  "confiance": 0.0-1.0,
  "erreur": "message si échec"
}
```

---

## 7. Checklist d'utilisation

### Conception de la chaîne

- [ ] La tâche a-t-elle été décomposée en étapes atomiques et validables ?
- [ ] Chaque étape a-t-elle un objectif unique et mesurable ?
- [ ] Le nombre d'étapes est-il compris entre 3 et 8 (grande majorité des cas) ?
- [ ] Le contrat d'interface (entrée/sortie) de chaque étape est-il documenté ?
- [ ] Le format de sortie est-il cohérent entre toutes les étapes ?

### Validation intermédiaire

- [ ] Chaque sortie d'étape est-elle validée avant transmission ?
- [ ] Un mécanisme de re-try (max 3 tentatives) est-il prévu ?
- [ ] En cas d'échec persistant, la chaîne s'arrête-t-elle proprement ?
- [ ] Le contexte original est-il préservé tout au long de la chaîne ?

### Exécution et débogage

- [ ] Le temps d'exécution total (N × latence API) est-il acceptable ?
- [ ] Les tokens consommés (cumul des étapes) sont-ils en ligne avec le budget ?
- [ ] Les erreurs sont-elles traçables jusqu'au maillon qui les a produites ?
- [ ] Un mode de débogage (sorties intermédiaires visibles) est-il disponible ?

### Qualité finale

- [ ] Le résultat final est-il supérieur à ce qu'un prompt unique produirait ?
- [ ] La cohérence est-elle maintenue entre les différentes étapes ?
- [ ] Le pipeline est-il reproductible (mêmes entrées → mêmes sorties) ?
- [ ] La chaîne peut-elle être réutilisée pour une tâche similaire ?

---

## 8. Variantes avancées

| Variante | Description | Quand l'utiliser |
|----------|-------------|-----------------|
| Chaîne conditionnelle | Certaines étapes ne sont exécutées que si la sortie précédente répond à un critère | Workflows avec embranchements |
| Chaîne parallèle | Plusieurs branches exécutées en parallèle, fusionnées ensuite | Tâches indépendantes au sein d'un même processus |
| Chaîne avec feedback | La sortie finale peut être réinjectée dans la chaîne pour itération | Amélioration continue (révisions) |
| Chaîne multi-modèle | Différents modèles pour différentes étapes (ex: GPT-4 pour rédaction, GPT-3.5 pour extraction) | Optimisation coût/performance |
| Sous-agent chaining | Chaque maillon est délégué à un sous-agent isolé (via `delegate_task`) | Tâches sensibles nécessitant isolation |

---

> **Note importante :** Prompt Chaining est l'une des méthodes les plus puissantes pour les tâches complexes, mais elle multiplie le coût en tokens (N × coût unitaire). Évaluez systématiquement si le bénéfice en qualité justifie le surcoût par rapport à un prompt unique bien conçu. Pour des pipelines en production, envisagez la mise en cache des sorties intermédiaires.

