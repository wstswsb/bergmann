import os
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class KeyMeta:
    salt: bytes = field(default=os.urandom(16))
    iterations: int = field(default=150_000)
    hash_function: str = field(default="sha256", init=False)


@dataclass(slots=True)
class Key:
    binary: bytes = field(repr=False)
    meta: KeyMeta
