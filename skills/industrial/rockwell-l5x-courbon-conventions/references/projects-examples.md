# Projets Réels — Exemples Conventions Courbon/Actemium

## ROH DevAssist — Royal Canin Lewisburg

**Projet :** P.0286989.H.01 — Ligne d'extrusion pet food
**CPU :** 1756-L83E v33
**FDS :** 54 (29 Extrusion + 25 Grinding)
**FCT :** 46

| Zone | Nb FCT | Plage |
|------|--------|-------|
| Extrusion + Coater + Dryer | 12 | FCT_01 à FCT_28 |
| Grinding Dosing + Process + Transfer | 21 | FCT_30 à FCT_61 |
| WWR + HWT + Cleaning + Supports | 13 | FCT_70 à FCT_111 |

**Tags typiques :** `IO_FCT`, `IO_RECIPE_EXTRU`, `L_EM_EXTRU_MAG`, `L_CURRENT_STEP`
**UDTs clés :** `UDT_EM_EXTRU_MAG`, `UDT_EM_COATING_COATER`, `UDT_EM_GRIND_GRINDER`

## RGY — Gimje Recycling/Plastics

**CPU :** 1756-L83E v33
**FCT :** 54

| Zone | Nb FCT | Plage |
|------|--------|-------|
| General (Supervision, Calibration, Agitation) | 10 | FCT_01 à FCT_10 |
| Reception (Liquid, Macro, Skid, BigBag) | 8 | FCT_11 à FCT_18 |
| Grinding (Grinder, Dosing, Mixer, Transfer) | 20 | FCT_19 à FCT_39 |
| Extrusion + Packaging + Interface + Utility | 16 | FCT_40 à FCT_54 |

## Siemens SCL équivalent

Les conventions logiques sont identiques en Siemens SCL :
- `FCT_XX` → `FB_XX`
- `UDT_EM_XXX` → `TYPE "UDT_EM_XXX"`
- `CASE L_Step` step sequencer (mêmes codes CMD/STS)
- Voir `output/ROH_DevAssite/siemens/fbs/` (46 FB) et `output/rockwell_gen/RGY_corrected/siemens/fbs/` (54 FB)