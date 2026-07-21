# Scraper Crypto Binance — Détails

## API Binance

Point d'entrée : `https://api.binance.com/api/v3/klines`

Paramètres :
- `symbol` : paire (ex: BTCUSDT)
- `interval` : 15m, 1h, 4h, 1d (mapping : m15→15m, h1→1h, h4→4h, d1→1d)
- `limit` : max 1000 barres par requête
- `endTime` : timestamp ms pour pagination arrière

Format de réponse (kline) :
```
[open_time, open, high, low, close, volume, close_time, quote_vol, trades, ...]
```

## Conversion MT5

Le script convertit chaque kline vers le format MT5 :
```
time,open,high,low,close,tick_volume,spread,real_volume
```

- `time` : timestamp formaté `YYYY-MM-DD HH:MM:SS`
- `tick_volume` : nombre de trades (int)
- `spread` : 1 (valeur fixe, pas disponible via Binance)
- `real_volume` : volume en quote asset (USDT)

## Pagination (50 000 barres)

L'API Binance limite à 1000 barres par requête. Le script pagine en
remontant dans le temps :

```python
toutes = []
end_time = None
while len(toutes) < total_barres:
    params = {"symbol": pair, "interval": interval, "limit": 1000}
    if end_time:
        params["endTime"] = end_time
    batch = requests.get(url, params=params).json()
    toutes = batch + toutes  # prepend
    end_time = batch[0][0] - 1  # avant la première barre
```

50 000 barres M15 couvrent ~520 jours (1.4 ans).

## Paires disponibles

Toutes les paires spot Binance : https://api.binance.com/api/v3/exchangeInfo

## Fallback Bybit

Si Binance échoue, le script tente Bybit :
```
https://api.bybit.com/v5/market/kline?category=spot&symbol=BTCUSDT&interval=15&limit=200
```
- Interval mapping : 15m→15, 1h→60, 4h→240, 1d→D
- Limité à 200 barres (pas de pagination profonde)
- Format différent : retourne `[timestamp, open, high, low, close, volume, turnover]`