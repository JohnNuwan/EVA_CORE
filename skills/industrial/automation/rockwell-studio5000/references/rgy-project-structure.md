# Projet RGY — Structure FDS et Génération Rockwell

## Contexte

Projet d'automatisation d'une ligne de recyclage et plasturgie (RGY) basée sur automates **Rockwell ControlLogix / CompactLogix**. L'ingénierie est fournie sous forme de Spécifications Fonctionnelles Détail (FDS) réparties par zone physique.

## Arborescence complète des FDS

```
client_data/RGY/FDS/
├── RGY-FS-LIST-100517-RVB.xls              ← I/O List principale (E/S, adresses, types)
│
├── 00-GENERAL/                             ← FDS transverses (applicables à tout le site)
│   ├── SUPERVISION-C.pdf / .docx           ← Architecture supervision, alarmes, tendances
│   ├── CALIBRATION-E.pdf / .docx           ← Procédure d'étalonnage des capteurs
│   ├── PNEUMATIC_TRANSFER-A.pdf / .docx    ← Transfert pneumatique générique
│   ├── WEIGHT_CONTROL_MODULE-A.pdf / .docx ← Module de contrôle de pesée
│   ├── HORIZON-D.pdf / .docx               ← Interface système Horizon (MES/ERP)
│   ├── HEATING-TANKS-B.pdf / .docx         ← Chauffage des cuves LI06A
│   ├── HEATING-PIPE-B.pdf / .docx          ← Chauffage des canalisations LI06A
│   ├── AGITATION-TANKS-B.pdf / .docx       ← Agitation des cuves
│   ├── AGITATION-LI06A-C.pdf / .docx       ← Agitation spécifique LI06A
│   └── AGITATION-LI06B-C.pdf               ← Agitation spécifique LI06B
│
├── 01-RECEPTION/                           ← Zone réception matières premières
│   ├── GENERALITIES-A.pdf / .docx          ← Généralités réception
│   ├── UNLOAD-G.pdf / .docx               ← Déchargement camions / conteneurs
│   ├── WAREHOUSE-E.pdf / .docx            ← Gestion stock entrepôt
│   ├── LIQUID-E.pdf / .docx               ← Réception liquides
│   ├── SKID-F.pdf / .docx                 ← Skid de réception (SKR07)
│   ├── SKID-SKR07-A.pdf / .docx           ← Variante skid SKR07
│   └── Master/                             ← Originaux non révisés
│
├── 02-GRINDING/                            ← Zone broyage et dosage
│   ├── GENERALITIES-C.pdf / .docx          ← Généralités broyage
│   ├── GRINDER-L.pdf / .docx              ← Broyeur principal
│   ├── DOSING-F.pdf / .docx               ← Station de dosage générale
│   ├── DOSING_STATION_BB-SC21-C.pdf/.docx ← Dosage big bag SC21
│   ├── DOSING-SC05-C.pdf / .docx          ← Dosage SC05
│   ├── HOPPER-DOSING-C.pdf / .docx         ← Trémie de dosage
│   ├── HOPPER-DOSING_SC05-B.pdf / .docx    ← Trémie dosage SC05
│   ├── HOPPER-INTERMEDIATE-C.pdf / .docx   ← Trémie intermédiaire
│   ├── HOPPER_PREMIXER-B.pdf / .docx       ← Trémie prémélange
│   ├── MIXER-H.pdf / .docx                ← Mélangeur principal
│   ├── LIQUID_MIXER-E.pdf / .docx         ← Mélangeur liquide
│   ├── PREMIXER-H.pdf / .docx             ← Prémélangeur
│   ├── BIGBAG_EMPTY-B.pdf / .docx         ← Vidange big bags
│   ├── BIGBAG_FILL-B.pdf / .docx          ← Remplissage big bags
│   ├── STATION_FILL-C.pdf / .docx          ← Station de remplissage
│   ├── TRANSFER-MACRO_MICRO-H.pdf / .docx  ← Transfert macro/micro
│   ├── TRANSFER-INTERMEDIATE-B.pdf / .docx ← Transfert intermédiaire
│   ├── TRANSFER_UNDER_MIXER-A.pdf / .docx  ← Transfert sous mélangeur
│   ├── TRANSFER_UNDER_MIXER-B.pdf / .docx  ← Transfert sous mélangeur (v2)
│   ├── EMPTYING_RM_SILOS-A.pdf / .docx     ← Vidange silos matières premières
│   ├── PNEUMATIC_TRANSFER-D.pdf / .docx    ← Transfert pneumatique
│   ├── CALIBRATION-MX_SKR07-B.pdf / .docx  ← Calibration mélangeur SKR07
│   ├── WEIGHING_TEST-SC05-B.pdf / .docx    ← Test de pesée SC05
│   ├── CLEANING-B.pdf / .docx             ← Nettoyage (CIP/NEP)
│   ├── CLEANING-B(modif).docx             ← Nettoyage modifié
│   └── KPI_INDICATOR-C.pdf / .docx        ← KPI / TRS indicateurs de performance
│
├── 03-EXTRUSION/                           ← Zone extrusion (2 lignes)
│   ├── 1-LINE_1/                          ← FDS Ligne 1 (à explorer)
│   └── 2-LINE_2/
│       ├── GENERALITIES-B.pdf / .docx      ← Généralités ligne 2
│       ├── LIQUID_DOSING-C.pdf / .docx     ← Dosage liquide ligne 2
│       ├── HOSPITAL_BIN-C.pdf / .docx      ← Benne hôpital ligne 2
│       ├── FINES_RECYCLING-C.pdf / .docx   ← Recyclage fines ligne 2
│       ├── FILLING_POWDER-L2_PW01-B.pdf/.docx ← Remplissage poudre PW01
│       ├── FILLING_POWDER-L2_PW03-B.pdf/.docx ← Remplissage poudre PW03
│       ├── FP_TRANSPORT-C.pdf / .docx      ← Transport poudre fine
│       ├── VENTILATION_COATER-B.pdf / .docx ← Ventilation coater
│       ├── DRYER_OUTPUT.pdf / .docx        ← Sortie sécheur
│       └── PRIMING_NAOX-C.pdf / .docx      ← Amorçage NaOX
│
├── 04-PACKAGING/                           ← Zone conditionnement
│   ├── GENERALITIES-C.pdf / .docx          ← Généralités conditionnement
│   ├── BIGBAG_PACKING-D.pdf / .docx        ← Ensachage big bags
│   ├── KIBBLE_RECOVERY-FR02-B.pdf / .docx  ← Récupération kibble FR02
│   └── Master/
│
├── 08-INTERFACE_OTHER_SYSTEMS/            ← Interfaces tiers
│   ├── WMS-A.pdf / .docx                  ← Interface WMS (Warehouse Management)
│   ├── KSE-C.pdf / .docx                  ← Interface KSE (système externe)
│   ├── PRINTBBLABEL-A.pdf / .docx         ← Impression étiquettes big bags
│   └── Références/KSE_Exchanges.vsd       ← Schéma Visio échanges KSE
│
└── 09-UTILITY/
    └── REGRIND-E.pdf / .docx              ← Utilitaires regrind (broyage fin)
```

## Statistiques

| Métrique | Valeur |
|----------|--------|
| Nombre total de FDS | ~45 fichiers (PDF + DOCX) |
| Zones fonctionnelles | 7 (Général, Réception, Broyage, Extrusion-L1/L2, Conditionnement, Interfaces, Utilitaires) |
| Fichier I/O List | 1 (RGY-FS-LIST-100517-RVB.xls) |
| Skids identifiés | SKR07, SC05, SC21, FR02, LI06A, LI06B, PW01, PW03 |

## Règles de traitement pour génération Rockwell

1. **Ordre de priorité** : Toujours traiter `GENERALITIES` d'une zone en premier — ils définissent les UDT/AOI réutilisables.
2. **Version la plus récente** : Les suffixes de version (A, B, C, D...) sont ordonnés alphabétiquement. Prendre le plus haut.
3. **Format préféré** : DOCX > PDF (le DOCX est l'original, le PDF une exportation). Si les deux existent, traiter le DOCX.
4. **Skid injection** : Utiliser `--skid` du script de génération pour remplacer `SKXX` par les valeurs réelles ci-dessus.
5. **Cross-reference I/O** : Après génération, vérifier que chaque tag de la logique ST a un mapping dans l'I/O List.

## Génération Rockwell attendue par zone

| Zone | Nb FDS | Type de blocs Rockwell attendus |
|------|--------|--------------------------------|
| 00-GENERAL | 8 | AOI supervision, AOI calibration, UDT analogiques, AOI transfert pneumatique |
| 01-RECEPTION | 6 | AOI déchargement, AOI skid, routines gestion stock, routines liquides |
| 02-GRINDING | ~20 | AOI broyeur, AOI mélangeur, AOI trémie, AOI transfert, routines CIP |
| 03-EXTRUSION L2 | ~10 | AOI extrusion, AOI dosage liquide, AOI transport poudre, routines ventilation |
| 04-PACKAGING | 3 | AOI ensachage, AOI recovery kibble |
| 08-INTERFACES | 3 | Routines MSG WMS/KSE, routines impression |
| 09-UTILITY | 1 | AOI regrind |

*Mis à jour le 2026-07-06 — Session découverte projet RGY.*