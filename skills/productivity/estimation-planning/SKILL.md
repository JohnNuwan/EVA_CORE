---
name: estimation-planning
description: Estimation projet — techniques (PERT, 3-points, Planning Poker, Wideband Delphi, Function Points), planification, buffers, concurrent engineering, Rolling Wave.
category: productivity
---

# Estimation & Planification — Référence Complète

## Contexte & Déclencheur
Utiliser quand l'utilisateur demande : estimation projet, planification, PERT, 3-points, Planning Poker, Wideband Delphi, Function Points, Rolling Wave, buffer management, CPM, Critical Chain.

---

## 1. Pourquoi l'Estimation Échoue

### Biais Cognitifs

| Biais | Description | Correction |
|-------|-------------|-----------|
| **Optimisme** | Sous-estimation systématique | Utiliser des données historiques |
| **Ancrage** | 1er chiffre proposé influence tout | Estimation indépendante d'abord |
| **Planning Fallacy** | On sous-estime même en connaissant le biais | Référence Class (similar projects) |
| **Confirmation** | On cherche des preuves pour son estimation | Pre-mortem + déviations |
| **Hofstadter** | Ça prend toujours plus de temps que prévu, même en incluant cette loi | Buffer de 50% |

### Loi de Hofstadter
> « Il faut toujours plus de temps que prévu, même en tenant compte de la loi de Hofstadter. »

---

## 2. Techniques d'Estimation

### 2.1 Estimation à 3 Points (PERT)

| Terme | Description |
|-------|-------------|
| **O** (Optimiste) | Tout se passe parfaitement |
| **M** (Très probable) | Estimation réaliste |
| **P** (Pessimiste) | Tout va mal |

**Formules PERT :**
```
Durée estimée (E) = (O + 4M + P) / 6
Écart-type (σ)    = (P - O) / 6
Variance (σ²)     = ((P - O) / 6)²
```

**Exemple :**
```
O = 3j, M = 5j, P = 12j
E = (3 + 20 + 12) / 6 = 5.8j
σ = (12 - 3) / 6 = 1.5j

→ 68% de chance de finir entre 4.3j et 7.3j (1σ)
→ 95% de chance de finir entre 2.8j et 8.8j (2σ)
→ 99.7% de chance de finir entre 1.3j et 10.3j (3σ)
```

### 2.2 Wideband Delphi

**Processus :**
1. Kick-off : présentation du scope
2. Estimation individuelle (anonyme)
3. Compilation et restitution
4. Discussion des écarts
5. Nouveau tour d'estimation
6. Convergence (ou rounds supplémentaires)

**Règles :**
- 3-7 experts
- Anonyme (évite l'influence hiérarchique)
- Round 1 : chiffre seul
- Round 2 : discussion + nouveau chiffre
- Round 3 : convergence forcée ou médiane

### 2.3 Planning Poker (Scrum)

| Cartes Fibonacci | Signification |
|-----------------|---------------|
| 0 | Déjà fait, trivial |
| 1 | Très simple |
| 2-3 | Simple |
| 5-8 | Complexité moyenne |
| 13-21 | Complexe |
| 40-100 | Trop gros → découper |
| ∞ | Je ne sais pas |
|  ? | Je ne comprends pas |

**Règles :**
- Tous votent simultanément (révélées ensemble)
- Écart > 2x → discuter et revoter
- Durée max : 60s par item (si pas de consensus)
- Jamais d'estimation > 1h

### 2.4 Function Points (Albrecht)

| Élément | Poids | Description |
|---------|-------|-------------|
| **Entrées externes (EI)** | 3-6 | Écran/formulaire d'entrée |
| **Sorties externes (EO)** | 4-7 | Rapport, interface |
| **Requêtes externes (EQ)** | 3-6 | Recherche, extraction |
| **Fichiers internes (ILF)** | 7-15 | Fichier/table logique |
| **Fichiers externes (EIF)** | 5-10 | Interface fichier externe |

```
FP = Σ (Éléments × Poids × Facteur d'ajustement)
Facteur d'ajustement = 0.65 + 0.01 × Σ(14 facteurs GSC)
```

### 2.5 Story Points (Relative Estimation)

**Calibration :**
```
Story Points → Heures (approximatif, varie selon l'équipe)
1 SP  = 2-4h
2 SP  = 4-8h
3 SP  = 1-2j
5 SP  = 2-3j
8 SP  = 3-5j
13 SP = 1-2 semaines → découper
```

**Règle :** Jamais de Story Points > 13 sans découpage.

---

## 3. Planification

### 3.1 Work Breakdown Structure (WBS)

```
Projet (Niveau 1)
├── Phase 1 : Initiation (Niveau 2)
│   ├── 1.1 Analyse des besoins (Niveau 3)
│   ├── 1.2 Spécifications (Niveau 3)
│   └── 1.3 Validation (Niveau 3)
├── Phase 2 : Développement
│   ├── 2.1 Backend
│   │   ├── 2.1.1 API Auth
│   │   ├── 2.1.2 API Core
│   │   └── 2.1.3 Base de données
│   ├── 2.2 Frontend
│   └── 2.3 Tests
└── Phase 3 : Déploiement
```

**Règle des 100% :** Le WBS couvre 100% du scope, et chaque niveau = 100% du niveau parent.

**Règle 8/80 :** Chaque élément entre 8h et 80h de travail.

### 3.2 CPM — Critical Path Method

```
Tâche   Durée   Prédécesseurs
A       5j      -
B       7j      A
C       3j      A
D       4j      B
E       6j      C, D
F       2j      E

Chemin critique : A → B → D → E → F = 5+7+4+6+2 = 24j
Marge totale C : 24 - (5+3+6+2) = 8j
```

**Formules :**
```
ES (Early Start) = max(EF des prédécesseurs)
EF (Early Finish) = ES + Durée
LS (Late Start) = LF - Durée
LF (Late Finish) = min(LS des successeurs)
Slack = LS - ES = LF - EF
```

### 3.3 Critical Chain (Goldratt)

**Principes :**
1. Pas de marges individuelles → Buffer central partagé
2. Buffer de projet = 50% de la durée estimée
3. Pas de multitasking
4. Ressources critiques = goulot

**Buffer Management :**
```
Vert   (< 33% buffer consommé) : OK
Jaune  (33-66%) : Alerte, commencer mitigation
Rouge  (> 66%) : Action immédiate requise
```

### 3.4 Rolling Wave Planning

```
Horizon 1 (Sprint +1) : Détaillé (Story Points)
Horizon 2 (Sprint +2-3) : Thèmes (Epics)
Horizon 3 (Sprint +4-6) : Grandes lignes (Features)
Horizon 4 (Release) : Vision (Objectifs)
```

---

## 4. Buffer Management

### 4.1 Types de Buffers

| Buffer | Usage | Taille recommandée |
|--------|-------|--------------------|
| **Projet** | Fin de projet | 50% de la durée totale estimée |
| **Nourriture** | Entre chaînes critiques | 50% de la chaîne |
| **Capacité** | Ressource partagée | Variable |
| **Contingence** | Risques identifiés | EMV des risques |

### 4.2 Goldratt's Buffer Sizing

```
Buffer = 50% × (Somme des durées des tâches du chemin critique)
```

**Exemple :** Chemin critique = 60j → Buffer = 30j → Durée totale = 75j planifiés (60j travail + 15j buffer à 50%)

---

## 5. Planification Agile

### 5.1 Release Planning
```
Release : 3 mois, 6 sprints
Vélocité moyenne : 35 SP/sprint
Capacité estimée : 35 × 6 × 0.8 (vélocité réelle) = 168 SP
Priorisation : Top 40% du backlog = 200 SP → trop
Option : Réduire scope ou ajouter sprint
```

### 5.2 Sprint Planning
```
Capacité = (∑ disponibilité membres) × 0.6 (focus factor)
Focus factor = 60% (réunions, reviews, bugs, support)

Exemple : 5 devs × 10j × 0.6 = 30j-homme disponibles
Vélocité attendue : 30 SP (si 1 SP ≈ 1j-homme en moyenne)
```

### 5.3 Velocity Tracking
```python
def forecast_velocity(velocity_history, n_sprints):
    """Prévision de vélocité avec intervalle de confiance."""
    import numpy as np
    v = np.array(velocity_history)
    avg = np.mean(v)
    std = np.std(v)
    
    # P50
    p50 = avg * n_sprints
    # P85 (moins risqué)
    p85 = (avg - std) * n_sprints
    # P95 (très conservateur)
    p95 = (avg - 1.645 * std) * n_sprints
    
    return {"P50": round(p50), "P85": round(p85), "P95": round(p95)}

# Exemple : 6 sprints, vélocités [35, 28, 42, 33, 30, 38]
print(forecast_velocity([35, 28, 42, 33, 30, 38], 6))
# → P50: 206, P85: 178, P95: 157
```

---

## 6. Référence Class (Estimation par Analogie)

**Principe :** Comparer le projet à des projets similaires déjà réalisés.

```
Projet actuel : Application web, 15 écrans, 3 rôles, 5 APIs
Projet référence : Application web, 12 écrans, 2 rôles, 4 APIs → 120j
Ratio : 15/12 × 3/2 × 5/4 = 1.25 × 1.5 × 1.25 = 2.34
Estimation : 120j × 2.34 = 281j
```

---

## 7. Outils de Planification

| Outil | Fonctionnalités | Prix |
|-------|----------------|------|
| **Microsoft Project** | CPM, PERT, Gantt, ressources | $30/mois |
| **Jira + Portfolio** | Planification hiérarchique | $15/user/mois |
| **Linear** | Cycle time, analytics | $8/user/mois |
| **Smartsheet** | Gantt, dépendances, rapports | $14/user/mois |
| **GanttProject** | Open source, CPM | Gratuit |
| **OpenProject** | Gantt, Agile, budgets | Gratuit/€7.95 |

---

## 8. Techniques de Découpage

### 8.1 User Story Splitting
```
- Par workflow : Login → Profile → Settings
- Par opération CRUD : Create / Read / Update / Delete
- Par interface : Web / Mobile / API
- Par règle métier : Standard / Exception
- Par données : Minimal / Complet
- Par spike : Investigation → Implémentation
```

### 8.2 INVEST (Bonnes User Stories)
```
I — Independent (Indépendante)
N — Negotiable (Négociable)
V — Valuable (Valeur métier)
E — Estimable (Estimable)
S — Small (Petite)
T — Testable (Testable)
```

---

## 9. Pièges

| Piège | Correction |
|-------|-----------|
| **Estimer en heures avec des story points** | Les SP sont relatifs, pas horaires |
| **Planner en détail > 3 mois** | Rolling Wave uniquement |
| **Ignorer la capacité réelle** | Compter réunions, support, bugs |
| **Pas de buffer** | Goldratt : 50% de buffer projet |
| **Estimation = engagement** | L'estimation est une prévision, pas une promesse |
| **Multi-tasking** | Réduire le WIP, focus sur une tâche |

---

## 10. Références

- **Steve McConnell — Software Estimation: Demystifying the Black Art**
- **Eliyahu Goldratt — Critical Chain**
- **Mike Cohn — Agile Estimating and Planning**
- **PMBOK 7th Ed.** — Planning Process Group
- **Tom DeMarco — Waltzing with Bears** (Risk Management)