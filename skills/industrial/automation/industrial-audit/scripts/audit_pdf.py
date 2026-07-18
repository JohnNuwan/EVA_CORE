#!/usr/bin/env python3
"""Script d'audit industriel pour extraire les échanges EPH (Section 2.5 et 1.5) depuis les PDFs locaux.

Ce script remplace l'ancienne dépendance Qdrant par une lecture locale directe des PDF
via 'pypdf', et utilise les adaptateurs de client LLM internes de Helios.
"""

from __future__ import annotations

import argparse
import asyncio
import glob
import json
import os
import re
import sys
import time
import concurrent.futures
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Raccordement dynamique au répertoire racine de Helios pour les imports internes
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Installation dynamique de pypdf si manquant
try:
    import pypdf
except ImportError:
    print("pypdf non détecté. Installation en cours...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf

from agent.auxiliary_client import async_call_llm
from agent.helios_constants import get_workspace_root, get_helios_home
from pathlib import Path


# =============================================================================
# Structures de données & Constantes
# =============================================================================

class ExchangeType(Enum):
    EPH_EM = "EPH-EM"
    EPH_TO_EPH = "eph to / from eph"

@dataclass
class ExchangeRow:
    filename: str
    source_instance: str
    source_as: str
    target_instance: str
    target_as: str
    exchange_type: ExchangeType


SYSTEM_PROMPT_25 = (
    "You are a Siemens Industrial Auditor. Extract Section 2.5 (External Exchanges).\n"
    "CRITICAL GUIDELINES (from Audit Minutes):\n"
    "1. FOCUS: Only extract exchanges of type 'eph to / from eph'.\n"
    "2. NOTE RESOLUTION: If the table says 'See note below', you MUST read the following text/tables to find the actual Instance EPH names (e.g., 610C5_P_PCIP_BTL_2).\n"
    "3. BIDIRECTIONAL: If a link exists between Instance A and Instance B, create two separate entries if indicated.\n"
    "4. COMAS INTERMEDIARIES: If 'ComAS' is mentioned in Section 2.4, ensure the exchange is recorded.\n"
    "5. OUTPUT FILTER: Only output rows where a valid Target Instance is found. Do not output 'N.A.' rows.\n\n"
    "6. FILENAME FORMAT: Use ONLY the identifier (e.g., E56_90_IDS851_An3_V00). Truncate any titles or .md extensions.\n"
    "7. DUPLICATE LINES: If a table has multiple lines for the same Instance EPH, output a separate entry for EACH line.\n"
    "8. MULTIPLE TYPES: If a single line has both 'Exchange Type 1' and 'Exchange Type 2' set to 'EPH to/from EPH', output TWO separate entries for that line.\n"
    "STRICT FORMAT:\n"
    "You MUST return a strictly valid JSON array of objects. DO NOT output any conversational text (e.g. 'Here are the...').\n"
    "[\n"
    "  {\n"
    "    \"filename\": \"[name]\",\n"
    "    \"source_instance\": \"[Document Title]\",\n"
    "    \"targets\": [\n"
    "      {\"target\": \"[Actual name found]\", \"type\": \"eph to / from eph\"}\n"
    "    ]\n"
    "  }\n"
    "]"
)

SYSTEM_PROMPT_15 = (
    "You are a Siemens Industrial Auditor specialized in Section 1.5 (EPH-EM Communications).\n"
    "Your job is to cleanly extract structural target names strictly from the 'Instance Tag' data column provided in the context.\n\n"
    "CRITICAL EXTRACATION & FORMAT RULES:\n"
    "1. SOURCE INSTANCE: The Source Instance MUST always be the exact Document Title found at the top of the context block.\n"
    "2. TARGET INSTANCE formatting: Extract the raw Target Instance exclusively from the text content inside the 'Instance Tag' column.\n"
    "   - Crucial: Output the raw name precisely as found (e.g., 664C6_E_B_INLET ... or 664C6_E_B_Outlet ...) without modifications. The backend parser maps the exact string to the application's AS normalization engine.\n"
    "3. FILENAME CONSISTENCY: Read the exact filename provided in the [SOURCE: ...] header. Retain ONLY the standard document prefix syntax (e.g., E56_90_IDSxxx_Anxx_Vxx). Strip trailing extensions like '.md' and skip any text following a hyphen '-'.\n"
    "4. CONDITIONAL FILTERS:\n"
    "   - Index Matrix Condition: Extract data only when an 'Index Matrix' column is visible and contains a valid, non-empty cell assignment. Skip rows where the Index Matrix field is explicitely 'N.A.' or empty.\n"
    "   - IDS666 Custom Rule: For contextual source files containing 'IDS666', filter entries strictly. Only extract rows where the 'EMT' column features an asterisk (*) AND the 'Instance Tag' has valid data.\n"
    "5. EXCHANGE TYPE: Always set the Type property exactly to 'EPH-EM'.\n\n"
    "STRICT OUTPUT STRUCTURE:\n"
    "You MUST return a strictly valid JSON array of objects. DO NOT output any conversational text (e.g. 'Here are the...').\n"
    "[\n"
    "  {\n"
    "    \"filename\": \"[clean standard name prefix]\",\n"
    "    \"source_instance\": \"[Document Title]\",\n"
    "    \"targets\": [\n"
    "      {\"target\": \"[Target Instance found inside Instance Tag]\", \"type\": \"EPH-EM\"}\n"
    "    ]\n"
    "  }\n"
    "]"
)


# =============================================================================
# Helper Functions
# =============================================================================

def extract_metadata(first_page_text: str, file_path: str) -> tuple[str, str]:
    """Extrait le nom de fichier propre et le titre de document de la page de garde."""
    basename = os.path.basename(file_path)
    m = re.search(r'(E\d{2}_\d{2}_IDS\d+_An\d+_V\d+)', basename, re.IGNORECASE)
    clean_fname = m.group(1) if m else basename.split(' - ')[0].strip()

    lines = [l.strip() for l in first_page_text.splitlines() if l.strip()]
    equipment = "Unknown"
    for i, line in enumerate(lines):
        if "Document Title" in line:
            if i + 1 < len(lines):
                equipment = lines[i + 1]
                break
    return clean_fname, equipment


def preprocess_text(text: str) -> str:
    """Restaure la disposition des astérisques isolés sur une nouvelle ligne par pypdf."""
    lines = text.splitlines()
    merged = []
    for line in lines:
        stripped = line.strip()
        if stripped == "(*)" or stripped == "*":
            if merged:
                merged[-1] = "(*) " + merged[-1]
        else:
            merged.append(line)
    return "\n".join(merged)


def extract_sections_from_pdf(file_path: str) -> dict[str, Any]:
    """Parcourt le PDF et extrait les sections 1.5 et 2.5 sous forme textuelle."""
    try:
        # Import dynamique et installation de pdfplumber si absent
        pdfplumber = None
        try:
            import pdfplumber
        except ImportError:
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import pdfplumber
            except Exception:
                pdfplumber = None

        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    pages = list(pdf.pages)
                    if not pages:
                        return {"filename": os.path.basename(file_path), "equipment": "Unknown", "sec15": "", "sec25": ""}

                    first_page_text = pages[0].extract_text() or ""
                    clean_fname, equipment = extract_metadata(first_page_text, file_path)

                    full_text = ""
                    start_page = 2 if len(pages) >= 3 else 0
                    for idx in range(start_page, len(pages)):
                        # layout=True permet de preserver l'alignement des colonnes
                        txt = pages[idx].extract_text(layout=True)
                        if txt:
                            full_text += txt + "\n"
            except Exception as e:
                print(f"⚠️ Erreur pdfplumber, repli vers pypdf pour {file_path}: {e}")
                pdfplumber = None

        if not pdfplumber:
            # Code de secours avec pypdf
            reader = pypdf.PdfReader(file_path)
            pages = list(reader.pages)
            if not pages:
                return {"filename": os.path.basename(file_path), "equipment": "Unknown", "sec15": "", "sec25": ""}

            # Extraction des métadonnées sur la première page
            first_page_text = pages[0].extract_text() or ""
            clean_fname, equipment = extract_metadata(first_page_text, file_path)

            # Concatenation du texte
            full_text = ""
            start_page = 2 if len(pages) >= 3 else 0
            for idx in range(start_page, len(pages)):
                full_text += (pages[idx].extract_text() or "") + "\n"

        # Recherche Section 1.5
        sec15_text = ""
        m15 = re.search(r'\b1\.5\s+EQUIPMENT\b', full_text, re.IGNORECASE)
        if m15:
            start_idx = m15.start()
            # Cherche la fin de la section (généralement 1.6)
            m16 = re.search(r'\b1\.6\s+MEASUREMENTS\b|\b2\.\s+CHARACTERISTICS\b', full_text, re.IGNORECASE)
            end_idx = m16.start() if m16 else len(full_text)
            sec15_text = full_text[start_idx:end_idx].strip()

        # Recherche Section 2.5
        sec25_text = ""
        m25 = re.search(r'\b2\.5\s+EXTERNAL\b', full_text, re.IGNORECASE)
        if m25:
            start_idx = m25.start()
            m26 = re.search(r'\b2\.6\s+ALARM\b', full_text, re.IGNORECASE)
            end_idx = m26.start() if m26 else len(full_text)
            sec25_text = full_text[start_idx:end_idx].strip()

        return {
            "filename": clean_fname,
            "equipment": equipment,
            "sec15": preprocess_text(sec15_text),
            "sec25": preprocess_text(sec25_text)
        }
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction de {file_path}: {e}")
        return {"filename": os.path.basename(file_path), "equipment": "Unknown", "sec15": "", "sec25": ""}


def _resolve_as_bulk(instances: list[str]) -> dict[str, str]:
    """Résout de manière heuristique la Station d'Automatisme (AS) à partir du préfixe d'instance."""
    as_map = {}
    for inst in instances:
        if not inst or inst == "Unknown":
            continue
        parts = inst.split('_')
        if parts:
            prefix = parts[0]
            m = re.match(r'^(\d+)', prefix)
            if m:
                # On ne conserve que le premier chiffre de la station (ex: 664 -> AS6, 732 -> AS7)
                as_map[inst] = f"AS{m.group(1)[0]}"
            else:
                as_map[inst] = f"AS_{prefix}"
        else:
            as_map[inst] = "AS_Unknown"
    return as_map


def _clean_and_repair_json(text: str) -> str:
    """Nettoie et tente de réparer une chaîne JSON mal formée."""
    # Enlever les commentaires de type // ou /* */
    text = re.sub(r'//.*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    # Supprimer les virgules traînantes (trailing commas)
    text = re.sub(r',\s*([\]}])', r'\1', text)
    
    # Si le texte ne commence pas par [ ou {, chercher la première occurrence
    text = text.strip()
    if not (text.startswith('[') or text.startswith('{')):
        m = re.search(r'([\[{])', text)
        if m:
            start_idx = m.start()
            # Chercher le dernier ] ou } de la fin vers le début
            for end_idx in range(len(text) - 1, start_idx, -1):
                if text[end_idx] in (']', '}'):
                    text = text[start_idx:end_idx + 1]
                    break
    return text.strip()

def _parse_response_to_exchange_rows(llm_text: str, default_type: ExchangeType) -> list[ExchangeRow]:
    """Parse le format du LLM en structures ExchangeRow (supporte le JSON et le texte)."""
    # 1. Tentative de parsing JSON si le LLM a renvoyé du JSON (ex: Gemini)
    json_text = llm_text.strip()
    m_json = re.search(r'```json\s*(.*?)\s*```', llm_text, re.DOTALL | re.IGNORECASE)
    if m_json:
        json_text = m_json.group(1).strip()
    elif llm_text.strip().startswith("```"):
        m_code = re.search(r'```\s*(.*?)\s*```', llm_text, re.DOTALL)
        if m_code:
            json_text = m_code.group(1).strip()

    # Nettoyer et réparer le JSON avant de le charger
    cleaned_json = _clean_and_repair_json(json_text)

    try:
        data = json.loads(cleaned_json)
        if isinstance(data, dict):
            # Si le dictionnaire représente lui-même un document, on le garde tel quel
            has_doc_keys = any(
                clean_k in {"filename", "file", "source", "sourceinstance", "instancesource"}
                for k in data.keys()
                for clean_k in [k.replace("-", "").replace("*", "").replace("_", "").strip().lower()]
            )
            if has_doc_keys:
                data = [data]
            else:
                # Sinon, on cherche s'il contient une liste de documents
                found_list = None
                for key, val in data.items():
                    if isinstance(val, list):
                        found_list = val
                        break
                if found_list is not None:
                    data = found_list
                else:
                    data = [data]

        if isinstance(data, list):
            rows = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                # Normalisation des clés pour éviter les tirets et underscores de formatage
                norm_item = {}
                for k, v in item.items():
                    clean_k = k.replace("-", "").replace("*", "").replace("_", "").strip().lower()
                    norm_item[clean_k] = v

                fname = norm_item.get("filename") or norm_item.get("file") or ""
                source_inst = norm_item.get("instancesource") or norm_item.get("sourceinstance") or norm_item.get("source") or ""

                # Détection de cibles imbriquées (ex: INSTANCE_TARGETS, INSTANCES)
                targets = []
                nested = (
                    norm_item.get("instancetargets") or 
                    norm_item.get("instances") or 
                    norm_item.get("targets") or 
                    norm_item.get("rows") or 
                    norm_item.get("exchanges")
                )
                if not nested:
                    # Recherche d'un champ qui contient une liste
                    for val in norm_item.values():
                        if isinstance(val, list):
                            nested = val
                            break

                if isinstance(nested, list):
                    for nt in nested:
                        if isinstance(nt, dict):
                            norm_nt = {nk.replace("-", "").replace("*", "").replace("_", "").strip().lower(): nv for nk, nv in nt.items()}
                            t_inst = norm_nt.get("instancetarget") or norm_nt.get("target") or norm_nt.get("instance") or ""
                            t_type = norm_nt.get("type") or default_type.value
                            if t_inst:
                                targets.append({"target": t_inst, "type": t_type})
                        elif isinstance(nt, str):
                            if nt.strip():
                                targets.append({"target": nt.strip(), "type": default_type.value})
                else:
                    t_inst = norm_item.get("instancetarget") or norm_item.get("target") or norm_item.get("instance") or ""
                    t_type = norm_item.get("type") or default_type.value
                    if t_inst:
                        targets.append({"target": t_inst, "type": t_type})

                if fname and source_inst and targets:
                    for t_item in targets:
                        target_inst = t_item["target"]
                        t_type = t_item["type"]
                        as_map = _resolve_as_bulk([source_inst, target_inst])
                        
                        t_type_lower = str(t_type).lower().strip()
                        if "eph-em" in t_type_lower or "ephem" in t_type_lower:
                            exchange_type = ExchangeType.EPH_EM
                        elif "eph to / from eph" in t_type_lower or "eph to eph" in t_type_lower or "eph_to_eph" in t_type_lower:
                            exchange_type = ExchangeType.EPH_TO_EPH
                        else:
                            exchange_type = default_type

                        rows.append(ExchangeRow(
                            filename=fname,
                            source_instance=source_inst,
                            source_as=as_map.get(source_inst, "Unknown"),
                            target_instance=target_inst,
                            target_as=as_map.get(target_inst, "Unknown"),
                            exchange_type=exchange_type
                        ))
            if rows:
                return rows
    except Exception as e:
        # Fallback Regex si le parsing JSON échoue et que le format semble être du JSON
        if "filename" in cleaned_json.lower() or "targets" in cleaned_json.lower():
            try:
                rows = []
                # Recherche des objets JSON ou des motifs similaires
                doc_blocks = re.findall(r'\{\s*"filename".*?\}\s*\}\s*\]|\{\s*"filename".*?\}\s*\}', cleaned_json, re.DOTALL)
                for block in doc_blocks:
                    fname_m = re.search(r'"filename"\s*:\s*"([^"]+)"', block)
                    source_m = re.search(r'"source_instance"\s*:\s*"([^"]+)"', block)
                    if fname_m and source_m:
                        fname = fname_m.group(1)
                        source_inst = source_m.group(1)
                        target_blocks = re.findall(r'\{\s*"target"\s*:\s*"([^"]+)".*?\}', block, re.DOTALL)
                        for target_name in target_blocks:
                            type_m = re.search(r'"type"\s*:\s*"([^"]+)"', block)
                            t_type = type_m.group(1) if type_m else default_type.value
                            t_type_lower = t_type.lower()
                            if "eph-em" in t_type_lower or "ephem" in t_type_lower:
                                exchange_type = ExchangeType.EPH_EM
                            elif "eph to / from eph" in t_type_lower or "eph to eph" in t_type_lower or "eph_to_eph" in t_type_lower:
                                exchange_type = ExchangeType.EPH_TO_EPH
                            else:
                                exchange_type = default_type
                            
                            as_map = _resolve_as_bulk([source_inst, target_name])
                            rows.append(ExchangeRow(
                                filename=fname,
                                source_instance=source_inst,
                                source_as=as_map.get(source_inst, "Unknown"),
                                target_instance=target_name,
                                target_as=as_map.get(target_name, "Unknown"),
                                exchange_type=exchange_type
                            ))
                if rows:
                    return rows
            except Exception:
                pass

    # 2. Parsing Regex classique (format texte brut spécifié par les prompts)
    blocks = re.split(r'\*?\*?FILENAME\*?\*?\s*:', llm_text, flags=re.IGNORECASE)
    rows: list[ExchangeRow] = []

    for block in blocks:
        if not block.strip():
            continue

        lines = block.strip().split('\n')
        raw_fname = lines[0].strip()

        fname_match = re.search(r'(E\d{2}_\d{2}_IDS\d+_An\d+_V\d+)', raw_fname, re.IGNORECASE)
        fname = fname_match.group(1) if fname_match else re.sub(r'\*+', '', raw_fname.split('-')[0].split('.md')[0].strip()).strip()

        source_inst = "Unknown"
        source_match = re.search(r'\*?\*?INSTANCE_SOURCE\*?\*?\s*:\s*(.*)', block, re.IGNORECASE)
        if source_match:
            source_inst = re.sub(r'\*+', '', source_match.group(1)).strip()

        # Nettoyage anti-hallucination (si le nom de fichier est une longue phrase)
        if len(fname.split()) > 3 or len(fname) > 50:
            fname = "Unknown"

        lines_in_block = block.strip().split('\n')
        block_targets: list[dict[str, str]] = []
        current_type = default_type.value

        for l in lines_in_block:
            l_strip = l.strip()

            t_match = re.search(r'^[-*#\d\.\s]*\*?\*?Instance_Target\*?\*?\s*:\s*(.*)', l_strip, re.IGNORECASE)
            if t_match:
                targets_raw = re.sub(r'\*+', '', t_match.group(1)).strip()
                split_targets = re.split(r'\s*,\s*|\s+and\s+|\s+et\s+|\s*&\s*|\s*/\s*', targets_raw, flags=re.IGNORECASE)
                for t in split_targets:
                    t_clean = re.sub(r'\(.*?\)', '', t).strip()
                    if t_clean.upper() not in ["N.A.", "NA", "NONE"] and "SEE NOTE" not in t_clean.upper() and t_clean:
                        block_targets.append({"target": t_clean, "type": current_type})
                continue

            type_match = re.search(r'^[-*#\d\.\s]*\*?\*?Type\*?\*?\s*:\s*(.*)', l_strip, re.IGNORECASE)
            if type_match and block_targets:
                current_type = re.sub(r'\*+', '', type_match.group(1)).strip()

        if source_inst != "Unknown" and block_targets:
            as_map = _resolve_as_bulk([source_inst] + [t["target"] for t in block_targets])

            for t_item in block_targets:
                try:
                    exchange_type = ExchangeType(t_item["type"].lower())
                except ValueError:
                    exchange_type = default_type

                rows.append(ExchangeRow(
                    filename=fname,
                    source_instance=source_inst,
                    source_as=as_map.get(source_inst, "Unknown"),
                    target_instance=t_item["target"],
                    target_as=as_map.get(t_item["target"], "Unknown"),
                    exchange_type=exchange_type
                ))
    return rows


# =============================================================================
# Core Async Processing
# =============================================================================

async def safe_llm_call(
    json_chunk: str,
    sys_prompt: str,
    user_suffix: str,
    semaphore: asyncio.Semaphore,
    verbose: bool = False
) -> Optional[str]:
    """Appel asynchrone sécurisé du LLM à l'aide de Helios."""
    if not json_chunk or json_chunk == "[]":
        return None

    async with semaphore:
        try:
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"JSON Data:\n{json_chunk}\n\n{user_suffix}"}
            ]
            try:
                resp = await async_call_llm(
                    messages=messages,
                    timeout=180.0,
                    temperature=0.0,
                    extra_body={"response_format": {"type": "json_object"}}
                )
            except Exception as e:
                # Si le fournisseur/modèle ne supporte pas response_format, on réessaye sans
                if "response_format" in str(e) or "json_object" in str(e) or "extra_body" in str(e):
                    resp = await async_call_llm(
                        messages=messages,
                        timeout=180.0,
                        temperature=0.0
                    )
                else:
                    raise e
            # Extrait le contenu du message de la réponse Helios
            content = ""
            if hasattr(resp, "choices") and resp.choices:
                content = resp.choices[0].message.content
            elif hasattr(resp, "message"):
                content = resp.message.content
            else:
                content = str(resp)

            if verbose:
                print(f"\n--- LLM RESPONSE FOR {user_suffix} ---")
                print(content)
                print("---------------------------------------\n")
            return content
        except Exception as e:
            print(f"❌ Erreur lors de l'appel LLM: {e}")
            return None


async def process_section(
    docs: list[dict[str, Any]],
    section_id: str,
    system_prompt: str,
    user_suffix: str,
    batch_size: int,
    semaphore: asyncio.Semaphore,
    verbose: bool = False
) -> list[ExchangeRow]:
    """Découpe les sections par lots et exécute les requêtes LLM en parallèle."""
    tasks = []
    # Filtrer les documents ayant une section non vide
    sec_key = "sec25" if section_id == "2.5" else "sec15"
    valid_docs = [d for d in docs if d[sec_key]]

    if not valid_docs:
        return []

    # Partitionnement dynamique basé sur la taille du texte (max_batch_chars = 40000)
    max_batch_chars = 40000
    batches = []
    current_batch = []
    current_chars = 0

    for d in valid_docs:
        doc_len = len(d[sec_key])
        if current_batch and (current_chars + doc_len > max_batch_chars or len(current_batch) >= batch_size):
            batches.append(current_batch)
            current_batch = [d]
            current_chars = doc_len
        else:
            current_batch.append(d)
            current_chars += doc_len
    if current_batch:
        batches.append(current_batch)

    for batch in batches:
        batch_data = []
        for d in batch:
            batch_data.append({
                "filename": d["filename"],
                "equipment": d["equipment"],
                "section_text": d[sec_key]
            })
        batch_json = json.dumps(batch_data, ensure_ascii=False, indent=2)
        if verbose:
            print(f"  [Lot Section {section_id}] Envoi de {len(batch)} documents (taille : {sum(len(d[sec_key]) for d in batch)} chars)...")
        tasks.append(safe_llm_call(batch_json, system_prompt, user_suffix, semaphore, verbose))

    responses = await asyncio.gather(*tasks)

    all_rows = []
    default_type = ExchangeType.EPH_TO_EPH if section_id == "2.5" else ExchangeType.EPH_EM
    for resp in responses:
        if resp:
            rows = _parse_response_to_exchange_rows(resp, default_type)
            all_rows.extend(rows)
            
    return all_rows


# =============================================================================
# Main Program
# =============================================================================

async def main():
    try:
        from helios_cli.env_loader import load_helios_dotenv
        load_helios_dotenv()
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Audit industriel des fichiers PDF de phases d'équipement.")
    parser.add_argument("--limit", "-l", type=int, default=None, help="Limiter le nombre de fichiers traités (ex: 5 pour tester)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Activer le mode verbeux")
    parser.add_argument("--output", "-o", type=str, default=None, help="Chemin du rapport final généré")
    parser.add_argument("--pattern", "-p", type=str, default="*.pdf", help="Motif glob pour filtrer les fichiers (ex: '*_IDS625_*.pdf')")
    parser.add_argument("--batch-size-15", type=int, default=35, help="Taille de lot Section 1.5")
    parser.add_argument("--batch-size-25", type=int, default=10, help="Taille de lot Section 2.5")
    parser.add_argument("--concurrency", type=int, default=5, help="Nombre maximum d'appels LLM concurrents")
    parser.add_argument("--time-limit", type=int, default=0, help="Limite de temps en secondes avant de faire une pause (0 = pas de limite)")
    args = parser.parse_args()

    # Définition des chemins de manière dynamique et robuste (anti-fragile)
    ws_root = get_workspace_root()
    
    # On cherche le dossier de données "client_data/EPH" de manière portable
    eph_path = ws_root / "client_data" / "EPH"
    if not eph_path.exists():
        eph_path = Path(os.getcwd()) / "client_data" / "EPH"
    
    eph_path = str(eph_path.resolve())
    
    # ANTI-FRAGILITÉ : Si l'agent force "client_data", on annule son paramètre
    if args.output and "client_data" in args.output.replace("\\", "/"):
        args.output = None

    if not args.output:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H")
        output_dir = get_helios_home() / "output" / "audit" / timestamp
        os.makedirs(output_dir, exist_ok=True)
        args.output = str((output_dir / "audit_report.md").resolve())
    else:
        args.output = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(args.output), exist_ok=True)

    checkpoint_file = args.output.replace(".md", "_checkpoint.jsonl")

    print("==================================================================")
    print("🚀 DÉMARRAGE DE L'AUDIT INDUSTRIEL DES DOCUMENTS EPH")
    print(f"Dossier source : {eph_path}")
    print("==================================================================")

    # 0. Load Checkpoint
    processed_files = set()
    all_rows = []
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        processed_files.add(data["file_path"])
                        for r in data.get("rows", []):
                            all_rows.append(ExchangeRow(
                                filename=r["filename"],
                                source_instance=r["source_instance"],
                                source_as=r["source_as"],
                                target_instance=r["target_instance"],
                                target_as=r["target_as"],
                                exchange_type=ExchangeType(r["exchange_type"])
                            ))
                    except Exception as e:
                        print(f"⚠️ Erreur de lecture du checkpoint: {e}")
        if processed_files:
            print(f"🔄 Reprise : {len(processed_files)} fichiers déjà traités chargés depuis le checkpoint.")

    pdf_files = glob.glob(os.path.join(eph_path, args.pattern))
    em_path = os.path.join(os.path.dirname(eph_path), "EM")
    if os.path.exists(em_path):
        pdf_files.extend(glob.glob(os.path.join(em_path, args.pattern)))

    if not pdf_files:
        print(f"❌ Aucun fichier PDF trouvé dans {eph_path} ou {em_path}")
        sys.exit(1)

    print(f"Trouvé {len(pdf_files)} fichiers PDF au total.")
    if args.limit:
        # Réactivé pour éviter les timeouts lors des phases de test rapide de l'agent.
        pdf_files = pdf_files[:args.limit]

    remaining_files = [f for f in pdf_files if f not in processed_files]
    print(f"Fichiers restants à traiter : {len(remaining_files)}")

    sem = asyncio.Semaphore(args.concurrency)
    chunk_size = 50  # Nombre de fichiers par lot de multiprocessing
    start_time = time.time()

    if remaining_files:
        print("\nTraitement des nouveaux fichiers (Multiprocessing & LLM)...")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for i in range(0, len(remaining_files), chunk_size):
                chunk_files = remaining_files[i:i + chunk_size]
                print(f"\n--- Traitement du lot {i//chunk_size + 1} ({len(chunk_files)} fichiers) ---")
                
                print("  1. Extraction du texte (Multiprocessing)...")
                loop = asyncio.get_running_loop()
                extract_tasks = [
                    loop.run_in_executor(executor, extract_sections_from_pdf, f)
                    for f in chunk_files
                ]
                chunk_docs_data = await asyncio.gather(*extract_tasks)

                print("  2. Analyse des Sections via le LLM...")
                rows_25 = await process_section(
                    chunk_docs_data, "2.5", SYSTEM_PROMPT_25, "List EPH external exchanges:",
                    args.batch_size_25, sem, args.verbose
                )
                rows_15 = await process_section(
                    chunk_docs_data, "1.5", SYSTEM_PROMPT_15, "List EPH-EM communications:",
                    args.batch_size_15, sem, args.verbose
                )
                
                chunk_rows = rows_25 + rows_15
                all_rows.extend(chunk_rows)

                # Sauvegarde du lot dans le checkpoint
                with open(checkpoint_file, "a", encoding="utf-8") as f:
                    for doc, fpath in zip(chunk_docs_data, chunk_files):
                        doc_rows = [r for r in chunk_rows if r.filename == doc["filename"]]
                        row_dicts = [
                            {
                                "filename": r.filename,
                                "source_instance": r.source_instance,
                                "source_as": r.source_as,
                                "target_instance": r.target_instance,
                                "target_as": r.target_as,
                                "exchange_type": r.exchange_type.value
                            } for r in doc_rows
                        ]
                        f.write(json.dumps({
                            "file_path": fpath,
                            "filename": doc["filename"],
                            "rows": row_dicts
                        }, ensure_ascii=False) + "\n")
                        
                print(f"  ✅ Lot terminé. Progression : {min(i + chunk_size, len(remaining_files))}/{len(remaining_files)}")

                if args.time_limit > 0 and (time.time() - start_time) > args.time_limit:
                    if i + chunk_size < len(remaining_files):
                        print("\n⏳ Limite de temps atteinte. Sauvegarde du checkpoint en cours...")
                        print("Fermeture propre pour autoriser la reprise (Exit 100).")
                        sys.exit(100)

    # 3. Consolidation et génération du rapport
    print(f"\n3. Consolidation du rapport final dans {args.output}...")
    
    # Séparer les résultats
    exchanges_25 = [r for r in all_rows if r.exchange_type == ExchangeType.EPH_TO_EPH]
    comms_15 = [r for r in all_rows if r.exchange_type == ExchangeType.EPH_EM]

    from datetime import datetime
    md_lines = [
        "# Rapport d'Audit Industriel EPH",
        "",
        "- **Auteur** : Agent Helios (Actemium)",
        f"- **Généré automatiquement le** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Nombre total de documents audités** : {len(processed_files) + len(remaining_files)}",
        f"- **Total des échanges externes extraits (Section 2.5)** : {len(exchanges_25)}",
        f"- **Total des communications EPH-EM extraites (Section 1.5)** : {len(comms_15)}",
        "",
        "## 1. Échanges Externes (Section 2.5)",
        "",
        "| Fichier Source | Instance Source | AS Source | Instance Cible | AS Cible | Type d'Échange |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for r in exchanges_25:
        md_lines.append(f"| {r.filename} | {r.source_instance} | {r.source_as} | {r.target_instance} | {r.target_as} | {r.exchange_type.value} |")

    if not exchanges_25:
        md_lines.append("| N.A. | Aucun échange trouvé | - | - | - | - |")

    md_lines.extend([
        "",
        "## 2. Communications EPH-EM (Section 1.5)",
        "",
        "| Fichier Source | Instance Source | AS Source | Instance Cible (Tag) | AS Cible | Type d'Échange |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ])

    for r in comms_15:
        md_lines.append(f"| {r.filename} | {r.source_instance} | {r.source_as} | {r.target_instance} | {r.target_as} | {r.exchange_type.value} |")

    if not comms_15:
        md_lines.append("| N.A. | Aucune communication trouvée | - | - | - | - |")

    # Écriture du rapport
    with open(args.output, "w", encoding="utf-8") as out_f:
        out_f.write("\n".join(md_lines))

    print("\n✅ AUDIT TERMINÉ ET RAPPORT CRÉÉ AVEC SUCCÈS !")
    print(f"  - Échanges 2.5 : {len(exchanges_25)} lignes")
    print(f"  - Communications 1.5 : {len(comms_15)} lignes")
    print(f"  - Fichier de sortie : {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
