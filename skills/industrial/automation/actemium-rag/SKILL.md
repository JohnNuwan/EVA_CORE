---
name: EVA-rag
description: "Utiliser quand l'utilisateur doit interroger, exploiter et citer correctement la base RAG EVA pour standards, architectures, automatisme et procédures internes."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [EVA, rag, knowledge-base, industrial, standards, internal-docs]
    related_skills: [industrial-generator, siemens-scl, industrial-protocols, ot-security-skill-map]
---

# Utilisation du RAG EVA

## Vue d'ensemble

Cette compétence permet à EVA d'utiliser au mieux le RAG EVA pour répondre aux questions sur les standards industriels, les guides de programmation d'automates, les architectures OT/IT et les procédures d'intégration internes. L'objectif n'est pas seulement de retrouver une information, mais d'en faire une réponse traçable et exploitable.

## Quand l'utiliser

À utiliser lorsque la requête porte sur :
- des standards ou pratiques internes EVA ;
- des guides de programmation automates (Structured Text, TIA Portal, etc.) ;
- des architectures réseau industrielles (SCADA, MES, OPC UA, Sparkplug B) ;
- des modèles ou spécifications propres à des sites, projets ou entités EVA.

Ne pas utiliser pour :
- une question générique sans besoin de connaissance interne ;
- une réponse réglementaire nécessitant une norme externe officielle comme source primaire ;
- une hypothèse technique non couverte par le corpus RAG.

## Prérequis

1. Le serveur MCP nommé `EVA_rag` doit être actif et configuré.
2. Si le serveur MCP n'est pas joignable, une commande CLI de fallback peut être utilisée si elle existe dans l'environnement.
3. Les réponses doivent toujours citer les sources retournées par le RAG.

## Workflow recommandé

1. Identifier si la question demande une connaissance interne plutôt qu'une simple expertise générale.
2. Interroger d'abord le RAG via les outils MCP exposés dans la session.
3. En fallback, utiliser la CLI prévue par l'environnement si le MCP n'est pas disponible.
4. Reformuler la réponse avec :
   - synthèse technique,
   - points de vigilance,
   - sources citées,
   - écarts ou alertes éventuelles.
5. Distinguer ce qui vient du RAG et ce qui relève de l'analyse de l'agent.

## Formatage des réponses

- Toujours citer les sources et fichiers référencés par le RAG.
- Si le RAG signale des écarts de conformité ou alertes spécifiques, créer une section dédiée.
- Si du code automate est restitué, le rendre lisible et contextualisé.
- Si la réponse reste incomplète, l'indiquer explicitement plutôt que d'inventer un standard interne.

## Support files

- `references/query-patterns.md` : patterns de requêtes utiles et règles de citation.

## Pièges Courants (Common Pitfalls)

1. Répondre de mémoire alors qu'une source interne existe dans le RAG.
2. Mélanger information issue du RAG et déduction personnelle sans le signaler.
3. Omettre la citation des sources documentaires.
4. Utiliser le RAG comme source réglementaire absolue sans vérifier la portée du document.

## Liste de vérification (Checklist)

- [ ] La question justifie bien l'usage du RAG EVA.
- [ ] Le RAG a été interrogé via MCP ou fallback approprié.
- [ ] Les sources sont citées.
- [ ] Les alertes ou écarts sont mis en évidence.
- [ ] La frontière entre source interne et analyse de l'agent est claire.
