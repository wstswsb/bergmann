import hashlib
import json
from typing import Self

from bergmann.entities.header import Header
from bergmann.entities.item import Item
from bergmann.entities.store_meta import StoreMeta
from bergmann.key import KeyMeta


class Store:
    def __init__(self, meta: "StoreMeta", items: list[Item] | None = None):
        self._meta = meta
        self._items: list[Item] = items or []

    @classmethod
    def from_header(cls, header: Header, items: list[Item] | None = None) -> Self:
        meta = StoreMeta(salt=header.salt_bytes)
        return cls(meta=meta, items=items)

    @property
    def key_meta(self) -> KeyMeta:
        return self._meta.key_meta

    @property
    def header(self) -> Header:
        return Header(
            magic_bytes=self._meta.magic_bytes,
            alg_bytes=self._meta.algorithm,
            salt_bytes=self._meta.salt,
            iterations_bytes=self._meta.iterations_bytes,
            content_hash=self.items_hash(),
        )

    @property
    def items(self) -> list[Item]:
        return self._items

    @items.setter
    def items(self, value: list[Item]) -> None:
        self._items = value

    def items_hash(self) -> bytes:
        json_convertible = [item.as_tuple() for item in self._items]
        json_bytes = json.dumps(json_convertible).encode("utf8")
        return hashlib.sha256(json_bytes).digest()

    def add_item(self, item: Item) -> None:
        self._items.append(item)
