# -*- coding: utf-8 -*-
"""Module de gestion de sandbox de workspace.

Permet de créer un environnement de travail temporaire isolé pour les sous-agents
et d'appliquer ou d'annuler les modifications apportées à la fin de leur exécution.
"""

import hashlib
import logging
import os
import shutil
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def make_long_path(path: Path) -> Path:
    """Ajoute le préfixe Windows long path si nécessaire.

    Args:
        path: Le chemin d'accès d'origine sous forme de Path.

    Returns:
        Path: Le chemin d'accès converti avec le préfixe long path Windows.
    """
    p_str = str(path.resolve())
    if os.name == "nt" and not p_str.startswith("\\\\?\\"):
        if p_str.startswith("\\\\"):
            return Path("\\\\?\\UNC\\" + p_str[2:])
        else:
            return Path("\\\\?\\" + p_str)
    return Path(p_str)


class WorkspaceSandbox:
    """Classe gérant le cycle de vie d'une sandbox de workspace isolée.

    Copie les fichiers du projet en excluant les dossiers lourds ou système,
    détecte les modifications apportées, et permet de les fusionner ou de les annuler.
    """

    def __init__(self, workspace_root: Path, sandbox_id: str, helios_home: Path):
        """Initialise la configuration de la sandbox.

        Args:
            workspace_root: Répertoire racine du projet d'origine.
            sandbox_id: Identifiant unique du sous-agent.
            helios_home: Répertoire de configuration de Helios.
        """
        self.workspace_root = make_long_path(Path(workspace_root))
        self.sandbox_id = sandbox_id
        self.sandbox_root = make_long_path(helios_home / "tmp" / "workspaces" / sandbox_id)
        self.ignored_dirs = {
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".gemini",
            "__pycache__",
            "build",
            "dist",
            ".idea",
            ".vscode",
            "projects",
            "brain",
            "logs",
            "artifacts",
        }

    def _should_ignore(self, path: Path) -> bool:
        """Détermine si un chemin fait partie des répertoires ignorés.

        Args:
            path: Chemin relatif ou absolu à tester.

        Returns:
            bool: True si le chemin doit être ignoré, False sinon.
        """
        for part in path.parts:
            if part in self.ignored_dirs:
                return True
        return False

    def create(self) -> Path:
        """Crée le dossier de sandbox et y copie les fichiers du workspace.

        Returns:
            Path: Le chemin absolu du répertoire racine de la sandbox.
        """
        if self.sandbox_root.exists():
            shutil.rmtree(self.sandbox_root, ignore_errors=True)
        self.sandbox_root.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Création de la sandbox isolée %s dans %s",
            self.sandbox_id,
            self.sandbox_root,
        )

        for root, dirs, files in os.walk(self.workspace_root):
            root_path = Path(root)
            rel_path = root_path.relative_to(self.workspace_root)

            if self._should_ignore(rel_path):
                continue

            # Filtrage en place pour éviter de parcourir les sous-dossiers ignorés
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]

            target_dir = self.sandbox_root / rel_path
            target_dir.mkdir(parents=True, exist_ok=True)

            for file in files:
                src_file = root_path / file
                dest_file = target_dir / file
                try:
                    shutil.copy2(src_file, dest_file)
                except Exception as e:
                    logger.warning(
                        "Impossible de copier %s dans la sandbox : %s",
                        src_file,
                        e,
                    )

        return self.sandbox_root

    def rollback(self) -> None:
        """Supprime le dossier temporaire de la sandbox pour annuler les modifications."""
        if self.sandbox_root.exists():
            shutil.rmtree(self.sandbox_root, ignore_errors=True)
            logger.info(
                "Sandbox %s nettoyée et modifications annulées (rollback).",
                self.sandbox_id,
            )

    def merge(self) -> List[Path]:
        """Fusionne les modifications de la sandbox vers le workspace d'origine.

        Returns:
            List[Path]: Liste des chemins de fichiers modifiés, créés ou supprimés.
        """
        changes = []
        if not self.sandbox_root.exists():
            return changes

        logger.info(
            "Fusion des modifications de la sandbox %s vers le projet principal",
            self.sandbox_id,
        )

        # 1. Détecter et copier les fichiers modifiés ou créés
        for root, dirs, files in os.walk(self.sandbox_root):
            root_path = Path(root)
            rel_path = root_path.relative_to(self.sandbox_root)

            workspace_dir = self.workspace_root / rel_path
            workspace_dir.mkdir(parents=True, exist_ok=True)

            for file in files:
                sandbox_file = root_path / file
                workspace_file = workspace_dir / file

                needs_copy = False
                if not workspace_file.exists():
                    needs_copy = True
                else:
                    try:
                        with open(sandbox_file, "rb") as f1, open(
                            workspace_file, "rb"
                        ) as f2:
                            if (
                                hashlib.md5(f1.read()).digest()
                                != hashlib.md5(f2.read()).digest()
                            ):
                                needs_copy = True
                    except Exception:
                        needs_copy = True

                if needs_copy:
                    try:
                        shutil.copy2(sandbox_file, workspace_file)
                        changes.append(workspace_file)
                    except Exception as e:
                        logger.error(
                            "Échec de la fusion de %s vers le workspace : %s",
                            sandbox_file,
                            e,
                        )

        # 2. Détecter et supprimer les fichiers effacés dans la sandbox
        for root, dirs, files in os.walk(self.workspace_root):
            root_path = Path(root)
            rel_path = root_path.relative_to(self.workspace_root)

            if self._should_ignore(rel_path):
                continue

            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]

            for file in files:
                workspace_file = root_path / file
                sandbox_file = self.sandbox_root / rel_path / file

                if not sandbox_file.exists():
                    try:
                        workspace_file.unlink()
                        changes.append(workspace_file)
                    except Exception as e:
                        logger.error(
                            "Échec de la suppression de %s lors de la fusion : %s",
                            workspace_file,
                            e,
                        )

        self.rollback()
        return changes
