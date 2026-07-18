---
name: iso-45001
description: "Concevoir, documenter et auditer un système de management de la santé et de la sécurité au travail (SST) conforme à ISO 45001 : évaluation des risques professionnels (EvRP), document unique, procédures LOTO, prévention des TMS et AT/MP."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [iso-45001, occupational-health, safety, risk-prevention, industrial-standards, sst, loto, evrp, document-unique, near-miss, hse, prevention]
    related_skills: [iso-quality, ot-security, industrial-risk-analysis-hazop]
    difficulty: intermediate
    industry_sectors: [manufacturing, construction, chemical, pharmaceutical, energy, logistics, mining, food-beverage]
---

# Santé et Sécurité au Travail & Norme ISO 45001

## Vue d'ensemble

La norme **ISO 45001** (version actuelle : ISO 45001:2018) spécifie les exigences pour un système de management de la santé et de la sécurité au travail (SST). Elle remplace l'ancienne norme OHSAS 18001 et adopte la structure HLS (High Level Structure) commune à toutes les normes ISO de système de management.

Elle permet aux entreprises industrielles de :
- Procurer des **lieux de travail sûrs et sains** en prévenant les accidents et les maladies professionnelles.
- Éviter les **traumatismes et les atteintes à la santé** liés au travail.
- Améliorer activement leur **performance en SST**.
- Satisfaire aux **obligations légales** et réglementaires (Code du Travail, CARSAT, DREETS).

### Contexte : Les Chiffres de la SST

Selon l'Organisation Internationale du Travail (OIT) :
- Près de **3 millions de décès** liés au travail chaque année dans le monde.
- **395 millions d'accidents du travail** non mortels par an.
- En France, la CNAMTS recense plus de **650 000 accidents du travail** et **60 000 maladies professionnelles** par an (dont 40 % de TMS).

L'industrie manufacturière et la construction sont les secteurs les plus exposés. Un accident grave coûte en moyenne entre 50 000 € et 200 000 € à l'entreprise (directs : indemnités, arrêts de production ; indirects : image, démarche qualité, augmentation des primes d'assurance).

### Principes Clés de l'ISO 45001

1. **Identification des dangers et évaluation des risques (EvRP)** : Analyser chaque poste de travail, chaque tâche et chaque situation pour identifier les risques physiques (chute, écrasement, brûlure), chimiques, ergonomiques (TMS), biologiques, thermiques, électriques et psychosociaux (RPS).
2. **Hiérarchie des mesures de prévention** (Article L.4121-2 du Code du Travail français) :
   1. Éviter le risque (supprimer le danger).
   2. Évaluer les risques qui ne peuvent pas être évités.
   3. Combattre les risques à la source.
   4. Adapter le travail à l'homme (conception des postes, choix des équipements).
   5. Tenir compte de l'évolution technique.
   6. Remplacer ce qui est dangereux par ce qui ne l'est pas.
   7. Planifier la prévention (technique, organisation, conditions de travail, relations sociales).
   8. Prendre des mesures de protection collective en priorité sur les EPI.
   9. Donner les instructions appropriées.
3. **Participation des travailleurs** : Impliquer activement les opérateurs de terrain dans l'identification des situations dangereuses ("Presqu'accidents" ou Near-Miss) et dans l'élaboration des procédures.
4. **Analyse des incidents** : Réaliser des arbres des causes après chaque incident (même sans blessure) pour éviter la récurrence.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :

- D'élaborer une **grille d'évaluation des risques professionnels (EvRP)** pour un poste de travail (maintenance, production, logistique, laboratoire).
- De concevoir des **plans de prévention** pour des interventions de sous-traitants externes (Protocole de sécurité).
- De rédiger des **procédures de Lockout/Tagout (LOTO — Consignation)** pour des phases de maintenance sur machines.
- De définir des **indicateurs SST** (Taux de fréquence TF, Taux de gravité TG, Indice de fréquence).
- De préparer l'actualisation du **Document Unique d'Évaluation des Risques (DUER)**.
- De mettre en place un système de **remontée des presqu'accidents (Near-Miss)**.
- D'accompagner la préparation d'un **audit de certification ISO 45001**.

**Ne pas utiliser pour :**
- La programmation de fonctions de sécurité automate (norme machine ISO 13849 / IEC 62061).
- Les études de sécurité des procédés chimiques (HAZOP / LOPA) — utiliser `industrial-risk-analysis-hazop`.

## 1. Exemple de Fiche de Consignation Machine (Lockout/Tagout — LOTO)

La consignation est l'action la plus critique de la prévention pour assurer la sécurité des techniciens de maintenance. Elle consiste à couper et verrouiller toutes les sources d'énergie d'une machine avant toute intervention.

### Procédure Standard de Consignation (7 Étapes)

```text
MACHINE : Palettiseur Automatique Ligne 3
FICHE LOTO — Réf: LOTO-L3-PAL01

1. PRÉPARATION :
   • Informer l'opérateur de ligne de l'arrêt de la machine pour maintenance.
   • Vérifier que l'intervention peut être réalisée en sécurité (EPI adaptés).
   • Rassembler les cadenas et étiquettes personnels (un par intervenant).

2. ARRÊT :
   • Mettre la machine à l'état initial sûr via le pupitre de commande (Bouton Stop).
   • Attendre l'arrêt complet de tous les mouvements.

3. ISOLATION DES ÉNERGIES :
   • Énergie Électrique (230 V / 400 V tri) :
     - Tourner le sectionneur principal Q1 sur la position "0" (OFF).
     - Apposer un cadenas personnel sur la poignée du sectionneur.
     - Apposer une étiquette de consignation (nom, date, motif).
   • Énergie Pneumatique (6 bar) :
     - Fermer la vanne d'arrivée d'air principale (vanne jaune à glissière).
     - Purger l'air résiduel du circuit (vérifier le manomètre à 0 bar).
     - Verrouiller la vanne avec un cadenas physique.
   • Énergie Gravitationnelle / Potentielle :
     - Mettre en place les goupilles de sécurité mécaniques sous le chariot élévateur.
     - Bloquer les axes de rotation avec des dispositifs mécaniques.
   • Énergie Hydraulique (si applicable) :
     - Purger le circuit hydraulique, verrouiller la vanne de barrage.
   • Énergie Thermique (si applicable) :
     - Vérifier que les surfaces chaudes sont refroidies (température < 50 °C).

4. VÉRIFICATION D'ABSENCE DE DANGER (VAD) :
   • Tenter de redémarrer la machine depuis le pupitre de commande IHM.
     La machine NE DOIT PAS démarrer.
   • Vérifier au multimètre l'absence de tension (VAT) sur les bornes de puissance.
   • Vérifier que la pression pneumatique est restée à 0 bar.

5. INTERVENTION :
   • Seul le personnel formé et habilité peut intervenir.
   • Respecter les gammes de maintenance.
   • Signaler toute anomalie ou modification.

6. DÉCONSIGNATION :
   • S'assurer que tous les intervenants ont retiré leur cadenas personnel.
   • Vérifier que tous les outils et équipements sont retirés de la zone.
   • S'assurer que les protections (capots, barrières) sont remises en place.
   • Rétablir les énergies dans l'ordre inverse (air, puis électricité).

7. REMISE EN SERVICE ET TEST :
   • Réarmer la machine et effectuer un cycle à vide complet.
   • Vérifier que tous les mouvements sont corrects.
   • Informer le responsable de production de la remise en service.
```

## 2. Grille d'Évaluation des Risques Professionnels (EvRP)

### Modèle de Grille (par Poste de Travail)

| Poste | Situation / Tâche | Danger | Risque associé | $F$ (1-4) | $G$ (1-4) | Criticité (F×G) | Mesures de prévention existantes | Mesures complémentaires proposées |
|:---|---|---|:---:|:---:|:---:|---|---|---|
| Opérateur ligne 1 | Changement de bobine | Écrasement par chariot élévateur | Fractures, écrasement membre inférieur | 3 | 4 | 12 | Sensibilisation, marche arrière avec gyrophare | Barrière immatérielle (laser-scanner) sur zone de travail |
| Technicien maintenance | Intervention sur moteur électrique | Contact avec pièce sous tension (400V) | Électrocution, brûlures graves | 2 | 5 | 10 | VAT avant intervention, EPI isolants | Cadenassage systématique LOTO, vérificateur d'absence de tension double |
| Opérateur logistique | Préparation de commande | Port de charges lourdes (20-30 kg) | TMS lombaires (lombalgies) | 4 | 3 | 12 | Formation gestes/postures, ceinture lombaire | Bras de préhension pneumatique, réduction des poids unitaires |
| Agent de nettoyage | Nettoyage sol atelier | Sol glissant (eau + huile) | Chute de plain-pied (fracture, entorse) | 4 | 2 | 8 | Signalétique, chaussures antidérapantes | Tapis absorbant, procédure de nettoyage immédiat des fuites |
| Opérateur laboratoire | Manipulation d'acide sulfurique | Projection chimique (brûlure acide) | Brûlure chimique, perte de vision | 2 | 4 | 8 | EPI (gants, lunettes), douche de sécurité | Bac de rétention, procédure d'urgence affichée |

**Légende :** F = Fréquence d'exposition (1 = rare/exceptionnel, 4 = permanent) | G = Gravité potentielle (1 = bénin, 4 = mortel ou irréversible).

### Niveaux de Criticité et Actions

| Criticité $C$ | Niveau | Action |
|:---:|:---:|---|
| 1 – 4 | Faible | Surveillance, information. Actions d'amélioration si opportunes. |
| 5 – 9 | Moyen | Plan d'action défini dans l'année. Indicateur de suivi. |
| 10 – 16 | Élevé | Action prioritaire. Mise en œuvre dans les 3 mois. Arrêt temporaire si non maîtrisé. |
| > 16 | Critique (intolérable) | Arrêt immédiat de l'activité. Risque inacceptable. |

## 3. Indicateurs Clés de Sécurité (KPI SST)

| Indicateur | Formule | Unité | Cible typique | Fréquence |
|:---|---|:---:|:---:|:---:|
| **Taux de Fréquence (TF)** | $\frac{Nb\ accidents\ avec\ arrêt \times 1\ 000\ 000}{Nb\ heures\ travaillées}$ | TF | < 10 (manufacturing) | Mensuelle |
| **Taux de Gravité (TG)** | $\frac{Nb\ jours\ d'arrêt\ \times 1\ 000}{Nb\ heures\ travaillées}$ | TG | < 0,5 | Mensuelle |
| **Indice de Fréquence (IF)** | $\frac{Nb\ AT\ avec\ arrêt}{Nb\ de\ salariés}$ | IF | – | Annuelle |
| **Taux de participation Near-Miss** | $\frac{Nb\ near-miss\ déclarés}{Nb\ de\ salariés}$ | % | > 50 % | Mensuelle |
| **Taux de réalisation des inspections** | $\frac{Inspections\ réalisées}{Inspections\ planifiées} \times 100$ | % | > 90 % | Mensuelle |
| **Taux de conformité LOTO** | $\frac{Audits\ LOTO\ OK}{Audits\ LOTO\ totaux} \times 100$ | % | > 95 % | Trimestrielle |

## 4. Gestion des Presqu'Accidents (Near-Miss)

La loi de Heinrich (1959) établit que pour un accident grave, on compte statistiquement :
- **1 accident grave** (blessure sérieuse)
- **29 accidents légers** (blessure mineure)
- **300 incidents / presqu'accidents** (aucune blessure mais potentiel grave)

L'objectif est de détecter et corriger les causes des presqu'accidents avant qu'ils ne se transforment en accidents.

### Procédure de Déclaration d'un Near-Miss

1. **Signalement** : Tout employé peut signaler un presqu'accident via une fiche dédiée (papier ou application mobile).
2. **Analyse** : Réunion rapide (5 min) de l'équipe concernée pour identifier les causes immédiates et racines.
3. **Action** : Définir une action corrective (responsable + échéance). L'action doit être visible (affichage en salle de réunion).
4. **Clôture** : Vérifier que l'action a été réalisée et communiquer le résultat à l'ensemble de l'équipe.
5. **Suivi statistique** : Le nombre de near-miss déclarés est un indicateur de maturité de la culture sécurité.

## Pièges Courants (Common Pitfalls)

1. **Consignation uniquement électrique :**
   - *Erreur :* Couper le disjoncteur électrique d'une machine mais laisser le circuit d'air comprimé sous pression. Un mouvement de vérin résiduel (chute d'une charge, mouvement de bras) peut écraser les doigts ou le corps du technicien.
   - *Correction :* Toujours purger et consigner **toutes** les énergies (électrique, pneumatique, hydraulique, vapeur, gravitationnelle, thermique). Utiliser la fiche LOTO multi-énergies systématiquement.

2. **Ignorer les presqu'accidents (Near-Miss) :**
   - *Erreur :* Ne déclarer et n'analyser que les accidents graves avec arrêt de travail. Les signaux faibles (glissade sans chute, outil qui tombe sans blesser, début d'incendie maîtrisé) ne sont pas remontés.
   - *Correction :* Encourager activement la remontée des presqu'accidents (ex : boîte à idées SST, application mobile anonyme, récompense pour le déclarant). Statistiquement, 300 near-miss non corrigés précèdent un accident grave.

3. **Document Unique non actualisé :**
   - *Erreur :* Réaliser le Document Unique d'Évaluation des Risques (DUER) une fois et ne jamais le mettre à jour malgré les évolutions (nouvelle machine, nouveau poste, nouveau produit chimique, réorganisation).
   - *Correction :* Mettre à jour le DUER à chaque modification significative du travail, et au minimum une fois par an (obligation légale en France — décret n°2001-1016).

4. **Protections collectives non priorisées :**
   - *Erreur :* Distribuer des EPI (gants, casques, lunettes) sans avoir d'abord cherché à supprimer le danger à la source. Exemple : continuer à exposer des opérateurs à un bruit de 95 dB(A) en leur donnant simplement des bouchons d'oreilles.
   - *Correction :* Appliquer la hiérarchie des mesures de prévention : 1. Supprimer le danger (silencieux sur la machine) → 2. Protection collective (capot insonorisant) → 3. Signalisation → 4. EPI (en dernier recours et en complément).

5. **Sous-traitance non coordonnée :**
   - *Erreur :* Laisser intervenir une entreprise extérieure sur le site sans Plan de Prévention (article L.4511-1 du Code du Travail), sans inspection commune préalable, ni permis de travail.
   - *Correction :* Établir systématiquement un Plan de Prévention écrit pour toute intervention sous-traitée, avec analyse des risques de coactivité, inspection commune des lieux, permis de feu pour les travaux par point chaud, et suivi quotidien de l'intervention.

## Références

- **ISO 45001:2018** : Systèmes de management de la santé et de la sécurité au travail — Exigences.
- **OHSAS 18001** (remplacée, mais toujours référencée dans certains contrats).
- **ILO-OSH 2001** : Principes directeurs concernant les systèmes de gestion de la SST (OIT).
- **Code du Travail (France)** : Articles L.4121-1 à L.4121-5 (principes généraux de prévention), articles R.4511-1 à R.4511-5 (plan de prévention).
- **Décret n°2001-1016** : Document Unique d'Évaluation des Risques (DUER).
- **INRS** (Institut National de Recherche et de Sécurité) : Guides pratiques et fiches techniques — https://www.inrs.fr/
- **CARSAT** : Référentiels et aides à la prévention des risques professionnels.

## Liste de vérification (Checklist)

- [ ] **L'évaluation des risques professionnels (EvRP)** couvre l'ensemble des postes de travail physiques (production, maintenance, logistique, laboratoire, bureaux) et les tâches de toutes les équipes (posté, journée, nuit).
- [ ] Une **procédure de consignation (LOTO) multi-énergies** claire est rédigée pour chaque machine critique et validée par le responsable sécurité.
- [ ] Les **protections collectives** (barrages physiques, capots de protection, aspiration des fumées, silencieux) sont privilégiées par rapport aux EPI (gants, lunettes, bouchons d'oreilles).
- [ ] Les **indicateurs de sécurité** (TF, TG, near-miss) sont calculés mensuellement et affichés dans les espaces communs pour mesurer l'efficacité de la prévention.
- [ ] Le **Document Unique (DUER)** est à jour (mis à jour dans l'année) et accessible à l'ensemble du personnel.
- [ ] Les **procédures d'urgence** (incendie, déversement chimique, accident grave, blessure) sont affichées, connues du personnel et testées par des exercices au moins semestriels.
- [ ] Les **formations SST** (sauveteur secouriste du travail, gestes et postures, habilitations électriques) sont à jour pour chaque collaborateur.

- [ ] Les **plans de prévention** avec les entreprises extérieures sont signés, joints aux bons de commande et mis à jour annuellement.
- [ ] Un **registre des accidents / incidents** (incluant les presqu'accidents) est tenu et analysé régulièrement (revue mensuelle HSE).
- [ ] La **direction** réalise une revue de management SST au moins une fois par an (conformément à l'ISO 45001 §9.3).

