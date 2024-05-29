from pathlib import Path

import pytest

from bergmann.common.exceptions import InvalidHeader
from bergmann.convention import (
    DB_ALG_BYTES,
    DB_ITERATIONS_BYTES,
    DB_MAGIC_BYTES,
    DB_SALT_SIZE,
)
from bergmann.di import di


def test_read_header__invalid_magic_bytes(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(b"invalid-bytes")
    sut = di.passwords_interactor

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "magic-bytes"


def test_read_header__invalid_alg_bytes(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(DB_MAGIC_BYTES + b"invalid-alg-bytes")
    sut = di.passwords_interactor

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "alg"


def test_read_header__invalid_salt_size(tmp_path: Path) -> None:
    # Arrange
    db_path = tmp_path / "new.bmn"
    db_path.write_bytes(DB_MAGIC_BYTES + DB_ALG_BYTES + b"short-salt")

    sut = di.passwords_interactor

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "salt"


def test_read_header__invalid_iteration_bytes(tmp_path: Path) -> None:
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

    sut = di.passwords_interactor

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "iterations"


def test_read_header__invalid_content_hash_size(tmp_path: Path) -> None:
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
    sut = di.passwords_interactor

    # Act\Assert
    with pytest.raises(InvalidHeader) as e:
        sut.read_header(db_path)

    assert e.value.reason == "content-hash"
