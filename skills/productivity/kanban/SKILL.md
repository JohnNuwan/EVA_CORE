---
name: kanban
description: Méthode Kanban — principes, pratiques, métriques (CFD, cycle time, WIP), banboards, implémentation, Kanban vs Scrum.
category: productivity
---

# Kanban — Référence Complète

## Contexte & Déclencheur
Utiliser quand l'utilisateur demande : Kanban, flux tiré, WIP, continuous delivery, board Kanban, métriques Kanban, CFD, Kanban vs Scrum, méthode Kanban.

---

## 1. Origine & Principes Fondamentaux

La méthode Kanban est née chez Toyota dans les années 1940 (Taiichi Ohno) comme système de flux tiré (pull) pour le juste-à-temps.

### 6 Règles Implicites (Toyota)
1. Le processus aval retire ce dont il a besoin (tirage)
2. Le processus amont produit juste la quantité retirée
3. Rien n'est produit sans kanban
4. Chaque article a un kanban attaché
5. Les défauts et quantités incorrectes ne passent pas
6. Le nombre de kanban est réduit pour exposer les problèmes

### 4 Principes Fondamentaux (David J. Anderson)
1. **Commencer là où vous êtes** — pas de transformation radicale
2. **Changer par accord** — les changements sont incrémentaux et respectueux
3. **Encourager l'initiative** — n'interdisez pas la prise de risque
4. **Leadership à tous les niveaux** — pas hiérarchique, distribué

---

## 2. Les 6 Pratiques Clés

| Pratique | Description | Impact |
|----------|-------------|--------|
| **1. Visualiser le flux** | Carte du workflow (colonnes), cartes de travail | Transparence |
| **2. Limiter le WIP (Work In Progress)** | Nombre max d'items en cours par colonne | Fluidité |
| **3. Gérer le flux** | Surveiller, mesurer, optimiser | Prédictibilité |
| **4. Rendre les politiques explicites** | Définition de "prêt", critères de passage | Alignement |
| **5. Boucles de feedback** | Revues, rétrospectives, standups | Amélioration |
| **6. Améliorer collaborativement** | Kaizen, expérimentations | Culture |

---

## 3. Conception du Board Kanban

### Colonnes Types
```
[Backlog] → [À faire] → [En cours] → [Review] → [Test] → [Terminé]
   WIP:∞       WIP:∞      WIP:3       WIP:2      WIP:2       WIP:∞
```

### Politiques Explicites (exemple "Prêt")

**Definition of Ready (DoR) — pour entrer dans "À faire"**
- [ ] Titre et description clairs
- [ ] Critères d'acceptation définis
- [ ] Dépendances identifiées et résolues
- [ ] Lié à un objectif (epic/OKR)

**Definition of Done (DoD) — pour sortir de "Terminé"**
- [ ] Code livré en production (ou validé PO)
- [ ] Documentation mise à jour
- [ ] Tests automatisés passent
- [ ] Observabilité configurée

### Swimlanes
- **Par priorité :** Critique / Haute / Normale / Basse
- **Par type :** Feature / Bug / Technical Debt / Spike
- **Par équipe :** Team A / Team B / Dépendance externe

---

## 4. Métriques Kanban

### 4.1 Cycle Time & Lead Time
```
Lead Time   = demande → livraison (vue client)
Cycle Time  = début travail → livraison (vue équipe)
```

**Interpretation :**
- Lead Time >> Cycle Time → attente excessive entre la demande et le début
- Cycle Time volatile → WIP trop élevé ou goulots

### 4.2 WIP (Work In Progress)
```
WIP idéal ≈ (temps de cycle cible / temps de développement moyen) × taille équipe
```
Règle empirique : WIP max = 2 × nombre de personnes dans la colonne

### 4.3 Throughput (Débit)
```
Throughput = ∑ items livrés / période
```

### 4.4 CFD (Cumulative Flow Diagram)

**Lecture du CFD :**

| Forme de la bande | Interprétation |
|------------------|---------------|
| Bande large en "En cours" | WIP élevé → goulot |
| Bande qui s'élargit | Taux d'entrée > taux de sortie |
| Bande horizontale | Travail bloqué / arrêté |

**Commande outils :**
```bash
# Exporter les données du board → CSV → graphique
python3 -c "
import matplotlib.pyplot as plt
import pandas as pd
# ... génération CFD
"
```

### 4.5 Distribution du Cycle Time (Histogramme)
- Distribution asymétrique (loi log-normale généralement)
- Médiane plutôt que moyenne
- P80/P95 pour les SLA

### 4.6 Throughput Run Chart
- Points par semaine/mois
- Ligne de tendance (moyenne mobile sur 4-6 périodes)
- Limites de contrôle (± 3σ)

---

## 5. Classes de Service

| Classe | Description | Priorité | Politique |
|--------|-------------|----------|-----------|
| **Standard** | Travail normal (features, bugs) | Selon backlog | FIFO, WIP limité |
| **Expedite** | Urgence critique | Préempte tout | WIP cap à 1, SLA 24h |
| **Fixed Date** | Échéance contractuelle | Anticiper | Buffer, commence tôt |
| **Intangible** | Dette technique, spikes | Slots alloués | 10-20% de capacité |

**Règle d'or :** Si plus de 20% des items sont Expedite, le système est en crise.

---

## 6. Kanban vs Scrum

| Dimension | Scrum | Kanban |
|-----------|-------|--------|
| **Iteration** | Sprints (time-boxés) | Flux continu |
| **Rôles** | PO, SM, Devs | Pas de rôles imposés |
| **WIP** | Implicite (Sprint Backlog) | Explicite |
| **Planning** | Début de sprint (time-box) | Cadence régulière (on demand) |
| **Changement** | Pas en cours de sprint | À tout moment (si capacité) |
| **Métrique clé** | Velocity (Points/Sprint) | Cycle Time, Throughput |
| **Rétro** | Fin de sprint | Continue + événements |
| **Livraison** | Fin de sprint | Continue (CD) |

### Scrumban (mélange)
- **Quand :** Équipes qui passent de Scrum à Kanban, ou maintenance lourde + features
- **Caractéristiques :** Sprint planning allégé, WIP Kanban visible, rétro Scrum
- **Outils :** Board Kanban avec colonne "Sprint" comme time-box

---

## 7. Implémentation Pas à Pas

### Phase 1 — Fondations (J1-J15)
1. Cartographier le workflow actuel (chaque étape)
2. Créer le board physique ou digital (Jira, Notion, Trello, Linear)
3. Ajouter une colonne "Bloqué" — visible, pas caché
4. Mettre un WIP initial (= effectif de la colonne × 2)

### Phase 2 — Mesure (J15-J45)
1. Collecter cycle time et throughput
2. Générer première CFD
3. Identifier le goulot primaire

### Phase 3 — Optimisation (J45+)
1. Réduire WIP au niveau du goulot
2. Ajouter politiques explicites (DoR/DoD)
3. Mettre en place les classes de service
4. Automatiser les métriques (dashboard)

---

## 8. Outils & Dashboards

| Outil | Fonctionnalités Kanban | Prix |
|-------|----------------------|------|
| **Jira** | Boards Scrum/Kanban, CFD natif | $7.50/user/mois |
| **Trello** | Boards simples, Butler automation | Gratuit/Team |
| **Notion** | Kanban database, relations | $10/user/mois |
| **Linear** | Kanban natif, cycle time, analytics | $8/user/mois |
| **LeanKit** | CFD, WIP limits, classes service | $19/user/mois |
| **SwiftKanban** | Analyse prédictive, Monte Carlo | $15/user/mois |

### Automatisation Dashboard
```python
# Exemple : collecte des métriques Kanban via API Jira
# pip install jira-python
from jira import JIRA
jira = JIRA(server="https://...", token_auth="...")
# Requête JQL pour cycle time
issues = jira.search_blocks("project = MONPROJ AND status CHANGED TO 'Done'")
```

---

## 9. Pièges & Correctifs

| Piège | Symptôme | Correction |
|-------|----------|------------|
| **WIP trop élevé** | Cycle time qui augmente | Réduire WIP de 20% |
| **Colonnes floues** | Items stagnent entre étapes | Définir politiques explicites |
| **Pas de limits WIP respectées** | Tout est "en cours" | Blocage automatique par l'outil |
| **Expedite permanent** | Plus de priorité | Service review, réduire le chaos |
| **Mesures sans actions** | Dashboards ignorés | Revue hebdomadaire des métriques |

---

## 10. Références

- **David J. Anderson — Kanban** (Blue Hole Press, 2010)
- **Kanban Maturity Model** (KMM) — 5 niveaux
- **ProKanban.org** — certifications (KMP I/II)
- **LeanKanban University**
- **Donald G. Reinertsen — The Principles of Product Development Flow**
