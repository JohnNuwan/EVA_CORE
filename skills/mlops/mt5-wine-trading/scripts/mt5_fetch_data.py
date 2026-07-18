#!/usr/bin/env python3
"""
mt5_fetch_data.py — Extraction automatisée des données MT5.

Télécharge les données historiques multi-symboles/multi-timeframes
depuis MT5 et les sauvegarde en Parquet pour EVO-ARENA.

Usage:
    python3 mt5_fetch_data.py --symbols XAUUSD EURUSD --timeframes M15 H1 D1 --days 365
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

WINEPREFIX = os.path.expanduser("~/.wine_mt5")
DATA_DIR = os.path.expanduser("~/ftmo_agent/data/mt5")
WIN_PYTHON = os.path.join(
    WINEPREFIX, "drive_c", "users", os.getenv("USER", "aza"),
    "AppData", "Local", "Programs", "Python", "Python312", "python.exe"
)
MT5_EXE = os.path.join(WINEPREFIX, "drive_c", "Program Files", "MetaTrader 5", "terminal64.exe")

FTMO_LOGIN = 521044924
FTMO_PASSWORD = "!Ge$3k9*?mq"
FTMO_SERVER = "FTMO-Server2"

TIMEFRAMES = {
    "M1": 1, "M5": 5, "M15": 15, "M30": 30,
    "H1": 16385, "H4": 16388, "D1": 16408
}


class MT5DataFetcher:
    def __init__(self):
        self.env = os.environ.copy()
        self.env["WINEPREFIX"] = WINEPREFIX
        self.env["DISPLAY"] = ":99"
        self.xvfb_proc = None
        self.mt5_proc = None

    def cleanup(self):
        """Nettoie les processus."""
        subprocess.run(["pkill", "-9", "-f", "terminal64"], capture_output=True)
        subprocess.run(["pkill", "-9", "Xvfb"], capture_output=True)
        time.sleep(2)

    def start(self):
        """Démarre Xvfb et MT5."""
        self.cleanup()

        print("Démarrage Xvfb...")
        self.xvfb_proc = subprocess.Popen(
            ["Xvfb", ":99", "-screen", "0", "1024x768x16"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)

        print("Démarrage MT5...")
        self.mt5_proc = subprocess.Popen(
            ["wine", MT5_EXE, "/skipupdate"],
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"MT5 PID: {self.mt5_proc.pid}")

    def wait_ready(self, timeout=180):
        """Attend que MT5 soit prêt."""
        print(f"Attente MT5 (max {timeout}s)...")

        test_script = '''
import MetaTrader5 as mt5
import sys
try:
    if mt5.initialize():
        info = mt5.terminal_info()
        if info:
            print("READY")
            mt5.shutdown()
            sys.exit(0)
    sys.exit(1)
except:
    sys.exit(1)
'''

        with open("/tmp/mt5_ready.py", "w") as f:
            f.write(test_script)

        start = time.time()
        while time.time() - start < timeout:
            result = subprocess.run(
                ["wine", WIN_PYTHON, "/tmp/mt5_ready.py"],
                env=self.env,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and "READY" in result.stdout:
                print(f"MT5 prêt après {int(time.time() - start)}s")
                return True

            elapsed = int(time.time() - start)
            if elapsed % 30 == 0:
                print(f"  ... {elapsed}s écoulés")
            time.sleep(5)

        print("Timeout: MT5 pas prêt")
        return False

    def fetch_all(self, symbols, timeframes, days):
        """Télécharge toutes les données."""
        tf_list = [(name, code) for name, code in TIMEFRAMES.items() if name in timeframes]

        script = f'''
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import time

# Attendre MT5
for i in range(60):
    if mt5.initialize():
        break
    time.sleep(1)
else:
    print("ERREUR: MT5 pas prêt")
    sys.exit(1)

# Login
if not mt5.login({FTMO_LOGIN}, password="{FTMO_PASSWORD}", server="{FTMO_SERVER}"):
    print("ERREUR login:", mt5.last_error())
    mt5.shutdown()
    sys.exit(1)

print(f"Connecté: {{mt5.account_info().login}}")

end = datetime.now()
start = end - timedelta(days={days})

symbols = {symbols}
timeframes = {dict(tf_list)}

for symbol in symbols:
    for tf_name, tf_code in timeframes.items():
        print(f"Téléchargement {{symbol}} {{tf_name}}...")

        rates = mt5.copy_rates_range(symbol, tf_code, start, end)
        if rates is None or len(rates) == 0:
            print(f"  Pas de données")
            continue

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")

        output_dir = rf"C:\\\\users\\\\aza\\\\ftmo_agent\\\\data\\\\mt5\\\\{{symbol}}"
        os.makedirs(output_dir, exist_ok=True)
        output = rf"{{output_dir}}\\\\{{symbol}}_{{tf_name}}.parquet"

        df.to_parquet(output, index=False)
        print(f"  OK: {{len(df)}} barres")

mt5.shutdown()
print("TERMINÉ")
'''

        script_path = "/tmp/mt5_fetch_all.py"
        with open(script_path, "w") as f:
            f.write(script)

        print("Exécution du téléchargement...")
        result = subprocess.run(
            ["wine", WIN_PYTHON, script_path],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=600
        )

        print(result.stdout)
        if result.stderr:
            print("ERREURS:", result.stderr[:1000])

        return "TERMINÉ" in result.stdout

    def stop(self):
        """Arrête tout proprement."""
        print("Arrêt...")
        if self.mt5_proc:
            self.mt5_proc.terminate()
        if self.xvfb_proc:
            self.xvfb_proc.terminate()
        self.cleanup()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", nargs="+", default=["XAUUSD", "EURUSD"])
    parser.add_argument("--timeframes", nargs="+", default=["M15", "H1", "D1"])
    parser.add_argument("--days", type=int, default=365)
    args = parser.parse_args()

    fetcher = MT5DataFetcher()

    try:
        fetcher.start()

        if not fetcher.wait_ready():
            print("ERREUR: MT5 n'a pas démarré correctement")
            return 1

        success = fetcher.fetch_all(args.symbols, args.timeframes, args.days)

        # Vérifier les résultats
        print("\n=== Fichiers créés ===")
        subprocess.run(["find", DATA_DIR, "-name", "*.parquet", "-exec", "ls", "-lh", "{}", ";"])

        return 0 if success else 1

    finally:
        fetcher.stop()


if __name__ == "__main__":
    sys.exit(main())
