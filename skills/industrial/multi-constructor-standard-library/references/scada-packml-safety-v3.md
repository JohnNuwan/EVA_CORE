# Référence v3 approfondie : SCADA, PackML et Safety

## Principe
Le JSON métier devient la source de vérité pour le PLC, le SCADA, le MES, la safety et les séquenceurs PackML. Le but est de produire des artefacts cohérents entre couches sans recopier la sémantique à la main.

## Couche SCADA / Ignition
Le générateur produit des tags structurés Cmd / Sts / Alm / Safety et ajoute PackML quand il est activé.

## Couche WinCC / InTouch / HMI
Le générateur produit aussi :
- un faceplate WinCC Unified XML ;
- des classes d'alarmes WinCC ;
- une navigation multi-écrans WinCC ;
- une vue OEE WinCC ;
- une vue Historian WinCC ;
- un export CSV InTouch ;
- des classes d'alarmes InTouch ;
- une navigation multi-écrans InTouch ;
- une vue OEE InTouch ;
- une vue Historian InTouch ;
- un faceplate safety standardisé ;
- un mapping HMI standardisé.

## Couche Safety
Les métadonnées de sécurité sont injectées dans les structures générées afin de garder visibles :
- la zone
- le PLr
- le SIL
- les fonctions STO / SS1 / SLS
- la nécessité de reset

## Couche PackML
Quand PackML est activé, le générateur ajoute un squelette de machine d'état standardisée et la structure de tags associée.

## Recommandation
Utiliser ce générateur pour amorcer les bibliothèques et contrats de données, puis compléter les détails spécifiques site/constructeur dans la phase d'ingénierie détaillée.
