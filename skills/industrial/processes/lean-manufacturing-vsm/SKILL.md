---
name: lean-manufacturing-vsm
description: "Déployer les outils du Lean Manufacturing en milieu industriel (5S, SMED, Kaizen, Kanban), lisser les flux de production (Heijunka), et cartographier les chaînes de valeur (VSM) pour éliminer les gaspillages et maximiser la valeur ajoutée."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [lean, lean-manufacturing, vsm, value-stream-mapping, smed, 5s, kaizen, kanban, heijunka, muda, flow-management, continuous-improvement, six-sigma, just-in-time, jidoka]
  EVA:
    related_skills: [industrial-flow-simulation, supply-chain-planning-erp, oee-performance, industrial-maintenance-reliability]
    difficulty: intermediate
    industry_sectors: [manufacturing, automotive, aerospace, electronics, food-beverage, pharmaceutical, chemical]
---

# Lean Manufacturing & Cartographie des Flux de Valeur (VSM)

## Vue d'ensemble

Cette compétence guide l'amélioration continue des processus industriels par l'élimination systématique des gaspillages (Mudas) en utilisant les outils et la philosophie du **Lean Manufacturing**. Elle couvre la cartographie des flux de valeur (**VSM - Value Stream Mapping**), la réduction des temps de changement de série (**SMED**), le rangement et l'organisation des postes de travail (**5S**), le lissage de la production (**Heijunka**), et la gestion visuelle des flux par cartes **Kanban**.

### Les 7 (+1) Gaspillages (Mudas)

Le Lean identifie 7 catégories classiques de gaspillage, plus une 8ème ajoutée par les réflexions modernes :

| # | Muda (Gaspillage) | Exemple industriel | Impact typique |
|:---:|:---|---|:---:|
| 1 | **Surproduction** | Fabriquer plus que la demande client ou produire en avance | Stock, trésorerie immobilisée |
| 2 | **Attentes** | Opérateur qui attend la matière première ou une machine | Main d'œuvre improductive |
| 3 | **Transports inutiles** | Déplacement de pièces entre ateliers éloignés | Manutention, risque qualité |
| 4 | **Surtraitement** | Contrôle qualité excessif ou finition inutile | Coût opératoire inutile |
| 5 | **Stocks** | En-cours (WIP) trop importants entre les étapes | Surface, obsolescence, trésorerie |
| 6 | **Mouvements** | Opérateur qui marche ou se baisse pour chercher des outils | Temps non productif, TMS |
| 7 | **Défauts / Rebuts** | Pièces non conformes, retouches | Coût qualité, perte matière |
| 8 | **Sous-utilisation des compétences** | Opérateur qualifié qui fait des tâches simples | Démotivation, potentiel perdu |

### Contexte : Pourquoi le Lean en Industrie ?

Le Lean Manufacturing, né du Système de Production Toyota (SPT / TPS), a prouvé son efficacité dans tous les secteurs industriels. Les bénéfices typiques d'une démarche Lean structurée sont :

- **Réduction des délais** (Lead Time) de 30 à 70 %.
- **Gain de productivité** de 20 à 40 %.
- **Réduction des stocks** de 30 à 60 %.
- **Amélioration de la qualité** (réduction des rebuts de 50 à 80 %).
- **Libération d'espace** de production de 15 à 30 %.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- **Dessiner ou analyser une cartographie VSM** "État actuel" pour identifier le temps de défilement (Lead Time) et le temps à valeur ajoutée d'une famille de produits.
- **Définir un VSM "État futur"** cible avec des actions d'amélioration et des gains quantifiés.
- **Mener un chantier SMED** (Single Minute Exchange of Die) pour réduire le temps d'arrêt lors d'un changement de série ou de référence sur une ligne de production.
- **Structurer un plan d'action 5S** complet (Seiri, Seiton, Seiso, Seiketsu, Shitsuke) pour un atelier, un magasin ou un poste de travail.
- **Dimensionner des boucles de régulation de flux** par cartes Kanban (Kanban de production, Kanban de transfert).
- **Animer des ateliers Kaizen** (amélioration continue) de 2 à 5 jours sur un périmètre défini.

**Ne pas utiliser pour :**
- Les analyses financières ou les calculs de rentabilité d'investissement (ROI) en dehors du contexte Lean.

## La Cartographie VSM (Value Stream Mapping)

### Symboles VSM Standard

La VSM représente graphiquement le flux d'informations et le flux physique de matières du fournisseur au client, en utilisant des symboles normalisés :

```text
Symboles clés de la VSM :

  [Procédé]      Boîte de processus / étape de fabrication
  [  =>   ]      Flux poussé (push)
  [  =>▷  ]      Flux tiré (pull / Kanban)
  [ Fourn.]      Source externe (fournisseur, client)
  [  /\   ]      Stock / en-cours (triangle d'inventaire)
  [ ───►  ]      Flux d'informations (électronique)
  [ ~~~►  ]      Flux d'informations (manuel / papier)
  [  ⚡   ]      Opérateur
  [  ■   ]      Données / boîte de données de processus
  [  ──── ]      Ligne de temps (Lead Time / VA Time)
```

### Exemple de VSM Industrielle

```text
    [ Client ] ◄───── Prévisions & Commandes ─────► [ Fournisseur ]
        │                                                │
        ▼                                                ▼
   ┌─────────┐    Transport     ┌──────────┐   Transport   ┌──────────┐
   │ Étape 1 │ ───────────────► │ Étape 2  │ ────────────► │ Expéd.  │
   │Découpage│     WIP 500 pcs  │Assemblage │   PF 300 pcs  │          │
   └─────────┘                  └──────────┘               └──────────┘
   ■ C/O: 45 min               ■ C/O: 15 min
   ■ CT: 2 sec                 ■ CT: 5 sec
   ■ Dispon: 85%               ■ Dispon: 92%
   ■ 1 opérateur               ■ 2 opérateurs

   Ligne de temps (Lead Time / VA) :
   0 ── 2s ──┐───────────────── 3 jrs ────┐─── 5s ───┐────── 5 jrs ────►
              (VA: 2s)        (NVA: stock)  (VA: 5s)  (NVA: stock PF)

   Temps total : Lead Time = 8 jours | Temps VA total = 7 secondes
   Efficacité du flux : 7 s / (8 j × 86400 s/j) = 0,001 %
```

**Lecture de l'exemple :** Le produit passe 8 jours dans le système pour seulement 7 secondes de transformation à valeur ajoutée. L'objectif du Lean est de réduire le Lead Time en s'attaquant aux stocks et aux temps d'attente (Non Valeur Ajoutée), plutôt qu'en cherchant uniquement à accélérer les temps de cycle machine (déjà très courts).

### Les 7 Questions Clés de la VSM

Pour chaque étape du flux, poser systématiquement ces questions :
1. Cette étape crée-t-elle de la valeur pour le client ?
2. Le flux est-il continu ou y a-t-il des ruptures (stocks entre étapes) ?
3. Le processus est-il contrôlé par la demande client (pull) ou par un programme (push) ?
4. Les temps de changement de série (C/O) sont-ils un goulot ?
5. La disponibilité machine est-elle suffisante ?
6. Les opérateurs sont-ils correctement formés et impliqués ?
7. Quels sont les gaspillages visibles (attentes, mouvements, défauts) ?

## Méthodologie SMED (Changement de Série Rapide)

Le SMED (Single Minute Exchange of Die) vise à réduire le temps d'arrêt de production lors d'un changement d'outillage ou de série. L'objectif est d'atteindre un temps de changement < 10 minutes (d'où le "Single Minute").

### Les 4 Étapes du SMED

| Étape | Description | Exemple concret | Gain potentiel |
|:---|---|:---:|:---:|
| 1. **Observation** | Chronométrer et filmer l'intégralité du changement actuel | 45 min de changement de moule | – |
| 2. **Séparation** | Distinguer les tâches internes (machine arrêtée) des tâches externes (machine en marche) | Identifier que la recherche d'outils (8 min) peut être faite avant l'arrêt | 20 – 30 % |
| 3. **Conversion** | Transformer le maximum de tâches internes en tâches externes | Préchauffer le moule pendant que la machine produit encore | 30 – 50 % |
| 4. **Rationalisation** | Simplifier toutes les tâches restantes | Fixations rapides (1/4 de tour au lieu de 8 vis), repères de position, outils pré-réglés | 10 – 30 % |

### Outils SMED Concrets

| Outil | Description | Exemple d'application |
|:---|---|:---|
| **Check-list de préparation** | Vérifier que tous les outils, pièces et documents sont prêts avant l'arrêt | Liste plastifiée avec photo |
| **Tableau de visualisation** | Afficher le déroulé du changement minute par minute | Tableau blanc + feutres de couleur |
| **Standard de changement** | Documenter la meilleure séquence connue (vidéo + fiche A3) | Affiche au poste de travail |
| **Poka-Yoke (détrompeur)** | Éviter les erreurs de montage (ex : formes asymétriques, repères de position) | Guide d'insertion usiné |

## Déploiement des 5S

| Étape japonaise | Étape française | Action concrète |
|:---|---:|:---|
| **Seiri** (整理) | **Débarrasser** | Trier : ne garder au poste que ce qui est nécessaire pour l'activité du jour. Éliminer les outils cassés, les pièces obsolètes, le matériel en trop. |
| **Seiton** (整頓) | **Ordonner** | Ranger chaque chose à sa place. Créer des emplacements dédiés (ombres d'outils, bacs étiquetés). Principe visuel : "tout est visible en un coup d'œil". |
| **Seiso** (清掃) | **Nettoyer** | Nettoyer le poste de travail en profondeur. Le nettoyage est une inspection : détecter les anomalies (fuites, fissures, jeux anormaux). |
| **Seiketsu** (清潔) | **Standardiser** | Créer des standards visuels : photos "Avant / Après", fiches de poste, signalétique au sol, code couleur. Définir des fréquences de nettoyage et de vérification. |
| **Shitsuke** (躾) | **Pérenniser** | Auditer régulièrement (audit 5S hebdomadaire avec grille de notation). Impliquer la hiérarchie dans les visites terrain (gemba walks). |

### Grille d'Audit 5S (notation sur 4 points par S)

| Critère | Note 0 | Note 1 | Note 2 | Note 3 | Note 4 |
|:---|---|---|:---:|:---:|:---:|
| Seiri (Débarrasser) | Objets inutiles partout | Objets inutiles identifiés | > 50 % éliminés | > 90 % éliminés | Poste 100 % utile |
| Seiton (Ordonner) | Aucun rangement | Zones définies | 50 % des outils ont un emplacement fixe | 90 % ont une ombre / étiquette | Chaque chose à sa place |
| Seiso (Nettoyer) | Poste sale, déchets | Nettoyage quotidien | Équipement propre | Anomalies détectées pendant nettoyage | Maintenance autonome active |
| Seiketsu (Standardiser) | Aucun standard | Standards écrits | Standards affichés | Standards visuels (photos) | Standards connus de tous |
| Shitsuke (Pérenniser) | Aucun audit | Audit mensuel | Audit et affichage | Score > 80 % | Amélioration continue active |

## Système Kanban (Flux Tiré)

Le Kanban est un système d'information visuelle qui autorise la production par l'aval (flux tiré).

### Types de Kanban

| Type | Description | Signal | Utilisation typique |
|:---|---|---|:---:|
| **Kanban de production** | Autorise la fabrication d'un lot | Carte physique ou signal électronique | Atelier, fabrication interne |
| **Kanban de transfert** | Autorise le déplacement entre deux postes | Carte ou bac vide | Circulation inter-îlots |
| **Kanban électronique (e-Kanban)** | Signal numérique automatisé | EDI, API, message ERP | Flux synchronisés ERP / WMS |
| **Signal Kanban (tri-card)** | 3 cartes par contenant : "À produire", "En production", "Livré" | Cartes de couleur | Production par lots |

### Calcul d'un Kanban de Production

$$N_{Kanban} = \frac{D_{moy} \times T_R \times (1 + SS)}{Q_{contenant}}$$

Où :
- $D_{moy}$ : Demande moyenne sur la période.
- $T_R$ : Temps de réapprovisionnement (fabrication + transfert).
- $SS$ : Coefficient de sécurité (10 à 30 % selon la variabilité).
- $Q_{contenant}$ : Quantité standard par contenant / carte.

**Exemple statistique :** Demande = 200 pièces/jour, TR = 0,5 jour, SS = 20 %, Q = 50 pièces.
$$N = \frac{200 \times 0,5 \times 1,2}{50} = 2,4 \text{ → soit 3 Kanban}$$

## Pièges Courants (Common Pitfalls)

1. **Appliquer les 5S uniquement comme une opération de nettoyage ponctuelle :**
   - *Erreur :* Nettoyer et ranger un poste de travail le vendredi après-midi, puis ne pas définir de standards visuels ni d'audits. En deux semaines, le poste revient à son état initial de désordre.
   - *Correction :* Mettre en œuvre le 4ème S (Standardiser) et le 5ème S (Pérenniser) : définir des repères visuels clairs au sol et sur les tables (ombres d'outils, bacs étiquetés) et réaliser des audits 5S hebdomadaires avec notation et affichage des résultats.

2. **Vouloir éliminer tous les stocks sans sécuriser les flux en amont :**
   - *Erreur :* Réduire brutalement les en-cours de production (WIP) sans avoir fiabilisé les machines (taux de panne élevé) ou stabilisé la qualité, provoquant des ruptures d'alimentation en cascade sur les postes aval.
   - *Correction :* La réduction des stocks doit être progressive et servir d'indicateur révélant les problèmes cachés (pannes, défauts qualité, absentéisme). Il faut d'abord fiabiliser l'outil de production (via la TPM) avant de réduire les stocks de sécurité. Principe du "niveau d'eau qui baisse" révélant les rochers.

3. **VSM trop macro ou trop détaillée :**
   - *Erreur :* Cartographier l'ensemble de l'usine en un seul VSM (trop large pour être actionable) OU détailler chaque geste d'opérateur (trop fin, noyé dans les détails).
   - *Correction :* Se limiter à une **famille de produits** (groupe de produits partageant les mêmes étapes de fabrication) sur l'ensemble du flux, du fournisseur au client. Le niveau de détail est celui des "boîtes de procédé" (ilots de fabrication).

4. **SMED sans appropriation par l'équipe de production :**
   - *Erreur :* Un ingénieur méthode réalise le SMED seul et impose la nouvelle procédure aux opérateurs. Ceux-ci n'adhèrent pas et reviennent à leurs anciennes habitudes.
   - *Correction :* Associer les opérateurs à l'observation et à l'analyse (Kaizen SMED de 3 à 5 jours). Ce sont eux les experts du changement de série actuel. Le standard final doit être co-construit.

5. **Kanban sans respect strict des règles :**
   - *Erreur :* Produire sans carte Kanban "parce que c'est urgent" ou prélever dans un bac Kanban sans retirer la carte. Le système se dégrade et les calculs de dimensionnement deviennent obsolètes.
   - *Correction :* La règle d'or du Kanban est : "Jamais de production ou de mouvement sans carte Kanban valide." Des audits Kanban réguliers doivent vérifier le respect de cette règle.

## Références

- **Womack, J.P. & Jones, D.T. (1996)** — *Lean Thinking* (ouvrage fondateur du Lean).
- **Shingo, S. (1985)** — *A Revolution in Manufacturing: The SMED System*.
- **Liker, J.K. (2004)** — *The Toyota Way* (14 principes du management Toyota).
- **NF EN ISO 9001:2015** §7.1.4 et §8.5 — Exigences pour la maîtrise des processus (lien avec le Lean).
- **VDA 6.3** — Standard allemand d'audit processus (inclut des critères Lean).
- **IATF 16949** — Standard automobile intègre les approches Lean et l'amélioration continue.

## Liste de vérification (Checklist)

- [ ] La **VSM État Actuel** distingue clairement le temps à valeur ajoutée (VA) du temps sans valeur ajoutée (NVA / attentes / stocks).
- [ ] Le **plan d'action SMED** identifie précisément les opérations converties d'internes en externes, avec les gains estimés pour chaque conversion.
- [ ] Les **standards 5S** sont documentés visuellement (photos "Avant / Après" affichées au poste de travail) et audités au moins une fois par mois.
- [ ] Les **boucles Kanban** sont calculées en intégrant la demande moyenne, le délai de réapprovisionnement ($T_R$) et le coefficient de sécurité ($SS$).
- [ ] Une **matrice de polyvalence** des opérateurs est en place pour permettre le travail en flux tendu et la gestion des absences.
- [ ] Les **goulots d'étranglement** (bottlenecks) du flux de production sont identifiés et font l'objet d'un plan d'action spécifique (principe TOC / Théorie des Contraintes).
- [ ] Les **indicateurs Lean** sont affichés en salle de réunion quotidienne : Lead Time, TRS/OEE, taux de rebut, taux de respect des séquences.
- [ ] Les **réunions quotidiennes** (daily stand-up meeting / point 5 min) sont organisées par secteur avec suivi des actions et des anomalies.
- [ ] Un **plan d'amélioration continue** (Kaizen) est défini avec des chantiers programmés pour l'année à venir.
- [ ] Les **compétences Lean** des équipes (VSM, SMED, 5S, résolution de problèmes) sont évaluées et un plan de formation est en place.

