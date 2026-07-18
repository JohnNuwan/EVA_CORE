# Industrial capability strengthening patterns

Session-derived patterns worth reusing when improving an industrial EVA library:

1. Priorize capability surface first.
   - Add MCPs/plugins before polishing SKILL.md when the user asked to improve the whole collection.
   - High-value examples from this session class: offline project inspector, industrial PCAP analyzer, document tag extractor, OPC UA companion validator, skill-audit plugin.

2. Upgrade weak umbrellas by cluster.
   - Treat coherent families together: motion/safety first, then OT audit, SCADA migration, validation, etc.
   - This keeps vocabulary, deliverables, and checklists aligned across vendors.

3. For motion/safety umbrellas, `references/version-validation-matrix.md` is a strong default support file.
   Recommended contents:
   - version/toolchain to confirm,
   - axis/safety function scope,
   - homing or reset behavior,
   - restart-after-fault expectations,
   - minimum FAT/SAT validation points.

4. Use a weakness audit heuristic before editing.
   Useful ranking dimensions:
   - short SKILL.md length,
   - missing `Quand l'utiliser`, `Pièges Courants`, or `Checklist`,
   - missing `references/`, `templates/`, or `scripts/`.

5. Do not overlearn from authorization-policy failures.
   If destructive cleanup is blocked by policy, capture the maintenance pattern elsewhere but do not record "tool X cannot delete files" as a durable constraint.

6. Expected user workflow preference for this class of task.
   In a collection-strengthening request, the preferred execution order is:
   - MCP/plugin work first,
   - umbrella skill strengthening second,
   - residual cleanup last.

7. Add a repository-hygiene pass after the capability work.
   Look specifically for:
   - duplicate trees under `workspace/` that shadow canonical `skills/` content,
   - stray root-level files/directories accidentally created during path normalization,
   - MCP/plugin manifests written outside their expected catalog directories.
   Treat move-safe normalization as a first-class maintenance step even when destructive cleanup must be deferred.
