---
name: multi-agent-orchestration
description: "Orchestrer des tâches d'automatisme avec des sous-agents."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - multi-agent
      - delegation
      - automation
      - plc
      - scada
      - orchestration
      - parallel-processing
      - task-splitting
      - result-consolidation
      - agent-patterns
    related_skills:
      - plan
      - plc-connectivity
      - ignition-scada
      - delegate-task
      - industrial-audit
---

# Orchestration Multi-Agents pour les Projets d'Automatisme Industriel

## Vue d'ensemble

Les projets d'automatisme industriel impliquent souvent de grands volumes de fichiers, de multiples automates (PLC) ou des configurations complexes à traiter en parallèle. L'orchestration multi-agents permet de diviser ces charges de travail massives en sous-tâches indépendantes, exécutées simultanément par des sous-agents EVA.

Cette compétence fournit les instructions et les patrons de conception nécessaires pour déléguer efficacement ces sous-tâches via l'outil [`delegate_task`](../../../tools/delegate_tool.py).

### Principe de fonctionnement

```
Agent Parent
    │
    ├── Stratégie de découpage des tâches
    │   └── Diviser par : entité logique, phase, fichier, type d'analyse
    │
    ├── delegate_task(tasks=[...])  ← Exécution parallèle
    │   ├── Sous-agent 1 (ex: Auditer AS6)
    │   ├── Sous-agent 2 (ex: Auditer AS7)
    │   ├── Sous-agent 3 (ex: Auditer AS8)
    │   └── ... (max 3 simultanés par défaut)
    │
    └── Consolidation des résultats
        ├── Agrégation des bilans
        ├── Détection des conflits / incohérences
        └── Génération du rapport final
```

### Propriétés fondamentales

- **Exécution synchrone** : L'agent parent suspend sa boucle et attend le rapport de chaque sous-agent. En cas d'interruption de l'agent parent, tous les sous-agents sont immédiatement arrêtés.
- **Isolation des sous-agents** : Chaque sous-agent dispose d'un contexte de travail et d'une session de terminal isolés, garantissant l'absence de conflits d'écriture.
- **Parallélisme contrôlé** : La limite par défaut est de 3 sous-agents simultanés, configurable via `delegation.max_concurrent_children`.

## Quand l'utiliser

### À utiliser lorsque l'utilisateur demande de :

- Traiter en parallèle des tâches volumineuses de génération, d'audit ou d'analyse (ex : analyser 20 automates simultanément).
- Diviser un projet complexe en sous-étapes indépendantes exécutées par des sous-agents spécialisés.
- Générer de la documentation technique pour plusieurs équipements en parallèle.
- Auditer la conformité d'un parc de machines avec des référentiels multiples (ISO 25010, ISA-95, IEC 62443).
- Convertir ou migrer des programmes PLC entre différentes plateformes de manière parallélisée.
- Exécuter des simulations sur plusieurs variantes de configuration simultanément.

### Ne pas utiliser pour :

- Des tâches séquentielles où chaque étape dépend du résultat de la précédente.
- Des opérations nécessitant un accès exclusif à une ressource partagée (ex : base de données unique sans verrou).
- Du débogage interactif nécessitant une intervention humaine entre chaque étape.

---

## 1. Stratégie de Découpage des Tâches

### 1.1 Patrons de division recommandés

| Patron | Description | Cas d'usage typique |
| :--- | :--- | :--- |
| **Par entité logique** | Une tâche par machine, station ou automate | Audit de parc, analyse de conformité |
| **Par phase** | Séparation en phases séquentielles mais parallélisables | Diagnostic → Correction → Vérification |
| **Par fichier** | Un sous-agent par fichier ou répertoire | Conversion de code, analyse de logs |
| **Par type d'analyse** | Chaque sous-agent applique une analyse différente sur les mêmes données | Analyse de code sous plusieurs angles (sécurité, performance, style) |
| **Par couche fonctionnelle** | ISA-95 split : Niveau 0 (capteurs), Niveau 1 (PLC), Niveau 2 (SCADA) | Documentation multi-niveaux |

### 1.2 Règles de découpage

1. **Isoler les dépendances** : Les sous-agents doivent travailler sur des fichiers ou répertoires disjoints pour éviter les conflits d'écriture.
2. **Homogénéité de charge** : Chaque sous-tâche doit représenter un volume de travail comparable pour éviter l'effet de goulet d'étranglement (straggler).
3. **Granularité adaptée** : Ni trop fine (surcharge de coordination) ni trop grossière (sous-parallélisation). Viser 5 à 20 sous-tâches par session.
4. **Préfixer les sorties** : Chaque sous-agent doit produire des fichiers identifiables (ex: `audit_AS6.md`, `audit_AS7.md`) pour faciliter la consolidation.

### 1.3 Exemple : Audit de parc automates

```python
automates = [
    {"id": "AS6", "type": "Siemens S7-1500", "projet": "/data/ligne1/AS6/"},
    {"id": "AS7", "type": "Rockwell CompactLogix", "projet": "/data/ligne1/AS7/"},
    {"id": "FC1", "type": "Siemens S7-1200", "projet": "/data/ligne2/FC1/"},
    {"id": "FC2", "type": "CODESYS Edge", "projet": "/data/ligne2/FC2/"},
]

tasks = [
    {
        "id": f"audit_{a['id']}",
        "goal": f"Auditer l'automate {a['id']} ({a['type']})",
        "context": {
            "automate_id": a['id'],
            "projet_path": a['projet'],
            "referential": "IEC-62443",
        }
    }
    for a in automates
]
```

---

## 2. Syntaxe de Délégation

### 2.1 Délégation parallèle (mode `tasks`)

Pour lancer plusieurs sous-agents en parallèle, passez une liste de dictionnaires à l'argument `tasks` :

```python
from tools.delegate_tool import delegate_task

tasks = [
    {"id": "as6", "goal": "Auditer l'automate AS6 (Siemens S7-1500)"},
    {"id": "as7", "goal": "Auditer l'automate AS7 (Rockwell CompactLogix)"},
    {"id": "fc1", "goal": "Auditer l'automate FC1 (Siemens S7-1200)"},
]

results = delegate_task(tasks=tasks)
```

### 2.2 Délégation simple (mode `goal`)

Pour une tâche unique exécutée par un sous-agent dédié :

```python
result = delegate_task(
    goal="Générer les schémas électriques du panneau P-101 "
          "à partir des fichiers DWG dans /data/panneaux/P-101/"
)
```

### 2.3 Paramètres avancés

```python
results = delegate_task(
    tasks=tasks,
    max_concurrent=3,           # Nombre max de sous-agents simultanés
    timeout_minutes=30,         # Timeout global pour la délégation
    consolidate=False,          # Retourner les résultats bruts sans consolidation
    priority="high",            # Priorité de la tâche (high / normal / low)
    tags=["audit", "ligne1"],   # Tags pour le suivi
    callback_url="https://...", # Webhook de notification de fin
)
```

### 2.4 Structure du résultat

```python
@dataclass
class DelegateResult:
    task_id: str                    # Identifiant de la tâche
    status: str                     # success / failure / timeout
    summary: str                    # Bilan textuel du sous-agent
    output_files: list[str]         # Fichiers produits
    duration_seconds: float         # Temps d'exécution
    token_usage: dict               # Consommation API (prompt + completion)
    error: str | None               # Message d'erreur si échec
```

---

## 3. Consolidation des Résultats

### 3.1 Agrégation automatique

Après l'exécution parallèle, l'agent parent doit consolider les résultats :

```python
def consolidate_audit_results(results: list[DelegateResult]) -> str:
    """Agrège les rapports d'audit individuels en un document global."""
    successful = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status != "success"]

    report = [
        "# Rapport de Consolidation d'Audit\n",
        f"**Date :** {datetime.now().isoformat()}\n",
        f"**Sous-agents :** {len(successful)} réussis, {len(failed)} échoués\n",
    ]

    # Section des succès
    for result in successful:
        report.append(f"\n## Résultat : {result.task_id}\n")
        report.append(result.summary)
        report.append(f"\n_Durée : {result.duration_seconds:.1f}s_")

    # Section des échecs
    if failed:
        report.append("\n## Échecs\n")
        for result in failed:
            report.append(f"- **{result.task_id}** : {result.error}")

    return "\n".join(report)
```

### 3.2 Détection de conflits

```python
def detect_conflicts(results: list[DelegateResult]) -> list[str]:
    """Détecte les incohérences entre les rapports des sous-agents."""
    conflicts = []
    # Vérifier les chevauchements de plages d'adresses
    # Vérifier les incohérences de nommage de variables
    # Vérifier les versions de protocole incompatibles
    return conflicts
```

---

## 4. Gestion des Erreurs et Réessais

### 4.1 Stratégie de reprise

| Type d'erreur | Comportement attendu |
| :--- | :--- |
| Timeout sous-agent | Relancer une fois avec un timeout doublé |
| Erreur API (rate limit) | Attendre 30 secondes et réessayer (max 3 tentatives) |
| Fichier introuvable | Marquer comme échec, continuer les autres tâches |
| Erreur interne sous-agent | Capturer la stack trace, rapporter dans le bilan |

### 4.2 Pattern de délégation résiliente

```python
MAX_RETRIES = 2
BACKOFF_SECONDS = 30

for attempt in range(MAX_RETRIES + 1):
    results = delegate_task(tasks=tasks)
    failed_tasks = [r for r in results if r.status != "success"]

    if not failed_tasks:
        break

    if attempt < MAX_RETRIES:
        print(f"Nouvelle tentative pour {len(failed_tasks)} tâche(s) échouée(s)...")
        time.sleep(BACKOFF_SECONDS * (attempt + 1))
        tasks = [r.task_config for r in failed_tasks]  # Re-soumettre
```

---

## 5. Bonnes Pratiques et Optimisation

### 5.1 Équilibrage de charge

Utiliser un prédécoupage basé sur la taille des fichiers ou le nombre d'éléments à traiter :

```python
import os
from pathlib import Path

def split_by_file_size(directory: str, max_tasks: int = 10):
    """Divise les fichiers d'un répertoire en lots de taille équilibrée."""
    files = list(Path(directory).rglob("*.scl"))
    files.sort(key=lambda f: f.stat().st_size, reverse=True)

    batches = [[] for _ in range(min(max_tasks, len(files)))]
    for i, file in enumerate(files):
        batches[i % len(batches)].append(str(file))

    return [
        {"id": f"batch_{i}", "goal": f"Traiter {len(batch)} fichiers SCL",
         "context": {"files": batch}}
        for i, batch in enumerate(batches)
    ]
```

### 5.2 Budget API et coûts

Chaque sous-agent consomme un budget API. Anticiper le coût total :

| Nombre de sous-agents | Tokens estimés par sous-agent | Coût total estimé |
| :--- | :--- | :--- |
| 3 | ~10 000 | ~30 000 tokens |
| 10 | ~15 000 | ~150 000 tokens |
| 20 | ~12 000 | ~240 000 tokens |

> **Note :** Le coût réel dépend du modèle utilisé et de la complexité de chaque sous-tâche. Le paramètre `max_iterations` de chaque sous-agent limite son budget.

### 5.3 Stratégies d'exclusion

> **Important :** Les sous-agents ne doivent jamais modifier les fichiers sources du noyau EVA (`run_agent.py`, `cli.py`, etc.). Si une opération nécessite une modification du noyau, elle doit être remontée à l'agent parent.

---

## 6. Exemple Complet : Audit et Correction de Parc PLC

```python
from tools.delegate_tool import delegate_task

# Étape 1 : Audit parallèle
print("Phase 1 : Audit des automates...")
stations = ["AS6", "AS7", "FC1", "FC2"]
audit_results = delegate_task(tasks=[
    {"id": s, "goal": f"Auditer la conformité IEC 62443 de {s}"}
    for s in stations
])

# Étape 2 : Consolidation
report = consolidate_audit_results(audit_results)
with open("rapport_audit_parc.md", "w") as f:
    f.write(report)

# Étape 3 : Corrections ciblées (uniquement sur les échecs)
failed = [r for r in audit_results if r.status != "success"]
if failed:
    print(f"Phase 2 : Correction de {len(failed)} automate(s)...")
    delegate_task(tasks=[
        {"id": f"fix_{r.task_id}",
         "goal": f"Appliquer les corrections nécessaires à {r.task_id}",
         "context": {"audit_report": r.summary}}
        for r in failed
    ])
```

---

## Pièges Courants (Common Pitfalls)

1. **Chevauchement des fichiers de sortie** : Deux sous-agents écrivant dans le même fichier provoquent une corruption. Toujours préfixer ou isoler les répertoires de sortie par sous-agent.

2. **Sous-estimation du budget API** : 10 sous-agents exécutant 5 itérations chacun = 50 appels API. Vérifier `self.iteration_budget` de l'agent parent avant de lancer.

3. **Dépendances séquentielles cachées** : Une tâche apparemment indépendante peut nécessiter le résultat d'une autre. Analyser le graphe de dépendances avant de paralléliser.

4. **Absence de consolidation** : Sans étape de fusion explicite, les résultats restent fragmentés. Toujours prévoir une fonction de consolidation après la délégation parallèle.

5. **Non-respect de l'isolation des contextes** : Les sous-agents partagent le contexte global de l'agent parent. Éviter de transmettre des secrets ou des informations sensibles dans les consignes déléguées.

6. **Timeout inadapté** : Un timeout trop court interrompt des sous-agents encore productifs. Le configurer en fonction de la complexité estimée (compter ~2 min par fichier de 1000 lignes).

---

## 7. Protocoles de Collaboration Hétérogène et Découverte (A2A, ACP, ARD, UCP, M2A)

EVA supporte les standards ouverts de Google et de la Linux Foundation pour interagir avec des agents tiers, découvrir des ressources et sécuriser les transactions.

### 7.1 Délégation Réseau (A2A & ACP)
Contrairement à `delegate_task` qui instancie un sous-agent local, l'outil `delegate_to_a2a_agent` permet de soumettre des tâches à un autre agent sur le réseau en utilisant la spécification JSON-RPC 2.0 (A2A) ou REST (ACP d'IBM/BeeAI) :

```python
from tools.a2a_delegate_tool import delegate_to_a2a_agent

# Délégation d'une sous-tâche à un agent distant (ex: validateur de code API Go)
res = delegate_to_a2a_agent(
    agent_url="http://127.0.0.1:8080",
    goal="Vérifier la conformité de la structure PLC générée",
    context={"system_id": "AS6"}
)
```

### 7.2 Découverte d'Actifs (ARD)
Le standard Agentic Resource Discovery (ARD) permet d'importer dynamiquement des capacités ou des schémas d'outils indexés par un registre global :
- Le client ARD (`ARDClient`) interroge un annuaire pour enregistrer des outils à la volée.
- Le publisher ARD (`ARDPublisher`) exporte les outils d'EVA pour les rendre découvrables.

### 7.3 Commerce Autonome Sécurisé (UCP & M2A)
L'outil `ucp_shopping` gère les opérations d'agentic commerce de façon unifiée (recherche de pièces, panier, checkout). Toute action menant à des dépenses ou à des modifications système critiques est interceptée par la couche d'autorisation **Model-to-Agent/Authorization (M2A)** qui sollicite une approbation utilisateur.

---

## Liste de vérification (Checklist)

- [ ] Les sous-agents ont des périmètres d'action distincts et isolés (pas de conflit d'écriture).
- [ ] Les chemins de fichiers de sortie des sous-agents sont préfixés par identifiant unique.
- [ ] L'agent parent implémente une fonction de consolidation des résultats.
- [ ] La gestion des erreurs inclut un mécanisme de réessai avec backoff exponentiel.
- [ ] Le budget d'API de la session est vérifié avant le lancement (`iteration_budget.remaining`).
- [ ] Les dépendances séquentielles sont identifiées et exclues du parallélisme.
- [ ] Le nombre de sous-agents simultanés respecte la limite configurée (`max_concurrent_children`).
- [ ] Les secrets et informations sensibles sont exclus des consignes de délégation.
- [ ] Les rapports individuels des sous-agents sont horodatés et traçables.
- [ ] Un mécanisme de notification (log ou webhook) signale la fin de chaque phase.
- [ ] Les appels réseau A2A ou UCP impliquent une validation explicite (politique M2A).
- [ ] Les outils dynamiques découverts via ARD sont enregistrés dans le bon toolset avant d'être appelés.

