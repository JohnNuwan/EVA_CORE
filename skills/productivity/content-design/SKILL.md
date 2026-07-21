---
name: content-design
description: "Use when designing content for user interfaces, help systems, and documentation — UX writing, plain language, accessibility, microcopy, error messages, and voice & tone."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [content-design, ux-writing, plain-language, accessibility, microcopy, voice-and-tone, design]
    related_skills: [technical-writing, instructional-design, information-architecture]
---

# Content Design

## Overview

Le content design (conception de contenu) est l'art de créer du contenu qui aide l'utilisateur à accomplir une tâche. Contrairement à la rédaction technique qui explique *ce qu'est* quelque chose, le content design se concentre sur *ce que l'utilisateur doit faire* et *ce qu'il doit savoir au moment où il en a besoin*.

## When to Use

- Rédaction de textes d'interface (microcopie, labels, messages d'erreur)
- Conception de systèmes de help in-app (tooltips, empty states, onboarding)
- Révision de contenu existant pour clarté et accessibilité
- Définition d'une charte éditoriale (voice & tone) pour un produit
- Création de contenu centré utilisateur pour flux critiques (erreur, validation, récupération)

## Principes Fondamentaux

### Les 4 Piliers du Content Design

1. **Utile** — Le contenu aide l'utilisateur à compléter sa tâche, pas à « comprendre le produit »
2. **Trouvable** — L'utilisateur trouve le contenu là où il en a besoin (pas dans une FAQ)
3. **Accessible** — Compréhensible par tous, y compris non-natifs et personnes handicapées
4. **Actionnable** — Dit explicitement à l'utilisateur quoi faire et ce qui va se passer

### Plain Language (Langage Clair)

| Au lieu de... | Écrire... |
|---------------|-----------|
| « Utiliser » | « Cliquez », « Saisissez », « Sélectionnez » |
| « Afin de » | « Pour » |
| « Dans l'éventualité où » | « Si » |
| « Le système ne parvient pas à » | « Impossible de » |
| « Les paramètres susmentionnés » | « Ces paramètres » |
| « Veuillez noter que » | Supprimer (le contenu doit être utile sans préambule) |
| Enchaînement de négations | Phrases affirmatives |

### Test de Lisibilité (FKGL)

- Document général : cibler **FKGL 6-8** (niveau collège)
- Documentation technique : cibler **FKGL 8-10**
- Phrases de moins de 20 mots en moyenne
- Un paragraphe = une idée (max 4-5 phrases)

## Voice & Tone

### Voix (permanente)

La voix est la personnalité du produit. Elle ne change pas.

Exemple de charte vocale :
```
Notre voix est :
- Directe : on dit les choses simplement, pas de circonvolutions
- Compétente : on maîtrise le sujet, on n'invente pas
- Humaine : on écrit comme on parle à un collègue
- Honnête : si on ne sait pas, on le dit
```

### Ton (variable selon le contexte)

| Contexte | Ton | Exemple |
|----------|-----|---------|
| Succès | Confiant, positif | « Votre projet a été créé. » |
| Erreur récupérable | Rassurant, actionnable | « Impossible d'enregistrer. Vérifiez votre connexion et réessayez. » |
| Erreur critique | Sérieux, précis | « Vos modifications n'ont pas été sauvegardées. Contactez le support avec le code ERR-3842. » |
| Onboarding | Encourageant, progressif | « Commençons par configurer votre premier projet. » |
| Maintenance planifiée | Neutre, transparent | « Service indisponible le 22 juillet de 02h00 à 04h00 UTC. » |

## Microcopie

### Messages d'Erreur — Template

```
[Titre : conséquence observable] + [Cause si utile] + [Action de résolution]

Mauvais :  « Erreur 500. »
Bon :      « Impossible de charger les données. Le service est momentanément indisponible. Réessayez dans quelques minutes. »
Mauvais :  « Champ obligatoire. »
Bon :      « Veuillez renseigner votre adresse email. »
```

### Boutons et Liens

| Au lieu de... | Écrire... | Pourquoi |
|---------------|-----------|----------|
| « OK » | « Confirmer la suppression » | Décrit l'action, pas un accord vague |
| « Valider » | « Créer le projet » | Prédictif : l'utilisateur sait ce qui va arriver |
| « Envoyer » | « Envoyer le rapport » | Spécifique au contexte |
| « Cliquez ici » | « Consultez le guide complet » | Descriptif pour accessibilité et SEO |

### Empty States (États Vides)

```
[Quoi ?] + [Pourquoi c'est vide] + [Action possible]

Exemple :
« Vous n'avez pas encore de projets.
Créez votre premier projet pour commencer à suivre vos déploiements.
→ Créer un projet »
```

### Confirmation/Annulation

```
Titre : « Supprimer le projet « Projet Alpha » ? »
Description : « Les données seront définitivement perdues. Cette action est irréversible. »
Bouton primaire : « Supprimer » (rouge/danger)
Bouton secondaire : « Annuler »
```

## Accessibilité en Content Design

### WCAG 2.1 — Critères Applicables au Contenu

1. **1.1.1 Contenu non textuel** — Chaque image a un `alt` text descriptif
2. **1.3.1 Info et relations** — Les titres, listes et tableaux sont sémantiquement marqués
3. **1.4.3 Contraste minimal** — Texte sur fond : ratio ≥ 4.5:1 (3:1 pour grand texte)
4. **2.4.4 Destination des liens** — Le texte du lien décrit la destination
5. **3.1.1 Langue de la page** — Attribut `lang` présent
6. **3.3.2 Étiquettes** — Chaque champ a un label explicite

### Écriture Inclusive

- Utiliser « vous » ou « l'utilisateur » (pas « il » comme défaut)
- Éviter les métaphores genrées ou culturellement spécifiques
- Noms de fonctions sans jargon : « Gérer les accès » plutôt que « Permission Master Control »

## Système de Contenu (Content Model)

### Exemple de Modèle de Contenu

```yaml
# Modèle pour un message d'erreur
content_type: error_message
fields:
  - title: string (≤ 60 chars, obligatoire)
  - description: string (≤ 200 chars, obligatoire)
  - cause: string (optionnelle, une phrase)
  - resolution: string (optionnelle, action concrète)
  - error_code: string (optionnelle, pour support)
  - action_label: string (optionnelle, label du bouton)
  - severity: enum [info, warning, critical]
  - component: string (module concerné)
```

## Workflow de Content Design

1. **Recherche** — Analytics, tickets support, interviews utilisateurs
2. **Brief** — Objectif, contexte, contraintes, voix/tone
3. **Écriture** — Première version, test de lisibilité, revue pair
4. **Test** — A/B test, user testing (l'utilisateur comprend-il l'action ?)
5. **Itération** — Ajustement basé sur les retours
6. **Documentation** — Mise à jour du content model et de la charte

## Common Pitfalls

1. **Neutralité excessive.** « Le système n'a pas pu traiter la demande. » → « Le paiement a échoué. » Le contenu doit être spécifique.
2. **Politesse contre clarté.** « Veuillez bien vouloir excuser la gêne occasionnée... » → trop de mots avant l'information. Le respect se montre par la clarté, pas par les formules.
3. **Jargon technique pour les utilisateurs finaux.** « DNS resolution failed » → « Impossible de joindre le site. »
4. **Contenu qui explique sans aider.** « Les projets sont des conteneurs d'environnements » → « Créez un projet pour grouper vos environnements. »
5. **Absence de test.** Un contenu non testé avec de vrais utilisateurs contient toujours au moins une ambiguïté.

## Outils Recommandés

| Besoin | Outil |
|--------|-------|
| Test de lisibilité | Hemingway Editor, Readable |
| Gestion de contenu | Airtable, Contentful, Strapi |
| Charte éditoriale | Frontify, Zeroheight |
| A/B test contenu | Google Optimize, VWO |
| Vérification accessibilité | WAVE, axe DevTools |
| Grammaire et style | LanguageTool, Grammarly, Antidote |

## Verification Checklist

- [ ] Chaque texte répond à la question : « L'utilisateur sait-il quoi faire ? »
- [ ] Phrases ≤ 20 mots en moyenne (FKGL 6-10 selon contexte)
- [ ] Pas de jargon non défini pour le public cible
- [ ] Messages d'erreur suivent le template : [conséquence] + [cause] + [résolution]
- [ ] Liens et boutons décrivent l'action (pas « cliquez ici »)
- [ ] Images et icônes ont des `alt` text descriptifs
- [ ] Voix cohérente dans tout le produit/document
- [ ] Les empty states guident vers la prochaine action
- [ ] Accessibilité : contraste ≥ 4.5:1, labels explicites