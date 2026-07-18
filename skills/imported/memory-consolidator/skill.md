---
name: memory-consolidator
description: Consolidation et optimisation de la mémoire agent
---

# Memory Consolidator Skill

Analyse et consolide les entrées mémoire pour éviter la fragmentation.

## Usage

Combine `memory_search` (vectoriel) et `memory` (traditionnel) pour
identifier les entrées redondantes et les fusionner.

## Procédure

1. **Analyse** — `memory_search` sur les entrées existantes pour détecter les doublons
2. **Identification** — entrées similaires (score cosinus > 0.85)
3. **Fusion** — combiner les entrées redondantes en une seule, plus complète
4. **Nettoyage** — `memory(action='remove')` sur les entrées obsolètes
5. **Vérification** — l'espace libéré permet de nouvelles entrées