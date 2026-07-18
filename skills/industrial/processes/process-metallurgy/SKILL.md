---
name: process-metallurgy
description: "Utiliser quand l'utilisateur demande d'écrire des algorithmes de régulation thermique (PID), de programmer des fonctions de sécurité machine (SIL/PL), ou de gérer des procédés en métallurgie et industrie lourde."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [metallurgy, heavy-industry, pid, safety-plc, sil, failsafe, alarm-storm, industrial-automation]
    related_skills: [simplify-code, plan]
---

# Métallurgie & Industrie Lourde (Sécurité SIL, PID Avancé & Températures)

## Vue d'ensemble

La métallurgie et l'industrie lourde (sidérurgie, cimenteries, fonderies) se caractérisent par des environnements physiques extrêmes (hautes températures, pressions élevées, charges lourdes) et des temps de réponse rapides. Deux axes logiciens y sont primordiaux :
1. **La régulation de procédés thermiques complexes :** Utilisation de boucles PID avancées (avec gestion d'Anti-Windup et régulation split-range pour le chauffage/refroidissement) et la gestion de rampes de cuisson.
2. **La sécurité fonctionnelle (Safety) :** Programmation de fonctions de sécurité conformes aux niveaux de performance **SIL** (Safety Integrity Level) et **PL** (Performance Level) sur des automates de sécurité (Failsafe).

Cette compétence guide l'agent Helios pour écrire des algorithmes de régulation thermique et des logiques de sécurité machine robustes.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire ou d'optimiser une boucle de régulation PID en SCL ou en Structured Text.
- De programmer des blocs de sécurité (arrêts d'urgence, barrières immatérielles, validation de portes) sur un automate Failsafe (ex. Siemens S7-1500F).
- De gérer un profil thermique avec des rampes de montée en température et des paliers de maintien.
- D'implémenter des algorithmes de filtrage de mesures bruitées pour capteurs de température (thermocouples, pyromètres).

**Ne pas utiliser pour :**
- Des applications SCADA pures d'historisation de données (utiliser `industrial-databases`).

---

## 1. Régulation Thermique PID & Anti-Windup

Les procédés thermiques (ex: fours de traitement thermique) ont une inertie importante. Lors d'un changement de consigne brusque, l'erreur s'accumule dans l'action intégrale du PID, provoquant un dépassement important (Overshoot) si aucun mécanisme d'Anti-Windup n'est implémenté.

### Squelette d'une boucle PID simple en SCL avec Anti-Windup :

```scl
FUNCTION "FC_Actemium_PID_Controller" : Real
VERSION : 0.1
   VAR_INPUT
      i_Setpoint : Real;      // Consigne
      i_ProcessValue : Real;  // Valeur mesurée (température)
      i_Kp : Real;            // Gain proportionnel
      i_Ki : Real;            // Gain intégral
      i_Kd : Real;            // Gain dérivé
      i_Ts : Real;            // Temps d'échantillonnage (s)
      i_OutMin : Real;        // Limite basse sortie
      i_OutMax : Real;        // Limite haute sortie
   END_VAR

   VAR_IN_OUT
      iq_IntegralSum : Real;  // Somme intégrale accumulée (persistante)
      iq_PrevError : Real;    // Erreur au cycle précédent (persistante)
   END_VAR

   VAR_TEMP
      temp_Error : Real;
      temp_P : Real;
      temp_I : Real;
      temp_D : Real;
      temp_Output : Real;
   END_VAR

BEGIN
   // Calcul de l'erreur
   #temp_Error := #i_Setpoint - #i_ProcessValue;
   
   // Action Proportionnelle
   #temp_P := #i_Kp * #temp_Error;
   
   // Action Dérivée
   #temp_D := #i_Kd * (#temp_Error - #iq_PrevError) / #i_Ts;
   
   // Action Intégrale avec Anti-Windup (Clamping)
   // On n'intègre pas si la sortie du régulateur est déjà saturée aux limites
   #temp_I := #iq_IntegralSum + (#i_Ki * #temp_Error * #i_Ts);
   
   #temp_Output := #temp_P + #temp_I + #temp_D;
   
   // Application des limites physiques et gestion de l'Anti-Windup
   IF #temp_Output > #i_OutMax THEN
       #temp_Output := #i_OutMax;
       // Bloquer l'accumulation intégrale à la limite haute
       #iq_IntegralSum := #i_OutMax - #temp_P - #temp_D;
   ELSIF #temp_Output < #i_OutMin THEN
       #temp_Output := #i_OutMin;
       // Bloquer l'accumulation intégrale à la limite basse
       #iq_IntegralSum := #i_OutMin - #temp_P - #temp_D;
   ELSE
       #iq_IntegralSum := #temp_I; // Accumulation normale
   END_IF;
   
   // Mémorisation de l'erreur pour le prochain cycle
   #iq_PrevError := #temp_Error;
   
   // Retourner la valeur calculée
   #FC_Actemium_PID_Controller := #temp_Output;
END_FUNCTION
```

---

## 2. Logique de Sécurité Failsafe (SIL/PL)

Le code de sécurité s'exécute dans un groupe d'exécution de sécurité (F-Runtime Group) séparé du code standard. Il utilise des variables spécifiques et des blocs certifiés par les constructeurs (ex: `ESTOP1` pour l'arrêt d'urgence).

### Exemple d'appel d'arrêt d'urgence certifié dans un bloc de sécurité (SCL Failsafe) :

```scl
// Appel du bloc d'arrêt d'urgence constructeur Siemens
"Inst_EmergencyStop"(
    E_STOP := #i_EstopButtonFeedback, // Contact physique NC de l'AU
    ACK := #i_ResetOperatorButton,   // Bouton reset physique
    RELEASE := TRUE,
    Q => #q_SafetyRelayActive,        // Sortie de sécurité vers bobine d'alimentation
    ACK_REQ => #q_ResetLightIndicator  // Voyant demandant un acquittement
);
```

*Note : Les blocs Failsafe interdisent les écritures directes depuis des IHM sans validation par un bouton matériel ou une procédure d'acquittement certifiée.*

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Saturation de l'action intégrale (Windup) :**
   * *Erreur :* Laisser l'action intégrale d'un régulateur de température accumuler de l'erreur lorsque la résistance chauffante est déjà à 100% de puissance. Lors du passage du point de consigne, le système mettra de longues minutes à refroidir, créant un dépassement thermique inacceptable.
   * *Correction :* Toujours mettre en place un algorithme de saturation (Clamping/Anti-Windup) comme décrit ci-dessus.

2. **Régulations rapides appelées dans la mauvaise tâche périodique :**
   * *Erreur :* Appeler un algorithme de régulation de pression très rapide (ex: 20ms) dans la tâche standard de l'automate qui s'exécute de façon non périodique ou avec une période trop longue (ex: 100ms).
   * *Correction :* Appeler les boucles de régulation dans une tâche cyclique périodique dédiée (Cyclic Interrupt OB30 sur Siemens, Task périodique sur Rockwell) à intervalle fixe et précis.

---

## Liste de vérification (Checklist)

- [ ] L'algorithme PID intègre une protection active contre la saturation de l'action intégrale (Anti-Windup).
- [ ] Les boucles de régulation rapides (température, pression, débit) sont exécutées dans des tâches cycliques périodiques dédiées à temps fixe.
- [ ] La logique de sécurité machine (arrêts d'urgence, verrous portes) est écrite dans le programme Failsafe séparé et utilise des blocs constructeurs certifiés.
- [ ] Les mesures analogiques des capteurs de température font l'objet d'un filtrage du premier ordre pour lisser le signal avant régulation.

