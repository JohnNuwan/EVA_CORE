#!/bin/bash
# Paper Trading E.V.A — cron tick
# S'exécute toutes les 15min pour un tick de paper trading
# Sortie : rapport des prix + positions si nouvelles barres détectées

cd /home/aza/jepa_eva || exit 1

OUTPUT=$(PYTHONPATH=. venv/bin/python -c "
from paper_trading import DataLiveBinance
from datetime import datetime

data = DataLiveBinance()
ohlcv_dict = data.rafraichir()
print(f'[Paper Trading E.V.A] {datetime.now().strftime(\"%Y-%m-%d %H:%M\")}')
for s, ohlcv in sorted(ohlcv_dict.items()):
    if len(ohlcv) > 0:
        prix = ohlcv[-1, 3]
        print(f'  {s}: {prix:.2f}')
print('OK')
" 2>&1)

if echo "$OUTPUT" | grep -q "OK"; then
    echo "$OUTPUT"
fi