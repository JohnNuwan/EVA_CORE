---
name: iso-22716-cosmetics-gmp
description: "Appliquer les Bonnes Pratiques de Fabrication des produits cosmétiques conformes à l'ISO 22716 et au Règlement Européen Cosmétiques (CE) N° 1223/2009."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [iso-22716, cosmetics, gmp, cosmetovigilance, product-safety, cpnp, eu-cosmetics-regulation]
    related_skills: [gmp-pharmaceutical, iso-quality, iso-22000, industrial-risk-analysis-hazop]
    difficulty: intermediate
    industry_sectors: [cosmetics, personal-care, perfumery, toiletries]
---

# Cosmétiques — ISO 22716 & Règlement Européen CE 1223/2009

## Vue d'ensemble

L'**ISO 22716:2007** (Bonnes Pratiques de Fabrication — GMP Cosmétiques) et le **Règlement (CE) N° 1223/2009** définissent les exigences pour la fabrication, le contrôle et la mise sur le marché des produits cosmétiques. Elles couvrent la sécurité du produit, la fabrication, le conditionnement et la cosmétovigilance.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'implémenter les GMP cosmétiques (ISO 22716) sur un site de production.
- De préparer un Dossier d'Information Produit (DIP) pour notification CPNP.
- De gérer la sécurité des produits cosmétiques (toxicologie, évaluation).
- De structurer le contrôle qualité des matières premières et produits finis.

---

## 1. Structure ISO 22716

| Chapitre | Domaine | Exigences Clés |
|:---|:---|:---|
| 4 | Personnel | Formation, hygiène, santé, tenue |
| 5 | Locaux | Zonage (sec/humide), surfaces lavables, flux |
| 6 | Équipements | Conception, nettoyage, maintenance |
| 7 | Matières premières | Réception, échantillonnage, quarantaine |
| 8 | Production | Pesée, mélange, conditionnement, libération |
| 9 | Produits finis | Contrôle, libération, stabilité |
| 10 | Laboratoire | Méthodes, étalonnage, validation |
| 11 | Documentation | Spécifications, dossiers de lot, SOP |

---

## 2. Contrôle Microbiologique Cosmétique

```yaml
Limites microbiologiques (ISO 17516 / Ph. Eur.):
  Catégorie 1 (produits pour enfants, contour des yeux):
    - Bactéries aérobies totales: ≤ 100 UFC/g
    - Levures/moisissures: ≤ 10 UFC/g
    - Pseudomonas aeruginosa: Absence / 1g
    - Staphylococcus aureus: Absence / 1g
  
  Catégorie 2 (autres cosmétiques):
    - Bactéries aérobies totales: ≤ 1000 UFC/g
    - Levures/moisissures: ≤ 100 UFC/g
    - Pseudomonas aeruginosa: Absence / 1g
    - Staphylococcus aureus: Absence / 1g
```

---

## 3. Pièges Courants

1. **DIP (Dossier d'Information Produit) incomplet :**
   - *Erreur* : Pas d'évaluation de sécurité toxicologique signée par un évaluateur qualifié.
   - *Correction* : Faire réaliser le safety assessment par un toxicologue (exigence Art. 10-11 CE 1223/2009).

2. **Allégations non justifiées :**
   - *Erreur* : Mentionner « dermatologiquement testé » ou « hypoallergénique » sans dossier justificatif.
   - *Correction* : Préparer un dossier d'évidence des allégations (claims substantiation).

---

## Liste de vérification

- [ ] Le site applique les GMP ISO 22716 (documenté et audité).
- [ ] Le Dossier d'Information Produit (DIP) est complet avec évaluation de sécurité.
- [ ] Les produits sont notifiés sur le portail CPNP avant mise sur le marché.
- [ ] Les limites microbiologiques sont respectées (ISO 17516).
- [ ] La cosmétovigilance est organisée (déclaration des effets indésirables).
