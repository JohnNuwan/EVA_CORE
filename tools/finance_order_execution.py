#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Outil d'exécution d'ordres de trading et de gestion du compte pour EVA.

Ce module gère le passage d'ordres d'achat/vente, la clôture de positions,
la modification de Stop Loss/Take Profit, et la récupération du solde de compte.
Il prend en charge un mode Simulation (Paper Trading persistant) et l'intégration
REST API vers MetaTrader 5.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Tente d'importer yfinance pour valoriser les positions en temps réel
try:
    import yfinance as yf
except ImportError:
    yf = None

# Fichier local de persistance des positions simulées (Paper Trading)
POSITIONS_FILE = Path.home() / ".hermes" / "finance_positions.json"


def charger_donnees_simulees() -> Dict[str, Any]:
    """Charge les données du compte et des positions simulées.

    Returns:
        Dictionnaire contenant le solde, l'équité et la liste des positions.
    """
    if not POSITIONS_FILE.parent.exists():
        POSITIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
    if not POSITIONS_FILE.exists():
        initial_data = {
            "balance": 100000.0,
            "equity": 100000.0,
            "positions": []
        }
        with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=4)
        return initial_data

    try:
        with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"balance": 100000.0, "equity": 100000.0, "positions": []}


def sauvegarder_donnees_simulees(data: Dict[str, Any]) -> None:
    """Sauvegarde les données simulées dans le fichier JSON.

    Args:
        data: Les données du compte à enregistrer.
    """
    try:
        with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error("Impossible de sauvegarder les positions simulées : %s", e)


def executer_ordre_simule(
    action: str,
    symbol: str,
    lot: float,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    position_id: Optional[int] = None
) -> Dict[str, Any]:
    """Exécute un ordre de trading en mode Simulation (Paper Trading).

    Args:
        action: L'action (buy, sell, close, modify, status).
        symbol: Le symbole financier.
        lot: La taille de lot.
        stop_loss: Le niveau de prix Stop Loss.
        take_profit: Le niveau de prix Take Profit.
        position_id: L'identifiant de la position à modifier ou fermer.

    Returns:
        Résultat structuré de la transaction simulée.
    """
    data = charger_donnees_simulees()

    # Résolution des symboles pour yfinance
    symbol_mappings = {
        "GOLD": "GC=F",
        "SILVER": "SI=F",
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDCAD": "USDCAD=X",
        "USDJPY": "JPY=X"
    }

    if action == "status":
        equity = data["balance"]
        # Met à jour les prix actuels et calcule les P&L en direct (logique calc_dif)
        for pos in data["positions"]:
            sym = pos["symbole"]
            yf_sym = symbol_mappings.get(sym.upper(), sym)
            prix_actuel = pos["prix_ouverture"]
            
            if yf:
                try:
                    ticker = yf.Ticker(yf_sym)
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        prix_actuel = float(hist.iloc[-1]["Close"])
                except Exception:
                    pass
            
            # Formule calc_dif : différence en pourcentage
            diff_pct = 0.0
            if pos["type"] == "BUY":
                diff_pct = ((prix_actuel - pos["prix_ouverture"]) / pos["prix_ouverture"]) * 100
            elif pos["type"] == "SELL":
                diff_pct = ((pos["prix_ouverture"] - prix_actuel) / pos["prix_ouverture"]) * 100
                
            pos["prix_actuel"] = prix_actuel
            pos["gain_pourcentage"] = round(diff_pct, 4)
            # Supposons un multiplicateur standard (1 lot standard = gain/perte proportionnelle)
            gain_reel = round(diff_pct * pos["lot"] * 1000, 2)
            pos["pnl"] = gain_reel
            equity += gain_reel
            
        data["equity"] = round(equity, 2)
        sauvegarder_donnees_simulees(data)
        
        return {
            "status": "succes",
            "mode": "Simulation (Paper Trading)",
            "solde": data["balance"],
            "equite": data["equity"],
            "positions_ouvertes": data["positions"]
        }

    if action == "modify":
        if not position_id:
            return {"status": "erreur", "message": "position_id requis pour modifier les stops."}
        
        position_trouvee = None
        for pos in data["positions"]:
            if pos["id"] == position_id:
                position_trouvee = pos
                break
                
        if not position_trouvee:
            return {"status": "erreur", "message": f"Position avec l'ID {position_id} introuvable."}

        if stop_loss is not None:
            position_trouvee["stop_loss"] = stop_loss
        if take_profit is not None:
            position_trouvee["take_profit"] = take_profit
            
        sauvegarder_donnees_simulees(data)
        return {
            "status": "succes",
            "message": f"Stops de la position {position_id} mis à jour avec succès.",
            "position": position_trouvee
        }

    if action == "close":
        if not position_id:
            return {"status": "erreur", "message": "position_id requis pour fermer une position."}
        
        position_trouvee = None
        nouvelles_positions = []
        for pos in data["positions"]:
            if pos["id"] == position_id:
                position_trouvee = pos
            else:
                nouvelles_positions.append(pos)
                
        if not position_trouvee:
            return {"status": "erreur", "message": f"Position avec l'ID {position_id} introuvable."}

        # Valorise la position finale
        sym = position_trouvee["symbole"]
        yf_sym = symbol_mappings.get(sym.upper(), sym)
        prix_actuel = position_trouvee["prix_ouverture"]
        
        if yf:
            try:
                ticker = yf.Ticker(yf_sym)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    prix_actuel = float(hist.iloc[-1]["Close"])
            except Exception:
                pass
                
        # Calcule le P&L final
        diff_pct = 0.0
        if position_trouvee["type"] == "BUY":
            diff_pct = ((prix_actuel - position_trouvee["prix_ouverture"]) / position_trouvee["prix_ouverture"]) * 100
        elif position_trouvee["type"] == "SELL":
            diff_pct = ((position_trouvee["prix_ouverture"] - prix_actuel) / position_trouvee["prix_ouverture"]) * 100
            
        gain_reel = round(diff_pct * position_trouvee["lot"] * 1000, 2)
        
        # Crédite/débite le solde du compte
        data["balance"] = round(data["balance"] + gain_reel, 2)
        data["positions"] = nouvelles_positions
        # Recalcule de l'equity globale
        data["equity"] = data["balance"]
        sauvegarder_donnees_simulees(data)
        
        return {
            "status": "succes",
            "message": f"Position {position_id} fermée à {prix_actuel}. P&L final: {gain_reel} $.",
            "solde_restant": data["balance"],
            "position_fermee": position_trouvee
        }

    # Actions Achat (buy) et Vente (sell)
    if not symbol or not lot:
        return {"status": "erreur", "message": "symbol et lot requis pour ouvrir un trade."}

    # Simulation d'un prix de départ via yfinance si dispo
    prix_simule = 1.0850
    yf_sym = symbol_mappings.get(symbol.upper(), symbol)
    if yf:
        try:
            ticker = yf.Ticker(yf_sym)
            hist = ticker.history(period="1d")
            if not hist.empty:
                prix_simule = float(hist.iloc[-1]["Close"])
        except Exception:
            pass

    nouvel_id = int(time.time())
    nouvelle_position = {
        "id": nouvel_id,
        "type": action.upper(),
        "symbole": symbol.upper(),
        "lot": lot,
        "prix_ouverture": prix_simule,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "heure_ouverture": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    data["positions"].append(nouvelle_position)
    sauvegarder_donnees_simulees(data)

    return {
        "status": "succes",
        "message": f"Ordre {action.upper()} exécuté en mode Simulation.",
        "mode": "Simulation",
        "position": nouvelle_position
    }


def executer_ordre_trading(
    action: str,
    symbol: str = "",
    lot: float = 0.01,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    position_id: Optional[int] = None
) -> Dict[str, Any]:
    """Point d'entrée principal pour l'exécution d'ordres de trading.

    Routes les appels vers l'API REST de trading si configurée, sinon bascule
    sur le mode simulation locale.

    Args:
        action: L'action (buy, sell, close, modify, status).
        symbol: Le symbole financier.
        lot: La taille de lot.
        stop_loss: Prix Stop Loss.
        take_profit: Prix Take Profit.
        position_id: Identifiant de position.

    Returns:
        Dictionnaire avec les résultats de la transaction ou du statut.
    """
    api_url = os.getenv("MT5_API_URL", "").strip()
    
    if not api_url:
        return executer_ordre_simule(action, symbol, lot, stop_loss, take_profit, position_id)

    try:
        import requests
        if action == "status":
            r = requests.get(f"{api_url}/positions_en_court", timeout=5)
            if r.status_code == 200:
                return {"status": "succes", "mode": "MetaTrader5 (REST)", "donnees": r.json()}
            
        elif action in ["buy", "sell"]:
            route = f"{api_url}/open_position/{symbol}/D1/{action}/EVA_CORE/{lot}"
            r = requests.get(route, timeout=10)
            if r.status_code == 200:
                return {"status": "succes", "mode": "MetaTrader5 (REST)", "resultat": r.json()}

        elif action == "modify":
            # Appel d'adaptation REST pour modifier les stops
            route = f"{api_url}/modify_position/{position_id}/{stop_loss}/{take_profit}"
            r = requests.get(route, timeout=5)
            if r.status_code == 200:
                return {"status": "succes", "mode": "MetaTrader5 (REST)", "resultat": r.json()}

        return {
            "status": "erreur",
            "message": f"Action REST '{action}' non implémentée ou erreur serveur (Code {r.status_code})."
        }
    except Exception as e:
        logger.warning("Connexion REST MT5 échouée, repli sur le mode Simulation. Erreur: %s", e)
        return executer_ordre_simule(action, symbol, lot, stop_loss, take_profit, position_id)


# ---------------------------------------------------------------------------
# Enregistrement dans le Registre de l'Agent
# ---------------------------------------------------------------------------
from tools.registry import registry

FINANCE_ORDRE_SCHEMA = {
    "name": "finance_execution_ordres",
    "description": (
        "Gère l'exécution des ordres de trading (achat, vente, fermeture de position, modification de stops) "
        "sur MetaTrader 5. Utilise le mode Simulation par défaut (Paper Trading local) "
        "ou l'API REST de trading si l'environnement le spécifie."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "L'action : 'buy' (achat), 'sell' (vente), 'close' (fermeture de position), 'modify' (modifier stops) ou 'status' (solde et positions).",
                "enum": ["buy", "sell", "close", "modify", "status"]
            },
            "symbol": {
                "type": "string",
                "description": "Le symbole de l'actif (ex: GOLD, EURUSD, AAPL)."
            },
            "lot": {
                "type": "number",
                "description": "La taille du lot pour le trade (ex: 0.01, 0.1, 1.0).",
                "minimum": 0.001
            },
            "stop_loss": {
                "type": "number",
                "description": "Prix du Stop Loss de protection."
            },
            "take_profit": {
                "type": "number",
                "description": "Prix du Take Profit."
            },
            "position_id": {
                "type": "integer",
                "description": "Identifiant de la position concernée (requis si action='close' ou 'modify')."
            }
        },
        "required": ["action"]
    }
}

registry.register(
    name="finance_execution_ordres",
    toolset="finance",
    schema=FINANCE_ORDRE_SCHEMA,
    handler=lambda args, **kw: executer_ordre_trading(
        action=args.get("action", ""),
        symbol=args.get("symbol", ""),
        lot=args.get("lot", 0.01),
        stop_loss=args.get("stop_loss"),
        take_profit=args.get("take_profit"),
        position_id=args.get("position_id")
    ),
    emoji="💳"
)
