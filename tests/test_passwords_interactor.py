import hashlib
import json
from pathlib import Path

from bergmann.convention import (
    CONTENT_HASH_SIZE,
    DB_ALG_BYTES,
    DB_ITERATIONS_BYTES,
    DB_MAGIC_BYTES,
    DB_SALT_SIZE,
)
from bergmann.passwords_interactor import PasswordsInteractor


def test_initialize_new_db(tmp_path: Path) -> None:
    # Arrange
    new_db_path = Path("new-db.bmn")
    password = "test-user-password"
    sut = PasswordsInteractor()
    sut.initialize_key(password)

    # Act
    sut.initialize_new_db(new_db_path)

    # Assert
    db_bytes = new_db_path.read_bytes()
    assert db_bytes != b""
    magic_bytes = db_bytes[: len(DB_MAGIC_BYTES)]
    offset = len(DB_MAGIC_BYTES)
    alg_bytes = db_bytes[offset : offset + len(DB_ALG_BYTES)]
    offset += len(DB_ALG_BYTES)
    salt_bytes = db_bytes[offset : offset + DB_SALT_SIZE]
    offset += DB_SALT_SIZE
    iteration_bytes = db_bytes[offset : offset + len(DB_ITERATIONS_BYTES)]
    offset += len(DB_ITERATIONS_BYTES)
    content_hash = db_bytes[offset : offset + CONTENT_HASH_SIZE]
    offset += CONTENT_HASH_SIZE
    content_bytes = db_bytes[offset:]
    encrypted_content = json.loads(content_bytes)
    encrypted_item = encrypted_content[0]
    decrypted_item = [
        sut.cypher_impl.decrypt(bytes.fromhex(encrypted_item[0])).decode("utf8"),
        sut.cypher_impl.decrypt(bytes.fromhex(encrypted_item[1])).decode("utf8"),
        sut.cypher_impl.decrypt(bytes.fromhex(encrypted_item[2])).decode("utf8"),
    ]
    content = [decrypted_item]
    plain_string = json.dumps(content).encode("utf8")
    expected_content_hash = hashlib.sha256(plain_string).digest()
    assert magic_bytes == DB_MAGIC_BYTES
    assert alg_bytes == DB_ALG_BYTES
    assert salt_bytes == sut.cypher_impl.key_meta.salt
    assert iteration_bytes == DB_ITERATIONS_BYTES
    assert content_hash == expected_content_hash


def test_load_db(tmp_path: Path) -> None:
    # Arrange
    pass
