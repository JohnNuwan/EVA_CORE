#!/usr/bin/env python3
"""Module Industrial Document Intelligence - Extraction de P&ID, BOM, datasheets."""
import json, logging
from pathlib import Path
from typing import Optional
logger = logging.getLogger(__name__)


def extract_tables_from_pdf(file_path: str, pages: Optional[str] = None) -> str:
    """Extrait les tableaux d'un document PDF technique (BOM, datasheets)."""
    path = Path(file_path)
    if not path.exists():
        return json.dumps({"error": f"Fichier introuvable: {file_path}"})
    try:
        import pdfplumber
    except ImportError:
        return json.dumps({"error": "Installez pdfplumber: pip install pdfplumber"})
    try:
        tables = []
        with pdfplumber.open(str(path)) as pdf:
            total_pages = len(pdf.pages)
            page_range = _parse_pages(pages, total_pages) if pages else list(range(total_pages))
            for pg_idx in page_range:
                if pg_idx >= total_pages:
                    continue
                page = pdf.pages[pg_idx]
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table and len(table) > 1:
                        tables.append({"page": pg_idx + 1, "rows": len(table), "cols": len(table[0]),
                                        "header": table[0], "sample_rows": table[1:4]})
        return json.dumps({"file": path.name, "total_pages": total_pages,
                            "tables_found": len(tables), "tables": tables}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _parse_pages(spec: str, max_pages: int) -> list:
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            s, e = part.split("-", 1)
            for p in range(int(s.strip()), int(e.strip()) + 1):
                pages.add(p - 1)
        else:
            pages.add(int(part) - 1)
    return [p for p in sorted(pages) if 0 <= p < max_pages]


from tools.registry import registry

registry.register(
    name="doc_intel_extract_tables",
    toolset="industrial",
    schema={"name": "doc_intel_extract_tables",
            "description": "Extrait les tableaux d'un PDF technique (BOM, datasheets).",
            "parameters": {"type": "object", "properties": {
                "file_path": {"type": "string", "description": "Chemin PDF"},
                "pages": {"type": "string", "description": "Pages (ex: 1-5,8) ou vide = toutes"}
            }, "required": ["file_path"]}},
    handler=lambda a, **kw: extract_tables_from_pdf(a.get("file_path", ""), a.get("pages")),
    is_async=False,
    description="Extraire les tableaux d'un document PDF technique.",
    emoji="📄",
)