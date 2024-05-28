import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from bergmann.entities.db_meta import DBMeta


@dataclass(slots=True, frozen=True)
class KeyMeta:
    salt: bytes = field(default=os.urandom(16))
    iterations: int = field(default=150_000)
    hash_function: str = field(default="sha256", init=False)

    @classmethod
    def from_db_meta(cls, db_meta: "DBMeta") -> Self:
        return cls(salt=db_meta.salt, iterations=db_meta.iterations)


@dataclass(slots=True)
class Key:
    binary: bytes = field(repr=False)
    meta: KeyMeta
