---
name: iso-standards-for-industry
description: "Comprendre, implémenter et certifier les normes ISO (9001, 14001, 45001, 50001) dans les environnements industriels et de production."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [iso, standards, quality, environment, safety, energy, certification, compliance]
    related_skills: [combining-industry40-security-iso, industrial-cybersecurity-guidelines, iso-standards-for-industry]
---

# Normes ISO pour l'Industrie

## Vue d'ensemble

Cette compétence guide l'implémentation des **normes ISO** dans les environnements industriels. Elle couvre les normes les plus courantes (ISO 9001 qualité, ISO 14001 environnement, ISO 45001 santé-sécurité, ISO 50001 énergie) ainsi que leur intégration dans un système de management unifié (SMSI). Un accent particulier est mis sur l'articulation entre ces normes et les systèmes connectés de l'Industrie 4.0.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'accompagner une démarche de certification ISO dans une usine ou un atelier.
- De cartographier les processus qualité (ISO 9001) dans un MES ou un ERP.
- D'intégrer les exigences environnementales (ISO 14001) dans un système de production.
- De préparer un audit ISO ou de répondre à des non-conformités.
- D'aligner la cybersécurité OT avec les exigences des normes de management.

---

## 1. Panorama des Normes ISO pour l'Industrie

### 1.1 Tableau Synthétique

| Norme | Domaine | Référence Clé | Public Cible |
|:---|:---|:---|:---|
| **ISO 9001** | Management de la qualité | Processus, amélioration continue, satisfaction client | Toute organisation industrielle |
| **ISO 14001** | Management environnemental | Impacts environnementaux, conformité légale, prévention pollution | Sites de production |
| **ISO 45001** | Santé et sécurité au travail | Identification des dangers, maîtrise des risques SST | Usines, ateliers, chantiers |
| **ISO 50001** | Management de l'énergie | Performance énergétique, indicateurs (EnPI), conception | Sites industriels énergivores |
| **ISO 27001** | Sécurité de l'information | SI, données, cybersécurité | TI/OT, services informatiques |
| **ISO 22000** | Sécurité des denrées alimentaires | HACCP, traçabilité, allergènes | IAA (Industrie Agro-Alimentaire) |

### 1.2 Structure Harmonisée (High-Level Structure — HLS)

Depuis 2012, toutes les nouvelles normes ISO de système de management adoptent une structure commune en 10 clauses :

1. **Domaine d'application**
2. **Références normatives**
3. **Termes et définitions**
4. **Contexte de l'organisme** (interne/externe, parties intéressées)
5. **Leadership** (engagement, politique, rôles)
6. **Planification** (risques et opportunités, objectifs)
7. **Support** (ressources, compétences, communication, documentation)
8. **Réalisation des activités opérationnelles**
9. **Évaluation des performances** (surveillance, audit, revue de direction)
10. **Amélioration** (non-conformité, action corrective, amélioration continue)

> Cette structure harmonisée permet l'intégration facile de plusieurs normes dans un **Système de Management Intégré (SMI)** unique.

---

## 2. Mise en Œuvre par Norme

### 2.1 ISO 9001:2015 — Qualité

**Exigences documentaires minimales :**
- Procédures documentées pour la maîtrise des documents et des enregistrements.
- Politique qualité et objectifs qualité mesurables.
- Manuel qualité (optionnel mais recommandé).

**Exemple d'objectif qualité :**
```
Objectif : Réduire le taux de rebut de 3% à 1,5% d'ici 12 mois.
Indicateur : Taux de rebut = (pièces rebutées / pièces produites) × 100
Moyen : Contrôle statistique des processus (SPC), formation opérateurs
Revue : Mensuelle en réunion de production
```

### 2.2 ISO 14001:2015 — Environnement

**Aspects environnementaux typiques en industrie :**
| Aspect | Impact | Maîtrise |
|:---|:---|:---|
| Rejets atmosphériques | Pollution air | Filtres, cyclones, mesure COV |
| Effluents liquides | Pollution eau | Station d'épuration, neutralisation |
| Déchets (DIB, DIS) | Pollution sol | Tri, filière agréée, bordereau de suivi |
| Consommation énergétique | Épuisement ressources | ISO 50001, bilan carbone |
| Bruit | Nuisance sonore | Capotage, silencieux, mesure |

### 2.3 ISO 45001:2018 — Santé et Sécurité

**Processus d'identification des dangers :**
```yaml
Danger: Machine rotative sans protection
Risque: Harcèlement / happement
Mesures existantes: Barrière immatérielle
Niveau de risque: 12 (critique)
Actions: Ajout d'un sectionneur cadenassable + procédure de consignation
Échéance: J+30
Responsable: Responsable maintenance
```

---

## 3. Intégration avec les Systèmes Industrie 4.0

Les normes ISO ne doivent pas être traitées indépendamment des systèmes connectés :

| Norme | Élément Industrie 4.0 | Intégration |
|:---|:---|:---|
| **ISO 9001** §7.5 | MES / ERP | Documents qualité numériques, workflow de validation |
| **ISO 9001** §9.1 | IoT / SCADA | Surveillance temps réel des indicateurs qualité |
| **ISO 14001** §6.1 | Capteurs environnementaux | Monitoring continu des rejets et consommation |
| **ISO 45001** §6.1 | IoT sécurité | Détection de présence, port des EPI connectés |
| **ISO 50001** §6.3 | Compteurs intelligents | EnPI temps réel, alertes de dérive énergétique |

---

## 4. Pièges Courants

1. **Surdocumentation :**
   - *Erreur* : Créer des centaines de documents sans valeur ajoutée opérationnelle.
   - *Correction* : ISO 9001:2015 ne requiert que 7 documents obligatoires. Le reste est libre.

2. **ISO comme contrainte et non comme levier :**
   - *Erreur* : Implémenter la norme pour « passer l'audit » sans chercher l'amélioration réelle.
   - *Correction* : Aligner les objectifs ISO avec les KPI de production (rendement, qualité, sécurité).

3. **Séparation IT/OT dans l'ISO 27001 :**
   - *Erreur* : Appliquer les mesures de sécurité IT sans tenir compte des contraintes OT (disponibilité, latence).
   - *Correction* : Utiliser le guide IEC 62443 comme complément OT à l'ISO 27001.

---

## Liste de vérification

- [ ] La norme cible est identifiée (9001, 14001, 45001, 50001, 27001) avec son année de version.
- [ ] Le contexte de l'organisme (clause 4) est documenté (interne/externe, parties intéressées).
- [ ] Les risques et opportunités (clause 6.1) sont identifiés et évalués.
- [ ] Les documents obligatoires sont créés (politique, objectifs, procédures, enregistrements).
- [ ] Un plan d'audit interne est établi (fréquence ≥ 1 fois par an).
- [ ] La revue de direction (clause 9.3) est programmée avec un ordre du jour défini.
- [ ] Les non-conformités sont tracées avec actions correctives et vérification d'efficacité.
