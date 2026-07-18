---
name: code-reviewer
description: Review de code automatisée avec analyse de sécurité, style et qualité
---

# Code Reviewer Skill

Analyse le code modifié dans une session et produit une review structurée.

## Usage

Appelé automatiquement après des modifications de code, ou manuellement via `code_review()`.

## Checklist

1. **Sécurité** — injections, secrets exposés, permissions
2. **Style** — conventions du projet (PEP 8 pour Python, normes IEC 61131-3 pour PLC)
3. **Performance** —复杂度, allocations inutiles
4. **Robustesse** — gestion d'erreurs, edge cases
5. **Maintenabilité** — nommage, documentation, complexité cyclomatique