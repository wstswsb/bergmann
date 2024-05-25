import hashlib
import json
from pathlib import Path

from bergmann.crypto.kuzcypher import ICypher, KuzCypher
from bergmann.entities.db_meta import DBMeta
from bergmann.entities.encrypted_item import EncryptedItem
from bergmann.entities.item import Item
from bergmann.key import KeyMeta


class Repository:
    def __init__(self, path: Path):
        self._path = path

    @property
    def path(self) -> Path:
        return self._path


class PasswordsInteractor:
    def __init__(self):
        self._cypher_impl: ICypher | None = None
        self._repository: Repository | None = None

    @property
    def cypher_impl(self) -> ICypher:
        if self._cypher_impl is None:
            raise ValueError("there no ICypher implementation set")
        return self._cypher_impl

    @property
    def repository(self) -> Repository:
        if self._repository is None:
            raise ValueError("there not Repository set")
        return self._repository

    def initialize_new_db(self, path: Path) -> None:
        db_meta = DBMeta.from_key_meta(self._cypher_impl.key_meta)
        default_content = [Item.example()]
        db_meta.content_hash = self._calculate_content_hash(default_content)
        encrypted_content = self._encrypt_content(default_content)
        template_bytes = self._present_template(db_meta, encrypted_content)

        path.write_bytes(template_bytes)
        self._repository = Repository(path)

    def _calculate_content_hash(self, content: list[Item]) -> bytes:
        content_json_convertible = [item.as_tuple() for item in content]
        content_json_bytes = json.dumps(content_json_convertible).encode("utf8")
        return hashlib.sha256(content_json_bytes).digest()

    def _encrypt_content(self, content: list[Item]) -> list[EncryptedItem]:
        return [
            EncryptedItem(
                description=self._cypher_impl.encrypt(item.description),
                login=self.cypher_impl.encrypt(item.login),
                password=self.cypher_impl.encrypt(item.password),
            )
            for item in content
        ]

    def _present_encrypted_content(
        self,
        encrypted_content: list[EncryptedItem],
    ) -> bytes:
        json_convertible = [item.as_hex_tuple() for item in encrypted_content]
        return json.dumps(json_convertible).encode("utf8")

    def _present_template(
        self,
        db_meta: DBMeta,
        encrypted_content: list[EncryptedItem],
    ) -> bytes:
        return b"".join(
            (
                db_meta.magic_bytes,
                db_meta.algorithm,
                db_meta.salt,
                db_meta.iterations.to_bytes(length=4),
                db_meta.content_hash,
                self._present_encrypted_content(encrypted_content),
            )
        )

    def initialize_key(self, master_password: str) -> None:
        key_meta = KeyMeta()
        self._cypher_impl = KuzCypher(master_password, key_meta)
