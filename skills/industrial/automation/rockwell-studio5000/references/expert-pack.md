# Pack Expert Rockwell Studio 5000 / Logix Designer

## Objectif

Ce pack expert complète la skill `rockwell-studio5000` avec une méthode de conception industrielle orientée réutilisabilité, import L5X propre, diagnostics efficaces et intégration HMI/SCADA stable.

## 1. Architecture Logix recommandée

### 1.1 Découpage minimal
- `Controller Tags` : interface HMI/SCADA, échanges inter-programmes, consignes globales.
- `Program Tags` : états internes, séquence locale, calculs temporaires.
- `UDT_*` : contrat de données standardisé.
- `AOI_*` : encapsulation des équipements et traitements répétés.
- `Routine Main_*` : orchestration lisible, sans micro-logiques dupliquées.
- `Periodic Tasks` : traitements déterministes critiques.
- `Continuous Task` : logique non critique ou supervision interne légère.

### 1.2 Principe de lisibilité
- Un équipement = un UDT + une routine ou AOI cohérente.
- Les tags exposés à l'extérieur ne doivent pas dépendre du nom d'une routine locale.
- Les commandes HMI entrantes doivent être arbitrées avant d'attaquer la logique process.

## 2. Modèle de données standard équipement

### 2.1 UDT moteur type
```pascal
TYPE UDT_MOTOR :
STRUCT
    Cmd :
    STRUCT
        StartAuto : BOOL;
        StopAuto : BOOL;
        Reset : BOOL;
        AutoMode : BOOL;
        ManualMode : BOOL;
    END_STRUCT;
    Fb :
    STRUCT
        Run : BOOL;
        Ready : BOOL;
        Fault : BOOL;
        Local : BOOL;
    END_STRUCT;
    Alm :
    STRUCT
        FaultGeneral : BOOL;
        StartTimeout : BOOL;
        ThermalTrip : BOOL;
    END_STRUCT;
    Ana :
    STRUCT
        Pv : REAL;
        Sp : REAL;
    END_STRUCT;
END_STRUCT;
END_TYPE;
```

### 2.2 Règles de nommage terrain
- Préfixe de zone ou machine au niveau du tag global si nécessaire.
- Noms < 40 caractères.
- Pas d'accents, pas d'espaces, pas de double underscore.
- Les booléens doivent exprimer un état clair : `Motor01_RunFb`, `Motor01_Fault`, `Cmd_Start`.

## 3. Pattern AOI recommandé

### 3.1 Responsabilités d'une AOI équipement
- Validation permissifs / interlocks
- Gestion start/stop/reset
- Timeout de démarrage
- Défaut mémorisé
- Exposition d'états synthétiques au SCADA

### 3.2 Squelette logique ST
```pascal
IF ResetCmd THEN
    FaultLatched := 0;
    StartTmr.ACC := 0;
END_IF;

PermissiveOk := EStopOk AND ThermalOk AND RemoteMode;

IF StartCmd AND PermissiveOk AND NOT FaultLatched THEN
    RunCmd := 1;
END_IF;

IF StopCmd OR NOT PermissiveOk THEN
    RunCmd := 0;
END_IF;

StartTmr.PRE := StartTimeoutMs;
StartTmr.TimerEnable := RunCmd AND NOT RunFb;
TON(StartTmr);

IF StartTmr.DN THEN
    FaultLatched := 1;
    StartTimeoutAlm := 1;
    RunCmd := 0;
END_IF;

Fault := FaultLatched OR DeviceFault;
Ready := PermissiveOk AND NOT Fault;
```

## 4. Convention HMI / SCADA Rockwell

### 4.1 À exposer en Controller Tags
- commandes opérateur consolidées
- états synthétiques d'équipement
- valeurs analogiques utiles au synoptique
- alarmes résumées
- pas de tags purement temporaires ou de debug interne de routine

### 4.2 Contrat conseillé
- `*_Cmd_Start`, `*_Cmd_Stop`, `*_Cmd_Reset`
- `*_Sts_Run`, `*_Sts_Ready`, `*_Sts_Fault`, `*_Sts_Local`
- `*_Alm_Summary`, `*_Alm_Code`
- `*_Pv`, `*_Sp`

### 4.3 Bonnes pratiques
- Le SCADA ne doit pas écrire directement dans des tags de séquence interne.
- Les commandes peuvent être impulsionnelles puis consommées par la logique automate.
- Les retours de terrain ne doivent jamais être simulés côté HMI en production.

## 5. L5X : structure et génération fiable

### 5.1 Recommandations
- Toujours encapsuler le ST dans `CDATA`.
- Garder un ordre XML propre : `DataTypes`, `AddOnInstructionDefinitions`, `Tags`, `Programs`.
- Nommer explicitement `SoftwareRevision` et `TargetType` si vous générez un fragment complet.
- Vérifier la cohérence des `DataType`, `TagType`, `Usage` avant import.

### 5.2 Points de contrôle avant import
- Noms < 40 caractères
- Aucun caractère XML non échappé hors CDATA
- AOI et UDT référencés présents dans le fichier ou déjà dans le projet
- Portée correcte `Controller` vs `Program`
- Pas de collision de nom dans la cible Studio 5000

## 6. Pattern analogique standard

### 6.1 Scaling réutilisable
```pascal
RawSpan := RawMax - RawMin;
EuSpan := EuMax - EuMin;

IF RawSpan <> 0.0 THEN
    PvScaled := ((InputRaw - RawMin) / RawSpan) * EuSpan + EuMin;
    IF PvScaled > EuMax THEN
        PvScaled := EuMax;
    ELSIF PvScaled < EuMin THEN
        PvScaled := EuMin;
    END_IF;
    ScaleFault := 0;
ELSE
    PvScaled := EuMin;
    ScaleFault := 1;
END_IF;
```

### 6.2 Compléments recommandés
- Deadband d'alarme sur analogiques bruyants
- Filtre simple premier ordre si le terrain l'impose
- Bit `BadQuality` si perte de valeur d'origine ou défaut module

## 7. Scheduling et performances

- Les équipements critiques doivent vivre dans une `Periodic Task` connue.
- Les AOI lourdes ne doivent pas recalculer inutilement les mêmes expressions.
- Les boucles de lecture massive via communications externes doivent être regroupées.
- Les tags SCADA très verbeux doivent être limités pour éviter l'inflation de trafic.

## 8. Plan de tests atelier recommandé
- Commande start/stop nominale
- Perte permissif en marche
- Timeout démarrage
- Reset défaut verrouillé
- Contrôle local / distant
- Échanges HMI sur Controller Tags
- Import L5X sur projet cible vierge

## 9. Checklist de revue experte
- [ ] Les portées `Controller Tags` / `Program Tags` sont justifiées.
- [ ] Les AOI encapsulent bien la logique récurrente.
- [ ] Les tags destinés au SCADA sont stables et lisibles.
- [ ] Les timers utilisent correctement `.PRE`, `.ACC`, `.DN`, `.TT`.
- [ ] Le scaling protège la division par zéro et les dépassements.
- [ ] Les fragments L5X sont importables sans correction manuelle.
- [ ] Les noms restent compatibles Studio 5000.

## 10. Cas d'usage où charger ce pack
- Création d'un standard Rockwell moteur/vanne.
- Génération de L5X à partir d'une liste d'E/S.
- Revue d'un projet CompactLogix/ControlLogix.
- Intégration Ignition ↔ Controller Tags Rockwell.
