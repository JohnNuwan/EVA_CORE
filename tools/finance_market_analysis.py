#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Outil d'analyse technique de marché pour EVA.

Ce module calcule les indicateurs clés (RSI, SMA, supports/résistances) et
détermine un signal de trading (Achat/Vente/Neutre) basé sur l'algorithme d'Enzo.
Il prend en charge yfinance pour l'extraction de données de marché gratuites et robustes.
"""

import logging
import os
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Tente d'importer yfinance pour la récupération des données
try:
    import yfinance as yf
except ImportError:
    yf = None


def calculer_rsi(series: pd.Series, window: int = 10) -> pd.Series:
    """Calcule l'indice de force relative (RSI) d'une série temporelle.

    Args:
        series: Série de prix de clôture.
        window: Fenêtre de calcul (défaut: 10).

    Returns:
        Série contenant les valeurs du RSI.
    """
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    ema_up = up.ewm(com=window - 1, adjust=False).mean()
    ema_down = down.ewm(com=window - 1, adjust=False).mean()
    
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))


def calculer_supports_resistances(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les supports et résistances majeurs sur une fenêtre de 5 bougies.

    Args:
        df: DataFrame contenant les colonnes 'high', 'low', 'close'.

    Returns:
        DataFrame complété avec les colonnes de supports et résistances lissées.
    """
    df = df.copy()
    df["support"] = np.nan
    df["resistance"] = np.nan

    # Identification des creux locaux (supports)
    df.loc[
        (df["low"].shift(5) > df["low"].shift(4)) &
        (df["low"].shift(4) > df["low"].shift(3)) &
        (df["low"].shift(3) > df["low"].shift(2)) &
        (df["low"].shift(2) > df["low"].shift(1)) &
        (df["low"].shift(1) > df["low"].shift(0)),
        "support"
    ] = df["low"]

    # Identification des sommets locaux (résistances)
    df.loc[
        (df["high"].shift(5) < df["high"].shift(4)) &
        (df["high"].shift(4) < df["high"].shift(3)) &
        (df["high"].shift(3) < df["high"].shift(2)) &
        (df["high"].shift(2) < df["high"].shift(1)) &
        (df["high"].shift(1) < df["high"].shift(0)),
        "resistance"
    ] = df["high"]

    # Lissage des niveaux par propagation vers l'avant (ffill)
    df["smooth_resistance"] = df["resistance"].ffill()
    df["smooth_support"] = df["support"].ffill()
    return df


def executer_analyse_technique(
    symbol: str,
    timeframe: str = "D1",
    num_bars: int = 200
) -> Dict[str, Any]:
    """Récupère les données historiques et exécute l'analyse technique pour un symbole.

    Args:
        symbol: Le symbole boursier (ex: AAPL, GC=F).
        timeframe: Unité de temps (D1, H1, M15). Défaut: D1.
        num_bars: Nombre de bougies historiques. Défaut: 200.

    Returns:
        Dictionnaire contenant les résultats de l'analyse et le signal de trading.
    """
    if not yf:
        return {
            "status": "erreur",
            "message": "La bibliothèque 'yfinance' n'est pas installée dans l'environnement d'EVA."
        }

    # Nettoyage et mappage des unités de temps pour yfinance
    tf_map = {
        "M1": "1m", "M5": "5m", "M15": "15m", "M30": "30m",
        "H1": "1h", "H4": "1h", "D1": "1d", "W1": "1wk", "MN1": "1mo"
    }
    interval = tf_map.get(timeframe, "1d")

    # Mappage de certains symboles communs
    symbol_mappings = {
        "GOLD": "GC=F",
        "SILVER": "SI=F",
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDCAD": "USDCAD=X",
        "USDJPY": "JPY=X"
    }
    yf_symbol = symbol_mappings.get(symbol.upper(), symbol)

    try:
        ticker = yf.Ticker(yf_symbol)
        # Détermination de la période de recherche
        period = "1mo" if interval in ["1m", "5m", "15m"] else "2y"
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return {
                "status": "erreur",
                "message": f"Aucune donnée trouvée pour le symbole {yf_symbol} ({symbol})."
            }

        # Formatage des colonnes en minuscules
        hist.columns = [col.lower() for col in hist.columns]
        df = hist.tail(num_bars).copy()

        # Calcul des indicateurs
        df = calculer_supports_resistances(df)
        df["sma_fast"] = df["close"].rolling(30).mean()
        df["sma_slow"] = df["close"].rolling(60).mean()
        df["rsi"] = calculer_rsi(df["close"], window=10)
        df["rsi_yesterday"] = df["rsi"].shift(1)

        # Génération des signaux basés sur l'algorithme d'Enzo
        df["signal"] = 0
        
        cond_buy = (
            (df["close"].shift(1) < df["smooth_resistance"].shift(1)) &
            (df["smooth_resistance"] * 1.005 < df["close"]) &
            (df["sma_fast"] > df["sma_slow"]) &
            (df["rsi"] < df["rsi_yesterday"])
        )

        cond_sell = (
            (df["close"].shift(1) > df["smooth_support"].shift(1)) &
            (df["smooth_support"] * 0.995 > df["close"]) &
            (df["sma_fast"] < df["sma_slow"]) &
            (df["rsi"] > df["rsi_yesterday"])
        )

        df.loc[cond_buy, "signal"] = 1
        df.loc[cond_sell, "signal"] = -1

        # Récupération des dernières valeurs
        derniere_bougie = df.iloc[-1]
        signal_final = int(derniere_bougie["signal"])
        signal_txt = "ACHAT" if signal_final == 1 else ("VENTE" if signal_final == -1 else "NEUTRE")

        return {
            "status": "succes",
            "symbole": symbol,
            "symbole_reel": yf_symbol,
            "timeframe": timeframe,
            "dernier_prix": float(derniere_bougie["close"]),
            "rsi": float(derniere_bougie["rsi"]) if not pd.isna(derniere_bougie["rsi"]) else None,
            "sma_rapide": float(derniere_bougie["sma_fast"]) if not pd.isna(derniere_bougie["sma_fast"]) else None,
            "sma_lente": float(derniere_bougie["sma_slow"]) if not pd.isna(derniere_bougie["sma_slow"]) else None,
            "support_actuel": float(derniere_bougie["smooth_support"]) if not pd.isna(derniere_bougie["smooth_support"]) else None,
            "resistance_actuelle": float(derniere_bougie["smooth_resistance"]) if not pd.isna(derniere_bougie["smooth_resistance"]) else None,
            "signal": signal_final,
            "interpretation": signal_txt
        }

    except Exception as e:
        logger.error("Erreur lors de l'analyse technique : %s", e)
        return {
            "status": "erreur",
            "message": f"Une exception est survenue lors de l'analyse : {str(e)}"
        }


# ---------------------------------------------------------------------------
# Enregistrement dans le Registre de l'Agent
# ---------------------------------------------------------------------------
from tools.registry import registry

FINANCE_ANALYSE_SCHEMA = {
    "name": "finance_analyse_technique",
    "description": (
        "Calcule les supports, resistances, RSI et SMA pour un symbole de marché donné (ex: GOLD, AAPL) "
        "et renvoie le dernier prix, les indicateurs et le signal de trading associé "
        "(1=Achat, -1=Vente, 0=Neutre)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "Le symbole boursier ou de change à analyser (ex: AAPL, BTC-USD, EURUSD ou GOLD)."
            },
            "timeframe": {
                "type": "string",
                "description": "L'unité de temps pour l'analyse (ex: 'D1' pour journalier, 'H1' pour horaire, 'M15'). Défaut: 'D1'.",
                "default": "D1"
            },
            "num_bars": {
                "type": "integer",
                "description": "Nombre de bougies historiques à analyser. Défaut: 200.",
                "default": 200
            }
        },
        "required": ["symbol"]
    }
}

registry.register(
    name="finance_analyse_technique",
    toolset="finance",
    schema=FINANCE_ANALYSE_SCHEMA,
    handler=lambda args, **kw: executer_analyse_technique(
        symbol=args.get("symbol", ""),
        timeframe=args.get("timeframe", "D1"),
        num_bars=args.get("num_bars", 200)
    ),
    emoji="📊"
)
