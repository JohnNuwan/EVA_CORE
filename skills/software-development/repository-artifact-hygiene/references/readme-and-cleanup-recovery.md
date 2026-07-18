# Nested README + post-cleanup recovery checklist

Use this when a repo session involved many file writes, nested project READMEs, or manual user cleanup.

## 1. Nested README write safety
- Treat writes to `projects/.../README.md` as high-risk if path resolution has already been flaky in the session.
- After the write, verify the resolved target path immediately.
- Re-open both files:
  - intended nested `projects/.../README.md`
  - root `README.md`
- If the nested file is missing and the root README changed, assume a mis-targeted write and stop further nested README writes until the root file is corrected.

## 2. Canonical files easy to delete by mistake during cleanup
Typical keep-files that users may remove while deleting duplicates:
- `optional-mcps/<name>/manifest.yaml`
- `plugins/<name>/plugin.yaml`
- `plugins/<name>/README.md`
- canonical `skills/.../SKILL.md` when a duplicate also existed under `workspace/...`

## 3. Post-cleanup verification sweep
Re-check these classes after any manual cleanup:
- `workspace/...` duplicates are gone
- root-level accidental files are gone
- canonical plugin directories still contain `__init__.py`, `plugin.yaml`, and README when expected
- canonical optional MCP entries still contain `manifest.yaml`
- top-level `README.md` still matches the intended repo entry-point content

## 4. Reporting pattern
When deletion was user-driven or policy-blocked, report explicitly:
- what was safely removed
- what canonical files had to be restored
- what still remains blocked
- whether the root README or manifests need manual git restoration
