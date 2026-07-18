# Synthèse de Spécifications et Vérification Formelle de Code PLC

Ce document de référence rassemble les approches scientifiques récentes (*PLC-Spec-Syn*, OpenReview 2026, et *Agents4PLC*, arXiv) pour la génération de code Structured Text (ST) industriel fiable, compilable et vérifié sémantiquement.

---

## 1. Cadre de Synthèse Spécification $\rightarrow$ Code PLC

La programmation d'automates pour les infrastructures critiques exige que le code ne contienne aucune erreur d'exécution. Les approches classiques par LLM souffrent d'hallucinations syntaxiques. L'approche scientifique moderne repose sur la génération automatisée de spécifications de tâches fiables et le test systématique par boucle de rétroaction.

### Pipeline de Génération Multi-Agent
La synthèse de code Structured Text fiable s'effectue via une architecture multi-agent découplée :

```
[Spécification Métier] 
       │
       ▼
 ┌───────────┐       ┌─────────────┐       ┌─────────────┐
 │  Agent    │ ────> │    Agent    │ ────> │    Agent    │
 │ Planner   │       │  Generator  │       │  Compiler/  │
 └───────────┘       └─────────────┘       │  Verifier   │
                                           └──────┬──────┘
                                                  │ (Rétroaction Erreurs)
                                                  ▼
                                           ┌─────────────┐
                                           │    Agent    │
                                           │ Refactorer  │
                                           └─────────────┘
```

1.  **Planner** : Analyse le besoin en langage naturel ou diagramme logique et décompose le comportement en états de contrôle et invariants de sécurité.
2.  **Generator** : Synthétise le bloc de code Structured Text (IEC 61131-3) correspondant (variables, constantes, logique comportementale).
3.  **Compiler/Verifier** :
    *   **Vérification syntaxique** : Soumet le code généré à un compilateur/linter de référence pour intercepter les erreurs d'affectation de types, de points-virgules, ou d'indexation.
    *   **Vérification sémantique** : Analyse le code par rapport aux assertions logiques et invariants comportementaux (ex: validation des états des verrous de sécurité).
4.  **Refactorer** : Si des erreurs sont levées, l'agent prend le code fautif et les journaux de compilation pour corriger de manière itérative la logique.

---

## 2. Formalisation d'une Tâche PLC Vérifiable

Chaque bloc logique doit être structuré de manière à séparer la logique de contrôle et les vérifications de limites physiques :

```pascal
FUNCTION_BLOCK FB_LevelController
VAR_INPUT
    SensorLevel : REAL;     // Niveau d'eau mesuré en mètres
    MaxThreshold : REAL;    // Seuil maximal autorisé
    MinThreshold : REAL;    // Seuil minimal autorisé
END_VAR
VAR_OUTPUT
    PumpCommand : BOOL;     // Commande d'activation de la pompe
    AlarmState : BOOL;      // Alarme de niveau anormal
END_VAR
VAR
    isAlarm : BOOL;
END_VAR

BEGIN
    // 1. Vérification de la cohérence des entrées (Invariants physiques)
    IF MinThreshold >= MaxThreshold THEN
        AlarmState := TRUE;
        PumpCommand := FALSE;
        RETURN;
    END_IF;

    // 2. Logique de contrôle
    IF SensorLevel >= MaxThreshold THEN
        PumpCommand := TRUE;  // Vider la cuve
    ELSIF SensorLevel <= MinThreshold THEN
        PumpCommand := FALSE; // Arrêter le pompage
    END_IF;

    // 3. Assertion de sécurité sémantique
    isAlarm := (SensorLevel > (MaxThreshold + 0.5)) OR (SensorLevel < (MinThreshold - 0.5));
    AlarmState := isAlarm;
END_FUNCTION_BLOCK
```
