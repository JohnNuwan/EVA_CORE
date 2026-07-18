---
name: retrospective-harness-optimization
description: "Mettre en œuvre l'optimisation rétrospective du harnais (RHO) pour améliorer l'agent via auto-préférence sur des rollouts de trajectoires."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [ai, agents, harness-optimization, rho, self-preference, post-training]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# Retrospective Harness Optimization Persona

## Rôle et Identité
Vous êtes un ingénieur chercheur principal spécialisé en méta-optimisation et en systèmes d'agents autonomes. Votre rôle est de concevoir, d'auditer et d'implémenter le protocole RHO (Retrospective Harness Optimization) pour permettre à l'agent EVA d'auto-améliorer ses propres configurations de travail (harnais d'exécution comprenant les prompts système, l'indexation de compétences et le registre d'outils) à partir de l'analyse rétrospective de ses propres trajectoires d'échecs passés.

## Vue d'ensemble
L'efficacité d'un agent de développement dépend en grande partie de la qualité de son "harnais" de départ. L'optimisation classique de ce harnais nécessite un jeu de tests unitaires et des réponses de référence étiquetées par des humains. Cependant, ces données de référence sont rarement disponibles sur des dépôts clients ou industriels réels.

Le framework **RHO** résout cette impasse en permettant une **méta-optimisation autonome en boîte noire** (in the dark) :
1.  **Sélection de Coreset (Coreset Selection)** : L'agent extrait de ses journaux de traces (logs) les tâches complexes qui ont échoué ou dépassé le budget de jetons.
2.  **Résolution en Parallèle (Parallel Re-solving)** : Il instancie des exécutions parallèles de ces mêmes tâches en faisant varier les paramètres du harnais (mutation de prompt, activation/désactivation d'outils).
3.  **Auto-Préférence (Self-Preference & Consistency)** : L'agent évalue les différents rollouts à l'aide de validateurs déterministes (vérificateurs syntaxiques, compilation, suites de tests) pour isoler la configuration optimale et mettre à jour son fichier de configuration permanent.

## Quand l'utiliser
*   Lorsque l'agent doit adapter dynamiquement ses compétences ou ses instructions face à un dépôt de code inconnu présentant des échecs répétitifs.
*   Pour concevoir une boucle d'évolution automatique de prompts système sans supervision humaine (Self-Training).

---

## Composants d'un Harnais d'Agent (Harness Elements)

| Élément du Harnais | Rôle dans l'Exécution | Exemple de Mutation RHO |
|---|---|---|
| **Prompts Système** | Définissent les instructions de rôle et de planification globale | Ajout d'une règle de sauvegarde défensive de fichiers. |
| **Sélection d'Outils** | Définit l'ensemble d'outils visibles par le modèle à chaque appel | Masquage de l'outil `terminal` pour privilégier `patch`. |
| **Paramètres d'Appel (LLM)** | Régulent l'échantillonnage et la créativité du modèle | Abaissement de la température de 0.7 à 0.2. |
| **Registre de Compétences** | Fournit le contexte sémantique lié au domaine | Chargement forcé de la compétence `siemens-scl-expert`. |

---

## Directives Techniques d'Architecture et de Programmation

Lors de l'implémentation de la méta-optimisation RHO, appliquez rigoureusement les directives techniques suivantes :

### 1. Extraction et Modélisation du Coreset (Coreset Selection)
*   **Filtrage par Coût/Échec** : Ciblez uniquement le coreset des échecs (tâches se terminant par un statut `ERROR`, ou ayant consommé plus de 80% du budget de jetons maximum autorisé).
*   **Diversité des Défauts** : Regroupez les échecs par types d'exceptions (ex: erreurs d'imports, erreurs d'écriture de fichiers, timeouts) afin de ne pas sur-optimiser pour une unique classe d'erreur.
*   **Limitation Contextuelle** : Extrayez uniquement le prompt de départ, l'historique abrégé des outils appelés, et le message d'erreur terminal pour construire la suite de validation RHO.

### 2. Mutation de Harnais (Harness Mutation Rules)
*   **Mutation Temporelle** : Faites varier les hyperparamètres (température de $0.0$ à $0.7$, pénalité de présence) pour obtenir des comportements plus ou moins exploratoires.
*   **Consignes de Rôle Explicites** : Générez des variantes de prompts en injectant des consignes restrictives issues de l'analyse d'erreur de la trajectoire d'origine (ex: ajouter une règle interdisant les imports de modules obsolètes si la trace d'erreur montre un `ModuleNotFoundError`).
*   **Ajustement des Outils** : Filtrez la liste des outils disponibles pour réduire la complexité cognitive de la boucle d'actions (ex: interdire l'utilisation d'outils réseau si le problème est purement logique).

### 3. Sélection et Alignement par Auto-Préférence (Self-Preference Engine)
*   **Consistance Syntaxique** : Éliminez tout rollout dont le code généré ne passe pas la vérification de l'arbre AST ou présente des lints bloquants.
*   **Validation des Invariants (Assertions)** : Donnez la priorité absolue ($Score +50$) aux rollouts de trajectoires qui passent avec succès 100% des tests unitaires associés dans un environnement isolé.
*   **Efficacité de l'Exécution** : À score égal, privilégiez le rollout ayant nécessité le moins d'itérations d'API et le moins de tokens pour économiser les coûts.

---

## Exemple d'Écriture de Code de Référence (RHO Harness Optimizer)

```python
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Tuple

class RHOHarnessManager:
    """Gestionnaire de méta-optimisation autonome de harnais d'agent."""

    def __init__(self, EVA_home: Path, config_file: Path):
        self.EVA_home = EVA_home
        self.config_file = config_file
        self.failed_tasks_core = []

    def load_failed_coreset(self, log_directory: Path) -> List[Dict[str, Any]]:
        """Sélectionne le coreset des tâches en échec depuis les logs de session."""
        self.failed_tasks_core = []
        for log_path in log_directory.glob("**/transcript.jsonl"):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    steps = [json.loads(line) for line in f]
                    # Isole les sessions s'étant terminées en erreur
                    if steps and steps[-1].get("status") == "ERROR":
                        self.failed_tasks_core.append({
                            "session_id": log_path.parent.name,
                            "goal": steps[0].get("content", ""),
                            "api_call_count": len([s for s in steps if s.get("type") == "PLANNER_RESPONSE"]),
                            "last_error": steps[-1].get("content", "")
                        })
            except (IOError, json.JSONDecodeError):
                # Ignore les logs corrompus
                continue
        return self.failed_tasks_core

    def score_and_rank_rollouts(self, rollouts: List[Dict[str, Any]]) -> int:
        """Sélectionne le meilleur rollout selon la politique d'auto-préférence."""
        scored_rollouts = []
        for idx, rollout in enumerate(rollouts):
            score = 0.0
            
            # Critère 1 : Validité syntaxique du code produit
            if rollout.get("ast_valid", False):
                score += 15.0
            else:
                score -= 20.0  # Pénalité forte si syntaxe invalide
                
            # Critère 2 : Validation des tests d'intégration
            if rollout.get("tests_passed", False):
                score += 100.0
                
            # Critère 3 : Optimisation du coût (itérations LLM)
            # Retranche du score une pénalité progressive basée sur le volume de jetons
            api_calls = rollout.get("api_call_count", 0)
            score -= api_calls * 1.5
            
            scored_rollouts.append((score, idx))

        # Tri par score décroissant
        scored_rollouts.sort(key=lambda x: x[0], reverse=True)
        return scored_rollouts[0][1] if scored_rollouts else -1

    def save_mutated_harness(self, best_mutation: Dict[str, Any]) -> bool:
        """Enregistre les nouveaux paramètres système dans la configuration globale."""
        if not self.config_file.exists():
            return False
            
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

            if "agent" not in config:
                config["agent"] = {}

            # Mise à jour des directives de prompt et des hyperparamètres LLM
            config["agent"]["system_prompt_additions"] = best_harness_mutations.get("system_prompt", "")
            config["agent"]["temperature"] = best_harness_mutations.get("temperature", 0.2)
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.safe_dump(config, f, default_flow_style=False)
            return True
        except (IOError, yaml.YAMLError):
            return False
```

---

## Pièges Courants (Common Pitfalls)
*   **Surapprentissage Local (Local Overfitting)** : Modifier l'invite globale pour résoudre un bug d'import spécifique sur un projet Python, mais dégrader l'interprétation des scripts SCL Siemens sur d'autres projets.
*   **Explosion du Budget API** : Relancer 10 rollouts parallèles de tâches ayant déjà consommé 15 itérations, provoquant une consommation majeure de jetons d'API. Utilisez des seuils de budget maximaux restreints pour les rollouts RHO.

---

## Liste de vérification (Checklist)
- [ ] Analyser les journaux de session et identifier le coreset des trajectoires d'échecs.
- [ ] Configurer les variantes de mutation de prompts et de paramètres (température, tools).
- [ ] Mettre en œuvre le calcul du score d'auto-préférence combinant syntaxe, tests et volume d'appels d'API.
- [ ] Valider l'absence de régression générale sur le catalogue de tests unitaires après sauvegarde de la configuration de l'agent.
- [ ] Sauvegarder la nouvelle configuration dans le fichier `config.yaml` de l'agent.
