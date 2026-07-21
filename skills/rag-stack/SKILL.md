---
name: rag-stack
description: Stack RAG complet avec ChromaDB + HippoRAG 2 pour la base de connaissances EVA
category: data-science
---

# Stack RAG EVA

Stack RAG (Retrieval-Augmented Generation) avec ChromaDB + embeddings sentence-transformers + HippoRAG 2 reranking.

## Structure

```
~/rag-stack/
├── server.py          # API Flask sur :8083
├── indexer.py         # Indexation skills + wiki + monitoring
├── embedder.py        # Embeddings Sentence Transformers + cache
├── query.sh           # CLI pour interroger l'API (pour subagents EVA)
├── start.sh           # Démarrage du serveur
├── install.sh         # Installation des dépendances
├── chroma_db/         # Base vectorielle persistée (~88 Mo)
├── .embed_cache/      # Cache des embeddings (~39 Mo)
├── templates/search.html
├── static/{style.css, script.js}
└── HippoRAG/          # Source cloné OSU-NLP-Group/HippoRAG
```

## API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/rag/stats` | GET | Stats : nb chunks, par source, taille DB |
| `/api/rag/search` | POST | Recherche vectorielle → top N chunks |
| `/api/rag/query` | POST | Question → réponse LLM + contexte avec reranking |
| `/api/rag/reindex` | GET | Réindexation complète asynchrone |

### POST /api/rag/search
```json
{"query": "OPC UA configuration", "top_k": 5, "source": "skill"}
```

### POST /api/rag/query
```json
{"query": "Comment configurer OPC UA ?", "top_k": 5, "use_llm": true}
```

## Stats actuelles

- **9,668 chunks** : 9,464 skills, 86 wiki, 118 cybersec
- **Modèle** : all-MiniLM-L6-v2 (384 dimensions)
- **Base ChromaDB** : ~88 Mo
- **Cache embeddings** : ~39 Mo

## Utilisation

```bash
# Démarrer le serveur
cd ~/rag-stack && bash start.sh

# Interroger (CLI)
./query.sh "Comment faire du SSRF ?"
./query.sh --search "PLC Siemens S7"
./query.sh --stats

# Via curl pour les subagents
curl -X POST http://192.168.1.5:8083/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query":"attaque JWT","top_k":3}'
```

## Points clés

- ChromaDB utilisée via pipx (évite les conflits de dépendances Python 3.13)
- HippoRAG 2 reranking : graphe d'entités + Personalized PageRank sur les chunks
- Le cache d'embeddings évite de ré-encoder les textes inchangés
- La réindexation se fait via `GET /api/rag/reindex` ou `python3 indexer.py --recreate`