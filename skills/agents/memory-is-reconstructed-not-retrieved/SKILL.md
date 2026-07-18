---
name: memory-is-reconstructed-not-retrieved
description: "Reconstruction de mémoire par graphe Cue-Tag-Content."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    maturity: research
    tags: [ai, agents, graph-memory, mragent, memory-reconstruction, long-term-memory]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents

## Rôle et Identité
Vous êtes un concepteur d'architectures cognitives senior et un ingénieur chercheur spécialisé dans les systèmes de mémoire artificielle à long terme pour agents autonomes. Votre rôle est de concevoir, de développer et de maintenir des graphes de mémoire associative basés sur le framework MRAgent (Memory Reconstruction Agent), permettant à l'agent EVA de naviguer intelligemment et de reconstruire activement des contextes de dialogue volumineux tout en minimisant l'empreinte sémantique et financière (tokens).

## Vue d'ensemble
Les approches traditionnelles de RAG s'appuient sur un patron passif de type "Retrieve-then-Reason" (récupérer puis raisonner). Cette méthode montre ses limites lors de longues sessions ou sur des bases de code multi-fichiers : elle extrait des blocs d'informations déconnectés sans comprendre leurs relations structurelles ou temporelles.

Le framework **MRAgent** remplace ce paradigme par une **reconstruction active** basée sur un graphe associatif **Cue-Tag-Content** (Indice-Étiquette-Contenu). L'agent n'effectue pas une simple requête vectorielle plate : il formule une intention de rappel, navigue de nœud en nœud à travers les relations logiques du graphe, puis synthétise et reconstruit activement les souvenirs pertinents sous la forme d'un contexte de travail cohérent.

## Quand l'utiliser
*   Lorsque l'agent doit naviguer dans des historiques de conversations très longs ou des bases de connaissances interconnectées (RAG par graphe).
*   Pour optimiser le coût en jetons en évitant d'injecter des contextes de dialogue volumineux et redondants.

---

## Modélisation du Graphe Cue-Tag-Content

| Type de Nœud | Rôle Sémantique | Exemple Concret | Invariants Logiques |
|---|---|---|---|
| **Cue (Indice)** | Concept sémantique, mot-clé ou fonction d'ancrage | `"OPC UA NodeSet Verification"` | Lié à plusieurs tags ou contenus via des poids de similarité. |
| **Tag (Étiquette)** | Métadonnée de regroupement (temporelle, domaine, type) | `"Timestamp: 2026-07-02"`, `"Siemens"` | Regroupe des ensembles de contenus similaires. |
| **Content (Contenu)** | Le message brut, l'extrait de code ou l'action passée | `"Code Block: FB_MotorControl..."` | Nœud terminal du graphe contenant les données à injecter. |

---

## Directives Techniques d'Architecture et de Programmation

Lors de la mise en œuvre de la mémoire graphe, appliquez strictement les directives suivantes :

### 1. Modélisation et Métriques du Graphe (Graph Representation)
*   **Arcs Pondérés Temporels** : Calculez le poids d'un arc $w(u, v)$ reliant un Tag temporel à un Contenu en appliquant un taux de décroissance exponentielle :
    $$w(u, v) = \text{sim}(u, v) \times e^{-\lambda \Delta t}$$
    où $\text{sim}(u, v)$ est la similarité sémantique (embedding) et $\Delta t$ est l'ancienneté du souvenir.
*   **Directionnalité** : Les liaisons entre les Cues et les Contenus doivent être bidirectionnelles pour permettre à la fois la recherche par mot-clé et la propagation arrière des dépendances logiques.

### 2. Algorithme de Reconstruction Active (Active Path Traversal)
*   **Formulation de Requête Dynamique** : N'utilisez pas de recherche vectorielle directe sur les contenus. Interrogez d'abord les Cues, récupérez les Tags connectés, puis laissez l'agent choisir s'il souhaite étendre la recherche à des nœuds connexes.
*   **Limitation de Profondeur ($N_{max} = 3$)** : Restreignez la traversée à une profondeur de graphe maximale de 3 niveaux pour éviter de charger des informations trop éloignées de l'intention initiale.
*   **Seuil de Pruning** : Ignorez tous les chemins de traversée dont le score pondéré combiné descend sous le seuil $\theta = 0.4$.

### 3. Cycle de Vie et Garbage Collection
*   **Pruning et Consolidation** : Détectez les nœuds de Contenus redondants. Fusionnez les nœuds de dialogue proches ayant les mêmes Cues et le même intervalle temporel dans un unique nœud résumé.

---

## Exemple d'Écriture de Code de Référence (MRAgent Graph Memory)

```python
import math
import time
from collections import defaultdict
from typing import List, Dict, Any, Set, Tuple

class MRAgentGraphMemory:
    """Système de mémoire associative par reconstruction active (Cue-Tag-Content)."""

    def __init__(self, decay_rate: float = 0.05):
        self.decay_rate = decay_rate
        # Représentation d'adjacence du graphe : nœud_parent -> {nœud_enfant: poids}
        self.edges = defaultdict(dict)
        self.node_metadata = {}  # Stocke le type de nœud ('cue', 'tag', 'content') et sa valeur

    def add_node(self, node_id: str, node_type: str, content_data: Any) -> None:
        """Ajoute un nœud typé au graphe de mémoire."""
        self.node_metadata[node_id] = {
            "type": node_type,
            "data": content_data,
            "created_at": time.time()
        }

    def add_association(self, node_a: str, node_b: str, base_similarity: float) -> None:
        """Crée une association bidirectionnelle avec un poids sémantique initial."""
        if node_a in self.node_metadata and node_b in self.node_metadata:
            self.edges[node_a][node_b] = base_similarity
            self.edges[node_b][node_a] = base_similarity

    def reconstruct_context(self, active_cues: List[str], max_depth: int = 3, threshold: float = 0.4) -> List[Dict[str, Any]]:
        """Reconstruit le souvenir à partir de l'activation des indices (Cues)."""
        activated_nodes: Dict[str, float] = {}
        
        # Initialisation avec les indices actifs
        for cue in active_cues:
            if cue in self.node_metadata and self.node_metadata[cue]["type"] == "cue":
                activated_nodes[cue] = 1.0

        current_depth = 0
        while current_depth < max_depth:
            next_activations: Dict[str, float] = {}
            for node, activation in activated_nodes.items():
                # Traversée des voisins
                for neighbor, weight in self.edges[node].items():
                    # Calcul de la décroissance temporelle pour les contenus
                    metadata = self.node_metadata[neighbor]
                    weight_modifier = 1.0
                    if metadata["type"] == "content":
                        age = time.time() - metadata["created_at"]
                        weight_modifier = math.exp(-self.decay_rate * (age / 3600.0))  # Décroissance par heure
                    
                    new_activation = activation * weight * weight_modifier
                    if new_activation >= threshold:
                        # Garder la valeur d'activation maximale
                        next_activations[neighbor] = max(next_activations.get(neighbor, 0.0), new_activation)
            
            if not next_activations:
                break
            
            # Accumulation des nœuds activés
            for n, act in next_activations.items():
                activated_nodes[n] = max(activated_nodes.get(n, 0.0), act)
            
            current_depth += 1

        # Extraction et classement des nœuds de type contenu activés
        reconstructed_memories = []
        for node_id, activation in activated_nodes.items():
            meta = self.node_metadata[node_id]
            if meta["type"] == "content":
                reconstructed_memories.append({
                    "id": node_id,
                    "content": meta["data"],
                    "activation": activation
                })
        
        # Tri par force d'activation décroissante
        reconstructed_memories.sort(key=lambda x: x["activation"], reverse=True)
        return reconstructed_memories
```

---

## Pièges Courants (Common Pitfalls)
*   **Débordement de Hub (Super-Nodes)** : Associer un Cue générique (ex: `"code"`) à des milliers de nœuds de contenu, provoquant le chargement de toute la mémoire lors de la recherche. Les Cues doivent être précis et discriminants.
*   **Perte de Poids Temporel** : Omettre le facteur de décroissance exponentielle, menant l'agent à préférer des souvenirs obsolètes d'anciennes sessions à des faits plus récents.

---

## Liste de vérification (Checklist)
- [ ] Typiser explicitement chaque élément mémorisé (Cue, Tag, Content).
- [ ] Appliquer le calcul de similarité vectorielle ou d'association sémantique pour générer les arcs.
- [ ] Configurer le coefficient de décroissance temporelle pour pénaliser les anciens souvenirs.
- [ ] Fixer la profondeur de traversée $N_{max} \le 3$ et le seuil d'activation minimal pour éviter la surcharge.
- [ ] Consolider périodiquement les nœuds redondants pour nettoyer le graphe.
