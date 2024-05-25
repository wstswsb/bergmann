import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self


@dataclass(frozen=True, slots=True)
class ContentItem:
    login: str
    password: str

    @classmethod
    def default(cls) -> Self:
        return cls("ivan-login", "ivan-password")


@dataclass
class DBTemplate:
    MAGIC_BYTES: bytes = b"10.12.2001"
    ALGORITHM: bytes = b"KUZ"
    SALT: bytes = os.urandom(16)
    ITERATIONS: int = 200_000
    CONTENT_HASH: bytes = field(init=False)
    CONTENT: bytes = field(init=False)


class FileDBHelper:
    def is_emtpy(self, path: Path) -> bool:
        return path.stat().st_size == 0
