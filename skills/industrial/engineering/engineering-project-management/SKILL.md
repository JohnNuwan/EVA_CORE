---
name: engineering-project-management
description: "Gérer des projets d'ingénierie industrielle (EPCm), planifier le chemin critique, maîtriser les risques, et piloter les phases de tests d'acceptation (FAT, SAT) et de mise en service (Commissioning)."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [project-management, epcm, commissioning, fat, sat, scheduling, gantt, risk-management, earned-value, wbs]
  EVA:
    related_skills: [industry40-digital-transformation, systems-engineering-sysml, supply-chain-planning-erp]
---

# Gestion de Projets d'Ingénierie & Commissioning (FAT / SAT)

## Vue d'ensemble

Cette compétence guide la gestion et la coordination de projets complexes d'ingénierie industrielle, typiquement exécutés sous des contrats de type **EPCm** (Engineering, Procurement, Construction Management) ou **EPC** (Engineering, Procurement, Construction). Elle couvre l'intégralité du cycle de vie d'un projet d'ingénierie, depuis les études d'avant-projet jusqu'à la mise en service opérationnelle et la réception définitive par le client.

Les projets d'ingénierie industrielle se caractérisent par :

- Une **multidisciplinarité** : génie civil, mécanique, électricité, automatisme, génie des procédés, CVC, sécurité.
- Des **délais serrés** avec des pénalités de retard contractuelles souvent importantes.
- Des **phases de tests rigoureuses** : FAT (Factory Acceptance Tests), SAT (Site Acceptance Tests), Commissioning, Qualification.
- Une **gestion des risques** intrinsèquement liés aux chantiers, aux interfaces et aux technologies.

Cette compétence intègre les bonnes pratiques du PMI (Project Management Institute) adaptées au contexte de l'ingénierie lourde : planification par chemin critique, management de la valeur acquise (EVM), gestion des réserves (Punch List), et management des risques projet.

Cette compétence est conçue pour être actionnée par l'agent EVA lorsque l'utilisateur exprime un besoin lié à la planification, l'organisation, la gestion des risques ou la mise en service d'un projet d'ingénierie industrielle.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de façon explicite ou implicite de :

- Planifier les étapes d'un projet industriel (conception, approvisionnement, fabrication, montage, essais) et identifier les dépendances temporelles.
- Établir le protocole et la liste de contrôle (checklist) pour des essais **FAT** chez le fournisseur ou **SAT** sur le site final.
- Structurer la phase de **Commissioning** (pré-commissioning statique, commissioning dynamique, mise en route).
- Rédiger ou analyser un registre de risques projet (Risk Register) avec cotation impact/probabilité et plans d'atténuation.
- Suivre l'avancement d'un chantier par la méthode de la **valeur acquise (EVM)** ou suivre la levée des réserves (Punch List).
- Rédiger un rapport de situation hebdomadaire (Weekly Progress Report) ou un dossier de fin de projet.
- Organiser la documentation de projet (plans, procédures, certificats, manuels) pour la remise finale au client.

---

## Cycle de vie d'un projet EPCm

Le cycle de vie d'un projet d'ingénierie industrielle se décompose en phases séquentielles avec des jalons de décision (gates) :

```text
    ┌────────────────────────────────────────────────────────────┐
    │   PHASE 1 : AVANT-PROJET (Feasibility / Front-End)        │
    │   • Étude de faisabilité technique et économique          │
    │   • Définition du périmètre et estimation budgétaire      │
    │   • Analyse des risques préliminaire                      │
    └────────────────────────┬───────────────────────────────────┘
                             │ Gate 1 : Go / No-Go
                             ▼
    ┌────────────────────────────────────────────────────────────┐
    │   PHASE 2 : CONCEPTION DE BASE (Basic Engineering)         │
    │   • Spécifications fonctionnelles (SRS)                   │
    │   • Schémas de procédé (PFD, P&ID)                        │
    │   • Plan de management de projet (PMP)                    │
    └────────────────────────┬───────────────────────────────────┘
                             │ Gate 2 : Validation avant détail
                             ▼
    ┌────────────────────────────────────────────────────────────┐
    │   PHASE 3 : CONCEPTION DÉTAILLÉE (Detail Engineering)     │
    │   • Plans d'exécution (génie civil, mécanique, électrique)│
    │   • Appels d'offres et commandes d'équipements longs délais│
    │   • Rédactions des procédures d'essais                     │
    └────────────────────────┬───────────────────────────────────┘
                             │ Gate 3 : Lancement fabrication
                             ▼
    ┌────────────────────────────────────────────────────────────┐
    │   PHASE 4 : FABRICATION & CONSTRUCTION                    │
    │   • Fabrication des équipements en usine                  │
    │   • Génie civil (terrassement, fondations, dalles)        │
    │   • Montage mécanique et électrique sur site              │
    └────────────────────────┬───────────────────────────────────┘
                             │ Gate 4 : Pré-commissioning
                             ▼
    ┌────────────────────────────────────────────────────────────┐
    │   PHASE 5 : ESSAIS & MISE EN SERVICE                     │
    │   • FAT (usine) → SAT (site) → Commissioning → Mise en route│
    │   • Qualification / Validation                           │
    │   • Formation des opérateurs                              │
    └────────────────────────┬───────────────────────────────────┘
                             │ Gate 5 : Réception provisoire
                             ▼
    ┌────────────────────────────────────────────────────────────┐
    │   PHASE 6 : CLÔTURE (Close-out)                          │
    │   • Levée des réserves finales (Punch List)               │
    │   • Remise des dossiers (As-Built, manuels, certificats)   │
    │   • Retour d'expérience (REX)                             │
    └────────────────────────────────────────────────────────────┘
```

---

## Planification et contrôle des délais

### Work Breakdown Structure (WBS)

La WBS (Structure de Découpage du Projet) décompose le projet en lots de travail livrables, organisés par discipline et par phase :

```text
PROJET : Ligne de conditionnement automatique
├── 1. Génie civil
│   ├── 1.1 Terrassement et fondations
│   └── 1.2 Dalle béton et réservation
├── 2. Mécanique
│   ├── 2.1 Convoyeurs (fabrication / montage)
│   ├── 2.2 Postes d'assemblage
│   └── 2.3 Robot de palettisation
├── 3. Électricité
│   ├── 3.1 Armoires générales (TGBT / distribution)
│   ├── 3.2 Câblage et chemins de câbles
│   └── 3.3 Éclairage et prises
├── 4. Automatisme
│   ├── 4.1 API et architecture réseau
│   ├── 4.2 Développement programme automate
│   └── 4.3 Supervision (SCADA / IHM)
├── 5. Essais et mise en service
│   ├── 5.1 FAT (Factory Acceptance Tests)
│   ├── 5.2 SAT (Site Acceptance Tests)
│   └── 5.3 Commissioning et mise en route
└── 6. Management de projet
    ├── 6.1 Coordination et réunions
    ├── 6.2 Documentation
    └── 6.3 Formation
```

### Le chemin critique (Méthode PERT / CPM)

Le **chemin critique** est la séquence de tâches qui détermine la durée totale minimale du projet. Tout retard sur une tâche du chemin critique retarde directement la date de livraison finale.

**Comment identifier le chemin critique :**

1. Pour chaque tâche, définir :
   - **Durée** ($D$)
   - **Date au plus tôt de début** ($ES$) et **de fin** ($EF$) — *Forward Pass*
   - **Date au plus tard de début** ($LS$) et **de fin** ($LF$) — *Backward Pass*
2. Calculer la **marge totale** ($MT$) : $MT = LS - ES = LF - EF$
3. Le chemin critique est la suite de tâches pour lesquelles $MT = 0$.

**Exemple de calcul de chemin critique :**

```text
Tâche A (5 j) ──► Tâche C (8 j) ──► Tâche F (6 j) ──► Fin
   │                                ▲
   │                                │
   └──► Tâche B (3 j) ──► Tâche D (4 j)
                           │
                           ▼
                     Tâche E (2 j) ──┘
```

Si A-C-F est le chemin le plus long (5+8+6 = 19 jours), c'est le chemin critique. Toute réduction de la durée du projet doit porter sur A, C ou F. Les autres tâches (B, D, E) ont une marge.

### Lissage de ressources (Resource Leveling)

Lorsque la charge de travail d'une ressource (ex : équipe de câbleurs) dépasse sa capacité sur une période donnée, le lissage de ressources décale les tâches non critiques dans leur marge pour étaler la charge, sans modifier la durée totale du projet.

**Indicateurs de suivi planning :**

| Indicateur | Formule | Cible |
|:-----------|:--------|:------|
| Taux d'avancement global | $\frac{\text{Tâches terminées}}{\text{Tâches totales}}$ | — |
| Dérive calendaire | $Date_{prévue} - Date_{réelle}$ | $\le 2$ semaines |
| Coefficient de chargement ressource | $\frac{\text{Charge allouée}}{\text{Capacité disponible}}$ | $< 90\%$ |

---

## Gestion des risques projet

Le management des risques projet identifie, évalue et traite les incertitudes pouvant affecter les objectifs (coût, délais, qualité, sécurité).

### Matrice de cotation des risques

| Probabilité | Très faible (1) | Faible (2) | Moyenne (3) | Élevée (4) | Très élevée (5) |
|:-----------|:---------------|:----------|:-----------|:----------|:---------------|
| **Très élevé (5)** | 5 | 10 | 15 | **20** | **25** |
| **Élevé (4)** | 4 | 8 | 12 | **16** | **20** |
| **Moyen (3)** | 3 | 6 | 9 | 12 | 15 |
| **Faible (2)** | 2 | 4 | 6 | 8 | 10 |
| **Très faible (1)** | 1 | 2 | 3 | 4 | 5 |

- **1 – 5** : Risque faible — Accepté, suivi simple.
- **6 – 14** : Risque moyen — Plan d'atténuation défini.
- **15 – 25** : Risque élevé — Action immédiate requise, comité de pilotage.

### Exemple de registre des risques (Risk Register)

| ID | Description | Cause | Prob. | Impact | Niveau | Action d'atténuation | Responsable | Échéance |
|:---|:-----------|:------|:----|:------|:------|:--------------------|:-----------|:--------|
| R-001 | Retard de livraison du robot de palettisation | Dépendance fournisseur unique, délai constructeur 16 semaines | 3 | 5 | 15 | Commande anticipée (avant validation détail); clause de pénalité dans le contrat | Chef de projet achats | J+2 semaines |
| R-002 | Non-conformité électrique lors du SAT | Différence entre norme française NF C 15-100 et norme constructeur allemand | 3 | 3 | 9 | Audit de conformité mi-montage; mise à disposition d'un bureau de contrôle | Responsable électricité | J+8 semaines |
| R-003 | Grève des monteurs en période de commissioning | Contexte social tendu sur la zone industrielle | 2 | 4 | 8 | Identifier une entreprise de sous-traitance de repli; provisions pour heures sup' | Chef de projet chantier | J+10 semaines |

---

## Les phases de tests et de mise en service

Le phasage des essais est le cœur de la validation d'une installation industrielle. Chaque phase possède un objectif, un protocole et des critères d'acceptation spécifiques.

### 1. FAT — Factory Acceptance Tests

**Où :** Chez le constructeur / intégrateur.
**Quand :** Avant expédition des équipements.
**Objectif :** Vérifier la conformité de fabrication, le fonctionnement à blanc des automatismes, et la documentation associée.

**Contenu typique d'un protocole FAT :**

| Domaine | Tests |
|:--------|:------|
| Mécanique | Vérification dimensionnelle (plan de montage), alignement, jeu mécanique, serrage |
| Électricité | Tests de continuité, isolement (mégaohmmètre), serrage des connexions |
| Automatisme | Test des E/S (entrées/sorties TOR et analogiques), test du programme automate en simulation, test des boucles de régulation |
| Sécurité | Test des arrêts d'urgence, des verrouillages de portes, des circuits de sécurité (reliability : catégorie PL/SIL) |
| Documentation | Notice de montage, schémas électriques à jour, plan de maintenance préventive |

**Critères d'acceptation FAT :**

- Tous les tests critiques (bloquants) sont réussis à 100 %.
- Les tests secondaires sont réussis à $> 90\%$, les échecs documentés dans une **Punch List**.
- La Punch List est signée par le client et le fournisseur, avec des dates de levée fermes.

### 2. SAT — Site Acceptance Tests

**Où :** Sur le site final de l'usine.
**Quand :** Après montage mécanique, câblage et pré-commissioning.
**Objectif :** Valider que l'équipement installé fonctionne correctement dans son environnement réel.

**Contenu typique d'un protocole SAT :**

- Mise sous tension des armoires et vérification des alimentations.
- Test de communication avec les équipements de terrain (capteurs, actionneurs, réseaux).
- Test des E/S réelles (forçage des entrées, vérification des sorties).
- Test à blanc des séquences automatiques sans produit.
- Vérification des alarmes et des seuils de déclenchement.

### 3. Pre-Commissioning (Statique)

Phase intermédiaire entre le montage et la mise sous tension :

| Opération | Description |
|:----------|:-----------|
| Nettoyage des lignes | Lavage, dégraissage, passivation des circuits (chemical cleaning) |
| Épreuve des tuyauteries | Test de pression hydraulique (hydrotest) à $1.43 \times P_{conception}$ |
| Rinçage des circuits | Circulation d'eau déminéralisée pour les circuits thermiques |
| Mégaohmmétrie | Test d'isolement des câbles moteurs et des liaisons électriques |
| Vérification des sens de rotation | Pointage moteur en mode manuel (courte impulsion) |

### 4. Commissioning (Dynamique)

Phase de mise en service active où l'installation est progressivement mise en fonctionnement avec un fluide inerte ou un produit.

**Séquence de commissioning :**

1. **Essais en eau / fluide inerte** : Tester les séquences de production avec de l'eau ou un produit neutre.
2. **Mise en température** : Montée progressive en température des circuits chauds.
3. **Boucles de régulation** : Mise au point des PID des régulateurs (température, pression, débit, niveau).
4. **Essais de production progressive** : Montée en cadence par paliers (10 %, 25 %, 50 %, 75 %, 100 % de la cadence nominale).
5. **Validation des performances (Performance Test)** : Mesure de la cadence maximale, du TRS/OEE, de la consommation énergétique, des rejets.

### 5. Réception et garantie

- **Réception provisoire (PAC)** : Après succès du SAT et début de la période de garantie (souvent 12 mois).
- **Réception définitive (DAC)** : Après levée de toutes les réserves et fin de la période de garantie.

---

## Pièges Courants (Common Pitfalls)

### 1. Réaliser des FAT incomplètes pour tenir les délais d'expédition

**Erreur :** Expédier une machine ou une armoire électrique sur le site de l'usine avant d'avoir testé les programmes automates, validé toutes les fonctionnalités de sécurité ou terminé les essais de simulation lors de la FAT, sous prétexte de gagner quelques jours sur le planning. En pratique, dépanner un bug logiciel sur un chantier en cours de montage coûte **10 fois plus cher** et prend **3 fois plus de temps** que chez le fournisseur (pas d'outils de développement, interférence avec le montage, absence du spécialiste).

**Correction :** Définir des critères d'acceptation FAT **impératifs** (bloquants) et **secondaires**. N'autoriser l'expédition que si :
- 100 % des critères bloquants sont validés.
- Les critères secondaires non validés sont consignés dans une **Punch List** avec une date de levée ferme et un responsable identifié.
- Une provision financière (généralement 5 à 10 % du montant du contrat) est retenue jusqu'à la levée complète des réserves.

### 2. Absence de procédure d'essais écrite pour le Commissioning

**Erreur :** Démarrer les pompes, injecter de la puissance dans un procédé, ou mettre en température sans guide écrit validé, en se fiant à l'intuition et à l'expérience de l'équipe de mise en route. Cela conduit à des risques d'accidents graves : pompe tournant à sec (destruction des garnitures mécaniques), ouverture d'une vanne sans vérifier le circuit d'arrivée (projection de fluide chaud), séquence automatique non testée (collision mécanique).

**Correction :** Rédiger un **Plan de Commissioning** détaillé contenant :
- Des **fiches d'essais** étape par étape avec les valeurs attendues et les tolérances.
- Les **signatures obligatoires** (intervenant, vérificateur, client) à chaque jalon validé.
- Les **règles de sécurité** (consignation LOTO, périmètre de sécurité, EPI requis).
- Les **procédures d'arrêt d'urgence** et de repli en cas d'anomalie.

### 3. Sous-estimer la gestion des interfaces

**Erreur :** Gérer la conception mécanique, électrique et d'automatisme dans des silos séparés sans réunion de synchronisation régulière. Résultat : les réservations dans le béton ne correspondent pas aux dimensions des équipements, les chemins de câbles sont posés avant que le tracé des tuyauteries ne soit figé, et les plans d'exécution ne sont pas mis à jour après modifications.

**Correction :** Organiser des **réunions d'interface** hebdomadaires avec TOUS les responsables de lots (civil, mécanique, électricité, automatisme). Tenir à jour une **matrice d'interfaces** listant tous les points de liaison entre lots (ex : "Lot A : réservation pour passage de gaine CVC dans dalle R+1" → "Lot CVC : dimension et position de la gaine"). Chaque interface doit avoir un responsable identifié et une date de levée.

### 4. Mauvaise gestion de la documentation et des plans As-Built

**Erreur :** Attendre la fin du projet pour rassembler les plans et les documents, en partant du principe que "les plans d'exécution sont déjà à jour". En réalité, les modifications de chantier (field changes) ne sont pas reportées sur les plans, qui deviennent obsolètes. À la fin du projet, le client reçoit des plans "As-Built" qui ne reflètent pas l'installation réelle, rendant la maintenance dangereuse (mauvais schéma électrique, tracé de tuyauterie erroné).

**Correction :** Mettre en place un processus de **documentation continue** :
- Toute modification de chantier donne lieu à un **Field Change Request (FCR)** signé par le client et l'ingénieur.
- Le FCR est immédiatement reporté sur les plans via un marquage "Rév. X — As-Built".
- Un **responsable documentation** unique collecte, indexe et archive tous les documents dans un système de gestion documentaire (GED) partagé.
- Un **dossier d'ouvrage exécuté (DOE)** complet est livré avant la réception définitive.

---

## Liste de vérification (Checklist)

- [ ] La WBS (Work Breakdown Structure) définit clairement les livrables de chaque lot (civil, mécanique, électricité, automatisme) avec des responsables identifiés.
- [ ] Le planning (diagramme Gantt) identifie le chemin critique et les marges libres des tâches non critiques.
- [ ] Le protocole de FAT/SAT contient les critères d'acceptation précis, mesurables et documentés (pressions d'épreuve, débits nominaux, temps de réponse, etc.).
- [ ] La Punch List (liste de réserves) est tenue à jour avec l'identification du responsable et de la date limite de levée pour chaque réserve.
- [ ] Les fiches de consignation de sécurité (LOTO — Lock-Out Tag-Out) sont en place et respectées pendant toute la phase de mise en service.
- [ ] Le registre des risques (Risk Register) est mis à jour mensuellement avec cotation (probabilité × impact) et actions d'atténuation.
- [ ] La courbe en S (valeur acquise / EVM) est produite mensuellement pour suivre l'avancement réel vs. budgété.
- [ ] Les réunions d'interface entre lots sont planifiées et tracées (compte rendu, actions, responsables, dates).
- [ ] Les plans As-Built sont mis à jour en continu lors des modifications de chantier (FCR).
- [ ] Un plan de formation des opérateurs et de transfert de compétences est établi avant la mise en route.

