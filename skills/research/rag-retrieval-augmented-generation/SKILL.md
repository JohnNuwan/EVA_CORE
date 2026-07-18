---
name: rag-retrieval-augmented-generation
description: "Explorer les systèmes avancés de génération augmentée par récupération (RAG) — architectures, stratégies de chunking, indexation hybride, récupération multi-hop et alternatives comme HippoRAG2."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
tags: [RAG, retrieval, embedding, vector-database, hippoRAG, multi-hop, hybrid-search]
keywords: [Retrieval Augmented Generation, RAG, embedding, chunking, hybrid search, dense retriever, sparse retriever]
---

# Systèmes de Génération Augmentée par Récupération (RAG)

## Vue d'ensemble

La génération augmentée par récupération (Retrieval-Augmented Generation — RAG) est une architecture qui combine un **système de recherche** (retriever) avec un **modèle de génération de texte** (generator). Au lieu de solliciter directement la mémoire paramétrique d'un LLM, RAG récupère d'abord des passages pertinents dans une base de connaissances externe, puis les fournit comme contexte au générateur.

Cette approche résout trois limitations majeures des LLM :

1. **Connaissances obsolètes** : le LLM est figé à sa date d'entraînement ; RAG consulte des bases actualisables.
2. **Hallucinations** : le contexte factuel réduit la propension à inventer des informations.
3. **Domaine spécifique** : RAG intègre des documents internes sans fine-tuning.

### Architecture canonique

```
┌──────────┐    requête    ┌──────────────┐    passages    ┌──────────┐
│  Index   │ ◄─────────── │   Retriever   │ ──────────────►│ Generator │
│  (VDB)   │    top-k      │  (BM25 + DPR) │                │  (LLM)   │
└────┬─────┘               └──────────────┘                └────┬─────┘
     │                                                          │
     └────────────── Documents découpés ────────────────────────┘
                        (chunking)
```

---

## Quand utiliser cette compétence

| Scénario | Pertinence |
|---|---|
| Répondre à des questions nécessitant des connaissances actualisées ou privées | Élevée |
| Réduire les hallucinations d'un LLM sur un domaine spécialisé | Élevée |
| Construire un assistant documentaire (juridique, médical, technique) | Élevée |
| Pipeline multi-hop nécessitant plusieurs allers-retours retriever-generator | Élevée |
| Simple question-réponse sans besoin de contexte externe | Faible (préférer un LLM direct) |

---

## 1. Indexation et chunking

### 1.1 Stratégies de découpage (chunking)

La qualité du découpage des documents est le facteur le plus important pour la performance RAG :

| Stratégie | Taille typique | Avantage | Inconvénient |
|---|---|---|---|
| **Fixe** (N tokens) | 256–512 tokens | Simple, reproductible | Coupe en milieu de phrase |
| **Sémantique** | Variable | Respecte les frontières naturelles | Plus coûteux |
| **Hiérarchique** | Sections + paragraphes | Représentation multi-échelle | Indexation complexe |

```python
from typing import Iterator

class ChunkSémantique:
    """Découpe un texte en chunks respectant les frontières sémantiques."""

    def __init__(self, taille_max: int = 512, chevauchement: int = 32):
        self.taille_max = taille_max
        self.chevauchement = chevauchement

    def decouper(self, texte: str) -> list[dict]:
        """Découpe un texte en chunks sémantiques avec chevauchement.

        Args:
            texte: Document complet à découper.

        Returns:
            Liste de chunks avec contenu, position de début et fin.
        """
        chunks = []
        debut = 0

        while debut < len(texte):
            fin = min(debut + self.taille_max, len(texte))

            # Ajuster fin à la frontière de phrase si possible
            if fin < len(texte):
                # Chercher le dernier point, point d'exclamation ou d'interrogation
                for delim in [". ", "!\n", "?\n", ".\n"]:
                    idx = texte.rfind(delim, debut, fin)
                    if idx > debut:
                        fin = idx + len(delim)
                        break

            chunks.append({
                "texte": texte[debut:fin],
                "debut": debut,
                "fin": fin,
            })

            # Avancer avec chevauchement
            debut = fin - self.chevauchement

        return chunks
```

### 1.2 Indexation hybride (dense + sparse)

La recherche hybride combine les forces de BM25 (recherche lexicale exacte) et des embeddings denses (similarité sémantique) :

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

class IndexHybride:
    """Index de recherche hybride : BM25 + embeddings denses."""

    def __init__(self, modele_embedding: str = "all-MiniLM-L6-v2",
                 poids_dense: float = 0.7):
        """Initialise l'index hybride.

        Args:
            modele_embedding: Nom du modèle Sentence-Transformers.
            poids_dense: Pondération du score dense vs. sparse (0 = BM25 pur, 1 = dense pur).
        """
        self.poids_dense = poids_dense
        self.embedder = SentenceTransformer(modele_embedding)
        self.tfidf = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), max_features=50000)
        self.chunks: list[str] = []
        self.embeddings: np.ndarray | None = None
        self.matrice_tfidf = None
        self.indexe = False

    def indexer(self, chunks: list[str]) -> None:
        """Indexe une liste de chunks pour la recherche hybride.

        Args:
            chunks: Liste de textes à indexer.
        """
        self.chunks = chunks

        # Embeddings denses
        self.embeddings = self.embedder.encode(chunks, show_progress_bar=False)

        # Index sparse (TF-IDF)
        self.matrice_tfidf = self.tfidf.fit_transform(chunks)

        self.indexe = True

    def rechercher(self, requete: str, k: int = 5) -> list[dict]:
        """Recherche hybride : fusionne scores BM25 + cosinus.

        Args:
            requete: Texte de la requête.
            k: Nombre de résultats à retourner.

        Returns:
            Liste des chunks avec scores hybrides.

        Raises:
            RuntimeError: Si l'index n'a pas été construit.
        """
        if not self.indexe:
            raise RuntimeError("L'index doit être construit avant la recherche.")

        # Score dense (similarité cosinus)
        embedding_requete = self.embedder.encode([requete])
        scores_denses = np.dot(self.embeddings, embedding_requete.T).flatten()

        # Score sparse (BM25 normalisé)
        vecteur_requete = self.tfidf.transform([requete])
        scores_sparses = (self.matrice_tfidf @ vecteur_requete.T).toarray().flatten()

        # Fusion hybride
        scores_denses = (scores_denses - scores_denses.min()) / \
                        (scores_denses.max() - scores_denses.min() + 1e-10)
        scores_sparses = (scores_sparses - scores_sparses.min()) / \
                         (scores_sparses.max() - scores_sparses.min() + 1e-10)

        scores_fusion = (self.poids_dense * scores_denses +
                         (1 - self.poids_dense) * scores_sparses)

        # Top-k
        indices_top_k = np.argsort(scores_fusion)[::-1][:k]

        return [
            {"texte": self.chunks[i], "score": float(scores_fusion[i]),
             "score_dense": float(scores_denses[i]),
             "score_sparse": float(scores_sparses[i])}
            for i in indices_top_k
        ]
```

---

## 2. Récupération multi-hop

### 2.1 Principe

Pour les questions complexes nécessitant plusieurs étapes de raisonnement, la récupération multi-hop décompose la requête en sous-questions et effectue plusieurs allers-retours :

```
Requête : "Quel est le PIB du pays où est né l'inventeur de l'ampoule ?"
    ↓
Hop 1 : "Qui a inventé l'ampoule ?" → "Thomas Edison"
    ↓
Hop 2 : "Où est né Thomas Edison ?" → "Milan, Ohio, États-Unis"
    ↓
Hop 3 : "Quel est le PIB des États-Unis ?" → réponse finale
```

### 2.2 Implémentation

```python
class RAGMultiHop:
    """Pipeline RAG multi-hop avec décomposition automatique de requêtes."""

    def __init__(self, index: IndexHybride, generateur=None):
        self.index = index
        self.generateur = generateur
        self.historique_hops: list[dict] = []

    def decomposer_requete(self, requete: str) -> list[str]:
        """Décompose une requête complexe en sous-questions.

        Args:
            requete: Requête originale.

        Returns:
            Liste des sous-questions à traiter séquentiellement.
        """
        # Dans un scénario réel, cette étape utilise un LLM pour décomposer
        # la requête en sous-questions. Exemple simplifié :
        if "où est né" in requete and "PIB" in requete:
            return [
                "Qui est la personne mentionnée dans la requête ?",
                "Où est née cette personne ?",
                f"Quel est le PIB de la localisation trouvée ?",
            ]
        return [requete]

    def executer(self, requete: str, k_par_hop: int = 3) -> tuple[str, list[dict]]:
        """Exécute une recherche multi-hop complète.

        Args:
            requete: Requête utilisateur complexe.
            k_par_hop: Nombre de passages récupérés par hop.

        Returns:
            Tuple (réponse finale, historique complet des hops).
        """
        sous_questions = self.decomposer_requete(requete)
        contexte_accumule = []

        for i, sq in enumerate(sous_questions):
            resultats = self.index.rechercher(sq, k=k_par_hop)
            contexte = "\n".join(r["texte"] for r in resultats)

            self.historique_hops.append({
                "hop": i + 1,
                "sous_question": sq,
                "contexte_extrait": contexte[:200],
                "resultats": resultats,
            })
            contexte_accumule.append(contexte)

        if self.generateur:
            contexte_final = "\n".join(contexte_accumule)
            prompt = f"Contexte :\n{contexte_final}\n\nQuestion : {requete}"
            reponse = self.generateur(prompt)
        else:
            reponse = contexte_accumule[-1][:500]

        return reponse, self.historique_hops
```

---

## 3. Alternatives et avancées

### 3.1 HippoRAG2

HippoRAG2 améliore le RAG classique par deux mécanismes :

1. **Récupération itérative** : au lieu d'un seul passage retriever→generator, HippoRAG2 alterne entre récupération et génération, utilisant le texte généré pour affiner la requête de récupération suivante.
2. **Mémoire à long terme** : les interactions passées sont stockées dans un graphe de connaissances qui guide la récupération future.

```python
from advanced_rag import initialize_search, multi_hop_run

def pipeline_hipporag(requete: str, chemin_config: str) -> str:
    """Exécute un pipeline HippoRAG2.

    Args:
        requete: Question utilisateur.
        chemin_config: Chemin vers le fichier de configuration HippoRAG2.

    Returns:
        Réponse générée après récupération itérative.
    """
    config = load_pipeline(chemin_config)

    # HippoRAG2 effectue automatiquement la décomposition en sous-questions
    # et alterne récupération / génération
    reponse = multi_hop_run(config, requete)

    return reponse
```

### 3.2 CORAG (Monte Carlo Tree Search + RAG)

CORAG utilise la recherche arborescente Monte Carlo (MCTS) pour explorer plusieurs chemins de récupération :

| Composant | Rôle |
|---|---|
| **Neud** | État de la récupération (texte partiel) |
| **Branche** | Passage de document récupéré |
| **Simulation** | Évaluation de la qualité de la réponse partielle |
| **Rétropropagation** | Mise à jour des scores des passages |

### 3.3 Self-RAG

Self-RAG introduit un mécanisme de **réflexion** où le LLM génère des tokens spéciaux indiquant la pertinence du contexte récupéré :

```python
class SelfRAG:
    """Self-RAG : le LLM évalue lui-même la pertinence des passages récupérés."""

    def __init__(self, modele_llm, seuil_pertinence: float = 0.7):
        self.modele = modele_llm
        self.seuil_pertinence = seuil_pertinence

    def generer_avec_reflexion(self, requete: str, passages: list[str]) -> str:
        """Génère une réponse en évaluant chaque passage.

        Args:
            requete: Question utilisateur.
            passages: Passages récupérés.

        Returns:
            Réponse générée, en ignorant les passages non pertinents.
        """
        for passage in passages:
            # Évaluation de la pertinence par le LLM lui-même
            prompt_eval = f"Ce passage est-il pertinent pour répondre à '{requete}' ?\nPassage : {passage}"
            score = self.modele.evaluer_pertinence(prompt_eval)
            if score < self.seuil_pertinence:
                continue  # Ignorer ce passage

        # Génération finale avec les passages pertinents
        return self.modele.generer(requete, passages)
```

---

## 4. Évaluation (Benchmarking)

### 4.1 Métriques standard

| Métrique | Mesure | Interprétation |
|---|---|---|
| **Hit Rate@k** | Proportion de questions où la réponse est dans les k premiers passages | Récupération |
| **MRR** (Mean Reciprocal Rank) | Rang moyen inversé du premier passage pertinent | Récupération |
| **F1** | Chevauchement lexical entre réponse et référence | Génération |
| **Faithfulness** | Proportion de la réponse qui est fidèle au contexte | Génération |
| **Answer Relevancy** | Pertinence de la réponse par rapport à la question | Génération |

### 4.2 Benchmarks de référence

| Benchmark | Type | Description |
|---|---|---|
| **HotpotQA** | Multi-hop | Questions nécessitant 2+ documents |
| **MultiHop-RAG** | RAG multi-hop | Questions spécifiques au RAG |
| **KILT** | Knowledge-intensive | 5 tâches (FEVER, TriviaQA, etc.) |
| **RGB** (RAG Benchmark) | RAG pur | Évaluation indépendante du LLM |

```python
def evaluer_pipeline_rag(pipeline, jeu_donnees: list[dict]) -> dict:
    """Évalue un pipeline RAG sur un jeu de données de questions-réponses.

    Args:
        pipeline: Pipeline RAG avec méthode executer(requete).
        jeu_donnees: Liste de dict avec 'question', 'reponse_attendue', 'contextes'.

    Returns:
        Métriques Hit Rate@k, MRR, F1.
    """
    hit_rate = 0
    mrr = 0.0

    for item in jeu_donnees:
        reponse, historique = pipeline.executer(item["question"])

        # Vérifier si la réponse correcte est dans les passages récupérés
        tous_passages = [r["texte"] for hop in historique for r in hop["resultats"]]
        trouvee = False
        for i, passage in enumerate(tous_passages):
            if item["reponse_attendue"].lower() in passage.lower():
                hit_rate += 1
                mrr += 1.0 / (i + 1)
                trouvee = True
                break

    n = len(jeu_donnees)
    return {
        "hit_rate": hit_rate / n,
        "mrr": mrr / n,
    }
```

---

## 5. Pièges courants (Pitfalls)

### 5.1 Taille de chunk inadaptée

> **Problème** : Chunks trop petits → contexte fragmenté, informations manquantes. Chunks trop grands → bruit, dépassement de la fenêtre de contexte du LLM.

**Solution** : Expérimentez avec 256, 384 et 512 tokens. Utilisez un découpage sémantique (respect des frontières de phrases et paragraphes) plutôt que des découpages fixes.

### 5.2 "Lost in the Middle"

> **Problème** : Les LLM performent mieux quand l'information pertinente est au début ou à la fin du contexte, et moins bien au milieu.

**Solution** : Réordonnez les passages récupérés pour placer les plus pertinents en premier. Limitez le nombre de passages à 3–5 maximum.

### 5.3 Similarité ≠ Pertinence

> **Problème** : La similarité cosinus mesure la proximité sémantique, pas la pertinence factuelle. Un passage peut être sémantiquement proche mais ne pas contenir la réponse.

**Solution** : Ajoutez un **re-ranker** après la récupération initiale :

```python
class ReRanker:
    """Re-rank les passages récupérés en utilisant un classifieur cross-encoder."""

    def __init__(self, modele: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        from sentence_transformers import CrossEncoder
        self.modele = CrossEncoder(modele)

    def re_ranger(self, requete: str, passages: list[dict], k: int = 3) -> list[dict]:
        """Re-rank les passages par pertinence croisée.

        Args:
            requete: Requête originale.
            passages: Liste de passages avec score.
            k: Nombre de passages à conserver après re-ranking.

        Returns:
            Passages ré-ordonnés par pertinence.
        """
        paires = [(requete, p["texte"]) for p in passages]
        scores = self.modele.predict(paires)

        for i, p in enumerate(passages):
            p["score_re_rank"] = float(scores[i])

        return sorted(passages, key=lambda p: p["score_re_rank"], reverse=True)[:k]
```

### 5.4 Pas de mise à jour de l'index

> **Problème** : L'index est construit une fois et jamais mis à jour, conduisant à des connaissances obsolètes.

**Solution** : Implémentez une stratégie de mise à jour incrémentale :

```python
def mettre_a_jour_index(index: IndexHybride, nouveaux_docs: list[str],
                        batch_size: int = 100) -> None:
    """Met à jour l'index RAG avec de nouveaux documents (incrémental).

    Args:
        index: Index hybride existant.
        nouveaux_docs: Nouveaux documents à indexer.
        batch_size: Taille du batch pour l'embedding.
    """
    # Dans un système réel, utiliser une base vectorielle qui supporte
    # les insertions incrémentales (Chroma, Qdrant, Weaviate)
    for i in range(0, len(nouveaux_docs), batch_size):
        batch = nouveaux_docs[i:i + batch_size]
        index.indexer(index.chunks + batch)
```

---

## 6. Checklist de validation

- [ ] La stratégie de chunking est-elle adaptée au type de documents (taille, frontières) ?
- [ ] L'index utilise-t-il une recherche hybride (dense + sparse) ?
- [ ] Un re-ranker (cross-encoder) est-il présent après la récupération initiale ?
- [ ] Le nombre de passages (k) est-il limité à 3–5 pour éviter le "lost in the middle" ?
- [ ] Le pipeline gère-t-il les questions multi-hop (décomposition automatique) ?
- [ ] Les métriques d'évaluation sont-elles définies (Hit Rate, MRR, F1) ?
- [ ] L'index est-il mis à jour régulièrement (incrémental) ?
- [ ] Le contexte passé au LLM respecte-t-il la limite de tokens du modèle ?
- [ ] Un mécanisme de citation des sources est-il implémenté dans la réponse ?
- [ ] Les dépendances (sentence-transformers, chromadb, pytorch) sont-elles installées ?

---

## 7. Extensions et intégrations

### 7.1 Intégration avec la mémoire de l'agent

Combinez RAG avec la mémoire à long terme de l'agent (cf. `memory-management-ai`) :

```python
class RAGAvecMemoire:
    """RAG enrichi par la mémoire des interactions passées."""

    def __init__(self, index: IndexHybride, memoire_agent):
        self.index = index
        self.memoire = memoire_agent

    def executer(self, requete: str) -> str:
        # 1. Récupérer les documents
        docs = self.index.rechercher(requete, k=3)

        # 2. Récupérer les souvenirs pertinents
        souvenirs = self.memoire.rechercher(requete, k=2)

        # 3. Fusionner
        contexte_complet = docs + souvenirs
        return self._generer(requete, contexte_complet)
```

### 7.2 Compétences complémentaires

- **`memory-management-ai`** : pour la mémoire persistante de l'agent couplée au RAG.
- **`agentic-research-and-arxiv`** : pour la veille sur les publications RAG récentes.

---

## 8. Références

- `references/rag_configurations.md` : matrice de configuration RAG (modèle d'embedding × chunk size × retriever type).
- `scripts/rag_pipeline_complet.py` : pipeline RAG complet de l'indexation à la génération.
- `templates/rag_report_template.md` : template de rapport d'évaluation RAG.

---

*Documentation maintenue par Helios Agent — Dernière mise à jour : 2025*
