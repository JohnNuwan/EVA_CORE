---
name: helios-agent-mcp-development
description: "Développer des serveurs Model Context Protocol (MCP) personnalisés pour Helios Agent."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [mcp, helios-agent, model-context-protocol, custom-tools, multi-agent, development, fastmcp, python, json-rpc, stdio]
    related_skills: [helios-agent, software-development, python-pep8, codex]
---

# Développement MCP (Model Context Protocol) pour Helios Agent

## Vue d'ensemble

Le **Model Context Protocol (MCP)** est un protocole standard ouvert qui permet aux modèles de langage (LLM) d'interagir de manière sécurisée avec des sources de données locales, des APIs et des outils système. Développé par la société Anthropic, le MCP définit un contrat d'interface clair entre l'agent (hôte MCP) et les serveurs d'outils.

Cette compétence guide la création de **serveurs MCP personnalisés en Python** à l'aide de la bibliothèque `FastMCP` (daskey/fastmcp) ou de la SDK MCP officielle, et explique comment déclarer et configurer ces serveurs dans Helios Agent.

### Architecture MCP dans Helios

```
Helios Agent
    │
    ├── Outils natifs (intégrés)
    ├── Outils skills (locaux)
    └── Serveurs MCP externes ←── Vous êtes ici
              │
        ┌─────┴─────┐
        │  STDIO    │  Communication via entrée/sortie standard (JSON-RPC)
        └─────┬─────┘
              │
    ┌─────────▼─────────┐
    │ MCP Server (Python)│  ← Votre code : outils, ressources, prompts
    │ - Outils (tools)   │
    │ - Ressources       │
    │ - Prompts          │
    └───────────────────┘
```

---

## Quand l'utiliser

### Cas d'usage

À utiliser lorsque l'utilisateur demande de :

- Créer un **outil personnalisé** ou une intégration système qui n'existe pas dans la liste des outils par défaut de Helios.
- Interfacer Helios Agent avec des **bases de données propriétaires**, des **APIs internes** ou des **équipements d'usine** (SCADA/OT).
- Mettre à disposition du modèle des **ressources en lecture seule** (rapports, fichiers de configuration, documentation métier).
- Configurer ou dépanner l'enregistrement d'un serveur MCP dans le fichier `cli-config.yaml` ou `config.yaml` de Helios.
- Développer un **écosystème multi-agents** où plusieurs spécialistes (MCP) collaborent.

### Ne pas utiliser pour

- L'utilisation basique de Helios Agent sans modification de son catalogue d'outils.
- Le développement d'API HTTP REST non compatibles avec le protocole MCP.
- Des outils qui existent déjà dans les skills intégrés Helios (vérifier d'abord).

---

## 1. Conception d'un Serveur MCP en Python (FastMCP)

### 1.1 Structure minimale

```python
# Fichier : mcp_server_custom.py
# Installation requise : pip install mcp[cli] ou fastmcp
from mcp.server.fastmcp import FastMCP
import sys
import logging

# Configuration du logging sur stderr (NE PAS polluer stdout !)
logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialisation du serveur
mcp = FastMCP("Actemium Industry Link")

@mcp.tool()
def get_machine_status(machine_id: str) -> str:
    """
    Récupère le statut actuel d'une machine de production à partir de son ID.

    Args:
        machine_id: L'identifiant unique de la machine (ex: 'PLC_01', 'PLC_02').
    """
    logger.info(f"Requête get_machine_status pour {machine_id}")
    # Simulation d'un appel à une base OT ou API d'usine
    statuses = {
        "PLC_01": "RUNNING - Vitesse: 1450 rpm - Temp: 62°C",
        "PLC_02": "STOPPED - Défaut arrêt d'urgence actif",
    }
    return statuses.get(machine_id,
                        f"Machine {machine_id} introuvable ou hors ligne")

@mcp.resource("report://production/today")
def get_daily_report() -> str:
    """Renvoie le rapport textuel de la production du jour (ressource)."""
    return "Rapport Actemium du jour : OEE global de 82.4%, aucune panne majeure."

if __name__ == "__main__":
    # Lancement du serveur (communication via STDIO)
    mcp.run()
```

### 1.2 Serveur avec dépendances et validation

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional
import json

mcp = FastMCP("API Météo Industrielle")

class WeatherQuery(BaseModel):
    city: str = Field(..., description="Nom de la ville (ex: Lyon)")
    units: Optional[str] = Field("metric", description="metric ou imperial")

@mcp.tool()
def get_weather(query: WeatherQuery) -> str:
    """
    Récupère les données météorologiques pour une ville donnée.

    Args:
        query: Paramètres de la requête (ville et unités).
    """
    # Simulation d'appel API météo
    data = {
        "city": query.city,
        "temperature": 22.5 if query.units == "metric" else 72.5,
        "humidity": 65,
        "conditions": "Partiellement nuageux"
    }
    return json.dumps(data, indent=2)

@mcp.tool()
def calculate_oee(availability: float, performance: float, quality: float) -> dict:
    """
    Calcule le taux de rendement synthétique (OEE/TRS).

    Args:
        availability: Disponibilité (0.0 - 1.0)
        performance: Performance (0.0 - 1.0)
        quality: Qualité (0.0 - 1.0)
    """
    oee = availability * performance * quality * 100
    return {
        "oee_percent": round(oee, 2),
        "availability": availability,
        "performance": performance,
        "quality": quality,
        "evaluation": "Excellent" if oee >= 85 else (
            "Bon" if oee >= 70 else "Acceptable" if oee >= 50 else "À améliorer"
        )
    }
```

---

## 2. Intégration du Serveur MCP dans Helios Agent

### 2.1 Configuration YAML

Pour enregistrer un serveur MCP personnalisé, ajouter une entrée dans la section `mcp_servers` du fichier de configuration Helios (`~/.helios/config.yaml` ou `cli-config.yaml`) :

```yaml
mcp_servers:
  actemium-industry-link:
    command: "python"
    args: ["C:/chemin/absolu/vers/mcp_server_custom.py"]
    env:
      DB_PASSWORD: "mot_de_passe_secret"
      API_ENDPOINT: "https://api.usine.local"
    # Optionnel : activer uniquement dans certains contextes
    # enabled: true
    # timeout: 30

  api-meteo:
    command: "python"
    args: ["/chemin/absolu/vers/meteo_server.py"]
```

### 2.2 Vérification et test

```bash
# Vérifier que le serveur est détecté et que ses outils sont chargés
helios doctor

# Tester un outil MCP via le chat
helios chat -q "Quel est le statut de la machine PLC_01 ?"

# Voir les logs MCP (sur stderr) :
helios chat --verbose -q "..."
```

### 2.3 Structure recommandée pour un projet MCP

```
mon-projet-mcp/
├── server.py              # Point d'entrée du serveur MCP
├── tools/
│   ├── __init__.py
│   ├── plc_tools.py       # Outils liés aux automates
│   └── quality_tools.py   # Outils qualité/OEE
├── resources/
│   ├── __init__.py
│   └── reports.py         # Ressources (rapports en lecture seule)
├── models/
│   ├── __init__.py
│   └── schemas.py         # Modèles Pydantic pour validation
├── utils/
│   ├── __init__.py
│   ├── db.py              # Connexion base de données
│   └── logging_config.py  # Configuration logging (stderr)
├── requirements.txt       # Dépendances Python
└── README.md              # Documentation
```

---

## 3. Ressources et Prompts MCP

### 3.1 Ressources (lecture seule)

Les ressources permettent d'exposer des données structurées (fichiers, rapports, configurations) :

```python
@mcp.resource("config://plc/defaults")
def get_plc_defaults() -> str:
    """Paramètres par défaut pour la configuration des automates."""
    return json.dumps({
        "watchdog_timeout_ms": 500,
        "retry_count": 3,
        "default_broker": "mqtt://192.168.1.10:1883"
    })

@mcp.resource("docs://api/reference")
def get_api_docs() -> str:
    """Documentation de référence de l'API d'usine."""
    with open("/chemin/absolu/vers/api_reference.md", "r") as f:
        return f.read()
```

### 3.2 Prompts (modèles réutilisables)

Les prompts MCP sont des templates de messages qui guident le LLM :

```python
@mcp.prompt()
def diagnose_plc_error(error_code: str) -> str:
    """Génère un prompt de diagnostic pour une erreur automate.

    Args:
        error_code: Code d'erreur à diagnostiquer.
    """
    return f"""
Tu es un expert en diagnostic d'automates industriels.
Analyse le code d'erreur suivant et propose des actions correctives :

Code erreur : {error_code}

Format de réponse :
1. Description de l'erreur
2. Causes possibles
3. Actions correctives immédiates
4. Actions correctives à long terme
"""
```

---

## 4. Bonnes pratiques de développement

### 4.1 Logging (sur stderr uniquement)

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,  # CRITIQUE : ne pas utiliser sys.stdout
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)
```

### 4.2 Gestion des erreurs

```python
from mcp.server.fastmcp import FastMCP
import traceback

mcp = FastMCP("Robust Server")

@mcp.tool()
def read_database(query: str) -> str:
    """Lecture sécurisée d'une base de données."""
    try:
        # Tentative de connexion et lecture
        result = execute_query(query)
        return str(result)
    except ConnectionError as e:
        logger.error(f"Erreur de connexion DB: {e}")
        return "ERREUR: Base de données inaccessible. Vérifier la connexion réseau."
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}\n{traceback.format_exc()}")
        return f"ERREUR: {str(e)}"
```

---

## Pièges Courants (Common Pitfalls)

1. **Pollution du flux de communication STDIO :**
   * *Erreur :* Ajouter des déclarations `print("Début du traitement...")` dans le code du serveur. Cela pollue le canal `stdout` que le protocole MCP utilise pour échanger ses messages JSON-RPC, provoquant le plantage de l'intégration dans Helios.
   * *Correction :* Utiliser exclusivement le logging Python configuré sur `sys.stderr`. Exemple : `logging.basicConfig(level=logging.INFO, stream=sys.stderr)`.

2. **Types de paramètres non typés ou sans description :**
   * *Erreur :* Ne pas typer les arguments de la fonction décorée avec `@mcp.tool()`, ni fournir de docstring. Le LLM ne saura pas comment ni quand appeler l'outil et l'ignorera.
   * *Correction :* Toujours documenter le but de la fonction et chacun de ses arguments avec des docstrings clairs et spécifier les annotations de type (ex: `machine_id: str`). Ajouter des descriptions Pydantic `Field` pour les modèles complexes.

3. **Absence de chemins absolus dans la configuration :**
   * *Erreur :* Utiliser des chemins relatifs dans `config.yaml`. Si Helios est lancé depuis un autre répertoire, le script ne sera pas trouvé.
   * *Correction :* Toujours utiliser des chemins absolus : `C:/Users/utilisateur/projet/mcp_server_custom.py`.

4. **Timeout trop court pour les outils longs :**
   * *Erreur :* Un outil MCP qui prend plus de 30 secondes (ex: analyse de gros fichiers) est tué par Helios avant d'avoir terminé.
   * *Correction :* Augmenter le timeout dans la configuration YAML : `timeout: 120`. Pour les opérations très longues, envisager un mécanisme asynchrone (file d'attente, callback).

5. **Décorateur manquant pour les outils :**
   * *Erreur :* Définir une fonction dans le fichier serveur mais oublier le décorateur `@mcp.tool()`. La fonction existe mais n'est pas exposée comme outil.
   * *Correction :* Vérifier que chaque fonction destinée à être un outil porte le décorateur `@mcp.tool()`. Vérifier avec `helios doctor` que l'outil est bien listé.

6. **Dépendances manquantes dans l'environnement Helios :**
   * *Erreur :* Le serveur importe des bibliothèques qui ne sont pas installées dans le `.venv` du projet Helios.
   * *Correction :* Installer les dépendances avec `pip install -r requirements.txt` ou les déclarer dans le script lui-même avec un message d'erreur explicite en cas d'import manquant.

---

## Liste de vérification (Checklist)

- [ ] La fonction du serveur MCP possède des annotations de type explicites pour tous ses paramètres.
- [ ] La docstring décrit clairement l'usage de l'outil et ses arguments pour guider le LLM.
- [ ] Aucun `print()` n'écrit sur `stdout` en dehors de la boucle principale MCP. Les logs écrivent sur `stderr`.
- [ ] Le serveur MCP est configuré avec un chemin absolu dans la configuration Helios.
- [ ] La commande `helios doctor` confirme que le serveur est joignable et charge ses outils.
- [ ] Les dépendances Python sont installées dans l'environnement Helios.
- [ ] Le timeout est adapté à la durée d'exécution des outils (valeur par défaut ou surchargée).
- [ ] Les modèles Pydantic (si utilisés) ont des descriptions de champ avec `Field(description=...)`.
- [ ] La gestion d'erreur retourne des messages explicites au LLM (pas de stack trace brute).
- [ ] Les ressources sont documentées avec leur URI et leur format de retour.

