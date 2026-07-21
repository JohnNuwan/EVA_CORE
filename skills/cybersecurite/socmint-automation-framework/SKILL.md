---
name: socmint-automation-framework
description: SOCMINT — framework d'automatisation d'enquêtes, orchestration multi-outils, pipelines de collecte, gestion de preuves, rapports automatisés et chaîne de traçabilité.
category: cybersecurite
author: EVA
version: 1.0
tags: [socmint, automation, framework, orchestration, pipeline, reporting, forensics, chain-of-custody]
---

# SOCMINT : Framework d'Automatisation

## 🎯 Description

Framework complet pour automatiser les enquêtes SOCMINT de bout en bout : orchestration des outils OSINT, pipelines de collecte parallélisés, gestion de preuves avec chaîne de traçabilité, rapports automatisés, et déploiement d'agents de surveillance persistants.

Ce skill transforme l'approche artisanale (outil par outil, copier-coller manuel) en **pipeline industrialisé** reproductible et scalable.

---

## 🏗️ Architecture du Framework

```
[Phase 1 : Ciblage]         [Phase 2 : Collecte]         [Phase 3 : Analyse]        [Phase 4 : Rapport]
      │                          │                            │                          │
      ▼                          ▼                            ▼                          ▼
┌──────────┐            ┌──────────────────┐          ┌──────────────┐          ┌──────────────┐
│ Identifier │            │ Scraper parallele  │          │Analyse Graphe │          │  Rapport PDF  │
│ cible     │──▶         │ + API + OSINT tools │──▶       │ + NLP +       │──▶       │  + Dashboard  │
│ (username,│            │ (multi-thread)     │          │Corrélation    │          │  + Archive    │
│ email, ID)│            └──────────────────┘          └──────────────┘          └──────────────┘
└──────────┘                     │                            │                        │
                                 ▼                            ▼                        ▼
                        ┌──────────────────┐          ┌──────────────┐          ┌──────────────┐
                        │  Cache SQLite +   │          │  Evidence    │          │  Wayback +    │
                        │  Screenshots PNG  │          │  DB (forensic)│          │  Blockchain   │
                        └──────────────────┘          └──────────────┘          └──────────────┘
```

---

## 📦 Socle : socmint-core.py

### Structure du Framework
```python
# socmint_core.py — Framework de base SOCMINT

import json
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class SOCMINTCase:
    """Gestion de cas d'enquête SOCMINT avec chaîne de traçabilité"""
    
    def __init__(self, case_name: str, investigator: str):
        self.case_name = case_name
        self.investigator = investigator
        self.case_dir = Path(f"cases/{case_name}_{datetime.now():%Y%m%d_%H%M%S}")
        self.case_dir.mkdir(parents=True, exist_ok=True)
        
        # Base de données des preuves
        self.db_path = self.case_dir / "evidence.db"
        self.init_db()
        
        # Journal des actions
        self.log_file = self.case_dir / "audit_log.json"
        self.actions = []
    
    def init_db(self):
        """Base de données forensique avec hash de chaque élément"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                platform TEXT NOT NULL,
                target TEXT NOT NULL,
                content_type TEXT NOT NULL,
                raw_data TEXT,
                sha256 TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                collected_by TEXT NOT NULL,
                notes TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chain_of_custody (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_id INTEGER,
                action TEXT NOT NULL,
                actor TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (evidence_id) REFERENCES evidence(id)
            )
        """)
        conn.commit()
        conn.close()
    
    def add_evidence(self, source: str, platform: str, target: str,
                     content_type: str, raw_data: str, notes: str = "") -> int:
        """Ajoute une preuve avec hash SHA256"""
        sha256 = hashlib.sha256(raw_data.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            INSERT INTO evidence 
            (source, platform, target, content_type, raw_data, sha256, timestamp, collected_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (source, platform, target, content_type, raw_data, sha256,
              datetime.now().isoformat(), self.investigator, notes))
        
        evidence_id = cur.lastrowid
        conn.commit()
        conn.close()
        
        # Enregistrer dans le journal
        self.log_action(f"EVIDENCE_ADDED:{evidence_id}", 
                       f"Platform={platform} Target={target} Type={content_type}")
        
        return evidence_id
    
    def log_action(self, action: str, description: str = ""):
        """Journal d'audit horodaté"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "actor": self.investigator,
            "description": description
        }
        self.actions.append(entry)
        
        with open(self.log_file, "w") as f:
            json.dump(self.actions, f, indent=2)
    
    def export_case(self) -> Dict:
        """Export complet du cas pour rapport"""
        return {
            "case_name": self.case_name,
            "investigator": self.investigator,
            "created": str(self.case_dir.name),
            "evidence_count": len(self.actions),
            "db_path": str(self.db_path),
            "log_path": str(self.log_file)
        }
```

---

## 🔧 Modules Automatisés

### Module 1 : Collecte Automatique Multi-Plateforme
```python
# socmint_collect.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

class SOCMINTCollector:
    def __init__(self, case: SOCMINTCase, target_config: Dict):
        self.case = case
        self.config = target_config
    
    def collect_all(self):
        """Lance la collecte sur toutes les cibles en parallèle"""
        targets = self.config.get("targets", [])
        collectors = {
            "username": self.collect_username,
            "email": self.collect_email,
            "phone": self.collect_phone,
            "domain": self.collect_domain,
        }
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for target in targets:
                collector = collectors.get(target["type"])
                if collector:
                    futures.append(executor.submit(collector, target["value"]))
            
            results = [f.result() for f in futures]
        
        self.case.log_action("COLLECTION_COMPLETE", 
                           f"{len(targets)} targets collected")
        return results
    
    def collect_username(self, username: str):
        """Maigret + Sherlock + Blackbird en parallèle"""
        from subprocess import run
        
        # Maigret
        result_m = run(["maigret", username, "--all", 
                       "--output", f"{self.case.case_dir}/maigret_{username}.json"],
                      capture_output=True, timeout=120)
        self.case.add_evidence("maigret", "multi", username, "json",
                              result_m.stdout.decode())
        
        # Blackbird
        result_b = run(["blackbird", "-u", username, "-f", "json",
                       "-o", f"{self.case.case_dir}/blackbird_{username}.json"],
                      capture_output=True, timeout=120)
        self.case.add_evidence("blackbird", "multi", username, "json",
                              result_b.stdout.decode())
        
        return {"username": username, "maigret": True, "blackbird": True}
```

### Module 2 : Screenshot Automatisé
```python
# socmint_screenshot.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

class SOCMINTScreenshotter:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920x1080")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
        )
        self.driver = webdriver.Chrome(options=options)
    
    def screenshot_profile(self, platform: str, username: str, save_path: Path):
        urls = {
            "twitter": f"https://x.com/{username}",
            "instagram": f"https://instagram.com/{username}",
            "reddit": f"https://reddit.com/u/{username}",
            "tiktok": f"https://tiktok.com/@{username}",
            "github": f"https://github.com/{username}",
        }
        
        url = urls.get(platform)
        if not url:
            return None
        
        self.driver.get(url)
        time.sleep(3)  # Attendre le chargement
        screenshot_path = save_path / f"{platform}_{username}.png"
        self.driver.save_screenshot(str(screenshot_path))
        return screenshot_path
    
    def close(self):
        self.driver.quit()
```

### Module 3 : Analyse Automatisée
```python
# socmint_analyze.py
import networkx as nx
import json
from datetime import datetime

class SOCMINTAnalyzer:
    def __init__(self, case: SOCMINTCase):
        self.case = case
    
    def analyze_network(self, followers_data: List[Dict]):
        """Analyse du graphe social"""
        G = nx.DiGraph()
        
        for item in followers_data:
            G.add_edge(item["follower"], item["target"])
        
        return {
            "density": nx.density(G),
            "communities": len(list(nx.community.greedy_modularity_communities(
                G.to_undirected()))),
            "top_influencers": sorted(
                nx.betweenness_centrality(G).items(),
                key=lambda x: x[1], reverse=True
            )[:10]
        }
    
    def analyze_temporal(self, posts: List[Dict]):
        """Analyse temporelle des posts"""
        hours = [datetime.fromisoformat(p["created_at"]).hour for p in posts]
        days = [datetime.fromisoformat(p["created_at"]).strftime("%A") for p in posts]
        
        from collections import Counter
        return {
            "peak_hour": Counter(hours).most_common(1)[0][0],
            "active_day": Counter(days).most_common(1)[0][0],
            "post_frequency": len(posts) / max(1, (max(hours) - min(hours)))
        }
    
    def correlation_matrix(self, accounts: List[Dict]):
        """Matrice de corrélation cross-platform"""
        matrix = {}
        for a in accounts:
            signals = 0
            if a.get("same_username"): signals += 1
            if a.get("same_email"): signals += 2
            if a.get("same_avatar"): signals += 1
            if a.get("same_bio"): signals += 1
            if a.get("cross_link"): signals += 2
            
            confidence = "CONFIRMÉ" if signals >= 4 else \
                         "PROBABLE" if signals >= 2 else \
                         "POSSIBLE" if signals >= 1 else "FAIBLE"
            matrix[a["platform"]] = confidence
        
        return matrix
```

---

## 📄 Générateur de Rapports Automatisé

```python
# socmint_report.py
class SOCMINTReport:
    def __init__(self, case: SOCMINTCase, analyzer: SOCMINTAnalyzer):
        self.case = case
        self.analyzer = analyzer
    
    def generate_markdown(self) -> str:
        """Génère un rapport Markdown complet"""
        
        conn = sqlite3.connect(self.case.db_path)
        evidence_count = conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
        platforms = conn.execute(
            "SELECT platform, COUNT(*) FROM evidence GROUP BY platform"
        ).fetchall()
        conn.close()
        
        import datetime
        now = datetime.datetime.now()
        
        report = f"""# Rapport SOCMINT : {self.case.case_name}

**Investigateur** : {self.case.investigator}
**Date** : {now.strftime('%Y-%m-%d %H:%M')}
**ID Cas** : {self.case.case_dir.name}

---

## Résumé

- **Preuves collectées** : {evidence_count}
- **Plateformes couvertes** : {len(platforms)}
"""
        for p, c in platforms:
            report += f"  - {p}: {c} items\n"
        
        report += """
## Chaîne de Traçabilité

| # | Plateforme | Type | Hash SHA256 | Horodatage |
|---|-----------|------|-------------|------------|
"""
        conn = sqlite3.connect(self.case.db_path)
        rows = conn.execute(
            "SELECT id, platform, content_type, sha256, timestamp FROM evidence"
        ).fetchall()
        for r in rows:
            report += f"| {r[0]} | {r[1]} | {r[2]} | {r[3][:16]}... | {r[4]} |\n"
        conn.close()
        
        report += """
---
*Rapport généré automatiquement par le framework SOCMINT EVA*
"""
        return report
    
    def export_pdf(self, markdown_path: Path):
        """Convertit le rapport Markdown en PDF"""
        import subprocess
        subprocess.run([
            "pandoc", str(markdown_path), 
            "-o", str(markdown_path.with_suffix(".pdf")),
            "--pdf-engine=weasyprint"
        ], check=True)
```

---

## 🚀 Pipeline Complet

```python
#!/usr/bin/env python3
"""socmint_pipeline.py — Pipeline d'enquête automatisée"""

from socmint_core import SOCMINTCase
from socmint_collect import SOCMINTCollector
from socmint_analyze import SOCMINTAnalyzer
from socmint_report import SOCMINTReport

def run_full_investigation(target_config: Dict, investigator: str = "EVA"):
    """
    Pipeline complet SOCMINT :
    1. Initialisation du cas
    2. Collecte multi-cible
    3. Analyse des données
    4. Génération du rapport
    """
    
    # Phase 1 : Initialisation
    case = SOCMINTCase(
        case_name=target_config.get("name", "anonymous"),
        investigator=investigator
    )
    case.log_action("CASE_CREATED", f"Target: {target_config.get('name')}")
    
    # Phase 2 : Collecte
    collector = SOCMINTCollector(case, target_config)
    collector.collect_all()
    
    # Phase 3 : Analyse
    analyzer = SOCMINTAnalyzer(case)
    # ... appliquer les analyses selon les données disponibles
    
    # Phase 4 : Rapport
    report = SOCMINTReport(case, analyzer)
    md = report.generate_markdown()
    
    report_path = case.case_dir / "report.md"
    report_path.write_text(md)
    
    print(f"✅ Enquête terminée : {case.case_dir}")
    print(f"📄 Rapport : {report_path}")
    print(f"🗄️ Base de preuves : {case.db_path}")
    
    return case
```

---

## 📊 Templates de Rapports

### Structure Standard
```
1. HEADER — Informations du cas
2. RÉSUMÉ EXÉCUTIF — Synthèse 1 page
3. MÉTHODOLOGIE — Outils et techniques utilisés
4. COLLECTE — Plateformes, cibles, données recueillies
5. ANALYSE — Corrélations, graphes, timelines
6. PREUVES — Tableau avec SHA256, source, timestamp
7. CHAÎNE DE TRAÇABILITÉ — Historique des actions
8. CONCLUSIONS — Certitudes, probabilités, lacunes
9. ANNEXES — Screenshots, exports bruts
```

### Exemple Automatique
```bash
# Usage
python3 socmint_pipeline.py --name "John Doe Investigation" \
    --username johndoe \
    --email john@example.com \
    --phone "+33612345678" \
    --output ~/cases/
```

---

## 🛠️ Orchestration avec Cron

```bash
# Surveillance quotidienne automatisée
# /etc/cron.d/socmint
0 6 * * * aza /usr/bin/python3 /home/aza/socmint/monitor_pipeline.py \
    --target "@target_username" \
    --webhook "https://discord.com/api/webhooks/..." \
    --output /home/aza/cases/monitoring/

# Rapport hebdomadaire
0 9 * * 1 aza /usr/bin/python3 /home/aza/socmint/weekly_report.py \
    --case /home/aza/cases/monitoring/latest/
```

---

## 📁 Structure du Cas (Output)

```
cases/Enquete_X_20250722_143022/
├── evidence.db          # Base SQLite forensique
├── audit_log.json       # Journal d'audit complet
├── report.md            # Rapport Markdown
├── report.pdf           # Rapport PDF (via pandoc)
├── screenshots/         # Captures d'écran
│   ├── twitter_johndoe.png
│   ├── instagram_johndoe.png
│   └── reddit_johndoe.png
├── exports/             # Données brutes
│   ├── maigret_johndoe.json
│   ├── blackbird_johndoe.json
│   └── holehe_john@example.com.json
└── graph/              # Analyses
    ├── social_graph.html
    ├── timeline.png
    └── correlation.json
```

---

## ⚠️ Pitfalls

- **Dépendances fragiles** : 15+ outils avec des APIs qui changent — tests réguliers nécessaires
- **Rate limiting** : la parallélisation agressive peut faire bannir les IPs
- **Stockage** : une enquête complète peut générer 50-500 Mo de screenshots + données
- **Chaîne de traçabilité** : toute modification manuelle des preuves casse la chaîne — toujours utiliser l'API
- **Sécurité** : les données d'enquête contiennent des informations sensibles — chiffrer le dossier case
- **Pandoc** : nécessaire pour la conversion PDF (sinon, Markdown uniquement)
- **Évolutivité** : pour 100+ cibles, passer à une queue Redis + workers Celery