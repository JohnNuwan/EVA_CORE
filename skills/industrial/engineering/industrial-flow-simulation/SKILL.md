---
name: industrial-flow-simulation
description: "Modéliser et simuler dynamiquement les flux de production en 3D (FlexSim, Arena, Witness), analyser les goulets d'étranglement, dimensionner les tampons de stockage et optimiser les implantations d'usine."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [simulation, flow-simulation, flexsim, arena, witness, bottleneck, layout, buffer-sizing, discrete-event, throughput]
  EVA:
    related_skills: [lean-manufacturing-vsm, supply-chain-planning-erp, hvac-industrial-ventilation]
---

# Simulation de Flux Industriels

## Vue d'ensemble

Cette compétence guide la modélisation et la simulation numérique des flux de production physiques par la **simulation à événements discrets (DES — Discrete Event Simulation)** . En utilisant des outils spécialisés comme **FlexSim**, **Arena**, **Simio** ou **Witness**, elle permet de concevoir des maquettes virtuelles dynamiques de lignes de fabrication, de systèmes logistiques ou d'installations complètes.

La simulation de flux est un outil d'aide à la décision puissant pour valider les investissements matériels avant leur réalisation, en répondant à des questions telles que :

- "Quelle est la capacité réelle de ma ligne si j'ajoute une deuxième machine au poste goulet ?"
- "Quelle taille de tampon installer entre les deux machines pour garantir un TRS cible ?"
- "Mon implantation d'usine proposée permet-elle d'absorber le pic de production de l'année prochaine ?"
- "Quelle règle d'ordonnancement minimise les retards de livraison ?"

Contrairement aux calculs statiques (feuilles Excel, formules déterministes), la simulation intégre la **variabilité** : pannes aléatoires, temps de cycle variables, arrivées non uniformes, absenteéisme. C'est cette capacité à capturer le comportement dynamique du système qui rend la simulation indispensable pour dimensionner correctement des systèmes complexes.

Cette compétence est conçue pour être actionnée par l'agent EVA lorsque l'utilisateur exprime un besoin lié à la modélisation, la simulation, l'analyse de flux ou l'optimisation de la production par simulation dynamique.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de façon explicite ou implicite de :

- Créer un modèle de simulation 3D pour représenter le comportement d'une nouvelle ligne de production ou d'un système logistique.
- Déterminer la capacité nécessaire d'une zone tampon (buffer) entre deux machines pour absorber les variations de production.
- Identifier et éliminer des goulets d'étranglement (bottleneck analysis) dans un atelier existant ou en conception.
- Tester l'impact de différentes règles d'ordonnancement (FIFO, EDD, SPT, règles hybrides) ou de cadences de machines sur le débit global (throughput).
- Valider l'implantation physique (layout) d'une usine et optimiser les circulations de matières et de chariots.
- Dimensionner une flotte d'équipements mobiles (AGV, chariots, transstockeurs) en fonction du flux de produits.
- Analyser le retour sur investissement (ROI) d'un projet d'automatisation par scénarios comparatifs.

---

## Concepts fondamentaux de la simulation à événements discrets

### Qu'est-ce qu'un événement discret ?

Un modèle DES évolue par **sauts** entre événements (arrivée d'une pièce, début/fin d'opération, panne, réparation). Entre deux événements, l'état du système ne change pas. L'horloge du modèle progresse du temps de l'événement courant au temps du prochain événement.

**Exemple :** Un poste d'assemblage traite une pièce. Les événements sont :

1. **Arrivée pièce** → la pièce entre dans la file d'attente.
2. **Début d'opération** → la pièce quitte la file, la machine passe en état "occupée", une temporisation de 45 secondes démarre.
3. **Fin d'opération** → la pièce sort du poste, la machine passe en état "libre".
4. **Panne** → la machine passe en état "panne", un compteur MTTR démarre.
5. **Réparation** → la machine repasse en "libre".

### Théorie des files d'attente (Loi de Little)

Dans un système stable, la relation entre les trois grandeurs fondamentales est :

$$WIP = TH \cdot CT$$

Où :
- $WIP$ (Work In Process) : Nombre moyen de produits en cours dans le système.
- $TH$ (Throughput) : Débit moyen de sortie ($\text{pièces / unité de temps}$).
- $CT$ (Cycle Time) : Temps de cycle moyen d'un produit dans le système (attente + opération).

**Conséquence pratique :** Si le temps de cycle augmente (attente de composants, pannes), les encours ($WIP$) augmentent proportionnellement, ce qui peut saturer les zones de stockage intermédiaires et dégrader la visibilité sur les flux.

### Concepts de variabilité

La **variabilité** est la cause principale de la différence entre capacité théorique et capacité réelle :

| Source de variabilité | Exemple | Loi statistique typique |
|:---------------------|:--------|:------------------------|
| Temps d'opération | Usinage, assemblage | Loi normale, log-normale |
| Pannes | MTBF, MTTR | Loi exponentielle (MTBF), log-normale (MTTR) |
| Arrivée des matières | Livraisons fournisseurs | Loi de Poisson / exponentielle |
| Demande client | Commandes urgentes | Loi de Poisson |
| Présence opérateur | Absentéisme, pauses | Distribution empirique |

---

## Processus de modélisation et de simulation

### Méthodologie en 7 étapes

1. **Définition du problème et des objectifs** : Questions à résoudre, indicateurs clés (TH, WIP, CT, TRS/OEE, taux de saturation).
2. **Collecte et analyse des données** : Données de production historiques (GMAO, MES, ERP), chroniques de pannes, gammes opératoires, temps standards.
3. **Construction du modèle conceptuel** : Diagramme de flux, logique de décision, hypothèses simplificatrices.
4. **Implémentation dans l'outil** : Saisie des machines, convoyeurs, opérateurs, flux de produits, logique de routage, lois statistiques.
5. **Vérification et validation (V&V)** :
   - **Vérification** : Le modèle se comporte-t-il comme prévu ? (animation visuelle, débogage pas à pas)
   - **Validation** : Le modèle reproduit-il le comportement du système réel ? (comparaison avec les données historiques)
6. **Expérimentation et analyse de scénarios** : Exécution de réplications (multiples runs avec des graines aléatoires différentes), analyse statistique.
7. **Interprétation et recommandations** : Rapport des résultats, graphiques, analyses de sensibilité, recommandations d'investissement.

### Nombre de réplications

Pour obtenir une estimation fiable de la moyenne $\bar{x}$ d'un indicateur avec un intervalle de confiance $IC$ donné :

$$n = \left(\frac{z \cdot s}{\delta}\right)^2$$

Où $z$ est le quantile de la loi normale (1.96 pour 95 %), $s$ l'écart-type estimé et $\delta$ la demi-largeur de l'intervalle désiré.

---

## Dimensionnement des zones tampons (Buffers)

Un tampon est placé entre deux machines A (productrice) et B (consommatrice). Si A tombe en panne, B peut continuer à puiser dans le tampon. Si B tombe en panne, A peut continuer à produire dans le tampon.

### Formule simplifiée de dimensionnement

$$Capacité\ du\ tampon = \frac{MTTR_{Amont}}{Temps\ de\ cycle_{Aval}}$$

Cela permet à la machine aval de tourner sans interruption pendant toute la durée moyenne de dépannage de la machine amont.

**Exemple :** Machine A avec $MTTR = 30$ minutes (1800 s), machine B avec temps de cycle $= 12$ s.

$$Capacité\ tampon = \frac{1800}{12} = 150\ pièces$$

Cependant, cette formule ne tient pas compte de la **variabilité** des pannes et des temps de cycle. Une simulation est nécessaire pour affiner :

- Si $MTTR$ suit une loi exponentielle (forte variabilité), le tampon doit être augmenté de 20 à 40 %.
- Si $MTBF$ est faible (pannes fréquentes), des tampons plus grands sont nécessaires pour maintenir le débit.

### Règle empirique (Kingman's equation pour files d'attente simples)

$$CT_q \approx \frac{C_a^2 + C_e^2}{2} \cdot \frac{u}{1-u} \cdot t_e$$

Où $CT_q$ est le temps d'attente moyen dans la file, $C_a^2$ le coefficient de variation au carré des arrivées, $C_e^2$ celui du temps d'opération, $u$ le taux d'utilisation et $t_e$ le temps effectif moyen. Cette équation montre que la variabilité ($C^2$) a un impact direct et non linéaire sur les attentes.

---

## Identification et gestion des goulets d'étranglement

Le goulet d'étranglement (bottleneck) est la ressource qui limite la capacité maximale du système global.

### Méthodes d'identification

| Méthode | Description | Avantage |
|:--------|:-----------|:---------|
| **Taux d'utilisation** | La ressource avec le taux d'utilisation le plus élevé (proche de 100 %) | Simple, visuel dans le modèle |
| **File d'attente amont** | La ressource avec la file d'attente la plus longue devant elle | Facile à observer in situ |
| **Méthode du débit marginal** | Augmenter la capacité de la ressource de 5 % : si le débit global augmente, c'est un goulet | Précise, quantitative |
| **Active Period** | La ressource dont la période active (temps entre deux blocages) est la plus longue | Utilisée dans les outils experts (Ex : Bottleneck Detector FlexSim) |

### Règles de gestion des goulets

1. **Une heure perdue sur le goulet est une heure perdue pour toute l'usine** : Protéger inconditionnellement le goulet contre la sous-alimentation, les pannes évitables, les changements de série non optimisés.
2. **Une heure gagnée sur une ressource non-goulet n'est qu'une illusion** : Elle augmente le stock intermédiaire sans augmenter le débit final.
3. **Le goulet se déplace** : Après avoir amélioré un goulet, le suivant apparaît (loi des rendements décroissants). Une simulation doit être relancée après chaque modification.

---

## Analyse d'implantation (Layout) par simulation

### Indicateurs de performance d'un layout

| Indicateur | Définition | Objectif |
|:-----------|:-----------|:---------|
| Distance parcourue totale | Somme des distances de transport des produits/opérateurs sur la période | Minimiser |
| Temps de déplacement | Temps passé à transporter vs à produire | $< 15\%$ du temps total |
| Taux de congestion | Fréquence de blocage des allées par les chariots ou les encours | $< 5\%$ |
| Flexibilité au changement | Capacité à réorganiser le layout en cas de nouveau produit | Maximiser |

### Scénarios comparatifs typiques

1. **Layout en ligne** (flow shop) : Produits homogènes, flux tendu, peu flexible.
2. **Layout cellulaire** (cellular manufacturing) : Familles de produits, distance réduite, meilleure flexibilité.
3. **Layout fonctionnel** (job shop) : Ateliers par type d'opération, très flexible, flux complexes.

---

## Pièges Courants (Common Pitfalls)

### 1. Utiliser des données de performance parfaites (théoriques)

**Erreur :** Configurer les machines du modèle avec des temps de cycle constants sans intégrer les pannes (MTBF/MTTR) ou la variabilité des temps de traitement. Le modèle surestimera largement le débit réel de l'usine — souvent de 20 à 30 %, rendant les décisions d'investissement basées sur ce modèle dangereusement optimistes.

**Exemple :** Une ligne avec 6 machines, chaque machine ayant $MTBF = 300$ min et $MTTR = 15$ min. Avec un temps de cycle de 60 s, le TRS moyen par machine est de $300 / (300 + 15) \approx 95.2\%$. Mais le TRS de la ligne entière (multiplicatif) est de $0.952^6 \approx 74\%$, soit 26 % de perte. Une simulation idéalisée montrerait une production de 100 %, alors que la réalité est à 74 %.

**Correction :** Utiliser des lois de distribution statistiques réalistes basées sur l'historique de la GMAO :
- Pannes : Loi exponentielle ($\lambda = 1/MTBF$) ou Weibull (si tendance au vieillissement).
- Réparations : Loi log-normale (événements rares mais longs) ou exponentielle.
- Temps d'opération : Loi normale avec $\sigma \approx 5-10\%$ de la moyenne.

### 2. Simulation sur une durée trop courte pour atteindre le régime établi (steady state)

**Erreur :** Lancer une simulation de 8 heures et analyser immédiatement les résultats, alors que les convoyeurs et stocks étaient vides au début (état initial "à vide"). La période de montée en charge (warm-up) fausse la moyenne des performances : les premières heures montrent des temps de cycle anormalement bas (pas d'attente), ce qui donne une vision trop optimiste du système.

**Correction :** Configurer une période de pré-chauffage (warm-up) pour charger le modèle de manière réaliste (remplir les buffers à 50 % de leur capacité nominale). Utiliser la méthode de Welch (moyenne mobile des réplications) pour déterminer visuellement la fin de la période transitoire. Ensuite, collecter les statistiques sur une durée longue — typiquement 1 semaine ou 1 mois de temps simulé.

### 3. Modèle trop détaillé et ingérable

**Erreur :** Modéliser chaque convoyeur individuel, chaque capteur, chaque micro-opération. Le modèle devient lent à exécuter (une simulation de 1 mois peut prendre 4 heures de temps CPU), difficile à valider et impossible à maintenir lorsque le système réel change.

**Correction :** Appliquer le principe de **parcimonie** (rasoir d'Occam) : ne modéliser que ce qui impacte les décisions à prendre. Un convoyeur long de 50 m peut être représenté par un temps de transfert fixe plutôt que par 50 segments individuels. Les micro-opérations (vis serrée, contrôle visuel) peuvent être agrégées en une seule étape si elles ne sont pas des goulets potentiels.

### 4. Oublier la validation du modèle

**Erreur :** Présenter les résultats de la simulation comme des faits sans avoir vérifié que le modèle reproduit fidèlement le comportement du système réel. Un décalage de 5 % sur les temps de cycle individuels peut se traduire par 20 % d'erreur sur le débit global après cumul, rendant les conclusions invalides.

**Correction :** Valider systématiquement le modèle en plusieurs étapes :
- **Validation face** : Soumettre la logique du modèle aux opérateurs et chefs d'atelier.
- **Validation quantitative** : Comparer le débit simulé (en régime stabilisé) avec 3 mois de production réelle.
- **Analyse de sensibilité** : Faire varier un paramètre et vérifier que le sens de variation est cohérent avec l'intuition physique.

---

## Liste de vérification (Checklist)

- [ ] Les lois de probabilité appliquées aux temps d'arrêt (MTBF/MTTR) et de traitement sont représentatives des données historiques (GMAO, MES).
- [ ] Une période de pré-chauffage (warm-up time) est programmée et les statistiques sont collectées après cette période uniquement.
- [ ] Le modèle reproduit fidèlement la capacité réelle des convoyeurs (accumulation physique, vitesse de transfert, temps d'arrêt).
- [ ] Les goulets d'étranglement détectés dans la simulation concordent avec les observations qualitatives de l'atelier de production.
- [ ] Les variables de résultats (TRS/OEE, débit, taux de saturation, temps de cycle) sont exportées sous forme de graphiques exploitables pour les décideurs.
- [ ] Le nombre de réplications est suffisant pour garantir des intervalles de confiance inférieurs à 5 % de la moyenne.
- [ ] Un plan de scénarios comparatifs (avant/après, avec/sans investissement, sensible/in sensible) est défini avant le lancement des runs.
- [ ] Les hypothèses simplificatrices sont documentées (ex : absence de panne électrique, temps de pause standard).
- [ ] Les données d'entrée (temps de cycle, MTBF, MTTR) sont auditées et validées avant implémentation.
- [ ] L'analyse de sensibilité inclut les cas pessimistes, optimistes et les valeurs les plus probables.

