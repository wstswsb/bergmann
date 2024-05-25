import hashlib
import typing

from grassnechik import Grassnechik
from grassnechik import Key as BinaryKey

from bergmann.key import KeyMeta


class ICypher(typing.Protocol):
    def encrypt(self, message: str) -> bytes: ...

    def decrypt(self, cypher_text: bytes) -> bytes: ...

    @property
    def key_meta(self) -> KeyMeta: ...


class KuzCypher:
    def __init__(self, password: str, key_meta: KeyMeta):
        self._key_meta = key_meta
        key_bytes = self._build_key_bytes(password.encode("utf8"), key_meta)
        self._crypto_impl = Grassnechik(BinaryKey(key_bytes))  # todo: less strict

    @property
    def key_meta(self) -> KeyMeta:
        return self._key_meta

    def encrypt(self, message: str) -> bytes:
        plain_text = self.pad(message.encode("utf8"))
        cypher_blocks: list[bytes] = []
        for block_index in range(0, len(plain_text), self.block_size):
            block = plain_text[block_index : block_index + self.block_size]
            encrypted = self._crypto_impl.encrypt(tuple(block))
            cypher_blocks.append(bytes(encrypted))
        return b"".join(cypher_blocks)

    def decrypt(self, cypher_bytes: bytes) -> bytes:
        plain_blocks: list[bytes] = []
        for block_index in range(0, len(cypher_bytes), self.block_size):
            block = cypher_bytes[block_index : block_index + self.block_size]
            decrypted = self._crypto_impl.decrypt(tuple(block))
            plain_blocks.append(bytes(decrypted))
        plain_text_with_padding = b"".join(plain_blocks)
        return self.unpad(plain_text_with_padding)

    def _build_key_bytes(self, password: bytes, key_meta: KeyMeta) -> bytes:
        key_bytes = hashlib.pbkdf2_hmac(
            hash_name=key_meta.hash_function,
            password=password,
            iterations=key_meta.iterations,
            salt=key_meta.salt,
        )
        return key_bytes

    @property
    def block_size(self) -> int:
        return 16

    def pad(self, message_bytes: bytes) -> bytes:
        pad_len = self.block_size - len(message_bytes) % self.block_size
        return message_bytes + (bytes([pad_len]) * pad_len)

    def unpad(self, message_bytes: bytes) -> bytes:
        pad_len = message_bytes[-1]
        return message_bytes[:-pad_len]
