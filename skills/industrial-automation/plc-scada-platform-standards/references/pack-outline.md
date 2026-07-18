# Plan détaillé d'un lot de packs experts PLC / SCADA

## 1. Pack Siemens SCL / TIA Portal
Inclure au minimum :
- architecture FB / FC / UDT / DB ;
- séquenceur type ;
- pattern analogique ;
- variables exposées au SCADA ;
- checklist de revue ;
- FAT / SAT ciblés.

## 2. Pack Rockwell Studio 5000
Inclure au minimum :
- rôle des Controller Tags vs Program Tags ;
- UDT / AOI / routines ;
- logique start / stop / reset / permissifs ;
- stratégie L5X ;
- contrat HMI / SCADA ;
- plan de tests atelier.

## 3. Pack Ignition SCADA / Jython
Inclure au minimum :
- architecture Gateway / Project Library / Perspective ;
- règles Jython 2.7 ;
- bulk read/write tags ;
- Named Queries ;
- asynchronisme ;
- sécurité / traçabilité opérateur.

## 4. Pack Intégration PLC ↔ SCADA
Inclure au minimum :
- taxonomie commune `Cmd`, `Sts`, `Alm`, `Ana`, `Meta` ;
- mapping Siemens / Rockwell / Ignition ;
- philosophie de commande ;
- standard alarmes ;
- historique utile ;
- matrice FAT / SAT interopérable.

## 5. Bundle final utilisateur
Créer un README sous `output/docs/guides/...` avec :
- la liste des packs créés ;
- les chemins ;
- ce que couvre chaque pack ;
- l'ordre conseillé d'exploitation.
