---
name: plc-diagnostics
description: Diagnostic automatisé de PLC Siemens et Rockwell
---

# PLC Diagnostics Skill

Analyse les diagnostics CPU, tampon d'erreur et état des modules.

## Usage

Combine `plc_read`, `plc_probe` et `automation_rule_evaluate` pour un diagnostic complet.

## Procédure

1. **Connexion** — `plc_probe(endpoint)` pour détecter le type
2. **État CPU** — lecture du status (RUN/STOP/FAULT)
3. **Buffer diagnostic** — extraction des dernières erreurs (Siemens: `get_diag_buffer()`)
4. **Analyse** — classification de l'erreur (matériel, programme, réseau)
5. **Recommandation** — action corrective