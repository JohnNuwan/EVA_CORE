---
name: information-architecture
description: "Use when designing or auditing information architecture for documentation systems — content hierarchy, navigation, labeling, taxonomy, findability, and user journeys."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [information-architecture, ia, navigation, taxonomy, findability, content-hierarchy]
    related_skills: [knowledge-management, documentation-systems, technical-writing]
---

# Information Architecture

## Overview

L'information architecture (IA) est la discipline qui organise et structure l'information pour maximiser sa trouvabilité et sa compréhensibilité. Contrairement au KM qui se concentre sur le contenu, l'IA se concentre sur les **chemins d'accès** au contenu : navigation, catégories, étiquettes, index et relations.

## When to Use

- L'utilisateur demande de structurer un site de documentation, un wiki ou un portail
- Vous devez auditer la navigation ou l'organisation d'un système existant
- Conception d'une taxonomie ou d'un système de catégories
- Définition d'un plan de site ou d'une arborescence de contenu
- Optimisation de la découvrabilité (search, cross-references, index)

## Les 4 Composantes de l'IA (Morville & Rosenfeld)

### 1. Systèmes d'Organisation

Comment le contenu est catégorisé et structuré.

| Schéma | Description | Exemple |
|--------|-------------|---------|
| **Hiérarchique** | Arbre de catégories et sous-catégories | Documentation technique par module |
| **Séquentiel** | Pas-à-pas linéaire | Tutoriel, guide d'installation |
| **Matriciel** | Croisement de deux axes | Docs par rôle × par tâche |
| **Facetté** | Filtres multi-dimensions | Catalogue de composants (par type, fabricant, tension) |

### 2. Systèmes de Navigation

Comment l'utilisateur se déplace dans l'information.

```
Navigation Globale (toujours visible)
├── Barre de navigation principale
├── Pied de page avec liens clés
└── Fil d'Ariane (breadcrumb)

Navigation Locale (contextuelle)
├── Table des matières de la page
├── Sections précédente/suivante
└── Pages soeurs dans la même catégorie

Navigation Transversale
├── Liens connexes / Voir aussi
├── Tags et catégories
└── Index alphabétique
```

### 3. Systèmes d'Étiquettage (Labeling)

Comment les concepts sont nommés.

**Règles d'étiquettage :**
- **Précision** — Une étiquette ne désigne qu'un seul groupe de contenu
- **Prédictibilité** — L'utilisateur sait ce qu'il trouvera derrière
- **Consistance** — Même étiquette pour même concept partout
- **Brièveté** — 1-3 mots, éviter le jargon interne
- **Audience** — Terminologie du public, pas de l'organisation

### 4. Systèmes de Recherche

Comment l'utilisateur trouve par query.

- Synonymes et alias pour les termes de recherche courants
- Filtres facettés (type, date, auteur, tags)
- Autocomplete et suggestions de recherche
- Tolérance aux fautes d'orthographe

## Architecture Hiérarchique

### Règles de Structure Arborescente

1. **Profondeur max 4 niveaux** — Au-delà, l'utilisateur se perd. 3 niveaux est optimal.
2. **Largeur 5-9 items par niveau** — Loi de Miller : le cerveau humain gère 7±2 options.
3. **Pas de catégorie vide** — Si une catégorie n'a pas de contenu, ne pas la créer.
4. **Règle du « un pas »** — Le contenu le plus important est accessible en ≤ 2 clics depuis l'accueil.
5. **Pas de croisement** — Un contenu n'appartient qu'à une seule catégorie principale (les tags gèrent le multi-appartenance).

### Test de l'Arbre (Tree Testing)

Pour valider une arborescence, utiliser le protocole :
1. Donner une tâche à un utilisateur : « Trouvez la procédure d'installation »
2. L'utilisateur navigue dans l'arbre sans voir le contenu
3. Mesurer : taux de succès, temps, chemin emprunté
4. Cible : > 80% de succès direct (sans rebroussement)

## Card Sorting pour la Catégorisation

### Méthode Ouverte
L'utilisateur crée ses propres catégories. Utilisé pour comprendre le **modèle mental** du public.

1. Préparer 30-60 cartes (concepts à organiser)
2. L'utilisateur groupe les cartes et nomme chaque groupe
3. Analyser : fréquence des regroupements, noms de catégories communs
4. Outils : OptimalSort, Miro, cartes physiques

### Méthode Fermée
L'utilisateur trie dans des catégories prédéfinies. Utilisé pour valider une taxonomie existante.

- Cible : > 70% d'accord inter-évaluateurs (Cohen's κ ≥ 0.7)
- Les items avec < 50% d'accord doivent être re-catégorisés ou renommés

## Taxonomie et Métadonnées

### Modèle de Métadonnées pour Documentation

```yaml
---
title: "Titre de la page"
description: "Résumé pour search et preview"
type: concept | tutorial | reference | troubleshooting | changelog
audience: developer | operator | end-user | admin
product: [produit A, produit B]  # Multi-produit
lifecycle: stable | beta | deprecated
difficulty: beginner | intermediate | advanced
---
```

### Polyhiérarchie avec Tags

Les tags permettent un classement multi-dimensions que l'arbre ne peut pas offrir :

- `#sécurité` — s'applique à des pages dans plusieurs catégories
- `#migration` — traverse les versions et les produits
- `#déprécié` — tout contenu retiré mais conservé pour référence

## Navigation — Patterns Éprouvés

### Fil d'Ariane (Breadcrumb)

```
Accueil > Documentation > API > Authentification
```

Format : chaque segment est un lien vers la catégorie parente. Le dernier segment est la page courante (non cliquable).

### Navigation Contextuelle

Dans une page de tutoriel :
```
[← Prérequis]  [↑ Index]  [Exercice suivant →]
```

### Index Alphabétique

Pour les glossaires, paramètres, commandes — entrées triées alphabétiquement avec lien direct vers la section.

## Audit d'IA

### Méthode d'audit en 5 étapes :

1. **Inventaire** — Lister toutes les pages, leur URL, titre, type, date
2. **Graphe des liens** — Extraire les liens entrants et sortants de chaque page
3. **Identifier les orphelines** — Pages sans liens entrants et/ou sortants
4. **Analyser la profondeur** — Combien de clics depuis l'accueil ?
5. **Sondage utilisateur** — « Avez-vous trouvé ce que vous cherchiez ? » sur les pages clés

### Métriques d'IA

| Métrique | Cible | Comment mesurer |
|----------|-------|-----------------|
| Succès de navigation | > 80% | Tree testing |
| Profondeur moyenne | ≤ 3 clics | Analytics |
| Pages orphelines | < 5% | Crawl interne |
| Rebond sur recherche | < 40% | Search analytics |
| Clics sur navigation | > clics sur search | Analytics |
| Taux de sortie navigation | < 20% | Analytics |

## Common Pitfalls

1. **Reflet de l'org chart.** Organiser la documentation comme l'organigramme de l'entreprise, pas comme le modèle mental de l'utilisateur. Faire du card sorting pour éviter cela.
2. **Profondeur excessive.** 5+ niveaux de hiérarchie = perte de l'utilisateur. Aplatir ou ajouter des portes d'entrée transversales.
3. **Multi-catégorisation.** Mettre une page dans plusieurs catégories simultanément crée de la confusion. Utiliser les tags pour la multi-appartenance.
4. **Labels internes.** « Procédures de décommissionnement des assets de l'infrastructure réseau sous-jacente » → l'utilisateur ne cherche pas ça. « Supprimer un serveur » est plus naturel.
5. **Architecture sans test.** Concevoir l'IA sans tree testing, c'est livrer une carte que vous seul savez lire.

## Outils Recommandés

| Besoin | Outil |
|--------|-------|
| Tree testing | Treejack, UserZoom |
| Card sorting | OptimalSort, Miro |
| Sitemap visuel | gliffy, draw.io, Mermaid mindmap |
| Audit IA | Screaming Frog, Sitebulb |
| Analytics search | Google Search Console, Algolia Analytics |
| Graphe de liens | Obsidian Graph View, Gephi |

## Verification Checklist

- [ ] Arborescence ≤ 4 niveaux, testée en tree testing (> 80% succès)
- [ ] Chaque page a un type, une audience et un lifecycle définis
- [ ] Pas de catégorie vide dans la navigation
- [ ] Pas de page orpheline (sans lien entrant) pour les pages clés
- [ ] Fil d'Ariane (breadcrumb) sur chaque page
- [ ] Labels testés avec le public (consistent, prédictibles, ≤ 3 mots)
- [ ] Tags disponibles pour la polyhiérarchie (pas de duplication dans l'arbre)
- [ ] Profondeur ≤ 3 clics depuis l'accueil pour le contenu critique