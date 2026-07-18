---
name: cad-bom-automation
description: "Utiliser quand l'utilisateur demande d'automatiser le traitement de fichiers CAO (DXF, DWG, STEP), d'extraire des nomenclatures (BOM) ou de manipuler des modèles géométriques en Python."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [cad, dxf, step, bom, python-ezdxf, industrial-engineering]
  related_skills: [simplify-code, industrial-reporting]
---

# Automatisation CAO & Nomenclatures (BOM)

## Vue d'ensemble

L'ingénierie industrielle implique la manipulation de milliers de plans de pièces en 2D (formats **DXF/DWG**) et de modèles en 3D (formats **STEP/IGES**). L'extraction manuelle des données pour générer des **Nomenclatures (BOM - Bill of Materials)** ou pour préparer les fichiers de découpe laser est une tâche répétitive sujette aux erreurs.

L'automatisation permet de :
1.  **Parser des fichiers DXF/DWG :** Lire la structure géométrique, extraire les textes des cartouches (titre du plan, indice de révision, matière, auteur) à l'aide de bibliothèques Python comme `ezdxf`.
2.  **Générer la BOM automatiquement :** Associer les fichiers de pièces 3D avec leurs attributs de base de données (ERP/PLM) pour créer des fichiers Excel/CSV exploitables par les achats ou la fabrication.
3.  **Vérifier la conformité géométrique :** Mesurer automatiquement les dimensions maximales (encombrement) pour valider si la pièce rentre dans le volume de travail d'une machine d'usinage.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire des scripts Python pour extraire des informations textuelles ou géométriques de fichiers DXF à l'aide de `ezdxf`.
- De générer des nomenclatures (BOM) structurées (arborescence parent-enfant de pièces) au format Excel ou JSON.
- De concevoir des scripts de traitement par lots (batch processing) pour renommer ou organiser des dossiers de plans industriels.
- De manipuler ou d'extraire des métadonnées de fichiers 3D (STEP/STP).

**Ne pas utiliser pour :**
- La modélisation de formes géométriques complexes ou la modification manuelle de fichiers CAO (qui doivent être faites dans SolidWorks, AutoCAD ou FreeCAD).

---

## 1. Extraction de Cartouche de Plan DXF en Python (ezdxf)

Le script ci-dessous montre comment charger un fichier DXF 2D et extraire les textes contenus dans un calque spécifique (par exemple, le calque du cartouche `CARTOUCHE_TEXTS`) pour récupérer le titre et la révision du plan :

```python
import ezdxf
import logging

logger = logging.getLogger(__name__)

def extract_dxf_titleblock(dxf_path, layer_name="CARTOUCHE_TEXTS"):
    """
    Lit un fichier DXF et extrait tous les textes du calque spécifié.
    """
    try:
        # Charger le fichier DXF
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        
        extracted_data = []
        
        # Parcourir les entités de type TEXT et MTEXT (Multiligne Text)
        for entity in msp.query('TEXT MTEXT'):
            if entity.dxf.layer == layer_name:
                text_value = entity.dxf.text if entity.dxftype() == 'TEXT' else entity.text
                text_clean = text_value.strip()
                if text_clean:
                    extracted_data.append(text_clean)
                    
        # Organisation simple des métadonnées (selon le format attendu du cartouche)
        # Supposons que le cartouche contient les lignes dans un ordre précis ou préfixées
        metadata = {
            "raw_texts": extracted_data,
            "revision": None,
            "part_number": None
        }
        
        for text in extracted_data:
            if text.startswith("REV:"):
                metadata["revision"] = text.replace("REV:", "").strip()
            elif text.startswith("REF:"):
                metadata["part_number"] = text.replace("REF:", "").strip()
                
        return {"success": True, "metadata": metadata}
        
    except IOError:
        return {"success": False, "error": f"Impossible d'ouvrir le fichier : {dxf_path}"}
    except ezdxf.DXFStructureError:
        return {"success": False, "error": f"Structure DXF invalide ou corrompue : {dxf_path}"}

# Exemple de retour d'appel :
# extract_dxf_titleblock("plan_chassis.dxf")
```

---

## 2. Structure et Génération d'une BOM (Bill of Materials)

Une nomenclature industrielle structurée est généralement représentée sous forme d'arborescence (arbre de composants). Chaque composant possède un statut de fabrication (Fabriqué ou Acheté - Make or Buy).

```json
{
  "assembly_id": "ASM-0012",
  "name": "Châssis Convoyeur Motorisé",
  "revision": "B",
  "components": [
    {
      "part_number": "MTR-0045",
      "name": "Motoréducteur 0.75kW",
      "quantity": 1,
      "source": "BUY",
      "supplier": "SEW"
    },
    {
      "part_number": "PLT-1002",
      "name": "Flanc Gauche Plié",
      "quantity": 1,
      "source": "MAKE",
      "material": "S235JR (Acier)",
      "dxf_file": "PLT-1002_RevA.dxf"
    }
  ]
}
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Incompatibilité de version DXF (Binary vs ASCII) :**
    *   *Erreur :* Essayer de lire un fichier DXF enregistré dans un format binaire propriétaire ou une version trop récente non supportée par la bibliothèque python.
    *   *Correction :* Configurer le logiciel CAO pour exporter les DXF en format **ASCII DXF R12** ou **R14** qui est le standard le plus universellement lisible par les scripts automatiques.
2.  **Textes éclatés dans les cartouches :**
    *   *Erreur :* Chercher une chaîne de caractères exacte dans le plan alors que le logiciel de CAO a exporté le texte sous forme de lettres individuelles séparées possédant chacune leurs coordonnées géométriques (effet d'éclatement du texte).
    *   *Correction :* Utiliser des fonctions de regroupement géométrique spatial (ex: regrouper les textes dont la distance Y est proche sur la même ligne) avant d'analyser le contenu textuel.

---

## Liste de vérification (Checklist)

- [ ] Les fichiers DXF d'entrée sont exportés au format ASCII standard (idéalement R12/R14) pour une compatibilité de lecture maximale.
- [ ] Le script de parsing gère à la fois les entités `TEXT` classiques et les entités multilignes `MTEXT`.
- [ ] La nomenclature (BOM) générée intègre des validations de cohérence (ex: pas de quantité négative, présence obligatoire du champ identifiant `part_number`).
- [ ] Les fichiers CAO ouverts sont fermés proprement dans le script pour libérer les verrous de fichiers du système.

