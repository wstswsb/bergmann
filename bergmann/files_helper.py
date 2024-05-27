from pathlib import Path


class FilesHelper:
    def is_emtpy(self, path: Path) -> bool:
        return path.stat().st_size == 0
