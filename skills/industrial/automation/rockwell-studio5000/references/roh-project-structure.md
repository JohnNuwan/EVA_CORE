# Projet ROH — Structure FDS et Génération Rockwell

## Contexte

Projet d'automatisation d'une ligne **d'extrusion plasturgie** (ROH) basée sur automates Rockwell ControlLogix / CompactLogix. L'ingénierie est fournie sous forme de Spécifications Fonctionnelles Détail (FDS) au format **PDF uniquement** (pas de DOCX).

## Arborescence des FDS

```
client_data/ROH/
├── ROH-FDS-EXTRUSION-CALIBRATION-NAOX-C.pdf         ← Calibration NAOX (23 pages)
├── ROH-FDS-EXTRUSION-CALIBRATION-D.pdf               ← Calibration générale (26 pages)
├── ROH-FDS-EXTRUSION-ASPIRATION-ELEVATOR_HOSPITAL-B.pdf  ← Aspiration élévateur/hôpital (24 pages)
├── ROH-FDS-EXTRUSION-ASPIRATION-DRYER_SIFTER-B.pdf   ← Aspiration sécheur/tamis (20 pages)
└── ROH-FDS-EXTRUSION-ASPIRATION-COATER_HOPPER-B.pdf  ← Aspiration trémie enrobeur (26 pages)
```

## Modules générés

| FDS | Fichier .st | Machine d'états | Particularités |
|-----|-------------|-----------------|----------------|
| CALIBRATION-NAOX-C | `ROH_CALIBRATION_NAOX.st` | 5 steps : Idle→Init→Calibration→Dripping→Waiting→End | Timers TON, mémoire push button, alarmes vannes manuelles, alarme niveau bas |
| CALIBRATION-D | `ROH_CALIBRATION.st` | 5 steps + vanne 4-voies vers pompe | Gestion pompe conditionnée par position vannes manuelles |
| ASPIRATION-ELEVATOR_HOSPITAL-B | `ROH_ASPIRATION_ELEVATOR.st` | 3 states : Idle→Waiting→End | Auto/manu, timer 300s hôpital, ventilation |
| ASPIRATION-DRYER_SIFTER-B | `ROH_ASPIRATION_DRYER.st` | 3 states : Idle→Waiting→End | Démarrage auto (Dryer Transport) ou manuel avec timer |
| ASPIRATION-COATER_HOPPER-B | `ROH_ASPIRATION_COATER.st` | 3 states + vidange cyclone (4 étapes) | Variateur vitesse 3 niveaux, vannes BD01/BD02/kibble |

## Contrainte spécifique : FDS en PDF uniquement

Contrairement au projet RGY (majorité de DOCX), le projet ROH est 100% PDF. Cela implique :

1. **Extraction moins fiable** : `pypdf` extrait le texte mais les tableaux peuvent être déformés, l'ordre des paragraphes peut être non linéaire.
2. **Vérification du code généré** : Chaque routine ST générée depuis un PDF doit être relue pour vérifier que les séquences et conditions sont correctes.
3. **Pas de script generate_rockwell_from_fds.py** : Ce script privilégie les DOCX. Pour les PDF, utiliser un sous-agent avec `pypdf` + génération directe de ST.

## Statistiques

| Métrique | Valeur |
|----------|--------|
| Nombre de FDS | 5 (PDF) |
| Zones fonctionnelles | 1 (Extrusion) |
| Fichiers ST générés | 5 (972 lignes total) |
| Fichiers L5X (AOI + Routine) | 10 |
| Programme zone | 1 |
| Projet master | 1 (1 031 lignes, 36 Ko) |
| Taille totale | 208 Ko |
| CDATA | 100% |

*Documenté le 2026-07-06 — Session projet ROH.*