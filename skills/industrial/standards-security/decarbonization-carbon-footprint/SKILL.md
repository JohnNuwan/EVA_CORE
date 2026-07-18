---
name: decarbonization-carbon-footprint
description: "Utiliser quand l'utilisateur demande de concevoir ou de configurer des systèmes de management de l'énergie (ISO 50001) ou des calculs de bilan carbone industriel (Scopes 1, 2, 3) basés sur des capteurs physiques."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [decarbonization, carbon-footprint, energy-monitoring, iso-50001, sustainability]
    related_skills: [iso-energy, industrial-databases, industrial-reporting]
---

# Bilan Carbone Temps Réel & Décarbonisation Industrielle

## Vue d'ensemble

Dans l'Industrie 4.0, la transition énergétique et la décarbonisation s'appuient sur des mesures physiques en temps réel (électricité, vapeur, gaz, eau) plutôt que sur des factures annuelles estimées. Le suivi s'inscrit dans la norme **ISO 50001** (Systèmes de management de l'énergie) et classe les émissions de gaz à effet de serre (GES) en trois périmètres (Scopes) :

*   **Scope 1 (Émissions directes) :** Combustion de gaz naturel dans les chaudières du site, carburant de la flotte interne, fuites de fluides frigorigènes.
*   **Scope 2 (Émissions indirectes liées à l'énergie achetée) :** Électricité consommée par le site, réseau de chaleur/froid urbain.
*   **Scope 3 (Autres émissions indirectes) :** Chaîne logistique amont/aval, cycle de vie des matières premières, déplacements des employés (souvent calculé par modélisation externe).

Pour les ingénieurs d'usine, l'objectif est d'associer ces consommations d'énergie à des indicateurs de performance énergétique (IPE/EnPI) corrélés au volume de production.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De calculer l'équivalent CO2 (CO2e) d'une consommation électrique ou de gaz naturel à partir de facteurs d'émission réglementaires (ADEME, GHG Protocol).
- D'implémenter des formules de calcul de consommation d'énergie spécifique (consommation par tonne de produit fini).
- De concevoir des architectures d'acquisition d'énergie (centrales de mesure communicant en Modbus-TCP).
- D'aligner des mesures énergétiques avec les objectifs de la certification ISO 50001.

**Ne pas utiliser pour :**
- Des audits carbone réglementaires certifiés (qui doivent être réalisés par des cabinets d'audit accrédités).

---

## 1. Calcul de l'équivalent CO2 (CO2e) en Python

Pour calculer l'empreinte carbone en temps réel des consommations énergétiques, on applique des facteurs d'émission qui dépendent de la source d'énergie et de la localisation géographique (par exemple, le mix électrique français est très décarboné par rapport à d'autres pays).

```python
# Facteurs d'émission par défaut (exemples de valeurs moyennes en kg CO2e / unité)
# Source : Base Carbone ADEME
EMISSION_FACTORS = {
    "electricity_fr": 0.052,  # kg CO2e / kWh (Mix électrique France)
    "electricity_de": 0.385,  # kg CO2e / kWh (Mix électrique Allemagne)
    "gas_natural": 0.227,     # kg CO2e / kWh (Pouvoir calorifique supérieur - PCS)
    "fuel_oil": 3.24,         # kg CO2e / Litre
    "steam_purchased": 0.170  # kg CO2e / kWh
}

def calculate_footprint(electricity_kwh, gas_kwh, location="fr"):
    """
    Calcule l'empreinte carbone pour les consommations Scope 1 (gaz) et Scope 2 (électricité).
    """
    elec_factor_key = f"electricity_{location}"
    elec_factor = EMISSION_FACTORS.get(elec_factor_key, 0.200) # Fallback moyen
    gas_factor = EMISSION_FACTORS["gas_natural"]
    
    # Scope 1: Gaz naturel
    scope_1_co2_kg = gas_kwh * gas_factor
    
    # Scope 2: Électricité
    scope_2_co2_kg = electricity_kwh * elec_factor
    
    total_co2_kg = scope_1_co2_kg + scope_2_co2_kg
    
    return {
        "success": True,
        "scope_1_co2_t": round(scope_1_co2_kg / 1000.0, 4), # Conversion en tonnes
        "scope_2_co2_t": round(scope_2_co2_kg / 1000.0, 4),
        "total_co2_t": round(total_co2_kg / 1000.0, 4),
        "unit": "tonnes CO2e"
    }

# Exemple d'appel :
# Consommation d'un atelier sur 24 heures : 15 000 kWh électrique et 8 000 kWh de gaz.
result = calculate_footprint(15000, 8000, location="fr")
print(result)
# Sortie : {'success': True, 'scope_1_co2_t': 1.816, 'scope_2_co2_t': 0.78, 'total_co2_t': 2.596, 'unit': 'tonnes CO2e'}
```

---

## 2. Définition des Indicateurs de Performance Énergétique (IPE / EnPI)

Un indicateur brut de consommation d'énergie (ex: kWh consommés) n'est pas représentatif de l'efficacité d'une usine car il varie selon les volumes produits. On utilise l'énergie spécifique (EnPI) :

$$\text{EnPI} = \frac{\text{Consommation Totale (kWh)}}{\text{Quantité Produite Conforme (Tonnes)}}$$

### Requête SQL type pour le suivi EnPI hebdomadaire :
```sql
SELECT
  DATE_TRUNC('week', timestamp) AS "Semaine",
  SUM(electric_energy_kwh) AS "Total Énergie (kWh)",
  SUM(good_production_tons) AS "Total Produit (Tonnes)",
  -- Division sécurisée pour éviter les erreurs de division par zéro
  CASE 
    WHEN SUM(good_production_tons) > 0 
    THEN SUM(electric_energy_kwh) / SUM(good_production_tons)
    ELSE 0
  END AS "EnPI (kWh/Tonne)"
FROM factory_energy_log
GROUP BY 1
ORDER BY 1;
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Utilisation de facteurs d'émission obsolètes ou non localisés :**
    *   *Erreur :* Appliquer un facteur d'émission global pour l'électricité sans tenir compte du réseau électrique local. Par exemple, utiliser le facteur d'émission de l'Allemagne pour une usine située en Suède (très hydroélectrique).
    *   *Correction :* Toujours documenter et lier la source des facteurs d'émission (ex: base ADEME, DEFRA) et utiliser le mix spécifique de la région de l'installation.
2.  **Ignorer le talon de consommation (Base Load) :**
    *   *Erreur :* Croire que la consommation d'énergie d'une machine s'arrête lorsqu'elle ne produit pas.
    *   *Correction :* Isoler et mesurer la consommation à vide (talon énergétique ou base load) des installations (centrales d'air comprimé, groupes froids, éclairage) pour optimiser les arrêts durant les week-ends.

---

## Liste de vérification (Checklist)

- [ ] Les facteurs d'émission utilisés sont documentés, datés et proviennent d'une base de données réglementaire (ex: ADEME, GHG Protocol).
- [ ] La distinction entre les émissions directes (Scope 1) et les émissions indirectes (Scope 2) est bien établie.
- [ ] Le calcul de l'efficacité énergétique (EnPI) est corrélé avec des volumes de production réels conformes (pas seulement le nombre d'heures de marche).
- [ ] Une gestion de division par zéro est implémentée dans toutes les requêtes d'indicateurs de ratio.

