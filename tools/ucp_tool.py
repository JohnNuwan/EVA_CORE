"""Outil Universal Commerce Protocol (UCP) pour le commerce par agent."""

import json
from typing import Dict, Any, Optional
from tools.registry import registry

# Simulation de panier d'achat
_shopping_cart = {}

UCP_SCHEMA = {
    "name": "ucp_shopping",
    "description": "Permet d'effectuer des opérations d'achat industriels standardisées via le protocole UCP (recherche, panier, checkout).",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["search", "add_to_cart", "view_cart", "checkout"],
                "description": "L'action e-commerce à effectuer"
            },
            "query": {
                "type": "string",
                "description": "Le mot-clé pour la recherche de produits (ex: 'automate Omron', 'câble ethernet')"
            },
            "product_id": {
                "type": "string",
                "description": "L'identifiant du produit pour l'action add_to_cart"
            },
            "quantity": {
                "type": "integer",
                "default": 1,
                "description": "La quantité à ajouter au panier"
            }
        },
        "required": ["action"]
    }
}

def _handle_ucp_shopping(args: Dict[str, Any], **kwargs) -> str:
    """Gestionnaire de l'outil UCP."""
    action = args.get("action")
    
    if action == "search":
        query = args.get("query", "").lower()
        # Mock catalogue de pièces industrielles
        catalog = [
            {"id": "omron-sysmac-1", "name": "Omron Sysmac NJ501 Controller", "price": 1250.00, "currency": "EUR"},
            {"id": "rockwell-cl-1", "name": "Rockwell ControlLogix 5580", "price": 2800.00, "currency": "EUR"},
            {"id": "eth-cable-10m", "name": "Câble Ethernet Cat6 blindé 10m", "price": 45.50, "currency": "EUR"}
        ]
        results = [p for p in catalog if query in p["name"].lower() or query in p["id"].lower()]
        return json.dumps({"success": True, "products": results}, ensure_ascii=False)
        
    elif action == "add_to_cart":
        prod_id = args.get("product_id")
        qty = args.get("quantity", 1)
        if not prod_id:
            return json.dumps({"success": False, "error": "product_id requis pour ajouter au panier"})
        _shopping_cart[prod_id] = _shopping_cart.get(prod_id, 0) + qty
        return json.dumps({"success": True, "message": f"{qty} unité(s) de {prod_id} ajoutée(s) au panier UCP."})
        
    elif action == "view_cart":
        return json.dumps({"success": True, "cart": _shopping_cart})
        
    elif action == "checkout":
        if not _shopping_cart:
            return json.dumps({"success": False, "error": "Le panier est vide. Impossible de procéder au checkout."})
            
        # Simulation d'approbation et checkout UCP
        # En production, cela s'intègre avec les politiques d'approbation (Model-to-Authorization / M2A)
        # pour s'assurer que le modèle ne dépense pas d'argent réel sans consentement.
        from tools.terminal_tool import prompt_dangerous_approval
        
        cart_summary = ", ".join(f"{k} (x{v})" for k, v in _shopping_cart.items())
        msg = f"Validez-vous l'achat UCP pour les articles suivants : {cart_summary} ?"
        
        # Interrogation interactive ou automatique d'approbation
        approved = prompt_dangerous_approval(
            command="UCP CHECKOUT",
            description=msg
        )
        
        if approved == "deny":
            return json.dumps({"success": False, "error": "Achat refusé par l'utilisateur (M2A Protection)."})
            
        # Vider le panier après validation
        receipt = {
            "success": True,
            "status": "completed",
            "transaction_id": "tx_ucp_123456",
            "purchased_items": _shopping_cart.copy()
        }
        _shopping_cart.clear()
        return json.dumps(receipt)

    return json.dumps({"success": False, "error": "Action inconnue"})

# Enregistrement de l'outil UCP
registry.register(
    name="ucp_shopping",
    toolset="industrial",
    schema=UCP_SCHEMA,
    handler=_handle_ucp_shopping,
    check_fn=lambda: True,
    requires_env=[]
)
