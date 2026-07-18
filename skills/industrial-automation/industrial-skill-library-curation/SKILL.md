---
name: industrial-skill-library-curation
description: "Use when auditing, expanding, or remediating an industrial Helios skill library across MCPs, plugins, and domain skills instead of treating updates as one-off edits."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [skills, curation, industrial, mcp, plugin, audit, remediation, library]
    related_skills: [helios-agent-skill-authoring, helios-agent-mcp-development, plc-scada-platform-standards]
---

# Industrial Skill Library Curation

## Vue d'ensemble

Use this skill when the task is to improve an industrial Helios knowledge/tooling library at the collection level: identify weak skills, add missing MCPs/plugins first, then enrich the weakest domain skills with better structure, support files, and reusable validation artifacts. The goal is to raise the whole library's quality, not just patch a single page.

## Quand l'utiliser

À utiliser pour :
- auditer une collection de skills industrielles ;
- prioriser les manques MCP / plugins avant les simples textes ;
- renforcer des skills trop courtes ou peu structurées ;
- transformer des notes plates en skills de classe avec `references/`, `templates/` ou `scripts/`.

Ne pas utiliser pour :
- une correction mineure sur une seule skill déjà complète ;
- une session de recherche sans volonté de mise à jour durable ;
- une simple installation d'une skill externe non modifiée.

## Workflow recommandé

1. Cartographier la bibliothèque : outils MCP, plugins, umbrellas, skills faibles.
2. Corriger d'abord les manques d'outillage durables : MCPs, plugins, validateurs, extracteurs.
3. Ensuite, lister les skills les plus faibles selon :
   - longueur anormalement faible,
   - sections standard absentes,
   - absence de `references/`, `templates/` ou `scripts/`.
4. Enrichir les skills par clusters cohérents (motion, safety, SCADA, OT security, etc.), pas au hasard.
5. Pour chaque skill renforcée, ajouter au moins un support file quand cela améliore la réutilisabilité.
6. Vérifier par relecture ciblée ou script d'inventaire que les skills traitées ne restent plus en bas de classement.

## Critères de remédiation d'une skill faible

Renforcer en priorité les skills qui cumulent :
- moins de ~50 lignes ;
- manque de `## Quand l'utiliser` ;
- manque de `## Pièges Courants (Common Pitfalls)` ;
- manque de `## Liste de vérification (Checklist)` ;
- aucun support file.

## Patterns de support files utiles

- `references/version-validation-matrix.md` pour motion, safety, variateurs, validation de versions et essais terrain.
- `references/*-governance-checklist.md` pour modèles d'information, standards ou gouvernance.
- `references/*-transition-matrix.md` pour migration et transformation.
- `templates/*` pour matrices de traçabilité, handshakes, zones, resets, etc.

Voir aussi `references/remediation-checklist.md`.

## Pièges Courants (Common Pitfalls)

1. Créer beaucoup de nouvelles skills alors qu'une umbrella existante doit être renforcée.
2. Corriger des textes avant les manques d'outillage MCP/plugin qui ont plus d'effet structurel.
3. Laisser des skills courtes sans support files réutilisables.
4. Traiter les skills une par une sans logique de cluster métier.
5. Finir la passe sans vérification que les skills renforcées ont réellement quitté le bas du classement.
6. Perdre du temps sur des nettoyages destructifs quand la politique d'autorisation les bloque : prioriser les améliorations non destructives, puis signaler explicitement le blocage.
7. Pour les mises à jour de fichiers nombreuses, préférer des écritures unitaires vérifiables plutôt que des lots parallèles si la politique d'autorisation refuse certaines écritures groupées.

## Liste de vérification (Checklist)

- [ ] Les MCPs/plugins manquants ont été traités avant la cosmétique des skills.
- [ ] Les skills faibles ont été identifiées par critères explicites.
- [ ] Les mises à jour ont été faites par clusters cohérents.
- [ ] Chaque skill renforcée dispose d'une structure standard suffisante.
- [ ] Des support files pertinents ont été ajoutés quand utile.
- [ ] Une vérification finale confirme l'amélioration du cluster traité.
