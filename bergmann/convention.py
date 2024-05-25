from typing import Final

DB_MAGIC_BYTES: Final[bytes] = b"68210121"
DB_ALG_BYTES: Final[bytes] = b"KUZ"
DB_ITERATIONS_BYTES: Final[bytes] = (150_000).to_bytes(length=4)
DB_SALT_SIZE: Final[int] = 16
CONTENT_HASH_SIZE: Final[int] = 32
