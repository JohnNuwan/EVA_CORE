# Approche "Recherche d'abord" (Research-First)

## Règle fondamentale

> **Quand l'agent ne possède pas de skill ou de connaissance fiable sur un sujet, il doit utiliser le navigateur intégré pour chercher l'information avant de répondre. Ne jamais improviser avec des connaissances incertaines.**

## Directive comportementale

```
Pas de skill ? → Navigateur → Sources autoritaires → Synthèse → Réponse
```

Cette règle a été explicitement demandée par l'utilisateur (session du 2026-07-02). L'utilisateur a indiqué que si les compétences sont absentes, il faut aller chercher sur internet plutôt que d'improviser.

## Outils à utiliser (par ordre de préférence)

1. **`browser_navigate`** — Pour les blogs officiels, la documentation, les articles
2. **`browser_console`** avec `document.body.innerText` — Pour extraire le contenu des pages lourdes en JS (ex: GitHub, Meta AI)
3. **APIs directes** (arXiv, Semantic Scholar, GitHub API) — Plus rapide que le navigateur pour les données structurées
4. **`execute_code`** avec `urllib` — Pour les requêtes HTTP programmatiques

## Anti-pattern (ce qu'il ne faut PAS faire)

- Improviser une réponse basée sur des connaissances générales obsolètes
- Dire "je ne sais pas" sans avoir cherché
- Faire confiance à sa date de cutoff sans vérifier les évolutions récentes

## Exemple concret (session JEPA)

L'utilisateur a demandé des informations sur JEPA. L'agent n'avait aucun skill sur le sujet.

**Démarche appliquée :**
1. Navigation vers `ai.meta.com/blog/yann-lecun-ai-model-i-jepa/` → blog I-JEPA
2. Navigation vers `raw.githubusercontent.com/facebookresearch/jepa/main/README.md` → README complet
3. `browser_console` pour extraire `document.body.innerText` → contournement JS
4. Navigation vers `ai.meta.com/blog/v-jepa...` → blog V-JEPA
5. Tentative arXiv API pour les papiers → extraction des abstracts
6. Synthèse et création du skill `jepa-joint-embedding-predictive-architecture`

**Résultat :** un skill complet basé sur des sources autoritaires (Meta AI, arXiv, GitHub), pas sur de l'improvisation.

## Coût-bénéfice

- **Coût** : 5-10 appels navigateur/outils → ~30-60 secondes
- **Bénéfice** : réponse fiable, sourcée, capitalisable en skill réutilisable
- **Ratio** : toujours positif pour des sujets que l'agent ne maîtrise pas

## Quand cette règle s'applique

| Situation | Action |
|---|---|
| Sujet absent des skills | Recherche web obligatoire |
| Sujet présent en skill mais potentiellement obsolète | Vérification web recommandée |
| Sujet maîtrisé avec skill à jour | Réponse directe OK |
| Question factuelle simple (date, définition) | Réponse directe OK si confiance élevée |