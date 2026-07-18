---
name: EVA-agent-skill-authoring
description: "Rédiger une compétence (SKILL.md) dans le dépôt."
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [skills, authoring, EVA-agent, conventions, skill-md]
    related_skills: [plan, requesting-code-review]
---

# Création de Compétences pour l'Agent EVA (dans le dépôt)

## Vue d'ensemble

Le fichier de compétence `SKILL.md` peut résider à deux emplacements distincts :

1. **Local utilisateur :** `~/.EVA/skills/<categorie>/<nom>/SKILL.md` — personnel, non partagé. Il se crée via `skill_manage(action='create')`.
2. **Dans le dépôt (concerne cette compétence) :** `skills/<categorie>/<nom>/SKILL.md` — versionné sous Git et distribué avec le paquet. Utilisez `write_file` puis `git add`. L'outil `skill_manage(action='create')` ne cible pas cette arborescence.

## Quand l'utiliser

- L'utilisateur vous demande d'ajouter une compétence « dans cette branche / ce dépôt / ce commit ».
- Vous enregistrez un flux de travail (workflow) réutilisable destiné à être distribué avec l'agent EVA.
- Vous modifiez une compétence existante sous `skills/` (utilisez un patch pour les corrections mineures, et `write_file` pour une réécriture complète ; `skill_manage` fonctionne pour modifier une compétence du dépôt, mais pas pour la créer).

## En-tête YAML (Frontmatter) Requis

La source de vérité se trouve dans `tools/skill_manager_tool.py::_validate_frontmatter`. Les contraintes obligatoires sont :

- Débuter par `---` dès les premiers octets (pas de ligne vide initiale).
- Se terminer par `\n---\n` juste avant le corps du document.
- Être analysable comme un dictionnaire YAML.
- Présence du champ `name`.
- Présence du champ `description`, d'une longueur maximale de **1024 caractères** (`MAX_DESCRIPTION_LENGTH`).
- Corps du document non vide après le `---` de fermeture.

Modèle de structure partagé par l'ensemble des compétences sous `skills/software-development/` :

```yaml
---
name: nom-de-ma-competence         # minuscules, tirets, ≤ 64 caractères (MAX_NAME_LENGTH)
description: Use when <declencheur>. <comportement en une ligne>.
version: 1.0.0
author: EVA Agent
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [mots, cles, descriptifs]
    related_skills: [autre-competence, encore-une-autre]
---
```

Les champs `version`, `author`, `license` et `metadata` ne sont pas imposés par le validateur, mais toutes les compétences existantes les intègrent. Ne pas les inclure rendrait la compétence incomplète par rapport aux autres.

## Limites de Taille

- Description : ≤ 1024 caractères (obligatoire).
- Fichier complet `SKILL.md` : ≤ 100 000 caractères (limite fixée par `MAX_SKILL_CONTENT_CHARS`, soit environ 36k tokens).
- Les compétences standards de `software-development/` comptent généralement entre **8 000 et 14 000 caractères**. C'est la taille idéale. Si vous dépassez 20 000 caractères, divisez le contenu en créant des fichiers sous `references/*.md` et pointez vers eux depuis le fichier `SKILL.md`.

## Structure Standard d'une Compétence

Toute compétence intégrée au dépôt doit respecter la structure suivante :

### Ajout d'enseignement clé détecté
- Lorsqu'un environnement Python activé n'offre pas les modules nécessaires (`ModuleNotFoundError`), toujours vérifier:
  1. Si le module est installé dans l'environnement correct (`pip show` via terminal);
  2. D'exécuter votre script depuis l'environnement approprié directement (`source activate && python script.py`).

```
# <Titre de la Compétence>

## Vue d'ensemble
Un ou deux paragraphes : quoi et pourquoi.

## Quand l'utiliser
- Liste à puces des cas d'usage (déclencheurs).
- Section « À proscrire pour : » (cas non applicables).

## <Sections thématiques spécifiques à la compétence>
- Tableaux de référence rapide.
- Blocs de code contenant les commandes exactes.
- Recettes spécifiques à EVA (tests via scripts/run_tests.sh, chemins ui-tui, etc.).

## Pièges Courants (Common Pitfalls)
Liste numérotée des erreurs fréquentes et de leurs corrections.

## Liste de vérification (Checklist)
- [ ] Liste à puces de vérifications post-action.

## Recettes Clés en Main (facultatif)
Scénarios nommés suivis de séquences de commandes concrètes.
```

Toutes les sections ne sont pas strictement obligatoires, mais le minimum requis pour garantir l'homogénéité comprend : `Vue d'ensemble`, `Quand l'utiliser`, le corps d'instructions concrètes et les `Pièges Courants (Common Pitfalls)`.

## Emplacement dans l'Arborescence

```
skills/<categorie>/<nom-de-la-competence>/SKILL.md
```

Catégories actuellement présentes dans le dépôt (à confirmer via `ls skills/`) : `autonomous-ai-agents`, `creative`, `data-science`, `devops`, `dogfood`, `email`, `gaming`, `github`, `leisure`, `mcp`, `media`, `mlops/*`, `note-taking`, `productivity`, `red-teaming`, `research`, `smart-home`, `social-media`, `software-development`.

Sélectionnez la catégorie existante la plus proche. Évitez de créer de nouvelles catégories de premier niveau sans nécessité absolue.

## Processus de Travail (Workflow)

1. **Étudier les compétences existantes** dans la catégorie cible :
   ```
   ls skills/<categorie>/
   ```
   Lisez 2 ou 3 fichiers `SKILL.md` pour vous imprégner du ton et de la structure.
2. **Vérifier les contraintes du validateur** dans `tools/skill_manager_tool.py` en cas de doute.
3. **Rédiger** la compétence avec `write_file` sous `skills/<categorie>/<nom>/SKILL.md`.
4. **Valider localement** :
   ```python
   import yaml, re, pathlib
   content = pathlib.Path("skills/<categorie>/<nom>/SKILL.md").read_text()
   assert content.startswith("---")
   m = re.search(r'\n---\s*\n', content[3:])
   fm = yaml.safe_load(content[3:m.start()+3])
   assert "name" in fm and "description" in fm
   assert len(fm["description"]) <= 1024
   assert len(content) <= 100_000
   ```
5. **Ajouter au suivi Git et commiter** sur la branche active.
6. **Remarque :** le chargeur de compétences de la session active met son état en cache. Les commandes `skill_view` ou `skills_list` ne détecteront la nouvelle compétence qu'à la session suivante. C'est le comportement attendu.

## Références Croisées entre Compétences

La section `metadata.EVA.related_skills` regroupe les compétences des deux répertoires (celui du dépôt `skills/` et celui de l'utilisateur `~/.EVA/skills/`) lors du chargement. Vous pouvez faire référence à une compétence locale à l'utilisateur depuis une compétence du dépôt, mais celle-ci ne se résoudra pas pour les autres développeurs clonant le projet. Privilégiez les références vers d'autres compétences du dépôt. Si une compétence fréquemment référencée n'existe que dans `~/.EVA/skills/`, envisagez de la déplacer dans le dépôt.

## Modification de Compétences Existantes du Dépôt

- **Correction mineure (coquille, ajout d'un piège courant, affinement d'un déclencheur) :** L'utilisation de `skill_manage(action='patch', name=..., old_string=..., new_string=...)` convient pour modifier les compétences du dépôt.
- **Réécriture majeure :** Réécrivez l'intégralité du fichier `SKILL.md` avec `write_file`. L'action `skill_manage(action='edit')` fonctionne également mais nécessite de passer la totalité du nouveau contenu en paramètre.
- **Ajout de fichiers de support :** Enregistrez vos fichiers à l'aide de `write_file` sous `skills/<categorie>/<nom>/references/<fichier>.md`, `templates/<fichier>` ou `scripts/<fichier>`. L'outil `skill_manage(action='write_file')` est également utilisable et applique la liste d'autorisation des sous-dossiers.
- **Committer devez toujours vos modifications** — les compétences intégrées au dépôt font partie du code source et ne sont pas des états de session.

## Pièges Courants (Common Pitfalls)

1. **Utiliser `skill_manage(action='create')` pour une compétence du dépôt.** Cela écrit dans le répertoire utilisateur `~/.EVA/skills/` au lieu du dépôt. Utilisez `write_file` pour créer une compétence dans le dépôt.

2. **Présence d'espaces avant `---`.** Le validateur vérifie `content.startswith("---")` ; toute ligne vide ou caractère BOM en tout début de fichier invalidera la compétence.

3. **Description trop générique.** Les descriptions doivent débuter par « Use when ... » (ou son équivalent traduit) et décrire la *classe de déclenchement* plutôt qu'une tâche isolée. Préférez « Use when debugging X » à « Debug X ».

4. **Omission du bloc author/license/metadata.** Bien que non bloquant pour le validateur, ce bloc est présent sur toutes les autres compétences et son absence donne une impression d'inachevé.

5. **Créer une compétence qui duplique une compétence existante.** Avant de créer, inspectez `ls skills/<categorie>/` et lisez quelques fichiers. Privilégiez l'enrichissement d'une compétence existante plutôt que la création d'une déclinaison trop proche.

6. **S'attendre à ce que la session actuelle de l'agent détecte la nouvelle compétence.** La configuration est lue au démarrage de la session. Vérifiez la compétence dans une nouvelle session ou accédez directement au fichier par son chemin.

7. **Lier des compétences inexistantes dans le dépôt.** Renseigner `related_skills: [ma-competence-locale]` fonctionne sur votre poste mais échouera ailleurs. Privilégiez les liens vers des compétences du dépôt.

## Liste de vérification (Checklist)

- [ ] Le fichier est situé sous `skills/<categorie>/<nom>/SKILL.md` (et non dans `~/.EVA/skills/`).
- [ ] L'en-tête commence au premier octet par `---` et se ferme par `\n---\n`.
- [ ] Les champs `name`, `description`, `version`, `author`, `license` et `metadata.EVA.{tags, related_skills}` sont tous définis.
- [ ] Le nom fait au maximum 64 caractères, en minuscules avec des tirets.
- [ ] La description fait au maximum 1024 caractères et débute par « Use when ... ».
- [ ] La taille totale du fichier est inférieure à 100 000 caractères (idéalement entre 8 000 et 15 000).
- [ ] La structure respecte le schéma : `# Titre` → `## Vue d'ensemble` → `## Quand l'utiliser` → Corps de texte → `## Pièges Courants (Common Pitfalls)` → `## Liste de vérification (Checklist)`.
- [ ] Les liens de `related_skills` pointent vers des compétences existantes du dépôt.
- [ ] La commande `git add skills/<categorie>/<nom>/ && git commit` a été exécutée sur la bonne branche.

