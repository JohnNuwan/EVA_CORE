#!/usr/bin/env python3
"""
Validation du frontmatter YAML des SKILL.md.
Vérifie : name, description, tags (liste)
Usage : python3 validate-skill-frontmatter.py [chemin/]
Retourne : code 0 si tout OK, 1 sinon
"""
import os
import sys
import yaml

def validate_skill(filepath):
    """Valide un fichier SKILL.md et retourne (ok, raison)"""
    dirname = os.path.basename(os.path.dirname(filepath))
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"[LECTURE] {dirname} : {e}"

    # Extraire le frontmatter entre les deux ---
    if not content.startswith('---'):
        return False, f"[ABSENT] {dirname} : pas de frontmatter (doit commencer par ---)"

    # Trouver le second ---
    end_idx = content.find('---', 3)
    if end_idx == -1:
        return False, f"[INCOMPLET] {dirname} : second --- introuvable"

    frontmatter = content[3:end_idx].strip()

    if not frontmatter:
        return False, f"[VIDE] {dirname} : frontmatter vide"

    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as e:
        return False, f"[YAML] {dirname} : {e}"

    if not isinstance(data, dict):
        return False, f"[TYPE] {dirname} : frontmatter n'est pas un dictionnaire"

    # Vérifier les champs requis
    required = {'name', 'description', 'tags'}
    missing = required - set(data.keys())
    if missing:
        return False, f"[CHAMPS] {dirname} : champs manquants {missing}"

    # Vérifier que tags est une liste
    if not isinstance(data.get('tags'), list):
        return False, f"[TAGS] {dirname} : 'tags' doit être une liste, pas {type(data.get('tags')).__name__}"

    # Vérifier que name est une chaîne non vide
    if not isinstance(data.get('name'), str) or not data['name'].strip():
        return False, f"[NAME] {dirname} : 'name' doit être une chaîne non vide"

    return True, f"[OK] {dirname}"


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    errors = 0
    total = 0

    for dirpath, _, filenames in os.walk(root):
        if 'SKILL.md' in filenames:
            filepath = os.path.join(dirpath, 'SKILL.md')
            total += 1
            ok, msg = validate_skill(filepath)
            print(f"  {msg}")
            if not ok:
                errors += 1

    print(f"\n---")
    print(f"Résultat : {total} SKILL.md vérifiés, {errors} erreurs")
    return 1 if errors > 0 else 0


if __name__ == '__main__':
    sys.exit(main())