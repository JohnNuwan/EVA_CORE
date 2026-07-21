---
name: agentic-ai
description: Guide complet des systèmes agentiques — agents autonomes, multi-agents, tools, planification, mémoire, RAG, frameworks (LangChain, CrewAI, AutoGen). En français.

---

# IA Agentique — Guide Complet (Français)

Systèmes autonomes : agents, outils, planification, mémoire, multi-agents.

---

## 1. Architecture d'un Agent

```
┌─────────────┐    ┌──────────┐    ┌───────────┐
│  Mémoire    │    │  LLM /   │    │  Outils   │
│  (court +   │◄──►│  Cerveau │───►│  (tools)  │
│   long)     │    │          │    │           │
└─────────────┘    └──────────┘    └───────────┘
        ▲                │               │
        └────────────────┴───────────────┘
                   Planification
```

### Boucle agentique
```
Observe → Planifie → Agit → Observe → ...
(ReAct = Reason + Act)
```

### Capacités clés
1. **Outils (Tools)** : appel d'API, exécution de code, recherche web
2. **Mémoire** : contexte court-terme + persistance long-terme
3. **Planification** : décomposer des tâches complexes
4. **Réflexion** : auto-critique, correction d'erreurs
5. **Multi-agent** : collaboration et délégation

---

## 2. Function Calling / Tools

```python
# Définition d'outils (schéma OpenAI)
tools = [
    {
        "type": "function",
        "function": {
            "name": "obtenir_meteo",
            "description": "Obtenir la météo pour une ville",
            "parameters": {
                "type": "object",
                "properties": {
                    "ville": {"type": "string"},
                    "unite": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["ville"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "envoyer_email",
            "description": "Envoyer un email",
            "parameters": {
                "type": "object",
                "properties": {
                    "destinataire": {"type": "string"},
                    "sujet": {"type": "string"},
                    "corps": {"type": "string"},
                },
                "required": ["destinataire", "sujet", "corps"],
            },
        },
    },
]

# Exécution d'outils
def executer_outil(appel):
    nom = appel.function.name
    args = json.loads(appel.function.arguments)
    
    if nom == "obtenir_meteo":
        return f"Météo pour {args['ville']}: 22°C, ensoleillé"
    elif nom == "envoyer_email":
        return f"Email envoyé à {args['destinataire']}"
```

---

## 3. ReAct (Reasoning + Acting)

```python
class AgentReAct:
    """Agent avec boucle Raisonnement → Action."""
    
    def __init__(self, llm, outils: dict[str, callable]):
        self.llm = llm
        self.outils = outils
        self.historique: list[dict] = []
    
    def agir(self, tache: str, max_iterations: int = 5) -> str:
        self.historique = [{"role": "user", "content": tache}]
        
        for _ in range(max_iterations):
            reponse = self.llm(self.historique, outils=self.outils)
            
            if reponse.final_answer:
                return reponse.final_answer
            
            if reponse.tool_calls:
                resultat = self.executer(reponse.tool_calls)
                self.historique.append({"role": "tool", "content": resultat})
        
        return "Limite d'itérations atteinte"
```

### Prompt ReAct
```
Tu es un agent qui raisonne étape par étape.

Format :
Thought: [ton raisonnement]
Action: [outil à appeler]
Action Input: [paramètres JSON]
Observation: [résultat de l'outil]
... (répète si nécessaire)
Final Answer: [réponse finale à l'utilisateur]
```

---

## 4. Planification (Plan-and-Execute)

```python
class Planificateur:
    """Décompose une tâche en sous-tâches, puis exécute."""
    
    def planifier(self, objectif: str) -> list[str]:
        """Décomposer l'objectif en étapes."""
        prompt = f"""
        Décompose l'objectif suivant en étapes ordonnées :
        Objectif : {objectif}
        
        Retourne une liste JSON d'étapes.
        """
        etapes = llm(prompt)
        return json.loads(etapes)
    
    def executer(self, etapes: list[str]) -> str:
        resultats = []
        for etape in etapes:
            resultat = agent.agir(etape)
            resultats.append(resultat)
        return "\n".join(resultats)
```

---

## 5. Gestion de Mémoire

```python
from typing import Any
import chromadb


class MemoireAgent:
    """Mémoire vectorielle pour persistance."""
    
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("memoire")
    
    def sauvegarder(self, cle: str, valeur: str, metadata: dict = None):
        self.collection.add(
            documents=[valeur],
            metadatas=[metadata or {}],
            ids=[cle],
        )
    
    def rechercher(self, requete: str, k: int = 5) -> list[str]:
        resultats = self.collection.query(
            query_texts=[requete],
            n_results=k,
        )
        return resultats["documents"][0]
    
    def resumer(self, conversation: list[dict]) -> str:
        """Résumer l'historique pour compression."""
        return llm.summarize(conversation)
```

---

## 6. Multi-Agents

### Patterns de collaboration
1. **Chaîne** : A → B → C (pipeline)
2. **Débat** : A ↔ B (discussion, consensus)
3. **Hiérarchique** : Manager → Workers
4. **Marché** : Agents enchérissent sur des tâches

```python
# Avec CrewAI
from crewai import Agent, Task, Crew, Process

chercheur = Agent(
    role="Chercheur",
    goal="Trouver des informations pertinentes",
    backstory="Expert en recherche documentaire",
    tools=[outil_recherche, outil_web],
    verbose=True,
)

redacteur = Agent(
    role="Rédacteur",
    goal="Rédiger des articles clairs",
    backstory="Journaliste expérimenté",
    verbose=True,
)

tache_recherche = Task(
    description="Rechercher les dernières avancées en IA",
    agent=chercheur,
)

tache_redaction = Task(
    description="Rédiger un article basé sur la recherche",
    agent=redacteur,
)

equipe = Crew(
    agents=[chercheur, redacteur],
    tasks=[tache_recherche, tache_redaction],
    process=Process.sequential,
)

resultat = equipe.kickoff()
```

---

## 7. RAG (Retrieval-Augmented Generation)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

# Indexation
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings()
vectorstore = Chroma.from_documents(chunks, embeddings)

# Récupération + Génération
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # Ou "map_reduce", "refine"
    retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
)

reponse = qa_chain.run("Quelle est la politique de retour ?")
```

---

## 8. Frameworks Agentiques

| Framework | Focus | Forces |
|-----------|-------|--------|
| **LangChain** | Généraliste | RAG, tools, mémoire, chaînes |
| **LlamaIndex** | RAG, données | Indexation avancée, structuration |
| **CrewAI** | Multi-agent | Orchestration d'équipes |
| **AutoGen** (Microsoft) | Multi-agent | Conversation, code execution |
| **LangGraph** | State machines | Graphes, flux complexes |
| **DSPy** | Optimisation de prompts | Compilation automatique de prompts |

---

## 9. Sécurité et Garde-fous

```python
# Validation des appels d'outils
def outil_securise(appel):
    actions_interdites = ["supprimer_fichiers", "executer_sql_raw"]
    
    if appel.function.name in actions_interdites:
        return "Action non autorisée"
    
    # Rate limiting
    if compteur_appels > MAX_APPELS:
        return "Limite d'appels atteinte"
    
    # Sandbox
    with environnement_isole():
        return executer(appel)


# Guardrails (validation sortie)
from guardrails import Guard

guard = Guard.from_string(
    validators=[
        "no_profanity",
        "length: 10-500",
        "valid_json"
    ]
)
```

---

## 10. Évaluation d'Agents

```python
# Métriques clés
- Taux de succès (% tâches accomplies)
- Nombre moyen d'itérations
- Coût (tokens consommés)
- Exactitude des appels d'outils
- Hallucinations (taux d'informations inventées)
- Latence (temps de réponse)

# Benchmarks
- SWE-bench : résolution de bugs réels
- WebArena : navigation web
- GAIA : questions complexes multi-étapes
- ToolBench : utilisation d'outils
```

---

## Références
- ReAct Paper : https://arxiv.org/abs/2210.03629
- AutoGPT : https://github.com/Significant-Gravitas/AutoGPT
- LangChain : https://python.langchain.com/
- CrewAI : https://docs.crewai.com/