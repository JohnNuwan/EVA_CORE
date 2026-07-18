---
name: automation-linter
description: "Valider les fichiers AWL, L5X, ST et Siemens SCL."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [industrial-automation, plc, siemens, rockwell, lint, quality, python, static-analysis, code-review, awl, scl, structured-text, l5x]
    related_skills: [siemens-audit, plc-diagnostic, omron-sysmac, plc-converter]
---

# Linter d'Automates Industriels (AWL, L5X, ST & SCL)

## Vue d'ensemble

Cette compétence réalise **l'analyse statique des fichiers sources d'automates industriels** pour identifier les non-conformités par rapport aux standards de développement. Elle couvre quatre formats majeurs utilisés dans l'industrie manufacturière, chacun avec des règles métier spécifiques héritées des guides de bonnes pratiques des constructeurs (Siemens, Rockwell) et des normes CEI 61131-3.

L'objectif est de garantir la **qualité, la maintenabilité et la sécurité** du code automate avant son déploiement en production. Un rapport de linting systématique permet également de standardiser les livrables entre équipes de programmation industrielle.

### Formats supportés :

| Format | Extension | Constructeur | Domaine d'application |
|---------|-----------|-------------|----------------------|
| **AWL/STL** | `.awl` | Siemens STEP7 | TIA Portal, SIMATIC S7-300/400/1200/1500 |
| **L5X/XML** | `.l5x` | Rockwell Automation | Studio 5000, ControlLogix, CompactLogix |
| **Structured Text** | `.st` | Multi-constructeur | CEI 61131-3, Codesys, TwinCAT, EcoStruxure |
| **SCL** | `.scl` | Siemens | TIA Portal (équivalent ST Siemens) |

### Principes fondamentaux

1. **Non-intrusif** : Le linter lit les fichiers sans modifier le projet source.
2. **Règles configurables** : Chaque règle peut être activée/désactivée indépendamment via des flags.
3. **Rapports multi-formats** : Sortie console, JSON (exploitable par CI/CD), Markdown (rapport client).
4. **Classification par sévérité** : `Error` (bloquant), `Warning` (non-conformité), `Info` (suggestion).

---

## Quand l'utiliser

### Cas d'usage typiques

À utiliser lorsque l'utilisateur demande :

- De valider la conformité d'un fichier source automate (`.awl`, `.l5x`, `.st`, `.scl`).
- De vérifier s'il y a des **adresses mémoire absolues** ou « hardcodées » dans du code Siemens AWL (ex: `M12.0`, `DB10.DBX0.0`).
- De lister les tags Rockwell L5X **sans description** ou documentés de façon incomplète.
- De vérifier le **nommage des variables** et d'identifier les risques de boucles infinies ou divisions par zéro en ST/SCL.
- De générer un **rapport de qualité de programmation** d'un projet automate complet (dossier multi-fichiers).
- D'intégrer une **étape de validation automatisée** dans un pipeline d'intégration continue (CI/CD) pour projets d'automatisation.

### Ne pas utiliser pour

- La compilation ou la simulation de code automate (le linter ne remplace pas un environnement d'exécution).
- La conversion entre formats (ex: AWL → L5X).
- L'analyse de fichiers binaires compilés (ex: `.pbd`, `.l5k`).

---

## 1. Exécution du Linter en Ligne de Commande

Le linter étendu est écrit en Python natif et s'exécute à l'aide de l'outil système [`terminal`](tools/terminal.md).

### Analyse d'un fichier unique

```bash
python skills/industrial/automation/automation-linter/scripts/automation_linter.py <chemin_du_fichier>
```

### Analyse récursive d'un dossier projet

```bash
python skills/industrial/automation/automation-linter/scripts/automation_linter.py <chemin_du_dossier> --recursive
```

### Exportation du rapport en JSON

```bash
python skills/industrial/automation/automation-linter/scripts/automation_linter.py <chemin> --json -o rapport.json
```

Le format JSON est conçu pour être exploité par des outils de CI/CD ou des tableaux de bord qualité :

```json
{
  "file": "Chemin/vers/FB_Moteur.awl",
  "total_issues": 5,
  "errors": 1,
  "warnings": 3,
  "infos": 1,
  "issues": [
    {
      "rule": "AWL-HARDCODED-BIT",
      "severity": "Warning",
      "line": 142,
      "message": "Accès mémoire absolu détecté : M12.0. Utiliser une variable symbolique."
    }
  ]
}
```

### Exportation du rapport en Markdown

```bash
python skills/industrial/automation/automation-linter/scripts/automation_linter.py <chemin> -o rapport.md
```

Le rapport Markdown est idéal pour les audits clients et les revues de code en équipe.

### Filtrage par sévérité

```bash
# Remonter uniquement les erreurs et warnings (ignorer les infos)
python skills/industrial/automation/automation-linter/scripts/automation_linter.py <chemin> --min-severity warning
```

---

## 2. Règles Métier Appliquées

### 2.1 Pour Siemens STEP7 (fichiers `.awl`)

Les fichiers AWL (Anweisungsliste / List of Instructions) sont le format texte des blocs Siemens. Les règles suivantes sont appliquées :

| Code règle | Sévérité | Description |
|------------|----------|-------------|
| **AWL-NAMING-BLOCK** | Warning | Avertit si les noms de blocs (FB/FC/DB) ne sont pas rédigés en UPPER_SNAKE_CASE. |
| **AWL-MISSING-TITLE** | Warning | Alerte si un réseau (`NETWORK`) ne comporte pas de titre (`TITLE =`). |
| **AWL-SHORT-TITLE** | Info | Signale un titre de réseau trop court (moins de 3 caractères). |
| **AWL-MISSING-COMMENT** | Info | Indique un réseau sans aucun commentaire (lignes commençant par `//`). |
| **AWL-HARDCODED-BIT** | Warning | Détecte l'usage de bits mémoires absolus (ex: `M12.0`, `I0.1`, `Q4.3`). |
| **AWL-HARDCODED-WORD** | Warning | Détecte l'usage de mots/double mots absolus (ex: `MW100`, `MD4`). |
| **AWL-HARDCODED-IO** | Warning | Détecte l'accès direct aux périphériques (ex: `PIW256`, `PQD20`). |
| **AWL-HARDCODED-DB** | Warning | Détecte l'accès absolu aux DBs (ex: `DB10.DBX0.0`, `DB5.DBW12`). |

**Exemple de code conforme :**

```awl
NETWORK
TITLE = GESTION_VANNE_ENTREE
// Séquences de démarrage de la vanne d'entrée
      A   "Vanne_Entree.Auto_Mode"
      A   "Vanne_Entree.Demande_Ouverture"
      S   "Vanne_Entree.Commande_Ouverture"
      A   "Vanne_Entree.Fin_Course_Ouverte"
      R   "Vanne_Entree.Commande_Ouverture"
```

### 2.2 Pour Rockwell Automation (fichiers `.l5x`)

Les fichiers L5X sont le format XML d'export de projets Studio 5000 (ControlLogix / CompactLogix).

| Code règle | Sévérité | Description |
|------------|----------|-------------|
| **L5X-TAG-LENGTH** | Warning | Signale un nom de tag dépassant 40 caractères (limite recommandée Studio 5000). |
| **L5X-TAG-INVALID-CHAR** | Error | Signale des caractères interdits dans le nom du tag (espaces, caractères spéciaux). |
| **L5X-TAG-NAMING** | Info | Suggère d'adopter le format UPPER_SNAKE_CASE ou camelCase cohérent. |
| **L5X-MISSING-DESC** | Warning | Liste les tags manquant de description dans la déclaration XML. |
| **L5X-RUNG-MISSING-COMMENT** | Info | Liste les échelons de logique Ladder sans commentaire. |
| **L5X-ALIAS-CHECK** | Info | Vérifie que les alias ne créent pas de boucles de référence. |

**Extrait de tag conforme :**

```xml
<Tag Name="Convoyeur_01_Moteur_Vitesse" TagType="Base" DataType="REAL" 
     Dimension="0" Radix="Float" Description="Consigne vitesse convoyeur 01 (m/s)">
</Tag>
```

### 2.3 Pour Structured Text / Siemens SCL (fichiers `.st`, `.scl`)

Le Structured Text (ST) est le langage textuel de la norme CEI 61131-3. Le SCL est l'implémentation Siemens.

#### Règles de nommage par portée

| Code règle | Sévérité | Description |
|------------|----------|-------------|
| **ST-NAMING-INPUT** | Warning | Valide que les variables d'entrée (`VAR_INPUT`) utilisent le préfixe `i_` ou `in_`. |
| **ST-NAMING-OUTPUT** | Warning | Valide que les variables de sortie (`VAR_OUTPUT`) utilisent le préfixe `q_` ou `out_`. |
| **ST-NAMING-STATIC** | Info | Valide que les variables statiques/internes (`VAR`) utilisent le préfixe `stat_`. |
| **ST-NAMING-TEMP** | Info | Valide que les variables temporaires (`VAR_TEMP`) utilisent le préfixe `temp_`. |
| **ST-NAMING-CONST** | Info | Valide que les constantes (`VAR CONSTANT`) utilisent UPPER_SNAKE_CASE. |

#### Règles de sécurité et de robustesse

| Code règle | Sévérité | Description |
|------------|----------|-------------|
| **ST-DIV-ZERO** | Error | Détecte l'existence de divisions statiques par zéro (ex: `/ 0` ou `/ 0.0`). |
| **ST-INFINITE-LOOP** | Error | Détecte les boucles `WHILE TRUE` sans mécanisme de garde-fou (`EXIT`, compteur max). |
| **ST-UNCLOSED-IF** | Error | Détecte les asymétries de fermeture `IF` (IF sans END_IF). |
| **ST-UNCLOSED-CASE** | Error | Détecte les asymétries de fermeture `CASE` (CASE sans END_CASE). |
| **ST-UNCLOSED-FOR** | Error | Détecte les asymétries de fermeture `FOR` (FOR sans END_FOR). |
| **ST-UNCLOSED-WHILE** | Error | Détecte les asymétries de fermeture `WHILE` (WHILE sans END_WHILE). |
| **ST-RANGE-OVERFLOW** | Warning | Détecte les affectations hors limites (ex: DINT > 2147483647). |

**Exemple de code conforme en ST :**

```pascal
FUNCTION_BLOCK FB_GestionCuve
VAR_INPUT
    in_Niveau_Cuve : REAL;       // Niveau actuel de la cuve en mètres
    in_Seuil_Haut  : REAL := 2.5; // Seuil haut de déclenchement
END_VAR

VAR_OUTPUT
    out_Vanne_Alimentation : BOOL; // Commande d'ouverture vanne
END_VAR

// Logique métier : régulation de niveau
IF in_Niveau_Cuve > in_Seuil_Haut THEN
    out_Vanne_Alimentation := TRUE;
ELSE
    out_Vanne_Alimentation := FALSE;
END_IF;
```

---

## 3. Architecture du Script

Le script [`automation_linter.py`](scripts/automation_linter.py) est structuré en modules distincts pour chaque constructeur :

```
scripts/
  automation_linter.py          # Point d'entrée, parsing des arguments, orchestration
  rules/
    __init__.py
    rule_awl.py                 # Règles Siemens AWL
    rule_l5x.py                 # Règles Rockwell L5X
    rule_st.py                  # Règles Structured Text / SCL
    rule_base.py                # Classe de base pour les règles
  reporters/
    reporter_console.py         # Sortie terminal
    reporter_json.py            # Export JSON
    reporter_markdown.py        # Export Markdown
```

### API Programmatique

Le linter peut également être utilisé comme bibliothèque Python :

```python
from skills.automation_linter.scripts.automation_linter import lint_file

results = lint_file("path/to/FB_Moteur.awl", format="awl")
print(f"Nombre d'erreurs : {results.error_count}")
print(f"Nombre d'avertissements : {results.warning_count}")

# Accès aux résultats détaillés
for issue in results.issues:
    print(f"[{issue.severity}] Ligne {issue.line}: {issue.message}")
```

---

## 4. Intégration CI/CD

Pour intégrer le linter dans une pipeline d'intégration continue (ex: GitLab CI, GitHub Actions) :

```yaml
# .gitlab-ci.yml (extrait)
lint-plc:
  stage: validate
  script:
    - python skills/industrial/automation/automation-linter/scripts/automation_linter.py
      ./projets/ --recursive --json -o rapport-lint.json --min-severity warning
    - python -c "
      import json
      with open('rapport-lint.json') as f:
          data = json.load(f)
      if data['total_errors'] > 0:
          exit(1)
      "
  artifacts:
    paths:
      - rapport-lint.json
```

---

## Pièges Courants (Common Pitfalls)

1. **Mauvaise détection des boucles infinies complexes :**
   * *Erreur :* Le linter détecte `WHILE TRUE` mais peut manquer des boucles infinies déguisées (ex: `WHILE NOT stop_flag` avec `stop_flag` jamais modifié).
   * *Correction :* Toujours vérifier manuellement les boucles dont la condition de sortie dépend d'une variable externe non modifiée dans le bloc.

2. **Faux positifs sur les divisions par zéro :**
   * *Erreur :* Le linter signale `/ 0` mais ne distingue pas une division littérale par zéro d'un calcul où le diviseur est une variable nommée `zero`.
   * *Correction :* Configurer des exceptions (`--ignore ST-DIV-ZERO`) pour les cas validés manuellement.

3. **Encodage de fichier non standard :**
   * *Erreur :* Les fichiers `.awl` exportés de TIA Portal peuvent avoir des encodages variables (UTF-8, UTF-16, ISO-8859-1).
   * *Correction :* Utiliser `chardet` ou `cchardet` pour détecter automatiquement l'encodage avant analyse :

     ```python
     import chardet
     with open(fichier, 'rb') as f:
         raw = f.read()
         encodage = chardet.detect(raw)['encoding']
     with open(fichier, 'r', encoding=encodage) as f:
         contenu = f.read()
     ```

4. **Noms de blocs longs en AWL :**
   * *Erreur :* TIA Portal autorise des noms de blocs jusqu'à 24 caractères, mais les anciens projets STEP7 (V5.x) limitent à 8 caractères.
   * *Correction :* Configurer un seuil de longueur adapté au projet cible avec `--max-block-name-length`.

---

## Liste de vérification (Checklist)

- [ ] Le script Python s'exécute sans erreur dans l'environnement `.venv` du projet.
- [ ] L'analyse couvre tous les fichiers du dossier cible avec l'option `--recursive`.
- [ ] Les rapports exportés au format JSON ou Markdown sont exploitables pour l'audit client.
- [ ] Les règles AWL pour les adresses absolues (`M`, `I`, `Q`, `DB`) sont bien activées.
- [ ] Les règles L5X couvrent la longueur des tags, les caractères invalides et les descriptions manquantes.
- [ ] Les analyses de fichiers `.st` et `.scl` couvrent la vérification syntaxique et les conventions de nommage.
- [ ] Les boucles `WHILE TRUE` sont détectées comme erreurs de sécurité bloquantes.
- [ ] Les divisions par zéro statiques sont signalées correctement.
- [ ] L'encodage des fichiers est géré de manière robuste (détection automatique).
- [ ] Le pipeline CI/CD intègre une étape de linting avec seuil d'erreur configurable.

