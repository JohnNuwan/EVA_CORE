# Méthodologie : Recherche Concurrentielle Agent IA

> Session : Juillet 2026 — Analyse concurrentielle EVA vs Claude Code, Google Antigravity, et acteurs industriels.
> Méthodes de recherche web utilisées et leçons apprises.

## Sources utilisées

| Source | URL | Fiabilité | Notes |
|--------|-----|-----------|-------|
| TechCrunch | techcrunch.com | Élevée | Couvre Google I/O, lancements produits. Recherche via `?s=` |
| Wikipedia API | wikipedia.org/w/api.php | Élevée | API JSON, pas de blocage |
| GitHub Search | github.com/search | Élevée | Bloqué (encoding errors) |
| DuckDuckGo | duckduckgo.com | Moyenne | Bloqué (encoding errors) |
| Bing | bing.com | Moyenne | Cloudflare challenge |
| Reddit JSON API | reddit.com/r/*/search.json | Moyenne | Bloqué (encoding errors) |

## Méthode efficace pour la recherche concurrentielle tech

### Étape 1 : TechCrunch (presse tech généraliste)
```
browser_navigate("https://techcrunch.com/?s=<terme de recherche>")
```
- Avantage : pas de blocage, snapshot lisible, résultats structurés
- Limite : ne couvre pas l'industrie/OT

### Étape 2 : Extraction des liens depuis le snapshot
```
browser_console("Array.from(document.querySelectorAll('a')).filter(a => a.textContent.includes('<terme>')).map(a => a.href)")
```

### Étape 3 : Navigation vers l'article cible
```
browser_navigate("<url extraite>")
```

### Étape 4 : Synthèse et comparaison
- Extraire les features clés, dates, prix
- Construire une matrice comparative
- Identifier les gaps et opportunités

## Pièges rencontrés

1. **Erreurs d'encodage UTF-8** : GitHub, Reddit, DuckDuckGo, Bing — échec systématique avec `'utf-8' codec can't decode byte`. Contournement : utiliser TechCrunch (site bien encodé) ou APIs JSON directes.

2. **Cloudflare / CAPTCHA** : Bing et Google bloquent les requêtes automatisées. Contournement : éviter les moteurs de recherche, privilégier les sites d'actualité tech directement.

3. **Recherche vide sur les sujets industriels** : TechCrunch n'a quasi aucun article sur Siemens Industrial Copilot, Beckhoff, ou l'automatisme. Pour le domaine OT, les connaissances internes (training data + skills) sont plus fiables que la recherche web.

4. **Terminal bloqué (M2A)** : Les appels `terminal()` étaient refusés par la politique d'autorisation. Contournement : utiliser exclusivement les outils browser.

## Résultats clés de la session

- **Claude Code** : 13 gaps identifiés, plan d'implémentation VS Code + TUI sur 8-10 semaines
- **Google Antigravity** : Inattaquable frontalement (650M users, Gemini 3.5 co-développé, écosystème Google)
- **Concurrents industriels** : Aucun concurrent direct. Siemens Copilot = 6/76 critères. EVA = 76/76.
- **Positionnement** : EVA est seul sur le croisement Multi-Constructeur × Génération de Code × Safety × Normes × Mémoire

## Documents produits

- `docs/strategie/analyse_concurrence_claude_code.md` — Gaps + plan VS Code/TUI
- `docs/strategie/analyse_concurrentielle_industrie40.md` — 76 critères, matrice concurrentielle OT