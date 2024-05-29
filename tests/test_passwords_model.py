from pathlib import Path

import pytest

from bergmann.common.exceptions import IntegrityError, InvalidHeader
from bergmann.convention import (
    DB_ALG_BYTES,
    DB_ITERATIONS_BYTES,
    DB_MAGIC_BYTES,
    DB_SALT_SIZE,
)
from bergmann.entities.store import Store
from bergmann.passwords_model import PasswordsModel


@pytest.fixture
def sut() -> PasswordsModel:
    return PasswordsModel()


def test_cypher_impl_property__not_initialized(sut: PasswordsModel) -> None:
    # Act\Assert
    with pytest.raises(ValueError):
        sut.cypher_impl  # noqa


def test_store_property__not_initialized(sut: PasswordsModel) -> None:
    # Act\Assert
    with pytest.raises(ValueError):
        sut.store  # noqa


def test_get_items__store_not_initialized(sut: PasswordsModel) -> None:
    # Act\Assert
    with pytest.raises(ValueError):
        sut.get_items()


def test_read_header__invalid_magic_bytes(sut: PasswordsModel, tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(b"invalid-bytes")

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "magic-bytes"


def test_read_header__invalid_alg_bytes(sut: PasswordsModel, tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(DB_MAGIC_BYTES + b"invalid-alg-bytes")

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "alg"


def test_read_header__invalid_salt_size(sut: PasswordsModel, tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(DB_MAGIC_BYTES + DB_ALG_BYTES + b"short-salt")

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "salt"


def test_read_header__invalid_iteration_bytes(
    sut: PasswordsModel, tmp_path: Path
) -> None:
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

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "iterations"


def test_read_header__invalid_content_hash_size(
    sut: PasswordsModel, tmp_path: Path
) -> None:
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

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "content-hash"


def test_initialize_new_store(sut: PasswordsModel) -> None:
    # Act
    sut.initialize_new_store()

    # Assert
    assert isinstance(sut.store, Store)
    assert sut.store.header
    assert sut.store.key_meta
    assert sut.store.items


def test_initialize_key_for_new_db(sut: PasswordsModel) -> None:
    # Arrange
    sut.initialize_new_store()

    # Act
    sut.initialize_key_for_new_db("test-password")

    # Assert
    assert sut.cypher_impl
    assert sut.cypher_impl.key_meta == sut.store.key_meta


def test_clean__no_initialized_properties_for_clean(sut: PasswordsModel) -> None:
    # Act
    sut.clean()

    # Assert
    with pytest.raises(ValueError):
        sut.store  # noqa
    with pytest.raises(ValueError):
        sut.cypher_impl  # noqa


def test_clean__properties_initialized(sut: PasswordsModel, tmp_path: Path) -> None:
    # Arrange
    sut.initialize_new_store()
    sut.initialize_key_for_new_db(master_password="test-key")

    # Act
    sut.clean()

    # Assert
    with pytest.raises(ValueError):
        sut.store  # noqa
    with pytest.raises(ValueError):
        sut.cypher_impl  # noqa


def test_decrypt_store(sut: PasswordsModel, tmp_path: Path) -> None:
    # Arrange
    path = tmp_path / "new.bmn"
    sut.initialize_new_store()
    sut.initialize_key_for_new_db(master_password="test-key")
    sut.flush_encrypted_store(path)
    old_store_id = id(sut.store)

    # Act
    sut.decrypt_store(path)

    # Assert
    assert id(sut.store) != old_store_id
    assert sut.store.items
    assert sut.store.key_meta
    assert sut.store.header


def test_decrypt_store__no_key_initialized(sut: PasswordsModel, tmp_path: Path) -> None:
    path = tmp_path / "new.bmn"
    sut.initialize_new_store()
    sut.initialize_key_for_new_db("test-key")
    sut.flush_encrypted_store(path)
    sut.clean()

    # Act\Assert
    with pytest.raises(ValueError):
        sut.decrypt_store(tmp_path / "new.bmn")


def test_decrypt_store__integrity_error(sut: PasswordsModel, tmp_path: Path) -> None:
    # Arrange
    path = tmp_path / "new.bmn"
    sut.initialize_new_store()
    sut.initialize_key_for_new_db("test-key")
    sut.flush_encrypted_store(path)
    with path.open("ab") as file:
        file.write(b"new-tail")

    # Act

    with pytest.raises(IntegrityError):
        sut.decrypt_store(path)


def test_initialize_key(sut: PasswordsModel, tmp_path: Path) -> None:
    # Arrange
    path = tmp_path / "new.bmn"
    sut.initialize_new_store()
    sut.initialize_key_for_new_db("test-key")
    sut.flush_encrypted_store(path)
    initialized_key_meta = sut.cypher_impl.key_meta
    sut.clean()

    # Act
    sut.initialize_key(path, master_password="test-key")

    # Assert
    assert sut.cypher_impl.key_meta == initialized_key_meta
    assert id(sut.cypher_impl.key_meta) != id(initialized_key_meta)
