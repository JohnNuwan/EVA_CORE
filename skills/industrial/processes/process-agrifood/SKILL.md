---
name: process-agrifood
description: "Utiliser quand l'utilisateur demande de concevoir des séquences de nettoyage en place (NEP/CIP), de gérer des recettes de dosage ou d'implémenter la traçabilité des lots d'ingrédients en agro-alimentaire."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [agri-food, agroalimentaire, cip, nep, batch, isa-88, traceability, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Procédés Agro-alimentaires (NEP/CIP & Recettes ISA-88 Batch)

## Vue d'ensemble

L'industrie agro-alimentaire (F&B - Food & Beverage) impose des règles strictes sur l'hygiène pour éviter toute contamination bactériologique et sur la traçabilité pour la gestion d'éventuels rappels de produits. Deux thématiques logicielles y sont omniprésentes :
1. **Le Nettoyage en Place (NEP / CIP - Cleaning in Place) :** Séquences de lavage des cuves et tuyauteries (rinçage à l'eau, injection de soude acide, rinçage final) sans démontage.
2. **Le contrôle des lots (norme ISA-88 Batch) :** Dosage précis d'ingrédients, suivi de recettes dynamiques et traçabilité ascendante/descendante des matières premières.

Cette compétence guide l'agent Helios pour concevoir des programmes automates de lavage NEP robustes et des structures de traçabilité d'ingrédients.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De programmer ou de modifier une séquence de lavage CIP/NEP sur un automate.
- D'implémenter des contrôles de température, de débit ou de conductivité pour valider les phases de lavage chimique.
- D'écrire des scripts de traçabilité de matières premières ou de transferts de cuves.
- De structurer des recettes de dosage d'ingrédients.

**Ne pas utiliser pour :**
- Des applications pharmaceutiques (utiliser `process-pharma` pour les contraintes 21 CFR Part 11).

---

## 1. Séquence de Lavage NEP / CIP (Cleaning in Place)

Une séquence NEP standard suit des étapes chronométrées validées par des capteurs de température (température de nettoyage de la soude à ~75-80°C) et de conductivité (pour distinguer l'eau, l'acide et la soude) :

### Exemple de structure de séquenceur NEP en SCL Siemens :

```scl
CASE #stat_CipStep OF
    0:  // IDLE (Attente démarrage)
        #q_PumpOut := FALSE;
        #q_ValveWater := FALSE;
        #q_ValveSoda := FALSE;
        IF #i_StartCmd THEN
            #stat_CipStep := 10; // Passer au pré-rinçage
            #stat_StepTimer(IN := FALSE); // Reset timer
        END_IF;
        
    10: // PRÉ-RINÇAGE (Eau perdue pour chasser le produit)
        #q_ValveWater := TRUE;
        #q_PumpOut := TRUE;
        #stat_StepTimer(IN := TRUE, PT := T#5m);
        IF #stat_StepTimer.Q THEN
            #stat_CipStep := 20; // Passage au lavage Soude
            #stat_StepTimer(IN := FALSE);
        END_IF;
        
    20: // LAVAGE CHIMIQUE (Soude récirculée - Température cible > 75°C)
        #q_ValveWater := FALSE;
        #q_ValveSoda := TRUE;
        #q_PumpOut := TRUE;
        #q_HeatingActive := TRUE;
        
        #stat_StepTimer(IN := (#i_ReturnTemp >= 75.0), PT := T#15m); // Le temps s'écoule uniquement si la température de retour est correcte
        
        IF #stat_StepTimer.Q THEN
            #stat_CipStep := 30; // Passage au rinçage intermédiaire
            #q_HeatingActive := FALSE;
            #stat_StepTimer(IN := FALSE);
        END_IF;
        
    30: // RINÇAGE FINAL & VALIDATION CONDUCTIVITÉ
        #q_ValveSoda := FALSE;
        #q_ValveWater := TRUE;
        #q_PumpOut := TRUE;
        
        #stat_StepTimer(IN := TRUE, PT := T#5m);
        
        // Sécurité : Vérifier que le rinçage est propre (conductivité de l'eau proche de 0)
        IF #stat_StepTimer.Q AND (#i_ReturnConductivity <= #c_WaterConductivityLimit) THEN
            #stat_CipStep := 100; // Fin de lavage - OK
            #stat_StepTimer(IN := FALSE);
        END_IF;
END_CASE;
```

---

## 2. Traçabilité des Transferts Matières

En agro-alimentaire, chaque déplacement de liquide entre cuves (ex: Cuve Stockage → Cuve Mélange) doit générer un enregistrement de traçabilité contenant le numéro de lot d'origine, le volume transféré et la cuve de destination :

```sql
CREATE TABLE mat_genealogy (
    transfer_id SERIAL PRIMARY KEY,
    t_stamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_tank VARCHAR(50) NOT NULL,
    dest_tank VARCHAR(50) NOT NULL,
    batch_number VARCHAR(100) NOT NULL, -- Lot d'origine
    volume_liters DOUBLE PRECISION NOT NULL,
    operator_username VARCHAR(100)
);
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Validation du temps de lavage sans contrôle de température :**
   * *Erreur :* Décompter le temps de circulation de la soude dès que l'étape de lavage commence, même si la soude est froide. Cela conduit à un nettoyage insuffisant de la cuve.
   * *Correction :* N'activer le temporisateur de l'étape de lavage que lorsque la température mesurée sur le capteur de retour de la boucle NEP a atteint son seuil de consigne (ex: 75°C).

2. **Mélange accidentel de produits chimiques et d'ingrédients :**
   * *Erreur :* Ouvrir une vanne de produit chimique alors que la cuve contient du produit fini, ou vis-versa, par manque de verrouillage physique.
   * *Correction :* Mettre en œuvre des interverrouillages stricts dans l'automate (ex: blocage de l'ouverture de la vanne de soude si la vanne de vidange produit ou de remplissage n'est pas fermée et verrouillée électriquement).

---

## Liste de vérification (Checklist)

- [ ] Les étapes de nettoyage chimique (Soude/Acide) valident la température minimale de retour avant de décompter le temps de phase.
- [ ] La phase de rinçage final vérifie un seuil maximal de conductivité pour garantir l'absence de traces de produits chimiques résiduels.
- [ ] Tous les mouvements de matières premières sont associés à un numéro de lot et historisés en base de données.
- [ ] Des verrous de sécurité logicielle empêchent l'ouverture des lignes NEP vers des lignes contenant du produit alimentaire.

