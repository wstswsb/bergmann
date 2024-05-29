from dataclasses import dataclass
from typing import Self

from bergmann.entities.item import Item


@dataclass(frozen=True, slots=True)
class LoadItemsResult:
    items: list[Item] | None
    new_db_initialized: bool

    @classmethod
    def new_store(cls, items: list[Item] | None) -> Self:
        return cls(items, new_db_initialized=True)

    @classmethod
    def existent_store(cls, items: list[Item] | None) -> Self:
        return cls(items, new_db_initialized=False)
