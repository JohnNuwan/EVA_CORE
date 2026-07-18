# Default-CWD bridge, launch chain, and live-value probes

Source files (EVA backend).

## Config → env bridge

`terminal.cwd` (config.yaml) is the *canonical* setting, but at runtime it is
bridged into the `TERMINAL_CWD` environment variable, which `_fs_default_cwd`
also reads. Two bridge sites:

| Site | File:line | Behavior |
|------|-----------|----------|
| CLI local backend | `EVA_cli/cli.py:593-640` | For `terminal.backend: local`, forces `terminal.cwd = os.getcwd()` (`:596-598`) then exports to `TERMINAL_CWD` via `env_mappings` `{"cwd": "TERMINAL_CWD"}` (`:604`). |
| Gateway | `gateway/run.py:1337-1345` | Reads `TERMINAL_CWD`; if empty/sentinel, defaults to `MESSAGING_CWD` or home dir. `_EVA_GATEWAY` marker stops the CLI bridge from clobbering it. |

`DEFAULT_CONFIG` (`EVA_cli/config.py:964-967`):

```python
"terminal": {
    "backend": "local",
    "cwd": ".",          # Use current directory  -> sentinel
    ...
}
```

If `~/.EVA/config.yaml` is absent, `load_config()` returns `DEFAULT_CONFIG`,
so `terminal.cwd` is `"."` -> sentinel -> resolver falls through to
`TERMINAL_CWD` / `Path.cwd()`.

## Web server launch chain

- Served by `web/server/web_server.py` (FastAPI `app` hosting `/api/fs/*`).
- Started **in-process** by `EVA_cli/web_server.start_server`
  (`from web.server import web_server` at `EVA_cli/web_server.py:12`).
- Called from the dashboard command (`EVA_cli/main.py:10178`).
- **No `os.chdir`** anywhere on this path -> backend `Path.cwd()` =
  launch dir of the `EVA` CLI = what the local-backend bridge wrote into
  `TERMINAL_CWD`.

## Live-value probe checklist

| # | What the user asks | How to read it |
|---|--------------------|----------------|
| 1 | `TERMINAL_CWD` | `echo $TERMINAL_CWD` (inherited by the in-process web server) |
| 2 | `terminal.cwd` in config.yaml | absent -> `DEFAULT_CONFIG["terminal"]["cwd"] == "."` (placeholder). Inspect `EVA_cli/config.py` `DEFAULT_CONFIG`. |
| 3 | process CWD of web server | launch dir of `EVA` CLI (no chdir); equals `os.getcwd()` at startup |
| 4 | relative position of `output/` (or any top-level dir) | terminal `ls -la` / `find . -maxdepth N` - `search_files` misses bare dirs |

## Net result for a default local launch from the repo root

`terminal.cwd="."` -> sentinel skipped -> `TERMINAL_CWD` = repo root ->
`/api/fs/default-cwd` returns the repo root, so `output/` (a direct child
`./output`) shows at the top level of the file browser.
