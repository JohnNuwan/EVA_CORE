# Pack Expert Ignition SCADA / Jython

## Objectif

Ce pack expert complète la skill `ignition-scada` avec une architecture de projet, des patterns Jython 2.7 industriels, une stratégie tags/base de données et un cadre d'intégration robuste avec Siemens ou Rockwell.

## 1. Architecture de projet Ignition recommandée

### 1.1 Séparation des responsabilités
- `Gateway scripts` : logique planifiée, intégration externe, orchestration de traitements.
- `Project library scripts` : fonctions réutilisables, aucun accès UI direct.
- `Perspective views` : rendu opérateur et appels vers APIs projet.
- `Vision` : seulement si le projet historique le nécessite.
- `Named Queries` : accès base de données centralisé et paramétré.
- `UDT instances` : modélisation standardisée des équipements.

### 1.2 Organisation type
- `project.motor.*` : fonctions métier moteur
- `project.alarm.*` : traduction / enrichissement alarmes
- `project.db.*` : wrappers de Named Queries
- `project.tag.*` : lecture/écriture groupée tags
- `project.util.*` : conversions, formatage, validation

## 2. Règles absolues Jython 2.7

- Pas de f-strings.
- Pas de `pathlib`, `dataclasses`, `async/await`.
- Favoriser `%` ou `.format()`.
- Éviter les bibliothèques CPython natives non supportées par Jython.
- Importer des classes Java si nécessaire pour dates, listes, threads, etc.

### 2.1 Gabarit de logger
```python
logger = system.util.getLogger("EVA.Ignition")
logger.info("Initialisation du module moteur")
```

### 2.2 Gabarit de fonction réutilisable
```python
def write_device_command(tag_paths, values):
    logger = system.util.getLogger("EVA.Ignition")
    results = system.tag.writeBlocking(tag_paths, values)
    for idx in range(len(results)):
        if not results[idx].isGood():
            logger.warn("Echec ecriture %s -> %s" % (tag_paths[idx], results[idx].toString()))
    return results
```

## 3. Modèle tags recommandé

### 3.1 Structure UDT type
- `Cmd/Start`, `Cmd/Stop`, `Cmd/Reset`
- `Sts/Run`, `Sts/Ready`, `Sts/Fault`, `Sts/Local`
- `Alm/Summary`, `Alm/Code`, `Alm/Text`
- `Ana/Pv`, `Ana/Sp`, `Ana/Unit`
- `Meta/EquipmentId`, `Meta/Area`, `Meta/Class`

### 3.2 Principes de supervision
- Le SCADA reflète la vérité automate, il ne la reconstruit pas.
- Les tags calculés lourds doivent rester limités.
- Préférer les UDTs et paramètres plutôt que des milliers de tags disparates.
- Exposer un bit résumé d'alarme et un code/texte d'aide opérateur.

## 4. Pattern lecture / écriture groupée

### 4.1 Lecture bulk obligatoire
```python
paths = [
    "[default]AreaA/Motor01/Sts/Run",
    "[default]AreaA/Motor01/Sts/Fault",
    "[default]AreaA/Motor01/Ana/Pv"
]
qvs = system.tag.readBlocking(paths)
run_val = qvs[0].value if qvs[0].quality.isGood() else None
fault_val = qvs[1].value if qvs[1].quality.isGood() else None
pv_val = qvs[2].value if qvs[2].quality.isGood() else None
```

### 4.2 Écriture sécurisée commande opérateur
```python
def pulse_start(base_path):
    paths = [base_path + "/Cmd/Start"]
    system.tag.writeBlocking(paths, [True])
    system.util.invokeLater(lambda: system.tag.writeBlocking(paths, [False]), 250)
```

## 5. Base de données et historisation

### 5.1 Règles
- Toute requête métier passe par `Named Queries`.
- Pas de concaténation SQL dynamique depuis l'IHM.
- Les écritures transactionnelles sensibles doivent être centralisées côté Gateway.
- L'historisation fine fréquence n'est pas un substitut à une logique automate propre.

### 5.2 Wrapper de Named Query
```python
def get_active_events(line_id):
    params = {"lineId": line_id}
    return system.db.runNamedQuery("EVAProject", "Events/GetActive", params)
```

## 6. Asynchronisme et expérience opérateur

### 6.1 Quand l'utiliser
- export CSV / Excel
- appel REST / MES
- calculs lourds
- requêtes SQL longues

### 6.2 Pattern recommandé
```python
def run_async(task_fn, done_fn=None):
    def _bg():
        result = task_fn()
        if done_fn is not None:
            system.util.invokeLater(lambda: done_fn(result))
    system.util.invokeAsynchronous(_bg)
```

## 7. Convention de navigation Perspective

- Les vues ne contiennent pas la logique métier profonde.
- Les scripts composants appellent une bibliothèque projet.
- Les paramètres de vue doivent être simples, explicites et sérialisables.
- Les popups d'action opérateur doivent journaliser l'origine de la commande si requis par le projet.

## 8. Sécurité et gouvernance

- Utiliser les rôles / zones Ignition pour séparer exploitation, maintenance et admin.
- Journaliser les actions critiques : start/stop/reset/override.
- Limiter les écrans de diagnostic profond aux profils autorisés.
- Pour des systèmes 21 CFR / pharma / auditables, tracer utilisateur, horodatage et valeur avant/après.

## 9. Contrat d'intégration PLC ↔ Ignition

### 9.1 Commandes
- Écriture uniquement dans un sous-arbre commande explicite.
- Idéalement impulsion courte ou bit consommé par l'automate.
- Les resets ne doivent pas masquer un défaut terrain non levé.

### 9.2 États
- Le PLC publie `Run`, `Ready`, `Fault`, `Local`, `Mode`, `Step`, `Pv`, `Sp`.
- Ignition transforme ces données en vues et rapports, pas en logique machine.

## 10. Checklist de revue experte
- [ ] Tous les scripts sont compatibles Jython 2.7.
- [ ] Les accès tags multiples sont groupés.
- [ ] Les requêtes SQL passent par des Named Queries.
- [ ] Les actions longues sont asynchrones.
- [ ] Les UDTs portent un contrat stable pour l'automate et la supervision.
- [ ] Les commandes opérateur sont traçables.
- [ ] Les vues Perspective restent légères et maintenables.

## 11. Cas d'usage où charger ce pack
- Standardiser un projet Ignition neuf.
- Refactoriser un projet Perspective lent ou désordonné.
- Concevoir la couche SCADA d'une ligne Siemens/Rockwell.
- Mettre en place tags, alarmes, historisation et commandes opérateur propres.
