#!/usr/bin/env python3
"""
Scraper de données crypto spot — Binance / Bybit
Format de sortie compatible MT5 : time,open,high,low,close,tick_volume,spread,real_volume

Usage :
    PYTHONPATH=. venv/bin/python scrape_crypto.py --pairs BTCUSDT,ETHUSDT,SOLUSDT --timeframe m15

Installation : pip install requests
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

TIMEFRAMES = {"m15": "15m", "m5": "5m", "h1": "1h", "h4": "4h", "d1": "1d"}
DATA_DIR = Path(__file__).parent.parent / "data"


def scraper_binance(pair: str, interval: str, total_barres: int = 50000) -> list[list]:
    """Scrape l'historique Binance par tranches de 1000."""
    toutes = []
    end_time = None
    url = "https://api.binance.com/api/v3/klines"

    while len(toutes) < total_barres:
        params = {"symbol": pair.upper(), "interval": interval, "limit": 1000}
        if end_time:
            params["endTime"] = end_time
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        toutes = batch + toutes
        end_time = batch[0][0] - 1
        print(f"   → {len(toutes)} barres...")
        if len(batch) < 1000:
            break
    return toutes[-total_barres:]


def convertir_en_csv(klines: list[list], pair: str, timeout: str, chemin: Path):
    """Convertit les klines Binance → CSV MT5."""
    with open(chemin, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"])
        for k in klines:
            dt = datetime.fromtimestamp(int(k[0]) / 1000, tz=timezone.utc)
            w.writerow([
                dt.strftime("%Y-%m-%d %H:%M:%S"),
                f"{float(k[1]):.2f}", f"{float(k[2]):.2f}",
                f"{float(k[3]):.2f}", f"{float(k[4]):.2f}",
                int(k[8]), 1, f"{float(k[7]):.2f}",
            ])
    print(f"✅ {pair} {timeout} → {chemin} ({len(klines)} barres)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pairs", default="BTCUSDT,ETHUSDT,SOLUSDT")
    p.add_argument("--timeframe", default="m15", choices=TIMEFRAMES.keys())
    p.add_argument("--barres", type=int, default=50000)
    args = p.parse_args()

    pairs = [s.strip().upper() for s in args.pairs.split(",")]
    interval = TIMEFRAMES[args.timeframe]
    os.makedirs(DATA_DIR, exist_ok=True)

    for pair in pairs:
        chemin = DATA_DIR / f"{pair}_{args.timeframe}.csv"
        if chemin.exists():
            n = len(open(chemin).readlines()) - 1
            print(f"⏭️ {pair} existe déjà ({n} barres)")
            continue
        print(f"📡 {pair} {args.timeframe} ({args.barres} barres)...")
        try:
            klines = scraper_binance(pair, interval, args.barres)
            if klines:
                convertir_en_csv(klines, pair, args.timeframe, chemin)
            else:
                print(f"   ❌ {pair}: aucune donnée")
        except Exception as e:
            print(f"   ❌ {pair}: {e}")


if __name__ == "__main__":
    main()