---
name: skill-library-maintenance
description: "Use when auditing, expanding, and strengthening a EVA skill/MCP/plugin library as a reusable capability collection rather than doing one-off edits."
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [skills, mcp, plugins, library-maintenance, curation, capability-design]
    related_skills: [EVA-agent-skill-authoring, plan, requesting-code-review]
---

# Skill Library Maintenance

## Vue d'ensemble

Cette compétence sert à maintenir une bibliothèque EVA comme une collection de capacités réutilisables, pas comme une accumulation de micro-skills liées à une seule session. Elle couvre l'audit de la collection, la priorisation des écarts, l'amélioration des umbrellas existantes, l'ajout de support files utiles, et l'extension de la surface MCP/plugin quand cela apporte plus de valeur qu'une simple réécriture de SKILL.md.

Elle est particulièrement adaptée quand l'utilisateur demande de "faire le tour" d'une collection, corriger ses points faibles, enrichir les capacités, ou industrialiser une base de skills orientée métier.

## Quand l'utiliser

À utiliser pour :
- auditer une collection de skills existante ;
- identifier les trous de couverture, doublons et skills trop faibles ;
- prioriser les ajouts MCP/plugins versus enrichissement des SKILL.md ;
- transformer des observations de session en améliorations de bibliothèque durables.

Ne pas utiliser pour :
- une simple création de skill isolée sans enjeu de collection ;
- une tâche de code sans impact sur la bibliothèque ;
- un compte-rendu de session sans action de maintenance sur les capacités.

## Principe de priorisation

Quand l'utilisateur demande explicitement d'améliorer la collection de capacités, suivre cet ordre :
1. Ajouter ou renforcer les MCPs / plugins qui élargissent réellement la surface d'action.
2. Ensuite enrichir les skills qui pilotent l'usage de ces capacités.
3. Enfin reprendre les umbrellas faibles, trop courtes, ou mal structurées.

Pour cet utilisateur en particulier, la préférence exprimée dans cette session est claire : quand on améliore la collection, commencer par les MCPs et plugins, puis faire "tout le reste" après.

## Workflow recommandé

1. Cartographier l'existant.
   - Lister skills, MCPs optionnels et plugins déjà présents.
   - Identifier les familles déjà profondes vs superficielles.
2. Auditer les skills faibles.
   - Repérer les SKILL.md courtes.
   - Vérifier la présence des sections structurantes (`Vue d'ensemble`, `Quand l'utiliser`, `Pièges Courants`, `Checklist`).
   - Vérifier l'existence de `references/`, `templates/` ou `scripts/`.
3. Décider du bon niveau d'action.
   - Si le trou est outillage/capabilité : MCP ou plugin.
   - Si le trou est guidance d'usage : patch d'une umbrella.
   - Si le besoin est session-spécifique mais réutilisable : support file sous `references/`.
4. Enrichir par clusters, pas au hasard.
   - Traiter une famille cohérente d'un coup (ex: motion/safety, SCADA migration, OT audit).
   - Harmoniser le vocabulaire, les livrables attendus et les checklists dans toute la famille.
5. Vérifier après chaque vague.
   - Relire les fichiers modifiés.
   - Vérifier que les skills enrichies sortent du bas du classement des plus faibles.
6. Faire une passe de rangement physique du dépôt.
   - Rechercher les fichiers ou dossiers hors emplacement canonique (ex: doublons sous `workspace/`, fichiers racine parasites, répertoires de plugin/MCP créés au mauvais niveau).
   - Distinguer immédiatement ce qui est déplaçable sans risque de ce qui exige une suppression destructrice.
   - Si la politique d'autorisation bloque la suppression, finaliser quand même tout ce qui relève d'un move-safe normalization et laisser une liste claire des reliquats à nettoyer.

## Pattern de renforcement des skills faibles

Quand une umbrella est trop courte mais déjà pertinente :
- garder le nom et le périmètre ;
- ajouter `Quand l'utiliser` avec cas d'usage et exclusions ;
- ajouter `Axes de structuration` ou `Workflow recommandé` ;
- ajouter `Livrables attendus` ;
- enrichir `Pièges Courants` ;
- ajouter au minimum un support file utile, souvent `references/version-validation-matrix.md` pour les familles motion/safety.

## Quand préférer MCP/plugin à une skill

Créer ou renforcer un MCP/plugin si le gain principal est l'action elle-même :
- inspection offline de projets,
- extraction structurée de tags,
- validation d'un NodeSet OPC UA,
- synthèse de captures PCAP industrielles,
- audit automatique d'un catalogue de skills.

Créer ou enrichir une skill si le gain principal est la méthode, la priorisation ou la structuration des livrables.

## Pièges Courants (Common Pitfalls)

1. Ajouter une nouvelle skill pour chaque session au lieu d'améliorer une umbrella existante.
2. Améliorer des SKILL.md alors que le vrai manque est un outil/MCP/plugin.
3. Laisser des skills très courtes sans livrables attendus ni support files.
4. Mélanger backlog de session et skill de classe générale.
5. Interpréter un blocage de politique d'autorisation comme une règle durable de la bibliothèque.

## Support files

- `references/industrial-capability-strengthening-patterns.md` : motifs réutilisables observés lors d'un chantier réel d'amélioration de collection industrielle.

## Liste de vérification (Checklist)

- [ ] Le travail porte bien sur une collection de capacités, pas une micro-tâche isolée.
- [ ] Les MCPs/plugins à forte valeur ont été considérés avant les retouches de wording.
- [ ] Les skills faibles ont été traitées par familles cohérentes.
- [ ] Chaque umbrella enrichie contient des déclencheurs, livrables, pièges et checklist.
- [ ] Les détails spécifiques à une session ont été mis dans `references/` plutôt que dans le corps principal.
