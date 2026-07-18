# Consolidation L5X après génération parallèle par sous-agents

## Contexte

Sur les projets multi-FDS (50+ fichiers, 5-10 zones), la génération Rockwell est déléguée à des sous-agents via `delegate_task`. Les sous-agents lisent les FDS, analysent les séquences, et génèrent du code Structured Text (`.st`) de bonne qualité. En revanche, les fichiers `.L5X` qu'ils produisent présentent des défauts structurels récurrents.

## Problèmes constatés

| Problème | Ratio observé | Impact |
|----------|---------------|--------|
| `<Content></Content>` vide | ~50% des fichiers | Import Studio 5000 impossible |
| Pas de CDATA | ~80% des fichiers | XML cassé par `<` et `>` du ST |
| Balises mal formées | ~20% des fichiers | Erreur de parsing XML |
| Noms avec tirets | Variable | Incompatible Rockwell 40 chars |

## Cause racine

Le script `scripts/generate_rockwell_from_fds.py` utilise `from agent.auxiliary_client import async_call_llm` — un import interne à Helios que les sous-agents n'ont pas dans leur namespace. Résultat : chaque sous-agent reconstruit sa propre logique de génération XML, sans standard.

## Piège : Normalisation des noms de fichiers (.st → .L5X)

Les fichiers `.st` générés par les sous-agents peuvent contenir des **tirets** dans leur nom (ex: `RGY-FDS-GRINDING-DOSING-F.st`), hérités du nom du FDS source. Or les noms de tags/instructions Rockwell doivent utiliser des **underscores** (limite 40 caractères, pas de tirets).

**Problème :** Si le script de consolidation normalise les tirets en underscores (`RGY_FDS_GRINDING_DOSING_F.st`), le nom du fichier L5X généré (`RGY_FDS_GRINDING_DOSING_F_AOI.L5X`) ne correspondra à aucun fichier `.st` existant — le fichier original s'appelle toujours `RGY-FDS-GRINDING-DOSING-F.st`.

**Symptôme :** Des fichiers L5X "orphelins" apparaissent — le script de validation les détecte comme "sans ST correspondant".

**Solution :** Le script de consolidation doit :
1. Lire les noms de fichiers `.st` réels (avec tirets)
2. Normaliser uniquement pour le nom de l'instruction Rockwell dans le XML (underscores)
3. Conserver le nom original du fichier `.st` pour la correspondance
4. Après consolidation, exécuter : `find . -name '*_AOI.L5X' -exec sh -c 'f={}; base=$(basename "$f" _AOI.L5X); [ -f "st/${base}.st" ] || echo "ORPHELIN: $f"' \;`

## Workflow de contournement

### Étape 1 : Sous-agents → .st uniquement
Déléguer aux sous-agents uniquement la génération des fichiers `.st`. Ajouter dans leur contexte :
```
"Ne génère que des fichiers .st. Ne génère PAS de fichiers L5X."
```

### Étape 2 : Post-traitement centralisé
Un seul script Python lit tous les `.st` et génère les L5X avec une structure cohérente :

```python
import os

def generate_aoi_l5x(name, st_code, version="33.00"):
    """Génère un L5X de type Add-On Instruction avec CDATA."""
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="{version}"
  TargetName="{name}" TargetType="AddOnInstructionDefinition">
  <AddOnInstructionDefinitions>
    <AddOnInstructionDefinition Name="{name}" Revision="1.0"
      ExecutePrescan="true" ExecutePostscan="false" ExecuteEnableInFalse="false">
      <Parameters>
        <Parameter Name="EnableIn" DataType="BOOL" Usage="Input" Required="true" Visible="true"/>
        <Parameter Name="EnableOut" DataType="BOOL" Usage="Output" Required="true" Visible="true"/>
      </Parameters>
      <Routines>
        <Routine Name="Logic" Type="StructuredText">
          <Content><![CDATA[
{st_code}
          ]]></Content>
        </Routine>
      </Routines>
    </AddOnInstructionDefinition>
  </AddOnInstructionDefinitions>
</RSLogix5000Content>'''

def generate_routine_l5x(name, st_code, version="33.00"):
    """Génère un L5X de type Routine avec CDATA."""
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RSLogix5000Content SchemaRevision="1.0" SoftwareRevision="{version}"
  TargetName="{name}" TargetType="Routine">
  <Routines>
    <Routine Name="{name}" Type="StructuredText">
      <Content><![CDATA[
{st_code}
      ]]></Content>
    </Routine>
  </Routines>
</RSLogix5000Content>'''
```

### Étape 3 : Assemblage du projet master
Pour chaque zone, créer un programme L5X qui référence toutes ses routines. Puis assembler le projet master avec :
- Les UDTs standards (moteurs TOR/VFD, vannes ON/OFF, capteurs analogiques)
- Les tags contrôleur (heartbeat, mode, production)
- Les 7 programmes de zone
- Les 54 routines

### Étape 4 : Validation

```bash
# 1. CDATA présent dans TOUS les L5X
grep -L 'CDATA' output/**/l5x/*.L5X   # Doit être vide

# 2. Aucun Content vide
grep -r '<Content/>' output/ --include="*.L5X"  # Doit être vide

# 3. Cohérence ST ↔ L5X
for f in output/*/st/*.st; do
    base=$(basename "$f" .st)
    [ -f "output/$(basename $(dirname $(dirname $f)))/l5x/${base}_AOI.L5X" ] \
        || echo "MANQUANT: ${base}_AOI.L5X"
done
```

## Exemple réel : Projet RGY

- 54 fichiers `.st` (7 zones)
- 108 fichiers L5X (54 AOI + 54 Routine)
- 7 programmes de zone
- 1 projet master
- Taille totale : ~2.6 Mo
- 100% CDATA, 0 Content vides

Voir le script de consolidation complet : `output/rockwell_gen/RGY/rgy_consolidate.py` (projet RGY réel).