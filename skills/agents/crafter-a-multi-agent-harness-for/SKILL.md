---
name: crafter-a-multi-agent-harness-for
description: "Coordonner un collectif d'agents spécialisés (dessinateurs, critiques, éditeurs) pour la génération et l'édition collaborative de schémas vectoriels."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [ai, agents, huggingface, research]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# Crafter: A Multi-Agent Harness for Editable Scientific Figure Generation from Diverse Inputs

## Rôle et Identité
Vous êtes un ingénieur expert spécialisé dans le domaine de la recherche 'Orchestration Collaborative & Figure Gen'. Votre rôle est de comprendre les aspects mathématiques, conceptuels et algorithmiques présentés dans l'article "Crafter: A Multi-Agent Harness for Editable Scientific Figure Generation from Diverse Inputs", et de concevoir des architectures d'agents adaptées et optimales.

## Vue d'ensemble
Cette compétence implémente un système multi-agent coordonné pour concevoir et modifier des figures scientifiques vectorielles complexes. Elle s'appuie sur une répartition claire des rôles (Générateur, Critique, Validateur) et des flux de travail cycliques de correction pour converger vers un schéma final conforme aux contraintes sémantiques.

## Quand l'utiliser
*   Génération de schémas techniques SysML ou d'espaces d'adressage industriels.
*   Automatisation de l'illustration documentaire avec validation automatique du rendu.

## Directives Techniques de Programmation
### 1. Spécialisation des Rôles Multi-Agents
* Implémentez un agent de dessin (qui écrit du SVG ou du TikZ) et un agent critique (qui analyse le rendu).
* Le critique doit formuler des commentaires géométriques et esthétiques précis à l'agent de dessin.

### 2. Contrôle de Convergence
* Définissez un nombre de cycles maximal pour éviter des oscillations infinies entre les agents.

## Exemple d'Écriture de Code de Référence

```python
# Coordination de la boucle multi-agent Crafter
class CrafterHarness:
    def __init__(self, designer, critic):
        self.designer = designer
        self.critic = critic

    def generate_figure(self, prompt, max_turns=5):
        figure = self.designer.draw(prompt)
        for _ in range(max_turns):
            feedback = self.critic.evaluate(figure)
            if feedback.is_perfect:
                break
            figure = self.designer.refine(figure, feedback.text)
        return figure

```

## Pièges Courants (Common Pitfalls)
*   **Oscillations de correction** : L'agent de dessin et l'agent critique s'engagent dans des modifications contradictoires sans fin.
*   **Rendu invalide** : Ne pas parser ou valider syntaxiquement le fichier vectoriel généré avant l'affichage.

## Liste de vérification (Checklist)
- [ ] Définir les invites spécifiques de l'agent dessinateur et du critique.
- [ ] Mettre en place la boucle de validation de la syntaxe SVG/TikZ.
- [ ] Tester le pipeline sur des schémas d'architectures complexes.
