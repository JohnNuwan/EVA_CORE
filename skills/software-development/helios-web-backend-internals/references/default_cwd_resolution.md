# `/api/fs/default-cwd` — exact resolution logic

Source: `web/server/web_server.py`

## Route handler (~line 1655)

```python
@app.get("/api/fs/default-cwd")
async def fs_default_cwd():
    cwd = _fs_default_cwd()
    return {"cwd": cwd, "branch": _fs_git_branch(cwd)}
```

## Resolution helper `_fs_default_cwd()` (~line 1123)

```python
def _fs_default_cwd() -> str:
    cfg_terminal = load_config().get("terminal") or {}
    raw = str(cfg_terminal.get("cwd") or os.environ.get("TERMINAL_CWD") or "").strip()
    if raw and raw not in {".", "auto", "cwd"}:
        try:
            candidate = Path(raw).expanduser().resolve(strict=False)
            if candidate.is_dir():
                return str(candidate)
        except (OSError, RuntimeError):
            pass
    return str(Path.cwd())
```

## Git branch helper `_fs_git_branch()` (~line 1136)

```python
def _fs_git_branch(cwd: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "branch", "--show-current"],
            capture_output=True, text=True, timeout=2, check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""
```

## Precedence summary

| Priority | Source | Notes |
|----------|--------|-------|
| 1 | `terminal.cwd` in config.yaml | via `load_config()` |
| 2 | `TERMINAL_CWD` env var | only if config has no value |
| 3 | `Path.cwd()` | process working dir of the backend |

- Sentinel values `.` / `auto` / `cwd` → treated as unset (skip to next).
- Candidate must `is_dir()` or it falls back silently.
- `branch` = `git -C <cwd> branch --show-current`, 2 s timeout, `""` on failure.

## Confirming tests (`tests/helios_cli/test_web_server_fs.py`)

- `test_fs_default_cwd_prefers_existing_terminal_cwd` (line 151): config `cwd`
  wins over `TERMINAL_CWD` and over the process CWD.
- `test_fs_default_cwd_falls_back_when_terminal_cwd_is_invalid` (line 163): an
  unresolvable `terminal.cwd` falls through to the process `Path.cwd()`.
- `test_fs_endpoints_require_auth` (line 177): `/api/fs/*` (incl. default-cwd)
  require the session token (401 without it).

## Frontend call sites

- `web/templates/pages/chat.html:820` — `fetch('/api/fs/default-cwd', { headers })`
- `web/vue-client/src/views/Chat.vue:630` — `apiFetch('/api/fs/default-cwd')`
