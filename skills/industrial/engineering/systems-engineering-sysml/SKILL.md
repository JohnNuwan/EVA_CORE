---
name: systems-engineering-sysml
description: "Appliquer l'ingénierie des systèmes et la modélisation SysML pour structurer le cycle en V d'un système complexe (analyse fonctionnelle, exigences, architecture logique et physique)."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [systems-engineering, mbse, sysml, architecture, requirements, v-cycle, modeling, capella, cameo]
    related_skills: [industry40-digital-transformation, cad-bom-automation, engineering-project-management]
---

# Ingénierie des Systèmes (MBSE & SysML)

## Vue d'ensemble

Cette compétence guide la mise en œuvre de l'ingénierie système basée sur les modèles (**MBSE — Model-Based Systems Engineering**) pour concevoir, spécifier, valider et documenter des systèmes industriels complexes : lignes de production automatisées, usines complètes, machines spéciales, systèmes mécatroniques, infrastructures de transport.

Le MBSE repose sur l'utilisation d'un **langage de modélisation** commun (SysML — Systems Modeling Language) et d'un **outil de modélisation** (Cameo Systems Modeler, Capella, IBM Rhapsody) pour créer un modèle unique et cohérent du système, reliant :

- Les **exigences** (besoins clients, spécifications techniques, normes)
- Les **fonctions** (analyse fonctionnelle, scénarios d'utilisation)
- L'**architecture logique** (blocs conceptuels, flux échangés)
- L'**architecture physique** (composants réels, allocation des fonctions)
- Les **paramètres** (équations de performance, contraintes dimensionnantes)
- Les **tests et la validation** (liens de vérification, critères d'acceptation)

Cette approche s'oppose à l'ingénierie documentaire traditionnelle (documents Word, tableaux Excel) où la cohérence entre les vues est manuelle et sujette aux erreurs.

Cette compétence est conçue pour être actionnée par l'agent Helios lorsque l'utilisateur exprime un besoin lié à la modélisation système, l'analyse d'exigences, la conception architecturale ou la documentation structurée d'un système industriel.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de façon explicite ou implicite de :

- Structurer le cycle en V d'un projet industriel (conception système → spécifications → intégration → validation → qualification).
- Rédiger, analyser ou structurer des exigences système avec des critères d'acceptation mesurables.
- Concevoir des diagrammes SysML : diagramme d'exigences (`req`), diagramme de définition de blocs (`bdd`), diagramme de blocs internes (`ibd`), diagramme d'états (`stm`), diagramme d'activités (`act`), diagramme séquentiel (`sd`), diagramme paramétrique (`par`).
- Réaliser une analyse fonctionnelle descendante (arbre fonctionnel, FAST, SADT).
- Allouer des fonctions à des composants physiques et assurer la traçabilité tout au long du cycle de vie.
- Préparer les dossiers de spécification technique, de conception détaillée ou de validation d'un système.

---

## Le cycle en V et le MBSE

Le cycle en V structure le développement d'un système en deux branches descendante (conception) et ascendante (intégration/validation) :

```text
                    ┌─────────────────────────────────────────────────────┐
                    │            BESOINS / EXIGENCES CLIENTS             │
                    │                   (Analyse du besoin)              │
                    └───────────────────────┬─────────────────────────────┘
                                            │
                    ┌───────────────────────▼─────────────────────────────┐
                    │         SPÉCIFICATION FONCTIONNELLE SYSTÈME        │
                    │          (Exigences système, cas d'utilisation)      │
                    └───────────────────────┬─────────────────────────────┘
                                            │
                    ┌───────────────────────▼─────────────────────────────┐
                    │         ARCHITECTURE LOGIQUE (Conception)          │
                    │       (Blocs logiques, flux, comportement)          │
                    └───────────────────────┬─────────────────────────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              │                             │                             │
    ┌─────────▼─────────┐         ┌─────────▼─────────┐       ┌─────────▼─────────┐
    │  SOUS-SYSTÈME A   │         │  SOUS-SYSTÈME B   │       │  SOUS-SYSTÈME C   │
    │  (Cahier des       │         │  (Cahier des       │       │  (Cahier des       │
    │   charges métier)  │         │   charges métier)  │       │   charges métier)  │
    └─────────┬─────────┘         └─────────┬─────────┘       └─────────┬─────────┘
              │                             │                             │
    ┌─────────▼─────────┐         ┌─────────▼─────────┐       ┌─────────▼─────────┐
    │  CONCEPTION       │         │  CONCEPTION       │       │  CONCEPTION       │
    │  DÉTAILLÉE        │         │  DÉTAILLÉE        │       │  DÉTAILLÉE        │
    └───────────────────┘         └───────────────────┘       └───────────────────┘
```

La branche montante du V consiste en :

1. **Vérification** : "A-t-on construit le système correctement ?" (test unitaire, intégration, qualification par rapport aux spécifications).
2. **Validation** : "A-t-on construit le bon système ?" (satisfaction des besoins clients, recette, qualification opérationnelle).

---

## Les piliers de SysML

La modélisation SysML s'articule autour de **neuf types de diagrammes** répartis en quatre catégories :

```text
    ┌──────────────────────────────────────────────────────────┐
    │                        EXIGENCES                         │
    │              Requirement Diagram (req)                    │
    │         Définit, structure et trace les exigences         │
    └────────────────────┬─────────────────────────────────────┘
                         │
    ┌────────────────────┼─────────────────────────────────────┐
    │                    │                                      │
    ▼ Comportement       ▼ Structure                   ▼ Paramétrique
    ┌────────────────┐  ┌────────────────────┐  ┌────────────────────┐
    │ COMPORTEMENT   │  │ STRUCTURE          │  │ PARAMÉTRIQUE      │
    │                │  │                    │  │                   │
    │ Use Case (uc)  │  │ Block Definition   │  │ Parametric (par)  │
    │ Activity (act) │  │ Diagram (bdd)      │  │ Équations,        │
    │ Sequence (sd)  │  │ Internal Block     │  │ contraintes       │
    │ State Machine  │  │ Diagram (ibd)      │  │ physiques         │
    │ (stm)          │  │ Package Diagram    │  │                   │
    └────────────────┘  └────────────────────┘  └────────────────────┘
```

### 1. Diagramme d'exigences (req)

Le diagramme `req` structure les exigences sous forme hiérarchique et définit les relations entre elles :

| Relation | Notation SysML | Signification |
|:---------|:--------------|:-------------|
| Dérivation | `deriveReqt` | L'exigence enfant détaille ou raffine l'exigence parente |
| Satisfaction | `satisfy` | Un bloc physique ou une fonction réalise l'exigence |
| Vérification | `verify` | Un cas de test ou une procédure vérifie l'exigence |
| Raffinement | `refine` | Un modèle ou une analyse affine l'exigence |
| Copie | `copy` | L'exigence est recopiée d'un autre contexte |

**Bonnes pratiques pour les exigences :**

- Chaque exigence doit avoir un **identifiant unique** (ex : REQ-SYS-001).
- La description doit être **mesurable** et **testable**. Pas de termes vagues comme "rapide", "sûr", "ergonomique".
- Structure : **Le [système] doit [action] dans [condition] avec [critère de performance]**.
- Exemple : "REQ-SYS-042 — La ligne de conditionnement doit atteindre une cadence nominale de 40 pièces par minute pour un produit de dimensions 150 × 200 × 80 mm."

### 2. Diagramme de définition de blocs (bdd)

Le `bdd` représente la **structure statique** du système :

- **Blocs** : Éléments du système (physiques ou logiques) avec leurs propriétés.
- **Compositions** : Relation *partie-de* (ex : un moteur contient un stator, un rotor, des roulements).
- **Spécialisations** : Relation *est-un-type-de* (ex : un moteur asynchrone est un type de moteur électrique).
- **Multiplicités** : Combien d'instances (1, 2, 0..\*, etc.)

**Exemple de bdd simplifié :**

```text
┌──────────────────────────────┐
│  [Block] Ligne de Production │
│  + propriétés:               │
│    - cadence: pièces/min     │
│    - trs: %                  │
├──────────────────────────────┤
│  Composition (part-of)       │
├──────────────────────────────┤
│ 1 ──► [Block] Convoyeur     │
│ 1 ──► [Block] Poste Assemblage│
│ 1 ──► [Block] Armoire Cde   │
└──────────────────────────────┘
```

### 3. Diagramme de blocs internes (ibd)

Le `ibd` décrit les **flux** (matière, énergie, informations) qui transitent entre les parties internes d'un bloc via des **ports** :

```text
┌─── Ligne de Production ───────────────────────────────────────┐
│                                                                 │
│  ┌──────────┐  Pièce brute  ┌──────────────┐  Pièce usinée    │
│  │ Convoyeur │────────────►│ Poste Assy   │──────────────► ...│
│  │ Entrée    │              │              │                  │
│  └──────────┘              └──────────────┘                  │
│       │                        │                              │
│       │ Signal "pièce prête"   │ Ordre d'actionnement         │
│       ▼                        ▼                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Armoire de Commande                       │  │
│  │        Port : Ethernet/IP, 24VDC                       │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### 4. Diagramme d'états (stm)

Le `stm` modélise les **modes de fonctionnement** du système (ou d'un bloc). Indispensable pour les machines automatisées :

```text
    [Initial] ──► ┌──────────────┐
                   │  ARRÊT       │
                   └──────┬───────┘
                          │ Ordre de marche
                          ▼
                   ┌──────────────┐
            ┌────►│  MARCHE      │◄────┐
            │     │ (Production) │     │ Reprise auto
            │     └──────┬───────┘     │
            │            │ Panne       │
            │            ▼             │
            │     ┌──────────────┐     │
            │     │  PANNE       │─────┘
            │     │ (Arrêt forcé)│
            │     └──────────────┘
            │
            │ Ordre d'arrêt
            ▼
       ┌──────────────┐
       │ ARRÊT        │
       │ (Maintenance) │
       └──────────────┘
```

### 5. Diagramme paramétrique (par)

Le `par` exprime les **contraintes physiques** (équations) liant les propriétés des blocs. Exemple : contrainte de puissance d'un moteur :

$$P_{moteur} = C \cdot \omega$$

$$P_{moteur} \ge \frac{P_{charge}}{\eta_{transmission}}$$

Le diagramme `par` lie ces équations aux propriétés réelles des blocs définis dans le `ibd` ou le `bdd`.

---

## Méthode ARCADIA / Capella

L'approche ARCADIA (Architecture Analysis & Design Integrated Approach), implémentée dans l'outil **Capella**, est une méthode MBSE complète décomposée en cinq niveaux :

1. **Analyse du besoin opérationnel (OA)** : Ce que les utilisateurs veulent faire (sans le système).
2. **Analyse du besoin système (SA)** : Ce que le système doit faire pour les utilisateurs (cas d'utilisation, fonctions système).
3. **Architecture logique (LA)** : Comment le système réalise les fonctions (décomposition logique, flux).
4. **Architecture physique (PA)** : Solution concrète (composants réels, allocation des fonctions logiques).
5. **EPBS (End Product Breakdown Structure)** : Décomposition des produits réalisant l'architecture physique.

---

## Pièges Courants (Common Pitfalls)

### 1. Exigences ambiguës ou invérifiables

**Erreur :** Écrire des exigences subjectives comme "La ligne de production doit être rapide et sûre". Ce type de formulation est inutile car impossible à tester. Une exigence non testable ne pourra jamais être validée, ce qui crée des litiges lors de la recette.

**Correction :** Appliquer la règle SMART (Spécifique, Mesurable, Atteignable, Réaliste, Temporellement défini) :

- "La ligne de production doit avoir une cadence nominale de 40 pièces par minute ± 5 % en régime stabilisé [REQ-002]."
- "La ligne de production doit être conforme à la Directive Machine 2006/42/CE et à la norme IEC 62061 (sécurité fonctionnelle) [REQ-003]."

### 2. Diagrammes de blocs internes (ibd) déconnectés du monde réel

**Erreur :** Relier des ports SysML sans spécifier la nature et le type des flux échangés. Par exemple, connecter le port d'un moteur à une vanne sans préciser s'il s'agit d'un signal électrique 24 VDC, d'une consigne analogique 4-20 mA, d'un bus de terrain Profinet ou d'un flux d'énergie mécanique (couple × vitesse).

**Correction :** Définir rigoureusement les **Flow Properties** sur chaque port :

| Port | Type de flux | Nature | Unité | Protocole |
|:----|:-------------|:-------|:------|:----------|
| Moteur.entrée_énergie | Énergie électrique | Triphasé 400 V | kW | — |
| Moteur.sortie_vitesse | Information | Mesure codeur | tr/min | SSI |
| Vanne.consigne | Information | Signal analogique | 4-20 mA | — |
| Vanne.position | Information | Feedback | 0-100 % | HART |

### 3. Surcharge de modélisation sans valeur ajoutée

**Erreur :** Modéliser tous les détails du système au même niveau de granularité, même ceux qui n'ont aucun impact sur la conception, la validation ou l'intégration. Le modèle devient illisible, impossible à maintenir, et sa valeur ajoutée par rapport à des schémas simples s'évapore.

**Correction :** Appliquer le principe de **sélectivité** : ne modéliser en SysML que ce qui apporte de la valeur à la traçabilité des exigences, à la validation des interfaces ou à la compréhension architecturale. Les détails d'implémentation pure (câblage interne d'une armoire, routine logicielle) restent dans les outils métiers (EPLAN, code source). Chaque élément du modèle doit répondre à la question : "À quelle décision de conception ou de validation ce modèle contribue-t-il ?"

### 4. Absence de réconciliation entre vues fonctionnelle et physique

**Erreur :** Définir l'analyse fonctionnelle et l'architecture physique dans des documents (ou des outils) séparés, sans lien systématique. Après une modification de l'architecture physique (ex : remplacement d'un vérin pneumatique par un moteur électrique), personne ne met à jour l'analyse fonctionnelle associée, et le lien fonction-solution se perd.

**Correction :** Utiliser les relations de traçabilité SysML (`satisfy`, `allocate`) pour lier chaque fonction du diagramme d'activités (`act`) au bloc physique qui la réalise dans le `bdd`. Lorsqu'un composant change, l'outil MBSE signale les fonctions impactées. Maintenir une matrice de traçabilité fonctions ↔ composants à chaque jalon de conception.

---

## Liste de vérification (Checklist)

- [ ] Chaque exigence possède un identifiant unique et des critères d'acceptation quantifiables et testables (SMART).
- [ ] La traçabilité est établie : chaque bloc physique du `bdd` satisfait au moins une exigence du `req`.
- [ ] Les diagrammes de comportement (activités, états) sont cohérents avec les diagrammes de structure (les actions utilisent les fonctions réelles des blocs).
- [ ] Les flux dans les diagrammes `ibd` sont typés : nature (énergie, matière, signal), unité, protocole.
- [ ] Les modes de fonctionnement du système sont modélisés par un diagramme d'états (`stm`) couvrant marche, arrêt, panne et maintenance.
- [ ] Les protocoles de tests de vérification sont explicitement liés aux exigences correspondantes (relation `verify`).
- [ ] Une revue de conception (PDR/CDR) valide la complétude et la cohérence du modèle à chaque jalon.
- [ ] Le modèle SysML est versionné et accessible par l'équipe projet (outil de modélisation partagé).
- [ ] Les contraintes dimensionnantes (vitesse, couple, énergie) sont modélisées dans un diagramme paramétrique (`par`).
- [ ] Une matrice de couverture exigences ↔ tests est éditée avant chaque phase de qualification.

