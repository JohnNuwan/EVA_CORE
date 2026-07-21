---
name: mcp-servers
description: Guide des MCP (Model Context Protocol) servers pour la cybersécurité et l'OSINT — installation, configuration, et utilisation des serveurs MCP avec Hermes Agent.
---

# MCP Servers — Guide Cybersécurité & OSINT

---

## Qu'est-ce que MCP ?

Model Context Protocol — protocole standardisé pour que des agents IA
interagissent avec des outils externes via un serveur local.

```
Agent IA  ←→  MCP Server  ←→  Outil/API externe
 (Hermes)      (middleware)      (Shodan, VirusTotal...)
```

---

## 1. MCP Servers OSINT

### osint-mcp-server (37 outils, 12 sources)
```bash
# Installation
npx @badchars/osint-mcp-server

# Sources disponibles :
# - Shodan — recherche d'appareils connectés
# - VirusTotal — analyse de hash, URLs, IPs
# - Censys — certificats SSL, exposition
# - SecurityTrails — historique DNS
# - WHOIS — propriété de domaine
# - DNS — résolution, MX, TXT, NS
# - BGP — routage, AS, préfixes
# - Wayback Machine — historique web
# - GeoIP — géolocalisation
```

### Maigret MCP
```bash
# MCP server pour Maigret (recherche de pseudos)
npx @burt/mcp-maigret
```

### Recon-ng MCP
```bash
# Interface MCP pour le framework recon-ng
npx @daedalus/mcp-recon-ng
```

---

## 2. MCP Servers Web Search

```bash
# Brave Search MCP
npx @anthropic/mcp-server-brave-search

# Google Search (via SerpAPI)
npx @anthropic/mcp-server-serpapi

# Exa Search
npx @anthropic/mcp-server-exa
```

---

## 3. MCP Servers Utilitaires

```bash
# Filesystem — opérations fichiers sécurisées
npx @anthropic/mcp-server-filesystem /chemin/autorisé

# GitHub — interaction avec repos, PR, issues
npx @anthropic/mcp-server-github

# Puppeteer — navigation web automatisée
npx @anthropic/mcp-server-puppeteer

# Sequential Thinking — raisonnement étape par étape
npx @anthropic/mcp-server-sequential-thinking

# Memory — base de connaissances persistante
npx @anthropic/mcp-server-memory
```

---

## 4. Installation et configuration

### Via Hermes config
```bash
# Configurer un MCP server
hermes config set mcp.servers.osint.type "stdio"
hermes config set mcp.servers.osint.command "npx"
hermes config set mcp.servers.osint.args "-y @badchars/osint-mcp-server"

# Lister les MCP servers configurés
hermes config get mcp.servers
```

### Fichier de config manuel (~/.hermes/config.yaml)
```yaml
mcp:
  servers:
    osint:
      type: "stdio"
      command: "npx"
      args: ["-y", "@badchars/osint-mcp-server"]
    filesystem:
      type: "stdio"
      command: "npx"
      args: ["-y", "@anthropic/mcp-server-filesystem", "/home/azazel/lab/data"]
```

---

## 5. Utilisation dans Hermes

Une fois configurés, les outils MCP apparaissent dans la liste des outils
disponibles pour l'agent. Exemple d'utilisation :

```
- mcp__osint__shodan_search(query="apache country:FR", limit=5)
- mcp__osint__virustotal_hash(hash="abc123...")
- mcp__osint__whois_lookup(domain="cible.com")
- mcp__filesystem__read_file(path="/data/rapport.md")
```

---

## 6. Créer son propre MCP server

### Structure minimale (Python)
```python
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
import asyncio

server = Server("mon-outil-osint")

@server.list_tools()
async def handle_list_tools():
    return [
        {"name": "mon_outil", "description": "Description", "inputSchema": {...}}
    ]

@server.call_tool()
async def handle_call_tool(name, arguments):
    if name == "mon_outil":
        return {"content": [{"type": "text", "text": "résultat"}]}

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, ...)

asyncio.run(main())
```

---

## Ressources

- **awesome-osint-mcp-servers** : https://github.com/soxoj/awesome-osint-mcp-servers
- **awesome-mcp-security** : https://github.com/Puliczek/awesome-mcp-security
- **osint-mcp-server** : https://github.com/badchars/osint-mcp-server
- **Model Context Protocol** : https://modelcontextprotocol.io
