# Pack Expert Bibliothèque Standard Multi-Constructeurs

## Objectif

Transformer une logique multi-marques en socle de patterns métier stables et portables. Le but n'est pas d'effacer les différences constructeurs, mais d'imposer un contrat métier unique puis de décliner l'implémentation par plateforme.

## 1. Objets standards prioritaires

- MotorStandard
- ValveStandard
- AnalogStandard
- SequenceStandard
- AlarmStandard
- InterlockStandard
- ExchangeStandard

## 2. Contrat métier recommandé

### MotorStandard
- Cmd.Start / Stop / Reset
- Mode.Auto / Manual
- Sts.Run / Ready / Fault / Local
- Alm.Summary / Code
- Tm.StartTimeout

### ValveStandard
- Cmd.Open / Close
- Sts.Opened / Closed / Moving / Fault
- Alm.Summary

### AnalogStandard
- RawValue
- Pv
- Sp
- Unit
- Fault
- HiAlarm / LoAlarm
- Quality

### SequenceStandard
- StepNo
- StepTextId
- Running
- Complete
- Fault
- ResetAllowed

## 3. Stratégie de déclinaison par constructeur

### Siemens
- UDT + FB + DB
- exposition symbolique TIA

### Rockwell
- UDT + AOI/routines + Controller Tags

### Beckhoff / WAGO / CODESYS-like
- DUT + FB + GVL

### Schneider
- DDT + DFB + variables d'échange

### Omron
- structures + FB + variables globales Sysmac

## 4. Couche d'adaptation constructeur

La logique doit être pensée sur 3 couches :
1. contrat métier transverse ;
2. adaptation constructeur ;
3. exposition supervision.

Ne jamais laisser la supervision dépendre directement de détails internes constructeur.

## 5. Contrat PLC ↔ SCADA recommandé

- commandes montantes dédiées ;
- états synthétiques ;
- alarmes résumées ;
- analogiques normalisés ;
- qualité/diagnostic ;
- noms stables d'une plateforme à l'autre.

## 6. Plan de déploiement de la bibliothèque

1. définir les objets de référence ;
2. figer le contrat de données ;
3. créer l'implémentation Siemens ;
4. créer l'implémentation Rockwell ;
5. dériver Beckhoff/WAGO/Omron/Schneider ;
6. brancher le SCADA sur le contrat transverse ;
7. documenter le mapping par plateforme.

## 7. Pièges Courants

1. Créer une bibliothèque différente par marque sans noyau commun.
2. Laisser les équipes SCADA consommer des détails internes variables.
3. Mélanger logique métier et mappage matériel.
4. Sous-documenter les équivalences de structures.

## 8. Checklist de mise en place

- [ ] Un modèle transverse a été défini avant la moindre implémentation.
- [ ] Chaque objet métier a son pattern standard.
- [ ] Le SCADA consomme un contrat stable.
- [ ] Les adaptations constructeur sont documentées séparément.
- [ ] Le mapping multi-marques est versionné.
