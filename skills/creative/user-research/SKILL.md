---
title: Recherche Utilisateur — UX Research & Insights
description: Recherche utilisateur — méthodes qualitatives/quantitatives, entretiens, tests utilisateurs, enquêtes, analytics, personae, cartographie d'expérience, synthèse
category: creative
author: E.V.A
tags: [user-research, ux, entretien, test-utilisateur, enquete, analytics, persona, journey-map, insight]
version: 1.0
---

# Recherche Utilisateur — UX Research & Insights

## Fondamentaux de la Recherche UX

### Cycle de recherche
```
Découvrir → Définir → Développer → Délivrer
    ↓          ↓          ↓           ↓
 Recherche  Synthèse  Prototypage   Tests +
 Générative  +         + Itération   Validation
             Insights
```

### Quand utiliser quelle méthode ?
```yaml
Découverte (Éviter les mauvaises solutions):
  Entretiens contextuels, ethnographie
  → "Quels sont les vrais problèmes ?"

Définition (Cadrer le problème):
  Personae, Journey Map, Problem Statement
  → "Pour qui et quoi exactement ?"

Idéation (Générer des solutions):
  Co-design, card sorting, brainstorming
  → "Quelles sont les options ?"

Validation (Tester les solutions):
  Usability testing, A/B testing, prototypes
  → "Ça marche ? Les utilisateurs comprennent ?"

Suivi (Mesurer l'impact):
  Analytics, satisfaction surveys, CSAT
  → "Est-ce que ça s'améliore ?"
```

## Méthodes Qualitatives

### Entretien Utilisateur

#### Types d'entretien
```yaml
Structuré: Questionnaire fixe, comparable
  → Bon pour : validation, comparaison
  → Durée: 30-45 min

Semi-structuré: Guide de questions + follow-up
  → Bon pour : exploration, compréhension profonde
  → Durée: 45-60 min

Non-structuré: Conversation libre
  → Bon pour : découverte, contexte
  → Durée: 60-90 min

Contextual Inquiry: Observation sur le terrain
  → Bon pour : comprendre le workflow réel
  → Durée: 1-2h
```

#### Guide d'entretien
```yaml
Introduction (5 min):
  - Présentation, objectif, confidentialité
  - Consentement enregistrement
  - "Pas de bonne ou mauvaise réponse"

Contexte (10-15 min):
  - Parlez-moi de votre rôle
  - À quoi ressemble votre journée typique ?
  - Quels outils utilisez-vous actuellement ?

Problème (15-20 min):
  - La dernière fois que vous avez fait X, racontez-moi
  - Qu'est-ce qui vous a frustré ?
  - Si vous pouviez changer une chose...

Solutions (10 min):
  - Que pensez-vous de cette idée ?
  - Qu'est-ce qui vous ferait passer à une nouvelle solution ?

Conclusion (5 min):
  - Qu'auriez-vous aimé que je demande ?
  - Recommandations ?
  - Remerciements
```

#### Techniques d'écoute active
```yaml
- Reformulation: "Si je comprends bien, vous dites que..."
- Silence: Laisser l'utilisateur combler le vide
- "Pouvez-vous m'en dire plus ?" → creuser
- "Qu'est-ce qui vous a fait dire ça ?" → chercher le pourquoi
- Éviter les questions suggestives:
  ❌ "C'était frustrant, non ?"
  ✅ "Comment vous êtes-vous senti ?"
- Éviter les questions fermées:
  ❌ "Avez-vous aimé ?"
  ✅ "Qu'avez-vous pensé de cette fonctionnalité ?"
```

### Tests Utilisateurs (Usability Testing)

#### Protocole
```yaml
Participants: 5 par segment (Nielsen, 2000)
  - 5 trouvent 85% des problèmes
  - 15+ = rendements décroissants

Scénarios: 3-5 par session
  - Basés sur des tâches réelles
  - "Vous voulez acheter X, montrez-moi comment vous feriez"

Mesures quantitatives:
  - Task success rate (oui/non)
  - Time on task (secondes)
  - Error rate (nombre d'erreurs)
  - Clicks to complete

Mesures qualitatives:
  - Satisfaction (SUS, SEQ)
  - Commentaires "pensez à voix haute"
  - Expressions faciales
  - Frustrations
```

#### Méthode "Pensez à voix haute"
```yaml
Instructions: "Dites tout ce qui vous passe par la tête"
  - Ce que vous voyez
  - Ce que vous pensez
  - Ce que vous attendez
  - Ce qui vous surprend

Avantages:
  - Comprendre le raisonnement
  - Identifier les attentes non satisfaites
  - Détecter les incompréhensions

Inconvénients:
  - Ralentit la tâche
  - Peut modifier le comportement
  - Certains participants ont du mal
```

### Tests à distance (Modéré vs Non-modéré)
```yaml
Modéré (via Zoom, Lookback):
  + Richesse des interactions
  + Possibilité de follow-up
  - Plus long à organiser

Non-modéré (UserTesting, Maze):
  + Rapide, scalable
  + Participants représentatifs
  - Pas de follow-up
  - Moins de contexte
```

### Card Sorting
```yaml
Ouvert:
  - Les utilisateurs créent leurs propres catégories
  - Idéal pour : architecture de l'information

Fermé:
  - Catégories prédéfinies
  - Idéal pour : valider une navigation

Résultat:
  - Dendrogramme (similarité entre items)
  - Matrice de similarité
  - Recommandations de catégorisation
```

## Méthodes Quantitatives

### Enquêtes (Surveys)

#### Types de questions
```yaml
Fermée:
  - Échelle de Likert (1-5, 1-7)
  - Choix multiple
  - Oui/Non
  - Classement

Ouverte:
  - "Qu'est-ce qui vous manque ?"
  - "Avez-vous des suggestions ?"

Démographique:
  - Âge, localisation, rôle
  - Expérience avec le produit
```

#### Métriques standard
```yaml
SUS (System Usability Scale):
  10 questions → score 0-100
  Moyenne: 68
  Excellent: >80
  Formule: (sum_odd - 5) + (25 - sum_even) * 2.5

NPS (Net Promoter Score):
  "Recommanderiez-vous X à un collègue ?" (0-10)
  Promoteurs (9-10) - Détracteurs (0-6) = NPS
  Bon: >30, Excellent: >50

CSAT (Customer Satisfaction):
  "À quel point êtes-vous satisfait ?" (1-5)
  % de 4-5
  Bon: >80%

SEQ (Single Ease Question):
  "Cette tâche était..." (1-7, très difficile → très facile)
  Après chaque tâche
```

### Analytics

#### Métriques comportementales
```yaml
Engagement:
  - Sessions / utilisateur / jour
  - Durée moyenne de session
  - Pages vues / session
  - Bounce rate

Conversion:
  - Funnel conversion rate
  - Drop-off points
  - Time to conversion
  - Abandon rate (panier, formulaire)

Rétention:
  - D1, D7, D30 retention
  - Churn rate
  - DAU/MAU ratio
  - Stickiness (DAU/MAU)
```

#### Heatmaps & Click Tracking
```yaml
Click maps:        Où les utilisateurs cliquent
Scroll maps:       Jusqu'où ils scrolent
Move maps:         Où la souris se déplace
Attention maps:    Où les yeux se posent (eye tracking)
```

### A/B Testing
```yaml
Principe: 50% des utilisateurs voient A, 50% voient B
Métrique: Conversion rate, click rate, time on page
Durée: Minimum 1 semaine (inclure week-end)
Significativité: p < 0.05, puissance > 80%

Pièges:
  - Arrêter trop tôt (peeking)
  - Trop de variations (multiplicity)
  - Effet novelty (les utilisateurs cliquent sur le nouveau)
  - Sample size insuffisant
```

## Synthèse & Insights

### Affinity Diagram
```yaml
1. Notes individuelles (post-it, 1 idée par note)
2. Regroupement silencieux (pas de discussion)
3. Nommer les groupes (thèmes)
4. Hiérarchiser (importance, urgence)
5. Insights → "Ah-ha moments"
```

### Personae
```yaml
Structure:
  - Nom, âge, photo (diversité)
  - Rôle, contexte
  - Objectifs (Jobs To Be Done)
  - Points de douleur
  - Comportements
  - Citation représentative

Exemple:
  ---
  Nom: Sophie Martin
  Âge: 34 ans
  Rôle: Responsable marketing
  Contexte: SaaS, équipe de 5, fait ses propres designs
  Objectifs: Créer des visuels rapidement sans designer
  Points de douleur: Outils trop complexes, perte de temps
  Comportements: Utilise Canva, suit des tutos YouTube
  Citation: "Je veux que ça soit beau, mais j'ai pas le temps d'apprendre"
  ---
```

### Journey Map
```yaml
Phases: Découverte → Achat → Utilisation → Support → Renouvellement
Actions: Ce que l'utilisateur fait
Pensées: Ce qu'il pense
Émotions: 😊 😐 😟 (graphique émotionnel)
Pain points: Frustrations
Opportunités: Solutions possibles

Échelle de satisfaction:
  😊 Heureux — 😶 Neutre — 😟 Frustré — 😡 En colère
```

### Empathy Map
```yaml
Dit: Citations directes de l'utilisateur
Fait: Actions observées
Pense: Pensées internes (pas toujours dites)
Ressent: Émotions, frustrations
Pains: Peurs, obstacles, risques
Gains: Désirs, besoins, mesures de succès
```

## Priorisation & Impact

### Matrice Impact / Effort
```yaml
        Effort Faible    |  Effort Élevé
        ────────────────┼───────────────
Impact  | Quick Wins     | Grands Projets
Élevé   | (Faire d'abord) | (Planifier)
        ────────────────┼───────────────
Impact  | Combler       | À éviter
Faible  | (Si rapide)   | (Ne pas faire)
```

### RICE Scoring
```yaml
R = Reach (portée):   Nb d'utilisateurs impactés / mois
I = Impact:           1-5 (faible → massif)
C = Confidence:       20-100% (intuition → data)
E = Effort:           Homme-mois

RICE Score = (R × I × C) / E
```

## Reporting & Communication

### Structure de rapport
```yaml
1. Executive Summary (1 page)
   - Problème, méthode, finding clé, recommandation
2. Méthodologie
   - Participants, durée, contexte
3. Key Findings (3-5 max)
   - Insight + data + citation + recommandation
4. Détail par finding
   - Evidence, screenshots, quotes
5. Recommandations
   - Priorisées, actionnables
6. Annexes
   - Script, questions, données brutes
```

### Présentation orale
```yaml
Rule of 3:
  - 3 findings principaux
  - 3 recommandations
  - 3 slides max si possible

Storytelling:
  - Commencer par le problème humain
  - "Sophie n'arrivait pas à trouver le bouton..."
  - Montrer des extraits vidéo (15-30s)
  - Terminer par "Donc on recommande..."

Pièges:
  - Trop de slides → noyade
  - Pas de recommandations → "et alors ?"
  - Jargon → "les stakeholders ne comprennent pas"
  - Défensif → "les données parlent, pas vous"
```

## Pièges
- ⚠️ Biais de confirmation → chercher ce qui valide vos hypothèses
- ⚠️ Tester avec ses collègues → pas représentatif des vrais utilisateurs
- ⚠️ Questions suggestives → biaise les réponses
- ⚠️ Trop de participants → rendements décroissants après 5
- ⚠️ Pas assez de diversité → manque de perspectives
- ⚠️ Rapports sans action → recherche qui prend la poussière
- ⚠️ Analytics sans qualitative → on sait quoi mais pas pourquoi
- ⚠️ Qualitative sans quantitative → anecdotes, pas de preuve
- ⚠️ Présenter des solutions, pas des problèmes → "les devs veulent le problème, pas la solution"
- ⚠️ Oublier le consentement → RGPD, enregistrement, anonymisation