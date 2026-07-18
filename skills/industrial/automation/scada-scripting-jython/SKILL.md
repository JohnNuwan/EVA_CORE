---
name: scada-scripting-jython
description: "Écrire des scripts Jython pour des applications SCADA."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [scada, scripting, jython, ignition, industrial-automation]
  related_skills: [industrial-databases, industrial-reporting]
---

# Scripting SCADA & Jython (Ignition)

## Vue d'ensemble

Les plateformes de supervision modernes (SCADA) intègrent des moteurs de scripting pour gérer la logique métier complexe qui dépasse le simple affichage graphique. La plateforme leader **Ignition** (éditée par Inductive Automation) utilise **Jython** (une implémentation de Python écrite en Java et s'exécutant sur la JVM). 

Le scripting Jython dans SCADA permet de gérer :
1.  **Les scripts d'événements (Event Scripts) :** Clic sur bouton, ouverture de page, saisie de valeur par l'opérateur.
2.  **Les scripts de passerelle (Gateway Scripts) :** Tâches planifiées (cron), exécution sur changement de valeur de tag, scripts de démarrage de l'application.
3.  **Les requêtes SQL dynamiques :** Lecture et écriture d'historiques en base de données relationnelle.
4.  **L'interfaçage avec des APIs :** Échanges de données REST/JSON avec des systèmes tiers (MES, ERP).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire des fonctions de script Jython en Python 2.7 (syntaxe utilisée par Jython dans Ignition v8.1).
- De manipuler la base de données d'Ignition à l'aide des fonctions `system.db.runNamedQuery` ou `system.db.runPrepUpdate`.
- D'écrire des scripts de synchronisation ou d'importation de tags en masse (`system.tag.writeBlocking`, `system.tag.readBlocking`).
- De concevoir des scripts d'affichage dynamique pour les composants des modules Vision ou Perspective d'Ignition.

**Ne pas utiliser pour :**
- Les scripts de supervision non basés sur Python/Jython (comme le VBScript de WinCC classique).

---

## 1. Exemple de Script Jython d'Écriture Sécurisée de Tags en Masse

Dans Ignition, il faut éviter de lire ou écrire les tags un par un dans des boucles `for` (ce qui génère de multiples requêtes réseau bloquantes). On utilise les écritures groupées (Bulk Write) via `system.tag.writeBlocking`.

```python
def write_conveyor_parameters(conveyor_id, target_speed_rpm, autostart_enabled):
    """
    Configure les paramètres d'un convoyeur de manière optimisée.
    """
    # 1. Définition des chemins de tags
    base_path = "[default]Usine_Lyon/Conditionnement/Convoyeur_%s/" % conveyor_id
    
    paths = [
        base_path + "Target_Speed",
        base_path + "AutoStart_Enable"
    ]
    
    # 2. Définition des valeurs correspondantes
    values = [
        target_speed_rpm,
        autostart_enabled
    ]
    
    # 3. Écriture bloquante groupée (envoi d'une seule requête réseau)
    # Renvoie une liste d'objets QualityCode (un par tag écrit)
    results = system.tag.writeBlocking(paths, values)
    
    # 4. Analyse des résultats de qualité
    success = True
    errors = []
    for i in range(len(results)):
        if not results[i].isGood():
            success = False
            errors.append("Erreur d'écriture sur le tag '%s' : %s" % (paths[i], results[i].toString()))
            
    return {
        "success": success,
        "errors": errors
    }
```

---

## 2. Requête de Données SQL & Génération de Fichier CSV

Ce script s'exécute généralement sur un événement Gateway (tâche planifiée quotidienne) pour exporter un rapport d'arrêts machine :

```python
import csv
import StringIO

def export_downtime_report_to_csv(hours_back=24):
    # Appel d'une requête nommée configurée dans Ignition (Named Query)
    # Named Query protège contre les injections SQL et est optimisée
    params = {"hours": hours_back}
    dataset = system.db.runNamedQuery("Downtime/GetRecentFaults", params)
    
    # Conversion du dataset Ignition en liste Python
    headers = list(dataset.getColumnNames())
    
    # Écriture en mémoire tampon CSV (Jython supporte StringIO)
    output = StringIO.StringIO()
    writer = csv.writer(output)
    
    # Écrire l'en-tête
    writer.writerow(headers)
    
    # Écrire les lignes
    for row in range(dataset.getRowCount()):
        row_data = []
        for col in range(dataset.getColumnCount()):
            row_data.append(dataset.getValueAt(row, col))
        writer.writerow(row_data)
        
    csv_data = output.getvalue()
    output.close()
    
    # Enregistrer le fichier sur le disque du serveur de passerelle (Gateway Node)
    filepath = "/var/lib/ignition/reports/fault_report.csv"
    system.file.writeFile(filepath, csv_data)
    
    return filepath
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Exécution de scripts SQL lourds dans le thread d'interface IHM (GUI Freeze) :**
    *   *Erreur :* Lancer une requête SQL longue de plusieurs secondes sur l'action d'un bouton de l'IHM. L'interface opérateur se fige (ne répond plus) en attendant la réponse de la base de données.
    *   *Correction :* Utiliser les appels asynchrones `system.util.invokeAsynchronous` pour exécuter la requête dans un thread d'arrière-plan, puis renvoyer le résultat à l'IHM via `system.util.invokeLater`.
2.  **Incompatibilité Python 3 (Jython limitation) :**
    *   *Erreur :* Tenter d'utiliser des bibliothèques C-Python compilées en C (comme `pandas`, `numpy`, `scikit-learn`) ou des fonctionnalités modernes de Python 3. Jython 2.7 ne supporte que la syntaxe Python 2.7 et les bibliothèques Java natives.
    *   *Correction :* Réécrire les calculs en Python pur compatible v2.7 ou importer et instancier des classes Java équivalentes (ex: `from java.util import Date`).

---

## Liste de vérification (Checklist)

- [ ] Les scripts accédant à la base de données utilisent des *Named Queries* (requêtes nommées et paramétrées) pour éviter les injections SQL.
- [ ] Les lectures et écritures de tags sont regroupées avec `readBlocking` / `writeBlocking` pour éviter les requêtes réseau unitaires répétitives.
- [ ] Les scripts d'IHM longs s'exécutent en asynchrone (`invokeAsynchronous`) pour ne pas figer l'affichage opérateur.
- [ ] Les imports de modules Python externes sont compatibles avec Jython 2.7 (pas de dépendances binaires C-Python).

