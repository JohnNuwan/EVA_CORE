---
name: retrieval-augmented-generation
description: "Concevoir et déployer des pipelines RAG (Retrieval-Augmented Generation) combinant recherche documentaire et LLM pour de l'IA contextuelle en milieu industriel."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [rag, retrieval-augmented-generation, llm, embeddings, vector-database, semantic-search]
    related_skills: [llm-frameworks-exploration, ai-foundations-exploration, rag, arxiv, prompt-engineering]
---

# Génération Augmentée par Recherche (RAG)

## Vue d'ensemble

Le **RAG** (Retrieval-Augmented Generation) est une architecture qui combine un **système de recherche documentaire** (vectoriel ou lexical) avec un **modèle de langage** (LLM) pour produire des réponses contextualisées à partir d'une base de connaissances. Cette approche résout les limitations des LLM (connaissance figée, hallucinations) en ancrant chaque réponse dans des documents réellement récupérés.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De créer un chatbot capable de répondre à partir d'une documentation technique.
- D'implémenter un système de question-réponse sur une base documentaire industrielle.
- De réduire les hallucinations d'un LLM en ancrant ses réponses dans des sources vérifiées.
- De configurer un pipeline d'embedding et d'indexation vectorielle.
- D'intégrer une recherche sémantique sur des manuels, normes ou rapports de maintenance.

---

## 1. Architecture d'un Pipeline RAG

### 1.1 Chaîne Fondamentale

```
Documents source
    ↓
[Découpage (Chunking)] → segments de texte
    ↓
[Embeddings] → vecteurs numériques
    ↓
[Base Vectorielle] (FAISS, Milvus, Qdrant, Weaviate)
    ↑
Requête utilisateur → [Embedding requête] → [Recherche de similarité] → [Documents pertinents]
    ↓
[LLM] + Contexte → Réponse finale
```

### 1.2 Composants Clés

| Composant | Rôle | Options |
|:---|:---|:---|
| **Chunker** | Découper les documents en segments exploitables | RecursiveCharacterTextSplitter, Semantic Chunker |
| **Embeddings** | Convertir le texte en vecteurs | text-embedding-3-small, BGE, E5, Instructor |
| **Base vectorielle** | Stocker et indexer les vecteurs | FAISS, Chroma, Qdrant, Milvus, Elasticsearch |
| **Retriever** | Chercher les documents similaires à la requête | Similarité cosinus, MMR, Fusion (hybrid search) |
| **LLM** | Générer la réponse à partir du contexte | GPT-4, Claude, Mistral, LLaMA |

---

## 2. Mise en Œuvre Pratique

### 2.1 Pipeline RAG Minimal avec LangChain

```bash
uv pip install langchain langchain-community chromadb sentence-transformers
```

```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from langchain.chains import RetrievalQA

# 1. Chargement des documents
loader = TextLoader("manuels/machine_operation.txt")
documents = loader.load()

# 2. Découpage en chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " "]
)
chunks = splitter.split_documents(documents)
print(f"{len(chunks)} chunks créés")

# 3. Embeddings et indexation vectorielle
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(chunks, embeddings)

# 4. Chaîne RAG
llm = Ollama(model="mistral")  # Ou tout autre LLM
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # "stuff", "map_reduce", "refine"
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# 5. Exécution
response = qa_chain.run("Quelle est la procédure de démarrage de la machine ?")
print(response)
```

### 2.2 Pipeline RAG avec Embedding de Requête Optimisé

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGPipeline:
    """Pipeline RAG avec FAISS pour la recherche vectorielle."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.encoder = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []

    def index_documents(self, chunks: list[str]):
        """Indexer une liste de chunks textuels."""
        self.chunks = chunks
        embeddings = self.encoder.encode(chunks, normalize_embeddings=True)
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings.astype(np.float32))

    def retrieve(self, query: str, k: int = 3) -> list[str]:
        """Rechercher les k chunks les plus pertinents."""
        q_embed = self.encoder.encode([query], normalize_embeddings=True)
        scores, indices = self.index.search(q_embed.astype(np.float32), k)
        return [self.chunks[i] for i in indices[0]]

    def generate(self, query: str, llm, k: int = 3) -> str:
        """Recherche + génération combinées."""
        context = "\n\n".join(self.retrieve(query, k))
        prompt = f"""Contexte:\n{context}\n\nQuestion: {query}\n\nRéponse:"""
        return llm.invoke(prompt)
```

---

## 3. Stratégies de Découpage (Chunking)

| Stratégie | Taille | Chevauchement | Usage |
|:---|:---|:---|:---|
| **Fixe** | 256-512 tokens | 10-20% | Documents génériques |
| **Paragraphe** | 1 paragraphe | 0 | Documentation structurée |
| **Sémantique** | Variable | 0 | Contenu hétérogène |
| **Par section** | 1 section | 0 | Manuels techniques, normes ISO |

---

## 4. Pièges Courants

1. **Perte de contexte (Lost in the Middle) :**
   - *Erreur* : Les chunks les plus pertinents sont au milieu du contexte fourni au LLM, qui accorde plus d'importance au début et à la fin.
   - *Correction* : Placez les chunks les plus pertinents en début et fin du prompt ; réordonnez par score de similarité.

2. **Chunks trop grands ou trop petits :**
   - *Erreur* : Chunk de 2000 tokens dilue la pertinence ; chunk de 50 tokens perd la cohérence sémantique.
   - *Correction* : Visez 256-512 tokens avec 10-20% de chevauchement.

3. **Absence de filtrage :**
   - *Erreur* : Retourner des chunks non pertinents qui polluent le contexte du LLM.
   - *Correction* : Utilisez un seuil de score minimum et re-rank with Cross-Encoder.

4. **Index non mis à jour :**
   - *Erreur* : La base vectorielle contient des documents obsolètes.
   - *Correction* : Implémentez un pipeline de mise à jour incrémentale ou régénération périodique.

---

## 5. Métriques d'Évaluation

| Métrique | Cible | Mesure |
|:---|:---|:---|
| **Recall@k** | > 0.85 | Proportion de documents pertinents dans les k premiers |
| **Precision@k** | > 0.70 | Proportion de documents pertinents parmi les k retournés |
| **MRR** (Mean Reciprocal Rank) | > 0.80 | Rang du premier document pertinent |
| **Faithfulness** | > 0.90 | Proportion de la réponse fidèle aux documents sources |

---

## Liste de vérification

- [ ] Les documents sources sont découpés en chunks de taille appropriée (256-512 tokens).
- [ ] Le modèle d'embedding est adapté à la langue des documents (multilingue si nécessaire).
- [ ] La base vectorielle est indexée et les recherches de similarité fonctionnent.
- [ ] Le prompt système du LLM intègre correctement le contexte récupéré.
- [ ] Les métriques (Recall, Precision, MRR, Faithfulness) sont mesurées sur un jeu de test.
- [ ] Un mécanisme de mise à jour des index est en place pour les nouveaux documents.
