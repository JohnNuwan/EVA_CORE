---
name: EVA-web-backend-internals
description: >-
  Investigate and explain how the EVA web dashboard / file-browser
  (web/server/web_server.py) determines filesystem paths, the default working
  directory, config precedence, and related /api/fs/* behavior. Use when the
  user asks "where is X", "what is my default workspace/CWD", "why does the
  terminal open in the wrong directory", or "how is Y path resolved" in the
  EVA backend.
---

# EVA Web Backend — Path & Default-CWD Resolution

## When to use

- "Where is the default workspace / CWD in the web UI?"
- "How does the file browser decide its starting directory?"
- "Why is my terminal opening in the wrong folder?"
- "How is `<some path | config>` determined in the EVA backend?"
- Tracing any `/api/fs/*` endpoint behavior.

## Key source files

- `web/server/web_server.py` — FastAPI app, all `/api/fs/*` endpoints and the
  private `_fs_*` helpers that hold the real logic.
- Frontend consumers: `web/templates/pages/chat.html` and
  `web/vue-client/src/views/Chat.vue` both call `GET /api/fs/default-cwd` on
  load to seed the file tree / terminal start directory.
- Config loader: `load_config()` (reads `config.yaml`).
- Tests that pin the intended behavior: `tests/EVA_cli/test_web_server_fs.py`.

## How the default working directory is resolved

Endpoint: `GET /api/fs/default-cwd` → handler `fs_default_cwd()`
(`web/server/web_server.py`, ~line 1655). Returns:

```json
{ "cwd": "<path>", "branch": "<git branch or ''>" }
```

The actual resolution lives in the private helper `_fs_default_cwd()`
(~line 1123). Precedence (first match wins):

1. `terminal.cwd` key in `config.yaml` (via `load_config()`).
2. else the `TERMINAL_CWD` environment variable.
3. else the web-server **process** working directory (`Path.cwd()` — i.e. the
   directory the backend was launched from).

Guards you must explain when asked:

- **Sentinel values are ignored.** If the value is `.`, `auto`, or `cwd`, it is
  treated as "unset" and the resolver falls through to the next source.
- **Must resolve to an existing directory.** The candidate is `~`-expanded and
  checked with `is_dir()`. If it does not exist / is not a directory (or
  `resolve()` raises), the code **silently falls back** to the next source and
  ultimately to the process CWD. A bad or missing `terminal.cwd` therefore
  never becomes the default.
- `branch` is obtained via `git -C <cwd> branch --show-current` with a 2-second
  timeout; returns `""` on any failure (`_fs_git_branch`, ~line 1136).

Exact code excerpts and the confirming tests are in
`references/default_cwd_resolution.md`.

## The config → env bridge, the `DEFAULT_CONFIG` default, and the launch chain

The three "sources" above are **not independent at runtime** — `terminal.cwd`
is bridged into `TERMINAL_CWD` at process startup, which is why a live
`TERMINAL_CWD` is usually present even when config only has a placeholder:

- **Default when no `config.yaml` exists.** `load_config()` (reads
  `~/.EVA/config.yaml`) falls back to `DEFAULT_CONFIG`, where
  `terminal.cwd = "."` (`EVA_cli/config.py`, ~line 964-967). The `"."`
  sentinel is treated as unset, so the resolver falls through to
  `TERMINAL_CWD` / process CWD.
- **CLI bridge (`EVA_cli/cli.py`, ~line 593-640).** For
  `terminal.backend: local` it forces `terminal.cwd = os.getcwd()`
  (~line 596-598) and then exports it to the `TERMINAL_CWD` env var via the
  `env_mappings` dict (`"cwd": "TERMINAL_CWD"`, ~line 604). So when running
  locally, `TERMINAL_CWD` becomes the launch directory.
- **Gateway bridge (`gateway/run.py`, ~line 1337-1345).** Reads `TERMINAL_CWD`;
  if it is empty or a sentinel (`.`/`auto`/`cwd`), it defaults to
  `MESSAGING_CWD` or the home directory. A `_EVA_GATEWAY` marker prevents the
  CLI bridge from clobbering a value already set correctly by the gateway.
- **Web server launch chain.** `GET /api/fs/*` is served by
  `web/server/web_server.py` (the FastAPI `app`). It is started **in-process**
  by `EVA_cli/web_server.start_server` (which does `from web.server import
  web_server` at `EVA_cli/web_server.py:12`), invoked from the dashboard
  command (`EVA_cli/main.py:10178`). There is **no `os.chdir`** on that
  path, so the backend's `Path.cwd()` = the launch directory of the `EVA`
  CLI — exactly what the local-backend bridge pushes into `TERMINAL_CWD`.

### How to check the live values (the four the user usually asks)

1. `os.environ.get("TERMINAL_CWD")` → `echo $TERMINAL_CWD` (the web server
   inherits this from the launching `EVA` process).
2. `terminal.cwd` in config.yaml → if no `~/.EVA/config.yaml` exists, it is
   the `DEFAULT_CONFIG` `"."` placeholder (effectively unset). Inspect
   `DEFAULT_CONFIG["terminal"]["cwd"]` in `EVA_cli/config.py`.
3. Process CWD of the web server → launch directory of the `EVA` CLI
   (no chdir on the launch path); equals `os.getcwd()` at startup.
4. Relative position of any top-level folder (e.g. `output/`) → confirm with a
   terminal `ls -la` / `find . -maxdepth N` — `search_files` is unreliable for
   bare directories (see Pitfalls).

The file:line map for the bridge, the launch chain, and the live-value probes
is in `references/cwd_bridge_and_launch.md`.

## Investigation workflow (reusable for any /api/fs/* question)

1. Grep the backend for the route string (e.g. `search_files` pattern
   `default-cwd`) to find the handler and the `_fs_*` helpers it calls.
2. Read the helper(s), not the route body — EVA routes delegate to private
   `_fs_*` functions where the precedence and guards actually live.
3. Confirm the intended contract with the tests under
   `tests/EVA_cli/test_web_server_fs.py` (e.g. `test_fs_default_cwd_*`
   encode config > env > process CWD and the invalid-path fallback).

## Pitfalls

- `search_files` with `target='files'` indexes file **names** and may **not**
  reliably surface a bare directory. Example from a real session: the `output/`
  folder at the repo root was missed by a name search but was confirmed
  immediately with a terminal `ls -la` / `find . -maxdepth N`. When you must
  confirm a directory exists or walk a tree, use the `terminal` tool, not
  `search_files` alone.
- Do not assume the route handler contains the logic — it almost always
  delegates to a `_fs_*` helper.
- `search_files` (the ripgrep-backed content search) can **silently return 0
  matches for a pattern that provably exists** when the regex contains special
  characters such as `(` `)` `{` or a `|` alternation, and it sometimes misses
  even plain substrings. In a real session `def _fs_default_cwd`,
  `uvicorn.run`, `DEFAULT_CONFIG`, and `web_server` all returned empty until
  re-run via `terminal` `grep -rn`. **Rule: when `search_files` returns an
  empty / suspicious result for a known-present string, verify with
  `terminal` `grep -rn --include=*.py` (or `rg`) before concluding the symbol
  is absent.**
