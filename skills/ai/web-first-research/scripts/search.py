#!/usr/bin/env python3
"""
Script d'extraction et de conversion de pages web en Markdown pour l'acquisition de connaissances.
"""

import sys
import re
import urllib.request
from bs4 import BeautifulSoup

def clean_html_to_markdown(html_content: str) -> str:
    """Nettoie le contenu HTML brut et le convertit en Markdown simplifié."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Supprimer les éléments non textuels ou parasites
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        element.decompose()
        
    # Extraire le corps principal du texte
    body = soup.body if soup.body else soup
    
    # Remplacer les balises courantes par du Markdown simplifié
    for h in body.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        level = int(h.name[1])
        h.replace_with(f"\n\n{'#' * level} {h.get_text().strip()}\n")
        
    for p in body.find_all("p"):
        p.replace_with(f"\n{p.get_text().strip()}\n")
        
    for a in body.find_all("a"):
        href = a.get("href", "")
        text = a.get_text().strip()
        if href and text:
            a.replace_with(f" [{text}]({href}) ")
            
    for li in body.find_all("li"):
        li.replace_with(f"\n- {li.get_text().strip()}")
        
    # Nettoyage final des espaces blancs et lignes vides consécutives
    text_content = body.get_text()
    text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
    return text_content.strip()

def fetch_page_as_markdown(url: str) -> str:
    """Télécharge l'URL et retourne le texte converti en Markdown."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return clean_html_to_markdown(html)
    except Exception as e:
        return f"Erreur lors du téléchargement de {url} : {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python search.py <url>")
        sys.exit(1)
        
    url = sys.argv[1]
    markdown = fetch_page_as_markdown(url)
    print(markdown)

if __name__ == "__main__":
    main()
