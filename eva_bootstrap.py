import os
import sys

# Bootstrapper pour insérer le dossier 'eva_core' dans le Python path.
# Cela permet de ranger tous les fichiers .py applicatifs dans 'eva_core'
# sans casser leurs imports croisés dans le reste du codebase.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EVA_CORE_DIR = os.path.join(ROOT_DIR, "eva_core")
if EVA_CORE_DIR not in sys.path:
    sys.path.insert(0, EVA_CORE_DIR)
