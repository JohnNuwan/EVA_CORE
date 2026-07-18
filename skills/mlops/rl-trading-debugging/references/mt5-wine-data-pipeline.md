# Pipeline MT5 sous Wine → données historiques pour EVO-ARENA

Recette validée pour installer MetaTrader 5 sous Wine (Debian trixie),
connecter un compte FTMO, et extraire l'historique multi-timeframes
(M1 → D1) pour alimenter les backtests GA.

## Prérequis critique : activer l'architecture i386 AVANT d'installer wine32

Sur Debian 64-bit, `apt install wine32:i386` échoue avec
« Impossible de trouver le paquet wine32:i386 » tant que l'architecture
i386 n'est pas déclarée :

```bash
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install -y wine64 wine32:i386 winetricks
wine --version
```

Sans cette étape, l'installation Wine est incomplète.

## Pitfall : `sudo -S` est bloqué par le terminal Hermes

Le runtime bloque tout pipe de mot de passe vers `sudo -S`
(« BLOCKED: sudo password guessing via stdin »). Ne JAMAIS essayer
`echo "$PASS" | sudo -S ...` — faire exécuter les commandes sudo par
l'utilisateur directement, ou préparer un script shell qu'il lance
avec `sudo bash script.sh`.

## Montage des partitions NTFS Windows

```bash
sudo mkdir -p /mnt/win_c /mnt/win_reco
sudo mount -t ntfs-3g -o ro /dev/sda1 /mnt/win_c     # OS Windows (ro = lecture seule)
sudo mount -t ntfs-3g -o ro /dev/sda2 /mnt/win_reco  # partition recovery
df -h | grep win
```

Note : une partition Windows réduite au minimum (97M utilisés sur 223G
= post-reset) ne montre que `System Volume Information`.

## Installation MT5 (préfixe dédié)

Toujours utiliser un préfixe Wine séparé pour ne pas polluer `~/.wine` :

```bash
export WINEPREFIX=~/.wine_mt5
export WINEARCH=win64
wineboot --init
winetricks -q vcrun2019 corefonts win10
wget "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe"
wine mt5setup.exe   # interactif (le /S silencieux est peu fiable)
```

Binaire installé : `~/.wine_mt5/drive_c/Program Files/MetaTrader 5/terminal64.exe`

Lancement :
```bash
WINEPREFIX=~/.wine_mt5 wine ~/.wine_mt5/drive_c/Program\ Files/MetaTrader\ 5/terminal64.exe
```

Connexion FTMO : login = numéro de compte, mot de passe, serveur
(ex: FTMO-Demo / FTMO-Server selon le challenge).

## Extraction des données : 2 méthodes

### Méthode A — script MQL5 (manuelle, fiable, recommandée pour démarrer)

Injecter un script dans
`~/.wine_mt5/drive_c/users/<user>/AppData/Roaming/MetaQuotes/Terminal/<hash32>/MQL5/Scripts/`
(ou `Common/Files/` en fallback), puis dans MT5 :
F4 (MetaEditor) → F7 (compiler) → F5 (exécuter sur le graphique).

Le script utilise `CopyRates(symbol, PERIOD_M15, start, end, rates)`
et écrit un CSV via `FileOpen(name, FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI)`.
Sortie : `Terminal/Common/Files/*.csv`.

Astuce progrès : exporter par chunks (CopyRates plafonne ~100k barres,
boucler en reculant `current_end`). Écrire un `export_done.flag` pour
détecter la fin depuis Linux.

Barres disponibles FTMO : historique profond (plusieurs années en M15,
moins en M1 selon le serveur). Toujours vérifier le nombre de barres
réellement copiées vs demandées.

### Méthode B — module Python MetaTrader5 (automatisée)

Le pip package `MetaTrader5` est un binding Windows qui parle au
terminal via IPC — il faut un Python **Windows** tournant dans le
MÊME préfixe Wine que le terminal :

```bash
# Dans le préfixe MT5, installer Python Windows puis :
WINEPREFIX=~/.wine_mt5 wine python.exe -m pip install MetaTrader5 pandas pyarrow
```

Script type :
```python
import MetaTrader5 as mt5
mt5.initialize()  # terminal64.exe doit tourner + compte connecté
rates = mt5.copy_rates_range("XAUUSD", mt5.TIMEFRAME_M15, start, end)
```

Codes timeframe de l'API : M1=1, M5=5, M15=15, M30=30,
H1=16385, H4=16388, D1=16408.

Pitfall : le module ne fonctionne PAS avec un Python Linux natif —
le binding exige le processus Windows.

## Conversion vers EVO-ARENA

Le CSV MT5 (time,open,high,low,close,tick_volume,spread,real_volume)
se convertit en parquet aligné sur le format `evo_core.load_data` :
renommer `time→timestamp`, `tick_volume→volume`, trier par timestamp,
sauvegarder en parquet dans `~/ftmo_agent/data/mt5/<SYMBOL>_<TF>.parquet`.

Pour le multi-timeframe : M15 pour le signal principal + H1/D1
précalculés comme features de contexte (tendance supérieure).

## Scripts de la session 2026-07-18 (dans ~/mt5_setup/)

- `install_wine_mt5.sh` — activation i386 + install Wine (à lancer `sudo bash`)
- `install_mt5.py` — création préfixe + winetricks + installeur MT5
- `mt5_pipeline.py` — génère et injecte les scripts MQL5 d'export
- `mt5_python_api.py` — extraction automatisée via module MetaTrader5
