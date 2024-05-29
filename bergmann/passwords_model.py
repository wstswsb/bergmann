import hashlib
import json
import os
from pathlib import Path

from bergmann.common.exceptions import IntegrityError
from bergmann.convention import (
    CONTENT_HASH_SIZE,
    DB_ALG_BYTES,
    DB_ITERATIONS_BYTES,
    DB_MAGIC_BYTES,
    DB_SALT_SIZE,
)
from bergmann.crypto.kuzcypher import ICypher, KuzCypher
from bergmann.entities.header import Header
from bergmann.entities.item import Item
from bergmann.entities.store import Store
from bergmann.entities.store_meta import StoreMeta
from bergmann.key import KeyMeta


class PasswordsModel:
    def __init__(self):
        self._cypher_impl: ICypher | None = None
        self._store: Store | None = None

    def get_items(self) -> list[Item]:
        return self.store.items

    @property
    def cypher_impl(self) -> ICypher:
        if self._cypher_impl is None:
            raise ValueError("there no ICypher implementation set")
        return self._cypher_impl

    @cypher_impl.setter
    def cypher_impl(self, value: ICypher) -> None:
        self._cypher_impl = value

    @property
    def store(self) -> Store:
        if self._store is None:
            raise ValueError("there no Store set")
        return self._store

    @store.setter
    def store(self, value: Store) -> None:
        self._store = value

    def read_header(self, path: Path) -> Header:
        with path.open("rb") as file:
            header = Header(
                magic_bytes=file.read(len(DB_MAGIC_BYTES)),
                alg_bytes=file.read(len(DB_ALG_BYTES)),
                salt_bytes=file.read(DB_SALT_SIZE),
                iterations_bytes=file.read(len(DB_ITERATIONS_BYTES)),
                content_hash=file.read(CONTENT_HASH_SIZE),
            )
        return header

    def update_items(self, items: list[Item]) -> None:
        self.store.items = items

    def decrypt_store(self, path: Path) -> None:
        header = self.read_header(path)
        content_bytes = self._decrypt_content(path, header)
        self._check_integrity(content_bytes, header)
        self.store = Store.from_header(header, items=self._parse_items(content_bytes))

    def initialize_new_store(self) -> None:
        self.store = Store(meta=StoreMeta(salt=os.urandom(DB_SALT_SIZE)))
        self.store.add_item(Item.example())

    def initialize_key_for_new_db(self, master_password: str) -> None:
        self._cypher_impl = KuzCypher(master_password, self.store.key_meta)

    def initialize_key(self, path: Path, master_password: str) -> None:
        header = self.read_header(path)
        key_meta = KeyMeta.from_header(header)
        self._cypher_impl = KuzCypher(master_password, key_meta)

    def flush_encrypted_store(self, path: Path) -> None:
        encrypted_items = self._encrypt_content(self.store.items)
        path.write_bytes(self.store.header.as_bytes() + encrypted_items)

    def clean(self) -> None:
        self._store = None
        self._cypher_impl = None

    def _check_integrity(self, content_bytes: bytes, header: Header) -> None:
        content_hash = hashlib.sha256(content_bytes).digest()
        if header.content_hash != content_hash:
            raise IntegrityError()

    def _read_encrypted_content(self, path: Path, header: Header) -> bytes:
        with path.open("rb") as file:
            file.seek(header.bytes_size_on_disk)
            content = file.read()
        return content

    def _parse_items(self, content: bytes) -> list[Item]:
        return [Item(*item_args) for item_args in json.loads(content)]

    def _encrypt_content(self, content: list[Item]) -> bytes:
        content_json_convertible = [item.as_tuple() for item in content]
        content_json = json.dumps(content_json_convertible)
        encrypted_content = self.cypher_impl.encrypt(content_json)
        return encrypted_content

    def _decrypt_content(self, path: Path, header: Header) -> bytes:
        encrypted_content = self._read_encrypted_content(path, header)
        return self.cypher_impl.decrypt(encrypted_content)
