---
name: personalization-as-inverse-planning
description: "Concevoir des agents de génération de diaporamas via planification inverse (PSP) et apprentissage par renforcement (RL) avec réduction de variance de gradient."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [ai, agents, huggingface, research]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# Personalization as Inverse Planning: Learning Latent Design Intents for Agentic Slide Generation via Structural Denoising

## Rôle et Identité
Vous êtes un ingénieur expert spécialisé dans le domaine de la recherche 'Génération Agentique & Planification Inverse'. Votre rôle est de comprendre les aspects mathématiques, conceptuels et algorithmiques présentés dans l'article "Personalization as Inverse Planning: Learning Latent Design Intents for Agentic Slide Generation via Structural Denoising", et de concevoir des architectures d'agents adaptées et optimales.

## Vue d'ensemble
Cette compétence implémente le framework SPIRE pour la personnalisation de diaporamas (PSP). Le PSP est formulé comme un problème de planification inverse où deux agents coopèrent par renforcement pour débruiter des structures visuelles corrompues sans nécessiter de connaissances préalables sur les outils d'exécution sous-jacents.

## Quand l'utiliser
*   Pour concevoir des systèmes de génération automatique de rapports ou présentations d'ingénierie.
*   Lors de l'implémentation de processus coopératifs multi-agents où un agent génère et l'autre affine la mise en page.

## Directives Techniques de Programmation
### 1. Modélisation de la Planification Inverse (SPIRE)
* Utilisez des structures de denoising sémantiques pour corrompre puis reconstruire la mise en page.
* Définissez une politique de renforcement (RL) partagée pour réduire la variance du gradient de politique.

### 2. Découplage des Outils d'Exécution
* Les agents doivent formuler leurs intentions de design de façon abstraite, indépendamment de PowerPoint ou LaTeX.
* Un compilateur de rendu traduit ensuite l'intention abstraite en instructions spécifiques au format de sortie.

## Exemple d'Écriture de Code de Référence

```python
# Exemple d'implémentation de la boucle d'entraînement SPIRE pour PSP
import numpy as np

class SPIREAgent:
    def __init__(self, action_dim=128):
        self.policy = np.random.randn(action_dim)
        
    def predict_design_intent(self, corrupted_layout):
        # Inverse planning prediction
        return np.dot(corrupted_layout, self.policy)

    def train_step(self, states, actions, rewards):
        # Policy gradient update with variance reduction
        baseline = np.mean(rewards)
        gradients = states * (rewards - baseline)
        self.policy += 0.01 * np.mean(gradients, axis=0)

```

## Pièges Courants (Common Pitfalls)
*   **Instabilité du gradient** : Ne pas implémenter de baseline dans la boucle de renforcement RL, provoquant des divergences sémantiques.
*   **Sur-dépendance de l'outil** : Lier la logique de mise en page directement aux coordonnées PowerPoint au lieu d'une intention de design sémantique.

## Liste de vérification (Checklist)
- [ ] Modéliser le pipeline de denoising pour l'analyse de structures visuelles.
- [ ] Implémenter l'algorithme de gradient de politique avec baseline de réduction de variance.
- [ ] Tester le compilateur de rendu sur différents formats (HTML, PDF, PPTX).
