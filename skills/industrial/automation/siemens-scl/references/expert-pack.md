# Pack Expert Siemens SCL / TIA Portal

## Objectif

Ce pack expert complète la skill `siemens-scl` avec un cadre de conception prêt à l'emploi pour des développements industriels maintenables, testables et facilement supervisables depuis un SCADA ou un MES.

## 1. Architecture de code recommandée

### 1.1 Répartition des blocs
- `UDT_*` : structures de données normalisées par type d'équipement.
- `FB_*` : logique avec mémoire d'état, séquenceurs, traitements d'équipement.
- `FC_*` : calculs purs, conversions, normalisation, validation.
- `DB_*` : données d'instance ou paramètres persistants.
- `OB1` : orchestration minimale, appels lisibles, sans logique métier dense.
- `OB100` : initialisation à froid si nécessaire.
- `OB82/OB86/OB121/OB122` : stratégie défaut matériel / erreur de programmation selon le contexte projet.

### 1.2 Séparation fonctionnelle type
- `FB_DeviceCore` : logique interne de l'équipement.
- `FB_DeviceCmd` : arbitrage des commandes local/auto/manuel.
- `FB_DeviceAlm` : calcul des alarmes et défauts.
- `FB_DeviceIoMap` : adaptation entre structure métier et cartes E/S.
- `FC_ScaleAnalog`, `FC_FilterAnalog`, `FC_LimitCheck` : traitements analogiques réutilisables.

## 2. Convention de modélisation d'un équipement

### 2.1 UDT standard moteur
```scl
TYPE "UDT_Motor"
VERSION : 0.1
   STRUCT
      Cmd : Struct
         StartAuto : Bool;
         StopAuto : Bool;
         Reset : Bool;
         ModeAuto : Bool;
         ModeMan : Bool;
      END_STRUCT;
      Fb : Struct
         Run : Bool;
         Ready : Bool;
         Fault : Bool;
         Local : Bool;
      END_STRUCT;
      Alm : Struct
         FaultGeneral : Bool;
         NoFeedback : Bool;
         ThermalTrip : Bool;
      END_STRUCT;
      Tm : Struct
         StartTimeoutMs : Time;
      END_STRUCT;
   END_STRUCT;
END_TYPE
```

### 2.2 Règles de design
- Les commandes et retours doivent être séparés dans des sous-structures lisibles.
- Les alarmes ne doivent pas être recalculées dans le synoptique SCADA : elles sont construites côté automate.
- Les temporisations projet doivent être paramétrables via DB, pas codées en dur dans la logique.
- Toute variable exposée au SCADA doit être symbolique, stable et documentée.

## 3. Pattern de séquenceur industriel

### 3.1 États minimaux
- `0` : arrêt / attente
- `10` : préconditions
- `20` : démarrage
- `30` : en marche
- `40` : arrêt normal
- `90` : arrêt contrôlé sur défaut
- `99` : défaut verrouillé

### 3.2 Règles d'implémentation
- Une seule variable d'état principale : `stat_Step`.
- Les transitions doivent être lisibles sur une seule ligne métier.
- Les actions d'entrée d'étape doivent être protégées par un front ou un `stat_StepPrev`.
- Tout état critique doit avoir un timeout explicite.
- En cas de défaut, imposer un retour centralisé via `99` ou `90`.

### 3.3 Gabarit de séquenceur
```scl
CASE #stat_Step OF
    0:
        #q_Run := FALSE;
        IF #i_StartReq AND #i_PermissiveOk THEN
            #stat_Step := 10;
        END_IF;

    10:
        #stat_StartTon(IN := TRUE, PT := #i_StartTimeout);
        #q_Run := TRUE;
        IF #i_RunFb THEN
            #stat_StartTon(IN := FALSE);
            #stat_Step := 30;
        ELSIF #stat_StartTon.Q THEN
            #stat_FaultLatched := TRUE;
            #stat_Step := 99;
        END_IF;

    30:
        #q_Run := TRUE;
        IF #i_StopReq THEN
            #stat_Step := 40;
        ELSIF NOT #i_PermissiveOk THEN
            #stat_Step := 90;
        END_IF;

    40:
        #q_Run := FALSE;
        IF NOT #i_RunFb THEN
            #stat_Step := 0;
        END_IF;

    90:
        #q_Run := FALSE;
        IF NOT #i_RunFb THEN
            #stat_Step := 99;
        END_IF;

    99:
        #q_Run := FALSE;
        #q_Fault := TRUE;
        IF #i_Reset AND NOT #i_RunFb THEN
            #q_Fault := FALSE;
            #stat_FaultLatched := FALSE;
            #stat_Step := 0;
        END_IF;
END_CASE;
```

## 4. Pattern analogique standard

### 4.1 Chaîne de traitement recommandée
1. Acquisition brute
2. Validation qualité / défaut capteur
3. Mise à l'échelle
4. Filtrage éventuel
5. Clamp mini/maxi
6. Seuils d'alarme
7. Exposition SCADA/Historian

### 4.2 FC de scaling robuste
```scl
FUNCTION "FC_ScaleAnalog" : Real
{ S7_Optimized_Access := 'TRUE' }
VAR_INPUT
    i_Raw : Real;
    i_RawMin : Real;
    i_RawMax : Real;
    i_EuMin : Real;
    i_EuMax : Real;
END_VAR
VAR_TEMP
    temp_RawSpan : Real;
    temp_EuSpan : Real;
END_VAR
BEGIN
    #temp_RawSpan := #i_RawMax - #i_RawMin;
    #temp_EuSpan := #i_EuMax - #i_EuMin;

    IF #temp_RawSpan = 0.0 THEN
        "FC_ScaleAnalog" := #i_EuMin;
    ELSE
        "FC_ScaleAnalog" := ((#i_Raw - #i_RawMin) / #temp_RawSpan) * #temp_EuSpan + #i_EuMin;
    END_IF;
END_FUNCTION
```

## 5. Contrat PLC ↔ SCADA conseillé

### 5.1 Variables à exposer par équipement
- `CmdAutoStart`, `CmdAutoStop`, `CmdReset`
- `StsRun`, `StsReady`, `StsFault`, `StsLocal`
- `StepNo`, `StepText` si disponible
- `AlmSummary`, `AlmCode`, `AlmTextId`
- `Pv`, `Sp`, `ModeAuto`, `ModeMan`

### 5.2 Principes
- Le SCADA n'écrit jamais directement dans les bits internes de séquence.
- Les commandes montantes sont idéalement impulsionnelles ou arbitrées par un FB de commande.
- Les acquittements doivent être séparés des resets process.
- Les textes opérateur doivent être indexés ou centralisés, pas reconstruits au hasard côté HMI.

## 6. Performance et robustesse CPU

- Éviter les boucles `WHILE` ouvertes.
- Encadrer les accès tableau par `LOWER_BOUND` / `UPPER_BOUND` si bornes non fixes.
- Favoriser les multi-instances plutôt que des DB dispersés pour les timers IEC.
- Ne pas dupliquer les calculs lourds dans plusieurs FB si une couche de prétraitement suffit.
- Déporter les diagnostics verbeux dans un DB de diagnostic, pas dans des dizaines de bits isolés.

## 7. Plan de tests atelier recommandé

### 7.1 Tests unitaires logiques
- Démarrage avec permissifs valides
- Refus de démarrage sans permissif
- Timeout de retour marche
- Défaut mémorisé + reset
- Passage auto ↔ manuel
- Validation des seuils analogiques

### 7.2 Tests I/O et supervision
- Cohérence des noms symboliques exposés
- Correspondance DB ↔ tags SCADA
- États sûrs au redémarrage CPU
- Comportement après perte d'un feedback terrain

## 8. Checklist de revue experte
- [ ] FB pour la logique à état, FC pour le calcul pur.
- [ ] Pas d'adressage absolu sur S7-1200/1500 modernes sauf contrainte projet explicite.
- [ ] Toute transition critique a une condition de retour et un timeout.
- [ ] Les alarmes sont calculées côté automate et exposées proprement au SCADA.
- [ ] Les temporisations et seuils sont paramétrables.
- [ ] Les tableaux et conversions de types sont sécurisés.
- [ ] La structure de données est stable pour l'intégration SCADA/MES.

## 9. Cas d'usage où charger ce pack
- Conception d'un FB moteur/vanne/pompe.
- Standardisation d'une bibliothèque EVA Siemens.
- Audit de séquenceur TIA Portal.
- Préparation d'une interface Ignition/WinCC vers automate Siemens.
