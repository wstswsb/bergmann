from typing import Final, Self

from bergmann.convention import DB_ALG_BYTES, DB_ITERATIONS_BYTES, DB_MAGIC_BYTES
from bergmann.entities.header import Header
from bergmann.key import KeyMeta


class StoreMeta:
    def __init__(self, salt: bytes):
        self.magic_bytes: Final[bytes] = DB_MAGIC_BYTES
        self.algorithm: Final[bytes] = DB_ALG_BYTES
        self.salt: Final[bytes] = salt
        self.iterations: Final[int] = int.from_bytes(DB_ITERATIONS_BYTES)

    @classmethod
    def from_header(cls, header: Header) -> Self:
        return cls(salt=header.salt_bytes)

    @property
    def key_meta(self) -> KeyMeta:
        return KeyMeta(self.salt, self.iterations)

    @property
    def iterations_bytes(self) -> bytes:
        return DB_ITERATIONS_BYTES
