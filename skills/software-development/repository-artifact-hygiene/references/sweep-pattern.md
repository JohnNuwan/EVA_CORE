# Repo artifact hygiene - concrete sweep pattern

Use this quick sequence after batch file creation:

1. Enumerate canonical parents
- `skills/`
- `plugins/`
- `optional-mcps/`
- `projects/`

2. Search for likely stray mirrors
- `workspace/skills/**`
- root-level directories named like a plugin or MCP
- root-level `references/` support files that should live under a skill
- generic root files accidentally created during patch/write retries

3. Produce two lists
- KEEP: canonical files that exist where intended
- REMOVE: duplicates and non-canonical mirrors

4. Special root-file check
- Re-open `README.md`
- Re-open any root manifest/config that could have been overwritten by a mis-resolved path

5. If cleanup is blocked
- Hand the user an explicit deletion list
- Mark any accidental root-file overwrite as high priority for manual restoration
