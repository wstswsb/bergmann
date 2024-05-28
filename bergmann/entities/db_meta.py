from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from bergmann.key import KeyMeta


@dataclass(frozen=True, slots=True)
class RawDBMeta:
    magic_bytes: bytes
    alg_bytes: bytes
    salt_bytes: bytes
    iterations_bytes: bytes
    content_hash: bytes


@dataclass(slots=True)
class DBMeta:
    magic_bytes: bytes = field(default=b"68210121", init=False)
    algorithm: bytes = field(default=b"KUZ", init=False)
    salt: bytes = field(kw_only=True)
    iterations: int = field(kw_only=True)
    content_hash: bytes = field(default=b"", init=False)

    @property
    def bytes_size_on_disk(self) -> int:
        iterations_byte_size = 4
        return sum(
            (
                len(self.magic_bytes),
                len(self.algorithm),
                len(self.salt),
                iterations_byte_size,
                len(self.content_hash),
            )
        )

    @classmethod
    def from_key_meta(cls, key_meta: "KeyMeta") -> Self:
        return cls(salt=key_meta.salt, iterations=key_meta.iterations)

    @classmethod
    def from_raw_db_meta(cls, raw_db_meta: RawDBMeta) -> Self:
        db_meta = cls(
            salt=raw_db_meta.salt_bytes,
            iterations=int.from_bytes(raw_db_meta.iterations_bytes),
        )
        db_meta.magic_bytes = raw_db_meta.magic_bytes
        db_meta.algorithm = raw_db_meta.alg_bytes
        db_meta.content_hash = raw_db_meta.content_hash
        return db_meta
