---
name: iso-energy
description: "Utiliser quand l'utilisateur demande d'implémenter des algorithmes de suivi de consommations d'énergie, de calculer des indicateurs de performance énergétique (IPE/EnPI) ou de configurer des systèmes de reporting conformes à l'ISO 50001."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [energy, sustainability, iso-50001, enpi, ipe, compressed-air, leak-detection, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Management de l'Énergie Industrielle (ISO 50001)

## Vue d'ensemble

L'efficacité énergétique est devenue un enjeu majeur pour l'industrie, tant pour la réduction des coûts que pour l'impact environnemental. La norme **ISO 50001** définit les exigences pour établir, mettre en œuvre, maintenir et améliorer un Système de Management de l'Énergie (SMÉ). 

Dans les systèmes de contrôle-commande (SCADA/MES), la contribution logicielle consiste à collecter les index des compteurs d'énergie (électricité, gaz, air comprimé, vapeur, eau), à calculer en temps réel des **Indicateurs de Performance Énergétique (IPE / EnPI)** et à détecter des anomalies de consommation.

Cette compétence guide l'agent Helios pour coder des modules de suivi et d'optimisation de l'énergie.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De calculer la consommation d'énergie rapportée aux unités produites (intensité énergétique).
- De concevoir des algorithmes de détection de fuites d'air comprimé ou de fluides.
- De créer des tableaux de bord énergétiques ou d'intégrer des compteurs d'énergie par communication (Modbus, Profinet).
- De calculer des cumuls horaires, journaliers ou par lot de production à partir d'index de compteurs.

**Ne pas utiliser pour :**
- Des calculs de bilans thermiques physiques de génie des procédés hors automatisation et instrumentation.

---

## 1. Calcul de l'Intensité Énergétique (EnPI / IPE) par Lot

L'indicateur le plus pertinent en industrie est la consommation d'énergie spécifique. Elle rapporte la consommation d'énergie (ex. en kWh) au volume ou à la masse de produit fini (ex. en tonnes ou en bouteilles).

### Exemple de requête SQL d'agrégation d'intensité énergétique par lot :

```sql
SELECT 
    b.batch_number,
    b.product_code,
    -- Cumul d'énergie consommée pendant le lot (Différence d'index compteur fin - début)
    (MAX(e.electricity_index_kwh) - MIN(e.electricity_index_kwh)) AS energy_consumed_kwh,
    
    -- Quantité de produit fini
    b.qty_produced_tons,
    
    -- Calcul de l'IPE (kWh / Tonne)
    CASE 
        WHEN b.qty_produced_tons > 0 
        THEN (MAX(e.electricity_index_kwh) - MIN(e.electricity_index_kwh)) / b.qty_produced_tons
        ELSE 0 
    END AS energy_performance_indicator_kwh_per_ton

FROM batch_production_logs b
-- Jointure temporelle sur la période de production du lot
JOIN energy_log_ticks e ON e.t_stamp BETWEEN b.start_time AND b.end_time
WHERE b.end_time IS NOT NULL
GROUP BY b.batch_number, b.product_code, b.qty_produced_tons;
```

---

## 2. Détection Automatique des Fuites d'Air Comprimé

L'air comprimé est l'une des sources d'énergie les plus coûteuses en usine. La détection de fuites se fait en mesurant le débit minimal (Base Load) pendant les périodes d'arrêt programmées de la production.

### Algorithme de détection de fuites en SCL Siemens (Tâche OB30) :

```scl
FUNCTION_BLOCK "FB_Actemium_AirLeakDetection"
   VAR_INPUT
      i_ProductionActive : Bool;  // Statut marche de la ligne de production
      i_AirFlow : Real;           // Débit d'air comprimé instantané (Nm³/h)
      i_CheckDuration : Time;     // Durée d'observation requise (ex: T#10m)
      i_LeakLimit : Real;         // Seuil d'alarme de fuite (ex: 15.0 Nm³/h)
   END_VAR

   VAR_OUTPUT
      q_LeakAlarm : Bool;         // Alarme fuite d'air active
      q_MinFlowMeasured : Real;   // Débit minimal enregistré pendant la phase
   END_VAR

   VAR
      stat_Timer : TON_TIME;
      stat_MinFlow : Real := 9999.0;
      stat_Checking : Bool;
   END_VAR

BEGIN
   // On démarre l'observation uniquement quand la production est à l'arrêt
   IF NOT #i_ProductionActive THEN
       IF NOT #stat_Checking THEN
           #stat_MinFlow := 9999.0; // Réinitialisation de la valeur min
           #stat_Checking := TRUE;
       END_IF;
       
       // Enregistrement du débit minimum observé
       IF #i_AirFlow < #stat_MinFlow THEN
           #stat_MinFlow := #i_AirFlow;
       END_IF;
       
       // Lancement du timer d'observation
       #stat_Timer(IN := TRUE, PT := #i_CheckDuration);
       
       IF #stat_Timer.Q THEN
           #q_MinFlowMeasured := #stat_MinFlow;
           // Si le débit minimal reste supérieur au seuil de fuite toléré
           #q_LeakAlarm := (#stat_MinFlow > #i_LeakLimit);
       END_IF;
   ELSE
       // Reset de l'alarme et du processus si la ligne redémarre
       #stat_Checking := FALSE;
       #stat_Timer(IN := FALSE);
   END_IF;
END_FUNCTION_BLOCK
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Calcul de consommation d'énergie brute sans indicateur contextuel :**
   * *Erreur :* Rapporter uniquement la consommation totale en kWh (ex: "l'usine a consommé 10 000 kWh aujourd'hui"). Cet indicateur est inutile pour l'ISO 50001 car il ne prend pas en compte le volume produit ou la météo (température extérieure influençant les groupes froids).
   * *Correction :* Contextualiser les mesures en calculant des intensités énergétiques (kWh/tonne) ou en établissant des modèles de régression linéaire (énergie vs volume produit).

2. **Dépassement de capacité du compteur (Rollover) :**
   * *Erreur :* Soustraire l'index précédent de l'index actuel sans anticiper le retour à zéro du compteur physique d'énergie (ex. : passage de `999999` à `000000`).
   * *Correction :* Gérer le retour à zéro (Rollover) dans le code de calcul :
     `IF IndexActuel < IndexPrecedent THEN Delta := (MaxCompteur - IndexPrecedent) + IndexActuel; ELSE Delta := IndexActuel - IndexPrecedent; END_IF;`

---

## Liste de vérification (Checklist)

- [ ] L'algorithme de calcul des variations d'index prend en compte le dépassement de capacité (Rollover) des compteurs d'énergie.
- [ ] Les calculs d'indicateurs de performance énergétique (EnPI) gèrent les divisions par zéro dans les cas où la production est nulle.
- [ ] Les détections de fuites ou de dérives s'appuient sur un filtrage ou une moyenne glissante des valeurs instantanées pour éviter les déclenchements sur pics transitoires.
- [ ] Les données de consommations sont rattachées temporellement de façon stricte aux lots de production ou périodes d'activité réelles.

