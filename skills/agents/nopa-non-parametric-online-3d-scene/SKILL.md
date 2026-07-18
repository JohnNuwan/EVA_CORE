---
name: nopa-non-parametric-online-3d-scene
description: "Générer en temps réel des graphes de scènes 3D via des distributions non-paramétriques (particle sets) et fusion robuste par divergences MMD."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [ai, agents, huggingface, research]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# NoPA: Non-Parametric Online 3D Scene Graph Generation

## Rôle et Identité
Vous êtes un ingénieur expert spécialisé dans le domaine de la recherche 'Modélisation Temporelle & Graphes 3D'. Votre rôle est de comprendre les aspects mathématiques, conceptuels et algorithmiques présentés dans l'article "NoPA: Non-Parametric Online 3D Scene Graph Generation", et de concevoir des architectures d'agents adaptées et optimales.

## Vue d'ensemble
Cette compétence implémente NoPA, un système en temps réel de génération de graphes de scènes 3D. Contrairement aux approches paramétriques qui perdent le détail géométrique en simplifiant chaque objet par une gaussienne unique, NoPA utilise des distributions non-paramétriques basées sur un ensemble fixe de particules et réalise la fusion d'instances via la divergence maximale moyenne (MMD).

## Quand l'utiliser
*   Pour la cartographie 3D temps réel de capteurs IoT et de scanners de lignes industrielles.
*   Lors de l'implémentation de jumeaux numériques nécessitant le suivi continu de la géométrie des objets.

## Directives Techniques de Programmation
### 1. Représentation des Objets par Particules
* Conservez un ensemble fixe de particules tridimensionnelles pour chaque candidat d'objet détecté.
* Évitez l'approximation gaussienne directe pour préserver la géométrie complexe des machines.

### 2. Algorithme de Fusion par Divergence MMD
* Calculez la distance MMD entre les estimations de densité par noyau pour décider s'il faut fusionner deux candidats d'objets.

## Exemple d'Écriture de Code de Référence

```python
# Algorithme de calcul de distance MMD pour la fusion d'objets 3D
import numpy as np

def compute_mmd(particle_set_x, particle_set_y, sigma=1.0):
    # Kernel computation
    def rbf_kernel(A, B):
        dist = np.sum(A**2, axis=1, keepdims=True) + np.sum(B**2, axis=1) - 2 * np.dot(A, B.T)
        return np.exp(-dist / (2 * sigma**2))
    
    xx = np.mean(rbf_kernel(particle_set_x, particle_set_x))
    yy = np.mean(rbf_kernel(particle_set_y, particle_set_y))
    xy = np.mean(rbf_kernel(particle_set_x, particle_set_y))
    return xx + yy - 2 * xy

```

## Pièges Courants (Common Pitfalls)
*   **Fusion incorrecte** : Utiliser des seuils de distance euclidienne simple (barycentres) qui fusionnent des objets distincts mais proches.
*   **Explosion de calcul** : Laisser l'ensemble de particules croître indéfiniment sans fixer de taille maximale (particle limit).

## Liste de vérification (Checklist)
- [ ] Initialiser les ensembles de particules pour chaque équipement détecté.
- [ ] Implémenter le calcul de la divergence MMD pour la validation des fusions.
- [ ] Optimiser la vitesse d'inférence en fixant la taille des particle sets.
