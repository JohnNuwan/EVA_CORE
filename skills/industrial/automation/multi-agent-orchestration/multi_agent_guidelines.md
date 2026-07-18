# Guide d'Orchestration Multi-Agents pour les Projets d'Automatisme

Ce guide décrit la méthodologie et les meilleures pratiques pour structurer et orchestrer des tâches complexes de développement et d'audit d'automates industriels à l'aide de l'outil de délégation de sous-agents Helios (`delegate_task`).

## 1. Principes de la Délégation avec `delegate_task`

L'outil `delegate_task` permet à l'agent parent de déléguer une tâche ou un sous-ensemble de tâches à un ou plusieurs sous-agents autonomes s'exécutant dans des environnements isolés.

Il existe deux modes d'exécution :
- **Délégation simple** : Transmission d'une consigne cible (`goal`). Le sous-agent s'exécute de manière synchrone et fournit un bilan.
- **Délégation par lots (parallèle)** : Envoi d'une liste de consignes (`tasks`). Les sous-agents s'exécutent en parallèle dans la limite de la configuration `delegation.max_concurrent_children` (par défaut 3).

## 2. Découpage du Travail pour les Automates (PLC) et la SCADA

Dans les projets industriels d'envergure, le volume de données (milliers de fichiers PDF d'audit, programmes PLC volumineux) justifie l'utilisation de sous-agents pour paralléliser les traitements et optimiser le budget d'API.

### A. Découpage par Station Automate (AS)
Plutôt que de faire traiter toutes les stations par un seul agent, divisez le périmètre en attribuant chaque station (AS) ou groupe de stations à un sous-agent :
- **Sous-Agent 1** : Audit et génération de tags pour la station `AS6`.
- **Sous-Agent 2** : Audit et génération de tags pour la station `AS7`.

### B. Découpage par Phase de Cycle de Vie
Vous pouvez décomposer une tâche complexe en phases séquentielles distribuées à des sous-agents spécialisés :
1. **Phase d'Audit** : Extraction des communications PLC/EPH à partir des documents PDF.
2. **Phase de Génération** : Modélisation des variables et génération des configurations SCADA (ex. Ignition `ignition_tags.json`).
3. **Phase de Validation** : Test de connectivité simulée via le serveur MCP et validation des scripts Jython.

## 3. Exemple de Script d'Orchestration

Voici un exemple type d'orchestration en Python montrant comment l'agent parent peut diviser un audit de 2 automates et paralléliser leur exécution :

```python
# -*- coding: utf-8 -*-
"""Exemple d'orchestration multi-agents pour l'audit de stations.

Ce script illustre comment diviser le travail d'audit entre plusieurs sous-agents
de manière parallèle en utilisant l'infrastructure Helios.
"""

import json
from tools.delegate_tool import delegate_task

def orchestrer_audit_stations():
    """Divise et délègue l'audit des stations AS6 et AS7 à deux sous-agents."""
    
    taches = [
        {
            "id": "audit_as6",
            "goal": "Réaliser l'audit des fichiers PDF pour la station AS6 uniquement et générer le rapport partiel dans output/audit/as6_report.json"
        },
        {
            "id": "audit_as7",
            "goal": "Réaliser l'audit des fichiers PDF pour la station AS7 uniquement et générer le rapport partiel dans output/audit/as7_report.json"
        }
    ]
    
    print("Démarrage de la délégation parallèle pour l'audit...")
    # Lancement des sous-agents via le mécanisme de lot (tasks) de delegate_task
    resultats = delegate_task(tasks=taches)
    
    print("Traitement des résultats des sous-agents :")
    print(json.dumps(resultats, indent=2))
    
    # Phase de consolidation finale par l'agent parent
    consolider_rapports("output/audit/as6_report.json", "output/audit/as7_report.json")

def consolider_rapports(path_as6, path_as7):
    """Consolide les données extraites par les sous-agents en un rapport unique.

    Args:
        path_as6: Chemin du rapport généré pour l'AS6.
        path_as7: Chemin du rapport généré pour l'AS7.
    """
    # Logique de fusion des structures de données
    pass

if __name__ == "__main__":
    orchestrer_audit_stations()
```

## 4. Recommandations et Limites

- **Respecter la normalisation des AS** : Veiller à ce que les sous-agents utilisent les identifiants normaux à un seul chiffre pour les stations (ex: `AS6` et `AS7`, et non `AS664` ou `AS732`) pour assurer la cohérence lors de la fusion.
- **Gestion du Budget d'API** : Surveiller le coût en tokens. Les sous-agents consomment le budget d'API de la session parente. Utilisez des instructions claires et concises pour éviter que les sous-agents n'effectuent des tours de boucle inutiles.
- **Vérification d'Erreur** : Toujours analyser le rapport de retour de chaque sous-agent. Si l'un d'eux échoue, l'agent parent doit être capable de relancer la tâche spécifique ou d'isoler l'erreur sans interrompre le reste du traitement.
