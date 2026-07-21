---
name: agile-scrum
description: Agile manifesto, Scrum framework complet — rôles, artefacts, événements, scalabilité (SAFe, LeSS, Scrum@Scale), certification, anti-patterns.
category: productivity
---

# Agile & Scrum — Référence Complète

## Contexte & Déclencheur
Utiliser quand l'utilisateur demande : processus Agile, framework Scrum, gestion de sprint, user stories, product backlog, Scrum Master, PO, cérémonies Scrum, scalabilité Agile.

---

## 1. Manifeste Agile (2001)

### 4 Valeurs
| Valeur | Priorité |
|--------|----------|
| Individus et interactions | > processus et outils |
| Logiciel opérationnel | > documentation exhaustive |
| Collaboration client | > négociation contractuelle |
| Adaptation au changement | > suivi d'un plan |

### 12 Principes (résumé opérationnel)
1. Livraison continue de valeur
2. Accueillir le changement même tardif
3. Livrer fréquemment (semaines plutôt que mois)
4. Équipe métier + développeurs — quotidien
5. Équipes motivées, confiance, environnement
6. Conversation en face-à-face (ou visio synchrone)
7. Logiciel fonctionnel = mesure principale de progression
8. Rythme soutenable (pas de burn-out)
9. Attention continue à l'excellence technique
10. Simplicité — art de maximiser le travail non fait
11. Équipes auto-organisées — meilleures architectures
12. Réflexion régulière → ajustement du comportement

---

## 2. Scrum — Le Framework

### Rôles (3 seulement)

| Rôle | Responsabilité | Piège fréquent |
|------|---------------|----------------|
| **Product Owner (PO)** | Maximiser la valeur du produit, gérer le Product Backlog, prioriser, définir la vision | Devenir un "groomer" sans pouvoir décisionnel |
| **Scrum Master (SM)** | Servant-leader, coach, garant du processus, supprime les impediments | Agir comme un chef de projet traditionnel |
| **Developer** | Auto-organisé, cross-fonctionnel, estime et livre | Être traité comme une ressource interchangeable |

**Anti-pattern :** "Scrum Master + PO = même personne" → conflit d'intérêts, pas de garde-fou.

### Artefacts

| Artefact | Contenu | Qui le gère |
|----------|---------|-------------|
| **Product Backlog** | Liste ordonnée de tout ce qui pourrait être nécessaire | PO |
| **Sprint Backlog** | Sélection d'items du Product Backlog + plan de livraison | Developers |
| **Increment** | Somme de tous les items complétés + valeur des incréments précédents | Developers |

**Definition of Done (DoD) :** Engagement partagé sur ce que "fini" signifie. Ex :
- [ ] Code revu et mergé
- [ ] Tests unitaires passent (>80% coverage)
- [ ] Documentation API à jour
- [ ] Déployé en staging validé par PO

### Événements (time-boxés)

| Événement | Durée max (Sprint 2 semaines) | Objectif |
|-----------|-------------------------------|----------|
| Sprint Planning | 4h | Quoi + Comment ce sprint |
| Daily Scrum | 15min | Synchronisation, plan des prochaines 24h |
| Sprint Review | 4h | Inspecter l'incrément, adapter le backlog |
| Sprint Retrospective | 3h | Amélioration continue du processus |

**Anti-pattern Daily :** Rapport de statut au manager. La Daily est pour l'équipe, pas pour le SM.

### Sprint (1-4 semaines, idéal 2)
- **Planning :** Capacity × Velocity → engagement réaliste
- **Exécution :** Tableau, burndown, daily sync
- **Review :** Démo au stakeholder (pas des slides)
- **Retro :** Start / Stop / Continue — actions concrètes

---

## 3. Scalabilité Agile

### SAFe (Scaled Agile Framework)
- **Niveaux :** Team → Program → Large Solution → Portfolio
- **Événements :** PI Planning (8-10 semaines), System Demo, Inspect & Adapt
- **Rôles additionnels :** Release Train Engineer (RTE), Product Management, Solution Management
- **Quand :** 150+ personnes, régulation forte
- **Critique :** Trop lourd pour <50 personnes

### LeSS (Large-Scale Scrum)
- **Principe :** Scrum à l'échelle — un Product Backlog, plusieurs équipes
- **Événements :** Overall Retrospective, Sprint Planning multi-équipe
- **Quand :** 2-8 équipes sur un même produit

### Scrum@Scale
- **Module :** Executive Action Team (EAT), Scrum of Scrums (SoS)
- **MetaScrum :** Tous les PO, priorisation cross-team

---

## 4. Estimation Agile

### Story Points vs Heures
| Story Points | Heures |
|-------------|--------|
| Relatif, pas absolu | Absolu, horloge |
| Stabilité indépendante de la personne | Varie selon le développeur |
| Se stabilise avec la vélocité | Toujours ré-estimé |

### Techniques
- **Planning Poker :** Fibonacci (1,2,3,5,8,13,21,40,100,∞)
- **T-Shirt Sizing :** XS/S/M/L/XL
- **Affinity Mapping :** Tri rapide en clusters
- **Bucket System :** 5-8 seaux par taille

### Vélocité
- Moyenne des 3-5 derniers sprints
- Jamais utilisée comme KPI de performance individuelle
- **Prévision :** `Vélocité_moy × Sprint_restants` — intervalle de confiance

---

## 5. Backlog Grooming (Refinement)

| Fréquence | Durée | Participants |
|-----------|-------|-------------|
| 1×/semaine | 30-60min | PO + Developers (SM facultatif) |

- Détailier les User Stories à venir
- Ajouter des critères d'acceptation
- Estimer (ou ré-estimer)
- Découper les épopées

**User Story Format :**
```
En tant que [rôle],
Je veux [fonctionnalité]
Afin de [bénéfice métier]

Critères d'acceptation :
- [ ] Condition 1
- [ ] Condition 2
```

---

## 6. Outils & Métriques

| Métrique | Formule | Objectif |
|----------|---------|----------|
| Vélocité | ∑ Story Points livrés / Sprint | Planification |
| Burndown | Travail restant vs temps | Visibilité sprint |
| Cycle Time | Date fin - Date début | Lead time |
| Throughput | Items livrés / unité de temps | Débit équipe |
| Escaped Defects | Bugs production / sprint | Qualité |

---

## 7. Anti-Patterns Catalog

| Anti-Pattern | Correction |
|-------------|-----------|
| **Water-Scrum-Fall** | Sprint planning = conception, sprint = implémentation, sprint + 1 = test → briser les silos |
| **ScrumBut** | "On fait Scrum mais sans Daily / sans PO / sans Retro" → ce n'est plus Scrum |
| **Estimation push** | Management impose les points → l'équipe perd l'auto-organisation |
| **Sprint == Deadline** | Un sprint est une boîte de temps, pas une échéance contractuelle |
| **PO absent** | Backlog non priorisé → l'équipe choisit → mauvaises features |

---

## 8. Certifications (2025-2026)

| Certif | Organisme | Public |
|--------|-----------|--------|
| PSM I/II/III | Scrum.org | Scrum Masters |
| CSPO | Scrum Alliance | Product Owners |
| SAFe SPC | Scaled Agile | Coachs SAFe |
| PMI-ACP | PMI | Généralistes |

---

## 9. Références

- **Scrum Guide 2020 :** scrumguides.org
- **State of Agile Report :** stateofagile.com
- **Martin Fowler — Agile :** martinfowler.com/agile
- **Ken Schwaber — Agile Software Development with Scrum**
- **HBR — Agile at Scale**
