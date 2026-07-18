---
name: prompt-method-analogical
description: "Résoudre des problèmes nouveaux en identifiant des analogies avec des situations connues et en transposant leurs solutions."
version: 2.0.0
author: John Nuwan Moncel (adapté par Actemium)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [prompt-engineering, analogical, biblio-ia, methods, reasoning, creative-problem-solving]
    related_skills: [python-pep8, simplify-code, plan, step-back, generated-knowledge]
---

# La méthode Analogical Prompting

## Guide de référence pour le raisonnement par analogie et le transfert de solutions

---

## 1. Vue d'ensemble

La méthode **Analogical Prompting** (ou raisonnement par analogie) est une technique de prompt engineering qui consiste à **identifier un problème connu et déjà résolu dans un domaine source**, puis à **transposer sa solution** au problème actuel dans un domaine cible. Cette approche exploite la capacité des LLM à reconnaître des similarités structurelles entre des situations apparemment différentes.

### Principe fondateur

Le cœur de la méthode repose sur le principe **« Like This, Do That »** (Comme ceci, fais cela) :

- **Analogies comme pont cognitif** : relier l'inconnu au connu pour accélérer la résolution
- **Transfert de solutions** : adapter une solution éprouvée d'un domaine à un autre
- **Créativité structurée** : générer des idées innovantes par croisement de domaines
- **Pédagogie augmentée** : expliquer des concepts complexes par des métaphores accessibles

### Architecture conceptuelle

```
                    ┌──────────────────────────────────┐
                    │   Problème nouveau / inédit      │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Phase 1 : RECHERCHE D'ANALOGIES │
                    │  Explorer des domaines variés     │
                    │  (nature, médecine, armée, sport, │
                    │   cuisine, architecture, etc.)    │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Phase 2 : SÉLECTION de la       │
                    │  meilleure analogie              │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Phase 3 : MAPPING des           │
                    │  correspondances                 │
                    │  Problème ←→ Analogie            │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Phase 4 : TRANSFERT de la       │
                    │  solution au problème cible      │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Phase 5 : ADAPTATION et         │
                    │  vérification des limites        │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │   ✅ Solution adaptée livrée     │
                    └──────────────────────────────────┘
```

---

## 2. Quand l'utiliser ?

### Cas d'usage recommandés

| Contexte | Description | Priorité |
|----------|-------------|----------|
| Problèmes nouveaux ou inédits | Aucune solution directe connue, besoin d'inspiration | Élevée |
| Blocage créatif | Impossible de trouver une approche par les méthodes conventionnelles | Élevée |
| Explication pédagogique | Vulgarisation de concepts complexes par des métaphores | Élevée |
| Architecture et design patterns | Transposer des patterns éprouvés d'un domaine à un autre | Moyenne |
| Résolution de bugs obscurs | Trouver une piste en comparant à des problèmes similaires | Moyenne |
| Innovation et R&D | Générer des idées disruptives par croisement de secteurs | Moyenne |

### Situations à éviter

- **Problèmes triviaux** : une solution directe existe déjà, l'analogie ajoute de la complexité inutile
- **Sujets à forte rigueur mathématique** : les analogies peuvent masquer des différences fondamentales dans les preuves
- **Domaines réglementaires stricts** : une analogie peut suggérer une approche non conforme
- **Situations où la précision est critique** : les analogies sont approximatives par nature

---

## 3. Procédure pas à pas

### Étape 1 : Définir le problème avec précision

Formalisez le problème en isolant sa structure fondamentale.

```
Problème : « Comment structurer une grande équipe de développement
de 200 personnes pour maximiser l'autonomie et la productivité ? »

Structure du problème :
- Ressource : 200 personnes
- Objectif : autonomie + productivité
- Contrainte : coordination à grande échelle
- Risque : silos et perte de cohérence
```

### Étape 2 : Explorer des domaines d'analogie

Cherchez dans des domaines variés un problème structurellement similaire.

**Promoteur d'analogies :**

```
Pour le problème suivant, explore au moins 4 domaines différents
pour trouver des analogies structurelles :

Problème : « Structurer 200 développeurs pour maximiser autonomie
et productivité. »

Domaines à explorer :
1. Militaire / Armée (organisation hiérarchique)
2. Biologie / Nature (essaims, colonies)
3. Architecture / Urbanisme (planification de quartiers)
4. Gastronomie / Cuisine (brigade de cuisine)
5. Sport (organisation d'équipes)
```

**Sortie :**

```
🔍 ANALOGIES IDENTIFIÉES

1. Domaine militaire :
   Analogie : « C'est comme organiser une armée en divisions,
   régiments, bataillons et escouades. »
   Points forts : chaîne de commandement claire
   Points faibles : rigidité, lenteur décisionnelle

2. Domaine biologique :
   Analogie : « C'est comme une colonie de fourmis avec des
   rôles spécialisés mais sans hiérarchie stricte. »
   Points forts : résilience, adaptabilité
   Points faibles : coordination complexe

3. Domaine architectural :
   Analogie : « C'est comme concevoir un quartier avec des
   îlots autonomes reliés par des artères. »
   Points forts : modularité, extensibilité
   Points faibles : duplication potentielle

4. Domaine sportif :
   Analogie : « C'est comme un club omnisports avec des
   sections spécialisées coordonnées. »
   Points forts : spécialisation, identité d'équipe
   Points faibles : compétition interne
```

### Étape 3 : Sélectionner la meilleure analogie

Choisissez l'analogie qui maximise les correspondances structurelles.

**Critères de sélection :**
| Critère | Poids | Explication |
|---------|-------|-------------|
| Correspondance structurelle | 40% | Les relations entre éléments sont-elles similaires ? |
| Transférabilité | 30% | La solution peut-elle être adaptée ? |
| Familiarité | 20% | L'analogie est-elle compréhensible par l'équipe ? |
| Précision | 10% | Les limites de l'analogie sont-elles acceptables ? |

### Étape 4 : Établir le mapping problème ↔ analogie

Créez un tableau de correspondances entre les éléments du problème et ceux de l'analogie.

```
Analogie retenue : Organisation militaire → Organisation d'équipe

MAPPING :
┌─────────────────────┬──────────────────────────────┐
│ Problème (Dev)      │ Analogie (Armée)              │
├─────────────────────┼──────────────────────────────┤
│ 200 développeurs    │ Division militaire (2000)     │
│ Équipe (8-10 pers.) │ Peloton / Escouade            │
│ Département         │ Bataillon                     │
│ CTO                 │ Général                       │
│ Tech Lead           │ Capitaine                     │
│ Sprint planning     │ Briefing de mission           │
│ Daily standup       │ Rapport matinal               │
│ Code review         │ Inspection des troupes        │
│ Déploiement         │ Assaut / Manœuvre             │
│ Rétrospective       │ Débriefing post-mission       │
│ Objectif produit    │ Mission / Ordre                │
└─────────────────────┴──────────────────────────────┘
```

### Étape 5 : Transférer et adapter la solution

À partir du mapping, générez une solution concrète et adaptée au domaine cible.

```
SOLUTION TRANSFÉRÉE :

Dans l'armée, une division de 2000 soldats est structurée en
4 bataillons de 500, chacun divisé en 5 compagnies de 100,
elles-mêmes divisées en pelotons de 10.

Transposition pour 200 développeurs :
- 4 départements de 50 personnes (Backend, Frontend, Data, DevOps)
- Chaque département : 5 équipes de 10 personnes
- Chaque équipe : 1 Tech Lead + 8 devs + 1 PM
- Rituels : daily standup (équipe), sync hebdo (département),
  quarterly planning (tous)

Bénéfices :
✅ Autonomie des équipes (pelotons autonomes)
✅ Hiérarchie plate (3 niveaux max)
✅ Coordination standardisée (rituels prévisibles)
✅ Scalabilité (ajouter un bataillon = ajouter 5 équipes)

Limites de l'analogie :
⚠️ L'armée est verticale, le développement agile a besoin
   de cross-fonctionnalité
⚠️ Trop de rigidité peut tuer l'innovation
⚠️ Les développeurs ne suivent pas des ordres, ils collaborent
```

---

## 4. Workflow complet

```
                    ┌──────────────────────────────────┐
                    │   Problème nouveau (cible)       │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Extraire la structure du         │
                    │  problème (contraintes, objectifs) │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Explorer N domaines sources      │
                    │  pour des analogies structurelles │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Évaluer chaque analogie :        │
                    │  - Correspondance structurelle    │
                    │  - Transférabilité                │
                    │  - Limites                        │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Sélectionner la meilleure        │
                    │  analogie                         │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Construire le mapping            │
                    │  Problème ←→ Analogie             │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Transférer la solution           │
                    │  Adapter au contexte cible        │
                    └──────────────┬───────────────────┘
                                   │
                    ┌──────────────▼───────────────────┐
                    │  Vérifier les limites :           │
                    │  Qu'est-ce qui ne se transpose    │
                    │  pas ?                            │◄── Si trop de limites,
                    └──────────────┬───────────────────┘    retour exploration
                                   │
                    ┌──────────────▼───────────────────┐
                    │  ✅ Solution adaptée              │
                    └──────────────────────────────────┘
```

---

## 5. Exemples concrets de code et prompts

### Exemple 1 : Gestion des bugs en production

**Prompt analogique :**

```
Problème : « Comment gérer efficacement les bugs critiques en
production sans paniquer et minimiser l'impact utilisateur ? »

Étape 1 — Trouve une analogie forte dans le domaine médical :
décris comment les urgences hospitalières gèrent les crises.

Étape 2 — Établis le mapping complet entre le problème et
l'analogie médicale.

Étape 3 — Transfère la solution médicale au problème technique.
```

**Réponse :**

```
🔍 MEILLEURE ANALOGIE : Médecine d'urgence

Les bugs en production sont comme les infections nosocomiales
ou les urgences vitales dans un hôpital.

📋 MAPPING :
┌────────────────────────┬──────────────────────┐
│ Problème (DevOps)      │ Analogie (Médecine)   │
├────────────────────────┼──────────────────────┤
│ Bug critique (P0)      │ Urgence vitale        │
│ Incident standard (P1) │ Consultation urgente  │
│ Bug mineur (P2)        │ Visite de routine     │
│ Hotfix                 │ Antibiotique           │
│ Rollback               │ Mise en quarantaine   │
│ Post-mortem            │ Autopsie / analyse    │
│ Feature flag           │ Médicament palliatif  │
│ Monitoring             │ Signes vitaux         │
│ Runbook                │ Protocole médical      │
│ On-call                │ Garde hospitalière    │
└────────────────────────┴──────────────────────┘

💡 SOLUTION TRANSFÉRÉE :

1. TRIAGE (à l'arrivée aux urgences) :
   - P0 = Urgence vitale : réponse immédiate (< 15 min)
   - P1 = Urgence relative : réponse < 1h
   - P2 = Non urgent : ticket backlog

2. CONTAINMENT (comme isoler un patient contagieux) :
   - Activer le feature flag désactivant la fonctionnalité
   - Rollback partiel de la feature
   - Redirection du trafic vers les instances saines

3. TRAITEMENT (comme administrer un traitement) :
   - Hotfix ciblé (comme un antibiotique à large spectre
     d'abord, puis ciblé après diagnostic)
   - Déploiement progressif (canary release)

4. PRÉVENTION (comme un vaccin) :
   - Post-mortem systématique dans les 48h
   - Ajout de tests spécifiques (comme des anticorps)
   - Mise à jour des runbooks (comme des protocoles)
```

### Exemple 2 : Architecture microservices

**Prompt :**

```
Problème : « Comment concevoir un système de microservices
qui soit à la fois modulaire et facile à orchestrer ? »

Trouve une analogie dans l'urbanisme ou l'architecture des
villes pour résoudre ce problème.
```

**Réponse :**

```
🔍 ANALOGIE : Urbanisme / Organisation d'une ville

📋 MAPPING :
┌─────────────────────┬─────────────────────────┐
│ Microservices       │ Quartiers d'une ville    │
├─────────────────────┼─────────────────────────┤
│ Service A           │ Quartier résidentiel     │
│ Service B           │ Quartier commercial      │
│ API Gateway         │ Mairie / Administration  │
│ Message Queue       │ Réseau routier           │
│ Service Mesh        │ Plan de circulation      │
│ Database            │ Infrastructure (eau/élec)│
│ Monitoring          │ Caméras et capteurs      │
│ CI/CD               │ Permis de construire     │
└─────────────────────┴─────────────────────────┘

💡 SOLUTION TRANSFÉRÉE :

Une ville bien conçue a :
- Des quartiers autonomes (microservices) avec leurs propres
  commerces (bases de données)
- Un réseau de transport (message queue) pour les échanges
- Une mairie (API Gateway) qui oriente les visiteurs
- Des règles d'urbanisme (contrats d'interface) claires
- Des zones industrielles séparées des zones résidentielles

Transposition :
1. Chaque microservice est un « quartier autonome »
2. Les contrats d'interface sont les « règles d'urbanisme »
3. L'API Gateway est la « mairie » qui oriente les requêtes
4. Le message broker est le « réseau de bus »
5. Le monitoring est la « vidéosurveillance urbaine »
6. Les tests de contrat sont les « inspections de conformité »

Point de vigilance : Une ville peut devenir une mégalopole
ingouvernable = vos microservices peuvent devenir trop nombreux
sans gouvernance.
```

---

## 6. Pièges courants (Pitfalls)

### ⚠️ Piège n°1 : Analogie superficielle (similarité de surface vs structurelle)

**Erreur :** L'analogie est choisie pour sa ressemblance superficielle, mais la structure profonde du problème est différente.

```
❌ Problème : « Optimiser le temps de compilation d'un projet »
   Analogie choisie : « C'est comme faire cuire un gâteau plus
   vite » (similarité : cuisson)
   → Problème : la compilation est parallélisable, la cuisson
     d'un gâteau ne l'est pas
   → Solution transférée inadaptée
```

**✅ Correction :** Distinguez similarité de surface et similarité structurelle :

```
Analogie de surface : mêmes mots, mêmes objets (cuisson = compilation)
Analogie structurelle : mêmes relations, mêmes contraintes

Avant de valider une analogie, vérifie que :
1. Les RELATIONS entre les éléments sont similaires
   (pas seulement les éléments eux-mêmes)
2. Les CONTRAINTES du problème source existent aussi
   dans le problème cible
3. La CAUSE profonde est analogue, pas seulement le symptôme
```

### ⚠️ Piège n°2 : Surcharge d'analogies (trop de métaphores tuent la métaphore)

**Erreur :** Utiliser plusieurs analogies contradictoires dans la même explication.

```
❌ « Notre architecture microservices est comme une ville,
   mais aussi comme un organisme vivant, et aussi comme
   une armée. » → confusion, incohérence
```

**✅ Correction :** Une seule analogie principale, des sous-analogies cohérentes :

```
Choisis UNE analogie principale et tiens-t'y.
Si besoin, des sous-analogies peuvent compléter, mais elles
doivent être cohérentes avec l'analogie principale.

Exemple correct :
Analogie principale : ville
Extensions cohérentes : permis de construire (CI/CD),
  réseau routier (message queue), mairie (API Gateway)
```

### ⚠️ Piège n°3 : Ignorer les limites de l'analogie

**Erreur :** Appliquer aveuglément la solution sans identifier ce qui ne se transpose pas.

```
❌ Analogue militaire : « Structurons l'équipe comme une armée »
   → Solution transférée à 100%
   → Problème : les développeurs ne sont pas des soldats,
     ils ont besoin d'autonomie créative, pas d'ordres
   → Résultat : équipe démotivée, turnover
```

**✅ Correction :** Documentez explicitement les limites dès le départ :

```
Pour chaque analogie, ajoute une section « POINTS DE VIGILANCE »
qui liste :
1. Ce qui NE se transpose PAS
2. Les différences fondamentales entre les domaines
3. Les adaptations nécessaires pour compenser

Exemple : « Dans l'armée, les ordres sont descendants.
Dans le développement, les décisions techniques doivent
être prises par l'équipe. Solution : adapter en donnant
des « missions » (objectifs) plutôt que des « ordres »
(instructions détaillées). »
```

### ⚠️ Piège n°4 : Confondre corrélation et causalité dans l'analogie

**Erreur :** Assumer que si A cause B dans l'analogie, alors A' cause B' dans le problème cible.

```
❌ Dans l'analogie médicale : « Antibiotiques → guérison »
   Transposition : « Hotfix → résolution du bug »
   → Manque : les antibiotiques ciblent la cause (bactérie),
     les hotfixes traitent le symptôme
```

**✅ Correction :** Vérifiez la chaîne causale :

```
Pour chaque relation causale transférée, demande-toi :
« Est-ce que la même relation de cause à effet existe dans
les deux domaines ? »
```

---

## 7. Checklist d'utilisation

### Exploration des analogies

- [ ] Au moins 3 domaines sources différents ont-ils été explorés ?
- [ ] La structure profonde du problème a-t-elle été extraite avant la recherche ?
- [ ] Les analogies sont-elles diversifiées (nature, technique, social, etc.) ?
- [ ] Chaque analogie a-t-elle été évaluée sur sa correspondance structurelle ?

### Sélection et mapping

- [ ] L'analogie retenue est-elle la plus pertinente structurellement (pas juste la plus évidente) ?
- [ ] Le mapping problème ↔ analogie est-il complet et cohérent ?
- [ ] Les correspondances sont-elles des relations (pas seulement des noms) ?
- [ ] Les limites de l'analogie sont-elles documentées ?

### Transfert et adaptation

- [ ] La solution transférée est-elle adaptée au contexte cible ?
- [ ] Les différences culturelles entre les domaines sont-elles prises en compte ?
- [ ] La solution est-elle suffisamment concrète pour être implémentée ?
- [ ] Les points de vigilance sont-ils intégrés dans le plan d'action ?

### Communication

- [ ] L'analogie est-elle compréhensible par l'audience cible ?
- [ ] Une seule analogie principale est-elle utilisée (pas de confusion) ?
- [ ] Les limites de l'analogie sont-elles communiquées ?
- [ ] L'analogie facilite-t-elle réellement la compréhension ou ajoute-t-elle du bruit ?

---

## 8. Variantes avancées

| Variante | Description | Quand l'utiliser |
|----------|-------------|-----------------|
| Analogie auto-générée | Le LLM génère lui-même l'analogie, le mapping et la solution en un seul prompt | Rapidité d'exécution |
| Analogie multi-sources | Combiner les forces de plusieurs analogies différentes | Problèmes complexes multi-dimensions |
| Analogie négative | Identifier des contre-exemples : « ce qui NE ressemble PAS à mon problème » | Éviter les pièges |
| Chaîne d'analogies | Analyser l'analogie elle-même par une autre analogie pour approfondir | Problèmes très abstraits |
| Analogie avec validation | Faire évaluer l'analogie par un second agent avant transfert | Réduction des biais |

---

> **Note importante :** Le raisonnement par analogie est un outil cognitif puissant, mais il nécessite de la rigueur. La tentation est grande de choisir l'analogie la plus séduisante plutôt que la plus pertinente structurellement. Prenez le temps de challenger chaque analogie avec des contre-exemples avant de l'utiliser comme base de décision.

