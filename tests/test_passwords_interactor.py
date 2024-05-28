import hashlib
from pathlib import Path

import pytest

from bergmann.convention import (
    CONTENT_HASH_SIZE,
    DB_ALG_BYTES,
    DB_ITERATIONS_BYTES,
    DB_MAGIC_BYTES,
    DB_SALT_SIZE,
)
from bergmann.entities.item import Item
from bergmann.passwords_interactor import InvalidHeader, PasswordsInteractor


def test_initialize_new_db(tmp_path: Path) -> None:
    # Arrange
    new_db_path = tmp_path / "new.bmn"
    password = "test-user-password"
    sut = PasswordsInteractor()
    sut.initialize_key_for_new_db(password)

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
    decrypted_content = sut.cypher_impl.decrypt(content_bytes)
    expected_content_hash = hashlib.sha256(decrypted_content).digest()
    assert magic_bytes == DB_MAGIC_BYTES
    assert alg_bytes == DB_ALG_BYTES
    assert salt_bytes == sut.cypher_impl.key_meta.salt
    assert iteration_bytes == DB_ITERATIONS_BYTES
    assert content_hash == expected_content_hash


def test_check_header__invalid_magic_bytes(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(b"invalid-bytes")

    sut = PasswordsInteractor()

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.check_header(db_path)

    assert e.value.reason == "magic-bytes"


def test_check_header__invalid_alg_bytes(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(DB_MAGIC_BYTES + b"invalid-alg-bytes")

    sut = PasswordsInteractor()

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.check_header(db_path)

    assert e.value.reason == "alg"


def test_check_header__invalid_salt_size(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(DB_MAGIC_BYTES + DB_ALG_BYTES + b"short-salt")

    sut = PasswordsInteractor()

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.check_header(db_path)

    assert e.value.reason == "salt"


def test_check_header__invalid_iteration_bytes(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(
        b"".join(
            (
                DB_MAGIC_BYTES,
                DB_ALG_BYTES,
                b"s" * DB_SALT_SIZE,
                b"////",
            )
        )
    )

    sut = PasswordsInteractor()

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.check_header(db_path)

    assert e.value.reason == "iterations"


def test_check_header__invalid_content_hash_size(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(
        b"".join(
            (
                DB_MAGIC_BYTES,
                DB_ALG_BYTES,
                b"s" * DB_SALT_SIZE,
                DB_ITERATIONS_BYTES,
                b"short-hash",
            )
        )
    )
    sut = PasswordsInteractor()

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.check_header(db_path)

    assert e.value.reason == "content-hash"


def test_decrypt_content(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    sut = PasswordsInteractor()
    sut.initialize_key_for_new_db("test-password")
    sut.initialize_new_db(db_path)

    # Act
    result = sut.decrypt(db_path)

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
    sut = PasswordsInteractor()
    sut.initialize_key_for_new_db("test-password")
    sut.initialize_new_db(db_path)
    items = sut.decrypt(db_path)
    items.append(Item.example())

    # Act
    sut.update(items, db_path)

    # assert
    loaded_items = sut.decrypt(db_path)
    assert len(loaded_items) == 2
