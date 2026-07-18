---
description: Détails techniques et guide pratique pour la génération automatisée de code Rockwell à partir de spécifications fonctionnelles (FDS).
tags: [automation, rockwell, generation, FDS]
---

# Guide de Génération Automatisée Rockwell

## Workflow de Génération depuis FDS
L'automatisation de la génération de code Rockwell à partir de documents FDS suit ce flux :

1.  **Extraction de texte** : Utilisation de `pypdf` (pour PDF) ou `python-docx` (pour DOCX).
2.  **Analyse LLM** : Extraction des séquences, états (CASE machine), entrées/sorties et interverrouillages.
3.  **Génération XML** : Utilisation du script `scripts/generate_rockwell_from_fds.py` pour créer :
    - Un fichier `.st` (Structured Text).
    - Un fichier `_AOI.L5X` (Add-On Instruction).
    - Un fichier `_Routine.L5X` (Routine de programme standard).
4.  **Validation** : Le code généré respecte strictement la syntaxe Rockwell : `:=` pour l'affectation, `;` en fin d'instruction, et timers avec `TON` (Preset en ms, accès via `.DN`).

### Pitfalls et Bonnes Pratiques
- **Numérotation des Skids** : Utilisez toujours le flag `--skid` pour remplacer dynamiquement les placeholders `SKXX` dans la FDS par le numéro réel du skid, sinon le code généré contiendra des noms de variables invalides.
- **Caractères XML** : Le script de génération gère automatiquement les caractères réservés (`<`, `>`) via des blocs CDATA. Ne tentez pas de les échapper manuellement.
- **Règles de nommage** : Si la FDS contient des noms longs, le générateur les nettoie mais vérifiez toujours que le nom résultant reste signifiant pour l'instrumentation (limite de 40 car.).
