---
name: ot-audit
description: "Auditer et valider le style du code automate (SCL/L5X)."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [industrial, automation, code-audit, quality, plc, static-analysis]
    related_skills: [rockwell-studio5000, siemens-scl]
---

# Audit de Qualité et Validation Statique du Code Automate (OT-Audit)

## Vue d'ensemble

Le code d'automatisation industrielle régit des installations physiques critiques (usines, machines). Une erreur de syntaxe ou logique peut entraîner des dégâts matériels ou des risques corporels majeurs. Cette compétence instruit l'agent pour auditer de manière statique le code automate généré ou modifié (fichiers Siemens SCL `.scl` ou Rockwell XML `.L5X`) avant tout chargement en machine.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'auditer la qualité ou de relire du code Structured Text.
- De valider la conformité aux standards de programmation Actemium.
- D'analyser un commit Git contenant des modifications de logique PLC pour validation automatique (intégration continue CI/CD OT).

---

## 1. Grille d'Audit Statique et Points de Contrôle

L'agent doit analyser le code source ligne par ligne et s'assurer du respect des règles suivantes :

### 1.1 Respect de la Nomenclature Actemium
Vérifier que toutes les variables déclarées respectent les préfixes de portée :
- `i_` ou `in_` : Paramètre d'entrée (lecture seule).
- `q_` ou `out_` : Paramètre de sortie (écriture uniquement).
- `iq_` ou `io_` : Paramètre d'entrée/sortie (passage par référence).
- `stat_` : Variable statique persistante (FB uniquement).
- `temp_` : Variable temporaire sur pile (perdue en fin de cycle).

### 1.2 Sécurité des Boucles d'Indexation (Dépassement de Bornes)
Toute boucle `FOR` ou accès à un tableau (`Array`) par index variable doit être protégé.
*Exemple de défaut critique :*
```scl
// ERREUR : Si #index dépasse 9, l'automate passe en CPU STOP.
#q_Value := #myArray[#index];
```
*Correction exigée :*
```scl
// CORRECTION : Encadrer par une condition limite.
IF #index >= 0 AND #index <= 9 THEN
    #q_Value := #myArray[#index];
ELSE
    #q_Value := 0.0; // Fallback sécurisé
END_IF;
```

### 1.3 Sécurité des Boucles `WHILE` / `REPEAT`
Les boucles dont la sortie dépend d'une condition dynamique doivent posséder une sécurité watchdog matérielle (compteur maximum) pour empêcher un blocage de tâche de l'automate.

### 1.4 Protection et Casse des Timers (Rockwell / Siemens)
- Rockwell : Le champ `.PRE` doit être configuré en millisecondes et la fin de tempo validée par `.DN`.
- Siemens : Les tempos doivent être déclarées en multi-instances statiques (`stat_Timer : TON_TIME;`) et non en DB globaux.

---

## 2. Processus d'Audit Intégré à Git (CI/CD OT)

Helios peut être configuré avec ses routines de webhooks pour intercepter chaque nouveau commit poussé dans le dépôt. Le processus automatique applique l'évaluation suivante :

```
Nouveau Commit Git ➔ Détection fichier automate (.scl/.L5X) ➔ Analyse statique par Helios (OT-Audit) ➔ Rapport de revue automatique
```

L'agent compile les non-conformités sous la forme d'un tableau et évalue le code sur un score de 0 à 100. Tout score inférieur à 80 doit bloquer le déploiement ou marquer la Pull Request comme rejetée.

---

## Liste de vérification (Checklist)

- [ ] Toutes les variables de l'interface respectent les préfixes de nommage.
- [ ] Les accès aux tableaux par index dynamique sont encadrés par des conditions limites.
- [ ] Il n'y a pas de variables temporaires (`VAR_TEMP`) dont on attend la persistance au cycle suivant.
- [ ] Le code ne contient aucune boucle de traitement non bornée.
- [ ] Les tempos sont déclarées en multi-instances statiques pour Siemens SCL.
- [ ] Les fichiers L5X protègent bien le code ST par des balises `<![CDATA[ ... ]]>`.

