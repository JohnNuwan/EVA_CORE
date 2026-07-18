---
name: siemens-industrial-extraction
description: "Extraire et documenter les technologies d'automatisation Siemens : Simatic, TIA Portal, MindSphere et l'écosystème Digital Enterprise."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags:
      - siemens
      - simatic
      - tia-portal
      - mindsphere
      - industrial-automation
      - plc
      - scada
      - industrie-4.0
      - digital-enterprise
      - extraction
      - documentation
      - iec-62443
      - opc-ua
      - profinet
    related_skills:
      - plc-connectivity
      - siemens-scl
      - industrial-diagnostic
      - ot-audit
      - isa95-modelling
---

# Extraction et Documentation des Technologies Siemens pour l'Automatisation Industrielle

## Vue d'ensemble

Cette compétence guide l'extraction systématique d'informations techniques, de procédures et de bonnes pratiques relatives à l'écosystème d'automatisation Siemens. Elle couvre les trois piliers de la transformation numérique industrielle du groupe :

1. **Simatic (Automate)** — La gamme d'automates programmables (PLC) allant du Simatic S7-1200 (entrée de gamme) au S7-1500 (haut de gamme) et au S7-400 (legacy process).
2. **TIA Portal (Ingénierie)** — L'environnement de développement intégré (Totally Integrated Automation Portal) couvrant la programmation, la configuration et la mise en service.
3. **MindSphere / Industrial IoT (Cloud)** — La plateforme IoT industrielle pour l'analyse de données, la maintenance prédictive et l'optimisation des processus.

### Objectifs de l'extraction

- Constituer une base de connaissance technique exploitable par l'agent Helios pour assister les ingénieurs automaticiens.
- Produire des fiches de référence, des guides pratiques et des checklists de validation.
- Assurer la reproductibilité des recherches face aux contraintes d'accès (CAPTCHA, paywalls, versions régionales).

### Architecture de la collecte

```
Sources d'information
│
├── Site officiel Siemens (new.siemens.com)
│   ├── Pages produits Simatic
│   ├── Documentation TIA Portal
│   └── Portail MindSphere / Insights Hub
│
├── Siemens Industry Online Support (support.industry.siemens.com)
│   ├── Manuels techniques (PDF)
│   ├── FAQ et articles de base de connaissance
│   └── Mise à jour de firmware et compatibility matrix
│
├── Sites techniques tiers
│   ├── GitHub (projets open source Siemens)
│   ├── Stack Overflow / Stack Exchange (questions techniques)
│   └── Forums spécialisés (PLCtalk, MrPLC)
│
└── Ressources additionnelles
    ├── Webinaires et sessions techniques Siemens
    └── Documentation des partenaires (distributeurs, intégrateurs)
```

## Quand l'utiliser

### À utiliser lorsque l'utilisateur demande de :

- Obtenir des informations techniques détaillées sur une gamme Simatic (S7-1200, S7-1500, S7-400, ET 200).
- Comprendre les workflows de configuration TIA Portal (création de projet, programmation SCL, mise en service).
- Explorer les capacités de MindSphere / Insights Hub (connectivité, analytics, marketplace d'applications).
- Comparer les protocoles industriels Siemens (Profinet, Profibus, AS-i, OPC UA).
- Documenter les bonnes pratiques de cybersécurité pour les environnements Siemens (IEC 62443, Defense in Depth).
- Extraire des spécifications techniques pour la rédaction de cahiers des charges ou d'appels d'offres.
- Préparer des supports de formation ou de transfert de compétences sur l'écosystème Siemens.

### Ne pas utiliser pour :

- La programmation directe d'automates Siemens (utiliser `siemens-scl` ou `tia-portal-projects`).
- Le diagnostic de pannes sur des équipements Siemens spécifiques (utiliser `industrial-diagnostic`).
- La conversion de code entre plateformes (utiliser `plc-converter`).

---

## 1. Procédure d'Extraction

### 1.1 Accès aux sources officielles

#### Site principal Siemens

```bash
# Extraction de la page d'automatisation Siemens
curl -s -A "Mozilla/5.0" \
  "https://new.siemens.com/global/en/products/automation.html" \
  -o siemens_automation_overview.html
```

> **Note :** En cas de blocage (CAPTCHA, rate limiting), utiliser l'outil `web_read` du navigateur ou basculer vers `support.industry.siemens.com` qui est généralement plus permissif.

#### Siemens Industry Online Support (SIOS)

```bash
# Recherche de documentation sur un produit spécifique
# URL pattern : https://support.industry.siemens.com/cs/products?q=<reference>&type=manuals
curl -s "https://support.industry.siemens.com/cs/products?q=6ES7517-3FP00-0AB0&type=manuals" \
  -o siemens_s71500_manual_search.html
```

### 1.2 Stratégies de contournement des blocages

| Obstacle | Stratégie de contournement |
| :--- | :--- |
| **CAPTCHA** | Limiter la fréquence (1 requête/5s) ; utiliser `web_read` avec interaction manuelle si nécessaire |
| **Rate limiting** | Rotation d'User-Agent ; délai exponentiel entre les tentatives |
| **Page régionale** | Forcer le sous-domaine : `new.siemens.com/fr/` pour le contenu français |
| **PDF protégé** | Utiliser l'aperçu HTML du navigateur plutôt que le téléchargement direct |
| **Contenu dynamique (JS)** | Utiliser l'outil navigateur `web_read` (moteur JavaScript complet) plutôt que `curl` |

### 1.3 Structure de collecte recommandée

```
client_data/siemens/
├── references/
│   ├── simatic/
│   │   ├── s7-1500_caracteristiques.md
│   │   ├── s7-1200_guide_selection.md
│   │   └── gamme_et200_io_devices.md
│   ├── tia-portal/
│   │   ├── workflow_creation_projet.md
│   │   ├── programmation_scl_bonnes_pratiques.md
│   │   └── mise_en_service_et_diagnostic.md
│   ├── mindsphere/
│   │   ├── connectivite_iot.md
│   │   └── maintenance_predictive_cas_usage.md
│   └── protocoles/
│       ├── profinet_vs_profibus_comparaison.md
│       └── opc_ua_siemens_integration.md
├── templates/
│   └── fiche_technique_produit.md
└── raw/
    └── (pages HTML, PDF extraits)
```

---

## 2. Domaines d'Extraction Détaillés

### 2.1 Simatic — Automates Programmables

Extraire pour chaque gamme :

| Propriété | S7-1200 | S7-1500 | ET 200SP |
| :--- | :--- | :--- | :--- |
| **Gamme** | Entrée / Milieu | Haut de gamme | Décentralisé |
| **Langages** | LAD, FBD, SCL, S7-GRAPH | LAD, FBD, SCL, S7-GRAPH, CFC | Configuration |
| **Profinet** | Oui (2 ports) | Oui (2-3 ports) | Oui (1-2 ports) |
| **OPC UA** | Serveur (option) | Serveur + Client | Serveur (option) |
| **Sécurité** | MOTION, sécurité F | Failsafe, PROFIsafe | Failsafe |
| **Firmware** | V4.x | V3.x | V3.x |

#### Sources de collecte recommandées

```python
# Exemple de pattern de collecte structurée
sources = {
    "simatic_s7_1500": [
        "https://new.siemens.com/global/en/products/automation/systems/industrial/plc/simatic-s7-1500.html",
        "https://support.industry.siemens.com/cs/products/6ES7517-3FP00-0AB0",
        "https://mall.industry.siemens.com/.../6ES7517-3FP00-0AB0",
    ],
    "tia_portal_v19": [
        "https://new.siemens.com/global/en/products/automation/industry-software/automation-software/tia-portal.html",
        "https://support.industry.siemens.com/cs/document/.../tia-portal-v19",
    ],
}
```

### 2.2 TIA Portal — Environnement d'Ingénierie

Documenter les aspects suivants :

1. **Création de projet** : Configuration du matériel (Hardware Catalog), réseau Profinet, adressage IO.
2. **Programmation** : Blocs (OB, FB, FC, DB), langages supportés, SCL snippets, librairies.
3. **Simulation** : Utilisation de PLCSIM (virtuel) ou S7-PLCSIM Advanced (pour tests avancés).
4. **Mise en service** : Téléchargement vers l'automate, démarrage, diagnostic en ligne.
5. **Sécurité** : Protection d'accès (mot de passe), Secure Communication (TLS), gestion des certificats.

```pascal
// Exemple de programme SCL documenté pour référence
FUNCTION_BLOCK FB_MoteurControl
    VAR_INPUT
        StartCmd : Bool;
        StopCmd  : Bool;
        SpeedRef : Real;
    END_VAR
    VAR_OUTPUT
        Running    : Bool;
        SpeedAct   : Real;
        ErrorCode  : Word;
    END_VAR
    VAR
        TimerOff   : TON;
        State      : Int;
    END_VAR
END_FUNCTION_BLOCK
```

### 2.3 MindSphere / Insights Hub — IoT Industriel

Extraire la documentation sur :

| Capacité | Description |
| :--- | :--- |
| **Connectivité** | MindConnect Nano/NanoPI, IoT 2040, protocoles (OPC UA, MQTT, Modbus) |
| **Data Lake** | Stockage et gestion des séries temporelles industrielles |
| **Analytics** | Fleet Analytics, Predictive Learning, Asset Performance Management |
| **Marketplace** | Applications partenaires et templates prêts à l'emploi |
| **Sécurité** | Authentification OAuth 2.0, chiffrement TLS, gouvernance des données |

### 2.4 Protocoles Industriels Siemens

Documenter les différences et cas d'usage :

| Protocole | Type | Topologie | Débit | Distance |
| :--- | :--- | :--- | :--- | :--- |
| **Profinet** | Ethernet (IEEE 802.3) | Étoile/Linéaire/Anneau | 100 Mbit/s - 1 Gbit/s | 100m (cuivre) |
| **Profibus** | Série (RS-485) | Bus | 12 Mbit/s | 1200m |
| **AS-Interface** | Capteurs/actionneurs | Arbre | 167 kbit/s | 100m |
| **OPC UA** | Logiciel (Client/Serveur) | Ethernet | Variable (bande passante réseau) | Illimité (via WAN) |

---

## 3. Format de Sortie des Références

Chaque fiche technique produite doit suivre ce gabarit :

```markdown
# Fiche Technique : [Produit/Gamme]

**Référence :** [ex: 6ES7517-3FP00-0AB0]
**Date d'extraction :** AAAA-MM-JJ
**Source :** [URL]

## Caractéristiques Techniques

| Propriété | Valeur |
| :--- | :--- |

## Configuration Requise (TIA Portal + Matériel)

- ...

## Procédure de Mise en Œuvre

1. ...

## Bonnes Pratiques

- ...

## Références Croisées

- [Simatic S7-1500](../references/simatic/s7-1500_caracteristiques.md)

## Notes de Version et Compatibilité

- ...
```

---

## 4. Vérification et Validation

### 4.1 Contrôle de qualité des extractions

```python
def validate_extraction(file_path: str) -> list[str]:
    """Valide la qualité d'une fiche extraite."""
    issues = []
    with open(file_path, "r") as f:
        content = f.read()

    checks = [
        ("Titre manquant", "# " not in content),
        ("Source manquante", "**Source :**" not in content),
        ("Date manquante", "**Date d'extraction :**" not in content),
        ("Contenu insuffisant", len(content) < 500),
    ]

    for message, failed in checks:
        if failed:
            issues.append(message)

    return issues
```

### 4.2 Cross-référencement

- Vérifier la cohérence des informations entre plusieurs sources.
- Signaler les contradictions avec des commentaires dans la fiche.
- Mettre à jour les versions et numéros de firmware régulièrement.

---

## Pièges Courants (Common Pitfalls)

1. **Documentation obsolète** : Siemens publie des mises à jour fréquentes (TIA Portal ~1 version/an). Toujours vérifier la date de publication et la version du firmware.

2. **Contenu régionalisé** : Les pages françaises (`/fr/`) peuvent avoir un contenu moins complet que les pages anglaises (`/global/en/`). Consulter les deux et fusionner.

3. **CAPTCHA et blocages** : Le site Siemens utilise des protections anti-bot agressives. Privilégier le support technique SIOS (`support.industry.siemens.com`) qui est plus accessible.

4. **Confusion entre gammes** : Ne pas confondre S7-1200 et S7-1500 (architectures différentes, jeux d'instructions différents). Préciser systématiquement la gamme cible.

5. **Informations de prix non fiables** : Les prix publics Siemens diffèrent des prix négociés par les intégrateurs. Ne pas inclure de données tarifaires sans vérification contractuelle.

6. **Dépendance à une seule source** : Toujours croiser les informations entre les sources officielles, les forums techniques et les documentations partenaires.

---

## Liste de vérification (Checklist)

- [ ] Les sources officielles sont prioritaires (`new.siemens.com`, `support.industry.siemens.com`).
- [ ] Les stratégies de contournement (CAPTCHA, rate limiting) sont documentées et appliquées.
- [ ] Chaque fiche technique contient un titre, une source, une date et un contenu technique substantiel.
- [ ] Les différences entre les gammes Simatic (S7-1200 vs S7-1500) sont clairement distinguées.
- [ ] Les protocoles sont documentés avec leurs cas d'usage respectifs (Profinet, Profibus, OPC UA).
- [ ] Les versions et numéros de firmware sont vérifiés et datés.
- [ ] Le format de sortie standardisé est respecté (gabarit de fiche technique).
- [ ] Les informations sont cross-référencées entre les différentes fiches du dossier `references/`.
- [ ] Les contradictions entre sources sont signalées et documentées.
- [ ] La reproduction de contenu propriétaire est conforme aux conditions d'utilisation (usage interne/documentation).

