---
name: isa95-modelling
description: "Modéliser les données et les UNS selon la norme ISA-95."
version: 1.2.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [isa-95, data-modelling, industrial-standards, enterprise-architecture]
    related_skills: [industrial-uns, mes-integration, industrial-databases]
---

# Modélisation Industrielle & Standard ANSI/ISA-95 (CEI 62264)

## Vue d'ensemble

La norme **ANSI/ISA-95** (reprise à l'international sous la norme **CEI 62264**) structure l'intégration des systèmes d'entreprise (ERP) et des systèmes de contrôle-commande (SCADA/PLC). Elle fournit des modèles de données et un langage commun pour relier les décisions de planification commerciale aux opérations physiques de fabrication au sein du Manufacturing Execution System (MES).

Dans le cadre de l'**Industrie 4.0**, l'apport majeur de l'ISA-95 est sa **Hiérarchie des Équipements**. Cette structure logique sert de fondation universelle pour organiser les bases de données d'historisation, les espaces d'adressage OPC UA et les arborescences de topics au sein d'un **Unified Namespace (UNS)**.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Structurer des topics MQTT pour un Unified Namespace (UNS).
- Définir l'arborescence des variables et des répertoires dans un serveur OPC UA ou un logiciel SCADA (ex: Ignition).
- Organiser les tables et modèles de données d'un MES pour représenter physiquement les équipements d'un site.
- Concevoir des schémas de messages d'échange de données (production, stocks, personnel) entre l'IT et l'OT (B2MML).

---

## 1. Modèle Fonctionnel & Hiérarchie d'Équipements

L'intégration d'usine est divisée en 5 niveaux logiques :

| Niveau | Systèmes | Rôle / Portée |
| :--- | :--- | :--- |
| **Niveau 4** | ERP / Gestion | Planification des ressources de l'entreprise, commandes clients, logistique globale. |
| **Niveau 3** | MES / MOM | Gestion des opérations de fabrication, exécution des lots, TRS/OEE, traçabilité. |
| **Niveau 2** | SCADA / HMI | Supervision locale, contrôle et acquisition de données en temps réel. |
| **Niveau 1** | PLC / Automates | Logique de commande physique, régulations, interverrouillages de sécurité. |
| **Niveau 0** | Capteurs / Actionneurs | Le procédé physique (moteurs, vannes, sondes analogiques, convoyeurs). |

### Hiérarchie standard de l'équipement (Partie 1)
Pour structurer les systèmes logiciels, les équipements physiques sont modélisés selon l'arborescence descendante suivante :
1.  **Enterprise (Entreprise) :** Le groupe industriel mondial.
2.  **Site (Usine/Site) :** Un site géographique autonome.
3.  **Area (Atelier/Zone) :** Secteur logique ou physique du site (ex: Conditionnement, Réception, Cuisson).
4.  **Work Cell / Production Line (Cellule / Ligne) :** Ensemble d'équipements coordonnés réalisant une tâche (ex: Ligne d'embouteillage, Atelier de pesage).
5.  **Unit / Work Element (Machine / Sous-système) :** Sous-élément machine individuel (ex: Moteur d'agitation, Sonde de température, Vanne d'alimentation).

---

## 2. Unified Namespace (UNS) : Structuration de Topics MQTT

Le Unified Namespace est un hub de données centralisé où toutes les informations de l'entreprise sont structurées selon la hiérarchie ISA-95. N'importe quel système consommateur (MES, Cloud, Analytique) peut s'abonner de manière intuitive aux données contextuelles.

### Format de Topic Standardisé :
```text
[Entreprise]/[Site]/[Area]/[Line_or_Cell]/[Equipment]/[Metric]
```

### Exemple 1 : Secteur Agroalimentaire (Brasserie)
- **Topic :** `EVA/Lyon/Brassage/Cuve_Matiere_01/Agitateur/Speed_RPM`
- **Topic :** `EVA/Lyon/Conditionnement/Ligne_Emballage_02/Remplisseuse/Total_Count`

### Exemple 2 : Secteur Traitement de l'Eau (Chimique)
- **Topic :** `EVA/Paris/Decantation/Bassin_01/Vanne_Entree/State_Opened`
- **Topic :** `EVA/Paris/Filtration/Filtre_Charbon/Pression_Delta/Value_Bar`

---

## 3. Script Python de Validation UNS et Payload B2MML (JSON)

Ce script permet de parser et de valider les topics MQTT arrivant sur un broker industriel afin d'assurer la conformité à la hiérarchie ISA-95, et valide un payload de type B2MML (Business to Manufacturing Markup Language) converti au format JSON.

```python
import re
import json

# Pattern Regex validant strictement les 5 niveaux ISA-95 + la métrique finale
# Format: Enterprise/Site/Area/LineOrCell/Equipment/Metric
UNS_TOPIC_REGEX = re.compile(
    r"^([a-zA-Z0-9_-]+)/"  # 1. Enterprise
    r"([a-zA-Z0-9_-]+)/"  # 2. Site
    r"([a-zA-Z0-9_-]+)/"  # 3. Area
    r"([a-zA-Z0-9_-]+)/"  # 4. Line/Cell
    r"([a-zA-Z0-9_-]+)/"  # 5. Equipment
    r"([a-zA-Z0-9_/-]+)$" # 6. Metric (peut contenir des sous-métriques)
)

def validate_uns_topic(topic: str) -> dict:
    """Valide et parse une arborescence de topic UNS selon la hiérarchie ISA-95."""
    match = UNS_TOPIC_REGEX.match(topic)
    if not match:
        return {
            "is_valid": False,
            "error": "Le topic ne respecte pas la hiérarchie ISA-95 : Enterprise/Site/Area/Line/Equipment/Metric."
        }
    
    parts = match.groups()
    return {
        "is_valid": True,
        "enterprise": parts[0],
        "site": parts[1],
        "area": parts[2],
        "line": parts[3],
        "equipment": parts[4],
        "metric": parts[5]
    }

def validate_b2mml_material_payload(payload_json: str) -> bool:
    """Valide sommairement un objet d'échange B2MML JSON pour la définition de matière."""
    try:
        data = json.loads(payload_json)
        
        # Structure de base B2MML requise
        required_keys = ["MaterialDefinitionID", "Description", "MaterialSubLot"]
        for key in required_keys:
            if key not in data:
                print(f"Clé manquante dans le schéma B2MML : {key}")
                return False
                
        # Validation du sous-lot
        sublot = data["MaterialSubLot"]
        if "SubLotID" not in sublot or "Quantity" not in sublot:
            print("Champs requis manquants dans 'MaterialSubLot'.")
            return False
            
        return True
    except json.JSONDecodeError:
        print("Erreur de décodage JSON.")
        return False

# --- EXEMPLES DE TESTS ---
if __name__ == "__main__":
    # Test Topic UNS
    topic_ok = "EVA/Lyon/Brassage/Cuve01/Agitateur/Speed_RPM"
    result = validate_uns_topic(topic_ok)
    print(f"Validation topic OK : {result}")

    topic_ko = "Lyon/Brassage/Cuve01/Speed_RPM"
    result_ko = validate_uns_topic(topic_ko)
    print(f"Validation topic KO : {result_ko}")

    # Test B2MML JSON Payload
    b2mml_json = """{
        "MaterialDefinitionID": "MAT-BRW-099",
        "Description": "Houblon aromatique type Cascade",
        "MaterialSubLot": {
            "SubLotID": "LOT-2026-06",
            "Quantity": 250.0,
            "UnitOfMeasure": "KG"
        }
    }"""
    print(f"Validation B2MML JSON : {validate_b2mml_material_payload(b2mml_json)}")
```

---

## Pièges Courants (Common Pitfalls)

1.  **Arborescence de Topics plate (Flat Namespace) :**
    *   *Erreur :* Publier toutes les variables en vrac sous un topic plat comme `usine/capteurs/T_01`. Les applications consommatrices doivent maintenir des tables de correspondances manuelles fastidieuses pour localiser l'équipement.
    *   *Correction :* Structurer chaque variable dans l'arborescence hiérarchique complète pour lui donner un contexte géographique et fonctionnel auto-déclaratif.
2.  **Modélisation orientée protocole au lieu de fonction :**
    *   *Erreur :* Utiliser le nom de la passerelle de communication ou du protocole dans le topic UNS (ex: `EVA/Site/Kepware_OPC/Modbus_Driver/Variable`).
    *   *Correction :* Le Unified Namespace doit modéliser la fonction et la hiérarchie physique réelle des équipements de l'usine, indépendamment de la tuyauterie informatique utilisée pour acheminer la donnée.
3.  **Inversion des niveaux de hiérarchie :**
    *   *Erreur :* Intervertir les niveaux, par exemple positionner l'équipement parent avant la zone (`EVA/Site/Cuve01/Brassage/...`).
    *   *Correction :* Rédiger et publier un document de taxonomie d'entreprise strict dès le début du projet, validé par toutes les équipes (Automatisme, Supervision, DSI).

---

## Liste de vérification (Checklist)

- [ ] La description frontmatter YAML fait moins de 60 caractères et se termine par un point.
- [ ] L'arborescence des variables respecte les 5 niveaux logiques de la norme ISA-95 (Entreprise ➔ Site ➔ Zone/Atelier ➔ Ligne/Cellule ➔ Machine/Sous-système).
- [ ] Les noms des niveaux et des variables ne contiennent ni espaces, ni caractères spéciaux, ni majuscules accentuées (utiliser des underscores et de l'ASCII simple).
- [ ] La structure hiérarchique est unifiée sur toutes les technologies d'échange du projet (Broker MQTT, Serveur OPC UA, structures d'Historian).
- [ ] Les métriques et capteurs finaux sont positionnés au niveau inférieur de l'équipement parent auquel ils appartiennent physiquement.
- [ ] Les structures d'échange complexes HMI/MES utilisent un format d'objet B2MML normalisé (XML ou sa conversion JSON propre).

