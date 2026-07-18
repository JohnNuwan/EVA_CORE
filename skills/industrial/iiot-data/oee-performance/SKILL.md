---
name: oee-performance
description: "Utiliser quand l'utilisateur demande de concevoir, implémenter ou optimiser le calcul du TRS (Taux de Rendement Synthétique / OEE) ou de modéliser les états machine pour le suivi de production."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [oee, trs, kpi, production-monitoring, industrial-analytics]
    related_skills: [industrial-databases, industrial-reporting, mes-integration]
---

# Calcul du TRS (Taux de Rendement Synthétique / OEE)

## Vue d'ensemble

Le **TRS (Taux de Rendement Synthétique)**, ou **OEE (Overall Equipment Effectiveness)**, est l'indicateur clé de performance (KPI) de la productivité d'une ligne ou d'une machine. Il mesure l'efficacité d'un équipement par rapport à sa capacité théorique maximale.

Le TRS se compose de trois facteurs :
1.  **Le Taux de Disponibilité (Availability) :** Temps de fonctionnement réel par rapport au temps de fonctionnement planifié.
2.  **Le Taux de Performance (Performance) :** Vitesse réelle de production par rapport à la vitesse nominale théorique de la machine.
3.  **Le Taux de Qualité (Quality) :** Nombre de pièces conformes produites par rapport au nombre total de pièces lancées.

$$\text{TRS (OEE)} = \text{Disponibilité} \times \text{Performance} \times \text{Qualité}$$

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire la logique automate pour catégoriser les états machine (Production, Arrêt planifié, Panne, Micro-arrêt).
- De concevoir des scripts SQL ou Python pour calculer le TRS, la disponibilité, la performance et la qualité.
- De modéliser les indicateurs de production pour des tableaux de bord SCADA (ex: Ignition, Node-RED).
- D'optimiser le suivi des cadences nominales et des rebus.

**Ne pas utiliser pour :**
- Les calculs comptables de l'entreprise non connectés aux données machines temps réel.

---

## 1. Modélisation des États Machine (Automate)

Pour calculer la **Disponibilité**, l'automate doit suivre le temps passé dans chaque état (généralement basé sur les états définis par la norme OMAC PackML) :

*   **Temps Requis (Planifié) :** Temps total de travail prévu (hors week-ends ou fermetures d'usine).
*   **Temps de Fonctionnement (Uptime) :** Machine en production automatique.
*   **Temps d'Arrêt (Downtime) :** Divisé en :
    *   *Arrêts non planifiés (Pannes/Défauts) :* L'équipement doit produire mais est bloqué.
    *   *Arrêts planifiés (Changements de série, maintenance préventive).*
    *   *Micro-arrêts :* Petits blocages < 5 minutes (souvent mesurés séparément pour ne pas fausser le taux de performance).

### Logique ST simple de détection de Micro-Arrêts :

```pascal
// --- Détection de Micro-Arrêt ---
// Si la machine n'est pas en marche mais qu'aucun gros défaut n'est actif,
// et que cela dure depuis plus de 10s mais moins de 5min (300s).

Timer_MicroStop.PRE := 10000; // 10 secondes
Timer_MicroStop.TimerEnable := NOT Machine_Running AND NOT Major_Fault_Active;
TON(Timer_MicroStop);

IF Timer_MicroStop.DN THEN
    State_Micro_Stopping := TRUE;
    // Commencer à incrémenter le compteur de temps micro-arrêts
END_IF;

// Si la machine repart ou qu'un gros défaut survient
IF Machine_Running OR Major_Fault_Active THEN
    State_Micro_Stopping := FALSE;
END_IF;
```

---

## 2. Calcul du TRS en Python

Voici la méthode standard pour calculer le TRS à partir de données brutes collectées sur une période :

```python
def calculate_oee(planned_production_time_min, actual_run_time_min, 
                  total_parts_produced, good_parts_produced, 
                  ideal_cycle_time_sec):
    """
    Calcule les indicateurs OEE (TRS).
    ideal_cycle_time_sec : temps nominal nécessaire pour produire 1 pièce.
    """
    if planned_production_time_min <= 0:
        return {"success": False, "error": "Le temps planifié doit être supérieur à 0."}

    # 1. Disponibilité (Availability)
    availability = actual_run_time_min / planned_production_time_min
    
    # 2. Performance
    # Temps théorique requis pour produire la quantité réelle
    theoretical_time_sec = total_parts_produced * ideal_cycle_time_sec
    actual_run_time_sec = actual_run_time_min * 60
    
    if actual_run_time_sec > 0:
        performance = theoretical_time_sec / actual_run_time_sec
    else:
        performance = 0.0
        
    # Limiter la performance à 100% pour éviter les anomalies de cadence surévaluée
    performance = min(performance, 1.0)
    
    # 3. Qualité
    if total_parts_produced > 0:
        quality = good_parts_produced / total_parts_produced
    else:
        quality = 0.0
        
    # 4. TRS (OEE)
    oee = availability * performance * quality
    
    return {
        "success": True,
        "availability": round(availability * 100, 2),
        "performance": round(performance * 100, 2),
        "quality": round(quality * 100, 2),
        "oee": round(oee * 100, 2)
    }

# Exemple d'appel :
# Poste de 8 heures (480 min) - 30 min pause repas = 450 min planifiées.
# Machine en marche pendant 390 min (60 min d'arrêts cumulés).
# Production de 3000 pièces, dont 2950 conformes.
# Cadence nominale de la machine : 6 secondes par pièce.
result = calculate_oee(
    planned_production_time_min=450,
    actual_run_time_min=390,
    total_parts_produced=3000,
    good_parts_produced=2950,
    ideal_cycle_time_sec=6.0
)
print(result)
# Sortie attendue : {'success': True, 'availability': 86.67, 'performance': 76.92, 'quality': 98.33, 'oee': 65.55}
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Performance supérieure à 100% :**
    *   *Erreur :* Avoir une cadence réelle plus rapide que la cadence nominale (cause souvent une performance calculée > 100%, masquant d'autres pertes).
    *   *Correction :* Vérifier la cadence nominale (idéale) définie pour l'article en production dans le référentiel MES. Elle doit représenter la vitesse mécanique maximale possible sans dégradation de l'équipement.
2.  **Mauvaise affectation des arrêts :**
    *   *Erreur :* Inclure les arrêts non planifiés (panne) dans le temps hors-planning, ce qui gonfle artificiellement le taux de disponibilité.
    *   *Correction :* Déterminer clairement les états "Planifiés" (Maintenance préventive, pause équipe, pas d'OF) et "Non planifiés" (Manque matière, panne, réglage).

---

## Liste de vérification (Checklist)

- [ ] La formule de disponibilité prend en compte le temps planifié de production comme base.
- [ ] Le calcul de la performance utilise le temps de cycle idéal (théorique) propre à l'article actuellement produit.
- [ ] Les rebuts (pièces défectueuses) sont correctement comptabilisés pour pénaliser uniquement le taux de qualité.
- [ ] Les micro-arrêts sont historisés séparément des pannes majeures.

