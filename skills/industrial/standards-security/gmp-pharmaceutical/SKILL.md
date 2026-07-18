---
name: gmp-pharmaceutical
description: "Implémenter les Bonnes Pratiques de Fabrication (GMP) pharmaceutiques : BPF, FDA 21 CFR Part 11/210/211, ICH Q7/Q10, EU GMP Annex 1, validation des procédés et qualité pharmaceutique."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [gmp, pharmaceutical, fda, bpF, ich-q7, ich-q10, validation, cfr21-part11, eu-gmp, quality-by-design, pharma-manufacturing]
    related_skills: [iso-22000, iso-quality, industrial-risk-analysis-hazop, cleanroom-sterile]
    difficulty: advanced
    industry_sectors: [pharmaceutical, biotech, medical-devices, cosmetics]
---

# Bonnes Pratiques de Fabrication (GMP / BPF) Pharmaceutiques

## Vue d'ensemble

Les **Bonnes Pratiques de Fabrication (BPF / GMP — Good Manufacturing Practice)** sont l'ensemble des exigences de qualité et de sécurité pour la fabrication des médicaments à usage humain et vétérinaire. Elles couvrent l'intégralité du cycle de vie du produit, de la réception des matières premières à l'expédition du produit fini. Les GMP sont encadrées par les autorités réglementaires : FDA (États-Unis), EMA (Europe), ANSM (France), WHO (international).

### Référentiels Clés

| Référentiel | Domaine | Autorité | Applicabilité |
|:---|:---|:---|:---|
| **FDA 21 CFR Part 210/211** | GMP médicaments | FDA (USA) | Toute fabrication pharmaceutique pour le marché US |
| **FDA 21 CFR Part 11** | Signatures électroniques, données informatisées | FDA (USA) | Systèmes informatisés (SCADA, MES, LIMS) |
| **FDA 21 CFR Part 820** | Système qualité dispositifs médicaux | FDA (USA) | Dispositifs médicaux (remplacé par ISO 13485) |
| **EU GMP Guide (EudraLex Vol. 4)** | GMP européennes | EMA / ANSM | Fabrication pour le marché UE |
| **EU GMP Annex 1** | Fabrication de produits stériles | EMA | Aseptique, cleanroom |
| **ICH Q7** | GMP des principes actifs (API) | ICH (international) | Fabrication de substances actives |
| **ICH Q10** | Système qualité pharmaceutique (PQS) | ICH | Management qualité intégré |
| **WHO GMP** | GMP recommandations internationales | OMS | Pays sans réglementation propre |
| **PIC/S** | Schéma de coopération en inspection pharmaceutique | PIC/S | Harmonisation des inspections |

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'implémenter un système qualité pharmaceutique (PQS) conforme GMP.
- De rédiger des procédures opératoires standardisées (SOP) pour un atelier pharmaceutique.
- De concevoir un plan de validation (procédé, nettoyage, système informatisé).
- De préparer un dossier de lot (Batch Record) ou un Dossier de Fabrication.
- De répondre à une inspection FDA, EMA ou ANSM.
- D'auditer un fournisseur de principes actifs (API) selon ICH Q7.

**Ne pas utiliser pour :**
- La sécurité alimentaire (utiliser `iso-22000`).
- Les cosmétiques simples (utiliser `iso-22716` si disponible).
- Les dispositifs médicaux (utiliser `iso-13485` si disponible).

---

## 1. Les 10 Piliers des GMP

### 1.1 Tableau des Exigences

| Pilier | Description | Référence Clé |
|:---|:---|:---|
| **1. Locaux et équipements** | Conception adaptée, surfaces lavables, flux matière/personnel | EU GMP Ch. 3, FDA 211.42 |
| **2. Personnel** | Formation initiale et continue, hygiène, habilitation | EU GMP Ch. 2, FDA 211.25 |
| **3. Documentation** | SOP, dossiers de lot, spécifications, enregistrements | EU GMP Ch. 4, FDA 211.180 |
| **4. Production** | Contrôle en cours, prévention des contaminations croisées | EU GMP Ch. 5, FDA 211.100 |
| **5. Contrôle qualité** | Laboratoire, échantillonnage, stabilité | EU GMP Ch. 6, FDA 211.160 |
| **6. Sous-traitance** | Qualification des fournisseurs, contrats qualité | EU GMP Ch. 7 |
| **7. Réclamations et rappels** | Gestion des non-conformités, rappels de lots | EU GMP Ch. 8, FDA 211.198 |
| **8. Auto-inspections** | Audits internes réguliers | EU GMP Ch. 9 |
| **9. Validation** | Procédé, nettoyage, méthodes analytiques, systèmes informatisés | EU GMP Annex 15, FDA 211.110 |
| **10. Gestion des risques qualité** | ICH Q9, FMEA, HACCP pharmaceutique | ICH Q9 |

---

## 2. FDA 21 CFR Part 11 — Signatures et Données Électroniques

### 2.1 Exigences pour les Systèmes Informatisés (SCADA, MES, LIMS)

| Exigence | Description | Implémentation |
|:---|:---|:---|
| **Validation** | Le système doit être validé pour l'usage prévu | IQ/OQ/PQ documenté |
| **Audit Trail** | Piste d'audit protégée (lecture seule) | Logs horodatés, non modifiables |
| **Signatures électroniques** | Équivalent des signatures manuscrites | Identifiant unique + mot de passe + bi‑clé |
| **Sécurité** | Contrôle d'accès, prévention des accès non autorisés | LDAP, RBAC, MFA |
| **Intégrité des données** | ALCOA+ (Attribuable, Lisible, Contemporain, Original, Exact) | Validation des champs, contrôles redondance |

**Exemple : Configuration d'Audit Trail pour SCADA pharmaceutique**

```yaml
audit_trail:
  enabled: true
  events_logged:
    - modification_consigne
    - changement_mode_marche
    - alarme_critique
    - changement_recette
    - arrêt_urgence
  storage: write_once_read_many (WORM)
  retention: 10 ans
  integrity: SHA-256 hash chain
  export: CSV signé numériquement
```

---

## 3. Validation de Procédé Pharmaceutique

### 3.1 Cycle de Validation (EU GMP Annex 15 / FDA Process Validation)

```
1. Stage 1 — Conception du procédé (Process Design)
   - Définition des paramètres critiques (CPP) et attributs qualité critiques (CQA)
   - Études de développement, DoE (Design of Experiments)

2. Stage 2 — Qualification du procédé (Process Qualification)
   - IQ (Installation Qualification) : Équipement installé selon specs
   - OQ (Operational Qualification) : Fonctionnement dans les limites opérationnelles
   - PQ (Performance Qualification) : Répétabilité du procédé (3 lots consécutifs)

3. Stage 3 — Vérification continue (Continued Process Verification)
   - Monitoring statistique en routine (SPC)
   - Réévaluation périodique des CPP
```

### 3.2 Plan de Validation Type

```python
import pandas as pd

# Définition des paramètres critiques (CPP)
cpp_table = pd.DataFrame({
    "CPP": ["Température granulation", "Vitesse mélangeur", "Temps séchage"],
    "CQA_associé": ["Taux humidité résiduelle", "Homogénéité dosage", "Taille particules"],
    "Limite_acceptable": ["70-85°C", "150-250 RPM", "≤ 2.0% H2O"],
    "Méthode_surveillance": ["SCADA Pt100", "Variateur → SCADA", "Balance halogène"],
    "Fréquence": ["Continue", "Continue", "Chaque lot"],
})

def genere_rapport_validation(cpp_df: pd.DataFrame, resultats_lot: dict) -> str:
    """Génère un rapport de validation de lot conforme GMP.

    Args:
        cpp_df: Tableau des CPP avec limites acceptables.
        resultats_lot: Dictionnaire des mesures par CPP.

    Returns:
        str: Rapport formaté.
    """
    rapport = "RAPPORT DE VALIDATION LOT — GMP\n"
    rapport += "=" * 50 + "\n"
    for _, row in cpp_df.iterrows():
        cpp = row["CPP"]
        mesure = resultats_lot.get(cpp, "N/A")
        limite = row["Limite_acceptable"]
        statut = "✅ CONFORME" if mesure != "N/A" else "❌ NON CONFORME"
        rapport += f"\n{row['CPP']} : {mesure} (limite {limite}) → {statut}"
    return rapport

resultats = {"Température granulation": "78°C", "Vitesse mélangeur": "200 RPM"}
print(genere_rapport_validation(cpp_table, resultats))
```

---

## 4. Qualification des Équipements (IQ/OQ/PQ)

### 4.1 Exemple : IQ d'un Pasteurisateur Pharmaceutique

```yaml
IQ_PASTEURISATEUR_L01:
  équipement: Pasteurisateur Flash Sterilizer
  fabricant: Tetra Pak / Alfa Laval
  tag: PASTEUR-001

  documentation_technique:
    - manuel_utilisateur: OK
    - schéma_P&ID: OK
    - plan_électrique: OK
    - certificat_matériaux: OK (AISI 316L)
    - certificat_étalonnage_capteurs: OK (Pt100, débitmètre)

  installation:
    alimentation_électrique: 400V / 50Hz / 32A
    alimentation_vapeur: 6 bar(g)
    alimentation_eau_GS: 3 bar
    raccordements: Conforme au P&ID
    mise_à_terre: OK (< 1 ohm)

  tests_fonctionnels:
    - test_vanne_dérivation: OK
    - test_pompe_recirculation: OK
    - test_arrêt_urgence: OK
    - test_enregistrement_température: OK

  conclusion: IQ PASSÉE — 2026-06-24
```

---

## 5. Pièges Courants

1. **Données non ALCOA+ :**
   - *Symptôme* : Données modifiables sans piste d'audit (ex: fichier Excel non protégé).
   - *Cause* : Système non validé 21 CFR Part 11.
   - *Solution* : Migrer vers un système avec audit trail (SCADA validé, LIMS, MES batch).

2. **Contamination croisée :**
   - *Symptôme* : Résidus de principe actif A retrouvés dans le lot B.
   - *Cause* : Nettoyage insuffisant entre campagnes.
   - *Solution* : Validation du nettoyage (swab tests, rinse samples) + CAM (Campaign Management).

3. **Dossier de lot incomplet :**
   - *Symptôme* : Écarts non documentés, signatures manquantes.
   - *Cause* : Opérateurs non formés ou procédure trop complexe.
   - *Solution* : MEB (Manufacturing Execution System) avec workflow guidé et contrôles bloquants.

4. **Fournisseur d'API non qualifié :**
   - *Symptôme* : Principe actif hors spécifications.
   - *Cause* : Audit fournisseur non réalisé.
   - *Solution* : Audit ICH Q7 du fabricant d'API, plan d'actions correctives.

5. **Stabilité non suivie :**
   - *Symptôme* : Produit dégradé avant date de péremption.
   - *Cause* : Études de stabilité non réalisées ou sous dimensionnées.
   - *Solution* : Plan de stabilité (ICH Q1A) : long terme + accéléré + suivi post-commercialisation.

---

## Liste de vérification

- [ ] Le système qualité pharmaceutique (PQS / ICH Q10) est documenté.
- [ ] Les procédures (SOP) couvrent les 10 piliers GMP.
- [ ] Les équipements critiques sont qualifiés (IQ/OQ/PQ).
- [ ] Les procédés critiques sont validés (3 lots consécutifs conformes).
- [ ] Les systèmes informatisés (SCADA, MES, LIMS) sont validés 21 CFR Part 11.
- [ ] Les données respectent ALCOA+ (Attribuable, Lisible, Contemporain, Original, Exact).
- [ ] Les fournisseurs de matières premières et API sont audités (ICH Q7).
- [ ] Le plan de validation nettoyage est documenté et exécuté.
- [ ] Les études de stabilité (ICH Q1A) sont en place.
- [ ] Un plan d'auto-inspection / audit interne est programmé annuellement.
