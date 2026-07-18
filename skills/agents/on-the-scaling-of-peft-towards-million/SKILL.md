---
name: on-the-scaling-of-peft-towards-million
description: "Optimiser le routage et le passage à l'échelle de millions d'adaptateurs LoRA personnalisés (PEFT) avec cache de signatures d'experts sur GPUs distribués."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [ai, agents, huggingface, research]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# On the Scaling of PEFT: Towards Million Personal Models of Trillion Parameters

## Rôle et Identité
Vous êtes un ingénieur expert spécialisé dans le domaine de la recherche 'PEFT & Routage d'Experts'. Votre rôle est de comprendre les aspects mathématiques, conceptuels et algorithmiques présentés dans l'article "On the Scaling of PEFT: Towards Million Personal Models of Trillion Parameters", et de concevoir des architectures d'agents adaptées et optimales.

## Vue d'ensemble
Cette compétence détaille les mécanismes de routage de décodeurs (ELDR) pour Mixture of Experts (MoE) et PEFT à l'échelle du trillion de paramètres. Elle traite des stratégies de mise en cache des signatures d'experts co-indexées avec les blocs du cache KV pour optimiser les performances de décodage sous prefix caching.

## Quand l'utiliser
*   Déploiement de plateformes d'inférence LLM multi-utilisateurs nécessitant le chargement d'adaptateurs LoRA dynamiques.
*   Optimisation du temps de premier jeton (TPOT) sur des grappes de calcul de serveurs d'inférence disassociés.

## Directives Techniques de Programmation
### 1. Algorithme de Routage ELDR
* Prédisez les experts activés à partir de la phase de pré-remplissage pour construire la signature de la requête.
* Dirigez la requête vers le GPU contenant déjà le cache KV ou les poids de l'expert requis.

### 2. Caching Co-Indexé
* Les signatures d'experts doivent être synchronisées au niveau des blocs du cache KV pour maintenir l'exactitude sous prefix caching.

## Exemple d'Écriture de Code de Référence

```python
# Routage d'experts conscient de la localité (ELDR)
class ELDRRouter:
    def __init__(self, decode_workers):
        self.workers = decode_workers

    def route_request(self, request_signature):
        # Find best match worker according to expert locality and current load
        best_worker = None
        min_load = float("inf")
        for worker in self.workers:
            affinity = worker.compute_affinity(request_signature)
            if affinity > 0.8 and worker.load < min_load:
                best_worker = worker
                min_load = worker.load
        return best_worker

```

## Pièges Courants (Common Pitfalls)
*   **Déséquilibre de charge** : Router uniquement par affinité d'experts sans prendre en compte la charge instantanée des workers, causant des embouteillages.
*   **Incohérence KV** : Ne pas invalider la signature d'experts lors de l'éviction de blocs du cache KV.

## Liste de vérification (Checklist)
- [ ] Configurer la prédiction de signature d'experts lors de la phase de prefill.
- [ ] Implémenter le routeur d'affinité ELDR prenant en compte la charge de calcul.
- [ ] Configurer les tests de performance de latence TPOT sous forte concurrence.
