---
name: instructional-design
description: "Use when designing learning experiences, training materials, courses, or tutorials — learning objectives, Bloom's taxonomy, assessment design, and curriculum planning."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [instructional-design, pedagogy, curriculum, training, e-learning, bloom-taxonomy]
    related_skills: [technical-writing, content-design, markdown-systems]
---

# Instructional Design

## Overview

L'instructional design (conception pédagogique) est la discipline qui transforme un savoir complexe en expérience d'apprentissage progressive et mesurable. Ce skill couvre la modélisation des objectifs pédagogiques, la structuration des contenus, la conception d'évaluations et les stratégies d'enseignement technique.

## When to Use

- L'utilisateur demande de créer un cours, tutoriel, formation ou atelier
- Vous devez structurer une progression pédagogique en plusieurs modules
- Conception d'évaluations (quiz, exercices, projets pratiques)
- Analyse et amélioration d'un contenu de formation existant
- Définition d'objectifs d'apprentissage mesurables

## Taxonomie des Objectifs Pédagogiques

### Bloom Révisé (Anderson & Krathwohl)

| Niveau | Verbes d'action | Exemple (devOps) |
|--------|----------------|------------------|
| **Créer** | Concevoir, développer, planifier, produire | Concevoir une pipeline CI/CD complète |
| **Évaluer** | Critiquer, justifier, évaluer, prioriser | Auditer la sécurité d'un déploiement |
| **Analyser** | Comparer, différencier, organiser, attribuer | Analyser les logs d'incident |
| **Appliquer** | Exécuter, implémenter, utiliser, démontrer | Configurer un load balancer |
| **Comprendre** | Expliquer, interpréter, résumer, paraphraser | Expliquer le fonctionnement d'un reverse proxy |
| **Mémoriser** | Lister, nommer, identifier, décrire | Lister les méthodes HTTP |

### Rédaction d'un Objectif SMART

**Format :** `[Verbe d'action] + [Condition] + [Critère de réussite]`

Exemples :
- Bad : « Comprendre Docker »
- SMART : « À l'issue du module, l'apprenant **construit** un Dockerfile multi-stage qui **produit une image < 100MB et passe le security scan** sans vulnérabilité critique »

## Structure de Cours

### Les 4 Phases Gagnantes (Gagné)

1. **Gain l'attention** — Problème réel, démonstration, question provocatrice
2. **Informer l'objectif** — « À la fin de ce module, vous serez capable de... »
3. **Stimuler le rappel** — Lien avec les prérequis, concepts déjà vus
4. **Présenter le contenu** — Théorie + Démo + Pratique

### Progression Module Type

```
Module N : Titre (durée estimée)
├── Objectifs (2-4 max)
├── Prérequis (liens vers modules précédents)
├── Contenu
│   ├── Concept (10-15 min) — Théorie minimale, pourquoi ?
│   ├── Démonstration (10-15 min) — En contexte réel
│   ├── Exercice guidé (15-20 min) — Pas-à-pas avec corrigé
│   └── Exercice autonome (20-30 min) — Sans corrigé, mais avec critères de succès
├── Vérification (quiz 5 questions, ou livrable)
└── Ressources complémentaires
```

### Loi de Miller : 7 ± 2

Un module ne devrait pas contenir plus de 5-9 concepts nouveaux. Au-delà, fractionner en sous-modules.

## Types de Contenu Pédagogique

| Type | Usage | Durée | Supports |
|------|-------|-------|----------|
| **Tutoriel** | Apprentissage guidé pas-à-pas | 15-30 min | Texte, screenshots, vidéo |
| **Workshop** | Mise en pratique supervisée | 1-3h | Code, environnement, exercices |
| **Talk/Conférence** | Présentation conceptuelle | 20-45 min | Slides, démo en direct |
| **Documentation de référence** | Consultation après formation | Page unique | API docs, commandes, exemples |
| **Projet** | Application intégrée | 1-5 jours | Spécification, repo vierge, critères |

## Évaluations

### Quiz à Choix Multiples — Règles

1. **Questions sur l'application, pas la mémorisation** — « Que se passe-t-il si X ? », pas « Qu'est-ce que X ? »
2. **3-4 options, dont une clairement correcte et les autres plausibles**
3. **Éviter « toutes les réponses ci-dessus » et « aucune de ces réponses »**
4. **Feedback pour bonne ET mauvaise réponse** — pourquoi cette réponse est correcte/incorrecte

### Exercices Pratiques — Critères de Succès

Chaque exercice doit avoir des critères objectifs :
- « Le script s'exécute sans erreur avec fichier d'entrée A et produit fichier B » (pas « Faire un script qui fonctionne »)
- « Le temps de réponse passe sous 200ms » (pas « Optimiser l'API »)
- « Tous les tests verts : `pytest -v` » (pas « Tester le code »)

## Formats de Livrables

### Fiche de Module

```yaml
module:
  id: docker-03
  title: "Multi-stage Builds"
  duration: "45 min"
  prerequisites: ["docker-01", "docker-02"]
  objectives:
    - "Construire un Dockerfile multi-stage optimisé"
    - "Réduire la taille d'image de 70% en moyenne"
  assessment:
    type: "exercise"
    criteria: "Le build produit une image < 50MB avec l'application fonctionnelle"
  tags: [docker, build, optimisation, devops]
```

### Plan de Leçon

```
| Durée | Activité | Format | Matériel |
|-------|----------|--------|----------|
| 5 min | Icebreaker : pourquoi les builds sont lents | Discussion | Miro board |
| 10 min | Concept : phases de build vs runtime | Présentation | Slides 3-8 |
| 10 min | Demo : refacto d'un Dockerfile | Live coding | Terminal |
| 15 min | Exercice : optimiser votre Dockerfile | Individuel | Repo starter |
| 5 min | Debrief et Q&A | Discussion | Corrigé |
```

## Common Pitfalls

1. **Objectifs non mesurables.** « Comprendre Kubernetes » est inverifiable. « Déployer une app sur un cluster Kind avec Helm » se mesure.
2. **Surcharge cognitive.** Plus de 5-7 nouveaux concepts par heure = perte d'attention. Prioriser et fractionner.
3. **Pas de pratique.** Un cours sans exercice n'est pas un cours, c'est une conférence. Ratio recommandé : 40% théorie / 60% pratique.
4. **Feedback absent.** Sans dire pourquoi une réponse est fausse, l'apprenant reproduit l'erreur. Chaque question/exercice a un feedback.
5. **Prérequis non vérifiés.** Commencer un module sans vérifier que l'apprenant a les bases crée de la frustration.

## Outils Recommandés

| Besoin | Outil |
|--------|-------|
| Authoring cours | Obsidian (MD), iSpring, Articulate |
| Quiz interactifs | H5P, Quizlet, Google Forms |
| Plateforme LMS | Moodle, Canvas, Thinkific |
| Diagrammes pédagogiques | Excalidraw, Mermaid |
| Vidéo tutoriel | OBS, Loom |
| Exercices code | GitHub Classroom, CodeSandbox |

## Verification Checklist

- [ ] Objectifs SMART : verbe action + condition + critère mesurable
- [ ] Progression cohérente (prérequis → concept → pratique → évaluation)
- [ ] Ratio théorie/pratique ≥ 40/60
- [ ] Chaque exercice a des critères de succès objectifs
- [ ] Feedback prévu pour chaque évaluation
- [ ] Pas plus de 7 concepts nouveaux par module
- [ ] Durée réaliste (inclut le temps de pratique, pas que la présentation)