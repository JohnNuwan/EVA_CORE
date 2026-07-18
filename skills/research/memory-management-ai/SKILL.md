---
name: memory-management-ai
description: "Explorer les techniques avancées de gestion de la mémoire dans les systèmes d'intelligence artificielle pour des applications à long terme, incluant les mémoires vectorielles, graphiques et adaptatives."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
tags: [mémoire, RAG, vector-store, mémoire-graphique, consolidation, oubli-stratégique]
keywords: [memory management, vector database, graph memory, memory consolidation, forgetting mechanism]
---

# Gestion Avancée de la Mémoire dans l'IA

## Vue d'ensemble

Les systèmes d'intelligence artificielle modernes — en particulier les agents conversationnels et les assistants autonomes — doivent maintenir un état mémoire cohérent et évolutif sur de longues périodes d'interaction. Contrairement aux bases de données classiques, la mémoire d'un agent IA doit gérer l'**incertitude**, l'**obsolescence** et les **conflits** entre informations.

Cette compétence couvre l'ensemble des mécanismes de gestion mémoire :

1. **Encodage et indexation** : transformer des informations brutes en représentations vectorielles ou symboliques.
2. **Stockage et organisation** : structurer la mémoire (linéaire, hiérarchique, graphique) pour faciliter la récupération.
3. **Récupération contextuelle** : extraire les informations pertinentes au moment opportun.
4. **Mise à jour et consolidation** : intégrer de nouvelles informations tout en résolvant les conflits.
5. **Oubli stratégique** : supprimer ou archiver les informations devenues obsolètes ou redondantes.

---

## Quand utiliser cette compétence

| Scénario | Pertinence |
|---|---|
| Assistant conversationnel opérant sur plusieurs sessions (jours/semaines) | Élevée |
| Agent devant mémoriser les préférences et l'historique d'un utilisateur | Élevée |
| Système multi-agents partageant une mémoire commune | Élevée |
| Application nécessitant une mémoire à long terme avec oubli progressif | Moyenne |
| Pipeline RAG standard (sans historique utilisateur) | Faible (préférer une base vectorielle simple) |

---

## 1. Architectures de mémoire

### 1.1 Taxonomie des types de mémoire

| Type | Persistance | Exemple d'usage |
|---|---|---|
| **Mémoire de travail** (Working Memory) | Session courante | Contexte de la conversation en cours |
| **Mémoire épisodique** | Long terme | Événements passés, interactions utilisateur |
| **Mémoire sémantique** | Long terme | Connaissances générales, faits appris |
| **Mémoire procédurale** | Long terme | Compétences, procédures, "comment faire" |

### 1.2 Mémoire vectorielle (Vector Store)

La forme la plus courante de mémoire pour les agents LLM. Chaque information est encodée en un vecteur dense et stockée dans une base vectorielle.

```python
import numpy as np
from typing import Any

class MemoireVectorielle:
    """Mémoire basée sur des vecteurs d'embedding avec recherche par similarité cosinus."""

    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.vecteurs: list[np.ndarray] = []
        self.donnees: list[dict[str, Any]] = []
        self.index: dict[int, list[float]] = {}

    def encoder(self, texte: str) -> np.ndarray:
        """Encode un texte en vecteur (simulation — utiliser un vrai modèle d'embedding)."""
        np.random.seed(hash(texte) % 2 ** 32)
        return np.random.randn(self.dimension) / np.sqrt(self.dimension)

    def stocker(self, texte: str, metadonnees: dict | None = None) -> int:
        """Stocke un texte avec ses métadonnées dans la mémoire vectorielle.

        Args:
            texte: Contenu textuel à mémoriser.
            metadonnees: Métadonnées associées (timestamp, source, priorité, etc.).

        Returns:
            ID unique de l'entrée mémoire.
        """
        vecteur = self.encoder(texte)
        idx = len(self.vecteurs)
        self.vecteurs.append(vecteur)
        self.donnees.append({
            "texte": texte,
            "metadonnees": metadonnees or {},
            "timestamp": metadonnees.get("timestamp", 0) if metadonnees else 0,
        })
        self.index[idx] = vecteur.tolist()
        return idx

    def rechercher(self, requete: str, k: int = 5) -> list[dict[str, Any]]:
        """Recherche les k entrées les plus similaires à la requête.

        Args:
            requete: Texte de requête.
            k: Nombre de résultats à retourner.

        Returns:
            Liste des entrées mémoire triées par pertinence.
        """
        vecteur_requete = self.encoder(requete)
        scores = [
            (np.dot(vecteur_requete, v) /
             (np.linalg.norm(vecteur_requete) * np.linalg.norm(v)), i)
            for i, v in enumerate(self.vecteurs)
        ]
        scores_tries = sorted(scores, key=lambda x: x[0], reverse=True)[:k]

        return [
            {**self.donnees[idx], "score": score}
            for score, idx in scores_tries
        ]
```

### 1.3 Mémoire graphique (Graph Memory)

La mémoire graphique organise les entités et leurs relations sous forme de graphe, permettant un raisonnement multi-sauts et une récupération hiérarchique.

```python
class MemoireGraphique:
    """Mémoire organisée en graphe orienté avec relations typées entre nœuds."""

    def __init__(self):
        self.noeuds: dict[str, dict] = {}
        self.relations: list[tuple[str, str, str]] = []  # (source, cible, type)

    def ajouter_entite(self, id_entite: str, proprietes: dict | None = None) -> None:
        """Ajoute ou met à jour une entité dans le graphe mémoire.

        Args:
            id_entite: Identifiant unique de l'entité.
            proprietes: Propriétés associées (nom, type, description, etc.).
        """
        self.noeuds[id_entite] = proprietes or {}

    def ajouter_relation(self, source: str, cible: str, type_relation: str) -> None:
        """Ajoute une relation typée entre deux entités.

        Args:
            source: Identifiant de l'entité source.
            cible: Identifiant de l'entité cible.
            type_relation: Type de relation (ex: 'collabore_avec', 'meme_projet').
        """
        if source in self.noeuds and cible in self.noeuds:
            self.relations.append((source, cible, type_relation))

    def recuperer_contexte(self, id_entite: str, profondeur: int = 2) -> list[dict]:
        """Récupère le contexte autour d'une entité par propagation dans le graphe.

        Args:
            id_entite: Entité centrale.
            profondeur: Nombre de sauts de relation à explorer.

        Returns:
            Liste des entités voisines avec leur distance.
        """
        visite = {id_entite: 0}
        file_attente = [(id_entite, 0)]

        while file_attente:
            courant, distance = file_attente.pop(0)
            if distance >= profondeur:
                continue
            for src, cible, _ in self.relations:
                voisin = cible if src == courant else (src if cible == courant else None)
                if voisin and voisin not in visite:
                    visite[voisin] = distance + 1
                    file_attente.append((voisin, distance + 1))

        return [
            {"id": n, "distance": d, "proprietes": self.noeuds.get(n, {})}
            for n, d in visite.items() if n != id_entite
        ]
```

---

## 2. Mise à jour sélective et consolidation

### 2.1 Filtrage dynamique des informations

Toutes les informations ne méritent pas d'être mémorisées. Un filtre de pertinence détermine ce qui doit être consolidé :

```python
class FiltreMemoire:
    """Filtre les informations entrantes pour ne conserver que celles pertinentes."""

    def __init__(self, seuil_pertinence: float = 0.6):
        self.seuil_pertinence = seuil_pertinence

    def evaluer_pertinence(self, information: dict) -> float:
        """Évalue la pertinence d'une information sur plusieurs critères.

        Critères :
        - Nouveauté : l'information apporte-t-elle quelque chose de nouveau ?
        - Spécificité : l'information est-elle spécifique à l'utilisateur ?
        - Actionnabilité : l'information peut-elle être utilisée pour une action future ?

        Args:
            information: Dictionnaire décrivant l'information (clés: contenu, source, type).

        Returns:
            Score de pertinence entre 0 et 1.
        """
        score = 0.0
        contenu = information.get("contenu", "")

        # Nouveauté (présence de mots uniques)
        mots_uniques = len(set(contenu.lower().split()))
        score += min(mots_uniques / 20, 0.4)  # max 0.4

        # Spécificité (référence à l'utilisateur)
        if "utilisateur" in contenu.lower():
            score += 0.3

        # Actionnabilité (présence de verbes d'action)
        verbes_action = {"programmer", "acheter", "réserver", "créer", "envoyer"}
        if any(v in contenu.lower() for v in verbes_action):
            score += 0.3

        return min(score, 1.0)

    def filtrer(self, informations: list[dict]) -> list[dict]:
        """Filtre une liste d'informations selon le seuil de pertinence.

        Args:
            informations: Liste d'informations à filtrer.

        Returns:
            Informations jugées pertinentes.
        """
        return [
            info for info in informations
            if self.evaluer_pertinence(info) >= self.seuil_pertinence
        ]
```

### 2.2 Consolidation et résolution de conflits

Lorsque deux informations contradictoires sont stockées, un mécanisme de résolution est nécessaire :

```python
class ConsolidateurMemoire:
    """Résout les conflits entre informations redondantes ou contradictoires."""

    def resoudre_conflit(self, existant: dict, nouveau: dict) -> dict:
        """Fusionne deux entrées mémoire en cas de conflit.

        Règles :
        - L'information la plus récente est prioritaire, sauf si l'ancienne est marquée comme confirmée.
        - Les préférences explicites (ex. 'je déteste X') écrasent les préférences implicites.

        Args:
            existant: Entrée mémoire existante.
            nouveau: Nouvelle information potentiellement contradictoire.

        Returns:
            Entrée consolidée.
        """
        priorite_existant = existant.get("metadonnees", {}).get("priorite", 0)
        priorite_nouveau = nouveau.get("metadonnees", {}).get("priorite", 0)

        if priorite_nouveau > priorite_existant:
            return nouveau

        if nouveau.get("metadonnees", {}).get("timestamp", 0) > \
           existant.get("metadonnees", {}).get("timestamp", 0) and \
           not existant.get("metadonnees", {}).get("confirmee", False):
            # La nouvelle info est plus récente et l'ancienne n'est pas confirmée
            existant.update(nouveau)
            existant["metadonnees"]["resolu"] = True

        return existant
```

---

## 3. Oubli stratégique (Forgetting)

### 3.1 Pourquoi oublier est nécessaire

| Raison | Impact |
|---|---|
| **Dérive contextuelle** | Une information utile hier peut être trompeuse aujourd'hui |
| **Coût de stockage** | Les bases vectorielles ont un coût mémoire proportionnel au nombre d'entrées |
| **Bruit** | Trop d'informations non pertinentes dégradent la précision de la récupération |
| **Confidentialité** | RGPD — droit à l'effacement |

### 3.2 Politique d'expiration

```python
import time

class PolitiqueExpiration:
    """Gère l'expiration des entrées mémoire selon leur âge et leur importance."""

    def __init__(self, duree_vie_defaut: int = 86400 * 30):  # 30 jours par défaut
        self.duree_vie_defaut = duree_vie_defaut

    def est_expiree(self, entree: dict) -> bool:
        """Vérifie si une entrée mémoire est expirée.

        Args:
            entree: Entrée mémoire avec métadonnées (timestamp, priorité).

        Returns:
            True si l'entrée doit être supprimée ou archivée.
        """
        metadonnees = entree.get("metadonnees", {})
        age = time.time() - metadonnees.get("timestamp", 0)

        # Les entrées à haute priorité vivent plus longtemps
        priorite = metadonnees.get("priorite", 1)
        duree_vie = self.duree_vie_defaut * priorite

        return age > duree_vie
```

### 3.3 Archive vs. suppression

Au lieu de supprimer définitivement, archivez les entrées expirées dans un stockage froid :

```python
class GestionnaireArchive:
    """Déplace les entrées expirées vers un stockage froid."""

    def __init__(self):
        self.archive: list[dict] = []

    def archiver(self, entree: dict) -> None:
        """Déplace une entrée mémoire vers l'archive.

        Args:
            entree: Entrée à archiver.
        """
        entree["metadonnees"]["archivee"] = True
        entree["metadonnees"]["date_archivage"] = time.time()
        self.archive.append(entree)

    def restaurer(self, id_recherche: str, memoires: MemoireVectorielle) -> bool:
        """Restaure une entrée archivée si elle redevient pertinente.

        Args:
            id_recherche: Identifiant de l'entrée à restaurer.
            memoires: Mémoire vectorielle active.

        Returns:
            True si l'entrée a été restaurée avec succès.
        """
        for entree in self.archive:
            if entree.get("id") == id_recherche:
                entree["metadonnees"]["archivee"] = False
                memoires.stocker(
                    entree.get("texte", ""),
                    entree.get("metadonnees"),
                )
                self.archive.remove(entree)
                return True
        return False
```

---

## 4. Pièges courants (Pitfalls)

### 4.1 Mémoire illimitée

> **Problème** : Stocker toutes les informations sans politique d'expiration conduit à une dégradation quadratique des performances de recherche.

**Solution** : Implémentez une politique d'expiration systématique (voir section 3.2). Fixez une taille maximale de mémoire active (ex. 10 000 entrées).

### 4.2 Confusion entre similarité et pertinence

> **Problème** : La recherche par similarité cosinus retourne des résultats sémantiquement proches mais contextuellement inutiles (ex. "Je n'aime pas les chats" et "Les chats sont des félins" ont une similarité élevée).

**Solution** : Combinez la similarité vectorielle avec un filtre temporel et contextuel. Utilisez une **recherche hybride** (BM25 + embeddings).

### 4.3 Écrasement des préférences utilisateur

> **Problème** : Une information accidentelle ("Je déteste le bleu") écrase une préférence établie ("Ma couleur préférée est le bleu").

**Solution** : Implémentez un mécanisme de confirmation pour les modifications contradictoires. Exigez 2 occurrences cohérentes avant de modifier une préférence établie.

### 4.4 Fuite d'information entre sessions utilisateur

> **Problème** : Dans un système multi-utilisateur, la mémoire d'un utilisateur fuit vers un autre, violant la confidentialité.

**Solution** : Segmentez strictement la mémoire par `user_id` ou `session_id`. Utilisez des index vectoriels isolés par utilisateur.

---

## 5. Checklist de validation

- [ ] Le type de mémoire est-il adapté au cas d'usage (vectorielle, graphique, hybride) ?
- [ ] Les embeddings sont-ils générés par un modèle cohérent (même dimension, même tokenizer) ?
- [ ] Une politique d'expiration est-elle définie et paramétrée ?
- [ ] Les conflits entre informations ont-ils un mécanisme de résolution documenté ?
- [ ] Les entrées sont-elles segmentées par utilisateur/session ?
- [ ] La recherche combine-t-elle similarité vectorielle et filtres temporels ?
- [ ] Les informations sensibles (mots de passe, tokens) sont-elles exclues du stockage mémoire ?
- [ ] Un mécanisme d'archive (vs. suppression définitive) est-il en place ?
- [ ] Les performances de recherche sont-elles benchmarkées (latence P50 < 100 ms) ?
- [ ] La taille maximale de la mémoire active est-elle configurable ?

---

## 6. Extensions et intégrations

### 6.1 Intégration avec les pipelines RAG

La mémoire vectorielle peut être branchée comme source de contexte supplémentaire dans un pipeline RAG :

```python
class MemoireRAG:
    """Brique mémoire pour pipeline RAG."""

    def __init__(self, memoire: MemoireVectorielle, seuil_similarite: float = 0.75):
        self.memoire = memoire
        self.seuil_similarite = seuil_similarite

    def enrichir_contexte(self, requete: str, contexte_base: str) -> str:
        """Enrichit un contexte RAG avec des informations issues de la mémoire.

        Args:
            requete: Requête utilisateur.
            contexte_base: Contexte initial (documents récupérés).

        Returns:
            Contexte enrichi avec les souvenirs pertinents.
        """
        souvenirs = self.memoire.rechercher(requete, k=3)
        souvenirs_pertinents = [
            s for s in souvenirs if s["score"] >= self.seuil_similarite
        ]

        if not souvenirs_pertinents:
            return contexte_base

        contexte_souvenirs = "\n".join(
            f"[Souvenir {i+1}] {s['texte']}"
            for i, s in enumerate(souvenirs_pertinents)
        )
        return f"{contexte_souvenirs}\n\n{contexte_base}"
```

### 6.2 Compétences complémentaires

- **`rag-retrieval-augmented-generation`** : pour intégrer la mémoire dans un pipeline de génération augmentée.
- **`multi-agent-reinforcement-learning`** : pour la coordination des mémoires partagées entre agents.

---

## 7. Références

- `references/memory_patterns.md` : catalogue des patrons de conception mémoire (CQRS, Event Sourcing, etc.).
- `scripts/memory_benchmark.py` : script de benchmark des performances de récupération mémoire.
- `templates/memory_config_template.yaml` : template de configuration mémoire pour config.yaml.

---

*Documentation maintenue par Helios Agent — Dernière mise à jour : 2025*
