#!/usr/bin/env python3
"""
Reference: complete portfolio monitoring script with matplotlib chart + Discord embed.
- Real-time prices via yfinance (no broker API needed)
- P&L calculation (requires qty + avg_price)
- RSI-14 + 1-month high/low proximity
- Buy/hold/sell signals based on RSI thresholds
- Dark-theme bar chart (matplotlib)
- Discord embed (rich formatting) + chart image as second POST
Usage: copy this file, edit CONFIGURATION section, run daily via cron.
"""
import yfinance as yf
import json, io, os, sys
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION — EDIT THESE
# ═══════════════════════════════════════════════════════════════

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/..."  # paste yours

PORTFOLIO = {
    # "Display Name": {"ticker": "TICKER", "qty": N, "avg_price": X.XX, "type": "Action/ETF"},
    "My ETF":   {"ticker": "IWDA.AS", "qty": 0, "avg_price": 0, "type": "ETF"},
    "My Stock": {"ticker": "NVDA",    "qty": 0, "avg_price": 0, "type": "Action"},
}

WATCHLIST = {
    "Candidate": {"ticker": "LLY", "type": "Action", "raison": "Reason to watch"},
}

ALERTE_SEUIL = 3.0  # % daily change to trigger alert

# ═══════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def fetch_prices(assets):
    results = {}
    for name, info in assets.items():
        ticker = info["ticker"]
        try:
            t = yf.Ticker(ticker); hist = t.history(period="1mo")
            if hist.empty or len(hist) < 2:
                results[name] = {"ticker": ticker, "error": "Pas assez de donnees"}; continue
            series = hist["Close"].dropna()
            last, prev = float(series.iloc[-1]), float(series.iloc[-2])
            chg = round(((last - prev) / prev) * 100, 2)
            mchg = 0.0
            if len(series) >= 20: mchg = round(((last - float(series.iloc[-20])) / float(series.iloc[-20])) * 100, 2)
            elif len(series) > 2: mchg = round(((last - float(series.iloc[0]))/ float(series.iloc[0])) * 100, 2)
            rsi = _calc_rsi(series)
            h1m, l1m = float(series.max()), float(series.min())
            result = {
                "ticker": ticker, "price": round(last, 2),
                "change_pct": chg, "month_change_pct": mchg,
                "rsi_14": round(rsi, 1) if rsi else None,
                "dist_from_high": round(((last - h1m) / h1m) * 100, 2),
                "dist_from_low": round(((last - l1m) / l1m) * 100, 2),
                "alert": abs(chg) >= ALERTE_SEUIL,
            }
            qty, avg = info.get("qty", 0), info.get("avg_price", 0)
            if qty and avg:
                result.update(investi=round(qty*avg,2), valeur=round(qty*last,2),
                    pnl=round(qty*(last-avg),2), pnl_pct=round(((last-avg)/avg)*100,2))
            results[name] = result
        except Exception as e:
            results[name] = {"ticker": ticker, "error": str(e)}
    return results

def _calc_rsi(series, period=14):
    if len(series) < period+1: return None
    delta = series.diff(); gain = delta.where(delta>0,0.0); loss = (-delta.where(delta<0,0.0))
    ag = gain.rolling(window=period).mean().iloc[-1]; al = loss.rolling(window=period).mean().iloc[-1]
    return 100.0 if al==0 else 100-(100/(1+ag/al))

def generate_chart(portfolio_prices, watchlist_prices):
    """Dark theme bar chart: green=up, red=down, via BytesIO (no temp file)."""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(14,8), gridspec_kw={'height_ratios':[1,1]})
    fig.patch.set_facecolor('#1a1a2e')
    for ax, title, items in [
        (a1, "Portefeuille - Var journaliere (%)", [(n,d) for n,d in portfolio_prices.items() if "error" not in d]),
        (a2, "Watchlist - Var journaliere (%)",    [(n,d) for n,d in watchlist_prices.items() if "error" not in d]),
    ]:
        names=[n[:14] for n,_ in items]; chgs=[d["change_pct"] for _,d in items]
        cols=['#4ade80' if c>=0 else '#ef4444' for c in chgs]
        bars=ax.barh(range(len(names)), chgs, color=cols, height=0.6, edgecolor='white', linewidth=0.5)
        ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=10, color='white')
        ax.axvline(0, color='white', linewidth=0.8, linestyle='-', alpha=0.3)
        ax.set_title(title, fontsize=13, color='white', fontweight='bold', pad=15)
        ax.set_facecolor('#16213e'); ax.tick_params(colors='white', labelsize=9)
        for s in ax.spines.values(): s.set_color('#333')
        for i,(b,c) in enumerate(zip(bars, chgs)):
            lbl=f"{c:+.2f}%"; xp=b.get_width()+(0.3 if c>=0 else -0.3); ha='left' if c>=0 else 'right'
            ax.text(xp, b.get_y()+b.get_height()/2, lbl, ha=ha, va='center', fontsize=9, fontweight='bold',
                    color='#4ade80' if c>=0 else '#ef4444')
    plt.tight_layout(pad=3); buf=io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig); buf.seek(0); return buf

def build_embed(portfolio_prices, watchlist_prices):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    alerts = []; total_pnl = total_investi = total_valeur = 0
    pf = []
    for name, d in portfolio_prices.items():
        if "error" in d: pf.append({"name": f"X {name}", "value": f"Error: {d['error']}", "inline": False}); continue
        chg, mch, rsi = d["change_pct"], d["month_change_pct"], d.get("rsi_14","?")
        val = f"**{d['price']:.2f} EUR**\nJour: {chg:+.2f}% | 1m: {mch:+.2f}%\nRSI: {rsi}"
        if "pnl" in d:
            val += f"\nP&L: {d['pnl']:+.2f} EUR ({d['pnl_pct']:+.2f}%)"
            total_pnl+=d["pnl"]; total_investi+=d["investi"]; total_valeur+=d["valeur"]
        pf.append({"name": f"{name} ({d['ticker']})", "value": val, "inline": True})
        if d.get("alert"): alerts.append(f"ALERTE: {name} ({d['ticker']}) : {chg:+.2f}%")

    clr = 0x4ade80 if total_pnl>=0 else 0xef4444
    embed = {"title": "Rapport Portefeuille", "description": f"Mise a jour: {now}", "color": clr,
             "fields": [{"name": "PORTEFEUILLE", "value": "---", "inline": False}, *pf]}
    if total_investi > 0:
        embed["fields"].append({"name": "RESUME FINANCIER", "value":
            f"P&L: {total_pnl:+.2f} EUR ({(total_pnl/total_investi)*100:+.2f}%)\n"
            f"Valeur: {total_valeur:.2f} EUR | Investi: {total_investi:.2f} EUR", "inline": False})
    wl = "\n".join(f"**{n}** ({d['ticker']}): {d['price']:.2f} EUR ({d['change_pct']:+.2f}%) RSI:{d.get('rsi_14','?')}"
                   for n,d in watchlist_prices.items() if "error" not in d)
    embed["fields"].append({"name": "WATCHLIST", "value": wl[:900] if wl else "Aucune", "inline": False})
    if alerts: embed["fields"].append({"name": "ALERTES", "value": "\n".join(alerts[:5])[:900], "inline": False})
    reco = []
    for name, d in {**portfolio_prices, **watchlist_prices}.items():
        rsi = d.get("rsi_14")
        if rsi is not None and rsi < 35: reco.append(f"ACHAT {name} - RSI {rsi:.0f} (survendu)")
        elif rsi is not None and rsi > 65: reco.append(f"ATTENDRE {name} - RSI {rsi:.0f} (cher)")
    embed["fields"].append({"name": "RECOMMANDATIONS",
        "value": ("\n".join(reco[:5]) if reco else "Aucun signal fort.")[:900], "inline": False})
    embed["footer"] = {"text": "Investissement long-terme"}; embed["timestamp"] = datetime.now().isoformat()
    return embed

def send_discord(embed, chart_buf):
    """Two separate POSTs: embed first, chart image second."""
    import requests as rq
    try:
        r = rq.post(DISCORD_WEBHOOK, json={"embeds": [embed]}, timeout=10)
        if r.status_code != 204: print(f"Discord embed HTTP {r.status_code}", file=sys.stderr); return False
    except Exception as e: print(f"Discord embed error: {e}", file=sys.stderr); return False
    try:
        r2 = rq.post(DISCORD_WEBHOOK, files={"file": ("chart.png", chart_buf, "image/png")}, timeout=15)
        if r2.status_code != 204: print(f"Discord image HTTP {r2.status_code}", file=sys.stderr)
    except Exception as e: print(f"Discord image error: {e}", file=sys.stderr)
    return True

if __name__ == "__main__":
    print("Fetching prices...", file=sys.stderr)
    pf = fetch_prices(PORTFOLIO); wl = fetch_prices(WATCHLIST)
    print("Generating chart...", file=sys.stderr)
    buf = generate_chart(pf, wl)
    print("Building embed...", file=sys.stderr)
    embed = build_embed(pf, wl)
    print("Sending to Discord...", file=sys.stderr)
    ok = send_discord(embed, buf)
    print("Done." if ok else "Failed Discord send.", file=sys.stderr)
