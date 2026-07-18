---
name: industrial-diagnostic
description: "Diagnostiquer des pannes industrielles via SQL et RAG local sur documentation technique."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags:
      - industrial
      - diagnostic
      - sql
      - rag
      - troubleshooting
      - extruder
      - maintenance
      - industrie-4.0
      - analyse-panne
      - base-de-connaissance
    related_skills:
      - industrial-audit
      - isa95-modelling
      - ot-audit
      - plc-connectivity
---

# Diagnostic Industriel par Analyse d'Alarmes et Recherche Documentaire

## Vue d'ensemble

Cette compétence permet de réaliser un diagnostic complet de panne sur des machines industrielles en combinant deux approches complémentaires :

1. **Analyse d'alarmes SQL/SQLite** — Filtre et extrait les historiques d'alarmes récents d'une machine (messages FIFO, horodatage, code erreur, sévérité) pour identifier les séquences d'événements ayant conduit à l'arrêt.

2. **RAG local (Retrieval-Augmented Generation)** — Interroge la documentation technique (fichiers PDF, manuels, spécifications) pour identifier les causes racines possibles, les actions correctives documentées et les mesures de prévention recommandées par le fabricant.

Le diagnostic est produit sous forme d'un rapport Markdown structuré comprenant : un résumé exécutif, la chronologie des alarmes, l'analyse des causes racines (RCA), les actions correctives immédiates, et les recommandations de maintenance préventive.

### Architecture du système

```
┌─────────────────────────────────────────────────────────────┐
│                  DiagnosticAgent                            │
│  ┌─────────────────────┐      ┌─────────────────────────┐   │
│  │   Analyseur SQL     │      │   Moteur RAG Local      │   │
│  │  ┌───────────────┐  │      │  ┌───────────────────┐  │   │
│  │  │ Base d'alarmes │  │      │  │ Documentation     │  │   │
│  │  │ (SQLite/MySQL) │  │      │  │ technique (PDF)   │  │   │
│  │  └───────────────┘  │      │  └───────────────────┘  │   │
│  │         │           │      │         │               │   │
│  │  ┌──────▼───────┐   │      │  ┌──────▼───────┐      │   │
│  │  │  Requêtes    │   │      │  │  Embeddings  │      │   │
│  │  │  temporelles │   │      │  │  & Recherche │      │   │
│  │  └──────────────┘   │      │  └──────────────┘      │   │
│  └─────────────────────┘      └─────────────────────────┘   │
│         │                           │                       │
│         └──────────┬───────────────┘                       │
│                    ▼                                        │
│      ┌────────────────────────┐                             │
│      │ Rapport de diagnostic  │                             │
│      │ (Markdown structuré)   │                             │
│      └────────────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

## Quand l'utiliser

### À utiliser lorsque l'utilisateur demande de :

- Diagnostiquer une panne ou un dysfonctionnement sur une machine industrielle (ex : « L'extrudeur est en panne », « Le four de la Ligne 1 est en surchauffe »).
- Analyser un historique d'alarmes pour identifier une cause racine (RCA — Root Cause Analysis).
- Rechercher des guides de maintenance, des actions correctives ou des procédures de dépannage dans la documentation technique.
- Corréler des événements d'alarmes avec des intervalles de maintenance planifiée.
- Générer un rapport de diagnostic structuré pour un suivi d'incident.

### Ne pas utiliser pour :

- La programmation d'automates PLC ou la génération de code source automate (utiliser les compétences `siemens-scl`, `rockwell-studio5000`, `plc-converter` ou `automation-linter`).
- La maintenance préventive planifiée sans composante d'analyse de données (utiliser `industrial-maintenance-preventive`).
- Le pilotage en temps réel de machines (latence trop élevée ; privilégier une supervision SCADA dédiée).
- La configuration de bases de données SQL ou l'administration système.

---

## 1. Installation et Dépendances

### Prérequis

- Python 3.10 ou supérieur.
- Bibliothèques Python : `pypdf`, `sqlalchemy`, `numpy`, `openai` (ou tout client LLM compatible).

```bash
pip install pypdf sqlalchemy numpy openai
```

> **Note :** Si `pypdf` n'est pas installé, le script tente une installation automatique au premier lancement. Il est recommandé de l'installer à l'avance pour éviter des délais.

### Structure des données attendue

```
client_data/
├── alarms.db              # Base SQLite des alarmes (optionnelle)
├── ROH/                   # Documentation technique (PDF)
│   ├── extrudeur_manuel_maintenance.pdf
│   ├── four_specifications_techniques.pdf
│   └── pompe_guide_depannage.pdf
└── schema.sql             # Schéma de la base optionnelle
```

---

## 2. Utilisation en Ligne de Commande

Le script [`diagnostic_agent.py`](scripts/diagnostic_agent.py) est le point d'entrée principal :

```bash
python skills/industrial/automation/industrial-diagnostic/scripts/diagnostic_agent.py \
    --prompt "Le four de la Ligne 1 est en surchauffe" \
    --verbose \
    --output ./rapport_diagnostic.md
```

### Arguments disponibles

| Argument | Court | Description | Défaut |
| :--- | :--- | :--- | :--- |
| `--prompt` | `-p` | Description textuelle de la panne ou anomalie | *(obligatoire)* |
| `--verbose` | `-v` | Active les logs détaillés (trace des recherches RAG et requêtes SQL) | `False` |
| `--output` | `-o` | Chemin du fichier Markdown généré | `output/diagnostic/YYYY-MM-DD_HH-MM-SS/diagnostic_report.md` |
| `--db-path` | `-d` | Chemin vers la base SQLite d'alarmes | `client_data/alarms.db` |
| `--docs-path` | | Dossier contenant les PDF de documentation | `client_data/ROH/` |

---

## 3. Utilisation en tant que Bibliothèque Python

```python
from skills.industrial.automation.industrial_diagnostic.scripts.diagnostic_agent import DiagnosticAgent
from sqlalchemy import create_engine

# Initialisation du moteur SQL (SQLite ou autre)
engine = create_engine("sqlite:///client_data/alarms.db")

# Instanciation de l'agent
agent = DiagnosticAgent(
    llm=llm_instance,           # Instance d'un LLM compatible (ex: OpenAI, Anthropic)
    db_engine=engine,           # Moteur SQLAlchemy
    docs_path="client_data/ROH/",  # Dossier de documentation
    top_k=5                     # Nombre de segments RAG à récupérer
)

# Exécution synchrone
result = await agent.run(prompt="L'extrudeur émet un bruit anormal et vibre")

# Exploitation du résultat
print(f"Machine détectée : {result.machine}")
print(f"Diagnostic : {result.diagnosis}")
print(f"Actions correctives : {result.corrective_actions}")
print(f"Probabilité estimée : {result.confidence:.0%}")
```

### Structure de l'objet `AgentResponse`

```python
@dataclass
class AgentResponse:
    machine: str                # Machine identifiée (ex: "Extrudeur Ligne 2")
    diagnosis: str              # Diagnostic textuel complet
    alarm_sequence: list[dict]  # Séquence d'alarmes ayant conduit à la panne
    corrective_actions: list[str]  # Liste d'actions recommandées
    preventive_measures: list[str] # Mesures de prévention
    confidence: float           # Niveau de confiance du diagnostic (0-1)
    sources: list[str]          # Sources documentaires consultées
    raw_alarm_data: list[dict]  # Données d'alarmes brutes
```

---

## 4. Analyse d'Alarmes par Requêtes SQL

### 4.1 Schéma de base recommandé

```sql
CREATE TABLE IF NOT EXISTS alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    machine TEXT NOT NULL,           -- Identifiant de la machine
    timestamp DATETIME NOT NULL,     -- Horodatage de l'alarme
    alarm_code TEXT NOT NULL,        -- Code de l'alarme (ex: "OVT-001")
    severity INTEGER DEFAULT 1,      -- 1=info, 2=warning, 3=critical
    message TEXT,                    -- Message lisible
    status TEXT DEFAULT 'active',    -- active / acknowledged / cleared
    FOREIGN KEY (machine) REFERENCES machines(id)
);
```

### 4.2 Requêtes types pour le diagnostic

```sql
-- Extraction des alarmes récentes pour une machine spécifique
SELECT timestamp, alarm_code, severity, message
FROM alarms
WHERE machine = 'EXTRUDEUR_L2'
  AND timestamp >= datetime('now', '-24 hours')
ORDER BY timestamp DESC;

-- Identification des alarmes les plus fréquentes sur les 7 derniers jours
SELECT alarm_code, message, COUNT(*) as occurrence,
       MAX(severity) as max_severity
FROM alarms
WHERE machine = 'EXTRUDEUR_L2'
  AND timestamp >= datetime('now', '-7 days')
GROUP BY alarm_code
ORDER BY occurrence DESC, max_severity DESC
LIMIT 20;

-- Corrélation temporelle : alarmes survenues dans une fenêtre de 5 minutes
-- avant et après un événement critique
SELECT a1.timestamp, a1.alarm_code, a1.message
FROM alarms a1
WHERE a1.machine = 'EXTRUDEUR_L2'
  AND a1.timestamp BETWEEN
      (SELECT timestamp FROM alarms
       WHERE machine = 'EXTRUDEUR_L2' AND alarm_code = 'EMERGENCY_STOP'
       ORDER BY timestamp DESC LIMIT 1)
      AND datetime(
          (SELECT timestamp FROM alarms
           WHERE machine = 'EXTRUDEUR_L2' AND alarm_code = 'EMERGENCY_STOP'
           ORDER BY timestamp DESC LIMIT 1),
          '+5 minutes'
      )
ORDER BY a1.timestamp;
```

### 4.3 Interprétation des séquences d'alarmes

L'agent analyse les séquences d'alarmes selon les motifs suivants :

- **Motif en cascade** : Une alarme racine (ex: surpression hydraulique) déclenche des alarmes secondaires (ex: température excessive, vibration). L'agent identifie la première occurrence comme cause probable.
- **Motif cyclique** : Des alarmes qui se répètent à intervalles réguliers suggèrent un défaut intermittent ou un paramétrage inapproprié des seuils.
- **Motif de confirmation** : Deux alarmes redondantes provenant de capteurs différents confirment une même défaillance (ex: pression ET débit anormaux).

---

## 5. Recherche Documentaire (RAG Local)

### 5.1 Principe de fonctionnement

Le moteur RAG local suit ce pipeline :

1. **Extraction** : Lecture des fichiers PDF dans le dossier de documentation via `pypdf`.
2. **Découpage** : Segmentation en chunks de ~500 caractères avec recouvrement de 50 caractères pour préserver le contexte.
3. **Vectorisation** : Calcul des embeddings pour chaque chunk (modèle local via `sentence-transformers` ou API distante).
4. **Recherche** : Pour un prompt donné, calcul de la similarité cosinus entre l'embedding de la requête et ceux des chunks.
5. **Reranking** : Les top-K chunks sont rerankés selon leur pertinence contextuelle.

### 5.2 Reranking contextuel avancé

```python
def rerank_chunks(query_embedding: list[float],
                  chunks: list[dict],
                  llm_client) -> list[dict]:
    """Reranke les chunks selon leur pertinence contextuelle via LLM."""
    scored_chunks = []
    for chunk in chunks:
        prompt = f"""Évalue la pertinence de ce passage technique pour la question posée.
Question : {query_embedding}
Passage : {chunk['text']}
Score (0-10) :"""
        response = llm_client.complete(prompt)
        chunk['relevance_score'] = extract_score(response)
        scored_chunks.append(chunk)

    return sorted(scored_chunks,
                  key=lambda x: x['relevance_score'],
                  reverse=True)[:5]
```

### 5.3 Structure des documents attendus

Les PDF doivent être organisés par machine dans le dossier `client_data/ROH/` :

```
client_data/ROH/
├── EXTRUDEUR_L1/
│   ├── manuel_operation.pdf
│   ├── guide_maintenance.pdf
│   └── schema_electrique.pdf
├── FOUR_L1/
│   ├── specification_technique.pdf
│   └── procedure_calibration.pdf
└── POMPE_VIDANGE/
    ├── fiche_technique.pdf
    └── historique_pannes.pdf
```

---

## 6. Rapport de Diagnostic Généré

Le rapport Markdown produit suit ce gabarit :

```markdown
# Rapport de Diagnostic Industriel

**Machine :** Extrudeur Ligne 2
**Date :** 2026-06-24 14:30
**Prompt initial :** L'extrudeur est en panne

## Résumé Exécutif

---

## Chronologie des Alarmes

| Horodatage | Code | Sévérité | Message |
| :--- | :--- | :--- | :--- |

## Analyse des Causes Racines (RCA)

### Cause primaire identifiée
...

### Facteurs contributifs
- ...

## Actions Correctives Immédiates

1. ...
2. ...

## Recommandations de Maintenance Préventive

- ...

## Sources Documentaires Consultées

- [manuel_operation.pdf](client_data/ROH/EXTRUDEUR_L1/manuel_operation.pdf)
```

---

## 7. Mode Simulation / Test

Si aucune base SQL n'est fournie, le script initialise automatiquement une base SQLite locale (`client_data/alarms.db`) contenant des alarmes de simulation réalistes pour l'extrudeuse :

```python
# Alarme simulée pour test
alarms = [
    {"machine": "EXTRUDEUR_L2", "timestamp": "2026-06-24 13:45",
     "alarm_code": "OVT-001", "severity": 2,
     "message": "Température moteur excessive (>85°C)"},
    {"machine": "EXTRUDEUR_L2", "timestamp": "2026-06-24 13:46",
     "alarm_code": "VIB-003", "severity": 3,
     "message": "Vibration anormale palier aval (>12 mm/s)"},
    {"machine": "EXTRUDEUR_L2", "timestamp": "2026-06-24 13:47",
     "alarm_code": "EMERGENCY_STOP", "severity": 3,
     "message": "Arrêt d'urgence déclenché (survitesse vis)"},
]
```

---

## Pièges Courants (Common Pitfalls)

1. **Absence de base d'alarmes** : Si la base n'existe pas, l'agent utilise des données simulées. Pour un diagnostic réel, fournir une base avec `--db-path` ou configurer l'URL de connexion.

2. **Dépendances manquantes** : `pypdf` est requis pour l'extraction de texte des PDF. L'installation automatique peut échouer dans des environnements restreints.

3. **Documentation insuffisante** : Le RAG nécessite au moins un PDF pertinent par machine. Sans documentation, l'agent se limite à l'analyse SQL.

4. **Fenêtre temporelle trop courte** : L'analyse par défaut porte sur les 24 dernières heures. Pour des pannes intermittentes, étendre la fenêtre à 7 ou 30 jours avec un paramètre `--window-hours`.

5. **Confusion entre corrélation et causalité** : Le RAG peut suggérer des causes documentées qui ne sont pas nécessairement en lien avec l'incident actuel. Toujours valider par un expert métier.

6. **Empreinte mémoire des PDF volumineux** : Des manuels de plusieurs centaines de pages peuvent saturer la mémoire du processus RAG. Utiliser un préfiltrage par table des matières si possible.

---

## Liste de vérification (Checklist)

- [ ] L'agent de diagnostic s'instancie sans erreur (`DiagnosticAgent(llm=..., db_engine=...)`).
- [ ] Le prompt est analysé et la machine correcte est détectée (ex: `"EXTRUDEUR_L2"`).
- [ ] La base d'alarmes est accessible et contient des données dans la fenêtre temporelle configurée.
- [ ] Le RAG extrait les pages pertinentes du dossier `client_data/ROH/`.
- [ ] Les séquences d'alarmes sont correctement ordonnées chronologiquement.
- [ ] Le rapport distingue clairement cause racine, facteurs contributifs et symptômes.
- [ ] Les actions correctives proposées sont référencées dans la documentation (traçables).
- [ ] Aucune information sensible (identifiants, chemins internes) n'est divulguée dans le rapport.
- [ ] Le niveau de confiance (`confidence`) est calibré de manière réaliste (ne pas annoncer 100%).
- [ ] La sortie `--verbose` permet de tracer les étapes du diagnostic pour débogage.

