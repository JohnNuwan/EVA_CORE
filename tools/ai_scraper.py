#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI-Powered Web Scraper - Extraction intelligente de contenu web via LLM.

Inspiré par ScrapeGraphAI. Utilise un LLM pour comprendre et extraire
le contenu pertinent d'une page web sans dépendre d'un navigateur lourd.
Tous les outils sont dans le toolset "web".
"""

import json
import logging
import re
import time
import urllib.parse
from html.parser import HTMLParser
from typing import Optional, Tuple
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

# Cache simple: {key: (timestamp, result)}
_SCRAPE_CACHE: dict = {}
_CACHE_TTL = 60  # Durée de vie du cache en secondes


# ── LLM Client (compatible OpenAI) ─────────────────────────────────────

def _get_llm_config() -> Tuple[str, str]:
    """Récupère la configuration LLM depuis les variables d'environnement.

    Ordre de priorité:
      1. HELIOS_LLM_API_KEY / HELIOS_LLM_BASE_URL
      2. OPENTERAI_API_KEY / OPENAI_BASE_URL
      3. OPENAI_API_KEY / OPENAI_BASE_URL

    Returns:
        Tuple[str, str]: Un couple (api_key, base_url).
    """
    import os
    api_key = (os.environ.get("HELIOS_LLM_API_KEY")
               or os.environ.get("OPENTERAI_API_KEY")
               or os.environ.get("OPENAI_API_KEY")
               or "")
    base_url = (os.environ.get("HELIOS_LLM_BASE_URL")
                or os.environ.get("OPENAI_BASE_URL")
                or "https://api.openai.com/v1")
    return api_key, base_url


def _call_llm(system_prompt: str, user_prompt: str, response_json: bool = False) -> str:
    """Appelle le LLM configuré via une API compatible OpenAI.

    Args:
        system_prompt: Consigne système pour le LLM.
        user_prompt: Consigne utilisateur contenant les données à extraire.
        response_json: Active le format de réponse JSON structuré (JSON Object).

    Returns:
        str: Résultat de l'extraction ou message d'erreur au format JSON.
    """
    api_key, base_url = _get_llm_config()
    if not api_key:
        return json.dumps({"error": "Aucune clé API LLM configurée. Définissez OPENAI_API_KEY ou OPENTERAI_API_KEY."})

    import httpx
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 4096,
        "temperature": 0.1,
    }
    if response_json:
        payload["response_format"] = {"type": "json_object"}

    try:
        resp = httpx.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return json.dumps({
            "content": content,
            "model": data.get("model", "unknown"),
            "tokens": {
                "prompt": usage.get("prompt_tokens", 0),
                "completion": usage.get("completion_tokens", 0),
                "total": usage.get("total_tokens", 0),
            }
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Échec appel LLM: {e}"})


# ── HTML Parser ────────────────────────────────────────────────────────

class _TextExtractor(HTMLParser):
    """HTMLParser personnalisé pour extraire le texte d'un document HTML."""

    def __init__(self):
        """Initialise l'extracteur de texte."""
        super().__init__()
        self._text_parts = []
        self._skip = False
        self._skip_tags = {"script", "style", "noscript", "svg", "path"}

    def handle_starttag(self, tag: str, attrs: list) -> None:
        """Gère l'ouverture d'une balise HTML.

        Args:
            tag: Nom de la balise (ex: 'div').
            attrs: Liste de tuples contenant les attributs (nom, valeur).
        """
        if tag in self._skip_tags:
            self._skip = True
        # Détecter les zones de contenu principal
        for name, val in attrs:
            if name in ("id", "class") and val and any(
                keyword in val.lower()
                for keyword in ("content", "main", "article", "body", "post")
            ):
                if tag not in self._skip_tags:
                    self._text_parts.append(f"\n[{tag}.{name}={val}]\n")

    def handle_endtag(self, tag: str) -> None:
        """Gère la fermeture d'une balise HTML.

        Args:
            tag: Nom de la balise fermée.
        """
        if tag in self._skip_tags:
            self._skip = False

    def handle_data(self, data: str) -> None:
        """Gère l'extraction du contenu texte.

        Args:
            data: Contenu texte de la balise.
        """
        if not self._skip and data.strip():
            self._text_parts.append(data.strip())

    def get_text(self) -> str:
        """Récupère le texte complet extrait.

        Returns:
            str: Texte brut extrait.
        """
        return "\n".join(self._text_parts)


def _extract_text_from_html(html: str) -> str:
    """Extrait le texte lisible d'une page HTML.

    Args:
        html: Contenu HTML brut.

    Returns:
        str: Contenu textuel nettoyé.
    """
    extractor = _TextExtractor()
    try:
        extractor.feed(html)
    except Exception:
        pass
    text = extractor.get_text()
    # Nettoyage des retours à la ligne consécutifs et des espaces
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def _extract_title(html: str) -> str:
    """Extrait le titre d'une page HTML.

    Args:
        html: Contenu HTML de la page.

    Returns:
        str: Le titre extrait de la balise <title>, ou une chaîne vide.
    """
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def _fetch_url(url: str, timeout: int = 30) -> Tuple[str, str, Optional[str]]:
    """Télécharge une URL et retourne son contenu.

    Args:
        url: L'URL cible à télécharger.
        timeout: Limite de temps en secondes.

    Returns:
        Tuple[str, str, Optional[str]]: Triplet (html_de_la_page, content_type, message_erreur).
    """
    import httpx
    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; Helios-Agent/1.0)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        resp.raise_for_status()

        # Limiter la taille à 500 Ko pour éviter les surcharges de mémoire
        max_bytes = 500 * 1024
        content = resp.content[:max_bytes].decode("utf-8", errors="replace")
        ctype = resp.headers.get("content-type", "").split(";")[0].strip()
        return content, ctype, None
    except Exception as e:
        return "", "", str(e)


# ── Fonctions principales ──────────────────────────────────────────────

def _cache_key(url: str, instruction: str = "") -> str:
    """Génère une clé de cache pour le scraping.

    Args:
        url: URL scrapée.
        instruction: Consigne d'extraction.

    Returns:
        str: Clé de cache unique.
    """
    return f"SCRAPE|{url}|{instruction}"


def ai_scrape(url: str, instruction: str = "", timeout: int = 30) -> str:
    """Scrape intelligemment une page web en utilisant un LLM pour l'extraction.

    Args:
        url: URL de la page à scraper.
        instruction: Instructions supplémentaires pour le LLM.
        timeout: Timeout HTTP en secondes.

    Returns:
        str: Rapport d'extraction au format JSON.
    """
    # Vérifier le cache
    cache_key = _cache_key(url, instruction)
    now = time.time()
    if cache_key in _SCRAPE_CACHE:
        ts, result = _SCRAPE_CACHE[cache_key]
        if now - ts < _CACHE_TTL:
            return result

    # Téléchargement
    html, ctype, error = _fetch_url(url, timeout)
    if error:
        result = json.dumps({"error": error, "url": url}, ensure_ascii=False)
        return result

    # Extraire le texte brut
    title = _extract_title(html)
    text = _extract_text_from_html(html)

    # Limiter la taille du texte envoyé au LLM
    max_text = 8000
    if len(text) > max_text:
        text = text[:max_text] + f"\n... [tronqué à partir de {len(text):,} caractères]"

    if not instruction:
        instruction = "Extrais et résume le contenu principal de cette page."

    # Appel du LLM
    system_prompt = (
        "Tu es un extracteur de contenu web. Extrais les informations pertinentes "
        "de la page fournie. Sois concis et structuré. Ne rajoute PAS d'informations "
        "qui ne sont pas dans le texte fourni."
    )
    user_prompt = f"URL: {url}\nTitre: {title}\n\nContenu:\n{text}\n\nInstruction: {instruction}"

    llm_result = _call_llm(system_prompt, user_prompt)
    llm_data = json.loads(llm_result)

    result = json.dumps({
        "url": url,
        "title": title,
        "extracted_content": llm_data.get("content", ""),
        "method": "ai_scrape",
        "tokens": llm_data.get("tokens", {}),
    }, ensure_ascii=False)

    # Mettre en cache
    _SCRAPE_CACHE[cache_key] = (time.time(), result)
    return result


def scrape_sitemap(url: str) -> str:
    """Découvre les URLs d'un site via sitemap.xml et robots.txt.

    Args:
        url: URL de base du site (ex: https://example.com).

    Returns:
        str: Liste JSON des URLs découvertes.
    """
    base = url.rstrip("/")
    all_urls = set()
    sources = {}

    # Tentative de récupération du sitemap.xml
    for sitemap_url in [f"{base}/sitemap.xml", f"{base}/sitemap_index.xml"]:
        html, ctype, error = _fetch_url(sitemap_url, timeout=15)
        if error:
            continue
        # Extraire les balises <loc>
        locs = re.findall(r'<loc[^>]*>(.*?)</loc>', html, re.IGNORECASE)
        if locs:
            for loc in locs:
                all_urls.add(loc.strip())
            sources["sitemap"] = sitemap_url

    # Tentative d'analyse de robots.txt
    robots_html, _, robots_err = _fetch_url(f"{base}/robots.txt", timeout=10)
    if not robots_err:
        # Extraire les directives Sitemap:
        for sm in re.findall(r'^Sitemap:\s*(\S+)', robots_html, re.IGNORECASE | re.MULTILINE):
            all_urls.add(sm.strip())
            sources.setdefault("robots.txt", []).append(sm.strip())

    result = {
        "url": url,
        "sitemap_urls": list(all_urls) if sources.get("sitemap") else [],
        "robots_urls": sources.get("robots.txt", []),
        "source": list(sources.keys()),
        "all_urls": sorted(all_urls) if all_urls else [],
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def extract_structured(url: str, schema_description: str, timeout: int = 30) -> str:
    """Extrait des données structurées (JSON) d'une page web selon un schéma donné.

    Args:
        url: URL de la page cible.
        schema_description: Description textuelle du schéma JSON attendu.
        timeout: Limite de temps HTTP en secondes.

    Returns:
        str: Données structurées extraites au format JSON.
    """
    cache_key = _cache_key(url, f"STRUCTURED|{schema_description}")
    now = time.time()
    if cache_key in _SCRAPE_CACHE:
        ts, result = _SCRAPE_CACHE[cache_key]
        if now - ts < _CACHE_TTL:
            return result

    html, ctype, error = _fetch_url(url, timeout)
    if error:
        result = json.dumps({"error": error, "url": url})
        return result

    title = _extract_title(html)
    text = _extract_text_from_html(html)

    max_text = 8000
    if len(text) > max_text:
        text = text[:max_text] + f"\n... [tronqué à partir de {len(text):,} caractères]"

    system_prompt = (
        "Tu es un extracteur de données structurées. Extrais les données de la page "
        "et retourne-les au format JSON strict selon le schéma décrit par l'utilisateur. "
        "Ne retourne QUE du JSON valide, sans texte additionnel."
    )
    user_prompt = (
        f"URL: {url}\nTitre: {title}\n\nContenu:\n{text}\n\n"
        f"Schéma JSON attendu:\n{schema_description}\n\n"
        "Extrais et retourne les données au format JSON."
    )

    llm_result = _call_llm(system_prompt, user_prompt, response_json=True)
    llm_data = json.loads(llm_result)
    content = llm_data.get("content", "{}")

    # Valider le format JSON du retour LLM
    try:
        json.loads(content)
    except json.JSONDecodeError:
        content = json.dumps({"error": "Le LLM n'a pas retourné de JSON valide", "raw": content})

    result = json.dumps({
        "url": url,
        "title": title,
        "extracted_data": json.loads(content) if isinstance(content, str) else content,
        "method": "extract_structured",
        "tokens": llm_data.get("tokens", {}),
    }, ensure_ascii=False)

    _SCRAPE_CACHE[cache_key] = (time.time(), result)
    return result


# ── Enregistrement dans le registre Helios ──────────────────────────────

from tools.registry import registry


def _check_httpx() -> bool:
    """Vérifie si la bibliothèque httpx est installée.

    Returns:
        bool: True si httpx est importable, False sinon.
    """
    try:
        import httpx
        return True
    except ImportError:
        return False


registry.register(
    name="ai_scrape",
    toolset="web",
    schema={
        "name": "ai_scrape",
        "description": "Scrape intelligemment une page web en utilisant un LLM. "
                       "Extrait le contenu pertinent sans navigateur lourd. "
                       "Moins cher et plus rapide que browser_navigate pour les sites statiques.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL de la page à scraper"},
                "instruction": {
                    "type": "string",
                    "description": "Instruction pour l'extraction (ex: 'extrais les prix et descriptions')"
                },
                "timeout": {"type": "integer", "description": "Timeout HTTP (secondes)", "default": 30}
            },
            "required": ["url"]
        }
    },
    handler=lambda a, **kw: ai_scrape(
        a.get("url", ""), a.get("instruction", ""), a.get("timeout", 30), **kw
    ),
    check_fn=_check_httpx,
    requires_env=[],
    description="Scraping intelligent de pages web via LLM",
    emoji="🕷️",
)

registry.register(
    name="scrape_sitemap",
    toolset="web",
    schema={
        "name": "scrape_sitemap",
        "description": "Découvre les URLs d'un site via sitemap.xml et robots.txt.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL de base du site (ex: https://example.com)"}
            },
            "required": ["url"]
        }
    },
    handler=lambda a, **kw: scrape_sitemap(a.get("url", ""), **kw),
    check_fn=_check_httpx,
    requires_env=[],
    description="Découverte d'URLs via sitemap.xml",
    emoji="🗺️",
)

registry.register(
    name="extract_structured",
    toolset="web",
    schema={
        "name": "extract_structured",
        "description": "Extrait des données structurées (JSON) d'une page web selon un schéma décrit. "
                       "Utile pour récupérer des données tabulaires, des listes de produits, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL de la page"},
                "schema_description": {
                    "type": "string",
                    "description": "Description du schéma JSON attendu (ex: 'liste de produits avec nom, prix, description')"
                },
                "timeout": {"type": "integer", "description": "Timeout HTTP (secondes)", "default": 30}
            },
            "required": ["url", "schema_description"]
        }
    },
    handler=lambda a, **kw: extract_structured(
        a.get("url", ""), a.get("schema_description", ""), a.get("timeout", 30), **kw
    ),
    check_fn=_check_httpx,
    requires_env=[],
    description="Extraction de données structurées (JSON) depuis une page web",
    emoji="📊",
)