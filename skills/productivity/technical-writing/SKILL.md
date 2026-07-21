---
name: technical-writing
description: "Use when writing, reviewing, or structuring technical documentation — style guides, audience analysis, information types, and documentation planning."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [writing, documentation, technical-writing, style, content]
    related_skills: [api-documentation, instructional-design, information-architecture]
---

# Technical Writing

## Overview

Technical writing transforms complex technical concepts into clear, accessible documentation. Ce skill fournit les principes, structures et workflows pour produire une documentation technique professionnelle — qu'il s'agisse de manuels utilisateur, de guides d'installation, de documentation de référence, de procédures internes ou de rapports d'ingénierie.

## When to Use

- L'utilisateur demande de rédiger, restructurer ou auditer un document technique
- Vous devez produire une documentation utilisateur, développeur ou opérateur
- L'utilisateur fournit des notes brutes et demande une mise en forme professionnelle
- Vous auditez une documentation existante pour clarté, complétude ou cohérence
- L'utilisateur a besoin d'un plan de documentation (table des matières, arborescence)

**Ne pas utiliser pour :** la rédaction créative, le copywriting marketing, la génération de prompts (autres skills existent).

## Audience Analysis Matrix

Avant d'écrire, déterminer le public cible selon ces axes :

| Axe | Questions | Implications rédactionnelles |
|-----|-----------|----------------------------|
| **Expertise technique** | Débutant / Intermédiaire / Expert ? | Niveau de jargon, profondeur des explications |
| **Contexte d'utilisation** | Installation / Dépannage / Référence / Apprentissage ? | Structure (procédurale vs conceptuelle) |
| **Support médiatique** | PDF / Web / Terminal / Vidéo ? | Longueur, liens, navigation, illustrations |
| **Urgence** | Documentation temps réel ou de référence ? | Priorité aux étapes critiques, mises en garde |

## Structure de Document Technique

### Types de Documentation

1. **Procédurale** (guides pas-à-pas, tutoriels)
   - Objectif unique, étapes numérotées
   - Chaque instruction = une action vérifiable
   - Notes / Avertissements avant l'étape concernée

2. **Conceptuelle** (explications, glossaires, architectures)
   - Définir les termes avant de les utiliser
   - Diagrammes pour les relations complexes
   - Analogies et comparaisons

3. **Référence** (API, commandes, configurations)
   - Format tabulaire ou fiche structurée
   - Exhaustif (pas « l'essentiel » mais tout)
   - Recherchable — entrées nommées, index

4. **Dépannage** (FAQ, guides d'erreur, runbooks)
   - Symptôme → Cause → Solution
   - Codes d'erreur exacts
   - Arbres de décision pour diagnostics

### Template de Page Technique

```
# Titre (Action + Objet : « Installer le module X »)

## Contexte
Pourquoi cette page existe, prérequis, références croisées.

## {Étapes | Sections | Paramètres}
1. Sous-titre d'étape
   - Action concrète avec retours attendus
   > **Note :** mise en garde contextuelle

## Dépannage
Erreurs fréquentes et leurs résolutions.

## Voir aussi
Liens vers documentation connexe.
```

## Style et Ton

### Principes de Base

1. **Principe de moindre surprise** — le document fait ce que le lecteur attend
2. **Une phrase = une idée** — pas de subordonnées en cascade
3. **Voix active, mode impératif** — « Exécutez la commande » et non « La commande doit être exécutée »
4. **Terminologie cohérente** — un terme = un concept, pas de synonymes dans le même document
5. **Accessibilité** — langage simple, phrases ≤ 25 mots, éviter les acronymes non définis

### Checklist de Qualité

- [ ] Chaque terme technique est défini à sa première occurrence
- [ ] Les instructions sont impératives et vérifiables
- [ ] Aucune référence à des versions non précisées
- [ ] Les avertissements précèdent l'action (pas après)
- [ ] Les entrées de référence sont triées alphabétiquement
- [ ] Les liens sont descriptifs (pas « cliquez ici »)
- [ ] Un glossaire des acronymes est présent si >5 acronymes

## Workflow de Rédaction Technique

1. **Analyse** — Auditoire, objectif, type de doc, contraintes
2. **Plan** — Table des matières, hiérarchie H1→H2→H3, flux de navigation
3. **Rédaction** — Corps brut par sections, sans chercher la perfection
4. **Révision structurelle** — Cohérence du plan, complétude, flux logique
5. **Révision stylistique** — Voix active, terminologie, longueur des phrases
6. **Relecture technique** — Exactitude des commandes, captures, versions
7. **Livraison** — Format final (PDF/MD/HTML), vérification des liens

## Common Pitfalls

1. **Écrire pour soi-même.** Le public n'a pas votre contexte. Faites lire par un novice.
2. **Jargon non défini.** Un acronyme utilisé sans définition exclut le lecteur débutant.
3. **Instructions ambiguës.** « Configurez le système » → quoi, où, comment ? Chaque étape doit être atomique.
4. **Sur-structuration.** Trop de niveaux de titre (H5+) noie l'information. Max 3 niveaux.
5. **Documentation figée.** Un document technique sans date de version ou sans historique de modification devient obsolète sans que personne le sache.

## Outils Recommandés

| Besoin | Outil |
|--------|-------|
| Rédaction structurée | Markdown + frontmatter YAML |
| Diagrammes | Mermaid, Excalidraw (JSON) |
| Validation stylistique | Vale.sh, write-good, proselint |
| Documentation API | OpenAPI/Swagger + Stoplight |
| Collaboration | Git (docs-as-code) |
| Publication | Docusaurus, MkDocs, Sphinx |

## Verification Checklist

- [ ] Le public cible est identifié et le ton adapté
- [ ] Tous les termes techniques sont définis à première occurrence
- [ ] Les instructions sont impératives, atomiques et vérifiables
- [ ] La hiérarchie n'excède pas 3 niveaux de titre
- [ ] Acronymes < 5 : définis dans le texte ; ≥ 5 : glossaire dédié
- [ ] Les avertissements précèdent l'action concernée
- [ ] Liens descriptifs et valides
- [ ] Version / date de dernière révision indiquée