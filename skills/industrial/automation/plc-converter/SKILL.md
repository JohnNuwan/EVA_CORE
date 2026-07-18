---
name: plc-converter
description: "Convertir bidirectionnellement du code Structured Text (ST/SCL) entre Rockwell, Siemens et CODESYS avec gestion des types, temporisateurs et AOI."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - industrial
      - automation
      - plc
      - rockwell
      - siemens
      - codesys
      - conversion
      - structured-text
      - scl
      - l5x
      - plcopen-xml
    related_skills:
      - rockwell-studio5000
      - siemens-scl
      - automation-linter
      - plcopen-xml
      - multi-agent-orchestration
---

# Convertisseur Bidirectionnel de Code PLC

## Vue d'ensemble

Le convertisseur bidirectionnel de code automate (`plc-converter`) permet de traduire du code Structured Text (ST / SCL) ainsi que des structures de variables et d'Add-On Instructions (AOI) entre les trois principales plateformes d'automatisme industriel :

1. **Rockwell Automation (L5X / Logix Designer)** — Fichiers d'export .L5X contenant les routines, AOI, tags et configurations.
2. **Siemens TIA Portal (SCL)** — Blocs de code source au format SCL (Structured Control Language) avec gestion des DB, FC, FB et UDT.
3. **CODESYS / TwinCAT (PLCopen XML)** — Format d'échange universel XML selon la norme IEC 61131-3.

Cette compétence s'appuie sur le script wrapper [`plc_converter_wrapper.py`](scripts/plc_converter_wrapper.py) pour lancer les conversions de manière portable et traçable.

### Architecture du convertisseur

```
Fichier source                              Fichier cible
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Rockwell    │     │  Analyseur      │     │  Siemens     │
│  (.L5X)      │────▶│  Syntaxique     │────▶│  (.scl)      │
└──────────────┘     │  + Mappage      │     └──────────────┘
                     │  Types/timers   │
┌──────────────┐     │  + Réécriture   │     ┌──────────────┐
│  Siemens     │     │  sémantique     │     │  Rockwell    │
│  (.scl)      │────▶│                 │────▶│  (.L5X/.st)  │
└──────────────┘     └─────────────────┘     └──────────────┘
```

## Quand l'utiliser

### À utiliser lorsque l'utilisateur demande de :

- Convertir du code Structured Text Rockwell vers Siemens SCL (ou inversement).
- Exporter un fichier d'Add-On Instruction Rockwell (.L5X) en fichier source Siemens SCL.
- Traduire un export d'AOI Rockwell (.L5X) en format universel PLCopen XML (pour CODESYS/TwinCAT).
- Migrer un projet d'une plateforme d'automatisme à une autre.
- Standardiser des bibliothèques de code entre différents ateliers utilisant des automates hétérogènes.
- Générer des squelettes de code pour une plateforme cible à partir de spécifications existantes.

### Ne pas utiliser pour :

- L'édition directe de programmes PLC sans étape de conversion (utiliser les outils natifs : Rockwell Logix Designer, Siemens TIA Portal).
- La simulation ou l'exécution de code PLC (utiliser PLCSIM, FactoryIO ou un automate physique).
- La conversion de code ladder (LD) ou diagramme de blocs (FBD) — seuls le texte structuré (ST/SCL) et les structures XML sont supportés.
- La vérification de conformité aux normes de sécurité (utiliser `automation-linter` ou un outil dédié).

---

## 1. Exécution du Convertisseur en Ligne de Commande

Le convertisseur s'exécute via l'outil système [`terminal`] en appelant le script wrapper.

### 1.1 Rockwell (L5X) vers Siemens (SCL)

```bash
python skills/industrial/automation/plc-converter/scripts/plc_converter_wrapper.py \
    --input ./sources/MonAoi.L5X \
    --output ./cibles/MonAoi.scl \
    --from-format rockwell \
    --to-format siemens
```

### 1.2 Siemens (SCL) vers Rockwell (ST)

```bash
python skills/industrial/automation/plc-converter/scripts/plc_converter_wrapper.py \
    --input ./sources/MonBloc.scl \
    --output ./cibles/MonBloc.st \
    --from-format siemens \
    --to-format rockwell
```

### 1.3 Rockwell (L5X) vers PLCopen XML

```bash
python skills/industrial/automation/plc-converter/scripts/plc_converter_wrapper.py \
    --input ./sources/MonAoi.L5X \
    --output ./cibles/MonBloc.xml \
    --from-format rockwell \
    --to-format plcopen
```

### 1.4 Siemens (SCL) vers PLCopen XML

```bash
python skills/industrial/automation/plc-converter/scripts/plc_converter_wrapper.py \
    --input ./sources/MonBloc.scl \
    --output ./cibles/MonBloc.xml \
    --from-format siemens \
    --to-format plcopen
```

### Options avancées

| Option | Description |
| :--- | :--- |
| `--encoding` | Encodage du fichier source (défaut: utf-8) |
| `--preserve-comments` | Conserver les commentaires dans le code converti |
| `--flatten-structs` | Aplatir les structures de données complexes en types primitifs |
| `--aoi-name <nom>` | Nom spécifique de l'AOI à extraire (si plusieurs dans le L5X) |
| `--verbose` | Afficher les étapes de conversion et les avertissements |

---

## 2. Règles de Traduction et Correspondances

### 2.1 Variables locales et préfixes

- **Siemens SCL** exige le préfixe `#` pour désigner les variables locales et les paramètres de blocs (FC, FB).
- **Rockwell ST** n'utilise pas de préfixe ; les variables locales sont directement accessibles par leur nom.
- **CODESYS ST** suit la même convention que Siemens, avec `#` pour les variables locales.

Le convertisseur détecte automatiquement les variables de portée locale et ajoute ou supprime le préfixe `#` selon la direction de la conversion.

```pascal
// Siemens SCL (source)
FUNCTION MaFonction : Int
VAR_INPUT
    VitesseConsigne : Int;    // → #VitesseConsigne dans le corps
END_VAR
    #VitesseConsigne := #VitesseConsigne * 2;
END_FUNCTION

// Rockwell ST (cible)
FUNCTION MaFonction : Int
    VitesseConsigne := VitesseConsigne * 2;
END_FUNCTION
```

### 2.2 Gestion des temporisateurs (Timers TON/TOF/TP)

| Plateforme | Syntaxe timer TON | Bit de sortie |
| :--- | :--- | :--- |
| **Rockwell** | `Timer.PRE := 1000; Timer.TimerEnable := Cond; TON(Timer);` | `.DN` (Done) |
| **Siemens SCL** | `Timer(IN := Cond, PT := T#1000ms);` | `.Q` (Output) |
| **CODESYS** | `TON_Instance(IN := Cond, PT := T#1000ms);` | `.Q` (Output) |

#### Exemple de conversion automatique :

```pascal
// Rockwell (source)
MyTimer.PRE := 5000;
MyTimer.TimerEnable := StartSignal;
TON(MyTimer);
Alarm := MyTimer.DN;

// Siemens (cible)
MyTimer(IN := StartSignal, PT := T#5000ms);
Alarm := MyTimer.Q;
```

### 2.3 Correspondance des types de données

#### Types primitifs

| Rockwell | Siemens TIA Portal | CODESYS | Taille |
| :--- | :--- | :--- | :--- |
| **BOOL** | Bool | BOOL | 1 bit |
| **SINT** | SInt | SINT | 8 bits signé |
| **INT** | Int | INT | 16 bits signé |
| **DINT** | DInt | DINT | 32 bits signé |
| **LINT** | LInt | LINT | 64 bits signé |
| **REAL** | Real | REAL | 32 bits flottant |
| **LREAL** | LReal | LREAL | 64 bits flottant |
| **STRING** | String | STRING | Variable |

#### Types dérivés et structurés

| Rockwell | Siemens | Notes |
| :--- | :--- | :--- |
| **TIMER** | TON / TOF / TP | Instance de temporisateur |
| **COUNTER** | CTU / CTD / CTUD | Compteur (conversion en bloc fonctionnel) |
| **ARRAY[0..N]** | ARRAY[0..N] OF | Tableaux (indexation identique) |
| **USER_DEFINED** | UDT / Struct | Types structurés convertis en UDT |

### 2.4 Conversion des blocs fonctionnels

Les Add-On Instructions (AOI) Rockwell sont converties en FB (Function Blocks) Siemens avec leur interface complète :

| Élément AOI Rockwell | Équivalent Siemens |
| :--- | :--- |
| `Parameters.Input` | `VAR_INPUT` |
| `Parameters.Output` | `VAR_OUTPUT` |
| `Parameters.InOut` | `VAR_IN_OUT` |
| `LocalTags` | `VAR` |
| `Routine` (ST) | Corps du FB en SCL |

---

## 3. Validation Post-Conversion

### 3.1 Vérification syntaxique

Après conversion, valider la syntaxe du code généré :

```bash
# Vérification SCL (Siemens)
python skills/industrial/automation/plc-converter/scripts/validate_scl.py \
    --input ./cibles/MonBloc.scl

# Vérification L5X (Rockwell)
python tools/validate_l5x.py --input ./cibles/MonAoi.L5X
```

### 3.2 Tests de non-régression

```python
from skills.plc_converter.scripts import plc_converter_wrapper as conv

# Test : Conversion aller-retour
original = "./tests/fixtures/sample.L5X"
intermediate = "./tmp/sample.scl"
final = "./tmp/sample_roundtrip.L5X"

conv.convert(original, intermediate, "rockwell", "siemens")
conv.convert(intermediate, final, "siemens", "rockwell")

# Comparaison structurelle (hors métadonnées)
assert compare_structures(original, final, ignore=["date", "version"])
```

---

## 4. Automatisation par Lot

Pour convertir un répertoire entier de fichiers :

```bash
# Convertir tous les .L5X d'un dossier en .scl
for file in ./sources/*.L5X; do
    python skills/industrial/automation/plc-converter/scripts/plc_converter_wrapper.py \
        --input "$file" \
        --output "./cibles/$(basename "$file" .L5X).scl" \
        --from-format rockwell \
        --to-format siemens
done
```

> **Note :** Pour des volumes importants (>50 fichiers), utiliser l'orchestration multi-agents (compétence [`multi-agent-orchestration`](../multi-agent-orchestration/SKILL.md)) pour paralléliser les conversions.

---

## 5. Traitement des Cas Particuliers

### 5.1 Instructions non convertibles

Certaines instructions spécifiques à une plateforme n'ont pas d'équivalent direct :

| Instruction Rockwell | Comportement |
| :--- | :--- |
| `MCR` (Master Control Relay) | Génère un avertissement ; nécessite une réécriture manuelle |
| `JMP` / `LBL` | Converti en `GOTO` Siemens si présent |
| `GSV` / `SSV` (Get/Set System Value) | Non convertible ; signalé comme avertissement |
| `MSG` (Message Instruction) | Non convertible ; nécessite une adaptation manuelle |

### 5.2 Gestion des commentaires

Les commentaires structurés (ex: `(* ... *)`) sont conservés par défaut. Utiliser `--no-preserve-comments` pour les supprimer du fichier de sortie.

### 5.3 Encodage et caractères spéciaux

Les fichiers SCL Siemens utilisent généralement l'encodage UTF-8 avec BOM. Les fichiers L5X Rockwell sont en UTF-8. Le convertisseur détecte et normalise automatiquement l'encodage.

---

## Pièges Courants (Common Pitfalls)

1. **Préfixe `#` manquant en SCL** : Si la conversion Siemens → Rockwell échoue avec des références non résolues, vérifier que le préfixe `#` a été correctement retiré des variables locales.

2. **Temporisateurs avec valeurs PT non standard** : Les valeurs `T#1000ms` (Siemens) et `10000` (Rockwell, en millisecondes) peuvent différer d'un facteur 10. Vérifier la correspondance des échelles de temps.

3. **AOI avec Logique Ladder** : Le convertisseur ne traite que le code Structured Text. Une AOI contenant des routines Ladder (LD) ou SFC sera partiellement convertie, avec un avertissement.

4. **Types UDT imbriqués** : Les structures de données complexes avec des UDT imbriqués peuvent nécessiter un aplatissement manuel (`--flatten-structs`).

5. **Métadonnées perdues** : Les informations de sécurité (accès, protection) et les annotations spécifiques à la plateforme ne sont pas conservées. Documenter ces éléments séparément.

6. **Différences de casse** : Rockwell est insensible à la casse, Siemens est sensible. Le convertisseur normalise en `PascalCase` pour éviter les conflits.

---

## Liste de vérification (Checklist)

- [ ] L'exécution s'effectue via le wrapper `plc_converter_wrapper.py` avec les bons arguments `--from-format` et `--to-format`.
- [ ] Les blocs de code Structured Text générés respectent la syntaxe de la plateforme cible (préfixes `#`, types, etc.).
- [ ] Les temporisateurs (timers) convertis ont fait l'objet d'une validation fonctionnelle (TON/TOF/TP).
- [ ] Les types de données ont été convertis conformément au tableau de correspondance.
- [ ] Les instructions spécifiques non convertibles sont signalées par un avertissement explicite.
- [ ] Les fichiers de sortie sont syntaxiquement valides (validation avec outil externe si disponible).
- [ ] Les commentaires et annotations sont préservés si `--preserve-comments` est actif.
- [ ] Les préfixes `#` sont correctement ajoutés ou retirés selon la direction de conversion.
- [ ] Les métadonnées critiques (sécurité, validation) sont documentées hors du fichier converti.
- [ ] Un test de non-régression (aller-retour) a été effectué sur un échantillon représentatif.

