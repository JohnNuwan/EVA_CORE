#!/usr/bin/env python3
"""Module RAG Tool - Interrogation du RAG industriel Actemium sous forme d'outil d'agent."""
import os
import logging
import asyncio
import httpx
from tools.registry import registry

logger = logging.getLogger(__name__)


def _expand_query(query: str) -> list[str]:
    """Génère des reformulations et variations de la requête pour la recherche RAG.

    Args:
        query: Requête d'origine.

    Returns:
        list[str]: Liste des variantes de la requête.
    """
    import re
    variations = [query]
    # Tente de matcher les codes d'alarmes courants du type EPH140, EPH 140, EPH-140, etc.
    match = re.search(r"\b([a-zA-Z]{2,5})[ -_]?(\d{2,4})\b", query)
    if match:
        prefix = match.group(1)
        num = match.group(2)
        variations.append(f"{prefix}{num}")
        variations.append(f"{prefix} {num}")
        variations.append(f"{prefix}-{num}")
        variations.append(f"alarme {prefix} {num}")
        variations.append(f"erreur {prefix} {num}")

    # Nettoyer et dédoubler les requêtes
    cleaned = []
    for var in variations:
        v = var.strip()
        if v and v not in cleaned:
            cleaned.append(v)
    return cleaned


async def _query_rag_server(client: httpx.AsyncClient, endpoint: str, query: str, equipment: str = None, function: str = None) -> dict:
    """Envoie la requête brute au serveur RAG de manière asynchrone.

    Args:
        client: Client HTTP asynchrone.
        endpoint: URL d'API complète.
        query: Requête de recherche.
        equipment: Filtrer sur l'équipement.
        function: Filtrer sur l'étape procédé.

    Returns:
        dict: Réponse brute ou dict d'erreur.
    """
    payload = {"prompt": query, "timeout_sec": 120}
    if equipment:
        payload["equipment"] = equipment
    if function:
        payload["function"] = function

    try:
        response = await client.post(endpoint, json=payload)
        if response.status_code == 200:
            data = response.json()
            max_score = 0.0
            sources = data.get("sources", [])
            for src in sources:
                score = src.get("score") or src.get("similarity") or 0.0
                try:
                    max_score = max(max_score, float(score))
                except (TypeError, ValueError):
                    pass
            data["max_score"] = max_score
            return data
        else:
            return {"error": f"Le serveur RAG a répondu avec le statut {response.status_code} : {response.text}"}
    except Exception as e:
        return {"error": f"Erreur de communication : {e}"}


async def query_industrial_rag(query: str, equipment: str = None, function: str = None) -> str:
    """Interroge le RAG industriel Actemium de manière asynchrone avec recherche parallèle et validation des scores.

    Args:
        query: La question de recherche ou le code d'alarme.
        equipment: Équipement cible (optionnel).
        function: Étape procédé cible (optionnel).

    Returns:
        str: Synthèse du RAG, liste des alarmes, sources et avertissements éventuels.
    """
    rag_url = None
    try:
        from helios_cli.config import get_env_value
        rag_url = get_env_value("RAG_URL")
    except Exception:
        pass
    if not rag_url:
        rag_url = os.environ.get("RAG_URL", "http://localhost:8001")
    rag_url = rag_url.rstrip("/")
    endpoint = f"{rag_url}/agent/query"

    from helios_cli.config import load_config
    try:
        self_corrective = load_config().get("rag", {}).get("self_corrective", True)
    except Exception:
        self_corrective = True

    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Première tentative avec la requête d'origine
        result = await _query_rag_server(client, endpoint, query, equipment, function)

        # Vérification de la confiance (seuil à 0.70)
        max_score = result.get("max_score", 0.0)
        sources = result.get("sources", [])
        is_confident = "error" not in result and (max_score >= 0.70 or (max_score == 0.0 and sources))

        # 2. Pipeline de secours parallèle : Reformulation / Expansion si confiance faible
        if not is_confident and self_corrective and "error" not in result:
            expanded = _expand_query(query)
            tasks = []
            for eq in expanded:
                if eq == query:
                    continue
                tasks.append(_query_rag_server(client, endpoint, eq, equipment, function))
            
            if tasks:
                expanded_results = await asyncio.gather(*tasks)
                for eq_res in expanded_results:
                    if "error" not in eq_res:
                        eq_max_score = eq_res.get("max_score", 0.0)
                        if eq_max_score > max_score:
                            result = eq_res
                            max_score = eq_max_score

    # 3. Formater la réponse finale
    if "error" in result:
        return f"Erreur lors de l'accès au RAG Actemium : {result['error']}"

    answer = result.get("answer", "")
    sources = result.get("sources", [])
    alarms = result.get("alarms", [])

    result_parts = []
    if answer:
        result_parts.append(f"Réponse du RAG : {answer}")
    if alarms:
        result_parts.append("Alarmes identifiées :")
        for alarm in alarms:
            result_parts.append(f"- {alarm}")
    if sources:
        result_parts.append("Sources consultées :")
        for src in sources:
            fname = src.get("filename") or src.get("name") or "Inconnu"
            ftype = src.get("file_type") or "Doc"
            result_parts.append(f"- {fname} ({ftype})")

    final_text = "\n".join(result_parts)

    # 4. Injection d'avertissements Self-RAG si nécessaire
    if self_corrective:
        if max_score > 0.0 and max_score < 0.70:
            final_text += "\n\n⚠️ Attention : Les résultats ci-dessus ont un score de confiance faible (< 0.70). Les informations peuvent être partielles ou incorrectes."
        elif not sources:
            final_text += "\n\n⚠️ Attention : Aucun document pertinent n'a été trouvé dans la base RAG."

    return final_text



# Enregistrement de l'outil dans le registre Helios
registry.register(
    name="query_industrial_rag",
    toolset="industrial",
    schema={
        "name": "query_industrial_rag",
        "description": "Interroge le RAG industriel Actemium pour extraire les manuels, plans ou alarmes SQL.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "La question de recherche ou le code d'alarme."
                },
                "equipment": {
                    "type": "string",
                    "description": "Filtrer sur un équipement spécifique (optionnel)."
                },
                "function": {
                    "type": "string",
                    "description": "Filtrer sur une étape ou fonction procédé (optionnel)."
                }
            },
            "required": ["query"]
        }
    },
    handler=lambda a, **kw: query_industrial_rag(
        a.get("query", ""),
        a.get("equipment"),
        a.get("function")
    ),
    is_async=True,
    description="Interroger le RAG industriel Actemium.",
    emoji="🔍",
)

