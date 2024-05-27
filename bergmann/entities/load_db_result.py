from dataclasses import dataclass
from typing import Self

from bergmann.entities.item import Item


@dataclass(frozen=True, slots=True)
class LoadDBResult:
    content: list[Item] | None
    new_db_initialized: bool

    @classmethod
    def new_db(cls, content: list[Item] | None) -> Self:
        return cls(content, new_db_initialized=True)

    @classmethod
    def existent_db(cls, content: list[Item] | None) -> Self:
        return cls(content, new_db_initialized=False)
