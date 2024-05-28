import hashlib
import json
import os
from pathlib import Path
from typing import Literal

from bergmann.convention import (
    CONTENT_HASH_SIZE,
    DB_ALG_BYTES,
    DB_ITERATIONS_BYTES,
    DB_MAGIC_BYTES,
    DB_SALT_SIZE,
)
from bergmann.crypto.kuzcypher import ICypher, KuzCypher
from bergmann.entities.db_meta import DBMeta, RawDBMeta
from bergmann.entities.item import Item
from bergmann.key import KeyMeta


class Repository:
    def __init__(self, path: Path):
        self._path = path

    @property
    def path(self) -> Path:
        return self._path


class InvalidHeader(Exception):
    def __init__(
        self,
        reason: Literal["magic-bytes", "alg", "salt", "iterations", "content-hash"],
        *args,
    ):
        self.reason = reason
        super().__init__(*args)


class IntegrityError(Exception):
    pass


class PasswordsInteractor:
    def __init__(self):
        self._cypher_impl: ICypher | None = None

    @property
    def cypher_impl(self) -> ICypher:
        if self._cypher_impl is None:
            raise ValueError("there no ICypher implementation set")
        return self._cypher_impl

    def check_header(self, path: Path) -> None:
        raw_db_meta = self.read_raw_db_meta(path)
        self.validate_raw_db_meta(raw_db_meta)

    def validate_raw_db_meta(self, raw_db_meta: RawDBMeta) -> None:
        if raw_db_meta.magic_bytes != DB_MAGIC_BYTES:
            raise InvalidHeader(reason="magic-bytes")
        if raw_db_meta.alg_bytes != DB_ALG_BYTES:
            raise InvalidHeader(reason="alg")
        if len(raw_db_meta.salt_bytes) != DB_SALT_SIZE:
            raise InvalidHeader(reason="salt")
        if raw_db_meta.iterations_bytes != DB_ITERATIONS_BYTES:
            raise InvalidHeader(reason="iterations")
        if len(raw_db_meta.content_hash) != CONTENT_HASH_SIZE:
            raise InvalidHeader(reason="content-hash")

    def read_raw_db_meta(self, path: Path) -> RawDBMeta:
        with path.open("rb") as file:
            magic_bytes = file.read(len(DB_MAGIC_BYTES))
            alg_bytes = file.read(len(DB_ALG_BYTES))
            salt_bytes = file.read(DB_SALT_SIZE)
            iterations_bytes = file.read(len(DB_ITERATIONS_BYTES))
            content_hash = file.read(CONTENT_HASH_SIZE)
        return RawDBMeta(
            magic_bytes,
            alg_bytes,
            salt_bytes,
            iterations_bytes,
            content_hash,
        )

    def update(self, content: list[Item], path: Path) -> None:
        raw_db_meta = self.read_raw_db_meta(path)
        self.validate_raw_db_meta(raw_db_meta)
        db_meta = DBMeta.from_raw_db_meta(raw_db_meta)
        db_meta.content_hash = self._calculate_content_hash(content)
        encrypted_content = self._encrypt_content(content)
        bytes_view = self._present_template(db_meta, encrypted_content)
        with path.open("wb") as file:
            file.write(bytes_view)

    def load_db_meta(self, path: Path) -> DBMeta:
        raw_db_meta = self.read_raw_db_meta(path)
        self.validate_raw_db_meta(raw_db_meta)
        return DBMeta.from_raw_db_meta(raw_db_meta)

    def decrypt(self, path: Path) -> list[Item]:
        db_meta = self.load_db_meta(path)
        encrypted_content = self.load_encrypted_content(path, db_meta)
        decrypted_content = self.cypher_impl.decrypt(encrypted_content)
        content_hash = hashlib.sha256(decrypted_content).digest()
        if db_meta.content_hash != content_hash:
            raise IntegrityError()
        return self._parse_items(decrypted_content)

    def _parse_items(self, content: bytes) -> list[Item]:
        return [Item(*item_args) for item_args in json.loads(content)]

    def load_encrypted_content(self, path: Path, db_meta: DBMeta) -> bytes:
        with path.open("rb") as file:
            file.seek(db_meta.bytes_size_on_disk)
            content = file.read()
        return content

    def initialize_new_db(self, path: Path) -> None:
        db_meta = DBMeta.from_key_meta(self.cypher_impl.key_meta)
        default_content = [Item.example()]
        db_meta.content_hash = self._calculate_content_hash(default_content)
        encrypted_content = self._encrypt_content(default_content)
        template_bytes = self._present_template(db_meta, encrypted_content)
        path.write_bytes(template_bytes)

    def file_empty(self, path: Path) -> bool:
        return os.stat(path).st_size == 0

    def _calculate_content_hash(self, content: list[Item]) -> bytes:
        content_json_convertible = [item.as_tuple() for item in content]
        content_json_bytes = json.dumps(content_json_convertible).encode("utf8")
        return hashlib.sha256(content_json_bytes).digest()

    def _encrypt_content(self, content: list[Item]) -> bytes:
        content_json_convertible = [item.as_tuple() for item in content]
        content_json = json.dumps(content_json_convertible)
        encrypted_content = self.cypher_impl.encrypt(content_json)
        return encrypted_content

    def _present_template(
        self,
        db_meta: DBMeta,
        encrypted_content: bytes,
    ) -> bytes:
        return b"".join(
            (
                db_meta.magic_bytes,
                db_meta.algorithm,
                db_meta.salt,
                db_meta.iterations.to_bytes(length=4),
                db_meta.content_hash,
                encrypted_content,
            )
        )

    def initialize_key_for_new_db(self, master_password: str) -> None:
        key_meta = KeyMeta()
        self._cypher_impl = KuzCypher(master_password, key_meta)

    def initialize_key(
        self,
        path: Path,
        master_password: str,
    ) -> None:
        db_meta = self.load_db_meta(path)
        key_meta = KeyMeta.from_db_meta(db_meta)
        self._cypher_impl = KuzCypher(master_password, key_meta)

    def delete_key(self) -> None:
        self._cypher_impl = None
