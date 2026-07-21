---
name: risk-management
description: Risk management projet — ISO 31000, identification, analyse qualitative/quantitative, mitigation, monitoring, Risk Register, Monte Carlo, RCA.
category: productivity
---

# Risk Management — Référence Complète

## Contexte & Déclencheur
Utiliser quand l'utilisateur demande : gestion des risques, analyse de risques, Risk Register, mitigation, ISO 31000, SWOT, Monte Carlo, cause racine, plan de contingence.

---

## 1. Cadre Normatif — ISO 31000:2018

### Principes
1. Intégré au processus de management
2. Structuré et exhaustif
3. Personnalisé selon le contexte
4. Inclusif (parties prenantes)
5. Dynamique et itératif
6. Amélioration continue

### Processus ISO 31000
```
Contexte (interne/externe) 
    → Identification des Risques
        → Analyse (qualitative / quantitative)
            → Évaluation (criticité)
                → Traitement (éviter/transférer/réduire/accepter)
                    → Monitoring & Revue
                        → Communication & Consultation
                            ← Retour au contexte
```

---

## 2. Identification des Risques

### 2.1 Catégories

| Catégorie | Exemples |
|-----------|----------|
| **Technique** | Stack inadaptée, dette technique, performance |
| **Planning** | Estimation irréaliste, dépendances critiques |
| **Ressources** | Turnover, manque compétences, indisponibilité |
| **Financier** | Budget insuffisant, change FX, inflation |
| **Externe** | Régulation, fournisseur, marché, géopolitique |
| **Sécurité** | Brèche data, ransomware, conformité RGPD |
| **Opérationnel** | Processus défaillant, panne SI |
| **Stratégique** | Mauvais alignement business, obsolescence |

### 2.2 Techniques d'Identification

| Technique | Quand | Format |
|-----------|-------|--------|
| **Brainstorming** | Début projet, revue | Session 1h, post-its |
| **SWOT** | Analyse stratégique | Forces/Faiblesses/Opportunités/Menaces |
| **Checklist** | Standard | Listes par catégorie |
| **Delphi** | Expert consensus | Questionnaire anonyme multi-tours |
| **What-If** | Scénarios | "Que se passe-t-il si...?" |
| **HazOp** | Process critique | Guidewords + déviations |
| **Interview** | Stakeholder 1:1 | Questions semi-structurées |

---

## 3. Analyse Qualitative

### 3.1 Matrice Probabilité × Impact

```
Impact →   Très faible   Faible   Moyen   Élevé   Critique
Probabilité ↓
Très probable       5       10       15       20       25
Probable            4        8       12       16       20
Moyen               3        6        9       12       15
Peu probable        2        4        6        8       10
Très peu probable   1        2        3        4        5

Score: 1-5 = Faible, 6-10 = Moyen, 12-16 = Élevé, 20-25 = Critique
```

### 3.2 Échelle d'Impact

| Impact | Coût | Délai | Qualité |
|--------|------|-------|---------|
| Très faible | < 1% budget | < 1% planning | Détail cosmétique |
| Faible | 1-5% | 1-5% | Mineur, sans conséquence |
| Moyen | 5-10% | 5-10% | Notable, gérable |
| Élevé | 10-20% | 10-20% | Majeur, repoussement |
| Critique | > 20% | > 20% | Projet compromis |

---

## 4. Analyse Quantitative

### 4.1 Monte Carlo Simulation

```python
import numpy as np

def monte_carlo_duration(optimistic, most_likely, pessimistic, n_simulations=10000):
    """Simulation Monte Carlo selon distribution triangulaire."""
    np.random.seed(42)
    durations = np.random.triangular(
        optimistic, most_likely, pessimistic, n_simulations)
    
    p50 = np.percentile(durations, 50)
    p80 = np.percentile(durations, 80)
    p95 = np.percentile(durations, 95)
    
    return {
        "P50": round(p50, 1),
        "P80": round(p80, 1),
        "P95": round(p95, 1),
        "moyenne": round(np.mean(durations), 1),
        "std": round(np.std(durations), 1)
    }

# Exemple : tâche avec estimation 3 points (jours)
result = monte_carlo_duration(3, 5, 12)
print(result)
# → {'P50': 5.8, 'P80': 7.1, 'P95': 9.2, 'moyenne': 6.0, 'std': 1.9}
```

### 4.2 Decision Tree Analysis

```
Scénario A (Investir) — Coût: 100k€
├── Succès (70%) — Gain: 300k€ → Valeur: 300k × 0.7 = 210k€
└── Échec (30%) — Perte: 50k€  → Valeur: -50k × 0.3 = -15k€
    Valeur attendue: 210k - 15k - 100k = 95k€

Scénario B (Attendre) — Coût: 20k€
├── Succès (40%) — Gain: 200k€ → Valeur: 200k × 0.4 = 80k€
└── Échec (60%) — Perte: 10k€  → Valeur: -10k × 0.6 = -6k€
    Valeur attendue: 80k - 6k - 20k = 54k€

→ Scénario A choisi (95k€ > 54k€)
```

### 4.3 Expected Monetary Value (EMV)
```
EMV = Σ (Probabilité_i × Impact_i)
Réserve de contingence = Somme des EMV des risques identifiés
```

---

## 5. Risk Register (Format Standard)

```
┌────────┬────────────┬────────┬──────────┬────────┬────────────┬──────────────┬──────────┬──────────┬───────┐
│ ID     │ Description│ Catégor│ Probabilité│ Impact │ Score      │ Stratégie    │ Proprié  │ Actions  │ Statut│
│        │            │ -orie  │ (1-5)     │ (1-5)  │ (P×I)      │              │ -taire   │          │       │
├────────┼────────────┼────────┼──────────┼────────┼────────────┼──────────────┼──────────┼──────────┼───────┤
│ R-001  │ Turnover   │ RH     │ 3        │ 4      │ 12 (Élevé) │ Réduire      │ PM       │ Plan de │ Actif │
│        │ lead dev   │        │          │        │            │              │          │ retention│       │
└────────┴────────────┴────────┴──────────┴────────┴────────────┴──────────────┴──────────┴──────────┴───────┘
```

---

## 6. Stratégies de Traitement

| Stratégie | Description | Exemple |
|-----------|-------------|---------|
| **Éviter (Avoid)** | Éliminer la cause | Changer de techno risquée |
| **Transférer (Transfer)** | Faire porter par un tiers | Assurance, contrat fixe |
| **Réduire (Mitigate)** | Diminuer probabilité ou impact | Tests + revues + prototypes |
| **Accepter (Accept)** | Conscient mais pas d'action active | Réserve de contingence |
| **Exploiter (Exploit)** | Opportunité positive | Accélérer le planning |

### Plan A vs Plan B
```
Plan A (Mitigation) : Actions préventives pour réduire le risque
Plan B (Contingence) : Actions si le risque se matérialise
Trigger : Événement mesurable qui déclenche le Plan B
```

---

## 7. RCA — Root Cause Analysis

### 7.1 5 Why (5 Pourquoi)
```
Problème : Plantage en production.
1. Pourquoi ? → Le déploiement a échoué
2. Pourquoi ? → Le script de CI a crashé
3. Pourquoi ? → Dépendance non versionnée
4. Pourquoi ? → Pas de lockfile
5. Pourquoi ? → Le template initial n'avait pas de lockfile
→ Cause racine : Process de démarrage de projet incomplet
```

### 7.2 Fishbone (Ishikawa / Diagramme en arêtes de poisson)
```
Catégories standard : Méthode, Machine, Matériel, Main-d'œuvre, Milieu, Mesure

           Méthode          Machine        Matériel
              \               |              /
               \              |             /
                ──────────◆ Problème ──────
               /              |             \
              /               |              \
         Main-d'œuvre      Milieu         Mesure
```

### 7.3 Arbre de Défaillance (FTA)
```
Événement sommet : Livraison en retard
    ├── Estimations trop optimistes
    │   ├── Manque de données historiques
    │   └── Pression commerciale
    ├── Dépendance externe bloquée
    │   ├── Fournisseur en retard
    │   └── API non documentée
    └── Turnover dans l'équipe
        └── Conditions de travail
```

---

## 8. Monitoring & Reporting

### 8.1 Risk Review Cadence
```
- Hebdomadaire : Top 5 risques, nouvelles occurrences
- Mensuel : Mise à jour du Risk Register, revue des actions
- Trimestriel : Réévaluation complète, tendances
- Projet close : Leçons apprises risques
```

### 8.2 Risk Burndown Chart
```python
# Visualisation de la réduction des risques dans le temps
import matplotlib.pyplot as plt

semaines = [1, 2, 3, 4, 5, 6, 7, 8]
risques_critiques = [8, 8, 7, 5, 4, 3, 2, 1]
risques_eleves = [12, 11, 10, 9, 8, 6, 5, 4]

plt.plot(semaines, risques_critiques, 'r-', label='Critiques')
plt.plot(semaines, risques_eleves, 'y-', label='Élevés')
plt.xlabel('Semaines')
plt.ylabel('Nombre de risques')
plt.legend()
```

### 8.3 Heatmap (visualisation)
```
Impact → 
Prob ↓   1       2       3       4       5
5        [M]     [M]     [H]     [C]     [C]
4        [F]     [M]     [H]     [H]     [C]
3        [F]     [M]     [M]     [H]     [H]
2        [F]     [F]     [M]     [M]     [H]
1        [F]     [F]     [F]     [M]     [M]

Légende: F=Faible, M=Moyen, H=Élevé, C=Critique
```

---

## 9. Risques Agile Spécifiques

| Risque Agile | Mitigation |
|-------------|-----------|
| **Scope creep via backlog infini** | WIP limit, time-box |
| **Vélocité non convergente** | Pas de données historiques → starter velocity |
| **Technical debt** | 20% capacité allouée refacto |
| **PO absent** | Backup PO, décisions par comité |
| **Estimation game** | Story points biaisés → calibrer |
| **Burn-out** | Rythme soutenable, rétro bien-être |

---

## 10. Outils de Risk Management

| Outil | Fonctionnalités | Prix |
|-------|----------------|------|
| **Jira + Risk Register plugin** | Matrice, heatmap, workflow risques | Plugin $ |
| **Notion** | DB relation risques → actions | Gratuit |
| **Risk Register Excel** | Template standard | Gratuit |
| **@Risk (Palisade)** | Monte Carlo avancé | $1k |
| **Spider Impact** | Risk management complet | $50/an |
| **RiskyProject** | Schedule risk analysis | $2k |

---

## 11. Pièges

| Piège | Symptôme | Correction |
|-------|----------|-----------|
| **Risk Register = exercice unique** | Pas mis à jour après J1 | Révision hebdomadaire |
| **Biais d'optimisme** | Risques sous-estimés | Utiliser des données historiques |
| **Trop de risques** | On ne voit plus les critiques | Top 10 règle |
| **Propriétaire passif** | Actions jamais faites | Risk Review obligatoire |
| **Confondre risque et problème** | Risque = futur, Problème = présent | Catégoriser |

---

## 12. Références

- **ISO 31000:2018** — Management du risque
- **PMBOK Guide 7th Ed.** — Chapitre Risk
- **NIST SP 800-30** — Guide for conducting risk assessments
- **Douglas Hubbard — The Failure of Risk Management**
- **Project Risk Coach** — projectriskcoach.com
