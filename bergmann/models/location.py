from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Self


@dataclass(frozen=True, slots=True, match_args=True)
class Location:
    type: Literal["FS", "WEB"]
    value: str

    @classmethod
    def path(cls, value: Path | str) -> Self:
        return cls("FS", str(value))
