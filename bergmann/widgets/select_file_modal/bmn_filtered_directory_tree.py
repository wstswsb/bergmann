import logging
from pathlib import Path
from typing import Iterable

from textual.widgets import DirectoryTree


class BmnFilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        for path in paths:
            try:
                if self._is_bmn_file(path) or self._is_not_empty_dir(path):
                    yield path
            except PermissionError:
                logging.debug(f"permission error for {path}")

    def _is_not_empty_dir(self, path: Path) -> bool:
        if not path.is_dir():
            return False
        return bool(list(path.iterdir()))

    def _is_bmn_file(self, path: Path) -> bool:
        if not path.is_file():
            return False
        return path.name.endswith(".bmn")
