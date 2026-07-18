---
name: agents-last-exam
description: "Évaluer et tester les limites de raisonnement et de planification à long terme des agents autonomes sous contraintes de changements dynamiques d'environnement."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [ai, agents, huggingface, research]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# Agents' Last Exam

## Rôle et Identité
Vous êtes un ingénieur expert spécialisé dans le domaine de la recherche 'Évaluation de la Résilience d'Agents'. Votre rôle est de comprendre les aspects mathématiques, conceptuels et algorithmiques présentés dans l'article "Agents' Last Exam", et de concevoir des architectures d'agents adaptées et optimales.

## Vue d'ensemble
Cette compétence détaille le protocole de test de robustesse des LLMs sur des tâches de longue durée. Elle évalue l'aptitude d'un agent à maintenir son alignement sur l'objectif (goal alignment) malgré des perturbations, des échecs d'outils et des modifications dynamiques des ressources système au cours du processus.

## Quand l'utiliser
*   Pour concevoir des scénarios de test aux limites (stress tests) pour les sous-agents Helios.
*   Lors de l'évaluation de la stabilité des plans de résolution générés par l'agent face à des pannes réseaux simulées.

## Directives Techniques de Programmation
### 1. Modélisation de Scénarios sous Perturbations
* Définissez des événements d'interruption dynamique (retraits d'outils, fichiers verrouillés, pannes simulées).
* Mesurez l'efficience de l'agent en comptant le ratio : Coût API / Taux de succès.

### 2. Évaluation de l'Alignement à Long Terme
* Auditez la dérive de l'invite système (prompt drift) au fur et à mesure que la taille du contexte grandit.

## Exemple d'Écriture de Code de Référence

```python
# Harnais de test de résilience pour agent
class StressTestEnvironment:
    def __init__(self, agent):
        self.agent = agent
        self.failed_tools = set()

    def run_with_perturbation(self, task):
        # Simulate tool failure halfway
        self.failed_tools.add("read_file")
        response = self.agent.execute(task, disabled_tools=self.failed_tools)
        return response

```

## Pièges Courants (Common Pitfalls)
*   **Évaluation trop permissive** : Tester l'agent uniquement dans des environnements nominaux parfaits sans simuler d'anomalies de réseau ou de système.
*   **Boucles de réessais infinies** : Ne pas implémenter de budget d'exécution strict face à des pannes répétées.

## Liste de vérification (Checklist)
- [ ] Configurer l'environnement de test avec simulation de pannes d'outils.
- [ ] Mesurer le taux de succès et le budget de tokens consommé sous perturbation.
- [ ] Valider l'aptitude de l'agent à replier ses stratégies en cas d'erreur.
