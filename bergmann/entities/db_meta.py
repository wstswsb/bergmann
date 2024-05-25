from dataclasses import dataclass, field
from typing import Self

from bergmann.key import KeyMeta


@dataclass(slots=True)
class DBMeta:
    magic_bytes: bytes = field(default=b"68210121", init=False)
    algorithm: bytes = field(default=b"KUZ", init=False)
    salt: bytes = field(kw_only=True)
    iterations: int = field(kw_only=True)
    content_hash: bytes = field(default=b"", init=False)

    @classmethod
    def from_key_meta(cls, key_meta: KeyMeta) -> Self:
        return cls(salt=key_meta.salt, iterations=key_meta.iterations)
