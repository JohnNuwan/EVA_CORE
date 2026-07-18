---
name: siemens-audit
description: "Extraire des données d'audit Siemens à partir de PDF."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [industrial-automation, siemens, audit, pdf-parsing, data-extraction, python, pypdf, eph, external-exchanges, ids]
    related_skills: [industrial-documents, automation-linter, plc-diagnostic]
---

# Extraction structurée de données d'audit Siemens (PDF)

## Vue d'ensemble

Cette compétence guide l'extraction structurée de données depuis des documents d'audit industriels Siemens (généralement au format PDF) vers un format texte standardisé. Elle cible spécifiquement deux sections critiques des rapports d'audit :

1. **Section 2.5 (External Exchanges)** : Liste des échanges de signaux externes entre instances EPH.
2. **Section 1.5 (EPH-EM Communications)** : Communications internes entre équipements EPH et EM.

Ces documents d'audit sont produits par les outils Siemens (ex: SIMATIC IDS, Industrial Cyber Security Assessment) et servent à cartographier les flux de données et les communications entre systèmes d'automatisation.

### Défis techniques

Les fichiers PDF d'audit posent plusieurs défis d'extraction :
- **Format binaire** : Impossible de lire directement avec des outils texte standards.
- **Structures tabulaires complexes** : Tableaux avec cellules fusionnées, notes en bas de tableau (« See note below »).
- **Encodages variables** : Mélange de texte OCRisé et de texte natif.
- **Contenu multilingue** : Souvent en anglais technique avec des spécificités allemandes.

Pour surmonter ces limitations, cette compétence utilise la bibliothèque `pypdf` sous Python.

---

## Quand l'utiliser

### Cas d'usage

À utiliser lorsque l'utilisateur demande :

- D'extraire la liste des **échanges externes (External Exchanges - Section 2.5)** depuis des comptes rendus ou spécifications d'audit Siemens.
- D'extraire les **communications EPH-EM (Section 1.5)** depuis ces mêmes documents d'audit.
- De lister **tous les échanges externes** à partir de fichiers PDF présents dans un dossier (ex: `client_data/EPH/`).
- De convertir un rapport d'audit Siemens PDF en un fichier de données structuré (CSV, JSON, Markdown).

### Ne pas utiliser pour

- L'extraction de schémas électriques ou de plans CAO (utiliser des outils spécialisés).
- La modification des fichiers PDF originaux (extraction en lecture seule).
- L'extraction de données d'automates temps réel (utiliser la compétence `plc-diagnostic`).

---

## 1. Extraction Technique de Texte depuis un PDF

### 1.1 Script de base avec `pypdf`

```python
import pypdf
import re
from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrait le texte brut de toutes les pages d'un fichier PDF.

    Args:
        pdf_path: Chemin absolu ou relatif vers le fichier PDF.

    Returns:
        str: Texte concaténé de toutes les pages, avec séparateurs de pages.
    """
    reader = pypdf.PdfReader(pdf_path)
    pages_text = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            # Nettoyage des espaces multiples
            text = re.sub(r'\s+', ' ', text)
            pages_text.append(f"--- PAGE {i+1} ---\n{text}")
    return "\n".join(pages_text)
```

### 1.2 Extraction avec détection de sections

```python
def extract_sections(text: str) -> dict:
    """Détecte et sépare les sections 1.5 et 2.5 du texte extrait.

    Args:
        text: Texte brut extrait du PDF.

    Returns:
        dict: Dictionnaire avec les clés 'section_1_5', 'section_2_5', 'other'.
    """
    sections = {'section_1_5': '', 'section_2_5': '', 'other': ''}

    # Patterns de détection des sections
    patterns = {
        'section_1_5': r'(?i)(?:section\s*1\.5|1\.5\s+EPH-EM|EPH[-\s]EM\s+Communications)',
        'section_2_5': r'(?i)(?:section\s*2\.5|2\.5\s+External\s+Exchanges|External\s+Exchanges)',
    }

    # Logique de découpage par sections
    # (implémentation adaptée au format réel des documents)
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            start = match.start()
            # Chercher la section suivante pour la fin
            next_section = None
            for other_key, other_pattern in patterns.items():
                if other_key != key:
                    other_match = re.search(other_pattern, text[start + len(match.group()):])
                    if other_match:
                        next_section = start + len(match.group()) + other_match.start()
                        break
            sections[key] = text[start:next_section] if next_section else text[start:]

    return sections
```

---

## 2. Règles d'extraction pour la Section 2.5 (External Exchanges)

Cette section répertorie les échanges de signaux externes, en particulier de type « eph to / from eph ».

### 2.1 Directives d'extraction

1. **FOCUS** : Extraire uniquement les échanges dont le type est exactement `'eph to / from eph'`.
2. **RÉSOLUTION DE NOTE** : Si la cellule du tableau indique « See note below », vous devez lire le texte ou les sous-tableaux qui suivent pour trouver le vrai nom de l'instance EPH (ex: `610C5_P_PCIP_BTL_2`).
3. **BIDIRECTIONNEL** : Si un lien existe entre l'Instance A et l'Instance B, générer deux entrées séparées si indiqué par le document.
4. **INTERMÉDIAIRES COMAS** : Si « ComAS » est mentionné dans la Section 2.4, veiller à ce que l'échange soit correctement enregistré.
5. **FILTRE DE SORTIE** : Exclure toutes les lignes où aucun « Target Instance » valide n'est trouvé (ne pas générer de lignes avec « N.A. »).
6. **FORMAT DU NOM DE FICHIER** : Conserver uniquement l'identifiant propre du document (ex: `E56_90_IDS851_An3_V00`). Tronquer tout titre supplémentaire ou extension (`.md`, `.pdf`).
7. **LIGNES DUPLIQUÉES** : Si un tableau contient plusieurs lignes pour la même Instance EPH, générer une entrée distincte pour **chaque** ligne.
8. **TYPES MULTIPLES** : Si une seule ligne possède à la fois 'Exchange Type 1' et 'Exchange Type 2' réglés sur 'EPH to / from EPH', générer **deux** entrées distinctes pour cette ligne.

### 2.2 Structure de sortie stricte (Section 2.5)

```text
FILENAME: [Nom propre nettoyé]
INSTANCE_SOURCE: [Titre exact du document]
- Instance_Target: [Vrai nom cible trouvé]
- Type: eph to / from eph
```

### 2.3 Script d'extraction Section 2.5

```python
def extract_external_exchanges(text: str, filename: str) -> list[dict]:
    """Extrait les échanges externes (Section 2.5) du texte PDF.

    Args:
        text: Texte de la Section 2.5.
        filename: Nom du fichier source nettoyé.

    Returns:
        list[dict]: Liste des échanges externes extraits.
    """
    exchanges = []
    lines = text.split('\n')

    # Nettoyage du nom de fichier
    clean_filename = re.sub(r'\s*[-–—].*$', '', filename)
    clean_filename = re.sub(r'\.(pdf|md)$', '', clean_filename).strip()

    # Recherche du titre du document (généralement en haut de section)
    doc_title = ""
    for line in lines[:20]:
        if 'INSTANCE' in line.upper() or 'DOCUMENT' in line.upper():
            doc_title = line.strip()
            break

    # Parsing du tableau des échanges
    current_table = False
    for i, line in enumerate(lines):
        # Détection d'une ligne de tableau significative
        if re.search(r'eph\s+to\s+/\s+from\s+eph', line, re.IGNORECASE):
            # Extraction des instances
            parts = line.split('|')
            if len(parts) >= 2:
                source = parts[0].strip()
                target = parts[1].strip()

                # Résolution des notes
                if 'see note' in target.lower():
                    target = resolve_note(target, lines[i:i+10])

                if target and target.upper() != 'N.A.':
                    exchanges.append({
                        'filename': clean_filename,
                        'instance_source': doc_title or clean_filename,
                        'instance_target': target,
                        'type': 'eph to / from eph'
                    })

    return exchanges

def resolve_note(note_ref: str, context_lines: list[str]) -> str:
    """Résout une référence de note en le vrai nom d'instance.

    Parcourt le contexte immédiat pour trouver la définition de la note.

    Args:
        note_ref: Texte de la référence de note (ex: 'See note below').
        context_lines: Lignes de contexte autour de la référence.

    Returns:
        str: Le nom d'instance résolu, ou la référence originale.
    """
    for line in context_lines:
        # Cherche un motif de nom d'instance (ex: 610C5_P_PCIP_BTL_2)
        match = re.search(r'\b([A-Z0-9]+_[A-Z0-9_]+)\b', line)
        if match:
            return match.group(1)
    return note_ref  # Si non résolu, retourner la référence
```

---

## 3. Règles d'extraction pour la Section 1.5 (EPH-EM Communications)

Cette section détaille les communications internes entre les équipements **EPH** (Electrical Power & Hydraulic) et **EM** (Equipment Module).

### 3.1 Directives d'extraction

1. **SOURCE INSTANCE** : La source doit toujours être le **titre exact** du document d'audit présent en haut du bloc de contexte.
2. **NOM TARGET INSTANCE** : Extraire le nom brut cible exclusivement de la colonne « Instance Tag » du tableau. Conserver le nom brut précis (ex: `664C6_E_B_INLET` ou `664C6_E_B_Outlet`).
3. **NOM DU FICHIER** : Utiliser uniquement le préfixe standard du document d'audit (ex: `E56_90_IDSxxx_Anxx_Vxx`). Supprimer tout texte après un tiret `-` et les extensions de fichier.
4. **FILTRES CONDITIONNELS** :
   - **Index Matrix** : Extraire les données uniquement si la colonne « Index Matrix » est visible et contient une affectation valide non vide. Ignorer les lignes contenant « N.A. » ou vides.
   - **Règle IDS666** : Si le nom de fichier contient « IDS666 », filtrer de façon stricte : n'extraire que les lignes ayant un astérisque (`*`) dans la colonne « EMT » **ET** une valeur valide dans « Instance Tag ».
5. **TYPE D'ÉCHANGE** : Définir la propriété Type exactement à `EPH-EM`.

### 3.2 Structure de sortie stricte (Section 1.5)

```text
FILENAME: [Préfixe propre nettoyé]
INSTANCE_SOURCE: [Titre exact du document]
- Instance_Target: [Target Instance trouvé dans Instance Tag]
- Type: EPH-EM
```

### 3.3 Exemple de résultat

```text
FILENAME: E56_90_IDS851_An3_V00
INSTANCE_SOURCE: E56_90 - System Overview IDS851_An3_V00
- Instance_Target: 664C6_E_B_INLET
- Type: EPH-EM

FILENAME: E56_90_IDS851_An3_V00
INSTANCE_SOURCE: E56_90 - System Overview IDS851_An3_V00
- Instance_Target: 664C6_E_B_OUTLET
- Type: EPH-EM
```

---

## Pièges Courants (Common Pitfalls)

1. **Ignorer les notes en bas de tableau :**
   * *Erreur :* Écrire `"See note below"` comme cible d'instance dans le résultat final.
   * *Correction :* Parcourir le texte immédiatement sous le tableau pour résoudre le nom d'instance réel. Chercher les motifs `[0-9A-Z_]+` après la note.

2. **Garder des extensions ou des titres dans FILENAME :**
   * *Erreur :* `FILENAME: E56_90_IDS851_An3_V00 - MBR.pdf`
   * *Correction :* Nettoyer avec une regex : supprimer tout ce qui suit un tiret `-`, `—`, ou `–`. Supprimer `.pdf`, `.md`. Résultat attendu : `FILENAME: E56_90_IDS851_An3_V00`.

3. **Confusion entre le type d'échange :**
   * *Erreur :* Marquer un échange Section 2.5 comme « EPH-EM » ou un échange Section 1.5 comme « eph to / from eph ».
   * *Correction :* Appliquer strictement :
     - Section 2.5 → `Type: eph to / from eph`
     - Section 1.5 → `Type: EPH-EM`

4. **OCR imparfaite sur les PDF scannés :**
   * *Erreur :* Les PDF scannés (non natifs) produisent du texte avec des caractères mal reconnus, rendant les motifs regex inefficaces.
   * *Correction :* Vérifier la qualité du texte extrait. Si le texte contient trop d'artefacts, suggérer d'utiliser un OCR (Tesseract) en amont :

     ```python
     # Détection de qualité OCR
     def is_text_quality_acceptable(text: str) -> bool:
         """Vérifie si le texte extrait est exploitable (>70% de mots valides)."""
         words = text.split()
         valid = sum(1 for w in words if re.match(r'^[A-Za-z0-9_\-\.]+$', w))
         return len(words) > 0 and (valid / len(words)) > 0.7
     ```

5. **Tableaux avec cellules fusionnées :**
   * *Erreur :* `pypdf` extrait les cellules fusionnées comme du texte plat, perdant la structure ligne/colonne.
   * *Correction :* Utiliser `pdfplumber` en complément pour les tableaux complexes :

     ```bash
     pip install pdfplumber
     ```

     ```python
     import pdfplumber
     with pdfplumber.open(pdf_path) as pdf:
         for page in pdf.pages:
             tables = page.extract_tables()
             for table in tables:
                 for row in table:
                     print(row)
     ```

---

## Liste de vérification (Checklist)

- [ ] L'extraction de PDF utilise la bibliothèque `pypdf` installée dans le `.venv` du projet.
- [ ] `pdfplumber` est installé pour les tableaux complexes avec cellules fusionnées.
- [ ] Les lignes contenant des « N.A. » pour la cible sont correctement filtrées.
- [ ] Le format de sortie respecte scrupuleusement la casse et les retours à la ligne demandés.
- [ ] Les notes en bas de tableau sont résolues (remplacement de « See note below » par le vrai nom d'instance).
- [ ] Les noms de fichiers sont nettoyés (suppression des extensions `.pdf`, `.md` et des textes après tiret).
- [ ] La distinction Section 1.5 (EPH-EM) vs Section 2.5 (eph to/from eph) est respectée.
- [ ] La règle spécifique IDS666 est appliquée avec le filtre `*` dans la colonne EMT.
- [ ] Les échanges bidirectionnels génèrent deux entrées séparées.
- [ ] Le script de détection de qualité OCR (seuil 70%) est implémenté pour valider les PDF scannés.

