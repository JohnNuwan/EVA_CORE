# Agents de Monitoring Automatisé des Marchés

## Vue d'Ensemble

Pattern pour créer des cron jobs qui surveillent un portefeuille d'actifs financiers, récupèrent les prix, les news, et livrent un rapport formaté.

Deux approches :
1. **yfinance** (public) — tickers publics, pas d'authentification, rapide
2. **trade_republic** (lecture seule) — données réelles du portefeuille Trade Republic (positions, cash, P&L), nécessite token

---

## Approche 1 : yfinance (Public)

### Stack Technique
- **Données marché** : `yfinance` (Python, Yahoo Finance, gratuit)
- **Orchestration** : `cronjob` Hermes avec `no_agent=True`
- **Script** : Python pur, lisible en terminal
- **Livraison** : `deliver` paramètre (local, telegram, email, all)

### Structure d'un Agent de Monitoring

```
~/.hermes/scripts/
├── <mon-portefeuille>-monitor.py     # Script principal
└── <mon-portefeuille>-wrapper.sh     # Wrapper si dépendances .local
```

### Script Python (monitor.py)

Structure type :

```python
#!/usr/bin/env python3
import yfinance as yf
from datetime import datetime

PORTFOLIO = {
    "Nom Actif": {"ticker": "TICKER", "isin": "XX0000000000", "type": "Action/ETF"},
}

ALERTE_SEUIL = 3.0  # % variation journalière pour alerter

def fetch_prices():
    """Récupère les prix via yfinance.Ticker"""
    results = {}
    for name, info in PORTFOLIO.items():
        t = yf.Ticker(info["ticker"])
        hist = t.history(period="1mo")
        # ... calculs prix, variation, alertes
        results[name] = { ... }
    return results

def fetch_news(name, ticker):
    """Récupère news via Yahoo Finance search API"""
    # ...

def generate_report(prices, news):
    """Génère un rapport formaté pour terminal"""
    # ...

if __name__ == "__main__":
    print(generate_report(fetch_prices(), fetch_news_for_all()))
```

### Wrapper Shell (wrapper.sh)

Nécessaire quand `yfinance` est installé dans `~/.local` (PEP 668) :

```bash
#!/usr/bin/env bash
export PYTHONPATH="$HOME/.local/lib/python3.13/site-packages:$PYTHONPATH"
cd "$HOME/.hermes/scripts" && python3 <mon-portefeuille>-monitor.py
```

---

## Approche 2 : trade_republic API (Unofficial, Read-Only)

### Stack Technique
- **Librairie** : `trade_republic` (PyPI, v0.1.1+)
- **Connexion** : WebSocket chiffré vers `wss://api.traderepublic.com`
- **Token** : Session token obtenu par 2FA (SMS), persisté dans `~/.hermes/.tr_token.json`
- **Orchestration** : `cronjob` Hermes avec `no_agent=True`
- **⚠️** : Usage lecture seule uniquement — ne PAS utiliser les méthodes `limit_order` / `market_order` / `stop_market_order`

### Installation

```bash
# Venv dédié (évite PEP 668)
python3 -m venv ~/.trade-republic-venv
~/.trade-republic-venv/bin/pip install trade_republic
```

### Initialisation avec 2FA (une seule fois)

La première connexion nécessite un code envoyé par SMS. Processus :

1. Installer la librairie dans un venv
2. Lancer le script d'init en mode PTY (interactif)
3. Le script envoie `phoneNumber` + `pin` → Trade Republic envoie un SMS
4. L'utilisateur lit le code SMS et le fournit
5. Le token est extrait du Set-Cookie et sauvegardé

```python
#!/usr/bin/env python3
"""
Init Trade Republic — une seule fois, avec 2FA interactive.
Usage: export TR_PHONE="+336..." TR_PIN="2602" && ~/.trade-republic-venv/bin/python3 tr-init.py
"""
import os, sys, json, asyncio

TOKEN_FILE = os.path.expanduser("~/.hermes/.tr_token.json")

async def main():
    phone = os.environ["TR_PHONE"]
    pin = os.environ["TR_PIN"]

    sys.path.insert(0, os.path.expanduser(
        "~/.trade-republic-venv/lib/python3.13/site-packages"))
    from trade_republic.repository.tr_api import TRApi

    print("📞 Connexion...")
    api = TRApi.login(phone, pin)  # Pose la question 2FA via input()

    accounts = await api.get_accounts()
    print(f"✅ Connecté. Comptes : {accounts}")

    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": api._token}, f)
    os.chmod(TOKEN_FILE, 0o600)
    print(f"💾 Token → {TOKEN_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Lecture du Portefeuille (script cron)

```python
#!/usr/bin/env python3
"""trade-republic-portfolio.py — lit le portefeuille réel via token sauvegardé."""
import os, sys, json, asyncio

TOKEN_FILE = os.path.expanduser("~/.hermes/.tr_token.json")

if not os.path.exists(TOKEN_FILE):
    print("❌ Aucun token. Lancer tr-init.py d'abord.")
    sys.exit(1)

with open(TOKEN_FILE) as f:
    TOKEN = json.load(f)["token"]

sys.path.insert(0, os.path.expanduser(
    "~/.trade-republic-venv/lib/python3.13/site-packages"))
from trade_republic.repository.tr_api import TRApi

async def main():
    api = TRApi(TOKEN)

    # Comptes
    accounts = await api.get_accounts()
    sec_acc_no = accounts[0]["id"]  # Premier compte titre

    # Cash disponible
    cash = await api.get_available_cash()
    print(f"💰 Cash: {cash[0]['amount']} {cash[0]['currencyId']}")

    # Portefeuille positions
    portfolio = await api.get_portfolio_by_type(sec_acc_no)
    # ... extraire positions, P&L, etc.

    # Performance
    perf = await api.performance("IE00B4L5Y983", "LSX")
    # ...

    # Transactions récentes
    txns = await api.get_transactions()
    # ...

if __name__ == "__main__":
    asyncio.run(main())
```

### Différence clé : yfinance vs trade_republic API

| Aspect | yfinance | trade_republic API |
|--------|----------|-------------------|
| **Authentification** | Aucune (public) | Token + 2FA |
| **Données** | Prix publics seulement | Portefeuille réel (positions, P&L, buy-in) |
| **Cash disponible** | Non | Oui (montant exact) |
| **Prix d'achat moyen** | Non | Oui |
| **Performance réelle** | Non (prix seul) | Oui (P&L calculé) |
| **Transactions** | Non | Oui (historique) |
| **Risque CGU** | Aucun | Contre CGU (lecture seulement) |
| **Fiabilité** | Yahoo Finance rate limits | API mobile reverse-engineered |

---

## Webhook Discord pour Alertes

### Envoi simple

```python
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/<ID>/<TOKEN>"

def send_discord_alert(message: str):
    """Envoie un message sur le channel Discord via webhook."""
    resp = requests.post(
        WEBHOOK_URL,
        json={"content": message},
        headers={"Content-Type": "application/json"},
    )
    # HTTP 204 = succès
    return resp.status_code == 204
```

### Format structuré (embed)

```python
def send_embed(title: str, fields: list, color: int = 0xFF0000):
    """Envoie un embed Discord (plus joli qu'un message brut)."""
    payload = {
        "embeds": [{
            "title": title,
            "color": color,
            "fields": [{"name": f["name"], "value": f["value"], "inline": f.get("inline", False)}
                      for f in fields],
            "timestamp": datetime.utcnow().isoformat()
        }]
    }
    requests.post(WEBHOOK_URL, json=payload)
```

### Ajout au cron job

```bash
# Créer le cron job avec le webhook
cronjob action=create \
  name="mon-portefeuille" \
  no_agent=true \
  script="mon-wrapper.sh" \
  schedule="0 22 * * 1-5" \
  deliver="local"   # Le webhook est appelé DANS le script, pas via deliver

# OU utiliser deliver="all" si un bot Discord est configuré
cronjob action=create \
  name="mon-portefeuille" \
  no_agent=true \
  script="mon-wrapper.sh" \
  schedule="0 22 * * 1-5" \
  deliver="all"
```

---

## Cron Job Hermes — Paramètres

```bash
# Création
cronjob action=create \
  name="mon-portefeuille" \
  no_agent=true \
  script="mon-wrapper.sh" \
  schedule="0 22 * * 1-5" \
  deliver="local"

# Mise à jour de la livraison
cronjob action=update job_id=<id> deliver="telegram"
```

### Paramètres clés

| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| `no_agent` | `true` | Pas de LLM, exécute le script directement |
| `script` | Chemin relatif sous `~/.hermes/scripts/` | Le script à exécuter |
| `schedule` | Format cron ou `"every 1h"` | Fréquence d'exécution |
| `deliver` | `"local"`, `"telegram"`, `"all"` | Canal de livraison |
| `.sh`/`.bash` | Bash | Extension → exécuté par bash |
| `.py` (ou autre) | Python | Extension → exécuté par Python |

### Schedule types courants

| Usage | Schedule |
|-------|----------|
| Après clôture US | `0 22 * * 1-5` (lun-ven 22h) |
| Après clôture Europe | `0 18 * * 1-5` (lun-ven 18h) |
| Ouverture US | `0 15 * * 1-5` (lun-ven 15h) |
| Hebdomadaire | `0 10 * * 1` (lundi 10h) |
| Toutes les heures | `every 1h` |

---

## Portefeuille Type Trade Republic

```python
PORTFOLIO = {
    "MSCI World ETF":  {"ticker": "IWDA.AS",  "isin": "IE00B4L5Y983", "type": "ETF"},
    "Schneider":       {"ticker": "SU.PA",    "isin": "FR0000121972", "type": "Action"},
    "NVIDIA":          {"ticker": "NVDA",     "isin": "US67066G1040", "type": "Action"},
    "ASML":            {"ticker": "ASML",     "isin": "NL0010273215", "type": "Action"},
    "TSMC":            {"ticker": "TSM",      "isin": "US8740391003", "type": "Action"},
}
```

### Tickers Trade Republic courants

| Actif | Ticker | Bourse |
|-------|--------|--------|
| iShares MSCI World | IWDA.AS | Euronext Amsterdam |
| iShares Core MSCI World | IWDA.AS | Euronext Amsterdam |
| Vanguard FTSE All-World | VWCE.DE | Xetra |
| S&P 500 | SXR8.DE | Xetra |
| NVIDIA | NVDA | NASDAQ |
| Schneider Electric | SU.PA | Euronext Paris |
| ASML | ASML | Euronext Amsterdam |
| TSMC | TSM | NYSE |
| Microsoft | MSFT | NASDAQ |
| Amazon | AMZN | NASDAQ |
| Eli Lilly | LLY | NYSE |
| Berkshire Hathaway | BRK-B | NYSE |
| Rheinmetall | RHM.DE | Xetra |

---

## Pièges et Solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| `ModuleNotFoundError: yfinance` | PEP 668, pip installé dans ~/.local | Wrapper avec PYTHONPATH |
| `HTTP Error 429` | Rate limiting Yahoo | Espacer les appels, utiliser `yf.Ticker` individuel |
| Pas de livraison | `deliver='local'` sur CLI | Vérifier avec `cronjob list` |
| `no delivery target resolved` | Pas de gateway connectée | Configurer Telegram ou utiliser `deliver='local'` |
| Données vides | Ticker non trouvé | Vérifier suffixe bourse (.AS, .DE, .PA, .L) |
| `JSONDecodeError` login TR | API bloquée/changée | Vérifier User-Agent, réessayer |
| Token expiré | Session timeout | Relancer tr-init.py avec 2FA |
| `input()` bloqué dans cron | Code 2FA nécessaire en interactif | Init en PTY, pas en cron |

---

## Évolution Possible

- Ajouter `yfinance` news API pour les news par actif
- Intégrer `polygon` ou `alphavantage` pour données temps réel
- Ajouter indicateurs techniques (RSI, MACD, moyennes mobiles)
- Multi-devise (USD → EUR conversion)
- Rapport PDF/Push Telegram avec graphiques
- Détection de split/dividende
- Agrégation multi-comptes
- Signaux d'achat/vente basés sur RSI, moyennes mobiles, niveaux support/résistance