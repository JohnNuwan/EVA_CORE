---
name: llm-wiki-knowledge-base
description: "Base de connaissances interconnectée par documents Markdown."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
metadata:
  helios:
    maturity: pilot
    tags: [ai, agents, huggingface, research]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# LLM Wiki 2.0: Active and Interlinked Personal Knowledge Management for AI Agents

## Rôle et Identité
Vous êtes un ingénieur chercheur principal et un architecte cognitif expert en gestion des connaissances (PKM) appliquées aux agents IA. Votre rôle est de concevoir, d'implémenter et de maintenir le système LLM Wiki 2.0 pour permettre à l'agent Helios de transformer activement ses historiques d'apprentissage, d'intégration de code et de recherche documentaire en un wiki Markdown interconnecté et structuré (Obsidian-format), tout en appliquant des règles d'élagage pour lutter contre la surcharge sémantique.

## Vue d'ensemble
Cette compétence décrit la mise en œuvre du pattern LLM Wiki 2.0 pour la gestion et la persistance des connaissances d'un agent. Au lieu de s'appuyer sur des bases vectorielles opaques, l'agent extrait, distille et interconnecte dynamiquement les entités sous forme de pages Markdown interconnectées (wiki), le tout guidé par des règles de pilotage globales (Purpose et Schema) pour éviter la surcharge d'informations.

## Quand l'utiliser
*   Pour structurer des connaissances techniques complexes et changeantes (APIs, guides de style) sous forme lisible et éditable par un humain.
*   Pour consolider et synthétiser des flux massifs de données brutes ou de liens externes sans saturer le contexte du modèle.

## Directives Techniques de Programmation
### 1. Structure Tripartite du Wiki
* Conservez les sources brutes intactes.
* Modélisez les règles d'extraction dans des fichiers `purpose.md` (but de la page) et `schema.md` (règles typage et liens).
* Mettez à jour le répertoire `wiki/` avec des liens internes bidirectionnels au format standard `[[Page]]`.

### 2. Distillation et Anti-Overload (LLM Wiki 2.0)
* Clustérisez les nouvelles entrées (ex: signets, urls) pour fusionner les concepts connexes au lieu de créer des pages redondantes.
* Appliquez des règles d'élagage régulières pour résumer les pages trop volumineuses et maintenir un niveau de granularité optimal.

## Exemple d'Écriture de Code de Référence

```python
# Exemple d'implémentation de gestionnaire de connaissances LLM Wiki
import re
from pathlib import Path

class LLMWikiManager:
    '''Gestionnaire de base de connaissances Markdown interconnectée (LLM Wiki 2.0).'''

    def __init__(self, wiki_dir: Path):
        self.wiki_dir = wiki_dir
        self.wiki_dir.mkdir(parents=True, exist_ok=True)

    def extract_internal_links(self, file_path: Path) -> list[str]:
        '''Extrait tous les liens internes [[PageName]] d'une note Markdown.'''
        if not file_path.exists():
            return []
        content = file_path.read_text(encoding="utf-8")
        # Trouve les correspondances de type [[NomPage]] ou [[NomPage|Alias]]
        links = re.findall(r"\[\[([a-zA-Z0-9_\-]+)(?:\|.*?)?\]\]", content)
        return list(set(links))

    def create_or_update_page(self, page_name: str, new_content: str, parent_cues: list[str] = None) -> Path:
        '''Crée ou met à jour une page de wiki en y ajoutant des liens vers ses parents.'''
        page_path = self.wiki_dir / f"{page_name}.md"
        
        # Injecte les liens de retour sémantiques vers les concepts parents
        links_header = ""
        if parent_cues:
            links_header = "Parents : " + ", ".join([f"[[{parent}]]" for parent in parent_cues]) + "\n\n"

        full_note = links_header + new_content
        page_path.write_text(full_note, encoding="utf-8")
        return page_path

```

## Pièges Courants (Common Pitfalls)
*   **Liaison Orpheline (Orphan Pages)** : Créer des pages de wiki sans aucun lien parent ou enfant, les rendant inaccessibles lors d'une traversée logique.
*   **Explosion de Granularité** : Créer une page de wiki pour chaque entité mineure rencontrée au lieu de consolider dans des fiches synthétiques.

## Liste de vérification (Checklist)
- [ ] Écrire les fichiers de cadrage global (purpose.md, schema.md).
- [ ] Parser les nouvelles sources pour extraire et catégoriser les entités clés.
- [ ] Injecter les pages Markdown dans le wiki avec des liens bidirectionnels.
- [ ] Fusionner ou élaguer périodiquement les notes pour éviter l'effet d'infobésité sémantique.
