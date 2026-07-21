---
name: notion-pm
description: Notion pour le management de projet — bases de données relationnelles, rollups, formules, templates (sprint, backlog, roadmap, retro), dashboards, automation.
category: productivity
---

# Notion pour le Management de Projet — Référence Complète

## Contexte & Déclencheur
Utiliser quand l'utilisateur demande : Notion gestion de projet, template Notion, database Notion, relation rollup, sprint Notion, roadmap Notion, backlog Notion.

---

## 1. Concepts Clés pour le PM

| Concept | Usage Projet |
|---------|-------------|
| **Database (BDD)** | Stocker les tâches, sprints, OKRs, notes |
| **Relation** | Lier tâches → projets, sprints → objectifs |
| **Rollup** | Agréger : total points, progression, % terminé |
| **Formula** | Calculs : retard, jours restants, priorité |
| **View** | Kanban, Timeline, Calendar, Table |
| **Template Button** | Créer un sprint, une réunion, un projet |
| **Linked Database** | Vue filtrée d'une DB centrale dans une autre page |

---

## 2. Architecture Recommandée

### Workspace Type
```
🏢 Espace Projet
├── 🎯 Objectifs & OKRs (DB — Calendar/Table)
├── 📋 Backlog Central (DB — Table)
├── 🏃 Sprints (DB — Board)
├── 📊 Roadmap (DB — Timeline)
├── 📝 Notes Réunions (DB — Calendar)
├── 👥 Équipe (DB — Table)
├── 📚 Base de Connaissances (Pages)
└── 📈 Dashboard Projet (Page with linked DBs)
```

---

## 3. Relations & Rollups — Patterns Essentiels

### Pattern 1: Projets → Tâches (1:N)
```
DB "Projets" → DB "Tâches"
├── Relation: Tâches liées → (inverse: Projet)
├── Rollup: Total points (sum de Points)
├── Rollup: Progression (% Done)
└── Rollup: Points restants (sum où Statut != Done)
```

### Pattern 2: Tâches → Sprints (N:1)
```
DB "Tâches" → DB "Sprints"
├── Relation: Sprint (inverse: Tâches du sprint)
├── Rollup: Vélocité sprint (sum Points où Statut=Done)
└── Formula: Burndown
```

### Pattern 3: OKRs → Projets (N:N)
```
DB "OKRs" → DB "Projets"
├── Relation: Projets contributeurs (inverse: OKR lié)
├── Rollup: Progression OKR (moyenne progression projets)
└── Formula: Statut OKR (rouge/ambre/vert)
```

---

## 4. Templates Clés

### 4.1 Template Sprint
```markdown
# Sprint {{Nom}} — {{Date début}} → {{Date fin}}

## 🎯 Objectif du sprint
...

## 📋 Engagement
| Tâche | Points | Assigné | Statut |
|-------|--------|---------|--------|

## 📊 Métriques
- Vélocité précédente : {{N}}
- Capacité : {{N}} points

## ⚠️ Risques
- ...

## ✅ Definition of Done
- [ ] Code revu
- [ ] Tests passent
- [ ] Déployé staging
```

### 4.2 Template Réunion Hebdo
```markdown
# Réunion {{Sprint}} — {{Date}}

## 🟢 Fait depuis dernière fois
- [ ] Tâche 1
- [ ] Tâche 2

## 🟡 En cours
- [ ] Tâche 3
- [ ] Tâche 4

## 🔴 Bloquant
- Blocage 1 (assigné, date)

## 📋 Actions
| Action | Responsable | Deadline |
|--------|-------------|----------|
```
---

## 5. Formules Avancées

### 5.1 Progression Projet
```javascript
// % de tâches terminées
round(length(filter(prop("Tâches"), current.prop("Statut") == "Done")) / 
      length(prop("Tâches")) * 100)
```

### 5.2 Statut Projet (RAG)
```javascript
// Rouge/Ambre/Vert
if(prop("Progression") == 100, "🟢 Terminé",
  if(prop("Date fin") < now() and prop("Progression") < 100, "🔴 En retard",
    if(prop("Date fin") < dateAdd(now(), 7, "days") and prop("Progression") < 80, "🟡 À risque", "🟢 OK")))
```

### 5.3 Priorité Calculée
```javascript
// Impact + Urgence
if(prop("Impact") == "Élevé" and prop("Urgence") == "Haute", "P0",
  if(or(prop("Impact") == "Élevé", prop("Urgence") == "Haute"), "P1", "P2"))
```

### 5.4 Burndown Sprint
```javascript
// Points restants projetés
prop("Points totaux") - 
  prop("Points terminés") - 
  round((dateBetween(now(), prop("Date début"), "days") / 
         dateBetween(prop("Date fin"), prop("Date début"), "days")) * 
         prop("Points totaux"))
```

---

## 6. Views par Rôle

| Rôle | Vue recommandée | Propriétés visibles |
|------|----------------|-------------------|
| **PO** | Board + Timeline | Statut, Priorité, Points, Sprint |
| **Dev** | Board filtré (assigné = moi) | Statut, Points, Bloquant |
| **SM** | Board + Table | Statut, Assigné, Cycle Time |
| **Manager** | Timeline + Dashboard | Progression, Risques, Budget |
| **Stakeholder** | Dashboard (read-only) | OKR, Roadmap, KPIs |

---

## 7. Automations & Boutons

### 7.1 Template Button — Nouveau Projet
```
Créer une page dans DB Projets
Titre: "{{input:Nom du projet}}"
Propriétés:
- Statut: "À lancer"
- Priorité: "Moyenne"
- Date début: now()
```

### 7.2 Template Button — Daily Standup
```
Créer une page dans DB Daily
Date: now()
Template: Standup Template
```

### 7.3 Automation (Notion Automations)
```
QUAND: Statut = "En cours"
ALORS: Definir Date début → now()

QUAND: Statut = "Terminé"
ALORS: Definir Date fin → now()
ET: Assigner → "" (vide)

QUAND: Priorité = "Bloquante" ET Statut != "Terminé"
ALORS: Notifier → @channel
```

---

## 8. Dashboards

### Page Dashboard Type
```
# 📊 Dashboard {{Projet}}

## 🎯 OKRs
[Linked DB — OKRs filtrée: Projet = {{current}}]

## 🏃 Sprint Actif
[Linked DB — Tâches filtrée: Sprint = current, Statut != Done]

## 📈 Vélocité
[Embed graphique — Notion Charts]

## ⚠️ Bloquants
[Linked DB — Tâches filtrée: Statut = Bloqué]

## 📅 Prochaines Échéances
[Linked DB — Jalon filtrée: Date > now() et Date < now() + 30j]
```

---

## 9. Intégrations Projet

| Service | Usage | Comment |
|---------|-------|---------|
| **Jira** | Sync issues ↔ Notion | Plugin Notion + Jira Bridge |
| **GitHub** | PRs, commits liés aux tâches | Relation Board → GitHub |
| **Slack** | Notifications, création rapide | Notion Bot Slack |
| **Google Calendar** | Deadlines, milestones | Embed Calendar |
| **Zapier / Make** | Sync cross-app | Nombreux templates |

---

## 10. Anti-Patterns Notion PM

| Anti-Pattern | Problème | Solution |
|-------------|----------|----------|
| **Tout dans une seule DB** | Pas de hiérarchie, impossible à filtrer | Multi-DB avec relations |
| **Pas de templates** | Incohérence entre pages | Template obligatoire par DB |
| **Relations non inversées** | Impossible de voir l'agrégation | Ajouter relation inverse |
| **Rollups à 3+ niveaux** | DB lente, limite API | Dénormaliser partiellement |
| **Permissions ouvertes** | Modification accidentelle | Restreindre édition par rôle |
| **Pas d'archivage** | DB de 5000+ items, lente | Archiver les sprints finis |

---

## 11. Références

- **Notion Academy — Project Management** : notion.so/help/guides/project-management
- **Notion Templates Gallery** : notion.so/templates
- **Notion API Docs** : developers.notion.com
- **Reddit r/Notion** : Meilleures pratiques communautaires
- **Marie Poulin — Notion for PM** : YouTube