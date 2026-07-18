---
name: plc-testing-cicd
description: "Concevoir des tests unitaires et pipelines CI/CD pour PLC."
version: 1.0.0
author: Actemium
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [plc, testing, unit-tests, cicd, devops, twincat, tcunit, plcsim-advanced, simulation]
  related_skills: [beckhoff-twincat, siemens-scl]
---

# CI/CD et Tests Unitaires pour Automates (PLC)

## Vue d'ensemble

Le développement d'automatisme moderne intègre les méthodologies DevOps. L'automatisation des compilations, le versioning propre avec Git et l'exécution systématique de tests unitaires permettent de sécuriser le code avant le déploiement sur site. 

Cette compétence guide l'agent Helios pour écrire des tests unitaires PLC (avec `TcUnit` sous TwinCAT), concevoir des scripts d'intégration fonctionnels (avec `PLCSIM Advanced` sous Siemens), et structurer des pipelines de CI/CD (GitLab CI, GitHub Actions) pour les projets d'automatisme.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Concevoir un jeu de tests unitaires pour valider la logique d'un bloc fonctionnel PLC (FB).
- Automatiser la validation d'un programme Siemens S7 en pilotant une simulation d'I/O via l'API PLCSIM Advanced.
- Écrire un script ou un fichier de configuration YAML de pipeline de CI/CD pour automatiser la compilation et le test de projets PLC.
- Configurer des runners de compilation headless pour TwinCAT ou TIA Portal.

---

## 1. Tests Unitaires pour TwinCAT avec TcUnit

`TcUnit` est le framework de test unitaire standard conforme à la CEI 61131-3 pour Beckhoff TwinCAT. Les tests sont écrits sous forme de blocs fonctionnels (FB) qui héritent de `FB_TestSuite`.

### Exemple de bloc de test unitaire pour un bloc d'échelle analogique :
```pascal
(* Bloc Fonctionnel FB_Scale_Test héritant de TcUnit.FB_TestSuite *)
FUNCTION_BLOCK FB_Scale_Test EXTENDS FB_TestSuite
VAR
    fbScale : FB_Scale; // Instance du bloc à tester
    
    // Variables d'entrées
    rInputRaw : REAL;
    rRawMin   : REAL := 0.0;
    rRawMax   : REAL := 100.0;
    rEUMin    : REAL := 0.0;
    rEUMax    : REAL := 10.0;
    
    // Variables de sorties
    rOutputScaled : REAL;
    bScaleFault   : BOOL;
END_VAR

(* Corps du Bloc de Test *)
TEST('TestScaleNominal');

// 1. Arrange & Act
rInputRaw := 50.0;
fbScale(
    Input_Raw := rInputRaw,
    Raw_Min := rRawMin,
    Raw_Max := rRawMax,
    EU_Min := rEUMin,
    EU_Max := rEUMax,
    Output_Scaled => rOutputScaled,
    Scale_Fault => bScaleFault
);

// 2. Assert
AssertEquals_REAL(
    Expected := 5.0,
    Actual := rOutputScaled,
    Delta := 0.01,
    Message := 'La valeur de mise à l'échelle nominale à 50% devrait être 5.0'
);
AssertFalse(
    Condition := bScaleFault,
    Message := 'Le bit de défaut ne devrait pas être actif'
);

TEST_FINISHED();
```

---

## 2. Tests Fonctionnels Automatisés Siemens (PLCSIM Advanced)

Pour Siemens S7-1500, nous utilisons l'API de **PLCSIM Advanced** pour lancer une instance virtuelle de l'automate, y charger le programme, et valider son comportement en simulant le terrain avec un script Python.

### Exemple de script Python de test fonctionnel d'I/O :
```python
import time
# verify_plc_sim charge dynamiquement le wrapper C# PLCSIM Advanced API
from tools.verify_plc_sim import SiemensPLCSimulator

# 1. Démarrage de l'instance de simulation
sim = SiemensPLCSimulator(instance_name="PLCSIM_Test_Line1")
sim.start()

# 2. Chargement des variables I/O
# Simuler l'appui sur le bouton marche (Entrée %I0.0 de l'automate)
sim.write_tag("Tag_Start_Button", True)
time.sleep(0.1) # Attente du cycle automate
sim.write_tag("Tag_Start_Button", False)

# 3. Validation de l'activation du moteur (Sortie %Q0.0 de l'automate)
time.sleep(1.0) # Attente du temps de démarrage
motor_state = sim.read_tag("Tag_Motor_Running")

# Assertion du test
if motor_state == True:
    print("TEST SUCCEEDED: Le moteur a démarré après appui sur le bouton.")
else:
    print("TEST FAILED: Le moteur ne s'est pas activé.")
    
# 4. Nettoyage
sim.stop()
```

---

## 3. Configuration de Pipelines de CI/CD (GitLab CI)

La compilation automatisée des projets PLC nécessite d'utiliser des conteneurs Windows ou des serveurs d'intégration possédant les licences et logiciels d'ingénierie installés.

### Exemple de fichier `.gitlab-ci.yml` pour compiler un projet TwinCAT :
```yaml
stages:
  - build
  - test

build_twincat:
  stage: build
  tags:
    - windows-builder # Cible un runner Windows avec TwinCAT XAE installé
  script:
    - echo "Démarrage de la compilation du projet TwinCAT..."
    # Utilisation de la CLI TwinCAT pour compiler
    - '& "C:\Program Files (x86)\Beckhoff\TcXaeShell\Common7\IDE\devenv.com" "MyTwinCATProject.sln" /Build "Release|TwinCAT RT (x64)"'
  artifacts:
    paths:
      - MyTwinCATProject/_boot/

run_unit_tests:
  stage: test
  tags:
    - windows-runner
  script:
    - echo "Exécution des tests unitaires TcUnit..."
    # Démarre le runtime TwinCAT local en mode Config et injecte les tests
    - '.venv\Scripts\python.exe scripts/run_tcunit_runner.py --solution "MyTwinCATProject.sln"'
  dependencies:
    - build_twincat
```

---

## Pièges Courants (Common Pitfalls)

1. **Compilation échouée en CI à cause de fenêtres interactives (Popups) :**
   * *Erreur :* Le script de CI reste bloqué indéfiniment. Le compilateur (ex: TIA Portal ou TwinCAT Shell) attend qu'un opérateur clique sur "OK" sur une fenêtre d'avertissement graphique invisible.
   * *Correction :* Utiliser des arguments de commande headless stricts (ex: `/NoSplash`, `/Silent`) et s'assurer que les configurations du projet désactivent l'authentification interactive.

2. **État mémoire persistant entre les tests (State Leakage) :**
   * *Erreur :* Le test 2 échoue de manière erratique car le test 1 a laissé un bit de défaut actif en mémoire ou n'a pas réinitialisé un timer.
   * *Correction :* Toujours écrire une phase de nettoyage ("Teardown" ou "Reset") dans le code automate au démarrage de chaque test unitaire pour remettre les mémoires à zéro.

3. **Instanciation concurrente de simulateurs :**
   * *Erreur :* Les tests en parallèle échouent car deux runners tentent de démarrer une instance PLCSIM Advanced avec le même port TCP ou le même nom d'instance.
   * *Correction :* Utiliser des variables d'environnement uniques (ex : `CI_JOB_ID`) pour nommer dynamiquement les instances et les isoler sur des adresses IP de sous-réseau virtuel différentes.

---

## Liste de Vérification (Checklist)

- [ ] Tous les blocs de tests unitaires héritent de `FB_TestSuite` de `TcUnit` et appellent `TEST_FINISHED()` en fin de cycle.
- [ ] Le code de test s'assure de réinitialiser l'état des variables globales et blocs fonctionnels avant le début de chaque bloc `TEST()`.
- [ ] Les scripts de compilation dans les fichiers de pipeline CI/CD redirigent la sortie d'erreur standard (stderr) et renvoient des codes de sortie non nuls en cas d'erreur.
- [ ] Les instances virtuelles d'automates (PLCSIM) créées pour les tests sont systématiquement arrêtées et supprimées dans des blocs `try...finally` pour éviter les fuites de processus sur le serveur.
- [ ] Les fichiers `.gitignore` du projet excluent les fichiers temporaires générés par TIA Portal (`~*`) et TwinCAT (`.vs`, `LineInfo`).
