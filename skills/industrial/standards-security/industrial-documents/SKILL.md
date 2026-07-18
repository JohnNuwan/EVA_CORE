---
name: industrial-documents
description: "Utiliser quand l'utilisateur demande d'analyser, d'extraire des données ou de manipuler des documents Excel (.xlsx, .xlsm), Word (.docx) ou des fichiers CAO/P&ID (.dxf)."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [documents, excel, word, dxf, cad, pid, parsing, python, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Traitement de Documents Industriels (Excel, Word, CAO/P&ID DXF)

## Vue d'ensemble

Dans l'ingénierie et l'informatique industrielle, les spécifications techniques, listes de variables, cahiers de tests et plans de réseaux/tuyauteries sont stockés sous différents formats.
- **Excel (.xlsx, .xlsm) :** Utilisé pour les listes de points d'entrées/sorties (I/O lists), les listes d'instruments, d'alarmes et de configurations d'équipements.
- **Word (.docx) :** Utilisé pour les analyses fonctionnelles, les cahiers des charges et les rapports d'essais.
- **DXF (Drawing Exchange Format) :** Format CAO vectoriel standard ouvert (AutoCAD) utilisé pour les schémas d'implantation d'armoires et les schémas tuyauteries et instrumentation (P&ID - Piping and Instrumentation Diagram).

Cette compétence guide l'agent EVA pour écrire des scripts d'extraction et de traitement automatique de ces documents en Python.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'extraire la liste des capteurs/actionneurs depuis un fichier Excel de configuration.
- De lire le texte d'un document Word d'analyse fonctionnelle pour en extraire des exigences.
- De chercher des annotations textuelles ou de lister les calques d'un plan de réseau ou de procédé au format DXF (CAO).
- D'écrire des scripts de génération automatique de cahiers d'essais.

**Ne pas utiliser pour :**
- Réaliser du rendu graphique ou de l'édition vectorielle géométrique lourde en 3D.

---

## 1. Extraction de Données Excel (`openpyxl`)

Le script charge un tableur de configuration (ex. liste d'I/O) et l'analyse ligne par ligne :

```python
import openpyxl

def extract_io_list(file_path: str):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active
    io_points = []
    
    # Parcourir les lignes du tableau à partir de la ligne 2
    for r in range(2, sheet.max_row + 1):
        adresse = sheet.cell(row=r, column=1).value # Colonne A (ex: %I0.0)
        symbole = sheet.cell(row=r, column=2).value # Colonne B (ex: BP_Marche)
        designation = sheet.cell(row=r, column=3).value # Colonne C
        
        if adresse and symbole:
            io_points.append({
                "address": adresse,
                "symbol": symbole,
                "description": designation
            })
            
    wb.close()
    return io_points
```

---

## 2. Lecture et Extraction de Texte Word (`.docx`) sans bibliothèque externe

Un fichier `.docx` étant une archive ZIP, nous pouvons en extraire le texte brut en parsant son XML interne (`word/document.xml`) sans nécessiter d'installer de dépendances externes complexes :

```python
import zipfile
import xml.etree.ElementTree as ET

def read_docx_text(file_path: str) -> str:
    """Extrait le texte brut d'un fichier Word en lisant son XML interne."""
    namespace = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    para_tag = namespace + 'p'
    text_tag = namespace + 't'
    
    text_runs = []
    with zipfile.ZipFile(file_path) as docx:
        # Lecture du document XML interne
        tree = ET.parse(docx.open('word/document.xml'))
        root = tree.getroot()
        
        # Parcourir tous les paragraphes du document
        for paragraph in root.iter(para_tag):
            # Cumuler le texte de chaque nœud texte dans le paragraphe
            texts = [node.text for node in paragraph.iter(text_tag) if node.text]
            if texts:
                text_runs.append("".join(texts))
                
    return "\n".join(text_runs)
```

---

## 3. Recherche de Tags et d'Annotations dans un Plan CAO (`.dxf`)

Les fichiers DXF contiennent des sections textuelles décrivant des entités de dessin. Nous pouvons y chercher des textes d'annotations (tags d'instruments comme `FIT-101`, `LS-102` sur un schéma P&ID) en lisant le fichier ligne par ligne :

```python
def find_instrument_tags_in_dxf(file_path: str):
    """Recherche des annotations textuelles (TEXT / MTEXT) dans un fichier DXF."""
    tags_found = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.read().splitlines()
        
    # Le format DXF associe un code groupe (ex: 0 pour l'entité, 1 pour le texte) à une valeur
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        # Entité texte détectée
        if line == '0' and idx + 1 < len(lines) and lines[idx+1].strip() in ('TEXT', 'MTEXT'):
            entity_type = lines[idx+1].strip()
            # Chercher le code groupe 1 (qui précède la valeur du texte)
            for j in range(idx + 2, min(idx + 30, len(lines))):
                if lines[j].strip() == '1' and j + 1 < len(lines):
                    text_val = lines[j+1].strip()
                    # Exemple de filtre pour capter des tags d'instruments (ex: FIT-101 ou XV_102)
                    if '-' in text_val or '_' in text_val:
                        tags_found.append(text_val)
                    break
        idx += 1
        
    return list(set(tags_found)) # Retourner la liste sans doublons
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Tentative de lecture de fichiers Excel fermés avec mots de passe :**
   * *Erreur :* Ouvrir un fichier Excel protégé par mot de passe avec `openpyxl`. Cela lève une exception non gérée.
   * *Correction :* Préciser à l'utilisateur de fournir le document non chiffré ou d'utiliser un script d'import avec déchiffrement préalable.

2. **Parsing de gros fichiers DXF en mémoire :**
   * *Erreur :* Charger l'intégralité d'un fichier DXF de 50 Mo en une seule chaîne de caractères ou dans un tableau géométrique complexe sous Python. Cela peut saturer la mémoire vive de l'agent.
   * *Correction :* Lire le fichier ligne par ligne (générateur de lignes) ou utiliser des filtres d'expressions régulières ciblés.

---

## Liste de vérification (Checklist)

- [ ] L'écriture ou la modification de feuilles Excel utilise le paramètre `data_only=True` lors de la lecture pour récupérer les valeurs calculées et non les formules brutes si nécessaire.
- [ ] Le parseur Word est capable d'extraire le texte sans lever d'erreurs en cas de présence de paragraphes vides ou d'éléments non textuels.
- [ ] Les recherches de texte dans les fichiers DXF sont insensibles à la casse pour capter les annotations quelle que soit leur casse.
- [ ] Les ressources de fichiers (fichiers ouverts, flux zip) sont systématiquement fermées après traitement.

