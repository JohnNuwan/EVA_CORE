---
name: cleanroom-sterile-environments
description: "Concevoir, auditer et maîtriser des environnements propres et stériles : zonage, HVAC, monitoring, flux et discipline d'exploitation."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [industrial, cleanroom, sterile, hvac, monitoring, gmp, pharma, medical, iso-14644]
    related_skills: [gmp-pharmaceutical, iso-13485-medical-devices, multi-sector-industrial-standards]
---

# Environnements propres et stériles

## Vue d'ensemble

Cette compétence sert à concevoir, auditer et remettre à niveau des environnements propres et stériles : salles blanches, zones aseptiques, sas, flux personnel/matière, pressions différentielles, HVAC, maîtrise particulaire, maîtrise microbiologique, nettoyage/désinfection et monitoring environnemental.

Elle vise un usage professionnel orienté audit, qualification d'exploitation et préparation d'inspection. Le cœur du sujet n'est pas uniquement la classe de salle : c'est la cohérence entre zoning, HVAC, discipline opérationnelle, nettoyage et interprétation des données de monitoring.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Structurer une zone propre ou stérile pharma/médical.
- Préparer un audit de salle propre.
- Définir les classes propres, les flux et les sas.
- Concevoir un plan de monitoring particulaire et microbiologique.
- Évaluer les risques de contamination croisée ou de perte de maîtrise environnementale.
- Formaliser une stratégie de contamination control.

À proscrire pour :
- Les seules questions GMP process sans dimension environnement propre : utiliser `gmp-pharmaceutical`.
- Les simples exigences bio / séparation de flux non stériles : utiliser `biological-organic-compliance`.

## Référentiel utile

### Références principales
- EU GMP Annex 1.
- ISO 14644 (salles propres).
- stratégie interne de contamination control.
- procédures d'habillage, nettoyage, désinfection et monitoring.

### Traduction pratique
Un environnement propre n'est fiable que si 5 éléments restent cohérents :
1. zoning et cascades de pression ;
2. HVAC et renouvellement d'air ;
3. flux personnel / matière ;
4. discipline opérationnelle ;
5. monitoring et gestion des excursions.

## Méthode de travail pas à pas

### Étape 1 — Définir le périmètre et les zones
Documenter :
- classes propres visées ;
- zones critiques / moins critiques ;
- sas personnel ;
- sas matière ;
- zones de nettoyage ;
- points de changement de tenue ;
- transferts inter-zones.

### Étape 2 — Définir la logique HVAC
Toujours expliciter :
- cascade de pression ;
- sens des flux d'air ;
- filtration ;
- température / humidité ;
- redondance si nécessaire ;
- alarmes HVAC critiques.

### Étape 3 — Définir les flux d'exploitation
Pour chaque zone, décrire :
- qui entre ;
- comment il s'habille ;
- ce qui entre ;
- comment la matière transite ;
- où se trouvent les points de rupture de maîtrise.

### Étape 4 — Construire le plan de monitoring
Définir :
- points de mesure ;
- paramètres ;
- fréquence ;
- seuils alerte / action ;
- règles de trending ;
- traitement des excursions ;
- responsabilités CAPA.

### Étape 5 — Préparer l'audit / inspection
Constituer un dossier avec :
- matrice de zoning ;
- plan de monitoring ;
- historiques d'alarmes ;
- procédures d'habillage ;
- procédures de nettoyage ;
- justifications des classes et des flux.

## Matrice de décision rapide

| Sujet | Question à trancher | Critère principal |
|---|---|---|
| Zoning | combien de zones / classes | criticité produit et procédé |
| Pression différentielle | niveau de cascade | protection zone critique |
| Monitoring | continu ou périodique | criticité et fréquence d'exposition |
| Habillage | standard ou renforcé | criticité microbiologique/particulaire |
| Nettoyage | fréquence et produits | niveau de risque et historique excursions |

## Livrables professionnels attendus

### Minimum pour un projet sérieux
- matrice zoning ;
- plan de monitoring environnemental ;
- procédure habillage / entrée / sortie ;
- logique HVAC et cascade de pression ;
- checklist d'audit ;
- modèle de rapport d'audit.

### Minimum pour un audit
- cohérence zoning / flux / HVAC ;
- tendances de monitoring ;
- gestion des excursions ;
- preuve de discipline opérationnelle ;
- plan d'action sur écarts.

## Cas d'usage terrain

### Zone de préparation propre pharma
Points critiques :
- flux matière ;
- habillage ;
- pression différentielle ;
- nettoyage entre campagnes.

### Zone stérile / aseptique
Points critiques :
- environnement critique ;
- surveillance renforcée ;
- interventions humaines ;
- gestion des excursions microbiologiques.

### Environnement propre médical
Points critiques :
- cohérence documentaire ;
- discipline d'exploitation ;
- qualification HVAC ;
- preuves auditables.

## Pièges Courants (Common Pitfalls)

1. Sous-estimer les flux croisés personnel/matière.
   - Symptôme : points de contamination difficilement expliqués.
   - Correction : revoir sas, circulations et règles de franchissement.

2. Ne pas relier HVAC et discipline opérationnelle.
   - Symptôme : salle techniquement conforme mais dérives récurrentes en exploitation.
   - Correction : traiter la salle comme un système global, pas comme un seul lot HVAC.

3. Faire du monitoring sans stratégie d'interprétation claire.
   - Symptôme : données accumulées mais peu exploitables.
   - Correction : définir seuils, revue périodique, CAPA et responsabilités.

4. Gérer le nettoyage comme une routine générique.
   - Symptôme : variabilité de maîtrise entre équipes ou postes.
   - Correction : formaliser produits, fréquences, méthodes et preuves.

5. Penser uniquement en classe ISO sans logique procédé.
   - Symptôme : solution coûteuse mais pas forcément adaptée.
   - Correction : partir du risque produit/procédé puis définir le zoning.

## Checklist de validation finale
- [ ] Le zonage et les classes propres sont définis.
- [ ] Les cascades de pression sont documentées.
- [ ] Les flux personnel / matière sont explicités.
- [ ] La stratégie HVAC est cohérente avec la criticité des zones.
- [ ] Le plan de monitoring est défini avec seuils et gestion des excursions.
- [ ] Les procédures d'habillage et de nettoyage sont en place.
- [ ] Les historiques et preuves auditables sont accessibles.
- [ ] Les écarts sont traités dans une logique CAPA.
