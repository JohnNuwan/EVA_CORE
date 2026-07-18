# Plans d'Implémentation Industrielle EB-JEPA & I-JEPA

## Vue d'ensemble

Ce document contient les plans d'implémentation détaillés pour :
- **EB-JEPA** (Apache 2.0) — le point d'entrée recommandé pour tout déploiement industriel
- **I-JEPA** (CVPR 2023) — le spécialiste inspection qualité, nécessite ré-entraînement propriétaire

---

## PARTIE 1 : EB-JEPA (Apache 2.0 — Production Ready)

### 1.1 Setup

```bash
git clone https://github.com/facebookresearch/eb_jepa.git
cd eb_jepa
conda create -n eb_jepa python=3.12 -y
conda activate eb_jepa
uv pip install -e . --group dev
export EBJEPA_DSETS=/data/industrial/datasets
export EBJEPA_CKPTS=/data/industrial/checkpoints
```

### 1.2 Structure des Données

```
datasets/
└── industrial_inspection/
    ├── train/          # 1000+ images OK, non étiquetées
    └── val/
        ├── normal/     # 100 images OK pour calibration
        └── anomaly/    # 50 anomalies pour validation
```

### 1.3 Lancement Entraînement

```bash
python -m examples.image_jepa.main \
  --config configs/industrial_inspection.yaml \
  --devices cuda:0
```

### 1.4 Roadmap

| Phase | Durée | Actions |
|---|---|---|
| Collecte données | Semaine 1-2 | 1000+ cycles normaux, 50 anomalies |
| Entraînement | Semaine 3-4 | Image JEPA sur GPU, calibration seuil |
| Intégration | Semaine 5-6 | API REST, OPC UA, Grafana |
| Production | Semaine 7-8 | Tests robustesse, monitoring drift |

---

## PARTIE 2 : I-JEPA (Spécialiste Inspection)

### 2.1 Stratégie de Contournement de Licence

- L'architecture I-JEPA est open-source (code)
- Seuls les poids pré-entraînés sont CC BY-NC
- → Ré-entraîner from scratch sur données propriétaires
- → Modèle libre de droits pour usage commercial

### 2.2 Ré-entraînement Propriétaire

```bash
git clone https://github.com/facebookresearch/ijepa.git
cd ijepa
conda create -n ijepa python=3.10 -y
conda activate ijepa
pip install -r requirements.txt
```

Entraînement : 16× A100 × ~72h pour ViT-H 632M, ou réduire (ViT-B ~8h sur 4× A100).

### 2.3 Inspection Avancée

- Détection d'anomalie (erreur JEPA > seuil calibré)
- Classification few-shot (12 exemples par type de défaut)
- Analyse de tendance (dérive process)
- Buffer glissant des 100 dernières erreurs

---

## PARTIE 3 : Intégration MES/SCADA

### 3.1 Pont OPC UA

Variables PLC exposées :
- `JEPA.Status` (0=OK, 1=ANOMALY)
- `JEPA.Confidence` (Float)
- `JEPA.PredictionError` (Float)
- `JEPA.DefectType` (String)
- `JEPA.TrendAlert` (Bool)

### 3.2 Dashboard Grafana

Métriques Prometheus :
- `jepa_anomaly_score` par ligne/produit
- `jepa_inference_seconds`
- `jepa_pieces_total` par status
- `jepa_trend_slope`

---

## Stratégie Hybride Recommandée

```
Phase 1 (Mois 1-2) : POC EB-JEPA (Apache 2.0, pas de risque)
Phase 2 (Mois 3-4) : Ré-entraînement I-JEPA propriétaire
Phase 3 (Mois 5-6) : Production hybride
  → EB-JEPA pour vidéo et planification
  → I-JEPA propriétaire pour inspection core
```

## Budget

| Poste | EB-JEPA | I-JEPA |
|---|---|---|
| GPU entraînement | 1× A100 ~8€ | 16× A100 ~2300€ |
| GPU inférence | 1× T4 ~0.5€/h | 1× T4 ~0.5€/h |
| Licence | 0€ (Apache 2.0) | 0€ (from scratch) |
| Développement | 2-3 semaines | 3-4 semaines |