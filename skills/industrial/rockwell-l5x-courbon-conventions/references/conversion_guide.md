# Guide de conversion — Zone-based / AOI-based → FCT Conventions

## Pourquoi convertir ?

Les projets Courbon/EVA utilisent **1 FCT = 1 programme** (pas 1 zone = 1 fichier).
Un projet correct contient 40-60 FCT, pas 9 fichiers zone.

## Scénario 1 : Projet zone-based (ma V1)

### Structure d'entrée
```
ROH_Zone_Extrusion.L5X    ← 1 fichier = 1 zone (1200+ lignes)
ROH_Zone_Coater.L5X
ROH_Zone_Dryer.L5X        ← Tout le dryer dans 1 fichier
```

### Problèmes
- 1 fichier contient trop d'équipements
- Pas de standard d'interface
- UDTs génériques (UDT_Motor, UDT_Valve)
- ST uniquement (pas de SFC)

### Conversion
1. **Découper** chaque zone en fonctions atomiques (1 équipement = 1 FCT)
2. **Créer** les UDT_EM_XXX pour chaque équipement (pattern CMD/STS)
3. **Ajouter** les interfaces standard (IO_FCT, IO_BATCH_MGT, PLC_TASK_EXC)
4. **Ajouter** les routines SFC (Main + Running)
5. **Ajouter** les routines RLL (EnableInFalse + Prescan)
6. **Numéroter** les FCT (01..99)

### Exemple : Dryer zone (1 fichier → 5 FCT)
```
Avant : ROH_Zone_Dryer.L5X (2689 lignes, 1 fichier)
Après :
  FCT_10_DRYER_TRANSPORT.L5X       (conveyor)
  FCT_12_HWT_PRODUCTION.L5X        (HWT production)
  FCT_13_HWT_CLEANING.L5X          (HWT cleaning)
  + UDTs dryer génériques dans le projet maître
```

## Scénario 2 : Projet AOI-based (structure RGY)

### Structure d'entrée
```
00-GENERAL/
  l5x/
    RGY_00SUPERVISION_AOI.L5X      ← AOI = Add-On Instruction
    RGY_00SUPERVISION_Routine.L5X   ← Routine séparée
    RGY_01CALIBRATION_AOI.L5X
    RGY_01CALIBRATION_Routine.L5X
  st/
    RGY_00SUPERVISION.st
    RGY_01CALIBRATION.st
  00_GENERAL_Program.L5X            ← Programme conteneur
```

### Problèmes
- AOI + Routine séparés = 2 fichiers par fonction (vs 1 FCT)
- Le programme conteneur référence les AOIs
- Pas de standard d'interface
- Structure de dossiers par zone (pas par fonction)

### Conversion
1. **Fusionner** AOI + Routine en 1 seul FCT_XX
2. **Supprimer** les paramètres AOI, utiliser les tags programme
3. **Conserver** la logique ST du fichier .st ou de la Routine
4. **Ajouter** les interfaces standard
5. **Ajouter** les routines SFC
6. **Renommer** : `RGY_XX_NAME` → `FCT_XX_NAME`

### Exemple : 1 fonction AOI-based → 1 FCT
```
Avant (3 fichiers par fonction) :
  RGY_06HEATING_TANK_AOI.L5X
  RGY_06HEATING_TANK_Routine.L5X
  RGY_06HEATING_TANK.st

Après (1 fichier) :
  FCT_07_HEATING_TANK.L5X
    DataTypes: UDT_EM_TANK_HEATING (CMD/STA/SETPOINT/REPORT)
    Tags: IO_FCT, IO_BATCH_MGT, L_EM_TANK_HEATING
    Routines: Main(SFC), Running(SFC), Logic(ST CDATA)
```

## Scénario 3 : Conversion depuis ACD (Studio 5000)

Quand on a un fichier `.ACD` (projet compilé) :
1. **Ouvrir** dans Studio 5000
2. **Exporter** chaque programme en L5X (File → Export)
3. **Analyser** la structure des tags et UDTs existants
4. **Créer** les UDT_EM_XXX correspondant aux structures existantes
5. **Adapter** chaque programme exporté au format FCT (ajouter interfaces)

## Vérification post-conversion

```bash
# Vérifier que tous les FCT ont CDATA
grep -c 'CDATA' FCT_*.L5X | grep ':0' || echo "OK - tous ont CDATA"

# Vérifier qu'aucun Content n'est vide
grep '<Content/>' FCT_*.L5X && echo "ATTENTION: Content vide détecté"

# Vérifier le nombre de FCT
ls FCT_*.L5X | wc -l

# Vérifier la cohérence des noms
for f in FCT_*.L5X; do
  name=$(grep 'Program Name=' "$f" | head -1 | sed 's/.*Name="\([^"]*\)".*/\1/')
  base=$(basename "$f" .L5X)
  if [ "$name" != "$base" ]; then
    echo "MISMATCH: $base → Program=$name"
  fi
done
```

## Pièges fréquents en conversion

| Problème | Cause | Solution |
|----------|-------|----------|
| Content/Content vide | L'AOI avait un paramètre EnableIn mais pas de code | Lire le code ST depuis le fichier .st |
| Pas de CDATA | L'export ACD ou la génération a oublié le wrapper | Envelopper dans CDATA |
| UDT dupliqués | Chaque FCT déclare ses propres UDTs | Mutualiser dans ROH_UDT_Definitions |
| Programme Name != filename | Renommage sans mise à jour XML | grep et remplacer |
| Tags manquants | L'ancien format utilisait des paramètres AOI au lieu de tags | Ajouter IO_FCT, IO_BATCH_MGT, etc. |
