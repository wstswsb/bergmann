from dataclasses import dataclass, field
from typing import Final, Self

from bergmann.convention import PASSWORDS_HASH_FUNCTION
from bergmann.entities.header import Header


class KeyMeta:
    def __init__(self, salt: bytes, iterations: int):
        self.salt: Final[bytes] = salt
        self.iterations: Final[int] = iterations
        self.hash_function: Final[str] = PASSWORDS_HASH_FUNCTION

    @classmethod
    def from_header(cls, header: Header) -> Self:
        return cls(
            salt=header.salt_bytes,
            iterations=int.from_bytes(header.iterations_bytes),
        )


@dataclass(slots=True)
class Key:
    binary: bytes = field(repr=False)
    meta: KeyMeta
