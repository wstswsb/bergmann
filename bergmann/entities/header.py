from dataclasses import dataclass

from bergmann.common.exceptions import InvalidHeader
from bergmann.convention import (
    CONTENT_HASH_SIZE,
    DB_ALG_BYTES,
    DB_ITERATIONS_BYTES,
    DB_MAGIC_BYTES,
    DB_SALT_SIZE,
)


@dataclass(frozen=True, slots=True)
class Header:
    magic_bytes: bytes
    alg_bytes: bytes
    salt_bytes: bytes
    iterations_bytes: bytes
    content_hash: bytes

    def __post_init__(self):
        if self.magic_bytes != DB_MAGIC_BYTES:
            raise InvalidHeader(reason="magic-bytes")
        if self.alg_bytes != DB_ALG_BYTES:
            raise InvalidHeader(reason="alg")
        if len(self.salt_bytes) != DB_SALT_SIZE:
            raise InvalidHeader(reason="salt")
        if self.iterations_bytes != DB_ITERATIONS_BYTES:
            raise InvalidHeader(reason="iterations")
        if len(self.content_hash) != CONTENT_HASH_SIZE:
            raise InvalidHeader(reason="content-hash")

    def as_bytes(self):
        return b"".join(
            (
                self.magic_bytes,
                self.alg_bytes,
                self.salt_bytes,
                self.iterations_bytes,
                self.content_hash,
            )
        )

    @property
    def bytes_size_on_disk(self) -> int:
        return len(self.as_bytes())
