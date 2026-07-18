---
name: hydraulic-industrial-standards
description: "Concevoir, auditer et fiabiliser des systèmes hydrauliques industriels selon les exigences de sécurité, de propreté fluide et de maintenabilité."
version: 2.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [industrial, hydraulic, fluid-power, iso-4413, iso-4406, pressure, filtration, maintenance, safety]
    related_skills: [multi-sector-industrial-standards, electrical-schematics-eplan, process-chemical-water]
---

# Hydraulique industrielle

## Vue d'ensemble

Cette compétence sert à concevoir, auditer et remettre à niveau des systèmes hydrauliques industriels de façon professionnelle. Elle couvre les groupes hydrauliques, pompes, distributeurs, vérins, moteurs hydrauliques, accumulateurs, filtration, sécurité des charges, propreté fluide et stratégie de maintenance.

Elle est adaptée aux presses, centrales hydrauliques, axes de levage, machines lourdes, bancs de test, équipements de process et machines spéciales où la densité de puissance et la maîtrise des charges sont critiques.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Concevoir un circuit hydraulique industriel.
- Dimensionner pression, débit, puissance, accumulation et refroidissement.
- Définir les sécurités liées aux charges suspendues ou à l'énergie stockée.
- Auditer la propreté fluide et la filtration.
- Diagnostiquer échauffement, dérives de performance, cavitation ou pics de pression.
- Structurer un plan de maintenance ou d'amélioration de fiabilité hydraulique.

À proscrire pour :
- Les systèmes majoritairement pneumatiques : utiliser `pneumatic-industrial-standards`.
- Les seules questions de conformité électrique : utiliser `electrical-distribution-protection` ou `electrical-schematics-eplan`.

## Référentiel normatif utile

### Normes principales
- ISO 4413 : règles générales et exigences de sécurité des systèmes hydrauliques.
- ISO 4406 : codification de la contamination particulaire.
- ISO 1219 : symboles et schémas fluidiques.
- ISO 12100 : cadre de réduction des risques machine.
- ISO 13849 / IEC 62061 : si l'hydraulique participe à une fonction de sécurité.

### Conséquence pratique
En hydraulique, la conformité ne suffit pas : il faut aussi maîtriser la propreté fluide, l'énergie stockée, la température, les charges, la stabilité dynamique et la maintenabilité terrain.

## Méthode de travail pas à pas

### Étape 1 — Définir la fonction physique
Pour chaque organe piloté, documenter :
- effort ou couple requis ;
- vitesse ;
- maintien de charge ;
- comportement en arrêt ;
- précision ;
- cycle thermique ;
- criticité sécurité.

### Étape 2 — Définir l'enveloppe hydraulique
Toujours relever ou fixer :
- pression nominale ;
- pics admissibles ;
- débit moyen et débit de pointe ;
- puissance installée ;
- volume réservoir ;
- viscosité de fonctionnement ;
- température mini / maxi ;
- classe de propreté cible.

### Étape 3 — Construire l'architecture du circuit
Décider explicitement :
- pompe fixe ou variable ;
- régulation pression, débit, charge ;
- accumulateur oui/non ;
- refroidissement nécessaire ou non ;
- type de filtration et position ;
- dispositifs de maintien ou de freinage de charge.

### Étape 4 — Intégrer la sécurité
Vérifier :
- clapets anti-retour pilotés ;
- limiteurs de pression ;
- sécurité de descente ;
- dissipation d'énergie résiduelle ;
- procédure de décompression ;
- isolement maintenance.

### Étape 5 — Préparer l'exploitation et la maintenance
Créer les livrables suivants :
- schéma fluidique ;
- matrice pression/débit/consigne ;
- plan de filtration ;
- plan d'analyse d'huile ;
- seuils d'alerte température/particules ;
- plan de remplacement flexibles/joints/filtres.

## Matrice de décision rapide

| Sujet | Question à trancher | Critère principal |
|---|---|---|
| Pompe | fixe ou variable | profil de charge et rendement |
| Filtration | aspiration / pression / retour | sensibilité composants et propreté cible |
| Accumulateur | nécessaire ou non | pics de demande et stabilité pression |
| Refroidissement | oui/non | bilan thermique |
| Maintien de charge | clapet, valve équilibre, servo | niveau de risque et tenue de position |
| Analyse d'huile | fréquence | criticité machine et coût d'arrêt |

## Livrables professionnels attendus

### Minimum pour un projet sérieux
- schéma fluidique conforme ;
- feuille de dimensionnement pompe / actionneur ;
- plan de propreté et filtration ;
- logique de sécurité hydraulique ;
- procédure de décompression maintenance ;
- plan de maintenance conditionnelle.

### Minimum pour un audit
- pression réelle vs consigne ;
- historique température ;
- classe de propreté mesurée ou cible ;
- cartographie fuites ;
- organes à risque sécurité ;
- recommandations court terme / long terme.

## Cas d'usage terrain

### Presse hydraulique
Points critiques :
- maintien d'effort ;
- sécurité opérateur ;
- pics de pression ;
- température huile ;
- répétabilité du cycle.

### Axe de levage / maintien de charge
Points critiques :
- tenue en position ;
- rupture flexible ;
- descente incontrôlée ;
- énergie résiduelle en maintenance.

### Centrale hydraulique de machine spéciale
Points critiques :
- propreté fluide ;
- accessibilité maintenance ;
- bruit ;
- rendement énergétique.

## Pièges Courants (Common Pitfalls)

1. Ignorer la classe de propreté ISO 4406.
   - Symptôme : usure prématurée, servo-valves instables, dérive de performance.
   - Correction : fixer une classe cible, filtrer et mesurer.

2. Sous-estimer l'échauffement et la dérive de viscosité.
   - Symptôme : comportement différent à froid/chaud, lenteur, pertes d'efficacité.
   - Correction : faire le bilan thermique et prévoir refroidissement si nécessaire.

3. Oublier les risques liés aux charges suspendues et à l'énergie stockée.
   - Symptôme : descente non maîtrisée, mouvements résiduels dangereux.
   - Correction : intégrer dispositifs de maintien, limiteurs et procédure de décompression.

4. Considérer le flexible comme un simple consommable sans criticité.
   - Symptôme : rupture, fuites, pollution, arrêt brutal.
   - Correction : gérer rayon de courbure, durée de vie, inspection périodique et traçabilité.

5. Diagnostiquer uniquement par la pression.
   - Symptôme : panne récurrente non comprise.
   - Correction : surveiller aussi débit, température, contamination et bruit/cavitation.

## Checklist de validation finale
- [ ] Les besoins en effort/couple/vitesse sont documentés.
- [ ] Pression, débit, puissance et température ont été dimensionnés.
- [ ] La classe de propreté cible est spécifiée.
- [ ] La stratégie de filtration est définie.
- [ ] Les fonctions de sécurité hydraulique sont documentées.
- [ ] La procédure de décompression maintenance existe.
- [ ] Les composants critiques (pompes, flexibles, valves, filtres) sont intégrés au plan de maintenance.
- [ ] Les seuils d'alerte température/contamination/fuite sont définis.
