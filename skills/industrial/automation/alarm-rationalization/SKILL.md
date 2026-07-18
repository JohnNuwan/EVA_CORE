---
name: alarm-rationalization
description: "Analyser et rationaliser les alarmes selon ISA-18.2."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [alarm-management, isa-18-2, iec-62682, rationalization, scada, hmi, industrial-automation]
    related_skills: [ignition-scada, siemens-audit, industrial-diagnostic, oee-performance]
---

# Rationalisation & Gestion des Alarmes Industrielles (ISA-18.2)

## Vue d'ensemble

La **gestion des alarmes** est un enjeu critique dans les usines modernes. Un opérateur confronté à plus de **10 alarmes par heure** (seuil ISA-18.2) ne peut plus réagir efficacement, ce qui entraîne des accidents, des arrêts non planifiés et des pertes de production. Le phénomène de **nuisance alarms** (alarmes inutiles) et d'**alarm flooding** (avalanche d'alarmes) est la première cause d'incidents opérationnels en industrie.

La norme **ISA-18.2 / IEC 62682** définit le cycle de vie complet de la gestion des alarmes : identification, rationalisation, conception, implémentation, exploitation, surveillance et audit.

Cette compétence guide l'agent Helios pour :
1. Analyser des **historiques d'alarmes** exportés depuis WinCC, Ignition ou Wonderware.
2. Calculer les **KPIs d'alarmes ISA-18.2** (alarmes/heure/opérateur, standing alarms, chattering).
3. Produire une **matrice de rationalisation** (priorité, conséquence, action requise, délai de réponse).
4. Identifier les **top offenders** (alarmes les plus fréquentes) et proposer des actions correctives.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'analyser un export d'historique d'alarmes (CSV, SQL) pour identifier les problèmes.
- De calculer les KPIs d'alarmes conformes à ISA-18.2 (alarmes/heure, standing ratio, chattering).
- De concevoir ou de réviser une matrice de rationalisation des alarmes.
- De préparer un audit ou un rapport de conformité ISA-18.2.

**Ne pas utiliser pour :**
- La programmation de blocs de gestion d'alarmes dans un automate PLC (utiliser `siemens-scl`).
- Le diagnostic de pannes en temps réel (utiliser `industrial-diagnostic`).

---

## 1. KPIs d'Alarmes selon ISA-18.2

La norme définit des seuils de performance clairs pour un système d'alarmes bien géré :

| KPI | Cible ISA-18.2 | Seuil d'Alerte | Description |
|---|:---:|:---:|---|
| **Alarmes par heure par opérateur** | ≤ 6 | > 10 | Charge moyenne d'alarmes que l'opérateur doit traiter |
| **Taux de standing alarms** | < 5% | > 10% | Alarmes actives en permanence (non résolues) |
| **Taux de chattering alarms** | < 1% | > 5% | Alarmes oscillant rapidement ON/OFF (> 3 transitions/min) |
| **Taux de stale alarms** | < 2% | > 5% | Alarmes activées depuis plus de 24h sans action |
| **Ratio alarmes priorité 1 (Urgentes)** | < 5% | > 10% | Part des alarmes de criticité maximale |
| **Flood rate** | < 10 alarmes/10min | > 30/10min | Débit d'alarmes lors d'un événement déclencheur |

---

## 2. Script d'Analyse d'Historique d'Alarmes

Ce script Python analyse un fichier CSV d'export d'alarmes et calcule les KPIs ISA-18.2 :

```python
import pandas as pd
from datetime import timedelta
from collections import Counter


def analyze_alarm_history(csv_path: str, timestamp_col: str = "Timestamp",
                          tag_col: str = "TagName", state_col: str = "State",
                          priority_col: str = "Priority") -> dict:
    """Analyse un export CSV d'historique d'alarmes et calcule les KPIs ISA-18.2.

    Args:
        csv_path: Chemin vers le fichier CSV d'alarmes.
        timestamp_col: Nom de la colonne d'horodatage.
        tag_col: Nom de la colonne du tag / mnémonique de l'alarme.
        state_col: Nom de la colonne d'état (Active, Cleared, Acknowledged).
        priority_col: Nom de la colonne de priorité (1=Urgente, 4=Faible).

    Returns:
        dict: Rapport complet contenant les KPIs et les top offenders.
    """
    df = pd.read_csv(csv_path, parse_dates=[timestamp_col])
    df = df.sort_values(timestamp_col)

    total_alarms = len(df)
    if total_alarms == 0:
        return {"error": "Aucune alarme trouvée dans le fichier."}

    # Période d'analyse
    time_range = df[timestamp_col].max() - df[timestamp_col].min()
    total_hours = max(time_range.total_seconds() / 3600, 1)

    # KPI 1 : Alarmes par heure
    alarms_per_hour = total_alarms / total_hours

    # KPI 2 : Top 10 offenders (alarmes les plus fréquentes)
    tag_counts = Counter(df[tag_col])
    top_offenders = tag_counts.most_common(10)

    # KPI 3 : Répartition par priorité
    priority_dist = df[priority_col].value_counts().to_dict()

    # KPI 4 : Détection des chattering alarms (> 3 transitions par minute)
    chattering = []
    for tag, group in df.groupby(tag_col):
        transitions = len(group)
        tag_duration_min = max(
            (group[timestamp_col].max() - group[timestamp_col].min()).total_seconds() / 60, 1
        )
        rate = transitions / tag_duration_min
        if rate > 3.0:
            chattering.append({"tag": tag, "transitions_per_min": round(rate, 2)})

    # KPI 5 : Standing alarms (alarmes actives sans Cleared dans la dernière heure)
    last_hour = df[timestamp_col].max() - timedelta(hours=1)
    recent = df[df[timestamp_col] >= last_hour]
    active_tags = set(recent[recent[state_col].str.contains("Active", case=False, na=False)][tag_col])
    cleared_tags = set(recent[recent[state_col].str.contains("Clear", case=False, na=False)][tag_col])
    standing = active_tags - cleared_tags

    return {
        "period_hours": round(total_hours, 1),
        "total_alarms": total_alarms,
        "alarms_per_hour": round(alarms_per_hour, 1),
        "isa_18_2_target": "≤ 6/h" if alarms_per_hour <= 6 else "⚠ DÉPASSÉ",
        "top_10_offenders": [{"tag": t, "count": c} for t, c in top_offenders],
        "priority_distribution": priority_dist,
        "chattering_alarms": chattering,
        "standing_alarms": list(standing),
        "standing_count": len(standing),
    }


if __name__ == "__main__":
    import json
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "alarm_history.csv"
    report = analyze_alarm_history(path)
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
```

---

## 3. Matrice de Rationalisation des Alarmes

Chaque alarme doit être évaluée selon la grille suivante pour déterminer sa priorité réelle :

| Priorité | Conséquence si non traitée | Délai de réponse | Action requise de l'opérateur |
|:---:|---|:---:|---|
| **1 — Urgente** | Danger immédiat pour la sécurité des personnes ou dommage irréversible à l'équipement | < 5 min | Action immédiate obligatoire |
| **2 — Haute** | Perte de production majeure ou dépassement de limites réglementaires | < 15 min | Action rapide requise |
| **3 — Moyenne** | Dégradation de qualité ou baisse de rendement significative | < 60 min | Action planifiable dans l'heure |
| **4 — Basse** | Information de maintenance ou écart mineur sans impact immédiat | < 8h | Prise en compte lors de la prochaine ronde |

### Critères d'exclusion (alarmes à supprimer) :

- Alarmes dont l'opérateur **ne peut rien faire** (pas d'action corrective possible).
- Alarmes redondantes avec une autre alarme de priorité supérieure.
- Alarmes de diagnostic purement techniques (les router vers la maintenance, pas vers l'opérateur).
- Alarmes déclenchées à chaque démarrage/arrêt normal de la machine.

---

## 4. Intégration avec le Projet Automate (Générateur AWL/SCL)

Le Projet Automate Actemium génère un fichier `DBLoad.csv` contenant la liste de tous les défauts par catégorie d'organe. Ce fichier peut être utilisé comme **base de rationalisation** :

```python
import csv

def extract_alarms_from_dbload(dbload_path: str) -> list:
    """Extrait la liste des alarmes depuis le fichier DBLoad.csv du Projet Automate.

    Args:
        dbload_path: Chemin vers le fichier DBLoad.csv généré par le Projet Automate.

    Returns:
        list: Liste des dictionnaires d'alarmes à rationaliser.
    """
    alarms = []
    with open(dbload_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            alarms.append({
                "category": row.get("Category", ""),
                "tag": row.get("Tagname", ""),
                "description": row.get("Description", ""),
                "acquit_def": row.get("AcquitDef", ""),
                "priority": "3",  # Priorité par défaut à rationaliser
                "action_required": "À définir",
                "response_time": "< 60 min",
            })
    return alarms
```

---

## Pièges Courants

1. **Classer toutes les alarmes en priorité haute par excès de prudence :**
   * *Erreur :* 60% des alarmes sont marquées "Urgente" (Priorité 1), ce qui noie les vraies urgences dans la masse et revient à n'avoir aucune priorisation.
   * *Correction :* Respecter la distribution cible ISA-18.2 : ~5% Priorité 1, ~15% Priorité 2, ~30% Priorité 3, ~50% Priorité 4.

2. **Ignorer les alarmes de type "chattering" :**
   * *Erreur :* Une vanne oscillante génère 200 alarmes/heure à elle seule et masque toutes les autres alarmes critiques.
   * *Correction :* Implémenter un mécanisme de dead-band temporel (délai ON/OFF de 5-10 secondes) sur les alarmes de seuil pour éliminer les oscillations.

3. **Ne pas impliquer les opérateurs dans la rationalisation :**
   * *Erreur :* Un ingénieur définit les priorités d'alarmes sans consulter les opérateurs qui connaissent le terrain.
   * *Correction :* Organiser des ateliers de rationalisation avec les opérateurs, les techniciens de maintenance et les ingénieurs de procédé (approche HAZOP simplifiée).

---

## Références

- **ISA-18.2 (ANSI/ISA-18.2-2016)** — Management of Alarm Systems for the Process Industries.
- **IEC 62682:2014** — Management of alarm systems for the process industries.
- **EEMUA Publication 191** — Alarm Systems: A Guide to Design, Management and Procurement.

---

## Liste de vérification (Checklist)

- [ ] Le KPI d'alarmes par heure par opérateur est inférieur au seuil de 6 (cible ISA-18.2).
- [ ] Les 10 alarmes les plus fréquentes (top offenders) ont été analysées et des actions correctives sont définies.
- [ ] La matrice de rationalisation a été revue par les opérateurs de terrain et les ingénieurs de procédé.
- [ ] Les alarmes de type "chattering" sont équipées d'un mécanisme de dead-band temporel dans l'automate.
- [ ] La distribution des priorités respecte la pyramide cible (5% / 15% / 30% / 50%).

