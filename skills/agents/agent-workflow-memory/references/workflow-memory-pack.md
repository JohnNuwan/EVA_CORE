# Mémoire de Flux de Travail pour Agents Autonomes (AWM)

Ce document de référence décrit la méthodologie d'extraction et de réutilisation des patrons de tâches sémantiques basés sur le modèle d'*Agent Workflow Memory* (OpenReview, 2026).

---

## 1. Différences entre Mémoire Brute et Mémoire de Workflow

Dans les architectures d'agents classiques, la mémoire à long terme stocke souvent des historiques bruts de conversations (trajectoires d'appels d'outils et réponses textuelles). Cette méthode engendre du surapprentissage (overfitting) et sature la fenêtre de contexte du modèle avec des détails obsolètes ou locaux.

**L'Agent Workflow Memory (AWM)** résout ce problème en séparant l'historique brut des structures comportementales. Il identifie les enchaînements logiques réussis et les convertit en **recettes de tâches (Task Recipes)** génériques et paramétrées.

---

## 2. Processus d'Extraction et de Généralisation

L'extraction d'une compétence ou d'une recette s'organise selon les étapes suivantes :

```
 Trajectoire brute d'exécution (Historique d'outils)
                   │
                   ▼
       ┌────────────────────────┐
       │   1. Filtrage Outils   │  <── Exclut le raisonnement textuel transitoire
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  2. Paramétrisation    │  <── Remplace les valeurs spécifiques par des variables
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │  3. Induction/Format   │  <── Synthétise sous forme de Skill structurée
       └────────────────────────┘
```

1.  **Filtrage des étapes transitoires** : Nettoyer la trajectoire pour ne conserver que les appels d'outils effectifs (lecture de fichiers, commandes shell, requêtes d'API) et leurs transitions logiques.
2.  **Paramétrisation (Abstraction)** : Remplacer les valeurs littérales (ex: `c:\Projet\FB100.scl`, `502`, `"MotorType"`) par des variables génériques (ex: `<file_path>`, `<port_number>`, `<class_name>`).
3.  **Induction** : Fusionner plusieurs exécutions similaires d'une même tâche pour extraire le plus petit dénominateur commun stable (le squelette logique du workflow).
4.  **Indexation sémantique** : Enregistrer le workflow avec ses critères d'activation (ex: balises sémantiques, description, et préconditions d'environnement).

---

## 3. Représentation d'une Recette de Workflow (Exemple)

Voici un exemple structurel d'un workflow extrait pour la génération de code :

```yaml
# Recette extraite : validation_scl_siemens
intent: "Review and compile Siemens SCL block"
prerequisites:
  tools: [read_file, write_to_file, run_command]
  env: [TIA_PORTAL_COMPILER_PATH]

steps:
  - step: 1
    action: "Read the SCL source file"
    tool: "read_file"
    args: { path: "<src_file>" }
    
  - step: 2
    action: "Extract block header to confirm optimized access tag is active"
    assertion: "contains('S7_Optimized_Access')"
    
  - step: 3
    action: "Compile via command line compiler"
    tool: "run_command"
    args: { command: "tiacompile --file <src_file> --out <temp_dir>" }
```
