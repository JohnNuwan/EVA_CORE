---
name: okrs-team-management
description: OKRs (Objectives & Key Results) — cascade stratégique, KR types, scoring, OKRs vs KPI, team management, leadership styles, motivation, feedback, 1:1, RADAR.
category: productivity
---

# OKRs & Team Management — Référence Complète

## Contexte & Déclencheur
Utiliser quand l'utilisateur demande : OKRs, Key Results, cascade stratégique, management d'équipe, leadership, feedback, 1:1, motivation, RADAR, gestion de conflit, alignment OKR.

---

# Partie 1 : OKRs (Objectives & Key Results)

## 1. Fondamentaux OKR

### Origine
- **Andy Grove (Intel)** — Inventeur du système
- **John Doerr (Kleiner Perkins)** — Introduction chez Google en 1999
- **Livre de référence :** *Measure What Matters* — John Doerr

### Structure

```
Objectif (O) : "Ce que je veux accomplir" — inspirant, qualitatif, ambitieux
├── Key Result 1 (KR1) : Comment mesurer le progrès — quantitatif, mesurable
├── Key Result 2 (KR2) : ...
└── Key Result 3 (KR3) : ...
```

### Règle des 3 pour 1
- **1 Objectif** = 3 ± 1 Key Results
- Pas plus → dilution de l'attention

### Exemple
```
O : Offrir la meilleure expérience de recherche au monde
├── KR1 : Réduire le temps de réponse < 100ms (actuel : 250ms)
├── KR2 : Score satisfaction utilisateur > 90%
└── KR3 : 100% des fonctionnalités supportées en mobile
```

---

## 2. Hiérarchie OKR (Cascade Stratégique)

```
Mission / Vision
    ↓
Objectifs Stratégiques (Company OKRs) — Annuel
    ↓
Objectifs d'Équipe (Team OKRs) — Trimestriel
    ↓
Objectifs Individuels (Personal OKRs) — Trimestriel
    ← Alignement vertical + horizontal →
```

### Alignement Vertical
```
Company O  : Devenir leader du marché en Europe
  KR1      : 50% de part de marché en France
    │
Team O     : Équipe Mobile — #1 sur l'App Store
  KR1      : 4.8+ rating, 100k téléchargements
    │
Personal O : Alice — Optimiser le onboarding iOS
  KR1      : Taux de conversion onboarding > 80%
```

### Alignement Horizontal (Cross-team)
```
Team A (Backend) : API response time < 50ms
Team B (Frontend) : P95 FCP < 2s
Team C (Mobile) : App launch < 3s
→ Tous alignés sur l'Objectif commun "Performance"
```

---

## 3. Types de Key Results

| Type | Description | Exemple |
|------|-------------|---------|
| **Baseline** | Mesurer un état initial | "Établir un NPS de base" |
| **Metric** | Améliorer un KPI existant | "Passer NPS de 40 à 60" |
| **Milestone** | Atteindre un jalon binaire | "Lancer la v3 en production" |
| **Outcome** | Résultat métier | "Générer 100k€ de MRR" |
| **Input** | Mesure d'effort (à éviter seul) | "Publier 10 articles" |

### Good KRs vs Bad KRs
```
❌ KR : "Améliorer le site web" (pas mesurable)
✅ KR : "Augmenter le taux de conversion de 3.5% à 5%"

❌ KR : "Lancer la feature X à temps" (opinion)
✅ KR : "Feature X déployée en production avant le 15 mars"

❌ KR : "Faire de notre mieux" (pas quantifiable)
✅ KR : "P95 satisfaction client > 4.5/5"
```

---

## 4. Scoring OKR

| Type | Cible | Interprétation |
|------|-------|---------------|
| **Atteint** | 1.0 (100%) | Résultat parfait, peut-être pas assez ambitieux |
| **Progres** | 0.6-0.7 (60-70%) | ✅ Résultat attendu (idéal !) |
| **Encourage** | 0.3-0.5 (30-50%) | Progrès significatif mais insuffisant |
| **Échec** | 0.0-0.2 (0-20%) | Objectif raté |

**Règles :**
- **Stretch Goals :** 70% = succès (si atteignable à 100%, pas assez ambitieux)
- **Committed Goals :** 100% attendu (opérationnel, contractuel)
- Jamais de scoring en milieu de trimestre (sauf revue mensuelle)

### Gradient Scoring (Alternative)
```
Rouge (< 30%)  🟥      Rien ou presque accompli
Ambre (30-60%) 🟧      Progrès partiel
Vert (> 60%)   🟩      On track ou en avance
Excellence (100%) 🏆   Key Result dépassé
```

---

## 5. Cycle OKR

### Trimestre Type
```
Semaine 0 (Annuel) : Définir Company OKRs pour l'année
Semaine -2 à -1     : Préparation Team OKRs
Semaine 0           : OKR Kick-off (company all-hands)
Semaine 1-4         : Sprint 1, KR tracking
Semaine 5-8         : Sprint 2, Mid-quarter check-in
Semaine 9-12        : Sprint 3, Final push
Semaine 12-13       : Scoring, rétro, lessons learned
Semaine 13          : Nouveau cycle
```

### Weekly Check-in
```
Project: "Sur la bonne voie ?" (🟢/🟡/🔴)
- 🟢 : KR > 60%, pas de risque
- 🟡 : KR 40-60%, risque identifié
- 🔴 : KR < 40%, help needed

What I did this week:
What I'll do next week:
Blockers:
```

---

## 6. OKRs vs KPIs

| Dimension | OKR | KPI |
|-----------|-----|-----|
| **Nature** | Objectif ambitieux | Indicateur de santé |
| **Période** | Trimestriel | Continu |
| **Échec** | OK (si stretch goal) | Alerte |
| **Focus** | Changement | Maintien |
| **Nombre** | 3-5 par niveau | 5-10 par équipe |
| **Cible** | 70% = succès | 100% attendu |

**Ne pas confondre :**
```
KPI : "Revenue mensuel" → mesurer la santé
OKR : "Doubler le MRR via le canal entreprise en Q2" → changer l'état
```

---

## 7. Outils OKR

| Outil | Fonctionnalités | Prix |
|-------|----------------|------|
| **Gtmhub** | OKR + KPI + analytics intégrés | $10/user/mois |
| **Workboard** | OKR natif, alignment AI | $14/user/mois |
| **Koan** | OKR simple, Slack integration | $8/user/mois |
| **Ally** | OKR + 1:1 + feedback | $6/user/mois |
| **BetterWorks** | Enterprise-grade | $20/user/mois |
| **Notion** | DB OKR custom (gratuit) | Gratuit/Team |
| **Google Sheets** | Template OKR simple | Gratuit |

---

# Partie 2 : Team Management

## 8. Styles de Leadership

| Style | Description | Quand |
|-------|-------------|-------|
| **Coach** | Développe les compétences long terme | Équipe junior, transition |
| **Visionnaire** | Inspire, donne la direction | Période de changement, startup |
| **Participatif** | Décision collective | Équipe senior, buy-in nécessaire |
| **Délégatif** | Autonomie complète | Équipe experte, stable |
| **Directif** | Décision rapide, top-down | Crise, urgence |
| **Pacesetter** | Montre l'exemple, exigeant | Équipe motivée, objectifs ambitieux |

### Situational Leadership (Hersey-Blanchard)
```
Niveau de compétence de l'équipe
    Faible → Délégue
    Moyen  → Participe / Vends
    Élevé  → Délègue / Confie
```

---

## 9. 1:1 Meetings

### Fréquence Recommandée
```
Senior / Experienced : 1× toutes les 2 semaines (30 min)
Junior / New hire    : 1× par semaine (30 min)
Manager direct       : 1× par semaine (45 min)
```

### Template 1:1
```
# 1:1 — {{employé}} — {{date}}

## 🎯 Priorités de la semaine
- ...

## ✅ Accomplissements récents
- ...

## 🚧 Défis / Bloquants
- ...

## 🧭 Développement
- Compétences à développer : ...
- Objectifs de carrière : ...
- Formation souhaitée : ...

## 💬 Feedback
- Manager → Employé : ...
- Employé → Manager : ...

## 📋 Actions
- ...
```

### Règle 80/20
- **80%** : employé parle
- **20%** : manager parle
- Le 1:1 est pour l'employé, pas pour le manager

---

## 10. Feedback & RADAR

### La Méthode RADAR

```
R — Recognize/Reconnaître le contexte
A — Affirmer/Action(s) observée(s)
D — Décrire l'impact
A — Attendre la réaction / Alternative
R — Renforcer / Recommander
```

**Feedback positif RADAR :**
```
(R) Pendant la revue de code hier...
(A) Tu as pris le temps d'expliquer pourquoi l'approche était meilleure...
(D) Ça a aidé Marc à comprendre et à monter en compétence...
(A) Comment as-tu perçu la discussion ?
(R) Continue comme ça, c'est exactement ce qu'on veut dans l'équipe.
```

**Feedback correctif RADAR :**
```
(R) Lors du sprint planning hier...
(A) Tu as interrompu Sophie 3 fois pendant son estimation...
(D) Elle n'a pas pu finir son raisonnement, et l'équipe a perdu une perspective importante...
(A) Tu vois ce que je veux dire ?
(R) La prochaine fois, laisse-la finir, puis pose tes questions après.
```

### SBI Model (Alternative)
```
S — Situation : "Lors de la revue de sprint hier..."
B — Behavior : "Tu as haussé le ton quand..."
I — Impact : "L'équipe s'est tendue et personne n'a plus parlé."
```

---

## 11. Gestion de Conflit

### Thomas-Kilmann Model (5 Modes)

```
        Assertif
            │
  Compétition │ Collaboration
      (gagne/perd)│     (gagne/gagne)
            │
            ────────→ Coopératif
  Évitement  │   Accommodement
   (perd/perd)│    (perd/gagne)
            │
        Non assertif
```

### Approche
1. **Écouter** chaque partie individuellement d'abord
2. **Recadrer** le problème (vs la personne)
3. **Identifier** les intérêts sous-jacents
4. **Proposer** des solutions gagnant-gagnant
5. **Documenter** l'accord
6. **Suivre** après 1 semaine

---

## 12. Motivation & Rétention

### Herzberg — 2 Factors

| Facteurs d'Hygiène (insatisfaction) | Facteurs de Motivation (satisfaction) |
|-------------------------------------|--------------------------------------|
| Salaire | Accomplissement |
| Conditions de travail | Reconnaissance |
| Sécurité de l'emploi | Responsabilité |
| Politiques d'entreprise | Avancement |
| Relations | Développement personnel |

**Règle :** Les facteurs d'hygiène ne motivent pas, ils empêchent la démotivation.

### Daniel Pink — Autonomie, Maîtrise, Sens
```
Autonomie : Liberté sur comment, quand, avec qui
Maîtrise : Opportunité de développer ses compétences
Sens : Comprendre l'impact de son travail
```

---

## 13. Team Building & Rituels

| Rituel | Fréquence | Durée |
|--------|-----------|-------|
| **Daily Standup** | Quotidien | 15 min |
| **1:1** | Hebdo/Bi-hebdo | 30 min |
| **Rétro** | Fin sprint | 1h |
| **Team Review** | Fin sprint | 1h |
| **Sprint Planning** | Début sprint | 2-4h |
| **Démo / Show & Tell** | Bi-hebdo | 30 min |
| **Blitz / Hackathon** | Trimestriel | 1-2j |
| **Team Offsite** | Semestriel | 1-2j |
| **Friday Wins** | Hebdo | 15 min |

---

## 14. Délégation

### Eisenhower Matrix (Urgent/Important)

```
                   Urgent         |     Non Urgent
                ══════════════════╪══════════════════
Important │    I. FAIRE            │ II. PLANIFIER
           │    (crise, deadline)  │ (stratégie, formation)
           │                       │
           │    Déléguer si urgent │ Ne pas déléguer
           ├───────────────────────┼──────────────────
Non        │    III. DÉLÉGUER      │ IV. ÉLIMINER
Important  │    (interruptions,    │ (distractions,
           │     réunions)         │  tâches sans valeur)
```

### Règle de Délégation
```
1. Dire quoi (le résultat attendu), pas comment
2. Donner le contexte et les ressources
3. Définir les points de contrôle
4. Accepter l'erreur comme apprentissage
5. Ne pas reprendre la tâche
```

---

## 15. Anti-Patterns du Management

| Anti-Pattern | Symptôme | Correction |
|-------------|----------|-----------|
| **Micromanagement** | L'équipe attend validation pour tout | Fixer des limites claires, déléguer |
| **Ghost Manager** | Jamais disponible en 1:1 | Bloquer du temps pour l'équipe |
| **Feedback sandwich** | Positif → Négatif → Positif (dilue le message) | RADAR direct |
| **Hero culture** | Celui qui sauve est récompensé | Récompenser ceux qui évitent les crises |
| **Bus factor = 1** | Une personne sait tout | Cross-training, documentation |
| **Hippo (Highest Paid Person's Opinion)** | Décision imposée par le plus gradé | Data-driven decisions |
| **Death by meeting** | Journées sans pause | Asynchrone > synchrone |

---

## 16. Références

- **John Doerr — Measure What Matters** (OKR)
- **Andy Grove — High Output Management**
- **Kim Scott — Radical Candor** (Feedback)
- **Patrick Lencioni — The 5 Dysfunctions of a Team**
- **Daniel Pink — Drive** (Motivation)
- **Michael Lopp — Managing Humans**
- **Hersey & Blanchard — Situational Leadership**
- **Herzberg — One More Time: How Do You Motivate Employees?**

### Certifications
- **OKR Coach** (okrinstitute.org)
- **PMP** (PMI) — Team Management domain
- **ICAgile** — Agile Team Facilitation
