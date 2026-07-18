#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Outil d'exécution d'ordres de trading et de gestion du compte pour EVA.

Ce module gère le passage d'ordres d'achat/vente, la clôture de positions,
et la récupération du solde de compte. Il prend en charge un mode Simulation
(Paper Trading persistant) et l'intégration REST API vers MetaTrader 5.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

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
        action: L'action (buy, sell, close, status).
        symbol: Le symbole financier.
        lot: La taille de lot.
        stop_loss: Le niveau de prix Stop Loss.
        take_profit: Le niveau de prix Take Profit.
        position_id: L'identifiant de la position à fermer.

    Returns:
        Résultat structuré de la transaction simulée.
    """
    data = charger_donnees_simulees()

    if action == "status":
        # Recalcule de l'equity (l'equity simulée reste égale au balance si pas d'API de flux)
        return {
            "status": "succes",
            "mode": "Simulation (Paper Trading)",
            "solde": data["balance"],
            "equite": data["equity"],
            "positions_ouvertes": data["positions"]
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

        # Simule un gain/perte neutre lors de la fermeture
        data["positions"] = nouvelles_positions
        sauvegarder_donnees_simulees(data)
        
        return {
            "status": "succes",
            "message": f"Position {position_id} fermée avec succès (Simulation).",
            "position_fermee": position_trouvee
        }

    # Actions Achat (buy) et Vente (sell)
    if not symbol or not lot:
        return {"status": "erreur", "message": "symbol et lot requis pour ouvrir un trade."}

    # Simulation d'un prix approximatif de marché si non fourni
    prix_simule = 1.0850 if "USD" in symbol.upper() else (2350.0 if "GOLD" in symbol.upper() else 150.0)
    
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
        action: L'action (buy, sell, close, status).
        symbol: Le symbole financier.
        lot: La taille de lot.
        stop_loss: Prix Stop Loss.
        take_profit: Prix Take Profit.
        position_id: Identifiant de position (fermeture).

    Returns:
        Dictionnaire avec les résultats de la transaction ou du statut.
    """
    # Vérifie si une URL de serveur API REST de trading est présente
    api_url = os.getenv("MT5_API_URL", "").strip()
    
    if not api_url:
        # Par défaut, bascule en mode Paper Trading simulé
        return executer_ordre_simule(action, symbol, lot, stop_loss, take_profit, position_id)

    # Logique d'appel HTTP vers le serveur REST du client
    try:
        import requests
        if action == "status":
            r = requests.get(f"{api_url}/positions_en_court", timeout=5)
            if r.status_code == 200:
                return {"status": "succes", "mode": "MetaTrader5 (REST)", "donnees": r.json()}
            
        elif action in ["buy", "sell"]:
            # Route type : /open_position/{name}/{timeframe}/{Type}/{comment}/{lot}
            route = f"{api_url}/open_position/{symbol}/D1/{action}/{comment}/{lot}"
            r = requests.get(route, timeout=10) # Utilise GET selon le pattern client
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
        "Gère l'exécution des ordres de trading (achat, vente, fermeture de position) "
        "sur MetaTrader 5. Utilise le mode Simulation par défaut (Paper Trading local) "
        "ou l'API REST de trading si l'environnement le spécifie."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "L'action : 'buy' (achat), 'sell' (vente), 'close' (fermeture de position), ou 'status' (solde et positions).",
                "enum": ["buy", "sell", "close", "status"]
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
                "description": "Identifiant de la position à fermer (requis si action='close')."
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
