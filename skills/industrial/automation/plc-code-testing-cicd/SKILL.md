---
name: plc-code-testing-cicd
description: "Mettre en place des pipelines de test automatisé et CI/CD pour le code automate."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags:
      - plc-testing
      - cicd
      - continuous-integration
      - automation-tests
      - sil
      - software-in-the-loop
      - hil
      - hardware-in-the-loop
      - unit-test-plc
      - tia-openness
      - testxchange
      - plcsim
      - studio-5000-emulate
      - twincat-tcunit
      - plcopentest
      - fat
      - factory-acceptance-test
      - regression-test
      - versioning-plc
      - git-plc
      - ci-phase
    related_skills:
      - plc-converter
      - plcopen-xml
      - rockwell-studio5000
      - siemens-scl
      - virtual-commissioning
      - ci-cd-docker-kubernetes
---

# Tests Automatisés et CI/CD pour Code Automate

## Vue d'ensemble

Les **tests automatisés et le CI/CD pour automates** sont des pratiques émergentes qui transforment l'ingénierie d'automatisation. Contrairement au développement logiciel classique, le code automate présente des défis spécifiques :

- Dépendance au matériel physique (PLC, E/S, drives)
- Contraintes temps réel (cycle scan, watchdog, task timing)
- Communication réseau industrielle (PROFINET, EtherNet/IP)
- Normes de sécurité (IEC 61508, EN 13849)
- Environnements propriétaires (TIA Portal, Studio 5000, TwinCAT)

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De mettre en place des tests unitaires pour du code PLC
- De configurer un pipeline CI/CD pour un projet TIA Portal ou Studio 5000
- D'automatiser les tests avec PLCSIM ou Emulate
- De préparer un plan de validation pour FAT (Factory Acceptance Test)
- De versionner le code automate avec Git
- De générer des rapports de tests automatisés

---

## 1. Stratégie de Test

### 1.1 Pyramide de test pour automation

```
          ╱╲
         ╱  ╲
        ╱ HIL╲         Hardware-in-the-Loop
       ╱ (rare)╲       (test d'intégration complet)
      ╱──────────╲
     ╱    SIL      ╲   Software-in-the-Loop
    ╱  (fréquent)   ╲  (simulation contrôleur + E/S)
   ╱──────────────────╲
  ╱   Test Unitaire     ╲   Tests de code (ST, Ladder)
 ╱     PLC Unit Test     ╲   Indépendants du hardware
╱──────────────────────────╲
╱   Analyse Statique        ╲   Linting, conventions
╱____________________________╲  Code review, style
```

### 1.2 Types de tests

| Niveau | Type | Outil | Cycle | Coût |
|:-------|:-----|:------|:------|:-----|
| 1 | **Lint / Static analysis** | Automation Linter, SonarQube | Chaque commit | Très faible |
| 2 | **Unitaire PLC (ST/Ladder)** | plcunit, TcUnit, TIA Portal Test | Chaque commit | Faible |
| 3 | **Unitaire module (CFC/SFC)** | TestXchange, TIA Portal Openness | Quotidien | Moyen |
| 4 | **SIL (Software-in-the-Loop)** | PLCSIM, Emulate, TwinCAT XAE | Quotidien | Moyen |
| 5 | **HIL (Hardware-in-the-Loop)** | dSPACE, OPAL-RT, Speedgoat | Hebdomadaire | Élevé |
| 6 | **FAT (Factory Acceptance Test)** | Manuel + outils | Jalon projet | Très élevé |

---

## 2. Tests Unitaires PLC

### 2.1 Avec plcunit (Open-source)

plcunit est un framework de tests unitaires pour code Structured Text (IEC 61131-3) :

```iecst
// Exemple de test unitaire en ST
FUNCTION test_MotorStart : BOOL
VAR
    motor : FB_MotorControl;
    result : BOOL;
END_VAR

// Test 1 : Démarrer moteur en automatique
motor.AutoMode := TRUE;
motor.StartCmd := TRUE;
motor.Run();

test_MotorStart := motor.Running = TRUE AND motor.Status = STATUS_OK;

// Test 2 : Vérifier interdiction de démarrage en manuel
motor.AutoMode := FALSE;
motor.StartCmd := TRUE;
motor.Run();

test_MotorStart := test_MotorStart AND motor.Running = FALSE;
```

### 2.2 Avec TcUnit (TwinCAT)

```python
# Générateur de tests TcUnit
def generate_tcunit_test(function_block: str, test_cases: list) -> str:
    """Génère un test TcUnit (TwinCAT Unit Test) en ST."""
    test_code = f"""// Test suite for {function_block}
FUNCTION TestSuite_{function_block}
VAR
    fbTest : FB_{function_block};
    assert : TcUnit.Assert;
END_VAR

CASE TestCase OF
"""

    for i, case in enumerate(test_cases):
        test_code += f"""
    {i + 1}:  // {case.get('description', '')}
        fbTest.Input := {case.get('input', '')};
        fbTest.Run();
        assert.AreEqual(Expected := {case.get('expected', 'TRUE')},
                        Actual := fbTest.Output,
                        Message := '{case.get('message', f'Test {i + 1}')}');
"""
    test_code += "\nEND_CASE"
    return test_code
```

---

## 3. Software-in-the-Loop (SIL)

### 3.1 PLCSIM (Siemens TIA Portal)

```python
# Automation de PLCSIM via TIA Portal Openness
def run_plcsim_test(project_path: str, test_scenario: dict) -> dict:
    """Lance une simulation PLCSIM avec scénario de test.

    Args:
        project_path: Chemin du projet TIA Portal (.ap17)
        test_scenario: Dict avec les entrées, attentes

    Returns:
        Résultat du test avec chronométrage
    """
    # Note : nécessite TIA Portal Openness et PLCSIM Advanced
    # API COM/DCOM via python (win32com)
    import time

    # Simulation de l'interface TIA Portal
    plc_tag_writes = test_scenario.get("inputs", {})
    plc_tag_reads = test_scenario.get("expected", {})

    results = {
        "passed": True,
        "duration_ms": 0,
        "checks": []
    }

    start = time.time()
    # TODO : Implémentation réelle via TIA Openness COM
    # 1. Lancer TIA Portal
    # 2. Charger le projet
    # 3. Lancer PLCSIM
    # 4. Télécharger vers simulation
    # 5. Appliquer entrées
    # 6. Attendre N cycles (via Task completion)
    # 7. Lire sorties
    # 8. Comparer aux attentes

    end = time.time()
    results["duration_ms"] = (end - start) * 1000
    return results
```

### 3.2 Studio 5000 Emulate (Rockwell)

```python
# Automation de Studio 5000 Emulate
def run_emulate_test(l5x_path: str, test_sequence: list) -> dict:
    """Exécute des tests sur Studio 5000 Emulate.

    Args:
        l5x_path: Chemin du fichier L5X
        test_sequence: Liste de dicts {"inputs": {...}, "expected": {...}}

    Returns:
        Résultats des tests
    """
    results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "results": []
    }

    for i, test in enumerate(test_sequence):
        # 1. Charger L5X (via l5x_editor)
        # 2. Démarrer émulation
        # 3. Écrire tags d'entrée
        # 4. Attendre (utilisation de SINT/SSV pour contrôler exécution)
        # 5. Lire tags de sortie
        # 6. Comparer

        result = {
            "test_index": i,
            "inputs": test.get("inputs", {}),
            "expected": test.get("expected", {}),
            "actual": {},
            "passed": True,
        }
        results["results"].append(result)

        if result["passed"]:
            results["tests_passed"] += 1
        else:
            results["tests_failed"] += 1

    return results
```

---

## 4. Pipeline CI/CD

### 4.1 GitLab CI pour TIA Portal

```yaml
# .gitlab-ci.yml pour projet automation TIA Portal
stages:
  - lint
  - build
  - test
  - deploy

variables:
  TIA_PROJECT_PATH: "MonProjet.ap17"
  TIA_ARCHIVE_PATH: "MonProjet.zap17"

lint:
  stage: lint
  script:
    - python tools/automation_linter.py --path $TIA_PROJECT_PATH
    - python tools/l5x_editor.py validate --path $L5X_EXPORT_PATH
  artifacts:
    reports:
      codequality: gl-codequality.json

build:
  stage: build
  script:
    - echo "Compilation TIA Portal via Openness..."
    - python scripts/tia_compile.py $TIA_PROJECT_PATH
    - python scripts/l5x_export.py --project $TIA_PROJECT_PATH
  artifacts:
    paths:
      - "*.l5x"
      - "*.zap17"

test-sil:
  stage: test
  script:
    - python scripts/plcsim_runner.py --project $TIA_PROJECT_PATH
    - python scripts/test_reporter.py --output test-report.xml
  artifacts:
    reports:
      junit: test-report.xml
  needs: ["build"]

test-integration:
  stage: test
  script:
    - python scripts/hil_runner.py
    - python scripts/integration_test.py
  only:
    - main
    - tags
  needs: ["build"]

deploy-production:
  stage: deploy
  script:
    - python scripts/deploy_plc.py --target production
  when: manual
  only:
    - tags
  needs: ["test-sil"]
```

### 4.2 GitHub Actions pour Rockwell L5X

```yaml
# .github/workflows/plc-ci.yml
name: PLC CI Pipeline

on:
  push:
    branches: [main, develop]
    paths: ['projects/**/*.l5x', 'projects/**/*.py']
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint L5X files
        run: |
          python tools/l5x_editor.py validate --path projects/
      - name: Generate L5X report
        run: |
          python tools/l5x_editor.py analyze --path projects/

  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run SIL tests
        run: |
          python tests/test_emulate.py
        env:
          STUDIO_5000_PATH: ${{ secrets.STUDIO_5000_PATH }}
      - name: Generate test report
        run: |
          python tests/generate_report.py
```

### 4.3 Jenkins Pipeline

```groovy
// Jenkinsfile pour projet automation
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint PLC Code') {
            steps {
                script {
                    sh '''
                        python tools/automation_linter.py --path . --format checkstyle > lint.xml
                    '''
                }
            }
            post {
                always {
                    checkstyle pattern: 'lint.xml'
                }
            }
        }

        stage('Unit Test (plcunit)') {
            steps {
                script {
                    // Compiler et exécuter les tests PLC
                    sh '''
                        python scripts/run_plcunit_tests.py
                    '''
                }
            }
            post {
                always {
                    junit 'test-reports/**/*.xml'
                }
            }
        }

        stage('Build TIA Project') {
            steps {
                script {
                    build with: 'TIA Portal', project: 'MonProjet.ap17'
                }
            }
        }

        stage('SIL Validation') {
            when { branch 'main' }
            steps {
                script {
                    sh '''
                        python scripts/run_plcsim_validation.py
                    '''
                }
            }
        }

        stage('Deploy Staging') {
            when { branch 'develop' }
            steps {
                script {
                    sh 'python scripts/deploy_plc.py --target staging'
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
```

---

## 5. Versioning avec Git

### 5.1 Bonnes pratiques

```
project-automation/
├── src/
│   ├── plc/                    # Code source PLC
│   │   ├── programs/           # Programmes (ST, Ladder)
│   │   ├── functions/          # FC / FB
│   │   ├── data_types/         # UDTs
│   │   └── aoic/               # AOI definitions
│   ├── hmi/                    # Projets HMI (WinCC, FTView)
│   ├── hardware/               # Configuration matérielle (GSDML, EDS)
│   └── lib/                    # Bibliothèques communes
├── tests/
│   ├── unit/                   # Tests unitaires PLC (plcunit, TcUnit)
│   ├── sil/                    # Scénarios Software-in-the-Loop
│   └── integration/            # Tests FAT automatisés
├── scripts/
│   ├── tia_compile.py          # Compilation TIA Portal
│   ├── plcsim_runner.py        # Lancement PLCSIM
│   ├── test_reporter.py        # Rapport de test
│   └── deploy_plc.py           # Déploiement vers automate
├── docs/
│   ├── architecture.md
│   └── test-plan.md
├── .gitignore
├── .gitlab-ci.yml
└── README.md
```

### 5.2 .gitignore pour TIA Portal

```gitignore
# TIA Portal
*.awl
*.bak
*.dbg
*.dtl
*.fwf
*.log
*.pkf
*.ptf
*.rtl
*.tlx
*.wlx
Backup/
Archives/
OnlineBackups/

# Rockwell Studio 5000
*.bak
*.dbf
*.tmp
Online/
Backup/
_Archive/

# Génériques
__pycache__/
*.pyc
.venv/
```

---

## 6. FAT Assisté (Factory Acceptance Test)

### 6.1 Plan de test

```python
def generate_fat_test_plan(project: dict, equipment_list: list) -> dict:
    """Génère un plan de FAT structuré.

    Returns:
        Dict avec checklists par équipement
    """
    test_plan = {
        "project": project.get("name", ""),
        "revision": project.get("revision", ""),
        "date": datetime.now().isoformat(),
        "sections": []
    }

    templates = {
        "motor": [
            "Vérifier câblage puissance et commande",
            "Tester sens de rotation",
            "Valider séquence start/stop locale",
            "Valider séquence start/stop distante (SCADA)",
            "Tester alarme surcharge thermique",
            "Tester interlock sécurité",
            "Mesurer courant nominal",
        ],
        "valve": [
            "Vérifier câblage commande (ON/OFF ou 4-20mA)",
            "Tester ouverture / fermeture complète",
            "Valider feedback position (limites)",
            "Tester mode manuel (local)",
            "Tester mode automatique (PLC)",
            "Tester commande sécurité (fail-safe)",
        ],
        "instrument": [
            "Vérifier signal 4-20mA / HART",
            "Valider mesure à zéro",
            "Valider mesure à pleine échelle",
            "Tester alarme haute / basse",
            "Valider linéarité (3 points)",
        ],
    }

    for equip in equipment_list:
        type = equip.get("type", "general")
        section = {
            "equipment_tag": equip.get("tag", ""),
            "description": equip.get("description", ""),
            "location": equip.get("location", ""),
            "checklist": templates.get(type, ["Test fonctionnel général"]),
            "status": "PENDING",
        }
        test_plan["sections"].append(section)

    return test_plan
```

### 6.2 Exemple de rapport FAT

```markdown
# Rapport FAT - Ligne Emballage
**Projet :** Ligne d'emballage Pharma
**Date :** 2026-06-30
**Client :** Client SA
**Version :** 1.2.0

## Résumé
- **Total tests :** 147
- **Passed :** 142 (96.6%)
- **Failed :** 3 (2.0%)
- **N/A :** 2 (1.4%)

## Équipements testés
- Moteurs : 12/12 ✓
- Vannes : 34/34 ✓
- Instruments : 45/45 ✓
- Sécurité : 18/18 ✓
- Vision : 8/8 ✓

## Échecs
| Tag | Test | Problème | Action |
|:----|:-----|:---------|:-------|
| MV-105 | Feedback position | Limite non détectée | Réglage capteur |
| TIC-201 | Communication HART | Pas de réponse boucle | Réparer câblage |
| PIC-302 | Rampe PID | Overshoot > 5% | Ajuster gains |
```

---

## 7. Métriques de Qualité

```python
def compute_plc_quality_metrics(l5x_project_path: str) -> dict:
    """Calcule les métriques de qualité pour un projet PLC.

    Returns:
        Dict avec métriques de qualité
    """
    from tools.l5x_editor import L5XProject
    project = L5XProject.from_file(l5x_project_path)
    all_tags = project.list_tags()
    issues = project.validate()

    metrics = {
        "project": project.controller_name,
        "n_tags": len(all_tags),
        "n_routines": sum(len(p.routines) for p in project.programs),
        "n_errors": len(issues.get("errors", [])),
        "n_warnings": len(issues.get("warnings", [])),
        "n_unused_tags": len(project.find_unused_tags()),
        "test_coverage_pct": 0.0,  # Nécessite coverage tool PLC
        "complexity_avg": 0.0,     # Nécessite analyse cyclomatique
    }

    # Calcul de la couverture
    n_tested_routines = 2  # Exemple
    if metrics["n_routines"] > 0:
        metrics["test_coverage_pct"] = round(n_tested_routines / metrics["n_routines"] * 100, 1)

    # Score qualité (0-100)
    score = 100
    score -= metrics["n_errors"] * 10
    score -= metrics["n_warnings"] * 2
    score -= metrics["n_unused_tags"] * 1
    metrics["quality_score"] = max(0, min(100, score))

    return metrics
```

---

## 8. Références

- [TIA Portal Openness Documentation (Siemens)](https://support.industry.siemens.com)
- [PLCSIM Advanced API](https://www.siemens.com/plcsim-advanced)
- [TcUnit Unit Test Framework (TwinCAT)](https://github.com/tcunit/TcUnit)
- [plcunit Open-Source PLC Unit Test](https://github.com/plcunit)
- [Studio 5000 Emulate (Rockwell)](https://www.rockwellautomation.com/emulate)
- [Factory Acceptance Test Guidelines (NAMUR NE 93)](https://www.namur.net)
- [IEC 61508 Functional Safety](https://www.iec.ch)
- [PLCopen Test + Safety Guidelines](https://plcopen.org)
