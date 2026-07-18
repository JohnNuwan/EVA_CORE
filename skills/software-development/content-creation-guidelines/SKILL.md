---
name: content-creation-guidelines
description: >-
  User preferences and standards for all written content — skills, documents,
  code comments, docstrings, chat responses, and research papers. Captures
  language, structure, and formatting conventions required by the user.
category: software-development
---

# Content Creation Guidelines

## Language Requirement

**All content MUST be written in French.** This is a hard, non-negotiable requirement that applies to every form of output:

| Content type | Examples |
|-------------|----------|
| **Skills** | SKILL.md frontmatter descriptions, body content, reference files, templates, scripts |
| **Documents** | Any file created via write_file, patch, or terminal |
| **Code comments** | Inline comments, module docstrings, function docstrings, README |
| **Chat responses** | All explanations, summaries, analyses, answers |
| **Research papers** | Drafts, abstracts, notes, internal content |
| **Error messages** | Explanations of failures, debugging steps |

**Exception**: Only literal quotations, technical acronyms, proper names, and code identifiers (function names, variable names, API endpoints) may remain in their original language. Everything else — including explanations, context, and descriptions — must be in French.

## Structure Rule

**One competence per skill file.** Each skill must be self-contained and focused on a single domain. Never merge multiple distinct competences into one file. If a topic spans multiple domains, create separate skill files for each.

## Skill File Format

Every SKILL.md must include:

1. **YAML frontmatter** with `name`, `description`, and `category`
2. **# Title** (French) matching the competence name
3. **## Présentation** — context, scope, and objectives
4. **## Domaines de Recherche Principaux** (or equivalent content sections) — 5-8 detailed sections with sub-sections
5. **## Catégories** — relevant arXiv categories, tools, or domains
6. **## Articles Notables Récents** — specific recent papers with real titles and venues
7. **## Comment Effectuer la Veille** — URLs, keywords, search strategies

## Git Commit Conventions

**Tous les messages de commit git doivent être en français.** Format :

- Messages concis, 50-72 caractères, une ligne
- Décrire le QUOI et le POURQUOI
- Préfixer par le composant quand pertinent : `ES: ...`, `V5: ...`, `PPO: ...`
- **Toujours `git push` immédiatement après chaque commit**
- Un commit par changement atomique

## Tone & Conventions

- Use professional but clear language — level ingénieur/docteur
- Be specific and concrete: include tool names, library versions, API endpoints, framework names
- Avoid vague generalities; prefer actionable, referenceable content
- Tables are preferred for structured comparisons
- Lists (bulleted or numbered) for enumerating options, categories, or steps
- Keep descriptions in YAML frontmatter concise (one sentence) but descriptive