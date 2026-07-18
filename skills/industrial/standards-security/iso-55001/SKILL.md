---
name: iso-55001
description: "Utiliser quand l'utilisateur demande de concevoir, documenter ou de structurer des plans de gestion des actifs physiques (Asset Management) industriels selon la norme ISO 55001 (cycles de vie, maintenance, criticité des machines)."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [iso-55001, asset-management, maintenance-strategy, lifecycle-optimization, industrial-standards]
  related_skills: [cmms-gmao-integration, predictive-maintenance, industrial-reporting]
---

# Gestion des Actifs Physiques & Norme ISO 55001

## Vue d'ensemble

La norme **ISO 55001** spécifie les exigences pour l'établissement, la mise en œuvre, la maintenance et l'amélioration d'un système de gestion des actifs (Asset Management). Dans un contexte industriel, un "actif" désigne toute machine, ligne de production, outil ou infrastructure physique qui génère de la valeur pour l'usine.

Les objectifs de l'ISO 55001 appliqués à la maintenance industrielle :
1.  **L'optimisation du coût global de possession (TCO - Total Cost of Ownership) :** Suivre les coûts de l'actif depuis sa conception/achat jusqu'à son déclassement/recyclage, en passant par son exploitation et sa maintenance.
2.  **L'analyse de criticité (FMECA/AMDEC) :** Hiérarchiser les équipements pour allouer les budgets de maintenance en priorité sur les machines goulots ou dangereuses.
3.  **La maintenance conditionnelle et prédictive :** Passer d'une maintenance réactive (attendre la panne) à une maintenance planifiée basée sur les données réelles de fonctionnement de la machine.
4.  **La gestion des pièces de rechange (Spare Parts) :** Optimiser les stocks de pièces critiques pour éviter les arrêts d'usines prolongés.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'établir une matrice de criticité pour les équipements d'une usine.
- De rédiger un plan de maintenance préventive basé sur des seuils temporels ou des compteurs d'heures.
- De concevoir des KPIs de gestion des actifs (MTBF - temps moyen entre pannes, MTTR - temps moyen de réparation).
- De structurer un plan de fin de vie (déclassement) ou de rétrofit (modernisation) pour des machines obsolètes.

**Ne pas utiliser pour :**
- La configuration de logiciels de GMAO spécifiques (utiliser `cmms-gmao-integration`).

---

## 1. Matrice de Criticité des Équipements (Exemple)

Pour appliquer l'ISO 55001, il faut classer les actifs selon leur criticité (Indice de Priorité de Maintenance - IPM) calculé sur les critères de Sécurité/Environnement (S), Production (P) et Qualité (Q) :

$$\text{IPM} = S \times P \times Q$$

Chaque critère est noté de 1 (faible impact) à 4 (impact catastrophique) :

| Équipement | Sécurité (1-4) | Production (1-4) | Qualité (1-4) | IPM (1-64) | Stratégie de Maintenance |
|---|:---:|:---:|:---:|:---:|---|
| Compresseur d'air principal | 1 | 4 | 2 | **8** | Redondance installée (Compresseur B). Maintenance préventive standard. |
| Pompe de dosage d'acide (NEP) | 4 | 2 | 2 | **16** | Critique Sécurité. Contrôle mensuel des joints et flexibles. |
| Four de cuisson (Métallurgie) | 2 | 4 | 4 | **32** | Critique Process. Maintenance conditionnelle (analyse vibratoire des ventilateurs). |
| Convoyeur de transfert carton | 1 | 1 | 1 | **1** | Non critique. Maintenance corrective simple (réparation après panne). |

---

## 2. Calcul des indicateurs clés (MTBF & MTTR) en Python

Le calcul régulier du MTBF (Mean Time Between Failures) et du MTTR (Mean Time To Repair) permet de mesurer l'efficacité de la stratégie de maintenance :

```python
def calculate_maintenance_kpis(total_run_time_hours, downtime_logs):
    """
    Calcule le MTBF et le MTTR.
    downtime_logs : liste de dictionnaires avec la durée de chaque arrêt de panne en heures.
    """
    total_failures = len(downtime_logs)
    if total_failures == 0:
        return {
            "success": True, 
            "message": "Aucune panne enregistrée. Équipement fiable.",
            "mtbf_hours": total_run_time_hours, 
            "mttr_hours": 0.0
        }
        
    total_repair_time = sum(log["repair_time_hours"] for log in downtime_logs)
    
    # MTBF = Temps de fonctionnement total / Nombre de pannes
    mtbf = total_run_time_hours / total_failures
    
    # MTTR = Temps de réparation total / Nombre de pannes
    mttr = total_repair_time / total_failures
    
    # Disponibilité intrinsèque
    availability = mtbf / (mtbf + mttr) if (mtbf + mttr) > 0 else 0.0
    
    return {
        "success": True,
        "failures_count": total_failures,
        "mtbf_hours": round(mtbf, 2),
        "mttr_hours": round(mttr, 2),
        "intrinsic_availability_percent": round(availability * 100, 2)
    }

# Exemple d'appel :
# Machine ayant tourné 1000 heures avec 3 pannes enregistrées.
pannes = [
    {"repair_time_hours": 2.5},
    {"repair_time_hours": 4.0},
    {"repair_time_hours": 1.5}
]
result = calculate_maintenance_kpis(1000, pannes)
print(result)
# Sortie : {'success': True, 'failures_count': 3, 'mtbf_hours': 333.33, 'mttr_hours': 2.67, 'intrinsic_availability_percent': 99.2}
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Maintenance préventive aveugle (Over-maintenance) :**
    *   *Erreur :* Remplacer des composants mécaniques coûteux uniquement en fonction du temps écoulé (ex: tous les 6 mois) sans vérifier leur état d'usure réel. Cela augmente inutilement les coûts et peut introduire des défauts au remontage.
    *   *Correction :* Mettre en place des indicateurs d'usure physiques (analyses d'huile, thermographie infrarouge, compteurs d'heures réels) pour passer à une maintenance conditionnelle.
2.  **Ignorer l'obsolescence matérielle :**
    *   *Erreur :* Conserver une machine critique dont le constructeur n'assure plus le support et pour laquelle aucune pièce de rechange n'est disponible sur le marché.
    *   *Correction :* Maintenir un plan d'obsolescence annuel pour planifier les rétrofits de commandes numériques ou d'automates avant la panne fatale.

---

## Liste de vérification (Checklist)

- [ ] L'inventaire de tous les actifs de production physiques est à jour avec leurs numéros de série et localisations (ISA-95).
- [ ] Une analyse de criticité AMDEC/FMECA a été menée pour catégoriser les équipements (A, B, C).
- [ ] Les pièces de rechange critiques pour les équipements de classe A sont identifiées, étiquetées et disponibles en stock.
- [ ] Les indicateurs de performance MTBF, MTTR et coûts de maintenance sont calculés et analysés périodiquement.

