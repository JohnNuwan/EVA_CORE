# Terminal FTMO branded sous Wine — notes de session (2026-07-18)

## Installeur

- URL : https://download.terminal.free/cdn/web/ftmo.global.markets/mt5/ftmo5setup.exe (~5,1 Mo)
- `wine ftmo5setup.exe /auto` installe dans `drive_c/Program Files/FTMO Global Markets MT5 Terminal/` (et non `MetaTrader 5/`)
- Binaires : terminal64.exe, MetaEditor64.exe, metatester64.exe, uninstall.exe
- Premier lancement : mise à jour de 453 fichiers MQL5, recompilation complète (~2 min), téléchargement des historiques (EURUSD, GBPUSD, USDJPY, USDCHF — fichiers 2023.hcc dans Bases/Default/History/)
- Vérifié : build 6032 démarre sous Wine 10.0 / Debian 13

## Comportement observé sous Wine

- Log terminal : `logs/YYYYMMDD.log` (UTF-16) dans le dossier du terminal. Lignes clés :
  - "FTMO Global Markets MT5 Terminal x64 build 6032 started for FTMO Global Markets Ltd"
  - "MCP started on 127.0.0.1:22346"
  - "Terminal  exit with code 0" quand il se ferme tout seul
- Sans `/login /password /server`, le terminal quitte ~1-2s après le démarrage malgré `/skipupdate`.
- Spam Wine bénin tant que le terminal tourne : `toolbar:ToolbarWindowProc unknown msg 0465` en boucle — ignorable.
- `mt5.initialize()` (Python Windows dans Wine) pend indéfiniment même après 120s+ d'attente — jamais de retour, ni True ni erreur IPC `(-10005)`. Non résolu à ce jour. Toujours entourer d'un timeout externe.

## Serveur MCP intégré (build FTMO ≥6032)

Strings relevés dans terminal64.exe : "MetaTrader 5 MCP", "mcpServers", "/mcp", "Mcp-Session-Id", "Server: MetaTrader5-MCP", "MCP-Protocol-Version: 2025-06-18", "WWW-Authenticate: Bearer realm=\"MetaTrader5-MCP\"".

Config : `Config/assistant.ini` (UTF-16LE) :
- `[MCP.MetaEditor]` Enable=1, Endpoint=http://127.0.0.1:22345/mcp, ApiKey=<128 hex>
- `[MCP.MetaTrader]` Enable=1, Endpoint=http://127.0.0.1:22346/mcp, ApiKey=<128 hex>

Le port n'écoute que tant qu'un terminal tourne (vérifier `ss -tlnp | grep 2234`).

Réponses observées : tout appel (GET/POST /mcp, /sse, /) retourne `HTTP/1.1 401 Unauthorized` avec headers CORS et `WWW-Authenticate: Bearer realm="MetaTrader5-MCP"`.

### Tentatives d'auth échouées (toutes 401)

- `Authorization: Bearer <api_key brute du .ini>`
- Bearer avec md5(api_key), sha256(api_key), base64(hex_decode(api_key))
- Headers X-API-Key, Api-Key, Authorization sans préfixe Bearer
- Basic auth (clé en user ou en password), Digest auth
- api_key/token/key en query params, cookie, ou JSON body
- POST initialize JSON-RPC avec protocolVersion 2025-06-18

### Hypothèses non testées

- La clé du .ini est peut-être chiffrée/dérivée (type DPAPI) et non utilisable telle quelle
- Le serveur attend peut-être un handshake initialize avec des capabilities précises ou un Mcp-Session-Id préexistant
- Le serveur n'accepte peut-être que son client interne : le dossier `llm-agent/` embarque un agent Goose (block/goose) avec sessions.db sqlite (tables sessions, messages, usage_ledger, provider_inventory_*) et logs dans `llm-agent/state/logs/cli/`

Si l'auth est débloquée, ce MCP est une alternative HTTP propre à l'API Python pour piloter le terminal (les strings mentionnent des outils MCP fichiers avec read_roots/write_roots, lecture des journaux, compilation).
