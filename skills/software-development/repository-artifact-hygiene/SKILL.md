---
name: repository-artifact-hygiene
description: "Use when creating, moving, or batch-editing many files in a repo so you finish with a clean canonical tree and a verified list of stray artifacts to remove."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [repository, hygiene, file-organization, cleanup, verification, artifacts]
    related_skills: [project-output-organization, helios-agent-skill-authoring, test-driven-development]
---

# Repository Artifact Hygiene

## Vue d'ensemble

Use this skill after any session that creates or rewrites many files across a repository: new skills, plugins, MCP manifests, tests, generated docs, or support files. The goal is not only to write the intended files, but to finish with a repository tree that is canonical, auditable, and free of accidental duplicates or misplaced artifacts.

This skill is especially useful when file-tool path resolution, batch writes, or partial retries can leave behind extra files in the repo root, under `workspace/`, or in sibling directories that look plausible but are not part of the intended structure.

## Quand l'utiliser

Use when:
- You created multiple files in one session and need to verify they landed in the correct directories.
- You added new skills, plugins, MCP servers, manifests, or tests.
- You suspect duplicate files may exist in both canonical and non-canonical locations.
- You need to hand the user an exact cleanup list when deletion is blocked by policy.

Do not use for:
- A single isolated file edit with no new files.
- Pure content revisions where no path ambiguity exists.
- Cleanup of build artifacts already covered by project-specific tooling.

## Workflow recommandé

1. Establish the canonical target tree first.
   - Skills belong under `skills/<category>/<name>/...`
   - Plugins belong under `plugins/<name>/...`
   - Optional MCP manifests belong under `optional-mcps/<name>/manifest.yaml`
   - MCP server code belongs under `projects/<project-name>/...`

2. After writing files, perform a hygiene sweep.
   - Look for duplicates under `workspace/`
   - Look for suspicious root-level files that match files you meant to place deeper in the tree
   - Look for sibling directories whose names mirror plugin or MCP names outside the canonical parent

3. Verify canonical files exist and are the ones that should be kept.
   - Confirm the intended file exists in the expected path
   - Confirm manifests point to real server files
   - Confirm support files (`references/`, `templates/`, `scripts/`) live under the owning skill directory

4. Build two explicit lists.
   - Keep list: canonical files and directories
   - Remove list: stray duplicates, root-level accidents, workspace mirrors, malformed sibling trees

5. Check for collateral damage.
   - Re-open any important top-level files touched during the session (especially `README.md` or key manifests)
   - If a top-level file was accidentally overwritten, restore it before finishing when policy allows
   - Treat nested README writes as high-risk when tool path resolution has been flaky: verify the resolved path immediately, then re-open BOTH the intended nested `.../README.md` and the root `README.md` to confirm the write landed where expected
   - After user-performed manual cleanup, re-run the hygiene sweep and confirm that canonical keep-files (for example plugin `plugin.yaml`, plugin `README.md`, and MCP `manifest.yaml`) were not deleted along with the stray artifacts

6. If destructive cleanup is blocked by policy, do not hide it.
   - Report the exact files to delete
   - Distinguish “safe to delete” from “needs user confirmation”
   - Make clear that the repository is functionally improved but not fully clean yet

## Heuristics for suspicious artifacts

Treat these as high-suspicion patterns:
- `workspace/skills/...` duplicates of real `skills/...` files
- Root-level files with generic names like `hello.txt` that were not part of the user request
- Root-level directories mirroring plugin or MCP names when the canonical location should be nested (`skill-audit/`, `industrial-pcap/`, etc.)
- Support files created under a shared top-level `references/` instead of the owning skill directory
- A root `README.md` changed when you were trying to write a nested project README

## Deliverable standard

When cleanup is needed, end with:
- Canonical paths to keep
- Exact stray paths to remove
- Any blocked cleanup actions due to policy/tooling
- Any high-risk file that should be manually restored from git before commit

## Support files

- `references/sweep-pattern.md` : concise post-write hygiene sweep for detecting canonical vs stray artifacts.
- `references/readme-and-cleanup-recovery.md` : recovery checklist for nested README path mistakes and post-cleanup restoration of canonical plugin/MCP files.

## Pièges Courants (Common Pitfalls)

1. Assuming a write succeeded to the intended nested path without re-checking the resolved path.
2. Leaving `workspace/` duplicates because the canonical file was also created successfully.
3. Reporting “done” without distinguishing keep-vs-remove artifacts.
4. Forgetting to inspect top-level files after path-resolution mistakes.
5. Letting a manual cleanup remove canonical plugin/MCP files together with the intended stray duplicates.
6. Treating blocked deletion as a minor note instead of a concrete cleanup task.

## Liste de vérification (Checklist)

- [ ] Canonical target directories were identified before or during the write phase.
- [ ] A post-write sweep checked for root-level accidents and `workspace/` duplicates.
- [ ] Canonical files to keep were explicitly identified.
- [ ] Stray files to remove were explicitly identified.
- [ ] Critical top-level files were checked for accidental overwrite.
- [ ] Any policy-blocked cleanup was reported clearly to the user.
