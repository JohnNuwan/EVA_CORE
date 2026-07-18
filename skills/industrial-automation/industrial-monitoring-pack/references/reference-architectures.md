# Architectures types de monitoring industriel

## 1. Machine simple
```text
PLC ──▶ Collecteur Edge ──▶ Historian ──▶ Grafana
```
Usage : machine autonome avec quelques états, défauts, analogiques.
Priorités : états machine, défaut général, cycle, compteurs.

## 2. Cellule robotisée
```text
PLC principal ─┬─ Robot interface
               ├─ Drive / périphériques
               └─ Collecteur Edge ──▶ Historian ──▶ Grafana
```
Usage : cellule avec handshake robot ↔ PLC.
Priorités : Ready/Busy/Fault/CycleDone, défauts cellule, temps de cycle, attentes.

## 3. Ligne multi-PLC
```text
PLC amont ─┐
PLC centre ├─▶ Collecteur / broker local ──▶ Historian ──▶ Dashboards ligne
PLC aval  ─┘
```
Usage : ligne où plusieurs contrôleurs contribuent à la performance globale.
Priorités : états consolidés, blocages inter-zones, top pertes, OEE ligne.

## 4. Utilities / énergie
```text
Compteurs / utilités ──▶ Collecteur Modbus / MQTT ──▶ Historian ──▶ Dashboard énergie
```
Usage : air comprimé, eau, vapeur, compteurs électriques.
Priorités : puissance, énergie, baseline, dérives hors production.

## 5. Architecture Edge / OT / IT segmentée
```text
Terrain OT ──▶ Edge OT (cache local) ──▶ Historian zone DMZ/IT ──▶ Grafana / reporting
```
Usage : sites avec séparation cybersécurité forte.
Priorités : store & forward, gouvernance flux, limitation des dépendances réseau.

## Règle de sélection
Choisir l'architecture la plus simple couvrant réellement le besoin métier, puis enrichir par couches.
