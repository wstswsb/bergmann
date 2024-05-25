import pytest

from bergmann.crypto.kuzcypher import KuzCypher
from bergmann.key import KeyMeta


@pytest.fixture(scope="session")
def sut() -> KuzCypher:
    key_meta = KeyMeta(salt=b"0123456789abcdef")
    return KuzCypher("test-password", key_meta)


def test_encrypt__message_shorter_than_block_size(sut: KuzCypher) -> None:
    # Arrange
    message = "0123"
    assert len(message.encode("utf8")) < sut.block_size

    # Act
    result = sut.encrypt(message)

    # Assert
    assert isinstance(result, bytes)
    assert len(result) % sut.block_size == 0
    assert result != message
    assert sut.decrypt(result) == message.encode("utf8")


def test_encrypt__message_equals_block_size(sut: KuzCypher) -> None:
    # Arrange
    message = "0123456789abcdef"
    assert len(message.encode("utf8")) == sut.block_size

    # Act
    result = sut.encrypt(message)

    # Assert
    assert isinstance(result, bytes)
    assert len(result) % sut.block_size == 0
    assert result != message
    assert sut.decrypt(result) == message.encode("utf8")


def test_encrypt__message_larger_than_block_size(sut: KuzCypher) -> None:
    # Arrange
    message = "0123456789abcdef0123"
    assert len(message.encode("utf8")) > sut.block_size

    # Act
    result = sut.encrypt(message)

    # Assert
    assert isinstance(result, bytes)
    assert len(result) % sut.block_size == 0
    assert result != message
    assert sut.decrypt(result) == message.encode("utf8")
