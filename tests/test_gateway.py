import hashlib
from pathlib import Path

from bergmann.convention import (
    CONTENT_HASH_SIZE,
    DB_ALG_BYTES,
    DB_ITERATIONS_BYTES,
    DB_MAGIC_BYTES,
    DB_SALT_SIZE,
)
from bergmann.di import di
from bergmann.entities.item import Item


def test_init_new_store(tmp_path: Path) -> None:
    # Arrange
    sut = di.gateway
    db_path = tmp_path / "db.bmn"
    password = "test-password"

    # Act
    sut.init_new_store(db_path, password)

    # Assert
    cypher_impl = di.passwords_interactor.cypher_impl
    db_bytes = db_path.read_bytes()
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
    assert magic_bytes == DB_MAGIC_BYTES
    assert alg_bytes == DB_ALG_BYTES
    assert salt_bytes == cypher_impl.key_meta.salt
    assert iteration_bytes == DB_ITERATIONS_BYTES

    offset += CONTENT_HASH_SIZE
    content_bytes = db_bytes[offset:]
    decrypted_content = cypher_impl.decrypt(content_bytes)
    expected_content_hash = hashlib.sha256(decrypted_content).digest()
    assert content_hash == expected_content_hash


def test_load_existent_store(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    sut = di.gateway
    sut.init_new_store(db_path, "test-password")

    # Act
    result = sut.load_existent_store(db_path, "test-password")

    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    item = result[0]
    assert isinstance(item, Item)
    assert item.description.startswith("site: vk.com")
    assert item.login.startswith("example login")
    assert item.password.startswith("example password")


def test_update(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    sut = di.gateway
    items = sut.init_new_store(db_path, "test-password")
    items.append(Item.example())

    # Act
    sut.update(db_path, items)

    # assert
    loaded_items = sut.load_existent_store(db_path, "test-password")
    assert len(loaded_items) == 2
