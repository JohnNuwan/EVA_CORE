---
name: ignition-scada
description: "Programmer en Jython et configurer Ignition SCADA."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [ignition, scada, jython, python-27, perspective, industrial-automation, tags-generation]
    related_skills: [simplify-code, plan, plc-connectivity]
---

# Programmation Jython et Configuration Ignition SCADA

## Vue d'ensemble

La plateforme industrielle **Ignition** par Inductive Automation repose sur un moteur de script utilisant **Jython** (Python s'exécutant sur la JVM Java). La syntaxe supportée par défaut est celle de **Python 2.7**.

Cette compétence fournit à l'agent EVA les directives, conventions d'écriture et recettes de code indispensables pour :
1. Écrire des scripts Jython performants et robustes.
2. Interagir efficacement avec les tags (QualifiedValues) et les bases de données (Named Queries).
3. Concevoir des scripts asynchrones pour éviter de bloquer l'IHM graphique.
4. Générer automatiquement des structures de tags importables et des scripts de synchronisation à partir des rapports d'audit industriels à l'aide de l'outil d'assistance [generate_ignition_config.py](scripts/generate_ignition_config.py).

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Concevoir ou optimiser des scripts Jython pour des événements de composants dans **Perspective** or **Vision**.
- Configurer ou écrire des scripts d'événements de tags (Tag Change Scripts, Alarms).
- Lire ou écrire dans des tags à l'aide de l'API moderne `system.tag.readBlocking` or `system.tag.writeBlocking`.
- Exécuter des transactions ou requêtes SQL via `system.db.runNamedQuery` ou requêtes préparées.
- Traduire un rapport d'audit documentaire en configuration d'import de tags Ignition.

---

## Guide de Développement Jython & API Ignition

### 1. Version de Python et Compatibilité (Python 2.7)
Ignition exécutant Jython 2.7, l'agent doit proscrire les syntaxes exclusives à Python 3 :
- **Pas de f-strings** : Utiliser le formatage classique `"Valeur : %s" % val` ou `"Valeur : {}".format(val)`.
- **Pas d'extensions C** : Les bibliothèques compilées en natif (comme `numpy` ou `pandas` standards) ne fonctionneront pas sous Jython. Privilégier les classes Java de la JVM importées directement :
  ```python
  from java.util import ArrayList
  list_java = ArrayList()
  list_java.add("EVA")
  ```

### 2. Gestion des commandes par impulsions (Boutons Poussoirs IHM)
Lors de l'écriture sur des tags de commande de type impulsion (ex: boutons Start, Stop, Reset d'un moteur), il convient de set le tag à `True` puis à `False` de façon asynchrone pour ne jamais bloquer le thread de rendu de l'interface client (IHM).
*   **Modèle d'impulsion asynchrone robuste (Perspective/Vision) :**
    ```python
    import time
    
    startPath = "%s/Commands/Start" % devicePath
    system.tag.writeBlocking([startPath], [True])
    
    def release_pulse():
        time.sleep(0.5) # Temporisation physique de l'impulsion (500 ms)
        system.tag.writeBlocking([startPath], [False])
        
    system.util.invokeAsynchronous(release_pulse)
    ```

### 3. Lecture et Écriture Groupées de Tags
Les anciennes fonctions `system.tag.read` et `system.tag.write` sont obsolètes. Depuis Ignition 8, il est obligatoire d'utiliser les fonctions bloquantes ou asynchrones prenant des listes pour des raisons de performance.

**Règle de performance absolue :** Ne jamais appeler `readBlocking` ou `writeBlocking` à l'intérieur d'une boucle `for` ou `while`. Toujours regrouper les chemins dans une liste unique et appeler la fonction une seule fois.

*   **Lecture groupée optimisée :**
    ```python
    # Regroupement des chemins dans une liste unique
    paths = ["[default]AS660/EPH/660C1_EPH_AgitCtrl/Status", "[default]AS664/EM/664C6_E_B_INLET/Command"]
    results = system.tag.readBlocking(paths)
    
    # Lecture des valeurs avec vérification de qualité
    if results[0].quality.isGood():
        status_val = results[0].value
    else:
        status_val = None
    ```

*   **Écriture groupée optimisée :**
    ```python
    paths = ["[default]AS660/EPH/660C1_EPH_AgitCtrl/Status", "[default]AS664/EM/664C6_E_B_INLET/Command"]
    values = [2, 1]
    
    # Renvoie une liste de statuts de qualité d'écriture
    write_status = system.tag.writeBlocking(paths, values)
    for idx, stat in enumerate(write_status):
        if not stat.isGood():
            system.util.getLogger("EVA_Ignition").warn("Erreur d'écriture sur le tag : " + paths[idx])
    ```

### 3. Named Queries (Prévention des Injections SQL)
Ne jamais concaténer de chaînes pour composer des requêtes SQL. Toujours configurer et appeler des **Named Queries** précompilées et paramétrées sur la Gateway.
```python
# Appel d'une requête nommée paramétrée
params = {"motorId": 12, "activeStatus": True}
dataset = system.db.runNamedQuery("MonProjetEVA", "Moteurs/GetActiveLogs", params)

# Parcours propre du dataset Ignition
for row in range(dataset.getRowCount()):
    msg = dataset.getValueAt(row, "message")
    t_stamp = dataset.getValueAt(row, "t_stamp")
```

### 4. Exécution Asynchrone dans l'IHM
Pour éviter de figer l'interface utilisateur lors de tâches lentes (requête SQL complexe, requête HTTP externe), utiliser `system.util.invokeAsynchronous` pour déléguer le travail à un thread d'arrière-plan, puis mettre à jour l'IHM de manière sécurisée via `system.util.invokeLater` :

```python
def task_heavy():
    # Opération lente d'arrière-plan
    import time
    time.sleep(2)
    res = "Succès"
    
    # Fonction de retour vers le thread graphique principal (IHM)
    def update_gui():
        # Mise à jour sécurisée du composant
        event.source.parent.getComponent('LabelResult').text = res
        
    system.util.invokeLater(update_gui)

# Lancer la tâche asynchrone sans figer l'IHM
system.util.invokeAsynchronous(task_heavy)
```

---

## Outil de Génération de Configuration de Tags

Cette compétence intègre un script Python [generate_ignition_config.py](scripts/generate_ignition_config.py) pour convertir directement le rapport consolidé de l'audit technique d'automatisme en :
1. Fichier d'importation de tags JSON (`tags.json`) définissant l'arborescence des dossiers par Station d'Automatisme (AS), divisée en sous-dossiers `EPH` (Phases) et `EM` (Équipements) contenant des instances de UDTs standardisés.
2. Un script de synchronisation Jython (`ignition_sync.py`) appliquant les lectures et écritures groupées pour lier les phases aux équipements.

### Exécution du Générateur

Pour appeler le générateur de configuration, exécutez le script d'assistance via l'outil d'exécution de code (`execute_code`) avec le snippet suivant :

```python
import subprocess
import os

# Définition des chemins
audit_report = "output/audit/2026-06-18_15/audit_report.md" # Remplacer par le chemin réel du rapport généré
out_tags = "output/audit/2026-06-18_15/ignition_tags.json"
out_script = "output/audit/2026-06-18_15/ignition_sync.py"

cmd = [
    ".venv/Scripts/python.exe",
    "skills/industrial/automation/ignition-scada/scripts/generate_ignition_config.py",
    "--audit-report", audit_report,
    "--out-tags", out_tags,
    "--out-script", out_script
]

print("Génération de la configuration Ignition en cours...")
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Erreurs :", result.stderr)
```

---

## Liste de vérification (Checklist)

- [ ] Tous les scripts Jython respectent la syntaxe stricte de Python 2.7 (pas de f-strings, etc.).
- [ ] Les lectures et écritures de tags multiples utilisent une seule opération groupée (`readBlocking`/`writeBlocking`).
- [ ] Toutes les requêtes de bases de données passent par des Named Queries ou du SQL préparé.
- [ ] Aucun appel réseau ou base de données bloquant n'est exécuté directement dans le thread graphique principal d'un composant (IHM).
- [ ] Les imports de tags JSON générés pointent vers des UDTs existants dans la configuration d'Ignition (ex: `_types_/EPH_Template` et `_types_/EM_Template`).

