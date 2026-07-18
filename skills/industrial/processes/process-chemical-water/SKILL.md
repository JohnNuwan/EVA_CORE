---
name: process-chemical-water
description: "Utiliser quand l'utilisateur demande de concevoir, réguler ou optimiser des systèmes de traitement d'eau industrielle ou des procédés chimiques continus impliquant des boucles PID et des vannes d'asservissement."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [chemical-processes, water-treatment, pid, process-engineering]
    related_skills: [industrial-protocols, systematic-debugging]
---

# Génie des Procédés Chimiques & Traitement d'Eau

## Vue d'ensemble

Les procédés de **traitement d'eau industrielle** (osmose inverse, filtration, neutralisation de pH) et les **procédés chimiques continus** nécessitent des régulations automatiques précises pour maintenir des conditions optimales de sécurité et de qualité. Le cœur de ces régulations repose sur des boucles fermées **PID (Proportionnel, Intégral, Dérivé)** agissant sur des vannes modulantes, des pompes doseuses ou des variateurs de vitesse.

Les principaux paramètres physiques surveillés et régulés sont :
- **Le pH (potentiel Hydrogène) :** Contrôle de l'acidité/alcalinité via le dosage d'acide ou de soude. Régulation hautement non-linéaire.
- **La conductivité :** Mesure de la concentration en ions pour évaluer la pureté de l'eau (critique pour l'osmose inverse ou les chaudières).
- **Le débit (m3/h) et la pression (bar) :** Régulation hydraulique classique.
- **La température (°C) :** Maîtrise des cinétiques de réaction chimique et des phases de nettoyage en place (NEP/CIP).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'implémenter ou d'ajuster des boucles de régulation PID en Structured Text (ST) pour des procédés de fluides.
- D'écrire des algorithmes de calcul ou de conversion d'unités physiques (par exemple, mise à l'échelle de capteurs 4-20 mA).
- De concevoir la logique de sécurité pour les surpressions, débits nuls ou surdosages de produits chimiques.
- De comprendre le fonctionnement et l'intégration des étapes d'un traitement d'eau standard (lavage de filtres, régénération de résines).

**Ne pas utiliser pour :**
- Les procédés d'usinage mécanique ou de robotique d'assemblage discret.

---

## 1. Implémentation d'une Boucle PID en Structured Text (ST)

Bien que la plupart des automates possèdent des blocs PID natifs (comme `PIDE` sur Rockwell ou `PID_Compact` sur Siemens), il est parfois nécessaire de coder ou de simuler une boucle PID simple :

```pascal
// --- REGULATION PID DE DEBIT / PRESSION ---
// Variables :
//   SP             : REAL (Setpoint / Consigne de débit, ex: 10.0 m3/h)
//   PV             : REAL (Process Variable / Mesure de débit réelle)
//   Kp, Ki, Kd     : REAL (Gains Proportionnel, Intégral, Dérivé)
//   Ts             : REAL (Temps d'échantillonnage de la tâche en secondes, ex: 0.1)
//   Error, Error_Old: REAL (Écarts de consigne)
//   P_Out, I_Out, D_Out: REAL (Actions intermédiaires)
//   CO             : REAL (Control Output / Commande vanne 0.0 à 100.0 %)

// 1. Calcul de l'erreur
Error := SP - PV;

// 2. Action Proportionnelle
P_Out := Kp * Error;

// 3. Action Intégrale (avec traitement anti-windup simple)
IF NOT Manual_Mode THEN
    I_Out := I_Out + (Ki * Error * Ts);
    
    -- Anti-windup : limitation de la somme intégrale pour éviter la saturation
    IF I_Out > 100.0 THEN
        I_Out := 100.0;
    ELSIF I_Out < 0.0 THEN
        I_Out := 0.0;
    END_IF;
ELSE
    I_Out := 0.0;
END_IF;

// 4. Action Dérivée
D_Out := Kd * ((Error - Error_Old) / Ts);
Error_Old := Error;

// 5. Calcul de la commande totale et saturation finale
CO := P_Out + I_Out + D_Out;

IF CO > 100.0 THEN
    CO := 100.0;
ELSIF CO < 0.0 THEN
    CO := 0.0;
END_IF;
```

---

## 2. Régulation du pH : La Non-Linéarité du Procédé

La courbe de neutralisation du pH est extrêmement non-linéaire (forme de courbe en "S" ou sigmoïde). Près du point de neutralité (pH = 7), une infime goutte d'acide ou de base peut faire varier le pH de façon brutale.

### Bonnes pratiques de régulation du pH :
*   **Gain adaptatif (Split-Range) :** Utiliser des gains PID très faibles autour de la zone neutre (pH 6 à 8) et des gains plus forts quand on s'éloigne des limites pour doser rapidement.
*   **Dosage impulsionnel (Pulse-Width Modulation - PWM) :** Pour les pompes doseuses à débit fixe, réguler en faisant varier le temps de marche sur une période (ex: 2 secondes de marche, 8 secondes d'arrêt).

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Saturation de l'intégrale (Integral Windup) :**
    *   *Erreur :* Laisser l'action intégrale s'accumuler indéfiniment pendant que l'actionneur est en butée physique (ex: vanne ouverte à 100% mais débit insuffisant car la pompe principale est coupée). Au redémarrage, la vanne restera bloquée ouverte trop longtemps le temps que l'intégrale se "décharge", provoquant un fort dépassement.
    *   *Correction :* Toujours geler ou limiter l'action intégrale dès que la sortie de commande PID atteint 0% ou 100% (Anti-Windup).
2.  **Mise à l'échelle linéaire sur des capteurs non-linéaires :**
    *   *Erreur :* Mettre à l'échelle linéairement un capteur de débit alors que l'organe de mesure (ex: plaque à orifice) requiert une loi d'extraction de racine carrée.
    *   *Correction :* Vérifier les spécifications techniques de l'instrument de mesure pour implémenter la bonne formule de mise à l'échelle.

---

## Liste de vérification (Checklist)

- [ ] L'algorithme PID intègre un mécanisme d'anti-windup pour éviter l'emballement de la partie intégrale en cas de saturation de la sortie.
- [ ] La fréquence d'exécution du bloc PID est fixe et stable (appel dans une tâche périodique dédiée, par ex. 100 ms).
- [ ] Une validation de la validité de la mesure (ex: détection de sonde cassée ou valeur hors gamme 4-20 mA) force la sortie PID en mode manuel de sécurité (0% de commande).
- [ ] La régulation de pH prend en compte la nature non-linéaire de la neutralisation (par gain adaptatif ou bande morte).

