---
name: seo
description: Référencement naturel (SEO) — audit technique, stratégie de mots-clés, netlinking, optimisation on-page et off-page pour le trafic organique
category: business
---

# SEO — Référencement Naturel

Compétence de niveau expert en Search Engine Optimization (SEO) couvrant l'audit technique, la recherche sémantique, la stratégie de contenu, le netlinking et le suivi de performance.

## 1. Audit Technique SEO

### Crawl et Indexation
- **Crawlers** : Screaming Frog, Sitebulb, DeepCrawl (Lumar) — configurer user-agent, respect robots.txt, limiter crawl budget
- **Fichiers robots.txt** : Vérifier les blocages accidentels (`Disallow: /`), sitemaps, directives `noindex`
- **Sitemaps XML** : Générer avec `<lastmod>`, `<changefreq>`, `<priority>`, soumettre via Google Search Console
- **Balisage canonique** : `rel="canonical"` — éviter le contenu dupliqué, self-referencing canonicals
- **HTTP Status Codes** : 200 OK, 301 (permanent), 302 (temporaire), 404 (introuvable), 410 (supprimé), 5xx (erreur serveur)
- **Pages orphelines** : Pages sans lien interne — détecter avec Screaming Frog + Google Analytics
- **Crawl budget** : Ratio pages crawlées / pages totales, limiter les paramètres d'URL, pagination

### Performance (Core Web Vitals)
- **LCP (Largest Contentful Paint)** : < 2.5s — optimiser images (WebP/AVIF), lazy loading, serveur rapide
- **FID (First Input Delay)** / **INP (Interaction to Next Paint)** : < 200ms — réduire JS bloquant, optimiser event handlers
- **CLS (Cumulative Layout Shift)** : < 0.1 — dimensions fixes pour images/iframes, réserves de polices
- **Outils** : PageSpeed Insights, Lighthouse CI, Chrome User Experience Report (CrUX), Web Vitals extension
- **Améliorations** : CDN, compression Brotli, HTTP/2 ou HTTP/3, préchargement des ressources critiques

### Mobile-First
- **Responsive design** : Media queries, viewport meta tag, test d'écran 320px
- **Mobile Usability** : Google Search Console > Mobile Usability
- **AMP (Accelerated Mobile Pages)** : Utile pour l'actualité, déclinant — privilégier le responsive
- **Touch targets** : Boutons ≥ 48x48px, espacement suffisant

### Données Structurées (Schema.org)
- **Types essentiels** : `Organization`, `LocalBusiness`, `Product`, `Article`, `FAQPage`, `HowTo`, `BreadcrumbList`, `Review`, `Event`
- **JSON-LD** : Format recommandé, injecté dans `<head>` ou via Google Tag Manager
- **Test** : Schema Markup Validator (Google), Rich Results Test
- **Autres vocabulaires** : Open Graph (Facebook), Twitter Cards, Dublin Core

## 2. Recherche de Mots-Clés

### Outils
- **Google Keyword Planner** : Volume, concurrence, CPC (nécessite compte Ads)
- **Ahrefs / Semrush / Moz** : KD (Keyword Difficulty), SERP features, volume, tendances
- **AnswerThePublic** : Questions naturelles, prépositions, comparaisons
- **Google Suggest / People Also Ask** : Requêtes longue traîne
- **GSC (Google Search Console)** : Requêtes existantes, impressions, CTR, position moyenne
- **AlsoAsked.com** : Arbres de questions associées
- **Trends** : Google Trends, tendances saisonnières, sujets émergents

### Taxonomie des Mots-Clés
1. **Tête de raquette** (head terms) : Fort volume, forte concurrence (ex: "assurance auto")
2. **Longue traîne** (long-tail) : Faible volume, faible concurrence, fort taux de conversion (ex: "assurance auto jeune conducteur pas cher")
3. **Mots-clés sémantiques** : Mots-clés LSI, synonymes, concepts associés
4. **Intentions de recherche** : Informationnelle (`comment`, `qu'est-ce que`), Navigationnelle (`nom de marque`), Transactionnelle (`acheter`, `prix`), Commerciale (`meilleur`, `comparatif`)

### Analyse des SERP
- **SERP Features** : Featured snippets, People Also Ask, Knowledge Panel, Images, Vidéos, Shopping, Local Pack
- **Fragment de code (Featured Snippet)** : Répondre directement à la question dans un format structuré (listes, tableaux, paragraphes)
- **Position zéro** : Optimiser pour les featured snippets — format concis, balises `<h2>`/`<h3>`, listes ordonnées

## 3. Optimisation On-Page

### Balises HTML
- **Title (`<title>`)** : 50-60 caractères, mot-clé principal au début, unique par page, marque à la fin
- **Meta Description** : 150-160 caractères, incitation au clic (CTR), mot-clé secondaire
- **Headings (H1-H6)** : Un seul H1 par page, arborescence logique, mots-clés dans les sous-titres
- **URLs** : Courtes, descriptives, traits d'union, mot-clé, ex: `/guides/seo-technique`
- **Alt Text (images)** : Descriptif + mot-clé pertinent, pas de keyword stuffing
- **Balises méta robots** : `noindex` (ne pas indexer), `nofollow` (ne pas suivre liens), `nosnippet`

### Contenu
- **Qualité E-E-A-T** : Experience, Expertise, Authoritativeness, Trustworthiness
- **Longueur** : Pas de minimum absolu — couvrir le sujet exhaustivement (1500-3000 mots pour le contenu standard)
- **Densité de mots-clés** : Naturelle, pas de bourrage (keyword stuffing)
- **Liens internes** : Maillage thématique, ancres descriptives, pas plus de 100 liens par page
- **Liens externes** : Vers des sources autorisées (gouvernement, éducation, .edu, .gov)
- **Fraîcheur** : Mettre à jour régulièrement le contenu, date de publication visible

### Multilingue
- **Hreflang** : `rel="alternate" hreflang="fr"`, `hreflang="x-default"`
- **Balise `<html lang="fr">`**
- **URLs** : Sous-domaines (`fr.example.com`), sous-répertoires (`example.com/fr/`), domaines séparés (`example.fr`)

## 4. Stratégie de Netlinking (Off-Page)

### Acquisition de Liens
- **Link bait** : Contenu viral, études originales, infographies, outils gratuits
- **Guest posting** : Articles invités sur des blogs autoritaires du secteur
- **Skyscraper technique** : Trouver un contenu populaire, créer une version supérieure, demander des backlinks
- **Digital PR** : Relations presse, mentions médiatiques, HARO (Help a Reporter Out)
- **Broken link building** : Trouver des liens morts sur des sites partenaires, proposer son contenu en remplacement
- **Forum / Community** : Reddit, Quora, Stack Overflow — liens naturels dans les réponses
- **Répertoires** : Uniquement les annuaires de qualité (Yelp, PagesJaunes, etc.)

### Analyse des Backlinks
- **Métriques** : Domain Rating (DR/Ahrefs), Authority Score (Semrush), Domain Authority (DA/Moz)
- **Qualité** : Pertinence thématique, autorité du domaine de référence, dofollow vs nofollow
- **Toxic backlinks** : Liens spam, PBN (Private Blog Networks), sites pénalisés — désavouer via Google Disavow Tool
- **Profil de liens** : Croissance naturelle, diversité des domaines référents, ratio dofollow/nofollow

## 5. SEO Local

- **Google Business Profile** : Fiche complète, catégories, photos, horaires, réponses aux avis, posts
- **NAP** : Name, Address, Phone — cohérent sur tout le web
- **Citations** : PagesJaunes, Mappy, 118000, etc.
- **Avis clients** : Gérer et répondre aux avis Google, Yelp, Trustpilot
- **Balisage LocalBusiness** : Schema.org LocalBusiness avec coordonnées, horaires d'ouverture

## 6. Suivi et Reporting

### KPIs
- **Trafic organique** : Sessions, utilisateurs, pages vues (Google Analytics 4)
- **Positions** : Position moyenne, distribution (top 3, top 10, top 30)
- **CTR** : Taux de clic dans les SERP (GSC)
- **Conversions** : Objectifs GA4, e-commerce, leads, appels téléphoniques
- **Taux de rebond** : Qualité du trafic et pertinence du contenu
- **Pages indexées** : Nombre de pages en index Google

### Outils de Reporting
- **Google Search Console** : Requêtes, impressions, clics, position, pages, sitemaps
- **Google Analytics 4** : Acquisition, comportement, conversions, exploration
- **Google Looker Studio** : Tableaux de bord personnalisés avec GSC + GA4
- **Ahrefs / Semrush** : Rank tracker, analyse concurrentielle, audits
- **Screaming Frog** : Audits techniques programmés
- **Botify / Oncrawl** : Analyse de crawl log (logs serveur)

## 7. Pénalités et Résolution

- **Pénalités manuelles** : Via GSC > Security & Manual Actions — corriger les problèmes, soumettre une demande de réexamen
- **Pénalités algorithmiques** : Panda (contenu), Penguin (liens), Core Updates
- **Réponse** : Audit complet, désaveu des liens toxiques, amélioration du contenu, nettoyage technique
- **Vérification** : Chute soudaine du trafic → consulter GSC, vérifier les Core Updates récents, comparer les dates

## 8. SEO Technique Avancé

- **JavaScript SEO** : Rendu côté client (CSR) vs SSR (Next.js, Nuxt.js), Dynamic Rendering, Googlebot rend le JS depuis 2019
- **Core Web Vitals** : Interaction to Next Paint (INP) remplace FID en mars 2024
- **HTTP/2 Server Push** : Obsolète — utiliser 103 Early Hints
- **Content Delivery Network (CDN)** : Cloudflare, Fastly, Akamai — cache, edge computing, DDoS protection
- **Page Experience** : Signal combiné (CWV + HTTPS + mobile-friendly + no intrusive interstitials)
- **Google Discover** : Contenu engageant et opportun pour le flux Discover (images de haute qualité, titres accrocheurs)
- **SGE (Search Generative Experience)** : L'IA générative de Google redéfinit les SERP — optimiser pour la réponse directe et les données structurées

## Pièges Courants

- **Keyword cannibalization** : Pages internes en concurrence pour le même mot-clé → fusionner ou rediriger 301
- **Contenu dupliqué** : Pages produits similaires, URLs avec paramètres — utiliser des canonicals ou `noindex`
- **Liens cassés** : Audit régulier avec Screaming Frog ou Ahrefs
- **Ralentissement du site** : Images non optimisées, trop de requêtes HTTP, JS/CSS non minifié
- **Ignorer le mobile** : Plus de 60% du trafic est mobile — tester Mobile-First
- **Mauvaise gestion des redirections** : Chaînes de redirection (A→B→C), boucles infinies
- **Google Analytics pas configuré** : GA4 obligatoire depuis juillet 2023 (Universal Analytics obsolète)
