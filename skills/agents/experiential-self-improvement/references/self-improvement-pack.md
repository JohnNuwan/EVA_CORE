# Auto-amélioration Expérientielle et Réflexion Multi-Niveaux

Ce document de référence rassemble les concepts d'*Experiential Reflective Learning* et les méthodes d'auto-optimisation textuelle des invites (prompts) basées sur la taxonomie d'erreurs multi-niveaux (SAMULE, arXiv).

---

## 1. Méta-Cognition et Boucles de Rétroaction Textuelle

L'auto-amélioration des agents IA sans mise à jour des poids du réseau (non-gradient-based optimization) repose sur la capacité d'auto-analyse sémantique. L'agent utilise sa propre capacité de raisonnement pour diagnostiquer ses erreurs passées et amender ses instructions de base (prompt système ou fichier de règles).

---

## 2. La Taxonomie d'Erreurs à 3 Niveaux (Modèle SAMULE)

Pour qu'une auto-réflexion soit efficace et évite le surapprentissage local (overfitting), le diagnostic des trajectoires de défaillance doit être catégorisé selon trois niveaux d'abstraction :

| Niveau de Réflexion | Portée et Diagnostic | Exemple d'Action Corrective |
| :--- | :--- | :--- |
| **Micro (Single-Trajectory)** | Erreur ponctuelle de syntaxe ou de paramétrage lors d'une étape précise de la trajectoire. | L'agent corrige la commande shell en ajoutant un paramètre manquant (ex: `-y` sur `npx`). |
| **Meso (Intra-Task)** | Erreur de logique ou de flux se répétant au sein de plusieurs essais sur la même tâche. | Identification d'une boucle infinie d'appels d'outils et ajout d'une garde dans le script local. |
| **Macro (Inter-Task)** | Modèle d'erreur structurelle transverse survenant à travers plusieurs catégories de tâches. | Détecter que l'agent sous-estime systématiquement la taille des fenêtres de contexte ou la limite d'appels API. |

---

## 3. Algorithme d'Auto-Optimisation (Reflect, Retry, Reward)

Le pipeline d'auto-amélioration s'organise selon une boucle d'évaluation continue :

```
       [ Tâche d'évaluation sur un Benchmark ]
                          │
                          ▼
            [ Exécution de la trajectoire ]
                          │
        Si Échec          ▼           Si Succès
   ┌──────────────────────────────────────────────┐
   │ 1. Analyse de cause racine (Post-Mortem)     │
   │ 2. Formulation d'un diagnostic d'erreur      │
   │ 3. Amendement du prompt système / règles     │ ────> [ Enregistrement ]
   │ 4. Nouvelle exécution (Retry)                │
   └──────────────────────────────────────────────┘
```

Chaque modification du prompt système ou de la base de règles de l'agent est traitée comme une hypothèse. L'agent la valide en relançant le benchmark ; si le score s'améliore (Reward), la règle est enregistrée définitivement dans la mémoire à long terme (compétences ou configuration).
