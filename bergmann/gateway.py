from pathlib import Path

from bergmann.files_helper import FilesHelper


class Gateway:
    def __init__(self, files_helper: FilesHelper):
        self._files_helper = files_helper

    def is_file_empty(self, path: Path) -> bool:
        return self._files_helper.is_emtpy(path)
