---
name: plc-simulation-blocks
description: "Générer des blocs de simulation de procédé pour tests."
version: 1.3.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [simulation, sil, hil, process-control, testing, automation-engineering, pid-control]
  related_skills: [siemens-scl-generation, rockwell-l5x-generation]
---

# Simulation de Procédé (SIL) & Algorithmes de Régulation Avancés

## Vue d'ensemble

Cette compétence régit la conception de modèles mathématiques discrets exécutés en temps réel dans les automates programmables (PLC) pour simuler la physique de procédés industriels (HIL/SIL), ainsi que l'implémentation d'algorithmes de régulation performants de niveau industriel.

---

## Fondements Mathématiques de la Discrétisation

Pour simuler un comportement physique continu (décrit par des équations différentielles) dans un automate fonctionnant par cycles d'exécution discrets de période $dT$, on applique des méthodes d'approximation numérique.

### Approximation d'Euler Avant (Explicit Euler)
Pour une équation différentielle du premier ordre $\tau \frac{dy(t)}{dt} + y(t) = K \cdot u(t)$, la dérivée est approchée par :
$$\frac{dy(t)}{dt} \approx \frac{y[k] - y[k-1]}{dT}$$
Ce qui donne l'équation de récurrence discrète du bloc PT1 (Premier ordre simple) :
$$y[k] = y[k-1] + \frac{dT}{\tau} \cdot (K \cdot u[k-1] - y[k-1])$$

---

## Régulateur PID Industriel avec Anti-Windup et Filtrage

Un PID continu sous forme parallèle standard s'exprime par :
$$u(t) = K_p \cdot \left( e(t) + \frac{1}{T_i} \int e(t)dt + T_d \frac{de(t)}{dt} \right)$$

Pour l'implémenter de manière industrielle, l'algorithme discret intègre :
1. **L'anti-windup** : Arrêt de l'intégration lorsque la sortie physique du régulateur est saturée (limites 0-100%).
2. **Le filtrage de l'action dérivée** : Ajout d'un filtre passe-bas du premier ordre sur la dérivée pour éviter l'amplification du bruit de mesure.
3. **Le transfert Bumpless (sans à-coups)** : Initialisation de l'action intégrale lors du passage du mode Manuel au mode Automatique pour éviter un saut brusque de la commande.

```pascal
FUNCTION_BLOCK "FB_Regul_PID_Industrial"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0
   VAR_INPUT 
      rSetpoint    : Real;        // Consigne (SP)
      rProcessVal  : Real;        // Mesure physique du procédé (PV)
      bModeAuto    : Bool;        // Mode : TRUE = Auto, FALSE = Manuel
      rManualVal   : Real;        // Valeur de commande forcée en mode Manuel (%)
      
      (* Paramètres de réglage *)
      rKp          : Real := 1.0; // Gain Proportionnel
      rTi          : Real := 10.0;// Constante de temps intégrale en secondes (0.0 = Désactivé)
      rTd          : Real := 0.0; // Constante de temps dérivée en secondes (0.0 = Désactivé)
      rN           : Real := 10.0;// Coefficient de filtrage de la dérivée (typiquement 8.0 - 20.0)
      rOutMin      : Real := 0.0; // Limite basse de la sortie (%)
      rOutMax      : Real := 100.0;// Limite haute de la sortie (%)
      rCycleTime   : Real := 0.1; // Période d'échantillonnage réelle dT (s)
   END_VAR

   VAR_OUTPUT 
      rOutValue    : Real;        // Commande finale (CV, 0.0 - 100.0 %)
      bSaturated   : Bool;        // Indicateur de saturation de la sortie
   END_VAR

   VAR 
      rErrorInt    : Real := 0.0; // Somme de l'intégrale
      rErrorLast   : Real := 0.0;
      rDerivFilter : Real := 0.0; // État du filtre de la dérivée
      bModeLast    : Bool := FALSE;
   END_VAR

   VAR_TEMP
      rError       : Real;        // Écart courant (e = SP - PV)
      rPropTerm    : Real;        // Terme Proportionnel
      rIntTerm     : Real;        // Terme Intégral
      rDerivTerm   : Real;        // Terme Dérivé
      rRawOut      : Real;        // Commande brute avant saturation
   END_VAR

BEGIN
    #rError := #rSetpoint - #rProcessVal;
    
    // 1. GESTION DU TRANSFERT BUMPLESS (MANUEL -> AUTO)
    IF NOT #bModeLast AND #bModeAuto THEN
        // Initialise la somme intégrale pour correspondre exactement à la sortie manuelle courante
        IF #rKp <> 0.0 THEN
            #rErrorInt := (#rManualVal / #rKp) - #rError;
        ELSE
            #rErrorInt := 0.0;
        END_IF;
        #rDerivFilter := 0.0;
    END_IF;
    #bModeLast := #bModeAuto;
    
    IF NOT #bModeAuto THEN
        // Mode Manuel : Sortie fixée par l'opérateur
        #rOutValue := LIMIT(MN := #rOutMin, IN := #rManualVal, MX := #rOutMax);
        #rErrorInt := 0.0; // Reset de l'intégrale en manuel
        RETURN;
    END_IF;
    
    // 2. ACTION PROPORTIONNELLE
    #rPropTerm := #rKp * #rError;
    
    // 3. ACTION INTÉGRALE (Avec Anti-Windup conditionnel)
    IF #rTi > 0.0 THEN
        // Anti-Windup : N'intègre l'erreur que si le régulateur n'est pas déjà saturé
        // ou si l'erreur ramène la commande vers sa plage active.
        IF NOT #bSaturated OR (#rError > 0.0 AND #rOutValue < #rOutMax) OR (#rError < 0.0 AND #rOutValue > #rOutMin) THEN
            #rErrorInt := #rErrorInt + #rError * #rCycleTime;
        END_IF;
        #rIntTerm := (#rKp / #rTi) * #rErrorInt;
    ELSE
        #rIntTerm := 0.0;
        #rErrorInt := 0.0;
    END_IF;
    
    // 4. ACTION DÉRIVÉE FILTRÉE
    IF #rTd > 0.0 AND #rN > 0.0 THEN
        // Discrétisation de l'action dérivée filtrée (approximation d'Euler arrière)
        #rDerivFilter := (#rTd * #rDerivFilter + #rKp * #rTd * #rN * (#rError - #rErrorLast)) / (#rTd + #rN * #rCycleTime);
        #rDerivTerm := #rDerivFilter;
    ELSE
        #rDerivTerm := 0.0;
        #rDerivFilter := 0.0;
    END_IF;
    
    #rErrorLast := #rError;
    
    // 5. CALCUL DU SIGNAL DE COMMANDE GLOBAL ET CLAMPING
    #rRawOut := #rPropTerm + #rIntTerm + #rDerivTerm;
    
    #bSaturated := (#rRawOut > #rOutMax) OR (#rRawOut < #rOutMin);
    #rOutValue := LIMIT(MN := #rOutMin, IN := #rRawOut, MX := #rOutMax);
END_FUNCTION_BLOCK
```

---

## Modélisation de Procédé PT1 avec Temps Mort (SCL Siemens)

Ce bloc simule la partie opérative physique d'un procédé thermique (ex: montée en température d'un four alimenté par une vanne de gaz).

```pascal
FUNCTION_BLOCK "FB_Sim_Process_PT1"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0
   VAR_INPUT 
      rInput       : Real;        // Commande d'entrée (ex: Ouverture vanne 0.0 - 100.0)
      rGain        : Real := 1.5; // Gain statique
      rTimeConst   : Real := 15.0;// Constante de temps Tc (s)
      rDeadTime    : Real := 5.0; // Temps mort de transmission (s)
      rAmbient     : Real := 20.0;// Température ambiante de départ (°C)
      rCycleTime   : Real := 0.1; // dT (s)
   END_VAR

   VAR_OUTPUT 
      rOutput      : Real;        // Mesure température simulée (°C)
   END_VAR

   VAR 
      arrDelayRing : Array[0..100] of Real; // Buffer circulaire pour simulation du retard
      iWriteIdx    : Int := 0;
      rLastOutput  : Real;
   END_VAR

   VAR_TEMP
      iDelaySteps : Int;
      iReadIdx    : Int;
      rDelayedIn  : Real;
   END_VAR

BEGIN
    // Calcul du nombre de cycles de retard
    #iDelaySteps := REAL_TO_INT(#rDeadTime / #rCycleTime);
    #iDelaySteps := LIMIT(MN := 0, IN := #iDelaySteps, MX := 100);
    
    #arrDelayRing[#iWriteIdx] := #rInput;
    
    #iReadIdx := #iWriteIdx - #iDelaySteps;
    IF #iReadIdx < 0 THEN
        #iReadIdx := 100 + #iReadIdx + 1;
    END_IF;
    
    #rDelayedIn := #arrDelayRing[#iReadIdx];
    
    #iWriteIdx := #iWriteIdx + 1;
    IF #iWriteIdx > 100 THEN
        #iWriteIdx := 0;
    END_IF;
    
    // Équation différentielle discrétisée (PT1)
    IF #rTimeConst > 0.0 THEN
        #rOutput := #rLastOutput + (#rCycleTime / #rTimeConst) * ((#rDelayedIn * #rGain) - (#rLastOutput - #rAmbient));
    ELSE
        #rOutput := (#rDelayedIn * #rGain) + #rAmbient;
    END_IF;
    
    #rLastOutput := #rOutput;
END_FUNCTION_BLOCK
```
