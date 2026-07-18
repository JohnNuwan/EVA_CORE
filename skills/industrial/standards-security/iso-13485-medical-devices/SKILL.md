---
name: iso-13485-medical-devices
description: "Implémenter un système de management qualité (SMQ) pour dispositifs médicaux conforme à ISO 13485 et FDA 21 CFR Part 820 (QSR)."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [iso-13485, medical-devices, fda-820, qsr, quality-management, ce-marking, mdr, sterilization, biocompatibility]
    related_skills: [gmp-pharmaceutical, iso-quality, iso-27001, industrial-risk-analysis-hazop]
    difficulty: advanced
    industry_sectors: [medical-devices, in-vitro-diagnostics, pharmaceuticals, biotech]
---

# Dispositifs Médicaux — ISO 13485 & FDA 21 CFR Part 820

## Vue d'ensemble

La norme **ISO 13485:2016** (dispositifs médicaux — SMQ) et **FDA 21 CFR Part 820** (Quality System Regulation — QSR) définissent les exigences qualité pour la conception, la fabrication, l'installation et le service après-vente des dispositifs médicaux. Elles couvrent l'ensemble du cycle de vie, de la conception au retrait du marché.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'implémenter un SMQ conforme ISO 13485 pour dispositifs médicaux.
- De répondre aux exigences FDA QSR (21 CFR Part 820) pour le marché US.
- De préparer un marquage CE (MDR 2017/745) ou FDA Premarket Notification (510k).
- De gérer la gestion des risques (ISO 14971) pour dispositifs.
- De structurer un dossier de conception (DHF) et historique de fabrication (DHR).

---

## 1. ISO 13485 vs FDA QSR — Correspondance

| Domaine | ISO 13485:2016 | FDA 21 CFR Part 820 |
|:---|:---|:---|
| Management qualité | §5.0 — Responsabilité direction | §820.20 — Management |
| Conception | §7.3 — Conception & développement | §820.30 — Design Controls |
| Achats | §7.4 — Achats | §820.50 — Purchasing Controls |
| Production | §7.5 — Production & prestation | §820.70 — Production & Process Controls |
| Équipements | §7.6 — Maîtrise équipements | §820.72 — Inspection, Measuring & Test Equipment |
| Traçabilité | §7.5.9 — Traçabilité | §820.65 — Traceability (implantables) |
| CAPA | §8.5.2 — Actions correctives | §820.100 — Corrective & Preventive Action |
| Audits internes | §8.2.4 — Audit interne | §820.22 — Quality Audit |
| Risques | ISO 14971 | ISO 14971 (reconnue FDA) |

---

## 2. Gestion des Risques (ISO 14971)

```yaml
Processus gestion des risques (ISO 14971:2019 / EN 62366):
  1. Analyse des risques:
     - Identification des dangers (électrique, mécanique, biologique, logiciel)
     - Estimation de la probabilité P et sévérité S
     - Niveau de risque = P × S

  2. Évaluation des risques:
     - Acceptable / Inacceptable
     - Fonction des critères définis dans le plan RMS

  3. Maîtrise des risques:
     - Sécurité intrinsèque (design)
     - Mesures techniques (barrière, alarme)
     - Information de sécurité (étiquetage, manuel)

  4. Évaluation du risque résiduel:
     - Acceptable si maîtrisé selon l'état de l'art

  5. Revue de gestion des risques:
     - À chaque étape du cycle de vie
     - Documentée dans le Risk Management File (RMF)
```

---

## 3. Pièges Courants

1. **Design Controls absents ou incomplets :**
   - *Erreur* : Dossier de conception (DHF) sans spécifications d'entrée ni validation clinique.
   - *Correction* : Établir un Design History File avec User Needs → Design Input → Design Output → Verification → Validation.

2. **Biocompatibilité non évaluée :**
   - *Erreur* : Matériaux en contact avec le patient sans tests ISO 10993.
   - *Correction* : Plan d'évaluation biologique (ISO 10993-1) + tests (cytotoxicité, sensibilisation, irritation).

3. **Stérilisation non validée :**
   - *Erreur* : Utilisation de méthodes de stérilisation sans validation ISO 11135/11137.
   - *Correction* : Validation selon ISO 11135 (EtO) ou ISO 11137 (irradiation) avec SAL 10⁻⁶.

---

## Liste de vérification

- [ ] Le SMQ ISO 13485 est documenté avec manuel qualité, procédures et enregistrements.
- [ ] Le Design History File (DHF) contient les entrées, sorties, vérifications et validations de conception.
- [ ] La gestion des risques (ISO 14971) est intégrée à chaque processus.
- [ ] Les équipements de mesure sont étalonnés selon un plan défini.
- [ ] Le système CAPA (Corrective and Preventive Action) est en place avec analyse de cause racine.
- [ ] La traçabilité des dispositifs implantables est assurée lot par lot.
- [ ] Les audits internes sont planifiés (≥ 1 fois/an).
- [ ] La revue de direction est réalisée annuellement.
