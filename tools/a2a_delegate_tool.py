"""Outil de délégation de tâches inter-agents (A2A)."""

import json
import time
import httpx
import logging
from typing import Dict, Any, Optional
from tools.registry import registry

logger = logging.getLogger(__name__)

A2A_DELEGATE_SCHEMA = {
    "name": "delegate_to_a2a_agent",
    "description": "Délègue un sous-but à un autre agent compatible A2A sur le réseau et récupère le résultat.",
    "parameters": {
        "type": "object",
        "properties": {
            "agent_url": {
                "type": "string",
                "description": "L'URL HTTP de base ou endpoint A2A de l'agent distant (ex: 'http://127.0.0.1:8080')"
            },
            "goal": {
                "type": "string",
                "description": "Le but précis ou consigne à confier à l'agent distant"
            },
            "context": {
                "type": "object",
                "description": "Variables de contexte additionnelles sous forme de dictionnaire clé-valeur"
            }
        },
        "required": ["agent_url", "goal"]
    }
}

def _handle_a2a_delegate(args: Dict[str, Any], **kwargs) -> str:
    """Gestionnaire d'exécution de la délégation de tâches A2A."""
    agent_url = args.get("agent_url", "").rstrip("/")
    goal = args.get("goal")
    context = args.get("context", {})
    
    # Construction de l'URL pour créer la tâche
    tasks_url = f"{agent_url}/a2a/tasks"
    
    try:
        logger.info("Délégation de la tâche à l'agent A2A distant %s", tasks_url)
        # Création de la tâche A2A
        with httpx.Client() as client:
            response = client.post(
                tasks_url,
                json={"goal": goal, "context": context},
                timeout=10.0
            )
            
            if response.status_code != 200:
                return json.dumps({
                    "success": False,
                    "error": f"Échec de création de la tâche A2A (HTTP {response.status_code}): {response.text}"
                })
                
            task_data = response.json()
            task_id = task_data.get("id")
            status = task_data.get("status", "pending")
            
            logger.info("Tâche A2A créée avec succès. ID: %s. Statut: %s", task_id, status)
            
            # Polling du statut de la tâche (limité à 60 secondes pour éviter de bloquer indéfiniment)
            max_polling_time = 60
            polling_interval = 2
            elapsed_time = 0
            
            while status in {"pending", "running"} and elapsed_time < max_polling_time:
                time.sleep(polling_interval)
                elapsed_time += polling_interval
                
                status_response = client.get(f"{tasks_url}/{task_id}", timeout=5.0)
                if status_response.status_code == 200:
                    task_data = status_response.json()
                    status = task_data.get("status")
                    logger.debug("Mise à jour statut tâche A2A %s: %s", task_id, status)
                else:
                    logger.warning("Échec de polling du statut A2A (HTTP %s)", status_response.status_code)
            
            if status == "completed":
                return json.dumps({
                    "success": True,
                    "status": "completed",
                    "result": task_data.get("result")
                }, ensure_ascii=False)
            elif status == "failed":
                return json.dumps({
                    "success": False,
                    "status": "failed",
                    "error": task_data.get("result", "Échec de l'agent distant")
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "success": False,
                    "status": status,
                    "error": "Dépassement du délai d'attente (timeout) ou statut inconnu."
                })
                
    except Exception as e:
        logger.exception("Erreur lors de la communication A2A: %s", e)
        return json.dumps({
            "success": False,
            "error": f"Erreur de transport réseau / protocole A2A: {str(e)}"
        })

# Enregistrement de l'outil dans le registre
registry.register(
    name="delegate_to_a2a_agent",
    toolset="delegation",
    schema=A2A_DELEGATE_SCHEMA,
    handler=_handle_a2a_delegate,
    check_fn=lambda: True,
    requires_env=[]
)
