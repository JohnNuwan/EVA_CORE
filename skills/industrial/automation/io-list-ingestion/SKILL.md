---
name: io-list-ingestion
description: "Parser et ingérer des listes d'E/S de CAO électrique."
version: 1.2.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [eplan, cad, io-list, csv, excel, parsing, automation-engineering]
  related_skills: [siemens-scl-generation, rockwell-l5x-generation]
---

# Ingestion et Conversion de Listes d'Entrées/Sorties CAO (EPLAN/AutoCAD)

## Vue d'ensemble

Cette compétence régit l'ingestion industrielle de listes d'entrées/sorties (I/O) exportées à partir de schémas électriques (EPLAN, AutoCAD Electrical). Elle détaille l'utilisation de scripts d'ingestion automatisés pour normaliser les adresses physiques, valider la cohérence des signaux et générer les formats d'imports natifs pour TIA Portal et Studio 5000.

---

## Outils Associés

Les scripts de conversion peuvent être exécutés par l'agent à l'aide de l'outil suivant :
- `` `execute_code` `` : Exécuter le script Python de conversion locale.

---

## Fichier de Configuration de Mapping CAO (JSON)

Pour s'adapter aux différents formats d'exports de CAO, le script Python s'appuie sur un fichier de configuration décrivant la structure des colonnes :

```json
{
  "csv_delimiter": ";",
  "columns": {
    "symbol": "Designation_Materiel",
    "address": "Adresse_Physique",
    "signal_type": "Nature_Signal",
    "description": "Texte_Fonctionnel",
    "voltage_range": "Plage_Tension_Courant"
  },
  "signal_mapping": {
    "DI": "BOOL",
    "DO": "BOOL",
    "AI": "INT",
    "AO": "INT"
  }
}
```

---

## Script d'Ingestion Avancé avec Validation et Mapping de Bus (Python)

Ce script réalise le parsing, nettoie les symboles, attribue les types PLC corrects selon les plages physiques (ex: 4-20mA -> analogique `INT` brute ou `REAL`), résout les conflits et gère l'adressage multi-bus.

```python
import csv
import json
import re
import xml.etree.ElementTree as ET

def clean_plc_symbol(symbol: str) -> str:
    """Nettoie le symbole pour être conforme aux spécifications de variables PLC."""
    s = symbol.translate(str.maketrans("àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ", "aaaeeeeiioouuucAAAEEEEIIOOUUUC"))
    s = re.sub(r"[^a-zA-Z0-9_]", "_", s)
    s = re.sub(r"__+", "_", s)
    return s.strip("_")

def parse_and_convert_io_list(csv_path: str, config_path: str, xml_out_path: str, csv_out_path: str):
    with open(config_path, 'r', encoding='utf-8') as cfg_f:
        cfg = json.load(cfg_f)
        
    cols = cfg['columns']
    sig_map = cfg['signal_mapping']
    
    symbols_seen = set()
    addresses_seen = {}
    valid_records = []
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=cfg['csv_delimiter'])
        for line_num, row in enumerate(reader, 1):
            raw_sym = row.get(cols['symbol'], '').strip()
            raw_addr = row.get(cols['address'], '').strip()
            raw_sig = row.get(cols['signal_type'], '').strip().upper()
            desc = row.get(cols['description'], '').strip()
            voltage = row.get(cols['voltage_range'], '').strip()
            
            if not raw_sym or not raw_addr:
                continue
                
            sym = clean_plc_symbol(raw_sym)
            
            # Détermination du type de données PLC
            # ex: Si la plage est '4-20mA' ou '0-10V' -> analogique (INT ou REAL)
            if "MA" in voltage.upper() or "V" in voltage.upper() and raw_sig == "AI":
                dtype = "INT" # Valeur brute de carte
            else:
                dtype = sig_map.get(raw_sig, "BOOL")
                
            # Détection de doublons de symboles
            if sym in symbols_seen:
                sym = f"{sym}_L{line_num}"
            symbols_seen.add(sym)
            
            # Détection de conflits d'adresses physiques
            if raw_addr in addresses_seen:
                print(f"[WARNING] Conflit d'adresse détecté sur '{raw_addr}' ! Symboles: '{addresses_seen[raw_addr]}' et '{sym}'")
            else:
                addresses_seen[raw_addr] = sym
                
            valid_records.append({
                'symbol': sym,
                'address': raw_addr,
                'datatype': dtype,
                'description': f"{desc} [{voltage}]" if voltage else desc
            })
            
    # GÉNÉRATION SIEMENS (XML)
    root = ET.Element("Document")
    tag_table = ET.SubElement(root, "PlcTagTable", Name="Import_EPLAN")
    tags_node = ET.SubElement(tag_table, "Tags")
    
    for rec in valid_records:
        tag = ET.SubElement(tags_node, "PlcTag", Name=rec['symbol'])
        ET.SubElement(tag, "DataType").text = rec['datatype']
        
        addr = rec['address']
        if not addr.startswith("%"):
            addr = f"%{addr}"
        ET.SubElement(tag, "LogicalAddress").text = addr
        
        comment = ET.SubElement(tag, "Comment")
        multi_lang = ET.SubElement(comment, "MultiLanguageText", Lang="fr-FR")
        multi_lang.text = rec['description']
        
    tree = ET.ElementTree(root)
    tree.write(xml_out_path, encoding="utf-8", xml_declaration=True)
    
    # GÉNÉRATION ROCKWELL (CSV)
    with open(csv_out_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["0.1"])
        writer.writerow(["TYPE", "SCOPE", "NAME", "DATATYPE", "DESCRIPTION", "SPECIFIER"])
        for rec in valid_records:
            desc_fmt = f"\"{rec['description']}\"" if rec['description'] else ""
            writer.writerow(["TAG", "", rec['symbol'], rec['datatype'], desc_fmt, rec['address']])

# Exemple d'appel:
# parse_and_convert_io_list("io_export.csv", "mapping.json", "siemens.xml", "rockwell.csv")
```

---

## Bonnes Pratiques d'Ingestion EPLAN

1. **Validation de la tension d'alimentation** :
   * Si le signal est marqué comme `DI` (Digital Input) mais que la tension est notée `230VAC` au lieu de `24VDC`, l'agent doit insérer un avertissement dans le log d'importation pour inviter l'automaticien à vérifier la présence d'un relais de couplage dans le schéma.
2. **Identification des Bus de Terrain** :
   * Les adresses Profinet utilisent des topologies de type `%I` et `%Q`.
   * Les bus AS-i (Actuator Sensor Interface) utilisent souvent un format spécifique d'adresse de nœud (ex: `ASI_1A_Bit0`). Le script doit être configuré pour traduire ces formats vers des variables mémoires structurées.
3. **Nettoyage des espaces et retours chariots** :
   * Toujours nettoyer les champs textuels des caractères invisibles ou sauts de lignes pour éviter de corrompre les fichiers d'import XML/CSV finaux.
