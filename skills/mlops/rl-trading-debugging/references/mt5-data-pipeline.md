# Pipeline MT5 → EVO-ARENA

Guide complet pour connecter MT5 (sous Wine) à EVO-ARENA et récupérer des données historiques multi-timeframes pour l'entraînement.

## Architecture

```
MT5 (Wine) ←→ API Python MetaTrader5 ←→ Script d'extraction
                                              ↓
                                    Parquet files
                                              ↓
                                    EVO-ARENA (evo_core.py)
```

## Prérequis

1. **Wine installé** avec architecture i386 :
   ```bash
   sudo dpkg --add-architecture i386
   sudo apt update
   sudo apt install -y wine64 wine32:i386 winetricks xvfb
   ```

2. **MT5 installé** sous Wine :
   ```bash
   export WINEPREFIX=~/.wine_mt5
   xvfb-run -a wine mt5setup.exe /auto
   ```

3. **Python Windows** dans Wine avec packages :
   ```bash
   WIN_PYTHON="$WINEPREFIX/drive_c/users/$USER/AppData/Local/Programs/Python/Python312/python.exe"
   wine "$WIN_PYTHON" -m pip install MetaTrader5 pandas pyarrow "numpy<2.0"
   ```

## Connexion FTMO

### Credentials par défaut

| Champ | Valeur |
|-------|--------|
| Login | 521044924 |
| Password | !Ge$3k9*?mq |
| Serveur | FTMO-Server2 |

### Lancement MT5 avec auto-login

```bash
export WINEPREFIX=~/.wine_mt5
export DISPLAY=:99

# Démarrer Xvfb
Xvfb :99 -screen 0 1024x768x16 &
sleep 2

# Lancer MT5 avec credentials
wine ~/.wine_mt5/drive_c/Program\ Files/MetaTrader\ 5/terminal64.exe \
  /login:521044924 \
  /password:'!Ge$3k9*?mq' \
  /server:FTMO-Server2 \
  /skipupdate
```

**⚠️ MT5 met 2-5 minutes à démarrer sous Wine.** Prévoir des timeouts longs.

## Extraction de données

### Méthode 1 : API Python (recommandée)

```python
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Initialiser
mt5.initialize()

# Login
mt5.login(521044924, password="!Ge$3k9*?mq", server="FTMO-Server2")

# Récupérer XAUUSD M15 sur 1 an
symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M15
end = datetime.now()
start = end - timedelta(days=365)

rates = mt5.copy_rates_range(symbol, timeframe, start, end)
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

# Sauvegarder pour EVO-ARENA
df.to_parquet("~/ftmo_agent/data/mt5/XAUUSD/XAUUSD_M15.parquet")
```

### Méthode 2 : Script MQL5 (fallback)

Si l'API Python ne fonctionne pas, utiliser un script MQL5 compilé dans MetaEditor :

```mql5
// Export XAUUSD M15 vers CSV
#property script_show_inputs
input string InpFileName = "XAUUSD_M15.csv";

void OnStart()
{
   int file = FileOpen(InpFileName, FILE_WRITE|FILE_CSV|FILE_COMMON);
   FileWrite(file, "time,open,high,low,close,tick_volume");
   
   MqlRates rates[];
   int copied = CopyRates("XAUUSD", PERIOD_M15, 0, 10000, rates);
   
   for(int i = copied-1; i >= 0; i--)
   {
      FileWrite(file,
         TimeToString(rates[i].time),
         rates[i].open, rates[i].high, rates[i].low, rates[i].close,
         rates[i].tick_volume
      );
   }
   FileClose(file);
}
```

Le CSV sera dans `~/.wine_mt5/drive_c/users/.../AppData/Roaming/MetaQuotes/Terminal/Common/Files/`.

## Timeframes supportés

| Nom | Constante MT5 | Minutes | Usage recommandé |
|-----|-------------|---------|------------------|
| M1 | TIMEFRAME_M1 | 1 | Scalping, haute fréquence |
| M5 | TIMEFRAME_M5 | 5 | Intraday court terme |
| M15 | TIMEFRAME_M15 | 15 | **Standard EVO-ARENA** |
| M30 | TIMEFRAME_M30 | 30 | Swing intraday |
| H1 | TIMEFRAME_H1 | 60 | Trend following |
| H4 | TIMEFRAME_H4 | 240 | Position trading |
| D1 | TIMEFRAME_D1 | 1440 | Long terme, contexte macro |

## Intégration EVO-ARENA

### Chargement des données

```python
import pandas as pd
from evo_core import compute_indicators, df_to_arrays

# Charger les données MT5
df = pd.read_parquet("~/ftmo_agent/data/mt5/XAUUSD/XAUUSD_M15.parquet")

# Renommer pour correspondre au format attendu
df = df.rename(columns={
    "time": "timestamp",
    "tick_volume": "volume"
})

# Vérifier les colonnes requises
required = ["timestamp", "open", "high", "low", "close", "volume"]
assert all(col in df.columns for col in required)

# Calculer les indicateurs (une seule fois)
A = compute_indicators(df)

# Convertir en arrays numpy pour le backtest
arrays = df_to_arrays(df)
```

### Multi-timeframes

Pour utiliser plusieurs timeframes (M15 pour signal, H1 pour tendance, D1 pour contexte) :

```python
# Charger plusieurs timeframes
df_m15 = pd.read_parquet("XAUUSD_M15.parquet")
df_h1 = pd.read_parquet("XAUUSD_H1.parquet")
df_d1 = pd.read_parquet("XAUUSD_D1.parquet")

# Synchroniser les timestamps (forward fill)
df_h1_sync = df_h1.set_index("time").reindex(df_m15["time"], method="ffill")
df_d1_sync = df_d1.set_index("time").reindex(df_m15["time"], method="ffill")

# Ajouter comme features supplémentaires
df_m15["h1_close"] = df_h1_sync["close"].values
df_m15["h1_ema_20"] = df_h1_sync["close"].ewm(span=20).mean().values
df_m15["d1_close"] = df_d1_sync["close"].values
```

## Pièges et solutions

### 1. NumPy 2.x incompatible Wine

**Erreur** : `ucrtbase.dll.crealf` non implémenté

**Solution** : Forcer NumPy 1.x :
```bash
wine python.exe -m pip install "numpy<2.0"
```

### 2. IPC Timeout

**Erreur** : `mt5.initialize()` retourne `(-10005, 'IPC timeout')`

**Causes** :
- MT5 pas complètement démarré
- Trop d'instances MT5
- Xvfb crashé

**Solution** :
```bash
# Nettoyer
pkill -9 -f terminal64
pkill -9 Xvfb
sleep 3

# Redémarrer proprement
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x16 &
sleep 2
wine terminal64.exe /skipupdate
```

### 3. MT5 lent à démarrer

**Normal** : 2-5 minutes sous Wine. Utiliser un retry pattern :

```python
import time

for i in range(120):  # 2 minutes max
    if mt5.initialize():
        break
    time.sleep(1)
else:
    raise TimeoutError("MT5 pas prêt après 120s")
```

### 4. Données manquantes

**Symptôme** : `copy_rates_range()` retourne None ou moins de barres que demandé.

**Causes** :
- Historique insuffisant sur le serveur FTMO
- Symbole pas encore affiché dans MT5
- Marché fermé

**Solution** :
```python
# Vérifier la disponibilité
info = mt5.symbol_info(symbol)
if info is None:
    print(f"Symbole {symbol} non trouvé")
    mt5.symbol_select(symbol, True)  # Ajouter au Market Watch

# Vérifier le nombre de barres disponibles
rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
if rates is None:
    print("Pas de données disponibles")
```

## Données historiques alternatives

Si MT5 est trop lent ou instable, utiliser des sources alternatives :

### Dukascopy (gratuit, haute qualité)

```bash
# Télécharger XAUUSD M1 2020-2024
wget https://datafeed.dukascopy.com/datafeed/XAUUSD/2020/00/01h_ticks.bi5
# ... décompresser et convertir
```

### HistData.com (forex gratuit)

```bash
# EURUSD M1 2023
wget https://www.histdata.com/download-free-forex-historical-data/?/metatrader/1-minute-bar-quotes/EURUSD/2023/12
```

### Yahoo Finance (actions/indices)

```python
import yfinance as yf

df = yf.download("GC=F", start="2020-01-01", end="2024-12-31", interval="15m")
```

## Checklist de démarrage

Avant de lancer un entraînement EVO-ARENA avec données MT5 :

- [ ] MT5 tourne sous Wine (`pgrep -f terminal64`)
- [ ] Connexion FTMO établie (`mt5.account_info()` retourne le login)
- [ ] Données téléchargées en Parquet dans `~/ftmo_agent/data/mt5/`
- [ ] Colonnes requises présentes : timestamp, open, high, low, close, volume
- [ ] Indicateurs calculés avec `compute_indicators()`
- [ ] Pas de NaN dans les features
- [ ] Split train/val respecté (pas de look-ahead bias)
