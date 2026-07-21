---
name: jira
description: Configuration, administration et utilisation avancée de Jira — workflows, schemas, JQL, automation, reports, plugins, migration.
category: productivity
---

# Jira — Référence Complète

## Contexte & Déclencheur
Utiliser quand l'utilisateur demande : Jira, configuration projet, workflows, JQL, automation, rapports Jira, administration Jira, migration Jira.

---

## 1. Architecture Jira

### 1.1 Concept fondamentaux

| Concept | Description |
|---------|-------------|
| **Project** | Conteneur d'issues, type (Scrum/Kanban/Business/DevOps) |
| **Issue** | Élément de travail (Story, Bug, Task, Epic, Sub-task) |
| **Scheme** | Configuration attachée (workflow, field, screen, permission) |
| **Workflow** | Étapes + transitions + conditions + validateurs + post-functions |
| **Field** | Champ (système ou custom) |
| **Screen** | Disposition des champs par opération (Create/Edit/View) |
| **Permission** | Qui peut faire quoi dans le projet |
| **Notification** | Qui est notifié sur quels événements |

### 1.2 Types d'Issues Standard

| Issue Type | Usage | Hiérarchie |
|-----------|-------|-----------|
| **Epic** | Large initiative, contient des stories | Parent |
| **Story** | Fonctionnalité utilisateur (valeur métier) | Enfant d'Epic |
| **Task** | Tâche technique sans valeur utilisateur directe | Enfant d'Epic |
| **Bug** | Défaut identifié | Enfant d'Epic |
| **Sub-task** | Découpage d'une Story/Task/Bug | Enfant d'issue |
| **Spike** | Investigation / POC | Enfant d'Epic |
| **Improvement** | Amélioration incrémentale | Enfant d'Epic |

---

## 2. JQL (Jira Query Language)

### 2.1 Syntaxe Fondamentale

```jql
project = "MONPROJ" AND status = "In Progress" ORDER BY priority DESC
```

| Opérateur | Usage | Exemple |
|-----------|-------|---------|
| `=`, `!=` | Égalité | `assignee = currentUser()` |
| `>`, `<`, `>=`, `<=` | Comparaison | `created > -7d` |
| `IN`, `NOT IN` | Liste | `priority IN (High, Critical)` |
| `~`, `!~` | Texte | `summary ~ "login"` |
| `IS`, `IS NOT` | Null | `fixVersion IS EMPTY` |
| `WAS`, `WAS IN` | Historique | `status WAS "In Progress"` |
| `CHANGED` | Changement | `status CHANGED AFTER "2025/01/01"` |

### 2.2 Fonctions Intégrées

| Fonction | Retourne | Exemple |
|----------|----------|---------|
| `currentUser()` | L'utilisateur connecté | `assignee = currentUser()` |
| `membersOf(group)` | Membres d'un groupe | `assignee IN membersOf("jira-developers")` |
| `projectsLeadByUser(user)` | Projets leadés | `project IN projectsLeadByUser("admin")` |
| `issueHistory()` | Issues récemment visitées | `issue IN issueHistory()` |
| `now()` | Date/heure actuelle | `due < now()` |
| `startOfDay()/endOfDay()` | Bornes temporelles | `created > startOfDay(-30d)` |

### 2.3 Requêtes Avancées

**Sprint actuel de l'équipe :**
```jql
project = MONPROJ AND sprint in openSprints() AND assignee = currentUser()
```

**Items non estimés dans les epics actives :**
```jql
project = MONPROJ AND "Story points" IS EMPTY AND 
issueFunction IN issuesInEpics("status != Done")
```

**Cycle Time (temps en "In Progress") :**
```jql
project = MONPROJ AND status CHANGED TO "In Progress" AFTER startOfDay(-30d) 
AND status = Done
```

### 2.4 Issue Function (Script Runner)

Requiert le plugin ScriptRunner :

```jql
issueFunction in commented("by membersOf(jira-developers) after -7d")
issueFunction in issuesInEpics("status != Done")
issueFunction in linkedIssuesFrom("blocks", "is blocked by")
```

---

## 3. Workflows

### 3.1 Workflow Simple (3 états)

```
To Do ──→ In Progress ──→ Done
   ↑            ↓
   └──────←─────┘
```

### 3.2 Workflow Avancé (Scrum)

```
             ┌─────────────────────────────────────┐
             ↓                                     │
[To Do] → [In Progress] → [Review] → [Testing] → [Done]
   ↑            ↓              ↑           ↓
   │       [Blocked]─→─────────┤           │
   │       [Reopened]←──────────────────────┘
   └───────────────────────────────────────────────┘
```

### 3.3 Configuration Workflow (YAML/XML)

```xml
<workflow name="Scrum Standard">
  <step id="1" name="To Do">
    <transition target="2" name="Commencer">
      <condition type="permission" argument="assign"/>
    </transition>
  </step>
  <step id="2" name="In Progress">
    <transition target="3" name="Terminer" />
    <transition target="4" name="Bloquer" />
  </step>
  <step id="3" name="Done">
    <transition target="1" name="Réouvrir"/>
  </step>
  <step id="4" name="Blocked">
    <transition target="2" name="Débloquer"/>
  </step>
</workflow>
```

---

## 4. Automation (Jira Automation)

### 4.1 Triggers Disponibles

| Trigger | Usage |
|---------|-------|
| `Issue Created` | Auto-assign, auto-label |
| `Issue Transitioned` | Notifications, champs dynamiques |
| `Field Value Changed` | Mise à jour dépendante |
| `Scheduled` | Rappels, bulk updates |
| `Webhook` | Intégration externe |

### 4.2 Règles Essentielles

**Auto-assigner les bugs bloquants :**
```yaml
trigger: Issue Created
conditions:
  - field: priority
    value: blocker
  - field: issuetype
    value: Bug
actions:
  - assignee: project.lead
  - label: auto-triaged
  - comment: "Bug bloquant auto-assigné au lead projet"
```

**Rappel de reboucher le chrono :**
```yaml
trigger: Scheduled
interval: daily 10:00
conditions:
  - field: status
    value: In Progress
  - field: timeSpent
    is: EMPTY
actions:
  - notify: assignee
    message: "⚠️ N'oublie pas de logger ton temps aujourd'hui"
```

---

## 5. Board Configuration

### 5.1 Board Scrum
```
Columns: To Do (1) | In Progress (2) | Review (2) | Testing (2) | Done (∞)
Quick Filters: 
- My Issues: assignee = currentUser()
- Blocker: priority = Blocker
- Hors Sprint: sprint IS EMPTY
```

### 5.2 Board Kanban
```
Columns: 
  Backlog (∞) | Selected (5) | In Progress (3) | Review (2) | Done (14d) | Done (∞)
WIP par colonne : explicite
```

---

## 6. Rapports & Analytics

| Rapport | Usage | Commande JQL suggérée |
|---------|-------|----------------------|
| **Sprint Burndown** | Équipe Scrum | `project = X AND sprint = Y` |
| **Velocity Chart** | Planification | `project = X AND type IN (Story, Bug)` |
| **Cumulative Flow** | Flow Kanban | `project = X AND created > -90d` |
| **Cycle Time** | Performance | `project = X AND status = Done DURING (startOfDay(-30d))` |
| **Resolution Time** | SLA | `project = X AND priority = Critical` |
| **Pie Chart** | Répartition | `status, priority, assignee` |

### Rapports personnalisés (export CSV → analyse Python)
```python
import pandas as pd
from jira import JIRA

jira = JIRA(server="...", token_auth="...")
issues = jira.search_blocks("project = MONPROJ AND status = Done", 
                             fields="summary,status,created,resolutiondate",
                             maxResults=1000)

df = pd.DataFrame([{
    'key': i.key,
    'cycle_time': (parse(i.fields.resolutiondate) - parse(i.fields.created)).days,
    'priority': i.fields.priority.name if i.fields.priority else None
} for i in issues])

print(df.groupby('priority')['cycle_time'].describe())
```

---

## 7. Administration & Maintenance

| Tâche | Commande / Chemin |
|-------|------------------|
| **Sauvegarde** | Administration → System → Backup |
| **Réindexation** | Administration → System → Indexing |
| **Projets fantômes** | JQL: `project = X AND created < -1y AND status IN (Backlog, To Do)` |
| **Permissions review** | Project Settings → Permissions → Audit |
| **Workflow draft** | Workflow → Copy → Edit draft → Publish |

---

## 8. Plugins Indispensables

| Plugin | Utilité | Prix |
|--------|---------|------|
| **ScriptRunner** | Groovy scripting, listeners, behaviours | $10/user/an |
| **Tempo** | Time tracking, planning, budgets | $4/user/mois |
| **Portfolio** | Planification hiérarchique | $15/user/mois |
| **Structure** | Arborescences multi-projets | $5/user/mois |
| **eazyBI** | Rapports BI avancés | $10/user/mois |
| **BigPicture** | PPM (Project Portfolio Management) | $15/user/mois |

---

## 9. Migration & API

### REST API
```bash
# Récupérer les issues d'un projet
curl -u email:token "https://votre-site.atlassian.net/rest/api/3/search?jql=project=MONPROJ"

# Créer une issue
curl -X POST -u email:token -H "Content-Type: application/json" \
  -d '{"fields":{"project":{"key":"MONPROJ"},"summary":"Nouveau bug","issuetype":{"name":"Bug"}}}' \
  "https://votre-site.atlassian.net/rest/api/3/issue"
```

### Migration (Jira Cloud → Data Center ou vice-versa)
1. Exporter les projets → CSV/XML
2. Utiliser **Jira Cloud Migration Assistant**
3. Vérifier les schémas (workflows, fields, screens)
4. Tester avec un projet miroir d'abord

---

## 10. Anti-Patterns

| Anti-Pattern | Correction |
|-------------|-----------|
| **Trop de statuts (15+)** | Fusionner les étapes redondantes |
| **Workflow sans transitions visibles** | Ajouter une matrice de transition |
| **Champs custom illimités** | Geler les nouveaux champs pendant 1 mois |
| **Permissions "Anyone"** | Revoir en lecture seule public |
| **JQL jamais utilisée** | Former aux filtres partagés |
| **Rapports ignorés** | Automatiser l'envoi hebdomadaire |

---

## 11. Références & Certifications

- **Atlassian University** — ACP-620 (Jira Admin)
- **Jira REST API v3** — developer.atlassian.com/cloud/jira
- **ScriptRunner Docs** — adaptavist.com
- **Atlassian Community** — community.atlassian.com
