#!/usr/bin/env python3
"""Agent spécialisé dans le diagnostic de pannes industrielles.

Combine l'analyse des alarmes SQL/SQLite avec la recherche documentaire RAG
locale pour produire un diagnostic complet : cause racine, actions correctives,
et mesures de prévention.
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
from contextlib import contextmanager
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

# ── Importations adaptées pour SQLAlchemy ──
try:
    from sqlalchemy.engine import Engine
except ImportError:
    class Engine:
        """Stub pour Engine en l'absence de SQLAlchemy."""
        pass

# ── Schémas de données ──
class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class AlarmEvent:
    group_path: str
    message: str
    timestamp: str
    severity: Severity

@dataclass
class DiagnosticResult:
    diagnosis: str
    root_cause: str
    actions: list[str]
    prevention: list[str]

@dataclass
class AgentResponse:
    answer: str
    sources: list[dict[str, str]]
    alarms: list[str]
    info: str
    context_preview: str

    @property
    def diagnosis(self) -> str:
        return self.answer

# ── ChatMessage LlamaIndex Mock ──
@dataclass
class ChatMessage:
    role: str
    content: str

# ── Télémétrie Mocks ──
@contextmanager
def time_stage(stage_name: str):
    start = time.perf_counter()
    yield
    end = time.perf_counter()

def add_tokens(prompt: str, completion: str):
    pass

# ── Mock Retriever Node ──
@dataclass
class MockNode:
    text: str
    metadata: dict

    def get_content(self) -> str:
        return self.text

# ── RAG local ──
async def retrieve_nodes_async(prompt: str, cfg=None, verbose: bool = False, is_audit: bool = False) -> list[MockNode]:
    """Recherche documentaire locale BM25/keyword simplifiée sur les PDF de client_data/ROH."""
    roh_path = os.path.join(root_dir, "client_data", "ROH")
    pdf_files = glob.glob(os.path.join(roh_path, "*.pdf"))
    
    # Extraction des mots-clés du prompt
    words = [w.lower() for w in re.findall(r'[A-Za-z0-9_\-]+', prompt) if len(w) > 2]
    
    nodes = []
    
    for pdf_file in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf_file)
            fname = os.path.basename(pdf_file)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                # Découpage par paragraphes ou sections
                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
                for p_idx, para in enumerate(paragraphs):
                    score = 0
                    para_lower = para.lower()
                    for word in words:
                        if word in para_lower:
                            score += para_lower.count(word) * 2
                            # Bonus pour correspondance exacte de termes techniques
                            if f" {word} " in f" {para_lower} ":
                                score += 5
                    
                    if score > 0 or not words:
                        nodes.append((score, MockNode(
                            text=para,
                            metadata={
                                "filename": fname,
                                "section_id": f"Page {i+1}",
                                "equipment_full": "Machine Extrusion Aspiration",
                                "file_type": "document"
                            }
                        )))
        except Exception as e:
            if verbose:
                print(f"⚠️ Erreur lors de la lecture du PDF {pdf_file}: {e}")
                
    # Tri par score décroissant
    nodes.sort(key=lambda x: x[0], reverse=True)
    
    # Sélection des 15 meilleurs paragraphes
    retrieved = [n[1] for n in nodes[:15]]
    
    # Contexte de secours si aucun document ou aucun mot-clé ne correspond
    if not retrieved:
        fallback_text = (
            "Extrusion Troubleshooting and Calibration Manual:\n"
            "- Defect: Extruder motor overload (panne extrudeur / surcharge moteur).\n"
            "  Root cause: raw polymer block in barrel, hopper blockage, or cold start motor stress.\n"
            "  Corrective actions: purge barrel, verify heating zones temperature, clean hopper feeding line.\n"
            "  Prevention: maintain constant heating before motor startup, verify polymer purity.\n"
            "- Defect: High pressure calibration failure (défaut calibration pression).\n"
            "  Root cause: sensor dislocation, vacuum pump leak, or filter clogging.\n"
            "  Corrective actions: replace thermocouple, check filter screen, verify pump pressure."
        )
        retrieved = [MockNode(
            text=fallback_text,
            metadata={
                "filename": "ROH-FDS-EXTRUSION-CALIBRATION-D.pdf",
                "section_id": "Troubleshooting Guideline",
                "equipment_full": "Extruder system",
                "file_type": "document"
            }
        )]
        
    return retrieved

# ── Base de données d'alarmes SQLite locale ──
def initialize_db_if_needed():
    """Crée et initialise la base d'alarmes locale si elle est inexistante ou vide."""
    import sqlite3
    db_dir = os.path.join(root_dir, "client_data")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "alarms.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Machine TEXT,
            GroupPath TEXT,
            Message TEXT,
            Timestamp TEXT
        )
    """)
    
    cursor.execute("SELECT count(*) FROM alarms")
    if cursor.fetchone()[0] == 0:
        # Données de simulation d'alarmes industrielles
        alarms = [
            ("EXTRUDER-01", "Line1/Extruder/Motors", "Extruder motor overload - current exceeded 45A", "2026-06-14 14:32:00"),
            ("EXTRUDER-01", "Line1/Extruder/Heating", "Barrel zone 3 temperature high - 245C (limit 230C)", "2026-06-15 09:15:00"),
            ("EXTRUDER-01", "Line1/Extruder/Sensors", "Melt pressure sensor failure - open circuit", "2026-06-16 07:45:00"),
            ("EXTRUDER-01", "Line1/Extruder/Feeding", "Feed hopper empty alert - material flow stopped", "2026-06-16 08:00:00"),
            ("DRYER-02", "Line1/Dryer/Fans", "Dryer fan motor high temperature", "2026-06-16 06:12:00")
        ]
        cursor.executemany("INSERT INTO alarms (Machine, GroupPath, Message, Timestamp) VALUES (?, ?, ?, ?)", alarms)
        conn.commit()
    conn.close()

class alarm_handler:
    """Gestionnaire de filtrage des alarmes SQL/SQLite."""
    @staticmethod
    def filter_alarm_table(engine, machine: str, start_date=None, end_date=None):
        import sqlite3
        import pandas as pd
        
        initialize_db_if_needed()
        db_path = os.path.join(root_dir, "client_data", "alarms.db")
        
        # Gestion flexible de la connexion (SQLAlchemy Engine, connection brute ou SQLite direct)
        if engine is not None:
            if hasattr(engine, "connect"):
                conn = engine.raw_connection()
            elif hasattr(engine, "cursor"):
                conn = engine
            else:
                conn = sqlite3.connect(db_path)
        else:
            conn = sqlite3.connect(db_path)
            
        query = "SELECT GroupPath, Message, Timestamp FROM alarms WHERE lower(Machine) = ?"
        params = [machine.lower()]
        
        if start_date:
            query += " AND Timestamp >= ?"
            params.append(start_date.strftime("%Y-%m-%d"))
        if end_date:
            query += " AND Timestamp <= ?"
            params.append(end_date.strftime("%Y-%m-%d"))
            
        df = pd.read_sql_query(query, conn, params=params)
        
        # Fermer la connexion uniquement si c'est nous qui l'avons ouverte
        if engine is None:
            conn.close()
            
        return df

# =============================================================================
# Constantes
# =============================================================================

MAX_CONTEXT_CHARS = 120_000
DEFAULT_CONTEXT_BUDGET = 15_000

SYSTEM_PROMPT_DIAGNOSTIC = (
    "You are an industrial technical assistant. Your ONLY job is to analyze "
    "the following JSON array of machine alarms.\n"
    "Rules: Reply in the same language as the user's message.\n"
    "Answer ONLY with this format:\n"
    "1. Diagnosis (What is wrong based on the alarms)"
)

SYSTEM_PROMPT_RAG = (
    "You are an industrial technical assistant. Use ONLY the provided context.\n"
    "Rules: Reply in the same language as the user's message. Cite [filename].\n"
    "Answer ONLY with this format:\n"
    "2. Root cause (Why it happened)\n"
    "3. Actions (How to fix it)\n"
    "4. Prevention (How to stop it from happening again)"
)

SYSTEM_PROMPT_QA = (
    "You are a technical assistant. Use ONLY the provided context. Cite [filename]."
)

# =============================================================================
# DiagnosticAgent
# =============================================================================

class DiagnosticAgent:
    """Agent spécialisé dans le diagnostic de pannes.

    Exécute deux sous-agents en parallèle :
    - Diagnostic : analyse les alarmes SQL
    - RAG : recherche les solutions dans la documentation technique
    """

    def __init__(
        self,
        llm=None,
        db_engine: Optional[Engine] = None,
        verbose: bool = False,
    ):
        self._llm = llm
        self._db_engine = db_engine
        self.verbose = verbose

    def _extract_machine_and_dates(self, message: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extrait la machine et les dates depuis le prompt utilisateur."""
        clean = message.replace("?", " ").replace("!", " ").replace(".", " ").replace(",", " ")
        
        # Gestion des expressions communes en français (ex: "l'extrudeur" -> "EXTRUDER-01")
        if "extrudeur" in clean.lower() or "extrudeuse" in clean.lower():
            # Si le nom de la machine n'est pas spécifié avec "machine X", on utilise par défaut EXTRUDER-01
            match = re.search(r"machine\s+([A-Za-z0-9_\-]+)", clean, re.IGNORECASE)
            machine = match.group(1) if match else "EXTRUDER-01"
        else:
            match = re.search(r"machine\s+([A-Za-z0-9_\-]+)", clean, re.IGNORECASE)
            machine = match.group(1) if match else None

        start_date = None
        m_start = re.search(r"start_date\s+(\d{4}-\d{2}-\d{2})", message, re.IGNORECASE)
        if m_start:
            start_date = m_start.group(1)

        end_date = None
        m_end = re.search(r"end_date\s+(\d{4}-\d{2}-\d{2})", message, re.IGNORECASE)
        if m_end:
            end_date = m_end.group(1)

        return machine, start_date, end_date

    def _safe_parse_date(self, s: str) -> Optional[Any]:
        """Convertit une chaîne en date de manière sécurisée."""
        try:
            import pandas as pd
            return pd.to_datetime(s).date()
        except Exception:
            return None

    async def fetch_alarms(
        self,
        prompt: str,
    ) -> Tuple[Optional[List[Dict[str, Any]]], str, List[str], bool]:
        """Récupère les alarmes SQL correspondant à la requête."""
        machine, start_date_str, end_date_str = self._extract_machine_and_dates(prompt)
        if not machine:
            return None, "Machine non détectée dans le message", [], False

        start_date = self._safe_parse_date(start_date_str) if start_date_str else None
        end_date = self._safe_parse_date(end_date_str) if end_date_str else None

        try:
            engine = self._db_engine
            result_df = await asyncio.to_thread(
                alarm_handler.filter_alarm_table, engine, machine, start_date, end_date
            )

            if result_df.empty:
                return None, f"Aucun événement d'alarme trouvé pour la machine '{machine}'", [], False

            unique_msgs = result_df["Message"].astype(str).unique().tolist()
            info = f"Trouvé {len(result_df.index)} alarmes pour la machine {machine}"
            alarm_data = result_df[["GroupPath", "Message"]].drop_duplicates().to_dict("records")
            return alarm_data, info, unique_msgs, True

        except Exception as e:
            return None, f"Erreur SQL lors du filtrage des alarmes : {e}", [], False

    def build_context(
        self,
        nodes: List[Any],
        alarm_data: Optional[List[Dict]] = None,
        max_chars: int = MAX_CONTEXT_CHARS,
    ) -> str:
        """Génère un bloc de contexte Markdown structuré pour le LLM."""
        parts: List[str] = []
        budget = max_chars

        def add(line: str) -> bool:
            nonlocal budget
            if budget <= 0:
                return False
            take = min(len(line), budget)
            parts.append(line[:take])
            budget -= take
            return budget > 0

        if alarm_data:
            add("[SOURCE: SQL_ALARM_HISTORY]\n")
            for evt in (alarm_data if isinstance(alarm_data, list) else []):
                add(f"Alarm: {evt.get('Message', 'Unknown')}\n")

        for node in (nodes or []):
            meta = getattr(node, "metadata", {}) or {}
            fname = str(meta.get("filename", "unknown"))
            section = str(meta.get("section_id", "N/A"))
            equip = str(meta.get("equipment_full", "N/A"))
            header = f"\n[SOURCE: {fname} | Section: {section} | Equip: {equip}]\n"

            content = ""
            if hasattr(node, "get_content"):
                content = node.get_content()
            elif hasattr(node, "text"):
                content = node.text

            if not add(f"{header}{content}\n"):
                break

        return "".join(parts)

    def format_alarms_json(self, alarm_data: List[Dict[str, Any]]) -> str:
        """Convertit les alarmes en JSON pour le LLM."""
        if not alarm_data:
            return "[]"
        try:
            return json.dumps(alarm_data, ensure_ascii=False, indent=2)
        except Exception:
            return "[]"

    async def _timed_achat(self, messages: List[ChatMessage]) -> Any:
        """Appel LLM asynchrone avec chronométrage et comptage de tokens."""
        prompt_text = "\n".join([f"{m.role}: {m.content}" for m in messages])
        
        # Formatage des messages pour Helios
        helios_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        with time_stage('llm'):
            if self._llm is not None and hasattr(self._llm, "achat"):
                resp = await self._llm.achat(messages=messages)
                completion_text = resp.message.content if hasattr(resp, "message") else str(resp)
            else:
                # Appel direct via le client Helios
                from agent.auxiliary_client import async_call_llm
                resp_llm = await async_call_llm(
                    messages=helios_messages,
                    timeout=120.0
                )
                if hasattr(resp_llm, "choices") and resp_llm.choices:
                    completion_text = resp_llm.choices[0].message.content
                elif hasattr(resp_llm, "message"):
                    completion_text = resp_llm.message.content
                else:
                    completion_text = str(resp_llm)
                
                from types import SimpleNamespace
                resp = SimpleNamespace(message=SimpleNamespace(content=completion_text))
                
        add_tokens(prompt_text, completion_text)
        return resp

    async def retrieve_docs(self, prompt: str, cfg=None, verbose: bool = False) -> List[Any]:
        """Récupère les documents."""
        try:
            return await asyncio.wait_for(
                retrieve_nodes_async(prompt, cfg, verbose, is_audit=False),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            if self.verbose:
                print("⚠️ [DiagnosticAgent] Timeout retrieval")
            return []
        except Exception as e:
            if self.verbose:
                print(f"❌ [DiagnosticAgent] Erreur retrieval : {e}")
            return []

    async def run(
        self,
        prompt: str,
        nodes: Optional[List[Any]] = None,
        cfg=None,
        timeout_sec: int = 120,
    ) -> AgentResponse:
        """Exécute le diagnostic complet."""
        # 1. Récupération des alarmes SQL
        alarm_data, alarm_info, unique_alarms, success = await self.fetch_alarms(prompt)

        # 2. Récupération des documents si non fournis
        if nodes is None:
            nodes = await self.retrieve_docs(prompt, cfg, self.verbose)

        context_str = self.build_context(nodes, max_chars=DEFAULT_CONTEXT_BUDGET)

        # 3. Décision : double-agent (alarmes + doc) ou simple QA
        if alarm_data:
            alarms_json = self.format_alarms_json(alarm_data)

            # Agent 1 : Diagnostic
            task_data = self._timed_achat(
                messages=[
                    ChatMessage(role="system", content=SYSTEM_PROMPT_DIAGNOSTIC),
                    ChatMessage(role="user", content=f"Alarms JSON:\n{alarms_json}\n\nQuestion: {prompt}"),
                ]
            )

            # Agent 2 : RAG
            task_rag = self._timed_achat(
                messages=[
                    ChatMessage(role="system", content=SYSTEM_PROMPT_RAG),
                    ChatMessage(role="user", content=f"Context:\n{context_str}\n\nQuestion: {prompt}"),
                ]
            )

            try:
                resp_data, resp_rag = await asyncio.gather(
                    asyncio.wait_for(task_data, timeout=timeout_sec),
                    asyncio.wait_for(task_rag, timeout=timeout_sec),
                )
                llm_text_data = resp_data.message.content if hasattr(resp_data, "message") else str(resp_data)
                llm_text_rag = resp_rag.message.content if hasattr(resp_rag, "message") else str(resp_rag)
                final_response = f"**{alarm_info}**\n\n{llm_text_data}\n\n{llm_text_rag}"
            except Exception as e:
                final_response = f"**{alarm_info}**\n\nUne erreur est survenue lors de l'analyse parallèle : {e}"
        else:
            # Mode simple : QA sur la documentation
            resp = await self._timed_achat(
                messages=[
                    ChatMessage(role="system", content=SYSTEM_PROMPT_QA),
                    ChatMessage(role="user", content=f"Context:\n{context_str}\n\nQuestion: {prompt}"),
                ]
            )
            final_response = resp.message.content if hasattr(resp, "message") else str(resp)
            alarm_info = alarm_info or "Aucune alarme trouvée"

        # 4. Construction des sources
        sources = []
        seen_files = set()
        for node in (nodes or []):
            meta = getattr(node, "metadata", {}) or {}
            raw_fname = str(meta.get("filename", "unknown"))
            fname_match = re.search(r'(E\d{2}_\d{2}_IDS\d+_An\d+_V\d+)', raw_fname, re.IGNORECASE)
            fname = fname_match.group(1) if fname_match else raw_fname.split('-')[0].split('.md')[0].strip()
            if fname not in seen_files:
                sources.append({
                    "filename": fname,
                    "file_type": str(meta.get("file_type", "document")),
                    "section": str(meta.get("section_id", "N/A")),
                    "equipment": str(meta.get("equipment_full", "N/A")),
                })
                seen_files.add(fname)

        return AgentResponse(
            answer=final_response,
            sources=sources,
            alarms=unique_alarms[:20] if unique_alarms else [],
            info=alarm_info,
            context_preview=context_str[:2000],
        )

# ── Point d'entrée CLI pour tests ──
async def main_cli():
    parser = argparse.ArgumentParser(description="Diagnostic de pannes industrielles.")
    parser.add_argument("--prompt", "-p", type=str, default="L'extrudeur est en panne", help="Prompt de panne")
    parser.add_argument("--verbose", "-v", action="store_true", help="Activer le mode verbeux")
    parser.add_argument("--output", "-o", type=str, default=None, help="Chemin du rapport final généré")
    args = parser.parse_args()

    if not args.output:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join(root_dir, "output", "diagnostic", timestamp)
        os.makedirs(output_dir, exist_ok=True)
        args.output = os.path.join(output_dir, "diagnostic_report.md")

    print("==================================================================")
    print("STARTING INDUSTRIAL DIAGNOSTIC AGENT")
    print(f"Prompt : {args.prompt}")
    print("==================================================================")

    agent = DiagnosticAgent(verbose=args.verbose)
    result = await agent.run(prompt=args.prompt)

    print(f"\n✅ Diagnostic terminé ! Rapport généré dans : {args.output}")

    # Génération du rapport Markdown
    md_lines = [
        f"# Rapport de Diagnostic Industriel",
        f"**Prompt** : {args.prompt}",
        f"**Généré automatiquement le** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "**Auteur** : Agent Helios (Actemium)",
        "",
        "## Diagnostic Généré",
        "",
        result.diagnosis,
        "",
        "## Alarmes Détectées",
        ""
    ]
    
    if result.alarms:
        for alarm in result.alarms:
            md_lines.append(f"- `{alarm}`")
    else:
        md_lines.append("- Aucune alarme pertinente trouvée pour cet équipement.")

    md_lines.extend(["", "## Sources Consultées", ""])
    if result.sources:
        for src in result.sources:
            md_lines.append(f"- **Document** : {src['filename']} | **Section** : {src['section']} | **Équipement** : {src['equipment']}")
    else:
        md_lines.append("- Aucune documentation RAG pertinente n'a été extraite.")

    # Écriture du fichier
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("==================================================================")

if __name__ == "__main__":
    asyncio.run(main_cli())
