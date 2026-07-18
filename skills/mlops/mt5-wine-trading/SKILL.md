---
name: mt5-wine-trading
description: Installation, configuration et extraction de données historiques MT5 via Wine pour pipelines ML/RL de trading
version: 1.0.0
author: Eva
---

# MetaTrader 5 sous Wine

Guide complet pour installer MT5 sous Wine, connecter un compte FTMO, et extraire des données historiques multi-timeframes pour l'entraînement d'agents de trading.

## Prérequis

- Linux 64-bit (Debian/Ubuntu testé)
- Wine 64-bit + 32-bit installés
- Xvfb pour display virtuel
- Compte FTMO (ou autre broker MT5)

## Installation

### 1. Installer Wine

```bash
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install -y wine64 wine32:i386 winetricks
```

### 2. Installer MT5

Télécharger l'installeur depuis https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe

**Version broker FTMO (à préférer pour les comptes FTMO)** : https://download.terminal.free/cdn/web/ftmo.global.markets/mt5/ftmo5setup.exe
L'installeur FTMO installe dans `drive_c/Program Files/FTMO Global Markets MT5 Terminal/` (et non `MetaTrader 5/`). Vérifié : build 6032 sous Wine 10.0 / Debian 13.

```bash
export WINEPREFIX=~/.wine_mt5
xvfb-run -a wine ftmo5setup.exe /auto   # ou mt5setup.exe /auto pour la version générique
```

Vérifier l'installation :
```bash
find ~/.wine_mt5 -name "terminal64.exe"
```

### 3. Installer Python Windows dans Wine

Nécessaire pour l'API MetaTrader5 Python :

```bash
# Télécharger Python 3.12 Windows
wget https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe

# Installer dans Wine
export WINEPREFIX=~/.wine_mt5
xvfb-run -a wine python-3.12.2-amd64.exe /quiet InstallAllUsers=0 PrependPath=1

# Installer les packages
WIN_PYTHON="$WINEPREFIX/drive_c/users/$USER/AppData/Local/Programs/Python/Python312/python.exe"
xvfb-run -a wine "$WIN_PYTHON" -m pip install MetaTrader5 pandas pyarrow "numpy<2.0"
```

**⚠️ CRITIQUE** : Installer `numpy<2.0` — NumPy 2.x cause des erreurs `ucrtbase.dll.crealf` sous Wine.

## Lancement de MT5

MT5 nécessite un display. Utiliser Xvfb :

```bash
export WINEPREFIX=~/.wine_mt5
export DISPLAY=:99

# Démarrer Xvfb
Xvfb :99 -screen 0 1024x768x16 &
sleep 2

# Lancer MT5 avec credentials FTMO
wine ~/.wine_mt5/drive_c/Program\ Files/MetaTrader\ 5/terminal64.exe \
  /login:521044924 \
  /password:'!Ge$3k9*?mq' \
  /server:FTMO-Server2 \
  /skipupdate
```

**⚠️ MT5 est TRÈS LENT à démarrer sous Wine** (2-5 minutes). Prévoir des timeouts longs.

## Extraction de données historiques

### Méthode API Python (recommandée)

```python
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Initialiser
mt5.initialize()

# Login FTMO
mt5.login(521044924, password="!Ge$3k9*?mq", server="FTMO-Server2")

# Récupérer données
symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M15
end = datetime.now()
start = end - timedelta(days=365)

rates = mt5.copy_rates_range(symbol, timeframe, start, end)
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

# Sauvegarder
df.to_parquet("xauusd_m15.parquet")
```

### Timeframes disponibles

| Nom | Constante MT5 | Minutes |
|-----|-------------|---------|
| M1 | TIMEFRAME_M1 | 1 |
| M5 | TIMEFRAME_M5 | 5 |
| M15 | TIMEFRAME_M15 | 15 |
| M30 | TIMEFRAME_M30 | 30 |
| H1 | TIMEFRAME_H1 | 60 |
| H4 | TIMEFRAME_H4 | 240 |
| D1 | TIMEFRAME_D1 | 1440 |

## Pièges courants

### 1. Erreur `ucrtbase.dll.crealf`

**Symptôme** : `wine: Call from ... to unimplemented function ucrtbase.dll.crealf`

**Cause** : NumPy 2.x utilise des fonctions C non implémentées dans Wine.

**Solution** : Downgrader NumPy :
```bash
wine python.exe -m pip uninstall -y numpy
wine python.exe -m pip install "numpy<2.0"
```

### 2. IPC Timeout — CAUSE RÉELLE (session 2026-07-18)

**Symptôme** : `mt5.initialize()` retourne `(-10005, 'IPC timeout')`

**Pattern exact observé** (terminal FTMO build 6032 + MetaTrader5 Python 5.0.5735) :
- 1er `mt5.initialize(path)` → `(-10005, 'IPC timeout')` en ~10s
- 2e appel → **hang infini**

Ce n'est PAS un problème de timing. Diagnostic fait :
- Même `WINEPREFIX`, même `wineserver64` pour terminal et Python
- Terminal démarre OK ("FTMO Global Markets MT5 Terminal x64 build 6032 started")
- Le terminal ne montre AUCUNE connexion TCP sortante vers FTMO même avec `/login /password /server`

**Hypothèses** : incompatibilité protocole IPC module 5.0.5735 ↔ build 6032, ou Wine 10.0 named-pipe incomplet.

**À tester** : downgrader module MetaTrader5 Python, activer le trading API via `Config/common.ini` (voir Piège 7), ou utiliser le MCP (voir Piège 5).

**Solution** :
```bash
# Tuer toutes les instances
pkill -9 -f terminal64
pkill -9 Xvfb
sleep 3
# Redémarrer proprement
```

### 2. `mt5.initialize()` pend indéfiniment (hang sans retour)

**Symptôme** : `mt5.initialize()` ne retourne JAMAIS — ni `True`, ni `(-10005, 'IPC timeout')` — même après 120s+. Aucun message, le process Python reste figé. Observé sous Wine 10.0 avec terminal FTMO build 6032.

**Distinction avec l'IPC timeout classique** : ici l'appel ne rend pas la main, donc une boucle de retry Python ne sert à rien — le script est bloqué au premier appel.

**À vérifier** :
- Le terminal se ferme tout seul ~1-2s après démarrage s'il est lancé SANS `/login /password /server` (log : "Terminal  exit with code 0"). Toujours lancer avec credentials.
- Vérifier dans `logs/YYYYMMDD.log` du terminal (fichier UTF-16) que la connexion au serveur broker a abouti.
- Toujours entourer l'appel d'un timeout EXTERNE (subprocess + timeout, pas juste une boucle interne).

**Solution** : non résolu à ce jour. Si l'IPC reste muet malgré terminal connecté : tuer tout (`pkill -9 -f terminal64; pkill -9 Xvfb; sleep 3`), relancer le terminal avec credentials, attendre 2-5 min, tester avec subprocess+timeout. Voir `references/ftmo-terminal-mcp.md` pour une piste alternative (serveur MCP intégré).

### 3. MT5 ne répond pas après démarrage

**Symptôme** : Le terminal semble lancé mais l'API ne répond pas.

**Solution** : MT5 peut prendre 3-5 minutes à être prêt. Augmenter les timeouts et ajouter des retries :

```python
import time

for i in range(60):  # Attendre jusqu'à 60s
    if mt5.initialize():
        break
    time.sleep(1)
else:
    raise TimeoutError("MT5 pas prêt après 60s")
```

### 4. Display non disponible

### 5. Serveur MCP intégré (port 22346) — alternative à l'IPC

**Découverte** : Le terminal FTMO build 6032 embarque un serveur MCP natif (`Server: MetaTrader5-MCP`, protocole `2025-06-18`) :
- MetaTrader (terminal) : `http://127.0.0.1:22346/mcp`
- MetaEditor : `http://127.0.0.1:22345/mcp`
- Outils exposés : `get_workspace_info`, fichiers (read/write/patch), compilation, logs, trading

**Config** : `Config/assistant.ini` (UTF-16LE) contient `ApiKey=...` (168 chars hex), **régénérée à chaque démarrage du terminal** (supprimer le fichier pour forcer la régénération).

**BLOCAGE non résolu** : `401 Unauthorized` sur TOUTES les requêtes malgré :
- `Authorization: Bearer <ApiKey>` (clé fraîche)
- Headers `MCP-Protocol-Version: 2025-06-18`, `Accept: application/json, text/event-stream`
- POST initialize JSON-RPC, GET SSE, OPTIONS
Le client intégré (goose, logs dans `llm-agent/state/logs/cli/`) communique en stdio/ACP, pas en HTTP direct — l'auth HTTP exacte reste à découvrir (possiblement signature HMAC ou token de session, pas la clé brute).

**Piste** : intercepter le trafic du client légitime ou trouver la doc MetaQuotes "MetaTrader5-MCP" pour le schéma d'auth exact.

**Symptôme** : `Application tried to create a window, but no driver could be loaded`

**Solution** : Toujours utiliser Xvfb ou `xvfb-run` :
```bash
xvfb-run -a wine terminal64.exe
```

### 5. Fichiers de config .ini illisibles (caractères entre chaque lettre)

**Symptôme** : `cat terminal.ini` affiche des caractères espacés/illisibles, grep ne trouve rien.

**Cause** : les .ini MT5 sont en UTF-16LE. Lire avec :
```bash
iconv -f UTF-16LE -t UTF-8 fichier.ini
# ou en Python : open(f, 'rb').read().decode('utf-16-le')
```

### 6. Spam `toolbar:ToolbarWindowProc unknown msg 0465` dans les logs Wine

Bénin — émis en boucle tant que le terminal tourne. À ignorer (c'est même un signe que le terminal vit).

### 7. Activer le trading API via `Config/common.ini` (piste pour l'IPC timeout)

**Source** : repo `tanguy-pauwels/trading-sdk` (`brocker_connector/mt5_connector.py`, méthode `_allow_api_trading`).

Le terminal peut refuser l'IPC Python si le trading algorithmique n'est pas activé dans sa config. Forcer via `Config/common.ini` (encodage UTF-16LE, utiliser `iconv` ou `open(f, encoding='utf-16')` en Python) :

```ini
[Experts]
Enabled=1
AllowDllImport=0
Account=1
Profile=1
```

Fichier : `~/.wine_mt5/drive_c/Program Files/FTMO Global Markets MT5 Terminal/Config/common.ini`. Redémarrer le terminal après édition, puis re-tester `mt5.initialize()`. **Non encore testé — à vérifier AVANT de conclure que l'IPC est définitivement mort.**

**Repos évalués (2026-07-18), sans autre workaround Wine** : `tanguy-pauwels/script-mt5-wine` (simples .bat venv Windows, rien sur Linux/IPC) et `tanguy-pauwels/trading-sdk` (framework standard appelant `mt5.initialize(path, login, password, server)` comme nous — seule la technique common.ini ci-dessus est réutilisable). Ne pas ré-évaluer ces repos pour le problème IPC.

### 8. Week-end / marchés fermés ≠ cause d'échec de connexion

Le week-end (vendredi 21h → dimanche 21h GMT), les marchés forex/métaux sont fermés : pas de ticks temps réel. MAIS la connexion TCP au serveur broker doit quand même s'établir, le login doit aboutir, et les données historiques (`copy_rates_range`) restent accessibles. Une absence totale de connexion réseau sortante ou un IPC timeout constatés un week-end ne sont donc PAS expliqués par la fermeture des marchés — chercher la cause ailleurs (Wine, IPC, config terminal). Diagnostic vérifié le samedi 2026-07-18 : zéro ligne login/connect/ping dans les logs terminal alors que le MCP local démarre sur 22346.

## Serveur MCP intégré (builds FTMO récents)

Les terminaux FTMO ≥ build 6032 exposent un serveur MCP HTTP : `http://127.0.0.1:22346/mcp` (terminal) et `:22345/mcp` (MetaEditor), config dans `Config/assistant.ini` (UTF-16). Auth Bearer requise — non débloquée à ce jour, détails et tentatives dans `references/ftmo-terminal-mcp.md`. Alternative potentielle à l'API Python si l'auth est résolue.

## Intégration avec EVO-ARENA

Les données MT5 exportées en Parquet sont directement compatibles avec `evo_core.py` :

```python
import pandas as pd
from evo_core import compute_indicators, df_to_arrays

# Charger données MT5
df = pd.read_parquet("xauusd_m15.parquet")

# Renommer colonnes si nécessaire
df = df.rename(columns={"time": "timestamp", "tick_volume": "volume"})

# Calculer indicateurs
A = compute_indicators(df)
```

## Credentials FTMO par défaut

| Champ | Valeur |
|-------|--------|
| Login | 521044924 |
| Password | !Ge$3k9*?mq |
| Serveur | FTMO-Server2 |

**Note** : Ces credentials sont stockés dans ce skill pour référence. En production, utiliser des variables d'environnement.

## Scripts disponibles

- `scripts/install_mt5.sh` — Installation complète Wine + MT5
- `scripts/mt5_fetch_data.py` — Extraction automatisée multi-symboles/multi-timeframes
- `scripts/mt5_test_connection.py` — Test de connexion rapide

## Références

- `references/mt5-wine-troubleshooting.md` — Guide détaillé des erreurs et solutions
- `references/ftmo-data-pipeline.md` — Pipeline complet données FTMO → EVO-ARENA
- `references/ftmo-terminal-mcp.md` — Terminal FTMO branded : chemins, comportement sous Wine, serveur MCP intégré (22345/22346) et tentatives d'authentification
