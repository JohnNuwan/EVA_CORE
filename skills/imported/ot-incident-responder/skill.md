---
name: ot-incident-responder
description: Réponse automatisée aux incidents OT avec procédures pas-à-pas
---

# OT Incident Responder Skill

Procédure de réponse aux incidents de cybersécurité OT/SCADA.

## Usage

Déclenché par `automation_rule_evaluate` ou manuellement.

## Procédure

1. **Identification** — quel équipement, quel protocole, quel impact
2. **Containement** — isolation réseau, mise en safe state du process
3. **Analyse** — logs, PCAP, buffer diagnostic PLC
4. **Remédiation** — restauration config, mise à jour firmware
5. **Documentation** — rapport d'incident, leçons apprises

## Références

- IEC 62443: Cyber security for industrial automation
- NIST SP 800-82: Guide to ICS security