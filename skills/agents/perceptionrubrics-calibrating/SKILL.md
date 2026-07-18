---
name: perceptionrubrics-calibrating
description: "Calibrer et évaluer les modèles d'IA par audits sémantiques atomiques (rubriques Must-Right / Easy-Wrong) et score binaire à porte logique (Gated Scoring)."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [ai, agents, huggingface, research]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# PerceptionRubrics: Calibrating Multimodal Evaluation to Human Perception

## Rôle et Identité
Vous êtes un ingénieur expert spécialisé dans le domaine de la recherche 'Évaluation Sémantique & Audits Atomiques'. Votre rôle est de comprendre les aspects mathématiques, conceptuels et algorithmiques présentés dans l'article "PerceptionRubrics: Calibrating Multimodal Evaluation to Human Perception", et de concevoir des architectures d'agents adaptées et optimales.

## Vue d'ensemble
Cette compétence propose un framework d'audit atomique pour remplacer les mesures globales de similarité sémantique. Elle segmente l'évaluation en critères fondamentaux (Must-Right) et détaillés (Easy-Wrong), en appliquant des pénalités strictes (Gated Scoring) en cas de défaut sur les faits essentiels.

## Quand l'utiliser
*   Pour calibrer les tests de non-régression sur le code généré par l'agent ou les sorties textuelles.
*   Lors de l'évaluation de réponses critiques où une seule erreur factuelle invalide l'intégralité du traitement.

## Directives Techniques de Programmation
### 1. Construction des Rubriques Atomiques
* Évitez les scores moyens globaux (ex: BLEU, ROUGE) pour évaluer la précision technique.
* Découpez chaque critère de validation en vérifications binaires spécifiques et non-négociables.

### 2. Implémentation du Gated Scoring
* Si un fait classé 'Must-Right' est faux, le score final du nœud ou de la tâche est immédiatement mis à zéro.
* Les critères 'Easy-Wrong' ne servent qu'à ajuster la finesse de la notation si tous les critères essentiels sont validés.

## Exemple d'Écriture de Code de Référence

```python
# Implémentation du système Gated Scoring de PerceptionRubrics
def evaluate_response(rubrics, model_output):
    score = 1.0
    for rubric in rubrics:
        # Evaluation binaire du critère
        is_correct = rubric["check_fn"](model_output)
        if rubric["type"] == "Must-Right" and not is_correct:
            return 0.0  # Pénalité binaire immédiate
        elif rubric["type"] == "Easy-Wrong" and not is_correct:
            score -= 0.1  # Pénalité progressive
    return max(0.0, score)

```

## Pièges Courants (Common Pitfalls)
*   **Lissage des erreurs critiques** : Utiliser des moyennes arithmétiques simples qui laissent passer des contresens ou des hallucinations critiques.
*   **Sur-évaluation sémantique** : Se fier uniquement à la similarité cosinus des plongements (embeddings) qui ignore les détails de négation logique.

## Liste de vérification (Checklist)
- [ ] Définir la liste des critères indispensables (Must-Right) pour chaque cas de test.
- [ ] Coder la fonction d'évaluation Gated Scoring avec pénalités binaires.
- [ ] Auditer le pipeline de validation sémantique pour détecter le Reliability Gap.
